"""Fonnte WhatsApp API client."""

import httpx
from settings import settings


async def send_message(phone: str, text: str) -> dict:
    """Sends a text message to a given phone number via the Fonnte API.

    Args:
        phone (str): The destination WhatsApp phone number.
        text (str): The text message content to send.

    Returns:
        dict: The JSON response parsed from the Fonnte API.
    """
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{settings.fonnte_base_url}/send",
            headers={"Authorization": settings.fonnte_token},
            json={"target": phone, "message": text},
            timeout=10,
        )
        return resp.json()


async def send_document(phone: str, file_path: str, caption: str = "") -> dict:
    """Sends a document (e.g., PDF) to a given phone number via the Fonnte API.

    Args:
        phone (str): The destination WhatsApp phone number.
        file_path (str): The local file path of the document to send.
        caption (str, optional): An optional text caption for the document. Defaults to "".

    Returns:
        dict: The JSON response parsed from the Fonnte API.
    """
    async with httpx.AsyncClient() as client:
        with open(file_path, "rb") as f:
            resp = await client.post(
                f"{settings.fonnte_base_url}/send-media",
                headers={"Authorization": settings.fonnte_token},
                data={"target": phone, "caption": caption},
                files={"file": f},
                timeout=30,
            )
        return resp.json()
