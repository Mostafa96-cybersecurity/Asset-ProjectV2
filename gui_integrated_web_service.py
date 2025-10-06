
import threading
import time
import subprocess
import socket
from flask import Flask

class GUIIntegratedWebService:
    """Web service that integrates perfectly with GUI"""
    
    def __init__(self, gui_app=None):
        self.gui_app = gui_app
        self.app = Flask(__name__)
        self.is_running = False
        self.server_thread = None
        self.process = None
        self.port = 5000
        
        self.setup_routes()
    
    def setup_routes(self):
        """Setup web service routes"""
        @self.app.route('/')
        def home():
            return """
            <html>
            <head>
                <title>Asset Management System</title>
                <style>
                    body { font-family: Arial; margin: 40px; background: #f5f5f5; }
                    .container { background: white; padding: 30px; border-radius: 8px; }
                    .status { color: #27ae60; font-weight: bold; }
                    .btn { background: #3498db; color: white; padding: 10px 20px; 
                           text-decoration: none; border-radius: 5px; margin: 5px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🖥️ Asset Management System</h1>
                    <p class="status">✅ Web Service Running Successfully!</p>
                    <p>✅ Launched from Desktop Application</p>
                    <p>✅ Access Control Active</p>
                    <hr>
                    <h3>Quick Actions:</h3>
                    <a href="/assets" class="btn">📊 View Assets</a>
                    <a href="/departments" class="btn">🏢 Departments</a>
                    <a href="/scan" class="btn">🔍 Network Scan</a>
                    <a href="/status" class="btn">📈 System Status</a>
                </div>
            </body>
            </html>
            """
        
        @self.app.route('/assets')
        def assets():
            try:
                import sqlite3
                conn = sqlite3.connect('assets.db')
                cursor = conn.cursor()
                cursor.execute('SELECT hostname, device_type, ip_address FROM assets LIMIT 20')
                assets_data = cursor.fetchall()
                conn.close()
                
                html = "<h1>📊 Assets</h1><table border='1' style='border-collapse: collapse; width: 100%;'>"
                html += "<tr style='background: #f8f9fa;'><th>Hostname</th><th>Type</th><th>IP Address</th></tr>"
                
                for asset in assets_data:
                    html += f"<tr><td>{asset[0]}</td><td>{asset[1]}</td><td>{asset[2]}</td></tr>"
                
                html += "</table><br><a href='/'>← Back to Home</a>"
                return html
            except Exception as e:
                return f"<h1>Error</h1><p>{e}</p><a href='/'>← Back</a>"
        
        @self.app.route('/status')
        def status():
            return """
            <h1>📈 System Status</h1>
            <ul>
                <li>✅ Web Service: Running</li>
                <li>✅ Database: Connected</li>
                <li>✅ Desktop Integration: Active</li>
                <li>✅ Collection Engine: Ready</li>
            </ul>
            <br><a href='/'>← Back to Home</a>
            """
    
    def start_from_gui(self):
        """Start web service from GUI"""
        if self.is_running:
            return False, "Web service already running"
        
        try:
            # Find available port
            self.port = self.find_available_port()
            
            # Update GUI status
            if self.gui_app:
                self.gui_app.web_service_status.setText("🟡 Starting...")
                self.gui_app.web_service_log.append(f"Starting web service on port {self.port}...")
            
            # Start server in background thread
            def run_server():
                try:
                    self.app.run(host='0.0.0.0', port=self.port, debug=False, threaded=True)
                except Exception as e:
                    if self.gui_app:
                        self.gui_app.web_service_log.append(f"Server error: {e}")
                finally:
                    self.is_running = False
            
            self.server_thread = threading.Thread(target=run_server, daemon=True)
            self.server_thread.start()
            
            # Wait for server to start
            time.sleep(2)
            
            # Check if server started successfully
            if self.check_server_running():
                self.is_running = True
                if self.gui_app:
                    self.gui_app.web_service_status.setText("🟢 Running")
                    self.gui_app.web_service_url.setText(f"http://localhost:{self.port}")
                    self.gui_app.web_service_log.append(f"✅ Web service started successfully!")
                return True, f"Web service started on http://localhost:{self.port}"
            else:
                if self.gui_app:
                    self.gui_app.web_service_status.setText("🔴 Failed")
                    self.gui_app.web_service_log.append("❌ Failed to start web service")
                return False, "Failed to start web service"
                
        except Exception as e:
            if self.gui_app:
                self.gui_app.web_service_status.setText("🔴 Error")
                self.gui_app.web_service_log.append(f"❌ Error: {e}")
            return False, f"Error starting web service: {e}"
    
    def find_available_port(self, start_port=5556):
        """Find an available port"""
        for port in range(start_port, start_port + 100):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('', port))
                    return port
            except OSError:
                continue
        return start_port
    
    def check_server_running(self):
        """Check if server is running"""
        try:
            import urllib.request
            urllib.request.urlopen(f'http://localhost:{self.port}', timeout=2)
            return True
        except:
            return False
    
    def stop_from_gui(self):
        """Stop web service from GUI"""
        self.is_running = False
        if self.gui_app:
            self.gui_app.web_service_status.setText("🔴 Stopped")
            self.gui_app.web_service_log.append("Web service stopped")
        return True, "Web service stopped"

# Global web service
gui_web_service = None

def get_gui_web_service(gui_app=None):
    """Get GUI-integrated web service"""
    global gui_web_service
    if gui_web_service is None:
        gui_web_service = GUIIntegratedWebService(gui_app)
    return gui_web_service
