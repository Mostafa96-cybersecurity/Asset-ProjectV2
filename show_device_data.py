#!/usr/bin/env python3
"""
Comprehensive Device Data Viewer
Shows ALL collected data for a specific device
"""

import sqlite3
import json
from datetime import datetime

def show_all_device_data(ip_address="10.0.21.47"):
    """Display all collected data for a specific device"""
    
    try:
        conn = sqlite3.connect('assets.db')
        cursor = conn.cursor()
        
        print('🔍 COMPREHENSIVE DEVICE DATA ANALYSIS')
        print('=' * 80)
        print(f'Target IP: {ip_address}')
        print()
        
        # Get all column names
        cursor.execute('PRAGMA table_info(assets)')
        columns_info = cursor.fetchall()
        all_columns = [col[1] for col in columns_info]
        
        print(f'📊 Database has {len(all_columns)} columns available')
        print()
        
        # Get all records for this IP
        cursor.execute('SELECT * FROM assets WHERE ip_address = ? ORDER BY created_at DESC', (ip_address,))
        records = cursor.fetchall()
        
        if not records:
            print(f'❌ No records found for IP {ip_address}')
            
            # Check for similar IPs
            cursor.execute('SELECT DISTINCT ip_address FROM assets WHERE ip_address LIKE ? LIMIT 10', (f'{ip_address[:-1]}%',))
            similar_ips = cursor.fetchall()
            if similar_ips:
                print(f'\\n🔍 Similar IPs found in database:')
                for ip_row in similar_ips:
                    print(f'   {ip_row[0]}')
            return
        
        print(f'✅ Found {len(records)} record(s) for IP {ip_address}')
        print()
        
        for record_num, record in enumerate(records, 1):
            print(f'📋 RECORD {record_num} DETAILS:')
            print('=' * 60)
            
            # Create dictionary of all data
            device_data = dict(zip(all_columns, record))
            
            # Group fields by category for better display
            categories = {
                '🔑 IDENTIFICATION': [
                    'id', 'hostname', 'computer_name', 'ip_address', 'mac_addresses'
                ],
                '💻 SYSTEM INFORMATION': [
                    'operating_system', 'os_version', 'os_build_number', 'os_architecture',
                    'system_manufacturer', 'system_model', 'system_type', 'system_family',
                    'device_type', 'asset_type'
                ],
                '🔧 HARDWARE': [
                    'processor_name', 'processor_architecture', 'processor_cores', 
                    'processor_logical_processors', 'total_physical_memory',
                    'bios_version', 'bios_manufacturer', 'bios_serial_number'
                ],
                '🌐 NETWORK': [
                    'domain_workgroup', 'ip_addresses', 'mac_addresses'
                ],
                '💾 STORAGE': [
                    'hard_drives', 'windows_directory', 'system_directory'
                ],
                '🔐 SECURITY & ACCESS': [
                    'working_user', 'current_user', 'last_boot_time'
                ],
                '📊 COLLECTION INFO': [
                    'collection_method', 'wmi_collection_status', 'wmi_collection_time',
                    'wmi_data_completeness', 'collection_time', 'collection_date',
                    'last_scan_date', 'last_update', 'quality_score', 'successful_credential'
                ],
                '🎯 DETECTION': [
                    'nmap_os_family', 'nmap_device_type', 'nmap_confidence', 'detection_method'
                ],
                '📅 TIMESTAMPS': [
                    'created_at', 'updated_at', 'last_scan_time', 'os_install_date'
                ],
                '🏷️ METADATA': [
                    'data_source', 'scan_status', 'realtime_status', 'status', 'collector'
                ]
            }
            
            # Display categorized data
            for category, fields in categories.items():
                category_data = {}
                for field in fields:
                    if field in device_data and device_data[field] is not None:
                        value = device_data[field]
                        if str(value).strip() and str(value).strip().lower() != 'none':
                            category_data[field] = value
                
                if category_data:
                    print(f'\\n{category}:')
                    for field, value in category_data.items():
                        # Format special fields
                        if field in ['total_physical_memory'] and str(value).isdigit():
                            # Convert bytes to GB
                            gb = round(int(value) / (1024**3), 2)
                            print(f'   {field}: {value} bytes ({gb} GB)')
                        elif field in ['created_at', 'updated_at', 'last_scan_time'] and value:
                            # Format timestamps
                            try:
                                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                                formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                                print(f'   {field}: {formatted_time}')
                            except:
                                print(f'   {field}: {value}')
                        else:
                            print(f'   {field}: {value}')
            
            # Show any additional fields not in categories
            categorized_fields = set()
            for fields_list in categories.values():
                categorized_fields.update(fields_list)
            
            additional_data = {}
            for field, value in device_data.items():
                if (field not in categorized_fields and 
                    value is not None and 
                    str(value).strip() and 
                    str(value).strip().lower() != 'none'):
                    additional_data[field] = value
            
            if additional_data:
                print(f'\\n🔧 ADDITIONAL FIELDS:')
                for field, value in additional_data.items():
                    print(f'   {field}: {value}')
            
            # Summary
            non_empty_fields = sum(1 for v in device_data.values() 
                                 if v is not None and str(v).strip() and str(v).strip().lower() != 'none')
            print(f'\\n📈 DATA COMPLETENESS:')
            print(f'   Total fields with data: {non_empty_fields}/{len(all_columns)}')
            print(f'   Completion percentage: {(non_empty_fields/len(all_columns)*100):.1f}%')
            
            if record_num < len(records):
                print('\\n' + '=' * 80 + '\\n')
        
        conn.close()
        
    except Exception as e:
        print(f'❌ Error accessing database: {e}')
        import traceback
        print(f'Details: {traceback.format_exc()}')

def show_recent_activity():
    """Show recent database activity"""
    try:
        conn = sqlite3.connect('assets.db')
        cursor = conn.cursor()
        
        print('\\n🕐 RECENT DATABASE ACTIVITY:')
        print('-' * 40)
        
        # Recent updates (last 24 hours)
        cursor.execute('''
            SELECT hostname, ip_address, collection_method, updated_at
            FROM assets 
            WHERE datetime(updated_at) > datetime('now', '-1 day')
            ORDER BY updated_at DESC
            LIMIT 10
        ''')
        
        recent = cursor.fetchall()
        if recent:
            print(f'Found {len(recent)} recent updates:')
            for hostname, ip, method, updated in recent:
                print(f'   {hostname or "Unknown"} ({ip}) - {method or "No method"} - {updated}')
        else:
            print('No updates in the last 24 hours')
        
        conn.close()
        
    except Exception as e:
        print(f'Error checking recent activity: {e}')

if __name__ == "__main__":
    show_all_device_data("10.0.21.47")
    show_recent_activity()