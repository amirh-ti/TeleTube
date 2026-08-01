"""
راه‌اندازی و نگه‌داری کلاینت Telethon (اکانت شخصی که فایل رو به کانال می‌فرسته).
"""
from telethon import TelegramClient
from telethon.sessions import StringSession

from config import API_ID, API_HASH, SESSION_STRING
from utils.logger import logger

_client = None


async def start_telethon_client():
    """کلاینت Telethon رو می‌سازه، لاگین می‌کنه و برمی‌گردونه."""
    global _client
    _client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
    await _client.start()
    me = await _client.get_me()
    logger.info(f"Telethon لاگین شد به عنوان: {me.first_name}")
    return _client


def get_client():
    """کلاینت فعال رو برمی‌گردونه؛ اگه هنوز start نشده باشه خطا می‌ده."""
    if _client is None:
        raise RuntimeError("Telethon client هنوز راه‌اندازی نشده. اول start_telethon_client رو صدا بزن.")
    return _client


async def stop_telethon_client():
    if _client is not None:
        await _client.disconnect()
