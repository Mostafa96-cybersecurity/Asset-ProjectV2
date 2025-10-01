# 🚀 ASSET MANAGEMENT SYSTEM - EASY LAUNCHER
# Run this script to start your asset management system

Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host ("=" * 78) -ForegroundColor Green
Write-Host "🏢 ASSET MANAGEMENT SYSTEM - EASY LAUNCHER" -ForegroundColor Cyan
Write-Host ("=" * 80) -ForegroundColor Green

# Check if we're in the right directory
if (-not (Test-Path "complete_asset_portal.py")) {
    Write-Host "❌ Please run this script from the Asset-Project-Enhanced directory" -ForegroundColor Red
    Write-Host "📁 Current directory: $PWD" -ForegroundColor Yellow
    Write-Host "🔄 Change to the correct directory and try again" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "🎯 Choose your preferred interface:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. 🌐 WEB PORTAL (Recommended)" -ForegroundColor Green
Write-Host "   - Modern web interface at http://localhost:5580" -ForegroundColor Gray
Write-Host "   - Real-time monitoring, search, add assets" -ForegroundColor Gray
Write-Host "   - Professional UI, works on any device" -ForegroundColor Gray
Write-Host ""
Write-Host "2. 📊 SYNC EXCEL DATA FIRST" -ForegroundColor Cyan
Write-Host "   - Load your Asset-db.xlsx into database" -ForegroundColor Gray
Write-Host "   - Required before using web portal" -ForegroundColor Gray
Write-Host ""
Write-Host "3. 🔧 CHECK SYSTEM STATUS" -ForegroundColor Magenta
Write-Host "   - See current database status" -ForegroundColor Gray
Write-Host "   - Check what data is available" -ForegroundColor Gray
Write-Host ""

$choice = Read-Host "👉 Enter your choice (1, 2, or 3)"

# Activate virtual environment
Write-Host ""
Write-Host "🔄 Activating Python environment..." -ForegroundColor Yellow
try {
    & .venv\Scripts\Activate.ps1
    Write-Host "✅ Virtual environment activated" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to activate virtual environment" -ForegroundColor Red
    Write-Host "🔧 Make sure .venv folder exists and is properly set up" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "🚀 Starting Complete Asset Portal..." -ForegroundColor Green
        Write-Host "🌐 Portal will be available at: http://localhost:5580" -ForegroundColor Cyan
        Write-Host "📊 Real-time monitoring active" -ForegroundColor Yellow
        Write-Host "⏱️  Please wait while the system initializes..." -ForegroundColor Gray
        Write-Host ""
        
        try {
            python complete_asset_portal.py
        } catch {
            Write-Host "❌ Error starting portal: $_" -ForegroundColor Red
        }
    }
    
    "2" {
        Write-Host ""
        Write-Host "📊 Syncing Excel data to database..." -ForegroundColor Green
        Write-Host "📁 Reading Asset-db.xlsx..." -ForegroundColor Yellow
        Write-Host ""
        
        try {
            python excel_to_db_sync.py
            Write-Host ""
            Write-Host "✅ Excel sync completed!" -ForegroundColor Green
            Write-Host "🚀 You can now run option 1 to start the web portal" -ForegroundColor Cyan
        } catch {
            Write-Host "❌ Error syncing Excel: $_" -ForegroundColor Red
        }
    }
    
    "3" {
        Write-Host ""
        Write-Host "🔍 Checking system status..." -ForegroundColor Green
        
        try {
            $assetCount = python -c "import sqlite3; conn=sqlite3.connect('assets.db'); print(conn.execute('SELECT COUNT(*) FROM assets').fetchone()[0]); conn.close()"
            Write-Host "📊 Assets in database: $assetCount" -ForegroundColor Cyan
            
            if ([int]$assetCount -eq 0) {
                Write-Host "⚠️  Database is empty. Run option 2 to load Excel data" -ForegroundColor Yellow
            } else {
                Write-Host "✅ Database has data. You can run option 1 for web portal" -ForegroundColor Green
            }
            
            # Check if Excel file exists
            if (Test-Path "Asset-db.xlsx") {
                Write-Host "📁 Excel file (Asset-db.xlsx): ✅ Found" -ForegroundColor Green
            } else {
                Write-Host "📁 Excel file (Asset-db.xlsx): ❌ Not found" -ForegroundColor Red
            }
            
        } catch {
            Write-Host "❌ Error checking status: $_" -ForegroundColor Red
        }
    }
    
    default {
        Write-Host "❌ Invalid choice. Please run the script again and choose 1, 2, or 3." -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "🎉 Thanks for using Asset Management System!" -ForegroundColor Green
Read-Host "Press Enter to exit"