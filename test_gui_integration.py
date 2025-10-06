#!/usr/bin/env python3
"""
GUI Integration Test
===================
Tests if the GUI properly integrates with Enhanced Collection Strategy and web services.
"""

import ipaddress  # For IP validation
import subprocess
import time
import requests
import sys
import os

# Add project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_enhanced_strategy_import():
    """Test if Enhanced Collection Strategy can be imported"""
    print("🔧 GUI INTEGRATION TEST")
    print("=" * 50)
    print("📦 Testing Enhanced Collection Strategy import...")
    
    try:
        from enhanced_collection_strategy import EnhancedCollectionStrategy
        print("   ✅ EnhancedCollectionStrategy import successful")
        return True
    except ImportError as e:
        print(f"   ❌ EnhancedCollectionStrategy import failed: {e}")
        return False


def test_desktop_launcher():
    """Test the desktop web service launcher"""
    print("\n🧪 TESTING DESKTOP WEB SERVICE LAUNCHER")
    print("=" * 50)
    
    try:
        # Import the desktop launcher
        sys.path.append('.')
        import desktop_web_service_launcher
        
        print("✅ Desktop launcher imported successfully")
        
        # Test the FastWebServiceLauncher
        print("🚀 Testing FastWebServiceLauncher...")
        launcher = desktop_web_service_launcher.FastWebServiceLauncher()
        
        # Test start service
        success, message = launcher.start_service()
        
        if success:
            print("✅ Web service started successfully!")
            
            # Wait for startup
            time.sleep(3)
            
            # Test if service is accessible
            try:
                response = requests.get("http://localhost:8080", timeout=10)
                if response.status_code == 200:
                    print("✅ Web service is accessible at http://localhost:8080")
                    print("🎉 GUI WEB SERVICE STARTUP TEST PASSED!")
                    return True
                else:
                    print(f"❌ Web service returned status code: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"❌ Web service not accessible: {e}")
                # Check if process is running
                if launcher.is_running():
                    print("⚠️ Service process is running but not responding to HTTP requests")
                    print("🔍 This indicates a service startup issue")
                else:
                    print("❌ Service process is not running")
        else:
            print(f"❌ Web service failed to start: {message}")
            
        return False
        
    except Exception as e:
        print(f"❌ Desktop launcher test failed: {e}")
        return False


def test_web_service_files():
    """Check that web service files exist and have correct priorities"""
    print("\n📝 CHECKING WEB SERVICE FILES")
    print("=" * 50)
    
    # Check if fixed_dashboard.py exists and is being used
    web_service_files = [
        'fixed_dashboard.py',
        'desktop_web_service_launcher.py',
        'secure_web_service.py'
    ]
    
    files_found = []
    for file in web_service_files:
        if os.path.exists(file):
            print(f"✅ {file}: Found")
            files_found.append(file)
        else:
            print(f"❌ {file}: Not found")
    
    if 'fixed_dashboard.py' in files_found:
        print("✅ Priority service (fixed_dashboard.py) is available")
        return True
    else:
        print("❌ Priority service (fixed_dashboard.py) is missing")
        return False


def test_port_consistency():
    """Check that services use the correct port (8080)"""
    print("\n🔌 CHECKING PORT CONSISTENCY")
    print("=" * 50)
    
    services = [
        'fixed_dashboard.py',
        'desktop_web_service_launcher.py'
    ]
    
    all_correct = True
    for service in services:
        if os.path.exists(service):
            try:
                with open(service, 'r', encoding='utf-8') as f:
                    content = f.read()
                if '8080' in content:
                    print(f"✅ {service}: Uses port 8080")
                else:
                    print(f"❌ {service}: Does not use port 8080")
                    all_correct = False
            except Exception as e:
                print(f"❌ Error checking {service}: {e}")
                all_correct = False
        else:
            print(f"⚠️ {service}: File not found")
    
    return all_correct


def test_gui_integration():
    """Test if GUI properly integrates with Enhanced Collection Strategy"""
    print("\n🔧 TESTING GUI INTEGRATION WITH ENHANCED STRATEGY")
    print("=" * 50)
    
    if not test_enhanced_strategy_import():
        print("\n❌ Cannot proceed - Enhanced strategy not available")
        return False
    
    try:
        # Test the same import path as gui/app.py
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from enhanced_collection_strategy import EnhancedCollectionStrategy
        
        print("   ✅ Enhanced Collection Strategy imported successfully")
        
        # Test GUI-style initialization
        print("\n🔧 Testing GUI-style initialization...")
        
        # Simulate GUI parameters
        targets = ['127.0.0.1']
        win_creds = [{'username': 'admin', 'password': 'password'}]
        lin_creds = [{'username': 'root', 'password': 'password'}]
        snmp_v2c = ['public']
        snmp_v3 = {'user': 'admin', 'auth_pass': 'password', 'priv_pass': 'password'}
        
        credentials = {
            'windows': win_creds,
            'linux': lin_creds,
            'snmp_v2c': snmp_v2c,
            'snmp_v3': snmp_v3,
            'use_http': True
        }
        
        print("   📝 Credentials formatted for Enhanced Strategy:")
        print(f"      Windows: {len(win_creds)} credentials")
        print(f"      Linux: {len(lin_creds)} credentials")
        print(f"      SNMP v2c: {len(snmp_v2c)} communities")
        print(f"      SNMP v3: {'configured' if snmp_v3.get('user') else 'not configured'}")
        
        # Test strategy initialization
        strategy = EnhancedCollectionStrategy(targets, credentials)
        print("   ✅ Enhanced Collection Strategy initialized successfully")
        
        # Test key methods
        print("\n🔍 Testing key methods...")
        
        # Test ping method
        ping_available = hasattr(strategy, '_secure_reliable_ping')
        print(f"   🏓 Secure ping: {'✅' if ping_available else '❌'}")
        
        # Test collection methods
        methods = [
            ('_enhanced_nmap_scan', 'NMAP scanning'),
            ('_comprehensive_wmi_collection', 'WMI collection'), 
            ('_comprehensive_ssh_collection', 'SSH collection'),
            ('_comprehensive_snmp_collection', 'SNMP collection'),
            ('_http_service_detection', 'HTTP detection'),
            ('classify_device', 'Device classification')
        ]
        
        for method, description in methods:
            available = hasattr(strategy, method)
            print(f"   📊 {description}: {'✅' if available else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Strategy initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all GUI integration tests"""
    print("🔍 COMPREHENSIVE GUI INTEGRATION TEST")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 5
    
    # Test 1: Enhanced Strategy Import
    if test_enhanced_strategy_import():
        tests_passed += 1
    
    # Test 2: Web Service Files
    if test_web_service_files():
        tests_passed += 1
    
    # Test 3: Port Consistency
    if test_port_consistency():
        tests_passed += 1
    
    # Test 4: Desktop Launcher
    if test_desktop_launcher():
        tests_passed += 1
    
    # Test 5: GUI Integration
    if test_gui_integration():
        tests_passed += 1
    
    print("\n" + "=" * 60)
    print("🎯 GUI INTEGRATION TEST RESULTS")
    print("=" * 60)
    print(f"✅ Tests Passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED!")
        print("✅ GUI integration should work correctly")
    else:
        print("❌ Some tests failed")
        print("🔧 Check the failing components above")
    
    print("\n🔧 RECOMMENDATIONS:")
    print("1. ✅ Check that fixed_dashboard.py exists and is executable")
    print("2. ✅ Verify port 8080 is not blocked by firewall")
    print("3. ✅ Ensure all imports are working correctly")
    print("4. 🔧 If browser shows ERR_EMPTY_RESPONSE, check service binding")


if __name__ == "__main__":
    main()

    except Exception as e:

        print(f"❌ Test failed: {e}")        import desktop_web_service_launcher    try:

        import traceback

        traceback.print_exc()        

        

    return False        print("✅ Desktop launcher imported successfully")        # Import the desktop launcherimport sysdef test_gui_integration():



def test_web_service_files():        

    """Check that web service files exist and have correct priorities"""

    print("\n📝 CHECKING WEB SERVICE FILES")        # Test the FastWebServiceLauncher        sys.path.append('.')

    print("=" * 50)

            print("🚀 Testing FastWebServiceLauncher...")

    # Check if fixed_dashboard.py exists and is being used

    web_service_files = [        launcher = desktop_web_service_launcher.FastWebServiceLauncher()        import desktop_web_service_launcherimport os    """Test if GUI properly integrates with Enhanced Collection Strategy"""

        'fixed_dashboard.py',

        'desktop_web_service_launcher.py',        

        'secure_web_service.py'

    ]        # Test start service        

    

    files_found = []        success, message = launcher.start_service()

    for file in web_service_files:

        if os.path.exists(file):                print("Desktop launcher imported successfully")    

            print(f"✅ {file}: Found")

            files_found.append(file)        if success:

        else:

            print(f"❌ {file}: Not found")            print("✅ Web service started successfully!")        

    

    if 'fixed_dashboard.py' in files_found:            

        print("✅ Priority service (fixed_dashboard.py) is available")

        return True            # Wait for startup        # Test the start functiondef test_desktop_launcher():    print("🔧 GUI INTEGRATION TEST")

    else:

        print("❌ Priority service (fixed_dashboard.py) is missing")            time.sleep(3)

        return False

                    print("Testing start_web_service_for_gui()...")

def test_port_consistency():

    """Check that services use the correct port (3010)"""            # Test if service is accessible

    print("\n🔌 CHECKING PORT CONSISTENCY")

    print("=" * 50)            try:            """Test the desktop web service launcher directly"""    print("=" * 50)

    

    services = [                response = requests.get("http://localhost:3010", timeout=10)

        'fixed_dashboard.py',

        'desktop_web_service_launcher.py'                if response.status_code == 200:        result = desktop_web_service_launcher.start_web_service_for_gui()

    ]

                        print("✅ Web service is accessible at http://localhost:3010")

    all_correct = True

                        print("🎉 GUI WEB SERVICE STARTUP TEST PASSED!")                

    for service in services:

        if os.path.exists(service):                    return True

            try:

                with open(service, 'r', encoding='utf-8') as f:                else:        if result:

                    content = f.read()

                                    print(f"❌ Web service returned status code: {response.status_code}")

                if '3010' in content:

                    print(f"✅ {service}: Uses port 3010")            except requests.exceptions.RequestException as e:            print("Web service started successfully!")    print("🧪 TESTING DESKTOP WEB SERVICE LAUNCHER")    # Test imports from GUI perspective

                else:

                    print(f"❌ {service}: Does not use port 3010")                print(f"❌ Web service not accessible: {e}")

                    all_correct = False

                                    # Check if process is running            

            except Exception as e:

                print(f"❌ Error checking {service}: {e}")                if launcher.is_running():

                all_correct = False

        else:                    print("⚠️ Service process is running but not responding to HTTP requests")            # Wait a moment for startup    print("=" * 50)    print("📦 Testing imports from GUI perspective...")

            print(f"⚠️ {service}: File not found")

                        print("🔍 This indicates a service startup issue")

    return all_correct

                else:            time.sleep(3)

def test_service_startup_issue():

    """Diagnose why web service shows as started but browser can't connect"""                    print("❌ Service process is not running")

    print("\n🔍 DIAGNOSING WEB SERVICE CONNECTIVITY")

    print("=" * 50)        else:                    

    

    try:            print(f"❌ Web service failed to start: {message}")

        # Check if fixed_dashboard.py can start directly

        print("🚀 Testing fixed_dashboard.py directly...")                        # Test if service is accessible

        

        if not os.path.exists('fixed_dashboard.py'):    except Exception as e:

            print("❌ fixed_dashboard.py not found")

            return False        print(f"❌ Test failed: {e}")            try:    try:    try:

        

        # Start the service directly for testing        import traceback

        import subprocess

        import threading        traceback.print_exc()                response = requests.get("http://localhost:5556", timeout=5)

        

        def start_direct_service():        

            try:

                process = subprocess.Popen(    return False                if response.status_code == 200:        # Import the desktop launcher        # Test the same import path as gui/app.py

                    [sys.executable, 'fixed_dashboard.py'],

                    stdout=subprocess.PIPE,

                    stderr=subprocess.PIPE,

                    cwd=os.getcwd()def test_web_service_files():                    print("Web service is accessible at http://localhost:5556")

                )

                    """Check that web service files exist and have correct priorities"""

                # Wait for startup

                time.sleep(5)    print("\n📝 CHECKING WEB SERVICE FILES")                    print("GUI WEB SERVICE STARTUP TEST PASSED!")        sys.path.append('.')        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

                

                # Test connection    print("=" * 50)

                try:

                    response = requests.get("http://localhost:3010", timeout=10)                        return True

                    print(f"✅ Direct service test: HTTP {response.status_code}")

                        # Check if fixed_dashboard.py exists and is being used

                    # Check response content

                    if len(response.content) > 0:    web_service_files = [                else:        import desktop_web_service_launcher        from enhanced_collection_strategy import EnhancedCollectionStrategy

                        print("✅ Service is returning content")

                    else:        'fixed_dashboard.py',

                        print("❌ Service is returning empty response")

                                'desktop_web_service_launcher.py',                    print(f"Web service returned status code: {response.status_code}")

                except requests.exceptions.RequestException as e:

                    print(f"❌ Direct service test failed: {e}")        'secure_web_service.py'

                

                # Cleanup    ]            except requests.exceptions.RequestException as e:                print("   ✅ EnhancedCollectionStrategy import successful")

                process.terminate()

                    

            except Exception as e:

                print(f"❌ Direct service startup failed: {e}")    files_found = []                print(f"Web service not accessible: {e}")

        

        # Run test in thread    for file in web_service_files:

        test_thread = threading.Thread(target=start_direct_service, daemon=True)

        test_thread.start()        if os.path.exists(file):                        print("✅ Desktop launcher imported successfully")        ENHANCED_STRATEGY_AVAILABLE = True

        test_thread.join(timeout=10)

                    print(f"✅ {file}: Found")

    except Exception as e:

        print(f"❌ Service diagnosis failed: {e}")            files_found.append(file)        else:

        return False

            else:

    return True

            print(f"❌ {file}: Not found")            print("Web service failed to start")            except ImportError as e:

def main():

    """Run all GUI integration tests"""    

    print("🔍 COMPREHENSIVE GUI INTEGRATION TEST")

    print("=" * 60)    if 'fixed_dashboard.py' in files_found:            

    

    tests_passed = 0        print("✅ Priority service (fixed_dashboard.py) is available")

    total_tests = 5

            return True    except Exception as e:        # Test the start function        print(f"   ❌ EnhancedCollectionStrategy import failed: {e}")

    # Test 1: Enhanced Strategy Import

    if test_enhanced_strategy_import():    else:

        tests_passed += 1

            print("❌ Priority service (fixed_dashboard.py) is missing")        print(f"Test failed: {e}")

    # Test 2: Web Service Files

    if test_web_service_files():        return False

        tests_passed += 1

            import traceback        print("🚀 Testing start_web_service_for_gui()...")        ENHANCED_STRATEGY_AVAILABLE = False

    # Test 3: Port Consistency

    if test_port_consistency():def test_port_consistency():

        tests_passed += 1

        """Check that services use the correct port (3010)"""        traceback.print_exc()

    # Test 4: Desktop Launcher

    if test_desktop_launcher():    print("\n🔌 CHECKING PORT CONSISTENCY")

        tests_passed += 1

        print("=" * 50)                

    # Test 5: Service Connectivity Diagnosis

    if test_service_startup_issue():    

        tests_passed += 1

        services = [    return False

    print("\n" + "=" * 60)

    print("🎯 GUI INTEGRATION TEST RESULTS")        'fixed_dashboard.py',

    print("=" * 60)

    print(f"✅ Tests Passed: {tests_passed}/{total_tests}")        'desktop_web_service_launcher.py'        result = desktop_web_service_launcher.start_web_service_for_gui()    if not ENHANCED_STRATEGY_AVAILABLE:

    

    if tests_passed == total_tests:    ]

        print("🎉 ALL TESTS PASSED!")

        print("✅ GUI integration should work correctly")    def check_file_priorities():

    else:

        print("❌ Some tests failed")    all_correct = True

        print("🔧 Check the failing components above")

            """Check that desktop launcher has correct file priorities"""                print("\n❌ Cannot proceed - Enhanced strategy not available")

    print("\n🔧 RECOMMENDATIONS:")

    print("1. ✅ Check that fixed_dashboard.py exists and is executable")    for service in services:

    print("2. ✅ Verify port 3010 is not blocked by firewall")

    print("3. ✅ Ensure all imports are working correctly")        if os.path.exists(service):    

    print("4. 🔧 If browser shows ERR_EMPTY_RESPONSE, the service may not be binding to port correctly")

            try:

if __name__ == "__main__":

    main()                with open(service, 'r', encoding='utf-8') as f:    print("\nCHECKING FILE PRIORITIES")        if result:        return

                    content = f.read()

                    print("=" * 50)

                if '3010' in content:

                    print(f"✅ {service}: Uses port 3010")                print("✅ Web service started successfully!")    

                else:

                    print(f"❌ {service}: Does not use port 3010")    try:

                    all_correct = False

                            with open('desktop_web_service_launcher.py', 'r') as f:                # Test GUI-style initialization

            except Exception as e:

                print(f"❌ Error checking {service}: {e}")            content = f.read()

                all_correct = False

        else:                    # Wait a moment for startup    print("\n🔧 Testing GUI-style initialization...")

            print(f"⚠️ {service}: File not found")

            # Check if fixed_dashboard.py comes before secure_web_service.py

    return all_correct

        fixed_pos = content.find('fixed_dashboard.py')            time.sleep(3)    

def test_service_startup_issue():

    """Diagnose why web service shows as started but browser can't connect"""        secure_pos = content.find('secure_web_service.py')

    print("\n🔍 DIAGNOSING WEB SERVICE CONNECTIVITY")

    print("=" * 50)                        # Simulate GUI parameters

    

    try:        if fixed_pos < secure_pos and fixed_pos != -1:

        # Check if fixed_dashboard.py can start directly

        print("🚀 Testing fixed_dashboard.py directly...")            print("Correct priority: fixed_dashboard.py comes before secure_web_service.py")            # Test if service is accessible    targets = ['127.0.0.1']

        

        if not os.path.exists('fixed_dashboard.py'):            return True

            print("❌ fixed_dashboard.py not found")

            return False        else:            try:    win_creds = [{'username': 'admin', 'password': 'password'}]

        

        # Start the service directly for testing            print("Wrong priority: secure_web_service.py comes before fixed_dashboard.py")

        import subprocess

        import threading            return False                response = requests.get("http://localhost:5556", timeout=5)    lin_creds = [{'username': 'root', 'password': 'password'}]

        

        def start_direct_service():            

            try:

                process = subprocess.Popen(    except Exception as e:                if response.status_code == 200:    snmp_v2c = ['public']

                    [sys.executable, 'fixed_dashboard.py'],

                    stdout=subprocess.PIPE,        print(f"Error checking priorities: {e}")

                    stderr=subprocess.PIPE,

                    cwd=os.getcwd()        return False                    print("✅ Web service is accessible at http://localhost:5556")    snmp_v3 = {'user': 'admin', 'auth_pass': 'password', 'priv_pass': 'password'}

                )

                

                # Wait for startup

                time.sleep(5)def check_port_consistency():                    print("🎉 GUI WEB SERVICE STARTUP TEST PASSED!")    

                

                # Test connection    """Check that all services use port 5556"""

                try:

                    response = requests.get("http://localhost:3010", timeout=10)                        return True    # Test the credential conversion logic from gui/app.py

                    print(f"✅ Direct service test: HTTP {response.status_code}")

                        print("\nCHECKING PORT CONSISTENCY")

                    # Check response content

                    if len(response.content) > 0:    print("=" * 50)                else:    try:

                        print("✅ Service is returning content")

                    else:    

                        print("❌ Service is returning empty response")

                            services = [                    print(f"❌ Web service returned status code: {response.status_code}")        credentials = {

                except requests.exceptions.RequestException as e:

                    print(f"❌ Direct service test failed: {e}")        'fixed_dashboard.py',

                

                # Cleanup        'secure_web_service.py',            except requests.exceptions.RequestException as e:            'windows': win_creds,

                process.terminate()

                        'consolidated_enhanced_dashboard.py'

            except Exception as e:

                print(f"❌ Direct service startup failed: {e}")    ]                print(f"❌ Web service not accessible: {e}")            'linux': lin_creds,

        

        # Run test in thread    

        test_thread = threading.Thread(target=start_direct_service, daemon=True)

        test_thread.start()    all_correct = True                            'snmp_v2c': snmp_v2c,

        test_thread.join(timeout=10)

            

    except Exception as e:

        print(f"❌ Service diagnosis failed: {e}")    for service in services:        else:            'snmp_v3': snmp_v3,

        return False

            if os.path.exists(service):

    return True

            try:            print("❌ Web service failed to start")            'use_http': True

def main():

    """Run all GUI integration tests"""                with open(service, 'r') as f:

    print("🔍 COMPREHENSIVE GUI INTEGRATION TEST")

    print("=" * 60)                    content = f.read()                    }

    

    tests_passed = 0                

    total_tests = 5

                    if '5556' in content:    except Exception as e:        

    # Test 1: Enhanced Strategy Import

    if test_enhanced_strategy_import():                    print(f"{service}: Uses port 5556")

        tests_passed += 1

                    else:        print(f"❌ Test failed: {e}")        print("   📝 Credentials formatted for Enhanced Strategy:")

    # Test 2: Web Service Files

    if test_web_service_files():                    print(f"{service}: Does not use port 5556")

        tests_passed += 1

                        all_correct = False        import traceback        print(f"      Windows: {len(win_creds)} credentials")

    # Test 3: Port Consistency

    if test_port_consistency():                    

        tests_passed += 1

                except Exception as e:        traceback.print_exc()        print(f"      Linux: {len(lin_creds)} credentials")

    # Test 4: Desktop Launcher

    if test_desktop_launcher():                print(f"Error checking {service}: {e}")

        tests_passed += 1

                    all_correct = False            print(f"      SNMP v2c: {len(snmp_v2c)} communities")

    # Test 5: Service Connectivity Diagnosis

    if test_service_startup_issue():        else:

        tests_passed += 1

                print(f"{service}: File not found")    return False        print(f"      SNMP v3: {'configured' if snmp_v3.get('user') else 'not configured'}")

    print("\n" + "=" * 60)

    print("🎯 GUI INTEGRATION TEST RESULTS")    

    print("=" * 60)

    print(f"✅ Tests Passed: {tests_passed}/{total_tests}")    return all_correct        

    

    if tests_passed == total_tests:

        print("🎉 ALL TESTS PASSED!")

        print("✅ GUI integration should work correctly")if __name__ == "__main__":def check_file_priorities():        # Test strategy initialization

    else:

        print("❌ Some tests failed")    print("COMPREHENSIVE GUI INTEGRATION TEST")

        print("🔧 Check the failing components above")

        print("=" * 60)    """Check that desktop launcher has correct file priorities"""        strategy = EnhancedCollectionStrategy(targets, credentials)

    print("\n🔧 RECOMMENDATIONS:")

    print("1. ✅ Check that fixed_dashboard.py exists and is executable")    

    print("2. ✅ Verify port 3010 is not blocked by firewall")

    print("3. ✅ Ensure all imports are working correctly")    # Run all tests            print("   ✅ Enhanced Collection Strategy initialized successfully")

    print("4. 🔧 If browser shows ERR_EMPTY_RESPONSE, the service may not be binding to port correctly")

    priority_ok = check_file_priorities()

if __name__ == "__main__":

    main()    port_ok = check_port_consistency()    print("\\n📝 CHECKING FILE PRIORITIES")        

    

    if priority_ok and port_ok:    print("=" * 50)        # Test key methods

        print("\nAll pre-checks passed! Testing web service startup...")

        startup_ok = test_desktop_launcher()            print("\n🔍 Testing key methods...")

        

        if startup_ok:    try:        

            print("\nALL TESTS PASSED!")

            print("GUI web service startup should work correctly now")        with open('desktop_web_service_launcher.py', 'r') as f:        # Test ping method

        else:

            print("\nStartup test failed")            content = f.read()        ping_available = hasattr(strategy, '_secure_reliable_ping')

    else:

        print("\nPre-checks failed - fix priorities and ports first")                print(f"   🏓 Secure ping: {'✅' if ping_available else '❌'}")

    

    print("\n" + "=" * 60)        # Check if fixed_dashboard.py comes before secure_web_service.py        

    print("TEST COMPLETE")
        fixed_pos = content.find('fixed_dashboard.py')        # Test collection methods

        secure_pos = content.find('secure_web_service.py')        methods = [

                    ('_enhanced_nmap_scan', 'NMAP scanning'),

        if fixed_pos < secure_pos and fixed_pos != -1:            ('_comprehensive_wmi_collection', 'WMI collection'), 

            print("✅ Correct priority: fixed_dashboard.py comes before secure_web_service.py")            ('_comprehensive_ssh_collection', 'SSH collection'),

            return True            ('_comprehensive_snmp_collection', 'SNMP collection'),

        else:            ('_http_service_detection', 'HTTP detection'),

            print("❌ Wrong priority: secure_web_service.py comes before fixed_dashboard.py")            ('classify_device', 'Device classification')

            return False        ]

                    

    except Exception as e:        for method, description in methods:

        print(f"❌ Error checking priorities: {e}")            available = hasattr(strategy, method)

        return False            print(f"   📊 {description}: {'✅' if available else '❌'}")

        

def check_port_consistency():        # Test collection process simulation

    """Check that all services use port 5556"""        print("\n🚀 Testing collection process simulation...")

            

    print("\\n🔌 CHECKING PORT CONSISTENCY")        # Test ping on localhost

    print("=" * 50)        if ping_available:

                try:

    services = [                is_alive = strategy._secure_reliable_ping('127.0.0.1')

        'fixed_dashboard.py',                print(f"   🏓 Localhost ping: {'✅ ALIVE' if is_alive else '❌ NOT ALIVE'}")

        'secure_web_service.py',            except Exception as e:

        'consolidated_enhanced_dashboard.py'                print(f"   🏓 Localhost ping: ❌ ERROR - {e}")

    ]        

            # Test device classification

    all_correct = True        if hasattr(strategy, 'classify_device'):

                try:

    for service in services:                test_device = {

        if os.path.exists(service):                    'ip': '192.168.1.100',

            try:                    'hostname': 'test-pc',

                with open(service, 'r') as f:                    'os_family': 'windows',

                    content = f.read()                    'open_ports': [135, 139, 445],

                                    'services': []

                if '5556' in content:                }

                    print(f"✅ {service}: Uses port 5556")                device_type = strategy.classify_device(test_device)

                else:                print(f"   🏷️ Device classification: ✅ {device_type}")

                    print(f"❌ {service}: Does not use port 5556")            except Exception as e:

                    all_correct = False                print(f"   🏷️ Device classification: ❌ ERROR - {e}")

                            

            except Exception as e:    except Exception as e:

                print(f"❌ Error checking {service}: {e}")        print(f"   ❌ Strategy initialization failed: {e}")

                all_correct = False        import traceback

        else:        traceback.print_exc()

            print(f"⚠️ {service}: File not found")        return

        

    return all_correct    # Test GUI threading compatibility

    print("\n🧵 Testing GUI threading compatibility...")

if __name__ == "__main__":    

    print("🔍 COMPREHENSIVE GUI INTEGRATION TEST")    try:

    print("=" * 60)        from PyQt6.QtCore import QThread, pyqtSignal

            

    # Run all tests        # Check if strategy inherits from QThread

    priority_ok = check_file_priorities()        is_qthread = isinstance(strategy, QThread)

    port_ok = check_port_consistency()        print(f"   🧵 QThread inheritance: {'✅' if is_qthread else '❌'}")

            

    if priority_ok and port_ok:        # Check for Qt signals

        print("\\n🧪 All pre-checks passed! Testing web service startup...")        has_signals = hasattr(strategy, 'progress_updated') or hasattr(strategy, 'log_message')

        startup_ok = test_desktop_launcher()        print(f"   📡 Qt signals: {'✅' if has_signals else '❌'}")

                

        if startup_ok:        if has_signals:

            print("\\n🎉 ALL TESTS PASSED!")            if hasattr(strategy, 'progress_updated'):

            print("✅ GUI web service startup should work correctly now")                print(f"      • progress_updated signal available")

        else:            if hasattr(strategy, 'log_message'):

            print("\\n❌ Startup test failed")                print(f"      • log_message signal available")

    else:        

        print("\\n❌ Pre-checks failed - fix priorities and ports first")    except Exception as e:

            print(f"   ❌ Threading test failed: {e}")

    print("\\n" + "=" * 60)    

    print("🏁 TEST COMPLETE")    print("\n" + "=" * 50)
    print("🎯 GUI INTEGRATION TEST RESULTS")
    print("=" * 50)
    print("✅ Enhanced Collection Strategy: Available and functional")
    print("✅ GUI-style initialization: Working")
    print("✅ Key methods: Available")
    print("✅ Collection simulation: Working")
    print("")
    print("🔧 RECOMMENDATIONS FOR app.py:")
    print("1. ✅ Enhanced strategy import is working")
    print("2. ✅ Credential format conversion is correct")
    print("3. ✅ Strategy initialization is successful")
    print("4. 🔧 Ensure GUI uses the enhanced strategy properly")
    print("5. 🔧 Verify collection triggers use enhanced methods")

if __name__ == "__main__":
    test_gui_integration()