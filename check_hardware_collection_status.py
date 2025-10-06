#!/usr/bin/env python3
"""
CHECK HARDWARE COLLECTION STATUS

This tool analyzes what happened with hardware data collection and hostname mismatch feature.
"""

import sqlite3
import json
from datetime import datetime

def check_hardware_collection_status():
    """Check current hardware collection status and hostname mismatch feature"""
    
    print("🔍 CHECKING HARDWARE COLLECTION STATUS")
    print("=" * 70)
    print(f"🕐 Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    conn = sqlite3.connect("assets.db")
    cursor = conn.cursor()
    
    # Check database structure
    cursor.execute("PRAGMA table_info(assets)")
    columns = [col[1] for col in cursor.fetchall()]
    
    print("📊 DATABASE STRUCTURE ANALYSIS:")
    print("-" * 50)
    
    # Hardware-related columns
    hardware_columns = [col for col in columns if any(keyword in col.lower() for keyword in 
                       ['processor', 'memory', 'cpu', 'ram', 'disk', 'hardware', 'bios', 'serial', 'mac', 'motherboard'])]
    
    print(f"🔧 Hardware-related columns ({len(hardware_columns)}):")
    for col in sorted(hardware_columns):
        print(f"   • {col}")
    
    # Check for hostname mismatch columns
    hostname_columns = [col for col in columns if any(keyword in col.lower() for keyword in 
                       ['hostname', 'mismatch', 'name', 'computer'])]
    
    print(f"\n🏷️ Hostname-related columns ({len(hostname_columns)}):")
    for col in sorted(hostname_columns):
        print(f"   • {col}")
    
    # Check total devices
    cursor.execute("SELECT COUNT(*) FROM assets")
    total_devices = cursor.fetchone()[0]
    
    print(f"\n📱 TOTAL DEVICES: {total_devices}")
    
    # Check hardware data completeness
    print(f"\n🔧 HARDWARE DATA COMPLETENESS:")
    print("-" * 50)
    
    key_hardware_fields = ['processor_name', 'total_physical_memory', 'mac_address', 'system_manufacturer', 'serial_number']
    
    for field in key_hardware_fields:
        if field in columns:
            cursor.execute(f"SELECT COUNT(*) FROM assets WHERE {field} IS NOT NULL AND {field} != ''")
            filled_count = cursor.fetchone()[0]
            percentage = (filled_count / total_devices * 100) if total_devices > 0 else 0
            print(f"   • {field}: {filled_count}/{total_devices} ({percentage:.1f}%)")
        else:
            print(f"   • {field}: Column not found")
    
    # Check recent collection activity
    print(f"\n📅 RECENT COLLECTION ACTIVITY:")
    print("-" * 50)
    
    # Check for collection timestamps
    timestamp_columns = [col for col in columns if any(keyword in col.lower() for keyword in 
                        ['last_scan', 'last_update', 'collection', 'timestamp'])]
    
    for col in timestamp_columns:
        cursor.execute(f"SELECT COUNT(*) FROM assets WHERE {col} IS NOT NULL AND {col} >= datetime('now', '-7 days')")
        recent_count = cursor.fetchone()[0]
        print(f"   • {col}: {recent_count} devices updated in last 7 days")
    
    # Check hostname mismatch feature
    print(f"\n🏷️ HOSTNAME MISMATCH ANALYSIS:")
    print("-" * 50)
    
    # Check if hostname mismatch columns exist
    mismatch_indicators = ['hostname_mismatch', 'name_mismatch', 'computer_name_mismatch']
    
    for indicator in mismatch_indicators:
        if indicator in columns:
            cursor.execute(f"SELECT COUNT(*) FROM assets WHERE {indicator} IS NOT NULL")
            total_checked = cursor.fetchone()[0]
            cursor.execute(f"SELECT COUNT(*) FROM assets WHERE {indicator} = 'True' OR {indicator} = '1' OR {indicator} = 'Yes'")
            mismatch_count = cursor.fetchone()[0]
            print(f"   • {indicator}: {mismatch_count} mismatches out of {total_checked} checked")
        else:
            print(f"   • {indicator}: Column not found")
    
    # Check for multiple hostname fields
    hostname_fields = ['hostname', 'computer_name', 'dns_name', 'netbios_name']
    existing_hostname_fields = [field for field in hostname_fields if field in columns]
    
    print(f"\n🏷️ HOSTNAME COMPARISON ANALYSIS:")
    print("-" * 50)
    
    if len(existing_hostname_fields) >= 2:
        print(f"Available hostname fields: {', '.join(existing_hostname_fields)}")
        
        # Compare different hostname fields
        cursor.execute(f"""
            SELECT hostname, computer_name, 
                   CASE WHEN hostname != computer_name THEN 'MISMATCH' ELSE 'MATCH' END as status,
                   COUNT(*) as count
            FROM assets 
            WHERE hostname IS NOT NULL AND computer_name IS NOT NULL
            GROUP BY hostname, computer_name, status
            ORDER BY count DESC
            LIMIT 10
        """)
        
        results = cursor.fetchall()
        if results:
            print("\nTop hostname comparison results:")
            for hostname, computer_name, status, count in results:
                print(f"   • {status}: '{hostname}' vs '{computer_name}' ({count} devices)")
    else:
        print(f"Not enough hostname fields for comparison. Available: {existing_hostname_fields}")
    
    # Check device status distribution
    print(f"\n📊 DEVICE STATUS DISTRIBUTION:")
    print("-" * 50)
    
    if 'device_status' in columns:
        cursor.execute("SELECT device_status, COUNT(*) FROM assets GROUP BY device_status ORDER BY COUNT(*) DESC")
        status_results = cursor.fetchall()
        for status, count in status_results:
            percentage = (count / total_devices * 100) if total_devices > 0 else 0
            print(f"   • {status or 'NULL'}: {count} devices ({percentage:.1f}%)")
    
    # Check collection methods
    print(f"\n🔧 COLLECTION METHODS:")
    print("-" * 50)
    
    method_columns = [col for col in columns if 'collection' in col.lower() or 'method' in col.lower()]
    
    for col in method_columns:
        cursor.execute(f"SELECT {col}, COUNT(*) FROM assets WHERE {col} IS NOT NULL GROUP BY {col} ORDER BY COUNT(*) DESC LIMIT 5")
        method_results = cursor.fetchall()
        if method_results:
            print(f"\n{col}:")
            for method, count in method_results:
                print(f"   • {method}: {count} devices")
    
    # Check for recent errors or issues
    print(f"\n⚠️ POTENTIAL ISSUES:")
    print("-" * 50)
    
    # Check for devices with no hardware data at all
    hardware_check_fields = ['processor_name', 'total_physical_memory', 'mac_address']
    available_hw_fields = [field for field in hardware_check_fields if field in columns]
    
    if available_hw_fields:
        where_clause = " AND ".join([f"({field} IS NULL OR {field} = '')" for field in available_hw_fields])
        cursor.execute(f"SELECT COUNT(*) FROM assets WHERE {where_clause}")
        no_hardware_count = cursor.fetchone()[0]
        percentage = (no_hardware_count / total_devices * 100) if total_devices > 0 else 0
        print(f"   • Devices with no hardware data: {no_hardware_count}/{total_devices} ({percentage:.1f}%)")
    
    # Check for devices with offline status but recent activity
    if 'device_status' in columns and 'last_seen' in columns:
        cursor.execute("""
            SELECT COUNT(*) FROM assets 
            WHERE device_status = 'offline' 
            AND last_seen >= datetime('now', '-24 hours')
        """)
        recent_offline = cursor.fetchone()[0]
        print(f"   • Recently seen but marked offline: {recent_offline} devices")
    
    # Summary
    print(f"\n📋 SUMMARY:")
    print("-" * 50)
    
    # Calculate overall hardware collection success
    if available_hw_fields:
        cursor.execute(f"""
            SELECT COUNT(*) FROM assets 
            WHERE {' OR '.join([f"({field} IS NOT NULL AND {field} != '')" for field in available_hw_fields])}
        """)
        with_some_hardware = cursor.fetchone()[0]
        hw_success_rate = (with_some_hardware / total_devices * 100) if total_devices > 0 else 0
        
        print(f"✅ Hardware collection success rate: {hw_success_rate:.1f}%")
        
        if hw_success_rate > 80:
            print("🎉 EXCELLENT: Hardware data collection is working very well!")
        elif hw_success_rate > 60:
            print("✅ GOOD: Hardware data collection is working well")
        elif hw_success_rate > 40:
            print("⚠️ MODERATE: Hardware data collection needs improvement")
        else:
            print("❌ POOR: Hardware data collection has significant issues")
    
    # Check if hostname mismatch feature is working
    hostname_mismatch_working = any(indicator in columns for indicator in mismatch_indicators)
    
    if hostname_mismatch_working:
        print("✅ Hostname mismatch feature: Columns present")
    else:
        print("⚠️ Hostname mismatch feature: Columns not found")
    
    conn.close()

if __name__ == "__main__":
    check_hardware_collection_status()