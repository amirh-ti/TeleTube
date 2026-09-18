"""هندلر پیام‌های متنی: لینک یوتیوب رو می‌گیره، کیفیت‌ها رو نشون می‌ده."""
import uuid
import asyncio

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import AUTO_SELECT_TIMEOUT
from core.qualities import fetch_available_qualities, filter_standard_qualities
from utils.validators import is_valid_youtube_url
from utils.helpers import format_size
from handlers.callback import auto_select_callback


async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not is_valid_youtube_url(url):
        await update.message.reply_text("لینک معتبر نیست!")
        return

    status_msg = await update.message.reply_text("در حال بررسی کیفیت‌های موجود...")

    loop = asyncio.get_running_loop()
    heights_info, title, error = await loop.run_in_executor(
        None, lambda: fetch_available_qualities(url)
    )

    if error:
        await status_msg.edit_text(f"خطا در گرفتن اطلاعات ویدیو: {error}")
        return

    offered = filter_standard_qualities(heights_info)

    # توکن کوتاه چون callback_data تلگرام محدود به ۶۴ بایته و لینک یوتیوب
    # ممکنه از این حد رد بشه
    token = uuid.uuid4().hex[:10]
    pending = context.user_data.setdefault("pending_downloads", {})
    pending[token] = {"url": url, "title": title, "heights": offered}
    if len(pending) > 50:
        pending.pop(next(iter(pending)), None)

    keyboard = []
    for h in offered:
        size_str = format_size(heights_info.get(h))
        label = f"{h}p" + (f" (~{size_str})" if size_str else "")
        keyboard.append([InlineKeyboardButton(label, callback_data=f"dl|{h}|{token}")])
    await status_msg.edit_text(
        f"«{title}»\nکیفیت رو انتخاب کن "
        f"(اگه تا {AUTO_SELECT_TIMEOUT} ثانیه انتخاب نکنی، خودکار دانلود می‌شه):",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    job_data = {
        "token": token,
        "chat_id": update.effective_chat.id,
        "message_id": status_msg.message_id,
        "user_id": update.effective_user.id,
    }
    context.job_queue.run_once(
        auto_select_callback, AUTO_SELECT_TIMEOUT, data=job_data, name=f"auto_{token}"
    )
