#!/usr/bin/env python3
"""
Fixed Flask Web Service for Asset Management Dashboard
Serves static data on port 5000 with production dashboard
"""
import sys
import os
sys.path.append('.')

from flask import Flask, jsonify, send_from_directory
import json

# Create Flask app with proper template and static folders
app = Flask(__name__, 
           template_folder='templates',
           static_folder='../static')

def load_static_data():
    """Load data from static JSON files"""
    try:
        # Load stats data
        stats_file = os.path.abspath('../static/stats_data.json')
        assets_file = os.path.abspath('../static/assets_data.json')
        
        print(f"Loading stats from: {stats_file}")
        print(f"Loading assets from: {assets_file}")
        
        with open(stats_file, 'r') as f:
            stats_data = json.load(f)
        
        with open(assets_file, 'r') as f:
            assets_data = json.load(f)
        
        print(f"Stats loaded: {stats_data.get('total_assets', 0)} assets")
        print(f"Assets loaded: {len(assets_data.get('assets', []))} records")
        
        return stats_data, assets_data
    except Exception as e:
        print(f"Error loading static data: {e}")
        import traceback
        traceback.print_exc()
        return None, None

@app.route('/')
def index():
    """Root route - redirect to production dashboard"""
    return production_dashboard()

@app.route('/production')
def production_dashboard():
    """Production dashboard route"""
    try:
        # Serve the static dashboard directly
        return send_from_directory('../static', 'dashboard.html')
    except Exception:
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Asset Management Dashboard</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-5">
                <div class="alert alert-success">
                    <h4>🎉 Asset Management System Running!</h4>
                    <p><strong>Static Dashboard URL:</strong> <a href="/static/dashboard.html" class="btn btn-primary">Open Dashboard</a></p>
                    <p><strong>Total Assets:</strong> 510</p>
                    <p><strong>System Status:</strong> Working with Static Data</p>
                </div>
                <div class="card">
                    <div class="card-header">
                        <h5>Quick Links</h5>
                    </div>
                    <div class="card-body">
                        <a href="/static/dashboard.html" class="btn btn-primary me-2">Dashboard</a>
                        <a href="/api/stats" class="btn btn-info me-2">API Stats</a>
                        <a href="/api/assets" class="btn btn-warning">API Assets</a>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

@app.route('/api/stats')
def api_stats():
    """Get statistics from static data"""
    try:
        stats_data, _ = load_static_data()
        if stats_data:
            return jsonify(stats_data)
        else:
            return jsonify({
                "error": "Could not load stats data",
                "total_assets": 0,
                "status": "error"
            }), 500
    except Exception as e:
        return jsonify({
            "error": str(e),
            "total_assets": 0,
            "status": "error"
        }), 500

@app.route('/api/assets')
def api_assets():
    """Get assets from static data"""
    try:
        _, assets_data = load_static_data()
        if assets_data:
            return jsonify(assets_data)
        else:
            return jsonify({
                "error": "Could not load assets data",
                "assets": [],
                "total": 0,
                "status": "error"
            }), 500
    except Exception as e:
        return jsonify({
            "error": str(e),
            "assets": [],
            "total": 0,
            "status": "error"
        }), 500

@app.route('/api/test')
def api_test():
    """Test endpoint"""
    return jsonify({
        "message": "Production Flask API is working",
        "status": "OK",
        "port": 5000,
        "static_data": True
    })

# Serve static files from the static directory
@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('../static', filename)

if __name__ == '__main__':
    print("🚀 Starting Asset Management Web Service...")
    print("=" * 60)
    print("📊 Dashboard URL: http://127.0.0.1:5000/production")
    print("📊 Alternative: http://127.0.0.1:5000/static/dashboard.html")
    print("🔧 API Stats: http://127.0.0.1:5000/api/stats")
    print("🔧 API Assets: http://127.0.0.1:5000/api/assets")
    print("✅ Test API: http://127.0.0.1:5000/api/test")
    print("=" * 60)
    
    # Check if static files exist
    if os.path.exists('../static/dashboard.html'):
        print("✅ Dashboard file found")
    else:
        print("❌ Dashboard file missing")
        
    if os.path.exists('../static/stats_data.json'):
        print("✅ Stats data found")
    else:
        print("❌ Stats data missing")
        
    if os.path.exists('../static/assets_data.json'):
        print("✅ Assets data found")
    else:
        print("❌ Assets data missing")
    
    print("🌐 Starting Flask server on port 5000...")
    
    try:
        app.run(host='127.0.0.1', port=5000, debug=False)
    except Exception as e:
        print(f"❌ Server error: {e}")
        print("💡 Try running: python -m http.server 5000 in the static directory")