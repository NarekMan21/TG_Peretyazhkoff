@echo off
setlocal enabledelayedexpansion
REM Скрипт для безопасного запуска бота (проверяет наличие запущенных экземпляров)

echo ========================================
echo Проверка запущенных экземпляров бота...
echo ========================================

REM Получаем PID всех процессов Python, которые запускают main.py
set found=0
for /f "tokens=2 delims=," %%i in ('wmic process where "name='python.exe' and CommandLine like '%%main.py%%'" get ProcessId /format:csv 2^>nul ^| findstr /V "Node,ProcessId"') do (
    set pid=%%i
    set pid=!pid: =!
    if not "!pid!"=="" (
        echo Обнаружен запущенный экземпляр бота (PID: !pid!). Остановка...
        taskkill /PID !pid! /F >nul 2>&1
        if !errorlevel! == 0 (
            echo Процесс !pid! успешно остановлен.
        ) else (
            echo Не удалось остановить процесс !pid!.
        )
        set found=1
    )
)

REM Ждем завершения процессов
if !found! == 1 (
    echo Ожидание завершения процессов...
    timeout /t 3 /nobreak >nul
)

REM Проверяем еще раз через wmic
set found=0
for /f "tokens=2 delims=," %%i in ('wmic process where "name='python.exe' and CommandLine like '%%main.py%%'" get ProcessId /format:csv 2^>nul ^| findstr /V "Node,ProcessId"') do (
    set pid=%%i
    set pid=!pid: =!
    if not "!pid!"=="" (
        echo ВНИМАНИЕ: Процесс !pid! все еще запущен! Попытка принудительной остановки...
        taskkill /PID !pid! /F
        timeout /t 2 /nobreak >nul
        set found=1
    )
)

if !found! == 0 (
    echo Все экземпляры бота остановлены.
)

echo Запуск бота...
cd /d "%~dp0"
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    python main.py
) else (
    python main.py
)

pause
