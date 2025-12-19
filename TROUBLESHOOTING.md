# Решение проблем

## Админ-панель недоступна

### Проблема: "Page not found" при открытии http://176.108.253.113:5000/admin

**Решение:**

1. **Очистите кэш браузера:**
   - Нажмите `Ctrl + Shift + Delete`
   - Или `Ctrl + F5` для жесткой перезагрузки страницы

2. **Проверьте правильный URL:**
   - Используйте: `http://176.108.253.113:5000/admin`
   - Или: `http://176.108.253.113:5000/` (автоматически перенаправит на /admin)

3. **Проверьте статус сервиса:**
   ```bash
   ssh cloud-ru-vm "sudo systemctl status peretyazhkoff-bot"
   ```

4. **Проверьте логи:**
   ```bash
   ssh cloud-ru-vm "sudo journalctl -u peretyazhkoff-bot -n 20 --no-pager"
   ```

5. **Проверьте доступность порта:**
   ```bash
   ssh cloud-ru-vm "ss -tlnp | grep 5000"
   ```
   Должно показать: `LISTEN 0 128 0.0.0.0:5000`

6. **Перезапустите сервис:**
   ```bash
   ssh cloud-ru-vm "sudo systemctl restart peretyazhkoff-bot"
   ```

### Проверка работы админ-панели

```bash
# Проверка через curl
ssh cloud-ru-vm "curl -s http://localhost:5000/admin | grep -o '<title>.*</title>'"
# Должно вернуть: <title>Заявки - Админ-панель Перетяжкофф</title>

# Проверка внешнего доступа
curl -s http://176.108.253.113:5000/admin | grep -o '<title>.*</title>'
```

## Бот не отвечает

1. **Проверьте статус:**
   ```bash
   ssh cloud-ru-vm "sudo systemctl status peretyazhkoff-bot"
   ```

2. **Проверьте логи на ошибки:**
   ```bash
   ssh cloud-ru-vm "sudo journalctl -u peretyazhkoff-bot -n 50 --no-pager | grep -i error"
   ```

3. **Проверьте .env файл:**
   ```bash
   ssh cloud-ru-vm "cd ~/TG_Peretyazhkoff/bot && cat .env"
   ```

4. **Перезапустите:**
   ```bash
   ssh cloud-ru-vm "sudo systemctl restart peretyazhkoff-bot"
   ```

## Проблемы с базой данных

1. **Проверьте права доступа:**
   ```bash
   ssh cloud-ru-vm "ls -la ~/TG_Peretyazhkoff/bot/bot.db"
   ```

2. **Проверьте целостность:**
   ```bash
   ssh cloud-ru-vm "cd ~/TG_Peretyazhkoff/bot && ./venv/bin/python -c 'import sqlite3; conn = sqlite3.connect(\"bot.db\"); print(\"OK\"); conn.close()'"
   ```

## Проблемы с зависимостями

1. **Переустановите зависимости:**
   ```bash
   ssh cloud-ru-vm "cd ~/TG_Peretyazhkoff/bot && ./venv/bin/pip install -r requirements.txt --upgrade"
   ```

## Проблемы с firewall

Если порт 5000 заблокирован:

```bash
# UFW
ssh cloud-ru-vm "sudo ufw allow 5000/tcp"

# iptables
ssh cloud-ru-vm "sudo iptables -I INPUT -p tcp --dport 5000 -j ACCEPT"
```

## Полезные команды

```bash
# Просмотр логов в реальном времени
ssh cloud-ru-vm "sudo journalctl -u peretyazhkoff-bot -f"

# Проверка процессов
ssh cloud-ru-vm "ps aux | grep python"

# Проверка сетевых соединений
ssh cloud-ru-vm "netstat -tlnp | grep 5000"

# Проверка использования ресурсов
ssh cloud-ru-vm "top -b -n 1 | grep python"
```

