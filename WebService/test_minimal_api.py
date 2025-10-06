#!/usr/bin/env python3
# Minimal Flask test to check assets API
import os
import sqlite3
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/test-assets')
def test_assets():
    """Simple test endpoint for assets"""
    try:
        # Direct database access
        db_path = "../assets.db"
        
        if not os.path.exists(db_path):
            return jsonify({
                'error': f'Database not found at {db_path}',
                'working_dir': os.getcwd()
            })
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all assets
        cursor.execute("SELECT * FROM assets")
        rows = cursor.fetchall()
        
        # Convert to list of dicts
        assets = []
        for row in rows:
            asset = dict(row)
            assets.append(asset)
        
        cursor.execute("SELECT COUNT(*) FROM assets")
        total = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'assets': assets,
            'total': total,
            'sample_count': len(assets),
            'status': 'SUCCESS',
            'database_path': os.path.abspath(db_path)
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'assets': [],
            'total': 0,
            'status': 'ERROR'
        })

if __name__ == '__main__':
    print("Starting minimal test server...")
    app.run(host='127.0.0.1', port=5001, debug=True)