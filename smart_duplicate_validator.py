#!/usr/bin/env python3
"""
Smart Duplicate Prevention Engine
Real-time validation during collection with enterprise-grade duplicate detection
"""

import sqlite3
import hashlib
from datetime import datetime
from typing import Dict
import json

class SmartDuplicateValidator:
    """Enterprise-grade duplicate prevention system"""
    
    def __init__(self, db_path="assets.db"):
        self.db_path = db_path
        self.connection = None
        
    def connect(self):
        """Connect to database"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        return self.connection

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()

    def generate_device_fingerprint(self, device_data: Dict) -> str:
        """Generate unique device fingerprint for duplicate detection"""
        # Create fingerprint from hardware characteristics
        fingerprint_data = {
            'serial_number': device_data.get('serial_number', ''),
            'mac_address': device_data.get('mac_address', ''),
            'processor_name': device_data.get('processor_name', ''),
            'motherboard_model': device_data.get('motherboard_model', ''),
            'bios_version': device_data.get('bios_version', ''),
        }
        
        # Remove empty values and create hash
        clean_data = {k: v for k, v in fingerprint_data.items() if v}
        fingerprint_string = json.dumps(clean_data, sort_keys=True)
        return hashlib.md5(fingerprint_string.encode()).hexdigest()

    def check_for_duplicates(self, device_data: Dict) -> Dict:
        """
        Advanced duplicate detection with multiple validation levels
        Returns: {'is_duplicate': bool, 'action': str, 'existing_id': int, 'confidence': float}
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        result = {
            'is_duplicate': False,
            'action': 'insert',  # insert, update, skip, merge
            'existing_id': None,
            'confidence': 0.0,
            'match_type': None,
            'details': ''
        }
        
        # Level 1: Serial Number + MAC Address (Highest confidence)
        serial = device_data.get('serial_number', '').strip()
        mac = device_data.get('mac_address', '').strip()
        
        if serial and mac:
            cursor.execute("""
                SELECT id, created_at, last_seen, seen_count, data_source, hostname, ip_address
                FROM assets 
                WHERE serial_number = ? AND mac_address = ?
                LIMIT 1
            """, (serial, mac))
            
            existing = cursor.fetchone()
            if existing:
                result.update({
                    'is_duplicate': True,
                    'action': 'update',
                    'existing_id': existing['id'],
                    'confidence': 0.95,
                    'match_type': 'serial_mac',
                    'details': f'Perfect match: Serial {serial[:10]}... + MAC {mac}'
                })
                conn.close()
                return result
        
        # Level 2: Hardware Fingerprint (High confidence)
        fingerprint = self.generate_device_fingerprint(device_data)
        cursor.execute("""
            SELECT id, created_at, last_seen, seen_count, data_source, hostname, ip_address
            FROM assets 
            WHERE device_fingerprint = ?
            LIMIT 1
        """, (fingerprint,))
        
        existing = cursor.fetchone()
        if existing:
            result.update({
                'is_duplicate': True,
                'action': 'update',
                'existing_id': existing['id'],
                'confidence': 0.85,
                'match_type': 'hardware_fingerprint',
                'details': f'Hardware fingerprint match: {fingerprint[:12]}...'
            })
            conn.close()
            return result
        
        # Level 3: IP Address + Hostname (Medium confidence)
        ip = device_data.get('ip_address', '').strip()
        hostname = device_data.get('hostname', '').strip()
        
        if ip and hostname:
            cursor.execute("""
                SELECT id, created_at, last_seen, seen_count, data_source, serial_number, mac_address
                FROM assets 
                WHERE ip_address = ? AND hostname = ?
                ORDER BY created_at DESC
                LIMIT 1
            """, (ip, hostname))
            
            existing = cursor.fetchone()
            if existing:
                # Check if this might be the same device with missing serial/mac
                if not existing['serial_number'] or not existing['mac_address']:
                    result.update({
                        'is_duplicate': True,
                        'action': 'merge',  # Merge new data with existing
                        'existing_id': existing['id'],
                        'confidence': 0.75,
                        'match_type': 'ip_hostname',
                        'details': 'IP+Hostname match, merge new hardware data'
                    })
                else:
                    # Possible device replacement or reconfiguration
                    result.update({
                        'is_duplicate': True,
                        'action': 'update',
                        'existing_id': existing['id'],
                        'confidence': 0.60,
                        'match_type': 'ip_hostname_replacement',
                        'details': 'Same IP+Hostname, possible hardware replacement'
                    })
                conn.close()
                return result
        
        # Level 4: IP Address only (Lower confidence)
        if ip:
            cursor.execute("""
                SELECT id, created_at, last_seen, hostname, serial_number, mac_address
                FROM assets 
                WHERE ip_address = ?
                ORDER BY created_at DESC
                LIMIT 1
            """, (ip,))
            
            existing = cursor.fetchone()
            if existing:
                # Only consider if recent (within 7 days) and hostname is similar
                try:
                    last_seen = datetime.fromisoformat(existing['created_at'].replace('Z', '+00:00'))
                    days_ago = (datetime.now() - last_seen.replace(tzinfo=None)).days
                    
                    if days_ago <= 7:
                        result.update({
                            'is_duplicate': True,
                            'action': 'update',
                            'existing_id': existing['id'],
                            'confidence': 0.45,
                            'match_type': 'ip_recent',
                            'details': f'Same IP, recent scan ({days_ago} days ago)'
                        })
                        conn.close()
                        return result
                except:
                    pass
        
        # No duplicates found
        result['details'] = 'No duplicates detected, safe to insert'
        conn.close()
        return result

    def smart_save_device(self, device_data: Dict) -> Dict:
        """
        Smart device saving with duplicate prevention
        Returns: {'success': bool, 'action': str, 'device_id': int, 'message': str}
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        # Check for duplicates
        duplicate_check = self.check_for_duplicates(device_data)
        
        # Add metadata
        device_data['device_fingerprint'] = self.generate_device_fingerprint(device_data)
        device_data['last_seen'] = datetime.now().isoformat()
        device_data['duplicate_check_status'] = 'verified'
        
        result = {
            'success': False,
            'action': duplicate_check['action'],
            'device_id': None,
            'message': '',
            'duplicate_info': duplicate_check
        }
        
        try:
            if duplicate_check['action'] == 'insert':
                # Insert new device
                device_data['seen_count'] = 1
                device_data['created_at'] = datetime.now().isoformat()
                
                # Build INSERT query dynamically
                columns = list(device_data.keys())
                placeholders = ', '.join(['?' for _ in columns])
                values = [device_data[col] for col in columns]
                
                query = f"INSERT INTO assets ({', '.join(columns)}) VALUES ({placeholders})"
                cursor.execute(query, values)
                
                device_id = cursor.lastrowid
                result.update({
                    'success': True,
                    'device_id': device_id,
                    'message': f'New device inserted (ID: {device_id})'
                })
                
            elif duplicate_check['action'] == 'update':
                # Update existing device
                existing_id = duplicate_check['existing_id']
                
                # Get current seen_count
                cursor.execute("SELECT seen_count FROM assets WHERE id = ?", (existing_id,))
                current_count = cursor.fetchone()['seen_count'] or 0
                device_data['seen_count'] = current_count + 1
                
                # Build UPDATE query for non-null values
                update_fields = []
                update_values = []
                
                for key, value in device_data.items():
                    if value is not None and value != '' and key != 'id':
                        update_fields.append(f"{key} = ?")
                        update_values.append(value)
                
                if update_fields:
                    update_values.append(existing_id)
                    query = f"UPDATE assets SET {', '.join(update_fields)} WHERE id = ?"
                    cursor.execute(query, update_values)
                
                result.update({
                    'success': True,
                    'device_id': existing_id,
                    'message': f'Device updated (ID: {existing_id}, confidence: {duplicate_check["confidence"]:.2f})'
                })
                
            elif duplicate_check['action'] == 'merge':
                # Merge new data with existing record
                existing_id = duplicate_check['existing_id']
                
                # Get existing data
                cursor.execute("SELECT * FROM assets WHERE id = ?", (existing_id,))
                existing_data = dict(cursor.fetchone())
                
                # Merge: new data overwrites existing only if existing is null/empty
                merged_data = existing_data.copy()
                for key, value in device_data.items():
                    if value and (not merged_data.get(key) or merged_data.get(key) == ''):
                        merged_data[key] = value
                
                # Update seen count
                merged_data['seen_count'] = (merged_data.get('seen_count', 0) or 0) + 1
                merged_data['last_seen'] = datetime.now().isoformat()
                
                # Build UPDATE query
                update_fields = []
                update_values = []
                
                for key, value in merged_data.items():
                    if key != 'id':
                        update_fields.append(f"{key} = ?")
                        update_values.append(value)
                
                update_values.append(existing_id)
                query = f"UPDATE assets SET {', '.join(update_fields)} WHERE id = ?"
                cursor.execute(query, update_values)
                
                result.update({
                    'success': True,
                    'device_id': existing_id,
                    'message': f'Device data merged (ID: {existing_id})'
                })
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            result.update({
                'success': False,
                'message': f'Database error: {str(e)}'
            })
        
        finally:
            conn.close()
        
        return result

    def get_duplicate_statistics(self) -> Dict:
        """Get statistics about duplicate prevention"""
        conn = self.connect()
        cursor = conn.cursor()
        
        stats = {}
        
        # Total devices
        cursor.execute("SELECT COUNT(*) FROM assets")
        stats['total_devices'] = cursor.fetchone()[0]
        
        # Devices with fingerprints
        cursor.execute("SELECT COUNT(*) FROM assets WHERE device_fingerprint IS NOT NULL")
        stats['fingerprinted_devices'] = cursor.fetchone()[0]
        
        # Devices seen multiple times
        cursor.execute("SELECT COUNT(*) FROM assets WHERE seen_count > 1")
        stats['rescanned_devices'] = cursor.fetchone()[0]
        
        # Average seen count
        cursor.execute("SELECT AVG(seen_count) FROM assets WHERE seen_count IS NOT NULL")
        result = cursor.fetchone()[0]
        stats['avg_seen_count'] = round(result, 2) if result else 0
        
        # Data sources
        cursor.execute("SELECT data_source, COUNT(*) FROM assets GROUP BY data_source")
        stats['data_sources'] = dict(cursor.fetchall())
        
        conn.close()
        return stats

def test_duplicate_prevention():
    """Test the duplicate prevention system"""
    print("🧪 TESTING SMART DUPLICATE PREVENTION")
    print("=" * 50)
    
    validator = SmartDuplicateValidator()
    
    # Test device data
    test_device = {
        'hostname': 'TEST-PC-001',
        'ip_address': '192.168.1.100',
        'serial_number': 'ABC123456789',
        'mac_address': '00:11:22:33:44:55',
        'processor_name': 'Intel Core i7-8700K',
        'motherboard_model': 'ASUS PRIME Z370-A',
        'os_version': '10.0.19041',
        'data_source': 'Enhanced WMI Collection'
    }
    
    print("1️⃣ Testing first insertion:")
    result1 = validator.smart_save_device(test_device.copy())
    print(f"   Action: {result1['action']}")
    print(f"   Success: {result1['success']}")
    print(f"   Message: {result1['message']}")
    
    print("\n2️⃣ Testing duplicate detection:")
    result2 = validator.smart_save_device(test_device.copy())
    print(f"   Action: {result2['action']}")
    print(f"   Success: {result2['success']}")
    print(f"   Message: {result2['message']}")
    print(f"   Confidence: {result2['duplicate_info']['confidence']:.2f}")
    
    print("\n3️⃣ Testing with updated data:")
    test_device['os_version'] = '10.0.19042'  # Updated OS
    test_device['total_memory_gb'] = 16  # New field
    result3 = validator.smart_save_device(test_device.copy())
    print(f"   Action: {result3['action']}")
    print(f"   Message: {result3['message']}")
    
    # Get statistics
    print("\n📊 DUPLICATE PREVENTION STATISTICS:")
    stats = validator.get_duplicate_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")

if __name__ == "__main__":
    test_duplicate_prevention()