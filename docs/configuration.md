# تنظیمات (متغیرهای محیطی)

همه‌ی مقادیر داخل فایل `.env` (کنار `bot.py`) قرار می‌گیرن. نمونه در
`.env.example` هست.

| متغیر | اجباری | توضیح |
|---|---|---|
| `TELEGRAM_TOKEN` | بله | توکن ربات، از [@BotFather](https://t.me/BotFather) |
| `API_ID` | بله | از [my.telegram.org](https://my.telegram.org) → API development tools |
| `API_HASH` | بله | از همون صفحه‌ی بالا |
| `SESSION_STRING` | بله | با اسکریپت Telethon ساخته می‌شه (به `faq.md` نگاه کن) |
| `TARGET_CHANNEL` | خیر | لینک کانال مقصد؛ پیش‌فرض داخل `config.py` |
| `TARGET_CHANNEL_USERNAME` | خیر | یوزرنیم کانال با @ |
| `DOWNLOAD_DIR` | خیر | مسیر ذخیره‌ی موقت فایل‌ها |
| `COOKIES_FILE` | خیر | مسیر فایل کوکی یوتیوب |

## متغیرهای ثابت داخل `config.py`
- `STANDARD_LADDER`: رده‌بندی کیفیت‌هایی که موقع نمایش گزینه‌ها فیلتر می‌شن.
- `AUTO_SELECT_TIMEOUT`: چند ثانیه صبر کنه قبل از انتخاب خودکار کیفیت (پیش‌فرض ۳۰).
- `AUTO_SELECT_PRIORITY`: ترتیب اولویت کیفیت‌ها برای انتخاب خودکار.

این‌ها متغیر محیطی نیستن؛ اگه می‌خوای عوضشون کنی مستقیم داخل `config.py`
ویرایش کن.
