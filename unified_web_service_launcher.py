#!/usr/bin/env python3
"""
🌐 UNIFIED WEB SERVICE LAUNCHER
==============================
Launches the asset management web service with enhanced security
"""

import sys
import os
from pathlib import Path
import subprocess
import threading
import time
import requests
from datetime import datetime

# Import comprehensive logging
try:
    from comprehensive_logging_system import log_web_service, start_job, complete_job
except ImportError:
    def log_web_service(level, message, **kwargs):
        print(f"[WEB_SERVICE_LAUNCHER] {level}: {message}")
    def start_job(job_id, feature, description):
        print(f"Starting job: {description}")
        return job_id
    def complete_job(job_id, success, message=""):
        print(f"Job completed: {success}")

class WebServiceLauncher:
    """Unified web service launcher with enhanced security"""
    
    def __init__(self):
        self.port = 5556
        self.host = "0.0.0.0"
        self.process = None
        self.running = False
        
    def check_dependencies(self) -> bool:
        """Check if all required dependencies are available"""
        try:
            log_web_service('INFO', '🔍 Checking web service dependencies...')
            
            required_files = [
                'enhanced_access_control_system.py',
                'secure_web_service.py',
                'complete_department_web_service.py',
                'comprehensive_logging_system.py'
            ]
            
            missing_files = []
            for file in required_files:
                if not Path(file).exists():
                    missing_files.append(file)
            
            if missing_files:
                log_web_service('ERROR', f'Missing required files: {missing_files}')
                return False
            
            # Check Python packages
            try:
                import flask
                import sqlite3
                import ipaddress
                log_web_service('INFO', '✅ All required Python packages available')
            except ImportError as e:
                log_web_service('ERROR', f'Missing Python package: {e}')
                return False
                
            log_web_service('INFO', '✅ All dependencies satisfied')
            return True
            
        except Exception as e:
            log_web_service('ERROR', f'Dependency check failed: {e}')
            return False
    
    def check_port_availability(self) -> bool:
        """Check if the port is available"""
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                result = s.connect_ex(('127.0.0.1', self.port))
                if result == 0:
                    log_web_service('WARNING', f'Port {self.port} is already in use')
                    return False
                else:
                    log_web_service('INFO', f'✅ Port {self.port} is available')
                    return True
        except Exception as e:
            log_web_service('ERROR', f'Port check failed: {e}')
            return False
    
    def launch_secure_service(self) -> bool:
        """Launch the secure web service"""
        try:
            job_id = start_job("web_service_launch", "Web Service", "Launching secure web service")
            
            log_web_service('INFO', f'🚀 Starting secure web service on {self.host}:{self.port}')
            
            # Try to start the secure web service
            try:
                from secure_web_service import run_web_service
                log_web_service('INFO', '🔐 Starting with enhanced security features')
                
                # Run in a separate thread
                def run_service():
                    try:
                        run_web_service()
                    except Exception as e:
                        log_web_service('ERROR', f'Secure web service error: {e}')
                
                service_thread = threading.Thread(target=run_service, daemon=True)
                service_thread.start()
                
                # Wait a moment for the service to start
                time.sleep(3)
                
                # Test if service is running
                if self.test_service():
                    complete_job(job_id, True, "Secure web service started successfully")
                    self.running = True
                    return True
                else:
                    raise Exception("Service failed to start properly")
                    
            except ImportError:
                log_web_service('WARNING', 'Secure web service not available, trying department service')
                return self.launch_department_service()
                
        except Exception as e:
            complete_job(job_id, False, f"Failed to start secure service: {e}")
            log_web_service('ERROR', f'Failed to launch secure service: {e}')
            return self.launch_department_service()
    
    def launch_department_service(self) -> bool:
        """Launch the department web service as fallback"""
        try:
            job_id = start_job("dept_web_service_launch", "Web Service", "Launching department web service")
            
            log_web_service('INFO', '🌐 Starting department web service (fallback mode)')
            
            from complete_department_web_service import CompleteDepartmentWebService
            
            # Create and run the service
            service = CompleteDepartmentWebService()
            
            def run_dept_service():
                try:
                    service.app.run(host=self.host, port=self.port, debug=False, threaded=True)
                except Exception as e:
                    log_web_service('ERROR', f'Department web service error: {e}')
            
            service_thread = threading.Thread(target=run_dept_service, daemon=True)
            service_thread.start()
            
            # Wait a moment for the service to start
            time.sleep(3)
            
            # Test if service is running
            if self.test_service():
                complete_job(job_id, True, "Department web service started successfully")
                self.running = True
                return True
            else:
                complete_job(job_id, False, "Department service failed to start properly")
                return False
                
        except Exception as e:
            complete_job(job_id, False, f"Failed to start department service: {e}")
            log_web_service('ERROR', f'Failed to launch department service: {e}')
            return False
    
    def test_service(self) -> bool:
        """Test if the web service is responding"""
        try:
            response = requests.get(f'http://127.0.0.1:{self.port}/api/status', timeout=5)
            if response.status_code == 200:
                log_web_service('INFO', '✅ Web service is responding correctly')
                return True
            else:
                log_web_service('WARNING', f'Web service responded with status {response.status_code}')
                return False
        except requests.exceptions.RequestException as e:
            log_web_service('WARNING', f'Web service test failed: {e}')
            return False
    
    def start(self) -> bool:
        """Start the web service with full initialization"""
        try:
            log_web_service('INFO', '🌐 Initializing Unified Web Service Launcher')
            
            # Check dependencies
            if not self.check_dependencies():
                log_web_service('ERROR', '❌ Dependency check failed - cannot start web service')
                return False
            
            # Check port availability
            if not self.check_port_availability():
                log_web_service('WARNING', f'Port {self.port} is in use - attempting to start anyway')
            
            # Try to launch the service
            if self.launch_secure_service():
                log_web_service('INFO', f'✅ Web service successfully started on http://localhost:{self.port}')
                return True
            else:
                log_web_service('ERROR', '❌ Failed to start web service')
                return False
                
        except Exception as e:
            log_web_service('ERROR', f'Web service launcher failed: {e}')
            return False
    
    def get_status(self) -> dict:
        """Get current status of the web service"""
        try:
            if not self.running:
                return {
                    'running': False,
                    'message': 'Web service is not running'
                }
            
            # Test service response
            if self.test_service():
                return {
                    'running': True,
                    'port': self.port,
                    'url': f'http://localhost:{self.port}',
                    'message': 'Web service is running and responding'
                }
            else:
                return {
                    'running': False,
                    'message': 'Web service process exists but not responding'
                }
                
        except Exception as e:
            return {
                'running': False,
                'message': f'Status check failed: {e}'
            }
    
    def open_in_browser(self) -> bool:
        """Open the web service in default browser"""
        try:
            import webbrowser
            url = f'http://localhost:{self.port}'
            
            if not self.running or not self.test_service():
                log_web_service('ERROR', 'Cannot open browser - web service is not running')
                return False
            
            log_web_service('INFO', f'🌐 Opening web service in browser: {url}')
            webbrowser.open(url)
            return True
            
        except Exception as e:
            log_web_service('ERROR', f'Failed to open browser: {e}')
            return False

# Global launcher instance
launcher = WebServiceLauncher()

def start_web_service():
    """Start the web service"""
    return launcher.start()

def get_web_service_status():
    """Get web service status"""
    return launcher.get_status()

def open_web_service_in_browser():
    """Open web service in browser"""
    return launcher.open_in_browser()

def main():
    """Main function for direct execution"""
    print("[LAUNCHER] Unified Web Service Launcher")
    print("=" * 50)
    
    if start_web_service():
        print(f"\\n✅ Web service started successfully!")
        print(f"[INFO] Access URL: http://localhost:{launcher.port}")
        print("\\n📊 Service Status:")
        status = get_web_service_status()
        for key, value in status.items():
            print(f"   {key}: {value}")
        
        print("\\nPress Ctrl+C to stop the service...")
        try:
            while True:
                time.sleep(10)
                if not launcher.test_service():
                    print("[WARNING] Service stopped responding")
                    break
        except KeyboardInterrupt:
            print("\\n🛑 Stopping web service...")
            
    else:
        print("[ERROR] Failed to start web service")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())