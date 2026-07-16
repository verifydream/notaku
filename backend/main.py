"""NotaKu — WhatsApp-native bookkeeping for Indonesian UMKM."""

import os
import json
import uuid
import asyncio
from datetime import datetime, timezone, timedelta
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from database import get_db, init_db
from models import User, MenuItem, Transaction, TransactionItem
from schemas import MenuItemCreate, MenuItemOut, TransactionOut, UserOut, DailySummary
from ai_parser import parse_message
from fonnte import send_message, send_document
from pdf_gen import generate_nota
from settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="NotaKu API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Temporary in-memory pending transactions (user_id → parsed items)
# In production, use Redis
# ---------------------------------------------------------------------------
pending: dict[str, dict] = {}


# ---------------------------------------------------------------------------
# Webhook — Fonnte WhatsApp
# ---------------------------------------------------------------------------
@app.post("/webhook/fonnte")
async def webhook_fonnte(request: Request, db: AsyncSession = Depends(get_db)):
    body = await request.json()
    phone: str = body.get("phone", "").strip()
    text: str = body.get("message", "").strip()
    msg_type: str = body.get("type", "text")

    if not phone or not text:
        return {"status": "ignored"}

    # Find or auto-create user
    result = await db.execute(select(User).where(User.phone == phone))
    user = result.scalar_one_or_none()
    if not user:
        user = User(phone=phone, name="User Baru")
        db.add(user)
        await db.commit()
        await db.refresh(user)

    text_lower = text.lower().strip()

    # --- Command: tambah menu ---
    if text_lower.startswith("tambah menu"):
        return await _handle_add_menu(user, text, db)

    # --- Command: rekap ---
    if text_lower in ("rekap", "rekap harian", "summary"):
        return await _handle_rekap(user, db)

    # --- Command: list menu ---
    if text_lower in ("menu", "list menu", "lihat menu"):
        return await _handle_list_menu(user, db)

    # --- Confirmation ---
    if text_lower in ("oke", "ok", "ya", "iy", "betul", "konfirm", "confirm"):
        return await _handle_confirm(user, db)

    # --- Cancel ---
    if text_lower in ("batal", "cancel", "x"):
        pending.pop(user.id, None)
        await send_message(phone, "❌ Dibatalkan. Kirim item lagi kalau mau.")
        return {"status": "cancelled"}

    # --- Default: parse as transaction ---
    return await _handle_parse(user, text, db)


async def _handle_add_menu(user: User, text: str, db: AsyncSession):
    """Parse 'tambah menu: nasi uduk Rp8000' → create menu item."""
    try:
        # "tambah menu: nasi uduk Rp8000"
        content = text.split(":", 1)[1].strip() if ":" in text else text.replace("tambah menu", "").strip()
        # Extract price
        import re
        price_match = re.search(r"[Rr][Pp]?\s*(\d[\d.]*\d|\d+)", content)
        if not price_match:
            await send_message(user.phone, "Format salah. Contoh:Tambah menu: nasi uduk Rp8000")
            return {"status": "error"}

        price_str = price_match.group(1).replace(".", "")
        price = int(price_str)
        name = content[:price_match.start()].strip().rstrip(",").rstrip("-")
        if not name:
            await send_message(user.phone, "Nama item kosong. Contoh: Tambah menu: nasi uduk Rp8000")
            return {"status": "error"}

        item = MenuItem(user_id=user.id, name=name, price=price, aliases=[name.lower()])
        db.add(item)
        await db.commit()

        msg = f"✅ Menu ditambahkan:\n• {name} — {_fmt_rp(price)}"
        await send_message(user.phone, msg)
        return {"status": "menu_added"}
    except Exception as e:
        await send_message(user.phone, f"❌ Error: {e}")
        return {"status": "error"}


async def _handle_list_menu(user: User, db: AsyncSession):
    """List all active menu items."""
    result = await db.execute(
        select(MenuItem).where(and_(MenuItem.user_id == user.id, MenuItem.active == True))
    )
    items = result.scalars().all()
    if not items:
        await send_message(user.phone, "📋 Menu kosong. Tambah dengan:\nTambah menu: [nama] Rp[harga]")
        return {"status": "empty_menu"}

    lines = ["📋 *Menu Warung:*"]
    for i, item in enumerate(items, 1):
        lines.append(f"{i}. {item.name} — {_fmt_rp(item.price)}")
    await send_message(user.phone, "\n".join(lines))
    return {"status": "menu_listed"}


async def _handle_parse(user: User, text: str, db: AsyncSession):
    """Parse message as transaction items."""
    # Get menu items
    result = await db.execute(
        select(MenuItem).where(and_(MenuItem.user_id == user.id, MenuItem.active == True))
    )
    menu_items = result.scalars().all()
    menu_dicts = [{"id": m.id, "name": m.name, "price": m.price, "aliases": m.aliases or []} for m in menu_items]

    if not menu_dicts:
        await send_message(user.phone, "⚠️ Menu kosong dulu. Tambah dengan:\nTambah menu: [nama] Rp[harga]")
        return {"status": "no_menu"}

    # AI parse
    parsed = await parse_message(text, menu_dicts)
    items = parsed.get("items", [])

    if not items:
        await send_message(user.phone, "🤔 Tidak bisa parse pesanmu. Coba format:\n3 nasi uduk, 1 kopi")
        return {"status": "parse_failed"}

    # Match items to menu
    matched = []
    unmatched = []
    for item in items:
        menu_id = item.get("matched_menu_id")
        menu = next((m for m in menu_items if m.id == menu_id), None) if menu_id else None
        if not menu:
            # Fuzzy match by name
            name_lower = item["name"].lower()
            menu = next(
                (m for m in menu_items if name_lower in m.name.lower() or
                 any(name_lower in (a or "").lower() for a in (m.aliases or []))),
                None,
            )
        if menu:
            qty = item.get("qty", 1)
            price_override = item.get("price_override")
            unit_price = price_override or menu.price
            matched.append({
                "menu_item_id": menu.id,
                "name": menu.name,
                "qty": qty,
                "unit_price": unit_price,
                "subtotal": unit_price * qty,
            })
        else:
            unmatched.append(item["name"])

    if not matched:
        await send_message(user.phone, f"❌ Tidak ada yang cocok di menu.\nItem: {', '.join(unmatched)}")
        return {"status": "no_match"}

    total = sum(m["subtotal"] for m in matched)

    # Store pending
    pending[user.id] = {"items": matched, "total": total}

    # Build confirmation message
    lines = ["📝 *Konfirmasi transaksi:*"]
    for m in matched:
        lines.append(f"• {m['qty']}x {m['name']} = {_fmt_rp(m['subtotal'])}")
    lines.append(f"\n💰 *Total: {_fmt_rp(total)}*")
    lines.append("\nKetik *oke* untuk konfirmasi, *batal* untuk batalkan.")
    if unmatched:
        lines.append(f"\n⚠️ Tidak dikenali: {', '.join(unmatched)}")

    await send_message(user.phone, "\n".join(lines))
    return {"status": "parsed"}


async def _handle_confirm(user: User, db: AsyncSession):
    """Confirm and save pending transaction."""
    if user.id not in pending:
        await send_message(user.phone, "Tidak ada transaksi yang pending. Kirim item dulu.")
        return {"status": "no_pending"}

    data = pending.pop(user.id)
    items = data["items"]
    total = data["total"]

    # Save transaction
    tx = Transaction(user_id=user.id, total=total, type="sale")
    db.add(tx)
    await db.flush()

    for item in items:
        tx_item = TransactionItem(
            transaction_id=tx.id,
            menu_item_id=item["menu_item_id"],
            quantity=item["qty"],
            unit_price=item["unit_price"],
            subtotal=item["subtotal"],
        )
        db.add(tx_item)
    await db.commit()

    # Generate PDF
    pdf_items = [{"name": i["name"], "qty": i["qty"], "subtotal": i["subtotal"]} for i in items]
    warung_name = user.warung_name or user.name or "Warung"
    pdf_path = generate_nota(warung_name, pdf_items, total, tx.id)

    # Send confirmation + PDF
    await send_message(user.phone, f"✅ Tersimpan! Total: {_fmt_rp(total)}")
    await send_document(user.phone, pdf_path, f"Nota #{tx.id[:8]}")

    # Cleanup
    try:
        os.unlink(pdf_path)
    except OSError:
        pass

    return {"status": "confirmed"}


async def _handle_rekap(user: User, db: AsyncSession):
    """Generate daily recap."""
    today_start = datetime.now(timezone(timedelta(hours=7))).replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    result = await db.execute(
        select(Transaction).where(
            and_(
                Transaction.user_id == user.id,
                Transaction.created_at >= today_start,
                Transaction.created_at < today_end,
            )
        )
    )
    txs = result.scalars().all()

    if not txs:
        await send_message(user.phone, "📊 Hari ini belum ada transaksi.")
        return {"status": "no_data"}

    sales = sum(t.total for t in txs if t.type == "sale")
    expenses = sum(t.total for t in txs if t.type == "expense")
    profit = sales - expenses
    count = len(txs)

    # Top items
    item_result = await db.execute(
        select(TransactionItem, func.sum(TransactionItem.quantity).label("total_qty"))
        .join(Transaction)
        .where(
            and_(
                Transaction.user_id == user.id,
                Transaction.created_at >= today_start,
                Transaction.created_at < today_end,
            )
        )
        .group_by(TransactionItem.menu_item_id)
        .order_by(func.sum(TransactionItem.quantity).desc())
        .limit(3)
    )
    top = item_result.all()

    lines = [f"📊 *Rekap {today_start.strftime('%d %b %Y')}*"]
    lines.append(f"💰 Omset: {_fmt_rp(sales)}")
    lines.append(f"📤 Pengeluaran: {_fmt_rp(expenses)}")
    lines.append(f"💵 Profit: {_fmt_rp(profit)}")
    lines.append(f"🧾 Transaksi: {count}")
    if top:
        lines.append("\n🏆 *Top item:*")
        for ti, qty in top:
            mi = next((m for m in [] if m.id == ti.menu_item_id), None)
            lines.append(f"• {ti.quantity}x item")

    await send_message(user.phone, "\n".join(lines))
    return {"status": "recap_sent"}


def _fmt_rp(amount: int) -> str:
    s = str(abs(amount))[::-1]
    chunks = [s[i:i + 3] for i in range(0, len(s), 3)]
    return "Rp " + ".".join(chunks)[::-1]


# ---------------------------------------------------------------------------
# REST API — for dashboard
# ---------------------------------------------------------------------------
@app.get("/api/users/{phone}", response_model=UserOut)
async def get_user(phone: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.phone == phone))
    user = result.scalar_one_or_none()
    if not user:
        from fastapi import HTTPException
        raise HTTPException(404, "User not found")
    return user


@app.get("/api/users/{phone}/menu", response_model=list[MenuItemOut])
async def list_menu(phone: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.phone == phone))
    user = result.scalar_one_or_none()
    if not user:
        from fastapi import HTTPException
        raise HTTPException(404, "User not found")
    result = await db.execute(
        select(MenuItem).where(and_(MenuItem.user_id == user.id, MenuItem.active == True))
    )
    return result.scalars().all()


@app.post("/api/users/{phone}/menu", response_model=MenuItemOut)
async def add_menu(phone: str, data: MenuItemCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.phone == phone))
    user = result.scalar_one_or_none()
    if not user:
        from fastapi import HTTPException
        raise HTTPException(404, "User not found")
    item = MenuItem(user_id=user.id, name=data.name, price=data.price, aliases=data.aliases)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@app.get("/api/users/{phone}/transactions", response_model=list[TransactionOut])
async def list_transactions(phone: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.phone == phone))
    user = result.scalar_one_or_none()
    if not user:
        from fastapi import HTTPException
        raise HTTPException(404, "User not found")
    result = await db.execute(
        select(Transaction)
        .where(Transaction.user_id == user.id)
        .order_by(Transaction.created_at.desc())
        .limit(100)
    )
    return result.scalars().all()


@app.get("/api/users/{phone}/summary", response_model=DailySummary)
async def daily_summary(phone: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.phone == phone))
    user = result.scalar_one_or_none()
    if not user:
        from fastapi import HTTPException
        raise HTTPException(404, "User not found")

    today = datetime.now(timezone(timedelta(hours=7))).replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)

    result = await db.execute(
        select(Transaction).where(
            and_(Transaction.user_id == user.id, Transaction.created_at >= today, Transaction.created_at < tomorrow)
        )
    )
    txs = result.scalars().all()
    sales = sum(t.total for t in txs if t.type == "sale")
    expenses = sum(t.total for t in txs if t.type == "expense")

    return DailySummary(
        date=today.strftime("%Y-%m-%d"),
        total_sales=sales,
        total_expenses=expenses,
        profit=sales - expenses,
        transaction_count=len(txs),
        top_items=[],
    )


@app.get("/health")
async def health():
    return {"status": "ok", "service": "notaku"}
