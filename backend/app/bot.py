import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.core.config import settings
from app.bot_handlers import start
from app.db.database import async_session_maker

# Настраиваем логирование
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

async def main():
    # Инициализируем бота и диспетчер
    bot = Bot(
        token=settings.BOT_TOKEN, 
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Подключаем middleware для автоматической передачи сессии БД в хендлеры
    from aiogram_dialog import setup_dialogs # Если будешь использовать aiogram-dialog позже
    # Простой middleware для БД:
    @dp.middleware()
    async def db_session_middleware(handler, event, data):
        async with async_session_maker() as session:
            data["session"] = session
            return await handler(event, data)

    # Регистрируем роутеры (наши хендлеры)
    dp.include_router(start.router)

    logging.info("🤖 Бот запущен и готов к работе!")
    
    # Запускаем polling (получение обновлений)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())