#!/usr/bin/env python3
"""
DIAGNOSTIC WEB SERVICE - ENHANCED ERROR REPORTING
=================================================
This version provides detailed error reporting to help diagnose issues
"""

import socketserver
import http.server
import sqlite3
import os
import socket
import sys

PORT = 5556
db_path = os.path.join(os.path.dirname(__file__), 'assets.db')

def check_port_availability():
    """Check if port is available"""
    print(f"🔍 Checking port {PORT} availability...")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', PORT))
            print(f"✅ Port {PORT} is available")
            return True
    except socket.error as e:
        print(f"❌ Port {PORT} is NOT available: {e}")
        return False

def check_database():
    """Check database connectivity"""
    print("🔍 Checking database connectivity...")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM assets")
        count = cursor.fetchone()[0]
        conn.close()
        print(f"✅ Database OK: {count} assets found")
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

class DiagnosticHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        print(f"📥 GET request: {self.path}")
        
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Diagnostic Dashboard</title>
                <style>
                    body { font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin: 0; padding: 20px; }
                    .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
                    h1 { color: #333; text-align: center; }
                    .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
                    .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
                    .info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🔧 Diagnostic Dashboard</h1>
                    <div class="status success">✅ HTTP Server is working!</div>
                    <div class="status info">📡 Port 5556 is accessible</div>
                    <div class="status info">🌐 Network connectivity OK</div>
                    <div class="status info">🐍 Python web server operational</div>
                    <p><strong>This confirms the basic web service is functional.</strong></p>
                    <p>If you see this page, the core server infrastructure is working correctly.</p>
                </div>
            </body>
            </html>
            """
            
            self.wfile.write(html.encode())
            print("✅ Diagnostic page sent successfully")
        else:
            self.send_error(404)

def main():
    print("=" * 60)
    print("🔧 DIAGNOSTIC WEB SERVICE")
    print("=" * 60)
    
    # Run diagnostics
    port_ok = check_port_availability()
    db_ok = check_database()
    
    if not port_ok:
        print(f"❌ Cannot start server - port {PORT} is in use")
        return False
    
    print(f"🚀 Starting diagnostic server on port {PORT}...")
    
    try:
        # Create server with explicit address binding
        server_address = ('', PORT)
        httpd = socketserver.TCPServer(server_address, DiagnosticHandler)
        
        print(f"✅ Server bound to port {PORT}")
        print(f"🌐 Access at: http://localhost:{PORT}")
        print("=" * 60)
        print("Press Ctrl+C to stop")
        
        # Start serving
        httpd.serve_forever()
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return True
    except Exception as e:
        print(f"❌ Server error: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)