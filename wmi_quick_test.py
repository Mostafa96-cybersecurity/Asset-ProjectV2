#!/usr/bin/env python3
"""
WMI Credentials & Permissions Test
==================================
Quick diagnostic tool to identify and fix working_user collection issues.
Integrates with your existing ultra_fast_collector.py

SOLVES:
- Working_user field showing "N/A" 
- WMI permission errors (0x80070005)
- Collected devices not saving to database
- DCOM configuration issues

USAGE:
1. Run this script to test your current WMI setup
2. Follow the permission fix instructions
3. Test again until working_user collection succeeds
"""

import os
import sys
import logging
from datetime import datetime
import json

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

# Try to import WMI
try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False
    print("❌ WMI module not installed. Run: pip install wmi")

def test_wmi_working_user(ip, username, password):
    """Test working_user collection exactly like your collector does"""
    
    if not WMI_AVAILABLE:
        return {
            'success': False,
            'working_user': 'System',
            'error': 'WMI module not installed'
        }
    
    try:
        print(f"🔌 Connecting to {ip} with {username}...")
        conn = wmi.WMI(computer=ip, user=username, password=password)
        print("✅ WMI connection successful")
        
        working_user = 'System'  # Default fallback
        methods_tried = []
        
        # Method 1: Win32_ComputerSystem UserName (matches your collector)
        try:
            print("👤 Testing Method 1: Win32_ComputerSystem...")
            sessions = conn.Win32_ComputerSystem()
            if sessions and len(sessions) > 0 and sessions[0].UserName:
                working_user = sessions[0].UserName
                methods_tried.append(f"✅ ComputerSystem: {working_user}")
                print(f"✅ Found working_user via ComputerSystem: {working_user}")
            else:
                methods_tried.append("❌ ComputerSystem: UserName is None/empty")
                print("❌ ComputerSystem UserName is empty")
        except Exception as e:
            methods_tried.append(f"❌ ComputerSystem: {str(e)}")
            print(f"❌ ComputerSystem failed: {e}")
        
        # Method 2: Win32_Process explorer.exe owner (matches your collector)
        if working_user == 'System':
            try:
                print("🔍 Testing Method 2: Win32_Process explorer.exe...")
                processes = conn.Win32_Process(Name="explorer.exe")
                if processes:
                    for proc in processes:
                        try:
                            owner = proc.GetOwner()
                            if owner and len(owner) > 0 and owner[0]:
                                working_user = owner[0]
                                methods_tried.append(f"✅ Process owner: {working_user}")
                                print(f"✅ Found working_user via explorer.exe owner: {working_user}")
                                break
                        except:
                            continue
                
                if working_user == 'System':
                    methods_tried.append("❌ Process: No explorer.exe owner found")
                    print("❌ No explorer.exe process owners found")
            except Exception as e:
                methods_tried.append(f"❌ Process: {str(e)}")
                print(f"❌ Process query failed: {e}")
        
        # Test additional system info that your collector needs
        try:
            print("💻 Testing Win32_ComputerSystem full access...")
            systems = conn.Win32_ComputerSystem()
            if systems:
                system = systems[0]
                system_info = {
                    'name': getattr(system, 'Name', 'N/A'),
                    'domain': getattr(system, 'Domain', 'N/A'),  
                    'manufacturer': getattr(system, 'Manufacturer', 'N/A'),
                    'model': getattr(system, 'Model', 'N/A')
                }
                print(f"✅ System info accessible: {system_info['name']} ({system_info['manufacturer']} {system_info['model']})")
            else:
                print("❌ No Win32_ComputerSystem objects returned")
        except Exception as e:
            print(f"❌ System info failed: {e}")
        
        return {
            'success': True,
            'working_user': working_user,
            'methods_tried': methods_tried,
            'connection_status': 'Connected successfully',
            'final_result': f"Working user: {working_user}"
        }
        
    except Exception as e:
        error_str = str(e)
        
        # Diagnose specific WMI errors
        if '0x80070005' in error_str:
            diagnosis = "Access Denied - WMI permission issue"
            fix = """
🔧 FIX STEPS FOR ACCESS DENIED:
1. Run 'dcomcnfg.exe' as administrator
2. Navigate: Component Services > Computers > My Computer > DCOM Config  
3. Find 'Windows Management Instrumentation'
4. Right-click > Properties > Security tab
5. Add your user account with 'Remote Enable' and 'Remote Activation' permissions
6. Restart WMI service: net stop winmgmt && net start winmgmt
            """
        elif '0x800706BA' in error_str:
            diagnosis = "RPC Server Unavailable - DCOM/Firewall issue"  
            fix = """
🔧 FIX STEPS FOR RPC ISSUE:
1. Check Windows Firewall - allow 'Windows Management Instrumentation (WMI)'
2. Verify RPC service is running: sc query rpcss
3. Configure DCOM for WMI in dcomcnfg.exe
4. Check network connectivity on port 135
            """
        else:
            diagnosis = "General WMI connection issue"
            fix = """
🔧 GENERAL WMI FIX:
1. Verify credentials are correct
2. Check network connectivity  
3. Ensure target system allows WMI connections
4. Try with domain administrator account
            """
        
        return {
            'success': False,
            'working_user': 'System',
            'error': error_str,
            'diagnosis': diagnosis,
            'fix': fix
        }

def quick_test():
    """Quick test with user input"""
    print("🧪 QUICK WMI & WORKING_USER TEST")
    print("=" * 40)
    
    ip = input("🎯 Enter IP address to test: ").strip() or "127.0.0.1"
    username = input("👤 Enter username (domain\\user): ").strip()
    password = input("🔑 Enter password: ").strip()
    
    if not username or not password:
        print("❌ Username and password are required")
        return
    
    print(f"\n🚀 Testing WMI working_user collection for {ip}...")
    print("-" * 50)
    
    result = test_wmi_working_user(ip, username, password)
    
    print(f"\n📊 TEST RESULTS:")
    print("-" * 20)
    
    if result['success']:
        print(f"✅ Connection: SUCCESS")
        print(f"👤 Working User: {result['working_user']}")
        if result['working_user'] != 'System':
            print("🎉 EXCELLENT! Working user collection is working properly!")
        else:
            print("⚠️ WARNING: Working user is 'System' - may indicate permission issues")
        
        print(f"\n🔍 Methods tested:")
        for method in result.get('methods_tried', []):
            print(f"   {method}")
    else:
        print(f"❌ Connection: FAILED")
        print(f"🚨 Error: {result['error']}")
        print(f"📋 Diagnosis: {result['diagnosis']}")
        print(f"\n{result['fix']}")

def test_collector_integration():
    """Test integration with your existing collector"""
    print("🔗 COLLECTOR INTEGRATION TEST")
    print("=" * 35)
    
    # Try to import your collector
    collector_found = False
    try:
        sys.path.append('.')
        
        # Check if your collector file exists
        if os.path.exists('ultra_fast_collector.py'):
            print("✅ Found ultra_fast_collector.py")
            collector_found = True
            
            # Read collector to find credential patterns
            with open('ultra_fast_collector.py', 'r') as f:
                content = f.read()
                
            if 'username' in content and 'password' in content:
                print("✅ Collector has credential configuration")
            
            if '_collect_windows_standalone' in content:
                print("✅ Windows collection method found")
                
            if 'working_user' in content:
                print("✅ Working_user logic found in collector")
            else:
                print("⚠️ Working_user logic may be missing")
        else:
            print("❌ ultra_fast_collector.py not found")
            
    except Exception as e:
        print(f"❌ Error checking collector: {e}")
    
    if collector_found:
        print(f"\n💡 COLLECTOR INTEGRATION TIPS:")
        print("1. Your collector should use the same WMI connection methods tested here")  
        print("2. Make sure database saving happens AFTER successful WMI data collection")
        print("3. Test with the same credentials that work in this test")
        print("4. Check collector logs for WMI permission errors")

def generate_credential_template():
    """Generate a template for WMI credentials configuration"""
    
    template = {
        "wmi_credentials": [
            {
                "description": "Domain Administrator",
                "username": "DOMAIN\\administrator", 
                "password": "your_password_here",
                "use_for": ["windows", "wmi"],
                "test_status": "untested"
            },
            {
                "description": "Local Administrator", 
                "username": "administrator",
                "password": "local_admin_password",
                "use_for": ["windows", "wmi"],
                "test_status": "untested"
            }
        ],
        "ssh_credentials": [
            {
                "description": "SSH Admin Account",
                "username": "admin",
                "password": "ssh_password", 
                "use_for": ["linux", "ssh"],
                "test_status": "untested"
            }
        ],
        "notes": [
            "Replace placeholder passwords with actual credentials",
            "Test each credential set before using in production",
            "Store this file securely - contains plain text passwords",
            "Use domain accounts for best WMI access across network"
        ]
    }
    
    with open('credential_template.json', 'w') as f:
        json.dump(template, f, indent=2)
    
    print("✅ Created credential_template.json")
    print("📝 Edit this file with your actual credentials")
    print("🔒 Secure this file appropriately (contains passwords)")

def main():
    """Main testing interface"""
    print("🔧 WMI WORKING_USER DIAGNOSTIC TOOL") 
    print("=" * 45)
    print("Diagnose and fix working_user collection issues")
    print()
    
    while True:
        print("📋 OPTIONS:")
        print("1. 🧪 Quick WMI Test")
        print("2. 🔗 Test Collector Integration") 
        print("3. 📄 Generate Credential Template")
        print("4. 📚 View Permission Help")
        print("5. 🚪 Exit")
        
        choice = input(f"\nSelect option (1-5): ").strip()
        
        if choice == '1':
            quick_test()
        elif choice == '2':
            test_collector_integration()
        elif choice == '3':
            generate_credential_template()
        elif choice == '4':
            print("""
📚 WMI PERMISSION HELP
=====================

WORKING_USER RETURNS "N/A" OR "SYSTEM":
This happens when WMI lacks permissions to query user information.

QUICK FIX STEPS:
1. Open 'dcomcnfg.exe' as administrator
2. Navigate to: Component Services > Computers > My Computer > DCOM Config
3. Find 'Windows Management Instrumentation'  
4. Right-click > Properties > Security tab
5. Add your collection account with these permissions:
   - Local Launch ✅
   - Remote Launch ✅  
   - Local Activation ✅
   - Remote Activation ✅
6. Click OK and restart WMI: 
   net stop winmgmt
   net start winmgmt

ALTERNATIVE WMI SECURITY:
1. Run 'wmimgmt.msc' as administrator
2. Right-click 'WMI Control (Local)' > Properties
3. Security tab > Root > Security button
4. Add your user account with:
   - Enable Account ✅
   - Remote Enable ✅
   - Read Security ✅

NETWORK REQUIREMENTS:
- Windows Firewall: Allow 'Windows Management Instrumentation (WMI)'
- Ports: 135 (RPC) + dynamic RPC range
- User must be in local 'DCOM Users' group on target machines

CREDENTIAL BEST PRACTICES:
- Use domain admin account for testing
- Create dedicated service account for production
- Grant 'Log on as a service' right
- Test with this tool before using in collector
""")
        elif choice == '5':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please select 1-5.")
        
        print() # Add spacing

if __name__ == "__main__":
    main()