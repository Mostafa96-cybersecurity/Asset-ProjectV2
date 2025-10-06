#!/usr/bin/env python3
"""
Generate Static JSON Data for Dashboard
"""
import sys
import json
import sqlite3
import os
from datetime import datetime

def generate_assets_json():
    """Generate static JSON files for the dashboard"""
    try:
        db_path = "../assets.db"
        if not os.path.exists(db_path):
            print(f"ERROR: Database not found at {db_path}")
            return False
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print("Generating assets data...")
        
        # Get assets with intelligent classification
        cursor.execute("""
            SELECT 
                id, hostname, computer_name, ip_address,
                CASE 
                    WHEN device_status = 'Online' OR ping_response_ms > 0 THEN 'online'
                    WHEN device_status = 'Offline' OR device_status = '' OR device_status IS NULL THEN 'offline'
                    ELSE 'unknown'
                END as device_status,
                CASE 
                    WHEN (processor_name IS NULL OR processor_name = '') AND 
                         (operating_system IS NULL OR operating_system = '') AND 
                         (total_physical_memory_gb IS NULL OR total_physical_memory_gb = 0) 
                    THEN 'Asset Incomplete'
                    WHEN device_type IS NULL OR device_type = '' OR device_type = 'Unknown Device' 
                    THEN 'Classification Pending'
                    ELSE COALESCE(device_type, 'Unknown Device')
                END as device_type,
                processor_name, total_physical_memory_gb, operating_system,
                COALESCE(assigned_department, 'Unassigned') as assigned_department,
                system_manufacturer, system_model,
                mac_address, current_user,
                collection_method, COALESCE(data_completeness_score, 0) as data_completeness_score,
                last_seen, created_at, updated_at
            FROM assets_enhanced 
            ORDER BY 
                CASE 
                    WHEN device_status = 'Online' OR ping_response_ms > 0 THEN 1
                    ELSE 2
                END,
                hostname
        """)
        
        assets = [dict(row) for row in cursor.fetchall()]
        
        # Generate statistics
        total_count = len(assets)
        
        # Device status distribution
        device_status = {'online': 0, 'offline': 0, 'unknown': 0}
        asset_types = {}
        departments = {}
        incomplete_count = 0
        
        for asset in assets:
            # Count by status
            status = asset['device_status']
            if status in device_status:
                device_status[status] += 1
            
            # Count by type
            asset_type = asset['device_type']
            asset_types[asset_type] = asset_types.get(asset_type, 0) + 1
            
            if asset_type == 'Asset Incomplete':
                incomplete_count += 1
            
            # Count by department
            dept = asset['assigned_department']
            departments[dept] = departments.get(dept, 0) + 1
        
        # Generate stats object
        stats = {
            "total_assets": total_count,
            "total_devices": total_count,
            "device_status": device_status,
            "device_types": [{"name": k, "count": v} for k, v in asset_types.items()],
            "departments": [{"name": k, "count": v} for k, v in departments.items()],
            "incomplete_assets": incomplete_count,
            "avg_data_completeness": sum(asset.get('data_completeness_score', 0) for asset in assets) / total_count if total_count > 0 else 0,
            "status": "OK",
            "classification_enabled": True,
            "last_updated": datetime.now().isoformat()
        }
        
        # Save assets JSON
        assets_file = "../static/assets_data.json"
        with open(assets_file, 'w') as f:
            json.dump({
                "assets": assets,
                "total": total_count,
                "status": "OK",
                "classification_enabled": True
            }, f, indent=2, default=str)
        
        # Save stats JSON
        stats_file = "../static/stats_data.json"
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2, default=str)
        
        conn.close()
        
        print(f"SUCCESS! Generated data files:")
        print(f"  - Assets: {assets_file} ({total_count} assets)")
        print(f"  - Stats: {stats_file}")
        print(f"  - Incomplete Assets: {incomplete_count}")
        print(f"  - Device Status: {device_status}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("Asset Data Generator - Converting Database to JSON")
    print("=" * 60)
    
    success = generate_assets_json()
    
    if success:
        print("\n[SUCCESS] JSON data files generated successfully!")
        print("The dashboard can now load data from these static files.")
    else:
        print("\n[ERROR] Failed to generate JSON data files.")
        
    print("=" * 60)