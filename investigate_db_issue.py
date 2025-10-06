#!/usr/bin/env python3
"""
Investigate Database Write Issue - Check why scan data isn't persisting
"""

import sqlite3
import os
from datetime import datetime

def investigate_database_issue():
    print("🔍 INVESTIGATING DATABASE WRITE ISSUE")
    print("=" * 50)
    
    print("📊 SCAN vs DATABASE MISMATCH:")
    print("   • Scan Completed: 452/452 devices ✅")
    print("   • Database Shows: 222 devices ❌")
    print("   • Missing: 230 devices")
    
    print(f"\n🗂️ DATABASE FILE ANALYSIS:")
    
    # Check database file
    db_file = "assets.db"
    if os.path.exists(db_file):
        stat = os.stat(db_file)
        size_mb = stat.st_size / (1024 * 1024)
        modified = datetime.fromtimestamp(stat.st_mtime)
        
        print(f"   📁 File: {db_file}")
        print(f"   📏 Size: {size_mb:.2f} MB")
        print(f"   🕐 Last Modified: {modified}")
        print(f"   ⏰ Modified Recently: {'YES' if (datetime.now() - modified).seconds < 3600 else 'NO'}")
    else:
        print("   ❌ Database file not found!")
        return
    
    # Check for backup databases
    print(f"\n🔍 CHECKING FOR MULTIPLE DATABASES:")
    backup_files = [f for f in os.listdir('.') if f.endswith('.db') and 'asset' in f.lower()]
    
    for db in backup_files:
        try:
            conn = sqlite3.connect(db)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM assets")
            count = cursor.fetchone()[0]
            conn.close()
            
            stat = os.stat(db)
            modified = datetime.fromtimestamp(stat.st_mtime)
            recently_modified = (datetime.now() - modified).seconds < 3600
            
            print(f"   📁 {db}: {count} devices {'🆕' if recently_modified else '🗓️'}")
            
        except Exception as e:
            print(f"   ❌ {db}: Error - {e}")
    
    # Check for recent database activity
    print(f"\n🔍 CHECKING DATABASE ACTIVITY:")
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Check for any recent timestamp updates
        cursor.execute("""
            SELECT COUNT(*) FROM assets 
            WHERE last_updated > datetime('now', '-2 hours')
        """)
        recent_updates = cursor.fetchone()[0]
        print(f"   🕐 Updates in last 2 hours: {recent_updates}")
        
        # Check for today's updates
        cursor.execute("""
            SELECT COUNT(*) FROM assets 
            WHERE date(last_updated) = date('now')
        """)
        today_updates = cursor.fetchone()[0]
        print(f"   📅 Updates today: {today_updates}")
        
        # Check if there are any NULL last_updated fields
        cursor.execute("SELECT COUNT(*) FROM assets WHERE last_updated IS NULL")
        null_updates = cursor.fetchone()[0]
        print(f"   ❓ No update timestamp: {null_updates}")
        
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Error checking activity: {e}")
    
    print(f"\n💡 POSSIBLE CAUSES:")
    print("1. 🔄 **Transaction Not Committed**: Scan data in memory, not saved")
    print("2. 📁 **Wrong Database File**: Writing to different database")
    print("3. 🔒 **Database Lock**: File locked during write")
    print("4. 💥 **Collection Error**: Data collected but not inserted")
    print("5. 🕐 **Timing Issue**: Scan still writing data")
    
    print(f"\n🔧 SOLUTIONS TO TRY:")
    print("1. Wait 1-2 minutes for database commit")
    print("2. Check application logs for errors")
    print("3. Restart application and check again")
    print("4. Force database refresh/commit")
    
    # Try to force a database refresh
    print(f"\n🔄 ATTEMPTING DATABASE REFRESH:")
    try:
        conn = sqlite3.connect(db_file)
        conn.execute("PRAGMA synchronous = FULL")
        conn.execute("PRAGMA journal_mode = WAL")
        conn.commit()
        conn.close()
        print("   ✅ Database refresh attempted")
    except Exception as e:
        print(f"   ❌ Refresh failed: {e}")

if __name__ == "__main__":
    investigate_database_issue()