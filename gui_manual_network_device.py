
import sqlite3
from datetime import datetime

class GUIManualNetworkDevice:
    """GUI-integrated manual network device addition"""
    
    def __init__(self, gui_app=None):
        self.gui_app = gui_app
    
    def add_device_from_gui(self, device_info):
        """Add device from GUI with all 469 DB columns"""
        try:
            conn = sqlite3.connect('assets.db')
            cursor = conn.cursor()
            
            # Get all column names from assets table
            cursor.execute("PRAGMA table_info(assets)")
            columns_info = cursor.fetchall()
            all_columns = [col[1] for col in columns_info]
            
            # Prepare comprehensive device data
            device_data = {
                'hostname': device_info.get('hostname', 'Unknown'),
                'ip_address': device_info.get('ip_address', ''),
                'device_type': device_info.get('device_type', 'Network Device'),
                'manufacturer': device_info.get('manufacturer', 'Unknown'),
                'model': device_info.get('model', 'Unknown'),
                'mac_address': device_info.get('mac_address', ''),
                'data_source': 'Manual GUI Addition',
                'collection_method': 'manual_gui',
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'status': 'Active',
                'location': device_info.get('location', ''),
                'department': device_info.get('department', ''),
                'notes': device_info.get('notes', ''),
                'asset_tag': device_info.get('asset_tag', ''),
                'serial_number': device_info.get('serial_number', ''),
                'collection_quality': 'Manual GUI Entry',
                'quality_score': 85,
                'created_by': 'GUI User',
                'last_updated_by': 'GUI User'
            }
            
            # Fill all columns with appropriate defaults
            final_data = {}
            for column in all_columns:
                if column in device_data:
                    final_data[column] = device_data[column]
                else:
                    final_data[column] = None
            
            # Insert into database
            placeholders = ', '.join(['?' for _ in all_columns])
            column_list = ', '.join(all_columns)
            values = [final_data[col] for col in all_columns]
            
            cursor.execute(f"INSERT OR REPLACE INTO assets ({column_list}) VALUES ({placeholders})", values)
            conn.commit()
            conn.close()
            
            # Update GUI if available
            if self.gui_app and hasattr(self.gui_app, 'log_output'):
                self.gui_app.log_output.append(f"✅ Added manual device: {device_info.get('hostname', 'Unknown')}")
            
            return True, f"Device {device_info.get('hostname', 'Unknown')} added successfully"
            
        except Exception as e:
            if self.gui_app and hasattr(self.gui_app, 'log_output'):
                self.gui_app.log_output.append(f"❌ Failed to add device: {e}")
            return False, f"Failed to add device: {e}"
    
    def get_device_template(self):
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

# Global instance
gui_manual_device = None

def get_gui_manual_device(gui_app=None):
    """Get GUI manual device manager"""
    global gui_manual_device
    if gui_manual_device is None:
        gui_manual_device = GUIManualNetworkDevice(gui_app)
    return gui_manual_device
