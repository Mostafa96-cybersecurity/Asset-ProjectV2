#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Desktop APP Launcher with 100% Data Collection Automation
================================================================
Complete Asset Management System with comprehensive data automation,
advanced notifications, and web service management.
"""

import sys
from pathlib import Path

# Add project root to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def main():
    """Launch Desktop APP with 100% Data Collection Automation"""
    
    print("🚀 LAUNCHING ASSET MANAGEMENT SYSTEM - 100% DATA COLLECTION AUTOMATION")
    print("=" * 80)
    print()
    print("🤖 100% DATA COLLECTION AUTOMATION SYSTEM")
    print("   📊 103-field database schema for complete device profiling")
    print("   🔍 WMI + SSH + SNMP comprehensive data collection")
    print("   🔔 Advanced notification system with desktop alerts")
    print("   🔄 Real-time duplicate detection and resolution")
    print("   📱 Performance monitoring with visual notifications")
    print("   🎯 Ensures 100% data collection from ALL registered devices")
    print()
    print("🌐 Web Service Management System ENABLED")
    print("   🎛️ Web Service Control tab integrated into Desktop APP")
    print("   🔧 Full service management from Desktop interface")
    print("   📁 WebService folder ready for management")
    print()
    
    try:
        # Import PyQt6 components  
        from PyQt6.QtWidgets import QApplication
        
        # Import comprehensive automation system
        print("🔄 Loading comprehensive automation components...")
        automation_available = False
        try:
            from comprehensive_data_automation import ComprehensiveDataCollector, AutomationIntegration
            from advanced_notification_system import AdvancedNotificationSystem
            automation_available = True
            print("✅ 100% Data Collection Automation: LOADED")
            print("✅ Advanced Notification System: LOADED")
            print("✅ Automation Integration: LOADED")
        except ImportError as e:
            print(f"⚠️ Automation system not available: {e}")
            print("⚠️ Running in basic mode without automation")
        
        # Import main application
        from gui.app import MainWindow
        
        # Create application
        app = QApplication(sys.argv)
        app.setApplicationName("Asset Management System - 100% Data Collection Automation")
        
        print("✅ Application initialized successfully")
        
        # Create main window with automation integration
        window = MainWindow()
        
        # Initialize automation if available
        if automation_available:
            try:
                print("🔄 Initializing automation integration...")
                
                # Create automation components
                data_collector = ComprehensiveDataCollector()
                notification_system = AdvancedNotificationSystem()
                automation_integration = AutomationIntegration(window)  # Pass window as parent_app
                
                # Attach automation to main window
                window.automation_collector = data_collector
                window.automation_notifications = notification_system
                window.automation_integration = automation_integration
                
                print("✅ Automation system integrated with main window")
                print("🔔 Desktop notifications will appear for automation events")
                
            except Exception as e:
                print(f"⚠️ Automation integration error: {e}")
                print("⚠️ Continuing without automation features")
        
        window.show()
        
        print("✅ Desktop APP launched successfully!")
        print()
        print("🎛️ AVAILABLE FEATURES:")
        print("   📊 Asset Collection and Management")
        if automation_available:
            print("   🤖 100% Data Collection Automation (NEW!)")
            print("   🔔 Advanced Notification System (NEW!)")
            print("   🔄 Real-time Duplicate Detection (NEW!)")
            print("   📱 Performance Monitoring with Alerts (NEW!)")
        print("   🌐 Web Service Control (look for the tab)")
        print("   🔐 Service Start/Stop/Restart")
        print("   👥 User Management & ACL")
        print("   📈 Real-time Monitoring & Logs")
        print("   ⚙️  Configuration Management")
        print("   🧹 Cache/Session/Connection Clearing")
        print()
        if automation_available:
            print("🎯 NEW: Look for 'Automation' tab for 100% data collection controls!")
            print("🔔 Desktop notifications will alert you to automation events!")
        print("🎯 Navigate to the 'Web Service Control' tab to manage web services!")
        print()
        print("💡 AUTOMATION FEATURES:")
        print("   • Automatically collects missing data from ALL registered devices")
        print("   • Real-time notifications for collection progress and issues")
        print("   • Duplicate detection and resolution")
        print("   • Performance monitoring with visual alerts")
        print("   • 103-field comprehensive device profiling")
        print("   • WMI, SSH, and SNMP data collection methods")
        
        # Run application
        return app.exec()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("💡 ALTERNATIVE: Try running your original launcher:")
        print("   python launch_original_desktop.py")
        return 1

if __name__ == "__main__":
    sys.exit(main())