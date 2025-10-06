#!/usr/bin/env python3
"""
SQLite Database Analysis Tool
Analyzes the current SQLite database structure and data
"""

import sqlite3
import os
import sys

def analyze_sqlite_database():
    """Analyze the current SQLite database"""
    
    db_path = 'assets.db'
    
    if not os.path.exists(db_path):
        print("❌ No assets.db file found")
        return
    
    print("📊 CURRENT SQLITE DATABASE STRUCTURE:")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        total_records = 0
        
        for table in tables:
            table_name = table[0]
            print(f"\n🗂️  TABLE: {table_name}")
            
            # Get table structure
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print("   COLUMNS:")
            for col in columns:
                pk_info = "PRIMARY KEY" if col[5] else ""
                null_info = "NOT NULL" if col[3] else "NULL"
                print(f"     - {col[1]} ({col[2]}) {pk_info} {null_info}")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            total_records += count
            print(f"   📈 RECORDS: {count}")
            
            # Show sample data (first 3 rows)
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                sample_data = cursor.fetchall()
                print("   📋 SAMPLE DATA:")
                for i, row in enumerate(sample_data, 1):
                    print(f"     Row {i}: {str(row)[:100]}...")
        
        print(f"\n✅ Total records across all tables: {total_records}")
        print(f"✅ Database file size: {os.path.getsize(db_path):,} bytes")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error analyzing database: {e}")

if __name__ == "__main__":
    analyze_sqlite_database()