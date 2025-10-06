
import sqlite3
import json
from datetime import datetime

def add_manual_network_device(device_info):
    """Add network device manually with all new DB columns"""
    try:
        conn = sqlite3.connect('assets.db')
        cursor = conn.cursor()
        
        # Get all column names
        cursor.execute("PRAGMA table_info(assets)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Prepare comprehensive device data
        device_data = {
            'hostname': device_info.get('hostname', 'Unknown'),
            'ip_address': device_info.get('ip_address', ''),
            'device_type': device_info.get('device_type', 'Network Device'),
            'manufacturer': device_info.get('manufacturer', 'Unknown'),
            'model': device_info.get('model', 'Unknown'),
            'mac_address': device_info.get('mac_address', ''),
            'data_source': 'Manual Network Addition',
            'collection_method': 'manual',
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'status': 'Active',
            'location': device_info.get('location', ''),
            'department': device_info.get('department', ''),
            'notes': device_info.get('notes', ''),
            'asset_tag': device_info.get('asset_tag', ''),
            'serial_number': device_info.get('serial_number', ''),
            'collection_quality': 'Manual Entry',
            'quality_score': 80
        }
        
        # Fill missing columns with appropriate defaults
        for column in columns:
            if column not in device_data:
                device_data[column] = None
        
        # Insert device
        placeholders = ', '.join(['?' for _ in columns])
        column_list = ', '.join(columns)
        values = [device_data.get(col) for col in columns]
        
        cursor.execute(f"INSERT OR REPLACE INTO assets ({column_list}) VALUES ({placeholders})", values)
        conn.commit()
        conn.close()
        
        print(f"✅ Added network device: {device_info.get('hostname', 'Unknown')}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to add network device: {e}")
        return False

def get_manual_device_template():
    """Get template for manual device entry"""
    return {
        'hostname': '',
        'ip_address': '',
        'device_type': 'Network Device',
        'manufacturer': '',
        'model': '',
        'mac_address': '',
        'location': '',
        'department': '',
        'asset_tag': '',
        'serial_number': '',
        'notes': ''
    }
