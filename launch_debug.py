#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Asset Management System - Minimal Desktop Application Launcher (Debug Version)
This version disables some enhancements to isolate threading issues
"""

import sys
import os
from pathlib import Path

# Add project root to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def main():
    """Launch the Asset Management Desktop Application"""
    
    try:
        print("🚀 Starting Asset Management Desktop Application (Debug Mode)")
        print("⚠️ Some enhancements disabled for debugging")
        
        # Temporarily disable problematic enhancements
        import gui.app as app_module
        
        # Disable thread-safe enhancements (the real culprit)
        try:
            app_module.THREAD_SAFE_AVAILABLE = False
            print("🔧 Thread-safe enhancements disabled")
        except:
            pass
        
        # Disable instant UI fix
        try:
            app_module.INSTANT_FIX_AVAILABLE = False
            print("🔧 Instant UI fix disabled")
        except:
            pass
        
        # Disable emergency fix
        try:
            app_module.EMERGENCY_FIX_AVAILABLE = False
            print("🔧 Emergency fix disabled")
        except:
            pass
        
        # Disable critical threading fix
        try:
            app_module.CRITICAL_THREADING_FIX_AVAILABLE = False
            print("🔧 Critical threading fix disabled")
        except:
            pass
        
        # PyQt6 imports
        from PyQt6.QtWidgets import QApplication
        
        # Import the main app from gui folder
        from gui.app import MainWindow
        
        # Create QApplication
        app = QApplication(sys.argv)
        app.setApplicationName("Asset Management System")
        app.setApplicationVersion("2.0")
        
        # Set application style
        try:
            app.setStyle('Fusion')
        except:
            pass
        
        # Create and show main window
        print("📱 Creating main application window...")
        window = MainWindow()
        window.show()
        window.raise_()
        window.activateWindow()
        
        print("✅ Asset Management System started successfully")
        print("💾 Data will be saved to SQLite database (assets.db)")
        print("🌐 Web service available separately")
        print("🚫 Excel files are NOT used - Database-only system")
        
        # Run application
        return app.exec()
        
    except Exception as e:
        print(f"❌ Application startup error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())