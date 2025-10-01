#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Direct Database Manual Update
============================
Manually update database records with enhanced data.
"""

import sqlite3
from datetime import datetime
import json

def manual_database_update():
    """Manually update database with enhanced data"""
    
    print("🔧 MANUAL DATABASE UPDATE")
    print("=" * 25)
    
    # Enhanced data sample (from our successful test)
    enhanced_sample = {
        'ip_address': '10.0.21.47',
        'hostname': 'LT-3541-0012',
        'working_user': 'SQUARE\\mahmoud.hamed',
        'manufacturer': 'Dell Inc.',
        'model': 'Precision 3541',
        'os_name': 'Microsoft Windows 10 Pro',
        'memory_gb': 16,
        'cpu_cores': 8,
        'serial_number': '3ZX1Y43',
        'device_type': 'Workstation',
        'classification': 'Workstation',
        'data_source': 'Enhanced WMI Collection',
        'processor_name': 'Intel(R) Core(TM) i7-9850H CPU @ 2.60GHz',
        'workgroup': 'WORKGROUP',
        'bios_version': 'Dell Inc. 1.19.0',
        'chassis_type': 'Portable',
        'domain': 'SQUARE',
        'operating_system': 'Microsoft Windows 10 Pro',
        'system_manufacturer': 'Dell Inc.',
        'system_model': 'Precision 3541',
        'status': 'Active',
        'department': 'IT Department',
        'last_updated': datetime.now().isoformat()
    }
    
    try:
        conn = sqlite3.connect('assets.db')
        cursor = conn.cursor()
        
        # Check if device exists
        cursor.execute('SELECT id FROM assets WHERE ip_address = ?', (enhanced_sample['ip_address'],))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing device
            update_query = '''
                UPDATE assets 
                SET hostname = ?, working_user = ?, manufacturer = ?, model = ?,
                    os_name = ?, memory_gb = ?, cpu_cores = ?, serial_number = ?,
                    device_type = ?, classification = ?, data_source = ?,
                    processor_name = ?, workgroup = ?, bios_version = ?,
                    chassis_type = ?, domain = ?, operating_system = ?,
                    system_manufacturer = ?, system_model = ?, status = ?,
                    department = ?, last_updated = ?
                WHERE ip_address = ?
            '''
            
            cursor.execute(update_query, (
                enhanced_sample['hostname'], enhanced_sample['working_user'],
                enhanced_sample['manufacturer'], enhanced_sample['model'],
                enhanced_sample['os_name'], enhanced_sample['memory_gb'],
                enhanced_sample['cpu_cores'], enhanced_sample['serial_number'],
                enhanced_sample['device_type'], enhanced_sample['classification'],
                enhanced_sample['data_source'], enhanced_sample['processor_name'],
                enhanced_sample['workgroup'], enhanced_sample['bios_version'],
                enhanced_sample['chassis_type'], enhanced_sample['domain'],
                enhanced_sample['operating_system'], enhanced_sample['system_manufacturer'],
                enhanced_sample['system_model'], enhanced_sample['status'],
                enhanced_sample['department'], enhanced_sample['last_updated'],
                enhanced_sample['ip_address']
            ))
            
            print(f"✅ Updated device {enhanced_sample['ip_address']}")
            
        else:
            # Insert new device
            insert_query = '''
                INSERT INTO assets (
                    ip_address, hostname, working_user, manufacturer, model,
                    os_name, memory_gb, cpu_cores, serial_number, device_type,
                    classification, data_source, processor_name, workgroup,
                    bios_version, chassis_type, domain, operating_system,
                    system_manufacturer, system_model, status, department,
                    created_at, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            
            cursor.execute(insert_query, (
                enhanced_sample['ip_address'], enhanced_sample['hostname'],
                enhanced_sample['working_user'], enhanced_sample['manufacturer'],
                enhanced_sample['model'], enhanced_sample['os_name'],
                enhanced_sample['memory_gb'], enhanced_sample['cpu_cores'],
                enhanced_sample['serial_number'], enhanced_sample['device_type'],
                enhanced_sample['classification'], enhanced_sample['data_source'],
                enhanced_sample['processor_name'], enhanced_sample['workgroup'],
                enhanced_sample['bios_version'], enhanced_sample['chassis_type'],
                enhanced_sample['domain'], enhanced_sample['operating_system'],
                enhanced_sample['system_manufacturer'], enhanced_sample['system_model'],
                enhanced_sample['status'], enhanced_sample['department'],
                enhanced_sample['last_updated'], enhanced_sample['last_updated']
            ))
            
            print(f"✅ Inserted new device {enhanced_sample['ip_address']}")
        
        conn.commit()
        
        # Verify the changes
        cursor.execute('''
            SELECT hostname, working_user, manufacturer, model, os_name, memory_gb
            FROM assets WHERE ip_address = ?
        ''', (enhanced_sample['ip_address'],))
        
        result = cursor.fetchone()
        if result:
            print("\n📊 Verification:")
            print(f"   Hostname: {result[0]}")
            print(f"   User: {result[1]}")
            print(f"   Manufacturer: {result[2]}")
            print(f"   Model: {result[3]}")
            print(f"   OS: {result[4]}")
            print(f"   Memory: {result[5]} GB")
        
        conn.close()
        
        print("\n🎉 Database update completed successfully!")
        print("💡 Refresh the web interface to see changes")
        print("🌐 http://127.0.0.1:8080")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = manual_database_update()
    input("\nPress Enter to continue...")