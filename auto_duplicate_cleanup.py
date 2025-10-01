#!/usr/bin/env python3
"""
Automatic Duplicate Detection and Test Data Cleanup System
Detects duplicates automatically and cleans test data
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

class AutoDuplicateCleanupSystem:
    def __init__(self, db_path="assets.db"):
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        """Connect to database"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def fix_duplicate_detection_schema(self):
        """Fix the duplicate detection schema issues"""
        if not self.connect():
            return False
            
        try:
            if not self.conn:
                return False
            cursor = self.conn.cursor()
            
            # Check if duplicate_match_id column exists
            cursor.execute("PRAGMA table_info(assets)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'duplicate_match_id' not in columns:
                print("🔧 Adding duplicate_match_id column...")
                cursor.execute("ALTER TABLE assets ADD COLUMN duplicate_match_id TEXT")
                
            if 'duplicate_status' not in columns:
                print("🔧 Adding duplicate_status column...")
                cursor.execute("ALTER TABLE assets ADD COLUMN duplicate_status TEXT DEFAULT 'active'")
                
            if 'duplicate_confidence' not in columns:
                print("🔧 Adding duplicate_confidence column...")
                cursor.execute("ALTER TABLE assets ADD COLUMN duplicate_confidence REAL")
                
            self.conn.commit()
            print("✅ Duplicate detection schema updated successfully")
            return True
            
        except Exception as e:
            print(f"❌ Schema update failed: {e}")
            return False
    
    def detect_and_mark_duplicates(self):
        """Detect duplicates and mark them automatically"""
        if not self.connect():
            return
            
        try:
            if not self.conn:
                return
            cursor = self.conn.cursor()
            duplicates_found = 0
            
            print("🔍 DETECTING DUPLICATES...")
            print("=" * 40)
            
            # 1. Find hostname duplicates
            cursor.execute("""
                SELECT hostname, COUNT(*) as count, GROUP_CONCAT(id) as ids
                FROM assets 
                WHERE hostname != '' AND hostname IS NOT NULL
                GROUP BY hostname 
                HAVING COUNT(*) > 1
            """)
            
            hostname_dups = cursor.fetchall()
            for dup in hostname_dups:
                ids = dup['ids'].split(',')
                match_id = f"HOST_{dup['hostname']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                # Mark all instances with same match_id
                for device_id in ids:
                    cursor.execute("""
                        UPDATE assets 
                        SET duplicate_match_id = ?, duplicate_confidence = 0.9
                        WHERE id = ?
                    """, (match_id, device_id))
                
                duplicates_found += len(ids)
                print(f"🔍 Hostname duplicate: {dup['hostname']} ({len(ids)} instances)")
            
            # 2. Find MAC address duplicates
            cursor.execute("""
                SELECT mac_address, COUNT(*) as count, GROUP_CONCAT(id) as ids
                FROM assets 
                WHERE mac_address != '' AND mac_address IS NOT NULL
                GROUP BY mac_address 
                HAVING COUNT(*) > 1
            """)
            
            mac_dups = cursor.fetchall()
            for dup in mac_dups:
                ids = dup['ids'].split(',')
                match_id = f"MAC_{dup['mac_address'].replace(':', '')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                for device_id in ids:
                    cursor.execute("""
                        UPDATE assets 
                        SET duplicate_match_id = ?, duplicate_confidence = 0.95
                        WHERE id = ?
                    """, (match_id, device_id))
                
                duplicates_found += len(ids)
                print(f"🔍 MAC duplicate: {dup['mac_address']} ({len(ids)} instances)")
            
            # 3. Find serial number duplicates
            cursor.execute("""
                SELECT serial_number, COUNT(*) as count, GROUP_CONCAT(id) as ids
                FROM assets 
                WHERE serial_number != '' AND serial_number IS NOT NULL
                GROUP BY serial_number 
                HAVING COUNT(*) > 1
            """)
            
            serial_dups = cursor.fetchall()
            for dup in serial_dups:
                ids = dup['ids'].split(',')
                match_id = f"SERIAL_{dup['serial_number']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                for device_id in ids:
                    cursor.execute("""
                        UPDATE assets 
                        SET duplicate_match_id = ?, duplicate_confidence = 0.98
                        WHERE id = ?
                    """, (match_id, device_id))
                
                duplicates_found += len(ids)
                print(f"🔍 Serial duplicate: {dup['serial_number']} ({len(ids)} instances)")
            
            self.conn.commit()
            print(f"\n✅ Marked {duplicates_found} duplicate devices")
            
        except Exception as e:
            print(f"❌ Duplicate detection failed: {e}")
    
    def clean_test_data(self):
        """Remove test data automatically"""
        if not self.connect():
            return
            
        try:
            if not self.conn:
                return
            cursor = self.conn.cursor()
            
            print("\n🧹 CLEANING TEST DATA...")
            print("=" * 30)
            
            # Identify test data patterns
            test_patterns = [
                "WS-TEST-%",
                "DUP-TEST-%", 
                "CONFLICT-%",
                "TEST-%",
                "%TEST%"
            ]
            
            test_devices_found = 0
            
            for pattern in test_patterns:
                # Find test devices by hostname
                cursor.execute("SELECT id, hostname, ip_address FROM assets WHERE hostname LIKE ?", (pattern,))
                test_devices = cursor.fetchall()
                
                if test_devices:
                    print(f"🗑️  Found {len(test_devices)} devices matching pattern: {pattern}")
                    for device in test_devices:
                        print(f"   • ID:{device['id']} {device['hostname']} ({device['ip_address']})")
                    
                    test_devices_found += len(test_devices)
            
            # Also check for test serial numbers
            cursor.execute("SELECT id, hostname, serial_number FROM assets WHERE serial_number LIKE 'DUP-TEST-%' OR serial_number LIKE 'CONFLICT-%'")
            test_serials = cursor.fetchall()
            
            if test_serials:
                print(f"🗑️  Found {len(test_serials)} devices with test serial numbers")
                for device in test_serials:
                    print(f"   • ID:{device['id']} {device['hostname']} (S/N: {device['serial_number']})")
                test_devices_found += len(test_serials)
            
            if test_devices_found > 0:
                confirm = input(f"\n⚠️  Found {test_devices_found} test devices. Delete them? (yes/no): ").lower()
                
                if confirm == 'yes':
                    deleted_count = 0
                    
                    # Delete by hostname patterns
                    for pattern in test_patterns:
                        cursor.execute("DELETE FROM assets WHERE hostname LIKE ?", (pattern,))
                        deleted_count += cursor.rowcount
                    
                    # Delete by test serial numbers
                    cursor.execute("DELETE FROM assets WHERE serial_number LIKE 'DUP-TEST-%' OR serial_number LIKE 'CONFLICT-%'")
                    deleted_count += cursor.rowcount
                    
                    self.conn.commit()
                    print(f"✅ Deleted {deleted_count} test devices")
                else:
                    print("⏭️  Skipped test data deletion")
            else:
                print("✅ No test data found to clean")
                
        except Exception as e:
            print(f"❌ Test data cleanup failed: {e}")
    
    def auto_resolve_exact_duplicates(self):
        """Automatically resolve exact duplicates (keep most recent)"""
        if not self.connect():
            return
            
        try:
            if not self.conn:
                return
            cursor = self.conn.cursor()
            
            print("\n🤖 AUTO-RESOLVING EXACT DUPLICATES...")
            print("=" * 40)
            
            # Find exact duplicates (same IP, same hostname, same serial)
            cursor.execute("""
                SELECT ip_address, hostname, serial_number, COUNT(*) as count, GROUP_CONCAT(id) as ids
                FROM assets 
                WHERE duplicate_match_id IS NOT NULL
                GROUP BY ip_address, hostname, serial_number
                HAVING COUNT(*) > 1
            """)
            
            exact_duplicates = cursor.fetchall()
            resolved_count = 0
            
            for dup in exact_duplicates:
                ids = dup['ids'].split(',')
                
                # Get detailed info for each duplicate
                cursor.execute(f"""
                    SELECT id, last_seen, collection_method
                    FROM assets 
                    WHERE id IN ({','.join(['?'] * len(ids))})
                    ORDER BY datetime(last_seen) DESC
                """, ids)
                
                devices = cursor.fetchall()
                
                if len(devices) > 1:
                    # Keep the most recently updated device
                    keep_device = devices[0]
                    delete_devices = devices[1:]
                    
                    print(f"🔄 Resolving exact duplicate: {dup['hostname']} ({dup['ip_address']})")
                    print(f"   • Keeping: ID {keep_device['id']} (last seen: {keep_device['last_seen']})")
                    
                    for delete_device in delete_devices:
                        print(f"   • Deleting: ID {delete_device['id']} (last seen: {delete_device['last_seen']})")
                        cursor.execute("DELETE FROM assets WHERE id = ?", (delete_device['id'],))
                        resolved_count += 1
                    
                    # Update the kept device to mark as resolved
                    cursor.execute("""
                        UPDATE assets 
                        SET duplicate_status = 'resolved_auto', duplicate_match_id = NULL
                        WHERE id = ?
                    """, (keep_device['id'],))
            
            self.conn.commit()
            print(f"\n✅ Auto-resolved {resolved_count} exact duplicates")
            
        except Exception as e:
            print(f"❌ Auto-resolution failed: {e}")
    
    def generate_duplicate_report(self):
        """Generate a report of remaining duplicates"""
        if not self.connect():
            return
            
        try:
            if not self.conn:
                return
            cursor = self.conn.cursor()
            
            print("\n📊 DUPLICATE DETECTION REPORT")
            print("=" * 40)
            
            # Count remaining duplicates
            cursor.execute("""
                SELECT COUNT(DISTINCT duplicate_match_id) as duplicate_groups
                FROM assets 
                WHERE duplicate_match_id IS NOT NULL AND duplicate_status != 'resolved_auto'
            """)
            
            remaining_groups = cursor.fetchone()['duplicate_groups']
            
            cursor.execute("""
                SELECT COUNT(*) as duplicate_devices
                FROM assets 
                WHERE duplicate_match_id IS NOT NULL AND duplicate_status != 'resolved_auto'
            """)
            
            remaining_devices = cursor.fetchone()['duplicate_devices']
            
            print(f"📊 Total devices in database: {self.get_total_device_count()}")
            print(f"⚠️  Remaining duplicate groups: {remaining_groups}")
            print(f"⚠️  Remaining duplicate devices: {remaining_devices}")
            
            if remaining_groups > 0:
                print("\n🔍 REMAINING DUPLICATES REQUIRING MANUAL REVIEW:")
                cursor.execute("""
                    SELECT duplicate_match_id, COUNT(*) as count, 
                           GROUP_CONCAT(hostname || ' (' || ip_address || ')') as devices
                    FROM assets 
                    WHERE duplicate_match_id IS NOT NULL AND duplicate_status != 'resolved_auto'
                    GROUP BY duplicate_match_id
                    ORDER BY count DESC
                """)
                
                manual_review = cursor.fetchall()
                for group in manual_review:
                    print(f"   • {group['duplicate_match_id']}: {group['count']} devices")
                    devices = group['devices'].split(',')
                    for device in devices[:3]:  # Show first 3
                        print(f"     - {device}")
                    if len(devices) > 3:
                        print(f"     - ... and {len(devices) - 3} more")
            
        except Exception as e:
            print(f"❌ Report generation failed: {e}")
    
    def get_total_device_count(self):
        """Get total device count"""
        try:
            if not self.conn:
                return 0
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) as total FROM assets")
            return cursor.fetchone()['total']
        except:
            return 0
    
    def run_full_cleanup(self):
        """Run the complete automatic cleanup process"""
        print("🚀 STARTING AUTOMATIC DUPLICATE CLEANUP")
        print("=" * 50)
        
        # Step 1: Fix schema
        print("Step 1: Fixing duplicate detection schema...")
        if not self.fix_duplicate_detection_schema():
            print("❌ Schema fix failed. Aborting.")
            return
        
        # Step 2: Clean test data
        print("\nStep 2: Cleaning test data...")
        self.clean_test_data()
        
        # Step 3: Detect and mark duplicates
        print("\nStep 3: Detecting and marking duplicates...")
        self.detect_and_mark_duplicates()
        
        # Step 4: Auto-resolve exact duplicates
        print("\nStep 4: Auto-resolving exact duplicates...")
        self.auto_resolve_exact_duplicates()
        
        # Step 5: Generate final report
        print("\nStep 5: Generating final report...")
        self.generate_duplicate_report()
        
        print("\n🎉 AUTOMATIC CLEANUP COMPLETE!")
        
        if self.conn:
            self.conn.close()

if __name__ == "__main__":
    cleanup_system = AutoDuplicateCleanupSystem()
    cleanup_system.run_full_cleanup()