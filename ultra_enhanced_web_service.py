#!/usr/bin/env python3
"""
Enhanced Web Service for Asset Management
Improved display with comprehensive device fields
واجهة الويب المحسنة مع عرض كامل للأجهزة
"""

from flask import Flask, render_template_string, jsonify, request, redirect, url_for
import sqlite3
import json
import logging
from datetime import datetime
import os
import socket
import subprocess
import threading
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - WebService - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
DATABASE_PATH = "assets.db"
HOST = "0.0.0.0"
PORT = 8080

def get_database_connection():
    """Get database connection with row factory"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return None

def log_access(request, endpoint=""):
    """Log access attempts"""
    client_ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', 'Unknown')[:100]
    endpoint = endpoint or request.endpoint or request.path
    logger.info(f"ACCESS: {client_ip} -> {request.method} {endpoint} | UA: {user_agent}")

@app.route('/')
def dashboard():
    """Enhanced dashboard with comprehensive device display"""
    log_access(request)
    return render_template_string(ENHANCED_DASHBOARD_TEMPLATE)

@app.route('/api/stats')
def api_stats():
    """Get system statistics"""
    log_access(request, "/api/stats")
    
    conn = get_database_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor()
        
        # Basic counts
        cursor.execute("SELECT COUNT(*) FROM assets")
        total_devices = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM assets WHERE status = 'Active'")
        active_devices = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM assets WHERE ping_status = 'Online'")
        online_devices = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM departments")
        total_departments = cursor.fetchone()[0]
        
        # Device type breakdown
        cursor.execute("""
            SELECT device_type, COUNT(*) as count 
            FROM assets 
            WHERE device_type IS NOT NULL AND device_type != 'Unknown'
            GROUP BY device_type 
            ORDER BY count DESC
        """)
        device_types = [{"type": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        # Health status breakdown
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN ping_status = 'Online' THEN 1 ELSE 0 END) as online,
                SUM(CASE WHEN ping_status = 'Offline' THEN 1 ELSE 0 END) as offline,
                SUM(CASE WHEN ping_status = 'Unknown' OR ping_status IS NULL THEN 1 ELSE 0 END) as unknown
            FROM assets
        """)
        health_row = cursor.fetchone()
        health_status = {
            "online": health_row[0] or 0,
            "offline": health_row[1] or 0,
            "unknown": health_row[2] or 0
        }
        
        # Data quality metrics
        cursor.execute("""
            SELECT 
                AVG(CASE WHEN data_quality_score IS NOT NULL THEN data_quality_score ELSE 0 END) as avg_quality,
                COUNT(CASE WHEN collection_method = 'WMI' THEN 1 END) as wmi_collected,
                COUNT(CASE WHEN collection_method = 'SSH' THEN 1 END) as ssh_collected,
                COUNT(CASE WHEN collection_method = 'SNMP' THEN 1 END) as snmp_collected
            FROM assets
        """)
        quality_row = cursor.fetchone()
        data_quality = {
            "average_score": round(quality_row[0] or 0, 1),
            "wmi_devices": quality_row[1] or 0,
            "ssh_devices": quality_row[2] or 0,
            "snmp_devices": quality_row[3] or 0
        }
        
        return jsonify({
            "total_devices": total_devices,
            "active_devices": active_devices,
            "online_devices": online_devices,
            "total_departments": total_departments,
            "device_types": device_types,
            "health_status": health_status,
            "data_quality": data_quality,
            "uptime_percentage": round((online_devices / max(total_devices, 1)) * 100, 1)
        })
        
    except Exception as e:
        logger.error(f"Stats API error: {e}")
        return jsonify({"error": "Failed to fetch statistics"}), 500
    finally:
        conn.close()

@app.route('/api/devices')
def api_devices():
    """Get devices with enhanced filtering and comprehensive data"""
    log_access(request, "/api/devices")
    
    conn = get_database_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor()
        
        # Get filter parameters
        search = request.args.get('search', '').strip()
        department = request.args.get('department', '').strip()
        device_type = request.args.get('device_type', '').strip()
        status = request.args.get('status', '').strip()
        collection_method = request.args.get('collection_method', '').strip()
        limit = min(int(request.args.get('limit', 100)), 1000)
        offset = int(request.args.get('offset', 0))
        
        # Build dynamic query
        base_query = """
            SELECT 
                id, hostname, ip_address, device_type, device_model, device_vendor,
                department, status, ping_status, last_seen, collection_method,
                cpu_model, total_memory, total_disk_space, os_name, os_version,
                mac_address, serial_number, asset_tag, data_quality_score,
                cpu_usage_percent, memory_usage_percent, disk_usage_percent,
                network_utilization, firewall_status, security_software,
                collection_source, last_updated, business_criticality,
                risk_score, performance_score
            FROM assets
            WHERE 1=1
        """
        
        params = []
        
        if search:
            base_query += " AND (hostname LIKE ? OR ip_address LIKE ? OR device_model LIKE ? OR serial_number LIKE ?)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param, search_param])
        
        if department:
            base_query += " AND department = ?"
            params.append(department)
        
        if device_type:
            base_query += " AND device_type = ?"
            params.append(device_type)
        
        if status:
            base_query += " AND status = ?"
            params.append(status)
        
        if collection_method:
            base_query += " AND collection_method = ?"
            params.append(collection_method)
        
        base_query += " ORDER BY hostname LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(base_query, params)
        devices = []
        
        for row in cursor.fetchall():
            device = dict(row)
            
            # Format display data
            device['display_name'] = device['hostname'] or device['ip_address'] or 'Unknown'
            device['device_info'] = f"{device['device_vendor'] or 'Unknown'} {device['device_model'] or ''}"
            device['os_info'] = f"{device['os_name'] or 'Unknown'} {device['os_version'] or ''}"
            
            # Status indicators
            device['status_color'] = get_status_color(device['status'], device['ping_status'])
            device['quality_level'] = get_quality_level(device['data_quality_score'])
            
            # Performance metrics (safely handle None values)
            device['performance'] = {
                'cpu': safe_round(device['cpu_usage_percent']),
                'memory': safe_round(device['memory_usage_percent']),
                'disk': safe_round(device['disk_usage_percent']),
                'overall_score': device['performance_score'] or 0
            }
            
            # Security status
            device['security'] = {
                'firewall': device['firewall_status'] or 'Unknown',
                'antivirus': bool(device['security_software']),
                'risk_level': get_risk_level(device['risk_score'])
            }
            
            # Format memory and storage
            device['formatted_memory'] = format_storage(device['total_memory'])
            device['formatted_storage'] = format_storage(device['total_disk_space'])
            
            devices.append(device)
        
        # Get total count for pagination
        count_query = "SELECT COUNT(*) FROM assets WHERE 1=1"
        count_params = []
        
        if search:
            count_query += " AND (hostname LIKE ? OR ip_address LIKE ? OR device_model LIKE ? OR serial_number LIKE ?)"
            count_params.extend([search_param, search_param, search_param, search_param])
        
        if department:
            count_query += " AND department = ?"
            count_params.append(department)
        
        if device_type:
            count_query += " AND device_type = ?"
            count_params.append(device_type)
        
        if status:
            count_query += " AND status = ?"
            count_params.append(status)
        
        if collection_method:
            count_query += " AND collection_method = ?"
            count_params.append(collection_method)
        
        cursor.execute(count_query, count_params)
        total_count = cursor.fetchone()[0]
        
        return jsonify({
            "devices": devices,
            "total_count": total_count,
            "page_size": limit,
            "offset": offset,
            "has_more": (offset + limit) < total_count
        })
        
    except Exception as e:
        logger.error(f"Devices API error: {e}")
        return jsonify({"error": "Failed to fetch devices"}), 500
    finally:
        conn.close()

@app.route('/api/devices/<int:device_id>')
def api_device_details(device_id):
    """Get comprehensive device details"""
    log_access(request, f"/api/devices/{device_id}")
    
    conn = get_database_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM assets WHERE id = ?", (device_id,))
        row = cursor.fetchone()
        
        if not row:
            return jsonify({"error": "Device not found"}), 404
        
        device = dict(row)
        
        # Organize data into logical sections
        organized_data = {
            "basic_info": {
                "hostname": device.get('hostname'),
                "ip_address": device.get('ip_address'),
                "device_type": device.get('device_type'),
                "device_vendor": device.get('device_vendor'),
                "device_model": device.get('device_model'),
                "serial_number": device.get('serial_number'),
                "asset_tag": device.get('asset_tag'),
                "mac_address": device.get('mac_address')
            },
            "location_info": {
                "department": device.get('department'),
                "location": device.get('location'),
                "building": device.get('building'),
                "floor": device.get('floor'),
                "room": device.get('room'),
                "assigned_user": device.get('assigned_user')
            },
            "system_info": {
                "os_name": device.get('os_name'),
                "os_version": device.get('os_version'),
                "os_build": device.get('os_build'),
                "os_architecture": device.get('os_architecture'),
                "os_install_date": device.get('os_install_date'),
                "last_boot_time": device.get('last_boot_time'),
                "uptime": device.get('uptime'),
                "system_manufacturer": device.get('system_manufacturer'),
                "system_model": device.get('system_model')
            },
            "hardware_info": {
                "cpu_model": device.get('cpu_model'),
                "cpu_cores": device.get('cpu_cores'),
                "cpu_threads": device.get('cpu_threads'),
                "cpu_speed": device.get('cpu_speed'),
                "total_memory": device.get('total_memory'),
                "total_disk_space": device.get('total_disk_space'),
                "motherboard": device.get('motherboard'),
                "bios_version": device.get('bios_version'),
                "bios_date": device.get('bios_date')
            },
            "network_info": {
                "ip_address_v6": device.get('ip_address_v6'),
                "subnet_mask": device.get('subnet_mask'),
                "gateway": device.get('gateway'),
                "dns_servers": device.get('dns_servers'),
                "domain_name": device.get('domain_name'),
                "network_adapter": device.get('network_adapter'),
                "listening_ports": parse_json_field(device.get('listening_ports'))
            },
            "performance_info": {
                "cpu_usage_percent": device.get('cpu_usage_percent'),
                "memory_usage_percent": device.get('memory_usage_percent'),
                "disk_usage_percent": device.get('disk_usage_percent'),
                "network_utilization": device.get('network_utilization'),
                "system_load": device.get('system_load'),
                "performance_score": device.get('performance_score')
            },
            "security_info": {
                "firewall_status": device.get('firewall_status'),
                "security_software": device.get('security_software'),
                "windows_updates": device.get('windows_updates'),
                "vulnerability_scan": device.get('vulnerability_scan'),
                "risk_score": device.get('risk_score'),
                "compliance_status": device.get('compliance_status')
            },
            "software_info": {
                "installed_software": parse_json_field(device.get('installed_software')),
                "running_services": parse_json_field(device.get('running_services')),
                "recent_software": parse_json_field(device.get('recent_software'))
            },
            "user_info": {
                "logged_in_users": parse_json_field(device.get('logged_in_users')),
                "last_logged_user": device.get('last_logged_user'),
                "user_profiles": parse_json_field(device.get('user_profiles'))
            },
            "management_info": {
                "collection_method": device.get('collection_method'),
                "collection_source": device.get('collection_source'),
                "data_quality_score": device.get('data_quality_score'),
                "last_seen": device.get('last_seen'),
                "last_updated": device.get('last_updated'),
                "business_criticality": device.get('business_criticality'),
                "support_contact": device.get('support_contact'),
                "maintenance_schedule": device.get('maintenance_schedule')
            },
            "status": {
                "status": device.get('status'),
                "ping_status": device.get('ping_status'),
                "last_ping": device.get('last_ping'),
                "response_time_ms": device.get('response_time_ms')
            }
        }
        
        return jsonify(organized_data)
        
    except Exception as e:
        logger.error(f"Device details API error: {e}")
        return jsonify({"error": "Failed to fetch device details"}), 500
    finally:
        conn.close()

@app.route('/api/departments')
def api_departments():
    """Get all departments"""
    log_access(request, "/api/departments")
    
    conn = get_database_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT d.*, COUNT(a.id) as device_count 
            FROM departments d 
            LEFT JOIN assets a ON d.name = a.department 
            GROUP BY d.id 
            ORDER BY d.name
        """)
        
        departments = []
        for row in cursor.fetchall():
            dept = dict(row)
            departments.append(dept)
        
        return jsonify(departments)
        
    except Exception as e:
        logger.error(f"Departments API error: {e}")
        return jsonify({"error": "Failed to fetch departments"}), 500
    finally:
        conn.close()

@app.route('/api/database/status')
def api_database_status():
    """Get database status and health"""
    log_access(request, "/api/database/status")
    
    conn = get_database_connection()
    if not conn:
        return jsonify({"error": "Database connection failed", "status": "offline"}), 500
    
    try:
        cursor = conn.cursor()
        
        # Get database size
        cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
        db_size = cursor.fetchone()[0]
        
        # Get table counts
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        table_stats = {}
        for table in tables:
            table_name = table[0]
            if not table_name.startswith('sqlite_'):
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                table_stats[table_name] = count
        
        return jsonify({
            "status": "online",
            "database_size_mb": round(db_size / (1024 * 1024), 2),
            "table_counts": table_stats,
            "last_check": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Database status API error: {e}")
        return jsonify({"error": "Failed to check database status", "status": "error"}), 500
    finally:
        conn.close()

# Helper functions
def get_status_color(status, ping_status):
    """Get color for device status"""
    if ping_status == 'Online':
        return 'success'
    elif ping_status == 'Offline':
        return 'danger'
    elif status == 'Active':
        return 'warning'
    else:
        return 'secondary'

def get_quality_level(score):
    """Get quality level description"""
    if not score:
        return 'Unknown'
    if score >= 4:
        return 'Excellent'
    elif score >= 3:
        return 'Good'
    elif score >= 2:
        return 'Fair'
    else:
        return 'Poor'

def get_risk_level(score):
    """Get risk level description"""
    if not score:
        return 'Unknown'
    if score >= 8:
        return 'High'
    elif score >= 5:
        return 'Medium'
    else:
        return 'Low'

def safe_round(value, decimals=1):
    """Safely round a value that might be None"""
    if value is None:
        return None
    try:
        return round(float(value), decimals)
    except (ValueError, TypeError):
        return None

def format_storage(value):
    """Format storage value"""
    if not value:
        return 'Unknown'
    try:
        if isinstance(value, str) and 'GB' in value:
            return value
        size_gb = float(value)
        if size_gb >= 1024:
            return f"{size_gb/1024:.1f} TB"
        else:
            return f"{size_gb:.1f} GB"
    except (ValueError, TypeError):
        return str(value)

def parse_json_field(value):
    """Safely parse JSON field"""
    if not value:
        return []
    try:
        if isinstance(value, str):
            return json.loads(value)
        return value
    except (json.JSONDecodeError, TypeError):
        return []

# HTML Template
ENHANCED_DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced Asset Management System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; }
        .card { margin-bottom: 1rem; box-shadow: 0 0.125rem 0.25rem rgba(0,0,0,0.075); }
        .stat-card { text-align: center; }
        .stat-number { font-size: 2rem; font-weight: bold; }
        .device-card { transition: transform 0.2s; cursor: pointer; }
        .device-card:hover { transform: translateY(-2px); }
        .status-online { border-left: 4px solid #28a745; }
        .status-offline { border-left: 4px solid #dc3545; }
        .status-unknown { border-left: 4px solid #6c757d; }
        .quality-excellent { color: #28a745; }
        .quality-good { color: #20c997; }
        .quality-fair { color: #ffc107; }
        .quality-poor { color: #dc3545; }
        .progress-sm { height: 0.5rem; }
        .filter-section { background: white; border-radius: 0.375rem; padding: 1rem; margin-bottom: 1rem; }
        .device-details { display: none; }
        .section-header { background: #e9ecef; padding: 0.5rem 1rem; margin: 0 -1rem 1rem -1rem; font-weight: bold; }
        #loadingIndicator { display: none; }
        .device-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(400px, 1fr)); gap: 1rem; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark bg-dark">
        <div class="container-fluid">
            <span class="navbar-brand mb-0 h1">
                <i class="fas fa-server"></i> Enhanced Asset Management System
            </span>
            <span class="navbar-text" id="lastUpdate">
                <i class="fas fa-clock"></i> Loading...
            </span>
        </div>
    </nav>

    <div class="container-fluid mt-3">
        <!-- Statistics Cards -->
        <div class="row mb-4" id="statsSection">
            <div class="col-md-3">
                <div class="card stat-card">
                    <div class="card-body">
                        <div class="stat-number text-primary" id="totalDevices">-</div>
                        <div>Total Devices</div>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stat-card">
                    <div class="card-body">
                        <div class="stat-number text-success" id="onlineDevices">-</div>
                        <div>Online Devices</div>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stat-card">
                    <div class="card-body">
                        <div class="stat-number text-info" id="totalDepartments">-</div>
                        <div>Departments</div>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stat-card">
                    <div class="card-body">
                        <div class="stat-number text-warning" id="dataQuality">-</div>
                        <div>Avg Data Quality</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Filters -->
        <div class="filter-section">
            <div class="row">
                <div class="col-md-3">
                    <input type="text" class="form-control" id="searchFilter" placeholder="Search devices...">
                </div>
                <div class="col-md-2">
                    <select class="form-select" id="departmentFilter">
                        <option value="">All Departments</option>
                    </select>
                </div>
                <div class="col-md-2">
                    <select class="form-select" id="deviceTypeFilter">
                        <option value="">All Types</option>
                    </select>
                </div>
                <div class="col-md-2">
                    <select class="form-select" id="statusFilter">
                        <option value="">All Status</option>
                        <option value="Active">Active</option>
                        <option value="Inactive">Inactive</option>
                        <option value="Maintenance">Maintenance</option>
                    </select>
                </div>
                <div class="col-md-2">
                    <select class="form-select" id="collectionMethodFilter">
                        <option value="">All Methods</option>
                        <option value="WMI">WMI</option>
                        <option value="SSH">SSH</option>
                        <option value="SNMP">SNMP</option>
                    </select>
                </div>
                <div class="col-md-1">
                    <button class="btn btn-primary" onclick="loadDevices()">
                        <i class="fas fa-search"></i>
                    </button>
                </div>
            </div>
        </div>

        <!-- Loading Indicator -->
        <div id="loadingIndicator" class="text-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>

        <!-- Devices Grid -->
        <div class="device-grid" id="devicesContainer">
            <!-- Devices will be loaded here -->
        </div>

        <!-- Device Details Modal -->
        <div class="modal fade" id="deviceModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="deviceModalTitle">Device Details</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body" id="deviceModalBody">
                        <!-- Device details will be loaded here -->
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let devicesData = [];
        let departmentsData = [];

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            loadStats();
            loadDepartments();
            loadDevices();
            
            // Set up auto-refresh
            setInterval(loadStats, 30000); // Every 30 seconds
            
            // Set up search
            document.getElementById('searchFilter').addEventListener('input', debounce(loadDevices, 500));
        });

        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();
                
                document.getElementById('totalDevices').textContent = data.total_devices || 0;
                document.getElementById('onlineDevices').textContent = data.online_devices || 0;
                document.getElementById('totalDepartments').textContent = data.total_departments || 0;
                document.getElementById('dataQuality').textContent = data.data_quality?.average_score || 0;
                
                document.getElementById('lastUpdate').innerHTML = 
                    '<i class="fas fa-clock"></i> ' + new Date().toLocaleTimeString();
                    
            } catch (error) {
                console.error('Failed to load stats:', error);
            }
        }

        async function loadDepartments() {
            try {
                const response = await fetch('/api/departments');
                departmentsData = await response.json();
                
                const select = document.getElementById('departmentFilter');
                select.innerHTML = '<option value="">All Departments</option>';
                
                departmentsData.forEach(dept => {
                    const option = document.createElement('option');
                    option.value = dept.name;
                    option.textContent = `${dept.name} (${dept.device_count})`;
                    select.appendChild(option);
                });
                
            } catch (error) {
                console.error('Failed to load departments:', error);
            }
        }

        async function loadDevices() {
            const loadingIndicator = document.getElementById('loadingIndicator');
            const container = document.getElementById('devicesContainer');
            
            loadingIndicator.style.display = 'block';
            
            try {
                const params = new URLSearchParams({
                    search: document.getElementById('searchFilter').value,
                    department: document.getElementById('departmentFilter').value,
                    device_type: document.getElementById('deviceTypeFilter').value,
                    status: document.getElementById('statusFilter').value,
                    collection_method: document.getElementById('collectionMethodFilter').value,
                    limit: 100
                });
                
                const response = await fetch(`/api/devices?${params}`);
                const data = await response.json();
                devicesData = data.devices || [];
                
                // Update device type filter
                updateDeviceTypeFilter();
                
                // Render devices
                renderDevices();
                
            } catch (error) {
                console.error('Failed to load devices:', error);
                container.innerHTML = '<div class="alert alert-danger">Failed to load devices</div>';
            } finally {
                loadingIndicator.style.display = 'none';
            }
        }

        function updateDeviceTypeFilter() {
            const deviceTypes = [...new Set(devicesData.map(d => d.device_type).filter(t => t))];
            const select = document.getElementById('deviceTypeFilter');
            const currentValue = select.value;
            
            select.innerHTML = '<option value="">All Types</option>';
            deviceTypes.forEach(type => {
                const option = document.createElement('option');
                option.value = type;
                option.textContent = type;
                if (type === currentValue) option.selected = true;
                select.appendChild(option);
            });
        }

        function renderDevices() {
            const container = document.getElementById('devicesContainer');
            
            if (devicesData.length === 0) {
                container.innerHTML = '<div class="alert alert-info">No devices found</div>';
                return;
            }
            
            container.innerHTML = devicesData.map(device => `
                <div class="card device-card status-${device.ping_status?.toLowerCase() || 'unknown'}" 
                     onclick="showDeviceDetails(${device.id})">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h6 class="card-title mb-0">
                                <i class="fas fa-${getDeviceIcon(device.device_type)}"></i>
                                ${device.display_name}
                            </h6>
                            <span class="badge bg-${device.status_color}">${device.ping_status || device.status}</span>
                        </div>
                        
                        <div class="small text-muted mb-2">
                            <div><strong>Type:</strong> ${device.device_type || 'Unknown'}</div>
                            <div><strong>IP:</strong> ${device.ip_address || 'N/A'}</div>
                            <div><strong>Department:</strong> ${device.department || 'Unknown'}</div>
                        </div>
                        
                        ${device.device_info !== 'Unknown ' ? `
                            <div class="small mb-2">
                                <strong>Model:</strong> ${device.device_info}
                            </div>
                        ` : ''}
                        
                        ${device.performance.cpu !== null || device.performance.memory !== null ? `
                            <div class="row g-2 mb-2">
                                ${device.performance.cpu !== null ? `
                                    <div class="col-6">
                                        <div class="small">CPU: ${device.performance.cpu}%</div>
                                        <div class="progress progress-sm">
                                            <div class="progress-bar ${getPerformanceColor(device.performance.cpu)}" 
                                                 style="width: ${device.performance.cpu}%"></div>
                                        </div>
                                    </div>
                                ` : ''}
                                ${device.performance.memory !== null ? `
                                    <div class="col-6">
                                        <div class="small">Memory: ${device.performance.memory}%</div>
                                        <div class="progress progress-sm">
                                            <div class="progress-bar ${getPerformanceColor(device.performance.memory)}" 
                                                 style="width: ${device.performance.memory}%"></div>
                                        </div>
                                    </div>
                                ` : ''}
                            </div>
                        ` : ''}
                        
                        <div class="d-flex justify-content-between align-items-center small">
                            <span class="quality-${device.quality_level?.toLowerCase()}">
                                <i class="fas fa-star"></i> ${device.quality_level}
                            </span>
                            <span class="text-muted">
                                ${device.collection_method || 'Unknown'}
                            </span>
                        </div>
                    </div>
                </div>
            `).join('');
        }

        async function showDeviceDetails(deviceId) {
            try {
                const response = await fetch(`/api/devices/${deviceId}`);
                const device = await response.json();
                
                document.getElementById('deviceModalTitle').textContent = 
                    device.basic_info.hostname || device.basic_info.ip_address || 'Unknown Device';
                
                document.getElementById('deviceModalBody').innerHTML = renderDeviceDetails(device);
                
                new bootstrap.Modal(document.getElementById('deviceModal')).show();
                
            } catch (error) {
                console.error('Failed to load device details:', error);
            }
        }

        function renderDeviceDetails(device) {
            return `
                <div class="row">
                    <div class="col-md-6">
                        <div class="section-header">Basic Information</div>
                        ${renderSection(device.basic_info)}
                        
                        <div class="section-header">System Information</div>
                        ${renderSection(device.system_info)}
                        
                        <div class="section-header">Hardware Information</div>
                        ${renderSection(device.hardware_info)}
                    </div>
                    <div class="col-md-6">
                        <div class="section-header">Network Information</div>
                        ${renderSection(device.network_info)}
                        
                        <div class="section-header">Performance Metrics</div>
                        ${renderSection(device.performance_info)}
                        
                        <div class="section-header">Security Information</div>
                        ${renderSection(device.security_info)}
                    </div>
                </div>
                
                <div class="section-header">Management Information</div>
                ${renderSection(device.management_info)}
            `;
        }

        function renderSection(data) {
            return Object.entries(data)
                .filter(([key, value]) => value !== null && value !== undefined && value !== '')
                .map(([key, value]) => `
                    <div class="row mb-1">
                        <div class="col-5 small text-muted">${formatKey(key)}:</div>
                        <div class="col-7 small">${formatValue(value)}</div>
                    </div>
                `).join('');
        }

        function formatKey(key) {
            return key.replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase());
        }

        function formatValue(value) {
            if (Array.isArray(value)) {
                return value.length > 0 ? value.slice(0, 3).join(', ') + (value.length > 3 ? '...' : '') : 'None';
            }
            return String(value);
        }

        function getDeviceIcon(type) {
            const icons = {
                'Server': 'server',
                'Desktop': 'desktop',
                'Laptop': 'laptop',
                'Router': 'network-wired',
                'Switch': 'network-wired',
                'Printer': 'print',
                'Firewall': 'shield-alt'
            };
            return icons[type] || 'question';
        }

        function getPerformanceColor(value) {
            if (value >= 90) return 'bg-danger';
            if (value >= 70) return 'bg-warning';
            return 'bg-success';
        }

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
    </script>
</body>
</html>
'''

if __name__ == "__main__":
    print("Starting Enhanced Complete Web Service")
    print(f"URL: http://{HOST}:{PORT}")
    print("Features:")
    print("   - Comprehensive Device Field Display")
    print("   - Enhanced Filtering and Search")
    print("   - Real-time Performance Metrics")
    print("   - Detailed Device Information")
    print("   - Improved Data Quality Indicators")
    print("   - 100% Functional Asset Management")
    
    try:
        app.run(host=HOST, port=PORT, debug=False)
    except KeyboardInterrupt:
        print("\nWeb service stopped by user")
    except Exception as e:
        print(f"Web service error: {e}")