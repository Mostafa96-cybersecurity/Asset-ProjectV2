#!/usr/bin/env python3
"""
🌐 ENHANCED WEB SERVICE MANAGER
===============================
Fixes all web service button issues and adds comprehensive logging
"""

import time
import subprocess
import socket
import webbrowser
import psutil
from pathlib import Path
from datetime import datetime
from typing import Tuple, Dict, Any, List
import json
import logging

# Import comprehensive logging
try:
    from comprehensive_logging_system import log_web_service, start_job, complete_job, update_job_progress
    from web_service_config import get_web_service_config, get_web_service_url, get_web_service_port, get_web_service_scripts
    WEB_SERVICE_CONFIG_AVAILABLE = True
except ImportError:
    # Fallback logging and config
    def log_web_service(level, message, **kwargs):
        print(f"[WEB_SERVICE] {level}: {message}")
    def start_job(job_id, feature, description):
        print(f"Starting job: {description}")
    def complete_job(job_id, success, message=""):
        print(f"Job completed: {success}")
    def update_job_progress(job_id, progress, message=""):
        print(f"Progress {progress}%: {message}")
    
    WEB_SERVICE_CONFIG_AVAILABLE = False
    
    # Fallback configuration
    def get_web_service_config():
        return {'port': 5556, 'host': 'localhost'}
    def get_web_service_url():
        return "http://localhost:5556"
    def get_web_service_port():
        return 5556
    def get_web_service_scripts():
        return ['complete_department_web_service.py', 'working_web_service.py']

class EnhancedWebServiceManager:
    """Enhanced web service manager with comprehensive logging and error handling"""
    
    def __init__(self):
        self.process = None
        self.is_running = False
        
        # Load unified configuration
        if WEB_SERVICE_CONFIG_AVAILABLE:
            config = get_web_service_config()
            self.port = config.get('port', 8080)
            self.host = config.get('host', 'localhost')
        else:
            self.port = 8080
            self.host = 'localhost'
            
        self.service_url = f"http://{self.host}:{self.port}"
        self.config_file = Path("web_service_config.json")
        self.log_file = Path("logs/web_service.log")
        
        # Create logs directory
        self.log_file.parent.mkdir(exist_ok=True)
        
        # Load any additional configuration
        self.load_config()
        
        # Setup logging
        self.setup_logging()
        
        log_web_service('INFO', f'🌐 Enhanced Web Service Manager initialized for {self.service_url}')
        
    def setup_logging(self):
        """Setup dedicated web service logging"""
        self.logger = logging.getLogger('WebServiceManager')
        self.logger.setLevel(logging.DEBUG)
        
        # File handler
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
    def load_config(self):
        """Load web service configuration"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.port = config.get('port', 5556)
                    self.host = config.get('host', 'localhost')
                    self.service_url = f"http://{self.host}:{self.port}"
                    log_web_service('INFO', f'Configuration loaded: {self.service_url}')
        except Exception as e:
            log_web_service('WARNING', f'Failed to load config: {e}')
            
    def save_config(self):
        """Save web service configuration"""
        try:
            config = {
                'port': self.port,
                'host': self.host,
                'last_started': datetime.now().isoformat()
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            log_web_service('DEBUG', 'Configuration saved')
        except Exception as e:
            log_web_service('ERROR', f'Failed to save config: {e}')
            
    def find_available_port(self, start_port: int = 5556) -> int:
        """Find an available port"""
        for port in range(start_port, start_port + 50):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('', port))
                    return port
            except OSError:
                continue
        return start_port
        
    def is_port_in_use(self, port: int) -> bool:
        """Check if port is in use"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return False
        except OSError:
            return True
            
    def kill_existing_service(self) -> bool:
        """Kill any existing web service on the port"""
        try:
            killed_any = False
            for proc in psutil.process_iter(['pid', 'name', 'connections']):
                try:
                    connections = proc.info['connections']
                    if connections:
                        for conn in connections:
                            if (hasattr(conn, 'laddr') and 
                                conn.laddr and 
                                conn.laddr.port == self.port):
                                log_web_service('INFO', f'Killing existing process on port {self.port}: PID {proc.pid}')
                                proc.kill()
                                killed_any = True
                                break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return killed_any
        except Exception as e:
            log_web_service('ERROR', f'Error killing existing service: {e}')
            return False
            
    def start_service(self) -> Tuple[bool, str]:
        """Start the web service with comprehensive error handling"""
        job_id = f"web_start_{int(time.time())}"
        start_job(job_id, 'web_service', 'Starting web service')
        
        try:
            # Check if already running
            if self.is_running and self.check_service_health():
                complete_job(job_id, False, 'Service already running')
                return False, "Web service is already running"
            
            update_job_progress(job_id, 10, 'Checking port availability')
            
            # Kill existing service if needed
            if self.is_port_in_use(self.port):
                log_web_service('WARNING', f'Port {self.port} is in use, attempting to free it')
                self.kill_existing_service()
                time.sleep(2)
                
            # Find available port if current is still busy
            if self.is_port_in_use(self.port):
                original_port = self.port
                self.port = self.find_available_port(self.port)
                self.service_url = f"http://{self.host}:{self.port}"
                log_web_service('INFO', f'Port {original_port} busy, using port {self.port}')
                
            update_job_progress(job_id, 30, f'Starting service on port {self.port}')
            
            # Determine which web service to start
            if WEB_SERVICE_CONFIG_AVAILABLE:
                web_service_scripts = get_web_service_scripts()
            else:
                web_service_scripts = [
                    'complete_department_web_service.py',
                    'working_web_service.py',
                    'gui_integrated_web_service.py'
                ]
            
            script_to_use = None
            for script in web_service_scripts:
                if Path(script).exists():
                    script_to_use = script
                    break
                    
            if not script_to_use:
                complete_job(job_id, False, 'No web service script found')
                return False, "No web service script found"
                
            update_job_progress(job_id, 50, f'Using script: {script_to_use}')
            
            # Start the service
            python_exe = self.find_python_executable()
            
            log_web_service('INFO', f'Starting web service: {python_exe} {script_to_use}')
            
            self.process = subprocess.Popen(
                [python_exe, script_to_use, '--port', str(self.port), '--host', self.host],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                cwd=Path.cwd()
            )
            
            update_job_progress(job_id, 70, 'Service process started, waiting for startup')
            
            # Wait for service to start
            start_time = time.time()
            timeout = 15
            
            while time.time() - start_time < timeout:
                if self.check_service_health():
                    self.is_running = True
                    self.save_config()
                    log_web_service('INFO', f'✅ Web service started successfully on {self.service_url}')
                    complete_job(job_id, True, f'Service running on {self.service_url}')
                    return True, f"Web service started successfully on {self.service_url}"
                    
                if self.process.poll() is not None:
                    # Process died
                    stdout, stderr = self.process.communicate(timeout=5)
                    error_msg = f"Service process died. STDERR: {stderr[:500]}"
                    log_web_service('ERROR', error_msg)
                    complete_job(job_id, False, error_msg)
                    return False, error_msg
                    
                time.sleep(1)
                update_job_progress(job_id, 70 + int((time.time() - start_time) / timeout * 20), 
                                  'Waiting for service to respond')
                
            # Timeout
            self.stop_service()
            complete_job(job_id, False, 'Service startup timeout')
            return False, "Service startup timeout"
            
        except Exception as e:
            error_msg = f"Failed to start web service: {e}"
            log_web_service('ERROR', error_msg)
            complete_job(job_id, False, error_msg)
            return False, error_msg
            
    def stop_service(self) -> Tuple[bool, str]:
        """Stop the web service"""
        job_id = f"web_stop_{int(time.time())}"
        start_job(job_id, 'web_service', 'Stopping web service')
        
        try:
            if not self.is_running and not self.process:
                complete_job(job_id, True, 'Service was not running')
                return True, "Web service was not running"
                
            update_job_progress(job_id, 30, 'Terminating service process')
            
            if self.process:
                try:
                    # Try graceful termination first
                    self.process.terminate()
                    
                    # Wait up to 5 seconds for graceful shutdown
                    try:
                        self.process.wait(timeout=5)
                        log_web_service('INFO', 'Service terminated gracefully')
                    except subprocess.TimeoutExpired:
                        # Force kill if it doesn't terminate gracefully
                        self.process.kill()
                        log_web_service('WARNING', 'Service force-killed after timeout')
                        
                except Exception as e:
                    log_web_service('ERROR', f'Error terminating process: {e}')
                    
                self.process = None
                
            update_job_progress(job_id, 70, 'Cleaning up port bindings')
            
            # Kill any remaining processes on the port
            self.kill_existing_service()
            
            self.is_running = False
            log_web_service('INFO', '🛑 Web service stopped successfully')
            complete_job(job_id, True, 'Service stopped successfully')
            return True, "Web service stopped successfully"
            
        except Exception as e:
            error_msg = f"Error stopping web service: {e}"
            log_web_service('ERROR', error_msg)
            complete_job(job_id, False, error_msg)
            return False, error_msg
            
    def restart_service(self) -> Tuple[bool, str]:
        """Restart the web service"""
        job_id = f"web_restart_{int(time.time())}"
        start_job(job_id, 'web_service', 'Restarting web service')
        
        try:
            update_job_progress(job_id, 20, 'Stopping current service')
            
            # Stop current service
            stop_success, stop_msg = self.stop_service()
            if not stop_success:
                complete_job(job_id, False, f'Failed to stop service: {stop_msg}')
                return False, f"Failed to stop service: {stop_msg}"
                
            update_job_progress(job_id, 50, 'Waiting before restart')
            time.sleep(2)  # Wait a bit before restart
            
            update_job_progress(job_id, 70, 'Starting service')
            
            # Start service
            start_success, start_msg = self.start_service()
            if start_success:
                complete_job(job_id, True, 'Service restarted successfully')
                return True, f"Web service restarted successfully: {start_msg}"
            else:
                complete_job(job_id, False, f'Failed to start service: {start_msg}')
                return False, f"Failed to start service: {start_msg}"
                
        except Exception as e:
            error_msg = f"Error restarting web service: {e}"
            log_web_service('ERROR', error_msg)
            complete_job(job_id, False, error_msg)
            return False, error_msg
            
    def open_in_browser(self) -> Tuple[bool, str]:
        """Open web service in browser"""
        try:
            if not self.check_service_health():
                return False, "Web service is not running"
                
            log_web_service('INFO', f'Opening {self.service_url} in browser')
            webbrowser.open(self.service_url)
            return True, f"Opened {self.service_url} in browser"
            
        except Exception as e:
            error_msg = f"Failed to open browser: {e}"
            log_web_service('ERROR', error_msg)
            return False, error_msg
            
    def check_service_health(self) -> bool:
        """Check if web service is responding"""
        try:
            import urllib.request
            response = urllib.request.urlopen(self.service_url, timeout=3)
            return response.status == 200
        except:
            return False
            
    def get_service_status(self) -> Dict[str, Any]:
        """Get comprehensive service status"""
        try:
            is_healthy = self.check_service_health()
            
            status = {
                'is_running': self.is_running,
                'is_healthy': is_healthy,
                'url': self.service_url,
                'port': self.port,
                'host': self.host,
                'process_alive': self.process is not None and self.process.poll() is None,
                'port_in_use': self.is_port_in_use(self.port),
                'last_check': datetime.now().isoformat()
            }
            
            if self.process:
                status['process_id'] = self.process.pid
                
            return status
        except Exception as e:
            log_web_service('ERROR', f'Error getting service status: {e}')
            return {'error': str(e)}
            
    def find_python_executable(self) -> str:
        """Find the appropriate Python executable"""
        python_options = [
            str(Path('.venv/Scripts/python.exe')),
            'python',
            'python3',
            'py'
        ]
        
        for python_exe in python_options:
            try:
                result = subprocess.run([python_exe, '--version'], 
                                      capture_output=True, timeout=5)
                if result.returncode == 0:
                    return python_exe
            except:
                continue
                
        return 'python'  # Fallback
        
    def get_recent_logs(self, lines: int = 50) -> List[str]:
        """Get recent web service logs"""
        try:
            if self.log_file.exists():
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    all_lines = f.readlines()
                    return all_lines[-lines:] if len(all_lines) > lines else all_lines
            return []
        except Exception as e:
            return [f"Error reading logs: {e}"]

# Global instance
enhanced_web_service_manager = EnhancedWebServiceManager()

# Convenience functions
def start_web_service():
    """Start web service"""
    return enhanced_web_service_manager.start_service()

def stop_web_service():
    """Stop web service"""
    return enhanced_web_service_manager.stop_service()

def restart_web_service():
    """Restart web service"""
    return enhanced_web_service_manager.restart_service()

def open_web_service_in_browser():
    """Open web service in browser"""
    return enhanced_web_service_manager.open_in_browser()

def get_web_service_status():
    """Get web service status"""
    return enhanced_web_service_manager.get_service_status()

def get_web_service_logs(lines: int = 50):
    """Get web service logs"""
    return enhanced_web_service_manager.get_recent_logs(lines)

if __name__ == "__main__":
    # Test the enhanced web service manager
    print("🌐 Testing Enhanced Web Service Manager...")
    
    manager = EnhancedWebServiceManager()
    
    # Test status
    status = manager.get_service_status()
    print(f"Current status: {status}")
    
    # Test start
    success, message = manager.start_service()
    print(f"Start result: {success} - {message}")
    
    if success:
        time.sleep(2)
        
        # Test browser open
        browser_success, browser_msg = manager.open_in_browser()
        print(f"Browser result: {browser_success} - {browser_msg}")
        
        time.sleep(2)
        
        # Test stop
        stop_success, stop_msg = manager.stop_service()
        print(f"Stop result: {stop_success} - {stop_msg}")