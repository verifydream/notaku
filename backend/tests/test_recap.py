import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
from models import User, Transaction, TransactionItem

@pytest.mark.asyncio
async def test_handle_rekap_no_data(async_client: AsyncClient, db_session):
    user = User(phone="08555", name="Pakde")
    db_session.add(user)
    await db_session.commit()

    with patch("main.send_message", new_callable=AsyncMock) as mock_send:
        resp = await async_client.post("/webhook/fonnte", json={"phone": "08555", "message": "rekap"})
        assert resp.status_code == 200
        assert resp.json() == {"status": "no_data"}

        mock_send.assert_called_once()
        assert "belum ada transaksi" in mock_send.call_args[0][1].lower()

@pytest.mark.asyncio
async def test_handle_rekap_with_data(async_client: AsyncClient, db_session):
    user = User(phone="08556", name="Bude")
    db_session.add(user)
    await db_session.commit()

    # Add transactions
    t1 = Transaction(user_id=user.id, total=150000, type="sale")
    t2 = Transaction(user_id=user.id, total=50000, type="expense")
    db_session.add_all([t1, t2])
    await db_session.commit()

    # We should add transaction items for "Top items"
    from main import _handle_rekap

    with patch("main.send_message", new_callable=AsyncMock) as mock_send:
        resp = await async_client.post("/webhook/fonnte", json={"phone": "08556", "message": "rekap"})
        assert resp.status_code == 200
        assert resp.json() == {"status": "recap_sent"}

        mock_send.assert_called_once()
        msg = mock_send.call_args[0][1]
        assert "Omset: Rp 150.000" in msg
        assert "Pengeluaran: Rp 50.000" in msg
        assert "Profit: Rp 100.000" in msg
        assert "Transaksi: 2" in msg
