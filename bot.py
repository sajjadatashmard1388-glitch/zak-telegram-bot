import os
import re
import logging
import requests

from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
AI_API_KEY = os.getenv("AI_API_KEY")

AI_URL = "https://openrouter.ai/api/v1/chat/completions"
AI_MODEL = "openai/gpt-4o-mini"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

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

def ask_ai(user_message: str) -> str:
    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": AI_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
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
        return result["choices"][0]["message"]["content"].strip()

    except Exception as e:
        logging.error("AI Error: %s", e)
        return "داداش مغزم یه لحظه هنگ کرد 😂 دوباره بپرس."

def contains_bad_word(text: str) -> bool:
    text = text.lower()
    return any(word.lower() in text for word in BAD_WORDS)

async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not update.message or not update.message.text:
        return

    text = update.message.text

    # اگر فحش/توهین تشخیص داده شد، زک پاسخ طنز می‌دهد.
    if contains_bad_word(text):
        prompt = f"""
کاربر در گروه این پیام را نوشته:

"{text}"

یک جواب کوتاه، خنده‌دار و دیس‌طور از طرف زک بده.
جواب تهدیدآمیز یا خشونت‌آمیز نباشد.
توهین سنگین نکن؛ بیشتر حالت کری‌خوانی بامزه داشته باشد.
"""
        await update.message.reply_text(ask_ai(prompt))
        return

    # زک فقط وقتی صدا زده شود پاسخ می‌دهد.
    if "زک" in text.lower():
        question = re.sub(r"زک", "", text, flags=re.IGNORECASE).strip()

        if not question:
            answer = "جان؟ 😎"
        else:
            answer = ask_ai(question)

        await update.message.reply_text(answer)

def main():
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN تنظیم نشده است.")

    if not AI_API_KEY:
        raise ValueError("AI_API_KEY تنظیم نشده است.")

    app = Application.builder().token(TELEGRAM_TOKEN).build()

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
