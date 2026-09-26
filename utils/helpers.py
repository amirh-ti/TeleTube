"""توابع کمکی عمومی که در چند جای پروژه استفاده می‌شن."""
import re
import base64
import requests
from urllib.parse import quote
from utils.logger import logger
from urllib.parse import urljoin

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


def make_nimbaha_link(direct_url, filename):
    """لینک نیم‌بهای آروان‌کلود رو از روی لینک مستقیم می‌سازه."""
    encoded = base64.b64encode(direct_url.encode("utf-8")).decode("ascii")
    safe_name = quote(filename)
    safe_encoded = quote(encoded, safe="")
    return f"https://nimbaha.ehsanpakar90.arvanedge.ir/file/{safe_name}?url={safe_encoded}"



def make_urldl_link(direct_url, timeout=30):
    """ لینک نیم‌بهای urldl.ir رو می‌سازه. (نسخه بهینه‌شده با یک ریکوئست) """
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    })
    try:
        logger.info(f"urldl optimized POST: {direct_url}")
        resp = session.post(
            "https://urldl.ir/add-link",
            data={"fileurl": direct_url},
            timeout=timeout,
            allow_redirects=False,
        )
        
        location = resp.headers.get("Location")
        if not location:
            logger.error(f"urldl error: No Location header. Status: {resp.status_code}")
            return None
            
        # استخراج فقط عدد (شناسه فایل) از آدرس مثلا download/561075
        match = re.search(r"\d+", location)
        if not match:
            logger.error(f"urldl error: No ID found in Location: {location}")
            return None
            
        file_id = match.group(0)
        final_link = f"https://urldl.ir/download/{file_id}"
        
        logger.info(f"urldl link successfully created: {final_link}")
        return final_link
        
    except Exception as e:
        logger.error(f"urldl exception: {e}")
        return None
