#!/usr/bin/env python3
"""
Manual Duplicate Resolution Interface
Provides a simple interface to resolve remaining duplicates
"""

import sqlite3
from datetime import datetime

class ManualDuplicateResolver:
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
    
    def get_duplicate_groups(self):
        """Get all duplicate groups that need manual resolution"""
        if not self.connect():
            return []
            
        try:
            if not self.conn:
                return []
            cursor = self.conn.cursor()
            
            cursor.execute("""
                SELECT duplicate_match_id, COUNT(*) as count
                FROM assets 
                WHERE duplicate_match_id IS NOT NULL AND duplicate_status != 'resolved_auto'
                GROUP BY duplicate_match_id
                ORDER BY count DESC
            """)
            
            return cursor.fetchall()
            
        except Exception as e:
            print(f"❌ Error getting duplicate groups: {e}")
            return []
    
    def get_duplicate_details(self, match_id):
        """Get detailed information about a duplicate group"""
        if not self.connect():
            return []
            
        try:
            if not self.conn:
                return []
            cursor = self.conn.cursor()
            
            cursor.execute("""
                SELECT id, hostname, ip_address, mac_address, serial_number, 
                       os_name, last_seen, collection_method, hard_drives
                FROM assets 
                WHERE duplicate_match_id = ?
                ORDER BY datetime(last_seen) DESC, id
            """, (match_id,))
            
            return cursor.fetchall()
            
        except Exception as e:
            print(f"❌ Error getting duplicate details: {e}")
            return []
    
    def resolve_duplicate_group(self, match_id, keep_id, action="manual"):
        """Resolve a duplicate group by keeping one device and deleting others"""
        if not self.connect():
            return False
            
        try:
            if not self.conn:
                return False
            cursor = self.conn.cursor()
            
            # Get all devices in the group
            devices = self.get_duplicate_details(match_id)
            
            if not devices:
                print("❌ No devices found in this duplicate group")
                return False
            
            # Find the device to keep
            keep_device = None
            for device in devices:
                if device['id'] == keep_id:
                    keep_device = device
                    break
            
            if not keep_device:
                print("❌ Device to keep not found in duplicate group")
                return False
            
            # Delete all other devices
            deleted_count = 0
            for device in devices:
                if device['id'] != keep_id:
                    cursor.execute("DELETE FROM assets WHERE id = ?", (device['id'],))
                    deleted_count += 1
                    print(f"🗑️  Deleted: {device['hostname']} ({device['ip_address']}) - ID:{device['id']}")
            
            # Update the kept device
            cursor.execute("""
                UPDATE assets 
                SET duplicate_status = ?, duplicate_match_id = NULL
                WHERE id = ?
            """, (f"resolved_{action}", keep_id))
            
            self.conn.commit()
            print(f"✅ Kept: {keep_device['hostname']} ({keep_device['ip_address']}) - ID:{keep_device['id']}")
            print(f"✅ Resolved duplicate group: {deleted_count} devices deleted, 1 kept")
            
            return True
            
        except Exception as e:
            print(f"❌ Error resolving duplicate: {e}")
            return False
    
    def quick_resolve_all(self):
        """Quick resolution: keep most recent for all duplicate groups"""
        print("⚡ QUICK RESOLVE ALL DUPLICATES")
        print("=" * 40)
        
        groups = self.get_duplicate_groups()
        
        if not groups:
            print("✅ No duplicates found!")
            return
        
        print(f"Found {len(groups)} duplicate groups")
        confirm = input(f"Auto-resolve all by keeping most recent? (yes/no): ")
        
        if confirm.lower() != 'yes':
            print("⏭️  Cancelled")
            return
        
        resolved_count = 0
        
        for group in groups:
            devices = self.get_duplicate_details(group['duplicate_match_id'])
            if devices:
                # Keep the most recent (first in list)
                keep_device = devices[0]
                if self.resolve_duplicate_group(group['duplicate_match_id'], keep_device['id'], "auto_quick"):
                    resolved_count += 1
        
        print(f"\n🎉 Quick-resolved {resolved_count} duplicate groups!")

if __name__ == "__main__":
    resolver = ManualDuplicateResolver()
    
    print("🔧 DUPLICATE RESOLUTION MENU")
    print("=" * 30)
    print("1. Quick resolve all (keep most recent)")
    print("2. Exit")
    
    while True:
        try:
            choice = input("\nChoose option (1-2): ").strip()
            
            if choice == '1':
                resolver.quick_resolve_all()
            elif choice == '2':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Please enter 1 or 2")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break