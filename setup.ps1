# This script automates the creation of a clean Python virtual environment
# and installs all required dependencies for the Network Assets Collector.

# --- Configuration ---
$VenvName = ".venv"
$PythonExecutable = "python" # Assumes 'python' is in your PATH and is Python 3.11+

# --- Script Body ---
Write-Host "Starting project setup..." -ForegroundColor Cyan

# Deactivate if currently in a virtual environment
if (Get-Command 'deactivate' -ErrorAction SilentlyContinue) {
    Write-Host "Deactivating existing virtual environment..."
    deactivate
}

# Forcefully remove the old virtual environment directory if it exists
if (Test-Path $VenvName) {
    Write-Host "Removing old virtual environment directory: $VenvName" -ForegroundColor Yellow
    Remove-Item -Recurse -Force $VenvName
    Write-Host "Old environment removed." -ForegroundColor Green
}

# Create a new virtual environment
Write-Host "Creating new virtual environment: $VenvName" -ForegroundColor Cyan
& $PythonExecutable -m venv $VenvName
if (-not $?) {
    Write-Host "Failed to create virtual environment. Please ensure Python 3.11+ is installed and in your PATH." -ForegroundColor Red
    exit 1
}

# Define the path to the activation script
$ActivateScript = Join-Path -Path $VenvName -ChildPath "Scripts\Activate.ps1"

# Activate the new environment
Write-Host "Activating the new environment..."
. $ActivateScript

# Verify activation by checking the Python executable path
$CurrentPython = (Get-Command python).Source
Write-Host "Current Python executable is: $CurrentPython"

# Install dependencies from requirements.txt
Write-Host "Installing dependencies from requirements.txt..." -ForegroundColor Cyan
pip install -r requirements.txt
if (-not $?) {
    Write-Host "Failed to install dependencies. Please check requirements.txt and your internet connection." -ForegroundColor Red
    exit 1
}

Write-Host "Setup complete! You can now run the application with 'python main.py'" -ForegroundColor Green
