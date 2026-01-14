<#
.SYNOPSIS
    Safe bot startup script - stops existing instances before starting
#>

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Checking for running bot instances..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

$processes = @()

try {
    $wmiProcesses = Get-WmiObject Win32_Process -Filter "name='python.exe'" -ErrorAction Stop
    foreach ($proc in $wmiProcesses) {
        if ($proc.CommandLine -like "*main.py*") {
            $processes += $proc
            Write-Host "Found process: PID=$($proc.ProcessId)" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "Could not get process list via WMI: $_" -ForegroundColor Yellow
}

if ($processes.Count -gt 0) {
    Write-Host "Found $($processes.Count) running bot instances. Stopping..." -ForegroundColor Red
    foreach ($proc in $processes) {
        try {
            Stop-Process -Id $proc.ProcessId -Force -ErrorAction Stop
            Write-Host "Stopped process PID: $($proc.ProcessId)" -ForegroundColor Green
        } catch {
            Write-Host "Could not stop process PID: $($proc.ProcessId)" -ForegroundColor Yellow
        }
    }
    Write-Host "Waiting for processes to terminate..." -ForegroundColor Yellow
    Start-Sleep -Seconds 3
} else {
    Write-Host "No local bot instances found." -ForegroundColor Green
    Write-Host ""
    Write-Host "WARNING: If you get a conflict error at startup," -ForegroundColor Yellow
    Write-Host "   it means the bot is running on the remote server." -ForegroundColor Yellow
    Write-Host "   Check server 176.108.253.113 or stop the bot there." -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "Starting bot..." -ForegroundColor Green

Set-Location $PSScriptRoot

if (Test-Path ".venv\Scripts\Activate.ps1") {
    & .\.venv\Scripts\Activate.ps1
}

python main.py
