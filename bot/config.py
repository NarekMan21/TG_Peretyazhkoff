"""Конфигурация бота"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Определяем путь к .env файлу (ищем в корне проекта или в директории bot/)
base_dir = Path(__file__).parent.parent
env_path = base_dir / '.env'
if not env_path.exists():
    env_path = Path(__file__).parent / '.env'

if env_path.exists():
    load_dotenv(env_path, override=True)
else:
    # Пробуем загрузить из текущей директории
    load_dotenv()

# Токен бота от @BotFather
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# ID чата менеджера для отправки заявок
MANAGER_CHAT_ID = os.getenv("MANAGER_CHAT_ID", "")

# ID Telegram-канала для публикации контента (формат: @channel_username или -1001234567890)
CHANNEL_ID = os.getenv("CHANNEL_ID", "")

# Порт для админ-панели
ADMIN_PORT = int(os.getenv("ADMIN_PORT", "5000"))

# Проверка CHANNEL_ID (опционально, можно закомментировать)
if not CHANNEL_ID:
    import logging
    logging.warning("CHANNEL_ID не установлен. Публикация в канал будет недоступна.")

# Путь к базе данных
DB_PATH = os.getenv("DB_PATH", "bot.db")

# Проверка обязательных параметров
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен в .env файле")

if not MANAGER_CHAT_ID:
    raise ValueError("MANAGER_CHAT_ID не установлен в .env файле")

