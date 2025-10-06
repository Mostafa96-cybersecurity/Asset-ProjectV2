#!/usr/bin/env python3
"""
Enhanced Complete Web Service with 100% Data Collection Automation
=================================================================
Main web service entry point with comprehensive automation for 100% asset data collection.
Launched by Asset_Management_System.bat -> launch_production_system.ps1

Features:
- 100% data collection automation for all registered devices
- Advanced notification system with real-time alerts
- Duplicate detection and resolution
- Device change monitoring
- Real-time performance monitoring
- Desktop notification windows
- Integration with GUI application
"""

import ipaddress  # For IP validation
import sys
import os
import logging
import asyncio
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_complete_web_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnhancedCompleteWebService:
    """Enhanced Complete Web Service with 100% Data Collection Automation"""
    
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.is_running = False
        self.automation_active = False
        
        # Initialize comprehensive automation components
        self.setup_automation_system()
        
        logger.info("🚀 Enhanced Complete Web Service initialized")
        logger.info(f"   🌐 Service URL: http://{host}:{port}")
        logger.info("   🤖 100% Data Collection Automation: READY")
        logger.info("   🔔 Advanced Notification System: READY")
        
    def setup_automation_system(self):
        """Setup comprehensive data collection automation system"""
        try:
            # Import comprehensive automation system
            from comprehensive_data_automation import ComprehensiveDataCollector
            from advanced_notification_system import AdvancedNotificationSystem
            
            # Initialize automation components
            self.data_collector = ComprehensiveDataCollector()
            self.notification_system = AdvancedNotificationSystem()
            
            # Initialize automation integration
            from comprehensive_data_automation import AutomationIntegration
            self.automation_integration = AutomationIntegration()
            
            logger.info("✅ Comprehensive automation system loaded successfully")
            logger.info("   📊 103-field database schema ready")
            logger.info("   🔍 WMI-based comprehensive data collection ready")
            logger.info("   🔔 Advanced notification system ready")
            logger.info("   🔄 Real-time duplicate detection ready")
            
        except ImportError as e:
            logger.error(f"❌ Failed to load automation system: {e}")
            logger.warning("⚠️ Running without automation features")
            self.data_collector = None
            self.notification_system = None
            self.automation_integration = None
            
    def start_automation(self):
        """Start 100% data collection automation"""
        if not self.automation_active and self.data_collector:
            try:
                logger.info("🚀 Starting 100% Data Collection Automation...")
                
                # Start comprehensive data collection
                self.automation_active = True
                
                # Start data collection in background
                asyncio.create_task(self.run_automation_loop())
                
                # Show desktop notification
                if self.notification_system:
                    self.notification_system.show_automation_started()
                
                logger.info("✅ 100% Data Collection Automation STARTED")
                logger.info("   🔍 Monitoring all registered devices")
                logger.info("   🔔 Real-time notifications enabled")
                logger.info("   📊 Performance monitoring active")
                
            except Exception as e:
                logger.error(f"❌ Failed to start automation: {e}")
                
    def stop_automation(self):
        """Stop data collection automation"""
        if self.automation_active:
            try:
                logger.info("⏹️ Stopping Data Collection Automation...")
                
                self.automation_active = False
                
                # Show desktop notification
                if self.notification_system:
                    self.notification_system.show_automation_stopped()
                
                logger.info("✅ Data Collection Automation STOPPED")
                
            except Exception as e:
                logger.error(f"❌ Failed to stop automation: {e}")
                
    async def run_automation_loop(self):
        """Main automation loop for 100% data collection"""
        while self.automation_active:
            try:
                if self.data_collector:
                    # Run comprehensive data collection
                    logger.info("🔍 Running comprehensive data collection cycle...")
                    
                    results = await self.data_collector.collect_all_registered_devices()
                    
                    # Process results
                    if results:
                        collected_count = results.get('collected_devices', 0)
                        missing_count = results.get('missing_data_devices', 0)
                        duplicate_count = results.get('duplicates_resolved', 0)
                        
                        logger.info("📊 Collection Cycle Complete:")
                        logger.info(f"   ✅ Devices collected: {collected_count}")
                        logger.info(f"   📋 Missing data resolved: {missing_count}")
                        logger.info(f"   🔄 Duplicates resolved: {duplicate_count}")
                        
                        # Show notification for significant events
                        if missing_count > 0 or duplicate_count > 0:
                            if self.notification_system:
                                self.notification_system.show_collection_update(
                                    collected_count, missing_count, duplicate_count
                                )
                    
                    # Wait before next cycle (configurable)
                    await asyncio.sleep(300)  # 5 minutes between cycles
                else:
                    await asyncio.sleep(60)  # Wait 1 minute if no collector
                    
            except Exception as e:
                logger.error(f"❌ Automation loop error: {e}")
                await asyncio.sleep(60)  # Wait before retry
                
    def get_automation_status(self):
        """Get current automation status"""
        return {
            'automation_active': self.automation_active,
            'service_running': self.is_running,
            'timestamp': datetime.now().isoformat(),
            'components': {
                'data_collector': self.data_collector is not None,
                'notification_system': self.notification_system is not None,
                'automation_integration': self.automation_integration is not None
            }
        }
        
    def start_web_service(self):
        """Start the enhanced web service"""
        try:
            logger.info("[STARTING] Enhanced Complete Web Service...")
            
            # Try to import and start web service
            try:
                # Import GUI application for integration
                from gui.app import MainWindow
                logger.info("[OK] GUI integration available")
                
                # Try to import web service components with safe handling
                try:
                    from flask import Flask, jsonify, render_template_string
                    
                    app = Flask(__name__)
                    
                    @app.route('/')
                    def index():
                        return render_template_string("""
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <title>Enhanced Complete Web Service</title>
                            <style>
                                body { font-family: Arial, sans-serif; margin: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
                                .container { max-width: 800px; margin: 0 auto; padding: 20px; background: rgba(255,255,255,0.1); border-radius: 15px; }
                                .status { background: #4CAF50; padding: 15px; border-radius: 10px; margin: 20px 0; }
                                .automation { background: #2196F3; padding: 15px; border-radius: 10px; margin: 20px 0; }
                                .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
                                .stat-card { background: rgba(255,255,255,0.2); padding: 15px; border-radius: 10px; text-align: center; }
                                button { background: #FF9800; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-size: 16px; }
                                button:hover { background: #F57C00; }
                            </style>
                        </head>
                        <body>
                            <div class="container">
                                <h1>Enhanced Complete Web Service</h1>
                                <div class="status">
                                    <h2>Service Status: RUNNING</h2>
                                    <p>Enhanced Complete Web Service is active and ready for 100% data collection automation.</p>
                                </div>
                                
                                <div class="automation">
                                    <h2>100% Data Collection Automation</h2>
                                    <p>Comprehensive automation system for complete asset data collection from all registered devices.</p>
                                    <button onclick="toggleAutomation()">{{ 'Stop' if automation_active else 'Start' }} Automation</button>
                                </div>
                                
                                <div class="stats">
                                    <div class="stat-card">
                                        <h3>Data Collection</h3>
                                        <p>103-Field Schema</p>
                                        <p>WMI + SSH + SNMP</p>
                                    </div>
                                    <div class="stat-card">
                                        <h3>Notifications</h3>
                                        <p>Real-time Alerts</p>
                                        <p>Desktop Notifications</p>
                                    </div>
                                    <div class="stat-card">
                                        <h3>Automation</h3>
                                        <p>{{ 'ACTIVE' if automation_active else 'INACTIVE' }}</p>
                                        <p>Continuous Monitoring</p>
                                    </div>
                                    <div class="stat-card">
                                        <h3>Performance</h3>
                                        <p>Real-time Metrics</p>
                                        <p>Performance Monitoring</p>
                                    </div>
                                </div>
                                
                                <div style="text-align: center; margin-top: 30px;">
                                    <button onclick="openGUI()">Open Desktop GUI</button>
                                    <button onclick="viewLogs()">View Logs</button>
                                    <button onclick="viewStatus()">System Status</button>
                                </div>
                            </div>
                            
                            <script>
                                function toggleAutomation() {
                                    fetch('/api/automation/toggle', {method: 'POST'})
                                        .then(response => response.json())
                                        .then(data => {
                                            alert(data.message);
                                            location.reload();
                                        });
                                }
                                
                                function openGUI() {
                                    fetch('/api/gui/launch', {method: 'POST'})
                                        .then(response => response.json())
                                        .then(data => alert(data.message));
                                }
                                
                                function viewLogs() {
                                    window.open('/api/logs', '_blank');
                                }
                                
                                function viewStatus() {
                                    window.open('/api/status', '_blank');
                                }
                            </script>
                        </body>
                        </html>
                        """, automation_active=self.automation_active)
                    
                    @app.route('/api/automation/toggle', methods=['POST'])
                    def toggle_automation():
                        try:
                            if self.automation_active:
                                self.stop_automation()
                                return jsonify({'success': True, 'message': 'Automation stopped successfully'})
                            else:
                                self.start_automation()
                                return jsonify({'success': True, 'message': 'Automation started successfully'})
                        except Exception as e:
                            return jsonify({'success': False, 'message': f'Error: {e}'})
                    
                    @app.route('/api/gui/launch', methods=['POST'])
                    def launch_gui():
                        try:
                            import subprocess
                            subprocess.Popen([sys.executable, os.path.join(project_root, 'gui', 'app.py')])
                            return jsonify({'success': True, 'message': 'Desktop GUI launched successfully'})
                        except Exception as e:
                            return jsonify({'success': False, 'message': f'Error launching GUI: {e}'})
                    
                    @app.route('/api/status')
                    def get_status():
                        status = self.get_automation_status()
                        return jsonify(status)
                    
                    @app.route('/api/logs')
                    def get_logs():
                        try:
                            with open('enhanced_complete_web_service.log', 'r') as f:
                                logs = f.read()
                            return f"<pre>{logs}</pre>"
                        except:
                            return "No logs available"
                    
                    # Start Flask app
                    self.is_running = True
                    logger.info(f"[SUCCESS] Enhanced Complete Web Service started on http://{self.host}:{self.port}")
                    logger.info("[INFO] Web interface available with automation controls")
                    
                    app.run(host=self.host, port=self.port, debug=False)
                    
                except ImportError as e:
                    logger.warning(f"[WARNING] Flask not available: {e}")
                    logger.info("[INFO] Starting simple HTTP server as fallback")
                    self.start_simple_server()
                    
            except ImportError:
                # Fallback: Simple HTTP server
                logger.warning("[WARNING] GUI integration not available, starting simple HTTP server")
                self.start_simple_server()
                
        except Exception as e:
            logger.error(f"[ERROR] Failed to start web service: {e}")
            logger.info("[INFO] Desktop application with automation is still available")
            
    def start_simple_server(self):
        """Start simple HTTP server as fallback"""
        try:
            import http.server
            import socketserver
            
            class AutomationHandler(http.server.SimpleHTTPRequestHandler):
                def do_GET(self):
                    if self.path == '/':
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        
                        html = f"""
                        <!DOCTYPE html>
                        <html>
                        <head><title>Enhanced Complete Web Service</title></head>
                        <body style="font-family: Arial, sans-serif; margin: 40px; background: #f0f0f0;">
                            <h1>🚀 Enhanced Complete Web Service</h1>
                            <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                                <h2>✅ Service Status: RUNNING</h2>
                                <p>Enhanced Complete Web Service is active on port {self.port}</p>
                                <h3>🤖 100% Data Collection Automation</h3>
                                <p>Status: {'ACTIVE' if self.automation_active else 'INACTIVE'}</p>
                                <p>Comprehensive automation system for complete asset data collection.</p>
                                <h3>📊 Features</h3>
                                <ul>
                                    <li>103-Field Database Schema</li>
                                    <li>WMI + SSH + SNMP Collection</li>
                                    <li>Real-time Notifications</li>
                                    <li>Duplicate Detection & Resolution</li>
                                    <li>Performance Monitoring</li>
                                </ul>
                            </div>
                        </body>
                        </html>
                        """
                        self.wfile.write(html.encode())
                    else:
                        super().do_GET()
            
            with socketserver.TCPServer((self.host, self.port), AutomationHandler) as httpd:
                self.is_running = True
                logger.info(f"✅ Simple HTTP server started on http://{self.host}:{self.port}")
                httpd.serve_forever()
                
        except Exception as e:
            logger.error(f"❌ Failed to start simple server: {e}")

def main():
    """Main entry point for Enhanced Complete Web Service"""
    logger.info("=" * 60)
    logger.info("🚀 ENHANCED COMPLETE WEB SERVICE STARTING")
    logger.info("=" * 60)
    logger.info("   💼 Asset Management System - Production Mode")
    logger.info("   🤖 100% Data Collection Automation")
    logger.info("   🔔 Advanced Notification System")
    logger.info("   📊 Real-time Performance Monitoring")
    logger.info("=" * 60)
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Enhanced Complete Web Service')
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to bind to')
    parser.add_argument('--auto-start', action='store_true', help='Auto-start automation')
    args = parser.parse_args()
    
    # Create and start service
    service = EnhancedCompleteWebService(host=args.host, port=args.port)
    
    # Auto-start automation if requested
    if args.auto_start:
        logger.info("🚀 Auto-starting 100% Data Collection Automation...")
        service.start_automation()
    
    try:
        # Start the web service
        service.start_web_service()
    except KeyboardInterrupt:
        logger.info("⏹️ Received shutdown signal")
        service.stop_automation()
        logger.info("✅ Enhanced Complete Web Service stopped")
    except Exception as e:
        logger.error(f"❌ Service error: {e}")
    
if __name__ == '__main__':
    main()