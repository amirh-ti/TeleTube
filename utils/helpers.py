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
