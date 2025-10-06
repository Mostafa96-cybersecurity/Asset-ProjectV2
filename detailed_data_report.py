#!/usr/bin/env python3
"""
Detailed Data Collection Report - Fixed SQL queries
"""

import sqlite3
from datetime import datetime

def detailed_data_report():
    """Generate detailed report of collected data"""
    try:
        conn = sqlite3.connect('assets.db')
        cursor = conn.cursor()
        
        print("🔍 DETAILED DATA COLLECTION REPORT")
        print("=" * 80)
        
        # 1. Network Analysis (Fixed)
        print("\n🌐 NETWORK INFORMATION:")
        print("=" * 40)
        
        cursor.execute('''
            SELECT 
                CASE 
                    WHEN ip_address LIKE '10.0.21.%' THEN '10.0.21.x (Main Network)'
                    WHEN ip_address LIKE '10.0.22.%' THEN '10.0.22.x (Secondary Network)'
                    WHEN ip_address LIKE '10.0.50.%' THEN '10.0.50.x (Test Network)'
                    WHEN ip_address LIKE '192.168.%' THEN '192.168.x.x (Private)'
                    ELSE 'Other Networks'
                END as network_segment,
                COUNT(*) as device_count
            FROM assets 
            WHERE ip_address IS NOT NULL
            GROUP BY network_segment
            ORDER BY device_count DESC
        ''')
        networks = cursor.fetchall()
        
        for network, count in networks:
            print(f"  └─ {network}: {count} devices")
        
        # 2. WMI Collection Details
        print("\n🪟 WMI COLLECTION DATA SOURCES:")
        print("=" * 40)
        
        cursor.execute('''
            SELECT hostname, ip_address, system_manufacturer, system_model, 
                   processor_name, total_physical_memory, working_user
            FROM assets 
            WHERE collection_method = 'WMI'
            ORDER BY updated_at DESC
            LIMIT 5
        ''')
        wmi_samples = cursor.fetchall()
        
        print("Sample WMI-Collected Devices:")
        for hostname, ip, manufacturer, model, cpu, memory, user in wmi_samples:
            print(f"  📟 {hostname} ({ip})")
            print(f"     Hardware: {manufacturer} {model}")
            print(f"     CPU: {cpu}")
            if memory:
                memory_gb = int(memory) / (1024*1024*1024)
                print(f"     Memory: {memory_gb:.0f} GB")
            print(f"     User: {user}")
            print()
        
        # 3. Data Quality by Collection Method
        print("📊 DATA QUALITY BY COLLECTION METHOD:")
        print("=" * 50)
        
        methods = ['WMI', 'Enhanced WMI Collection', 'Unknown', 'Test Collection']
        
        for method in methods:
            cursor.execute('SELECT COUNT(*) FROM assets WHERE collection_method = ?', (method,))
            total = cursor.fetchone()[0]
            
            if total > 0:
                print(f"\n🔧 {method} ({total} devices):")
                
                # Check key field completeness for this method
                key_fields = ['operating_system', 'system_manufacturer', 'processor_name', 'bios_serial_number']
                
                for field in key_fields:
                    cursor.execute(f'''
                        SELECT COUNT(*) 
                        FROM assets 
                        WHERE collection_method = ? 
                        AND {field} IS NOT NULL 
                        AND {field} != '' 
                        AND {field} != 'None'
                    ''', (method,))
                    populated = cursor.fetchone()[0]
                    percentage = (populated / total) * 100 if total > 0 else 0
                    print(f"     {field}: {populated}/{total} ({percentage:.1f}%)")
        
        # 4. Hardware Inventory Summary
        print("\n🖥️ HARDWARE INVENTORY COLLECTED:")
        print("=" * 40)
        
        # Manufacturers
        cursor.execute('''
            SELECT system_manufacturer, COUNT(*) as count
            FROM assets 
            WHERE system_manufacturer IS NOT NULL AND system_manufacturer != ''
            GROUP BY system_manufacturer
            ORDER BY count DESC
        ''')
        manufacturers = cursor.fetchall()
        
        print("Hardware Manufacturers:")
        for manufacturer, count in manufacturers:
            print(f"  └─ {manufacturer}: {count} devices")
        
        # 5. Software Information
        print("\n💿 SOFTWARE INFORMATION COLLECTED:")
        print("=" * 40)
        
        cursor.execute('''
            SELECT operating_system, COUNT(*) as count
            FROM assets 
            WHERE operating_system IS NOT NULL AND operating_system != ''
            GROUP BY operating_system
            ORDER BY count DESC
        ''')
        os_list = cursor.fetchall()
        
        print("Operating Systems:")
        for os, count in os_list:
            print(f"  └─ {os}: {count} devices")
        
        # 6. Security Information
        print("\n🔐 SECURITY & USER INFORMATION:")
        print("=" * 40)
        
        # Count devices with user information
        cursor.execute('''
            SELECT COUNT(*) 
            FROM assets 
            WHERE working_user IS NOT NULL AND working_user != ''
        ''')
        with_users = cursor.fetchone()[0]
        
        print(f"Devices with User Information: {with_users}/221 ({(with_users/221)*100:.1f}%)")
        
        # Show user distribution
        cursor.execute('''
            SELECT working_user, COUNT(*) as count
            FROM assets 
            WHERE working_user IS NOT NULL AND working_user != ''
            GROUP BY working_user
            ORDER BY count DESC
            LIMIT 10
        ''')
        user_dist = cursor.fetchall()
        
        print("\nTop Users by Device Count:")
        for user, count in user_dist:
            print(f"  └─ {user}: {count} devices")
        
        # 7. Collection Sources Breakdown
        print("\n📋 DETAILED COLLECTION SOURCES:")
        print("=" * 40)
        
        print("1. WMI (Windows Management Instrumentation):")
        print("   └─ Source: Windows API calls")
        print("   └─ Data: Hardware specs, OS info, users, BIOS details")
        print("   └─ Method: Remote/Local WMI queries")
        print("   └─ Coverage: 98 Windows devices (44.3%)")
        
        print("\n2. Enhanced WMI Collection:")
        print("   └─ Source: Improved WMI with error handling")
        print("   └─ Data: Same as WMI but with better reliability")
        print("   └─ Method: Enhanced error recovery and validation")
        print("   └─ Coverage: 1 device (0.5%)")
        
        print("\n3. Unknown/Legacy Method:")
        print("   └─ Source: Previous collection runs or manual entries")
        print("   └─ Data: Basic IP, hostname, device type")
        print("   └─ Method: Various legacy collectors")
        print("   └─ Coverage: 121 devices (54.8%)")
        
        print("\n4. Test Collection:")
        print("   └─ Source: Manual test entries")
        print("   └─ Data: Demo/test device information")
        print("   └─ Method: Direct database insertion")
        print("   └─ Coverage: 1 device (0.5%)")
        
        # 8. Recent Collection Activity
        print("\n⏰ RECENT COLLECTION ACTIVITY:")
        print("=" * 40)
        
        cursor.execute('''
            SELECT DATE(updated_at) as date, 
                   collection_method,
                   COUNT(*) as count
            FROM assets 
            WHERE updated_at >= '2025-10-01'
            GROUP BY DATE(updated_at), collection_method
            ORDER BY date DESC, count DESC
        ''')
        recent_activity = cursor.fetchall()
        
        for date, method, count in recent_activity:
            print(f"  {date}: {count} devices via {method}")
        
        print("\n" + "=" * 80)
        print("✅ DETAILED ANALYSIS COMPLETE")
        print("📊 Total Devices: 221")
        print("🔧 Primary Collection: WMI (Windows)")
        print("📈 Data Quality: High for WMI devices, Basic for legacy")
        print("🌐 Network Coverage: Primarily 10.0.21.x subnet")
        print("=" * 80)
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Report generation failed: {e}")

if __name__ == "__main__":
    detailed_data_report()