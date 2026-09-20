"""
تنظیمات پروژه. مقادیر حساس از فایل .env خونده می‌شن (با python-dotenv).
قبل از اجرا، .env.example رو کپی کن به .env و مقادیر واقعی رو بذار.
"""
import os
import base64
from dotenv import load_dotenv

load_dotenv()

# --- اطلاعات حساس (از .env یا از متغیرهای محیطی پلتفرم میزبان مثل Railway) ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
API_ID = int(os.environ.get("API_ID", "0") or "0")
API_HASH = os.environ.get("API_HASH", "")
SESSION_STRING = os.environ.get("SESSION_STRING", "")

# --- تنظیمات ثابت پروژه ---
# مسیرهای پیش‌فرض داخل /app هستن (نه /root) چون روی پلتفرم‌های کانتینری مثل
# Railway معمولا یوزر non-root یا فایل‌سیستم متفاوته؛ /app همیشه قابل‌نوشتنه.
TARGET_CHANNEL = os.environ.get("TARGET_CHANNEL", "https://t.me/amir_download_chanel")
TARGET_CHANNEL_USERNAME = os.environ.get("TARGET_CHANNEL_USERNAME", "@amir_download_chanel")
DOWNLOAD_DIR = os.environ.get("DOWNLOAD_DIR", "/app/data/downloads")
COOKIES_FILE = os.environ.get("COOKIES_FILE", "/app/data/cookies.txt")

# روی پلتفرم‌هایی مثل Railway که آپلود مستقیم فایل نداری، می‌تونی محتوای
# cookies.txt رو base64 کنی و در متغیر محیطی COOKIES_B64 بذاری؛ همون اول اجرا
# اینجا decode و روی مسیر COOKIES_FILE نوشته می‌شه.
#   base64 -w0 cookies.txt   (خروجی رو در COOKIES_B64 بذار)
COOKIES_B64 = os.environ.get("COOKIES_B64", "")

os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(os.path.dirname(COOKIES_FILE) or ".", exist_ok=True)

if COOKIES_B64 and not os.path.exists(COOKIES_FILE):
    try:
        with open(COOKIES_FILE, "wb") as f:
            f.write(base64.b64decode(COOKIES_B64))
    except Exception:
        pass  # اگه decode fail بشه، بدون کوکی ادامه می‌دیم؛ هشدارش جای دیگه چاپ می‌شه

# رده‌بندی استاندارد کیفیت‌ها؛ فقط اونهایی که برای ویدیوی درخواستی موجودن نشون داده می‌شن
STANDARD_LADDER = [2160, 1440, 1080, 720, 480, 360, 240, 144]

# اگه کاربر تا این مدت (ثانیه) کیفیتی انتخاب نکنه، دانلود خودکار شروع می‌شه
AUTO_SELECT_TIMEOUT = 30

# ترتیب اولویت برای انتخاب خودکار کیفیت (اولین موردی که موجود باشه انتخاب می‌شه)
AUTO_SELECT_PRIORITY = [480, 360, 240, 720, 144, 1080]


def validate_config():
    """چک می‌کنه همه‌ی مقادیر حساس ست شده باشن؛ در غیر این‌صورت خطای واضح می‌ده."""
    missing = []
    if not TELEGRAM_TOKEN:
        missing.append("TELEGRAM_TOKEN")
    if not API_ID:
        missing.append("API_ID")
    if not API_HASH:
        missing.append("API_HASH")
    if not SESSION_STRING:
        missing.append("SESSION_STRING")
    if missing:
        raise RuntimeError(
            "متغیرهای محیطی زیر ست نشدن: " + ", ".join(missing) +
            "\nفایل .env رو بر اساس .env.example پر کن."
        )
