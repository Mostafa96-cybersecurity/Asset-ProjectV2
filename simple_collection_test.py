#!/usr/bin/env python3
"""
Simple Asset Collection Test
Uses existing infrastructure to collect assets and save to database
"""

import sqlite3
import subprocess
import sys
import time
import json
from datetime import datetime

def check_database_count():
    """Get current database count"""
    try:
        conn = sqlite3.connect('assets.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM assets")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except:
        return 0

def check_for_collector_scripts():
    """Find available collector scripts"""
    import glob
    
    collectors = []
    patterns = [
        "*collector*.py",
        "*scan*.py", 
        "*discovery*.py"
    ]
    
    for pattern in patterns:
        files = glob.glob(pattern)
        collectors.extend(files)
    
    # Filter out test files and focus on main collectors
    main_collectors = []
    for collector in collectors:
        if any(word in collector.lower() for word in ['ultimate', 'fast', 'enhanced', 'comprehensive']):
            main_collectors.append(collector)
    
    return main_collectors

def run_collection_via_ultra_fast():
    """Try to run collection using ultra_fast_collector directly"""
    print("🔍 TESTING ULTRA FAST COLLECTOR")
    print("=" * 40)
    
    try:
        # Import and test
        sys.path.insert(0, '.')
        from ultra_fast_collector import UltraFastDeviceCollector
        
        print("✅ UltraFastDeviceCollector imported successfully")
        
        # Initialize collector
        collector = UltraFastDeviceCollector(
            enable_wmi=True,
            enable_ssh=True, 
            enable_snmp=True,
            timeout=30
        )
        
        print("✅ Collector initialized")
        
        # Test with a small IP range first
        test_range = "10.0.21.1-10.0.21.20"
        print(f"🔍 Testing range: {test_range}")
        
        start_time = time.time()
        devices = collector.collect_range(test_range)
        end_time = time.time()
        
        print(f"⏱️ Collection took: {end_time - start_time:.1f} seconds")
        print(f"📊 Found {len(devices)} devices")
        
        # Try to save to database manually
        if len(devices) > 0:
            saved_count = save_devices_to_database(devices)
            print(f"💾 Saved {saved_count} devices to database")
            return saved_count > 0
        else:
            print("⚠️ No devices found to save")
            return False
            
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Collection failed: {e}")
        return False

def save_devices_to_database(devices):
    """Manually save devices to database"""
    saved_count = 0
    
    try:
        conn = sqlite3.connect('assets.db')
        cursor = conn.cursor()
        
        for device in devices:
            try:
                # Prepare device data
                hostname = getattr(device, 'hostname', 'Unknown')
                ip = getattr(device, 'ip_address', '')
                os_name = getattr(device, 'operating_system', '')
                device_type = getattr(device, 'device_type', 'Other Asset')
                
                # Insert or update
                cursor.execute("""
                    INSERT OR REPLACE INTO assets 
                    (hostname, ip_address, operating_system, device_type, last_seen, collection_method)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    hostname,
                    ip,
                    os_name,
                    device_type,
                    datetime.now().isoformat(),
                    'Manual Collection Test'
                ))
                
                saved_count += 1
                print(f"   💾 Saved: {hostname} ({ip})")
                
            except Exception as e:
                print(f"   ❌ Failed to save device: {e}")
        
        conn.commit()
        conn.close()
        
        print(f"✅ Database commit successful: {saved_count} devices saved")
        
    except Exception as e:
        print(f"❌ Database error: {e}")
    
    return saved_count

def test_simple_ping_scan():
    """Run a simple ping-based discovery"""
    print("\n🏓 TESTING SIMPLE PING SCAN")
    print("=" * 40)
    
    try:
        import ipaddress
        import subprocess
        import concurrent.futures
        
        # Define network range
        network = ipaddress.IPv4Network('10.0.21.0/24', strict=False)
        
        def ping_host(ip):
            try:
                result = subprocess.run(
                    ['ping', '-n', '1', '-w', '1000', str(ip)],
                    capture_output=True,
                    text=True,
                    timeout=3
                )
                if result.returncode == 0:
                    return str(ip)
                return None
            except:
                return None
        
        print(f"🔍 Scanning network: {network}")
        live_hosts = []
        
        # Ping scan with threading
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            futures = {executor.submit(ping_host, ip): ip for ip in network.hosts()}
            
            for future in concurrent.futures.as_completed(futures, timeout=60):
                result = future.result()
                if result:
                    live_hosts.append(result)
                    print(f"   ✅ Live: {result}")
        
        print(f"📊 Found {len(live_hosts)} live hosts")
        
        # Create simple device objects and save
        if live_hosts:
            simple_devices = []
            for ip in live_hosts:
                device = type('Device', (), {
                    'hostname': f'device-{ip.replace(".", "-")}',
                    'ip_address': ip,
                    'operating_system': 'Unknown',
                    'device_type': 'Network Device'
                })()
                simple_devices.append(device)
            
            saved_count = save_devices_to_database(simple_devices)
            return saved_count > 0
        
        return False
        
    except Exception as e:
        print(f"❌ Ping scan failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 SIMPLE ASSET COLLECTION TEST")
    print("=" * 50)
    print(f"🕐 Started: {datetime.now()}")
    
    # Check initial database state
    initial_count = check_database_count()
    print(f"📊 Initial database count: {initial_count}")
    
    # Find available collectors
    collectors = check_for_collector_scripts()
    print(f"🔍 Found collectors: {len(collectors)}")
    for collector in collectors[:5]:
        print(f"   • {collector}")
    
    success = False
    
    # Try method 1: Ultra Fast Collector
    print(f"\n{'='*50}")
    if not success:
        success = run_collection_via_ultra_fast()
    
    # Try method 2: Simple ping scan
    if not success:
        print(f"\n{'='*50}")
        success = test_simple_ping_scan()
    
    # Check final database state
    final_count = check_database_count()
    growth = final_count - initial_count
    
    print(f"\n🎯 RESULTS SUMMARY")
    print("=" * 50)
    print(f"📊 Initial count: {initial_count}")
    print(f"📊 Final count: {final_count}")
    print(f"📈 Growth: +{growth} devices")
    
    if growth > 0:
        print(f"✅ SUCCESS! Added {growth} new devices to database")
        print(f"💡 Run 'py simple_db_analysis.py' to see detailed results")
    else:
        print(f"⚠️ No new devices added to database")
        if success:
            print(f"💡 Collection worked but may have found duplicate devices")
        else:
            print(f"💡 Try using the GUI application for a full scan")
    
    print(f"\n🕐 Completed: {datetime.now()}")