#!/usr/bin/env python3
"""
Check database structure
"""

import sqlite3

conn = sqlite3.connect('assets.db')
cursor = conn.cursor()

# Check what tables exist
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('📊 Available database tables:')
for table in tables:
    print(f'   {table[0]}')

# Check if assets_enhanced exists
try:
    cursor.execute('SELECT COUNT(*) FROM assets_enhanced')
    count = cursor.fetchone()[0]
    print(f'✅ assets_enhanced table: {count} records')
except Exception as e:
    print(f'❌ assets_enhanced table not found: {e}')
    
    # Check original assets table
    try:
        cursor.execute('SELECT COUNT(*) FROM assets')
        count = cursor.fetchone()[0]
        print(f'✅ assets table: {count} records')
    except Exception as e:
        print(f'❌ assets table also not found: {e}')

conn.close()