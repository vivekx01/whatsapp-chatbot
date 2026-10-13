import logging

from fastapi import BackgroundTasks, FastAPI, Request, Response

from app.chatbot import get_bot_reply
from app.config import config
from app.storage import get_history, init_db, save_message
from app.whatsapp_client import mark_as_read, send_text_message, verify_signature

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

app = FastAPI(title="WhatsApp Chatbot")


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def health():
    return {"status": "ok"}


@app.get("/webhook")
def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == config.WHATSAPP_VERIFY_TOKEN:
        return Response(content=challenge, media_type="text/plain")
    return Response(content="Forbidden", status_code=403)


@app.post("/webhook")
async def receive_webhook(request: Request, background_tasks: BackgroundTasks):
    raw_body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256")

    if not verify_signature(raw_body, signature):
        logger.warning("Invalid webhook signature")
        return Response(status_code=403)

    payload = await request.json()
    background_tasks.add_task(process_webhook_payload, payload)
    return Response(status_code=200)


async def process_webhook_payload(payload: dict):
    try:
        entries = payload.get("entry", [])
        for entry in entries:
            for change in entry.get("changes", []):
                value = change.get("value", {})
                for message in value.get("messages", []):
                    await handle_incoming_message(message)
    except Exception:
        logger.exception("Error processing webhook payload")


async def handle_incoming_message(message: dict):
    message_type = message.get("type")
    from_number = message.get("from")
    message_id = message.get("id")

    if message_type != "text":
        logger.info("Ignoring non-text message of type %s from %s", message_type, from_number)
        return

    user_text = message["text"]["body"]
    logger.info("Incoming message from %s: %s", from_number, user_text)

    await mark_as_read(message_id)

    history = get_history(from_number, limit=config.HISTORY_LIMIT)
    reply = await get_bot_reply(history, user_text)

    save_message(from_number, "user", user_text)
    save_message(from_number, "assistant", reply)

    await send_text_message(from_number, reply)
