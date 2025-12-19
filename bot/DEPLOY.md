# Инструкция по деплою на VPS

## Информация о сервере

- **Host:** cloud-ru-vm
- **IP:** 176.108.253.113
- **User:** user1
- **SSH Key:** ~/.ssh/id_ed25519

## Подготовка сервера

### 1. Подключение к серверу

```bash
ssh cloud-ru-vm
# или
ssh user1@176.108.253.113
```

### 2. Установка зависимостей на сервере

```bash
# Обновление системы (Ubuntu/Debian)
sudo apt update && sudo apt upgrade -y

# Установка Python 3.11+ и pip
sudo apt install -y python3 python3-pip python3-venv git

# Установка nginx (для проксирования админ-панели, опционально)
sudo apt install -y nginx

# Установка supervisor (для автозапуска бота)
sudo apt install -y supervisor
```

### 3. Клонирование репозитория

```bash
cd ~
git clone https://github.com/NarekMan21/TG_Peretyazhkoff.git
cd TG_Peretyazhkoff/bot
```

### 4. Создание виртуального окружения

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Создание .env файла

```bash
nano .env
```

Содержимое `.env`:
```env
BOT_TOKEN=REMOVED_TELEGRAM_BOT_TOKEN
MANAGER_CHAT_ID=-5007917864
ADMIN_PORT=5000
DB_PATH=/home/user1/TG_Peretyazhkoff/bot/bot.db
```

Сохраните файл (Ctrl+O, Enter, Ctrl+X)

## Настройка Supervisor

### 1. Создание конфигурации supervisor

```bash
sudo nano /etc/supervisor/conf.d/peretiazhkoff-bot.conf
```

Содержимое файла:
```ini
[program:peretiazhkoff-bot]
command=/home/user1/TG_Peretyazhkoff/bot/venv/bin/python /home/user1/TG_Peretyazhkoff/bot/main.py
directory=/home/user1/TG_Peretyazhkoff/bot
user=user1
autostart=true
autorestart=true
stderr_logfile=/var/log/peretiazhkoff-bot.err.log
stdout_logfile=/var/log/peretiazhkoff-bot.out.log
environment=HOME="/home/user1",USER="user1"
```

### 2. Запуск через supervisor

```bash
# Перезагрузка конфигурации
sudo supervisorctl reread
sudo supervisorctl update

# Запуск бота
sudo supervisorctl start peretiazhkoff-bot

# Проверка статуса
sudo supervisorctl status peretiazhkoff-bot

# Просмотр логов
sudo tail -f /var/log/peretiazhkoff-bot.out.log
```

## Настройка Nginx (опционально, для внешнего доступа к админ-панели)

### 1. Создание конфигурации nginx

```bash
sudo nano /etc/nginx/sites-available/peretiazhkoff
```

Содержимое:
```nginx
server {
    listen 80;
    server_name your-domain.com;  # Замените на ваш домен или IP

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2. Активация конфигурации

```bash
sudo ln -s /etc/nginx/sites-available/peretiazhkoff /etc/nginx/sites-enabled/
sudo nginx -t  # Проверка конфигурации
sudo systemctl restart nginx
```

### 3. Настройка SSL (Let's Encrypt, опционально)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Управление ботом

### Полезные команды

```bash
# Остановить бота
sudo supervisorctl stop peretiazhkoff-bot

# Запустить бота
sudo supervisorctl start peretiazhkoff-bot

# Перезапустить бота
sudo supervisorctl restart peretiazhkoff-bot

# Просмотр логов
sudo tail -f /var/log/peretiazhkoff-bot.out.log
sudo tail -f /var/log/peretiazhkoff-bot.err.log

# Обновление кода
cd ~/TG_Peretyazhkoff
git pull
cd bot
source venv/bin/activate
pip install -r requirements.txt
sudo supervisorctl restart peretiazhkoff-bot
```

## Резервное копирование базы данных

### Создание скрипта бэкапа

```bash
nano ~/backup_bot.sh
```

Содержимое:
```bash
#!/bin/bash
BACKUP_DIR="/home/user1/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
cp /home/user1/TG_Peretyazhkoff/bot/bot.db $BACKUP_DIR/bot_$DATE.db
# Удаление старых бэкапов (старше 7 дней)
find $BACKUP_DIR -name "bot_*.db" -mtime +7 -delete
```

Сделать исполняемым:
```bash
chmod +x ~/backup_bot.sh
```

Добавить в cron (ежедневный бэкап в 3:00):
```bash
crontab -e
# Добавить строку:
0 3 * * * /home/user1/backup_bot.sh
```

## Проверка работы

1. Проверьте, что бот запущен:
   ```bash
   sudo supervisorctl status
   ```

2. Проверьте логи:
   ```bash
   sudo tail -50 /var/log/peretiazhkoff-bot.out.log
   ```

3. Проверьте админ-панель:
   - Локально на сервере: `http://localhost:5000/admin`
   - Через nginx: `http://your-domain.com/admin` или `http://176.108.253.113/admin`

4. Отправьте `/start` боту в Telegram и проверьте работу

## Решение проблем

### Бот не запускается

1. Проверьте логи: `sudo tail -50 /var/log/peretiazhkoff-bot.err.log`
2. Проверьте .env файл: `cat ~/TG_Peretyazhkoff/bot/.env`
3. Проверьте права доступа: `ls -la ~/TG_Peretyazhkoff/bot/`

### Порт занят

Если порт 5000 занят, измените `ADMIN_PORT` в `.env` файле.

### Проблемы с правами

```bash
sudo chown -R user1:user1 ~/TG_Peretyazhkoff
chmod +x ~/TG_Peretyazhkoff/bot/main.py
```

