#!/usr/bin/env python3
"""
Robust Data Persistence System

Handles all collected network data and saves properly to SQLite database.
Converts lists and complex data to JSON strings for storage.
"""

import sqlite3
import json
from datetime import datetime
import hashlib

class RobustDataSaver:
    def __init__(self, db_path="assets.db"):
        self.db_path = db_path
        self.saved_count = 0
        self.updated_count = 0
        self.error_count = 0
        
    def save_device_data(self, device_data):
        """Save device data with proper type conversion"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Convert lists and complex data to JSON strings
            processed_data = self._process_data_for_sqlite(device_data)
            
            # Generate data hash for change detection
            data_hash = self._generate_data_hash(processed_data)
            
            # Check if record exists
            cursor.execute("SELECT id, data_hash FROM assets WHERE ip_address = ?", 
                          (processed_data['ip_address'],))
            existing = cursor.fetchone()
            
            if existing:
                existing_id, existing_hash = existing
                if existing_hash != data_hash:
                    # Update existing record
                    self._update_record(cursor, existing_id, processed_data, data_hash)
                    self.updated_count += 1
                    print(f"   Updated: {processed_data['ip_address']}")
                else:
                    print(f"   No changes: {processed_data['ip_address']}")
            else:
                # Insert new record
                self._insert_record(cursor, processed_data, data_hash)
                self.saved_count += 1
                print(f"   Added: {processed_data['ip_address']}")
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            self.error_count += 1
            print(f"   Save error for {device_data.get('ip_address', 'unknown')}: {e}")
            return False
    
    def _process_data_for_sqlite(self, data):
        """Convert complex data types to SQLite-compatible formats"""
        processed = {}
        
        for key, value in data.items():
            if isinstance(value, (list, dict)):
                # Convert lists and dicts to JSON strings
                processed[key] = json.dumps(value) if value else None
            elif isinstance(value, (int, float, str)) or value is None:
                processed[key] = value
            else:
                # Convert other types to string
                processed[key] = str(value)
        
        # Ensure required fields exist
        if 'collection_time' not in processed:
            processed['collection_time'] = datetime.now().isoformat()
        
        return processed
    
    def _generate_data_hash(self, data):
        """Generate hash of data for change detection"""
        # Create a stable string representation
        stable_data = {k: v for k, v in data.items() 
                      if k not in ['collection_time', 'last_updated']}
        data_string = json.dumps(stable_data, sort_keys=True)
        return hashlib.md5(data_string.encode()).hexdigest()
    
    def _insert_record(self, cursor, data, data_hash):
        """Insert new record into database"""
        
        # Get all available columns from table
        cursor.execute("PRAGMA table_info(assets)")
        table_columns = [row[1] for row in cursor.fetchall()]
        
        # Prepare data for insertion
        insert_data = {'data_hash': data_hash, 'last_updated': datetime.now().isoformat()}
        
        for column in table_columns:
            if column in data:
                insert_data[column] = data[column]
            elif column in ['id']:  # Skip auto-increment columns
                continue
            else:
                insert_data[column] = None
        
        # Build INSERT query
        columns = list(insert_data.keys())
        placeholders = ['?' for _ in columns]
        
        query = f"INSERT INTO assets ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        values = [insert_data[col] for col in columns]
        
        cursor.execute(query, values)
    
    def _update_record(self, cursor, record_id, data, data_hash):
        """Update existing record"""
        
        # Get all available columns
        cursor.execute("PRAGMA table_info(assets)")
        table_columns = [row[1] for row in cursor.fetchall()]
        
        # Prepare update data
        update_data = {'data_hash': data_hash, 'last_updated': datetime.now().isoformat()}
        
        for column in table_columns:
            if column in data and column not in ['id']:
                update_data[column] = data[column]
        
        # Build UPDATE query
        set_clauses = [f"{col} = ?" for col in update_data.keys()]
        query = f"UPDATE assets SET {', '.join(set_clauses)} WHERE id = ?"
        values = list(update_data.values()) + [record_id]
        
        cursor.execute(query, values)
    
    def get_summary(self):
        """Get summary of save operations"""
        return {
            'new_records': self.saved_count,
            'updated_records': self.updated_count,
            'errors': self.error_count,
            'total_processed': self.saved_count + self.updated_count + self.error_count
        }

if __name__ == "__main__":
    # Test the saver
    saver = RobustDataSaver()
    
    # Test data
    test_device = {
        'ip_address': '10.0.21.1',
        'hostname': 'test-device.local',
        'os': 'Windows',
        'status': 'active',
        'open_ports': [80, 443, 22],
        'services': {'80': 'http', '443': 'https'},
        'collection_methods': ['ping', 'port_scan'],
        'device_classification': 'Web Server'
    }
    
    result = saver.save_device_data(test_device)
    print(f"Test save result: {result}")
    print(f"Summary: {saver.get_summary()}")
