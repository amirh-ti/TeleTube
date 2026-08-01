"""
حذف فایل‌های موقت (ویدیو و تامبنیل) بعد از یک تاخیر، بعد از ارسال موفق.
"""

import os
import asyncio

from utils.logger import logger


def schedule_cleanup(context, file_path, thumb_path=None, delay=30):
    """
    حذف فایل‌ها رو بعد از `delay` ثانیه زمان‌بندی می‌کنه، بدون بلاک کردن جریان
    اصلی. تسک ساخته‌شده رو نگه می‌داره تا garbage collect نشه و خطاهاش لاگ بشه.
    """

    async def delete_later():
        await asyncio.sleep(delay)
        for p in (file_path, thumb_path):
            try:
                if p and os.path.exists(p):
                    os.remove(p)
                    logger.info(f"✅ File removed successfully / فایل با موفقیت حذف شد: {p}")
            except Exception as e:
                logger.error(f"❌ Failed to remove file / خطا در حذف فایل {p}: {e}")

    task = asyncio.create_task(delete_later())
    context.application.bot_data.setdefault("cleanup_tasks", set()).add(task)
    task.add_done_callback(
        lambda t: context.application.bot_data.get("cleanup_tasks", set()).discard(t)
    )
