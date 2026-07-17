import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from main import _handle_parse
from models import User, MenuItem

@pytest.mark.asyncio
async def test_handle_parse_fuzzy_matching():
    user = User(id="user1", phone="08123")

    m1 = MenuItem(id="m1", user_id="user1", name="Nasi Uduk", price=10000, aliases=["nasduk"], active=True)
    m2 = MenuItem(id="m2", user_id="user1", name="Kopi Susu", price=5000, aliases=["kopi"], active=True)
    menu_items = [m1, m2]

    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = menu_items
    mock_db.execute.return_value = mock_result

    # Fuzzy matching in main.py checks if item["name"].lower() is IN m.name.lower() or aliases
    # So if user types "nasi uduk spesial", "nasi uduk spesial" in "nasi uduk" is False
    # But if user types "udu", "udu" in "nasi uduk" is True
    parsed_data = {
        "items": [
            {"name": "udu", "qty": 1, "matched_menu_id": None, "price_override": None},
            {"name": "kopi", "qty": 2, "matched_menu_id": None, "price_override": None},
            {"name": "sate", "qty": 1, "matched_menu_id": None, "price_override": None}
        ]
    }

    with patch("main.parse_message", new_callable=AsyncMock) as mock_parse:
        mock_parse.return_value = parsed_data

        with patch("main.send_message", new_callable=AsyncMock) as mock_send:
            with patch("main.pending", {}):
                import main
                res = await _handle_parse(user, "1 udu, 2 kopi, 1 sate", mock_db)

                assert res["status"] == "parsed"

                pending_tx = main.pending["user1"]
                matched_items = pending_tx["items"]

                assert len(matched_items) == 2
                assert matched_items[0]["menu_item_id"] == "m1"  # Nasi Uduk
                assert matched_items[1]["menu_item_id"] == "m2"  # Kopi Susu

                mock_send.assert_called_once()
                call_arg = mock_send.call_args[0][1]
                assert "Tidak dikenali: sate" in call_arg
