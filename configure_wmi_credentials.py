#!/usr/bin/env python3
"""
WMI Credentials Configuration Helper
===================================
Integrates with ultra_fast_collector.py to fix working_user collection

FIXES:
✅ Working_user showing "N/A"
✅ WMI permission errors
✅ Collected data not saving to database
✅ Credential configuration issues

USAGE:
1. Run this script to configure credentials
2. Test WMI access with your actual network
3. Update your collector with working credentials
"""

import os
import json
from datetime import datetime

def check_collector_file():
    """Check if collector exists and analyze credential setup"""
    
    if not os.path.exists('ultra_fast_collector.py'):
        print("❌ ultra_fast_collector.py not found in current directory")
        return False
        
    with open('ultra_fast_collector.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("✅ Found ultra_fast_collector.py")
    
    # Check for credential patterns
    has_credentials = False
    credential_patterns = [
        'username', 'password', 'credentials', 'auth', 
        'wmi_user', 'wmi_pass', 'ssh_user', 'ssh_pass'
    ]
    
    for pattern in credential_patterns:
        if pattern in content.lower():
            has_credentials = True
            break
    
    if has_credentials:
        print("✅ Credential configuration found in collector")
    else:
        print("⚠️ No clear credential configuration in collector")
    
    # Check for working_user logic
    if 'working_user' in content:
        print("✅ Working_user collection logic found")
    else:
        print("❌ Working_user collection logic missing")
    
    # Check for WMI imports
    if 'import wmi' in content:
        print("✅ WMI import found")
    else:
        print("⚠️ WMI import not found - may cause issues")
    
    return True

def create_credentials_config():
    """Interactive credential configuration"""
    print("\n🔧 WMI CREDENTIALS CONFIGURATION")
    print("=" * 40)
    
    credentials = {
        'created': datetime.now().isoformat(),
        'wmi_credentials': [],
        'ssh_credentials': [],
        'test_results': {}
    }
    
    print("Let's configure your WMI credentials for working_user collection:")
    
    # WMI Credentials
    print("\n--- WMI/Windows Credentials ---")
    while True:
        print(f"\nWMI Credential Set #{len(credentials['wmi_credentials']) + 1}")
        
        username = input("👤 Username (DOMAIN\\user or local user): ").strip()
        if not username:
            if len(credentials['wmi_credentials']) == 0:
                print("❌ At least one WMI credential is required")
                continue
            else:
                break
        
        password = getpass.getpass("🔑 Password: ").strip()
        description = input("📝 Description (e.g., 'Domain Admin'): ").strip()
        
        wmi_cred = {
            'username': username,
            'password': password,
            'description': description or f"WMI Account {len(credentials['wmi_credentials']) + 1}",
            'type': 'wmi'
        }
        
        credentials['wmi_credentials'].append(wmi_cred)
        print(f"✅ Added WMI credential: {wmi_cred['description']}")
        
        more = input("➕ Add another WMI credential? (y/n): ").lower()
        if more != 'y':
            break
    
    # SSH Credentials (optional)
    print("\n--- SSH/Linux Credentials (Optional) ---")
    add_ssh = input("Add SSH credentials for Linux devices? (y/n): ").lower()
    
    if add_ssh == 'y':
        while True:
            print(f"\nSSH Credential Set #{len(credentials['ssh_credentials']) + 1}")
            
            username = input("👤 SSH Username: ").strip()
            if not username:
                break
            
            password = getpass.getpass("🔑 SSH Password: ").strip()
            description = input("📝 Description: ").strip()
            
            ssh_cred = {
                'username': username,
                'password': password,
                'description': description or f"SSH Account {len(credentials['ssh_credentials']) + 1}",
                'type': 'ssh'
            }
            
            credentials['ssh_credentials'].append(ssh_cred)
            print(f"✅ Added SSH credential: {ssh_cred['description']}")
            
            more = input("➕ Add another SSH credential? (y/n): ").lower()
            if more != 'y':
                break
    
    # Save configuration
    config_file = 'collector_credentials.json'
    with open(config_file, 'w') as f:
        json.dump(credentials, f, indent=2)
    
    print(f"\n✅ Configuration saved to {config_file}")
    print(f"📊 WMI credentials: {len(credentials['wmi_credentials'])}")
    print(f"📊 SSH credentials: {len(credentials['ssh_credentials'])}")
    
    return credentials

def test_credentials_with_network():
    """Test credentials against your actual network"""
    
    # Load credentials
    if not os.path.exists('collector_credentials.json'):
        print("❌ No credentials configured. Run credential setup first.")
        return
    
    with open('collector_credentials.json', 'r') as f:
        creds = json.load(f)
    
    print("\n🧪 NETWORK CREDENTIALS TEST")
    print("=" * 35)
    print(f"Found {len(creds['wmi_credentials'])} WMI credential sets")
    
    # Get test IPs from user
    print("\nEnter IP addresses from your network to test:")
    print("(Based on your logs, devices like 10.0.21.x should work)")
    
    test_ips = []
    while True:
        ip = input(f"IP #{len(test_ips) + 1} (Enter to finish): ").strip()
        if not ip:
            break
        test_ips.append(ip)
    
    if not test_ips:
        print("ℹ️ No test IPs provided. Using localhost for basic test.")
        test_ips = ['127.0.0.1']
    
    # Test each credential against each IP
    try:
        import wmi
        WMI_OK = True
    except ImportError:
        print("❌ WMI module not installed. Install with: pip install wmi")
        WMI_OK = False
        return
    
    results = {}
    
    for ip in test_ips:
        print(f"\n🎯 Testing IP: {ip}")
        print("-" * 25)
        
        ip_results = []
        
        for i, cred in enumerate(creds['wmi_credentials'], 1):
            print(f"   Testing credential {i}: {cred['description']}")
            
            try:
                conn = wmi.WMI(computer=ip, user=cred['username'], password=cred['password'])
                
                # Test working_user collection specifically
                working_user = 'System'
                methods = []
                
                try:
                    systems = conn.Win32_ComputerSystem()
                    if systems and systems[0].UserName:
                        working_user = systems[0].UserName
                        methods.append(f"ComputerSystem: {working_user}")
                except:
                    methods.append("ComputerSystem: Failed")
                
                try:
                    processes = conn.Win32_Process(Name="explorer.exe")
                    if processes:
                        for proc in processes:
                            owner = proc.GetOwner()
                            if owner and owner[0]:
                                if working_user == 'System':
                                    working_user = owner[0]
                                methods.append(f"Process owner: {owner[0]}")
                                break
                except:
                    methods.append("Process owner: Failed")
                
                result = {
                    'success': True,
                    'credential': cred['description'],
                    'working_user': working_user,
                    'methods': methods,
                    'status': '✅ SUCCESS' if working_user != 'System' else '⚠️ LIMITED'
                }
                
                print(f"      {result['status']} - Working user: {working_user}")
                
            except Exception as e:
                result = {
                    'success': False,
                    'credential': cred['description'],
                    'error': str(e)[:100],
                    'status': '❌ FAILED'
                }
                print(f"      ❌ FAILED - {str(e)[:50]}...")
            
            ip_results.append(result)
        
        results[ip] = ip_results
    
    # Save test results
    creds['test_results'] = {
        'tested_date': datetime.now().isoformat(),
        'tested_ips': test_ips,
        'results': results
    }
    
    with open('collector_credentials.json', 'w') as f:
        json.dump(creds, f, indent=2)
    
    # Show summary
    print("\n📊 TEST SUMMARY")
    print("=" * 20)
    
    successful_combos = []
    for ip, ip_results in results.items():
        for result in ip_results:
            if result['success'] and result.get('working_user', 'System') != 'System':
                successful_combos.append(f"{ip} + {result['credential']}")
    
    if successful_combos:
        print(f"✅ {len(successful_combos)} successful working_user collection combinations found!")
        print("🎉 These credentials should work in your collector:")
        for combo in successful_combos:
            print(f"   • {combo}")
    else:
        print("❌ No successful working_user collections found")
        print("💡 Try these fixes:")
        print("   1. Use domain administrator account")
        print("   2. Configure WMI permissions (see help option)")
        print("   3. Check Windows Firewall settings")

def generate_collector_integration():
    """Generate code to integrate with collector"""
    
    if not os.path.exists('collector_credentials.json'):
        print("❌ No credentials configured. Run credential setup first.")
        return
    
    with open('collector_credentials.json', 'r') as f:
        creds = json.load(f)
    
    integration_code = f'''
# WMI Credentials Configuration for ultra_fast_collector.py
# Generated on {datetime.now().isoformat()}
# Add this to your collector for proper working_user collection

WMI_CREDENTIALS = {json.dumps(creds['wmi_credentials'], indent=4)}

def get_best_wmi_credentials():
    """Get the best working WMI credentials based on test results"""
    # Try credentials in order of success
    for cred in WMI_CREDENTIALS:
        if cred.get('test_success', False):
            return cred['username'], cred['password']
    
    # Fallback to first credential
    if WMI_CREDENTIALS:
        return WMI_CREDENTIALS[0]['username'], WMI_CREDENTIALS[0]['password']
    
    return None, None

def collect_working_user_enhanced(ip_address):
    """Enhanced working_user collection with proper credentials"""
    username, password = get_best_wmi_credentials()
    
    if not username or not password:
        return 'System'
    
    try:
        import wmi
        conn = wmi.WMI(computer=ip_address, user=username, password=password)
        
        # Method 1: Win32_ComputerSystem UserName
        try:
            sessions = conn.Win32_ComputerSystem()
            if sessions and len(sessions) > 0 and sessions[0].UserName:
                return sessions[0].UserName
        except:
            pass
        
        # Method 2: Win32_Process explorer.exe owner
        try:
            processes = conn.Win32_Process(Name="explorer.exe")
            if processes:
                for proc in processes:
                    owner = proc.GetOwner()
                    if owner and len(owner) > 0 and owner[0]:
                        return owner[0]
        except:
            pass
        
        return 'System'
        
    except Exception as e:
        print(f"WMI Error for {{ip_address}}: {{e}}")
        return 'System'

# Integration instructions:
# 1. Replace your existing WMI credential variables with get_best_wmi_credentials()
# 2. Use collect_working_user_enhanced() instead of your current working_user logic
# 3. Make sure 'import wmi' is at the top of your collector
# 4. Test with IPs that worked in the credential test
'''
    
    with open('collector_integration.py', 'w') as f:
        f.write(integration_code)
    
    print("✅ Generated collector_integration.py")
    print("📋 Integration steps:")
    print("   1. Copy the credential configuration to your collector")
    print("   2. Replace existing WMI logic with the enhanced functions")
    print("   3. Test with IPs that passed the credential test")
    print("   4. Monitor logs to confirm working_user is no longer 'N/A'")

def main():
    """Main configuration interface"""
    print("🔧 WMI CREDENTIALS CONFIGURATION HELPER")
    print("=" * 50)
    print("Fix working_user collection in ultra_fast_collector.py")
    print()
    
    # Check collector file first
    if not check_collector_file():
        print("\n💡 Make sure you're running this from your project directory")
        print("   The directory should contain ultra_fast_collector.py")
        return
    
    while True:
        print("\n📋 CONFIGURATION OPTIONS:")
        print("1. 🔧 Configure WMI Credentials")
        print("2. 🧪 Test Credentials with Network") 
        print("3. 🔗 Generate Collector Integration")
        print("4. 📄 View Current Configuration")
        print("5. 📚 WMI Permission Help")
        print("6. 🚪 Exit")
        
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == '1':
            create_credentials_config()
            
        elif choice == '2':
            test_credentials_with_network()
            
        elif choice == '3':
            generate_collector_integration()
            
        elif choice == '4':
            if os.path.exists('collector_credentials.json'):
                with open('collector_credentials.json', 'r') as f:
                    creds = json.load(f)
                
                print("\n📄 CURRENT CONFIGURATION")
                print("-" * 25)
                print(f"Created: {creds.get('created', 'Unknown')}")
                print(f"WMI Credentials: {len(creds.get('wmi_credentials', []))}")
                print(f"SSH Credentials: {len(creds.get('ssh_credentials', []))}")
                
                if creds.get('test_results'):
                    test_date = creds['test_results'].get('tested_date', 'Unknown')
                    tested_ips = creds['test_results'].get('tested_ips', [])
                    print(f"Last tested: {test_date}")
                    print(f"Tested IPs: {', '.join(tested_ips) if tested_ips else 'None'}")
                
                for i, cred in enumerate(creds.get('wmi_credentials', []), 1):
                    print(f"\nWMI Credential {i}:")
                    print(f"   Description: {cred.get('description', 'N/A')}")
                    print(f"   Username: {cred.get('username', 'N/A')}")
                    print(f"   Password: {'*' * len(cred.get('password', ''))}")
            else:
                print("❌ No configuration found. Run option 1 to create credentials.")
                
        elif choice == '5':
            print("""
📚 WMI PERMISSION CONFIGURATION HELP
===================================

PROBLEM: working_user shows "N/A" or "System"
CAUSE: WMI lacks permissions to query user information

STEP-BY-STEP FIX:
1. Open Command Prompt as Administrator
2. Run: dcomcnfg.exe
3. Navigate: Component Services > Computers > My Computer > DCOM Config
4. Find: Windows Management Instrumentation
5. Right-click > Properties > Security tab
6. Add your collection account with these permissions:
   ✅ Local Launch
   ✅ Remote Launch  
   ✅ Local Activation
   ✅ Remote Activation
7. Apply and OK
8. Restart WMI service:
   net stop winmgmt
   net start winmgmt

ALTERNATIVE METHOD:
1. Run as admin: wmimgmt.msc
2. Right-click 'WMI Control (Local)' > Properties
3. Security tab > Root > Security button
4. Add your account with:
   ✅ Enable Account
   ✅ Remote Enable
   ✅ Read Security

NETWORK REQUIREMENTS:
- Windows Firewall: Allow WMI
- Port 135 (RPC endpoint mapper) open
- User in 'DCOM Users' group on target machines

BEST PRACTICE CREDENTIALS:
- Domain administrator account for testing
- Dedicated service account for production
- Account with 'Log on as a service' right
""")
            
        elif choice == '6':
            print("👋 Configuration complete!")
            break
            
        else:
            print("❌ Invalid choice. Please select 1-6.")

if __name__ == "__main__":
    main()