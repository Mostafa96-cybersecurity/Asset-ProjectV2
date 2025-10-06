#!/usr/bin/env python3
"""
Find Scan Data Tool
Helps locate where the missing 230 devices from the recent scan might be stored
"""

import sqlite3
import os
import json
import glob
from datetime import datetime

def check_database_connections():
    """Check for active database connections"""
    print("🔍 CHECKING FOR ACTIVE DATABASE CONNECTIONS")
    print("=" * 50)
    
    # Check if database is locked
    try:
        conn = sqlite3.connect('assets.db', timeout=1)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM assets")
        count = cursor.fetchone()[0]
        print(f"   ✅ Database accessible: {count} assets")
        
        # Check for recent activity
        cursor.execute("""
            SELECT hostname, ip_address, last_seen 
            FROM assets 
            WHERE last_seen > datetime('now', '-1 day')
            ORDER BY last_seen DESC 
            LIMIT 10
        """)
        recent = cursor.fetchall()
        print(f"   📅 Recent activity (last 24h): {len(recent)} devices")
        for device in recent:
            print(f"      • {device[0]} ({device[1]}) - {device[2]}")
        
        conn.close()
        
    except sqlite3.OperationalError as e:
        print(f"   ❌ Database locked or busy: {e}")
        return False
    
    return True

def search_for_temp_databases():
    """Search for temporary or alternative database files"""
    print("\n🔍 SEARCHING FOR TEMPORARY DATABASES")
    print("=" * 50)
    
    patterns = [
        "*.db",
        "*.sqlite",
        "*.sqlite3",
        "*temp*.db",
        "*cache*.db",
        "*backup*.db"
    ]
    
    all_files = set()
    for pattern in patterns:
        files = glob.glob(pattern)
        all_files.update(files)
    
    for file in sorted(all_files):
        try:
            stat = os.stat(file)
            size_mb = stat.st_size / (1024 * 1024)
            mod_time = datetime.fromtimestamp(stat.st_mtime)
            
            print(f"   📁 {file}: {size_mb:.2f}MB, modified: {mod_time}")
            
            # Check if it's a SQLite database
            try:
                conn = sqlite3.connect(file)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='assets'")
                if cursor.fetchone():
                    cursor.execute("SELECT COUNT(*) FROM assets")
                    count = cursor.fetchone()[0]
                    print(f"      📊 Contains {count} assets")
                conn.close()
            except:
                print("      ❓ Not a valid SQLite database or no assets table")
                
        except Exception as e:
            print(f"   ❌ Error checking {file}: {e}")

def check_memory_cache():
    """Check for data that might be cached in memory"""
    print("\n🔍 CHECKING FOR MEMORY CACHED DATA")
    print("=" * 50)
    
    # Look for JSON files that might contain scan results
    json_files = glob.glob("*.json") + glob.glob("**/*.json", recursive=True)
    
    recent_files = []
    for file in json_files:
        try:
            stat = os.stat(file)
            mod_time = datetime.fromtimestamp(stat.st_mtime)
            if mod_time > datetime(2025, 10, 2):  # Files modified after Oct 2
                recent_files.append((file, mod_time, stat.st_size))
        except:
            continue
    
    recent_files.sort(key=lambda x: x[1], reverse=True)
    
    for file, mod_time, size in recent_files[:10]:
        print(f"   📄 {file}: {size} bytes, {mod_time}")
        
        # Check if it contains device data
        try:
            with open(file, 'r') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    if 'devices' in data or 'assets' in data:
                        print("      🎯 Contains device/asset data!")
                elif isinstance(data, list) and len(data) > 100:
                    print(f"      📊 Large list with {len(data)} items")
        except:
            pass

def check_application_logs():
    """Check application logs for scan completion info"""
    print("\n🔍 CHECKING APPLICATION LOGS")
    print("=" * 50)
    
    log_patterns = ["*.log", "logs/*.log", "**/*.log"]
    
    for pattern in log_patterns:
        for log_file in glob.glob(pattern, recursive=True):
            try:
                stat = os.stat(log_file)
                mod_time = datetime.fromtimestamp(stat.st_mtime)
                
                if mod_time > datetime(2025, 10, 2):
                    print(f"   📄 {log_file}: modified {mod_time}")
                    
                    # Check for scan completion messages
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if '452' in content or 'Collected:' in content:
                            print("      🎯 Contains scan completion data!")
                            lines = content.split('\n')
                            for line in lines[-20:]:
                                if '452' in line or 'Collected:' in line:
                                    print(f"         {line.strip()}")
            except:
                continue

if __name__ == "__main__":
    print("🔍 SCAN DATA LOCATION FINDER")
    print("=" * 50)
    print("🎯 Looking for 452 devices from recent scan...")
    print("📊 Database currently shows: 222 devices")
    print("❓ Missing: 230 devices")
    print()
    
    db_ok = check_database_connections()
    search_for_temp_databases()
    check_memory_cache()
    check_application_logs()
    
    print("\n💡 RECOMMENDATIONS:")
    print("=" * 50)
    if not db_ok:
        print("   1. ⚠️ Database is locked - kill running processes")
    print("   2. 🔄 Restart the asset management application")
    print("   3. 🔍 Check if scan wrote to a different database")
    print("   4. 📝 Review application logs for errors")
    print("   5. ⚡ Run a new scan with debug logging enabled")