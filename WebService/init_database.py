#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Initialization and Data Creation Script
Ensures the database has proper structure and sample data
"""

import sqlite3
import os
import json
from datetime import datetime

def find_database_path():
    """Find the correct database path"""
    possible_paths = [
        "../assets.db",
        "../../assets.db", 
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets.db"),
        "d:/Assets-Projects/Asset-Project-Enhanced/assets.db",
        "assets.db"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # Return the most likely path for creation
    return "../assets.db"

def create_database_structure(db_path):
    """Create the database structure"""
    print(f"[INFO] Creating database structure in {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create assets table
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
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            serial_number TEXT,
            purchase_date TEXT,
            warranty_expiry TEXT,
            asset_tag TEXT,
            notes TEXT
        )
    """)
    
    # Create departments table
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
    
    # Create asset_history table for tracking changes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS asset_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_id INTEGER,
            change_type TEXT,
            old_value TEXT,
            new_value TEXT,
            changed_by TEXT,
            changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (asset_id) REFERENCES assets (id)
        )
    """)
    
    conn.commit()
    conn.close()
    print("[OK] Database structure created")

def populate_sample_data(db_path):
    """Populate the database with sample data"""
    print("[INFO] Populating database with sample data")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if data already exists
    cursor.execute("SELECT COUNT(*) FROM assets")
    asset_count = cursor.fetchone()[0]
    
    if asset_count > 0:
        print(f"[INFO] Database already has {asset_count} assets")
        conn.close()
        return
    
    # Sample departments
    departments = [
        ('IT Department', 'Information Technology', 'Building A - Floor 3', 'John Smith', 'john.smith@company.com'),
        ('HR Department', 'Human Resources', 'Building A - Floor 2', 'Jane Doe', 'jane.doe@company.com'),
        ('Finance Department', 'Finance and Accounting', 'Building A - Floor 4', 'Bob Johnson', 'bob.johnson@company.com'),
        ('Operations', 'Operations and Logistics', 'Building B - Floor 1', 'Alice Brown', 'alice.brown@company.com'),
        ('Marketing', 'Marketing and Sales', 'Building A - Floor 1', 'Charlie Wilson', 'charlie.wilson@company.com')
    ]
    
    cursor.executemany("""
        INSERT OR IGNORE INTO departments (name, description, location, manager_name, manager_email)
        VALUES (?, ?, ?, ?, ?)
    """, departments)
    
    # Sample assets with diverse data
    assets = [
        # Workstations
        ('WS-IT-001', '192.168.1.100', '00:15:5D:00:01:00', 'Workstation', 'Dell', 'OptiPlex 7090', 'Windows 11 Pro', 'Intel Core i7-11700', '16', '512', 'IT Department', 'Building A - Floor 3', 'Active', 'DT001001', '2023-01-15', '2026-01-15', 'AST001'),
        ('WS-HR-001', '192.168.1.101', '00:15:5D:00:01:01', 'Workstation', 'HP', 'EliteDesk 800 G8', 'Windows 11 Pro', 'Intel Core i5-11500', '8', '256', 'HR Department', 'Building A - Floor 2', 'Active', 'HP001001', '2023-02-20', '2026-02-20', 'AST002'),
        ('WS-FIN-001', '192.168.1.102', '00:15:5D:00:01:02', 'Workstation', 'Lenovo', 'ThinkCentre M90s', 'Windows 11 Pro', 'Intel Core i7-11700T', '16', '512', 'Finance Department', 'Building A - Floor 4', 'Active', 'LN001001', '2023-03-10', '2026-03-10', 'AST003'),
        
        # Laptops
        ('LP-MKT-001', '192.168.1.110', '00:15:5D:00:02:00', 'Laptop', 'Dell', 'Latitude 5520', 'Windows 11 Pro', 'Intel Core i5-1135G7', '8', '256', 'Marketing', 'Building A - Floor 1', 'Active', 'DL001001', '2023-04-05', '2026-04-05', 'AST004'),
        ('LP-HR-002', '192.168.1.111', '00:15:5D:00:02:01', 'Laptop', 'HP', 'EliteBook 840 G8', 'Windows 11 Pro', 'Intel Core i7-1165G7', '16', '512', 'HR Department', 'Building A - Floor 2', 'Active', 'HP002001', '2023-05-15', '2026-05-15', 'AST005'),
        
        # Servers
        ('SRV-DB-001', '192.168.1.10', '00:15:5D:00:03:00', 'Server', 'HPE', 'ProLiant DL380 Gen10', 'Windows Server 2022', 'Intel Xeon Gold 6226R', '128', '4000', 'IT Department', 'Server Room A', 'Active', 'HPE001001', '2022-12-01', '2025-12-01', 'SRV001'),
        ('SRV-WEB-001', '192.168.1.11', '00:15:5D:00:03:01', 'Server', 'Dell', 'PowerEdge R740', 'Ubuntu Server 22.04', 'Intel Xeon Gold 5218R', '64', '2000', 'IT Department', 'Server Room A', 'Active', 'DL003001', '2023-01-10', '2026-01-10', 'SRV002'),
        ('SRV-FILE-001', '192.168.1.12', '00:15:5D:00:03:02', 'Server', 'Synology', 'DiskStation DS1621+', 'DSM 7.1', 'AMD Ryzen V1500B', '4', '12000', 'IT Department', 'Server Room B', 'Active', 'SY001001', '2023-06-01', '2026-06-01', 'SRV003'),
        
        # Network Equipment
        ('SW-CORE-001', '192.168.1.1', '00:15:5D:00:04:00', 'Network Device', 'Cisco', 'Catalyst 9300-48U', 'IOS XE 16.12', 'N/A', 'N/A', 'N/A', 'IT Department', 'Server Room A', 'Active', 'CS001001', '2022-11-15', '2025-11-15', 'NET001'),
        ('SW-ACCESS-001', '192.168.1.2', '00:15:5D:00:04:01', 'Network Device', 'Cisco', 'Catalyst 2960-X', 'IOS 15.2', 'N/A', 'N/A', 'N/A', 'IT Department', 'Building A - Floor 1', 'Active', 'CS002001', '2023-01-20', '2026-01-20', 'NET002'),
        ('FW-001', '192.168.1.3', '00:15:5D:00:04:02', 'Firewall', 'Fortinet', 'FortiGate 200F', 'FortiOS 7.2', 'N/A', 'N/A', 'N/A', 'IT Department', 'Server Room A', 'Active', 'FG001001', '2023-02-28', '2026-02-28', 'NET003'),
        
        # Printers
        ('PRT-HR-001', '192.168.1.200', '00:15:5D:00:05:00', 'Printer', 'Canon', 'imageRUNNER ADVANCE C3525i', 'N/A', 'N/A', 'N/A', 'N/A', 'HR Department', 'Building A - Floor 2', 'Active', 'CN001001', '2023-03-15', '2026-03-15', 'PRT001'),
        ('PRT-FIN-001', '192.168.1.201', '00:15:5D:00:05:01', 'Printer', 'HP', 'LaserJet Enterprise M608dn', 'N/A', 'N/A', 'N/A', 'N/A', 'Finance Department', 'Building A - Floor 4', 'Active', 'HP005001', '2023-04-20', '2026-04-20', 'PRT002'),
        
        # Mobile Devices / Tablets
        ('TAB-OPS-001', '192.168.1.220', '00:15:5D:00:06:00', 'Tablet', 'Microsoft', 'Surface Pro 9', 'Windows 11', 'Intel Core i5-1235U', '8', '256', 'Operations', 'Building B - Floor 1', 'Active', 'MS001001', '2023-05-10', '2026-05-10', 'TAB001'),
        
        # Test offline device
        ('WS-OFFLINE-001', '192.168.1.199', '00:15:5D:00:07:00', 'Workstation', 'Dell', 'OptiPlex 7080', 'Windows 10 Pro', 'Intel Core i5-10500', '8', '256', 'IT Department', 'Storage Room', 'Offline', 'DT002001', '2022-08-15', '2025-08-15', 'AST006')
    ]
    
    cursor.executemany("""
        INSERT INTO assets (hostname, ip_address, mac_address, device_type, manufacturer, model, operating_system, processor, memory_gb, storage_gb, department, location, status, serial_number, purchase_date, warranty_expiry, asset_tag)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, assets)
    
    conn.commit()
    conn.close()
    
    print(f"[OK] Created {len(departments)} departments and {len(assets)} assets")

def verify_data(db_path):
    """Verify the data was created correctly"""
    print("[INFO] Verifying database data")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check assets
    cursor.execute("SELECT COUNT(*) FROM assets")
    asset_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM assets WHERE status = 'Active'")
    active_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM assets WHERE status = 'Offline'")
    offline_count = cursor.fetchone()[0]
    
    # Check departments
    cursor.execute("SELECT COUNT(*) FROM departments")
    dept_count = cursor.fetchone()[0]
    
    # Check device types
    cursor.execute("SELECT DISTINCT device_type FROM assets")
    device_types = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    print(f"[OK] Database verification complete:")
    print(f"  - Total assets: {asset_count}")
    print(f"  - Active devices: {active_count}")
    print(f"  - Offline devices: {offline_count}")
    print(f"  - Departments: {dept_count}")
    print(f"  - Device types: {len(device_types)} ({', '.join(device_types)})")

def main():
    """Main function"""
    print("=" * 60)
    print("DATABASE INITIALIZATION SCRIPT")
    print("=" * 60)
    
    # Find database path
    db_path = find_database_path()
    abs_path = os.path.abspath(db_path)
    
    print(f"[INFO] Database path: {abs_path}")
    print(f"[INFO] Database exists: {os.path.exists(db_path)}")
    
    # Create structure
    create_database_structure(db_path)
    
    # Populate data
    populate_sample_data(db_path)
    
    # Verify
    verify_data(db_path)
    
    print("\n" + "=" * 60)
    print("DATABASE INITIALIZATION COMPLETE")
    print("=" * 60)
    print(f"Database ready at: {abs_path}")
    print("Web service should now be able to connect and load data.")

if __name__ == "__main__":
    main()