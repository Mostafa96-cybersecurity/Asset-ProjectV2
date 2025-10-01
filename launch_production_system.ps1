
# Production Asset Management System Launcher
# Auto-generated on create_desktop_shortcut.py

Write-Host "Starting Production Asset Management System..." -ForegroundColor Green
Write-Host "Project Location: D:\Assets-Projects\Asset-Project-Enhanced" -ForegroundColor Yellow

# Activate virtual environment
& "D:\Assets-Projects\Asset-Project-Enhanced\.venv\Scripts\Activate.ps1"

# Start the enhanced web service
Write-Host "Starting web service on http://localhost:8080..." -ForegroundColor Cyan
& "D:\Assets-Projects\Asset-Project-Enhanced\.venv\Scripts\python.exe" "D:\Assets-Projects\Asset-Project-Enhanced\enhanced_complete_web_service.py"

# Keep window open on exit
Write-Host "Press any key to exit..." -ForegroundColor Red
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
