"""Главный файл для запуска бота и веб-сервера"""
import asyncio
import logging
import sys
import os

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN, ADMIN_PORT
from database import init_db
from handlers import start, common, order, fallback
from admin.app import create_admin_app

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Главная функция запуска бота"""
    # Инициализация базы данных
    logger.info("Инициализация базы данных...")
    await init_db()
    
    # Создание бота и диспетчера
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())
    
    # Регистрация роутеров (важен порядок - более специфичные первыми)
    dp.include_router(start.router)
    dp.include_router(common.router)
    dp.include_router(order.router)
    # Fallback роутер должен быть последним
    dp.include_router(fallback.router)
    
    logger.info("Бот запущен и готов к работе!")
    
    # Запуск админ-панели в отдельном потоке
    admin_app = create_admin_app()
    
    import threading
    def run_admin():
        admin_app.run(host='0.0.0.0', port=ADMIN_PORT, debug=False)
    
    admin_thread = threading.Thread(target=run_admin, daemon=True)
    admin_thread.start()
    logger.info(f"Админ-панель запущена на http://localhost:{ADMIN_PORT}/admin")
    
    # Запуск бота
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен")

