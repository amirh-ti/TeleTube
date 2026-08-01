"""
📋 Quality Fetcher / دریافت کننده کیفیت
Fetches list of actual available qualities for a video (without downloading).
گرفتن لیست کیفیت‌های واقعی موجود برای یک ویدیو (بدون دانلود).
"""

import os
from yt_dlp import YoutubeDL

from config import COOKIES_FILE, STANDARD_LADDER
from utils.logger import logger


def _base_ydl_opts():
    """
    Base yt-dlp options / تنظیمات پایه yt-dlp
    """
    opts = {
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "no_check_certificate": True,
    }
    if os.path.exists(COOKIES_FILE):
        opts["cookiefile"] = COOKIES_FILE
    else:
        logger.warning(f"⚠️ Cookie file not found / فایل کوکی پیدا نشد: {COOKIES_FILE} — continuing without cookies / بدون کوکی ادامه داده می‌شه.")
    return opts


def fetch_available_qualities(url):
    """
    Fetch available video qualities / دریافت کیفیت‌های موجود ویدیو
    
    Returns / خروجی:
        (heights, title, error_message)
        - heights: list of available qualities / لیست کیفیت‌های موجود
        - title: video title / عنوان ویدیو
        - error_message: None if success, otherwise error description
    """
    opts = _base_ydl_opts()
    
    # --- First attempt: extract info without download / تلاش اول: دریافت اطلاعات بدون دانلود ---
    try:
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False, process=False)
    except Exception as e:
        err = str(e)
        hint = ""
        if "Sign in to confirm" in err or "not a bot" in err.lower():
            hint = "\n💡 احتمالا نیاز به کوکی معتبر داری / You probably need valid cookies."
        elif "Private video" in err or "members-only" in err.lower():
            hint = "\n🔒 این ویدیو خصوصی/مخصوص اعضاست و با این اکانت/کوکی در دسترس نیست / This video is private/members-only and not accessible with this account/cookies."
        return None, None, f"❌ {err}{hint}"

    formats = info.get("formats", [])
    
    # --- Second attempt: full extraction if needed / تلاش دوم: استخراج کامل در صورت نیاز ---
    if not formats:
        # Sometimes process=False returns a "lazy" result that needs full processing
        # بعضی وقت‌ها process=False یک نتیجه‌ی «تنبل» برمی‌گردونه که باید یک بار دیگه با process=True کامل بشه
        try:
            with YoutubeDL(opts) as ydl:
                info = ydl.process_ie_result(info, download=False)
        except Exception as e:
            return None, None, f"❌ {str(e)}"
        formats = info.get("formats", [])

    # --- Extract heights from mp4 formats / استخراج ارتفاع از فرمت‌های mp4 ---
    heights = set()
    for f in formats:
        height = f.get("height")
        ext = f.get("ext", "")
        if height and ext == "mp4":
            heights.add(height)

    if not heights:
        return None, None, "⚠️ هیچ فرمت mp4ی برای این ویدیو پیدا نشد / No mp4 format found for this video. (شاید فقط فرمت‌های محدود/تصویری در دسترسه / Maybe only limited/video formats are available.)"

    return sorted(heights, reverse=True), info.get("title", "video"), None


def filter_standard_qualities(heights):
    """
    Keep only standard qualities that are actually available; if none, return whatever is available.
    فقط کیفیت‌های استانداردی که واقعا موجودن رو نگه می‌داره؛ اگه هیچ‌کدوم نبود، هرچی موجوده رو برمی‌گردونه.
    """
    offered = [h for h in STANDARD_LADDER if h in heights]
    return offered if offered else heights
