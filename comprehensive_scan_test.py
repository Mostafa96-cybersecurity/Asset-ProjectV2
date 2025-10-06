#!/usr/bin/env python3
"""
Comprehensive Scan Test
Tests the asset scanning system with unlimited timeout settings
"""

import ipaddress  # For IP validation
import sqlite3
import time
import subprocess
import sys
import os
from datetime import datetime
import json

def check_database_before_scan():
    """Check database state before starting scan"""
    print("🔍 PRE-SCAN DATABASE CHECK")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('assets.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM assets")
        count_before = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM assets 
            WHERE last_seen > datetime('now', '-1 hour')
        """)
        recent_count = cursor.fetchone()[0]
        
        print(f"   📊 Current assets: {count_before}")
        print(f"   🕐 Updated in last hour: {recent_count}")
        
        conn.close()
        return count_before
        
    except Exception as e:
        print(f"   ❌ Error checking database: {e}")
        return 0

def check_timeout_config():
    """Verify timeout configuration is set to unlimited"""
    print("\n🔧 TIMEOUT CONFIGURATION CHECK")
    print("=" * 50)
    
    config_files = [
        'unlimited_collection_config.json',
        'collection_timeout_config.json'
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                print(f"   📁 {config_file}:")
                for key, value in config.items():
                    print(f"      • {key}: {value}")
            except:
                print(f"   ❌ Error reading {config_file}")
        else:
            print(f"   ❓ {config_file}: Not found")

def run_enhanced_collector():
    """Run the enhanced ultimate performance collector"""
    print("\n🚀 STARTING ENHANCED COLLECTOR")
    print("=" * 50)
    
    try:
        # Check if the collector exists
        collector_file = 'enhanced_ultimate_performance_collector.py'
        if not os.path.exists(collector_file):
            print(f"   ❌ {collector_file} not found")
            return False
        
        print(f"   ✅ Found {collector_file}")
        print("   🔄 Starting collection process...")
        
        # Start the collector
        start_time = time.time()
        
        result = subprocess.run([
            sys.executable, 
            collector_file
        ], capture_output=True, text=True, timeout=7200)  # 2-hour timeout
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"   ⏱️ Collection completed in {duration:.1f} seconds")
        print(f"   📤 Return code: {result.returncode}")
        
        if result.stdout:
            print("   📋 Output:")
            for line in result.stdout.split('\n')[-10:]:  # Last 10 lines
                if line.strip():
                    print(f"      {line}")
        
        if result.stderr:
            print("   ⚠️ Errors:")
            for line in result.stderr.split('\n')[-5:]:  # Last 5 error lines
                if line.strip():
                    print(f"      {line}")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("   ⏰ Collection timed out after 2 hours")
        return False
    except Exception as e:
        print(f"   ❌ Error running collector: {e}")
        return False

def check_database_after_scan():
    """Check database state after scan completion"""
    print("\n🔍 POST-SCAN DATABASE CHECK")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('assets.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM assets")
        count_after = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM assets 
            WHERE last_seen > datetime('now', '-1 hour')
        """)
        recent_count = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT hostname, ip_address, last_seen 
            FROM assets 
            WHERE last_seen > datetime('now', '-1 hour')
            ORDER BY last_seen DESC 
            LIMIT 5
        """)
        recent_devices = cursor.fetchall()
        
        print(f"   📊 Total assets: {count_after}")
        print(f"   🆕 Updated in last hour: {recent_count}")
        
        if recent_devices:
            print("   🔄 Recently updated devices:")
            for device in recent_devices:
                print(f"      • {device[0]} ({device[1]}) - {device[2]}")
        
        conn.close()
        return count_after, recent_count
        
    except Exception as e:
        print(f"   ❌ Error checking database: {e}")
        return 0, 0

def monitor_scan_progress():
    """Monitor scan progress during execution"""
    print("\n📊 SCAN PROGRESS MONITORING")
    print("=" * 50)
    
    initial_count = check_database_before_scan()
    
    print("\n   Starting enhanced collector...")
    success = run_enhanced_collector()
    
    final_count, recent_updates = check_database_after_scan()
    
    print("\n📈 SCAN RESULTS:")
    print(f"   📊 Before: {initial_count} devices")
    print(f"   📊 After: {final_count} devices")
    print(f"   📈 Growth: +{final_count - initial_count} devices")
    print(f"   🆕 Recent updates: {recent_updates}")
    print(f"   ✅ Success: {success}")
    
    return success, final_count - initial_count

if __name__ == "__main__":
    print("🧪 COMPREHENSIVE SCAN TEST")
    print("=" * 50)
    print(f"🕐 Test started: {datetime.now()}")
    print()
    
    # Check configuration
    check_timeout_config()
    
    # Run the test
    success, growth = monitor_scan_progress()
    
    print("\n🎯 TEST SUMMARY:")
    print("=" * 50)
    if success and growth > 0:
        print("   ✅ SCAN SUCCESSFUL!")
        print(f"   📈 Added {growth} new devices")
        print("   💾 Data successfully saved to database")
    elif success and growth == 0:
        print("   ⚠️ SCAN COMPLETED BUT NO NEW DATA")
        print("   🤔 May indicate all devices already collected")
        print("   🔍 Or scan range might be limited")
    else:
        print("   ❌ SCAN FAILED")
        print("   🔧 Check collector configuration and network settings")
    
    print(f"\n🕐 Test completed: {datetime.now()}")