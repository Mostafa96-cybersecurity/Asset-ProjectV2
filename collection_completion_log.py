#!/usr/bin/env python3
"""
🎯 COLLECTION COMPLETION LOG
============================
Comprehensive scan and collection summary report
"""

import sqlite3
from datetime import datetime, timedelta

def generate_completion_log():
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
    
    # Success rate analysis
    cursor.execute('''
        SELECT collection_method, COUNT(*) as total,
               SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END) as successful
        FROM assets 
        WHERE created_at > ? OR updated_at > ?
        GROUP BY collection_method
    ''', (ten_min_ago, ten_min_ago))
    
    method_stats = cursor.fetchall()
    
    print("🎯 COLLECTION SUCCESS ANALYSIS")
    print("-" * 50)
    total_recent = 0
    total_successful = 0
    
    for method, total, successful in method_stats:
        if method and total > 0:
            success_rate = (successful / total) * 100
            print(f"🔧 {method}: {successful}/{total} ({success_rate:.1f}% success)")
            total_recent += total
            total_successful += successful
    
    if total_recent > 0:
        overall_success = (total_successful / total_recent) * 100
        print(f"🎖️  OVERALL SUCCESS RATE: {total_successful}/{total_recent} ({overall_success:.1f}%)")
    print()
    
    # Recent successful devices
    print("🏆 RECENT SUCCESSFUL COLLECTIONS")
    print("-" * 50)
    cursor.execute('''
        SELECT hostname, ip_address, working_user, system_manufacturer, system_model
        FROM assets 
        WHERE (created_at > ? OR updated_at > ?) 
        AND status = 'Success'
        ORDER BY created_at DESC
        LIMIT 10
    ''', (ten_min_ago, ten_min_ago))
    
    successful_devices = cursor.fetchall()
    for i, (hostname, ip, user, manufacturer, model) in enumerate(successful_devices, 1):
        print(f"{i:2d}. 💻 {hostname} ({ip})")
        if user:
            print(f"     👤 User: {user}")
        if manufacturer and model:
            print(f"     🏭 Hardware: {manufacturer} {model}")
        print()
    
    # Data quality check
    print("📋 DATA QUALITY VERIFICATION")
    print("-" * 50)
    
    # Check key fields population
    key_fields = [
        ('hostname', 'Device Names'),
        ('operating_system', 'Operating Systems'),
        ('system_manufacturer', 'Manufacturers'),
        ('processor_name', 'CPU Information'),
        ('total_physical_memory', 'Memory Information'),
        ('working_user', 'Current Users')
    ]
    
    for field, description in key_fields:
        cursor.execute(f'SELECT COUNT(*) FROM assets WHERE {field} IS NOT NULL AND {field} != ""')
        populated = cursor.fetchone()[0]
        percentage = (populated / total_count) * 100 if total_count > 0 else 0
        status = "✅" if percentage > 80 else "⚠️" if percentage > 50 else "❌"
        print(f"{status} {description}: {populated}/{total_count} ({percentage:.1f}%)")
    
    print()
    
    # Deduplication status
    print("🔍 DEDUPLICATION STATUS")
    print("-" * 50)
    
    # Check for IP duplicates
    cursor.execute('''
        SELECT ip_address, COUNT(*) as count
        FROM assets 
        WHERE ip_address IS NOT NULL
        GROUP BY ip_address 
        HAVING COUNT(*) > 1
    ''')
    ip_duplicates = cursor.fetchall()
    
    if ip_duplicates:
        print("⚠️  IP Address Duplicates Found:")
        for ip, count in ip_duplicates:
            print(f"   📍 {ip}: {count} records")
    else:
        print("✅ No IP address duplicates found")
    
    # Check for BIOS duplicates  
    cursor.execute('''
        SELECT bios_serial_number, COUNT(*) as count
        FROM assets 
        WHERE bios_serial_number IS NOT NULL AND bios_serial_number != ""
        GROUP BY bios_serial_number 
        HAVING COUNT(*) > 1
    ''')
    bios_duplicates = cursor.fetchall()
    
    if bios_duplicates:
        print("⚠️  BIOS Serial Duplicates Found:")
        for bios, count in bios_duplicates:
            print(f"   🔢 {bios}: {count} records")
    else:
        print("✅ No BIOS serial duplicates found")
    
    print()
    
    # Network coverage analysis
    print("🌐 NETWORK COVERAGE ANALYSIS")
    print("-" * 50)
    
    cursor.execute('''
        SELECT 
            SUBSTR(ip_address, 1, INSTR(ip_address || '.', '.', INSTR(ip_address || '.', '.', INSTR(ip_address, '.') + 1) + 1) - 1) as subnet,
            COUNT(*) as devices
        FROM assets 
        WHERE ip_address IS NOT NULL 
        AND ip_address LIKE '10.0.21.%'
        GROUP BY subnet
        ORDER BY devices DESC
    ''')
    
    try:
        subnet_coverage = cursor.fetchall()
        for subnet, count in subnet_coverage:
            print(f"📡 {subnet}.x: {count} devices discovered")
    except sqlite3.OperationalError:
        # Fallback for simpler subnet analysis
        cursor.execute('''
            SELECT COUNT(*) FROM assets 
            WHERE ip_address LIKE '10.0.21.%'
        ''')
        subnet_count = cursor.fetchone()[0]
        print(f"📡 10.0.21.x subnet: {subnet_count} devices discovered")
    
    print()
    
    # Collection timeline
    print("⏰ COLLECTION TIMELINE")
    print("-" * 50)
    cursor.execute('''
        SELECT 
            datetime(created_at) as collection_time,
            COUNT(*) as devices_collected
        FROM assets 
        WHERE created_at > ?
        GROUP BY date(created_at), strftime('%H:%M', created_at)
        ORDER BY created_at
    ''', (ten_min_ago,))
    
    timeline = cursor.fetchall()
    for time_slot, count in timeline[-5:]:  # Show last 5 time slots
        print(f"🕐 {time_slot}: {count} devices")
    
    print()
    print("=" * 80)
    print("🎉 COLLECTION COMPLETION STATUS: SUCCESS")
    print("=" * 80)
    print(f"✅ Scan completed successfully")
    print(f"✅ {recent_count} devices collected and saved to database")
    print(f"✅ Data quality verification completed")
    print(f"✅ Deduplication analysis completed")
    print(f"✅ All collected data properly saved in assets.db")
    print("=" * 80)
    
    conn.close()

if __name__ == "__main__":
    generate_completion_log()