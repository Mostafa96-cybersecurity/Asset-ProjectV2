#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Cleanup and Enhancement Script
======================================
Clean up test data and enhance database structure
"""

import sqlite3
from datetime import datetime

def cleanup_and_enhance_database():
    """Clean up test data and enhance database structure"""
    
    print("🗄️ Database Cleanup and Enhancement")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('assets.db')
        cursor = conn.cursor()
        
        # 1. Remove test/demo data
        print("🧹 Cleaning up test/demo data...")
        cursor.execute("""
            DELETE FROM assets WHERE 
            hostname LIKE '%TEST%' OR 
            hostname LIKE '%DEMO%' OR 
            hostname LIKE '%SAMPLE%' OR
            hostname = 'DESKTOP-TEST-001' OR
            hostname = 'WEB-SERVER-001' OR
            hostname = 'TEST-DEVICE-001' OR
            hostname = 'asdasdasdas'
        """)
        deleted_count = cursor.rowcount
        print(f"✅ Removed {deleted_count} test records")
        
        # 2. Check remaining data
        cursor.execute("SELECT COUNT(*) FROM assets")
        total_assets = cursor.fetchone()[0]
        print(f"📊 Remaining assets: {total_assets}")
        
        # 3. Show current assets
        if total_assets > 0:
            print("\n📋 Current Assets:")
            cursor.execute("SELECT hostname, ip_address, classification, department FROM assets ORDER BY hostname")
            for asset in cursor.fetchall():
                hostname = asset[0] or 'N/A'
                ip = asset[1] or 'N/A'
                classification = asset[2] or 'N/A'
                dept = asset[3] or 'Unknown'
                print(f"  • {hostname} | {ip} | {classification} | {dept}")
        
        # 4. Add missing database columns for comprehensive data
        print("\n🔧 Enhancing database structure...")
        try:
            # Check existing columns
            cursor.execute("PRAGMA table_info(assets)")
            existing_columns = [col[1] for col in cursor.fetchall()]
            
            # Add missing columns for comprehensive data collection
            new_columns = [
                ("os_name", "TEXT"),
                ("os_version", "TEXT"), 
                ("manufacturer", "TEXT"),
                ("model", "TEXT"),
                ("serial_number", "TEXT"),
                ("mac_address", "TEXT"),
                ("cpu_info", "TEXT"),
                ("memory_gb", "REAL"),
                ("storage_info", "TEXT"),
                ("vendor", "TEXT"),
                ("ping_status", "TEXT DEFAULT 'Unknown'"),
                ("last_ping", "TEXT"),
                ("collection_method", "TEXT DEFAULT 'Unknown'")
            ]
            
            added_columns = 0
            for col_name, col_type in new_columns:
                if col_name not in existing_columns:
                    cursor.execute(f"ALTER TABLE assets ADD COLUMN {col_name} {col_type}")
                    added_columns += 1
                    print(f"  ✅ Added column: {col_name}")
            
            if added_columns == 0:
                print("  ✅ Database structure is up to date")
            else:
                print(f"  ✅ Added {added_columns} new columns")
                
        except Exception as e:
            print(f"  ⚠️ Column enhancement warning: {e}")
        
        # 5. Create departments list for web interface
        print("\n🏢 Setting up departments...")
        departments = [
            'IT', 'Finance', 'HR', 'Operations', 'Marketing', 
            'Sales', 'Engineering', 'Support', 'Management', 'Unknown'
        ]
        
        # Update any NULL departments to 'Unknown'
        cursor.execute("UPDATE assets SET department = 'Unknown' WHERE department IS NULL OR department = ''")
        updated_depts = cursor.rowcount
        if updated_depts > 0:
            print(f"  ✅ Updated {updated_depts} records with missing departments")
        
        conn.commit()
        conn.close()
        
        print("\n✅ Database cleanup and enhancement completed successfully!")
        print(f"📊 Final asset count: {total_assets}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database enhancement failed: {e}")
        return False

if __name__ == "__main__":
    cleanup_and_enhance_database()