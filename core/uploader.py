"""
📤 Channel Uploader / ارسال‌کننده به کانال
Sends downloaded file to Telegram channel using personal account (Telethon).
ارسال فایل دانلودشده به کانال تلگرام با اکانت شخصی (Telethon).
"""

import os
import asyncio

from config import TARGET_CHANNEL
from tg.telethon_client import get_client
from utils.logger import logger


async def send_to_channel(file_path, title, thumb_path=None, status=None):
    """
    Send file with thumbnail (if available) to target channel.
    فایل رو با تامبنیل (اگه موجود باشه) به کانال هدف می‌فرسته.
    
    Args / آرگومان‌ها:
        file_path: Path to the video file / مسیر فایل ویدیو
        title: Video title / عنوان ویدیو
        thumb_path: Path to thumbnail (optional) / مسیر تامبنیل (اختیاری)
        status: Mutable dict for progress reporting / دیکشنری قابل‌تغییر برای گزارش پیشرفت
                status["percent"] gets updated during upload / توش همزمان با آپلود آپدیت می‌شه
    
    Returns / خروجی:
        message_id: ID of sent message / آیدی پیام ارسال‌شده
        None if failed / در صورت خطا
    """
    client = get_client()
    file_size = os.path.getsize(file_path)
    size_mb = file_size / (1024 * 1024)

    logger.info(f"📤 Starting upload to channel / شروع ارسال به کانال: {title} ({size_mb:.1f} MB)")

    last_logged_percent = {"value": -10}

    def progress_callback(sent_bytes, total_bytes):
        percent = int(sent_bytes / total_bytes * 100) if total_bytes else 0
        if status is not None:
            status["percent"] = percent
        if percent >= last_logged_percent["value"] + 10:
            last_logged_percent["value"] = percent
            logger.info(f"📊 Upload progress / پیشرفت آپلود {title}: {percent}%")

    try:
        message = await asyncio.wait_for(
            client.send_file(
                TARGET_CHANNEL,
                file_path,
                caption=f"📥 {title}\n📦 {size_mb:.1f} MB",
                progress_callback=progress_callback,
                part_size_kb=512,
                thumb=thumb_path,
                supports_streaming=True,
            ),
            timeout=900,  # 15 minutes / ۱۵ دقیقه
        )
        logger.info(f"✅ Upload successful / ارسال شد. Message ID: {message.id}")
        return message.id

    except asyncio.TimeoutError:
        logger.error(
            f"⏰ Upload timeout / ارسال به کانال بعد از ۱۵ دقیقه هنوز تموم نشد "
            f"(last progress / آخرین پیشرفت: {max(last_logged_percent['value'], 0)}%)."
        )
        return None

    except Exception as e:
        logger.error(f"❌ Error uploading to channel / خطا در ارسال به کانال: {e}")
        return None
