# -*- coding: utf-8 -*-
"""
ENHANCED COMPLETE WEB SERVICE WITH FULL FUNCTIONALITY
===================================================
Features:
- ✅ Fixed edit functionality with working forms
- ✅ Auto-refresh every 10 seconds 
- ✅ Database status monitoring with health checks
- ✅ Asset control features (ping, port scan, status update)
- ✅ Real-time updates and live monitoring
- ✅ 100% functional asset management
"""

from flask import Flask, render_template_string, request, jsonify, redirect, url_for
import sqlite3
import logging
import ipaddress
from datetime import datetime
from typing import Dict, List, Optional
import json
import functools
import subprocess
import socket
import os

# Setup logging for web service access
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('web_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('WebService')

def log_access(f):
    """Decorator to log web service access"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'Unknown'))
        user_agent = request.headers.get('User-Agent', 'Unknown')
        logger.info(f"ACCESS: {client_ip} -> {request.method} {request.path} | UA: {user_agent[:50]}")
        return f(*args, **kwargs)
    return decorated_function

class EnhancedCompleteDepartmentWebService:
    """Enhanced web service with full functionality"""
    
    def __init__(self, db_path: str = 'assets.db'):
        self.app = Flask(__name__)
        self.db_path = db_path
        # Simple ACL - allow local network by default
        self.allowed_networks = [
            ipaddress.IPv4Network('127.0.0.0/8'),    # Localhost
            ipaddress.IPv4Network('192.168.0.0/16'), # Private networks
            ipaddress.IPv4Network('10.0.0.0/8'),
            ipaddress.IPv4Network('172.16.0.0/12')
        ]
        self.setup_routes()
        self.init_departments()
        
    def check_access(self, client_ip: str) -> bool:
        """Check if client IP is allowed"""
        try:
            client_addr = ipaddress.IPv4Address(client_ip)
            for network in self.allowed_networks:
                if client_addr in network:
                    return True
            return False
        except:
            return False  # Block invalid IPs
    
    def require_access(self, f):
        """Decorator to check access control"""
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
            if not self.check_access(client_ip):
                logger.warning(f"ACCESS DENIED: {client_ip} -> {request.path}")
                return jsonify({"error": "Access denied"}), 403
            return f(*args, **kwargs)
        return decorated_function
    
    def init_departments(self):
        """Initialize departments table if it doesn't exist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create departments table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS departments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    manager TEXT,
                    location TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Check if departments table is empty and add defaults
            cursor.execute("SELECT COUNT(*) FROM departments")
            if cursor.fetchone()[0] == 0:
                default_departments = [
                    ('IT', 'Information Technology Department', 'IT Manager', 'Building A - Floor 2'),
                    ('Finance', 'Finance and Accounting Department', 'Finance Manager', 'Building A - Floor 1'),  
                    ('HR', 'Human Resources Department', 'HR Manager', 'Building A - Floor 3'),
                    ('Operations', 'Operations Department', 'Operations Manager', 'Building B - Floor 1'),
                    ('Marketing', 'Marketing Department', 'Marketing Manager', 'Building B - Floor 2'),
                    ('Sales', 'Sales Department', 'Sales Manager', 'Building B - Floor 3'),
                    ('Engineering', 'Engineering Department', 'Engineering Manager', 'Building C - Floor 1'),
                    ('Support', 'Customer Support Department', 'Support Manager', 'Building C - Floor 2'),
                    ('Management', 'Executive Management', 'CEO', 'Building A - Floor 4'),
                    ('Unknown', 'Unassigned Department', 'N/A', 'Various')
                ]
                
                cursor.executemany('''
                    INSERT INTO departments (name, description, manager, location)
                    VALUES (?, ?, ?, ?)
                ''', default_departments)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error initializing departments: {e}")
    
    def scan_single_device(self, ip_address, username, password, scan_wmi=True, scan_ssh=False):
        """Scan a single device using WMI or SSH"""
        try:
            device_info = {
                'ip_address': ip_address,
                'hostname': 'Unknown',
                'working_user': 'N/A',
                'domain': '',
                'operating_system': 'Unknown',
                'os_version': '',
                'system_manufacturer': '',
                'system_model': '',
                'serial_number': '',
                'processor_name': '',
                'total_physical_memory': '',
                'collection_method': 'Web Discovery',
                'classification': 'Other Asset',
                'status': 'Active'
            }
            
            # Test if device is reachable first
            import subprocess
            try:
                result = subprocess.run(['ping', '-n', '1', ip_address], 
                                      capture_output=True, timeout=5)
                if result.returncode != 0:
                    return None  # Device not reachable
            except:
                return None
            
            if scan_wmi:
                # Try WMI collection
                try:
                    import wmi
                    c = wmi.WMI(computer=ip_address, user=username, password=password)
                    
                    # Get computer system info
                    for computer in c.Win32_ComputerSystem():
                        device_info['hostname'] = computer.Name or ip_address
                        device_info['working_user'] = computer.UserName or 'N/A'
                        device_info['domain'] = computer.Domain or ''
                        device_info['system_manufacturer'] = computer.Manufacturer or ''
                        device_info['system_model'] = computer.Model or ''
                        device_info['total_physical_memory'] = str(round(int(computer.TotalPhysicalMemory or 0) / (1024**3), 2)) + ' GB' if computer.TotalPhysicalMemory else ''
                        break
                    
                    # Get OS info
                    for os_info in c.Win32_OperatingSystem():
                        device_info['operating_system'] = os_info.Caption or 'Windows'
                        device_info['os_version'] = os_info.Version or ''
                        break
                    
                    # Get processor info
                    for processor in c.Win32_Processor():
                        device_info['processor_name'] = processor.Name or ''
                        break
                    
                    # Get BIOS info for serial number
                    for bios in c.Win32_BIOS():
                        device_info['serial_number'] = bios.SerialNumber or ''
                        break
                    
                    device_info['collection_method'] = 'WMI'
                    device_info['classification'] = 'Windows Workstation'
                    
                    return device_info
                    
                except Exception as wmi_error:
                    print(f"WMI failed for {ip_address}: {wmi_error}")
            
            if scan_ssh:
                # Try SSH collection (basic)
                try:
                    import paramiko
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(ip_address, username=username, password=password, timeout=10)
                    
                    # Get hostname
                    stdin, stdout, stderr = ssh.exec_command('hostname')
                    hostname = stdout.read().decode().strip()
                    if hostname:
                        device_info['hostname'] = hostname
                    
                    # Get OS info
                    stdin, stdout, stderr = ssh.exec_command('uname -a')
                    os_info = stdout.read().decode().strip()
                    if os_info:
                        device_info['operating_system'] = os_info.split()[0] + ' ' + os_info.split()[2]
                    
                    # Get current user
                    stdin, stdout, stderr = ssh.exec_command('whoami')
                    current_user = stdout.read().decode().strip()
                    if current_user:
                        device_info['working_user'] = current_user
                    
                    ssh.close()
                    device_info['collection_method'] = 'SSH'
                    device_info['classification'] = 'Linux Workstation'
                    
                    return device_info
                    
                except Exception as ssh_error:
                    print(f"SSH failed for {ip_address}: {ssh_error}")
            
            return None  # No successful connection
            
        except Exception as e:
            print(f"Error scanning {ip_address}: {e}")
            return None
    
    def setup_routes(self):
        """Setup all Flask routes"""
        
        @self.app.after_request
        def add_cache_busting_headers(response):
            """Add cache-busting headers to prevent page caching"""
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            response.headers['Last-Modified'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
            return response
        
        @self.app.route('/')
        @log_access
        @self.require_access
        def dashboard():
            """Main dashboard"""
            return render_template_string(self.get_enhanced_dashboard_template())
        
        @self.app.route('/departments')
        @log_access
        @self.require_access
        def departments_page():
            """Department management page"""
            return render_template_string(self.get_departments_template())
            
        @self.app.route('/add-asset')
        @log_access
        @self.require_access
        def add_asset_page():
            """Add asset page"""
            return render_template_string(self.get_add_asset_template())
        
        # ============ DATABASE STATUS API ============
        @self.app.route('/api/database/status')
        @log_access
        @self.require_access
        def database_status():
            """Get database connection status and health info"""
            try:
                conn = sqlite3.connect(self.db_path, timeout=5)
                cursor = conn.cursor()
                
                # Test basic connectivity
                cursor.execute('SELECT 1')
                
                # Get database info
                cursor.execute('SELECT COUNT(*) FROM assets')
                total_assets = cursor.fetchone()[0]
                
                # Get recent activity
                try:
                    cursor.execute('''
                        SELECT COUNT(*) FROM assets 
                        WHERE created_at > datetime('now', '-1 hour')
                    ''')
                    recent_additions = cursor.fetchone()[0]
                except:
                    recent_additions = 0
                
                # Get database file size
                db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
                
                conn.close()
                
                return jsonify({
                    'status': 'connected',
                    'health': 'healthy',
                    'total_assets': total_assets,
                    'recent_additions': recent_additions,
                    'database_size_mb': round(db_size / (1024*1024), 2),
                    'last_check': datetime.now().isoformat()
                })
                
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'health': 'unhealthy',
                    'error': str(e),
                    'last_check': datetime.now().isoformat()
                }), 500
        
        # ============ ASSET MANAGEMENT API ============
        @self.app.route('/api/assets/<int:asset_id>')
        @log_access
        @self.require_access
        def get_asset(asset_id):
            """Get specific asset details for editing"""
            try:
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('SELECT * FROM assets WHERE id = ?', (asset_id,))
                asset = cursor.fetchone()
                
                if not asset:
                    return jsonify({'error': 'Asset not found'}), 404
                
                # Convert Row to dict
                asset_dict = dict(asset)
                conn.close()
                
                return jsonify(asset_dict)
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/assets/<int:asset_id>', methods=['PUT'])
        @log_access
        @self.require_access
        def update_asset(asset_id):
            """Update asset information"""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'No data provided'}), 400
                
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Build dynamic UPDATE query based on provided fields
                update_fields = []
                values = []
                
                editable_fields = [
                    'hostname', 'ip_address', 'working_user', 'domain', 'classification',
                    'department', 'status', 'operating_system', 'os_version',
                    'system_manufacturer', 'system_model', 'serial_number',
                    'mac_address', 'processor_name', 'total_physical_memory',
                    'notes', 'location'
                ]
                
                for field in editable_fields:
                    if field in data:
                        update_fields.append(f'{field} = ?')
                        values.append(data[field])
                
                if not update_fields:
                    return jsonify({'error': 'No valid fields to update'}), 400
                
                values.append(asset_id)
                
                query = f'''
                    UPDATE assets 
                    SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                '''
                
                cursor.execute(query, values)
                
                if cursor.rowcount == 0:
                    return jsonify({'error': 'Asset not found'}), 404
                
                conn.commit()
                conn.close()
                
                return jsonify({'message': 'Asset updated successfully'})
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/assets/<int:asset_id>/control', methods=['POST'])
        @log_access
        @self.require_access
        def control_asset(asset_id):
            """Perform control actions on asset (ping, wake, shutdown, etc.)"""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'No action specified'}), 400
                    
                action = data.get('action')
                
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Get asset details
                cursor.execute('SELECT ip_address, hostname FROM assets WHERE id = ?', (asset_id,))
                asset = cursor.fetchone()
                
                if not asset:
                    return jsonify({'error': 'Asset not found'}), 404
                
                ip_address = asset[0]
                hostname = asset[1]
                
                result = {'action': action, 'target': ip_address, 'status': 'unknown'}
                
                if action == 'ping':
                    try:
                        # Ping the device
                        response = subprocess.run(
                            ['ping', '-n', '3', ip_address], 
                            capture_output=True, text=True, timeout=10
                        )
                        if response.returncode == 0:
                            result['status'] = 'success'
                            result['message'] = 'Device is reachable'
                        else:
                            result['status'] = 'failed'
                            result['message'] = 'Device is not reachable'
                    except Exception as e:
                        result['status'] = 'error'
                        result['message'] = str(e)
                
                elif action == 'scan_ports':
                    # Basic port scan
                    common_ports = [22, 23, 53, 80, 135, 139, 443, 445, 3389]
                    open_ports = []
                    
                    for port in common_ports:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(2)
                        try:
                            result_code = sock.connect_ex((ip_address, port))
                            if result_code == 0:
                                open_ports.append(port)
                        except:
                            pass
                        finally:
                            sock.close()
                    
                    result['status'] = 'success'
                    result['open_ports'] = open_ports
                    result['message'] = f'Found {len(open_ports)} open ports'
                
                elif action == 'update_status':
                    new_status = data.get('new_status', 'Active')
                    cursor.execute(
                        'UPDATE assets SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                        (new_status, asset_id)
                    )
                    conn.commit()
                    result['status'] = 'success'
                    result['message'] = f'Status updated to {new_status}'
                
                else:
                    result['status'] = 'error'
                    result['message'] = f'Unknown action: {action}'
                
                conn.close()
                return jsonify(result)
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/assets/<int:asset_id>', methods=['DELETE'])
        @log_access
        @self.require_access
        def delete_asset(asset_id):
            """Delete an asset"""
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM assets WHERE id = ?', (asset_id,))
                
                if cursor.rowcount == 0:
                    return jsonify({'error': 'Asset not found'}), 404
                
                conn.commit()
                conn.close()
                
                return jsonify({'message': 'Asset deleted successfully'})
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        # ============ SCANNING AND DISCOVERY API ============
        @self.app.route('/api/scan/discover', methods=['POST'])
        @log_access
        @self.require_access
        def discover_assets():
            """Scan network and discover assets using WMI/SSH"""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'No scan parameters provided'}), 400
                
                username = data.get('username')
                password = data.get('password') 
                ip_range = data.get('ip_range')
                scan_wmi = data.get('scan_wmi', True)
                scan_ssh = data.get('scan_ssh', False)
                
                if not all([username, password, ip_range]):
                    return jsonify({'error': 'Username, password, and IP range are required'}), 400
                
                # Parse IP range
                discovered_devices = []
                
                if '-' in ip_range:
                    # Range like 10.0.21.1-50
                    try:
                        base_ip, range_end = ip_range.split('-')
                        base_parts = base_ip.strip().split('.')
                        start_num = int(base_parts[3])
                        end_num = int(range_end.strip())
                        base_network = '.'.join(base_parts[:3])
                        
                        for i in range(start_num, end_num + 1):
                            ip = f"{base_network}.{i}"
                            device_info = self.scan_single_device(ip, username, password, scan_wmi, scan_ssh)
                            if device_info:
                                discovered_devices.append(device_info)
                    except Exception as e:
                        logger.error(f"Error parsing IP range: {e}")
                        return jsonify({'error': 'Invalid IP range format'}), 400
                else:
                    # Single IP
                    device_info = self.scan_single_device(ip_range.strip(), username, password, scan_wmi, scan_ssh)
                    if device_info:
                        discovered_devices.append(device_info)
                
                return jsonify({
                    'devices': discovered_devices,
                    'total_scanned': len(discovered_devices),
                    'scan_type': 'WMI+SSH' if scan_wmi and scan_ssh else ('WMI' if scan_wmi else 'SSH')
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/assets/bulk', methods=['POST'])
        @log_access
        @self.require_access
        def add_bulk_assets():
            """Add multiple assets from discovery scan"""
            try:
                data = request.get_json()
                if not data or 'devices' not in data:
                    return jsonify({'error': 'No devices provided'}), 400
                
                devices = data['devices']
                added_count = 0
                
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                for device in devices:
                    try:
                        # Check if device already exists
                        cursor.execute('SELECT id FROM assets WHERE ip_address = ?', (device.get('ip_address'),))
                        if cursor.fetchone():
                            continue  # Skip existing devices
                        
                        # Insert new device
                        cursor.execute('''
                            INSERT INTO assets (
                                hostname, ip_address, working_user, domain, classification,
                                department, status, operating_system, os_version,
                                system_manufacturer, system_model, serial_number,
                                processor_name, total_physical_memory, collection_method,
                                device_type, created_at, updated_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                        ''', (
                            device.get('hostname', 'Unknown'),
                            device.get('ip_address'),
                            device.get('working_user', 'N/A'),
                            device.get('domain', ''),
                            device.get('classification', 'Other Asset'),
                            device.get('department', 'Unknown'),
                            device.get('status', 'Active'),
                            device.get('operating_system', 'Unknown'),
                            device.get('os_version', ''),
                            device.get('system_manufacturer', ''),
                            device.get('system_model', ''),
                            device.get('serial_number', ''),
                            device.get('processor_name', ''),
                            device.get('total_physical_memory', ''),
                            device.get('collection_method', 'Web Discovery'),
                            device.get('device_type', 'Workstation')
                        ))
                        added_count += 1
                        
                    except Exception as e:
                        print(f"Error adding device {device.get('ip_address', 'unknown')}: {e}")
                        continue
                
                conn.commit()
                conn.close()
                
                return jsonify({
                    'message': f'Successfully added {added_count} devices',
                    'added_count': added_count,
                    'total_provided': len(devices)
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/assets', methods=['POST'])
        @log_access
        @self.require_access
        def add_single_asset():
            """Add a single asset manually"""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'No asset data provided'}), 400
                
                hostname = data.get('hostname', '').strip()
                ip_address = data.get('ip_address', '').strip()
                
                if not hostname or not ip_address:
                    return jsonify({'error': 'Hostname and IP address are required'}), 400
                
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Check if asset already exists
                cursor.execute('SELECT id FROM assets WHERE ip_address = ? OR hostname = ?', (ip_address, hostname))
                if cursor.fetchone():
                    return jsonify({'error': 'Asset with this IP or hostname already exists'}), 400
                
                # Insert new asset
                cursor.execute('''
                    INSERT INTO assets (
                        hostname, ip_address, working_user, domain, classification,
                        department, status, operating_system, system_manufacturer,
                        system_model, serial_number, location, notes, collection_method,
                        device_type, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ''', (
                    hostname,
                    ip_address,
                    data.get('working_user', ''),
                    data.get('domain', ''),
                    data.get('classification', 'Other Asset'),
                    data.get('department', 'Unknown'),
                    data.get('status', 'Active'),
                    data.get('operating_system', ''),
                    data.get('system_manufacturer', ''),
                    data.get('system_model', ''),
                    data.get('serial_number', ''),
                    data.get('location', ''),
                    data.get('notes', ''),
                    'Manual Entry',
                    data.get('classification', 'Other Asset')
                ))
                
                conn.commit()
                conn.close()
                
                return jsonify({'message': 'Asset added successfully'})
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        # ============ EXISTING API ENDPOINTS ============
        @self.app.route('/api/stats')
        @log_access
        @self.require_access
        def api_stats():
            """Get dashboard statistics"""
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Total assets
                cursor.execute('SELECT COUNT(*) FROM assets')
                total_assets = cursor.fetchone()[0]
                
                # Active assets
                cursor.execute("SELECT COUNT(*) FROM assets WHERE status = 'Active' OR status IS NULL")
                active_assets = cursor.fetchone()[0]
                
                # Classifications
                cursor.execute('''
                    SELECT classification, COUNT(*) 
                    FROM assets 
                    WHERE classification IS NOT NULL 
                    GROUP BY classification
                ''')
                classifications = dict(cursor.fetchall())
                
                # Departments count
                cursor.execute('SELECT COUNT(*) FROM departments')
                departments_count = cursor.fetchone()[0]
                
                conn.close()
                
                return jsonify({
                    'total_assets': total_assets,
                    'active_assets': active_assets,
                    'classifications': classifications,
                    'departments': departments_count
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/devices')
        @log_access  
        @self.require_access
        def api_devices():
            """Get devices with filtering and pagination"""
            try:
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Get query parameters
                department = request.args.get('department', '')
                classification = request.args.get('classification', '')
                status = request.args.get('status', '')
                search = request.args.get('search', '')
                
                # Build query
                where_conditions = []
                params = []
                
                if department and department != 'All Departments':
                    where_conditions.append('department = ?')
                    params.append(department)
                
                if classification and classification != 'All Classifications':
                    where_conditions.append('classification = ?')
                    params.append(classification)
                
                if status and status != 'All Statuses':
                    where_conditions.append('status = ?')
                    params.append(status)
                
                if search:
                    where_conditions.append('''
                        (hostname LIKE ? OR ip_address LIKE ? OR 
                         working_user LIKE ? OR operating_system LIKE ?)
                    ''')
                    search_param = f'%{search}%'
                    params.extend([search_param, search_param, search_param, search_param])
                
                where_clause = 'WHERE ' + ' AND '.join(where_conditions) if where_conditions else ''
                
                query = f'''
                    SELECT id, hostname, ip_address, working_user, domain, 
                           manufacturer, model, serial_number, os_name, memory_gb,
                           cpu_cores, processor_name, classification, department, 
                           status, device_type, system_manufacturer, system_model,
                           operating_system, total_physical_memory, collection_method,
                           data_source, last_updated, created_at, updated_at,
                           workgroup, timezone, bios_version, chassis_type, network_adapter,
                           graphics_card, sound_device, antivirus_software, installed_software,
                           disk_drives, motherboard, power_supply, optical_drives,
                           usb_devices, printer_devices, network_connections, installed_updates,
                           registry_info, event_logs, performance_counters, environment_variables
                    FROM assets 
                    {where_clause}
                    ORDER BY created_at DESC
                    LIMIT 100
                '''
                
                cursor.execute(query, params)
                devices = [dict(row) for row in cursor.fetchall()]
                
                conn.close()
                return jsonify(devices)
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/departments')
        @log_access
        @self.require_access
        def api_departments():
            """Get all departments"""
            try:
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT d.*, COUNT(a.id) as asset_count
                    FROM departments d
                    LEFT JOIN assets a ON d.name = a.department
                    GROUP BY d.id
                    ORDER BY d.name
                ''')
                
                departments = [dict(row) for row in cursor.fetchall()]
                conn.close()
                
                return jsonify(departments)
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        # ============ PRODUCTION DATA MANAGEMENT ============
        @self.app.route('/api/database/cleanup', methods=['POST'])
        @log_access
        @self.require_access
        def cleanup_test_data():
            """Remove test/fake data and keep only real collected devices"""
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Remove test devices (devices with test names or fake data)
                test_patterns = [
                    'test%', 'TEST%', 'queue%', 'QUEUE%', 'collector-test%', 
                    'COLLECTOR-TEST%', 'demo%', 'DEMO%', 'fake%', 'FAKE%'
                ]
                
                removed_count = 0
                for pattern in test_patterns:
                    cursor.execute('DELETE FROM assets WHERE hostname LIKE ?', (pattern,))
                    removed_count += cursor.rowcount
                
                # Also remove devices without proper collection method or with placeholder data
                cursor.execute('''
                    DELETE FROM assets WHERE 
                    collection_method IS NULL OR 
                    collection_method = '' OR
                    (working_user = 'TestWorkingUser') OR
                    (hostname LIKE '%test%' AND working_user = 'N/A')
                ''')
                removed_count += cursor.rowcount
                
                conn.commit()
                conn.close()
                
                return jsonify({
                    'message': f'Cleaned up {removed_count} test/fake devices',
                    'removed_count': removed_count
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/database/validate', methods=['POST'])
        @log_access
        @self.require_access
        def validate_device_status():
            """Validate device status by pinging all devices"""
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Get all devices
                cursor.execute('SELECT id, ip_address, status FROM assets')
                devices = cursor.fetchall()
                
                updated_count = 0
                for device_id, ip_address, current_status in devices:
                    # Ping device
                    try:
                        result = subprocess.run(['ping', '-n', '1', ip_address], 
                                              capture_output=True, timeout=5)
                        new_status = 'Active' if result.returncode == 0 else 'Inactive'
                        
                        if new_status != current_status:
                            cursor.execute('UPDATE assets SET status = ? WHERE id = ?', 
                                         (new_status, device_id))
                            updated_count += 1
                    except:
                        # If ping fails, mark as inactive
                        if current_status != 'Inactive':
                            cursor.execute('UPDATE assets SET status = ? WHERE id = ?', 
                                         ('Inactive', device_id))
                            updated_count += 1
                
                conn.commit()
                conn.close()
                
                return jsonify({
                    'message': f'Validated {len(devices)} devices, updated {updated_count} statuses',
                    'total_devices': len(devices),
                    'updated_count': updated_count
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500

    def get_enhanced_dashboard_template(self):
        """Enhanced dashboard template with all functionality"""
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏢 Enhanced Asset Management System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
        }
        .hero-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem 0;
            margin-bottom: 2rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .stat-card {
            background: white;
            border-radius: 15px;
            padding: 1.5rem;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            transition: transform 0.3s ease;
            border: 2px solid #e9ecef;
        }
        .stat-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        }
        .stat-icon {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            color: #667eea;
        }
        .stat-number {
            font-size: 2rem;
            font-weight: bold;
            color: #333;
            margin-bottom: 0.25rem;
        }
        .stat-label {
            color: #666;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .controls-section {
            background: white;
            border-radius: 15px;
            padding: 1.5rem;
            margin-bottom: 2rem;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        }
        .device-table {
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        }
        .table th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            font-weight: 600;
        }
        .btn-action {
            margin: 1px;
            padding: 0.25rem 0.5rem;
            font-size: 0.75rem;
        }
        .status-active { color: #28a745; }
        .status-inactive { color: #dc3545; }
        .status-maintenance { color: #ffc107; }
        .auto-refresh-indicator {
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 10px 15px;
            border-radius: 20px;
            font-size: 0.8rem;
            z-index: 1000;
            display: none;
        }
        .db-healthy { background-color: #d4edda !important; border-color: #c3e6cb !important; }
        .db-unhealthy { background-color: #f8d7da !important; border-color: #f5c6cb !important; }
        .db-warning { background-color: #fff3cd !important; border-color: #ffeaa7 !important; }
    </style>
</head>
<body>
    <div class="auto-refresh-indicator" id="autoRefreshIndicator">
        <i class="fas fa-sync-alt fa-spin"></i> Auto-refreshing...
    </div>

    <div class="hero-header">
        <div class="container">
            <div class="row align-items-center">
                <div class="col-md-8">
                    <h1><i class="fas fa-building"></i> Enhanced Asset Management System</h1>
                    <p class="mb-0">Enterprise Edition - Department Management & Comprehensive Asset Tracking</p>
                </div>
                <div class="col-md-4 text-end">
                    <div class="btn-group">
                        <a href="/departments" class="btn btn-light"><i class="fas fa-building"></i> Departments</a>
                        <a href="/add-asset" class="btn btn-success"><i class="fas fa-plus"></i> Add Asset</a>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="container-fluid">
        <!-- Statistics Cards -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="stat-card">
                    <div class="stat-icon">📊</div>
                    <div class="stat-number" id="totalAssets">0</div>
                    <div class="stat-label">Total Assets</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card">
                    <div class="stat-icon">✅</div>
                    <div class="stat-number" id="activeAssets">0</div>
                    <div class="stat-label">Active Assets</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card">
                    <div class="stat-icon">🏢</div>
                    <div class="stat-number" id="departmentsCount">0</div>
                    <div class="stat-label">Departments</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card" id="databaseStatusCard">
                    <div class="stat-icon">🗄️</div>
                    <div class="stat-number" id="databaseStatus">⚠️</div>
                    <div class="stat-label">Database Status</div>
                </div>
            </div>
        </div>

        <!-- Controls Section -->
        <div class="controls-section">
            <div class="row align-items-center">
                <div class="col-md-6">
                    <div class="row">
                        <div class="col-md-6">
                            <input type="text" class="form-control" id="searchInput" placeholder="🔍 Search assets...">
                        </div>
                        <div class="col-md-3">
                            <select class="form-select" id="departmentFilter">
                                <option value="">🏢 All Departments</option>
                            </select>
                        </div>
                        <div class="col-md-3">
                            <select class="form-select" id="statusFilter">
                                <option value="">♾️ All Statuses</option>
                                <option value="Active">✅ Active</option>
                                <option value="Inactive">❌ Inactive</option>
                                <option value="Maintenance">🔧 Maintenance</option>
                            </select>
                        </div>
                    </div>
                </div>
                <div class="col-md-6 text-end">
                    <div class="btn-group me-2">
                        <button class="btn btn-warning" onclick="cleanupTestData()" title="Remove test/fake data">
                            <i class="fas fa-broom"></i> Cleanup
                        </button>
                        <button class="btn btn-info" onclick="validateDeviceStatus()" title="Ping all devices to validate status">
                            <i class="fas fa-heartbeat"></i> Validate
                        </button>
                    </div>
                    <div class="btn-group">
                        <button class="btn btn-outline-secondary" onclick="refreshData()">
                            <i class="fas fa-sync-alt"></i> Refresh
                        </button>
                        <button class="btn btn-success" onclick="toggleView()" id="viewToggle">
                            <i class="fas fa-th-list"></i> Detailed View
                        </button>
                    </div>
                    <small class="text-muted d-block mt-1">
                        <i class="fas fa-clock"></i> Auto-refresh: 10s
                    </small>
                </div>
            </div>
        </div>

        <!-- Assets Table -->
        <div class="device-table">
            <div class="table-responsive">
                <table class="table table-hover mb-0">
                    <thead>
                        <tr id="tableHeaders">
                            <th>DEVICE INFO</th>
                            <th>USER & DOMAIN</th>
                            <th>NETWORK</th>
                            <th>CLASSIFICATION</th>
                            <th>DEPARTMENT</th>
                            <th>HARDWARE</th>
                            <th>SYSTEM</th>
                            <th>STATUS</th>
                            <th>ACTIONS</th>
                        </tr>
                    </thead>
                    <tbody id="devicesTableBody">
                        <tr>
                            <td colspan="9" class="text-center py-4">
                                <div class="spinner-border" role="status"></div>
                                <p class="mt-2">Loading devices...</p>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // ============ INITIALIZATION ============
        let detailedView = false;
        
        document.addEventListener('DOMContentLoaded', function() {
            loadStats();
            loadDevices();
            loadDepartments();
            loadDatabaseStatus();
            
            // Setup auto-refresh every 10 seconds
            setInterval(function() {
                showAutoRefreshIndicator();
                refreshData();
                loadDatabaseStatus();
            }, 10000);
            
            // Setup search and filter event listeners
            document.getElementById('searchInput').addEventListener('input', debounce(loadDevices, 500));
            document.getElementById('departmentFilter').addEventListener('change', loadDevices);
            document.getElementById('statusFilter').addEventListener('change', loadDevices);
        });
        
        // ============ UTILITY FUNCTIONS ============
        function debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        }
        
        function showAutoRefreshIndicator() {
            const indicator = document.getElementById('autoRefreshIndicator');
            indicator.style.display = 'block';
            setTimeout(() => {
                indicator.style.display = 'none';
            }, 2000);
        }
        
        // ============ DATA LOADING FUNCTIONS ============
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const stats = await response.json();
                
                document.getElementById('totalAssets').textContent = stats.total_assets;
                document.getElementById('activeAssets').textContent = stats.active_assets;
                document.getElementById('departmentsCount').textContent = stats.departments;
                
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }
        
        async function loadDatabaseStatus() {
            try {
                const response = await fetch('/api/database/status');
                const status = await response.json();
                
                const statusCard = document.getElementById('databaseStatusCard');
                const statusElement = document.getElementById('databaseStatus');
                
                // Remove existing classes
                statusCard.classList.remove('db-healthy', 'db-unhealthy', 'db-warning');
                
                if (status.status === 'connected' && status.health === 'healthy') {
                    statusElement.innerHTML = '✅';
                    statusCard.classList.add('db-healthy');
                    statusCard.title = `Database: ${status.total_assets} assets, ${status.database_size_mb}MB`;
                } else {
                    statusElement.innerHTML = '❌';
                    statusCard.classList.add('db-unhealthy');
                    statusCard.title = `Database Error: ${status.error || 'Unknown error'}`;
                }
                
            } catch (error) {
                const statusElement = document.getElementById('databaseStatus');
                const statusCard = document.getElementById('databaseStatusCard');
                statusElement.innerHTML = '⚠️';
                statusCard.classList.remove('db-healthy', 'db-unhealthy');
                statusCard.classList.add('db-warning');
                statusCard.title = `Connection Error: ${error.message}`;
            }
        }
        
        async function loadDevices() {
            try {
                const params = new URLSearchParams({
                    search: document.getElementById('searchInput').value,
                    department: document.getElementById('departmentFilter').value,
                    status: document.getElementById('statusFilter').value
                });
                
                const response = await fetch(`/api/devices?${params}`);
                const devices = await response.json();
                
                displayDevices(devices);
                
            } catch (error) {
                console.error('Error loading devices:', error);
                document.getElementById('devicesTableBody').innerHTML = 
                    '<tr><td colspan="9" class="text-center text-danger">Error loading devices</td></tr>';
            }
        }
        
        async function loadDepartments() {
            try {
                const response = await fetch('/api/departments');
                const departments = await response.json();
                
                const select = document.getElementById('departmentFilter');
                const currentValue = select.value;
                
                select.innerHTML = '<option value="">🏢 All Departments</option>';
                departments.forEach(dept => {
                    const option = document.createElement('option');
                    option.value = dept.name;
                    option.textContent = `${dept.name} (${dept.asset_count || 0})`;
                    select.appendChild(option);
                });
                
                select.value = currentValue;
                
            } catch (error) {
                console.error('Error loading departments:', error);
            }
        }
        
        // ============ DISPLAY FUNCTIONS ============
        function displayDevices(devices) {
            const tbody = document.getElementById('devicesTableBody');
            
            if (devices.length === 0) {
                tbody.innerHTML = '<tr><td colspan="9" class="text-center">No devices found matching criteria</td></tr>';
                return;
            }
            
            if (detailedView) {
                displayDetailedDevices(devices);
            } else {
                displaySimpleDevices(devices);
            }
        }
        
        function displaySimpleDevices(devices) {
            const tbody = document.getElementById('devicesTableBody');
            
            tbody.innerHTML = devices.map(device => `
                <tr>
                    <td>
                        <strong>${device.hostname || device.ip_address || 'Unknown'}</strong><br>
                        <small class="text-muted">ID: ${device.id}</small>
                    </td>
                    <td>
                        ${device.working_user || 'N/A'}<br>
                        <small class="text-muted">${device.domain || device.workgroup || 'No Domain'}</small>
                    </td>
                    <td>
                        <span class="badge bg-primary">${device.ip_address || 'Unknown'}</span>
                    </td>
                    <td>
                        <span class="badge bg-info">${device.classification || device.device_type || 'Other Asset'}</span>
                    </td>
                    <td>
                        <span class="badge bg-secondary">${device.department || 'Unknown'}</span>
                    </td>
                    <td>
                        ${device.manufacturer || device.system_manufacturer || 'Unknown'}<br>
                        <small class="text-muted">${device.model || device.system_model || 'Unknown'}</small>
                    </td>
                    <td>
                        ${device.os_name || device.operating_system || 'Unknown'}<br>
                        <small class="text-muted">${device.memory_gb ? device.memory_gb + ' GB RAM' : 'Unknown RAM'}</small>
                    </td>
                    <td>
                        <span class="badge ${getStatusClass(device.status)}">${device.status || 'Unknown'}</span><br>
                        <small class="text-muted">${device.data_source || device.collection_method || 'N/A'}</small>
                    </td>
                    <td>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-primary btn-action" onclick="editDevice(${device.id})" title="Edit Device">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-success btn-action" onclick="controlDevice(${device.id}, 'ping')" title="Ping Device">
                                <i class="fas fa-wifi"></i>
                            </button>
                            <button class="btn btn-info btn-action" onclick="controlDevice(${device.id}, 'scan_ports')" title="Scan Ports">
                                <i class="fas fa-search"></i>
                            </button>
                            <button class="btn btn-danger btn-action" onclick="deleteDevice(${device.id})" title="Delete Device">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `).join('');
        }
        
        function displayDetailedDevices(devices) {
            const tbody = document.getElementById('devicesTableBody');
            const headers = document.getElementById('tableHeaders');
            
            // Update headers for detailed view
            headers.innerHTML = `
                <th>ID</th><th>HOSTNAME</th><th>IP ADDRESS</th><th>USER</th><th>DOMAIN</th>
                <th>OS</th><th>MANUFACTURER</th><th>MODEL</th><th>SERIAL</th><th>MEMORY</th>
                <th>PROCESSOR</th><th>DEPARTMENT</th><th>CLASSIFICATION</th><th>STATUS</th>
                <th>COLLECTION</th><th>CREATED</th><th>ACTIONS</th>
            `;
            
            tbody.innerHTML = devices.map(device => `
                <tr>
                    <td><small>${device.id}</small></td>
                    <td><strong>${device.hostname || device.ip_address || 'Unknown'}</strong></td>
                    <td><span class="badge bg-primary">${device.ip_address || 'Unknown'}</span></td>
                    <td>${device.working_user || 'N/A'}</td>
                    <td>${device.domain || device.workgroup || 'N/A'}</td>
                    <td><small>${device.os_name || device.operating_system || 'Unknown'}</small></td>
                    <td><small>${device.manufacturer || device.system_manufacturer || 'Unknown'}</small></td>
                    <td><small>${device.model || device.system_model || 'Unknown'}</small></td>
                    <td><small>${device.serial_number || 'N/A'}</small></td>
                    <td><small>${device.memory_gb ? device.memory_gb + ' GB' : device.total_physical_memory || 'N/A'}</small></td>
                    <td><small>${device.processor_name || 'N/A'}</small></td>
                    <td><span class="badge bg-secondary">${device.department || 'Unknown'}</span></td>
                    <td><span class="badge bg-info">${device.classification || device.device_type || 'Other Asset'}</span></td>
                    <td><span class="badge ${getStatusClass(device.status)}">${device.status || 'Unknown'}</span></td>
                    <td><small>${device.data_source || device.collection_method || 'N/A'}</small></td>
                    <td><small>${device.created_at ? new Date(device.created_at).toLocaleDateString() : 'N/A'}</small></td>
                    <td>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-primary btn-action" onclick="editDevice(${device.id})" title="Edit">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-success btn-action" onclick="controlDevice(${device.id}, 'ping')" title="Ping">
                                <i class="fas fa-wifi"></i>
                            </button>
                            <button class="btn btn-danger btn-action" onclick="deleteDevice(${device.id})" title="Delete">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `).join('');
        }
        
        function toggleView() {
            detailedView = !detailedView;
            const button = document.getElementById('viewToggle');
            
            if (detailedView) {
                button.innerHTML = '<i class="fas fa-th"></i> Simple View';
                button.classList.remove('btn-success');
                button.classList.add('btn-warning');
            } else {
                button.innerHTML = '<i class="fas fa-th-list"></i> Detailed View';
                button.classList.remove('btn-warning');
                button.classList.add('btn-success');
                
                // Reset headers
                document.getElementById('tableHeaders').innerHTML = `
                    <th>DEVICE INFO</th>
                    <th>USER & DOMAIN</th>
                    <th>NETWORK</th>
                    <th>CLASSIFICATION</th>
                    <th>DEPARTMENT</th>
                    <th>HARDWARE</th>
                    <th>SYSTEM</th>
                    <th>STATUS</th>
                    <th>ACTIONS</th>
                `;
            }
            
            loadDevices(); // Reload with new view
        }
        
        function getStatusClass(status) {
            switch(status) {
                case 'Active': return 'bg-success';
                case 'Inactive': return 'bg-danger';
                case 'Maintenance': return 'bg-warning';
                default: return 'bg-secondary';
            }
        }
        
        // ============ DEVICE MANAGEMENT FUNCTIONS ============
        async function editDevice(id) {
            try {
                // Get device details
                const response = await fetch(`/api/assets/${id}`);
                if (!response.ok) {
                    throw new Error('Failed to load device details');
                }
                
                const device = await response.json();
                
                // Create edit modal HTML
                const modalHtml = `
                    <div class="modal fade" id="editDeviceModal" tabindex="-1">
                        <div class="modal-dialog modal-lg">
                            <div class="modal-content">
                                <div class="modal-header">
                                    <h5 class="modal-title">✏️ Edit Device: ${device.hostname || 'Unknown'}</h5>
                                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                                </div>
                                <div class="modal-body">
                                    <form id="editDeviceForm">
                                        <div class="row">
                                            <div class="col-md-6">
                                                <div class="mb-3">
                                                    <label class="form-label">Hostname</label>
                                                    <input type="text" class="form-control" id="edit_hostname" value="${device.hostname || ''}">
                                                </div>
                                                <div class="mb-3">
                                                    <label class="form-label">IP Address</label>
                                                    <input type="text" class="form-control" id="edit_ip_address" value="${device.ip_address || ''}">
                                                </div>
                                                <div class="mb-3">
                                                    <label class="form-label">Working User</label>
                                                    <input type="text" class="form-control" id="edit_working_user" value="${device.working_user || ''}">
                                                </div>
                                                <div class="mb-3">
                                                    <label class="form-label">Domain</label>
                                                    <input type="text" class="form-control" id="edit_domain" value="${device.domain || ''}">
                                                </div>
                                                <div class="mb-3">
                                                    <label class="form-label">Classification</label>
                                                    <select class="form-select" id="edit_classification">
                                                        <option value="Windows Workstation" ${device.classification === 'Windows Workstation' ? 'selected' : ''}>Windows Workstation</option>
                                                        <option value="Windows Server" ${device.classification === 'Windows Server' ? 'selected' : ''}>Windows Server</option>
                                                        <option value="Linux Workstation" ${device.classification === 'Linux Workstation' ? 'selected' : ''}>Linux Workstation</option>
                                                        <option value="Linux Server" ${device.classification === 'Linux Server' ? 'selected' : ''}>Linux Server</option>
                                                        <option value="Network Device" ${device.classification === 'Network Device' ? 'selected' : ''}>Network Device</option>
                                                        <option value="Other Asset" ${device.classification === 'Other Asset' ? 'selected' : ''}>Other Asset</option>
                                                    </select>
                                                </div>
                                                <div class="mb-3">
                                                    <label class="form-label">Status</label>
                                                    <select class="form-select" id="edit_status">
                                                        <option value="Active" ${device.status === 'Active' ? 'selected' : ''}>Active</option>
                                                        <option value="Inactive" ${device.status === 'Inactive' ? 'selected' : ''}>Inactive</option>
                                                        <option value="Maintenance" ${device.status === 'Maintenance' ? 'selected' : ''}>Maintenance</option>
                                                    </select>
                                                </div>
                                            </div>
                                            <div class="col-md-6">
                                                <div class="mb-3">
                                                    <label class="form-label">Operating System</label>
                                                    <input type="text" class="form-control" id="edit_operating_system" value="${device.operating_system || ''}">
                                                </div>
                                                <div class="mb-3">
                                                    <label class="form-label">System Manufacturer</label>
                                                    <input type="text" class="form-control" id="edit_system_manufacturer" value="${device.system_manufacturer || ''}">
                                                </div>
                                                <div class="mb-3">
                                                    <label class="form-label">System Model</label>
                                                    <input type="text" class="form-control" id="edit_system_model" value="${device.system_model || ''}">
                                                </div>
                                                <div class="mb-3">
                                                    <label class="form-label">Serial Number</label>
                                                    <input type="text" class="form-control" id="edit_serial_number" value="${device.serial_number || ''}">
                                                </div>
                                                <div class="mb-3">
                                                    <label class="form-label">Location</label>
                                                    <input type="text" class="form-control" id="edit_location" value="${device.location || ''}">
                                                </div>
                                                <div class="mb-3">
                                                    <label class="form-label">Notes</label>
                                                    <textarea class="form-control" id="edit_notes" rows="3">${device.notes || ''}</textarea>
                                                </div>
                                            </div>
                                        </div>
                                    </form>
                                </div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                                    <button type="button" class="btn btn-primary" onclick="saveDeviceEdit(${id})">💾 Save Changes</button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                
                // Remove existing modal if any
                const existingModal = document.getElementById('editDeviceModal');
                if (existingModal) {
                    existingModal.remove();
                }
                
                // Add modal to page
                document.body.insertAdjacentHTML('beforeend', modalHtml);
                
                // Show modal
                const modal = new bootstrap.Modal(document.getElementById('editDeviceModal'));
                modal.show();
                
            } catch (error) {
                alert(`Error loading device details: ${error.message}`);
            }
        }
        
        async function saveDeviceEdit(id) {
            try {
                const data = {
                    hostname: document.getElementById('edit_hostname').value,
                    ip_address: document.getElementById('edit_ip_address').value,
                    working_user: document.getElementById('edit_working_user').value,
                    domain: document.getElementById('edit_domain').value,
                    classification: document.getElementById('edit_classification').value,
                    status: document.getElementById('edit_status').value,
                    operating_system: document.getElementById('edit_operating_system').value,
                    system_manufacturer: document.getElementById('edit_system_manufacturer').value,
                    system_model: document.getElementById('edit_system_model').value,
                    serial_number: document.getElementById('edit_serial_number').value,
                    location: document.getElementById('edit_location').value,
                    notes: document.getElementById('edit_notes').value
                };
                
                const response = await fetch(`/api/assets/${id}`, {
                    method: 'PUT',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                
                if (response.ok) {
                    // Close modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('editDeviceModal'));
                    modal.hide();
                    
                    // Refresh data
                    refreshData();
                    alert('✅ Device updated successfully!');
                } else {
                    const error = await response.json();
                    alert(`❌ Error: ${error.error}`);
                }
                
            } catch (error) {
                alert(`❌ Error saving changes: ${error.message}`);
            }
        }
        
        async function controlDevice(id, action) {
            try {
                const response = await fetch(`/api/assets/${id}/control`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({action: action})
                });
                
                const result = await response.json();
                
                if (result.status === 'success') {
                    let message = `✅ ${action.toUpperCase()}: ${result.message}`;
                    if (result.open_ports) {
                        message += `\\nOpen ports: ${result.open_ports.join(', ')}`;
                    }
                    alert(message);
                } else {
                    alert(`❌ ${action.toUpperCase()} failed: ${result.message}`);
                }
                
                // Refresh devices if status was updated
                if (action === 'update_status') {
                    refreshData();
                }
                
            } catch (error) {
                alert(`❌ Error performing ${action}: ${error.message}`);
            }
        }
        
        async function deleteDevice(id) {
            if (confirm('Are you sure you want to delete this device?')) {
                try {
                    const response = await fetch(`/api/assets/${id}`, {
                        method: 'DELETE'
                    });
                    
                    if (response.ok) {
                        refreshData();
                        alert('✅ Device deleted successfully');
                    } else {
                        const error = await response.json();
                        alert(`❌ Error: ${error.error}`);
                    }
                } catch (error) {
                    alert(`❌ Error deleting device: ${error}`);
                }
            }
        }
        
        // ============ OTHER FUNCTIONS ============
        async function cleanupTestData() {
            if (!confirm('This will remove all test/fake devices from the database. Continue?')) {
                return;
            }
            
            try {
                const response = await fetch('/api/database/cleanup', {
                    method: 'POST'
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    alert(`✅ Cleanup completed: ${result.removed_count} test devices removed`);
                    refreshData();
                } else {
                    alert(`❌ Cleanup failed: ${result.error}`);
                }
                
            } catch (error) {
                alert(`❌ Error during cleanup: ${error.message}`);
            }
        }
        
        async function validateDeviceStatus() {
            if (!confirm('This will ping all devices to validate their status. This may take some time. Continue?')) {
                return;
            }
            
            const button = event.target;
            const originalText = button.innerHTML;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Validating...';
            button.disabled = true;
            
            try {
                const response = await fetch('/api/database/validate', {
                    method: 'POST'
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    alert(`✅ Validation completed: ${result.updated_count} devices updated out of ${result.total_devices} total`);
                    refreshData();
                } else {
                    alert(`❌ Validation failed: ${result.error}`);
                }
                
            } catch (error) {
                alert(`❌ Error during validation: ${error.message}`);
            } finally {
                button.innerHTML = originalText;
                button.disabled = false;
            }
        }
        
        function refreshData() {
            loadStats();
            loadDevices();
            loadDepartments();
        }
        
        function exportData() {
            // Enhanced export with more fields
            const devices = Array.from(document.querySelectorAll('#devicesTableBody tr')).map(row => {
                const cells = row.querySelectorAll('td');
                if (cells.length < 8) return null;
                
                if (detailedView) {
                    return {
                        id: cells[0].textContent.trim(),
                        hostname: cells[1].textContent.trim(),
                        ip_address: cells[2].textContent.trim(),
                        working_user: cells[3].textContent.trim(),
                        domain: cells[4].textContent.trim(),
                        operating_system: cells[5].textContent.trim(),
                        manufacturer: cells[6].textContent.trim(),
                        model: cells[7].textContent.trim(),
                        serial_number: cells[8].textContent.trim(),
                        memory: cells[9].textContent.trim(),
                        processor: cells[10].textContent.trim(),
                        department: cells[11].textContent.trim(),
                        classification: cells[12].textContent.trim(),
                        status: cells[13].textContent.trim(),
                        collection_method: cells[14].textContent.trim(),
                        created_at: cells[15].textContent.trim()
                    };
                } else {
                    return {
                        hostname: cells[0].textContent.split('\\n')[0].trim(),
                        user: cells[1].textContent.split('\\n')[0].trim(),
                        ip: cells[2].textContent.trim(),
                        classification: cells[3].textContent.trim(),
                        department: cells[4].textContent.trim(),
                        hardware: cells[5].textContent.split('\\n')[0].trim(),
                        system: cells[6].textContent.trim(),
                        status: cells[7].textContent.trim()
                    };
                }
            }).filter(device => device !== null);
            
            let csv;
            if (detailedView) {
                csv = [
                    'ID,Hostname,IP Address,Working User,Domain,Operating System,Manufacturer,Model,Serial Number,Memory,Processor,Department,Classification,Status,Collection Method,Created At',
                    ...devices.map(d => `"${d.id}","${d.hostname}","${d.ip_address}","${d.working_user}","${d.domain}","${d.operating_system}","${d.manufacturer}","${d.model}","${d.serial_number}","${d.memory}","${d.processor}","${d.department}","${d.classification}","${d.status}","${d.collection_method}","${d.created_at}"`)
                ].join('\\n');
            } else {
                csv = [
                    'Hostname,User,IP Address,Classification,Department,Hardware,System,Status',
                    ...devices.map(d => `"${d.hostname}","${d.user}","${d.ip}","${d.classification}","${d.department}","${d.hardware}","${d.system}","${d.status}"`)
                ].join('\\n');
            }
            
            const blob = new Blob([csv], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `assets_export_${new Date().toISOString().split('T')[0]}.csv`;
            a.click();
            window.URL.revokeObjectURL(url);
        }
    </script>
</body>
</html>
        '''

    def get_departments_template(self):
        """Keep existing departments template"""
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏢 Department Management</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
        }
        .hero-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem 0;
            margin-bottom: 2rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>
    <div class="hero-header">
        <div class="container">
            <div class="row align-items-center">
                <div class="col-md-8">
                    <h1><i class="fas fa-building"></i> Department Management</h1>
                    <p class="mb-0">Manage departments and assign devices</p>
                </div>
                <div class="col-md-4 text-end">
                    <a href="/" class="btn btn-light"><i class="fas fa-home"></i> Dashboard</a>
                </div>
            </div>
        </div>
    </div>
    <div class="container">
        <p>Department management functionality is available through the main dashboard.</p>
    </div>
</body>
</html>
        '''

    def get_add_asset_template(self):
        """Professional Add Asset template with full functionality"""
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>➕ Add New Asset - Production System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
        }
        .hero-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem 0;
            margin-bottom: 2rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .form-card {
            background: white;
            border-radius: 15px;
            padding: 2rem;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            margin-bottom: 2rem;
        }
        .section-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 10px 10px 0 0;
            margin: -2rem -2rem 1.5rem -2rem;
        }
        .scan-section {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        }
        .manual-section {
            background: linear-gradient(135deg, #007bff 0%, #6610f2 100%);
        }
        .btn-scan {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            border: none;
            color: white;
            padding: 0.75rem 2rem;
            border-radius: 25px;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        .btn-scan:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(40, 167, 69, 0.3);
            color: white;
        }
        .credential-form {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 1.5rem;
            margin: 1rem 0;
        }
        .scan-progress {
            display: none;
            margin: 1rem 0;
        }
        .scan-results {
            display: none;
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid #dee2e6;
            border-radius: 10px;
            padding: 1rem;
            margin: 1rem 0;
        }
        .device-result {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem 0;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .device-result:hover {
            background: #e9ecef;
            border-color: #007bff;
        }
        .device-result.selected {
            background: #d4edda;
            border-color: #28a745;
        }
    </style>
</head>
<body>
    <div class="hero-header">
        <div class="container">
            <div class="row align-items-center">
                <div class="col-md-8">
                    <h1><i class="fas fa-plus-circle"></i> Add New Asset</h1>
                    <p class="mb-0">Professional Asset Discovery & Manual Addition System</p>
                </div>
                <div class="col-md-4 text-end">
                    <a href="/" class="btn btn-light btn-lg"><i class="fas fa-home"></i> Back to Dashboard</a>
                </div>
            </div>
        </div>
    </div>

    <div class="container">
        <div class="row">
            <!-- Scan & Discover Section -->
            <div class="col-lg-6">
                <div class="form-card">
                    <div class="section-header scan-section">
                        <h4><i class="fas fa-radar"></i> Smart Discovery & Scan</h4>
                        <p class="mb-0">Automatically discover and collect device information</p>
                    </div>
                    
                    <div class="credential-form">
                        <h6><i class="fas fa-key"></i> WMI/SSH Credentials</h6>
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Username</label>
                                    <input type="text" class="form-control" id="scan_username" placeholder="domain\\username">
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Password</label>
                                    <input type="password" class="form-control" id="scan_password">
                                </div>
                            </div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">IP Range/Single IP</label>
                            <input type="text" class="form-control" id="scan_range" placeholder="10.0.21.1-50 or 10.0.21.47" value="10.0.21.1-50">
                        </div>
                        <div class="row">
                            <div class="col-md-6">
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="scan_wmi" checked>
                                    <label class="form-check-label" for="scan_wmi">
                                        <i class="fab fa-windows"></i> WMI Scan (Windows)
                                    </label>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="scan_ssh">
                                    <label class="form-check-label" for="scan_ssh">
                                        <i class="fab fa-linux"></i> SSH Scan (Linux)
                                    </label>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="text-center">
                        <button class="btn btn-scan btn-lg" onclick="startDiscoveryScan()">
                            <i class="fas fa-search"></i> Start Smart Discovery
                        </button>
                    </div>
                    
                    <div class="scan-progress" id="scanProgress">
                        <div class="d-flex align-items-center">
                            <div class="spinner-border text-success me-3" role="status"></div>
                            <div>
                                <strong>Scanning Network...</strong><br>
                                <span id="scanStatus">Initializing scan...</span>
                            </div>
                        </div>
                        <div class="progress mt-3">
                            <div class="progress-bar bg-success" role="progressbar" style="width: 0%" id="scanProgressBar"></div>
                        </div>
                    </div>
                    
                    <div class="scan-results" id="scanResults">
                        <h6><i class="fas fa-list"></i> Discovered Devices (Click to select):</h6>
                        <div id="discoveredDevices"></div>
                        <div class="text-center mt-3">
                            <button class="btn btn-success" onclick="addSelectedDevices()">
                                <i class="fas fa-plus"></i> Add Selected Devices
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Manual Addition Section -->
            <div class="col-lg-6">
                <div class="form-card">
                    <div class="section-header manual-section">
                        <h4><i class="fas fa-edit"></i> Manual Asset Addition</h4>
                        <p class="mb-0">Add device information manually</p>
                    </div>
                    
                    <form id="manualAssetForm">
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Hostname *</label>
                                    <input type="text" class="form-control" id="manual_hostname" required>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">IP Address *</label>
                                    <input type="text" class="form-control" id="manual_ip_address" required>
                                </div>
                            </div>
                        </div>
                        
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Working User</label>
                                    <input type="text" class="form-control" id="manual_working_user">
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Domain</label>
                                    <input type="text" class="form-control" id="manual_domain">
                                </div>
                            </div>
                        </div>
                        
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Classification</label>
                                    <select class="form-select" id="manual_classification">
                                        <option value="Windows Workstation">Windows Workstation</option>
                                        <option value="Windows Server">Windows Server</option>
                                        <option value="Linux Workstation">Linux Workstation</option>
                                        <option value="Linux Server">Linux Server</option>
                                        <option value="Network Device">Network Device</option>
                                        <option value="Other Asset">Other Asset</option>
                                    </select>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Department</label>
                                    <select class="form-select" id="manual_department">
                                        <option value="">Loading departments...</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                        
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Operating System</label>
                                    <input type="text" class="form-control" id="manual_operating_system">
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Status</label>
                                    <select class="form-select" id="manual_status">
                                        <option value="Active">Active</option>
                                        <option value="Inactive">Inactive</option>
                                        <option value="Maintenance">Maintenance</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                        
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Manufacturer</label>
                                    <input type="text" class="form-control" id="manual_manufacturer">
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Model</label>
                                    <input type="text" class="form-control" id="manual_model">
                                </div>
                            </div>
                        </div>
                        
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Serial Number</label>
                                    <input type="text" class="form-control" id="manual_serial_number">
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Location</label>
                                    <input type="text" class="form-control" id="manual_location">
                                </div>
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label">Notes</label>
                            <textarea class="form-control" id="manual_notes" rows="3"></textarea>
                        </div>
                        
                        <div class="text-center">
                            <button type="button" class="btn btn-secondary me-2" onclick="window.location.href='/'">Cancel</button>
                            <button type="submit" class="btn btn-primary btn-lg">
                                <i class="fas fa-save"></i> Add Asset Manually
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let discoveredDevicesData = [];
        let selectedDevices = [];
        
        document.addEventListener('DOMContentLoaded', loadDepartments);

        async function loadDepartments() {
            try {
                const response = await fetch('/api/departments');
                const departments = await response.json();
                
                const select = document.getElementById('manual_department');
                select.innerHTML = '<option value="">Select Department</option>';
                
                departments.forEach(dept => {
                    const option = document.createElement('option');
                    option.value = dept.name;
                    option.textContent = dept.name;
                    select.appendChild(option);
                });
            } catch (error) {
                console.error('Error loading departments:', error);
            }
        }

        async function startDiscoveryScan() {
            const username = document.getElementById('scan_username').value;
            const password = document.getElementById('scan_password').value;
            const range = document.getElementById('scan_range').value;
            const wmi = document.getElementById('scan_wmi').checked;
            const ssh = document.getElementById('scan_ssh').checked;
            
            if (!username || !password || !range) {
                alert('Please fill in credentials and IP range');
                return;
            }
            
            // Show progress
            document.getElementById('scanProgress').style.display = 'block';
            document.getElementById('scanResults').style.display = 'none';
            
            try {
                const response = await fetch('/api/scan/discover', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        username: username,
                        password: password,
                        ip_range: range,
                        scan_wmi: wmi,
                        scan_ssh: ssh
                    })
                });
                
                if (response.ok) {
                    const result = await response.json();
                    displayScanResults(result.devices || []);
                } else {
                    const error = await response.json();
                    alert(`Scan failed: ${error.error}`);
                    document.getElementById('scanProgress').style.display = 'none';
                }
                
            } catch (error) {
                alert(`Error starting scan: ${error.message}`);
                document.getElementById('scanProgress').style.display = 'none';
            }
        }
        
        function displayScanResults(devices) {
            document.getElementById('scanProgress').style.display = 'none';
            document.getElementById('scanResults').style.display = 'block';
            
            discoveredDevicesData = devices;
            const container = document.getElementById('discoveredDevices');
            
            if (devices.length === 0) {
                container.innerHTML = '<div class="text-center text-muted">No devices discovered</div>';
                return;
            }
            
            container.innerHTML = devices.map((device, index) => `
                <div class="device-result" onclick="toggleDeviceSelection(${index})">
                    <div class="row">
                        <div class="col-md-8">
                            <h6><i class="fas fa-desktop"></i> ${device.hostname || device.ip_address}</h6>
                            <small class="text-muted">
                                IP: ${device.ip_address} | 
                                OS: ${device.operating_system || 'Unknown'} |
                                User: ${device.working_user || 'N/A'}
                            </small>
                        </div>
                        <div class="col-md-4 text-end">
                            <span class="badge bg-success" id="select-badge-${index}">Click to Select</span>
                        </div>
                    </div>
                </div>
            `).join('');
        }
        
        function toggleDeviceSelection(index) {
            const deviceElement = document.querySelectorAll('.device-result')[index];
            const badge = document.getElementById(`select-badge-${index}`);
            
            if (selectedDevices.includes(index)) {
                selectedDevices = selectedDevices.filter(i => i !== index);
                deviceElement.classList.remove('selected');
                badge.textContent = 'Click to Select';
                badge.className = 'badge bg-success';
            } else {
                selectedDevices.push(index);
                deviceElement.classList.add('selected');
                badge.textContent = 'Selected';
                badge.className = 'badge bg-primary';
            }
        }
        
        async function addSelectedDevices() {
            if (selectedDevices.length === 0) {
                alert('Please select at least one device');
                return;
            }
            
            const devicesToAdd = selectedDevices.map(index => discoveredDevicesData[index]);
            
            try {
                const response = await fetch('/api/assets/bulk', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({devices: devicesToAdd})
                });
                
                if (response.ok) {
                    const result = await response.json();
                    alert(`✅ Successfully added ${result.added_count} devices!`);
                    window.location.href = '/';
                } else {
                    const error = await response.json();
                    alert(`❌ Error: ${error.error}`);
                }
                
            } catch (error) {
                alert(`❌ Error adding devices: ${error.message}`);
            }
        }

        document.getElementById('manualAssetForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = {
                hostname: document.getElementById('manual_hostname').value,
                ip_address: document.getElementById('manual_ip_address').value,
                working_user: document.getElementById('manual_working_user').value,
                domain: document.getElementById('manual_domain').value,
                classification: document.getElementById('manual_classification').value,
                department: document.getElementById('manual_department').value,
                status: document.getElementById('manual_status').value,
                operating_system: document.getElementById('manual_operating_system').value,
                system_manufacturer: document.getElementById('manual_manufacturer').value,
                system_model: document.getElementById('manual_model').value,
                serial_number: document.getElementById('manual_serial_number').value,
                location: document.getElementById('manual_location').value,
                notes: document.getElementById('manual_notes').value
            };

            try {
                const response = await fetch('/api/assets', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(formData)
                });

                if (response.ok) {
                    alert('✅ Asset added successfully!');
                    window.location.href = '/';
                } else {
                    const error = await response.json();
                    alert(`❌ Error: ${error.error}`);
                }
            } catch (error) {
                alert(`❌ Error adding asset: ${error.message}`);
            }
        });
    </script>
</body>
</html>
        '''

    def scan_single_device(self, ip_address, username, password, scan_wmi=True, scan_ssh=False):
        """Enhanced single device scanning with multi-protocol support"""
        try:
            # Import the enhanced discovery functions
            from comprehensive_discovery_engine import enhanced_wmi_collection, ssh_collection, snmp_collection, ping_test
            
            # Test connectivity first
            if not ping_test(ip_address):
                return None
            
            device_data = None
            
            # Try SNMP first (fastest for network devices)
            try:
                device_data = snmp_collection(ip_address)
                if device_data:
                    return device_data
            except:
                pass
            
            # Try WMI if enabled
            if scan_wmi:
                try:
                    device_data = enhanced_wmi_collection(ip_address, username, password)
                    if device_data:
                        return device_data
                except:
                    pass
            
            # Try SSH if enabled
            if scan_ssh:
                try:
                    device_data = ssh_collection(ip_address, username, password)
                    if device_data:
                        return device_data
                except:
                    pass
            
            return None
            
        except Exception as e:
            logger.error(f"Error scanning {ip_address}: {e}")
            return None

    def run(self, host='0.0.0.0', port=8080, debug=False):
        """Run the enhanced web service"""
        import sys
        import os
        
        # Set UTF-8 environment for Windows console
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        
        print("Starting Enhanced Complete Web Service")
        print(f"URL: http://{host}:{port}")
        print("Features:")
        print("   - Fixed Edit Functionality with Working Forms")
        print("   - Auto-refresh Every 10 Seconds")  
        print("   - Database Status Monitoring")
        print("   - Asset Control Features (Ping, Port Scan, Status Update)")
        print("   - Real-time Statistics and Live Updates")
        print("   - 100% Functional Asset Management")
        
        # Production mode configuration
        self.app.run(
            host=host,
            port=port,
            debug=False,  # Production mode, not development
            threaded=True,
            use_reloader=False
        )

if __name__ == '__main__':
    service = EnhancedCompleteDepartmentWebService()
    service.run(debug=False)  # Production mode