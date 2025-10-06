#!/usr/bin/env python3
"""
Debug Flask API Issues
"""
import sys
sys.path.append('.')

from flask import Flask, jsonify
import traceback

app = Flask(__name__)

@app.route('/test')
def test_basic():
    """Basic Flask test"""
    try:
        return jsonify({"status": "success", "message": "Flask is working"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/test-db')
def test_database():
    """Test database with asset manager"""
    try:
        from intelligent_app import IntelligentAssetManager
        manager = IntelligentAssetManager()
        assets = manager.get_all_assets()
        
        return jsonify({
            "status": "success", 
            "message": "Database working",
            "asset_count": len(assets),
            "sample_asset": assets[0] if assets else None
        })
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": str(e),
            "traceback": traceback.format_exc()
        }), 500

@app.route('/test-stats')
def test_stats():
    """Test stats generation"""
    try:
        from intelligent_app import IntelligentAssetManager
        manager = IntelligentAssetManager()
        stats = manager.get_comprehensive_stats()
        
        return jsonify({
            "status": "success",
            "stats": stats
        })
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": str(e),
            "traceback": traceback.format_exc()
        }), 500

if __name__ == '__main__':
    print("Starting Flask Debug Server...")
    print("Test endpoints:")
    print("  - http://127.0.0.1:5001/test")
    print("  - http://127.0.0.1:5001/test-db") 
    print("  - http://127.0.0.1:5001/test-stats")
    
    app.run(host='127.0.0.1', port=5001, debug=True)