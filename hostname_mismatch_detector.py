#!/usr/bin/env python3
"""
HOSTNAME MISMATCH DETECTOR

This tool implements the missing hostname mismatch feature by:
✅ Adding hostname_mismatch column to database
✅ Comparing hostname vs computer_name fields  
✅ Flagging mismatches automatically
✅ Providing detailed mismatch analysis
"""

import sqlite3
from datetime import datetime
import re

class HostnameMismatchDetector:
    def __init__(self, db_path="assets.db"):
        self.db_path = db_path
        self.stats = {
            'total_devices': 0,
            'devices_with_both_names': 0,
            'exact_matches': 0,
            'mismatches_found': 0,
            'domain_mismatches': 0,
            'case_mismatches': 0,
            'prefix_mismatches': 0
        }

    def implement_hostname_mismatch_detection(self):
        """Implement complete hostname mismatch detection system"""
        
        print("🏷️ HOSTNAME MISMATCH DETECTOR")
        print("=" * 70)
        print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("🎯 Goal: Implement automatic hostname mismatch detection")
        print()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Step 1: Add hostname mismatch column if it doesn't exist
        self.add_hostname_mismatch_column(cursor)
        
        # Step 2: Analyze and detect hostname mismatches
        self.detect_hostname_mismatches(cursor)
        
        # Step 3: Update database with mismatch flags
        self.update_hostname_mismatch_flags(cursor)
        
        # Step 4: Generate detailed mismatch report
        self.generate_mismatch_report(cursor)
        
        conn.commit()
        conn.close()
        
        self.show_detection_results()

    def add_hostname_mismatch_column(self, cursor):
        """Add hostname mismatch columns to database if they don't exist"""
        
        print("📊 ADDING HOSTNAME MISMATCH COLUMNS:")
        
        # Check existing columns
        cursor.execute("PRAGMA table_info(assets)")
        existing_columns = [col[1] for col in cursor.fetchall()]
        
        # Add hostname mismatch columns
        new_columns = {
            'hostname_mismatch': 'TEXT',
            'hostname_mismatch_type': 'TEXT', 
            'hostname_mismatch_details': 'TEXT',
            'hostname_comparison_date': 'TEXT'
        }
        
        for column_name, column_type in new_columns.items():
            if column_name not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE assets ADD COLUMN {column_name} {column_type}")
                    print(f"   ✅ Added column: {column_name}")
                except Exception as e:
                    print(f"   ⚠️ Column {column_name} already exists or error: {str(e)[:50]}")
            else:
                print(f"   ℹ️ Column {column_name} already exists")

    def detect_hostname_mismatches(self, cursor):
        """Detect hostname mismatches using comprehensive comparison logic"""
        
        print(f"\n🔍 DETECTING HOSTNAME MISMATCHES:")
        
        # Get all devices with both hostname and computer_name
        cursor.execute("""
            SELECT id, hostname, computer_name 
            FROM assets 
            WHERE hostname IS NOT NULL 
            AND computer_name IS NOT NULL
            AND hostname != ''
            AND computer_name != ''
        """)
        
        devices = cursor.fetchall()
        self.stats['total_devices'] = len(devices)
        self.stats['devices_with_both_names'] = len(devices)
        
        print(f"   📱 Found {len(devices)} devices with both hostname and computer_name")
        
        mismatch_results = []
        
        for device_id, hostname, computer_name in devices:
            mismatch_info = self.analyze_hostname_mismatch(hostname, computer_name)
            mismatch_results.append((device_id, mismatch_info))
            
            # Update statistics
            if mismatch_info['is_mismatch']:
                self.stats['mismatches_found'] += 1
                if mismatch_info['mismatch_type'] == 'domain':
                    self.stats['domain_mismatches'] += 1
                elif mismatch_info['mismatch_type'] == 'case':
                    self.stats['case_mismatches'] += 1
                elif mismatch_info['mismatch_type'] == 'prefix':
                    self.stats['prefix_mismatches'] += 1
            else:
                self.stats['exact_matches'] += 1
        
        return mismatch_results

    def analyze_hostname_mismatch(self, hostname, computer_name):
        """Analyze specific hostname mismatch types"""
        
        mismatch_info = {
            'is_mismatch': False,
            'mismatch_type': 'none',
            'details': '',
            'severity': 'low'
        }
        
        # Clean and normalize names for comparison
        hostname_clean = hostname.strip().lower()
        computer_name_clean = computer_name.strip().lower()
        
        # Remove domain suffixes for base comparison
        hostname_base = re.sub(r'\..*$', '', hostname_clean)
        computer_name_base = re.sub(r'\..*$', '', computer_name_clean)
        
        # Exact match check
        if hostname_clean == computer_name_clean:
            mismatch_info['details'] = 'Exact match'
            return mismatch_info
        
        # Base name match (ignoring domain)
        if hostname_base == computer_name_base:
            mismatch_info['details'] = 'Base names match, domain difference only'
            return mismatch_info
        
        # Case-only difference
        if hostname.lower() == computer_name.lower() and hostname != computer_name:
            mismatch_info = {
                'is_mismatch': True,
                'mismatch_type': 'case',
                'details': f'Case difference: "{hostname}" vs "{computer_name}"',
                'severity': 'low'
            }
            return mismatch_info
        
        # Domain mismatch (same base, different domain)
        if hostname_base == computer_name_base and '.' in (hostname + computer_name):
            mismatch_info = {
                'is_mismatch': True,
                'mismatch_type': 'domain',
                'details': f'Domain difference: "{hostname}" vs "{computer_name}"',
                'severity': 'medium'
            }
            return mismatch_info
        
        # Prefix/suffix similarity
        if (hostname_base in computer_name_base or computer_name_base in hostname_base):
            mismatch_info = {
                'is_mismatch': True,
                'mismatch_type': 'prefix',
                'details': f'Partial match: "{hostname}" vs "{computer_name}"',
                'severity': 'medium'
            }
            return mismatch_info
        
        # Complete mismatch
        mismatch_info = {
            'is_mismatch': True,
            'mismatch_type': 'complete',
            'details': f'Complete mismatch: "{hostname}" vs "{computer_name}"',
            'severity': 'high'
        }
        
        return mismatch_info

    def update_hostname_mismatch_flags(self, cursor):
        """Update database with hostname mismatch flags"""
        
        print(f"\n💾 UPDATING HOSTNAME MISMATCH FLAGS:")
        
        # Get mismatch results
        mismatch_results = self.detect_hostname_mismatches(cursor)
        
        updated_count = 0
        
        for device_id, mismatch_info in mismatch_results:
            try:
                cursor.execute("""
                    UPDATE assets 
                    SET hostname_mismatch = ?,
                        hostname_mismatch_type = ?,
                        hostname_mismatch_details = ?,
                        hostname_comparison_date = ?
                    WHERE id = ?
                """, (
                    'Yes' if mismatch_info['is_mismatch'] else 'No',
                    mismatch_info['mismatch_type'],
                    mismatch_info['details'],
                    datetime.now().isoformat(),
                    device_id
                ))
                updated_count += 1
            except Exception as e:
                print(f"   ⚠️ Error updating device {device_id}: {str(e)[:50]}")
        
        print(f"   ✅ Updated {updated_count} devices with mismatch flags")

    def generate_mismatch_report(self, cursor):
        """Generate detailed hostname mismatch report"""
        
        print(f"\n📋 GENERATING MISMATCH REPORT:")
        
        # Get mismatch summary
        cursor.execute("""
            SELECT 
                hostname_mismatch,
                hostname_mismatch_type,
                COUNT(*) as count
            FROM assets 
            WHERE hostname_mismatch IS NOT NULL
            GROUP BY hostname_mismatch, hostname_mismatch_type
            ORDER BY count DESC
        """)
        
        summary_results = cursor.fetchall()
        
        print(f"   📊 Mismatch Summary:")
        for mismatch_status, mismatch_type, count in summary_results:
            print(f"      • {mismatch_status} ({mismatch_type}): {count} devices")
        
        # Get top mismatches for review
        cursor.execute("""
            SELECT hostname, computer_name, hostname_mismatch_details
            FROM assets 
            WHERE hostname_mismatch = 'Yes'
            ORDER BY hostname_mismatch_type, hostname
            LIMIT 10
        """)
        
        top_mismatches = cursor.fetchall()
        
        if top_mismatches:
            print(f"\n   🔍 Top Mismatches (first 10):")
            for hostname, computer_name, details in top_mismatches:
                print(f"      • {hostname} ↔ {computer_name}")
                print(f"        Details: {details}")

    def show_detection_results(self):
        """Show hostname mismatch detection results"""
        
        print(f"\n📊 HOSTNAME MISMATCH DETECTION RESULTS")
        print("=" * 70)
        print(f"📱 Total devices analyzed: {self.stats['devices_with_both_names']}")
        print(f"✅ Exact matches: {self.stats['exact_matches']}")
        print(f"⚠️ Mismatches found: {self.stats['mismatches_found']}")
        
        if self.stats['devices_with_both_names'] > 0:
            mismatch_rate = (self.stats['mismatches_found'] / self.stats['devices_with_both_names'] * 100)
            print(f"📈 MISMATCH RATE: {mismatch_rate:.1f}%")
        
        print(f"\n🔍 MISMATCH BREAKDOWN:")
        print(f"   • Domain mismatches: {self.stats['domain_mismatches']}")
        print(f"   • Case mismatches: {self.stats['case_mismatches']}")  
        print(f"   • Prefix mismatches: {self.stats['prefix_mismatches']}")
        print(f"   • Complete mismatches: {self.stats['mismatches_found'] - self.stats['domain_mismatches'] - self.stats['case_mismatches'] - self.stats['prefix_mismatches']}")
        
        print(f"\n✅ HOSTNAME MISMATCH DETECTION FEATURE IMPLEMENTED!")
        print("   • hostname_mismatch column added")
        print("   • hostname_mismatch_type column added")  
        print("   • hostname_mismatch_details column added")
        print("   • Automatic detection logic implemented")
        print("   • All devices analyzed and flagged")

def main():
    """Run hostname mismatch detection"""
    
    detector = HostnameMismatchDetector()
    detector.implement_hostname_mismatch_detection()

if __name__ == "__main__":
    main()