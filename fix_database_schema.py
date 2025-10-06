#!/usr/bin/env python3
"""
Database Schema Fix and Data Persistence Tool

This script fixes database schema issues and ensures proper data storage.
Addresses SQLite parameter binding issues with list types and missing columns.
"""

import sqlite3
import json
from datetime import datetime
import os

def fix_database_schema():
    """Fix database schema to support all collected data properly"""
    
    db_path = "assets.db"
    
    # Backup current database
    backup_path = f"assets_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    if os.path.exists(db_path):
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"📁 Database backed up to: {backup_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get current table structure
    cursor.execute("PRAGMA table_info(assets)")
    current_columns = [row[1] for row in cursor.fetchall()]
    print(f"📋 Current columns: {current_columns}")
    
    # Add missing columns if needed
    new_columns = [
        ("collection_time", "TEXT"),
        ("mac_address", "TEXT"),
        ("vendor", "TEXT"),
        ("services", "TEXT"),  # Store as JSON string
        ("open_ports", "TEXT"),  # Store as JSON string
        ("http_banner", "TEXT"),
        ("device_classification", "TEXT"),
        ("collection_methods", "TEXT"),  # Store as JSON string
        ("scan_data", "TEXT"),  # Store as JSON string for comprehensive data
        ("last_updated", "TEXT DEFAULT CURRENT_TIMESTAMP")
    ]
    
    for column_name, column_type in new_columns:
        if column_name not in current_columns:
            try:
                cursor.execute(f"ALTER TABLE assets ADD COLUMN {column_name} {column_type}")
                print(f"✅ Added column: {column_name}")
            except sqlite3.OperationalError as e:
                print(f"⚠️ Column {column_name} might already exist: {e}")
    
    # Create indexes for better performance
    indexes = [
        ("idx_ip", "ip_address"),
        ("idx_hostname", "hostname"), 
        ("idx_classification", "device_classification"),
        ("idx_updated", "last_updated")
    ]
    
    for index_name, column in indexes:
        try:
            cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON assets ({column})")
            print(f"📊 Created index: {index_name}")
        except sqlite3.OperationalError:
            pass
    
    conn.commit()
    conn.close()
    
    print("✅ Database schema updated successfully!")
    return True

def create_robust_data_saver():
    """Create a robust data persistence system that handles all data types"""
    
    saver_code = '''#!/usr/bin/env python3
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
                    print(f"   🔄 Updated: {processed_data['ip_address']}")
                else:
                    print(f"   ⏭️ No changes: {processed_data['ip_address']}")
            else:
                # Insert new record
                self._insert_record(cursor, processed_data, data_hash)
                self.saved_count += 1
                print(f"   ➕ Added: {processed_data['ip_address']}")
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            self.error_count += 1
            print(f"   ❌ Save error for {device_data.get('ip_address', 'unknown')}: {e}")
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
        
        # Core columns that should always exist
        core_columns = ['ip_address', 'hostname', 'os', 'status']
        
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
'''
    
    with open("robust_data_saver.py", "w") as f:
        f.write(saver_code)
    
    print("✅ Created robust_data_saver.py")

def main():
    """Main function to fix database and create tools"""
    
    print("🔧 FIXING DATABASE SCHEMA AND CREATING ROBUST TOOLS")
    print("=" * 60)
    
    # Step 1: Fix database schema
    print("\n1️⃣ Fixing database schema...")
    fix_database_schema()
    
    # Step 2: Create robust data saver
    print("\n2️⃣ Creating robust data saver...")
    create_robust_data_saver()
    
    # Step 3: Verify database structure
    print("\n3️⃣ Verifying database structure...")
    conn = sqlite3.connect("assets.db")
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(assets)")
    columns = cursor.fetchall()
    
    print("📋 Current database columns:")
    for col in columns:
        print(f"   - {col[1]} ({col[2]})")
    
    cursor.execute("SELECT COUNT(*) FROM assets")
    count = cursor.fetchone()[0]
    print(f"📊 Current record count: {count}")
    
    conn.close()
    
    print("\n✅ DATABASE SCHEMA FIX COMPLETE!")
    print("💡 Now you can re-run the network scan and data will save properly")

if __name__ == "__main__":
    main()