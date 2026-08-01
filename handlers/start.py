"""هندلر دستور /start."""
from telegram import Update
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! لینک یوتیوب رو بفرست تا برات دانلود کنم.\n\n"
        "--------------------------------"
        "Hi! Send me the YouTube link so I can download it for you."
    )
