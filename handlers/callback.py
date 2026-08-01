"""
📥 Video Download Manager / مدیریت دانلود ویدیو
Handles quality selection buttons + auto-select after timeout + full orchestration:
download → upload → forward → cleanup.
"""

import os
import asyncio
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

from config import TARGET_CHANNEL, TARGET_CHANNEL_USERNAME, AUTO_SELECT_PRIORITY
from core.downloader import download_video
from core.uploader import send_to_channel
from core.cleanup import schedule_cleanup
from handlers.progress import report_progress


async def process_download(context, chat_id, message_id, user_id, quality, url):
    """
    Full process: download → upload to channel → forward to user → cleanup.
    فرآیند کامل: دانلود → آپلود به کانال → فوروارد به کاربر → پاکسازی.
    """
    bot = context.bot
    loop = asyncio.get_running_loop()

    # --- Download phase with live progress / مرحله دانلود با گزارش پیشرفت زنده ---
    dl_status = {"percent": 0}
    dl_stop = asyncio.Event()
    dl_reporter = asyncio.create_task(
        report_progress(bot, chat_id, message_id, dl_status, f"📥 Downloading {quality}p... / در حال دانلود {quality}p...", dl_stop)
    )

    def hook(d):
        if d.get("status") == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            downloaded = d.get("downloaded_bytes")
            if total and downloaded:
                dl_status["percent"] = int(downloaded / total * 100)
        elif d.get("status") == "finished":
            dl_status["percent"] = 100

    try:
        file_path, title, thumb_path, msg = await loop.run_in_executor(
            None, lambda: download_video(url, quality, progress_hook=hook)
        )
    finally:
        dl_stop.set()
        dl_reporter.cancel()

    if not file_path:
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=msg)
        return

    file_size = os.path.getsize(file_path)
    size_mb = file_size / (1024 * 1024)

    # --- Download complete / دانلود کامل شد ---
    await bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=(
            f"✅ **Download completed! / دانلود کامل شد!**\n"
            f"━─━─━─━─━─━─━─━─━\n"
            f"📥 **Title / عنوان:** `{title}`\n"
            f"📦 **Size / حجم:** `{size_mb:.1f} MB`\n"
            f"📤 **Status / وضعیت:** در حال ارسال به کانال... / Sending to channel..."
        ),
    )

    try:
        # --- Upload phase with live progress / مرحله آپلود با گزارش پیشرفت زنده ---
        up_status = {"percent": 0}
        up_stop = asyncio.Event()
        up_reporter = asyncio.create_task(
            report_progress(bot, chat_id, message_id, up_status, "📤 Uploading to channel... / در حال ارسال به کانال...", up_stop)
        )
        try:
            channel_msg_id = await send_to_channel(
                file_path, title, thumb_path=thumb_path, status=up_status
            )
        finally:
            up_stop.set()
            up_reporter.cancel()

        if not channel_msg_id:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=(
                    "❌ **Error / خطا:**\n"
                    "Timeout or error sending to channel! Check server logs.\n"
                    "خطا یا timeout در ارسال به کانال! لاگ سرور رو چک کن."
                ),
            )
            return

        # --- Forwarding to user / فوروارد به کاربر ---
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="🔄 Forwarding to you... / در حال فوروارد به شما..."
        )

        try:
            await bot.forward_message(
                chat_id=user_id,
                from_chat_id=TARGET_CHANNEL_USERNAME,
                message_id=channel_msg_id,
            )
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=(
                    f"✅ **Success! / موفق!**\n"
                    f"━─━─━─━─━─━─━─━─━\n"
                    f"📥 **Title / عنوان:** `{title}`\n"
                    f"📦 **Size / حجم:** `{size_mb:.1f} MB`\n"
                    f"🕒 **Time / زمان:** `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`\n"
                    f"━─━─━─━─━─━─━─━─━\n"
                    f"✨ File sent successfully! / فایل با موفقیت ارسال شد!"
                ),
            )
        except Exception as e:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=(
                    f"⚠️ **Partial success / موفقیت نسبی**\n"
                    f"━─━─━─━─━─━─━─━─━\n"
                    f"📥 **Title / عنوان:** `{title}`\n"
                    f"📦 **Size / حجم:** `{size_mb:.1f} MB`\n"
                    f"━─━─━─━─━─━─━─━─━\n"
                    f"📤 File uploaded to channel but forward failed.\n"
                    f"فایل در کانال آپلود شد ولی فوروارد نشد.\n\n"
                    f"📢 **Download from channel / دانلود از کانال:**\n"
                    f"`{TARGET_CHANNEL}/{channel_msg_id}`\n\n"
                    f"❌ **Error / خطا:** `{str(e)}`"
                ),
            )
    finally:
        schedule_cleanup(context, file_path, thumb_path)


async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    When user clicks on a quality button.
    وقتی کاربر روی یکی از دکمه‌های کیفیت کلیک می‌کنه.
    """
    query = update.callback_query
    await query.answer()
    parts = query.data.split("|", 2)
    if len(parts) < 3:
        return

    quality = int(parts[1])
    token = parts[2]
    chat_id = query.message.chat_id
    message_id = query.message.message_id
    user_id = query.from_user.id

    pending = context.user_data.get("pending_downloads", {})
    entry = pending.pop(token, None)
    if not entry:
        await query.edit_message_text(
            "❌ This request has expired. Please send the link again.\n"
            "این درخواست منقضی شده. لطفا لینک رو دوباره بفرست."
        )
        return

    # Cancel auto-select timer / لغو تایمر انتخاب خودکار
    for job in context.job_queue.get_jobs_by_name(f"auto_{token}"):
        job.schedule_removal()

    await query.edit_message_text(
        f"📥 Downloading {quality}p... / در حال دانلود {quality}p...\n"
        f"⏳ Please wait / لطفا صبر کن..."
    )
    await process_download(context, chat_id, message_id, user_id, quality, entry["url"])


async def auto_select_callback(context: ContextTypes.DEFAULT_TYPE):
    """
    If user doesn't select a quality within AUTO_SELECT_TIMEOUT seconds, this job runs.
    اگه کاربر تا AUTO_SELECT_TIMEOUT ثانیه کیفیتی انتخاب نکنه، این job اجرا می‌شه.
    """
    job = context.job
    data = job.data
    token = data["token"]
    chat_id = data["chat_id"]
    message_id = data["message_id"]
    user_id = data["user_id"]

    user_data = context.application.user_data.get(user_id, {})
    pending = user_data.get("pending_downloads", {})
    entry = pending.pop(token, None)
    if not entry:
        return  # User already selected / کاربر خودش قبلاً انتخاب کرده

    heights = entry.get("heights", [])
    quality = next((q for q in AUTO_SELECT_PRIORITY if q in heights), None)
    if quality is None and heights:
        quality = heights[0]
    if quality is None:
        return

    await context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=(
            f"⏰ Time is up! Auto-selecting {quality}p...\n"
            f"زمان تموم شد، خودکار {quality}p دانلود می‌شه...\n"
            f"⏳ Please wait / لطفا صبر کن..."
        ),
    )
    await process_download(context, chat_id, message_id, user_id, quality, entry["url"])
