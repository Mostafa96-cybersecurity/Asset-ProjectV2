#!/usr/bin/env python3
"""
Full Network Asset Scan
Runs a comprehensive scan of your network and saves all data to database
"""

import sys
import os
import sqlite3
import time
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_database_before():
    """Check database state before scan"""
    try:
        conn = sqlite3.connect('assets.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM assets")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return 0

def run_full_network_scan():
    """Run full network scan using the GUI's collector"""
    print("🚀 STARTING FULL NETWORK ASSET SCAN")
    print("=" * 50)
    
    # Check initial state
    initial_count = check_database_before()
    print(f"📊 Initial database count: {initial_count} devices")
    
    try:
        # Import the GUI's collector system
        from gui.app import AssetCollectionWorker
        from ultra_fast_collector import UltraFastDeviceCollector
        
        print("✅ Asset collection system loaded")
        
        # Configure for full network scan
        collector_kwargs = {
            'ip_ranges': ['10.0.21.1-10.0.21.255'],  # Your main network
            'enable_wmi': True,
            'enable_ssh': True,
            'enable_snmp': True,
            'collection_timeout': 7200,  # 2 hours
            'per_device_timeout': 120,   # 2 minutes per device
            'max_workers': 50,           # Parallel processing
            'save_to_database': True     # Ensure database saving
        }
        
        print("🔧 Configuration:")
        print(f"   📡 Network: {collector_kwargs['ip_ranges']}")
        print(f"   ⏱️ Timeout: {collector_kwargs['collection_timeout']} seconds")
        print(f"   👥 Workers: {collector_kwargs['max_workers']}")
        print(f"   💾 Save to DB: {collector_kwargs['save_to_database']}")
        
        # Create and start worker
        worker = AssetCollectionWorker(UltraFastDeviceCollector, **collector_kwargs)
        
        # Set up monitoring
        devices_collected = []
        
        def on_device_collected(device_data):
            devices_collected.append(device_data)
            print(f"✅ Collected: {device_data.get('hostname', 'Unknown')} ({device_data.get('ip_address', 'No IP')})")
        
        def on_log_message(message):
            print(f"📝 {message}")
        
        def on_scan_complete():
            print("🎉 Scan completed!")
        
        # Connect signals
        worker.device_collected.connect(on_device_collected)
        worker.log_message.connect(on_log_message)
        worker.finished.connect(on_scan_complete)
        
        print("\n🔄 Starting collection...")
        start_time = time.time()
        
        # Start the worker
        worker.start()
        
        # Wait for completion (with timeout)
        if worker.wait(collector_kwargs['collection_timeout'] * 1000):  # Convert to milliseconds
            print("✅ Worker completed successfully")
        else:
            print("⏰ Worker timed out")
            worker.terminate()
            worker.wait(5000)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Check final state
        final_count = check_database_before()
        growth = final_count - initial_count
        
        print("\n📊 SCAN RESULTS:")
        print(f"   ⏱️ Duration: {duration:.1f} seconds")
        print(f"   📈 Database growth: +{growth} devices")
        print(f"   📊 Final count: {final_count} devices")
        print(f"   🔄 Memory collected: {len(devices_collected)} devices")
        
        if growth > 0:
            print(f"   ✅ SUCCESS: Added {growth} new devices to database!")
        else:
            print("   ⚠️ No new devices added - may need to check network range or credentials")
        
        return growth > 0
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Try running from the GUI application instead")
        return False
    except Exception as e:
        print(f"❌ Scan error: {e}")
        return False

def alternative_scan_method():
    """Alternative method using direct collector integration"""
    print("\n🔄 TRYING ALTERNATIVE SCAN METHOD")
    print("=" * 40)
    
    try:
        # Import collector directly
        from ultra_fast_collector import UltraFastDeviceCollector
        from database import Database
        
        print("✅ Direct collector and database loaded")
        
        # Initialize database
        db = Database()
        initial_count = len(db.get_all_assets())
        print(f"📊 Initial count: {initial_count}")
        
        # Initialize collector
        collector = UltraFastDeviceCollector(
            enable_wmi=True,
            enable_ssh=True,
            enable_snmp=True,
            timeout=120
        )
        
        # Scan network range
        ip_range = "10.0.21.1-10.0.21.255"
        print(f"🔍 Scanning range: {ip_range}")
        
        devices = collector.collect_range(ip_range)
        
        print(f"✅ Collected {len(devices)} devices")
        
        # Save to database
        saved_count = 0
        for device in devices:
            try:
                db.add_or_update_asset(device)
                saved_count += 1
                print(f"💾 Saved: {device.hostname} ({device.ip_address})")
            except Exception as e:
                print(f"❌ Failed to save {device.hostname}: {e}")
        
        final_count = len(db.get_all_assets())
        growth = final_count - initial_count
        
        print("\n📊 ALTERNATIVE SCAN RESULTS:")
        print(f"   📈 Database growth: +{growth} devices")
        print(f"   💾 Saved successfully: {saved_count}/{len(devices)}")
        
        return growth > 0
        
    except Exception as e:
        print(f"❌ Alternative scan error: {e}")
        return False

if __name__ == "__main__":
    print("🎯 FULL NETWORK ASSET SCAN")
    print("=" * 50)
    print(f"🕐 Started: {datetime.now()}")
    print()
    
    # Try primary method
    success = run_full_network_scan()
    
    # If primary fails, try alternative
    if not success:
        print("\n🔄 Primary method failed, trying alternative...")
        success = alternative_scan_method()
    
    print("\n🎯 FINAL RESULT:")
    if success:
        print("   ✅ SCAN SUCCESSFUL - New devices added to database!")
        print("   📊 Run 'py simple_db_analysis.py' to see updated results")
    else:
        print("   ❌ SCAN FAILED - No new devices added")
        print("   💡 Try running the scan from the GUI application")
        print("   💡 Or check network connectivity and credentials")
    
    print(f"\n🕐 Completed: {datetime.now()}")