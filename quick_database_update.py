#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quick Database Update Test
=========================
Test and update the database with enhanced data to fix the N/A fields.
"""

import sys
import os
import sqlite3
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.getcwd())

from enhanced_data_collector import enhanced_wmi_collection

def quick_database_update():
    """Quick test to update one device with enhanced data"""
    
    # Test device that we know works
    test_ip = "10.0.21.47"
    test_user = ".\\administrator"  
    test_pass = "LocalAdmin"
    
    print("🔧 QUICK DATABASE UPDATE TEST")
    print("=" * 35)
    
    # Get enhanced data
    print(f"📡 Collecting enhanced data for {test_ip}...")
    device_data = enhanced_wmi_collection(test_ip, test_user, test_pass)
    
    if device_data and len(device_data) > 10:
        print(f"✅ Enhanced data collected: {len(device_data)} fields")
        
        # Show what we got
        print("📊 Key data collected:")
        key_fields = ['hostname', 'working_user', 'manufacturer', 'model', 'os_name', 'memory_gb']
        for field in key_fields:
            value = device_data.get(field, 'N/A')
            print(f"   {field}: {value}")
        
        # Update database
        print("\n💾 Updating database...")
        try:
            conn = sqlite3.connect('assets.db')
            cursor = conn.cursor()
            
            # Update the device
            cursor.execute('''
                UPDATE assets 
                SET hostname = ?, working_user = ?, manufacturer = ?, 
                    model = ?, os_name = ?, memory_gb = ?, cpu_cores = ?,
                    serial_number = ?, device_type = ?, classification = ?,
                    data_source = ?, last_updated = ?
                WHERE ip_address = ?
            ''', (
                device_data.get('hostname', 'Unknown'),
                device_data.get('working_user', 'N/A'),
                device_data.get('manufacturer', 'Unknown'),
                device_data.get('model', 'Unknown'),
                device_data.get('os_name', 'Unknown'),
                device_data.get('memory_gb', 0),
                device_data.get('cpu_cores', 0),
                device_data.get('serial_number', ''),
                device_data.get('device_type', 'Workstation'),
                device_data.get('classification', 'Workstation'),
                'Enhanced WMI Collection',
                datetime.now().isoformat(),
                test_ip
            ))
            
            if cursor.rowcount > 0:
                print(f"✅ Updated {cursor.rowcount} device(s)")
            else:
                print("⚠️ No devices updated (device may not exist)")
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            return False
    
    else:
        print(f"❌ Enhanced collection failed")
        return False
    
    # Verify the update
    print("\n🔍 Verifying update...")
    try:
        conn = sqlite3.connect('assets.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT hostname, working_user, manufacturer, model, os_name 
            FROM assets WHERE ip_address = ?
        ''', (test_ip,))
        
        result = cursor.fetchone()
        if result:
            print("✅ Verification successful:")
            print(f"   hostname: {result[0]}")
            print(f"   working_user: {result[1]}")
            print(f"   manufacturer: {result[2]}")
            print(f"   model: {result[3]}")
            print(f"   os_name: {result[4]}")
        else:
            print("❌ Device not found")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Verification error: {e}")
    
    return True

if __name__ == "__main__":
    success = quick_database_update()
    
    if success:
        print("\n🎉 Database update successful!")
        print("💡 Check the web interface to see the updated data")
        print("🌐 http://127.0.0.1:8080")
    else:
        print("\n❌ Database update failed")