"""
🤖 UzBot - Professional Telegram Bot
YouTube | Instagram | TikTok | Music Recognition | Admin Panel
"""

import asyncio
import logging
import os
import base64
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN


def setup_youtube_cookies():
    """Decode YOUTUBE_COOKIES env var (base64) and save to /app/cookies.txt"""
    cookies_b64 = os.getenv("YOUTUBE_COOKIES")
    if cookies_b64:
        try:
            cookies_data = base64.b64decode(cookies_b64).decode("utf-8")
            with open("/app/cookies.txt", "w") as f:
                f.write(cookies_data)
            logger_pre = logging.getLogger(__name__)
            logger_pre.info("✅ YouTube cookies loaded")
        except Exception as e:
            logging.getLogger(__name__).warning(f"⚠️ Failed to load YouTube cookies: {e}")
from database import Database
from middleware import UserMiddleware
from handlers import start, video, music, admin

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

db = Database()

async def main():
    setup_youtube_cookies()
    await db.init()

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Register middleware
    dp.message.middleware(UserMiddleware())
    dp.callback_query.middleware(UserMiddleware())

    # Register routers
    dp.include_router(start.router)
    dp.include_router(video.router)
    dp.include_router(music.router)
    dp.include_router(admin.router)

    logger.info("🚀 Bot ishga tushdi!")
    try:
        await dp.start_polling(bot, db=db)
    finally:
        logger.info("Bot to'xtatildi.")
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
