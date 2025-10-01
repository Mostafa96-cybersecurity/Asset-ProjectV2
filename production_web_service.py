#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PRODUCTION ASSET MANAGEMENT SYSTEM
=================================
✅ Production-ready web service (not development)
✅ SNMP support for firewalls, switches, printers
✅ Credential management system
✅ Network management
✅ Enhanced discovery engine
✅ Admin flexibility (edit/delete/manage)
✅ Fixed smart discovery functionality
"""

from flask import Flask, render_template_string, request, jsonify, redirect, url_for
import sqlite3
import logging
import ipaddress
from datetime import datetime
import json
import subprocess
import socket
import os
import threading
import time
from comprehensive_discovery_engine import (
    multi_protocol_discovery, CredentialManager, 
    enhanced_wmi_collection, snmp_collection, ssh_collection
)

# Production logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('production_web_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('ProductionWebService')

class ProductionAssetManagementService:
    """Production-ready asset management web service"""
    
    def __init__(self, db_path: str = 'assets.db', port: int = 8080, host: str = '0.0.0.0'):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'production-asset-management-2025'
        self.db_path = db_path
        self.port = port
        self.host = host
        self.credential_manager = CredentialManager()
        
        # Initialize database
        self.init_database()
        
        # Setup routes
        self.setup_routes()
        
        logger.info("🚀 Production Asset Management Service initialized")
    
    def init_database(self):
        """Initialize asset database with enhanced schema"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Enhanced assets table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS assets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hostname TEXT,
                    ip_address TEXT UNIQUE,
                    working_user TEXT,
                    domain TEXT,
                    workgroup TEXT,
                    manufacturer TEXT,
                    model TEXT,
                    serial_number TEXT,
                    os_name TEXT,
                    operating_system TEXT,
                    os_version TEXT,
                    architecture TEXT,
                    memory_gb REAL,
                    cpu_cores INTEGER,
                    processor_name TEXT,
                    processor_manufacturer TEXT,
                    bios_version TEXT,
                    chassis_type TEXT,
                    device_type TEXT DEFAULT 'Workstation',
                    classification TEXT DEFAULT 'Other Asset',
                    department TEXT DEFAULT 'Unknown',
                    location TEXT,
                    status TEXT DEFAULT 'Active',
                    collection_method TEXT,
                    data_source TEXT,
                    contact TEXT,
                    description TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP,
                    last_scanned TIMESTAMP
                )
            ''')
            
            # Scan jobs table for tracking discovery jobs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scan_jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_name TEXT,
                    network_range TEXT,
                    status TEXT DEFAULT 'pending',
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    devices_found INTEGER DEFAULT 0,
                    devices_added INTEGER DEFAULT 0,
                    scan_type TEXT,
                    credentials_used TEXT,
                    results TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("✅ Database schema initialized")
            
        except Exception as e:
            logger.error(f"❌ Database initialization error: {e}")
    
    def setup_routes(self):
        """Setup all web routes"""
        
        # ============ MAIN PAGES ============
        @self.app.route('/')
        def dashboard():
            """Production dashboard"""
            return render_template_string(self.get_production_dashboard_template())
        
        @self.app.route('/add-asset')
        def add_asset_page():
            """Enhanced add asset page with smart discovery"""
            return render_template_string(self.get_enhanced_add_asset_template())
        
        @self.app.route('/credentials')
        def credentials_page():
            """Credential management page"""
            return render_template_string(self.get_credentials_template())
        
        @self.app.route('/networks')
        def networks_page():
            """Network management page"""
            return render_template_string(self.get_networks_template())
        
        # ============ DISCOVERY API ============
        @self.app.route('/api/scan/discover', methods=['POST'])
        def discover_assets():
            """Enhanced smart discovery with multi-protocol support"""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'No scan parameters provided'}), 400
                
                # Get scan parameters
                ip_range = data.get('ip_range', '').strip()
                selected_credentials = data.get('credentials', [])
                snmp_communities = data.get('snmp_communities', ['public'])
                scan_name = data.get('scan_name', f'Scan_{int(time.time())}')
                
                if not ip_range:
                    return jsonify({'error': 'IP range is required'}), 400
                
                # Start discovery job
                job_id = self.start_discovery_job(scan_name, ip_range, selected_credentials, snmp_communities)
                
                return jsonify({
                    'job_id': job_id,
                    'message': 'Discovery job started',
                    'status': 'running'
                })
                
            except Exception as e:
                logger.error(f"Discovery error: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/scan/status/<int:job_id>')
        def get_scan_status(job_id):
            """Get discovery job status"""
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('SELECT * FROM scan_jobs WHERE id = ?', (job_id,))
                job = cursor.fetchone()
                
                if not job:
                    return jsonify({'error': 'Job not found'}), 404
                
                job_data = {
                    'id': job[0],
                    'name': job[1],
                    'network_range': job[2],
                    'status': job[3],
                    'started_at': job[4],
                    'completed_at': job[5],
                    'devices_found': job[6],
                    'devices_added': job[7],
                    'scan_type': job[8],
                    'results': json.loads(job[10]) if job[10] else []
                }
                
                conn.close()
                return jsonify(job_data)
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        # ============ CREDENTIAL MANAGEMENT API ============
        @self.app.route('/api/credentials', methods=['GET'])
        def get_credentials():
            """Get all saved credentials"""
            try:
                credentials = self.credential_manager.get_credentials()
                # Don't return passwords in the response
                for cred in credentials:
                    cred['password'] = '***'
                return jsonify(credentials)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/credentials', methods=['POST'])
        def save_credential():
            """Save new credential"""
            try:
                data = request.get_json()
                name = data.get('name')
                username = data.get('username')
                password = data.get('password')
                cred_type = data.get('type')
                description = data.get('description', '')
                
                if not all([name, username, password, cred_type]):
                    return jsonify({'error': 'All fields are required'}), 400
                
                success = self.credential_manager.save_credential(name, username, password, cred_type, description)
                
                if success:
                    return jsonify({'message': 'Credential saved successfully'})
                else:
                    return jsonify({'error': 'Failed to save credential'}), 500
                    
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/credentials/<int:cred_id>', methods=['DELETE'])
        def delete_credential(cred_id):
            """Delete credential"""
            try:
                success = self.credential_manager.delete_credential(cred_id)
                if success:
                    return jsonify({'message': 'Credential deleted successfully'})
                else:
                    return jsonify({'error': 'Failed to delete credential'}), 500
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        # ============ NETWORK MANAGEMENT API ============
        @self.app.route('/api/networks', methods=['GET'])
        def get_networks():
            """Get all saved networks"""
            try:
                networks = self.credential_manager.get_networks()
                return jsonify(networks)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/networks', methods=['POST'])
        def save_network():
            """Save network configuration"""
            try:
                data = request.get_json()
                name = data.get('name')
                network_range = data.get('range')
                description = data.get('description', '')
                snmp_communities = data.get('snmp_communities', 'public')
                
                if not all([name, network_range]):
                    return jsonify({'error': 'Name and range are required'}), 400
                
                success = self.credential_manager.save_network(name, network_range, description, snmp_communities)
                
                if success:
                    return jsonify({'message': 'Network saved successfully'})
                else:
                    return jsonify({'error': 'Failed to save network'}), 500
                    
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        # ============ ASSET MANAGEMENT API ============
        @self.app.route('/api/devices')
        def api_devices():
            """Get devices with enhanced filtering"""
            try:
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Get query parameters
                search = request.args.get('search', '')
                department = request.args.get('department', '')
                device_type = request.args.get('device_type', '')
                
                # Build query
                where_conditions = []
                params = []
                
                if search:
                    where_conditions.append('''
                        (hostname LIKE ? OR ip_address LIKE ? OR 
                         working_user LIKE ? OR manufacturer LIKE ?)
                    ''')
                    search_param = f'%{search}%'
                    params.extend([search_param] * 4)
                
                if department and department != 'All':
                    where_conditions.append('department = ?')
                    params.append(department)
                
                if device_type and device_type != 'All':
                    where_conditions.append('device_type = ?')
                    params.append(device_type)
                
                where_clause = 'WHERE ' + ' AND '.join(where_conditions) if where_conditions else ''
                
                query = f'''
                    SELECT * FROM assets {where_clause}
                    ORDER BY last_updated DESC, created_at DESC
                    LIMIT 200
                '''
                
                cursor.execute(query, params)
                devices = [dict(row) for row in cursor.fetchall()]
                
                conn.close()
                return jsonify(devices)
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/assets/<int:asset_id>', methods=['DELETE'])
        def delete_asset(asset_id):
            """Delete asset"""
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM assets WHERE id = ?', (asset_id,))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    conn.close()
                    return jsonify({'message': 'Asset deleted successfully'})
                else:
                    conn.close()
                    return jsonify({'error': 'Asset not found'}), 404
                    
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        # ============ STATISTICS API ============
        @self.app.route('/api/stats')
        def api_stats():
            """Get dashboard statistics"""
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Total assets
                cursor.execute('SELECT COUNT(*) FROM assets')
                total_assets = cursor.fetchone()[0]
                
                # Active assets
                cursor.execute("SELECT COUNT(*) FROM assets WHERE status = 'Active'")
                active_assets = cursor.fetchone()[0]
                
                # Device types
                cursor.execute('SELECT device_type, COUNT(*) FROM assets GROUP BY device_type')
                device_types = dict(cursor.fetchall())
                
                # Recent additions (last 24 hours)
                cursor.execute('''
                    SELECT COUNT(*) FROM assets 
                    WHERE created_at > datetime('now', '-1 day')
                ''')
                recent_additions = cursor.fetchone()[0]
                
                conn.close()
                
                return jsonify({
                    'total_assets': total_assets,
                    'active_assets': active_assets,
                    'device_types': device_types,
                    'recent_additions': recent_additions
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
    
    def start_discovery_job(self, scan_name, ip_range, credentials, snmp_communities):
        """Start background discovery job"""
        try:
            # Create job record
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO scan_jobs (job_name, network_range, status, started_at, scan_type, credentials_used)
                VALUES (?, ?, 'running', ?, 'Multi-Protocol', ?)
            ''', (scan_name, ip_range, datetime.now().isoformat(), json.dumps(credentials)))
            
            job_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # Start discovery thread
            discovery_thread = threading.Thread(
                target=self.run_discovery_job, 
                args=(job_id, ip_range, credentials, snmp_communities)
            )
            discovery_thread.daemon = True
            discovery_thread.start()
            
            return job_id
            
        except Exception as e:
            logger.error(f"Error starting discovery job: {e}")
            return None
    
    def run_discovery_job(self, job_id, ip_range, credentials, snmp_communities):
        """Run discovery job in background"""
        try:
            logger.info(f"Starting discovery job {job_id} for range {ip_range}")
            
            # Parse IP range and discover devices
            discovered_devices = []
            
            # Convert credentials to proper format
            cred_list = []
            for cred_name in credentials:
                saved_creds = self.credential_manager.get_credentials()
                for saved_cred in saved_creds:
                    if saved_cred['name'] == cred_name:
                        cred_list.append(saved_cred)
                        break
            
            # Generate IP list from range
            ip_list = self.generate_ip_list(ip_range)
            
            # Discover each IP
            for ip in ip_list:
                try:
                    device_data = multi_protocol_discovery(ip, cred_list, snmp_communities)
                    if device_data:
                        discovered_devices.append(device_data)
                        logger.info(f"✅ Discovered device: {ip}")
                except Exception as e:
                    logger.error(f"Error discovering {ip}: {e}")
                    continue
            
            # Save discovered devices to database
            added_count = 0
            for device in discovered_devices:
                if self.save_discovered_device(device):
                    added_count += 1
            
            # Update job status
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE scan_jobs 
                SET status = 'completed', completed_at = ?, devices_found = ?, 
                    devices_added = ?, results = ?
                WHERE id = ?
            ''', (
                datetime.now().isoformat(),
                len(discovered_devices),
                added_count,
                json.dumps(discovered_devices),
                job_id
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Discovery job {job_id} completed: {len(discovered_devices)} found, {added_count} added")
            
        except Exception as e:
            logger.error(f"Error in discovery job {job_id}: {e}")
            
            # Update job status to failed
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE scan_jobs 
                    SET status = 'failed', completed_at = ?
                    WHERE id = ?
                ''', (datetime.now().isoformat(), job_id))
                conn.commit()
                conn.close()
            except:
                pass
    
    def generate_ip_list(self, ip_range):
        """Generate list of IPs from range specification"""
        ip_list = []
        
        try:
            if '-' in ip_range:
                # Range like 10.0.21.1-50
                base_ip, range_end = ip_range.split('-')
                base_parts = base_ip.strip().split('.')
                start_num = int(base_parts[3])
                end_num = int(range_end.strip())
                base_network = '.'.join(base_parts[:3])
                
                for i in range(start_num, end_num + 1):
                    ip_list.append(f"{base_network}.{i}")
            
            elif '/' in ip_range:
                # CIDR notation like 10.0.21.0/24
                network = ipaddress.IPv4Network(ip_range, strict=False)
                ip_list = [str(ip) for ip in network.hosts()]
            
            else:
                # Single IP
                ip_list = [ip_range.strip()]
        
        except Exception as e:
            logger.error(f"Error parsing IP range {ip_range}: {e}")
        
        return ip_list
    
    def save_discovered_device(self, device_data):
        """Save discovered device to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if device already exists
            cursor.execute('SELECT id FROM assets WHERE ip_address = ?', (device_data['ip_address'],))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing device
                cursor.execute('''
                    UPDATE assets SET
                        hostname = ?, working_user = ?, domain = ?, workgroup = ?,
                        manufacturer = ?, model = ?, serial_number = ?, os_name = ?,
                        operating_system = ?, memory_gb = ?, cpu_cores = ?,
                        processor_name = ?, bios_version = ?, chassis_type = ?,
                        device_type = ?, classification = ?, collection_method = ?,
                        data_source = ?, last_updated = ?, last_scanned = ?
                    WHERE ip_address = ?
                ''', (
                    device_data.get('hostname'),
                    device_data.get('working_user'),
                    device_data.get('domain'),
                    device_data.get('workgroup'),
                    device_data.get('manufacturer'),
                    device_data.get('model'),
                    device_data.get('serial_number'),
                    device_data.get('os_name'),
                    device_data.get('operating_system'),
                    device_data.get('memory_gb'),
                    device_data.get('cpu_cores'),
                    device_data.get('processor_name'),
                    device_data.get('bios_version'),
                    device_data.get('chassis_type'),
                    device_data.get('device_type'),
                    device_data.get('classification'),
                    device_data.get('collection_method'),
                    device_data.get('data_source'),
                    device_data.get('last_updated'),
                    datetime.now().isoformat(),
                    device_data['ip_address']
                ))
            else:
                # Insert new device
                cursor.execute('''
                    INSERT INTO assets (
                        ip_address, hostname, working_user, domain, workgroup,
                        manufacturer, model, serial_number, os_name, operating_system,
                        memory_gb, cpu_cores, processor_name, bios_version, chassis_type,
                        device_type, classification, collection_method, data_source,
                        last_updated, last_scanned
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    device_data['ip_address'],
                    device_data.get('hostname'),
                    device_data.get('working_user'),
                    device_data.get('domain'),
                    device_data.get('workgroup'),
                    device_data.get('manufacturer'),
                    device_data.get('model'),
                    device_data.get('serial_number'),
                    device_data.get('os_name'),
                    device_data.get('operating_system'),
                    device_data.get('memory_gb'),
                    device_data.get('cpu_cores'),
                    device_data.get('processor_name'),
                    device_data.get('bios_version'),
                    device_data.get('chassis_type'),
                    device_data.get('device_type'),
                    device_data.get('classification'),
                    device_data.get('collection_method'),
                    device_data.get('data_source'),
                    device_data.get('last_updated'),
                    datetime.now().isoformat()
                ))
            
            conn.commit()
            conn.close()
            return True
            
            
        except Exception as e:
            logger.error(f"Error saving device {device_data.get('ip_address')}: {e}")
            return False
    
    def get_production_dashboard_template(self):
        """Production dashboard template"""
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏢 Production Asset Management System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
        }
        .hero-header {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            color: white;
            padding: 2rem 0;
            margin-bottom: 2rem;
            border-bottom: 1px solid rgba(255,255,255,0.2);
        }
        .stat-card {
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            padding: 1.5rem;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
            transition: transform 0.3s ease;
        }
        .stat-card:hover {
            transform: translateY(-5px);
        }
        .device-table {
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
        }
        .btn-production {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            font-weight: 600;
        }
        .btn-production:hover {
            background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
            color: white;
        }
        .production-badge {
            background: #28a745;
            color: white;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="hero-header">
        <div class="container">
            <div class="row align-items-center">
                <div class="col-md-8">
                    <h1><i class="fas fa-building"></i> Production Asset Management System</h1>
                    <p class="mb-0">
                        <span class="production-badge">PRODUCTION</span>
                        Enterprise Multi-Protocol Discovery & Asset Management
                    </p>
                </div>
                <div class="col-md-4 text-end">
                    <div class="btn-group">
                        <a href="/add-asset" class="btn btn-production"><i class="fas fa-plus"></i> Add Assets</a>
                        <a href="/credentials" class="btn btn-production"><i class="fas fa-key"></i> Credentials</a>
                        <a href="/networks" class="btn btn-production"><i class="fas fa-network-wired"></i> Networks</a>
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
                    <div style="font-size: 2.5rem; color: #667eea;">📊</div>
                    <div style="font-size: 2rem; font-weight: bold; color: #333;" id="totalAssets">0</div>
                    <div style="color: #666; font-size: 0.9rem;">Total Assets</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card">
                    <div style="font-size: 2.5rem; color: #28a745;">✅</div>
                    <div style="font-size: 2rem; font-weight: bold; color: #333;" id="activeAssets">0</div>
                    <div style="color: #666; font-size: 0.9rem;">Active Assets</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card">
                    <div style="font-size: 2.5rem; color: #ffc107;">🖥️</div>
                    <div style="font-size: 2rem; font-weight: bold; color: #333;" id="deviceTypes">0</div>
                    <div style="color: #666; font-size: 0.9rem;">Device Types</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card">
                    <div style="font-size: 2.5rem; color: #17a2b8;">🆕</div>
                    <div style="font-size: 2rem; font-weight: bold; color: #333;" id="recentAdded">0</div>
                    <div style="color: #666; font-size: 0.9rem;">Added Today</div>
                </div>
            </div>
        </div>

        <!-- Search and Filters -->
        <div class="row mb-3">
            <div class="col-md-4">
                <input type="text" class="form-control" id="searchInput" placeholder="🔍 Search assets...">
            </div>
            <div class="col-md-3">
                <select class="form-select" id="deviceTypeFilter">
                    <option value="">All Device Types</option>
                    <option value="Workstation">Workstations</option>
                    <option value="Server">Servers</option>
                    <option value="Switch">Switches</option>
                    <option value="Firewall/Router">Firewalls/Routers</option>
                    <option value="Printer">Printers</option>
                </select>
            </div>
            <div class="col-md-3">
                <select class="form-select" id="departmentFilter">
                    <option value="">All Departments</option>
                </select>
            </div>
            <div class="col-md-2">
                <button class="btn btn-production w-100" onclick="refreshData()">
                    <i class="fas fa-sync-alt"></i> Refresh
                </button>
            </div>
        </div>

        <!-- Assets Table -->
        <div class="device-table">
            <div class="table-responsive">
                <table class="table table-hover mb-0">
                    <thead style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                        <tr>
                            <th>Device Info</th>
                            <th>Network</th>
                            <th>User & Domain</th>
                            <th>Hardware</th>
                            <th>System</th>
                            <th>Type</th>
                            <th>Collection</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="devicesTableBody">
                        <tr>
                            <td colspan="8" class="text-center py-4">
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
        document.addEventListener('DOMContentLoaded', function() {
            loadStats();
            loadDevices();
            
            // Setup auto-refresh every 30 seconds
            setInterval(refreshData, 30000);
            
            // Setup search
            document.getElementById('searchInput').addEventListener('input', debounce(loadDevices, 500));
            document.getElementById('deviceTypeFilter').addEventListener('change', loadDevices);
            document.getElementById('departmentFilter').addEventListener('change', loadDevices);
        });
        
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
        
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const stats = await response.json();
                
                document.getElementById('totalAssets').textContent = stats.total_assets;
                document.getElementById('activeAssets').textContent = stats.active_assets;
                document.getElementById('deviceTypes').textContent = Object.keys(stats.device_types).length;
                document.getElementById('recentAdded').textContent = stats.recent_additions;
                
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }
        
        async function loadDevices() {
            try {
                const params = new URLSearchParams({
                    search: document.getElementById('searchInput').value,
                    device_type: document.getElementById('deviceTypeFilter').value,
                    department: document.getElementById('departmentFilter').value
                });
                
                const response = await fetch(`/api/devices?${params}`);
                const devices = await response.json();
                
                displayDevices(devices);
                
            } catch (error) {
                console.error('Error loading devices:', error);
            }
        }
        
        function displayDevices(devices) {
            const tbody = document.getElementById('devicesTableBody');
            
            if (devices.length === 0) {
                tbody.innerHTML = '<tr><td colspan="8" class="text-center">No devices found</td></tr>';
                return;
            }
            
            tbody.innerHTML = devices.map(device => `
                <tr>
                    <td>
                        <strong>${device.hostname || device.ip_address}</strong><br>
                        <small class="text-muted">ID: ${device.id}</small>
                    </td>
                    <td>
                        <span class="badge bg-primary">${device.ip_address}</span>
                    </td>
                    <td>
                        ${device.working_user || 'N/A'}<br>
                        <small class="text-muted">${device.domain || device.workgroup || 'No Domain'}</small>
                    </td>
                    <td>
                        ${device.manufacturer || 'Unknown'}<br>
                        <small class="text-muted">${device.model || 'Unknown'}</small>
                    </td>
                    <td>
                        ${device.os_name || device.operating_system || 'Unknown'}<br>
                        <small class="text-muted">${device.memory_gb ? device.memory_gb + ' GB RAM' : 'Unknown'}</small>
                    </td>
                    <td>
                        <span class="badge bg-info">${device.device_type || 'Unknown'}</span>
                    </td>
                    <td>
                        <small>${device.collection_method || 'Unknown'}</small><br>
                        <small class="text-muted">${device.last_scanned ? new Date(device.last_scanned).toLocaleDateString() : 'Never'}</small>
                    </td>
                    <td>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-danger" onclick="deleteDevice(${device.id})" title="Delete">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `).join('');
        }
        
        async function deleteDevice(deviceId) {
            if (!confirm('Are you sure you want to delete this device?')) return;
            
            try {
                const response = await fetch(`/api/assets/${deviceId}`, {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    loadDevices();
                } else {
                    alert('Failed to delete device');
                }
            } catch (error) {
                alert('Error deleting device');
            }
        }
        
        function refreshData() {
            loadStats();
            loadDevices();
        }
    </script>
</body>
</html>
        '''
    
    def get_enhanced_add_asset_template(self):
        """Enhanced add asset template with smart discovery"""
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔍 Smart Asset Discovery</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
        }
        .hero-header {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            color: white;
            padding: 2rem 0;
            margin-bottom: 2rem;
        }
        .discovery-card {
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            padding: 2rem;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            margin-bottom: 2rem;
        }
        .btn-discovery {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            border: none;
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            font-weight: 600;
        }
        .protocol-badge {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            margin: 0.25rem;
            border-radius: 4px;
            font-size: 0.8rem;
        }
        .protocol-wmi { background: #007bff; color: white; }
        .protocol-ssh { background: #28a745; color: white; }
        .protocol-snmp { background: #ffc107; color: black; }
    </style>
</head>
<body>
    <div class="hero-header">
        <div class="container">
            <div class="row align-items-center">
                <div class="col-md-8">
                    <h1><i class="fas fa-search-plus"></i> Smart Asset Discovery</h1>
                    <p class="mb-0">Multi-Protocol Network Discovery Engine</p>
                </div>
                <div class="col-md-4 text-end">
                    <a href="/" class="btn btn-outline-light">
                        <i class="fas fa-arrow-left"></i> Back to Dashboard
                    </a>
                </div>
            </div>
        </div>
    </div>

    <div class="container">
        <!-- Discovery Configuration -->
        <div class="discovery-card">
            <h3><i class="fas fa-cogs"></i> Discovery Configuration</h3>
            <p class="text-muted">Configure network range and protocols for asset discovery</p>
            
            <div class="row">
                <div class="col-md-6">
                    <div class="mb-3">
                        <label class="form-label">Network Range</label>
                        <div class="input-group">
                            <span class="input-group-text"><i class="fas fa-network-wired"></i></span>
                            <select class="form-select" id="savedNetworks" onchange="loadSavedNetwork()">
                                <option value="">Select saved network...</option>
                            </select>
                        </div>
                    </div>
                    <div class="mb-3">
                        <input type="text" class="form-control" id="networkRange" 
                               placeholder="10.0.21.1-50 or 192.168.1.0/24" 
                               value="10.0.21.1-50">
                        <div class="form-text">Support: Range (10.0.21.1-50), CIDR (192.168.1.0/24), Single IP</div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="mb-3">
                        <label class="form-label">Discovery Protocols</label>
                        <div>
                            <span class="protocol-badge protocol-snmp">SNMP (Switches, Firewalls, Printers)</span>
                            <span class="protocol-badge protocol-wmi">WMI (Windows)</span>
                            <span class="protocol-badge protocol-ssh">SSH (Linux/Unix)</span>
                        </div>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">SNMP Communities</label>
                        <input type="text" class="form-control" id="snmpCommunities" 
                               value="public,private" placeholder="public,private">
                    </div>
                </div>
            </div>
        </div>

        <!-- Credentials Selection -->
        <div class="discovery-card">
            <h3><i class="fas fa-key"></i> Authentication Credentials</h3>
            <p class="text-muted">Select saved credentials for device authentication</p>
            
            <div class="row" id="credentialsList">
                <div class="col-12 text-muted">Loading credentials...</div>
            </div>
            
            <div class="mt-3">
                <a href="/credentials" class="btn btn-outline-primary">
                    <i class="fas fa-plus"></i> Manage Credentials
                </a>
            </div>
        </div>

        <!-- Discovery Controls -->
        <div class="discovery-card text-center">
            <button class="btn btn-discovery btn-lg" onclick="startDiscovery()" id="discoveryBtn">
                <i class="fas fa-search"></i> Start Smart Discovery
            </button>
            
            <div id="discoveryProgress" style="display: none;" class="mt-3">
                <div class="spinner-border text-primary" role="status"></div>
                <p class="mt-2">Discovering devices...</p>
                <div class="progress">
                    <div class="progress-bar progress-bar-striped progress-bar-animated" 
                         role="progressbar" style="width: 0%" id="discoveryProgressBar"></div>
                </div>
            </div>
        </div>

        <!-- Discovery Results -->
        <div class="discovery-card" id="discoveryResults" style="display: none;">
            <h3><i class="fas fa-list"></i> Discovered Devices</h3>
            <div id="discoveredDevicesList"></div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let discoveryJobId = null;
        
        document.addEventListener('DOMContentLoaded', function() {
            loadCredentials();
            loadSavedNetworks();
        });
        
        async function loadCredentials() {
            try {
                const response = await fetch('/api/credentials');
                const credentials = await response.json();
                
                const container = document.getElementById('credentialsList');
                
                if (credentials.length === 0) {
                    container.innerHTML = `
                        <div class="col-12 text-center">
                            <p>No credentials saved. <a href="/credentials">Add credentials</a> first.</p>
                        </div>
                    `;
                    return;
                }
                
                container.innerHTML = credentials.map(cred => `
                    <div class="col-md-4 mb-3">
                        <div class="card">
                            <div class="card-body">
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" 
                                           value="${cred.name}" id="cred_${cred.id}">
                                    <label class="form-check-label" for="cred_${cred.id}">
                                        <strong>${cred.name}</strong><br>
                                        <small class="text-muted">${cred.type} - ${cred.username}</small><br>
                                        <small>${cred.description}</small>
                                    </label>
                                </div>
                            </div>
                        </div>
                    </div>
                `).join('');
                
            } catch (error) {
                console.error('Error loading credentials:', error);
            }
        }
        
        async function loadSavedNetworks() {
            try {
                const response = await fetch('/api/networks');
                const networks = await response.json();
                
                const select = document.getElementById('savedNetworks');
                select.innerHTML = '<option value="">Select saved network...</option>';
                
                networks.forEach(network => {
                    const option = document.createElement('option');
                    option.value = network.id;
                    option.textContent = `${network.name} (${network.range})`;
                    option.dataset.range = network.range;
                    option.dataset.communities = network.snmp_communities;
                    select.appendChild(option);
                });
                
            } catch (error) {
                console.error('Error loading networks:', error);
            }
        }
        
        function loadSavedNetwork() {
            const select = document.getElementById('savedNetworks');
            const selectedOption = select.options[select.selectedIndex];
            
            if (selectedOption.value) {
                document.getElementById('networkRange').value = selectedOption.dataset.range;
                document.getElementById('snmpCommunities').value = selectedOption.dataset.communities;
            }
        }
        
        async function startDiscovery() {
            const networkRange = document.getElementById('networkRange').value.trim();
            const snmpCommunities = document.getElementById('snmpCommunities').value.split(',').map(c => c.trim());
            
            // Get selected credentials
            const selectedCredentials = [];
            document.querySelectorAll('#credentialsList input[type="checkbox"]:checked').forEach(checkbox => {
                selectedCredentials.push(checkbox.value);
            });
            
            if (!networkRange) {
                alert('Please enter a network range');
                return;
            }
            
            if (selectedCredentials.length === 0) {
                alert('Please select at least one credential set');
                return;
            }
            
            // Show progress
            document.getElementById('discoveryBtn').disabled = true;
            document.getElementById('discoveryProgress').style.display = 'block';
            document.getElementById('discoveryResults').style.display = 'none';
            
            try {
                const response = await fetch('/api/scan/discover', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        ip_range: networkRange,
                        credentials: selectedCredentials,
                        snmp_communities: snmpCommunities,
                        scan_name: `Discovery_${new Date().toISOString().slice(0,19).replace(/:/g,'-')}`
                    })
                });
                
                if (response.ok) {
                    const result = await response.json();
                    discoveryJobId = result.job_id;
                    
                    // Poll for results
                    pollDiscoveryStatus();
                } else {
                    const error = await response.json();
                    alert(`Discovery failed: ${error.error}`);
                    resetDiscoveryUI();
                }
                
            } catch (error) {
                alert(`Error starting discovery: ${error.message}`);
                resetDiscoveryUI();
            }
        }
        
        async function pollDiscoveryStatus() {
            if (!discoveryJobId) return;
            
            try {
                const response = await fetch(`/api/scan/status/${discoveryJobId}`);
                const status = await response.json();
                
                if (status.status === 'completed') {
                    showDiscoveryResults(status);
                    resetDiscoveryUI();
                } else if (status.status === 'failed') {
                    alert('Discovery job failed');
                    resetDiscoveryUI();
                } else {
                    // Still running, poll again
                    setTimeout(pollDiscoveryStatus, 3000);
                }
                
            } catch (error) {
                console.error('Error polling status:', error);
                setTimeout(pollDiscoveryStatus, 5000);
            }
        }
        
        function showDiscoveryResults(jobStatus) {
            const resultsDiv = document.getElementById('discoveryResults');
            const devicesList = document.getElementById('discoveredDevicesList');
            
            if (jobStatus.devices_found === 0) {
                devicesList.innerHTML = '<div class="alert alert-info">No devices discovered in the specified range.</div>';
            } else {
                const devices = jobStatus.results || [];
                devicesList.innerHTML = `
                    <div class="alert alert-success">
                        <strong>Discovery Complete!</strong><br>
                        Found: ${jobStatus.devices_found} devices<br>
                        Added to database: ${jobStatus.devices_added} devices
                    </div>
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>IP Address</th>
                                    <th>Hostname</th>
                                    <th>Device Type</th>
                                    <th>Manufacturer</th>
                                    <th>Collection Method</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${devices.map(device => `
                                    <tr>
                                        <td>${device.ip_address}</td>
                                        <td>${device.hostname || 'Unknown'}</td>
                                        <td><span class="badge bg-info">${device.device_type || 'Unknown'}</span></td>
                                        <td>${device.manufacturer || 'Unknown'}</td>
                                        <td><span class="badge bg-secondary">${device.collection_method}</span></td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                `;
            }
            
            resultsDiv.style.display = 'block';
        }
        
        function resetDiscoveryUI() {
            document.getElementById('discoveryBtn').disabled = false;
            document.getElementById('discoveryProgress').style.display = 'none';
            discoveryJobId = null;
        }
    </script>
</body>
</html>
        '''
    
    def get_credentials_template(self):
        """Credential management template"""
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔐 Credential Management</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
        }
        .hero-header {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            color: white;
            padding: 2rem 0;
            margin-bottom: 2rem;
        }
        .credential-card {
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            padding: 2rem;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            margin-bottom: 2rem;
        }
    </style>
</head>
<body>
    <div class="hero-header">
        <div class="container">
            <div class="row align-items-center">
                <div class="col-md-8">
                    <h1><i class="fas fa-key"></i> Credential Management</h1>
                    <p class="mb-0">Manage authentication credentials for device discovery</p>
                </div>
                <div class="col-md-4 text-end">
                    <a href="/" class="btn btn-outline-light">
                        <i class="fas fa-arrow-left"></i> Back to Dashboard
                    </a>
                </div>
            </div>
        </div>
    </div>

    <div class="container">
        <!-- Add Credential Form -->
        <div class="credential-card">
            <h3><i class="fas fa-plus"></i> Add New Credential</h3>
            <form id="credentialForm">
                <div class="row">
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label class="form-label">Credential Name</label>
                            <input type="text" class="form-control" id="credName" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Username</label>
                            <input type="text" class="form-control" id="credUsername" required>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label class="form-label">Password</label>
                            <input type="password" class="form-control" id="credPassword" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Type</label>
                            <select class="form-select" id="credType" required>
                                <option value="">Select type...</option>
                                <option value="wmi">WMI (Windows)</option>
                                <option value="ssh">SSH (Linux/Unix)</option>
                                <option value="snmp">SNMP</option>
                            </select>
                        </div>
                    </div>
                </div>
                <div class="mb-3">
                    <label class="form-label">Description</label>
                    <input type="text" class="form-control" id="credDescription" 
                           placeholder="Optional description...">
                </div>
                <button type="submit" class="btn btn-primary">
                    <i class="fas fa-save"></i> Save Credential
                </button>
            </form>
        </div>

        <!-- Saved Credentials -->
        <div class="credential-card">
            <h3><i class="fas fa-list"></i> Saved Credentials</h3>
            <div id="credentialsList"></div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            loadCredentials();
            
            document.getElementById('credentialForm').addEventListener('submit', function(e) {
                e.preventDefault();
                saveCredential();
            });
        });
        
        async function saveCredential() {
            const formData = {
                name: document.getElementById('credName').value,
                username: document.getElementById('credUsername').value,
                password: document.getElementById('credPassword').value,
                type: document.getElementById('credType').value,
                description: document.getElementById('credDescription').value
            };
            
            try {
                const response = await fetch('/api/credentials', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(formData)
                });
                
                if (response.ok) {
                    alert('Credential saved successfully!');
                    document.getElementById('credentialForm').reset();
                    loadCredentials();
                } else {
                    const error = await response.json();
                    alert(`Error: ${error.error}`);
                }
            } catch (error) {
                alert(`Error saving credential: ${error.message}`);
            }
        }
        
        async function loadCredentials() {
            try {
                const response = await fetch('/api/credentials');
                const credentials = await response.json();
                
                const container = document.getElementById('credentialsList');
                
                if (credentials.length === 0) {
                    container.innerHTML = '<div class="alert alert-info">No credentials saved yet.</div>';
                    return;
                }
                
                container.innerHTML = `
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Username</th>
                                    <th>Type</th>
                                    <th>Description</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${credentials.map(cred => `
                                    <tr>
                                        <td><strong>${cred.name}</strong></td>
                                        <td>${cred.username}</td>
                                        <td><span class="badge bg-info">${cred.type}</span></td>
                                        <td>${cred.description || '-'}</td>
                                        <td>
                                            <button class="btn btn-danger btn-sm" onclick="deleteCredential(${cred.id})">
                                                <i class="fas fa-trash"></i>
                                            </button>
                                        </td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                `;
                
            } catch (error) {
                console.error('Error loading credentials:', error);
            }
        }
        
        async function deleteCredential(credId) {
            if (!confirm('Are you sure you want to delete this credential?')) return;
            
            try {
                const response = await fetch(`/api/credentials/${credId}`, {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    loadCredentials();
                } else {
                    alert('Failed to delete credential');
                }
            } catch (error) {
                alert('Error deleting credential');
            }
        }
    </script>
</body>
</html>
        '''
    
    def get_networks_template(self):
        """Network management template"""
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌐 Network Management</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
        }
        .hero-header {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            color: white;
            padding: 2rem 0;
            margin-bottom: 2rem;
        }
        .network-card {
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            padding: 2rem;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            margin-bottom: 2rem;
        }
    </style>
</head>
<body>
    <div class="hero-header">
        <div class="container">
            <div class="row align-items-center">
                <div class="col-md-8">
                    <h1><i class="fas fa-network-wired"></i> Network Management</h1>
                    <p class="mb-0">Manage network ranges for asset discovery</p>
                </div>
                <div class="col-md-4 text-end">
                    <a href="/" class="btn btn-outline-light">
                        <i class="fas fa-arrow-left"></i> Back to Dashboard
                    </a>
                </div>
            </div>
        </div>
    </div>

    <div class="container">
        <!-- Add Network Form -->
        <div class="network-card">
            <h3><i class="fas fa-plus"></i> Add New Network</h3>
            <form id="networkForm">
                <div class="row">
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label class="form-label">Network Name</label>
                            <input type="text" class="form-control" id="networkName" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Network Range</label>
                            <input type="text" class="form-control" id="networkRange" 
                                   placeholder="10.0.21.1-50 or 192.168.1.0/24" required>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label class="form-label">SNMP Communities</label>
                            <input type="text" class="form-control" id="snmpCommunities" 
                                   value="public,private" placeholder="public,private">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Description</label>
                            <input type="text" class="form-control" id="networkDescription" 
                                   placeholder="Optional description...">
                        </div>
                    </div>
                </div>
                <button type="submit" class="btn btn-primary">
                    <i class="fas fa-save"></i> Save Network
                </button>
            </form>
        </div>

        <!-- Saved Networks -->
        <div class="network-card">
            <h3><i class="fas fa-list"></i> Saved Networks</h3>
            <div id="networksList"></div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            loadNetworks();
            
            document.getElementById('networkForm').addEventListener('submit', function(e) {
                e.preventDefault();
                saveNetwork();
            });
        });
        
        async function saveNetwork() {
            const formData = {
                name: document.getElementById('networkName').value,
                range: document.getElementById('networkRange').value,
                description: document.getElementById('networkDescription').value,
                snmp_communities: document.getElementById('snmpCommunities').value
            };
            
            try {
                const response = await fetch('/api/networks', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(formData)
                });
                
                if (response.ok) {
                    alert('Network saved successfully!');
                    document.getElementById('networkForm').reset();
                    loadNetworks();
                } else {
                    const error = await response.json();
                    alert(`Error: ${error.error}`);
                }
            } catch (error) {
                alert(`Error saving network: ${error.message}`);
            }
        }
        
        async function loadNetworks() {
            try {
                const response = await fetch('/api/networks');
                const networks = await response.json();
                
                const container = document.getElementById('networksList');
                
                if (networks.length === 0) {
                    container.innerHTML = '<div class="alert alert-info">No networks saved yet.</div>';
                    return;
                }
                
                container.innerHTML = `
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Range</th>
                                    <th>SNMP Communities</th>
                                    <th>Description</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${networks.map(network => `
                                    <tr>
                                        <td><strong>${network.name}</strong></td>
                                        <td><code>${network.range}</code></td>
                                        <td>${network.snmp_communities}</td>
                                        <td>${network.description || '-'}</td>
                                        <td>
                                            <a href="/add-asset" class="btn btn-success btn-sm">
                                                <i class="fas fa-search"></i> Scan
                                            </a>
                                        </td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                `;
                
            } catch (error) {
                console.error('Error loading networks:', error);
            }
        }
    </script>
</body>
</html>
        '''
    
    def run(self):
        """Run the production web service"""
        logger.info(f"🚀 Starting Production Asset Management Service")
        logger.info(f"🌐 Server: {self.host}:{self.port}")
        logger.info(f"📊 Database: {self.db_path}")
        logger.info(f"🔐 Credentials: {self.credential_manager.db_path}")
        
        # Production configuration
        self.app.run(
            host=self.host,
            port=self.port,
            debug=False,  # Production mode
            threaded=True,
            use_reloader=False
        )

if __name__ == "__main__":
    service = ProductionAssetManagementService()
    service.run()