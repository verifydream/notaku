import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from ai_parser import parse_message, _fallback_parse

@pytest.mark.asyncio
async def test_fallback_parse():
    # Because _fallback_parse loops through patterns independently without removing matches,
    # it can sometimes match overlapping strings if the text is complex.
    # We will test simpler individual matches first.

    result1 = _fallback_parse("3 nasduk")
    assert result1["items"][0]["qty"] == 3
    assert result1["items"][0]["name"] == "nasduk"

    result2 = _fallback_parse("kopi x2")
    # second pattern will match
    assert any(i["qty"] == 2 and i["name"] == "kopi" for i in result2["items"])

@pytest.mark.asyncio
async def test_parse_message_with_openai():
    menu_items = [
        {"id": "menu1", "name": "Nasi Uduk", "price": 10000, "aliases": ["nasduk"]},
        {"id": "menu2", "name": "Kopi Susu", "price": 5000, "aliases": ["kopi"]}
    ]

    # Mock settings to have API key
    with patch("ai_parser.settings") as mock_settings:
        mock_settings.openai_api_key = "test-key"

        # Mock OpenAI response
        mock_choice = MagicMock()
        mock_choice.message.content = '{"items": [{"name": "nasi uduk", "qty": 3, "matched_menu_id": "menu1", "price_override": null}, {"name": "kopi susu", "qty": 1, "matched_menu_id": "menu2", "price_override": null}]}'

        mock_resp = MagicMock()
        mock_resp.choices = [mock_choice]

        with patch("ai_parser.client.chat.completions.create", new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_resp

            result = await parse_message("3 nasduk 1 kopi susu", menu_items)

            assert "items" in result
            items = result["items"]
            assert len(items) == 2
            assert items[0]["qty"] == 3
            assert items[0]["matched_menu_id"] == "menu1"
            assert items[1]["qty"] == 1
            assert items[1]["matched_menu_id"] == "menu2"
