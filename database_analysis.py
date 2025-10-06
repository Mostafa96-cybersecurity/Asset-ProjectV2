#!/usr/bin/env python3
"""
Comprehensive Database Analysis Tool
Checks data integrity, duplicates, completeness, and DNS validation data
"""

import sqlite3

def analyze_database():
    print('COMPREHENSIVE DATABASE ANALYSIS')
    print('=' * 60)

    try:
        conn = sqlite3.connect('assets.db')
        cursor = conn.cursor()
        
        # 1. Check total record count
        cursor.execute('SELECT COUNT(*) FROM assets')
        total_records = cursor.fetchone()[0]
        print(f'Total Records in Database: {total_records}')
        
        # 2. Check for duplicates by IP address
        cursor.execute('''
            SELECT ip_address, COUNT(*) as count 
            FROM assets 
            GROUP BY ip_address 
            HAVING COUNT(*) > 1
            ORDER BY count DESC
        ''')
        duplicates = cursor.fetchall()
        
        if duplicates:
            print(f'\nDUPLICATE IPs FOUND: {len(duplicates)} IPs have multiple records')
            for ip, count in duplicates[:10]:  # Show first 10
                print(f'  {ip}: {count} records')
            if len(duplicates) > 10:
                print(f'  ... and {len(duplicates) - 10} more')
        else:
            print('\nDUPLICATE CHECK: No duplicate IP addresses found ✓')
        
        # 3. Check recent collection data (last 24 hours)
        cursor.execute('''
            SELECT ip_address, hostname, dns_hostname, dns_status, device_type, 
                   collection_method, created_at
            FROM assets 
            WHERE datetime(created_at) >= datetime('now', '-1 day')
            ORDER BY created_at DESC
        ''')
        recent_records = cursor.fetchall()
        
        print(f'\nRECENT COLLECTIONS (Last 24 hours): {len(recent_records)} records')
        for record in recent_records[:5]:  # Show last 5
            ip, hostname, dns_hostname, dns_status, device_type, method, created = record
            print(f'  {ip} | {hostname or "Unknown"} | DNS: {dns_status or "None"} | {device_type} | {created}')
        
        # 4. Check data completeness for recent records
        if recent_records:
            print('\nDATA COMPLETENESS ANALYSIS:')
            cursor.execute('PRAGMA table_info(assets)')
            columns = [col[1] for col in cursor.fetchall()]
            total_columns = len(columns)
            print(f'  Total database columns: {total_columns}')
            
            # Check latest record
            cursor.execute('SELECT * FROM assets ORDER BY created_at DESC LIMIT 1')
            latest_record = cursor.fetchone()
            
            if latest_record:
                non_null_count = sum(1 for value in latest_record if value is not None and str(value).strip() != '')
                completion_rate = (non_null_count / total_columns) * 100
                print(f'  Latest record completion: {non_null_count}/{total_columns} fields ({completion_rate:.1f}%)')
                
                # Check specific important fields
                important_fields = {}
                for field in ['hostname', 'device_type', 'os_name', 'processor_name', 'total_ram', 'dns_hostname', 'dns_status']:
                    if field in columns:
                        idx = columns.index(field)
                        important_fields[field] = latest_record[idx]
                    else:
                        important_fields[field] = None
                
                print('  Key fields populated:')
                for field, value in important_fields.items():
                    status = '✓' if value and str(value).strip() else '✗'
                    print(f'    {field}: {status} {value or "Not set"}')
        
        # 5. Check DNS validation data
        cursor.execute('''
            SELECT dns_status, COUNT(*) as count
            FROM assets 
            WHERE dns_status IS NOT NULL AND dns_status != ''
            GROUP BY dns_status
        ''')
        dns_stats = cursor.fetchall()
        
        if dns_stats:
            print('\nDNS VALIDATION STATISTICS:')
            for status, count in dns_stats:
                print(f'  {status}: {count} records')
        else:
            print('\nDNS VALIDATION: No DNS validation data found')
        
        # 6. Check collection methods used
        cursor.execute('''
            SELECT collection_method, COUNT(*) as count
            FROM assets 
            WHERE collection_method IS NOT NULL
            GROUP BY collection_method
            ORDER BY count DESC
        ''')
        methods = cursor.fetchall()
        
        if methods:
            print('\nCOLLECTION METHODS USED:')
            for method, count in methods:
                print(f'  {method}: {count} records')
        
        # 7. Check for any records with DNS mismatches
        cursor.execute('''
            SELECT ip_address, hostname, dns_hostname, dns_status
            FROM assets 
            WHERE dns_status = 'mismatch'
            ORDER BY created_at DESC
            LIMIT 5
        ''')
        mismatches = cursor.fetchall()
        
        if mismatches:
            print('\nDNS MISMATCHES DETECTED:')
            for ip, hostname, dns_hostname, status in mismatches:
                print(f'  {ip}: Device="{hostname}" vs DNS="{dns_hostname}"')
        
        # 8. Check all collected fields for latest record
        if recent_records:
            cursor.execute('SELECT * FROM assets ORDER BY created_at DESC LIMIT 1')
            latest_full = cursor.fetchone()
            
            print('\nLATEST RECORD DETAILED ANALYSIS:')
            populated_fields = []
            empty_fields = []
            
            for i, col_name in enumerate(columns):
                value = latest_full[i] if i < len(latest_full) else None
                if value is not None and str(value).strip() != '':
                    populated_fields.append(f'{col_name}: {str(value)[:50]}...' if len(str(value)) > 50 else f'{col_name}: {value}')
                else:
                    empty_fields.append(col_name)
            
            print(f'  POPULATED FIELDS ({len(populated_fields)}):')
            for field in populated_fields[:20]:  # Show first 20
                print(f'    {field}')
            if len(populated_fields) > 20:
                print(f'    ... and {len(populated_fields) - 20} more populated fields')
            
            print(f'  EMPTY FIELDS ({len(empty_fields)}):')
            for field in empty_fields[:10]:  # Show first 10 empty
                print(f'    {field}')
            if len(empty_fields) > 10:
                print(f'    ... and {len(empty_fields) - 10} more empty fields')
        
        conn.close()
        
        print('\n' + '=' * 60)
        print('DATABASE ANALYSIS COMPLETE')
        
        # Summary assessment
        if not duplicates:
            print('✓ No duplicate records found')
        else:
            print(f'⚠ {len(duplicates)} IPs have duplicate records')
        
        if recent_records:
            print('✓ Recent collection data found')
        else:
            print('⚠ No recent collection data')
        
        if dns_stats:
            print('✓ DNS validation data is being saved')
        else:
            print('⚠ DNS validation data missing')
        
        print('✓ Database structure and connectivity OK')
        
        # Return status for automation
        return {
            'total_records': total_records,
            'duplicates': len(duplicates) if duplicates else 0,
            'recent_records': len(recent_records),
            'dns_validation_working': bool(dns_stats),
            'latest_completion_rate': completion_rate if 'completion_rate' in locals() else 0
        }

    except Exception as e:
        print(f'Database analysis failed: {e}')
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    analyze_database()