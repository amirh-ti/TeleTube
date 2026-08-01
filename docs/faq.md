# سوالات متداول

## چطور SESSION_STRING بسازم؟
```python
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

api_id = 123456       # از my.telegram.org
api_hash = "..."      # از my.telegram.org

with TelegramClient(StringSession(), api_id, api_hash) as client:
    print(client.session.save())
```

اجراش کن، شماره تلفن و کد تایید رو وارد کن، رشته‌ی چاپ‌شده رو در `.env` بذار.
⚠️ این رشته معادل رمز عبور اکانتته، جایی share نکن.
## روش ساده‌تر SESSION_STRING :
دستور زیر رو توی ترمینال اجرا کنید:
```bash
python3 /opt/TeleTube/sess_st.py
```

## خطای "Sign in to confirm you're not a bot" چیه؟
یعنی کوکی نداری یا کوکی expire شده. یک فایل کوکی تازه (از یک اکانت
لاگین‌شده) export کن و مسیرش رو در `COOKIES_FILE` بذار.

## خطای "n challenge solving failed" چیه؟
یعنی به یک JS runtime نیاز داری. Deno رو نصب کن:
```bash
curl -fsSL https://deno.land/install.sh | sh
```
و مطمئن شو `yt-dlp[default]` (نه فقط `yt-dlp`) نصب شده.

## آیا دو کاربر می‌تونن همزمان استفاده کنن؟
بله. هر کاربر `pending_downloads` جدا داره، فایل‌ها نام یکتا دارن، و دانلودها
هرکدوم در thread جدا اجرا می‌شن. محدودیت واقعی فقط پهنای‌باند و CPU خود
سرورته.
