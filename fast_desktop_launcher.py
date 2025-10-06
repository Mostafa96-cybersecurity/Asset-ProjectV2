#!/usr/bin/env python3
"""
⚡ FAST DESKTOP WEB SERVICE LAUNCHER
==================================
Super fast launcher that works immediately
"""

import ipaddress  # For IP validation
import subprocess
import sys
import os
import time
import requests
from pathlib import Path

class FastWebServiceLauncher:
    def __init__(self):
        self.process = None
        self.port = 8080
        self.service_url = f"http://localhost:{self.port}"
        self.python_path = self.get_python_path()
    
    def get_python_path(self):
        """Get the correct Python executable path"""
        venv_python = Path('.venv/Scripts/python.exe')
        if venv_python.exists():
            return str(venv_python.absolute())
        return sys.executable or 'python'
    
    def start_service(self):
        """Start the web service - FAST VERSION"""
        try:
            service_file = 'fixed_dashboard.py'
            
            if not os.path.exists(service_file):
                return False, "Service file not found"
            
            print(f"🚀 Starting web service: {service_file}")
            
            # Start the service with no window
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            self.process = subprocess.Popen(
                [self.python_path, service_file],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=os.getcwd(),
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # Quick test - only wait 3 seconds total
            print("⚡ Quick startup test...")
            for attempt in range(6):  # Only 6 attempts = 3 seconds
                if self.process.poll() is not None:
                    return False, "Service process died"
                
                try:
                    response = requests.get(self.service_url, timeout=1)
                    if response.status_code == 200:
                        print(f"✅ Web service started on {self.service_url}")
                        return True, f"Service started on {self.service_url}"
                except:
                    pass
                
                time.sleep(0.5)
            
            # If still not responding, assume it's starting
            if self.process.poll() is None:
                print("⚠️ Service starting in background...")
                return True, f"Service starting on {self.service_url}"
            else:
                return False, "Service failed to start"
                
        except Exception as e:
            return False, f"Error: {e}"
    
    def stop_service(self):
        """Stop the web service"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=2)
                return True
            except:
                try:
                    self.process.kill()
                except:
                    pass
                return True
        return True
    
    def is_running(self):
        """Check if service is running"""
        try:
            response = requests.get(self.service_url, timeout=1)
            return response.status_code == 200
        except:
            return False

# Global instance for GUI integration
fast_launcher = FastWebServiceLauncher()

def start_web_service_for_gui():
    """Start web service for GUI integration - FAST VERSION"""
    return fast_launcher.start_service()

def stop_web_service_for_gui():
    """Stop web service for GUI integration"""
    return fast_launcher.stop_service()

def get_web_service_status():
    """Get web service status for GUI"""
    return fast_launcher.is_running()

def get_web_service_url():
    """Get web service URL for GUI"""
    return fast_launcher.service_url

if __name__ == '__main__':
    launcher = FastWebServiceLauncher()
    success, message = launcher.start_service()
    if success:
        print(f"✅ {message}")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            launcher.stop_service()
    else:
        print(f"❌ {message}")