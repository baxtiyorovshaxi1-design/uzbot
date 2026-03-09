"""
🤖 UzBot - Professional Telegram Bot
YouTube | Instagram | TikTok | Music Recognition | Admin Panel
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
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
