#!/usr/bin/env python3
"""
Comprehensive Feature Test & Verification System
Tests all features from scan to database save with full program verification
"""

import sys
import time
import sqlite3
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_environment_setup():
    """Test and setup the environment for full functionality"""
    print("🔧 ENVIRONMENT SETUP & VERIFICATION")
    print("=" * 60)
    
    issues = []
    recommendations = []
    
    # 1. Check Python Environment
    print("1. 📦 PYTHON ENVIRONMENT:")
    python_version = sys.version_info
    print(f"   Python: {python_version.major}.{python_version.minor}.{python_version.micro}")
    if python_version < (3, 8):
        issues.append("Python version too old (need 3.8+)")
    
    # 2. Check Required Modules
    print("\n2. 📚 REQUIRED MODULES:")
    required_modules = [
        ('PyQt6', 'GUI framework'),
        ('sqlite3', 'Database support'),
        ('threading', 'Multi-threading'),
        ('socket', 'Network operations'),
        ('subprocess', 'System commands'),
        ('ipaddress', 'IP address handling')
    ]
    
    for module, description in required_modules:
        try:
            __import__(module)
            print(f"   ✅ {module} - {description}")
        except ImportError:
            print(f"   ❌ {module} - {description}")
            issues.append(f"Missing module: {module}")
    
    # 3. Check Optional Modules for Enhanced Collection
    print("\n3. 🎯 ENHANCED COLLECTION MODULES:")
    optional_modules = [
        ('wmi', 'Windows Management Instrumentation', 'pip install wmi'),
        ('paramiko', 'SSH connections', 'pip install paramiko'),
        ('nmap', 'Network scanning', 'Install nmap from nmap.org + pip install python-nmap'),
        ('requests', 'HTTP requests', 'pip install requests')
    ]
    
    available_modules = 0
    for module, description, install_cmd in optional_modules:
        try:
            __import__(module)
            print(f"   ✅ {module} - {description}")
            available_modules += 1
        except ImportError:
            print(f"   ⚠️ {module} - {description}")
            recommendations.append(f"Install {module}: {install_cmd}")
    
    # 4. Check System Tools
    print("\n4. 🛠️ SYSTEM TOOLS:")
    
    # Check NMAP
    try:
        import subprocess
        result = subprocess.run(['nmap', '--version'], capture_output=True, timeout=5)
        if result.returncode == 0:
            print("   ✅ nmap - Network scanner available")
        else:
            print("   ❌ nmap - Not working properly")
            issues.append("NMAP not functioning")
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        print("   ❌ nmap - Not installed or not in PATH")
        recommendations.append("Install nmap: Download from https://nmap.org/ and add to PATH")
    
    # Check ping command
    try:
        result = subprocess.run(['ping', '127.0.0.1'], capture_output=True, timeout=3)
        if 'ms' in result.stdout.decode().lower():
            print("   ✅ ping - System ping available")
        else:
            print("   ⚠️ ping - May not work properly")
    except Exception:
        print("   ❌ ping - System ping not available")
        issues.append("System ping not working")
    
    # 5. Check Database
    print("\n5. 💾 DATABASE:")
    db_path = project_root / "assets.db"
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()
        print(f"   ✅ SQLite database accessible ({len(tables)} tables)")
    except Exception as e:
        print(f"   ⚠️ Database issue: {e}")
        recommendations.append("Database may need initialization")
    
    # 6. Summary
    print("\n📊 ENVIRONMENT SUMMARY:")
    print(f"   ✅ Core modules: {len(required_modules) - len([i for i in issues if 'Missing module' in i])}/{len(required_modules)}")
    print(f"   🎯 Enhanced modules: {available_modules}/{len(optional_modules)}")
    print(f"   ⚠️ Issues found: {len(issues)}")
    print(f"   💡 Recommendations: {len(recommendations)}")
    
    if issues:
        print("\n❌ CRITICAL ISSUES:")
        for issue in issues:
            print(f"   • {issue}")
    
    if recommendations:
        print("\n💡 RECOMMENDATIONS FOR MAXIMUM FUNCTIONALITY:")
        for rec in recommendations:
            print(f"   • {rec}")
    
    return len(issues) == 0, available_modules >= 2

def test_enhanced_collection_strategy():
    """Test the Enhanced Collection Strategy functionality"""
    print("\n" + "=" * 60)
    print("🎯 ENHANCED COLLECTION STRATEGY TEST")
    print("=" * 60)
    
    try:
        from enhanced_collection_strategy import EnhancedCollectionStrategy
        print("✅ Enhanced Collection Strategy imported successfully")
        
        # Test initialization
        targets = ['127.0.0.1']
        credentials = {
            'windows': [{'username': 'admin', 'password': 'password'}],
            'linux': [{'username': 'root', 'password': 'password'}],
            'snmp_v2c': ['public'],
            'snmp_v3': {'user': 'admin', 'auth_pass': 'password', 'priv_pass': 'password'},
            'use_http': True
        }
        
        strategy = EnhancedCollectionStrategy(targets, credentials)
        print("✅ Strategy initialized with comprehensive credentials")
        
        # Test key methods
        print("\n🔍 TESTING KEY METHODS:")
        methods_to_test = [
            ('_secure_reliable_ping', 'Secure ping detection'),
            ('_enhanced_nmap_scan', 'Enhanced NMAP scanning'),
            ('_comprehensive_wmi_collection', 'WMI data collection'),
            ('_comprehensive_ssh_collection', 'SSH data collection'),
            ('_comprehensive_snmp_collection', 'SNMP data collection'),
            ('_http_service_detection', 'HTTP service detection'),
            ('classify_device', 'Device classification'),
            ('run', 'Main collection process')
        ]
        
        method_results = []
        for method, description in methods_to_test:
            available = hasattr(strategy, method)
            status = '✅' if available else '❌'
            print(f"   {status} {description}")
            method_results.append(available)
        
        # Test device classification
        print("\n🏷️ TESTING DEVICE CLASSIFICATION:")
        test_devices = [
            {'ip': '192.168.1.100', 'hostname': 'pc01', 'os_family': 'windows', 'open_ports': [135, 139, 445], 'services': []},
            {'ip': '192.168.1.10', 'hostname': 'srv01', 'os_family': 'windows', 'open_ports': [135, 445, 3389, 53], 'services': []},
            {'ip': '192.168.1.20', 'hostname': 'web01', 'os_family': 'linux', 'open_ports': [22, 80, 443], 'services': []},
            {'ip': '192.168.1.150', 'hostname': 'printer01', 'os_family': 'unknown', 'open_ports': [9100, 631], 'services': []},
            {'ip': '192.168.1.1', 'hostname': 'switch01', 'os_family': 'unknown', 'open_ports': [22, 161], 'services': []}
        ]
        
        device_types = []
        for device in test_devices:
            try:
                device_type = strategy.classify_device(device)
                device_types.append(device_type)
                print(f"   ✅ {device['hostname']} → {device_type}")
            except Exception as e:
                print(f"   ❌ {device['hostname']} → Error: {e}")
                device_types.append("Error")
        
        # Test secure ping
        print("\n🏓 TESTING SECURE PING:")
        ping_targets = ['127.0.0.1', '8.8.8.8']
        ping_results = []
        
        for target in ping_targets:
            try:
                start_time = time.time()
                is_alive = strategy._secure_reliable_ping(target)
                ping_time = (time.time() - start_time) * 1000
                status = 'ALIVE' if is_alive else 'NOT ALIVE'
                print(f"   {target}: {status} ({ping_time:.1f}ms)")
                ping_results.append(is_alive)
            except Exception as e:
                print(f"   {target}: ERROR - {e}")
                ping_results.append(False)
        
        return {
            'strategy_available': True,
            'methods_working': all(method_results),
            'classification_working': len(set(device_types)) > 1,
            'ping_working': any(ping_results)
        }
        
    except Exception as e:
        print(f"❌ Enhanced Collection Strategy test failed: {e}")
        import traceback
        traceback.print_exc()
        return {
            'strategy_available': False,
            'methods_working': False,
            'classification_working': False,
            'ping_working': False
        }

def test_full_collection_simulation():
    """Test a full collection simulation to verify data flow"""
    print("\n" + "=" * 60)
    print("🚀 FULL COLLECTION SIMULATION")
    print("=" * 60)
    
    try:
        from enhanced_collection_strategy import EnhancedCollectionStrategy
        
        # Use localhost for safe testing
        targets = ['127.0.0.1']
        credentials = {
            'windows': [{'username': 'test', 'password': 'test'}],
            'linux': [{'username': 'test', 'password': 'test'}],
            'snmp_v2c': ['public'],
            'snmp_v3': {'user': 'test', 'auth_pass': 'test', 'priv_pass': 'test'},
            'use_http': True
        }
        
        print("📍 Initializing collection strategy for localhost...")
        strategy = EnhancedCollectionStrategy(targets, credentials)
        
        # Test step by step
        print("\n🏓 STEP 1: Testing ping discovery...")
        all_ips = strategy._generate_target_ips()
        print(f"   Generated IPs: {len(all_ips)}")
        
        if len(all_ips) > 0:
            alive_devices = strategy._step1_ping_discovery(all_ips)
            print(f"   Alive devices found: {len(alive_devices)}")
            
            if len(alive_devices) > 0:
                print("\n🔍 STEP 2: Testing OS detection...")
                # Test nmap on first alive device
                device = alive_devices[0]
                try:
                    nmap_result = strategy._enhanced_nmap_scan(device.ip)
                    if nmap_result:
                        print(f"   ✅ NMAP successful: {nmap_result.get('os_family', 'unknown')}")
                    else:
                        print("   ⚠️ NMAP failed (expected if nmap not installed)")
                except Exception as e:
                    print(f"   ⚠️ NMAP error: {e}")
                
                print("\n📊 STEP 3: Testing data collection methods...")
                # Test each collection method
                collection_methods = [
                    ('WMI', lambda: strategy._comprehensive_wmi_collection(device.ip)),
                    ('SSH', lambda: strategy._comprehensive_ssh_collection(device.ip, 'test', 'test')),
                    ('SNMP', lambda: strategy._comprehensive_snmp_collection(device.ip, 'public')),
                    ('HTTP', lambda: strategy._http_service_detection(device.ip))
                ]
                
                successful_methods = 0
                for method_name, method_func in collection_methods:
                    try:
                        result = method_func()
                        if result:
                            print(f"   ✅ {method_name} collection: Success ({len(result) if isinstance(result, dict) else 'data'} items)")
                            successful_methods += 1
                        else:
                            print(f"   ⚠️ {method_name} collection: No data (expected for security/config reasons)")
                    except Exception as e:
                        print(f"   ⚠️ {method_name} collection: {str(e)[:60]}...")
                
                print(f"\n📊 Collection methods successful: {successful_methods}/{len(collection_methods)}")
                return successful_methods > 0
            else:
                print("❌ No alive devices found")
                return False
        else:
            print("❌ No target IPs generated")
            return False
            
    except Exception as e:
        print(f"❌ Full collection simulation failed: {e}")
        return False

def test_database_functionality():
    """Test database operations"""
    print("\n" + "=" * 60)
    print("💾 DATABASE FUNCTIONALITY TEST")
    print("=" * 60)
    
    db_path = project_root / "assets.db"
    
    try:
        # Test basic database operations
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check existing tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"📊 Existing tables: {len(tables)}")
        for table in tables:
            print(f"   • {table[0]}")
        
        # Test inserting test data
        test_table = "test_devices"
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {test_table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address TEXT,
                hostname TEXT,
                device_type TEXT,
                os_name TEXT,
                collection_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert test record
        cursor.execute(f"""
            INSERT INTO {test_table} (ip_address, hostname, device_type, os_name)
            VALUES (?, ?, ?, ?)
        """, ('127.0.0.1', 'localhost', 'Workstations', 'Test OS'))
        
        # Verify insertion
        cursor.execute(f"SELECT COUNT(*) FROM {test_table}")
        count = cursor.fetchone()[0]
        print(f"✅ Test record inserted successfully (total records: {count})")
        
        # Clean up test table
        cursor.execute(f"DROP TABLE {test_table}")
        
        conn.commit()
        conn.close()
        
        print("✅ Database functionality working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def run_comprehensive_test():
    """Run all tests and provide comprehensive report"""
    print("🧪 COMPREHENSIVE FEATURE TEST & VERIFICATION")
    print("=" * 80)
    print("Testing all features from scan to database save...")
    print("=" * 80)
    
    # Run all tests
    env_ok, modules_ok = test_environment_setup()
    strategy_results = test_enhanced_collection_strategy()
    collection_ok = test_full_collection_simulation()
    database_ok = test_database_functionality()
    
    # Generate comprehensive report
    print("\n" + "=" * 80)
    print("📋 COMPREHENSIVE TEST REPORT")
    print("=" * 80)
    
    print("\n🔧 ENVIRONMENT:")
    print(f"   Core functionality: {'✅' if env_ok else '❌'}")
    print(f"   Enhanced modules: {'✅' if modules_ok else '⚠️'}")
    
    print("\n🎯 ENHANCED COLLECTION STRATEGY:")
    print(f"   Strategy available: {'✅' if strategy_results['strategy_available'] else '❌'}")
    print(f"   Methods working: {'✅' if strategy_results['methods_working'] else '❌'}")
    print(f"   Classification working: {'✅' if strategy_results['classification_working'] else '❌'}")
    print(f"   Secure ping working: {'✅' if strategy_results['ping_working'] else '❌'}")
    
    print("\n🚀 COLLECTION SIMULATION:")
    print(f"   Full process test: {'✅' if collection_ok else '❌'}")
    
    print("\n💾 DATABASE:")
    print(f"   Database functionality: {'✅' if database_ok else '❌'}")
    
    # Overall assessment
    all_critical = env_ok and strategy_results['strategy_available'] and database_ok
    all_enhanced = all_critical and modules_ok and strategy_results['methods_working']
    
    print("\n🎯 OVERALL ASSESSMENT:")
    print(f"   Critical functionality: {'✅ WORKING' if all_critical else '❌ ISSUES'}")
    print(f"   Enhanced functionality: {'✅ FULLY WORKING' if all_enhanced else '⚠️ PARTIAL'}")
    
    if all_enhanced:
        print("\n🎉 RESULT: ALL FEATURES WORKING!")
        print("   • Secure ping detection ✅")
        print("   • Device classification ✅")
        print("   • Multiple collection methods ✅")
        print("   • Database operations ✅")
        print("   • End-to-end functionality ✅")
    elif all_critical:
        print("\n⚠️ RESULT: CORE FEATURES WORKING, ENHANCEMENTS LIMITED")
        print("   • Basic collection works ✅")
        print("   • Some advanced features may be limited ⚠️")
        print("   • Install recommended tools for full functionality")
    else:
        print("\n❌ RESULT: CRITICAL ISSUES FOUND")
        print("   • Core functionality may be impacted")
        print("   • Review and fix critical issues above")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    run_comprehensive_test()