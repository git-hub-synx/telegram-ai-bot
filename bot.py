import os
import requests

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = os.environ["BOT_TOKEN"]
OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 AI Bot चालू है!\n\nमुझसे कोई भी सवाल पूछें।"
    )


async def ai_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "openrouter/free",
        "messages": [
            {
                "role": "user",
                "content": user_text
            }
        ]
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=60
        )

        result = response.json()

        if "error" in result:
            error = result["error"].get(
                "message",
                "Unknown OpenRouter error"
            )
            await update.message.reply_text(
                f"AI Error:\n{error}"
            )
            return

        choices = result.get("choices", [])

        if not choices:
            await update.message.reply_text(
                "AI ने कोई जवाब नहीं दिया।"
            )
            return

        answer = choices[0]["message"]["content"]
        await update.message.reply_text(answer)

    except Exception as e:
        await update.message.reply_text(
            f"Error: {e}"
        )


app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        ai_reply
    )
)

app.run_polling()
