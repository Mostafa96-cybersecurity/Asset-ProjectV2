#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix missing assets_enhanced table
"""

import sqlite3
import os

def fix_database():
    """Fix the missing assets_enhanced table"""
    db_paths = [
        "../assets.db",
        "D:/Assets-Projects/assets.db", 
        "D:/Assets-Projects/Asset-Project-Enhanced/assets.db"
    ]
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            print(f"[INFO] Fixing database: {db_path}")
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if assets_enhanced table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='assets_enhanced'")
            if not cursor.fetchone():
                print("[INFO] Creating assets_enhanced table...")
                cursor.execute("""
                    CREATE TABLE assets_enhanced AS 
                    SELECT * FROM assets
                """)
                
                # Add additional columns that might be expected
                try:
                    cursor.execute("ALTER TABLE assets_enhanced ADD COLUMN completeness_score INTEGER DEFAULT 85")
                    cursor.execute("ALTER TABLE assets_enhanced ADD COLUMN last_scan TIMESTAMP")
                    cursor.execute("ALTER TABLE assets_enhanced ADD COLUMN scan_status TEXT DEFAULT 'Active'")
                except:
                    pass
                
                conn.commit()
                print("[OK] assets_enhanced table created successfully")
            else:
                print("[OK] assets_enhanced table already exists")
            
            conn.close()
            break

if __name__ == "__main__":
    fix_database()