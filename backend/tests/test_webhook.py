import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
from models import User

@pytest.mark.asyncio
async def test_webhook_fonnte_ignored(async_client: AsyncClient):
    resp = await async_client.post("/webhook/fonnte", json={"phone": "", "message": ""})
    assert resp.status_code == 200
    assert resp.json() == {"status": "ignored"}

@pytest.mark.asyncio
async def test_webhook_fonnte_auto_create_user_and_list_menu(async_client: AsyncClient, db_session):
    with patch("main.send_message", new_callable=AsyncMock) as mock_send:
        resp = await async_client.post("/webhook/fonnte", json={"phone": "089999", "message": "menu"})
        assert resp.status_code == 200
        assert resp.json() == {"status": "empty_menu"}

        # User should be created
        import sqlalchemy
        from models import User
        result = await db_session.execute(sqlalchemy.select(User).where(User.phone == "089999"))
        user = result.scalar_one_or_none()
        assert user is not None
        assert user.name == "User Baru"

@pytest.mark.asyncio
async def test_webhook_fonnte_add_menu(async_client: AsyncClient, db_session):
    with patch("main.send_message", new_callable=AsyncMock) as mock_send:
        resp = await async_client.post("/webhook/fonnte", json={"phone": "089999", "message": "tambah menu: nasi goreng rp15000"})
        assert resp.status_code == 200
        assert resp.json() == {"status": "menu_added"}

        mock_send.assert_called_once()
        assert "nasi goreng" in mock_send.call_args[0][1]

@pytest.mark.asyncio
async def test_webhook_fonnte_full_flow(async_client: AsyncClient, db_session):
    # 1. Add menu
    with patch("main.send_message", new_callable=AsyncMock):
        await async_client.post("/webhook/fonnte", json={"phone": "087777", "message": "tambah menu: Kopi Rp5000"})

    # 2. Parse transaction
    with patch("main.send_message", new_callable=AsyncMock) as mock_send:
        with patch("ai_parser.client.chat.completions.create", new_callable=AsyncMock) as mock_create:
            mock_choice = AsyncMock()
            mock_choice.message.content = '{"items": [{"name": "kopi", "qty": 2, "matched_menu_id": null, "price_override": null}]}'
            mock_resp = AsyncMock()
            mock_resp.choices = [mock_choice]
            mock_create.return_value = mock_resp

            # Use a slightly fuzzy name to also test matching
            resp = await async_client.post("/webhook/fonnte", json={"phone": "087777", "message": "2 kopi"})
            assert resp.status_code == 200
            assert resp.json() == {"status": "parsed"}

            mock_send.assert_called_once()
            assert "📝 *Konfirmasi transaksi:*" in mock_send.call_args[0][1]
            assert "Total: Rp 10.000" in mock_send.call_args[0][1]

    # 3. Confirm transaction
    with patch("main.send_message", new_callable=AsyncMock) as mock_send:
        with patch("main.send_document", new_callable=AsyncMock) as mock_doc:
            resp = await async_client.post("/webhook/fonnte", json={"phone": "087777", "message": "oke"})
            assert resp.status_code == 200
            assert resp.json() == {"status": "confirmed"}

            mock_send.assert_called_once()
            assert "✅ Tersimpan! Total: Rp 10.000" in mock_send.call_args[0][1]
            mock_doc.assert_called_once()
            assert mock_doc.call_args[0][1].endswith(".pdf")
