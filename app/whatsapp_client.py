import hashlib
import hmac
import logging

import httpx

from app.config import config

logger = logging.getLogger("whatsapp_client")

GRAPH_BASE_URL = "https://graph.facebook.com"


def verify_signature(raw_body: bytes, signature_header: str | None) -> bool:
    """Verify Meta's X-Hub-Signature-256 header against the raw request body."""
    if not config.WHATSAPP_APP_SECRET:
        logger.warning("WHATSAPP_APP_SECRET not set — skipping signature verification")
        return True

    if not signature_header or not signature_header.startswith("sha256="):
        return False

    expected = signature_header.split("sha256=", 1)[1]
    computed = hmac.new(
        config.WHATSAPP_APP_SECRET.encode("utf-8"), raw_body, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, computed)


async def send_text_message(to: str, body: str) -> None:
    url = (
        f"{GRAPH_BASE_URL}/{config.WHATSAPP_API_VERSION}/"
        f"{config.WHATSAPP_PHONE_NUMBER_ID}/messages"
    )
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": body},
    }
    headers = {"Authorization": f"Bearer {config.WHATSAPP_ACCESS_TOKEN}"}

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(url, json=payload, headers=headers)
        if response.status_code >= 400:
            logger.error("Failed to send message: %s %s", response.status_code, response.text)
        response.raise_for_status()


async def mark_as_read(message_id: str) -> None:
    url = (
        f"{GRAPH_BASE_URL}/{config.WHATSAPP_API_VERSION}/"
        f"{config.WHATSAPP_PHONE_NUMBER_ID}/messages"
    )
    payload = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": message_id,
    }
    headers = {"Authorization": f"Bearer {config.WHATSAPP_ACCESS_TOKEN}"}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(url, json=payload, headers=headers)
    except Exception:
        logger.exception("Failed to mark message as read (non-fatal)")
