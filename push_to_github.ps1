# Скрипт для отправки кода на GitHub
# Замените YOUR_USERNAME на ваш GitHub username

$username = Read-Host "Введите ваш GitHub username"
$repo = "TG_Peretyazhkoff"

Write-Host "Добавляю remote repository..." -ForegroundColor Green
git remote add origin "https://github.com/$username/$repo.git"

Write-Host "Переименовываю ветку в main..." -ForegroundColor Green
git branch -M main

Write-Host "Отправляю код на GitHub..." -ForegroundColor Green
git push -u origin main

Write-Host "Готово! Репозиторий доступен по адресу:" -ForegroundColor Green
Write-Host "https://github.com/$username/$repo" -ForegroundColor Cyan

