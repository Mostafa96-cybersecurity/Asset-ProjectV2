#!/usr/bin/env python3
"""
Quick Authentication Test Script
Run this after setting up credentials
"""

import ipaddress  # For IP validation
import subprocess

def test_wmi_auth():
    """Test WMI authentication"""
    print("Testing WMI Authentication...")
    try:
        # Simple WMI test
        result = subprocess.run([
            'wmic', 'computersystem', 'get', 'name,manufacturer'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("   ✓ WMI Authentication: SUCCESS")
            return True
        else:
            print("   ✗ WMI Authentication: FAILED")
            return False
    except Exception as e:
        print(f"   ✗ WMI Authentication: ERROR - {e}")
        return False

def test_ssh_connection(host="192.168.1.10"):
    """Test SSH connection"""
    print(f"Testing SSH Connection to {host}...")
    try:
        result = subprocess.run([
            'ssh', '-o', 'ConnectTimeout=10', 
            '-o', 'BatchMode=yes',
            f'asset-scanner@{host}', 
            'echo "SSH Test Successful"'
        ], capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            print("   ✓ SSH Authentication: SUCCESS")
            return True
        else:
            print("   ✗ SSH Authentication: FAILED")
            return False
    except Exception as e:
        print(f"   ✗ SSH Authentication: ERROR - {e}")
        return False

def test_snmp_access(host="192.168.1.1", community="public"):
    """Test SNMP access"""
    print(f"Testing SNMP Access to {host}...")
    try:
        # Try snmpwalk if available
        result = subprocess.run([
            'snmpwalk', '-v2c', '-c', community, host, 'system'
        ], capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            print("   ✓ SNMP Authentication: SUCCESS")
            return True
        else:
            print("   ! SNMP Authentication: No snmpwalk tool found")
            return False
    except Exception as e:
        print(f"   ✗ SNMP Authentication: ERROR - {e}")
        return False

def main():
    print("=" * 60)
    print("AUTHENTICATION TEST RESULTS")
    print("=" * 60)
    
    wmi_ok = test_wmi_auth()
    ssh_ok = test_ssh_connection()
    snmp_ok = test_snmp_access()
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"   WMI:  {'✓ Ready' if wmi_ok else '✗ Needs Setup'}")
    print(f"   SSH:  {'✓ Ready' if ssh_ok else '✗ Needs Setup'}")
    print(f"   SNMP: {'✓ Ready' if snmp_ok else '✗ Needs Setup'}")
    
    ready_count = sum([wmi_ok, ssh_ok, snmp_ok])
    print(f"\nAuthentication Status: {ready_count}/3 methods ready")
    
    if ready_count >= 2:
        print("✓ EXCELLENT! Ready for enhanced data collection!")
    elif ready_count >= 1:
        print("! GOOD! Some authentication configured, continue setup")
    else:
        print("! SETUP NEEDED: Configure authentication methods")

if __name__ == "__main__":
    main()
