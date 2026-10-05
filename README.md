# ZAK Telegram Bot

ربات تلگرامی آموزشی «زک».

## قابلیت‌ها
- پاسخ به پیام‌هایی که شامل «زک» باشند
- پاسخ به سوالات درسی با AI
- پاسخ طنز و دیس‌طور به توهین‌ها
- مناسب برای اجرای Railway
- دریافت Token و API Key از Environment Variables

## Railway Variables

در Railway > Variables این دو مقدار را اضافه کنید:

TELEGRAM_TOKEN=توکن ربات تلگرام
AI_API_KEY=کلید OpenRouter

## اجرای محلی

```bash
pip install -r requirements.txt
python bot.py
```

## تنظیم Telegram Privacy

برای اینکه ربات بتواند پیام‌های گروه را برای تشخیص توهین دریافت کند، در BotFather:

/setprivacy

سپس Disable را انتخاب کنید.

بعد ربات را به گروه اضافه کنید.

## نکته امنیتی

توکن تلگرام و API Key را داخل GitHub یا فایل bot.py قرار ندهید.
آن‌ها را به عنوان Environment Variable در Railway قرار دهید.
