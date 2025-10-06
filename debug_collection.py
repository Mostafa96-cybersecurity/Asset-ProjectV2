#!/usr/bin/env python3
"""
Debug Collection Issues for Alive Devices
Investigates why collection fails on devices that ping successfully
"""

import time
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_collection_strategy import EnhancedCollectionStrategy

def debug_collection_failure():
    """Debug why collection fails for alive devices"""
    
    print("🔧 COLLECTION FAILURE INVESTIGATION")
    print("=" * 50)
    
    # Test the problematic IP
    test_ip = "10.0.21.47"
    credentials = {
        'username': 'admin',
        'password': 'password'
    }
    
    strategy = EnhancedCollectionStrategy([test_ip], credentials)
    
    print(f"📍 Investigating collection failure for: {test_ip}")
    print("-" * 50)
    
    # Step 1: Confirm device is alive
    print("🔍 STEP 1: Confirming device is alive...")
    start_time = time.time()
    is_alive = strategy._secure_reliable_ping(test_ip)
    ping_time = (time.time() - start_time) * 1000
    
    if is_alive:
        print(f"   ✅ Device is ALIVE ({ping_time:.1f}ms)")
    else:
        print(f"   ❌ Device is NOT ALIVE ({ping_time:.1f}ms)")
        print("   🛑 Cannot investigate further - device not responding")
        return
    
    # Step 2: Test NMAP scan
    print("\n🔍 STEP 2: Testing NMAP scan...")
    try:
        nmap_result = strategy._enhanced_nmap_scan(test_ip)
        if nmap_result:
            print("   ✅ NMAP scan successful")
            print(f"   📊 OS family: {nmap_result.get('os_family', 'unknown')}")
            print(f"   🔌 Open ports: {nmap_result.get('open_ports', [])}")
            print(f"   🏷️ Hostname: {nmap_result.get('hostname', 'unknown')}")
        else:
            print("   ❌ NMAP scan failed or returned no data")
    except Exception as e:
        print(f"   ❌ NMAP scan error: {e}")
    
    # Step 3: Test WMI collection (if Windows)
    print("\n🔍 STEP 3: Testing WMI collection...")
    try:
        wmi_result = strategy._comprehensive_wmi_collection(test_ip)
        if wmi_result:
            print("   ✅ WMI collection successful")
            print(f"   📊 Data fields: {len(wmi_result)}")
            print(f"   💻 Computer name: {wmi_result.get('computer_name', 'unknown')}")
            print(f"   🖥️ OS: {wmi_result.get('os_name', 'unknown')}")
        else:
            print("   ❌ WMI collection failed or returned no data")
    except Exception as e:
        print(f"   ❌ WMI collection error: {e}")
    
    # Step 4: Test SSH collection
    print("\n🔍 STEP 4: Testing SSH collection...")
    try:
        # Use credentials from strategy
        ssh_result = strategy._comprehensive_ssh_collection(test_ip, credentials['username'], credentials['password'])
        if ssh_result:
            print("   ✅ SSH collection successful")
            print(f"   📊 Data fields: {len(ssh_result)}")
            print(f"   💻 Hostname: {ssh_result.get('hostname', 'unknown')}")
            print(f"   🖥️ OS: {ssh_result.get('os_name', 'unknown')}")
        else:
            print("   ❌ SSH collection failed or returned no data")
    except Exception as e:
        print(f"   ❌ SSH collection error: {e}")
    
    # Step 5: Test SNMP collection
    print("\n🔍 STEP 5: Testing SNMP collection...")
    try:
        # Use default SNMP community
        snmp_result = strategy._comprehensive_snmp_collection(test_ip, 'public')
        if snmp_result:
            print("   ✅ SNMP collection successful")
            print(f"   📊 Data fields: {len(snmp_result)}")
            print(f"   🏷️ System description: {snmp_result.get('system_description', 'unknown')}")
        else:
            print("   ❌ SNMP collection failed or returned no data")
    except Exception as e:
        print(f"   ❌ SNMP collection error: {e}")
    
    # Step 6: Test HTTP service detection
    print("\n🔍 STEP 6: Testing HTTP service detection...")
    try:
        http_result = strategy._http_service_detection(test_ip)
        if http_result:
            print("   ✅ HTTP detection successful")
            print(f"   📊 Services found: {len(http_result)}")
            for service, details in http_result.items():
                print(f"      • {service}: {details}")
        else:
            print("   ❌ HTTP detection failed or found no services")
    except Exception as e:
        print(f"   ❌ HTTP detection error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 DIAGNOSIS SUMMARY")
    print("=" * 50)
    print("✅ Device is confirmed ALIVE via secure ping")
    print("📊 Collection methods tested individually above")
    print("🔧 Any failures indicate specific collection issues, not ping problems")
    print("")
    print("� COMMON ISSUES & SOLUTIONS:")
    print("   📌 NMAP scan failure:")
    print("      • Install nmap: winget install nmap or download from nmap.org")
    print("      • Add nmap to system PATH")
    print("      • Run as administrator if needed")
    print("")
    print("   📌 WMI collection failure:")
    print("      • Requires Windows target device")
    print("      • May need administrator credentials")
    print("      • Check Windows firewall settings")
    print("")
    print("   📌 SSH collection failure:")
    print("      • Requires SSH service on target")
    print("      • Check username/password credentials")
    print("      • Verify SSH port 22 is open")
    print("")
    print("   📌 SNMP collection failure:")
    print("      • Requires SNMP service enabled")
    print("      • Check SNMP community string")
    print("      • Verify SNMP port 161 is open")
    print("")
    print("   📌 HTTP detection failure:")
    print("      • Device may not have web services")
    print("      • Check ports 80, 443, 8080, etc.")
    print("      • Firewall may be blocking access")
    print("")
    print("🎯 CONCLUSION:")
    print("   The secure ping is working correctly!")
    print("   Device 10.0.21.47 IS alive and responding.")
    print("   Collection failures are due to service/configuration issues,")
    print("   not ping detection problems.")

if __name__ == "__main__":
    debug_collection_failure()