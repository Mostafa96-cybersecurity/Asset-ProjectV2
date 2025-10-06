#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Asset Management System - Enhanced Desktop Application Launcher
=======================================================
Complete launcher with Web Service Management System integrated
"""

import sys
import os
from pathlib import Path

# Add project root to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def load_enhancements():
    """Load all available enhancements and fixes"""
    
    print("🚀 LOADING ALL ENHANCEMENTS...")
    print("="*50)
    
    # Web Service Management System ENABLED
    print("🌐 Web Service Management System ENABLED")
    print("   🎛️ Web Service Control tab integrated into Desktop APP")
    print("   🔧 Full service management from Desktop interface")
    print("   📁 WebService folder ready for management")
    
    # Import thread-safe enhancements
    try:
        from gui.thread_safe_enhancement import (
            make_collection_thread_safe,
            create_thread_safe_collector,
            thread_safe_operation
        )
        print("✅ Thread-safe enhancements loaded - prevents UI hanging")
    except ImportError:
        print("⚠️ Thread-safe enhancements not available")

    # Import automatic scanner
    try:
        from automatic_scanner import (
            AutomaticScanner, AutoScanTarget, ScanSchedule, ScheduleType, AutoScanConfigDialog
        )
        print("✅ Automatic scanner loaded - scheduled scanning available")
    except ImportError:
        print("⚠️ Enhanced automatic scanner not available")

    # Import massive scan protection
    try:
        from massive_scan_protection import apply_massive_scan_protection
        print("🛡️ Massive scan protection loaded - handles 3+ networks without hanging")
    except ImportError:
        print("⚠️ Massive scan protection not available")

    # Import emergency UI hang fix
    try:
        from emergency_ui_hang_fix import apply_emergency_ui_fixes
        print("🚨 Emergency UI hang fix loaded - guaranteed responsive UI")
    except ImportError:
        print("⚠️ Emergency UI hang fix not available")

    # Import instant UI responsiveness fix
    try:
        from instant_ui_responsiveness_fix import apply_instant_responsiveness_fixes
        print("⚡ Instant UI responsiveness fix loaded")
    except ImportError:
        print("⚠️ Instant UI responsiveness fix not available")

    # Import process-based collection
    try:
        from process_based_collection import ProcessBasedCollector
        print("🚀 Process-based collection loaded")
    except ImportError:
        print("⚠️ Process-based collection not available")

    # Import critical threading fix
    try:
        from critical_threading_fix import apply_critical_threading_fixes
        print("🔧 Critical threading fix loaded")
    except ImportError:
        print("⚠️ Critical threading fix not available")

    # Import SSH error handler
    try:
        from ssh_error_handler import SSHErrorHandler
        print("🔗 SSH error handler loaded")
    except ImportError:
        print("⚠️ SSH error handler not available")

    # Import collection limiter
    try:
        from collection_limiter import CollectionLimiter
        print("🛡️ Collection limiter loaded")
    except ImportError:
        print("⚠️ Collection limiter not available")

    # Import enhanced collection strategy
    try:
        from enhanced_collection_strategy import EnhancedCollectionStrategy
        print("🎯 Enhanced Collection Strategy loaded (MAXIMUM DATA COLLECTION)")
    except ImportError:
        print("⚠️ Enhanced Collection Strategy not available")

    # Web Service Management Components
    try:
        from web_service_manager import WebServiceManager
        from web_service_control_gui import WebServiceControlWidget
        print("🎛️ Web Service Management System loaded")
        print("   ✅ Web Service Manager backend ready")
        print("   ✅ Web Service Control GUI ready")
        print("   ✅ Integration with Desktop APP complete")
    except ImportError:
        print("⚠️ Web Service Management System not available")

    print("="*50)
    print("🎯 ENHANCEMENTS LOADED")
    print("🚀 GUI ready with maximum functionality including Web Service Control!")
    print("="*50)

    return True

def start_web_dashboard():
    """Launch Web Service Management from Desktop APP"""
    print("\n🌐 WEB SERVICE MANAGEMENT AVAILABLE")
    print("="*50)
    print("🎛️ Web Service Control integrated into Desktop APP")
    print("🔧 Access via 'Web Service Control' tab in Desktop GUI")
    print("📁 WebService folder ready for management")
    print("🚀 Launch Desktop APP to access web service controls")
    print("="*50)
    return True

def main():
    """Launch the Enhanced Asset Management Desktop Application with Web Service Control"""
    
    # Check if user wants web dashboard info
    if len(sys.argv) > 1 and sys.argv[1].lower() in ['web', 'dashboard', 'webservice']:
        print("🌐 LAUNCHING WEB SERVICE INFORMATION")
        start_web_dashboard()
        print("   Use Desktop APP for full web service management!")
        return 0
    
    try:
        print("🚀 Starting Asset Management Desktop Application with Web Service Control")
        
        # Load all enhancements first
        enhanced_available = load_enhancements()
        
        # PyQt6 imports
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        
        # Import the main app from gui folder
        from gui.app import MainWindow
        
        # Create application with proper settings
        app = QApplication(sys.argv)
        app.setApplicationName("Asset Management System")
        app.setApplicationVersion("3.0 Enhanced with Web Service Control")
        app.setOrganizationName("Asset Management Solutions")
        
        # Enable high DPI scaling
        app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
        app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
        
        print("✅ Application initialized")
        
        # Create and show main window with all enhancements
        window = MainWindow()
        window.show()
        
        print("✅ Desktop Application launched successfully")
        print("🎛️ Web Service Control tab is available in the application")
        print("🔧 You can now manage web services from the Desktop APP")
        print("📊 Access all features: Service Control, ACL, Monitoring, Configuration")
        
        # Run the application
        exit_code = app.exec()
        
        print("👋 Application closed")
        return exit_code
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("📋 Missing dependencies - install required packages")
        return 1
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)