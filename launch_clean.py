#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Asset Management System - Clean Desktop Application Launcher
Minimal launcher with essential features only
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
        print("🚀 Starting Asset Management Desktop Application")
        
        # Temporarily disable some excessive enhancement systems
        import gui.app as app_module
        
        # Keep essential systems, disable duplicates
        try:
            # Keep thread-safe but disable duplicates
            app_module.EMERGENCY_FIX_AVAILABLE = False
            app_module.INSTANT_FIX_AVAILABLE = False  
            app_module.PROCESS_COLLECTION_AVAILABLE = False
            app_module.CRITICAL_THREADING_FIX_AVAILABLE = False
            print("🔧 Duplicate enhancement systems disabled for cleaner operation")
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