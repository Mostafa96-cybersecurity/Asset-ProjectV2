# -*- coding: utf-8 -*-
"""
Complete Enhanced Web Service with Department Management
======================================================
Features:
- Full department management (add, edit, delete departments)  
- Manual asset addition through web interface
- Comprehensive device data display with all collected columns
- Enhanced UI with department assignment capabilities
- INTEGRATED WITH ENHANCED ACCESS CONTROL SYSTEM
"""

from flask import Flask, render_template_string, request, jsonify, redirect, url_for
import sqlite3
import logging
import ipaddress
from datetime import datetime
from typing import Dict, List, Optional
import json
import functools

# Import enhanced access control system
try:
    from enhanced_access_control_system import (
        access_control_manager,
        check_ip_access,
        authenticate_user,
        create_session,
        validate_session,
        check_rate_limit,
        log_access_attempt
    )
    ACCESS_CONTROL_ENABLED = True
    print("[SECURITY] Enhanced Access Control System loaded successfully")
except ImportError:
    ACCESS_CONTROL_ENABLED = False
    print("[WARNING] Enhanced Access Control System not available - using basic security")

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

class CompleteDepartmentWebService:
    """Complete web service with department and asset management"""
    
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
        """Enhanced access control check"""
        try:
            if ACCESS_CONTROL_ENABLED:
                # Use enhanced access control system
                ip_allowed, reason = check_ip_access(client_ip)
                if ip_allowed:
                    logger.info(f"ACCESS ALLOWED: {client_ip} - {reason}")
                    return True
                else:
                    logger.warning(f"ACCESS DENIED: {client_ip} - {reason}")
                    return False
            else:
                # Fallback to basic IP network checking
                client_addr = ipaddress.IPv4Address(client_ip)
                for network in self.allowed_networks:
                    if client_addr in network:
                        return True
                return False
        except:
            return False  # Block invalid IPs
    
    def require_access(self, f):
        """Enhanced decorator to check access control with comprehensive logging"""
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', 
                                              request.environ.get('REMOTE_ADDR', '127.0.0.1'))
                user_agent = request.headers.get('User-Agent', 'Unknown')
                endpoint = request.endpoint or request.path
                method = request.method
                
                # Enhanced access control check
                if not self.check_access(client_ip):
                    if ACCESS_CONTROL_ENABLED:
                        log_access_attempt(client_ip, endpoint, method, user_agent, "ACCESS_DENIED")
                    logger.warning(f"ACCESS DENIED: {client_ip} -> {method} {request.path}")
                    return jsonify({
                        "error": "Access denied",
                        "message": "Your IP address is not authorized to access this service",
                        "code": "ACCESS_DENIED"
                    }), 403
                
                # Rate limiting check (if enhanced access control is available)
                if ACCESS_CONTROL_ENABLED:
                    rate_ok, rate_reason = check_rate_limit(client_ip, endpoint)
                    if not rate_ok:
                        log_access_attempt(client_ip, endpoint, method, user_agent, f"RATE_LIMITED: {rate_reason}")
                        logger.warning(f"RATE LIMITED: {client_ip} -> {method} {request.path}")
                        return jsonify({
                            "error": "Rate limit exceeded",
                            "message": "Too many requests, please try again later",
                            "code": "RATE_LIMITED"
                        }), 429
                    
                    # Log successful access
                    log_access_attempt(client_ip, endpoint, method, user_agent, "SUCCESS")
                
                logger.info(f"ACCESS GRANTED: {client_ip} -> {method} {request.path}")
                return f(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"Access control error: {e}")
                return jsonify({
                    "error": "Security check failed", 
                    "message": "Please try again later",
                    "code": "SECURITY_ERROR"
                }), 500
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
    
    def setup_routes(self):
        """Setup all Flask routes"""
        
        @self.app.route('/')
        @log_access
        @self.require_access
        def dashboard():
            """Main dashboard"""
            return render_template_string(self.get_dashboard_template())
        
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
        
        @self.app.route('/logs')
        @log_access
        @self.require_access
        def logs_page():
            """Access logs page"""
            return render_template_string(self.get_logs_template())
        
        @self.app.route('/monitor')
        @log_access
        @self.require_access
        def realtime_monitor():
            """Real-time monitoring page"""
            return render_template_string(self.get_realtime_monitor_template())
        
        # ============ ASSET CONTROL API ENDPOINTS ============
        
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
                    import subprocess
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
                    import socket
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
                cursor.execute('''
                    SELECT COUNT(*) FROM assets 
                    WHERE created_at > datetime('now', '-1 hour')
                ''')
                recent_additions = cursor.fetchone()[0]
                
                # Get database file size
                import os
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
        
        @self.app.route('/api/realtime/stats')
        @log_access
        @self.require_access
        def realtime_stats():
            """Get real-time statistics for monitoring"""
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Get comprehensive stats
                stats = {
                    'timestamp': datetime.now().isoformat(),
                    'total_devices': 0,
                    'collection_methods': {},
                    'device_types': {},
                    'operating_systems': {},
                    'recent_discoveries': [],
                    'scan_summary': {}
                }
                
                # Total devices
                cursor.execute('SELECT COUNT(*) FROM assets')
                stats['total_devices'] = cursor.fetchone()[0]
                
                # Collection methods breakdown  
                cursor.execute('''
                    SELECT collection_method, COUNT(*) 
                    FROM assets 
                    WHERE collection_method IS NOT NULL 
                    GROUP BY collection_method
                ''')
                for method, count in cursor.fetchall():
                    stats['collection_methods'][method or 'UNKNOWN'] = count
                
                # Device types
                cursor.execute('''
                    SELECT device_type, COUNT(*) 
                    FROM assets 
                    WHERE device_type IS NOT NULL AND device_type != '' 
                    GROUP BY device_type
                ''')
                for device_type, count in cursor.fetchall():
                    stats['device_types'][device_type] = count
                
                # Operating systems
                cursor.execute('''
                    SELECT operating_system, COUNT(*) 
                    FROM assets 
                    WHERE operating_system IS NOT NULL AND operating_system != '' 
                    GROUP BY operating_system
                ''')
                for os, count in cursor.fetchall():
                    stats['operating_systems'][os] = count
                
                # Recent discoveries (last 10)
                cursor.execute('''
                    SELECT ip_address, hostname, operating_system, device_type,
                           collection_method, last_update_time
                    FROM assets 
                    ORDER BY last_update_time DESC 
                    LIMIT 10
                ''')
                
                recent = []
                for row in cursor.fetchall():
                    recent.append({
                        'ip_address': row[0] or 'N/A',
                        'hostname': row[1] or 'N/A', 
                        'operating_system': row[2] or 'N/A',
                        'device_type': row[3] or 'N/A',
                        'collection_method': row[4] or 'N/A',
                        'last_update': row[5] or 'N/A'
                    })
                stats['recent_discoveries'] = recent
                
                conn.close()
                return jsonify(stats)
                
            except Exception as e:
                return jsonify({'error': str(e)})
        
        @self.app.route('/api/realtime/devices/<int:limit>')
        @log_access  
        @self.require_access
        def realtime_devices(limit=20):
            """Get recent devices with full details"""
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT ip_address, hostname, operating_system, device_type,
                           collection_method, last_update_time, total_physical_memory,
                           processor_name, ssh_cpu_count, snmp_sys_descr,
                           realtime_status, scan_status
                    FROM assets 
                    ORDER BY last_update_time DESC 
                    LIMIT ?
                ''', (limit,))
                
                devices = []
                for row in cursor.fetchall():
                    device = {
                        'ip_address': row[0] or 'N/A',
                        'hostname': row[1] or 'N/A',
                        'operating_system': row[2] or 'N/A', 
                        'device_type': row[3] or 'N/A',
                        'collection_method': row[4] or 'N/A',
                        'last_update': row[5] or 'N/A',
                        'memory': f"{row[6]} MB" if row[6] else 'N/A',
                        'processor': row[7] or 'N/A',
                        'cpu_count': row[8] if row[8] else 'N/A',
                        'description': row[9] or 'N/A',
                        'realtime_status': row[10] or 'N/A',
                        'scan_status': row[11] or 'N/A'
                    }
                    devices.append(device)
                
                conn.close()
                return jsonify(devices)
                
            except Exception as e:
                return jsonify({'error': str(e)})
            """Get comprehensive statistics"""
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Total assets
                cursor.execute("SELECT COUNT(*) FROM assets")
                total_assets = cursor.fetchone()[0]
                
                # Active assets
                cursor.execute("SELECT COUNT(*) FROM assets WHERE status = 'Active'")
                active_assets = cursor.fetchone()[0]
                
                # Classifications
                cursor.execute("SELECT COUNT(DISTINCT classification) FROM assets WHERE classification IS NOT NULL")
                classifications_count = cursor.fetchone()[0]
                
                # Departments
                cursor.execute("SELECT COUNT(*) FROM departments")
                departments_count = cursor.fetchone()[0]
                
                # Recent assets (last 24 hours)
                cursor.execute("""
                    SELECT COUNT(*) FROM assets 
                    WHERE created_at >= datetime('now', '-1 day')
                """)
                recent_count = cursor.fetchone()[0]
                
                conn.close()
                
                return jsonify({
                    'total_assets': total_assets,
                    'active_assets': active_assets,
                    'classifications': classifications_count,
                    'departments': departments_count,
                    'recent_24h': recent_count
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/devices')
        def get_devices():
            """Get all devices with comprehensive data"""
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Get devices with all available columns
                cursor.execute("""
                    SELECT 
                        id, hostname, ip_address, working_user, classification, 
                        department, status, data_source, created_at, last_updated,
                        os_name, os_version, manufacturer, model, serial_number,
                        mac_address, cpu_info, memory_gb, storage_info, vendor,
                        ping_status, last_ping, collection_method, domain, notes
                    FROM assets 
                    ORDER BY hostname
                """)
                
                devices = []
                for row in cursor.fetchall():
                    device = {
                        'id': row[0],
                        'hostname': row[1] or 'Unknown',
                        'ip_address': row[2],
                        'user': row[3],
                        'classification': row[4] or 'Unknown',
                        'department': row[5] or 'Unknown',
                        'status': row[6] or 'Unknown', 
                        'data_source': row[7],
                        'created_at': row[8],
                        'last_updated': row[9],
                        'os_name': row[10],
                        'os_version': row[11],
                        'manufacturer': row[12] or 'Unknown',
                        'model': row[13],
                        'serial_number': row[14],
                        'mac_address': row[15],
                        'cpu_info': row[16],
                        'memory_gb': row[17],
                        'storage_info': row[18],
                        'vendor': row[19],
                        'ping_status': row[20] or 'Unknown',
                        'last_ping': row[21],
                        'collection_method': row[22],
                        'domain': row[23],
                        'notes': row[24]
                    }
                    devices.append(device)
                
                conn.close()
                return jsonify(devices)
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/departments', methods=['GET', 'POST'])
        def handle_departments():
            """Handle department operations"""
            if request.method == 'GET':
                try:
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    
                    cursor.execute("""
                        SELECT d.id, d.name, d.description, d.manager, d.location, 
                               d.created_at, COUNT(a.id) as asset_count
                        FROM departments d
                        LEFT JOIN assets a ON d.name = a.department
                        GROUP BY d.id, d.name, d.description, d.manager, d.location, d.created_at
                        ORDER BY d.name
                    """)
                    
                    departments = []
                    for row in cursor.fetchall():
                        departments.append({
                            'id': row[0],
                            'name': row[1],
                            'description': row[2],
                            'manager': row[3],
                            'location': row[4],
                            'created_at': row[5],
                            'asset_count': row[6]
                        })
                    
                    conn.close()
                    return jsonify(departments)
                    
                except Exception as e:
                    return jsonify({'error': str(e)}), 500
            
            elif request.method == 'POST':
                try:
                    data = request.json or {}
                    name = data.get('name', '').strip()
                    description = data.get('description', '').strip()
                    manager = data.get('manager', '').strip()
                    location = data.get('location', '').strip()
                    
                    if not name:
                        return jsonify({'error': 'Department name is required'}), 400
                    
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        INSERT INTO departments (name, description, manager, location, updated_at)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (name, description, manager, location, datetime.now().isoformat()))
                    
                    dept_id = cursor.lastrowid
                    conn.commit()
                    conn.close()
                    
                    return jsonify({'id': dept_id, 'message': 'Department created successfully'})
                    
                except Exception as e:
                    return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/departments/<int:dept_id>', methods=['PUT', 'DELETE'])
        def handle_department(dept_id):
            """Handle individual department operations"""
            if request.method == 'PUT':
                try:
                    data = request.json or {}
                    name = data.get('name', '').strip()
                    description = data.get('description', '').strip()
                    manager = data.get('manager', '').strip()
                    location = data.get('location', '').strip()
                    
                    if not name:
                        return jsonify({'error': 'Department name is required'}), 400
                    
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    
                    # Update department
                    cursor.execute('''
                        UPDATE departments 
                        SET name = ?, description = ?, manager = ?, location = ?, updated_at = ?
                        WHERE id = ?
                    ''', (name, description, manager, location, datetime.now().isoformat(), dept_id))
                    
                    # Update assets that reference the old department name
                    cursor.execute('SELECT name FROM departments WHERE id = ?', (dept_id,))
                    old_name = cursor.fetchone()
                    if old_name:
                        cursor.execute('UPDATE assets SET department = ? WHERE department = ?', (name, old_name[0]))
                    
                    conn.commit()
                    conn.close()
                    
                    return jsonify({'message': 'Department updated successfully'})
                    
                except Exception as e:
                    return jsonify({'error': str(e)}), 500
            
            elif request.method == 'DELETE':
                try:
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    
                    # Get department name before deleting
                    cursor.execute('SELECT name FROM departments WHERE id = ?', (dept_id,))
                    dept = cursor.fetchone()
                    if not dept:
                        return jsonify({'error': 'Department not found'}), 404
                    
                    # Update assets to 'Unknown' department
                    cursor.execute('UPDATE assets SET department = "Unknown" WHERE department = ?', (dept[0],))
                    
                    # Delete department
                    cursor.execute('DELETE FROM departments WHERE id = ?', (dept_id,))
                    
                    conn.commit()
                    conn.close()
                    
                    return jsonify({'message': 'Department deleted successfully'})
                    
                except Exception as e:
                    return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/assets', methods=['POST'])
        def add_asset():
            """Add new asset through web interface"""
            try:
                data = request.json or {}
                
                # Validate required fields
                hostname = data.get('hostname', '').strip()
                if not hostname:
                    return jsonify({'error': 'Hostname is required'}), 400
                
                # Check for duplicates
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                ip_address = data.get('ip_address', '').strip() or None
                cursor.execute('''
                    SELECT COUNT(*) FROM assets 
                    WHERE hostname = ? OR (ip_address = ? AND ip_address IS NOT NULL)
                ''', (hostname, ip_address))
                
                if cursor.fetchone()[0] > 0:
                    conn.close()
                    return jsonify({'error': 'Device with this hostname or IP already exists'}), 400
                
                # Insert asset with comprehensive data
                asset_data = {
                    'hostname': hostname,
                    'ip_address': ip_address,
                    'working_user': data.get('user', '').strip() or None,
                    'domain': data.get('domain', '').strip() or None,
                    'classification': data.get('classification', 'Unknown'),
                    'department': data.get('department', 'Unknown'),
                    'status': data.get('status', 'Active'),
                    'data_source': 'Manual Entry (Web Interface)',
                    'created_at': datetime.now().isoformat(),
                    'last_updated': datetime.now().isoformat(),
                    'updated_by': 'Web Interface',
                    'device_type': data.get('classification', 'Unknown'),
                    'os_name': data.get('os_name', '').strip() or None,
                    'os_version': data.get('os_version', '').strip() or None,
                    'manufacturer': data.get('manufacturer', '').strip() or None,
                    'model': data.get('model', '').strip() or None,
                    'serial_number': data.get('serial_number', '').strip() or None,
                    'mac_address': data.get('mac_address', '').strip() or None,
                    'cpu_info': data.get('cpu_info', '').strip() or None,
                    'memory_gb': float(data.get('memory_gb', 0)) if data.get('memory_gb') else None,
                    'storage_info': data.get('storage_info', '').strip() or None,
                    'vendor': data.get('vendor', '').strip() or None,
                    'notes': data.get('notes', '').strip() or f"Added via Web Interface on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
                
                # Insert asset
                cursor.execute('''
                    INSERT INTO assets (
                        hostname, ip_address, working_user, domain, classification, department,
                        status, data_source, created_at, last_updated, updated_by, device_type,
                        os_name, os_version, manufacturer, model, serial_number, mac_address,
                        cpu_info, memory_gb, storage_info, vendor, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    asset_data['hostname'], asset_data['ip_address'], asset_data['working_user'],
                    asset_data['domain'], asset_data['classification'], asset_data['department'],
                    asset_data['status'], asset_data['data_source'], asset_data['created_at'],
                    asset_data['last_updated'], asset_data['updated_by'], asset_data['device_type'],
                    asset_data['os_name'], asset_data['os_version'], asset_data['manufacturer'],
                    asset_data['model'], asset_data['serial_number'], asset_data['mac_address'],
                    asset_data['cpu_info'], asset_data['memory_gb'], asset_data['storage_info'],
                    asset_data['vendor'], asset_data['notes']
                ))
                
                asset_id = cursor.lastrowid
                conn.commit()
                conn.close()
                
                return jsonify({'id': asset_id, 'message': 'Asset added successfully'})
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/assets/<int:asset_id>', methods=['PUT', 'DELETE'])
        def handle_asset(asset_id):
            """Handle individual asset operations"""
            if request.method == 'PUT':
                try:
                    data = request.json or {}
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    
                    # Update asset
                    cursor.execute('''
                        UPDATE assets SET
                            hostname = ?, ip_address = ?, working_user = ?, domain = ?,
                            classification = ?, department = ?, status = ?, last_updated = ?,
                            os_name = ?, os_version = ?, manufacturer = ?, model = ?,
                            serial_number = ?, mac_address = ?, cpu_info = ?, memory_gb = ?,
                            storage_info = ?, vendor = ?, notes = ?
                        WHERE id = ?
                    ''', (
                        data.get('hostname', ''), data.get('ip_address'), data.get('user'),
                        data.get('domain'), data.get('classification'), data.get('department'),
                        data.get('status'), datetime.now().isoformat(),
                        data.get('os_name'), data.get('os_version'), data.get('manufacturer'),
                        data.get('model'), data.get('serial_number'), data.get('mac_address'),
                        data.get('cpu_info'), data.get('memory_gb'), data.get('storage_info'),
                        data.get('vendor'), data.get('notes'), asset_id
                    ))
                    
                    conn.commit()
                    conn.close()
                    
                    return jsonify({'message': 'Asset updated successfully'})
                    
                except Exception as e:
                    return jsonify({'error': str(e)}), 500
                    
            elif request.method == 'DELETE':
                try:
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    
                    cursor.execute('DELETE FROM assets WHERE id = ?', (asset_id,))
                    
                    conn.commit()
                    conn.close()
                    
                    return jsonify({'message': 'Asset deleted successfully'})
                    
                except Exception as e:
                    return jsonify({'error': str(e)}), 500

    def get_dashboard_template(self):
        """Enhanced dashboard template with comprehensive device data"""
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏢 Complete Asset & Department Management</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --success-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            --warning-gradient: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
            --info-gradient: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        }
        
        body {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
        }
        
        .hero-header {
            background: var(--primary-gradient);
            color: white;
            padding: 2rem 0;
            margin-bottom: 2rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .stat-card {
            background: white;
            border-radius: 15px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            border: none;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0,0,0,0.15);
        }
        
        .stat-number {
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 0;
        }
        
        .devices-table {
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        }
        
        .table th {
            background: var(--primary-gradient);
            color: white;
            border: none;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.85rem;
            letter-spacing: 0.5px;
            padding: 1rem;
        }
        
        .table td {
            padding: 1rem;
            vertical-align: middle;
            border-color: #f8f9fa;
        }
        
        .badge {
            font-size: 0.75rem;
            padding: 0.5rem 0.75rem;
        }
        
        .classification-badge {
            background: var(--success-gradient);
            color: white;
            border: none;
        }
        
        .department-badge {
            background: var(--info-gradient);
            color: #333;
            border: none;
        }
        
        .status-badge {
            background: var(--warning-gradient);
            color: white;
            border: none;
        }
        
        .btn-action {
            margin: 0 0.25rem;
            padding: 0.5rem 0.75rem;
            border-radius: 8px;
            border: none;
            transition: all 0.3s ease;
        }
        
        .search-box {
            border-radius: 25px;
            border: 2px solid #e9ecef;
            padding: 0.75rem 1.25rem;
            background: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        
        .search-box:focus {
            border-color: #667eea;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
        }
        
        .filter-section {
            background: white;
            border-radius: 15px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        }
        
        .ping-online { color: #28a745; }
        .ping-offline { color: #dc3545; }
        .ping-unknown { color: #6c757d; }
        
        .loading-spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .nav-pills .nav-link {
            border-radius: 25px;
            margin: 0 0.5rem;
            padding: 0.75rem 1.5rem;
            transition: all 0.3s ease;
        }
        
        .nav-pills .nav-link.active {
            background: var(--primary-gradient);
        }
    </style>
</head>
<body>
    <div class="hero-header">
        <div class="container">
            <div class="row align-items-center">
                <div class="col-md-8">
                    <h1><i class="fas fa-building"></i> Complete Asset & Department Management</h1>
                    <p class="mb-0">Enterprise Edition - Department Management & Comprehensive Asset Tracking</p>
                </div>
                <div class="col-md-4 text-end">
                    <div class="btn-group" role="group">
                        <a href="/" class="btn btn-light"><i class="fas fa-home"></i> Dashboard</a>
                        <a href="/departments" class="btn btn-info"><i class="fas fa-building"></i> Departments</a>
                        <a href="/add-asset" class="btn btn-success"><i class="fas fa-plus"></i> Add Asset</a>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="container-fluid">
        <!-- Statistics Cards -->
        <div class="row mb-4">
            <div class="col-lg-3 col-md-6">
                <div class="stat-card text-center">
                    <div class="stat-number text-primary" id="totalAssets">
                        <div class="loading-spinner"></div>
                    </div>
                    <h5 class="text-muted">Total Assets</h5>
                </div>
            </div>
            <div class="col-lg-3 col-md-6">
                <div class="stat-card text-center">
                    <div class="stat-number text-success" id="activeAssets">
                        <div class="loading-spinner"></div>
                    </div>
                    <h5 class="text-muted">Active Assets</h5>
                </div>
            </div>
            <div class="col-lg-3 col-md-6">
                <div class="stat-card text-center">
                    <div class="stat-number text-info" id="classificationsCount">
                        <div class="loading-spinner"></div>
                    </div>
                    <h5 class="text-muted">Classifications</h5>
                </div>
            </div>
            <div class="col-lg-3 col-md-6">
                <div class="stat-card text-center">
                    <div class="stat-number text-warning" id="departmentsCount">
                        <div class="loading-spinner"></div>
                    </div>
                    <h5 class="text-muted">Departments</h5>
                </div>
            </div>
        </div>

        <!-- Filters -->
        <div class="filter-section">
            <div class="row">
                <div class="col-md-3">
                    <label class="form-label"><i class="fas fa-search"></i> Search Assets</label>
                    <input type="text" class="form-control search-box" id="searchBox" 
                           placeholder="Search by hostname, IP, user..." onkeyup="filterDevices()">
                </div>
                <div class="col-md-2">
                    <label class="form-label"><i class="fas fa-building"></i> Department</label>
                    <select class="form-select" id="departmentFilter" onchange="filterDevices()">
                        <option value="">All Departments</option>
                    </select>
                </div>
                <div class="col-md-2">
                    <label class="form-label"><i class="fas fa-tags"></i> Classification</label>
                    <select class="form-select" id="classificationFilter" onchange="filterDevices()">
                        <option value="">All Classifications</option>
                    </select>
                </div>
                <div class="col-md-2">
                    <label class="form-label"><i class="fas fa-heartbeat"></i> Status</label>
                    <select class="form-select" id="statusFilter" onchange="filterDevices()">
                        <option value="">All Statuses</option>
                        <option value="Active">Active</option>
                        <option value="Inactive">Inactive</option>
                        <option value="Maintenance">Maintenance</option>
                    </select>
                </div>
                <div class="col-md-3">
                    <label class="form-label"><i class="fas fa-cog"></i> Actions</label>
                    <div class="btn-group w-100">
                        <button class="btn btn-success" onclick="window.location.href='/add-asset'">
                            <i class="fas fa-plus"></i> Add Asset
                        </button>
                        <button class="btn btn-primary" onclick="refreshData()">
                            <i class="fas fa-sync-alt"></i> Refresh
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Enhanced Assets Table with All Device Data -->
        <div class="devices-table">
            <div class="table-responsive">
                <table class="table table-hover mb-0">
                    <thead>
                        <tr>
                            <th>Device Info</th>
                            <th>User & Domain</th>
                            <th>Network</th>
                            <th>Classification</th>
                            <th>Department</th>
                            <th>Hardware</th>
                            <th>System</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="devicesTable">
                        <tr>
                            <td colspan="9" class="text-center py-5">
                                <div class="loading-spinner me-2"></div>
                                Loading devices...
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let allDevices = [];
        let departments = [];

        // Load initial data
        document.addEventListener('DOMContentLoaded', function() {
            loadStats();
            loadDevices();
            loadDepartments();
            loadDatabaseStatus();
            
            // Auto-refresh every 10 seconds
            setInterval(function() {
                refreshData();
                loadDatabaseStatus();
            }, 10000);
            
            // Show auto-refresh indicator
            setInterval(function() {
                const refreshBtn = document.querySelector('.btn[onclick="refreshData()"]');
                if (refreshBtn) {
                    refreshBtn.classList.add('btn-warning');
                    refreshBtn.innerHTML = '<i class="fas fa-sync-alt fa-spin"></i> Auto-Refreshing...';
                    
                    setTimeout(() => {
                        refreshBtn.classList.remove('btn-warning');
                        refreshBtn.classList.add('btn-outline-secondary');
                        refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i> Refresh';
                    }, 1000);
                }
            }, 10000);
        });
        
        async function loadDatabaseStatus() {
            try {
                const response = await fetch('/api/database/status');
                const status = await response.json();
                
                const statusCard = document.getElementById('databaseStatusCard');
                const statusElement = document.getElementById('databaseStatus');
                
                if (status.status === 'connected' && status.health === 'healthy') {
                    statusElement.innerHTML = '✅';
                    statusCard.style.backgroundColor = '#d4edda';
                    statusCard.style.borderColor = '#c3e6cb';
                    statusCard.title = `Database: ${status.total_assets} assets, ${status.database_size_mb}MB`;
                } else {
                    statusElement.innerHTML = '❌';
                    statusCard.style.backgroundColor = '#f8d7da';
                    statusCard.style.borderColor = '#f5c6cb';
                    statusCard.title = `Database Error: ${status.error || 'Unknown error'}`;
                }
                
            } catch (error) {
                const statusElement = document.getElementById('databaseStatus');
                const statusCard = document.getElementById('databaseStatusCard');
                statusElement.innerHTML = '⚠️';
                statusCard.style.backgroundColor = '#fff3cd';
                statusCard.style.borderColor = '#ffeaa7';
                statusCard.title = `Connection Error: ${error.message}`;
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
                        message += `\nOpen ports: ${result.open_ports.join(', ')}`;
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
        });

        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const stats = await response.json();
                
                document.getElementById('totalAssets').textContent = stats.total_assets || 0;
                document.getElementById('activeAssets').textContent = stats.active_assets || 0;
                document.getElementById('classificationsCount').textContent = stats.classifications || 0;
                document.getElementById('departmentsCount').textContent = stats.departments || 0;
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }

        async function loadDevices() {
            try {
                const response = await fetch('/api/devices');
                allDevices = await response.json();
                displayDevices(allDevices);
            } catch (error) {
                console.error('Error loading devices:', error);
                document.getElementById('devicesTable').innerHTML = 
                    '<tr><td colspan="9" class="text-center text-danger">Error loading devices</td></tr>';
            }
        }

        async function loadDepartments() {
            try {
                const response = await fetch('/api/departments');
                departments = await response.json();
                
                const select = document.getElementById('departmentFilter');
                select.innerHTML = '<option value="">All Departments</option>';
                
                departments.forEach(dept => {
                    const option = document.createElement('option');
                    option.value = dept.name;
                    option.textContent = `${dept.name} (${dept.asset_count})`;
                    select.appendChild(option);
                });
            } catch (error) {
                console.error('Error loading departments:', error);
            }
        }

        function displayDevices(devices) {
            const tbody = document.getElementById('devicesTable');
            
            if (devices.length === 0) {
                tbody.innerHTML = '<tr><td colspan="9" class="text-center text-muted py-5">No devices found</td></tr>';
                return;
            }

            tbody.innerHTML = devices.map(device => `
                <tr>
                    <td>
                        <strong>${device.hostname}</strong>
                        ${device.manufacturer ? `<br><small class="text-muted">${device.manufacturer}</small>` : ''}
                        ${device.model ? `<br><small class="text-muted">${device.model}</small>` : ''}
                    </td>
                    <td>
                        ${device.user || 'N/A'}
                        ${device.domain ? `<br><small class="text-muted">${device.domain}</small>` : ''}
                    </td>
                    <td>
                        ${device.ip_address ? `<code>${device.ip_address}</code>` : 'N/A'}
                        ${device.mac_address ? `<br><small class="text-muted">${device.mac_address}</small>` : ''}
                    </td>
                    <td><span class="badge classification-badge">${device.classification}</span></td>
                    <td><span class="badge department-badge">${device.department}</span></td>
                    <td>
                        ${device.cpu_info ? `<small>${device.cpu_info}</small><br>` : ''}
                        ${device.memory_gb ? `<small>RAM: ${device.memory_gb}GB</small><br>` : ''}
                        ${device.storage_info ? `<small>${device.storage_info}</small>` : ''}
                    </td>
                    <td>
                        ${device.os_name || 'Unknown'}
                        ${device.os_version ? `<br><small class="text-muted">${device.os_version}</small>` : ''}
                    </td>
                    <td>
                        <span class="badge status-badge">${device.status}</span>
                        <br><i class="fas fa-circle ${getPingStatusClass(device.ping_status)}"></i>
                        ${device.ping_status || 'Unknown'}
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

        function getPingStatusClass(status) {
            switch(status?.toLowerCase()) {
                case 'online': case 'active': return 'ping-online';
                case 'offline': case 'inactive': return 'ping-offline';
                default: return 'ping-unknown';
            }
        }

        function filterDevices() {
            const searchTerm = document.getElementById('searchBox').value.toLowerCase();
            const deptFilter = document.getElementById('departmentFilter').value;
            const classFilter = document.getElementById('classificationFilter').value;
            const statusFilter = document.getElementById('statusFilter').value;

            const filtered = allDevices.filter(device => {
                const matchesSearch = !searchTerm || 
                    device.hostname?.toLowerCase().includes(searchTerm) ||
                    device.ip_address?.toLowerCase().includes(searchTerm) ||
                    device.user?.toLowerCase().includes(searchTerm) ||
                    device.classification?.toLowerCase().includes(searchTerm);
                
                const matchesDept = !deptFilter || device.department === deptFilter;
                const matchesClass = !classFilter || device.classification === classFilter;
                const matchesStatus = !statusFilter || device.status === statusFilter;

                return matchesSearch && matchesDept && matchesClass && matchesStatus;
            });

            displayDevices(filtered);
        }

        function refreshData() {
            loadStats();
            loadDevices();
            loadDepartments();
        }

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

        async function deleteDevice(id) {
            if (confirm('Are you sure you want to delete this device?')) {
                try {
                    const response = await fetch(`/api/assets/${id}`, {
                        method: 'DELETE'
                    });
                    
                    if (response.ok) {
                        refreshData();
                        alert('Device deleted successfully');
                    } else {
                        const error = await response.json();
                        alert(`Error: ${error.error}`);
                    }
                } catch (error) {
                    alert(`Error deleting device: ${error}`);
                }
            }
        }
    </script>
</body>
</html>
        '''

    def get_departments_template(self):
        """Department management template"""
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
        .dept-card {
            background: white;
            border-radius: 15px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            transition: transform 0.3s ease;
        }
        .dept-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
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
                    <div class="btn-group">
                        <a href="/" class="btn btn-light"><i class="fas fa-home"></i> Dashboard</a>
                        <button class="btn btn-success" onclick="addDepartment()"><i class="fas fa-plus"></i> Add Department</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="container-fluid">
        <div class="row" id="departmentsContainer">
            <div class="col-12 text-center py-5">
                <div class="spinner-border" role="status"></div>
                <p>Loading departments...</p>
            </div>
        </div>
    </div>

    <!-- Add Department Modal -->
    <div class="modal fade" id="addDeptModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Add New Department</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="addDeptForm">
                        <div class="mb-3">
                            <label class="form-label">Department Name</label>
                            <input type="text" class="form-control" id="deptName" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Description</label>
                            <textarea class="form-control" id="deptDesc" rows="3"></textarea>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Manager</label>
                            <input type="text" class="form-control" id="deptManager">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Location</label>
                            <input type="text" class="form-control" id="deptLocation">
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-success" onclick="saveDepartment()">Save Department</button>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', loadDepartments);

        async function loadDepartments() {
            try {
                const response = await fetch('/api/departments');
                const departments = await response.json();
                displayDepartments(departments);
            } catch (error) {
                console.error('Error loading departments:', error);
            }
        }

        function displayDepartments(departments) {
            const container = document.getElementById('departmentsContainer');
            
            if (departments.length === 0) {
                container.innerHTML = '<div class="col-12 text-center"><p>No departments found</p></div>';
                return;
            }

            container.innerHTML = departments.map(dept => `
                <div class="col-md-6 col-lg-4">
                    <div class="dept-card">
                        <div class="d-flex justify-content-between align-items-start">
                            <h5><i class="fas fa-building text-primary"></i> ${dept.name}</h5>
                            <div class="btn-group btn-group-sm">
                                <button class="btn btn-outline-primary" onclick="editDepartment(${dept.id})">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-outline-danger" onclick="deleteDepartment(${dept.id})">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                        <p class="text-muted">${dept.description || 'No description'}</p>
                        <div class="row">
                            <div class="col-6">
                                <small class="text-muted">Manager:</small><br>
                                <strong>${dept.manager || 'N/A'}</strong>
                            </div>
                            <div class="col-6">
                                <small class="text-muted">Assets:</small><br>
                                <strong>${dept.asset_count || 0}</strong>
                            </div>
                        </div>
                        <div class="mt-2">
                            <small class="text-muted">Location:</small><br>
                            <strong>${dept.location || 'N/A'}</strong>
                        </div>
                    </div>
                </div>
            `).join('');
        }

        function addDepartment() {
            document.getElementById('addDeptForm').reset();
            new bootstrap.Modal(document.getElementById('addDeptModal')).show();
        }

        async function saveDepartment() {
            const data = {
                name: document.getElementById('deptName').value,
                description: document.getElementById('deptDesc').value,
                manager: document.getElementById('deptManager').value,
                location: document.getElementById('deptLocation').value
            };

            if (!data.name.trim()) {
                alert('Department name is required');
                return;
            }

            try {
                const response = await fetch('/api/departments', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });

                if (response.ok) {
                    bootstrap.Modal.getInstance(document.getElementById('addDeptModal')).hide();
                    loadDepartments();
                    alert('Department created successfully');
                } else {
                    const error = await response.json();
                    alert(`Error: ${error.error}`);
                }
            } catch (error) {
                alert(`Error creating department: ${error}`);
            }
        }

        async function deleteDepartment(id) {
            if (confirm('Are you sure? Assets in this department will be moved to "Unknown".')) {
                try {
                    const response = await fetch(`/api/departments/${id}`, {
                        method: 'DELETE'
                    });

                    if (response.ok) {
                        loadDepartments();
                        alert('Department deleted successfully');
                    } else {
                        const error = await response.json();
                        alert(`Error: ${error.error}`);
                    }
                } catch (error) {
                    alert(`Error deleting department: ${error}`);
                }
            }
        }

        function editDepartment(id) {
            alert(`Edit department ${id} - would open edit form`);
        }
    </script>
</body>
</html>
        '''

    def get_add_asset_template(self):
        """Add asset template"""
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>➕ Add New Asset</title>
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
        }
    </style>
</head>
<body>
    <div class="hero-header">
        <div class="container">
            <div class="row align-items-center">
                <div class="col-md-8">
                    <h1><i class="fas fa-plus"></i> Add New Asset</h1>
                    <p class="mb-0">Add comprehensive device information</p>
                </div>
                <div class="col-md-4 text-end">
                    <a href="/" class="btn btn-light"><i class="fas fa-home"></i> Back to Dashboard</a>
                </div>
            </div>
        </div>
    </div>

    <div class="container">
        <div class="form-card">
            <form id="addAssetForm">
                <div class="row">
                    <div class="col-md-6">
                        <h5><i class="fas fa-desktop"></i> Basic Information</h5>
                        <div class="mb-3">
                            <label class="form-label">Hostname *</label>
                            <input type="text" class="form-control" id="hostname" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">IP Address</label>
                            <input type="text" class="form-control" id="ip_address">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">User</label>
                            <input type="text" class="form-control" id="user">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Domain</label>
                            <input type="text" class="form-control" id="domain">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Classification</label>
                            <select class="form-select" id="classification">
                                <option value="Windows Workstation">Windows Workstation</option>
                                <option value="Windows Server">Windows Server</option>
                                <option value="Linux Workstation">Linux Workstation</option>
                                <option value="Linux Server">Linux Server</option>
                                <option value="Network Device">Network Device</option>
                                <option value="Hypervisor">Hypervisor</option>
                                <option value="Printer">Printer</option>
                                <option value="Access Point">Access Point</option>
                                <option value="Unknown">Unknown</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Department</label>
                            <select class="form-select" id="department">
                                <option value="">Loading departments...</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Status</label>
                            <select class="form-select" id="status">
                                <option value="Active">Active</option>
                                <option value="Inactive">Inactive</option>
                                <option value="Maintenance">Maintenance</option>
                            </select>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <h5><i class="fas fa-cogs"></i> Hardware Information</h5>
                        <div class="mb-3">
                            <label class="form-label">OS Name</label>
                            <input type="text" class="form-control" id="os_name">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">OS Version</label>
                            <input type="text" class="form-control" id="os_version">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Manufacturer</label>
                            <input type="text" class="form-control" id="manufacturer">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Model</label>
                            <input type="text" class="form-control" id="model">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Serial Number</label>
                            <input type="text" class="form-control" id="serial_number">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">MAC Address</label>
                            <input type="text" class="form-control" id="mac_address">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">CPU Info</label>
                            <input type="text" class="form-control" id="cpu_info">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Memory (GB)</label>
                            <input type="number" class="form-control" id="memory_gb" step="0.1">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Storage Info</label>
                            <input type="text" class="form-control" id="storage_info">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Vendor</label>
                            <input type="text" class="form-control" id="vendor">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Notes</label>
                            <textarea class="form-control" id="notes" rows="3"></textarea>
                        </div>
                    </div>
                </div>
                <div class="text-center mt-4">
                    <button type="button" class="btn btn-secondary me-2" onclick="window.location.href='/'">Cancel</button>
                    <button type="submit" class="btn btn-success"><i class="fas fa-save"></i> Save Asset</button>
                </div>
            </form>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', loadDepartments);

        async function loadDepartments() {
            try {
                const response = await fetch('/api/departments');
                const departments = await response.json();
                
                const select = document.getElementById('department');
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

        document.getElementById('addAssetForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = {
                hostname: document.getElementById('hostname').value,
                ip_address: document.getElementById('ip_address').value,
                user: document.getElementById('user').value,
                domain: document.getElementById('domain').value,
                classification: document.getElementById('classification').value,
                department: document.getElementById('department').value,
                status: document.getElementById('status').value,
                os_name: document.getElementById('os_name').value,
                os_version: document.getElementById('os_version').value,
                manufacturer: document.getElementById('manufacturer').value,
                model: document.getElementById('model').value,
                serial_number: document.getElementById('serial_number').value,
                mac_address: document.getElementById('mac_address').value,
                cpu_info: document.getElementById('cpu_info').value,
                memory_gb: document.getElementById('memory_gb').value,
                storage_info: document.getElementById('storage_info').value,
                vendor: document.getElementById('vendor').value,
                notes: document.getElementById('notes').value
            };

            try {
                const response = await fetch('/api/assets', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(formData)
                });

                if (response.ok) {
                    alert('Asset added successfully!');
                    window.location.href = '/';
                } else {
                    const error = await response.json();
                    alert(`Error: ${error.error}`);
                }
            } catch (error) {
                alert(`Error adding asset: ${error}`);
            }
        });
    </script>
</body>
</html>
        '''

    def get_logs_template(self):
        """Logs page template"""
        try:
            # Read recent log entries
            log_entries = []
            try:
                with open('web_service.log', 'r') as f:
                    lines = f.readlines()
                    log_entries = lines[-100:]  # Last 100 entries
            except FileNotFoundError:
                log_entries = ['No log file found yet.']
            
            log_content = ''.join(log_entries)
            
        except Exception:
            log_content = "Error reading log file"
            
        return '''
<!DOCTYPE html>
<html>
<head>
    <title>Access Logs - Asset Management</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .log-container {
            background: #1a1a1a;
            color: #00ff00;
            font-family: 'Courier New', monospace;
            padding: 20px;
            border-radius: 8px;
            max-height: 600px;
            overflow-y: auto;
            font-size: 12px;
            line-height: 1.4;
        }
        .log-entry {
            margin-bottom: 2px;
            white-space: pre-wrap;
        }
        .access-entry { color: #00aaff; }
        .error-entry { color: #ff4444; }
        .warning-entry { color: #ffaa00; }
        .info-entry { color: #00ff00; }
    </style>
</head>
<body class="bg-light">
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-server me-2"></i>Asset Management System
            </a>
            <div class="navbar-nav">
                <a class="nav-link" href="/"><i class="fas fa-home"></i> Dashboard</a>
                <a class="nav-link" href="/departments"><i class="fas fa-building"></i> Departments</a>
                <a class="nav-link" href="/add-asset"><i class="fas fa-plus"></i> Add Asset</a>
                <a class="nav-link active" href="/logs"><i class="fas fa-list"></i> Logs</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row">
            <div class="col-12">
                <h2><i class="fas fa-list-alt text-primary"></i> Access Logs & System Activity</h2>
                <p class="text-muted">Real-time access logs and system events</p>
            </div>
        </div>
        
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">
                            <i class="fas fa-terminal text-success"></i> System Logs
                        </h5>
                        <button class="btn btn-sm btn-outline-secondary" onclick="refreshLogs()">
                            <i class="fas fa-sync-alt"></i> Refresh
                        </button>
                    </div>
                    <div class="card-body p-0">
                        <div class="log-container" id="logContainer">''' + log_content.replace('<', '&lt;').replace('>', '&gt;') + '''</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mt-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h6><i class="fas fa-shield-alt text-warning"></i> Access Control</h6>
                    </div>
                    <div class="card-body">
                        <div class="alert alert-info mb-2">
                            <i class="fas fa-info-circle"></i> <strong>Allowed Networks:</strong>
                        </div>
                        <ul class="list-unstyled">
                            <li><i class="fas fa-check text-success"></i> 127.0.0.0/8 (Localhost)</li>
                            <li><i class="fas fa-check text-success"></i> 192.168.0.0/16 (Private)</li>
                            <li><i class="fas fa-check text-success"></i> 10.0.0.0/8 (Private)</li>
                            <li><i class="fas fa-check text-success"></i> 172.16.0.0/12 (Private)</li>
                        </ul>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h6><i class="fas fa-info-circle text-info"></i> Log Legend</h6>
                    </div>
                    <div class="card-body">
                        <div class="d-flex align-items-center mb-2">
                            <span class="badge bg-info me-2">INFO</span> Normal operations
                        </div>
                        <div class="d-flex align-items-center mb-2">
                            <span class="badge bg-warning me-2">WARN</span> Access denied, issues
                        </div>
                        <div class="d-flex align-items-center mb-2">
                            <span class="badge bg-danger me-2">ERROR</span> System errors
                        </div>
                        <div class="d-flex align-items-center">
                            <span class="badge bg-success me-2">ACCESS</span> Web requests
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function refreshLogs() {
            location.reload();
        }
        
        // Auto-refresh every 30 seconds
        setInterval(refreshLogs, 30000);
        
        // Auto-scroll to bottom
        const logContainer = document.getElementById('logContainer');
        logContainer.scrollTop = logContainer.scrollHeight;
    </script>
</body>
</html>
        '''
    
    @log_access
    def logs(self):
        """Display access logs and security information"""
        try:
            # Read recent log entries
            logs_content = []
            try:
                with open('web_service.log', 'r') as f:
                    logs_content = f.readlines()[-50:]  # Last 50 lines
            except FileNotFoundError:
                logs_content = ["No log file found yet."]
            
            return render_template_string(self.get_logs_template(), 
                                        logs=logs_content,
                                        allowed_networks=[str(net) for net in self.allowed_networks])
        except Exception as e:
            return f"Error loading logs: {e}"
    
    def get_realtime_monitor_template(self):
        """Template for real-time monitoring dashboard"""
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Real-Time Asset Monitor</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    min-height: 100vh;
                }
                .dashboard {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    max-width: 1400px;
                    margin: 0 auto;
                }
                .card {
                    background: rgba(255, 255, 255, 0.1);
                    backdrop-filter: blur(10px);
                    border-radius: 15px;
                    padding: 20px;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
                }
                .header {
                    text-align: center;
                    margin-bottom: 30px;
                    grid-column: 1 / -1;
                }
                .stat-number {
                    font-size: 2.5em;
                    font-weight: bold;
                    margin: 10px 0;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                    color: #00ff88;
                }
                .device-item {
                    background: rgba(255, 255, 255, 0.1);
                    margin: 10px 0;
                    padding: 15px;
                    border-radius: 8px;
                    border-left: 4px solid #00ff88;
                }
                .pulse {
                    animation: pulse 2s infinite;
                }
                @keyframes pulse {
                    0% { opacity: 1; }
                    50% { opacity: 0.5; }
                    100% { opacity: 1; }
                }
                .online { color: #00ff88; }
                .refresh-btn {
                    background-color: #00ff88;
                    color: #333;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    cursor: pointer;
                    font-weight: bold;
                    margin: 10px;
                }
            </style>
        </head>
        <body>
            <div class="dashboard">
                <div class="header">
                    <h1>🚀 Real-Time Asset Monitor</h1>
                    <p>Live monitoring of network asset discovery and collection</p>
                    <p id="last-update">Last Update: <span class="pulse online">Loading...</span></p>
                    <button class="refresh-btn" onclick="loadAllData()">🔄 Refresh Now</button>
                </div>
                
                <div class="card">
                    <h2>📊 Collection Statistics</h2>
                    <div class="stat-number pulse" id="total-devices">0</div>
                    <div>Total Devices Discovered</div>
                </div>
                
                <div class="card">
                    <h2>🔧 Collection Methods</h2>
                    <div id="collection-methods">
                        <div>🖥️ WMI: <span id="wmi-count">0</span></div>
                        <div>🐧 SSH: <span id="ssh-count">0</span></div>
                        <div>🌐 SNMP: <span id="snmp-count">0</span></div>
                    </div>
                </div>
                
                <div class="card" style="grid-column: 1 / -1;">
                    <h2>🔍 Recently Discovered Devices</h2>
                    <div id="recent-devices">Loading...</div>
                </div>
            </div>
            
            <script>
                async function loadAllData() {
                    try {
                        const response = await fetch('/api/realtime/stats');
                        const stats = await response.json();
                        
                        document.getElementById('total-devices').textContent = stats.total_devices;
                        
                        const methods = stats.collection_methods || {};
                        document.getElementById('wmi-count').textContent = methods.WMI || 0;
                        document.getElementById('ssh-count').textContent = methods.SSH || 0;
                        document.getElementById('snmp-count').textContent = methods.SNMP || 0;
                        
                        const updateTime = new Date(stats.timestamp).toLocaleTimeString();
                        document.getElementById('last-update').innerHTML = 
                            `Last Update: <span class="online">${updateTime}</span>`;
                        
                        // Load recent devices
                        const devicesResponse = await fetch('/api/realtime/devices/10');
                        const devices = await devicesResponse.json();
                        
                        const recentDiv = document.getElementById('recent-devices');
                        if (devices && devices.length > 0) {
                            recentDiv.innerHTML = devices.map(device => `
                                <div class="device-item">
                                    <strong>🌐 ${device.ip_address}</strong> - ${device.hostname}<br>
                                    🖥️ ${device.operating_system} | 🔧 ${device.collection_method}
                                </div>
                            `).join('');
                        } else {
                            recentDiv.innerHTML = '<div>🔍 No devices discovered yet</div>';
                        }
                        
                    } catch (error) {
                        console.error('Error:', error);
                        document.getElementById('last-update').innerHTML = 
                            'Last Update: <span style="color: #ff4757;">Error</span>';
                    }
                }
                
                loadAllData();
                setInterval(loadAllData, 5000); // Refresh every 5 seconds
            </script>
        </body>
        </html>
        '''

    def run(self, host='0.0.0.0', port=5556, debug=False):
        """Run the complete web service"""
        print("Starting Complete Department & Asset Management Web Service")
        print(f"URL: http://{host}:{port}")
        print("Features:")
        print("   * Full Department Management (Add/Edit/Delete)")
        print("   * Manual Asset Addition through Web Interface")
        print("   * Comprehensive Device Data Display")
        print("   * Department Assignment & Filtering")
        print("   * Professional UI with Enhanced Tables")
        self.app.run(host=host, port=port, debug=debug)

# NOTE: Auto-startup disabled - use launch_original_desktop.py or GUI buttons
# if __name__ == '__main__':
#     service = CompleteDepartmentWebService()
#     service.run(debug=True)