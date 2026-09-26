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

# چت‌آیدی ادمین برای دریافت هشدار «کوکی منقضی شده». اگه خالی بمونه، هشدار
# فرستاده نمی‌شه. با @userinfobot می‌تونی چت‌آیدی خودت رو بگیری.
ADMIN_CHAT_ID = int(os.environ.get("ADMIN_CHAT_ID", "0") or "0")

# حداقل فاصله (ثانیه) بین دو هشدار کوکی منقضی، تا اسپم نشه. پیش‌فرض یک ساعت.
COOKIE_ALERT_COOLDOWN = int(os.environ.get("COOKIE_ALERT_COOLDOWN", "3600") or "3600")

# --- وب‌سرور، لینک مستقیم، و پنل مدیریت ---
# پورتی که وب‌سرور روش بالا میاد. Railway خودش PORT رو ست می‌کنه؛ روی VPS
# پیش‌فرض ۸۰۸۰ هست، هر چیزی خواستی توی .env عوضش کن.
PORT = int(os.environ.get("PORT", "8080") or "8080")

# آدرس عمومی که کاربرها باهاش به وب‌سرور دسترسی دارن، بدون اسلش آخر.
# روی Railway: همون دامنه‌ای که از "Generate Domain" می‌گیری (https://xxx.up.railway.app)
# روی VPS: مثلا http://IP:8080 یا دامنه‌ی خودت اگه ریورس‌پروکسی زدی.
# اگه خالی بمونه، تولید لینک مستقیم غیرفعال می‌مونه (فقط آپلود به کانال کار می‌کنه).
PUBLIC_BASE_URL = os.environ.get("PUBLIC_BASE_URL", "").rstrip("/")

# لینک‌های مستقیم بعد از چند ساعت منقضی و فایلشون پاک می‌شه.
LINK_TTL_HOURS = int(os.environ.get("LINK_TTL_HOURS", "24") or "24")

# یوزرنیم/پسورد ورود به پنل مدیریت (/admin). اگه پسورد خالی بمونه، پنل با
# خطای 503 غیرفعال می‌مونه — یعنی حتما قبل از استفاده باید ستش کنی.
ADMIN_PANEL_USERNAME = os.environ.get("ADMIN_PANEL_USERNAME", "admin")
ADMIN_PANEL_PASSWORD = os.environ.get("ADMIN_PANEL_PASSWORD", "")

# مسیر ذخیره‌ی متادیتای لینک‌ها و تنظیمات runtime پنل (فایل JSON ساده، نیازی
# به دیتابیس جدا نیست).
LINKS_DB_PATH = os.environ.get("LINKS_DB_PATH", "/app/data/links.json")
SETTINGS_PATH = os.environ.get("SETTINGS_PATH", "/app/data/settings.json")

os.makedirs(os.path.dirname(LINKS_DB_PATH) or ".", exist_ok=True)
os.makedirs(os.path.dirname(SETTINGS_PATH) or ".", exist_ok=True)


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
