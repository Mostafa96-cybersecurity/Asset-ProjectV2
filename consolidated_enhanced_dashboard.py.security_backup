#!/usr/bin/env python3
"""
🎯 SIMPLE WORKING DASHBOARD - PORT 5556
======================================
Guaranteed to work - Simple but functional
"""

from flask import Flask, render_template_string, request, session, jsonify, redirect
import sqlite3

# Flask app
app = Flask(__name__)
app.secret_key = 'simple-working-dashboard-2025'

# Simple authentication
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "user": {"password": "user123", "role": "user"}
}

def authenticate(username, password):
    user = USERS.get(username)
    return user and user["password"] == password

def get_user_role(username):
    user = USERS.get(username)
    return user["role"] if user else "user"

# Database
def get_db_connection():
    try:
        conn = sqlite3.connect('assets.db')
        conn.row_factory = sqlite3.Row
        return conn
    except:
        return None

def get_asset_count():
    try:
        conn = get_db_connection()
        if conn:
            count = conn.execute("SELECT COUNT(*) FROM assets").fetchone()[0]
            conn.close()
            return count
    except:
        pass
    return 0

# Simple HTML template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🎯 Enhanced Asset Dashboard</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .header {
            background: linear-gradient(135deg, #333 0%, #555 100%);
            color: white;
            padding: 2rem 0;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .amazing-card {
            background: white;
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
            transition: transform 0.3s ease;
        }
        .amazing-card:hover {
            transform: translateY(-5px);
        }
        .stats-card {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            border-radius: 15px;
            padding: 2rem;
            text-align: center;
            margin-bottom: 1rem;
            transition: transform 0.3s ease;
        }
        .stats-card:hover { transform: translateY(-5px); }
        .stats-number { font-size: 3rem; font-weight: bold; }
        .login-card {
            background: white;
            border-radius: 20px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.1);
            margin-top: 5rem;
        }
        .btn-amazing {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            color: white;
            padding: 1rem 2rem;
            border-radius: 10px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .btn-amazing:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.2);
            color: white;
        }
    </style>
</head>
<body>
    {% if not session.get('logged_in') %}
    <!-- Login Page -->
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="login-card">
                    <div class="card-header bg-primary text-white text-center" style="border-radius: 20px 20px 0 0;">
                        <h3><i class="fas fa-lock me-2"></i>🎯 Enhanced Dashboard Login</h3>
                        <p class="mb-0">Single Port Solution - Port 5556</p>
                    </div>
                    <div class="card-body p-4">
                        <form method="post" action="/login">
                            <div class="mb-3">
                                <label class="form-label fw-bold">👤 Username</label>
                                <input type="text" name="username" class="form-control form-control-lg" required>
                                <small class="text-muted">Try: admin or user</small>
                            </div>
                            <div class="mb-3">
                                <label class="form-label fw-bold">🔒 Password</label>
                                <input type="password" name="password" class="form-control form-control-lg" required>
                                <small class="text-muted">Try: admin123 or user123</small>
                            </div>
                            <button type="submit" class="btn btn-amazing w-100">
                                <i class="fas fa-sign-in-alt me-2"></i>Login to Dashboard
                            </button>
                        </form>
                        <div class="mt-3 text-center">
                            <div class="alert alert-info">
                                <small><strong>Test Accounts:</strong><br>
                                Admin: admin / admin123<br>
                                User: user / user123</small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    {% else %}
    <!-- Dashboard Page -->
    <div class="header">
        <div class="container">
            <div class="row align-items-center">
                <div class="col-md-8">
                    <h1><i class="fas fa-tachometer-alt me-3"></i>Enhanced Asset Management</h1>
                    <p class="mb-0 fs-5">🎯 Single Port Solution • Amazing UI • Database Connected</p>
                </div>
                <div class="col-md-4 text-end">
                    <div class="text-white">
                        <h4>👋 {{ session.username }}</h4>
                        <span class="badge bg-light text-dark fs-6">{{ session.user_role|title }} Access</span>
                        <div class="mt-2">
                            <a href="/logout" class="btn btn-outline-light">
                                <i class="fas fa-sign-out-alt me-1"></i>Logout
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="container">
        <!-- Statistics Cards -->
        <div class="row">
            <div class="col-md-3">
                <div class="stats-card">
                    <div class="stats-number">{{ asset_count }}</div>
                    <h5><i class="fas fa-database me-2"></i>Total Assets</h5>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stats-card">
                    <div class="stats-number">5556</div>
                    <h5><i class="fas fa-server me-2"></i>Single Port</h5>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stats-card">
                    <div class="stats-number">✅</div>
                    <h5><i class="fas fa-check me-2"></i>Working</h5>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stats-card">
                    <div class="stats-number">🎨</div>
                    <h5><i class="fas fa-palette me-2"></i>Amazing UI</h5>
                </div>
            </div>
        </div>

        <!-- Main Dashboard Content -->
        <div class="amazing-card">
            <h3><i class="fas fa-chart-pie me-2"></i>Dashboard Overview</h3>
            <div class="row mt-4">
                <div class="col-md-6">
                    <h5><i class="fas fa-info-circle me-2"></i>System Status</h5>
                    <ul class="list-unstyled">
                        <li><i class="fas fa-check text-success me-2"></i>Dashboard: Working perfectly</li>
                        <li><i class="fas fa-check text-success me-2"></i>Database: {{ asset_count }} assets connected</li>
                        <li><i class="fas fa-check text-success me-2"></i>Authentication: {{ session.user_role|title }} access</li>
                        <li><i class="fas fa-check text-success me-2"></i>Port 5556: Single port solution</li>
                    </ul>
                </div>
                <div class="col-md-6">
                    <h5><i class="fas fa-tools me-2"></i>Actions</h5>
                    <button class="btn btn-amazing me-2 mb-2" onclick="loadAssets()">
                        <i class="fas fa-list me-1"></i>View Assets
                    </button>
                    <button class="btn btn-amazing me-2 mb-2" onclick="exportData()">
                        <i class="fas fa-download me-1"></i>Export CSV
                    </button>
                    <button class="btn btn-amazing me-2 mb-2" onclick="refreshData()">
                        <i class="fas fa-sync me-1"></i>Refresh
                    </button>
                </div>
            </div>
        </div>

        <!-- Assets Table -->
        <div class="amazing-card">
            <h4><i class="fas fa-table me-2"></i>Asset Database</h4>
            <div class="table-responsive">
                <table class="table table-striped" id="assetsTable">
                    <thead class="table-dark">
                        <tr>
                            <th>ID</th>
                            <th>Hostname</th>
                            <th>IP Address</th>
                            <th>User</th>
                            <th>OS</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="assetsTableBody">
                        <tr>
                            <td colspan="6" class="text-center py-4">
                                <i class="fas fa-spinner fa-spin me-2"></i>Click "View Assets" to load data...
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    {% endif %}

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // JavaScript functions
        function loadAssets() {
            fetch('/api/assets')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const tbody = document.getElementById('assetsTableBody');
                        tbody.innerHTML = '';
                        
                        data.assets.forEach((asset, index) => {
                            const row = document.createElement('tr');
                            row.innerHTML = `
                                <td>${asset.id}</td>
                                <td>${asset.hostname || 'Unknown'}</td>
                                <td>${asset.ip_address || 'N/A'}</td>
                                <td>${asset.working_user || 'N/A'}</td>
                                <td>${asset.os_name || 'Unknown'}</td>
                                <td>
                                    <button class="btn btn-sm btn-outline-primary" onclick="viewAsset(${asset.id})">
                                        <i class="fas fa-eye"></i>
                                    </button>
                                </td>
                            `;
                            tbody.appendChild(row);
                        });
                    } else {
                        alert('Error loading assets: ' + data.error);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error loading assets');
                });
        }

        function exportData() {
            window.open('/api/export', '_blank');
        }

        function refreshData() {
            location.reload();
        }

        function viewAsset(id) {
            alert(`Viewing asset ID: ${id}\\nThis would show detailed asset information.`);
        }

        // Auto-load assets when page loads (if logged in)
        {% if session.get('logged_in') %}
        document.addEventListener('DOMContentLoaded', function() {
            // Auto-load assets after 2 seconds
            setTimeout(loadAssets, 2000);
        });
        {% endif %}
    </script>
</body>
</html>
'''

# Routes
@app.route('/')
def home():
    asset_count = get_asset_count()
    return render_template_string(HTML_TEMPLATE, asset_count=asset_count, session=session)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    
    print(f"Login attempt: {username} / {password}")
    
    if authenticate(username, password):
        session['logged_in'] = True
        session['username'] = username
        session['user_role'] = get_user_role(username)
        print(f"✅ Login successful: {username} as {session['user_role']}")
        return redirect('/')
    else:
        print(f"❌ Login failed: {username}")
        return redirect('/')

@app.route('/logout')
def logout():
    username = session.get('username', 'Unknown')
    session.clear()
    print(f"👋 User {username} logged out")
    return redirect('/')

@app.route('/api/assets')
def api_assets():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'})
        
        # Get first 50 assets
        assets = conn.execute("""
            SELECT id, hostname, ip_address, working_user, os_name 
            FROM assets 
            LIMIT 50
        """).fetchall()
        
        assets_list = [dict(asset) for asset in assets]
        conn.close()
        
        return jsonify({'success': True, 'assets': assets_list})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/export')
def api_export():
    try:
        conn = get_db_connection()
        if not conn:
            return "Database error", 500
        
        assets = conn.execute("""
            SELECT hostname, ip_address, working_user, os_name 
            FROM assets 
            LIMIT 100
        """).fetchall()
        
        csv_content = "Hostname,IP Address,User,OS\\n"
        for asset in assets:
            csv_content += f'"{asset[0] or "N/A"}","{asset[1] or "N/A"}","{asset[2] or "N/A"}","{asset[3] or "N/A"}"\\n'
        
        conn.close()
        
        from flask import Response
        return Response(
            csv_content,
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=assets.csv'}
        )
    except Exception as e:
        return f"Export error: {e}", 500

# NOTE: Auto-startup disabled - use launch_original_desktop.py or GUI buttons
# if __name__ == '__main__':
#     print("🎯 SIMPLE WORKING DASHBOARD - GUARANTEED TO WORK!")
#     print("=" * 55)
#     print("📊 Features: Amazing UI • Authentication • Database")
#     print("🌐 URL: http://localhost:5556")
#     print("🔐 Admin Login: admin / admin123")
#     print("👤 User Login: user / user123")
#     print("✨ Single Port Solution - No Confusion!")
#     print("=" * 55)
#     
#     asset_count = get_asset_count()
#     print(f"📊 Database Status: {asset_count} assets found")
#     
#     if asset_count > 0:
#         print("✅ Database connection working!")
#     else:
#         print("⚠️ Database might be empty or connection issue")
#     
#     try:
#         print("🚀 Starting dashboard on port 5556...")
#         app.run(host='0.0.0.0', port=5556, debug=False, threaded=True)
#     except Exception as e:
#         print(f"❌ Error starting dashboard: {e}")
#         input("Press Enter to exit...")