#!/usr/bin/env python3
"""
Database Columns and Data Analysis Tool

Shows exactly which columns exist and what data was collected.
"""

import sqlite3
import json
from datetime import datetime

def show_database_columns_and_data():
    """Show all database columns and collected data details"""
    
    print("🔍 DATABASE COLUMNS & COLLECTED DATA ANALYSIS")
    print("=" * 70)
    print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    conn = sqlite3.connect("assets.db")
    cursor = conn.cursor()
    
    # 1. SHOW ALL DATABASE COLUMNS
    print("\n📋 ALL DATABASE COLUMNS")
    print("=" * 50)
    
    cursor.execute("PRAGMA table_info(assets)")
    all_columns = cursor.fetchall()
    
    print(f"Total Columns in Database: {len(all_columns)}")
    print("\nComplete Column List:")
    
    for i, (col_id, name, data_type, not_null, default, pk) in enumerate(all_columns, 1):
        pk_indicator = " (PRIMARY KEY)" if pk else ""
        print(f"   {i:3d}. {name:<30} | {data_type:<10} {pk_indicator}")
    
    # 2. CHECK WHICH COLUMNS HAVE DATA
    print("\n\n📊 COLUMNS WITH ACTUAL DATA")
    print("=" * 50)
    
    cursor.execute("SELECT COUNT(*) FROM assets")
    total_records = cursor.fetchone()[0]
    
    print(f"Total Records: {total_records}")
    print("\nColumns containing data:")
    print(f"{'Column Name':<35} | {'Records':<8} | {'%':<6} | {'Sample Data'}")
    print("-" * 95)
    
    columns_with_data = []
    
    for col_id, name, data_type, not_null, default, pk in all_columns:
        if name == 'id':  # Skip ID column
            continue
            
        try:
            # Check how many records have data in this column
            cursor.execute(f"SELECT COUNT(*) FROM assets WHERE {name} IS NOT NULL AND {name} != ''")
            count = cursor.fetchone()[0]
            
            if count > 0:
                percentage = (count / total_records * 100)
                
                # Get sample data
                cursor.execute(f"SELECT {name} FROM assets WHERE {name} IS NOT NULL AND {name} != '' LIMIT 1")
                sample_result = cursor.fetchone()
                sample = sample_result[0] if sample_result else ""
                
                # Format sample data
                if isinstance(sample, str):
                    if len(sample) > 35:
                        sample = sample[:32] + "..."
                    # Clean up JSON-like data
                    if sample.startswith('[') or sample.startswith('{'):
                        try:
                            parsed = json.loads(sample)
                            if isinstance(parsed, list) and len(parsed) > 3:
                                sample = f"[{', '.join(map(str, parsed[:3]))}...]"
                        except:
                            pass
                
                columns_with_data.append((name, count, percentage))
                print(f"{name:<35} | {count:<8} | {percentage:>5.1f}% | {sample}")
        except Exception:
            # Skip columns that cause errors
            continue
    
    # 3. SPECIFICALLY COLLECTED SCAN DATA
    print("\n\n🚀 NETWORK SCAN COLLECTED DATA")
    print("=" * 50)
    
    scan_columns = [
        'ip_address', 'hostname', 'device_classification', 'open_ports',
        'collection_methods', 'http_banner', 'collection_time', 'ping_status'
    ]
    
    cursor.execute("SELECT COUNT(*) FROM assets WHERE collection_time IS NOT NULL")
    scan_records = cursor.fetchone()[0]
    print(f"Records from Network Scan: {scan_records}")
    
    print("\nScan Data Breakdown:")
    for column in scan_columns:
        cursor.execute(f"SELECT COUNT(*) FROM assets WHERE {column} IS NOT NULL AND {column} != ''")
        count = cursor.fetchone()[0]
        percentage = (count / scan_records * 100) if scan_records > 0 else 0
        
        # Get sample from scan data
        cursor.execute(f"""
            SELECT {column} FROM assets 
            WHERE collection_time IS NOT NULL AND {column} IS NOT NULL AND {column} != ''
            LIMIT 1
        """)
        sample_result = cursor.fetchone()
        sample = sample_result[0] if sample_result else "No data"
        
        if isinstance(sample, str) and len(sample) > 30:
            sample = sample[:27] + "..."
        
        status = "✅" if percentage > 90 else "⚠️" if percentage > 50 else "❌"
        print(f"   {status} {column:<25}: {count}/{scan_records} ({percentage:>5.1f}%) | {sample}")
    
    # 4. DETAILED DATA EXAMPLES
    print("\n\n📋 DETAILED DATA EXAMPLES")
    print("=" * 50)
    
    cursor.execute("""
        SELECT ip_address, hostname, device_classification, open_ports, 
               collection_methods, http_banner
        FROM assets 
        WHERE collection_time IS NOT NULL
        ORDER BY collection_time DESC
        LIMIT 5
    """)
    
    examples = cursor.fetchall()
    
    for i, (ip, hostname, classification, ports, methods, banner) in enumerate(examples, 1):
        print(f"\nExample {i}:")
        print(f"   📍 IP: {ip}")
        print(f"   🏷️ Hostname: {hostname}")
        print(f"   📱 Type: {classification}")
        
        if ports and ports != '[]':
            try:
                port_list = json.loads(ports)
                print(f"   🔌 Ports: {port_list}")
            except:
                print(f"   🔌 Ports: {ports}")
        
        if methods:
            try:
                method_list = json.loads(methods)
                print(f"   🔍 Methods: {method_list}")
            except:
                print(f"   🔍 Methods: {methods}")
        
        if banner:
            banner_display = banner[:60] + "..." if len(banner) > 60 else banner
            print(f"   🌐 Banner: {banner_display}")
    
    # 5. SUMMARY OF WHAT WAS COLLECTED
    print("\n\n🎯 COLLECTION SUMMARY")
    print("=" * 50)
    
    # Device types collected
    cursor.execute("""
        SELECT device_classification, COUNT(*) 
        FROM assets 
        WHERE collection_time IS NOT NULL
        GROUP BY device_classification
        ORDER BY COUNT(*) DESC
    """)
    
    device_types = cursor.fetchall()
    print(f"Device Types Identified: {len(device_types)}")
    for device_type, count in device_types:
        print(f"   • {device_type}: {count} devices")
    
    # Ports collected
    cursor.execute("SELECT open_ports FROM assets WHERE open_ports IS NOT NULL AND open_ports != '[]'")
    ports_data = cursor.fetchall()
    
    unique_ports = set()
    for ports_json in ports_data:
        try:
            ports = json.loads(ports_json[0])
            unique_ports.update(ports)
        except:
            continue
    
    print(f"\nUnique Ports Discovered: {len(unique_ports)}")
    sorted_ports = sorted(unique_ports)
    port_ranges = []
    if sorted_ports:
        port_ranges.append(f"{sorted_ports[0]}-{sorted_ports[-1]}")
    print(f"   Port Range: {', '.join(port_ranges) if port_ranges else 'None'}")
    
    # Collection methods used
    cursor.execute("SELECT DISTINCT collection_methods FROM assets WHERE collection_methods IS NOT NULL")
    methods_data = cursor.fetchall()
    
    all_methods = set()
    for methods_json in methods_data:
        try:
            methods = json.loads(methods_json[0])
            all_methods.update(methods)
        except:
            continue
    
    print(f"\nCollection Methods Used: {len(all_methods)}")
    for method in sorted(all_methods):
        print(f"   • {method}")
    
    conn.close()
    
    print("\n\n✅ FINAL SUMMARY")
    print("=" * 50)
    print(f"📊 Total Database Columns: {len(all_columns)}")
    print(f"📈 Columns with Data: {len(columns_with_data)}")
    print(f"🚀 Network Scan Records: {scan_records}")
    print(f"🏷️ Device Types Found: {len(device_types)}")
    print(f"🔌 Unique Ports Found: {len(unique_ports)}")
    print(f"🔍 Collection Methods: {len(all_methods)}")
    print("💾 All data successfully stored and accessible!")

if __name__ == "__main__":
    show_database_columns_and_data()