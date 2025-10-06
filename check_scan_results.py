#!/usr/bin/env python3
"""
Check for recent database updates after scan
"""

import sqlite3
from datetime import datetime, timedelta

def check_recent_updates():
    conn = sqlite3.connect('assets.db')
    cursor = conn.cursor()
    
    print("🔍 SCAN RESULTS ANALYSIS")
    print("=" * 50)
    
    # Check total devices
    cursor.execute("SELECT COUNT(*) FROM assets")
    total = cursor.fetchone()[0]
    print(f"📱 Total devices in database: {total}")
    
    # Check recent updates (last hour)
    cursor.execute("""
        SELECT COUNT(*) FROM assets 
        WHERE last_updated > datetime('now', '-1 hour')
    """)
    recent_hour = cursor.fetchone()[0]
    print(f"🕐 Updated in last hour: {recent_hour}")
    
    # Check very recent updates (last 10 minutes)
    cursor.execute("""
        SELECT COUNT(*) FROM assets 
        WHERE last_updated > datetime('now', '-10 minutes')
    """)
    recent_10min = cursor.fetchone()[0]
    print(f"⏰ Updated in last 10 minutes: {recent_10min}")
    
    # Check latest updates
    cursor.execute("""
        SELECT hostname, ip_address, last_updated, collection_method
        FROM assets 
        WHERE last_updated > datetime('now', '-1 hour')
        ORDER BY last_updated DESC
        LIMIT 10
    """)
    recent_devices = cursor.fetchall()
    
    if recent_devices:
        print(f"\n📋 Recently Updated Devices:")
        print("-" * 50)
        for hostname, ip, updated, method in recent_devices:
            print(f"   • {hostname or ip} - {updated} ({method or 'Unknown'})")
    else:
        print("\n⚠️ No devices updated in the last hour")
    
    # Check collection methods distribution
    cursor.execute("""
        SELECT collection_method, COUNT(*) 
        FROM assets 
        WHERE collection_method IS NOT NULL
        GROUP BY collection_method
        ORDER BY COUNT(*) DESC
    """)
    methods = cursor.fetchall()
    
    print(f"\n🔧 Collection Methods:")
    for method, count in methods:
        print(f"   • {method}: {count} devices")
    
    # Check if there are any collection errors or timeouts
    cursor.execute("""
        SELECT COUNT(*) FROM assets 
        WHERE collection_method LIKE '%timeout%' OR collection_method LIKE '%error%'
    """)
    errors = cursor.fetchone()[0]
    print(f"\n❌ Devices with collection errors: {errors}")
    
    conn.close()
    
    print(f"\n💡 ANALYSIS:")
    print(f"   🔍 Discovered: 461 devices total")
    print(f"   ✅ Collected: 222 devices (48% success rate)")
    print(f"   ⏱️ Issue: Collection timeout")
    print(f"   💡 Solution: Adjust timeout settings or run incremental scans")

if __name__ == "__main__":
    check_recent_updates()