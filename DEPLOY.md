# Инструкция по созданию GitHub репозитория

## Шаг 1: Создайте репозиторий на GitHub

1. Откройте https://github.com/new (должен открыться автоматически)
2. Заполните форму:
   - **Repository name:** `TG_Peretyazhkoff`
   - **Description:** `Telegram bot for Peretyazhkoff - furniture reupholstery lead collection`
   - **Visibility:** Выберите **Private** (приватный)
   - **НЕ** ставьте галочки на "Add a README file", "Add .gitignore", "Choose a license"
3. Нажмите **"Create repository"**

## Шаг 2: Подключите локальный репозиторий

После создания репозитория выполните в терминале:

```bash
# Подключите удаленный репозиторий
git remote add origin https://github.com/NarekMan21/TG_Peretyazhkoff.git

# Или если remote уже существует, обновите URL
git remote set-url origin https://github.com/NarekMan21/TG_Peretyazhkoff.git

# Проверьте подключение
git remote -v
```

## Шаг 3: Отправьте код на GitHub

```bash
# Отправьте все коммиты
git push -u origin main
```

Если возникнет ошибка, возможно нужно переименовать ветку:
```bash
git branch -M main
git push -u origin main
```

## Проверка

После успешной отправки:
1. Откройте https://github.com/NarekMan21/TG_Peretyazhkoff
2. Убедитесь, что все файлы загружены
3. Проверьте, что `.env` и `*.db` файлы **НЕ** попали в репозиторий

## Важно!

⚠️ **Перед отправкой убедитесь:**
- ✅ Файл `.env` в `.gitignore`
- ✅ Файлы `*.db` в `.gitignore`
- ✅ Токен бота не попал в репозиторий

Если токен случайно попал в историю коммитов:
1. Немедленно отзовите токен через @BotFather
2. Создайте новый токен
3. Обновите `.env` файл

