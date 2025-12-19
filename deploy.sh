#!/bin/bash
# Скрипт для автоматического деплоя на сервер

set -e

echo "🚀 Начало деплоя бота Перетяжкофф..."

# Параметры сервера
SERVER="user1@176.108.253.113"
REMOTE_DIR="~/TG_Peretyazhkoff"

# Проверка подключения
echo "📡 Проверка подключения к серверу..."
ssh -o ConnectTimeout=5 $SERVER "echo 'Подключение успешно!'" || {
    echo "❌ Ошибка: Не удалось подключиться к серверу"
    exit 1
}

# Отправка файлов
echo "📦 Отправка файлов на сервер..."
rsync -avz --exclude='.env' --exclude='*.db' --exclude='__pycache__' --exclude='venv' \
    bot/ $SERVER:$REMOTE_DIR/bot/

# Выполнение команд на сервере
echo "⚙️  Настройка на сервере..."
ssh $SERVER << 'ENDSSH'
cd ~/TG_Peretyazhkoff/bot

# Активация виртуального окружения и установка зависимостей
if [ ! -d "venv" ]; then
    echo "Создание виртуального окружения..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Перезапуск бота через supervisor
echo "Перезапуск бота..."
sudo supervisorctl restart peretiazhkoff-bot || echo "⚠️  Supervisor не настроен. Запустите бот вручную."

echo "✅ Деплой завершен!"
ENDSSH

echo "✨ Деплой успешно завершен!"
echo "📝 Проверьте логи: ssh $SERVER 'sudo tail -f /var/log/peretiazhkoff-bot.out.log'"

