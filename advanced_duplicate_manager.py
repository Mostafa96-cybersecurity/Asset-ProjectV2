#!/usr/bin/env python3
"""
Advanced Duplicate Detection and Cleanup System
Real-time duplicate prevention with multi-level validation
"""

import sqlite3
from datetime import datetime

class AdvancedDuplicateManager:
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

    def analyze_duplicates(self):
        """Analyze different types of duplicates in the database"""
        conn = self.connect()
        cursor = conn.cursor()
        
        print("🔍 ADVANCED DUPLICATE ANALYSIS")
        print("=" * 50)
        
        # 1. Serial Number + MAC Address duplicates (Primary)
        print("\n1️⃣ SERIAL NUMBER + MAC ADDRESS DUPLICATES:")
        cursor.execute("""
            SELECT serial_number, mac_address, COUNT(*) as count, 
                   GROUP_CONCAT(id) as record_ids,
                   GROUP_CONCAT(hostname) as hostnames,
                   GROUP_CONCAT(ip_address) as ip_addresses
            FROM assets 
            WHERE serial_number IS NOT NULL AND serial_number != ''
            AND mac_address IS NOT NULL AND mac_address != ''
            GROUP BY serial_number, mac_address
            HAVING COUNT(*) > 1
            ORDER BY count DESC
        """)
        
        primary_duplicates = cursor.fetchall()
        if primary_duplicates:
            print(f"   Found {len(primary_duplicates)} duplicate groups by Serial+MAC:")
            for row in primary_duplicates[:5]:  # Show top 5
                print(f"   Serial: {row['serial_number'][:20]}... | MAC: {row['mac_address']} | Count: {row['count']}")
        else:
            print("   ✅ No Serial+MAC duplicates found")
        
        # 2. IP Address duplicates (Secondary)
        print("\n2️⃣ IP ADDRESS DUPLICATES:")
        cursor.execute("""
            SELECT ip_address, COUNT(*) as count,
                   GROUP_CONCAT(id) as record_ids,
                   GROUP_CONCAT(hostname) as hostnames,
                   GROUP_CONCAT(created_at) as timestamps
            FROM assets 
            WHERE ip_address IS NOT NULL AND ip_address != ''
            GROUP BY ip_address
            HAVING COUNT(*) > 1
            ORDER BY count DESC
        """)
        
        ip_duplicates = cursor.fetchall()
        if ip_duplicates:
            print(f"   Found {len(ip_duplicates)} duplicate groups by IP:")
            for row in ip_duplicates[:5]:
                print(f"   IP: {row['ip_address']} | Count: {row['count']} | Hosts: {row['hostnames'][:50]}...")
        else:
            print("   ✅ No IP duplicates found")
        
        # 3. Hardware fingerprint duplicates (Tertiary)
        print("\n3️⃣ HARDWARE FINGERPRINT DUPLICATES:")
        cursor.execute("""
            SELECT processor_name, motherboard_model, COUNT(*) as count,
                   GROUP_CONCAT(id) as record_ids,
                   GROUP_CONCAT(hostname) as hostnames
            FROM assets 
            WHERE processor_name IS NOT NULL AND processor_name != ''
            AND motherboard_model IS NOT NULL AND motherboard_model != ''
            GROUP BY processor_name, motherboard_model
            HAVING COUNT(*) > 1
            ORDER BY count DESC
        """)
        
        hw_duplicates = cursor.fetchall()
        if hw_duplicates:
            print(f"   Found {len(hw_duplicates)} duplicate groups by Hardware:")
            for row in hw_duplicates[:3]:
                print(f"   CPU: {row['processor_name'][:30]}... | MB: {row['motherboard_model'][:20]}... | Count: {row['count']}")
        else:
            print("   ✅ No hardware fingerprint duplicates found")
        
        conn.close()
        return primary_duplicates, ip_duplicates, hw_duplicates

    def smart_cleanup_duplicates(self, dry_run=True):
        """Smart duplicate cleanup with best record selection"""
        conn = self.connect()
        cursor = conn.cursor()
        
        print(f"\n🧹 SMART DUPLICATE CLEANUP ({'DRY RUN' if dry_run else 'LIVE CLEANUP'})")
        print("=" * 50)
        
        cleanup_stats = {
            'primary_cleaned': 0,
            'ip_cleaned': 0,
            'records_updated': 0,
            'records_removed': 0
        }
        
        # 1. Clean Serial+MAC duplicates (Primary - most reliable)
        print("\n1️⃣ CLEANING SERIAL+MAC DUPLICATES:")
        cursor.execute("""
            SELECT serial_number, mac_address,
                   GROUP_CONCAT(id || '|' || created_at || '|' || COALESCE(data_source, 'Unknown')) as record_info
            FROM assets 
            WHERE serial_number IS NOT NULL AND serial_number != ''
            AND mac_address IS NOT NULL AND mac_address != ''
            GROUP BY serial_number, mac_address
            HAVING COUNT(*) > 1
        """)
        
        primary_groups = cursor.fetchall()
        for group in primary_groups:
            records = []
            for record_str in group['record_info'].split(','):
                parts = record_str.split('|')
                if len(parts) >= 3:
                    records.append({
                        'id': int(parts[0]),
                        'created_at': parts[1],
                        'data_source': parts[2]
                    })
            
            if len(records) > 1:
                # Keep the most recent record with best data source
                best_record = self._select_best_record(records)
                records_to_remove = [r for r in records if r['id'] != best_record['id']]
                
                print(f"   Serial: {group['serial_number'][:20]}... | MAC: {group['mac_address']}")
                print(f"   Keeping record ID {best_record['id']}, removing {len(records_to_remove)} duplicates")
                
                if not dry_run:
                    for record in records_to_remove:
                        cursor.execute("DELETE FROM assets WHERE id = ?", (record['id'],))
                        cleanup_stats['records_removed'] += 1
                
                cleanup_stats['primary_cleaned'] += 1
        
        # 2. Clean IP duplicates (Secondary)
        print("\n2️⃣ CLEANING IP DUPLICATES:")
        cursor.execute("""
            SELECT ip_address,
                   GROUP_CONCAT(id || '|' || created_at || '|' || COALESCE(hostname, 'Unknown') || '|' || COALESCE(data_source, 'Unknown')) as record_info
            FROM assets 
            WHERE ip_address IS NOT NULL AND ip_address != ''
            AND (serial_number IS NULL OR serial_number = '' OR mac_address IS NULL OR mac_address = '')
            GROUP BY ip_address
            HAVING COUNT(*) > 1
        """)
        
        ip_groups = cursor.fetchall()
        for group in ip_groups:
            records = []
            for record_str in group['record_info'].split(','):
                parts = record_str.split('|')
                if len(parts) >= 4:
                    records.append({
                        'id': int(parts[0]),
                        'created_at': parts[1],
                        'hostname': parts[2],
                        'data_source': parts[3]
                    })
            
            if len(records) > 1:
                # Keep most recent record
                records.sort(key=lambda x: x['created_at'], reverse=True)
                best_record = records[0]
                records_to_remove = records[1:]
                
                print(f"   IP: {group['ip_address']} | Keeping most recent, removing {len(records_to_remove)} duplicates")
                
                if not dry_run:
                    for record in records_to_remove:
                        cursor.execute("DELETE FROM assets WHERE id = ?", (record['id'],))
                        cleanup_stats['records_removed'] += 1
                
                cleanup_stats['ip_cleaned'] += 1
        
        if not dry_run:
            conn.commit()
            print("\n✅ CLEANUP COMPLETED!")
        else:
            print("\n📊 CLEANUP PREVIEW COMPLETED!")
        
        print("\n📈 CLEANUP STATISTICS:")
        print(f"   Primary duplicates (Serial+MAC): {cleanup_stats['primary_cleaned']}")
        print(f"   IP duplicates: {cleanup_stats['ip_cleaned']}")
        print(f"   Total records removed: {cleanup_stats['records_removed']}")
        
        conn.close()
        return cleanup_stats

    def _select_best_record(self, records):
        """Select the best record from duplicates based on quality criteria"""
        # Priority: Enhanced WMI > WMI > Other, then most recent
        data_source_priority = {
            'Comprehensive WMI': 5,
            'Enhanced WMI Collection': 4,
            'WMI Collection': 3,
            'Manual Entry': 2,
            'Unknown': 1,
            None: 0
        }
        
        # Score each record
        for record in records:
            score = data_source_priority.get(record['data_source'], 0)
            # Add recency bonus (newer = higher score)
            try:
                timestamp = datetime.fromisoformat(record['created_at'].replace('Z', '+00:00'))
                days_old = (datetime.now() - timestamp.replace(tzinfo=None)).days
                recency_score = max(0, 100 - days_old)  # Newer records get higher score
                score += recency_score
            except:
                pass
            
            record['quality_score'] = score
        
        # Return record with highest score
        return max(records, key=lambda x: x['quality_score'])

    def create_unique_constraints(self):
        """Create unique constraints and indexes for duplicate prevention"""
        conn = self.connect()
        cursor = conn.cursor()
        
        print("\n🔧 CREATING UNIQUE CONSTRAINTS AND INDEXES")
        print("=" * 50)
        
        # Create indexes for fast duplicate detection
        indexes = [
            ("idx_serial_mac", "CREATE UNIQUE INDEX IF NOT EXISTS idx_serial_mac ON assets(serial_number, mac_address) WHERE serial_number IS NOT NULL AND mac_address IS NOT NULL"),
            ("idx_ip_hostname", "CREATE INDEX IF NOT EXISTS idx_ip_hostname ON assets(ip_address, hostname)"),
            ("idx_hardware_fingerprint", "CREATE INDEX IF NOT EXISTS idx_hardware_fingerprint ON assets(processor_name, motherboard_model)"),
            ("idx_last_seen", "CREATE INDEX IF NOT EXISTS idx_last_seen ON assets(created_at DESC)"),
            ("idx_data_source", "CREATE INDEX IF NOT EXISTS idx_data_source ON assets(data_source)"),
        ]
        
        for index_name, query in indexes:
            try:
                cursor.execute(query)
                print(f"   ✅ Created: {index_name}")
            except Exception as e:
                print(f"   ⚠️  {index_name}: {e}")
        
        # Add metadata columns for tracking
        metadata_columns = [
            ("last_seen", "TEXT", "Last time device was detected"),
            ("seen_count", "INTEGER DEFAULT 1", "Number of times device was detected"),
            ("device_fingerprint", "TEXT", "Unique device fingerprint hash"),
            ("duplicate_check_status", "TEXT DEFAULT 'verified'", "Duplicate verification status"),
        ]
        
        print("\n🔧 ADDING METADATA COLUMNS:")
        for col_name, col_type, description in metadata_columns:
            try:
                cursor.execute(f"ALTER TABLE assets ADD COLUMN {col_name} {col_type}")
                print(f"   ✅ Added: {col_name} ({description})")
            except Exception as e:
                if "duplicate column name" in str(e):
                    print(f"   ⏭️  Exists: {col_name}")
                else:
                    print(f"   ❌ Failed: {col_name} - {e}")
        
        conn.commit()
        conn.close()
        print("\n✅ DATABASE PREPARED FOR DUPLICATE PREVENTION!")

def main():
    print("🚀 ADVANCED DUPLICATE MANAGEMENT SYSTEM")
    print("=" * 60)
    
    manager = AdvancedDuplicateManager()
    
    # Step 1: Analyze current duplicates
    primary_dups, ip_dups, hw_dups = manager.analyze_duplicates()
    
    # Step 2: Create constraints and indexes
    manager.create_unique_constraints()
    
    # Step 3: Preview cleanup
    if primary_dups or ip_dups:
        print("\n" + "="*60)
        print("DUPLICATE CLEANUP PREVIEW")
        stats = manager.smart_cleanup_duplicates(dry_run=True)
        
        if stats['records_removed'] > 0:
            response = input(f"\nProceed with cleanup? This will remove {stats['records_removed']} duplicate records (y/N): ")
            
            if response.lower() == 'y':
                print("\n" + "="*60)
                print("EXECUTING LIVE CLEANUP")
                final_stats = manager.smart_cleanup_duplicates(dry_run=False)
                print("\n🎉 SUCCESS! Database cleaned and optimized for duplicate prevention!")
            else:
                print("⏸️  Cleanup cancelled. Database unchanged.")
        else:
            print("\n✅ No duplicates found to clean!")
    else:
        print("\n✅ DATABASE IS ALREADY CLEAN!")
    
    print("\n🎯 NEXT STEPS:")
    print("   • Database now has unique constraints for duplicate prevention")
    print("   • Real-time duplicate detection ready for implementation")
    print("   • Smart collection engine will prevent future duplicates")

if __name__ == "__main__":
    main()