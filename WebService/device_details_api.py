#!/usr/bin/env python3
"""
Add detailed device view API endpoint to intelligent app
"""

from flask import jsonify
import json

def add_device_detail_endpoint(app, asset_manager):
    """Add device detail API endpoint"""
    
    @app.route('/api/device/<int:device_id>')
    def api_device_detail(device_id):
        """Get comprehensive device details"""
        conn = asset_manager.get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Get comprehensive device data
            cursor.execute("""
                SELECT * FROM assets_enhanced WHERE id = ?
            """, (device_id,))
            
            device_data = cursor.fetchone()
            
            if not device_data:
                return jsonify({'error': 'Device not found'}), 404
            
            # Convert to dict
            device = dict(device_data)
            
            # Parse JSON fields
            json_fields = ['graphics_cards', 'network_adapters', 'installed_software', 'user_profiles']
            for field in json_fields:
                if device.get(field):
                    try:
                        device[field] = json.loads(device[field])
                    except (json.JSONDecodeError, TypeError):
                        pass
            
            # Format data for display
            device_details = {
                'basic_info': {
                    'id': device['id'],
                    'hostname': device['hostname'],
                    'computer_name': device['computer_name'],
                    'ip_address': device['ip_address'],
                    'mac_address': device['mac_address'],
                    'device_status': device['device_status'],
                    'device_type': device['device_type']
                },
                'system_info': {
                    'operating_system': device['operating_system'],
                    'os_version': device['os_version'],
                    'os_build': device['os_build'],
                    'system_manufacturer': device['system_manufacturer'],
                    'system_model': device['system_model'],
                    'bios_version': device['bios_version'],
                    'serial_number': device['serial_number']
                },
                'hardware': {
                    'processor_name': device['processor_name'],
                    'processor_cores': device['processor_cores'],
                    'processor_logical_cores': device['processor_logical_cores'],
                    'total_physical_memory_gb': device['total_physical_memory_gb'],
                    'available_memory_gb': device['available_memory_gb'],
                    'storage_summary': device['storage_summary'],
                    'total_storage_gb': device['total_storage_gb'],
                    'graphics_cards': device['graphics_cards'],
                    'connected_monitors': device['connected_monitors']
                },
                'network': {
                    'ip_address': device['ip_address'],
                    'mac_address': device['mac_address'],
                    'network_adapters': device['network_adapters'],
                    'ping_response_ms': device.get('ping_response_ms')
                },
                'software': {
                    'installed_software': device['installed_software'],
                    'antivirus_software': device['antivirus_software'],
                    'firewall_status': device['firewall_status']
                },
                'users': {
                    'current_user': device['current_user'],
                    'user_profiles': device['user_profiles'],
                    'last_logged_users': device.get('last_logged_users')
                },
                'performance': {
                    'cpu_usage_percent': device.get('cpu_usage_percent'),
                    'memory_usage_percent': device.get('memory_usage_percent'),
                    'system_uptime_hours': device.get('system_uptime_hours'),
                    'data_completeness_score': device.get('data_completeness_score')
                },
                'management': {
                    'assigned_department': device['assigned_department'],
                    'location': device['location'],
                    'site': device['site'],
                    'cost_center': device['cost_center'],
                    'asset_tag': device['asset_tag'],
                    'purchase_date': device['purchase_date'],
                    'warranty_expiry': device['warranty_expiry']
                },
                'collection': {
                    'collection_method': device['collection_method'],
                    'hostname_mismatch_status': device.get('hostname_mismatch_status'),
                    'last_seen': device['last_seen'],
                    'created_at': device['created_at'],
                    'updated_at': device['updated_at']
                }
            }
            
            return jsonify(device_details)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            conn.close()

if __name__ == '__main__':
    print("Device detail endpoint module ready for integration")