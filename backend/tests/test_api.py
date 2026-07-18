import pytest
from httpx import AsyncClient
from models import User, MenuItem, Transaction, TransactionItem
from sqlalchemy.orm import selectinload

@pytest.mark.asyncio
async def test_api_get_user(async_client: AsyncClient, db_session):
    user = User(phone="08111222", name="Budi")
    db_session.add(user)
    await db_session.commit()

    resp = await async_client.get("/api/users/08111222")
    assert resp.status_code == 200
    data = resp.json()
    assert data["phone"] == "08111222"
    assert data["name"] == "Budi"

@pytest.mark.asyncio
async def test_api_add_menu(async_client: AsyncClient, db_session):
    user = User(phone="08111333", name="Siti")
    db_session.add(user)
    await db_session.commit()

    resp = await async_client.post(
        "/api/users/08111333/menu",
        json={"name": "Soto Ayam", "price": 15000, "aliases": ["soto"]}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Soto Ayam"
    assert data["price"] == 15000
    assert data["aliases"] == ["soto"]

@pytest.mark.asyncio
async def test_api_list_menu(async_client: AsyncClient, db_session):
    user = User(phone="08111444", name="Tono")
    db_session.add(user)
    await db_session.commit()

    m1 = MenuItem(user_id=user.id, name="Mie Goreng", price=12000, active=True)
    db_session.add(m1)
    await db_session.commit()

    resp = await async_client.get("/api/users/08111444/menu")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "Mie Goreng"

@pytest.mark.asyncio
async def test_api_list_transactions(async_client: AsyncClient, db_session):
    user = User(phone="08111555", name="Andi")
    db_session.add(user)
    await db_session.commit()

    t1 = Transaction(user_id=user.id, total=50000, type="sale")
    db_session.add(t1)
    await db_session.commit()

    resp = await async_client.get("/api/users/08111555/transactions")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["total"] == 50000
    assert data[0]["type"] == "sale"

@pytest.mark.asyncio
async def test_api_summary(async_client: AsyncClient, db_session):
    user = User(phone="08111666", name="Joko")
    db_session.add(user)
    await db_session.commit()

    t1 = Transaction(user_id=user.id, total=100000, type="sale")
    t2 = Transaction(user_id=user.id, total=20000, type="expense")
    db_session.add_all([t1, t2])
    await db_session.commit()

    resp = await async_client.get("/api/users/08111666/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_sales"] == 100000
    assert data["total_expenses"] == 20000
    assert data["profit"] == 80000
    assert data["transaction_count"] == 2
