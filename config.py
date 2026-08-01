"""
تنظیمات پروژه. مقادیر حساس از فایل .env خونده می‌شن (با python-dotenv).
قبل از اجرا، .env.example رو کپی کن به .env و مقادیر واقعی رو بذار.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# --- اطلاعات حساس (از .env) ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
API_ID = int(os.environ.get("API_ID", "0") or "0")
API_HASH = os.environ.get("API_HASH", "")
SESSION_STRING = os.environ.get("SESSION_STRING", "")

# --- تنظیمات ثابت پروژه ---
TARGET_CHANNEL = os.environ.get("TARGET_CHANNEL", "")
TARGET_CHANNEL_USERNAME = os.environ.get("TARGET_CHANNEL_USERNAME", "")
DOWNLOAD_DIR = os.environ.get("DOWNLOAD_DIR", "/root/TeleTube/youtube_memory")
COOKIES_FILE = os.environ.get("COOKIES_FILE", "/root/TeleTube/cookies.txt")
# اگه کاربر تا این مدت (ثانیه) کیفیتی انتخاب نکنه، دانلود خودکار شروع می‌شه
AUTO_SELECT_TIMEOUT = int(os.environ.get("AUTO_SELECT_TIMEOUT", "15") or "30")

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# رده‌بندی استاندارد کیفیت‌ها؛ فقط اونهایی که برای ویدیوی درخواستی موجودن نشون داده می‌شن
STANDARD_LADDER = [2160, 1440, 1080, 720, 480, 360, 240, 144]

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
            "━─━─━─━─━─━─━─━─━\n"
            "❌ Configuration Error / خطای پیکربندی\n"
            "━─━─━─━─━─━─━─━─━\n"
            f"Missing variables / متغیرهای缺失: {', '.join(missing)}\n"
            "━─━─━─━─━─━─━─━─━\n"
            "💡 Solution / راه حل:\n"
            "   Copy .env.example to .env and fill in the values\n"
            "   فایل .env رو بر اساس .env.example پر کن.\n"
            "━─━─━─━─━─━─━─━─━"
                )
