#!/usr/bin/env python3
"""
Database Schema Setup for Duplicate Prevention
Adds necessary columns and indexes for smart duplicate detection
"""

import sqlite3
import os
from datetime import datetime

class DuplicatePreventionSchema:
    def __init__(self, db_path='assets.db'):
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        """Connect to the database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn
        
    def setup_duplicate_prevention_schema(self):
        """Set up complete schema for duplicate prevention"""
        if not self.conn:
            self.connect()
            
        if not self.conn:
            print("❌ Failed to establish database connection")
            return
            
        cursor = self.conn.cursor()
        
        print("🔧 Setting up duplicate prevention schema...")
        
        # 1. Add duplicate detection columns to assets table
        duplicate_columns = [
            ('device_fingerprint', 'TEXT'),
            ('duplicate_confidence', 'REAL DEFAULT 0.0'),
            ('duplicate_status', 'TEXT DEFAULT "unique"'),
            ('duplicate_group_id', 'TEXT'),
            ('last_duplicate_check', 'TEXT'),
            ('duplicate_resolution_action', 'TEXT'),
            ('duplicate_resolution_date', 'TEXT'),
            ('duplicate_resolution_by', 'TEXT'),
            ('is_archived', 'INTEGER DEFAULT 0'),
            ('archived_date', 'TEXT'),
            ('archived_reason', 'TEXT'),
            ('transfer_history', 'TEXT'),  # JSON string of user transfers
            ('hardware_upgrade_history', 'TEXT'),  # JSON string of upgrades
            ('network_change_history', 'TEXT'),  # JSON string of network changes
            ('data_quality_score', 'REAL DEFAULT 0.0'),
            ('collection_method', 'TEXT'),  # WMI, SSH, SNMP, Manual
            ('collection_authentication', 'TEXT'),  # Success, Failed, Partial
            ('previous_user', 'TEXT'),
            ('transfer_date', 'TEXT'),
            ('hardware_change_detected', 'INTEGER DEFAULT 0'),
            ('network_change_detected', 'INTEGER DEFAULT 0')
        ]
        
        for column_name, column_type in duplicate_columns:
            try:
                cursor.execute(f'ALTER TABLE assets ADD COLUMN {column_name} {column_type}')
                print(f"  ✅ Added column: {column_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"  ⚠️  Column already exists: {column_name}")
                else:
                    print(f"  ❌ Error adding column {column_name}: {e}")
        
        # 2. Create device_history table for audit trail
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS device_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id INTEGER,
                field_name TEXT,
                old_value TEXT,
                new_value TEXT,
                changed_at TEXT,
                changed_by TEXT,
                change_reason TEXT,
                collection_id TEXT,
                confidence_score REAL,
                FOREIGN KEY (device_id) REFERENCES assets (id)
            )
        ''')
        print("  ✅ Created device_history table")
        
        # 3. Create duplicate_detection_log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS duplicate_detection_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id INTEGER,
                potential_duplicate_id INTEGER,
                confidence_score REAL,
                duplicate_type TEXT,
                resolution_action TEXT,
                detected_at TEXT,
                resolved_at TEXT,
                resolved_by TEXT,
                manual_review_required INTEGER DEFAULT 0,
                resolution_notes TEXT,
                FOREIGN KEY (device_id) REFERENCES assets (id),
                FOREIGN KEY (potential_duplicate_id) REFERENCES assets (id)
            )
        ''')
        print("  ✅ Created duplicate_detection_log table")
        
        # 4. Create manual_review_queue table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS manual_review_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id INTEGER,
                potential_duplicate_id INTEGER,
                priority TEXT DEFAULT 'medium',
                confidence_score REAL,
                duplicate_type TEXT,
                conflict_details TEXT,
                created_at TEXT,
                assigned_to TEXT,
                status TEXT DEFAULT 'pending',
                resolved_at TEXT,
                resolution_action TEXT,
                resolution_notes TEXT,
                FOREIGN KEY (device_id) REFERENCES assets (id),
                FOREIGN KEY (potential_duplicate_id) REFERENCES assets (id)
            )
        ''')
        print("  ✅ Created manual_review_queue table")
        
        # 5. Create duplicate_statistics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS duplicate_statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                collection_date TEXT,
                total_devices_scanned INTEGER,
                duplicates_detected INTEGER,
                auto_resolved INTEGER,
                manual_review_required INTEGER,
                resolution_types TEXT,  -- JSON string
                confidence_distribution TEXT,  -- JSON string
                processing_time_seconds REAL,
                data_quality_improvements INTEGER,
                created_at TEXT
            )
        ''')
        print("  ✅ Created duplicate_statistics table")
        
        # 6. Create indexes for performance
        indexes = [
            ('idx_device_fingerprint', 'assets', 'device_fingerprint'),
            ('idx_serial_number', 'assets', 'serial_number'),
            ('idx_mac_address', 'assets', 'mac_address'),
            ('idx_hostname', 'assets', 'computer_name'),
            ('idx_working_user', 'assets', 'working_user'),
            ('idx_duplicate_status', 'assets', 'duplicate_status'),
            ('idx_duplicate_group', 'assets', 'duplicate_group_id'),
            ('idx_last_collection', 'assets', 'last_collection_date'),
            ('idx_device_history_device', 'device_history', 'device_id'),
            ('idx_device_history_date', 'device_history', 'changed_at'),
            ('idx_duplicate_log_device', 'duplicate_detection_log', 'device_id'),
            ('idx_duplicate_log_date', 'duplicate_detection_log', 'detected_at'),
            ('idx_review_queue_priority', 'manual_review_queue', 'priority'),
            ('idx_review_queue_status', 'manual_review_queue', 'status')
        ]
        
        for index_name, table_name, column_name in indexes:
            try:
                cursor.execute(f'CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} ({column_name})')
                print(f"  ✅ Created index: {index_name}")
            except sqlite3.Error as e:
                print(f"  ❌ Error creating index {index_name}: {e}")
        
        # 7. Create views for easier querying
        
        # Duplicate candidates view
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS duplicate_candidates AS
            SELECT 
                a1.id as device1_id,
                a1.computer_name as device1_name,
                a1.serial_number as device1_serial,
                a1.working_user as device1_user,
                a2.id as device2_id,
                a2.computer_name as device2_name,
                a2.serial_number as device2_serial,
                a2.working_user as device2_user,
                CASE 
                    WHEN a1.serial_number = a2.serial_number THEN 'serial_match'
                    WHEN a1.mac_address = a2.mac_address THEN 'mac_match'
                    WHEN a1.computer_name = a2.computer_name THEN 'hostname_match'
                    ELSE 'other'
                END as match_type
            FROM assets a1, assets a2
            WHERE a1.id < a2.id
            AND (
                a1.serial_number = a2.serial_number OR
                a1.mac_address = a2.mac_address OR
                a1.computer_name = a2.computer_name
            )
            AND a1.is_archived = 0 
            AND a2.is_archived = 0
        ''')
        print("  ✅ Created duplicate_candidates view")
        
        # Data quality summary view
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS data_quality_summary AS
            SELECT 
                COUNT(*) as total_devices,
                SUM(CASE WHEN serial_number IS NOT NULL AND serial_number != '' THEN 1 ELSE 0 END) as has_serial,
                SUM(CASE WHEN mac_address IS NOT NULL AND mac_address != '' THEN 1 ELSE 0 END) as has_mac,
                SUM(CASE WHEN working_user IS NOT NULL AND working_user != '' THEN 1 ELSE 0 END) as has_user,
                SUM(CASE WHEN duplicate_status = 'duplicate' THEN 1 ELSE 0 END) as duplicates,
                SUM(CASE WHEN is_archived = 1 THEN 1 ELSE 0 END) as archived,
                AVG(data_quality_score) as avg_quality_score,
                COUNT(DISTINCT duplicate_group_id) as duplicate_groups
            FROM assets
            WHERE is_archived = 0
        ''')
        print("  ✅ Created data_quality_summary view")
        
        self.conn.commit()
        print("\n🎉 Duplicate prevention schema setup complete!")
        
        return True
        
    def analyze_existing_duplicates(self):
        """Analyze existing data for potential duplicates"""
        if not self.conn:
            self.connect()
            
        if not self.conn:
            print("❌ Failed to establish database connection")
            return
            
        cursor = self.conn.cursor()
        
        print("\n🔍 Analyzing existing data for potential duplicates...")
        
        # Check for exact serial number matches
        cursor.execute('''
            SELECT serial_number, COUNT(*) as count
            FROM assets 
            WHERE serial_number IS NOT NULL 
            AND serial_number != ''
            AND is_archived = 0
            GROUP BY serial_number 
            HAVING COUNT(*) > 1
            ORDER BY count DESC
        ''')
        
        serial_duplicates = cursor.fetchall()
        if serial_duplicates:
            print(f"\n⚠️  Found {len(serial_duplicates)} serial numbers with multiple devices:")
            for row in serial_duplicates[:10]:  # Show top 10
                print(f"  📋 Serial '{row['serial_number']}': {row['count']} devices")
        else:
            print("  ✅ No exact serial number duplicates found")
        
        # Check for MAC address matches
        cursor.execute('''
            SELECT mac_address, COUNT(*) as count
            FROM assets 
            WHERE mac_address IS NOT NULL 
            AND mac_address != ''
            AND is_archived = 0
            GROUP BY mac_address 
            HAVING COUNT(*) > 1
            ORDER BY count DESC
        ''')
        
        mac_duplicates = cursor.fetchall()
        if mac_duplicates:
            print(f"\n⚠️  Found {len(mac_duplicates)} MAC addresses with multiple devices:")
            for row in mac_duplicates[:10]:  # Show top 10
                print(f"  🌐 MAC '{row['mac_address']}': {row['count']} devices")
        else:
            print("  ✅ No MAC address duplicates found")
        
        # Check for hostname matches
        cursor.execute('''
            SELECT computer_name, COUNT(*) as count
            FROM assets 
            WHERE computer_name IS NOT NULL 
            AND computer_name != ''
            AND is_archived = 0
            GROUP BY computer_name 
            HAVING COUNT(*) > 1
            ORDER BY count DESC
        ''')
        
        hostname_duplicates = cursor.fetchall()
        if hostname_duplicates:
            print(f"\n⚠️  Found {len(hostname_duplicates)} hostnames with multiple devices:")
            for row in hostname_duplicates[:10]:  # Show top 10
                print(f"  💻 Hostname '{row['computer_name']}': {row['count']} devices")
        else:
            print("  ✅ No hostname duplicates found")
        
        # Overall data quality
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN serial_number IS NOT NULL AND serial_number != '' THEN 1 ELSE 0 END) as has_serial,
                SUM(CASE WHEN mac_address IS NOT NULL AND mac_address != '' THEN 1 ELSE 0 END) as has_mac,
                SUM(CASE WHEN computer_name IS NOT NULL AND computer_name != '' THEN 1 ELSE 0 END) as has_hostname,
                SUM(CASE WHEN working_user IS NOT NULL AND working_user != '' THEN 1 ELSE 0 END) as has_user
            FROM assets
            WHERE is_archived = 0
        ''')
        
        quality = cursor.fetchone()
        if quality:
            print(f"\n📊 Data Quality Summary:")
            print(f"  📱 Total active devices: {quality['total']}")
            print(f"  📋 Has serial number: {quality['has_serial']} ({quality['has_serial']/quality['total']*100:.1f}%)")
            print(f"  🌐 Has MAC address: {quality['has_mac']} ({quality['has_mac']/quality['total']*100:.1f}%)")
            print(f"  💻 Has hostname: {quality['has_hostname']} ({quality['has_hostname']/quality['total']*100:.1f}%)")
            print(f"  👤 Has user: {quality['has_user']} ({quality['has_user']/quality['total']*100:.1f}%)")
        
        return {
            'serial_duplicates': len(serial_duplicates),
            'mac_duplicates': len(mac_duplicates),
            'hostname_duplicates': len(hostname_duplicates),
            'total_devices': quality['total'] if quality else 0
        }
    
    def create_sample_duplicate_scenarios(self):
        """Create sample data to test duplicate detection"""
        if not self.conn:
            self.connect()
            
        if not self.conn:
            print("❌ Failed to establish database connection")
            return
            
        cursor = self.conn.cursor()
        
        print("\n🧪 Creating sample duplicate scenarios for testing...")
        
        # Sample scenario 1: User transfer
        sample_data = [
            {
                'computer_name': 'WS-SAMPLE-001',
                'serial_number': 'TEST123456',
                'mac_address': '00:11:22:33:44:55',
                'working_user': 'john.doe',
                'ip_address': '10.0.21.100',
                'manufacturer': 'Dell',
                'model': 'OptiPlex 7090',
                'memory_gb': 16,
                'last_collection_date': '2024-09-01',
                'device_fingerprint': 'test_fp_001',
                'duplicate_status': 'unique'
            },
            {
                'computer_name': 'WS-SAMPLE-001',
                'serial_number': 'TEST123456',
                'mac_address': '00:11:22:33:44:55',
                'working_user': 'jane.smith',  # Different user - transfer scenario
                'ip_address': '10.0.22.100',   # Different IP - moved
                'manufacturer': 'Dell',
                'model': 'OptiPlex 7090',
                'memory_gb': 16,
                'last_collection_date': '2024-10-01',
                'device_fingerprint': 'test_fp_001',
                'duplicate_status': 'pending_review'
            }
        ]
        
        for data in sample_data:
            # Check if sample already exists
            cursor.execute('SELECT id FROM assets WHERE device_fingerprint = ?', (data['device_fingerprint'],))
            if not cursor.fetchone():
                columns = ', '.join(data.keys())
                placeholders = ', '.join(['?' for _ in data])
                cursor.execute(f'INSERT INTO assets ({columns}) VALUES ({placeholders})', list(data.values()))
                print(f"  ✅ Created sample device: {data['computer_name']} - {data['working_user']}")
        
        if self.conn:
            self.conn.commit()
        print("  🎯 Sample scenarios created for testing")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

def main():
    """Main function to set up duplicate prevention schema"""
    print("🚀 Setting up Database Schema for Duplicate Prevention")
    print("=" * 60)
    
    # Check if database exists
    db_path = 'assets.db'
    if not os.path.exists(db_path):
        print(f"❌ Database file '{db_path}' not found!")
        print("Please run the asset collection system first to create the database.")
        return
    
    # Initialize schema setup
    schema_setup = DuplicatePreventionSchema(db_path)
    
    try:
        # Set up schema
        success = schema_setup.setup_duplicate_prevention_schema()
        
        if success:
            # Analyze existing data
            analysis = schema_setup.analyze_existing_duplicates()
            
            # Create sample scenarios for testing
            schema_setup.create_sample_duplicate_scenarios()
            
            print("\n" + "=" * 60)
            print("🎉 DATABASE SCHEMA SETUP COMPLETE!")
            print("=" * 60)
            print("\n📋 What's been added:")
            print("  ✅ Duplicate detection columns in assets table")
            print("  ✅ device_history table for audit trail")
            print("  ✅ duplicate_detection_log table")
            print("  ✅ manual_review_queue table")
            print("  ✅ duplicate_statistics table")
            print("  ✅ Performance indexes")
            print("  ✅ Helper views for querying")
            print("  ✅ Sample test data")
            
            print(f"\n📊 Current Status:")
            if analysis:
                print(f"  📱 Total devices: {analysis['total_devices']}")
                print(f"  ⚠️  Potential serial duplicates: {analysis['serial_duplicates']}")
                print(f"  ⚠️  Potential MAC duplicates: {analysis['mac_duplicates']}")
                print(f"  ⚠️  Potential hostname duplicates: {analysis['hostname_duplicates']}")
            else:
                print("  ⚠️  Analysis data unavailable")
            
            print(f"\n🚀 Ready for duplicate detection testing!")
            print(f"  💻 Run smart_duplicate_detector.py to test detection")
            print(f"  📊 Run collection_duplicate_manager.py for bulk processing")
            
    except Exception as e:
        print(f"❌ Error setting up schema: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        schema_setup.close()

if __name__ == '__main__':
    main()