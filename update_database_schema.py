#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Schema Update for NMAP OS Detection
==========================================
Add new columns for NMAP/OS detection results
"""

import sqlite3
import sys
from pathlib import Path

def update_database_schema():
    """Add NMAP OS detection columns to assets table"""
    
    print("🔧 UPDATING DATABASE SCHEMA FOR NMAP OS DETECTION")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect('assets.db')
        cursor = conn.cursor()
        
        # Check current schema
        cursor.execute('PRAGMA table_info(assets)')
        existing_columns = [col[1] for col in cursor.fetchall()]
        
        print(f"📊 Current database has {len(existing_columns)} columns")
        
        # Add new columns for NMAP OS detection
        new_columns = [
            ('nmap_os_family', 'TEXT'),
            ('nmap_device_type', 'TEXT'), 
            ('nmap_confidence', 'TEXT'),
            ('detection_method', 'TEXT')
        ]
        
        added_columns = []
        for column_name, column_type in new_columns:
            if column_name not in existing_columns:
                try:
                    alter_sql = f'ALTER TABLE assets ADD COLUMN {column_name} {column_type}'
                    cursor.execute(alter_sql)
                    added_columns.append(column_name)
                    print(f"✅ Added column: {column_name} ({column_type})")
                except Exception as e:
                    print(f"❌ Failed to add {column_name}: {e}")
            else:
                print(f"ℹ️ Column already exists: {column_name}")
        
        if added_columns:
            conn.commit()
            print(f"\n✅ Successfully added {len(added_columns)} new columns")
            print(f"   New columns: {', '.join(added_columns)}")
        else:
            print(f"\nℹ️ No new columns needed - schema already up to date")
        
        # Verify the update
        cursor.execute('PRAGMA table_info(assets)')
        final_columns = [col[1] for col in cursor.fetchall()]
        
        print(f"\n📊 Updated database now has {len(final_columns)} columns")
        
        # Show NMAP-related columns
        nmap_columns = [col for col in final_columns if 'nmap' in col.lower() or 'detection' in col.lower()]
        if nmap_columns:
            print(f"🎯 NMAP/Detection columns: {', '.join(nmap_columns)}")
        
        conn.close()
        
        print(f"\n✅ Database schema update completed successfully!")
        
    except Exception as e:
        print(f"❌ Database schema update failed: {e}")
        return False
    
    return True

def test_updated_schema():
    """Test the updated schema with a sample insert"""
    
    print(f"\n🧪 TESTING UPDATED SCHEMA")
    print("-" * 40)
    
    try:
        conn = sqlite3.connect('assets.db')
        cursor = conn.cursor()
        
        # Test insert with new NMAP columns
        test_data = {
            'ip_address': '192.168.1.999',  # Test IP
            'hostname': 'test-device',
            'nmap_os_family': 'Windows',
            'nmap_device_type': 'Windows Computer',
            'nmap_confidence': '85',
            'detection_method': 'Port-based OS Detection'
        }
        
        # Insert test record
        insert_sql = '''INSERT OR REPLACE INTO assets 
                       (ip_address, hostname, nmap_os_family, nmap_device_type, 
                        nmap_confidence, detection_method, last_updated)
                       VALUES (?, ?, ?, ?, ?, ?, datetime('now'))'''
        
        cursor.execute(insert_sql, (
            test_data['ip_address'],
            test_data['hostname'], 
            test_data['nmap_os_family'],
            test_data['nmap_device_type'],
            test_data['nmap_confidence'],
            test_data['detection_method']
        ))
        
        conn.commit()
        
        # Verify the insert
        cursor.execute('''SELECT ip_address, hostname, nmap_os_family, nmap_device_type, 
                         nmap_confidence, detection_method FROM assets 
                         WHERE ip_address = ?''', (test_data['ip_address'],))
        
        result = cursor.fetchone()
        
        if result:
            print(f"✅ Test insert successful:")
            print(f"   IP: {result[0]}")
            print(f"   Hostname: {result[1]}")
            print(f"   OS Family: {result[2]}")
            print(f"   Device Type: {result[3]}")
            print(f"   Confidence: {result[4]}%")
            print(f"   Detection Method: {result[5]}")
            
            # Clean up test record
            cursor.execute('DELETE FROM assets WHERE ip_address = ?', (test_data['ip_address'],))
            conn.commit()
            print(f"🧹 Test record cleaned up")
        else:
            print(f"❌ Test insert failed - no record found")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Schema test failed: {e}")

def main():
    """Main update function"""
    
    print("🚀 DATABASE SCHEMA UPDATE FOR ENHANCED OS DETECTION")
    print("=" * 70)
    print("📋 Adding support for NMAP OS detection results")
    print("=" * 70)
    
    # Update schema
    if update_database_schema():
        # Test the update
        test_updated_schema()
        
        print(f"\n" + "=" * 70)
        print("📋 SCHEMA UPDATE SUMMARY")
        print("=" * 70)
        print("✅ Database schema updated for NMAP OS detection")
        print("✅ New columns: nmap_os_family, nmap_device_type, nmap_confidence, detection_method")
        print("✅ Schema tested successfully")
        print("🎯 Ready for enhanced OS-aware data collection")
    else:
        print(f"\n❌ Schema update failed")
        sys.exit(1)

if __name__ == "__main__":
    main()