#!/usr/bin/env python3
"""
🎯 ULTRA SIMPLE FLASK TEST
==========================
Just test if Flask works on port 5556
"""

from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🎯 Test Dashboard</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                text-align: center; 
                padding: 50px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
            }
            .card { 
                background: white; 
                color: #333; 
                padding: 40px; 
                border-radius: 20px; 
                display: inline-block;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🎯 Dashboard is Working!</h1>
            <h2>✅ Flask is running on Port 5556</h2>
            <p><strong>This proves the port and Flask are working correctly.</strong></p>
            <p>🌐 URL: http://localhost:5556</p>
            <p>📊 Single Port Solution Success!</p>
            <hr>
            <p><em>Now we can build the full dashboard on this working foundation.</em></p>
        </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    print("🎯 ULTRA SIMPLE FLASK TEST")
    print("=" * 30)
    print("🌐 Testing Flask on port 5556")
    print("✨ If this works, the problem is in the dashboard code")
    print("=" * 30)
    
    try:
        print("🚀 Starting Flask test server...")
        app.run(host='0.0.0.0', port=5556, debug=True)
    except Exception as e:
        print(f"❌ Error: {e}")
        input("Press Enter to exit...")