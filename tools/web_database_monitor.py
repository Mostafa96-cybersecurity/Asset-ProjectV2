"""
🌐 Web Database Monitor - Professional Asset Dashboard
=====================================================

A modern web interface to monitor your network assets from any browser.

Features:
🎨 Beautiful, responsive dashboard
📊 Real-time device statistics  
🔍 Advanced search and filtering
📈 Professional data presentation
📱 Mobile-friendly interface
🛡️ Smart duplicate detection insights
💾 Export capabilities

Access from any browser: http://localhost:5555
"""

from flask import Flask, render_template, jsonify, request, send_file
import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Any
import pandas as pd
from io import BytesIO
import tempfile

app = Flask(__name__)

# Database path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets.db')

def init_database():
    """Initialize database if needed"""
    try:
        conn = get_db_connection()
        # Check if assets table exists
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='assets'").fetchall()
        if not tables:
            # Create basic assets table if it doesn't exist
            conn.execute('''
                CREATE TABLE IF NOT EXISTS assets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hostname TEXT,
                    ip_address TEXT,
                    os_name TEXT,
                    device_type TEXT,
                    manufacturer TEXT,
                    model TEXT,
                    serial_number TEXT,
                    asset_tag TEXT,
                    owner TEXT,
                    department TEXT,
                    site TEXT,
                    status TEXT DEFAULT 'Active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Database initialization error: {e}")
        return False

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # This allows dict-like access
    return conn

def get_device_stats():
    """Get device statistics"""
    conn = get_db_connection()
    try:
        # Get total devices
        total_devices = conn.execute("SELECT COUNT(*) FROM assets WHERE hostname IS NOT NULL AND hostname != ''").fetchone()[0]
        
        # Get devices by type/OS
        os_stats = conn.execute("""
            SELECT 
                CASE 
                    WHEN os_name LIKE '%Windows%' AND os_name LIKE '%Server%' THEN 'Windows Server'
                    WHEN os_name LIKE '%Windows%' THEN 'Windows Workstation'
                    WHEN os_name LIKE '%Linux%' OR os_name LIKE '%Ubuntu%' OR os_name LIKE '%CentOS%' THEN 'Linux'
                    WHEN hostname LIKE '%switch%' OR hostname LIKE '%sw-%' THEN 'Network Device'
                    ELSE 'Other'
                END as device_type,
                COUNT(*) as count
            FROM assets 
            WHERE hostname IS NOT NULL AND hostname != ''
            GROUP BY device_type
        """).fetchall()
        
        # Get recent additions
        recent_count = conn.execute("""
            SELECT COUNT(*) FROM assets 
            WHERE datetime(created_at) > datetime('now', '-7 days')
        """).fetchone()[0]
        
        # Get devices with issues
        issues_count = conn.execute("""
            SELECT COUNT(*) FROM assets 
            WHERE (ip_address IS NULL OR ip_address = '') AND hostname IS NOT NULL
        """).fetchone()[0]
        
        return {
            'total_devices': total_devices,
            'os_distribution': [{'type': row[0], 'count': row[1]} for row in os_stats],
            'recent_additions': recent_count,
            'devices_with_issues': issues_count
        }
    finally:
        conn.close()

def get_all_devices(search='', device_type='', limit=100, offset=0):
    """Get devices with filtering"""
    conn = get_db_connection()
    try:
        query = """
            SELECT 
                id, hostname, ip_address, os_name, device_model, manufacturer,
                serial_number, cpu_info, ram_gb, storage_info, working_user,
                domain, mac_address, created_at, updated_at,
                CASE 
                    WHEN os_name LIKE '%Windows%' AND os_name LIKE '%Server%' THEN 'Windows Server'
                    WHEN os_name LIKE '%Windows%' THEN 'Windows Workstation'
                    WHEN os_name LIKE '%Linux%' OR os_name LIKE '%Ubuntu%' OR os_name LIKE '%CentOS%' THEN 'Linux'
                    WHEN hostname LIKE '%switch%' OR hostname LIKE '%sw-%' THEN 'Network Device'
                    ELSE 'Other'
                END as device_type
            FROM assets 
            WHERE (hostname IS NOT NULL AND hostname != '')
        """
        
        params = []
        
        if search:
            query += " AND (hostname LIKE ? OR ip_address LIKE ? OR os_name LIKE ? OR working_user LIKE ?)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param, search_param])
        
        if device_type and device_type != 'All':
            if device_type == 'Windows Server':
                query += " AND os_name LIKE '%Windows%' AND os_name LIKE '%Server%'"
            elif device_type == 'Windows Workstation':
                query += " AND os_name LIKE '%Windows%' AND os_name NOT LIKE '%Server%'"
            elif device_type == 'Linux':
                query += " AND (os_name LIKE '%Linux%' OR os_name LIKE '%Ubuntu%' OR os_name LIKE '%CentOS%')"
            elif device_type == 'Network Device':
                query += " AND (hostname LIKE '%switch%' OR hostname LIKE '%sw-%')"
        
        query += " ORDER BY updated_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        devices = conn.execute(query, params).fetchall()
        
        # Get total count for pagination
        count_query = "SELECT COUNT(*) FROM assets WHERE (hostname IS NOT NULL AND hostname != '')"
        count_params = []
        
        if search:
            count_query += " AND (hostname LIKE ? OR ip_address LIKE ? OR os_name LIKE ? OR working_user LIKE ?)"
            count_params.extend([search_param, search_param, search_param, search_param])
        
        total_count = conn.execute(count_query, count_params).fetchone()[0]
        
        return {
            'devices': [dict(row) for row in devices],
            'total': total_count
        }
    finally:
        conn.close()

@app.route('/')
def dashboard():
    """Main dashboard"""
    return render_template('dashboard.html')

@app.route('/api/stats')
def api_stats():
    """Get device statistics"""
    return jsonify(get_device_stats())

@app.route('/api/devices')
def api_devices():
    """Get devices with filtering"""
    search = request.args.get('search', '')
    device_type = request.args.get('type', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    
    offset = (page - 1) * per_page
    result = get_all_devices(search, device_type, per_page, offset)
    
    return jsonify({
        'devices': result['devices'],
        'total': result['total'],
        'page': page,
        'per_page': per_page,
        'total_pages': (result['total'] + per_page - 1) // per_page
    })

@app.route('/api/device/<int:device_id>')
def api_device_details(device_id):
    """Get detailed device information"""
    conn = get_db_connection()
    try:
        device = conn.execute("SELECT * FROM assets WHERE id = ?", (device_id,)).fetchone()
        if device:
            return jsonify(dict(device))
        return jsonify({'error': 'Device not found'}), 404
    finally:
        conn.close()

@app.route('/api/export/excel')
def export_excel():
    """Export devices to Excel"""
    result = get_all_devices(limit=10000)  # Export all
    
    if not result['devices']:
        return jsonify({'error': 'No devices to export'}), 400
    
    # Create DataFrame
    df = pd.DataFrame(result['devices'])
    
    # Select and rename columns for better presentation
    columns_mapping = {
        'hostname': 'Hostname',
        'ip_address': 'IP Address',
        'os_name': 'Operating System',
        'device_model': 'Device Model',
        'manufacturer': 'Manufacturer',
        'serial_number': 'Serial Number',
        'cpu_info': 'CPU Information',
        'ram_gb': 'RAM (GB)',
        'storage_info': 'Storage',
        'working_user': 'Working User',
        'domain': 'Domain',
        'mac_address': 'MAC Address',
        'device_type': 'Device Type',
        'created_at': 'Created At',
        'updated_at': 'Last Updated'
    }
    
    # Select only existing columns
    available_columns = [col for col in columns_mapping.keys() if col in df.columns]
    df_export = df[available_columns].copy()
    df_export.columns = [columns_mapping[col] for col in available_columns]
    
    # Create Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_export.to_excel(writer, sheet_name='Network Assets', index=False)
        
        # Get the workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets['Network Assets']
        
        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    output.seek(0)
    filename = f"Network_Assets_Export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )

# Create templates directory and files
def create_templates():
    """Create HTML templates"""
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(template_dir, exist_ok=True)
    
    dashboard_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🛡️ Network Assets Monitor</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
        }
        
        .stat-number {
            font-size: 2.5em;
            font-weight: bold;
            color: #4a90e2;
            margin-bottom: 10px;
        }
        
        .stat-label {
            color: #666;
            font-size: 1.1em;
        }
        
        .main-content {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .controls {
            display: flex;
            gap: 15px;
            margin-bottom: 25px;
            flex-wrap: wrap;
            align-items: center;
        }
        
        .search-box, .filter-select {
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s ease;
        }
        
        .search-box {
            flex: 1;
            min-width: 200px;
        }
        
        .search-box:focus, .filter-select:focus {
            outline: none;
            border-color: #4a90e2;
        }
        
        .btn {
            padding: 12px 20px;
            background: #4a90e2;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: background 0.3s ease;
        }
        
        .btn:hover {
            background: #357abd;
        }
        
        .btn-success {
            background: #5cb85c;
        }
        
        .btn-success:hover {
            background: #4cae4c;
        }
        
        .devices-grid {
            display: grid;
            gap: 20px;
        }
        
        .device-card {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            border-left: 5px solid #4a90e2;
            transition: box-shadow 0.3s ease;
        }
        
        .device-card:hover {
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .device-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .device-name {
            font-size: 1.3em;
            font-weight: bold;
            color: #2c3e50;
        }
        
        .device-type {
            background: #4a90e2;
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.85em;
            font-weight: 600;
        }
        
        .device-info {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
        }
        
        .info-item {
            display: flex;
            justify-content: space-between;
        }
        
        .info-label {
            font-weight: 600;
            color: #666;
        }
        
        .info-value {
            color: #333;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
            font-size: 1.2em;
        }
        
        .pagination {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-top: 30px;
        }
        
        .page-btn {
            padding: 8px 12px;
            border: 1px solid #ddd;
            background: white;
            cursor: pointer;
            border-radius: 5px;
        }
        
        .page-btn.active {
            background: #4a90e2;
            color: white;
            border-color: #4a90e2;
        }
        
        .chart-container {
            width: 100%;
            max-width: 400px;
            margin: 20px auto;
        }
        
        @media (max-width: 768px) {
            .controls {
                flex-direction: column;
            }
            
            .search-box {
                width: 100%;
            }
            
            .device-info {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🛡️ Network Assets Monitor</h1>
        <p>Professional Device Management Dashboard</p>
    </div>
    
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-number" id="totalDevices">-</div>
            <div class="stat-label">Total Devices</div>
        </div>
        <div class="stat-card">
            <div class="stat-number" id="recentAdditions">-</div>
            <div class="stat-label">Added This Week</div>
        </div>
        <div class="stat-card">
            <div class="stat-number" id="devicesWithIssues">-</div>
            <div class="stat-label">Need Attention</div>
        </div>
        <div class="stat-card">
            <div class="chart-container">
                <canvas id="deviceTypeChart"></canvas>
            </div>
        </div>
    </div>
    
    <div class="main-content">
        <div class="controls">
            <input type="text" class="search-box" id="searchBox" placeholder="🔍 Search devices...">
            <select class="filter-select" id="typeFilter">
                <option value="">All Device Types</option>
                <option value="Windows Workstation">Windows Workstation</option>
                <option value="Windows Server">Windows Server</option>
                <option value="Linux">Linux</option>
                <option value="Network Device">Network Device</option>
                <option value="Other">Other</option>
            </select>
            <button class="btn" onclick="searchDevices()">Search</button>
            <button class="btn btn-success" onclick="exportToExcel()">📊 Export Excel</button>
        </div>
        
        <div id="devicesContainer">
            <div class="loading">Loading devices...</div>
        </div>
        
        <div id="pagination" class="pagination"></div>
    </div>
    
    <script>
        let currentPage = 1;
        let totalPages = 1;
        
        // Load initial data
        loadStats();
        loadDevices();
        
        function loadStats() {
            fetch('/api/stats')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('totalDevices').textContent = data.total_devices;
                    document.getElementById('recentAdditions').textContent = data.recent_additions;
                    document.getElementById('devicesWithIssues').textContent = data.devices_with_issues;
                    
                    // Create chart
                    const ctx = document.getElementById('deviceTypeChart').getContext('2d');
                    new Chart(ctx, {
                        type: 'doughnut',
                        data: {
                            labels: data.os_distribution.map(item => item.type),
                            datasets: [{
                                data: data.os_distribution.map(item => item.count),
                                backgroundColor: [
                                    '#4a90e2',
                                    '#50c8a3',
                                    '#f5a623',
                                    '#d0021b',
                                    '#9013fe'
                                ]
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: true,
                            plugins: {
                                legend: {
                                    position: 'bottom'
                                }
                            }
                        }
                    });
                })
                .catch(error => {
                    console.error('Error loading stats:', error);
                });
        }
        
        function loadDevices(page = 1) {
            const search = document.getElementById('searchBox').value;
            const type = document.getElementById('typeFilter').value;
            
            const params = new URLSearchParams({
                page: page,
                per_page: 20,
                search: search,
                type: type
            });
            
            fetch(`/api/devices?${params}`)
                .then(response => response.json())
                .then(data => {
                    displayDevices(data.devices);
                    updatePagination(data.page, data.total_pages);
                    currentPage = data.page;
                    totalPages = data.total_pages;
                })
                .catch(error => {
                    console.error('Error loading devices:', error);
                    document.getElementById('devicesContainer').innerHTML = 
                        '<div class="loading">Error loading devices</div>';
                });
        }
        
        function displayDevices(devices) {
            const container = document.getElementById('devicesContainer');
            
            if (devices.length === 0) {
                container.innerHTML = '<div class="loading">No devices found</div>';
                return;
            }
            
            const html = devices.map(device => `
                <div class="device-card">
                    <div class="device-header">
                        <div class="device-name">${device.hostname || 'Unknown'}</div>
                        <div class="device-type">${device.device_type || 'Unknown'}</div>
                    </div>
                    <div class="device-info">
                        <div class="info-item">
                            <span class="info-label">IP Address:</span>
                            <span class="info-value">${device.ip_address || 'N/A'}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Operating System:</span>
                            <span class="info-value">${device.os_name || 'N/A'}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Model:</span>
                            <span class="info-value">${device.device_model || 'N/A'}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">User:</span>
                            <span class="info-value">${device.working_user || 'N/A'}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">RAM:</span>
                            <span class="info-value">${device.ram_gb ? device.ram_gb + ' GB' : 'N/A'}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Serial Number:</span>
                            <span class="info-value">${device.serial_number || 'N/A'}</span>
                        </div>
                    </div>
                </div>
            `).join('');
            
            container.innerHTML = '<div class="devices-grid">' + html + '</div>';
        }
        
        function updatePagination(current, total) {
            const container = document.getElementById('pagination');
            if (total <= 1) {
                container.innerHTML = '';
                return;
            }
            
            let html = '';
            
            // Previous button
            if (current > 1) {
                html += `<button class="page-btn" onclick="loadDevices(${current - 1})">Previous</button>`;
            }
            
            // Page numbers
            const start = Math.max(1, current - 2);
            const end = Math.min(total, current + 2);
            
            for (let i = start; i <= end; i++) {
                const active = i === current ? 'active' : '';
                html += `<button class="page-btn ${active}" onclick="loadDevices(${i})">${i}</button>`;
            }
            
            // Next button
            if (current < total) {
                html += `<button class="page-btn" onclick="loadDevices(${current + 1})">Next</button>`;
            }
            
            container.innerHTML = html;
        }
        
        function searchDevices() {
            currentPage = 1;
            loadDevices(1);
        }
        
        function exportToExcel() {
            const btn = event.target;
            const originalText = btn.textContent;
            btn.textContent = 'Exporting...';
            btn.disabled = true;
            
            fetch('/api/export/excel')
                .then(response => {
                    if (response.ok) {
                        return response.blob();
                    }
                    throw new Error('Export failed');
                })
                .then(blob => {
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `Network_Assets_${new Date().toISOString().slice(0,10)}.xlsx`;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    window.URL.revokeObjectURL(url);
                })
                .catch(error => {
                    console.error('Export error:', error);
                    alert('Export failed. Please try again.');
                })
                .finally(() => {
                    btn.textContent = originalText;
                    btn.disabled = false;
                });
        }
        
        // Enable Enter key for search
        document.getElementById('searchBox').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchDevices();
            }
        });
        
        // Auto-refresh every 30 seconds
        setInterval(() => {
            loadStats();
            loadDevices(currentPage);
        }, 30000);
    </script>
</body>
</html>'''
    
    with open(os.path.join(template_dir, 'dashboard.html'), 'w', encoding='utf-8') as f:
        f.write(dashboard_html)

def start_web_server():
    """Start the web server"""
    print("🌐 Starting Network Assets Web Monitor...")
    print("=" * 50)
    
    # Create templates
    create_templates()
    
    # Check if database exists
    if not os.path.exists(DB_PATH):
        print(f"⚠️  Database not found at: {DB_PATH}")
        print("Please run the asset collector first to create the database.")
        return
    
    try:
        from waitress import serve
        print("✅ Web server starting...")
        print(f"🔗 Access your dashboard at: http://localhost:5555")
        print(f"📊 Database location: {DB_PATH}")
        print("=" * 50)
        print("Features available:")
        print("  • 📊 Real-time device statistics")
        print("  • 🔍 Advanced search and filtering")  
        print("  • 📱 Mobile-friendly responsive design")
        print("  • 📈 Professional data presentation")
        print("  • 💾 Excel export functionality")
        print("=" * 50)
        print("Press Ctrl+C to stop the server")
        print()
        
        serve(app, host='0.0.0.0', port=5555)
    except ImportError:
        print("⚠️  Waitress not found, falling back to Flask dev server")
        app.run(host='0.0.0.0', port=5555, debug=False)
    except KeyboardInterrupt:
        print("\n👋 Web server stopped")
    except Exception as e:
        print(f"❌ Error starting web server: {e}")

if __name__ == "__main__":
    start_web_server()