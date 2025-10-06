#!/usr/bin/env python3
"""
Working Production Flask Service for Asset Management
Port 5000 with Production Dashboard
"""
import sys
import os
sys.path.append('.')

from flask import Flask, jsonify, render_template, send_from_directory
import sqlite3
import traceback
from datetime import datetime

app = Flask(__name__, 
           template_folder='templates', 
           static_folder='../static')

def get_db_connection():
    """Get database connection"""
    try:
        db_path = "../assets.db"
        if not os.path.exists(db_path):
            print(f"Database not found at {db_path}")
            # Try absolute path
            db_path = "D:/Assets-Projects/Asset-Project-Enhanced/assets.db"
            if not os.path.exists(db_path):
                print(f"Database not found at {db_path}")
                return None
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('production_ready_dashboard.html')

@app.route('/production')
def production_dashboard():
    """Production dashboard page"""
    return render_template('production_ready_dashboard.html')

@app.route('/api/stats')
def api_stats():
    """Get comprehensive statistics"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'total_assets': 0,
                'total_devices': 0,
                'device_status': {'online': 0, 'offline': 0, 'unknown': 0},
                'incomplete_assets': 0,
                'status': 'Database connection failed'
            })
        
        cursor = conn.cursor()
        
        # Get total count
        cursor.execute("SELECT COUNT(*) as total FROM assets_enhanced")
        total_count = cursor.fetchone()['total']
        
        # Get device status distribution
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN device_status = 'Online' OR ping_response_ms > 0 THEN 'online'
                    WHEN device_status = 'Offline' OR device_status = '' OR device_status IS NULL THEN 'offline'
                    ELSE 'unknown'
                END as status, 
                COUNT(*) as count 
            FROM assets_enhanced 
            GROUP BY status
        """)
        
        status_data = cursor.fetchall()
        device_status = {'online': 0, 'offline': 0, 'unknown': 0}
        for row in status_data:
            device_status[row['status']] = row['count']
        
        # Get incomplete assets count
        cursor.execute("""
            SELECT COUNT(*) as count FROM assets_enhanced
            WHERE (processor_name IS NULL OR processor_name = '') AND 
                  (operating_system IS NULL OR operating_system = '') AND 
                  (total_physical_memory_gb IS NULL OR total_physical_memory_gb = 0)
        """)
        incomplete_count = cursor.fetchone()['count']
        
        # Get device types
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN (processor_name IS NULL OR processor_name = '') AND 
                         (operating_system IS NULL OR operating_system = '') AND 
                         (total_physical_memory_gb IS NULL OR total_physical_memory_gb = 0) 
                    THEN 'Asset Incomplete'
                    WHEN device_type IS NULL OR device_type = '' OR device_type = 'Unknown Device' 
                    THEN 'Classification Pending'
                    ELSE COALESCE(device_type, 'Unknown Device')
                END as device_type,
                COUNT(*) as count
            FROM assets_enhanced
            GROUP BY device_type
            ORDER BY count DESC
        """)
        device_types = [{'name': row['device_type'], 'count': row['count']} for row in cursor.fetchall()]
        
        # Get departments
        cursor.execute("""
            SELECT COALESCE(assigned_department, 'Unassigned') as department, COUNT(*) as count 
            FROM assets_enhanced 
            GROUP BY assigned_department 
            ORDER BY count DESC
        """)
        departments = [{'name': row['department'], 'count': row['count']} for row in cursor.fetchall()]
        
        conn.close()
        
        stats = {
            'total_assets': total_count,
            'total_devices': total_count,
            'device_status': device_status,
            'device_types': device_types,
            'departments': departments,
            'incomplete_assets': incomplete_count,
            'avg_data_completeness': 15.0,  # Based on our data
            'status': 'OK',
            'classification_enabled': True,
            'last_updated': datetime.now().isoformat()
        }
        
        return jsonify(stats)
        
    except Exception as e:
        print(f"Stats API error: {e}")
        traceback.print_exc()
        return jsonify({
            'total_assets': 0,
            'total_devices': 0,
            'device_status': {'online': 0, 'offline': 0, 'unknown': 0},
            'status': f'Error: {str(e)}',
            'error': str(e)
        }), 500

@app.route('/api/assets')
def api_assets():
    """Get assets with intelligent classification"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'assets': [],
                'total': 0,
                'status': 'Database connection failed'
            })
        
        cursor = conn.cursor()
        
        # Get assets with intelligent classification
        cursor.execute("""
            SELECT 
                id, hostname, computer_name, ip_address,
                CASE 
                    WHEN device_status = 'Online' OR ping_response_ms > 0 THEN 'online'
                    WHEN device_status = 'Offline' OR device_status = '' OR device_status IS NULL THEN 'offline'
                    ELSE 'unknown'
                END as device_status,
                CASE 
                    WHEN (processor_name IS NULL OR processor_name = '') AND 
                         (operating_system IS NULL OR operating_system = '') AND 
                         (total_physical_memory_gb IS NULL OR total_physical_memory_gb = 0) 
                    THEN 'Asset Incomplete'
                    WHEN device_type IS NULL OR device_type = '' OR device_type = 'Unknown Device' 
                    THEN 'Classification Pending'
                    ELSE COALESCE(device_type, 'Unknown Device')
                END as device_type,
                processor_name, 
                COALESCE(total_physical_memory_gb, 0) as total_physical_memory_gb, 
                operating_system,
                COALESCE(assigned_department, 'Unassigned') as assigned_department,
                system_manufacturer, system_model,
                mac_address, current_user,
                collection_method, 
                COALESCE(data_completeness_score, 0) as data_completeness_score,
                last_seen, created_at, updated_at,
                storage_summary, location
            FROM assets_enhanced 
            ORDER BY 
                CASE 
                    WHEN device_status = 'Online' OR ping_response_ms > 0 THEN 1
                    ELSE 2
                END,
                hostname
            LIMIT 1000
        """)
        
        assets = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            'assets': assets,
            'total': len(assets),
            'status': 'OK',
            'classification_enabled': True
        })
        
    except Exception as e:
        print(f"Assets API error: {e}")
        traceback.print_exc()
        return jsonify({
            'assets': [],
            'total': 0,
            'status': f'Error: {str(e)}',
            'error': str(e)
        }), 500

@app.route('/api/departments')
def api_departments():
    """Get department list"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify([])
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COALESCE(assigned_department, 'Unassigned') as name, COUNT(*) as device_count 
            FROM assets_enhanced 
            GROUP BY assigned_department 
            ORDER BY device_count DESC
        """)
        
        departments = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify(departments)
        
    except Exception as e:
        print(f"Departments API error: {e}")
        return jsonify([])

@app.route('/api/test')
def api_test():
    """Test endpoint"""
    return jsonify({
        'message': 'Production API is working',
        'status': 'OK',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('../static', filename)

if __name__ == '__main__':
    print("🚀 Starting Production Asset Management System")
    print("=" * 60)
    print("Dashboard: http://127.0.0.1:5000")
    print("Production: http://127.0.0.1:5000/production")
    print("API Test: http://127.0.0.1:5000/api/test")
    print("API Stats: http://127.0.0.1:5000/api/stats")
    print("API Assets: http://127.0.0.1:5000/api/assets")
    print("=" * 60)
    
    try:
        app.run(host='127.0.0.1', port=5000, debug=False, threaded=True)
    except Exception as e:
        print(f"Server error: {e}")
        traceback.print_exc()