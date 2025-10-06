#!/usr/bin/env python3
"""
GUI Automation Integration Launcher
==================================
Launches the main GUI application with integrated 100% data collection automation.
This is the recommended way to run the application with full automation features.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

def main():
    """Launch GUI with integrated automation system"""
    print("🚀 Launching Asset Management System with 100% Data Collection Automation...")
    print("=" * 70)
    print("   📊 103-Field Database Schema")
    print("   🤖 Comprehensive Data Automation")
    print("   🔔 Advanced Notification System") 
    print("   🔄 Real-time Duplicate Detection")
    print("   📱 Desktop Notification Windows")
    print("   🎯 100% Asset Data Collection")
    print("=" * 70)
    
    try:
        # Import and run the main GUI application
        from gui.app import launch_gui
        
        print("✅ Starting Desktop Application with Full Automation...")
        print("🖥️ Main GUI will open with automation controls")
        print("🔔 Notifications will appear for automation events")
        
        # Launch the GUI application
        launch_gui()
        
    except ImportError as e:
        print(f"❌ Failed to import GUI application: {e}")
        print("⚠️ Make sure all dependencies are installed")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()