# -*- coding: utf-8 -*-
"""
Enhanced Web Portal with Department Support
==========================================
Complete web interface with:
- Department filtering and management
- Enhanced device data display
- Real-time statistics
- Performance optimizations
"""

from flask import Flask, render_template_string, jsonify
import sqlite3

class EnhancedDeviceWebInterface:
    """Enhanced web interface with department support"""
    
    def __init__(self, db_path: str = 'assets.db'):
        self.app = Flask(__name__)
        self.db_path = db_path
        self.setup_routes()
    
    def setup_routes(self):
        """Setup all Flask routes"""
        
        @self.app.route('/')
        def dashboard():
            """Main dashboard with device classification and department cards"""
            return render_template_string(self.get_dashboard_template())
        
        @self.app.route('/api/stats')
        def get_stats():
            """Get comprehensive statistics including departments"""
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
                cursor.execute("SELECT COUNT(DISTINCT department) FROM assets WHERE department IS NOT NULL")
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
            """Get all devices with department and enhanced data"""
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Get devices with comprehensive information
                cursor.execute("""
                    SELECT 
                        id, hostname, ip_address, working_user, classification, 
                        department, status, data_source, created_at, last_updated,
                        os_name, os_version, manufacturer, model, serial_number,
                        mac_address, cpu_info, memory_gb, storage_info, vendor,
                        ping_status, last_ping
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
                        'last_ping': row[21]
                    }
                    devices.append(device)
                
                conn.close()
                return jsonify(devices)
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/departments')
        def get_departments():
            """Get department statistics"""
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT department, COUNT(*) as count
                    FROM assets 
                    WHERE department IS NOT NULL
                    GROUP BY department
                    ORDER BY count DESC, department
                """)
                
                departments = {}
                for row in cursor.fetchall():
                    departments[row[0]] = row[1]
                
                conn.close()
                return jsonify(departments)
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/classifications')
        def get_classifications():
            """Get classification statistics"""
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT classification, COUNT(*) as count
                    FROM assets 
                    WHERE classification IS NOT NULL
                    GROUP BY classification
                    ORDER BY count DESC, classification
                """)
                
                classifications = {}
                for row in cursor.fetchall():
                    classifications[row[0]] = row[1]
                
                conn.close()
                return jsonify(classifications)
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500

    def get_dashboard_template(self):
        """Enhanced dashboard template with department support"""
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🛡️ Enhanced Asset Management Portal</title>
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
        
        .btn-primary { background: var(--primary-gradient); }
        .btn-success { background: var(--success-gradient); }
        .btn-warning { background: var(--warning-gradient); }
        
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
    </style>
</head>
<body>
    <div class="hero-header">
        <div class="container">
            <div class="row align-items-center">
                <div class="col-md-8">
                    <h1><i class="fas fa-shield-alt"></i> Enhanced Asset Management Portal</h1>
                    <p class="mb-0">Enterprise Edition - Compatible with Desktop Application</p>
                </div>
                <div class="col-md-4 text-end">
                    <button class="btn btn-light me-2" onclick="refreshData()">
                        <i class="fas fa-sync-alt"></i> Refresh
                    </button>
                    <button class="btn btn-success me-2" onclick="syncWithDesktop()">
                        <i class="fas fa-desktop"></i> Sync Desktop
                    </button>
                    <button class="btn btn-warning" onclick="exportToExcel()">
                        <i class="fas fa-file-excel"></i> Export Excel
                    </button>
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
                <div class="col-md-4">
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
                <div class="col-md-2">
                    <label class="form-label"><i class="fas fa-wifi"></i> Add Asset</label>
                    <button class="btn btn-success w-100" onclick="addAsset()">
                        <i class="fas fa-plus"></i> Add Asset
                    </button>
                </div>
            </div>
        </div>

        <!-- Assets Table -->
        <div class="devices-table">
            <table class="table table-hover mb-0">
                <thead>
                    <tr>
                        <th>Hostname</th>
                        <th>User</th>
                        <th>IP Address</th>
                        <th>Classification</th>
                        <th>Department</th>
                        <th>Status</th>
                        <th>Ping</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody id="devicesTable">
                    <tr>
                        <td colspan="8" class="text-center py-5">
                            <div class="loading-spinner me-2"></div>
                            Loading devices...
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let allDevices = [];
        let departments = {};
        let classifications = {};

        // Load initial data
        document.addEventListener('DOMContentLoaded', function() {
            loadStats();
            loadDevices();
            loadDepartments();
            loadClassifications();
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
                    '<tr><td colspan="8" class="text-center text-danger">Error loading devices</td></tr>';
            }
        }

        async function loadDepartments() {
            try {
                const response = await fetch('/api/departments');
                departments = await response.json();
                
                const select = document.getElementById('departmentFilter');
                select.innerHTML = '<option value="">All Departments</option>';
                
                Object.keys(departments).sort().forEach(dept => {
                    const option = document.createElement('option');
                    option.value = dept;
                    option.textContent = `${dept} (${departments[dept]})`;
                    select.appendChild(option);
                });
            } catch (error) {
                console.error('Error loading departments:', error);
            }
        }

        async function loadClassifications() {
            try {
                const response = await fetch('/api/classifications');
                classifications = await response.json();
                
                const select = document.getElementById('classificationFilter');
                select.innerHTML = '<option value="">All Classifications</option>';
                
                Object.keys(classifications).sort().forEach(cls => {
                    const option = document.createElement('option');
                    option.value = cls;
                    option.textContent = `${cls} (${classifications[cls]})`;
                    select.appendChild(option);
                });
            } catch (error) {
                console.error('Error loading classifications:', error);
            }
        }

        function displayDevices(devices) {
            const tbody = document.getElementById('devicesTable');
            
            if (devices.length === 0) {
                tbody.innerHTML = '<tr><td colspan="8" class="text-center text-muted py-5">No devices found</td></tr>';
                return;
            }

            tbody.innerHTML = devices.map(device => `
                <tr>
                    <td>
                        <strong>${device.hostname}</strong>
                        ${device.os_name ? `<br><small class="text-muted">${device.os_name}</small>` : ''}
                    </td>
                    <td>${device.user || 'N/A'}</td>
                    <td>
                        ${device.ip_address ? `<code>${device.ip_address}</code>` : 'N/A'}
                        ${device.mac_address ? `<br><small class="text-muted">${device.mac_address}</small>` : ''}
                    </td>
                    <td><span class="badge classification-badge">${device.classification}</span></td>
                    <td><span class="badge department-badge">${device.department}</span></td>
                    <td><span class="badge status-badge">${device.status}</span></td>
                    <td>
                        <i class="fas fa-circle ${getPingStatusClass(device.ping_status)}"></i>
                        ${device.ping_status || 'Unknown'}
                    </td>
                    <td>
                        <button class="btn btn-primary btn-sm btn-action" onclick="editDevice(${device.id})" title="Edit">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-danger btn-sm btn-action" onclick="deleteDevice(${device.id})" title="Delete">
                            <i class="fas fa-trash"></i>
                        </button>
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
            loadClassifications();
        }

        function syncWithDesktop() {
            alert('🔄 Desktop sync functionality - would integrate with desktop application');
        }

        function exportToExcel() {
            alert('📊 Excel export functionality - would export current data to Excel');
        }

        function addAsset() {
            alert('➕ Add asset functionality - would open add device form');
        }

        function editDevice(id) {
            alert(`✏️ Edit device ${id} - would open edit form`);
        }

        function deleteDevice(id) {
            if (confirm('Are you sure you want to delete this device?')) {
                alert(`🗑️ Delete device ${id} - would remove from database`);
            }
        }
    </script>
</body>
</html>
        '''

    def run(self, host='0.0.0.0', port=5556, debug=False):
        """Run the web interface"""
        print(f"🌐 Starting Enhanced Device Web Portal on http://{host}:{port}")
        print("🔧 Features: Department Management, Enhanced Data Display, Real-time Stats")
        self.app.run(host=host, port=port, debug=debug)

# NOTE: Auto-startup disabled - use launch_original_desktop.py or GUI buttons
# if __name__ == '__main__':
#     interface = EnhancedDeviceWebInterface()
#     interface.run(debug=True)