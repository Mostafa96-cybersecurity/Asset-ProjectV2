import sqlite3

# Check the backup file with data
conn = sqlite3.connect('assets.db.backup_20251005_174844')
cursor = conn.cursor()

# Check tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables:", tables)

# Check assets_enhanced table
try:
    cursor.execute("PRAGMA table_info(assets_enhanced)")
    columns = cursor.fetchall()
    print(f"Columns in assets_enhanced: {len(columns)}")
    
    cursor.execute("SELECT COUNT(*) FROM assets_enhanced")
    count = cursor.fetchone()[0]
    print(f"Assets in backup: {count}")
    
    if count > 0:
        cursor.execute("SELECT hostname, device_type, ip_address FROM assets_enhanced LIMIT 3")
        sample = cursor.fetchall()
        print("Sample data:", sample)
        
except Exception as e:
    print(f"Error: {e}")

conn.close()