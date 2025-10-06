#!/usr/bin/env python3
# Test database and API endpoint directly
import sqlite3
import os

def test_database():
    """Test database access directly"""
    db_paths = [
        "../assets.db",
        "D:/Assets-Projects/Asset-Project-Enhanced/assets.db",
        "assets.db"
    ]
    
    for db_path in db_paths:
        print(f"Testing: {db_path}")
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Test assets query
                cursor.execute("SELECT COUNT(*) FROM assets")
                count = cursor.fetchone()[0]
                print(f"  Assets count: {count}")
                
                if count > 0:
                    cursor.execute("SELECT * FROM assets LIMIT 3")
                    assets = cursor.fetchall()
                    print("  Sample assets:")
                    for asset in assets:
                        print(f"    {asset['hostname']} - {asset['ip_address']} - {asset['device_type']}")
                
                conn.close()
                return db_path, count
            except Exception as e:
                print(f"  Error: {e}")
    
    return None, 0

if __name__ == "__main__":
    print("=== DATABASE TEST ===")
    db_path, count = test_database()
    
    if count > 0:
        print(f"\n[SUCCESS] Found {count} assets in {db_path}")
    else:
        print("\n[ERROR] No assets found or database error")