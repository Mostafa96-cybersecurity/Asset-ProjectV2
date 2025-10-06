#!/usr/bin/env python3
"""
🚀 SIMPLE DESKTOP WEB SERVICE LAUNCHER - FIXED VERSION
=====================================================
Reliable launcher that actually works for GUI integration
"""

import subprocess
import sys
import os
import time
import requests
import threading
from pathlib import Path

class SimpleWebServiceLauncher:
    def __init__(self):
        self.process = None
        self.port = 8080
        self.service_url = f"http://localhost:{self.port}"
        self.python_path = self.get_python_path()
        self.is_running_flag = False
    
    def get_python_path(self):
        """Get the correct Python executable path"""
        venv_python = Path('.venv/Scripts/python.exe')
        if venv_python.exists():
            return str(venv_python.absolute())
        return sys.executable or 'python'
    
    def start_service_background(self):
        """Start the web service in background thread"""
        try:
            service_file = 'fixed_dashboard.py'
            
            if not os.path.exists(service_file):
                print(f"❌ Service file not found: {service_file}")
                return False
            
            print(f"🚀 Starting web service: {service_file}")
            
            # Start the service with minimal output redirection
            self.process = subprocess.Popen(
                [self.python_path, service_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd(),
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            # Wait for service to become available
            max_attempts = 20
            for attempt in range(max_attempts):
                if self.process.poll() is not None:
                    # Process died
                    stdout, stderr = self.process.communicate()
                    print(f"❌ Service process died. Error: {stderr[:200]}")
                    return False
                
                try:
                    # Check if service is responding
                    response = requests.get(self.service_url, timeout=3)
                    if response.status_code == 200:
                        print(f"✅ Web service started successfully!")
                        print(f"🌐 URL: {self.service_url}")
                        print(f"🔐 Login: admin / admin123")
                        self.is_running_flag = True
                        return True
                except requests.exceptions.RequestException:
                    pass
                
                time.sleep(0.5)
                if attempt % 4 == 0:
                    print(f"   Waiting... ({attempt + 1}/{max_attempts})")
            
            # Timeout reached
            print("⚠️ Service started but not responding to requests")
            if self.process and self.process.poll() is None:
                return True  # Process is running, might just be slow
            else:
                return False
                
        except Exception as e:
            print(f"❌ Error starting service: {e}")
            return False
    
    def start_service(self):
        """Start the web service (main method)"""
        if self.is_running():
            print("✅ Web service is already running!")
            return True, f"Service already running on {self.service_url}"
        
        success = self.start_service_background()
        if success:
            return True, f"Service started on {self.service_url}"
        else:
            return False, "Failed to start web service"
    
    def stop_service(self):
        """Stop the web service"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
                print("🛑 Web service stopped")
                self.is_running_flag = False
                return True
            except subprocess.TimeoutExpired:
                self.process.kill()
                print("🔥 Web service force killed")
                self.is_running_flag = False
                return True
            except Exception as e:
                print(f"❌ Error stopping service: {e}")
                return False
        return True
    
    def is_running(self):
        """Check if service is running"""
        try:
            response = requests.get(self.service_url, timeout=3)
            return response.status_code == 200
        except:
            return False
    
    def open_browser(self):
        """Open the web service in browser"""
        import webbrowser
        try:
            webbrowser.open(self.service_url)
            print(f"🌐 Opened {self.service_url} in browser")
            return True
        except Exception as e:
            print(f"❌ Error opening browser: {e}")
            return False

# Global instance for GUI integration
simple_launcher = SimpleWebServiceLauncher()

def start_web_service_for_gui():
    """Start web service for GUI integration - SIMPLIFIED VERSION"""
    return simple_launcher.start_service()

def stop_web_service_for_gui():
    """Stop web service for GUI integration"""
    return simple_launcher.stop_service()

def open_web_service_for_gui():
    """Open web service for GUI integration"""
    return simple_launcher.open_browser()

def get_web_service_status():
    """Get web service status for GUI"""
    return simple_launcher.is_running()

def get_web_service_url():
    """Get web service URL for GUI"""
    return simple_launcher.service_url

if __name__ == '__main__':
    launcher = SimpleWebServiceLauncher()
    
    print("🎯 SIMPLE DESKTOP WEB SERVICE LAUNCHER")
    print("=" * 40)
    
    success, message = launcher.start_service()
    if success:
        print(f"✅ {message}")
        
        # Keep running
        try:
            print("\n⌨️ Press Ctrl+C to stop the service")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n⏹️ Stopping service...")
            launcher.stop_service()
    else:
        print(f"❌ {message}")
        sys.exit(1)