#!/usr/bin/env python3
"""Database structure checker"""
import sqlite3
import os

def check_database_structure():
    db_path = 'assets.db'
    if not os.path.exists(db_path):
        print("Database not found!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("📊 Database Tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        print("\n🗃️ Assets Table Structure:")
        cursor.execute('PRAGMA table_info(assets)')
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'}")
        
        # Sample data
        print("\n📋 Sample Asset Records (first 3):")
        cursor.execute('SELECT * FROM assets LIMIT 3')
        rows = cursor.fetchall()
        if rows:
            for i, row in enumerate(rows, 1):
                print(f"\n  Record {i}:")
                for j, col in enumerate(columns):
                    if j < len(row) and row[j]:
                        print(f"    {col[1]}: {row[j]}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_database_structure()