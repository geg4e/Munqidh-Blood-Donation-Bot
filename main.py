import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis
from dotenv import load_dotenv
from aiohttp import web

from app.database.database import init_db
from app.bot.handlers import registration, users, emergency
from app.admin import admin_handlers
from app.bot.middlewares.logging_middleware import LoggingMiddleware

load_dotenv()

async def main():
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

    # Initialize DB
    await init_db()

    # Initialize Bot and Dispatcher
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    
    # Redis for FSM
    redis = Redis(host=os.getenv("REDIS_HOST", "localhost"), port=int(os.getenv("REDIS_PORT", 6379)))
    storage = RedisStorage(redis=redis)
    
    dp = Dispatcher(storage=storage)
    
    # Register middlewares
    dp.message.middleware(LoggingMiddleware())

    # Register routers
    dp.include_router(registration.router)
    dp.include_router(users.router)
    dp.include_router(emergency.router)
    dp.include_router(admin_handlers.router)

    # Start Health Check Server (Keep-alive)
    app = web.Application()
    app.router.add_get("/", lambda r: web.Response(text="Bot is running!"))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.getenv("PORT", 8080)))
    await site.start()
    logger.info(f"Health check server started on port {os.getenv('PORT', 8080)}")

    # Start polling
    logger.info("Bot is starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot stopped!")
