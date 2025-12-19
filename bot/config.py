"""Конфигурация бота"""
import os
from dotenv import load_dotenv

load_dotenv()

# Токен бота от @BotFather
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# ID чата менеджера для отправки заявок
MANAGER_CHAT_ID = os.getenv("MANAGER_CHAT_ID", "")

# Порт для админ-панели
ADMIN_PORT = int(os.getenv("ADMIN_PORT", "5000"))

# Путь к базе данных
DB_PATH = os.getenv("DB_PATH", "bot.db")

# Проверка обязательных параметров
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен в .env файле")

if not MANAGER_CHAT_ID:
    raise ValueError("MANAGER_CHAT_ID не установлен в .env файле")

