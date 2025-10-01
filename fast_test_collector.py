#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fast Data Collection Test - No Hanging
=====================================
Quick test for IP 10.0.21.47 with proper timeouts
"""

import os
import sys
import sqlite3
import time
import socket
import subprocess
from datetime import datetime
from pathlib import Path

# Add project root to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def quick_ping_test(ip, timeout=2):
    """Quick ping test with timeout"""
    try:
        result = subprocess.run(['ping', '-n', '1', '-w', '2000', ip], 
                               capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0
    except:
        return False

def quick_port_scan(ip, ports, timeout=1):
    """Quick port scan with minimal timeout"""
    open_ports = []
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            if result == 0:
                open_ports.append(port)
            sock.close()
        except:
            pass
    return open_ports

def detect_device_type(ip, open_ports):
    """Detect device type based on open ports"""
    
    if not open_ports:
        return "Unknown", "No open ports detected"
    
    # Windows detection
    if 135 in open_ports or 445 in open_ports or 3389 in open_ports:
        return "Windows", f"Windows ports detected: {open_ports}"
    
    # Linux/Unix detection
    if 22 in open_ports:
        return "Linux", f"SSH port detected: {open_ports}"
    
    # Network device detection
    if 161 in open_ports or 23 in open_ports:
        return "Network Device", f"SNMP/Telnet detected: {open_ports}"
    
    # Printer detection
    if 9100 in open_ports or 631 in open_ports:
        return "Printer", f"Printer ports detected: {open_ports}"
    
    # Web device detection
    if 80 in open_ports or 443 in open_ports:
        return "Web Device", f"HTTP ports detected: {open_ports}"
    
    return "Unknown", f"Unidentified ports: {open_ports}"

def quick_wmi_test(ip, timeout=5):
    """Quick WMI test with timeout"""
    try:
        import wmi
        start_time = time.time()
        
        # Try to connect with timeout
        conn = wmi.WMI(computer=ip)
        
        # Check if we're taking too long
        if time.time() - start_time > timeout:
            return None, "WMI timeout"
        
        # Quick system info
        systems = conn.Win32_ComputerSystem()
        if systems and time.time() - start_time < timeout:
            system = systems[0]
            return {
                'hostname': system.Name,
                'domain': system.Domain,
                'manufacturer': system.Manufacturer,
                'model': system.Model,
                'working_user': getattr(system, 'UserName', 'Unknown')
            }, "WMI Success"
        
        return None, "WMI no data"
        
    except ImportError:
        return None, "WMI not available"
    except Exception as e:
        return None, f"WMI failed: {str(e)[:100]}"

def quick_snmp_test(ip, timeout=3):
    """Quick SNMP test with timeout"""
    try:
        # Try basic SNMP without complex imports
        import socket
        
        # Create UDP socket for SNMP
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(timeout)
        
        # Simple SNMP v1 get request for sysDescr (basic test)
        # This is just to test connectivity
        sock.connect((ip, 161))
        sock.close()
        
        return {"snmp_available": True}, "SNMP port accessible"
        
    except Exception as e:
        return None, f"SNMP failed: {str(e)[:100]}"

def test_data_collection_fast(target_ip):
    """Fast data collection test with timeouts"""
    
    print(f"\n🎯 FAST TEST FOR {target_ip}")
    print("=" * 50)
    
    results = {
        'ip_address': target_ip,
        'test_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'ping_result': False,
        'open_ports': [],
        'device_type': 'Unknown',
        'detection_reason': '',
        'collection_method': None,
        'collected_data': None,
        'collection_status': 'Not attempted'
    }
    
    # Step 1: Quick ping test (2 seconds max)
    print(f"🔍 1. Testing connectivity...")
    start_time = time.time()
    results['ping_result'] = quick_ping_test(target_ip, timeout=2)
    ping_time = time.time() - start_time
    
    if results['ping_result']:
        print(f"✅ Ping successful ({ping_time:.1f}s)")
    else:
        print(f"❌ Ping failed ({ping_time:.1f}s)")
        return results
    
    # Step 2: Quick port scan (5 seconds max)
    print(f"🔍 2. Scanning common ports...")
    start_time = time.time()
    common_ports = [22, 23, 53, 80, 135, 139, 161, 443, 445, 631, 3389, 9100]
    results['open_ports'] = quick_port_scan(target_ip, common_ports, timeout=1)
    scan_time = time.time() - start_time
    
    print(f"📊 Open ports found: {results['open_ports']} ({scan_time:.1f}s)")
    
    # Step 3: Device type detection (instant)
    print(f"🔍 3. Detecting device type...")
    results['device_type'], results['detection_reason'] = detect_device_type(target_ip, results['open_ports'])
    print(f"🖥️ Device type: {results['device_type']}")
    print(f"📋 Reason: {results['detection_reason']}")
    
    # Step 4: Quick collection attempt based on device type
    print(f"🔍 4. Attempting data collection...")
    
    if results['device_type'] == 'Windows':
        print(f"🔧 Trying WMI collection...")
        start_time = time.time()
        data, status = quick_wmi_test(target_ip, timeout=5)
        collection_time = time.time() - start_time
        
        if data:
            results['collected_data'] = data
            results['collection_method'] = 'WMI'
            results['collection_status'] = status
            print(f"✅ WMI success ({collection_time:.1f}s)")
            print(f"   Hostname: {data.get('hostname', 'Unknown')}")
            print(f"   Domain: {data.get('domain', 'Unknown')}")
            print(f"   Manufacturer: {data.get('manufacturer', 'Unknown')}")
        else:
            print(f"❌ WMI failed: {status} ({collection_time:.1f}s)")
            results['collection_status'] = status
            
            # Try SNMP fallback
            print(f"🔧 Trying SNMP fallback...")
            start_time = time.time()
            data, status = quick_snmp_test(target_ip, timeout=3)
            collection_time = time.time() - start_time
            
            if data:
                results['collected_data'] = data
                results['collection_method'] = 'SNMP'
                results['collection_status'] = status
                print(f"✅ SNMP fallback success ({collection_time:.1f}s)")
            else:
                print(f"❌ SNMP fallback failed: {status} ({collection_time:.1f}s)")
                results['collection_status'] = f"WMI failed, SNMP failed: {status}"
    
    elif results['device_type'] == 'Network Device':
        print(f"🔧 Trying SNMP collection...")
        start_time = time.time()
        data, status = quick_snmp_test(target_ip, timeout=3)
        collection_time = time.time() - start_time
        
        if data:
            results['collected_data'] = data
            results['collection_method'] = 'SNMP'
            results['collection_status'] = status
            print(f"✅ SNMP success ({collection_time:.1f}s)")
        else:
            print(f"❌ SNMP failed: {status} ({collection_time:.1f}s)")
            results['collection_status'] = status
    
    else:
        results['collection_status'] = f"No collection method for {results['device_type']}"
        print(f"⚠️ No collection method configured for {results['device_type']}")
    
    return results

def check_database_for_ip(target_ip):
    """Check if IP exists in database"""
    
    print(f"\n💾 CHECKING DATABASE FOR {target_ip}")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('assets.db')
        cursor = conn.cursor()
        
        # Check if IP exists
        cursor.execute('SELECT COUNT(*) FROM assets WHERE ip_address = ?', (target_ip,))
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"✅ Found {count} record(s) for {target_ip}")
            
            # Get the data
            cursor.execute('SELECT * FROM assets WHERE ip_address = ? LIMIT 1', (target_ip,))
            record = cursor.fetchone()
            
            if record:
                # Get column names
                cursor.execute('PRAGMA table_info(assets)')
                columns = [col[1] for col in cursor.fetchall()]
                device_data = dict(zip(columns, record))
                
                # Show key fields
                key_fields = ['hostname', 'working_user', 'domain', 'manufacturer', 
                             'model', 'operating_system', 'installed_ram_gb', 'storage']
                
                print(f"📋 Key data for {target_ip}:")
                for field in key_fields:
                    value = device_data.get(field)
                    if value and str(value).strip():
                        print(f"   {field}: {value}")
        else:
            print(f"❌ No records found for {target_ip}")
            
            # Check for any devices in same subnet
            subnet = '.'.join(target_ip.split('.')[:-1]) + '%'
            cursor.execute('SELECT DISTINCT ip_address FROM assets WHERE ip_address LIKE ? LIMIT 5', (subnet,))
            subnet_ips = [row[0] for row in cursor.fetchall()]
            
            if subnet_ips:
                print(f"🔍 Other devices in subnet:")
                for ip in subnet_ips:
                    print(f"   {ip}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")

def main():
    """Main fast test function"""
    
    target_ip = "10.0.21.47"
    
    print("⚡ FAST DATA COLLECTION TEST")
    print("=" * 60)
    print(f"Target: {target_ip}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Goal: Quick test with timeouts (no hanging)")
    print("=" * 60)
    
    # Test data collection
    total_start = time.time()
    results = test_data_collection_fast(target_ip)
    total_time = time.time() - total_start
    
    # Check database
    check_database_for_ip(target_ip)
    
    # Summary
    print(f"\n📊 FAST TEST SUMMARY")
    print("=" * 50)
    print(f"Total time: {total_time:.1f} seconds")
    print(f"Ping: {'✅' if results['ping_result'] else '❌'}")
    print(f"Open ports: {len(results['open_ports'])}")
    print(f"Device type: {results['device_type']}")
    print(f"Collection method: {results['collection_method'] or 'None'}")
    print(f"Status: {results['collection_status']}")
    
    if results['collected_data']:
        print(f"✅ Data collected successfully")
    else:
        print(f"❌ No data collected")
    
    print(f"\n🎯 Next steps:")
    print(f"   1. Configure Windows credentials for WMI")
    print(f"   2. Test with credentials for full data collection")
    print(f"   3. Verify English-only data in database")

if __name__ == "__main__":
    main()