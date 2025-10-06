#!/usr/bin/env python3
"""
Database Connection and Data Integrity Validator
Ensures proper data persistence and update-only behavior (no data replacement)
"""

import sqlite3
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import hashlib

class DatabaseIntegrityValidator:
    """Validates database operations and ensures data integrity"""
    
    def __init__(self, db_path: str = 'assets.db'):
        self.db_path = db_path
        self.backup_data = {}
        
    def validate_connection(self) -> Dict[str, Any]:
        """Validate database connection and structure"""
        result = {
            'connection_status': False,
            'table_exists': False,
            'record_count': 0,
            'last_update': None,
            'schema_valid': False,
            'errors': []
        }
        
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()
            
            # Test connection
            result['connection_status'] = True
            
            # Check if assets table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='assets'")
            if cursor.fetchone():
                result['table_exists'] = True
                
                # Get record count
                cursor.execute("SELECT COUNT(*) FROM assets")
                result['record_count'] = cursor.fetchone()[0]
                
                # Get last update time
                cursor.execute("SELECT MAX(last_seen) FROM assets WHERE last_seen IS NOT NULL")
                last_update = cursor.fetchone()[0]
                if last_update:
                    result['last_update'] = last_update
                
                # Validate schema
                cursor.execute("PRAGMA table_info(assets)")
                columns = [row[1] for row in cursor.fetchall()]
                required_columns = ['id', 'hostname', 'ip_address', 'operating_system', 'device_type', 'last_seen']
                result['schema_valid'] = all(col in columns for col in required_columns)
                result['columns'] = columns
            
            conn.close()
            
        except Exception as e:
            result['errors'].append(str(e))
            
        return result
    
    def create_data_backup(self) -> bool:
        """Create backup of current data before any operations"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM assets")
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            
            self.backup_data = {
                'timestamp': datetime.now().isoformat(),
                'columns': columns,
                'data': [dict(zip(columns, row)) for row in rows],
                'count': len(rows)
            }
            
            # Save backup to file
            backup_filename = f"data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(backup_filename, 'w') as f:
                json.dump(self.backup_data, f, indent=2, default=str)
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return False
    
    def validate_data_integrity(self) -> Dict[str, Any]:
        """Validate data integrity and check for duplicates"""
        result = {
            'total_records': 0,
            'unique_ips': 0,
            'unique_hostnames': 0,
            'duplicates': [],
            'null_data': [],
            'data_quality_score': 0.0
        }
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total records
            cursor.execute("SELECT COUNT(*) FROM assets")
            result['total_records'] = cursor.fetchone()[0]
            
            # Unique IPs
            cursor.execute("SELECT COUNT(DISTINCT ip_address) FROM assets WHERE ip_address IS NOT NULL")
            result['unique_ips'] = cursor.fetchone()[0]
            
            # Unique hostnames
            cursor.execute("SELECT COUNT(DISTINCT hostname) FROM assets WHERE hostname IS NOT NULL")
            result['unique_hostnames'] = cursor.fetchone()[0]
            
            # Check for IP duplicates
            cursor.execute("""
                SELECT ip_address, COUNT(*) as count 
                FROM assets 
                WHERE ip_address IS NOT NULL 
                GROUP BY ip_address 
                HAVING COUNT(*) > 1
            """)
            ip_duplicates = cursor.fetchall()
            
            # Check for hostname duplicates
            cursor.execute("""
                SELECT hostname, COUNT(*) as count 
                FROM assets 
                WHERE hostname IS NOT NULL 
                GROUP BY hostname 
                HAVING COUNT(*) > 1
            """)
            hostname_duplicates = cursor.fetchall()
            
            result['duplicates'] = {
                'ip_duplicates': ip_duplicates,
                'hostname_duplicates': hostname_duplicates
            }
            
            # Check for null/empty data
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN hostname IS NULL OR hostname = '' THEN 1 ELSE 0 END) as null_hostnames,
                    SUM(CASE WHEN ip_address IS NULL OR ip_address = '' THEN 1 ELSE 0 END) as null_ips,
                    SUM(CASE WHEN operating_system IS NULL OR operating_system = '' THEN 1 ELSE 0 END) as null_os,
                    SUM(CASE WHEN device_type IS NULL OR device_type = '' THEN 1 ELSE 0 END) as null_types
                FROM assets
            """)
            null_stats = cursor.fetchone()
            result['null_data'] = {
                'null_hostnames': null_stats[0],
                'null_ips': null_stats[1], 
                'null_os': null_stats[2],
                'null_types': null_stats[3]
            }
            
            # Calculate data quality score
            total = result['total_records']
            if total > 0:
                quality_score = (
                    (total - null_stats[0]) * 0.3 +  # Hostname completeness
                    (total - null_stats[1]) * 0.4 +  # IP completeness
                    (total - null_stats[2]) * 0.2 +  # OS completeness
                    (total - null_stats[3]) * 0.1    # Type completeness
                ) / total
                result['data_quality_score'] = round(quality_score, 2)
            
            conn.close()
            
        except Exception as e:
            result['error'] = str(e)
            
        return result

class SmartUpdateManager:
    """Manages database updates intelligently - only updates changed data"""
    
    def __init__(self, db_path: str = 'assets.db'):
        self.db_path = db_path
        
    def calculate_data_hash(self, device_data: Dict) -> str:
        """Calculate hash of device data for change detection"""
        # Include only substantive fields in hash (exclude timestamps)
        hash_fields = ['hostname', 'ip_address', 'operating_system', 'device_type', 
                      'manufacturer', 'model', 'cpu_info', 'ram_gb', 'storage_info']
        
        hash_data = {}
        for field in hash_fields:
            hash_data[field] = device_data.get(field, '')
        
        return hashlib.md5(json.dumps(hash_data, sort_keys=True).encode()).hexdigest()
    
    def smart_update_device(self, device_data: Dict) -> Dict[str, Any]:
        """Update device only if data has changed"""
        result = {
            'action': 'none',
            'updated_fields': [],
            'new_record': False,
            'data_changed': False
        }
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if device exists
            ip_address = device_data.get('ip_address')
            hostname = device_data.get('hostname')
            
            # Try to find existing record by IP first, then hostname
            existing_record = None
            if ip_address:
                cursor.execute("SELECT * FROM assets WHERE ip_address = ?", (ip_address,))
                existing_record = cursor.fetchone()
            
            if not existing_record and hostname:
                cursor.execute("SELECT * FROM assets WHERE hostname = ?", (hostname,))
                existing_record = cursor.fetchone()
            
            if existing_record:
                # Get column names
                cursor.execute("PRAGMA table_info(assets)")
                columns = [row[1] for row in cursor.fetchall()]
                existing_data = dict(zip(columns, existing_record))
                
                # Calculate hashes
                new_hash = self.calculate_data_hash(device_data)
                existing_hash = self.calculate_data_hash(existing_data)
                
                if new_hash != existing_hash:
                    # Data has changed - update only changed fields
                    updated_fields = []
                    update_pairs = []
                    values = []
                    
                    for field, new_value in device_data.items():
                        if field in existing_data:
                            old_value = existing_data[field]
                            if str(new_value) != str(old_value) and new_value not in [None, '', 'Unknown']:
                                updated_fields.append(field)
                                update_pairs.append(f"{field} = ?")
                                values.append(new_value)
                    
                    # Always update last_seen
                    if 'last_seen' not in updated_fields:
                        updated_fields.append('last_seen')
                        update_pairs.append("last_seen = ?")
                        values.append(datetime.now().isoformat())
                    
                    if update_pairs:
                        update_sql = f"UPDATE assets SET {', '.join(update_pairs)} WHERE id = ?"
                        values.append(existing_data['id'])
                        
                        cursor.execute(update_sql, values)
                        conn.commit()
                        
                        result['action'] = 'updated'
                        result['updated_fields'] = updated_fields
                        result['data_changed'] = True
                else:
                    # Data unchanged - just update timestamp
                    cursor.execute("UPDATE assets SET last_seen = ? WHERE id = ?", 
                                 (datetime.now().isoformat(), existing_data['id']))
                    conn.commit()
                    result['action'] = 'timestamp_updated'
            else:
                # New record - insert
                fields = list(device_data.keys())
                placeholders = ', '.join(['?' for _ in fields])
                values = list(device_data.values())
                
                # Add timestamp if not present
                if 'last_seen' not in fields:
                    fields.append('last_seen')
                    values.append(datetime.now().isoformat())
                    placeholders += ', ?'
                
                insert_sql = f"INSERT INTO assets ({', '.join(fields)}) VALUES ({placeholders})"
                cursor.execute(insert_sql, values)
                conn.commit()
                
                result['action'] = 'inserted'
                result['new_record'] = True
                result['data_changed'] = True
            
            conn.close()
            
        except Exception as e:
            result['error'] = str(e)
            
        return result

def test_database_operations():
    """Test database connection and operations"""
    print("🔍 DATABASE CONNECTION & INTEGRITY TEST")
    print("=" * 60)
    
    # Initialize validators
    validator = DatabaseIntegrityValidator()
    updater = SmartUpdateManager()
    
    # Test 1: Connection validation
    print("📡 Testing Database Connection...")
    connection_result = validator.validate_connection()
    
    print(f"   🔗 Connection: {'✅' if connection_result['connection_status'] else '❌'}")
    print(f"   📋 Table exists: {'✅' if connection_result['table_exists'] else '❌'}")
    print(f"   📊 Record count: {connection_result['record_count']}")
    print(f"   🏗️ Schema valid: {'✅' if connection_result['schema_valid'] else '❌'}")
    
    if connection_result['errors']:
        print(f"   ❌ Errors: {connection_result['errors']}")
    
    # Test 2: Create backup
    print(f"\n💾 Creating Data Backup...")
    backup_success = validator.create_data_backup()
    print(f"   {'✅' if backup_success else '❌'} Backup created")
    
    # Test 3: Data integrity check
    print(f"\n🔍 Checking Data Integrity...")
    integrity_result = validator.validate_data_integrity()
    
    print(f"   📊 Total records: {integrity_result['total_records']}")
    print(f"   🌐 Unique IPs: {integrity_result['unique_ips']}")
    print(f"   🏷️ Unique hostnames: {integrity_result['unique_hostnames']}")
    print(f"   📈 Data quality score: {integrity_result['data_quality_score']:.1%}")
    
    # Check duplicates
    duplicates = integrity_result.get('duplicates', {})
    ip_dups = duplicates.get('ip_duplicates', [])
    hostname_dups = duplicates.get('hostname_duplicates', [])
    
    if ip_dups:
        print(f"   ⚠️ IP duplicates found: {len(ip_dups)}")
        for ip, count in ip_dups[:3]:
            print(f"      • {ip}: {count} records")
    
    if hostname_dups:
        print(f"   ⚠️ Hostname duplicates found: {len(hostname_dups)}")
        for hostname, count in hostname_dups[:3]:
            print(f"      • {hostname}: {count} records")
    
    # Test 4: Smart update test
    print(f"\n🧠 Testing Smart Update System...")
    
    # Test with sample device data
    test_device = {
        'hostname': 'test-device-validator',
        'ip_address': '10.0.21.999',
        'operating_system': 'Test OS',
        'device_type': 'Test Device',
        'manufacturer': 'Test Manufacturer'
    }
    
    # First insert
    update_result1 = updater.smart_update_device(test_device)
    print(f"   📝 First insert: {update_result1['action']}")
    
    # Second insert (should detect no change)
    update_result2 = updater.smart_update_device(test_device)
    print(f"   🔄 Duplicate insert: {update_result2['action']}")
    
    # Modified data (should update)
    test_device['operating_system'] = 'Updated Test OS'
    update_result3 = updater.smart_update_device(test_device)
    print(f"   ✏️ Data change: {update_result3['action']}")
    if update_result3.get('updated_fields'):
        print(f"      Updated fields: {update_result3['updated_fields']}")
    
    # Cleanup test record
    try:
        import sqlite3
        conn = sqlite3.connect('assets.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM assets WHERE ip_address = '10.0.21.999'")
        conn.commit()
        conn.close()
        print(f"   🧹 Test record cleaned up")
    except:
        pass
    
    return connection_result, integrity_result

if __name__ == "__main__":
    print("🔧 DATABASE INTEGRITY & SMART UPDATE VALIDATOR")
    print("=" * 60)
    print(f"🕐 Started: {datetime.now()}")
    print()
    
    connection_result, integrity_result = test_database_operations()
    
    print(f"\n📋 SUMMARY REPORT")
    print("=" * 60)
    
    # Connection status
    if connection_result['connection_status'] and connection_result['table_exists']:
        print("✅ Database connection: HEALTHY")
    else:
        print("❌ Database connection: ISSUES DETECTED")
    
    # Data integrity
    quality_score = integrity_result.get('data_quality_score', 0)
    if quality_score >= 0.8:
        print("✅ Data integrity: EXCELLENT")
    elif quality_score >= 0.6:
        print("⚠️ Data integrity: GOOD")
    else:
        print("❌ Data integrity: NEEDS IMPROVEMENT")
    
    # Record count
    record_count = connection_result.get('record_count', 0)
    print(f"📊 Total records: {record_count}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if quality_score < 0.8:
        print("   1. Run enhanced collection to improve data completeness")
    
    duplicates = integrity_result.get('duplicates', {})
    if duplicates.get('ip_duplicates') or duplicates.get('hostname_duplicates'):
        print("   2. Clean up duplicate records")
    
    if record_count < 500:
        print("   3. Expand network scanning to discover more devices")
    
    print("   4. Set up automatic scanning to keep data current")
    
    print(f"\n🕐 Completed: {datetime.now()}")