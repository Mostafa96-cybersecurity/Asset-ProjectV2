# Enhanced Network Assets Collector - Launcher Script
# This script ensures proper UTF-8 encoding for the application

Write-Host "🚀 Starting Enhanced Network Assets Collector..." -ForegroundColor Green
Write-Host "📍 Setting up environment..." -ForegroundColor Yellow

# Set UTF-8 encoding for console
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Set environment variables for proper encoding
$env:PYTHONIOENCODING = "utf-8"

# Activate virtual environment if exists
if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    Write-Host "✅ Activating virtual environment..." -ForegroundColor Green
    & .\.venv\Scripts\Activate.ps1
}

Write-Host "🛡️ Launching Enhanced Network Assets Collector..." -ForegroundColor Cyan

# Run the application
python enhanced_main.py

Write-Host "📊 Application closed." -ForegroundColor Yellow