"""هندلر دستور /start."""
from telegram import Update
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
    "🎬 YouTube Downloader Bot\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "📥 Send your YouTube link.\n"
    "📥 لینک یوتیوب خود را ارسال کنید.\n\n"
    "⚡ Choose your preferred quality.\n"
    "⚡ کیفیت موردنظر خود را انتخاب کنید.\n\n"
    "🚀 I'll download and send the file.\n"
    "🚀 فایل را دانلود کرده و برایتان ارسال می‌کنم."
)
