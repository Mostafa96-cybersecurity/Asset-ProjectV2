#!/usr/bin/env python3
"""
Duplicate Prevention Integration for Collection System
Integrates smart duplicate detection with hierarchical collection
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional
from smart_duplicate_detector import SmartDuplicateDetector, DuplicateMatch, ResolutionAction

class CollectionDuplicateManager:
    """Manages duplicates during collection operations"""
    
    def __init__(self, db_path: str = "assets.db"):
        self.db_path = db_path
        self.detector = SmartDuplicateDetector(db_path)
        self.collection_stats = {
            'devices_processed': 0,
            'duplicates_found': 0,
            'auto_resolved': 0,
            'flagged_for_review': 0,
            'new_devices_added': 0,
            'devices_updated': 0
        }
    
    def process_collected_device(self, device_data: Dict, collection_method: str = 'auto') -> Dict:
        """Process a newly collected device with duplicate detection"""
        
        self.collection_stats['devices_processed'] += 1
        
        # Detect potential duplicates
        matches = self.detector.detect_duplicates(device_data)
        
        if not matches:
            # No duplicates found - add as new device
            result = self._add_new_device(device_data, collection_method)
            self.collection_stats['new_devices_added'] += 1
            return result
        
        # Process the best match
        best_match = matches[0]
        self.collection_stats['duplicates_found'] += 1
        
        # Auto-resolve if confidence is high enough
        if best_match.confidence >= 0.85:
            result = self._auto_resolve_duplicate(best_match, collection_method)
            self.collection_stats['auto_resolved'] += 1
        else:
            result = self._flag_for_manual_review(best_match, collection_method)
            self.collection_stats['flagged_for_review'] += 1
        
        return result
    
    def _add_new_device(self, device_data: Dict, collection_method: str) -> Dict:
        """Add a new device to the database"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Add collection metadata
            enhanced_data = device_data.copy()
            enhanced_data.update({
                'collection_date': datetime.now().isoformat(),
                'collection_method': collection_method,
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                '_duplicate_checked': True,
                '_duplicate_check_date': datetime.now().isoformat()
            })
            
            # Insert new device
            columns = list(enhanced_data.keys())
            placeholders = ', '.join(['?' for _ in columns])
            query = f"INSERT INTO assets ({', '.join(columns)}) VALUES ({placeholders})"
            
            cursor.execute(query, list(enhanced_data.values()))
            new_id = cursor.lastrowid
            
            conn.commit()
            
            return {
                'status': 'new_device_added',
                'device_id': new_id,
                'action': 'created',
                'hostname': device_data.get('hostname', 'Unknown'),
                'ip_address': device_data.get('ip_address', 'Unknown'),
                'message': 'New device successfully added to inventory'
            }
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _auto_resolve_duplicate(self, match: DuplicateMatch, collection_method: str) -> Dict:
        """Automatically resolve a high-confidence duplicate"""
        
        # Log the resolution
        self._log_duplicate_resolution(match, 'auto_resolved', collection_method)
        
        # Resolve the duplicate
        resolution_result = self.detector.resolve_duplicate(match)
        
        self.collection_stats['devices_updated'] += 1
        
        return {
            'status': 'duplicate_resolved',
            'device_id': resolution_result['device_id'],
            'action': resolution_result['action'],
            'confidence': f"{match.confidence:.1%}",
            'duplicate_type': match.duplicate_type.value,
            'hostname': match.new_device.get('hostname', 'Unknown'),
            'ip_address': match.new_device.get('ip_address', 'Unknown'),
            'message': f"Duplicate auto-resolved: {match.reason}"
        }
    
    def _flag_for_manual_review(self, match: DuplicateMatch, collection_method: str) -> Dict:
        """Flag a potential duplicate for manual review"""
        
        # Log the flag
        self._log_duplicate_resolution(match, 'flagged_for_review', collection_method)
        
        # Create flagged entry
        resolution_result = self.detector.resolve_duplicate(match)
        
        return {
            'status': 'flagged_for_review',
            'device_id': resolution_result.get('new_device_id', resolution_result.get('device_id')),
            'existing_device_id': resolution_result.get('existing_device_id'),
            'action': 'flagged',
            'confidence': f"{match.confidence:.1%}",
            'duplicate_type': match.duplicate_type.value,
            'hostname': match.new_device.get('hostname', 'Unknown'),
            'ip_address': match.new_device.get('ip_address', 'Unknown'),
            'message': f"Potential duplicate flagged for review: {match.reason}"
        }
    
    def _log_duplicate_resolution(self, match: DuplicateMatch, action: str, collection_method: str):
        """Log duplicate resolution for audit trail"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO duplicate_resolution_log 
                (existing_device_id, new_device_data, duplicate_type, confidence, 
                 resolution_action, reason, resolved_at, resolved_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                match.existing_id,
                json.dumps(match.new_device),
                match.duplicate_type.value,
                match.confidence,
                action,
                match.reason,
                datetime.now().isoformat(),
                f'auto_collector_{collection_method}'
            ))
            
            conn.commit()
        finally:
            conn.close()
    
    def batch_process_devices(self, devices_list: List[Dict], collection_method: str = 'batch') -> Dict:
        """Process multiple devices in batch with duplicate detection"""
        
        results = {
            'total_processed': 0,
            'new_devices': [],
            'updated_devices': [],
            'duplicates_resolved': [],
            'flagged_devices': [],
            'errors': [],
            'summary': {}
        }
        
        for device_data in devices_list:
            try:
                result = self.process_collected_device(device_data, collection_method)
                
                if result['status'] == 'new_device_added':
                    results['new_devices'].append(result)
                elif result['status'] == 'duplicate_resolved':
                    results['duplicates_resolved'].append(result)
                elif result['status'] == 'flagged_for_review':
                    results['flagged_devices'].append(result)
                
                results['total_processed'] += 1
                
            except Exception as e:
                results['errors'].append({
                    'device': device_data.get('hostname', 'Unknown'),
                    'error': str(e)
                })
        
        # Generate summary
        results['summary'] = self.collection_stats.copy()
        
        return results
    
    def get_duplicate_review_queue(self) -> List[Dict]:
        """Get devices flagged for duplicate review"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, hostname, ip_address, serial_number, mac_addresses,
                       working_user, duplicate_match_id, duplicate_confidence,
                       duplicate_reason, flagged_at
                FROM assets 
                WHERE duplicate_review_needed = 1
                ORDER BY duplicate_confidence DESC, flagged_at DESC
            """)
            
            flagged_devices = cursor.fetchall()
            
            review_queue = []
            for device in flagged_devices:
                # Get the matching device details
                cursor.execute("""
                    SELECT id, hostname, ip_address, serial_number, working_user
                    FROM assets WHERE id = ?
                """, (device[6],))  # duplicate_match_id
                
                match_device = cursor.fetchone()
                
                review_queue.append({
                    'flagged_device': {
                        'id': device[0],
                        'hostname': device[1],
                        'ip_address': device[2],
                        'serial_number': device[3],
                        'mac_addresses': device[4],
                        'working_user': device[5],
                        'confidence': device[7],
                        'reason': device[8],
                        'flagged_at': device[9]
                    },
                    'matching_device': {
                        'id': match_device[0] if match_device else None,
                        'hostname': match_device[1] if match_device else None,
                        'ip_address': match_device[2] if match_device else None,
                        'serial_number': match_device[3] if match_device else None,
                        'working_user': match_device[4] if match_device else None
                    } if match_device else None
                })
            
            return review_queue
            
        finally:
            conn.close()
    
    def manual_resolve_duplicate(self, flagged_device_id: int, action: str, user: str = 'manual') -> Dict:
        """Manually resolve a flagged duplicate"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if action == 'merge_and_keep_flagged':
                # Keep the flagged device, remove duplicate flag
                cursor.execute("""
                    UPDATE assets 
                    SET duplicate_flag = 0, duplicate_review_needed = 0,
                        _duplicate_resolved_at = ?, _resolution_action = ?,
                        last_updated = ?, updated_by = ?
                    WHERE id = ?
                """, (datetime.now().isoformat(), action, datetime.now().isoformat(), user, flagged_device_id))
                
                result = {'action': 'kept_flagged_device', 'device_id': flagged_device_id}
                
            elif action == 'merge_and_keep_original':
                # Get match ID and remove flagged device
                cursor.execute("SELECT duplicate_match_id FROM assets WHERE id = ?", (flagged_device_id,))
                match_id = cursor.fetchone()[0]
                
                cursor.execute("DELETE FROM assets WHERE id = ?", (flagged_device_id,))
                
                # Update original device
                cursor.execute("""
                    UPDATE assets 
                    SET duplicate_flag = 0, duplicate_review_needed = 0,
                        _duplicate_resolved_at = ?, _resolution_action = ?,
                        last_updated = ?, updated_by = ?
                    WHERE id = ?
                """, (datetime.now().isoformat(), action, datetime.now().isoformat(), user, match_id))
                
                result = {'action': 'kept_original_device', 'device_id': match_id}
                
            elif action == 'keep_both':
                # Remove duplicate flags from both
                cursor.execute("SELECT duplicate_match_id FROM assets WHERE id = ?", (flagged_device_id,))
                match_id = cursor.fetchone()[0]
                
                for device_id in [flagged_device_id, match_id]:
                    cursor.execute("""
                        UPDATE assets 
                        SET duplicate_flag = 0, duplicate_review_needed = 0,
                            _duplicate_resolved_at = ?, _resolution_action = ?,
                            last_updated = ?, updated_by = ?
                        WHERE id = ?
                    """, (datetime.now().isoformat(), action, datetime.now().isoformat(), user, device_id))
                
                result = {'action': 'kept_both_devices', 'devices': [flagged_device_id, match_id]}
            
            conn.commit()
            return result
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_collection_statistics(self) -> Dict:
        """Get comprehensive collection and duplicate statistics"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            stats = {}
            
            # Total devices
            cursor.execute("SELECT COUNT(*) FROM assets")
            stats['total_devices'] = cursor.fetchone()[0]
            
            # Flagged devices
            cursor.execute("SELECT COUNT(*) FROM assets WHERE duplicate_flag = 1")
            stats['flagged_duplicates'] = cursor.fetchone()[0]
            
            # Devices needing review
            cursor.execute("SELECT COUNT(*) FROM assets WHERE duplicate_review_needed = 1")
            stats['needs_review'] = cursor.fetchone()[0]
            
            # Recent collections (last 7 days)
            cursor.execute("""
                SELECT COUNT(*) FROM assets 
                WHERE collection_date > datetime('now', '-7 days')
            """)
            stats['recent_collections'] = cursor.fetchone()[0]
            
            # Collection methods breakdown
            cursor.execute("""
                SELECT collection_method, COUNT(*) 
                FROM assets 
                WHERE collection_method IS NOT NULL
                GROUP BY collection_method
            """)
            stats['collection_methods'] = dict(cursor.fetchall())
            
            # Duplicate resolution history
            cursor.execute("""
                SELECT resolution_action, COUNT(*) 
                FROM duplicate_resolution_log 
                GROUP BY resolution_action
            """)
            stats['resolution_history'] = dict(cursor.fetchall())
            
            # Add current session stats
            stats['session_stats'] = self.collection_stats
            
            return stats
            
        finally:
            conn.close()

def setup_duplicate_prevention_database():
    """Set up database schema for duplicate prevention"""
    
    conn = sqlite3.connect("assets.db")
    cursor = conn.cursor()
    
    try:
        # Add duplicate detection columns (if they don't exist)
        new_columns = [
            ("duplicate_flag", "BOOLEAN DEFAULT FALSE"),
            ("duplicate_review_needed", "BOOLEAN DEFAULT FALSE"), 
            ("duplicate_match_id", "INTEGER"),
            ("duplicate_confidence", "REAL"),
            ("duplicate_reason", "TEXT"),
            ("flagged_at", "TEXT"),
            ("_duplicate_resolved_at", "TEXT"),
            ("_resolution_action", "TEXT"),
            ("_resolution_reason", "TEXT"),
            ("_duplicate_checked", "BOOLEAN DEFAULT FALSE"),
            ("_device_fingerprint", "TEXT"),
            ("_duplicate_check_date", "TEXT")
        ]
        
        for column_name, column_def in new_columns:
            try:
                cursor.execute(f"ALTER TABLE assets ADD COLUMN {column_name} {column_def}")
                print(f"✅ Added column: {column_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"⚠️  Column {column_name} already exists")
                else:
                    raise
        
        # Create duplicate resolution log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS duplicate_resolution_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                existing_device_id INTEGER,
                new_device_data TEXT,
                duplicate_type TEXT,
                confidence REAL,
                resolution_action TEXT,
                reason TEXT,
                resolved_at TEXT,
                resolved_by TEXT,
                FOREIGN KEY (existing_device_id) REFERENCES assets (id)
            )
        """)
        print("✅ Created duplicate_resolution_log table")
        
        # Create performance indexes
        indexes = [
            ("idx_assets_duplicate_flag", "CREATE INDEX IF NOT EXISTS idx_assets_duplicate_flag ON assets (duplicate_flag)"),
            ("idx_assets_serial_number", "CREATE INDEX IF NOT EXISTS idx_assets_serial_number ON assets (serial_number)"),
            ("idx_assets_mac_addresses", "CREATE INDEX IF NOT EXISTS idx_assets_mac_addresses ON assets (mac_addresses)"),
            ("idx_assets_hostname", "CREATE INDEX IF NOT EXISTS idx_assets_hostname ON assets (hostname)"),
            ("idx_assets_ip_address", "CREATE INDEX IF NOT EXISTS idx_assets_ip_address ON assets (ip_address)")
        ]
        
        for index_name, index_sql in indexes:
            cursor.execute(index_sql)
            print(f"✅ Created index: {index_name}")
        
        conn.commit()
        print("\n🎉 Duplicate prevention database setup completed!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error setting up database: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    print("🔧 DUPLICATE PREVENTION SYSTEM SETUP")
    print("=" * 50)
    
    # Setup database
    setup_duplicate_prevention_database()
    
    print("\n📊 DUPLICATE PREVENTION DEMO")
    print("-" * 30)
    
    # Initialize the manager
    manager = CollectionDuplicateManager()
    
    # Example devices
    test_devices = [
        {
            'hostname': 'WS-TEST-001',
            'ip_address': '10.0.21.100',
            'serial_number': 'TEST123456',
            'mac_addresses': '00:11:22:33:44:55',
            'working_user': 'john.doe',
            'operating_system': 'Windows 11 Pro'
        },
        {
            'hostname': 'WS-TEST-001',  # Same hostname
            'ip_address': '10.0.21.101', # Different IP
            'serial_number': 'TEST123456', # Same serial - duplicate!
            'mac_addresses': '00:11:22:33:44:55', # Same MAC
            'working_user': 'jane.smith',  # Different user - transfer?
            'operating_system': 'Windows 11 Pro'
        }
    ]
    
    # Process devices
    results = manager.batch_process_devices(test_devices, 'demo')
    
    print(f"Processed: {results['total_processed']} devices")
    print(f"New devices: {len(results['new_devices'])}")
    print(f"Duplicates resolved: {len(results['duplicates_resolved'])}")
    print(f"Flagged for review: {len(results['flagged_devices'])}")
    
    # Show statistics
    stats = manager.get_collection_statistics()
    print(f"\n📈 STATISTICS:")
    print(f"Total devices: {stats['total_devices']}")
    print(f"Flagged duplicates: {stats['flagged_duplicates']}")
    print(f"Needs review: {stats['needs_review']}")
    
    print("\n✅ DUPLICATE PREVENTION SYSTEM READY!")