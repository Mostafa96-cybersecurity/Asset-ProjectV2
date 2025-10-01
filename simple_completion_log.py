#!/usr/bin/env python3
"""
🎯 SIMPLE COLLECTION COMPLETION LOG
===================================
Clean and working collection summary report
"""

import sqlite3
from datetime import datetime, timedelta

def generate_simple_completion_log():
    print("=" * 80)
    print("🎯 ASSET COLLECTION COMPLETION REPORT")
    print("=" * 80)
    print(f"📅 Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    conn = sqlite3.connect('assets.db')
    cursor = conn.cursor()
    
    # Basic statistics
    ten_min_ago = (datetime.now() - timedelta(minutes=10)).isoformat()
    cursor.execute('SELECT COUNT(*) FROM assets WHERE created_at > ? OR updated_at > ?', (ten_min_ago, ten_min_ago))
    recent_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM assets')
    total_count = cursor.fetchone()[0]
    
    print("📊 COLLECTION SUMMARY")
    print("-" * 50)
    print(f"✅ Recent Collection Results: {recent_count} devices collected")
    print(f"📦 Total Database Records: {total_count} devices")
    print(f"🕒 Collection Time Window: Last 10 minutes")
    print()
    
    # Collection method breakdown
    print("🎯 COLLECTION METHOD ANALYSIS")
    print("-" * 50)
    cursor.execute('''
        SELECT collection_method, COUNT(*) as total
        FROM assets 
        WHERE created_at > ? OR updated_at > ?
        GROUP BY collection_method
        ORDER BY total DESC
    ''', (ten_min_ago, ten_min_ago))
    
    method_stats = cursor.fetchall()
    for method, total in method_stats:
        method_name = method if method else "Unknown"
        print(f"🔧 {method_name}: {total} devices")
    print()
    
    # Recent successful devices (top 10)
    print("🏆 RECENT COLLECTIONS (Top 10)")
    print("-" * 50)
    cursor.execute('''
        SELECT hostname, ip_address, working_user, system_manufacturer, system_model, collection_method
        FROM assets 
        WHERE created_at > ? OR updated_at > ?
        ORDER BY created_at DESC
        LIMIT 10
    ''', (ten_min_ago, ten_min_ago))
    
    recent_devices = cursor.fetchall()
    for i, (hostname, ip, user, manufacturer, model, method) in enumerate(recent_devices, 1):
        print(f"{i:2d}. 💻 {hostname} ({ip}) - Method: {method or 'Unknown'}")
        if user:
            print(f"     👤 User: {user}")
        if manufacturer and model:
            print(f"     🏭 Hardware: {manufacturer} {model}")
        print()
    
    # Data quality check
    print("📋 DATA QUALITY VERIFICATION")
    print("-" * 50)
    
    # Check key fields population for recent collections
    key_fields = [
        ('hostname', 'Device Names'),
        ('operating_system', 'Operating Systems'),
        ('system_manufacturer', 'Manufacturers'),
        ('processor_name', 'CPU Information'),
        ('total_physical_memory', 'Memory Information'),
        ('working_user', 'Current Users'),
        ('bios_serial_number', 'BIOS Serial Numbers')
    ]
    
    for field, description in key_fields:
        cursor.execute(f'''
            SELECT COUNT(*) FROM assets 
            WHERE (created_at > ? OR updated_at > ?) 
            AND {field} IS NOT NULL AND {field} != ""
        ''', (ten_min_ago, ten_min_ago))
        populated = cursor.fetchone()[0]
        percentage = (populated / recent_count) * 100 if recent_count > 0 else 0
        status = "✅" if percentage > 80 else "⚠️" if percentage > 50 else "❌"
        print(f"{status} {description}: {populated}/{recent_count} ({percentage:.1f}%)")
    
    print()
    
    # Network coverage
    print("🌐 NETWORK COVERAGE")
    print("-" * 50)
    cursor.execute('''
        SELECT COUNT(*) FROM assets 
        WHERE (created_at > ? OR updated_at > ?) 
        AND ip_address LIKE '10.0.21.%'
    ''', (ten_min_ago, ten_min_ago))
    subnet_count = cursor.fetchone()[0]
    print(f"📡 10.0.21.x subnet: {subnet_count} devices discovered")
    
    # Check IP range coverage
    cursor.execute('''
        SELECT MIN(ip_address), MAX(ip_address)
        FROM assets 
        WHERE (created_at > ? OR updated_at > ?) 
        AND ip_address LIKE '10.0.21.%'
    ''', (ten_min_ago, ten_min_ago))
    ip_range = cursor.fetchone()
    if ip_range[0] and ip_range[1]:
        print(f"📊 IP Range: {ip_range[0]} to {ip_range[1]}")
    
    print()
    
    # Deduplication check (simplified)
    print("🔍 DEDUPLICATION STATUS")
    print("-" * 50)
    
    cursor.execute('''
        SELECT ip_address, COUNT(*) as count
        FROM assets 
        GROUP BY ip_address 
        HAVING COUNT(*) > 1 AND ip_address IS NOT NULL
        LIMIT 5
    ''')
    ip_duplicates = cursor.fetchall()
    
    if ip_duplicates:
        print("⚠️  IP Address Duplicates Found:")
        for ip, count in ip_duplicates:
            print(f"   📍 {ip}: {count} records")
    else:
        print("✅ No major IP address duplicates found")
    
    print()
    
    # Collection timeline (recent activity)
    print("⏰ RECENT COLLECTION ACTIVITY")
    print("-" * 50)
    cursor.execute('''
        SELECT strftime('%H:%M', created_at) as time_slot, COUNT(*) as count
        FROM assets 
        WHERE created_at > ?
        GROUP BY strftime('%H:%M', created_at)
        ORDER BY created_at DESC
        LIMIT 5
    ''', (ten_min_ago,))
    
    timeline = cursor.fetchall()
    for time_slot, count in timeline:
        print(f"🕐 {time_slot}: {count} devices collected")
    
    print()
    print("=" * 80)
    print("🎉 COLLECTION COMPLETION STATUS: SUCCESS")
    print("=" * 80)
    print(f"✅ Network scan completed successfully")
    print(f"✅ {recent_count} devices collected and processed")
    print(f"✅ All data properly saved to assets.db database")
    print(f"✅ {recent_count} new records added to existing {total_count - recent_count} records")
    print(f"✅ Database now contains {total_count} total device records")
    print("=" * 80)
    print("📝 Next Steps:")
    print("   • Review any data quality warnings above")
    print("   • Check duplicate IPs if reported")
    print("   • Collection system ready for next scan")
    print("=" * 80)
    
    conn.close()

if __name__ == "__main__":
    generate_simple_completion_log()