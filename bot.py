import os
import re
import logging
import requests

from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    filters,
)

# =========================
# CONFIG
# =========================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
AI_API_KEY = os.getenv("AI_API_KEY")

# OpenRouter
AI_URL = "https://openrouter.ai/api/v1/chat/completions"
AI_MODEL = "openai/gpt-4o-mini"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# =========================
# BAD WORDS
# =========================

BAD_WORDS = [
    "احمق",
    "کودن",
    "بی شعور",
    "بی‌شعور",
    "خفه شو",
    "حرومزاده",
    "فحش",
    "fuck",
    "shit",
]

# =========================
# ZAK PERSONALITY
# =========================

SYSTEM_PROMPT = """
اسم تو «زک» است.

تو یک ربات تلگرامی با شخصیت باحال، باهوش، شوخ و کمی شیطون هستی.

قوانین:

1. اگر کاربر سؤال درسی پرسید، دقیق و آموزشی جواب بده.
2. اگر سؤال ریاضی، فیزیک، شیمی، زیست، زمین‌شناسی،
   فارسی، عربی، دینی یا زبان بود، مرحله‌به‌مرحله توضیح بده.
3. اگر کاربر فقط شوخی کرد، می‌توانی شوخی دوستانه کنی.
4. اگر کسی توهین کرد، عصبانی نشو.
   جواب تو باید دیس‌طور، خنده‌دار و باهوش باشد؛
   اما تهدید، خشونت، نفرت‌پراکنی یا توهین شدید نکن.
5. جواب‌ها طبیعی باشند و شبیه ربات خشک نباشند.
6. در بحث کم نیاور، ولی وارد دعوای واقعی نشو.
7. اگر چیزی را نمی‌دانی، الکی جواب نساز.
8. فارسی را طبیعی و محاوره‌ای بنویس.
9. جواب‌ها بیش از حد طولانی نباشند مگر اینکه سؤال درسی
   نیاز به توضیح کامل داشته باشد.
10. اگر کاربر گفت «زک»، منظورش تو هستی.
"""

# =========================
# AI REQUEST
# =========================

def ask_ai(user_message: str) -> str:

    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": AI_MODEL,
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        "temperature": 0.8,
        "max_tokens": 700,
    }

    try:
        response = requests.post(
            AI_URL,
            headers=headers,
            json=data,
            timeout=30
        )

        response.raise_for_status()

        result = response.json()

        return result["choices"][0]["message"]["content"]

    except Exception as e:
        logging.error(f"AI Error: {e}")
        return "داداش مغزم یه لحظه هنگ کرد 😂 دوباره بپرس."


# =========================
# BAD WORD DETECTION
# =========================

def contains_bad_word(text: str) -> bool:

    text = text.lower()

    for word in BAD_WORDS:
        if word.lower() in text:
            return True

    return False


# =========================
# MESSAGE HANDLER
# =========================

async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    text = update.message.text

    if not text:
        return

    # -------------------------
    # Check bad words
    # -------------------------

    if contains_bad_word(text):

        prompt = f"""
کاربر در گروه این پیام را نوشته:

"{text}"

یک جواب کوتاه، خنده‌دار و دیس‌طور از طرف زک بده.
جواب نباید تهدیدآمیز یا خشونت‌آمیز باشد.
خیلی هم توهین سنگین نکن؛ بیشتر حالت کری‌خوانی بامزه داشته باشد.
"""

        answer = ask_ai(prompt)

        await update.message.reply_text(answer)

        return

    # -------------------------
    # Check "زک"
    # -------------------------

    if "زک" in text.lower():

        # حذف اسم زک از متن
        question = re.sub(
            r"زک",
            "",
            text,
            flags=re.IGNORECASE
        ).strip()

        if not question:
            answer = "جان؟ 😎"

        else:
            answer = ask_ai(question)

        await update.message.reply_text(answer)

        return


# =========================
# START
# =========================

def main():

    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN تنظیم نشده!")

    if not AI_API_KEY:
        raise ValueError("AI_API_KEY تنظیم نشده!")

    app = Application.builder().token(
        TELEGRAM_TOKEN
    ).build()

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    print("ZAK is running...")

    app.run_polling()


if __name__ == "__main__":
    main()
