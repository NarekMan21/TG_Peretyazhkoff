# Скрипт для отправки кода в GitHub репозиторий
# Используйте после создания репозитория на GitHub

Write-Host "=== Настройка GitHub репозитория ===" -ForegroundColor Green

# Проверка существования remote
$remoteExists = git remote get-url origin 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "Remote 'origin' уже существует: $remoteExists" -ForegroundColor Yellow
    $update = Read-Host "Обновить URL? (y/n)"
    if ($update -eq "y") {
        git remote set-url origin https://github.com/NarekMan21/TG_Peretyazhkoff.git
        Write-Host "URL обновлен" -ForegroundColor Green
    }
} else {
    Write-Host "Добавление remote 'origin'..." -ForegroundColor Cyan
    git remote add origin https://github.com/NarekMan21/TG_Peretyazhkoff.git
    Write-Host "Remote добавлен" -ForegroundColor Green
}

# Проверка текущей ветки
$currentBranch = git branch --show-current
Write-Host "Текущая ветка: $currentBranch" -ForegroundColor Cyan

# Переименование ветки в main если нужно
if ($currentBranch -ne "main") {
    Write-Host "Переименование ветки в 'main'..." -ForegroundColor Yellow
    git branch -M main
}

# Проверка статуса
Write-Host "`nПроверка статуса репозитория..." -ForegroundColor Cyan
git status

# Отправка кода
Write-Host "`nОтправка кода на GitHub..." -ForegroundColor Cyan
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Код успешно отправлен на GitHub!" -ForegroundColor Green
    Write-Host "Репозиторий: https://github.com/NarekMan21/TG_Peretyazhkoff" -ForegroundColor Cyan
} else {
    Write-Host "`n❌ Ошибка при отправке кода" -ForegroundColor Red
    Write-Host "Убедитесь, что:" -ForegroundColor Yellow
    Write-Host "1. Репозиторий создан на GitHub" -ForegroundColor Yellow
    Write-Host "2. Вы авторизованы в GitHub (gh auth login)" -ForegroundColor Yellow
    Write-Host "3. У вас есть права на запись в репозиторий" -ForegroundColor Yellow
}

