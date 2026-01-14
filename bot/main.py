"""Главный файл для запуска бота и веб-сервера"""
import asyncio
import logging
import sys
import os
import platform

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


def check_running_instances():
    """Проверить наличие других запущенных экземпляров бота"""
    if platform.system() != 'Windows':
        return  # Проверка только для Windows
    
    try:
        import subprocess
        # Получаем PID текущего процесса
        current_pid = os.getpid()
        
        # Ищем все процессы Python с main.py
        result = subprocess.run(
            ['wmic', 'process', 'where', 
             "name='python.exe' and CommandLine like '%main.py%'", 
             'get', 'ProcessId', '/format:csv'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            pids = []
            for line in result.stdout.split('\n'):
                if line.strip() and 'ProcessId' in line:
                    try:
                        pid = int(line.split(',')[-1].strip())
                        if pid != current_pid:
                            pids.append(pid)
                    except (ValueError, IndexError):
                        continue
            
            if pids:
                logger.warning(
                    f"Обнаружены другие запущенные экземпляры бота (PIDs: {pids}). "
                    f"Это может вызвать конфликты. Рекомендуется остановить их перед запуском."
                )
                return True
    except Exception as e:
        logger.debug(f"Не удалось проверить запущенные экземпляры: {e}")
    
    return False


async def main():
    """Главная функция запуска бота"""
    # Проверка на множественные запуски
    if check_running_instances():
        logger.warning(
            "ВНИМАНИЕ: Обнаружены другие экземпляры бота! "
            "Используйте start_bot.bat для безопасного запуска."
        )
    
    # Предупреждение о возможном удаленном экземпляре
    logger.info(
        "Если возникнет TelegramConflictError, проверьте, не запущен ли бот "
        "на удаленном сервере (176.108.253.113). Telegram не позволяет "
        "нескольким экземплярам одного бота получать обновления одновременно."
    )
    
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
    
    # Проверка на конфликт перед запуском polling
    try:
        # Пытаемся получить информацию о боте
        me = await bot.get_me()
        logger.info(f"Подключение к боту успешно: @{me.username}")
        
        # Пытаемся сделать тестовый запрос getUpdates для проверки конфликта
        try:
            # Используем offset=-1 для проверки без получения обновлений
            updates = await bot.get_updates(offset=-1, limit=1, timeout=1)
        except Exception as check_error:
            error_str = str(check_error)
            if "Conflict" in error_str or "getUpdates" in error_str or "409" in error_str:
                logger.error(
                    "\n" + "="*60 + "\n"
                    "ОШИБКА КОНФЛИКТА: Бот уже запущен на другом экземпляре!\n"
                    "Telegram не позволяет нескольким экземплярам одного бота\n"
                    "получать обновления одновременно.\n\n"
                    "РЕШЕНИЕ:\n"
                    "1. Остановите бота на удаленном сервере (176.108.253.113):\n"
                    "   ssh user@176.108.253.113\n"
                    "   sudo systemctl stop peretiazhkoff-bot\n"
                    "   или\n"
                    "2. Используйте только один экземпляр (локальный ИЛИ удаленный)\n"
                    "="*60
                )
                await bot.session.close()
                return
            # Если другая ошибка - продолжаем (может быть временная проблема сети)
    except Exception as e:
        logger.warning(f"Не удалось проверить статус бота перед запуском: {e}")
        # Продолжаем запуск - возможно, это временная проблема
    
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
    except Exception as e:
        error_str = str(e)
        if "Conflict" in error_str or "getUpdates" in error_str or "409" in error_str:
            logger.error(
                "\n" + "="*60 + "\n"
                "ОШИБКА КОНФЛИКТА: Бот уже запущен на другом экземпляре!\n"
                "Telegram не позволяет нескольким экземплярам одного бота\n"
                "получать обновления одновременно.\n\n"
                "РЕШЕНИЕ:\n"
                "1. Остановите бота на удаленном сервере (176.108.253.113):\n"
                "   ssh user@176.108.253.113\n"
                "   sudo systemctl stop peretiazhkoff-bot\n"
                "   или\n"
                "2. Используйте только один экземпляр (локальный ИЛИ удаленный)\n"
                "="*60
            )
        raise
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен")

