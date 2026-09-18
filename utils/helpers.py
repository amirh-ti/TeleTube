"""توابع کمکی عمومی که در چند جای پروژه استفاده می‌شن."""
import re


def extract_video_id(url):
    """شناسه ویدیوی یوتیوب رو از فرمت‌های مختلف لینک استخراج می‌کنه."""
    match = re.search(r"v=([a-zA-Z0-9_-]+)", url)
    if match:
        return match.group(1)
    match = re.search(r"youtu\.be/([a-zA-Z0-9_-]+)", url)
    if match:
        return match.group(1)
    match = re.search(r"youtube\.com/embed/([a-zA-Z0-9_-]+)", url)
    if match:
        return match.group(1)
    return None


def sanitize_filename(name):
    """کاراکترهای غیرمجاز برای نام فایل رو با _ جایگزین می‌کنه."""
    return re.sub(r'[\\/*?:"<>|]', "_", name)


def progress_bar(percent, width=12):
    """یک نوار پیشرفت متنی می‌سازه، مثلا: ####--------"""
    percent = max(0, min(100, percent))
    filled = int(width * percent / 100)
    return "#" * filled + "-" * (width - filled)


def format_size(num_bytes):
    """بایت رو به یک رشته‌ی خوانا مثل «85.3 MB» تبدیل می‌کنه. اگه None باشه
    (یعنی حجم فرمت نامعلوم بود)، None برمی‌گردونه."""
    if not num_bytes:
        return None
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"
