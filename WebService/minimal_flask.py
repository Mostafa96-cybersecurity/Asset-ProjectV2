#!/usr/bin/env python3
"""
Minimal Flask Test for Asset Management
"""
import sys
import os
sys.path.append('.')

from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

@app.route('/')
def index():
    return "Minimal Asset API - Working"

@app.route('/api/test')
def test():
    return jsonify({"status": "success", "message": "Basic API working"})

@app.route('/api/db-test')
def db_test():
    try:
        db_path = "../assets.db"
        if not os.path.exists(db_path):
            return jsonify({"status": "error", "message": "Database not found"})
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Test enhanced table
        cursor.execute("SELECT COUNT(*) FROM assets_enhanced")
        count = cursor.fetchone()[0]
        
        # Get first 3 records
        cursor.execute("SELECT hostname, ip_address, device_type FROM assets_enhanced LIMIT 3")
        samples = cursor.fetchall()
        
        conn.close()
        
        return jsonify({
            "status": "success",
            "database_found": True,
            "enhanced_table_count": count,
            "sample_assets": samples
        })
        
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": str(e)
        })

@app.route('/api/simple-assets')
def simple_assets():
    try:
        db_path = "../assets.db"
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Simple query - just first 10 assets
        cursor.execute("""
            SELECT 
                id, hostname, ip_address, device_type,
                last_seen
            FROM assets_enhanced 
            LIMIT 10
        """)
        
        assets = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            "status": "success",
            "assets": assets,
            "count": len(assets)
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })

if __name__ == '__main__':
    print("Starting Minimal Flask Server...")
    print("Available endpoints:")
    print("  http://127.0.0.1:5002/")
    print("  http://127.0.0.1:5002/api/test")
    print("  http://127.0.0.1:5002/api/db-test")
    print("  http://127.0.0.1:5002/api/simple-assets")
    
    app.run(host='127.0.0.1', port=5002, debug=True)