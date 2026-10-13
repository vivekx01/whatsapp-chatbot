# WhatsApp Chatbot

A small LLM-backed chatbot that sits on a WhatsApp number via the Meta WhatsApp Cloud API.
Incoming WhatsApp messages are received through a webhook, passed to an LLM (via OpenRouter,
through LangChain) along with the sender's recent conversation history, and the reply is sent
back over WhatsApp.

## How it works

```
WhatsApp user -> Meta -> POST /webhook -> LangChain (OpenRouter LLM) -> Meta Send API -> WhatsApp user
```

- `app/main.py` — FastAPI app, webhook verification (GET) and message receiving (POST).
- `app/whatsapp_client.py` — sends messages / marks messages read via the Graph API, verifies
  Meta's webhook signature.
- `app/chatbot.py` — builds the LLM call (LangChain + OpenRouter) using the conversation history.
- `app/storage.py` — SQLite-backed per-number conversation history.
- `app/config.py` — all configuration, read from environment variables.

## Environment variables

Copy `.env.example` to `.env` and fill in:

| Variable | Where to get it |
|---|---|
| `WHATSAPP_ACCESS_TOKEN` | Meta App Dashboard → WhatsApp → API Setup |
| `WHATSAPP_PHONE_NUMBER_ID` | Same page |
| `WHATSAPP_VERIFY_TOKEN` | Any random string you choose — used during webhook setup |
| `WHATSAPP_APP_SECRET` | Meta App Dashboard → App Settings → Basic |
| `OPENROUTER_API_KEY` | openrouter.ai dashboard |
| `OPENROUTER_MODEL` | Any OpenRouter model slug, e.g. `anthropic/claude-3.5-haiku` |

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate       # Windows
pip install -r requirements.txt
cp .env.example .env          # then fill in values
uvicorn app.main:app --reload
```

Expose it with `ngrok http 8000` if you want Meta to reach your local machine for testing.

## Run with Docker

```bash
docker build -t whatsapp-chatbot .
docker run -p 8000:8000 --env-file .env -v $(pwd)/data:/data whatsapp-chatbot
```

## Deploying on Coolify

1. Push this repo to GitHub.
2. In Coolify, create a new app from the GitHub repo — it will detect the `Dockerfile` automatically.
3. Set all the environment variables from `.env.example` in Coolify's app settings.
4. Mount a persistent volume at `/data` (so conversation history survives redeploys).
5. Deploy. Coolify will give you a public HTTPS URL.

## Registering the webhook with Meta

Once deployed, go to Meta App Dashboard → WhatsApp → Configuration:

- **Callback URL**: `https://<your-coolify-domain>/webhook`
- **Verify token**: same value as `WHATSAPP_VERIFY_TOKEN` in your env
- Click "Verify and Save"
- Subscribe to the `messages` webhook field

Send a WhatsApp message to your test number — it should receive an LLM-generated reply.

## Notes

- Only plain text messages are handled; other message types (images, audio, etc.) are logged
  and ignored for now.
- History is capped at the last `HISTORY_LIMIT` messages per phone number to control prompt size
  and OpenRouter cost.
- This is a test/MVP setup — the SQLite file approach doesn't scale beyond a single container
  instance. A proper CRM/multi-tenant version would need a real database and multi-tenant data model.
