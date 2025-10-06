#!/usr/bin/env python3
"""
Simple Database Check - View collected data in assets.db
"""

import sqlite3

def check_database():
    """Check database contents"""
    try:
        conn = sqlite3.connect('assets.db')
        cursor = conn.cursor()
        
        # Count total devices
        cursor.execute('SELECT COUNT(*) FROM assets')
        total_count = cursor.fetchone()[0]
        print(f"📊 Total devices in database: {total_count}")
        
        if total_count == 0:
            print("❌ No data found in database!")
            print("💡 You need to run a collection first to populate the database")
            return
        
        # Show recent devices
        cursor.execute('''
            SELECT hostname, ip_address, device_type, operating_system, created_at, updated_at
            FROM assets 
            ORDER BY 
                CASE 
                    WHEN updated_at IS NOT NULL THEN updated_at 
                    ELSE created_at 
                END DESC 
            LIMIT 10
        ''')
        recent_devices = cursor.fetchall()
        
        print("\n🔍 Most Recently Added/Updated Devices:")
        print("=" * 80)
        for i, device in enumerate(recent_devices, 1):
            hostname = device[0] or "Unknown"
            ip = device[1] or "Unknown"
            device_type = device[2] or "Unknown"
            os = device[3] or "Unknown"
            created = device[4] or "Unknown"
            updated = device[5] or created
            
            print(f"{i:2d}. {hostname} ({ip})")
            print(f"    Type: {device_type} | OS: {os}")
            print(f"    Last Update: {updated}")
            print("-" * 40)
        
        # Show collection methods
        cursor.execute('''
            SELECT collection_method, COUNT(*) as count
            FROM assets 
            WHERE collection_method IS NOT NULL
            GROUP BY collection_method
            ORDER BY count DESC
        ''')
        methods = cursor.fetchall()
        
        if methods:
            print("\n📈 Collection Methods Used:")
            print("=" * 40)
            for method, count in methods:
                print(f"  {method}: {count} devices")
        
        # Show device types
        cursor.execute('''
            SELECT device_type, COUNT(*) as count
            FROM assets 
            WHERE device_type IS NOT NULL
            GROUP BY device_type
            ORDER BY count DESC
        ''')
        device_types = cursor.fetchall()
        
        if device_types:
            print("\n🏷️ Device Types Found:")
            print("=" * 40)
            for dtype, count in device_types:
                print(f"  {dtype}: {count} devices")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")

if __name__ == "__main__":
    check_database()