# -*- coding: utf-8 -*-
"""
Enhanced Web Interface for Device Management
===========================================
Beautiful, organized web interface with:
- Device classification cards with amazing views
- Drag-and-drop vendor management
- Real-time device management (add, edit, delete, move)
- Responsive design with modern UI
- Integration with intelligent device collector
"""

from flask import Flask, render_template_string, request, jsonify, redirect, url_for
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
import json

class EnhancedDeviceWebInterface:
    """Enhanced web interface for device management"""
    
    def __init__(self, db_path: str = 'assets.db'):
        self.app = Flask(__name__)
        self.db_path = db_path
        self.setup_routes()
    
    def run(self, host: str = '0.0.0.0', port: int = 5556, debug: bool = False):
        """Run the web application"""
        self.app.run(host=host, port=port, debug=debug)

# NOTE: Auto-startup disabled - use launch_original_desktop.py or GUI buttons
# if __name__ == '__main__':
#     app = EnhancedDeviceWebInterface()
#     print("🚀 Starting Enhanced Device Management Portal...")
#     print("📱 Access: http://localhost:5556")
#     app.run(debug=True)  self.setup_routes()
    
    def setup_routes(self):
        """Setup all Flask routes"""
        
        @self.app.route('/')
        def dashboard():
            """Main dashboard with device classification cards"""
            return render_template_string(self.get_dashboard_template())
        
        @self.app.route('/api/devices')
        def get_devices():
            """Get all devices organized by classification"""
            try:
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Get devices grouped by classification
                cursor.execute("""
                    SELECT classification, COUNT(*) as count,
                           GROUP_CONCAT(
                               json_object(
                                   'id', id,
                                   'hostname', hostname,
                                   'ip_address', ip_address,
                                   'status', status,
                                   'vendor', model_vendor,
                                   'os_name', os_name,
                                   'last_updated', updated_at
                               )
                           ) as devices
                    FROM assets 
                    GROUP BY classification
                    ORDER BY classification
                """)
                
                classifications = {}
                for row in cursor.fetchall():
                    classification = row['classification'] or 'Unknown'
                    count = row['count']
                    
                    # Parse device JSON
                    devices = []
                    if row['devices']:
                        device_list = row['devices'].split('},{')
                        for i, device_json in enumerate(device_list):
                            # Fix JSON formatting
                            if i == 0 and not device_json.startswith('{'):
                                device_json = '{' + device_json
                            if i == len(device_list) - 1 and not device_json.endswith('}'):
                                device_json = device_json + '}'
                            if i > 0 and i < len(device_list) - 1:
                                device_json = '{' + device_json + '}'
                            
                            try:
                                device = json.loads(device_json)
                                devices.append(device)
                            except json.JSONDecodeError:
                                continue
                    
                    classifications[classification] = {
                        'count': count,
                        'devices': devices
                    }
                
                conn.close()
                return jsonify(classifications)
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/vendors')
        def get_vendors():
            """Get available vendors"""
            from core.intelligent_device_collector import IntelligentDeviceCollector
            collector = IntelligentDeviceCollector()
            return jsonify(collector.get_vendor_list())
        
        @self.app.route('/api/device-types')
        def get_device_types():
            """Get available device types"""
            from core.intelligent_device_collector import IntelligentDeviceCollector
            collector = IntelligentDeviceCollector()
            return jsonify(collector.get_device_types())
        
        @self.app.route('/api/device/<int:device_id>')
        def get_device_details(device_id):
            """Get detailed device information"""
            try:
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("SELECT * FROM assets WHERE id = ?", (device_id,))
                device = cursor.fetchone()
                
                if device:
                    device_dict = dict(device)
                    conn.close()
                    return jsonify(device_dict)
                else:
                    conn.close()
                    return jsonify({'error': 'Device not found'}), 404
                    
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/device/<int:device_id>', methods=['PUT'])
        def update_device(device_id):
            """Update device information"""
            try:
                data = request.json
                if not data:
                    return jsonify({'error': 'No data provided'}), 400
                
                # Update timestamp
                data['updated_at'] = datetime.now().isoformat()
                
                # Build update query
                update_fields = []
                values = []
                
                for key, value in data.items():
                    if key != 'id':  # Don't update ID
                        update_fields.append(f"{key} = ?")
                        values.append(value)
                
                values.append(device_id)
                
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                query = f"UPDATE assets SET {', '.join(update_fields)} WHERE id = ?"
                cursor.execute(query, values)
                
                if cursor.rowcount > 0:
                    conn.commit()
                    conn.close()
                    return jsonify({'success': True, 'message': 'Device updated successfully'})
                else:
                    conn.close()
                    return jsonify({'error': 'Device not found'}), 404
                    
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/device/<int:device_id>', methods=['DELETE'])
        def delete_device(device_id):
            """Delete device"""
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM assets WHERE id = ?", (device_id,))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    conn.close()
                    return jsonify({'success': True, 'message': 'Device deleted successfully'})
                else:
                    conn.close()
                    return jsonify({'error': 'Device not found'}), 404
                    
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/device/<int:device_id>/move', methods=['POST'])
        def move_device(device_id):
            """Move device to different classification"""
            try:
                data = request.json
                if not data:
                    return jsonify({'error': 'No data provided'}), 400
                    
                new_classification = data.get('classification')
                
                if not new_classification:
                    return jsonify({'error': 'Classification required'}), 400
                
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE assets 
                    SET classification = ?, updated_at = ?
                    WHERE id = ?
                """, (new_classification, datetime.now().isoformat(), device_id))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    conn.close()
                    return jsonify({'success': True, 'message': f'Device moved to {new_classification}'})
                else:
                    conn.close()
                    return jsonify({'error': 'Device not found'}), 404
                    
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/collect-device', methods=['POST'])
        def collect_device_data():
            """Collect data from a device using intelligent collector"""
            try:
                data = request.json
                if not data:
                    return jsonify({'error': 'No data provided'}), 400
                    
                ip_address = data.get('ip_address')
                vendor = data.get('vendor')
                credentials = data.get('credentials', {})
                
                if not ip_address:
                    return jsonify({'error': 'IP address required'}), 400
                
                # Use intelligent collector
                from core.intelligent_device_collector import IntelligentDeviceCollector
                collector = IntelligentDeviceCollector()
                
                # Collect device data
                device_data = collector.collect_device_data(ip_address, credentials=credentials)
                
                if device_data:
                    # Save to database
                    success = collector.save_to_database(device_data, vendor=vendor)
                    
                    if success:
                        return jsonify({
                            'success': True, 
                            'message': 'Device data collected and saved successfully',
                            'device_data': device_data
                        })
                    else:
                        return jsonify({'error': 'Failed to save device data'}), 500
                else:
                    return jsonify({'error': 'Failed to collect device data'}), 500
                    
            except Exception as e:
                return jsonify({'error': str(e)}), 500
    
    def get_dashboard_template(self) -> str:
        """Get the enhanced dashboard HTML template"""
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 Enhanced Device Management Portal</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .dashboard-header {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            margin-bottom: 30px;
            padding: 20px;
            color: white;
        }
        
        .device-card {
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
            border: none;
        }
        
        .device-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        }
        
        .classification-header {
            background: linear-gradient(45deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .device-item {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
            border-left: 4px solid #007bff;
            transition: all 0.2s ease;
            cursor: pointer;
        }
        
        .device-item:hover {
            background: #e9ecef;
            border-left-color: #28a745;
        }
        
        .status-badge {
            font-size: 0.8em;
            padding: 4px 8px;
        }
        
        .btn-floating {
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: linear-gradient(45deg, #ff6b6b, #ee5a6f);
            border: none;
            color: white;
            font-size: 24px;
            box-shadow: 0 8px 20px rgba(255,107,107,0.4);
            transition: all 0.3s ease;
            z-index: 1000;
        }
        
        .btn-floating:hover {
            transform: scale(1.1);
            box-shadow: 0 12px 30px rgba(255,107,107,0.6);
        }
        
        .stats-card {
            background: rgba(255,255,255,0.9);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            border: none;
        }
        
        .stats-number {
            font-size: 2.5em;
            font-weight: bold;
            color: #007bff;
        }
        
        .vendor-dropdown {
            border-radius: 25px;
            border: 2px dashed #007bff;
            min-height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .vendor-dropdown:hover {
            background: #f8f9fa;
            border-color: #28a745;
        }
        
        .modal-content {
            border-radius: 15px;
            border: none;
        }
        
        .modal-header {
            background: linear-gradient(45deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            border-radius: 15px 15px 0 0;
        }
        
        .loading-spinner {
            display: none;
            text-align: center;
            padding: 20px;
        }
    </style>
</head>
<body>
    <div class="container-fluid p-4">
        <!-- Dashboard Header -->
        <div class="dashboard-header">
            <div class="row align-items-center">
                <div class="col-md-8">
                    <h1><i class="fas fa-network-wired"></i> Enhanced Device Management Portal</h1>
                    <p class="mb-0">Intelligent device collection with automatic protocol detection</p>
                </div>
                <div class="col-md-4 text-end">
                    <button class="btn btn-light btn-lg" onclick="refreshDevices()">
                        <i class="fas fa-sync-alt"></i> Refresh
                    </button>
                    <button class="btn btn-success btn-lg ms-2" onclick="showCollectModal()">
                        <i class="fas fa-plus"></i> Collect Device
                    </button>
                </div>
            </div>
        </div>
        
        <!-- Statistics Row -->
        <div class="row mb-4" id="statsRow">
            <!-- Dynamic stats will be loaded here -->
        </div>
        
        <!-- Device Classifications -->
        <div class="row" id="deviceClassifications">
            <div class="col-12 text-center">
                <div class="loading-spinner" id="loadingSpinner">
                    <i class="fas fa-spinner fa-spin fa-3x text-white"></i>
                    <p class="text-white mt-2">Loading devices...</p>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Floating Add Button -->
    <button class="btn-floating" onclick="showCollectModal()" title="Add New Device">
        <i class="fas fa-plus"></i>
    </button>
    
    <!-- Device Collection Modal -->
    <div class="modal fade" id="collectModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title"><i class="fas fa-robot"></i> Intelligent Device Collection</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="collectForm">
                        <div class="row">
                            <div class="col-md-6">
                                <label class="form-label">Device IP Address *</label>
                                <input type="text" class="form-control" id="deviceIP" required placeholder="192.168.1.100">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">Vendor (Optional)</label>
                                <select class="form-select" id="deviceVendor">
                                    <!-- Vendors loaded dynamically -->
                                </select>
                            </div>
                        </div>
                        
                        <div class="mt-3">
                            <h6>Credentials (if required)</h6>
                            <div class="row">
                                <div class="col-md-6">
                                    <label class="form-label">Username</label>
                                    <input type="text" class="form-control" id="credUsername">
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label">Password</label>
                                    <input type="password" class="form-control" id="credPassword">
                                </div>
                            </div>
                        </div>
                        
                        <div class="mt-3">
                            <div class="alert alert-info">
                                <i class="fas fa-info-circle"></i>
                                <strong>Automatic Detection:</strong> The system will automatically detect the OS and use the appropriate collection method:
                                <br>• Windows/Windows Server: WMI
                                <br>• Linux: SSH  
                                <br>• Network Devices: SNMP
                            </div>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" onclick="collectDeviceData()">
                        <i class="fas fa-search"></i> Collect Device Data
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Device Details Modal -->
    <div class="modal fade" id="deviceModal" tabindex="-1">
        <div class="modal-dialog modal-xl">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="deviceModalTitle"></h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body" id="deviceModalBody">
                    <!-- Device details loaded dynamically -->
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    <button type="button" class="btn btn-warning" onclick="editDevice()">Edit</button>
                    <button type="button" class="btn btn-danger" onclick="deleteDevice()">Delete</button>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let currentDeviceId = null;
        
        // Load devices on page load
        document.addEventListener('DOMContentLoaded', function() {
            loadDevices();
            loadVendors();
        });
        
        function loadDevices() {
            document.getElementById('loadingSpinner').style.display = 'block';
            
            fetch('/api/devices')
                .then(response => response.json())
                .then(data => {
                    displayDevices(data);
                    updateStats(data);
                })
                .catch(error => {
                    console.error('Error loading devices:', error);
                    showAlert('Error loading devices: ' + error.message, 'danger');
                })
                .finally(() => {
                    document.getElementById('loadingSpinner').style.display = 'none';
                });
        }
        
        function displayDevices(classifications) {
            const container = document.getElementById('deviceClassifications');
            container.innerHTML = '';
            
            for (const [classification, data] of Object.entries(classifications)) {
                const col = document.createElement('div');
                col.className = 'col-lg-6 col-xl-4 mb-4';
                
                col.innerHTML = `
                    <div class="device-card">
                        <div class="classification-header">
                            <h5 class="mb-0">
                                <i class="fas ${getClassificationIcon(classification)}"></i>
                                ${classification}
                            </h5>
                            <span class="badge bg-light text-dark">${data.count}</span>
                        </div>
                        <div class="device-list">
                            ${data.devices.map(device => `
                                <div class="device-item" onclick="showDeviceDetails(${device.id})">
                                    <div class="d-flex justify-content-between align-items-center">
                                        <div>
                                            <strong>${device.hostname || 'Unknown'}</strong>
                                            <br>
                                            <small class="text-muted">
                                                ${device.ip_address || 'No IP'} • ${device.vendor || 'No Vendor'}
                                            </small>
                                        </div>
                                        <span class="badge status-badge ${getStatusColor(device.status)}">
                                            ${device.status || 'Unknown'}
                                        </span>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `;
                
                container.appendChild(col);
            }
        }
        
        function updateStats(classifications) {
            const statsRow = document.getElementById('statsRow');
            
            let totalDevices = 0;
            let activeDevices = 0;
            let classificationsCount = Object.keys(classifications).length;
            
            for (const [classification, data] of Object.entries(classifications)) {
                totalDevices += data.count;
                data.devices.forEach(device => {
                    if (device.status === 'Active') activeDevices++;
                });
            }
            
            statsRow.innerHTML = `
                <div class="col-md-4">
                    <div class="stats-card card">
                        <div class="stats-number">${totalDevices}</div>
                        <h6>Total Devices</h6>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="stats-card card">
                        <div class="stats-number">${activeDevices}</div>
                        <h6>Active Devices</h6>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="stats-card card">
                        <div class="stats-number">${classificationsCount}</div>
                        <h6>Classifications</h6>
                    </div>
                </div>
            `;
        }
        
        function loadVendors() {
            fetch('/api/vendors')
                .then(response => response.json())
                .then(vendors => {
                    const select = document.getElementById('deviceVendor');
                    select.innerHTML = '<option value="">Select Vendor...</option>';
                    
                    vendors.forEach(vendor => {
                        const option = document.createElement('option');
                        option.value = vendor;
                        option.textContent = vendor;
                        select.appendChild(option);
                    });
                })
                .catch(error => console.error('Error loading vendors:', error));
        }
        
        function showCollectModal() {
            new bootstrap.Modal(document.getElementById('collectModal')).show();
        }
        
        function collectDeviceData() {
            const ip = document.getElementById('deviceIP').value.trim();
            const vendor = document.getElementById('deviceVendor').value;
            const username = document.getElementById('credUsername').value.trim();
            const password = document.getElementById('credPassword').value.trim();
            
            if (!ip) {
                showAlert('IP address is required', 'warning');
                return;
            }
            
            const credentials = {};
            if (username && password) {
                credentials.windows = { username, password };
                credentials.linux = { username, password };
                credentials.snmp = { community: password || 'public' };
            }
            
            const button = event.target;
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Collecting...';
            
            fetch('/api/collect-device', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    ip_address: ip,
                    vendor: vendor,
                    credentials: credentials
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert('Device data collected successfully!', 'success');
                    bootstrap.Modal.getInstance(document.getElementById('collectModal')).hide();
                    loadDevices();
                } else {
                    showAlert('Error: ' + data.error, 'danger');
                }
            })
            .catch(error => {
                showAlert('Error collecting device data: ' + error.message, 'danger');
            })
            .finally(() => {
                button.disabled = false;
                button.innerHTML = '<i class="fas fa-search"></i> Collect Device Data';
            });
        }
        
        function showDeviceDetails(deviceId) {
            currentDeviceId = deviceId;
            
            fetch(`/api/device/${deviceId}`)
                .then(response => response.json())
                .then(device => {
                    document.getElementById('deviceModalTitle').innerHTML = `
                        <i class="fas fa-desktop"></i> ${device.hostname || 'Unknown Device'}
                    `;
                    
                    document.getElementById('deviceModalBody').innerHTML = `
                        <div class="row">
                            <div class="col-md-6">
                                <h6>Basic Information</h6>
                                <table class="table table-sm">
                                    <tr><td><strong>Hostname:</strong></td><td>${device.hostname || 'N/A'}</td></tr>
                                    <tr><td><strong>IP Address:</strong></td><td>${device.ip_address || 'N/A'}</td></tr>
                                    <tr><td><strong>Classification:</strong></td><td>${device.classification || 'N/A'}</td></tr>
                                    <tr><td><strong>Status:</strong></td><td><span class="badge ${getStatusColor(device.status)}">${device.status || 'N/A'}</span></td></tr>
                                </table>
                            </div>
                            <div class="col-md-6">
                                <h6>Technical Details</h6>
                                <table class="table table-sm">
                                    <tr><td><strong>OS:</strong></td><td>${device.os_name || 'N/A'}</td></tr>
                                    <tr><td><strong>Vendor:</strong></td><td>${device.model_vendor || 'N/A'}</td></tr>
                                    <tr><td><strong>RAM:</strong></td><td>${device.installed_ram_gb || 'N/A'} GB</td></tr>
                                    <tr><td><strong>Storage:</strong></td><td>${device.storage || 'N/A'}</td></tr>
                                </table>
                            </div>
                        </div>
                        <div class="row mt-3">
                            <div class="col-12">
                                <h6>Additional Information</h6>
                                <table class="table table-sm">
                                    <tr><td><strong>Processor:</strong></td><td>${device.processor || 'N/A'}</td></tr>
                                    <tr><td><strong>Serial Number:</strong></td><td>${device.serial_number || 'N/A'}</td></tr>
                                    <tr><td><strong>Data Source:</strong></td><td>${device.data_source || 'N/A'}</td></tr>
                                    <tr><td><strong>Last Updated:</strong></td><td>${device.updated_at || 'N/A'}</td></tr>
                                </table>
                            </div>
                        </div>
                    `;
                    
                    new bootstrap.Modal(document.getElementById('deviceModal')).show();
                })
                .catch(error => {
                    showAlert('Error loading device details: ' + error.message, 'danger');
                });
        }
        
        function refreshDevices() {
            loadDevices();
        }
        
        function getClassificationIcon(classification) {
            const icons = {
                'Windows': 'fa-windows',
                'Windows Server': 'fa-server',
                'Linux': 'fa-linux',
                'Hypervisor': 'fa-cloud',
                'Switches': 'fa-network-wired',
                'AP': 'fa-wifi',
                'Fingerprint': 'fa-fingerprint',
                'Printers': 'fa-print',
                'Unknown': 'fa-question'
            };
            return icons[classification] || 'fa-desktop';
        }
        
        function getStatusColor(status) {
            const colors = {
                'Active': 'bg-success',
                'Inactive': 'bg-secondary',
                'Offline': 'bg-danger',
                'Maintenance': 'bg-warning',
                'Unknown': 'bg-secondary'
            };
            return colors[status] || 'bg-secondary';
        }
        
        function showAlert(message, type) {
            const alert = document.createElement('div');
            alert.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
            alert.style.zIndex = '9999';
            alert.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            document.body.appendChild(alert);
            
            setTimeout(() => {
                alert.remove();
            }, 5000);
        }
    </script>
</body>
</html>
        '''
    
    def run(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
        """Run the web application"""
        self.app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    app = EnhancedDeviceWebInterface()
    print("🚀 Starting Enhanced Device Management Portal...")
    print("📱 Access: http://localhost:5000")
    app.run(debug=True)