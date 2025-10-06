#!/usr/bin/env python3
"""
Sample Device Data Viewer - Shows actual collected fields
"""

import sqlite3
import json

def show_sample_device_data():
    """Show detailed data for sample devices"""
    try:
        conn = sqlite3.connect('assets.db')
        cursor = conn.cursor()
        
        print("🔍 SAMPLE DEVICE DATA - SHOWING ACTUAL COLLECTED FIELDS")
        print("=" * 80)
        
        # Get one device from each collection method
        methods = ['WMI', 'Enhanced WMI Collection', 'Unknown', 'Test Collection']
        
        for method in methods:
            print(f"\n🔧 SAMPLE: {method} Collection")
            print("=" * 50)
            
            cursor.execute('''
                SELECT * FROM assets 
                WHERE collection_method = ?
                ORDER BY updated_at DESC
                LIMIT 1
            ''', (method,))
            
            device = cursor.fetchone()
            if device:
                # Get column names
                cursor.execute('PRAGMA table_info(assets)')
                columns = [col[1] for col in cursor.fetchall()]
                
                # Create device dictionary
                device_dict = dict(zip(columns, device))
                
                # Show only populated fields
                print(f"📱 Device: {device_dict.get('hostname', 'Unknown')} ({device_dict.get('ip_address', 'Unknown')})")
                print("\nCollected Data Fields:")
                
                categories = {
                    'Basic Info': ['hostname', 'ip_address', 'device_type', 'operating_system', 'status'],
                    'Hardware': ['system_manufacturer', 'system_model', 'processor_name', 'total_physical_memory', 'bios_serial_number', 'mac_address'],
                    'User/Security': ['working_user', 'domain', 'logged_on_users', 'last_boot_time'],
                    'Network': ['primary_ip', 'secondary_ips', 'default_gateway', 'dns_servers', 'network_adapters'],
                    'System Details': ['os_build_number', 'bios_version', 'motherboard_manufacturer', 'cpu_cores', 'memory_gb'],
                    'Collection Meta': ['collection_method', 'created_at', 'updated_at', 'last_scan_time']
                }
                
                for category, fields in categories.items():
                    has_data = False
                    category_data = []
                    
                    for field in fields:
                        if field in device_dict and device_dict[field] is not None and str(device_dict[field]).strip() != '' and str(device_dict[field]) != 'None':
                            value = str(device_dict[field])
                            if len(value) > 60:
                                value = value[:60] + "..."
                            category_data.append(f"    {field}: {value}")
                            has_data = True
                    
                    if has_data:
                        print(f"\n  📋 {category}:")
                        for data_line in category_data:
                            print(data_line)
            else:
                print(f"  No devices found with {method} collection method")
        
        # Show comprehensive data for one well-populated device
        print(f"\n🏆 MOST COMPLETE DEVICE RECORD:")
        print("=" * 50)
        
        cursor.execute('''
            SELECT * FROM assets 
            WHERE collection_method = 'WMI'
            AND operating_system IS NOT NULL
            AND system_manufacturer IS NOT NULL
            AND processor_name IS NOT NULL
            AND bios_serial_number IS NOT NULL
            ORDER BY updated_at DESC
            LIMIT 1
        ''')
        
        complete_device = cursor.fetchone()
        if complete_device:
            cursor.execute('PRAGMA table_info(assets)')
            columns = [col[1] for col in cursor.fetchall()]
            device_dict = dict(zip(columns, complete_device))
            
            print(f"📱 Device: {device_dict.get('hostname', 'Unknown')} ({device_dict.get('ip_address', 'Unknown')})")
            
            # Count populated fields
            populated_fields = sum(1 for field, value in device_dict.items() 
                                 if value is not None and str(value).strip() != '' and str(value) != 'None')
            total_fields = len(device_dict)
            
            print(f"📊 Data Completeness: {populated_fields}/{total_fields} fields ({(populated_fields/total_fields)*100:.1f}%)")
            
            # Show all populated fields
            print("\nAll Populated Fields:")
            for field, value in device_dict.items():
                if value is not None and str(value).strip() != '' and str(value) != 'None':
                    display_value = str(value)
                    if len(display_value) > 80:
                        display_value = display_value[:80] + "..."
                    print(f"  {field}: {display_value}")
        
        print("\n" + "=" * 80)
        print("✅ SAMPLE DATA ANALYSIS COMPLETE")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Sample data analysis failed: {e}")

if __name__ == "__main__":
    show_sample_device_data()