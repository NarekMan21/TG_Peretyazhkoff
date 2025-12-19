# Инструкция по развертыванию

## Сервер

- **IP:** 176.108.253.113
- **Пользователь:** user1
- **SSH:** `ssh cloud-ru-vm`

## Расположение проекта

```
/home/user1/TG_Peretyazhkoff/bot/
```

## Управление сервисом

### Проверка статуса
```bash
ssh cloud-ru-vm "sudo systemctl status peretyazhkoff-bot"
```

### Просмотр логов
```bash
ssh cloud-ru-vm "sudo journalctl -u peretyazhkoff-bot -f"
```

### Перезапуск
```bash
ssh cloud-ru-vm "sudo systemctl restart peretyazhkoff-bot"
```

### Остановка
```bash
ssh cloud-ru-vm "sudo systemctl stop peretyazhkoff-bot"
```

### Запуск
```bash
ssh cloud-ru-vm "sudo systemctl start peretyazhkoff-bot"
```

## Доступ к админ-панели

Админ-панель доступна по адресу:
- **Локально на сервере:** http://localhost:5000/admin
- **Внешний доступ:** http://176.108.253.113:5000/admin
- **Корневой URL:** http://176.108.253.113:5000/ (автоматически перенаправляет на /admin)

⚠️ **Важно:** 
1. Порт 5000 открыт в firewall (уже настроено)
2. Для продакшена рекомендуется настроить nginx с SSL
3. Если админ-панель недоступна, проверьте логи: `sudo journalctl -u peretyazhkoff-bot -f`

## Обновление кода

```bash
# На локальной машине
cd bot
scp -r * cloud-ru-vm:~/TG_Peretyazhkoff/bot/

# На сервере
ssh cloud-ru-vm "cd ~/TG_Peretyazhkoff/bot && sudo systemctl restart peretyazhkoff-bot"
```

## Резервное копирование

База данных находится в:
```
/home/user1/TG_Peretyazhkoff/bot/bot.db
```

Для резервного копирования:
```bash
ssh cloud-ru-vm "cd ~/TG_Peretyazhkoff/bot && cp bot.db bot.db.backup.$(date +%Y%m%d_%H%M%S)"
```

## Мониторинг

Проверка работы бота:
```bash
# Статус сервиса
ssh cloud-ru-vm "sudo systemctl status peretyazhkoff-bot"

# Последние логи
ssh cloud-ru-vm "sudo journalctl -u peretyazhkoff-bot -n 50 --no-pager"

# Проверка порта
ssh cloud-ru-vm "ss -tlnp | grep 5000"
```

## Настройка firewall (если нужно)

```bash
ssh cloud-ru-vm "sudo ufw allow 5000/tcp"
# или
ssh cloud-ru-vm "sudo iptables -A INPUT -p tcp --dport 5000 -j ACCEPT"
```

