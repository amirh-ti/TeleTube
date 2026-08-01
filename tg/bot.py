"""ساخت Application ربات تلگرام و ثبت هندلرها."""
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from config import TELEGRAM_TOKEN
from handlers.start import start
from handlers.download import handle_url
from handlers.callback import button_click


def build_application():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    application.add_handler(CallbackQueryHandler(button_click, pattern="^dl\\|"))
    return application
