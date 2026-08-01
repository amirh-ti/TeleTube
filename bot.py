"""
نقطه‌ی ورود پروژه. اجرا با: python bot.py
پیش‌نیاز: فایل .env پر شده باشه (بر اساس .env.example) و ffmpeg/deno/aria2c
نصب باشن (به README.md و docs/installation.md نگاه کن).
"""
import asyncio

from config import validate_config
from utils.logger import setup_logging, logger
from tg.telethon_client import start_telethon_client, stop_telethon_client
from tg.bot import build_application


async def main():
    validate_config()
    setup_logging()

    await start_telethon_client()

    application = build_application()
    logger.info("=" * 50)
    logger.info("🚀 Bot started successfully! / ربات با موفقیت شروع به کار کرد!")
    logger.info("=" * 50)

    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)

    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        logger.info("━─━─━─━─━─━─━─━─━")
        logger.info("🛑 Shutting down... / در حال خاموش شدن...")
        logger.info("━─━─━─━─━─━─━─━─━")
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()
        await stop_telethon_client()


if __name__ == "__main__":
    asyncio.run(main())
