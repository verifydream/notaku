"""PDF nota generator — ReportLab."""

import os
import tempfile
from datetime import datetime
from reportlab.lib.pagesizes import A6
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


def _fmt_rp(amount: int) -> str:
    """Formats an integer amount into a Rupiah string.

    Args:
        amount (int): The amount in integer format (e.g., 42000).

    Returns:
        str: The formatted currency string (e.g., 'Rp 42.000').
    """
    s = str(amount)[::-1]
    chunks = [s[i:i + 3] for i in range(0, len(s), 3)]
    return "Rp " + ".".join(chunks)[::-1]


def generate_nota(
    warung_name: str,
    items: list[dict],
    total: int,
    transaction_id: str,
    date: datetime | None = None,
) -> str:
    """Generates a PDF receipt (nota) using ReportLab.

    Args:
        warung_name (str): The name of the warung/shop.
        items (list[dict]): A list of dictionaries representing the transaction items.
            Expected format: [{"name": str, "qty": int, "subtotal": int}]
        total (int): The total amount for the transaction.
        transaction_id (str): The unique transaction ID.
        date (datetime | None, optional): The date and time of the transaction.
            Defaults to the current datetime if not provided.

    Returns:
        str: The file path to the generated temporary PDF file.
    """
    date = date or datetime.now()
    width, height = A6  # 105mm x 148mm

    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False, prefix="nota_")
    c = canvas.Canvas(tmp.name, pagesize=A6)

    y = height - 15 * mm

    # Warung name
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, y, warung_name)
    y -= 7 * mm

    # Date & ID
    c.setFont("Helvetica", 7)
    c.drawCentredString(width / 2, y, date.strftime("%d %b %Y %H:%M"))
    y -= 4 * mm
    c.drawCentredString(width / 2, y, f"#{transaction_id[:8]}")
    y -= 8 * mm

    # Divider
    c.line(8 * mm, y, width - 8 * mm, y)
    y -= 6 * mm

    # Items
    c.setFont("Helvetica", 8)
    for item in items:
        line = f"{item['qty']}x {item['name']}"
        price = _fmt_rp(item["subtotal"])
        c.drawString(8 * mm, y, line)
        c.drawRightString(width - 8 * mm, y, price)
        y -= 5 * mm

    # Divider
    y -= 2 * mm
    c.line(8 * mm, y, width - 8 * mm, y)
    y -= 6 * mm

    # Total
    c.setFont("Helvetica-Bold", 10)
    c.drawString(8 * mm, y, "TOTAL")
    c.drawRightString(width - 8 * mm, y, _fmt_rp(total))
    y -= 8 * mm

    # Footer
    c.setFont("Helvetica", 6)
    c.drawCentredString(width / 2, y, "Terima kasih atas kunjungan Anda! 🙏")

    c.save()
    return tmp.name
