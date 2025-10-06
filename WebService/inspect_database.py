#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Inspection and Repair Script
"""

import sqlite3
import os
import json

def inspect_database():
    """Inspect the database structure and contents"""
    db_path = "../assets.db"
    
    print("=" * 60)
    print("DATABASE INSPECTION REPORT")
    print("=" * 60)
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"[ERROR] Database file not found: {db_path}")
        return False
    
    print(f"[OK] Database file exists: {db_path}")
    print(f"[INFO] File size: {os.path.getsize(db_path):,} bytes")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"\n[INFO] Found {len(tables)} tables:")
        for table in tables:
            table_name = table[0]
            print(f"  - {table_name}")
            
            # Get table info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print(f"    Columns: {len(columns)}")
            
            # Get row count
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"    Records: {count}")
                
                # Show sample data for main tables
                if table_name in ['assets', 'assets_enhanced'] and count > 0:
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
                    sample = cursor.fetchone()
                    if sample:
                        print(f"    Sample columns: {list(sample.keys())[:10]}...")
                        
            except Exception as e:
                print(f"    Error reading table: {e}")
        
        # Test specific queries that the web service uses
        print(f"\n[INFO] Testing web service queries:")
        
        # Test assets query
        try:
            cursor.execute("SELECT * FROM assets LIMIT 5")
            assets = cursor.fetchall()
            print(f"[OK] Assets query: {len(assets)} records")
            
            if assets:
                sample_asset = dict(assets[0])
                print(f"[INFO] Sample asset keys: {list(sample_asset.keys())[:10]}...")
                
        except Exception as e:
            print(f"[ERROR] Assets query failed: {e}")
        
        # Test enhanced assets query
        try:
            cursor.execute("SELECT * FROM assets_enhanced LIMIT 5")
            enhanced_assets = cursor.fetchall()
            print(f"[OK] Enhanced assets query: {len(enhanced_assets)} records")
        except Exception as e:
            print(f"[WARNING] Enhanced assets query failed: {e}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return False

def create_sample_data():
    """Create sample data if database is empty"""
    db_path = "../assets.db"
    
    print("\n" + "=" * 60)
    print("CREATING SAMPLE DATA")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create assets table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hostname TEXT,
                ip_address TEXT,
                mac_address TEXT,
                device_type TEXT,
                manufacturer TEXT,
                model TEXT,
                operating_system TEXT,
                processor TEXT,
                memory_gb TEXT,
                storage_gb TEXT,
                department TEXT,
                location TEXT,
                status TEXT DEFAULT 'Active',
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Check if assets table is empty
        cursor.execute("SELECT COUNT(*) FROM assets")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("[INFO] Assets table is empty. Creating sample data...")
            
            sample_assets = [
                ('DESKTOP-001', '192.168.1.100', '00:11:22:33:44:55', 'Workstation', 'Dell', 'OptiPlex 7090', 'Windows 10', 'Intel i7-10700', '16', '512', 'IT Department', 'Office Floor 1', 'Active'),
                ('LAPTOP-HR-01', '192.168.1.101', '00:11:22:33:44:56', 'Laptop', 'HP', 'EliteBook 840', 'Windows 11', 'Intel i5-1135G7', '8', '256', 'HR Department', 'Office Floor 2', 'Active'),
                ('SERVER-DB-01', '192.168.1.10', '00:11:22:33:44:57', 'Server', 'HPE', 'ProLiant DL380', 'Windows Server 2019', 'Intel Xeon Gold 6226R', '64', '2000', 'IT Department', 'Server Room', 'Active'),
                ('PRINTER-01', '192.168.1.200', '00:11:22:33:44:58', 'Printer', 'Canon', 'imageRUNNER ADVANCE', 'N/A', 'N/A', 'N/A', 'N/A', 'Admin', 'Office Floor 1', 'Active'),
                ('SWITCH-01', '192.168.1.1', '00:11:22:33:44:59', 'Network Device', 'Cisco', 'Catalyst 2960', 'IOS', 'N/A', 'N/A', 'N/A', 'IT Department', 'Server Room', 'Active')
            ]
            
            cursor.executemany("""
                INSERT INTO assets (hostname, ip_address, mac_address, device_type, manufacturer, model, operating_system, processor, memory_gb, storage_gb, department, location, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, sample_assets)
            
            conn.commit()
            print(f"[OK] Created {len(sample_assets)} sample assets")
            
        else:
            print(f"[INFO] Assets table already has {count} records")
        
        # Create departments table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                description TEXT,
                location TEXT,
                manager_name TEXT,
                manager_email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Check if departments table is empty
        cursor.execute("SELECT COUNT(*) FROM departments")
        dept_count = cursor.fetchone()[0]
        
        if dept_count == 0:
            print("[INFO] Departments table is empty. Creating sample departments...")
            
            sample_departments = [
                ('IT Department', 'Information Technology', 'Server Room', 'John Smith', 'john.smith@company.com'),
                ('HR Department', 'Human Resources', 'Office Floor 2', 'Jane Doe', 'jane.doe@company.com'),
                ('Finance Department', 'Finance and Accounting', 'Office Floor 3', 'Bob Johnson', 'bob.johnson@company.com'),
                ('Admin', 'Administration', 'Office Floor 1', 'Alice Brown', 'alice.brown@company.com')
            ]
            
            cursor.executemany("""
                INSERT INTO departments (name, description, location, manager_name, manager_email)
                VALUES (?, ?, ?, ?, ?)
            """, sample_departments)
            
            conn.commit()
            print(f"[OK] Created {len(sample_departments)} sample departments")
        else:
            print(f"[INFO] Departments table already has {dept_count} records")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to create sample data: {e}")
        return False

def main():
    """Main function"""
    print("ASSET DATABASE INSPECTOR & REPAIR TOOL")
    
    # Inspect database
    db_ok = inspect_database()
    
    if db_ok:
        # Create sample data if needed
        create_sample_data()
        
        # Re-inspect after creating data
        print("\n" + "=" * 60)
        print("POST-REPAIR INSPECTION")
        print("=" * 60)
        inspect_database()
    
    print("\n" + "=" * 60)
    print("INSPECTION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()