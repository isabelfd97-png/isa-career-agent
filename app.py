import os
from flask import Flask, request
from telegram import Bot
import anthropic

app = Flask(__name__)

# 🔐 Leer variables de entorno (OBLIGATORIO en Render)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY")

# Validación básica para evitar crashes silenciosos
if not TELEGRAM_TOKEN:
    raise ValueError("Missing TELEGRAM_TOKEN environment variable")

if not CLAUDE_API_KEY:
    raise ValueError("Missing CLAUDE_API_KEY environment variable")

bot = Bot(token=TELEGRAM_TOKEN)
claude = anthropic.Anthropic(api_key=CLAUDE_API_KEY)


@app.route(f"/webhook/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text")

    if not text:
        return "ok"

    if text == "/start":
        bot.send_message(chat_id, "Isa 😌 Mándame las 5 ofertas y las analizo.")
        return "ok"

    prompt = f"""
Act as a strategic career market analyst for a Senior Product Designer in B2C health.
Analyze these job descriptions and extract:
- Repeated skills
- AI-related signals
- Culture signals (pressure vs stability)
- One strategic skill to prioritize
- If any job is especially strong fit

Job descriptions:
{text}
"""

    response = claude.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=800,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    analysis = response.content[0].text

    bot.send_message(chat_id, f"📊 Análisis listo:\n\n{analysis}")

    return "ok"


@app.route("/")
def home():
    return "Isa Career Agent is running."


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)