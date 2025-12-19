# Настройка GitHub репозитория

## Создание репозитория

### Вариант 1: Через веб-интерфейс GitHub

1. Перейдите на https://github.com/new
2. Название репозитория: `TG_Peretyazhkoff`
3. Выберите **Private** (приватный)
4. **НЕ** добавляйте README, .gitignore или лицензию (они уже есть)
5. Нажмите "Create repository"

### Вариант 2: Через GitHub CLI (если установлен)

```bash
gh repo create TG_Peretyazhkoff --private --source=. --remote=origin --description="Telegram bot for Peretyazhkoff"
```

## Подключение и отправка кода

После создания репозитория выполните:

```bash
# Если репозиторий создан через веб-интерфейс
git remote add origin https://github.com/NarekMan21/TG_Peretyazhkoff.git

# Или если уже есть remote, обновите URL
git remote set-url origin https://github.com/NarekMan21/TG_Peretyazhkoff.git

# Отправьте код
git push -u origin main
```

## Проверка

После отправки проверьте:
- ✅ Файл `.env` НЕ должен быть в репозитории
- ✅ Файл `bot.db` НЕ должен быть в репозитории
- ✅ Все исходные файлы должны быть закоммичены

## Важно!

⚠️ **Никогда не коммитьте:**
- `.env` файлы с токенами
- `*.db` файлы базы данных
- `__pycache__/` директории
- Личные заметки

Все это уже добавлено в `.gitignore`.

