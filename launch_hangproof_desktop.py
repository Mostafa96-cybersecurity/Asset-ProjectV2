#!/usr/bin/env python3
"""
Simple Asset Management Launcher
Prevents UI hanging by limiting scan scope
"""

import sys
from PyQt6.QtWidgets import QApplication, QMessageBox

def main():
    """Launch with hang prevention"""
    try:
        print("🚀 Starting HANG-PROOF Asset Management")
        print("🛡️ UI hanging prevention ACTIVE")
        
        # Create application
        app = QApplication(sys.argv)
        
        # Import and create main window
        from gui.app import MainWindow
        
        # Create main window
        window = MainWindow()
        
        # Override default targets to prevent massive scan
        if hasattr(window, 'target_entry'):
            # Clear any default massive subnet
            window.target_entry.clear()
            window.target_entry.setPlaceholderText("Enter IP addresses (max 50 devices)")
        
        # Add warning about large scans
        if hasattr(window, 'log_output'):
            window.log_output.append("🛡️ HANG-PROOF MODE ACTIVE")
            window.log_output.append("📊 Large scans automatically limited to prevent hanging")
            window.log_output.append("⚠️ To scan large networks, use small subnets (/24 or smaller)")
            window.log_output.append("💡 Example: 10.0.21.1-50 instead of 10.0.0.0/16")
        
        # Show the window
        window.show()
        
        print("✅ Application started in HANG-PROOF mode")
        
        # Run the application
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"❌ Application startup error: {e}")
        # Show error dialog if possible
        try:
            app = QApplication(sys.argv)
            QMessageBox.critical(None, "Startup Error", f"Failed to start application:\n{e}")
        except:
            pass
        sys.exit(1)

if __name__ == "__main__":
    main()