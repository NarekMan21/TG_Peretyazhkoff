# Инструкция по настройке GitHub репозитория

## Шаг 1: Создание репозитория на GitHub

1. Перейдите на https://github.com/new
2. Заполните форму:
   - **Repository name:** `TG_Peretyazhkoff`
   - **Description:** `Telegram bot for Peretyazhkoff - furniture reupholstery service with admin panel`
   - **Visibility:** ✅ **Private** (приватный)
   - **НЕ добавляйте** README, .gitignore или license (у нас уже есть файлы)
3. Нажмите "Create repository"

## Шаг 2: Подключение локального репозитория

После создания репозитория GitHub покажет инструкции. Выполните команды:

```bash
# Добавить remote (замените YOUR_USERNAME на ваш GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/TG_Peretyazhkoff.git

# Или если используете SSH:
# git remote add origin git@github.com:YOUR_USERNAME/TG_Peretyazhkoff.git

# Переименовать ветку в main (если нужно)
git branch -M main

# Отправить код на GitHub
git push -u origin main
```

## Альтернатива: Через GitHub Desktop

1. Установите GitHub Desktop: https://desktop.github.com/
2. Откройте GitHub Desktop
3. File → Add Local Repository
4. Выберите папку `D:\cursor\TELEGRAMM`
5. Publish repository → выберите "TG_Peretyazhkoff" и "Private"

## Проверка

После успешного push проверьте:
- https://github.com/YOUR_USERNAME/TG_Peretyazhkoff
- Все файлы должны быть видны
- `.env` и `bot.db` НЕ должны быть в репозитории (благодаря .gitignore)

