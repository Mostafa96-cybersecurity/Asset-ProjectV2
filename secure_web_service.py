#!/usr/bin/env python3
"""
🌐 SECURE WEB SERVICE WITH ENHANCED ACCESS CONTROL
=================================================
Updated web service with comprehensive security integration
"""

from flask import Flask, request, jsonify, session, render_template_string, redirect, url_for, make_response
import json
import os
import sqlite3
import logging
from datetime import datetime, timedelta
import threading
import time
from pathlib import Path

# Import enhanced access control
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
except ImportError:
    ACCESS_CONTROL_ENABLED = False
    print("Warning: Enhanced access control not available")

# Import comprehensive logging
try:
    from comprehensive_logging_system import log_web_service, start_job, complete_job
except ImportError:
    def log_web_service(level, message, **kwargs):
        print(f"[WEB_SERVICE] {level}: {message}")
    def start_job(job_id, feature, description):
        print(f"Starting job: {description}")
    def complete_job(job_id, success, message=""):
        print(f"Job completed: {success}")

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Port configuration (standardized to 5556)
PORT = 5556

# Database path
DB_PATH = "assets.db"

# Security decorator
def require_access(permissions=None):
    """Enhanced security decorator with comprehensive access control"""
    def decorator(f):
        def decorated_function(*args, **kwargs):
            try:
                # Get client information
                client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', 
                                              request.environ.get('REMOTE_ADDR', '127.0.0.1'))
                user_agent = request.headers.get('User-Agent', 'Unknown')
                endpoint = request.endpoint or request.path
                method = request.method
                
                # Check if access control is enabled
                if not ACCESS_CONTROL_ENABLED:
                    log_access_attempt(client_ip, endpoint, method, user_agent, "ACCESS_CONTROL_DISABLED")
                    return f(*args, **kwargs)
                
                # Check IP access
                ip_allowed, ip_reason = check_ip_access(client_ip)
                if not ip_allowed:
                    log_access_attempt(client_ip, endpoint, method, user_agent, f"IP_BLOCKED: {ip_reason}")
                    return jsonify({
                        'error': 'Access denied',
                        'message': 'Your IP address is not authorized',
                        'code': 'IP_BLOCKED'
                    }), 403
                
                # Check rate limiting
                rate_ok, rate_reason = check_rate_limit(client_ip, endpoint)
                if not rate_ok:
                    log_access_attempt(client_ip, endpoint, method, user_agent, f"RATE_LIMITED: {rate_reason}")
                    return jsonify({
                        'error': 'Rate limit exceeded',
                        'message': 'Too many requests, please try again later',
                        'code': 'RATE_LIMITED'
                    }), 429
                
                # Check session-based authentication for API endpoints
                if endpoint.startswith('/api/') and permissions:
                    session_id = request.headers.get('Authorization', '').replace('Bearer ', '')
                    if not session_id:
                        session_id = session.get('session_id')
                    
                    if session_id:
                        valid, user_info = validate_session(session_id, client_ip)
                        if valid:
                            # Check permissions
                            if permissions and not any(perm in user_info.get('permissions', []) for perm in permissions):
                                log_access_attempt(client_ip, endpoint, method, user_agent, "INSUFFICIENT_PERMISSIONS", user_info)
                                return jsonify({
                                    'error': 'Insufficient permissions',
                                    'message': f'Required permissions: {permissions}',
                                    'code': 'INSUFFICIENT_PERMISSIONS'
                                }), 403
                            
                            log_access_attempt(client_ip, endpoint, method, user_agent, "SUCCESS", user_info)
                            return f(*args, **kwargs)
                        else:
                            log_access_attempt(client_ip, endpoint, method, user_agent, "INVALID_SESSION")
                            return jsonify({
                                'error': 'Authentication required',
                                'message': 'Please login to access this resource',
                                'code': 'AUTHENTICATION_REQUIRED'
                            }), 401
                    else:
                        log_access_attempt(client_ip, endpoint, method, user_agent, "NO_SESSION")
                        return jsonify({
                            'error': 'Authentication required',
                            'message': 'Please login to access this resource',
                            'code': 'AUTHENTICATION_REQUIRED'
                        }), 401
                
                # Allow access for non-API endpoints (web interface)
                log_access_attempt(client_ip, endpoint, method, user_agent, "SUCCESS")
                return f(*args, **kwargs)
                
            except Exception as e:
                log_web_service('ERROR', f'Access control error: {e}')
                return jsonify({
                    'error': 'Security check failed',
                    'message': 'Please try again later',
                    'code': 'SECURITY_ERROR'
                }), 500
                
        decorated_function.__name__ = f.__name__
        return decorated_function
    return decorator

# Web interface routes
@app.route('/')
@require_access()
def index():
    """Main dashboard with login form"""
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>🔐 Secure Asset Management System</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
            .login-form { background: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
            .form-group { margin-bottom: 15px; }
            .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
            .form-group input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
            .btn { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; margin-right: 10px; }
            .btn:hover { background: #0056b3; }
            .btn-success { background: #28a745; }
            .btn-danger { background: #dc3545; }
            .status { padding: 10px; border-radius: 5px; margin-bottom: 10px; }
            .status.success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            .status.error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
            .dashboard { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }
            .card { background: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #dee2e6; }
            .card h3 { margin-top: 0; color: #495057; }
            .logs { background: #1e1e1e; color: #f8f9fa; padding: 15px; border-radius: 5px; font-family: monospace; font-size: 12px; max-height: 300px; overflow-y: auto; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔐 Secure Asset Management System</h1>
                <p>Enhanced Security & Access Control | Port 8080</p>
            </div>
            
            <div class="login-form">
                <h3>🔑 Authentication Required</h3>
                <form id="loginForm">
                    <div class="form-group">
                        <label>Username:</label>
                        <input type="text" id="username" required>
                        <small>Default: admin / user</small>
                    </div>
                    <div class="form-group">
                        <label>Password:</label>
                        <input type="password" id="password" required>
                        <small>Default: admin123 / user123</small>
                    </div>
                    <button type="submit" class="btn">Login</button>
                    <button type="button" class="btn btn-success" onclick="checkStatus()">Check Status</button>
                </form>
                <div id="loginStatus"></div>
            </div>
            
            <div class="dashboard">
                <div class="card">
                    <h3>🛡️ Security Status</h3>
                    <div id="securityStatus">Loading...</div>
                    <button class="btn" onclick="refreshSecurity()">Refresh Security</button>
                </div>
                
                <div class="card">
                    <h3>📊 System Information</h3>
                    <div id="systemInfo">Loading...</div>
                    <button class="btn" onclick="refreshSystem()">Refresh System</button>
                </div>
            </div>
            
            <div class="card" style="margin-top: 20px;">
                <h3>📝 Access Logs</h3>
                <div id="accessLogs" class="logs">Loading access logs...</div>
                <button class="btn" onclick="refreshLogs()">Refresh Logs</button>
            </div>
        </div>
        
        <script>
            let sessionId = null;
            
            document.getElementById('loginForm').onsubmit = async function(e) {
                e.preventDefault();
                
                const username = document.getElementById('username').value;
                const password = document.getElementById('password').value;
                const statusDiv = document.getElementById('loginStatus');
                
                try {
                    const response = await fetch('/api/login', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ username, password })
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        sessionId = result.session_id;
                        statusDiv.innerHTML = '<div class="status success">✅ Login successful! Session active.</div>';
                        refreshSecurity();
                        refreshSystem();
                        refreshLogs();
                    } else {
                        statusDiv.innerHTML = `<div class="status error">❌ Login failed: ${result.message}</div>`;
                    }
                } catch (error) {
                    statusDiv.innerHTML = `<div class="status error">❌ Connection error: ${error.message}</div>`;
                }
            };
            
            async function checkStatus() {
                const statusDiv = document.getElementById('loginStatus');
                try {
                    const response = await fetch('/api/status');
                    const result = await response.json();
                    statusDiv.innerHTML = `<div class="status success">🌐 Web service is running on port ${result.port || 8080}</div>`;
                } catch (error) {
                    statusDiv.innerHTML = `<div class="status error">❌ Service unavailable: ${error.message}</div>`;
                }
            }
            
            async function refreshSecurity() {
                const securityDiv = document.getElementById('securityStatus');
                try {
                    const headers = sessionId ? { 'Authorization': `Bearer ${sessionId}` } : {};
                    const response = await fetch('/api/security/status', { headers });
                    const result = await response.json();
                    
                    if (result.error) {
                        securityDiv.innerHTML = `<div class="status error">${result.message}</div>`;
                    } else {
                        securityDiv.innerHTML = `
                            <p><strong>Authentication:</strong> ${result.settings?.authentication_enabled ? '✅ Enabled' : '❌ Disabled'}</p>
                            <p><strong>IP Filtering:</strong> ${result.settings?.ip_filtering_enabled ? '✅ Enabled' : '❌ Disabled'}</p>
                            <p><strong>Rate Limiting:</strong> ${result.settings?.rate_limiting_enabled ? '✅ Enabled' : '❌ Disabled'}</p>
                            <p><strong>Active Sessions:</strong> ${result.active_sessions || 0}</p>
                            <p><strong>Allowed IPs:</strong> ${result.allowed_ips_count || 0}</p>
                            <p><strong>Blocked IPs:</strong> ${result.blocked_ips_count || 0}</p>
                        `;
                    }
                } catch (error) {
                    securityDiv.innerHTML = `<div class="status error">Failed to load security status</div>`;
                }
            }
            
            async function refreshSystem() {
                const systemDiv = document.getElementById('systemInfo');
                try {
                    const headers = sessionId ? { 'Authorization': `Bearer ${sessionId}` } : {};
                    const response = await fetch('/api/system/info', { headers });
                    const result = await response.json();
                    
                    if (result.error) {
                        systemDiv.innerHTML = `<div class="status error">${result.message}</div>`;
                    } else {
                        systemDiv.innerHTML = `
                            <p><strong>Server Time:</strong> ${result.server_time || 'Unknown'}</p>
                            <p><strong>Database:</strong> ${result.database_status || 'Unknown'}</p>
                            <p><strong>Port:</strong> ${result.port || 8080}</p>
                            <p><strong>Client IP:</strong> ${result.client_ip || 'Unknown'}</p>
                        `;
                    }
                } catch (error) {
                    systemDiv.innerHTML = `<div class="status error">Failed to load system info</div>`;
                }
            }
            
            async function refreshLogs() {
                const logsDiv = document.getElementById('accessLogs');
                try {
                    const headers = sessionId ? { 'Authorization': `Bearer ${sessionId}` } : {};
                    const response = await fetch('/api/logs/access', { headers });
                    const result = await response.json();
                    
                    if (result.error) {
                        logsDiv.innerHTML = result.message;
                    } else {
                        const logs = result.logs || [];
                        logsDiv.innerHTML = logs.slice(-50).map(log => 
                            `${log.timestamp} | ${log.client_ip} -> ${log.method} ${log.endpoint} | ${log.result}`
                        ).join('\\n') || 'No access logs available';
                    }
                } catch (error) {
                    logsDiv.innerHTML = 'Failed to load access logs';
                }
            }
            
            // Initial load
            checkStatus();
            refreshSecurity();
            refreshSystem();
            
            // Auto-refresh every 30 seconds
            setInterval(() => {
                refreshSecurity();
                refreshSystem();
                refreshLogs();
            }, 30000);
        </script>
    </body>
    </html>
    """)

# API endpoints
@app.route('/api/status')
@require_access()
def api_status():
    """Get service status"""
    return jsonify({
        'success': True,
        'message': 'Web service is running',
        'port': PORT,
        'timestamp': datetime.now().isoformat(),
        'access_control_enabled': ACCESS_CONTROL_ENABLED
    })

@app.route('/api/login', methods=['POST'])
@require_access()
def api_login():
    """User login endpoint"""
    try:
        data = request.get_json()
        username = data.get('username', '')
        password = data.get('password', '')
        
        if not ACCESS_CONTROL_ENABLED:
            return jsonify({
                'success': True,
                'message': 'Access control disabled - login not required',
                'session_id': 'mock_session'
            })
        
        # Authenticate user
        auth_success, message, user_info = authenticate_user(username, password)
        
        if auth_success:
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', 
                                          request.environ.get('REMOTE_ADDR', '127.0.0.1'))
            session_id = create_session(user_info, client_ip)
            
            # Store in Flask session as well
            session['session_id'] = session_id
            session['user_info'] = user_info
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'session_id': session_id,
                'user_info': user_info
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 401
            
    except Exception as e:
        log_web_service('ERROR', f'Login error: {e}')
        return jsonify({
            'success': False,
            'message': 'Login failed'
        }), 500

@app.route('/api/logout', methods=['POST'])
@require_access()
def api_logout():
    """User logout endpoint"""
    try:
        if ACCESS_CONTROL_ENABLED:
            session_id = session.get('session_id')
            if session_id:
                access_control_manager.revoke_session(session_id)
        
        session.clear()
        
        return jsonify({
            'success': True,
            'message': 'Logout successful'
        })
        
    except Exception as e:
        log_web_service('ERROR', f'Logout error: {e}')
        return jsonify({
            'success': False,
            'message': 'Logout failed'
        }), 500

@app.route('/api/security/status')
@require_access(['read'])
def api_security_status():
    """Get security status"""
    try:
        if not ACCESS_CONTROL_ENABLED:
            return jsonify({
                'error': True,
                'message': 'Access control system not available'
            })
        
        stats = access_control_manager.get_access_stats()
        return jsonify(stats)
        
    except Exception as e:
        log_web_service('ERROR', f'Security status error: {e}')
        return jsonify({
            'error': True,
            'message': 'Failed to get security status'
        })

@app.route('/api/system/info')
@require_access(['read'])
def api_system_info():
    """Get system information"""
    try:
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', 
                                      request.environ.get('REMOTE_ADDR', '127.0.0.1'))
        
        # Check database
        db_status = "Unknown"
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            table_count = cursor.fetchone()[0]
            conn.close()
            db_status = f"Connected ({table_count} tables)"
        except Exception as e:
            db_status = f"Error: {str(e)[:50]}"
        
        return jsonify({
            'server_time': datetime.now().isoformat(),
            'database_status': db_status,
            'port': PORT,
            'client_ip': client_ip,
            'access_control_enabled': ACCESS_CONTROL_ENABLED
        })
        
    except Exception as e:
        log_web_service('ERROR', f'System info error: {e}')
        return jsonify({
            'error': True,
            'message': 'Failed to get system information'
        })

@app.route('/api/logs/access')
@require_access(['admin'])
def api_access_logs():
    """Get access logs"""
    try:
        if not ACCESS_CONTROL_ENABLED:
            return jsonify({
                'error': True,
                'message': 'Access control system not available'
            })
        
        log_file = Path("logs/access_control.log")
        logs = []
        
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        log_entry = json.loads(line.strip())
                        logs.append(log_entry)
                    except:
                        continue
        
        return jsonify({
            'logs': logs[-100:],  # Last 100 entries
            'total': len(logs)
        })
        
    except Exception as e:
        log_web_service('ERROR', f'Access logs error: {e}')
        return jsonify({
            'error': True,
            'message': 'Failed to get access logs'
        })

@app.route('/api/assets')
@require_access(['read'])
def api_assets():
    """Get assets list"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT ip_address, hostname, os_info, last_seen, status 
            FROM assets 
            ORDER BY last_seen DESC 
            LIMIT 100
        """)
        
        assets = []
        for row in cursor.fetchall():
            assets.append({
                'ip_address': row[0],
                'hostname': row[1],
                'os_info': row[2],
                'last_seen': row[3],
                'status': row[4]
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'assets': assets,
            'count': len(assets)
        })
        
    except Exception as e:
        log_web_service('ERROR', f'Assets API error: {e}')
        return jsonify({
            'success': False,
            'message': 'Failed to retrieve assets',
            'error': str(e)
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested resource was not found',
        'code': 'NOT_FOUND'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An internal server error occurred',
        'code': 'INTERNAL_ERROR'
    }), 500

def run_web_service():
    """Run the secure web service"""
    try:
        log_web_service('INFO', f'🔐 Starting secure web service on port {PORT}')
        
        if ACCESS_CONTROL_ENABLED:
            log_web_service('INFO', '🛡️ Enhanced access control system enabled')
        else:
            log_web_service('WARNING', '⚠️ Access control system not available - running in basic mode')
        
        # Run Flask app
        app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)
        
    except Exception as e:
        log_web_service('ERROR', f'Failed to start web service: {e}')
        raise

# NOTE: Auto-startup disabled - use launch_original_desktop.py or GUI buttons
# if __name__ == "__main__":
#     run_web_service()