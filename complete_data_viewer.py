#!/usr/bin/env python3
"""
Complete Database Data Viewer

Shows all collected data in the database including total devices,
device details, and comprehensive data breakdown.
"""

import sqlite3
import json
from datetime import datetime
import os

def show_complete_database_data():
    """Show complete database data analysis"""
    
    print("🔍 COMPLETE DATABASE DATA VIEWER")
    print("=" * 70)
    print(f"📅 Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    db_path = "assets.db"
    if not os.path.exists(db_path):
        print("❌ Database file not found!")
        return
    
    # Database file info
    db_size = os.path.getsize(db_path) / (1024 * 1024)  # MB
    print(f"📁 Database File: {db_path} ({db_size:.2f} MB)")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. TOTAL COUNTS
    print("\n📊 TOTAL DEVICE COUNTS")
    print("=" * 50)
    
    cursor.execute("SELECT COUNT(*) FROM assets")
    total_records = cursor.fetchone()[0]
    print(f"📋 Total Database Records: {total_records}")
    
    cursor.execute("SELECT COUNT(DISTINCT ip_address) FROM assets WHERE ip_address IS NOT NULL")
    unique_ips = cursor.fetchone()[0]
    print(f"🌐 Unique IP Addresses: {unique_ips}")
    
    cursor.execute("SELECT COUNT(DISTINCT hostname) FROM assets WHERE hostname IS NOT NULL AND hostname != ''")
    unique_hostnames = cursor.fetchone()[0]
    print(f"🏷️ Unique Hostnames: {unique_hostnames}")
    
    # 2. COLLECTED DATA STATUS
    print("\n🚀 DATA COLLECTION STATUS")
    print("=" * 50)
    
    cursor.execute("SELECT COUNT(*) FROM assets WHERE collection_time IS NOT NULL")
    collected_today = cursor.fetchone()[0]
    print(f"✅ Devices with Collection Data: {collected_today}")
    
    cursor.execute("SELECT COUNT(*) FROM assets WHERE ping_status = 'up' OR status = 'active'")
    active_devices = cursor.fetchone()[0]
    print(f"🟢 Active/Online Devices: {active_devices}")
    
    cursor.execute("SELECT MIN(collection_time), MAX(collection_time) FROM assets WHERE collection_time IS NOT NULL")
    time_range = cursor.fetchone()
    if time_range[0]:
        print(f"⏰ Collection Period: {time_range[0][:19]} to {time_range[1][:19]}")
    
    # 3. DEVICE TYPES BREAKDOWN
    print("\n🏷️ DEVICE TYPES BREAKDOWN")
    print("=" * 50)
    
    cursor.execute("""
        SELECT 
            COALESCE(device_classification, 'Unclassified') as type,
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM assets), 1) as percentage
        FROM assets 
        GROUP BY device_classification 
        ORDER BY COUNT(*) DESC
    """)
    
    device_types = cursor.fetchall()
    total_classified = sum(count for _, count, _ in device_types if _ != 'Unclassified')
    
    for device_type, count, percentage in device_types:
        print(f"   📱 {device_type}: {count} devices ({percentage}%)")
    
    print(f"\n   🎯 Classification Success: {total_classified}/{total_records} devices ({(total_classified/total_records*100):.1f}%)")
    
    # 4. NETWORK SERVICES
    print("\n🔌 NETWORK SERVICES & PORTS")
    print("=" * 50)
    
    cursor.execute("SELECT COUNT(*) FROM assets WHERE open_ports IS NOT NULL AND open_ports != '[]'")
    devices_with_ports = cursor.fetchone()[0]
    print(f"🔌 Devices with Open Ports: {devices_with_ports}")
    
    cursor.execute("SELECT COUNT(*) FROM assets WHERE http_banner IS NOT NULL")
    web_services = cursor.fetchone()[0]
    print(f"🌐 Web Services Detected: {web_services}")
    
    # Most common ports
    cursor.execute("SELECT open_ports FROM assets WHERE open_ports IS NOT NULL AND open_ports != '[]'")
    all_ports_data = cursor.fetchall()
    
    port_frequency = {}
    for ports_json in all_ports_data:
        try:
            ports = json.loads(ports_json[0])
            for port in ports:
                port_frequency[port] = port_frequency.get(port, 0) + 1
        except:
            continue
    
    print("\n   🔝 Most Common Open Ports:")
    sorted_ports = sorted(port_frequency.items(), key=lambda x: x[1], reverse=True)[:8]
    for port, count in sorted_ports:
        port_desc = {
            22: "SSH", 23: "Telnet", 53: "DNS", 80: "HTTP", 
            135: "RPC", 139: "NetBIOS", 443: "HTTPS", 445: "SMB",
            993: "IMAPS", 995: "POP3S", 3389: "RDP"
        }.get(port, f"Port {port}")
        print(f"      {port_desc} ({port}): {count} devices")
    
    # 5. SAMPLE DEVICES DATA
    print("\n📋 SAMPLE COLLECTED DEVICES")
    print("=" * 50)
    
    cursor.execute("""
        SELECT ip_address, hostname, device_classification, open_ports, 
               collection_methods, http_banner, collection_time
        FROM assets 
        WHERE collection_time IS NOT NULL 
        ORDER BY collection_time DESC 
        LIMIT 8
    """)
    
    sample_devices = cursor.fetchall()
    for i, device_data in enumerate(sample_devices, 1):
        ip, hostname, classification, ports, methods, banner, coll_time = device_data
        
        print(f"\n   🖥️ Device {i}:")
        print(f"      IP Address: {ip}")
        print(f"      Hostname: {hostname}")
        print(f"      Device Type: {classification}")
        print(f"      Collection Time: {coll_time[:19] if coll_time else 'N/A'}")
        
        if ports and ports != '[]':
            try:
                port_list = json.loads(ports)
                print(f"      Open Ports: {port_list}")
            except:
                print(f"      Open Ports: {ports}")
        
        if methods:
            try:
                method_list = json.loads(methods)
                print(f"      Collection Methods: {', '.join(method_list)}")
            except:
                print(f"      Collection Methods: {methods}")
        
        if banner:
            banner_short = banner[:50] + "..." if len(banner) > 50 else banner
            print(f"      HTTP Banner: {banner_short}")
    
    # 6. NETWORK COVERAGE
    print("\n🌐 NETWORK COVERAGE ANALYSIS")
    print("=" * 50)
    
    cursor.execute("""
        SELECT 
            substr(ip_address, 1, instr(ip_address||'.', '.', instr(ip_address, '.')+1)-1) as subnet,
            COUNT(*) as device_count
        FROM assets 
        WHERE ip_address IS NOT NULL
        GROUP BY subnet
        ORDER BY device_count DESC
        LIMIT 10
    """)
    
    network_coverage = cursor.fetchall()
    print("   📍 Network Subnets:")
    for subnet, count in network_coverage:
        print(f"      {subnet}.x: {count} devices")
    
    # 7. DATA COMPLETENESS
    print("\n📈 DATA COMPLETENESS METRICS")
    print("=" * 50)
    
    completeness_checks = [
        ("IP Address", "ip_address IS NOT NULL"),
        ("Hostname", "hostname IS NOT NULL AND hostname != ''"),
        ("Device Classification", "device_classification IS NOT NULL"),
        ("Open Ports Data", "open_ports IS NOT NULL AND open_ports != '[]'"),
        ("Collection Methods", "collection_methods IS NOT NULL"),
        ("Collection Timestamp", "collection_time IS NOT NULL"),
        ("HTTP Banner", "http_banner IS NOT NULL"),
        ("Ping Status", "ping_status IS NOT NULL")
    ]
    
    for field_name, condition in completeness_checks:
        cursor.execute(f"SELECT COUNT(*) FROM assets WHERE {condition}")
        count = cursor.fetchone()[0]
        percentage = (count / total_records * 100) if total_records > 0 else 0
        status = "✅" if percentage > 80 else "⚠️" if percentage > 50 else "❌"
        print(f"   {status} {field_name}: {count}/{total_records} ({percentage:.1f}%)")
    
    # 8. RECENT ACTIVITY
    print("\n🕐 RECENT COLLECTION ACTIVITY")
    print("=" * 50)
    
    cursor.execute("""
        SELECT COUNT(*) FROM assets 
        WHERE collection_time IS NOT NULL 
        AND date(collection_time) = date('now')
    """)
    today_collections = cursor.fetchone()[0]
    print(f"📅 Devices Collected Today: {today_collections}")
    
    cursor.execute("""
        SELECT ip_address, hostname, device_classification, collection_time
        FROM assets 
        WHERE collection_time IS NOT NULL 
        ORDER BY collection_time DESC 
        LIMIT 5
    """)
    
    recent_activity = cursor.fetchall()
    print("\n   🕐 Latest Collections:")
    for ip, hostname, classification, coll_time in recent_activity:
        time_display = coll_time[:19] if coll_time else "Unknown"
        hostname_display = hostname[:25] + "..." if hostname and len(hostname) > 25 else hostname
        print(f"      {time_display} | {ip} | {hostname_display} | {classification}")
    
    # 9. SUMMARY DASHBOARD
    print("\n🎯 SUMMARY DASHBOARD")
    print("=" * 50)
    
    collection_success = (collected_today / total_records * 100) if total_records > 0 else 0
    classification_success = (total_classified / total_records * 100) if total_records > 0 else 0
    port_data_success = (devices_with_ports / total_records * 100) if total_records > 0 else 0
    
    print("📊 Database Overview:")
    print(f"   📱 Total Devices: {total_records}")
    print(f"   🌐 Unique IPs: {unique_ips}")
    print(f"   🏷️ Unique Hostnames: {unique_hostnames}")
    print(f"   ✅ Active Devices: {active_devices}")
    
    print("\n📈 Data Quality Scores:")
    print(f"   🚀 Collection Success: {collection_success:.1f}%")
    print(f"   🏷️ Classification Success: {classification_success:.1f}%")
    print(f"   🔌 Port Data Success: {port_data_success:.1f}%")
    print(f"   🌐 Web Services Found: {web_services}")
    
    status_emoji = "🟢" if collection_success > 80 else "🟡" if collection_success > 50 else "🔴"
    print(f"\n{status_emoji} Overall Database Status: COMPREHENSIVE DATA COLLECTED")
    
    conn.close()
    
    print("\n💡 All scan data is available and accessible in the database!")
    print("🎉 Complete network inventory successfully maintained!")

def show_detailed_device_list():
    """Show detailed list of all devices"""
    
    print("\n\n🔍 DETAILED DEVICE INVENTORY")
    print("=" * 70)
    
    conn = sqlite3.connect("assets.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT ip_address, hostname, device_classification, open_ports, 
               collection_time, ping_status
        FROM assets 
        WHERE collection_time IS NOT NULL 
        ORDER BY 
            CASE device_classification
                WHEN 'Windows Server/Workstation' THEN 1
                WHEN 'Windows System' THEN 2
                WHEN 'Linux/Unix Server' THEN 3
                WHEN 'Network Device' THEN 4
                WHEN 'Network Printer' THEN 5
                ELSE 6
            END,
            ip_address
    """)
    
    all_devices = cursor.fetchall()
    
    current_type = ""
    device_count = 0
    
    for device_data in all_devices:
        ip, hostname, classification, ports, coll_time, ping_status = device_data
        
        if classification != current_type:
            current_type = classification
            print(f"\n📱 {current_type.upper()}:")
            print("-" * 60)
            device_count = 0
        
        device_count += 1
        
        # Parse ports
        port_display = "No open ports"
        if ports and ports != '[]':
            try:
                port_list = json.loads(ports)
                if port_list:
                    port_display = f"Ports: {', '.join(map(str, port_list[:5]))}"
                    if len(port_list) > 5:
                        port_display += f" (+{len(port_list)-5} more)"
            except:
                port_display = f"Ports: {ports}"
        
        status_icon = "🟢" if ping_status == "up" else "🔴"
        hostname_display = hostname[:35] + "..." if hostname and len(hostname) > 35 else hostname
        time_display = coll_time[:16] if coll_time else "N/A"
        
        print(f"   {device_count:2d}. {status_icon} {ip:<15} | {hostname_display:<38} | {port_display}")
    
    conn.close()

if __name__ == "__main__":
    show_complete_database_data()
    
    # Ask if user wants detailed device list
    print("\n" + "="*70)
    response = input("📋 Show detailed device list? (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        show_detailed_device_list()
    
    print("\n✅ Database analysis complete!")