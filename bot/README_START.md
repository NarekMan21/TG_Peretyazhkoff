# Инструкция по запуску бота

## Для PowerShell (рекомендуется)

Если вы используете PowerShell, используйте PowerShell скрипт:

```powershell
cd bot
.\start_bot.ps1
```

## Для CMD (Command Prompt)

Если вы используете обычную командную строку Windows:

```cmd
cd bot
start_bot.bat
```

## Для PowerShell (если хотите использовать BAT-файл)

В PowerShell BAT-файлы нужно запускать с префиксом `.\`:

```powershell
cd bot
.\start_bot.bat
```

Или через cmd:

```powershell
cd bot
cmd /c start_bot.bat
```

## Что делают скрипты?

1. ✅ Проверяют наличие запущенных экземпляров бота
2. ✅ Автоматически останавливают их (чтобы избежать конфликтов)
3. ✅ Запускают новый экземпляр бота
4. ✅ Активируют виртуальное окружение (если есть)

## Важно!

**Всегда используйте скрипты для запуска бота**, чтобы избежать ошибки:
```
TelegramConflictError: terminated by other getUpdates request
```

Не запускайте `python main.py` напрямую несколько раз!
