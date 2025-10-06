#!/usr/bin/env python3
"""
Fixed Flask API Server for Asset Management
"""
import sys
import os
sys.path.append('.')

from flask import Flask, jsonify, render_template
import sqlite3
import traceback

app = Flask(__name__, template_folder='../templates', static_folder='../static')

def get_assets_data():
    """Get assets data with error handling"""
    try:
        db_path = "../assets.db"
        if not os.path.exists(db_path):
            return [], 0, "Database not found"
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
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
                processor_name, total_physical_memory_gb, operating_system,
                COALESCE(assigned_department, 'Unassigned') as assigned_department,
                system_manufacturer, system_model,
                mac_address, current_user,
                collection_method, data_completeness_score,
                last_seen, created_at, updated_at
            FROM assets_enhanced 
            ORDER BY 
                CASE 
                    WHEN device_status = 'Online' OR ping_response_ms > 0 THEN 1
                    ELSE 2
                END,
                hostname
        """)
        
        assets = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return assets, len(assets), "OK"
        
    except Exception as e:
        print(f"Database error: {e}")
        traceback.print_exc()
        return [], 0, f"Error: {str(e)}"

def get_stats_data():
    """Get statistics with error handling"""
    try:
        db_path = "../assets.db"
        if not os.path.exists(db_path):
            return {"total_assets": 0, "device_status": {"online": 0, "offline": 0}, "status": "Database not found"}
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM assets_enhanced")
        total_count = cursor.fetchone()[0]
        
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
            device_status[row[0]] = row[1]
        
        # Get incomplete assets count
        cursor.execute("""
            SELECT COUNT(*) FROM assets_enhanced
            WHERE (processor_name IS NULL OR processor_name = '') AND 
                  (operating_system IS NULL OR operating_system = '') AND 
                  (total_physical_memory_gb IS NULL OR total_physical_memory_gb = 0)
        """)
        incomplete_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_assets": total_count,
            "total_devices": total_count,
            "device_status": device_status,
            "incomplete_assets": incomplete_count,
            "status": "OK"
        }
        
    except Exception as e:
        print(f"Stats error: {e}")
        return {
            "total_assets": 0,
            "total_devices": 0, 
            "device_status": {"online": 0, "offline": 0, "unknown": 0},
            "status": f"Error: {str(e)}"
        }

@app.route('/')
def index():
    return "Fixed Asset Management API - Working"

@app.route('/production')
def production_dashboard():
    """Production dashboard route"""
    try:
        return render_template('production_dashboard.html')
    except Exception as e:
        return f"Dashboard error: {str(e)}"

@app.route('/api/stats')
def api_stats():
    """Get statistics"""
    try:
        stats = get_stats_data()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500

@app.route('/api/assets')
def api_assets():
    """Get assets"""
    try:
        assets, total, status = get_assets_data()
        
        return jsonify({
            "assets": assets,
            "total": total,
            "status": status,
            "classification_enabled": True
        })
    except Exception as e:
        return jsonify({"error": str(e), "assets": [], "total": 0}), 500

@app.route('/api/test')
def api_test():
    """Test endpoint"""
    return jsonify({"message": "Fixed API is working", "status": "OK"})

if __name__ == '__main__':
    print("Starting Fixed Asset Management API...")
    print("Dashboard: http://127.0.0.1:5000/production")
    print("API Test: http://127.0.0.1:5000/api/test")
    print("API Stats: http://127.0.0.1:5000/api/stats")
    print("API Assets: http://127.0.0.1:5000/api/assets")
    
    try:
        app.run(host='127.0.0.1', port=5000, debug=False)
    except Exception as e:
        print(f"Server error: {e}")