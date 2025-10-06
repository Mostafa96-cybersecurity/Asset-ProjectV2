#!/usr/bin/env python3
"""
Comprehensive Data Collection Analysis
Shows what data is collected, sources, and collection methods
"""

import sqlite3
from datetime import datetime, timedelta
import json

def analyze_collected_data():
    """Analyze all collected data and show sources"""
    try:
        conn = sqlite3.connect('assets.db')
        cursor = conn.cursor()
        
        print("🔍 COMPREHENSIVE DATA COLLECTION ANALYSIS")
        print("=" * 80)
        print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 1. Overall Statistics
        cursor.execute('SELECT COUNT(*) FROM assets')
        total_devices = cursor.fetchone()[0]
        print(f"📊 TOTAL DEVICES: {total_devices}")
        
        # 2. Collection Methods Breakdown
        print("\n🔧 COLLECTION METHODS & SOURCES:")
        print("=" * 50)
        
        cursor.execute('''
            SELECT 
                collection_method,
                COUNT(*) as device_count,
                COUNT(*) * 100.0 / (SELECT COUNT(*) FROM assets) as percentage
            FROM assets 
            WHERE collection_method IS NOT NULL
            GROUP BY collection_method
            ORDER BY device_count DESC
        ''')
        methods = cursor.fetchall()
        
        for method, count, percentage in methods:
            print(f"  {method}: {count} devices ({percentage:.1f}%)")
            
            # Show sample devices for each method
            cursor.execute('''
                SELECT hostname, ip_address, device_type, operating_system
                FROM assets 
                WHERE collection_method = ?
                ORDER BY updated_at DESC
                LIMIT 3
            ''', (method,))
            samples = cursor.fetchall()
            
            for hostname, ip, dtype, os in samples:
                print(f"    └─ {hostname or 'Unknown'} ({ip}) - {dtype} - {os}")
            print()
        
        # 3. Data Completeness Analysis
        print("📈 DATA COMPLETENESS BY FIELD TYPE:")
        print("=" * 50)
        
        # Key fields to analyze
        key_fields = [
            'hostname', 'ip_address', 'operating_system', 'device_type',
            'system_manufacturer', 'system_model', 'processor_name',
            'total_physical_memory', 'bios_serial_number', 'mac_address',
            'working_user', 'domain', 'last_boot_time'
        ]
        
        for field in key_fields:
            cursor.execute(f'''
                SELECT COUNT(*) 
                FROM assets 
                WHERE {field} IS NOT NULL AND {field} != '' AND {field} != 'Unknown'
            ''')
            populated = cursor.fetchone()[0]
            percentage = (populated / total_devices) * 100 if total_devices > 0 else 0
            print(f"  {field}: {populated}/{total_devices} ({percentage:.1f}%)")
        
        # 4. Device Types and OS Distribution
        print("\n🏷️ DEVICE TYPES DISCOVERED:")
        print("=" * 40)
        
        cursor.execute('''
            SELECT device_type, operating_system, COUNT(*) as count
            FROM assets 
            WHERE device_type IS NOT NULL
            GROUP BY device_type, operating_system
            ORDER BY count DESC
        ''')
        device_os = cursor.fetchall()
        
        current_type = None
        for dtype, os, count in device_os:
            if dtype != current_type:
                print(f"\n📱 {dtype}:")
                current_type = dtype
            print(f"  └─ {os}: {count} devices")
        
        # 5. Collection Timeline
        print("\n⏰ COLLECTION TIMELINE:")
        print("=" * 40)
        
        # Recent collections (last 7 days)
        seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
        cursor.execute('''
            SELECT DATE(updated_at) as collection_date, COUNT(*) as devices_updated
            FROM assets 
            WHERE updated_at >= ?
            GROUP BY DATE(updated_at)
            ORDER BY collection_date DESC
        ''', (seven_days_ago,))
        
        timeline = cursor.fetchall()
        for date, count in timeline:
            print(f"  {date}: {count} devices updated")
        
        # 6. Hardware Information Collected
        print("\n🖥️ HARDWARE DATA COLLECTED:")
        print("=" * 40)
        
        # CPU Information
        cursor.execute('''
            SELECT processor_name, COUNT(*) as count
            FROM assets 
            WHERE processor_name IS NOT NULL AND processor_name != ''
            GROUP BY processor_name
            ORDER BY count DESC
            LIMIT 5
        ''')
        cpus = cursor.fetchall()
        print("Top CPUs:")
        for cpu, count in cpus:
            print(f"  └─ {cpu}: {count} devices")
        
        # Memory Information
        cursor.execute('''
            SELECT 
                CASE 
                    WHEN total_physical_memory < 4000000000 THEN '< 4GB'
                    WHEN total_physical_memory < 8000000000 THEN '4-8GB'
                    WHEN total_physical_memory < 16000000000 THEN '8-16GB'
                    WHEN total_physical_memory < 32000000000 THEN '16-32GB'
                    ELSE '32GB+'
                END as memory_range,
                COUNT(*) as count
            FROM assets 
            WHERE total_physical_memory IS NOT NULL
            GROUP BY memory_range
            ORDER BY count DESC
        ''')
        memory_dist = cursor.fetchall()
        print("\nMemory Distribution:")
        for mem_range, count in memory_dist:
            print(f"  └─ {mem_range}: {count} devices")
        
        # 7. Network Information
        print("\n🌐 NETWORK DATA COLLECTED:")
        print("=" * 40)
        
        # IP Address ranges
        cursor.execute('''
            SELECT 
                SUBSTR(ip_address, 1, INSTR(ip_address||'.', '.', INSTR(ip_address||'.', '.', INSTR(ip_address||'.', '.')+1)+1)-1) as subnet,
                COUNT(*) as count
            FROM assets 
            WHERE ip_address IS NOT NULL
            GROUP BY subnet
            ORDER BY count DESC
            LIMIT 10
        ''')
        subnets = cursor.fetchall()
        print("IP Subnets:")
        for subnet, count in subnets:
            print(f"  └─ {subnet}.x: {count} devices")
        
        # 8. Security & User Information
        print("\n🔐 SECURITY & USER DATA:")
        print("=" * 40)
        
        # Working users
        cursor.execute('''
            SELECT working_user, COUNT(*) as count
            FROM assets 
            WHERE working_user IS NOT NULL AND working_user != ''
            GROUP BY working_user
            ORDER BY count DESC
            LIMIT 10
        ''')
        users = cursor.fetchall()
        print("Active Users:")
        for user, count in users:
            print(f"  └─ {user}: {count} devices")
        
        # Domains
        cursor.execute('''
            SELECT domain, COUNT(*) as count
            FROM assets 
            WHERE domain IS NOT NULL AND domain != ''
            GROUP BY domain
            ORDER BY count DESC
        ''')
        domains = cursor.fetchall()
        print("\nDomains:")
        for domain, count in domains:
            print(f"  └─ {domain}: {count} devices")
        
        # 9. Collection Quality Metrics
        print("\n📊 COLLECTION QUALITY METRICS:")
        print("=" * 40)
        
        # Devices with serial numbers (hardware fingerprint)
        cursor.execute('''
            SELECT COUNT(*) 
            FROM assets 
            WHERE bios_serial_number IS NOT NULL AND bios_serial_number != ''
        ''')
        with_serial = cursor.fetchone()[0]
        serial_percentage = (with_serial / total_devices) * 100 if total_devices > 0 else 0
        print(f"Hardware Serial Numbers: {with_serial}/{total_devices} ({serial_percentage:.1f}%)")
        
        # Devices with MAC addresses
        cursor.execute('''
            SELECT COUNT(*) 
            FROM assets 
            WHERE mac_address IS NOT NULL AND mac_address != ''
        ''')
        with_mac = cursor.fetchone()[0]
        mac_percentage = (with_mac / total_devices) * 100 if total_devices > 0 else 0
        print(f"MAC Addresses: {with_mac}/{total_devices} ({mac_percentage:.1f}%)")
        
        # Complete device profiles (all key fields populated)
        cursor.execute('''
            SELECT COUNT(*) 
            FROM assets 
            WHERE hostname IS NOT NULL AND hostname != ''
            AND ip_address IS NOT NULL AND ip_address != ''
            AND operating_system IS NOT NULL AND operating_system != ''
            AND system_manufacturer IS NOT NULL AND system_manufacturer != ''
            AND processor_name IS NOT NULL AND processor_name != ''
        ''')
        complete_profiles = cursor.fetchone()[0]
        complete_percentage = (complete_profiles / total_devices) * 100 if total_devices > 0 else 0
        print(f"Complete Profiles: {complete_profiles}/{total_devices} ({complete_percentage:.1f}%)")
        
        # 10. Data Sources Summary
        print("\n📋 DATA SOURCES SUMMARY:")
        print("=" * 40)
        
        cursor.execute('''
            SELECT 
                CASE 
                    WHEN collection_method = 'WMI' THEN 'Windows WMI (Local/Remote)'
                    WHEN collection_method = 'Enhanced WMI Collection' THEN 'Enhanced WMI with Error Handling'
                    WHEN collection_method = 'SSH' THEN 'Linux SSH Commands'
                    WHEN collection_method = 'SNMP' THEN 'SNMP Network Queries'
                    WHEN collection_method = 'Test Collection' THEN 'Manual Test Entry'
                    ELSE 'Legacy/Unknown Method'
                END as source_description,
                COUNT(*) as count
            FROM assets
            GROUP BY source_description
            ORDER BY count DESC
        ''')
        sources = cursor.fetchall()
        
        for source, count in sources:
            print(f"  └─ {source}: {count} devices")
        
        print("\n" + "=" * 80)
        print("✅ ANALYSIS COMPLETE")
        print(f"📊 Total Assets Analyzed: {total_devices}")
        print(f"🔧 Collection Methods: {len(methods)}")
        print(f"🏷️ Device Types: {len(set(row[0] for row in device_os))}")
        print("=" * 80)
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")

if __name__ == "__main__":
    analyze_collected_data()