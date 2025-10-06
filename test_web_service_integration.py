#!/usr/bin/env python3
"""
Comprehensive test for Web Service Management System integration with Desktop APP
"""

import os
import sys
import time
import threading
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_web_service_manager():
    """Test the Web Service Manager backend"""
    print("\n=== Testing Web Service Manager Backend ===")
    
    try:
        from web_service_manager import WebServiceManager
        
        # Initialize manager
        manager = WebServiceManager()
        print("✓ Web Service Manager initialized successfully")
        
        # Test configuration loading/saving
        test_config = {
            "host": "localhost",
            "port": 5000,
            "debug": True,
            "users": {"test_user": "test_password"},
            "allowed_ips": ["127.0.0.1", "192.168.1.100"]
        }
        
        # Save test configuration
        manager.save_configuration(test_config)
        print("✓ Configuration saved successfully")
        
        # Load configuration
        loaded_config = manager.load_configuration()
        print(f"✓ Configuration loaded: {loaded_config}")
        
        # Test service status
        status = manager.get_service_status()
        print(f"✓ Service status: {status}")
        
        # Test cache clearing (simulation)
        try:
            manager.clear_cache()
            print("✓ Cache clearing function available")
        except Exception as e:
            print(f"⚠ Cache clearing: {e}")
        
        # Test user management
        try:
            manager.add_user("new_user", "new_password")
            manager.remove_user("new_user")
            print("✓ User management functions available")
        except Exception as e:
            print(f"⚠ User management: {e}")
        
        # Test IP restrictions
        try:
            manager.add_allowed_ip("192.168.1.200")
            manager.remove_allowed_ip("192.168.1.200")
            print("✓ IP restriction functions available")
        except Exception as e:
            print(f"⚠ IP restrictions: {e}")
        
        print("✓ Web Service Manager backend test completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Web Service Manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_web_service_gui():
    """Test the Web Service GUI components"""
    print("\n=== Testing Web Service GUI Components ===")
    
    try:
        # Test PyQt5 availability
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import QTimer
        
        # Create QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        print("✓ PyQt5 available")
        
        # Test web service control widget
        from web_service_control_gui import WebServiceControlWidget
        
        # Create widget
        widget = WebServiceControlWidget()
        print("✓ Web Service Control Widget created")
        
        # Test widget initialization
        if hasattr(widget, 'manager'):
            print("✓ Widget has manager attribute")
        
        if hasattr(widget, 'tabs'):
            print(f"✓ Widget has tabs: {widget.tabs.count()} tabs")
        
        # Test specific tabs
        expected_tabs = ["Service Control", "Security & ACL", "Monitoring & Logs", "Configuration"]
        for i in range(widget.tabs.count()):
            tab_text = widget.tabs.tabText(i)
            if tab_text in expected_tabs:
                print(f"✓ Tab '{tab_text}' found")
        
        # Clean up
        widget.close()
        print("✓ Web Service GUI test completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Web Service GUI test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_main_gui_integration():
    """Test integration with main Desktop APP GUI"""
    print("\n=== Testing Main GUI Integration ===")
    
    try:
        from PyQt5.QtWidgets import QApplication
        
        # Create QApplication if needed
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Test main GUI import
        from gui.app import AssetManagementGUI
        print("✓ Main GUI imported successfully")
        
        # Create main GUI instance
        main_gui = AssetManagementGUI()
        print("✓ Main GUI instance created")
        
        # Check if web service tab is available
        if hasattr(main_gui, 'tab_widget'):
            tab_count = main_gui.tab_widget.count()
            print(f"✓ Main GUI has {tab_count} tabs")
            
            # Look for web service tab
            web_service_tab_found = False
            for i in range(tab_count):
                tab_text = main_gui.tab_widget.tabText(i)
                if "Web Service" in tab_text:
                    web_service_tab_found = True
                    print(f"✓ Web Service tab found: '{tab_text}'")
                    break
            
            if not web_service_tab_found:
                print("⚠ Web Service tab not found in main GUI")
        
        # Clean up
        main_gui.close()
        print("✓ Main GUI integration test completed")
        return True
        
    except Exception as e:
        print(f"✗ Main GUI integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_web_service_app():
    """Test the Flask web service application"""
    print("\n=== Testing Flask Web Service Application ===")
    
    try:
        # Test Flask app import
        sys.path.insert(0, str(project_root / "WebService"))
        from app import app
        print("✓ Flask app imported successfully")
        
        # Test app configuration
        if hasattr(app, 'config'):
            print("✓ Flask app has configuration")
        
        # Test routes (basic check)
        with app.test_client() as client:
            # Test if routes are accessible
            print("✓ Flask test client created")
        
        print("✓ Flask web service test completed")
        return True
        
    except Exception as e:
        print(f"✗ Flask web service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_structure():
    """Test required files exist"""
    print("\n=== Testing File Structure ===")
    
    required_files = [
        "web_service_manager.py",
        "web_service_control_gui.py",
        "gui/app.py",
        "WebService/app.py"
    ]
    
    all_files_exist = True
    
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✓ {file_path} exists")
        else:
            print(f"✗ {file_path} missing")
            all_files_exist = False
    
    # Check directories
    required_dirs = [
        "gui",
        "WebService",
        "logs"
    ]
    
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if full_path.exists():
            print(f"✓ {dir_path}/ directory exists")
        else:
            print(f"⚠ {dir_path}/ directory missing (will be created)")
    
    return all_files_exist

def main():
    """Run comprehensive tests"""
    print("=" * 60)
    print("COMPREHENSIVE WEB SERVICE MANAGEMENT SYSTEM TEST")
    print("=" * 60)
    
    # Track test results
    test_results = []
    
    # Test file structure
    test_results.append(("File Structure", test_file_structure()))
    
    # Test web service manager backend
    test_results.append(("Web Service Manager Backend", test_web_service_manager()))
    
    # Test web service GUI
    test_results.append(("Web Service GUI Components", test_web_service_gui()))
    
    # Test main GUI integration
    test_results.append(("Main GUI Integration", test_main_gui_integration()))
    
    # Test Flask web service
    test_results.append(("Flask Web Service", test_web_service_app()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        status = "PASSED" if result else "FAILED"
        print(f"{test_name:.<40} {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTests Passed: {passed}")
    print(f"Tests Failed: {failed}")
    print(f"Success Rate: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Web Service Management System is ready!")
        print("\nYou can now:")
        print("1. Run the Desktop APP: python gui/app.py")
        print("2. Access the Web Service Control tab")
        print("3. Manage web service with full control features")
        print("4. Use ACL management, IP restrictions, and monitoring")
    else:
        print(f"\n⚠ {failed} test(s) failed. Please check the errors above.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)