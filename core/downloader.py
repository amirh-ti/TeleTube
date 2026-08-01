"""
📥 Video Downloader / دانلودر ویدیو
Downloads video with yt-dlp, format selection, audio merge, and speed optimization.
دانلود واقعی ویدیو با yt-dlp، با انتخاب فرمت، merge صدا و بهینه‌سازی سرعت.
"""

import os
import uuid
import shutil
from yt_dlp import YoutubeDL

from config import DOWNLOAD_DIR, COOKIES_FILE
from utils.helpers import extract_video_id, sanitize_filename
from core.thumbnail import prepare_thumbnail


def download_video(url, quality, progress_hook=None):
    """
    Download video with selected quality / ویدیو رو با کیفیت انتخابی دانلود می‌کنه.
    
    Returns / خروجی:
        (file_path, title, thumb_path, message)
        If download fails / اگه دانلود fail بشه:
            file_path, title, thumb_path = None
            message explains the error / message دلیل خطا رو توضیح می‌ده.
    """
    video_id = extract_video_id(url) or "video"
    unique_id = uuid.uuid4().hex[:8]
    output_template = f"{DOWNLOAD_DIR}/{video_id}_{quality}_{unique_id}.%(ext)s"

    # --- Format selector / انتخاب فرمت ---
    # One-step download: combines format selection and download in one go
    # (instead of separate extract_info + download) — eliminates one network round-trip
    # (به‌جای یک extract_info جدا برای انتخاب فرمت + یک دانلود جدا) — این یک
    # round-trip شبکه‌ی کامل رو حذف می‌کنه.
    fmt_string = (
        f"bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]"
        f"/best[ext=mp4][height<={quality}]"
        f"/best[ext=mp4]"
    )

    # --- yt-dlp options / تنظیمات yt-dlp ---
    ydl_opts = {
        "format": fmt_string,
        "outtmpl": output_template,
        "noplaylist": True,
        "merge_output_format": "mp4",
        "no_check_certificate": True,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "concurrent_fragment_downloads": 8,
        "http_chunk_size": 10 * 1024 * 1024,
        "retries": 10,
        "fragment_retries": 10,
    }

    # --- Cookie support / پشتیبانی از کوکی ---
    if os.path.exists(COOKIES_FILE):
        ydl_opts["cookiefile"] = COOKIES_FILE

    # --- Progress hook / گزارش پیشرفت ---
    if progress_hook:
        ydl_opts["progress_hooks"] = [progress_hook]

    # --- aria2c accelerator (if installed) / شتاب‌دهنده aria2c (اگه نصب باشه) ---
    # Uses multiple concurrent connections — much faster for large files
    # با چند کانکشن همزمان دانلود می‌کنه و برای فایل‌های بزرگ معمولا خیلی سریع‌تره.
    if shutil.which("aria2c"):
        ydl_opts["external_downloader"] = "aria2c"
        ydl_opts["external_downloader_args"] = {
            "aria2c": ["-x", "16", "-s", "16", "-k", "1M"]
        }

    # --- Download / دانلود ---
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
    except Exception as e:
        err = str(e)
        hint = ""
        if "Sign in to confirm" in err or "not a bot" in err.lower():
            hint = "\n💡 احتمالا نیاز به کوکی معتبر داری. فایل کوکی رو بررسی و آپدیت کن."
        elif "Requested format is not available" in err:
            hint = "\n💡 این کیفیت برای این ویدیو موجود نیست، کیفیت دیگه‌ای رو امتحان کن."
        return None, None, None, f"❌ خطا در دانلود / Download error:\n{err}{hint}"

    # --- Extract metadata / استخراج متادیتا ---
    title = info.get("title", "video")
    safe_title = sanitize_filename(title)

    # --- Find downloaded file / پیدا کردن فایل دانلود شده ---
    final_path = f"{DOWNLOAD_DIR}/{video_id}_{quality}_{unique_id}.mp4"
    if not os.path.exists(final_path):
        for ext in ["mp4", "webm", "mkv"]:
            candidate = f"{DOWNLOAD_DIR}/{video_id}_{quality}_{unique_id}.{ext}"
            if os.path.exists(candidate):
                final_path = candidate
                break

    # --- Validate file / بررسی فایل ---
    if not os.path.exists(final_path):
        return None, None, None, "❌ فایل پیدا نشد / File not found."

    file_size = os.path.getsize(final_path)
    if file_size < 100 * 1024:
        return None, None, None, "❌ فایل خیلی کوچیکه (احتمالا ناقص) / File too small (possibly incomplete)."

    # --- Prepare thumbnail / آماده‌سازی بند انگشتی ---
    thumb_path = prepare_thumbnail(info, video_id, unique_id)

    return final_path, safe_title, thumb_path, "✅ موفق / Success"
