"""گزارش دوره‌ای پیشرفت (دانلود/آپلود) به کاربر با ادیت کردن پیام تلگرام."""
import asyncio

from utils.helpers import progress_bar


async def report_progress(bot, chat_id, message_id, status, label, stop_event):
    """
    هر ۱.۲ ثانیه status["percent"] رو چک می‌کنه و اگه تغییر معناداری کرده
    باشه، پیام رو با یک نوار پیشرفت متنی آپدیت می‌کنه. با stop_event.set()
    متوقف می‌شه.
    """
    last_sent = -100
    while not stop_event.is_set():
        await asyncio.sleep(0.5)
        percent = status.get("percent", 0)
        if percent - last_sent >= 4 or (percent >= 100 and last_sent < 100):
            last_sent = percent
            bar = progress_bar(percent)
            try:
                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=f"{label}\n{bar} {percent}%",
                )
            except Exception:
                pass
