"""
نقطه‌ی ورود پروژه. اجرا با: python bot.py
پیش‌نیاز: فایل .env پر شده باشه (بر اساس .env.example) و ffmpeg/deno/aria2c
نصب باشن (به README.md و docs/installation.md نگاه کن).
"""
import asyncio

import uvicorn

from config import validate_config, PORT
from utils.logger import setup_logging, logger
from tg.telethon_client import start_telethon_client, stop_telethon_client
from tg.bot import build_application
from web.server import app as web_app
from web import store as link_store


async def _run_web_server():
    """وب‌سرور (لینک مستقیم + پنل مدیریت) رو توی همون event loop اجرا می‌کنه."""
    config = uvicorn.Config(web_app, host="0.0.0.0", port=PORT, log_level="warning")
    server = uvicorn.Server(config)
    await server.serve()


async def _periodic_link_purge(interval_seconds=1800):
    """هر نیم‌ساعت لینک‌های منقضی‌شده و فایل‌هاشون رو پاک می‌کنه."""
    while True:
        await asyncio.sleep(interval_seconds)
        try:
            removed = link_store.purge_expired()
            if removed:
                logger.info(f"🧹 {len(removed)} لینک منقضی‌شده پاکسازی شد.")
        except Exception as e:
            logger.error(f"خطا در پاکسازی دوره‌ای لینک‌ها: {e}")


async def main():
    validate_config()
    setup_logging()

    await start_telethon_client()

    application = build_application()
    logger.info("=" * 50)
    logger.info("🚀 Bot started successfully! / ربات با موفقیت شروع به کار کرد!")
    logger.info(f"🌐 Web server on port {PORT} / وب‌سرور روی پورت {PORT}")
    logger.info("=" * 50)

    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)

    web_task = asyncio.create_task(_run_web_server())
    purge_task = asyncio.create_task(_periodic_link_purge())

    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        logger.info("━─━─━─━─━─━─━─━─━")
        logger.info("🛑 Shutting down... / در حال خاموش شدن...")
        logger.info("━─━─━─━─━─━─━─━─━")
    finally:
        web_task.cancel()
        purge_task.cancel()
        await application.updater.stop()
        await application.stop()
        await application.shutdown()
        await stop_telethon_client()


if __name__ == "__main__":
    asyncio.run(main())
