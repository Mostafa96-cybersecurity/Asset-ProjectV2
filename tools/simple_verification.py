#!/usr/bin/env python3
"""
Simple Technical Data Collection Test

This tool tests if all required technical data fields exist in the database
and can successfully store complete device data.
"""

import os
import sys
import sqlite3
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.connection import connect

def test_database_fields():
    """Test if all technical fields exist in database"""
    print("Testing database schema...")
    
    REQUIRED_FIELDS = [
        "hostname", "working_user", "domain_name", "model_vendor", 
        "device_infrastructure", "firmware_os_version", "installed_ram_gb",
        "ip_address", "storage_info", "manufacturer", "sn", "processor_info",
        "system_sku", "active_gpu", "connected_screens", "disk_count", 
        "mac_address", "all_mac_addresses", "cpu_details", "disk_details",
        "device_type", "data_source"
    ]
    
    try:
        with connect() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(assets)")
            columns = [row[1] for row in cursor.fetchall()]
            
            missing_fields = []
            existing_fields = []
            
            for field in REQUIRED_FIELDS:
                if field in columns:
                    existing_fields.append(field)
                else:
                    missing_fields.append(field)
            
            print(f"DATABASE SCHEMA TEST RESULTS:")
            print(f"Total Technical Fields Required: {len(REQUIRED_FIELDS)}")
            print(f"Fields Found in Database: {len(existing_fields)}")
            print(f"Missing Fields: {len(missing_fields)}")
            
            if missing_fields:
                print(f"Missing: {missing_fields}")
                return False
            else:
                print("SUCCESS: All technical fields exist in database!")
                return True
                
    except Exception as e:
        print(f"Database test failed: {e}")
        return False

def test_data_storage():
    """Test storing complete technical data"""
    print("\nTesting data storage...")
    
    # Sample complete technical data
    test_data = {
        "hostname": "TEST-PC-001",
        "working_user": "testuser",
        "domain_name": "TESTDOMAIN",
        "model_vendor": "Dell Inc. OptiPlex 7090",
        "device_infrastructure": "Workstation",
        "firmware_os_version": "Windows 10 Pro",
        "installed_ram_gb": 16,
        "ip_address": "192.168.1.100",
        "storage_info": "512GB SSD",
        "manufacturer": "Dell Inc.",
        "sn": "ABC123456789",
        "processor_info": "Intel Core i7-10700",
        "system_sku": "OptiPlex 7090",
        "active_gpu": "NVIDIA GeForce RTX 3060",
        "connected_screens": 2,
        "disk_count": 1,
        "mac_address": "AA:BB:CC:DD:EE:FF",
        "all_mac_addresses": "AA:BB:CC:DD:EE:FF, 11:22:33:44:55:66",
        "cpu_details": "[{\"name\": \"Intel Core i7-10700\", \"cores\": 8}]",
        "disk_details": "[{\"model\": \"Samsung SSD 980\", \"size\": \"512GB\"}]",
        "device_type": "workstation",
        "data_source": "Enhanced Collection Test",
        "status": "Active",
        "notes": "Test device for verification",
        "updated_at": datetime.now().isoformat()
    }
    
    try:
        with connect() as conn:
            cursor = conn.cursor()
            
            # Prepare insert
            fields = list(test_data.keys())
            placeholders = ', '.join(['?' for _ in fields])
            columns = ', '.join(fields)
            values = [test_data[field] for field in fields]
            
            # Insert test data
            cursor.execute(f"""
                INSERT OR REPLACE INTO assets ({columns})
                VALUES ({placeholders})
            """, values)
            
            # Verify data was stored
            cursor.execute("SELECT * FROM assets WHERE hostname = ?", ("TEST-PC-001",))
            result = cursor.fetchone()
            
            if result:
                print("SUCCESS: Test data stored and retrieved successfully!")
                
                # Check key fields
                stored_fields = dict(result)
                print(f"Stored Hostname: {stored_fields.get('hostname')}")
                print(f"Stored Working User: {stored_fields.get('working_user')}")
                print(f"Stored RAM: {stored_fields.get('installed_ram_gb')} GB")
                print(f"Stored Processor: {stored_fields.get('processor_info')}")
                print(f"Stored GPU: {stored_fields.get('active_gpu')}")
                
                # Calculate completion rate
                non_empty_fields = sum(1 for v in stored_fields.values() if v and str(v).strip())
                completion_rate = (non_empty_fields / len(stored_fields)) * 100
                print(f"Data Completion Rate: {completion_rate:.1f}%")
                
                return True
            else:
                print("ERROR: Data was not stored properly")
                return False
                
    except Exception as e:
        print(f"Data storage test failed: {e}")
        return False

def main():
    """Run all verification tests"""
    print("=" * 60)
    print("TECHNICAL DATA COLLECTION VERIFICATION")
    print("=" * 60)
    
    # Test 1: Database schema
    schema_ok = test_database_fields()
    
    # Test 2: Data storage
    storage_ok = test_data_storage()
    
    print("\n" + "=" * 60)
    print("FINAL RESULTS:")
    print(f"Database Schema: {'PASS' if schema_ok else 'FAIL'}")
    print(f"Data Storage: {'PASS' if storage_ok else 'FAIL'}")
    
    if schema_ok and storage_ok:
        print("OVERALL: SUCCESS - Complete technical data collection system is ready!")
        return True
    else:
        print("OVERALL: FAILED - Some issues need to be addressed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)