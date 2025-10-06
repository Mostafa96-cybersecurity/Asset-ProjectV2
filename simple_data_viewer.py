#!/usr/bin/env python3
"""
Simple Database Data Viewer - Fixed Version

Shows all collected data in the database.
"""

import sqlite3
import json
from datetime import datetime
import os

def show_database_summary():
    """Show database summary and all collected data"""
    
    print("🔍 DATABASE DATA SUMMARY")
    print("=" * 60)
    print(f"📅 Report Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    conn = sqlite3.connect("assets.db")
    cursor = conn.cursor()
    
    # Basic counts
    cursor.execute("SELECT COUNT(*) FROM assets")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM assets WHERE collection_time IS NOT NULL")
    collected = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT ip_address) FROM assets WHERE ip_address IS NOT NULL")
    unique_ips = cursor.fetchone()[0]
    
    print(f"\n📊 BASIC STATISTICS")
    print(f"   Total Records: {total}")
    print(f"   Devices with Collection Data: {collected}")
    print(f"   Unique IP Addresses: {unique_ips}")
    
    # Device types
    print(f"\n🏷️ DEVICE TYPES")
    cursor.execute("""
        SELECT device_classification, COUNT(*) 
        FROM assets 
        WHERE device_classification IS NOT NULL
        GROUP BY device_classification 
        ORDER BY COUNT(*) DESC
    """)
    
    device_types = cursor.fetchall()
    for device_type, count in device_types:
        print(f"   {device_type}: {count}")
    
    # Network activity
    print(f"\n🌐 NETWORK STATUS")
    cursor.execute("SELECT COUNT(*) FROM assets WHERE open_ports IS NOT NULL AND open_ports != '[]'")
    with_ports = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM assets WHERE http_banner IS NOT NULL")
    web_services = cursor.fetchone()[0]
    
    print(f"   Devices with Open Ports: {with_ports}")
    print(f"   Web Services Found: {web_services}")
    
    # Show all collected devices
    print(f"\n📋 ALL COLLECTED DEVICES")
    print("=" * 60)
    
    cursor.execute("""
        SELECT ip_address, hostname, device_classification, open_ports, collection_time
        FROM assets 
        WHERE collection_time IS NOT NULL 
        ORDER BY ip_address
    """)
    
    all_devices = cursor.fetchall()
    
    print(f"{'IP Address':<15} | {'Hostname':<35} | {'Type':<25} | {'Ports'}")
    print("-" * 100)
    
    for ip, hostname, device_type, ports, coll_time in all_devices:
        hostname_short = hostname[:34] if hostname else "Unknown"
        device_type_short = device_type[:24] if device_type else "Unknown"
        
        port_info = "None"
        if ports and ports != '[]':
            try:
                port_list = json.loads(ports)
                if port_list:
                    port_info = ', '.join(map(str, port_list[:4]))
                    if len(port_list) > 4:
                        port_info += "..."
            except:
                port_info = "Error"
        
        print(f"{ip:<15} | {hostname_short:<35} | {device_type_short:<25} | {port_info}")
    
    conn.close()
    
    print(f"\n✅ Total: {len(all_devices)} devices with complete collection data")
    print(f"🎯 All scan data successfully stored in database!")

if __name__ == "__main__":
    show_database_summary()