#!/usr/bin/env python3
import sqlite3
import os

# Check database schema
db_path = "../assets.db"
print(f"Checking database: {os.path.abspath(db_path)}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check what tables exist
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"\nTables found: {[table[0] for table in tables]}")

# Check assets_enhanced columns if it exists
try:
    cursor.execute("PRAGMA table_info(assets_enhanced)")
    enhanced_columns = cursor.fetchall()
    print(f"\nAssets Enhanced table columns ({len(enhanced_columns)}):")
    for col in enhanced_columns:
        print(f"  {col[1]} ({col[2]})")
except:
    print("\nAssets Enhanced table not found")

# Check basic assets columns
try:
    cursor.execute("PRAGMA table_info(assets)")
    basic_columns = cursor.fetchall()
    print(f"\nBasic Assets table columns ({len(basic_columns)}):")
    for col in basic_columns:
        print(f"  {col[1]} ({col[2]})")
except:
    print("\nBasic Assets table not found")

# Check row counts
try:
    cursor.execute("SELECT COUNT(*) FROM assets_enhanced")
    enhanced_count = cursor.fetchone()[0]
    print(f"\nAssets Enhanced row count: {enhanced_count}")
except:
    enhanced_count = 0
    print("\nAssets Enhanced table has no rows or doesn't exist")

try:
    cursor.execute("SELECT COUNT(*) FROM assets")
    basic_count = cursor.fetchone()[0]
    print(f"Basic Assets row count: {basic_count}")
except:
    basic_count = 0
    print("Basic Assets table has no rows or doesn't exist")

conn.close()