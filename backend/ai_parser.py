"""AI parser — GPT-4o-mini parses raw WhatsApp chat into structured transactions."""

import json
from openai import AsyncOpenAI
from settings import settings

client = AsyncOpenAI(api_key=settings.openai_api_key)

SYSTEM_PROMPT = """Kamu adalah parser transaksi untuk warung Indonesia.
Tugas: ekstrak item dan jumlah dari pesan mentah WhatsApp.

ATURAN:
- Match item ke menu yang tersedia (fuzzy matching, typo tolerant)
- "3 nasduk" → nasi uduk qty 3
- "kopi 2" → kopi qty 2
- "rokok sampoerna" → rokok sampoerna qty 1
- Jika ada harga manual "nasi uduk 8000" → override price
- Return JSON saja, tanpa penjelasan

Menu tersedia:
{menu_json}

Return format:
{{
  "items": [
    {{"name": "nama item asli", "qty": N, "matched_menu_id": "id", "price_override": null}},
    ...
  ]
}}
Jika tidak ada yang match, set matched_menu_id ke null."""


async def parse_message(raw_text: str, menu_items: list[dict]) -> dict:
    """Parse raw WhatsApp message → structured items.

    menu_items: [{"id": "...", "name": "Nasi Uduk", "price": 8000, "aliases": ["nasduk"]}]
    Returns: {"items": [{"name": "...", "qty": 3, "matched_menu_id": "...", "price_override": null}]}
    """
    if not settings.openai_api_key:
        # Fallback: simple regex parser when no OpenAI key
        return _fallback_parse(raw_text)

    menu_json = json.dumps(menu_items, ensure_ascii=False, indent=2)
    prompt = SYSTEM_PROMPT.format(menu_json=menu_json)

    try:
        resp = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": raw_text},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )
        return json.loads(resp.choices[0].message.content)
    except Exception as e:
        return {"items": [], "error": str(e)}


def _fallback_parse(text: str) -> dict:
    """Simple fallback when OpenAI is unavailable."""
    import re
    items = []
    # Pattern: "3 item_name" or "item_name x3" or "item_name 3"
    patterns = [
        r"(\d+)\s+(.+?)(?:\s*,|\s*$)",           # "3 nasi uduk"
        r"(.+?)\s*[xX×]\s*(\d+)(?:\s*,|\s*$)",   # "nasi uduk x3"
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            groups = match.groups()
            if pattern.startswith("(\\d+)"):
                qty, name = int(groups[0]), groups[1].strip()
            else:
                name, qty = groups[0].strip(), int(groups[1])
            items.append({"name": name, "qty": qty, "matched_menu_id": None, "price_override": None})
    return {"items": items}
