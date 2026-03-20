# Быстрый старт

## 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

## 2. Создание Telegram-бота

Создайте бота через `@BotFather` и сохраните токен в `.env`.

## 3. Подготовка чата менеджеров

Добавьте бота в нужный чат или группу и получите `chat_id`.

## 4. Создание `.env`

Создайте файл `.env` в директории `bot/`:

```env
BOT_TOKEN=your_bot_token
MANAGER_CHAT_ID=your_manager_chat_id
CHANNEL_ID=@your_channel_username
ADMIN_PORT=5000
DB_PATH=bot.db
```

## 5. Запуск

```bash
python main.py
```

## Админ-панель

После запуска откройте в браузере:
- `http://localhost:5000/admin` — список заявок
- `http://localhost:5000/admin/lead/<id>` — детали заявки

## Важно

- Не коммитьте реальные токены и chat IDs
- Если токен уже был опубликован, перевыпустите его через BotFather
