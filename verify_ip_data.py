#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Data Verification for IP 10.0.21.47
============================================
Check all stored data and verify English-only content
"""

import sqlite3
import re
from datetime import datetime

def check_arabic_text(text):
    """Check if text contains Arabic characters"""
    if not text or not isinstance(text, str):
        return False
    # Arabic Unicode range: 0600-06FF
    return bool(re.search(r'[\u0600-\u06FF]', text))

def verify_database_data(target_ip):
    """Verify all data for specific IP"""
    
    print(f"🔍 VERIFYING DATABASE DATA FOR {target_ip}")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect('assets.db')
        cursor = conn.cursor()
        
        # Get all records for this IP
        cursor.execute('SELECT * FROM assets WHERE ip_address = ?', (target_ip,))
        records = cursor.fetchall()
        
        if not records:
            print(f"❌ No records found for {target_ip}")
            return
        
        # Get column names
        cursor.execute('PRAGMA table_info(assets)')
        columns = [col[1] for col in cursor.fetchall()]
        
        print(f"✅ Found {len(records)} record(s) for {target_ip}")
        
        for i, record in enumerate(records, 1):
            print(f"\n📋 RECORD {i} - COMPLETE DATA VERIFICATION")
            print("-" * 50)
            
            device_data = dict(zip(columns, record))
            
            # Track data quality
            arabic_fields = []
            english_fields = []
            empty_fields = []
            
            # Windows-specific fields we want to verify
            windows_fields = {
                'hostname': 'Hostname',
                'working_user': 'Working User', 
                'domain': 'Domain',
                'manufacturer': 'Model/Vendor',
                'model': 'Model/Vendor',
                'ip_address': 'IP Address',
                'operating_system': 'OS Name',
                'installed_ram_gb': 'Installed RAM (GB)',
                'storage': 'Storage',
                'serial_number': 'SN',
                'processor': 'Processor',
                'system_sku': 'System SKU',
                'active_gpu': 'Active GPU',
                'connected_screens': 'Connected Screens'
            }
            
            print(f"🖥️ WINDOWS DATA FIELDS:")
            for field, label in windows_fields.items():
                value = device_data.get(field)
                
                if value and str(value).strip():
                    value_str = str(value).strip()
                    if check_arabic_text(value_str):
                        arabic_fields.append(field)
                        print(f"❌ {label}: {value_str} (CONTAINS ARABIC)")
                    else:
                        english_fields.append(field)
                        print(f"✅ {label}: {value_str}")
                else:
                    empty_fields.append(field)
                    print(f"⚪ {label}: (Empty/Null)")
            
            # Manual fields (not collected automatically)
            manual_fields = {
                'asset_tag': 'Asset Tag',
                'owner': 'Owner',
                'department': 'Department',
                'site': 'Site',
                'building': 'Building',
                'floor': 'Floor',
                'room': 'Room'
            }
            
            print(f"\n📝 MANUAL DATA FIELDS:")
            for field, label in manual_fields.items():
                value = device_data.get(field)
                if value and str(value).strip():
                    print(f"✅ {label}: {value}")
                else:
                    print(f"⚪ {label}: (To be filled manually)")
            
            # System fields
            system_fields = {
                'data_source': 'Data Source',
                'created_at': 'Created At',
                'last_updated': 'Last Updated',
                'device_type': 'Device Type',
                'collection_method': 'Collection Method'
            }
            
            print(f"\n🔧 SYSTEM FIELDS:")
            for field, label in system_fields.items():
                value = device_data.get(field)
                if value:
                    print(f"ℹ️ {label}: {value}")
            
            # Summary for this record
            print(f"\n📊 DATA QUALITY SUMMARY:")
            print(f"   ✅ English fields: {len(english_fields)}")
            print(f"   ❌ Arabic fields: {len(arabic_fields)}")
            print(f"   ⚪ Empty fields: {len(empty_fields)}")
            
            if arabic_fields:
                print(f"   🚨 ARABIC DETECTED IN: {', '.join(arabic_fields)}")
            else:
                print(f"   ✅ ALL TEXT DATA IS IN ENGLISH")
            
            # Check for unique identifier to prevent duplicates
            unique_identifiers = []
            if device_data.get('serial_number'):
                unique_identifiers.append(f"Serial: {device_data['serial_number']}")
            if device_data.get('hostname'):
                unique_identifiers.append(f"Hostname: {device_data['hostname']}")
            if device_data.get('system_sku'):
                unique_identifiers.append(f"SKU: {device_data['system_sku']}")
            
            print(f"   🔑 Unique identifiers: {', '.join(unique_identifiers) if unique_identifiers else 'None found'}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database verification failed: {e}")

def check_collection_capabilities():
    """Check what collection methods are working"""
    
    print(f"\n🔧 COLLECTION CAPABILITIES CHECK")
    print("=" * 60)
    
    # Check WMI
    try:
        import wmi
        print("✅ WMI library available")
    except ImportError:
        print("❌ WMI library not available")
    
    # Check SSH
    try:
        import paramiko
        print("✅ SSH (paramiko) library available")
    except ImportError:
        print("❌ SSH library not available")
    
    # Check SNMP
    try:
        import pysnmp
        print("✅ SNMP library available")
    except ImportError:
        print("❌ SNMP library not available")
    
    # Check database
    try:
        import sqlite3
        conn = sqlite3.connect('assets.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM assets')
        total_devices = cursor.fetchone()[0]
        conn.close()
        print(f"✅ Database working - {total_devices} total devices")
    except Exception as e:
        print(f"❌ Database issue: {e}")

def main():
    """Main verification function"""
    
    target_ip = "10.0.21.47"
    
    print("🔍 DATABASE DATA VERIFICATION")
    print("=" * 70)
    print(f"Target: {target_ip}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Goal: Verify English-only data and completeness")
    print("=" * 70)
    
    # Check collection capabilities
    check_collection_capabilities()
    
    # Verify database data
    verify_database_data(target_ip)
    
    print(f"\n" + "=" * 70)
    print("📋 VERIFICATION SUMMARY")
    print("=" * 70)
    print("✅ Data verification completed")
    print("🎯 Check above for any Arabic text issues")
    print("🎯 Configure WMI credentials for complete data collection")

if __name__ == "__main__":
    main()