#!/usr/bin/env python3
"""
FINAL Working Production Service - Port 5000
"""
import sys
import os
sys.path.append('.')

from flask import Flask, jsonify, render_template
import sqlite3
import traceback
from datetime import datetime

app = Flask(__name__, 
           template_folder='templates', 
           static_folder='../static')

def get_db_connection():
    """Get database connection with proper path handling"""
    try:
        # Try relative path first
        db_path = "../assets.db"
        if not os.path.exists(db_path):
            # Try absolute path
            db_path = "D:/Assets-Projects/Asset-Project-Enhanced/assets.db"
        
        if not os.path.exists(db_path):
            print("❌ Database not found at any location")
            return None
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        print(f"✅ Database connected: {db_path}")
        return conn
    except Exception as e:
        print(f"❌ Database connection error: {e}")
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
    """Get statistics with simplified queries"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'total_assets': 0,
                'device_status': {'online': 0, 'offline': 0},
                'status': 'Database connection failed'
            })
        
        cursor = conn.cursor()
        
        # Simple count query
        cursor.execute("SELECT COUNT(*) as total FROM assets_enhanced")
        total_count = cursor.fetchone()['total']
        
        # Simple status check (use basic columns only)
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN device_status = 'Online' THEN 'online'
                    ELSE 'offline'
                END as status, 
                COUNT(*) as count 
            FROM assets_enhanced 
            GROUP BY status
        """)
        
        status_data = cursor.fetchall()
        device_status = {'online': 0, 'offline': 0}
        for row in status_data:
            if row['status'] in device_status:
                device_status[row['status']] = row['count']
        
        # Count incomplete assets (check if columns exist)
        try:
            cursor.execute("""
                SELECT COUNT(*) as count FROM assets_enhanced
                WHERE (processor_name IS NULL OR processor_name = '') OR
                      (operating_system IS NULL OR operating_system = '') OR
                      (total_physical_memory_gb IS NULL OR total_physical_memory_gb = 0)
            """)
            incomplete_count = cursor.fetchone()['count']
        except:
            incomplete_count = total_count  # Assume all are incomplete if we can't check
        
        conn.close()
        
        stats = {
            'total_assets': total_count,
            'total_devices': total_count,
            'device_status': device_status,
            'incomplete_assets': incomplete_count,
            'status': 'OK'
        }
        
        print(f"📊 Stats generated: {stats}")
        return jsonify(stats)
        
    except Exception as e:
        print(f"❌ Stats API error: {e}")
        traceback.print_exc()
        return jsonify({
            'total_assets': 0,
            'device_status': {'online': 0, 'offline': 0},
            'status': f'Error: {str(e)}'
        }), 500

@app.route('/api/assets')
def api_assets():
    """Get assets with basic columns only"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'assets': [],
                'total': 0,
                'status': 'Database connection failed'
            })
        
        cursor = conn.cursor()
        
        # Use only basic columns that we know exist
        cursor.execute("""
            SELECT 
                id, 
                COALESCE(hostname, '') as hostname,
                COALESCE(computer_name, '') as computer_name,
                COALESCE(ip_address, '') as ip_address,
                COALESCE(device_status, 'offline') as device_status,
                COALESCE(device_type, 'Asset Incomplete') as device_type,
                COALESCE(mac_address, '') as mac_address,
                created_at,
                updated_at
            FROM assets_enhanced 
            ORDER BY id
            LIMIT 100
        """)
        
        assets = []
        for row in cursor.fetchall():
            asset = dict(row)
            # Ensure required fields
            if not asset['hostname']:
                asset['hostname'] = f"Device-{asset['id']}"
            if not asset['device_type'] or asset['device_type'] == '':
                asset['device_type'] = 'Asset Incomplete'
            assets.append(asset)
        
        conn.close()
        
        result = {
            'assets': assets,
            'total': len(assets),
            'status': 'OK'
        }
        
        print(f"📋 Assets loaded: {len(assets)} assets")
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Assets API error: {e}")
        traceback.print_exc()
        return jsonify({
            'assets': [],
            'total': 0,
            'status': f'Error: {str(e)}'
        }), 500

@app.route('/api/test')
def api_test():
    """Test endpoint"""
    return jsonify({
        'message': 'Production API is working',
        'status': 'OK',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 FINAL PRODUCTION ASSET MANAGEMENT SYSTEM")
    print("=" * 70)
    print("🌐 Dashboard: http://127.0.0.1:5000")
    print("🎯 Production: http://127.0.0.1:5000/production")
    print("🔧 API Test: http://127.0.0.1:5000/api/test")
    print("📊 API Stats: http://127.0.0.1:5000/api/stats")
    print("📋 API Assets: http://127.0.0.1:5000/api/assets")
    print("=" * 70)
    
    try:
        app.run(host='127.0.0.1', port=5000, debug=False, threaded=True)
    except Exception as e:
        print(f"❌ Server error: {e}")
        traceback.print_exc()