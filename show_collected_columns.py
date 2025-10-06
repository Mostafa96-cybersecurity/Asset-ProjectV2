#!/usr/bin/env python3
"""
Display Collected Database Columns
Shows all populated columns and their values from recent collections
"""

import sqlite3
from datetime import datetime

def show_collected_columns():
    print('COLLECTED DATABASE COLUMNS ANALYSIS')
    print('=' * 80)

    try:
        conn = sqlite3.connect('assets.db')
        cursor = conn.cursor()
        
        # Get all column names
        cursor.execute('PRAGMA table_info(assets)')
        all_columns = [col[1] for col in cursor.fetchall()]
        
        print(f'Total Database Schema: {len(all_columns)} columns')
        
        # Get the latest record with most data
        cursor.execute('SELECT * FROM assets ORDER BY created_at DESC LIMIT 1')
        latest_record = cursor.fetchone()
        
        if not latest_record:
            print('No records found in database')
            return
        
        # Analyze populated vs empty columns
        populated_columns = []
        empty_columns = []
        
        for i, column_name in enumerate(all_columns):
            value = latest_record[i] if i < len(latest_record) else None
            
            if value is not None and str(value).strip() != '':
                populated_columns.append((column_name, value))
            else:
                empty_columns.append(column_name)
        
        print(f'\nLATEST RECORD ANALYSIS:')
        print(f'Record ID: {latest_record[0]}')
        print(f'IP Address: {latest_record[all_columns.index("ip_address")] if "ip_address" in all_columns else "N/A"}')
        print(f'Hostname: {latest_record[all_columns.index("hostname")] if "hostname" in all_columns else "N/A"}')
        print(f'Collection Date: {latest_record[all_columns.index("created_at")] if "created_at" in all_columns else "N/A"}')
        
        print(f'\nCOLLECTED COLUMNS ({len(populated_columns)} out of {len(all_columns)}):')
        print('=' * 80)
        
        # Group columns by category for better organization
        categories = {
            'Basic Info': ['id', 'hostname', 'ip_address', 'domain', 'workgroup'],
            'Device Info': ['model_vendor', 'serial_number', 'asset_tag', 'device_type', 'classification'],
            'Operating System': ['os_name', 'os_version', 'os_architecture', 'os_build_number', 'os_service_pack'],
            'Hardware': ['processor_name', 'processor_speed', 'processor_cores', 'total_ram', 'installed_ram_gb'],
            'BIOS/Firmware': ['bios_version', 'bios_date', 'firmware_version', 'firmware_os_version'],
            'Network': ['mac_address', 'network_adapters', 'ip_configuration', 'dns_servers'],
            'Storage': ['disk_info', 'storage_summary', 'hard_drive_capacity', 'available_storage'],
            'Graphics': ['graphics_cards', 'video_memory'],
            'Software': ['installed_software', 'installed_programs', 'antivirus_software'],
            'User Info': ['current_user', 'working_user', 'last_logged_user'],
            'DNS Validation': ['dns_hostname', 'dns_status'],
            'Management': ['department', 'location', 'site', 'owner', 'assigned_user'],
            'Status': ['status', 'ping_status', 'uptime', 'uptime_percentage'],
            'Collection': ['data_source', 'collection_method', 'created_by', 'created_at', 'last_updated']
        }
        
        # Display populated columns by category
        for category, column_list in categories.items():
            category_columns = []
            for col_name, value in populated_columns:
                if col_name in column_list:
                    category_columns.append((col_name, value))
            
            if category_columns:
                print(f'\n📁 {category.upper()}:')
                for col_name, value in category_columns:
                    # Truncate long values for display
                    display_value = str(value)
                    if len(display_value) > 100:
                        display_value = display_value[:100] + '...'
                    print(f'   ✓ {col_name}: {display_value}')
        
        # Show remaining populated columns not in categories
        categorized_columns = []
        for category_list in categories.values():
            categorized_columns.extend(category_list)
        
        other_columns = [(col, val) for col, val in populated_columns if col not in categorized_columns]
        
        if other_columns:
            print(f'\n📁 OTHER POPULATED COLUMNS:')
            for col_name, value in other_columns:
                display_value = str(value)
                if len(display_value) > 100:
                    display_value = display_value[:100] + '...'
                print(f'   ✓ {col_name}: {display_value}')
        
        print(f'\n' + '=' * 80)
        print(f'COLLECTION SUMMARY:')
        print(f'✓ Populated Columns: {len(populated_columns)}')
        print(f'✗ Empty Columns: {len(empty_columns)}')
        print(f'📊 Collection Rate: {(len(populated_columns)/len(all_columns)*100):.1f}%')
        
        # Show top empty columns that could be collected
        important_empty = []
        for col in empty_columns:
            if any(keyword in col.lower() for keyword in ['processor', 'memory', 'disk', 'network', 'software', 'version']):
                important_empty.append(col)
        
        if important_empty:
            print(f'\n⚠️  IMPORTANT EMPTY COLUMNS (Could be enhanced):')
            for col in important_empty[:10]:  # Show first 10
                print(f'   ✗ {col}')
            if len(important_empty) > 10:
                print(f'   ... and {len(important_empty) - 10} more')
        
        # Check multiple recent records for consistency
        cursor.execute('SELECT * FROM assets ORDER BY created_at DESC LIMIT 5')
        recent_records = cursor.fetchall()
        
        print(f'\nRECENT COLLECTION CONSISTENCY (Last 5 records):')
        for i, record in enumerate(recent_records):
            populated_count = sum(1 for value in record if value is not None and str(value).strip() != '')
            ip = record[all_columns.index("ip_address")] if "ip_address" in all_columns else "Unknown"
            hostname = record[all_columns.index("hostname")] if "hostname" in all_columns else "Unknown"
            created = record[all_columns.index("created_at")] if "created_at" in all_columns else "Unknown"
            
            print(f'   {i+1}. {ip} ({hostname}) - {populated_count} fields - {created}')
        
        conn.close()
        
    except Exception as e:
        print(f'Analysis failed: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    show_collected_columns()