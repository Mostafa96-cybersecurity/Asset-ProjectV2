#!/usr/bin/env python3
"""
Force Database Commit - Try to save scan data that's in memory
"""

import sqlite3
import os
from datetime import datetime

def force_database_commit():
    print("🔄 FORCING DATABASE COMMIT")
    print("=" * 40)
    
    print("🎯 Problem: Scan collected 452 devices but database shows 222")
    print("💡 Solution: Force commit any pending transactions")
    
    try:
        # Connect to database with explicit settings
        conn = sqlite3.connect('assets.db', timeout=30)
        
        print("\n🔍 Current database state:")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM assets")
        current_count = cursor.fetchone()[0]
        print(f"   📊 Current assets: {current_count}")
        
        # Force commit any pending transactions
        print("\n🔄 Forcing commit...")
        conn.commit()
        
        # Check if anything changed
        cursor.execute("SELECT COUNT(*) FROM assets")
        after_commit = cursor.fetchone()[0]
        print(f"   📊 After commit: {after_commit}")
        
        if after_commit != current_count:
            print(f"   ✅ Success! {after_commit - current_count} devices committed")
        else:
            print("   ⚠️ No change - data might be lost or in different location")
        
        # Try to vacuum the database to ensure integrity
        print("\n🧹 Optimizing database...")
        conn.execute("VACUUM")
        conn.commit()
        
        # Check for any recent activity that might not be showing
        cursor.execute("""
            SELECT hostname, ip_address, last_updated 
            FROM assets 
            ORDER BY id DESC 
            LIMIT 5
        """)
        recent = cursor.fetchall()
        
        print("\n🔍 Most recent entries:")
        for hostname, ip, updated in recent:
            print(f"   • {hostname or ip}: {updated}")
        
        conn.close()
        
        print("\n💡 NEXT STEPS:")
        print("1. If count didn't change, data might be in memory only")
        print("2. Try restarting the application")
        print("3. Check if scan is writing to a different database")
        print("4. Look for temporary or cache files")
        
        return after_commit
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return None

def check_for_temp_databases():
    print("\n🔍 CHECKING FOR TEMPORARY DATABASES:")
    
    # Look for any database-like files
    db_files = []
    for file in os.listdir('.'):
        if (file.endswith('.db') or file.endswith('.sqlite') or 
            file.endswith('.sqlite3') or 'asset' in file.lower()):
            db_files.append(file)
    
    print(f"Found {len(db_files)} database-like files:")
    
    for db_file in db_files:
        try:
            if os.path.isfile(db_file):
                size = os.path.getsize(db_file) / 1024 / 1024
                modified = datetime.fromtimestamp(os.path.getmtime(db_file))
                
                # Try to check if it has assets table
                try:
                    conn = sqlite3.connect(db_file)
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM assets")
                    count = cursor.fetchone()[0]
                    conn.close()
                    
                    recently_modified = (datetime.now() - modified).seconds < 7200  # 2 hours
                    status = "🆕" if recently_modified else "🗓️"
                    
                    print(f"   {status} {db_file}: {count} assets, {size:.2f}MB, modified: {modified}")
                    
                except:
                    print(f"   ❓ {db_file}: {size:.2f}MB (no assets table)")
        except Exception as e:
            print(f"   ❌ {db_file}: Error - {e}")

if __name__ == "__main__":
    result = force_database_commit()
    check_for_temp_databases()
    
    print("\n📋 SUMMARY:")
    if result and result > 222:
        print(f"   ✅ Database now has {result} devices!")
    else:
        print("   ⚠️ Issue persists - may need to restart application or check collection process")