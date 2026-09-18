"""گرفتن لیست کیفیت‌های واقعی موجود برای یک ویدیو (بدون دانلود)."""
import os
from yt_dlp import YoutubeDL

from config import COOKIES_FILE, STANDARD_LADDER
from utils.logger import logger


def _base_ydl_opts():
    opts = {
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "no_check_certificate": True,
    }
    if os.path.exists(COOKIES_FILE):
        opts["cookiefile"] = COOKIES_FILE
    else:
        logger.warning(f"فایل کوکی پیدا نشد: {COOKIES_FILE} — بدون کوکی ادامه داده می‌شه.")
    return opts


def fetch_available_qualities(url):
    """
    فقط اطلاعات ویدیو رو می‌گیره (بدون دانلود) و برای هر کیفیت mp4ی موجود،
    یک تخمین حجم (بر حسب بایت) برمی‌گردونه.
    خروجی: (heights_info, title, error) که heights_info یک dict به شکل
    {height: estimated_bytes_or_None} هست.

    نکته فنی: با process=False استخراج می‌کنیم تا yt-dlp وارد فاز «انتخاب
    فرمت پیش‌فرض» نشه. بدون این کار، حتی در حالت download=False هم اگه
    ویدیو فرمت قابل‌ترکیبی نداشته باشه (مثلا به‌خاطر محدودیت سنی/منطقه‌ای یا
    نیاز به کوکی دیگه)، yt-dlp خطای "Requested format is not available" می‌ده
    در حالی که فقط داریم لیست می‌گیریم، نه دانلود.
    """
    opts = _base_ydl_opts()
    try:
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False, process=False)
    except Exception as e:
        err = str(e)
        hint = ""
        if "Sign in to confirm" in err or "not a bot" in err.lower():
            hint = "\nاحتمالا نیاز به کوکی معتبر داری."
        elif "Private video" in err or "members-only" in err.lower():
            hint = "\nاین ویدیو خصوصی/مخصوص اعضاست و با این اکانت/کوکی در دسترس نیست."
        return None, None, f"{err}{hint}"

    formats = info.get("formats", [])
    if not formats:
        # بعضی وقت‌ها process=False یک نتیجه‌ی «تنبل» برمی‌گردونه که باید یک
        # بار دیگه با process=True کامل بشه (مثلا برای بعضی پلی‌لیست‌ها).
        try:
            with YoutubeDL(opts) as ydl:
                info = ydl.process_ie_result(info, download=False)
        except Exception as e:
            return None, None, str(e)
        formats = info.get("formats", [])

    # بزرگ‌ترین فرمت mp4 برای هر ارتفاع (که همون چیزیه که موقع دانلود واقعی
    # انتخاب می‌شه)، به‌علاوه بهترین فرمت صوتی m4a برای تخمین حجم نهایی بعد
    # از merge.
    video_sizes = {}
    audio_size = None
    for f in formats:
        ext = f.get("ext", "")
        size = f.get("filesize") or f.get("filesize_approx")
        height = f.get("height")

        if height and ext == "mp4" and size:
            if height not in video_sizes or size > video_sizes[height]:
                video_sizes[height] = size

        if not height and ext == "m4a" and size:
            if audio_size is None or size > audio_size:
                audio_size = size

    if not video_sizes:
        return None, None, "هیچ فرمت mp4ی برای این ویدیو پیدا نشد. (شاید فقط فرمت‌های محدود/تصویری در دسترسه.)"

    heights_info = {
        h: (v + audio_size if audio_size else v) for h, v in video_sizes.items()
    }

    return heights_info, info.get("title", "video"), None


def filter_standard_qualities(heights_info):
    """فقط کیفیت‌های استانداردی که واقعا موجودن رو نگه می‌داره؛ اگه هیچ‌کدوم
    نبود، هرچی موجوده رو برمی‌گردونه. خروجی یک لیست از ارتفاع‌هاست."""
    offered = [h for h in STANDARD_LADDER if h in heights_info]
    return offered if offered else sorted(heights_info.keys(), reverse=True)
