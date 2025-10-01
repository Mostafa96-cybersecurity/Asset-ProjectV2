#!/usr/bin/env python3
"""
Enhanced Data Collector GUI Integration
جامع البيانات المحسن مع تكامل الواجهة الرسومية
"""

import sqlite3
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import json
import traceback
from collector_integration import CollectorIntegration

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - EnhancedCollectorGUI - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedCollectorGUI:
    """Enhanced data collector with GUI integration for desktop app"""
    
    def __init__(self, database_path="assets.db"):
        self.database_path = database_path
        self.integration = CollectorIntegration(database_path)
        self.logger = logger
        
    def enhance_existing_device(self, device_id):
        """Enhance existing device with comprehensive data collection - called from GUI"""
        try:
            self.logger.info(f"GUI requested enhancement for device {device_id}")
            return self.integration.enhance_existing_device_data(device_id)
        except Exception as e:
            self.logger.error(f"GUI enhancement failed for device {device_id}: {e}")
            return False
    
    def enhance_device_by_ip(self, ip_address, update_database=True):
        """Enhance device by IP address with comprehensive data - called from GUI"""
        try:
            self.logger.info(f"GUI requested enhancement for IP {ip_address}")
            enhanced_data = self.integration.collect_enhanced_data(ip_address, {})
            
            if update_database:
                # Find device by IP
                conn = sqlite3.connect(self.database_path)
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM assets WHERE ip_address = ?", (ip_address,))
                row = cursor.fetchone()
                
                if row:
                    device_id = row[0]
                    success = self.integration.update_device_with_enhanced_data(device_id, enhanced_data)
                    self.logger.info(f"Enhanced existing device {device_id} at {ip_address}")
                    conn.close()
                    return success
                else:
                    # Create new device
                    device_id = self._create_new_device_with_enhanced_data(ip_address, enhanced_data)
                    self.logger.info(f"Created new enhanced device {device_id} at {ip_address}")
                    conn.close()
                    return device_id is not None
                
            return True
            
        except Exception as e:
            self.logger.error(f"GUI device enhancement failed for {ip_address}: {e}")
            return False
    
    def _create_new_device_with_enhanced_data(self, ip_address, enhanced_data):
        """Create new device with enhanced data"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Prepare insert data
            insert_data = {
                'ip_address': ip_address,
                'hostname': enhanced_data.get('hostname', f'device-{ip_address.replace(".", "-")}'),
                'device_type': enhanced_data.get('device_type', 'Unknown'),
                'scan_date': datetime.now().isoformat(),
                'scan_status': 'Completed',
                'collection_method': 'Enhanced Network Scan',
                'data_source': 'GUI Enhanced Collection',
                'status': 'Active',
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'created_by': 'Desktop GUI'
            }
            
            # Merge enhanced data
            for key, value in enhanced_data.items():
                if key not in insert_data:
                    insert_data[key] = value
            
            # Get column names
            cursor.execute("PRAGMA table_info(assets)")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Filter data to only include valid columns
            filtered_data = {k: v for k, v in insert_data.items() if k in columns}
            
            # Create insert query
            columns_str = ', '.join(filtered_data.keys())
            placeholders = ', '.join(['?' for _ in filtered_data])
            insert_sql = f"INSERT INTO assets ({columns_str}) VALUES ({placeholders})"
            
            cursor.execute(insert_sql, list(filtered_data.values()))
            device_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return device_id
            
        except Exception as e:
            self.logger.error(f"Failed to create new device {ip_address}: {e}")
            return None

    def get_enhancement_status(self, device_id):
        """Get enhancement status for a device - called from GUI"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT data_quality_score, performance_score, risk_score, 
                       last_updated, collection_method
                FROM assets WHERE id = ?
            """, (device_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'data_quality_score': row[0] or 'N/A',
                    'performance_score': row[1] or 'N/A', 
                    'risk_score': row[2] or 'N/A',
                    'last_updated': row[3] or 'Never',
                    'collection_method': row[4] or 'Basic'
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get enhancement status for device {device_id}: {e}")
            return None

    def bulk_enhance_devices(self, device_ids):
        """Enhance multiple devices - called from GUI"""
        results = {}
        total = len(device_ids)
        
        self.logger.info(f"GUI requested bulk enhancement for {total} devices")
        
        for i, device_id in enumerate(device_ids):
            try:
                self.logger.info(f"Enhancing device {device_id} ({i+1}/{total})")
                success = self.enhance_existing_device(device_id)
                results[device_id] = 'Success' if success else 'Failed'
            except Exception as e:
                self.logger.error(f"Bulk enhancement failed for device {device_id}: {e}")
                results[device_id] = f'Error: {str(e)}'
        
        return results

    def scan_and_enhance_range(self, ip_range_start, ip_range_end):
        """Scan IP range and enhance all discovered devices - called from GUI"""
        try:
            self.logger.info(f"GUI requested range scan and enhancement: {ip_range_start} to {ip_range_end}")
            
            # Parse IP range
            start_parts = ip_range_start.split('.')
            end_parts = ip_range_end.split('.')
            
            if len(start_parts) != 4 or len(end_parts) != 4:
                return {'error': 'Invalid IP range format'}
            
            base_ip = '.'.join(start_parts[:3])
            start_last = int(start_parts[3])
            end_last = int(end_parts[3])
            
            results = {}
            total_ips = end_last - start_last + 1
            
            for i in range(start_last, end_last + 1):
                target_ip = f"{base_ip}.{i}"
                
                try:
                    self.logger.info(f"Scanning and enhancing {target_ip} ({i-start_last+1}/{total_ips})")
                    success = self.enhance_device_by_ip(target_ip, update_database=True)
                    results[target_ip] = 'Enhanced' if success else 'Failed'
                except Exception as e:
                    results[target_ip] = f'Error: {str(e)}'
            
            return results
            
        except Exception as e:
            self.logger.error(f"Range scan and enhancement failed: {e}")
            return {'error': str(e)}

    def get_comprehensive_device_report(self, device_id):
        """Get comprehensive device report for GUI display"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Get all device data
            cursor.execute("SELECT * FROM assets WHERE id = ?", (device_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            # Get column names
            cursor.execute("PRAGMA table_info(assets)")
            columns = [col[1] for col in cursor.fetchall()]
            
            device_data = dict(zip(columns, row))
            
            # Parse JSON fields
            json_fields = ['open_ports', 'closed_ports', 'service_detection', 'security_assessment', 'listening_ports']
            for field in json_fields:
                if device_data.get(field):
                    try:
                        device_data[field] = json.loads(device_data[field])
                    except:
                        pass
            
            # Create comprehensive report
            report = {
                'basic_info': {
                    'hostname': device_data.get('hostname', 'Unknown'),
                    'ip_address': device_data.get('ip_address', 'Unknown'),
                    'device_type': device_data.get('device_type', 'Unknown'),
                    'status': device_data.get('status', 'Unknown'),
                    'last_updated': device_data.get('last_updated', 'Never')
                },
                'scores': {
                    'data_quality': device_data.get('data_quality_score', 'N/A'),
                    'performance': device_data.get('performance_score', 'N/A'),
                    'risk': device_data.get('risk_score', 'N/A')
                },
                'network_info': {
                    'ping_status': device_data.get('ping_status', 'Unknown'),
                    'response_time': device_data.get('response_time_ms', 'N/A'),
                    'open_ports': device_data.get('open_ports', []),
                    'services': device_data.get('service_detection', [])
                },
                'system_info': {
                    'os_name': device_data.get('os_name', 'Unknown'),
                    'manufacturer': device_data.get('manufacturer', 'Unknown'),
                    'model': device_data.get('model', 'Unknown'),
                    'processor': device_data.get('processor', 'Unknown'),
                    'memory_gb': device_data.get('memory_gb', 'Unknown')
                },
                'security': {
                    'security_score': device_data.get('security_score', 'N/A'),
                    'firewall_detected': device_data.get('firewall_detected', 'Unknown'),
                    'security_issues': device_data.get('security_assessment', [])
                },
                'collection_info': {
                    'method': device_data.get('collection_method', 'Unknown'),
                    'source': device_data.get('data_source', 'Unknown'),
                    'scan_date': device_data.get('scan_date', 'Unknown'),
                    'created_by': device_data.get('created_by', 'Unknown')
                }
            }
            
            conn.close()
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate device report for {device_id}: {e}")
            return None

# For backward compatibility
class EnhancedDataCollector(EnhancedCollectorGUI):
    """Alias for backward compatibility"""
    pass

def main():
    """Test the GUI integration"""
    collector = EnhancedCollectorGUI()
    
    # Get the first available device ID from database
    import sqlite3
    try:
        conn = sqlite3.connect("assets.db")
        cursor = conn.cursor()
        cursor.execute("SELECT MIN(id) FROM assets")
        first_device_id = cursor.fetchone()[0]
        conn.close()
        
        if first_device_id is None:
            print("No devices found in database. Please run collection first.")
            return
            
        print(f"Testing enhancement with device ID {first_device_id}")
        
        # Test enhancement
        success = collector.enhance_existing_device(first_device_id)
        print(f"Enhancement {'successful' if success else 'failed'}")
        
        # Test report generation
        report = collector.get_comprehensive_device_report(first_device_id)
        if report:
            print("Device report generated successfully")
            print(f"Device: {report['basic_info']['hostname']} ({report['basic_info']['ip_address']})")
            print(f"Scores: Quality={report['scores']['data_quality']}, Performance={report['scores']['performance']}, Risk={report['scores']['risk']}")
        else:
            print("Failed to generate device report")
            
    except Exception as e:
        print(f"Error in main test: {e}")
        print("Make sure the database exists and contains devices.")

if __name__ == "__main__":
    main()