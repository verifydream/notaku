"""Fonnte WhatsApp API client."""

import httpx
from settings import settings


async def send_message(phone: str, text: str) -> dict:
    """Send text message via Fonnte API."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{settings.fonnte_base_url}/send",
            headers={"Authorization": settings.fonnte_token},
            json={"target": phone, "message": text},
            timeout=10,
        )
        return resp.json()


async def send_document(phone: str, file_path: str, caption: str = "") -> dict:
    """Send document (PDF) via Fonnte API."""
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
