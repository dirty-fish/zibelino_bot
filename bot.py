import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import load_config
from handlers import router


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    config = load_config()
    bot = Bot(token=config.bot_token)

    dispatcher = Dispatcher(storage=MemoryStorage())
    dispatcher.include_router(router)

    logging.info("ZIBELINO bot is starting in polling mode")
    try:
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()
        logging.info("ZIBELINO bot stopped")


if __name__ == "__main__":
    asyncio.run(main())
