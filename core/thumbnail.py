"""دانلود و آماده‌سازی تامبنیل ویدیو برای پیوست به فایل ارسالی در تلگرام."""
import io
import requests
from PIL import Image

from config import DOWNLOAD_DIR
from utils.logger import logger


def prepare_thumbnail(info, video_id, unique_id):
    """
    تامبنیل ویدیو رو دانلود و برای تلگرام آماده می‌کنه (jpeg، حداکثر ۳۲۰
    پیکسل، حجم کم). اگه هر مرحله fail بشه، None برمی‌گردونه و ویدیو بدون
    تامبنیل ارسال می‌شه — این باعث fail شدن کل دانلود نمی‌شه.
    """
    thumb_url = info.get("thumbnail")
    if not thumb_url:
        thumbnails = info.get("thumbnails") or []
        if thumbnails:
            thumb_url = thumbnails[-1].get("url")
    if not thumb_url:
        return None

    try:
        resp = requests.get(thumb_url, timeout=10)
        resp.raise_for_status()
        img = Image.open(io.BytesIO(resp.content)).convert("RGB")
        img.thumbnail((320, 320))
        thumb_path = f"{DOWNLOAD_DIR}/{video_id}_{unique_id}_thumb.jpg"
        img.save(thumb_path, "JPEG", quality=85)
        return thumb_path
    except Exception as e:
        logger.warning(f"⚠️ Failed to fetch/prepare thumbnail / دریافت/آماده‌سازی تامبنیل با خطا مواجه شد: {e}")
        return None
