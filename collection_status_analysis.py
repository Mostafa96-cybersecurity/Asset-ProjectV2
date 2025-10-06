#!/usr/bin/env python3
"""
Device Collection Status Analysis

Shows which devices have been collected by network scan vs 
which devices exist in database but were never scanned.
"""

import sqlite3
from datetime import datetime

def analyze_collection_status():
    """Analyze which devices have been collected vs not collected"""
    
    print("🔍 DEVICE COLLECTION STATUS ANALYSIS")
    print("=" * 70)
    print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    conn = sqlite3.connect("assets.db")
    cursor = conn.cursor()
    
    # 1. TOTAL DEVICE COUNTS
    print(f"\n📊 TOTAL DEVICE COUNTS")
    print("=" * 50)
    
    cursor.execute("SELECT COUNT(*) FROM assets")
    total_devices = cursor.fetchone()[0]
    print(f"📱 Total Devices in Database: {total_devices}")
    
    # Devices with collection data (from network scan)
    cursor.execute("SELECT COUNT(*) FROM assets WHERE collection_time IS NOT NULL")
    collected_devices = cursor.fetchone()[0]
    print(f"✅ Devices Collected by Network Scan: {collected_devices}")
    
    # Devices without collection data (never scanned)
    never_collected = total_devices - collected_devices
    print(f"❌ Devices Never Collected: {never_collected}")
    
    collection_percentage = (collected_devices / total_devices * 100) if total_devices > 0 else 0
    print(f"📈 Collection Coverage: {collection_percentage:.1f}%")
    
    # 2. DEVICES NEVER COLLECTED
    print(f"\n❌ DEVICES THAT HAVE NEVER BEEN COLLECTED")
    print("=" * 50)
    
    cursor.execute("""
        SELECT ip_address, hostname, status, data_source, created_at, last_updated
        FROM assets 
        WHERE collection_time IS NULL
        ORDER BY ip_address
    """)
    
    never_collected_devices = cursor.fetchall()
    
    if never_collected_devices:
        print(f"Found {len(never_collected_devices)} devices that have never been collected:")
        print(f"\n{'IP Address':<15} | {'Hostname':<35} | {'Status':<10} | {'Source':<20} | {'Last Updated'}")
        print("-" * 120)
        
        for ip, hostname, status, source, created, updated in never_collected_devices[:20]:  # Show first 20
            ip_display = ip if ip else "No IP"
            hostname_display = hostname[:34] if hostname else "No Hostname"
            status_display = status if status else "Unknown"
            source_display = source[:19] if source else "Unknown"
            updated_display = updated[:19] if updated else "Never"
            
            print(f"{ip_display:<15} | {hostname_display:<35} | {status_display:<10} | {source_display:<20} | {updated_display}")
        
        if len(never_collected_devices) > 20:
            print(f"... and {len(never_collected_devices) - 20} more devices")
    else:
        print("🎉 All devices in database have been collected!")
    
    # 3. RECENTLY COLLECTED DEVICES
    print(f"\n✅ RECENTLY COLLECTED DEVICES")
    print("=" * 50)
    
    cursor.execute("""
        SELECT ip_address, hostname, device_classification, collection_time
        FROM assets 
        WHERE collection_time IS NOT NULL
        ORDER BY collection_time DESC
        LIMIT 10
    """)
    
    recent_collected = cursor.fetchall()
    
    print(f"Last 10 devices collected by network scan:")
    print(f"\n{'IP Address':<15} | {'Hostname':<35} | {'Type':<25} | {'Collection Time'}")
    print("-" * 100)
    
    for ip, hostname, device_type, coll_time in recent_collected:
        hostname_display = hostname[:34] if hostname else "Unknown"
        type_display = device_type[:24] if device_type else "Unknown"
        time_display = coll_time[:19] if coll_time else "Unknown"
        
        print(f"{ip:<15} | {hostname_display:<35} | {type_display:<25} | {time_display}")
    
    # 4. DATA SOURCES ANALYSIS
    print(f"\n📊 DATA SOURCES ANALYSIS")
    print("=" * 50)
    
    cursor.execute("""
        SELECT 
            CASE 
                WHEN collection_time IS NOT NULL THEN 'Network Scan'
                WHEN data_source IS NOT NULL THEN data_source
                ELSE 'Unknown Source'
            END as source_type,
            COUNT(*) as count
        FROM assets
        GROUP BY source_type
        ORDER BY count DESC
    """)
    
    data_sources = cursor.fetchall()
    
    print("Device sources breakdown:")
    for source, count in data_sources:
        percentage = (count / total_devices * 100) if total_devices > 0 else 0
        print(f"   📂 {source}: {count} devices ({percentage:.1f}%)")
    
    # 5. DEVICES BY IP RANGE
    print(f"\n🌐 DEVICES BY IP RANGE")
    print("=" * 50)
    
    cursor.execute("""
        SELECT 
            CASE 
                WHEN ip_address LIKE '10.0.21.%' THEN '10.0.21.x (Scanned Network)'
                WHEN ip_address LIKE '10.%' THEN '10.x.x.x (Other Private)'
                WHEN ip_address LIKE '192.168.%' THEN '192.168.x.x (Private)'
                WHEN ip_address IS NULL THEN 'No IP Address'
                ELSE 'Other/Public'
            END as ip_range,
            COUNT(*) as total_count,
            COUNT(CASE WHEN collection_time IS NOT NULL THEN 1 END) as collected_count
        FROM assets
        GROUP BY ip_range
        ORDER BY total_count DESC
    """)
    
    ip_ranges = cursor.fetchall()
    
    print("IP range analysis:")
    for ip_range, total, collected in ip_ranges:
        collection_rate = (collected / total * 100) if total > 0 else 0
        print(f"   🌐 {ip_range}: {collected}/{total} collected ({collection_rate:.1f}%)")
    
    # 6. COLLECTION RECOMMENDATIONS
    print(f"\n💡 RECOMMENDATIONS")
    print("=" * 50)
    
    if never_collected > 0:
        print(f"⚠️  You have {never_collected} devices that have never been scanned")
        print(f"📋 These devices might be:")
        print(f"   • Offline/unreachable devices")
        print(f"   • Devices in different network segments")
        print(f"   • Manually entered devices")
        print(f"   • Devices from imports/other sources")
        
        # Check if there are devices with IPs in different ranges
        cursor.execute("""
            SELECT COUNT(*) FROM assets 
            WHERE collection_time IS NULL 
            AND ip_address IS NOT NULL 
            AND ip_address NOT LIKE '10.0.21.%'
        """)
        other_networks = cursor.fetchone()[0]
        
        if other_networks > 0:
            print(f"\n🔍 SUGGESTED ACTIONS:")
            print(f"   1. Expand network scan to other IP ranges")
            print(f"   2. Check if {other_networks} devices are in different subnets")
            print(f"   3. Run targeted scans on specific IP ranges")
            print(f"   4. Verify network connectivity to missing devices")
    else:
        print(f"🎉 Excellent! All devices have been collected")
        print(f"✅ 100% collection coverage achieved")
    
    conn.close()
    
    # 7. SUMMARY
    print(f"\n🎯 SUMMARY")
    print("=" * 50)
    print(f"📊 Total Devices: {total_devices}")
    print(f"✅ Collected: {collected_devices} ({collection_percentage:.1f}%)")
    print(f"❌ Never Collected: {never_collected}")
    
    if never_collected > 0:
        print(f"⚠️  Collection Status: PARTIAL - Some devices need scanning")
    else:
        print(f"🏆 Collection Status: COMPLETE - All devices scanned")

if __name__ == "__main__":
    analyze_collection_status()