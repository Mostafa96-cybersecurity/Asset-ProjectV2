"""
DESKTOP SHORTCUT CREATOR - PRODUCTION ASSET MANAGEMENT SYSTEM
============================================================
Creates desktop shortcuts for easy access to the production system
"""

import os
import sys
from pathlib import Path

def create_desktop_shortcut():
    """Create a desktop shortcut for the Asset Management System"""
    
    # Get current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Desktop path
    desktop = Path.home() / "Desktop"
    
    # Create PowerShell script for launching
    launcher_script = f"""
# Production Asset Management System Launcher
# Auto-generated on {os.path.basename(__file__)}

Write-Host "Starting Production Asset Management System..." -ForegroundColor Green
Write-Host "Project Location: {current_dir}" -ForegroundColor Yellow

# Activate virtual environment
& "{current_dir}\\.venv\\Scripts\\Activate.ps1"

# Start the enhanced web service
Write-Host "Starting web service on http://localhost:8080..." -ForegroundColor Cyan
& "{current_dir}\\.venv\\Scripts\\python.exe" "{current_dir}\\enhanced_complete_web_service.py"

# Keep window open on exit
Write-Host "Press any key to exit..." -ForegroundColor Red
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
"""
    
    # Write launcher script
    launcher_path = os.path.join(current_dir, "launch_production_system.ps1")
    with open(launcher_path, 'w', encoding='utf-8') as f:
        f.write(launcher_script)
    
    # Create batch file for double-click execution
    batch_content = f"""@echo off
title Production Asset Management System
cd /d "{current_dir}"
powershell -ExecutionPolicy Bypass -File "launch_production_system.ps1"
pause
"""
    
    batch_path = os.path.join(current_dir, "Asset_Management_System.bat")
    with open(batch_path, 'w', encoding='utf-8') as f:
        f.write(batch_content)
    
    # Create desktop shortcut (Windows)
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop_shortcut = os.path.join(str(desktop), "🏢 Asset Management System.lnk")
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(desktop_shortcut)
        shortcut.Targetpath = batch_path
        shortcut.WorkingDirectory = current_dir
        shortcut.Description = "Production Asset Management System - Network Discovery & Device Management"
        shortcut.save()
        
        print(f"✅ Desktop shortcut created: {desktop_shortcut}")
        
    except ImportError:
        print("⚠️ winshell not available, creating manual shortcut instructions")
        
        # Create instructions in project directory instead
        instructions_file = os.path.join(current_dir, "PRODUCTION_SYSTEM_INSTRUCTIONS.txt")
        with open(instructions_file, 'w', encoding='utf-8') as f:
            f.write(f"""
PRODUCTION ASSET MANAGEMENT SYSTEM
=====================================

Project Location: {current_dir}

TO START THE SYSTEM:
1. Double-click: {batch_path}
   OR
2. Open PowerShell and run: {launcher_path}

WEB ACCESS:
Once started, open your browser to: http://localhost:8080

FEATURES:
- Smart Network Discovery & Device Scanning
- Real-time Asset Management 
- WMI/SSH Credential Management
- Professional Production Interface
- Database Status Monitoring
- Asset Control Features (Ping, Port Scan)
- Comprehensive Export Capabilities

SUPPORT:
All features are production-ready and fully functional.
Auto-refresh every 10 seconds for real-time updates.
""")
        
        print(f"✅ Instructions created: {instructions_file}")
    
    print(f"✅ Launcher script created: {launcher_path}")
    print(f"✅ Batch file created: {batch_path}")
    print("\n🎯 SYSTEM READY FOR PRODUCTION USE!")
    print(f"🌐 Start system by running: {batch_path}")

if __name__ == "__main__":
    create_desktop_shortcut()