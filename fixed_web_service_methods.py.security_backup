#!/usr/bin/env python3
"""
Fixed Web Service Methods
========================
Contains the corrected web service startup methods for the GUI application.
"""

# Required imports
from PyQt6.QtCore import QTime, QTimer
import subprocess
import os
import sys

class WebServiceMethods:
    """Fixed web service methods that can be integrated into the main GUI class"""
    
    def start_web_service(self):
        """🚀 Start the web service - FIXED VERSION"""
        try:
            self.web_service_log.append(f"🚀 Starting web service at {QTime.currentTime().toString()}")
            
            # Update status
            self.web_service_status.setText("🟡 Starting...")
            self.web_service_status.setStyleSheet("color: orange; font-weight: bold; padding: 5px;")
            
            # Try the desktop launcher first (fastest method)
            try:
                from desktop_web_service_launcher import FastWebServiceLauncher
                
                launcher = FastWebServiceLauncher()
                success, message = launcher.start_service()
                
                if success:
                    self.web_service_log.append("✅ Web service started successfully!")
                    self.web_service_status.setText("🟢 Running")
                    self.web_service_status.setStyleSheet("color: green; font-weight: bold; padding: 5px;")
                    self.web_service_log.append("🌐 Access URL: http://localhost:8080")
                    self.web_service_log.append("🔐 Login: admin/admin123 or user/user123")
                    
                    # Auto-open browser after service is ready
                    QTimer.singleShot(3000, self.open_web_service)
                    return
                else:
                    self.web_service_log.append(f"❌ Launcher failed: {message}")
                    
            except Exception as e:
                self.web_service_log.append(f"⚠️ Launcher not available: {e}")
            
            # Fallback to direct service start
            self._start_web_service_direct()
            
        except Exception as e:
            self.web_service_log.append(f"❌ Error starting web service: {str(e)}")
            self.web_service_status.setText("🔴 Error")
            self.web_service_status.setStyleSheet("color: red; font-weight: bold; padding: 5px;")
    
    def _start_web_service_direct(self):
        """Direct service startup using fixed dashboard"""
        try:
            self.web_service_log.append("🔄 Starting FIXED DASHBOARD directly...")
            
            # Use fixed_dashboard.py
            service_script = 'fixed_dashboard.py'
            
            if not os.path.exists(service_script):
                self.web_service_log.append("❌ Fixed dashboard not found!")
                self.web_service_status.setText("🔴 Error")
                self.web_service_status.setStyleSheet("color: red; font-weight: bold; padding: 5px;")
                return
            
            # Get correct Python executable
            python_exe = sys.executable
            venv_python = os.path.join('.venv', 'Scripts', 'python.exe')
            if os.path.exists(venv_python):
                python_exe = os.path.abspath(venv_python)
            
            # Start the service
            self.web_service_process = subprocess.Popen(
                [python_exe, service_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=os.getcwd(),
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            self.web_service_log.append(f"🚀 Fixed dashboard started (PID: {self.web_service_process.pid})")
            self.web_service_log.append("🌐 Access at: http://localhost:8080")
            self.web_service_log.append("✨ Features: Gradient UI, Login system, 222 assets")
            
            # Update status
            self.web_service_status.setText("🟢 Running")
            self.web_service_status.setStyleSheet("color: green; font-weight: bold; padding: 5px;")
            
            # Auto-open browser and check status
            QTimer.singleShot(5000, self.open_web_service)
            QTimer.singleShot(6000, self.check_web_service_status)
            
        except Exception as e:
            self.web_service_log.append(f"❌ Direct startup failed: {str(e)}")
            self.web_service_status.setText("🔴 Error")
            self.web_service_status.setStyleSheet("color: red; font-weight: bold; padding: 5px;")

    def stop_web_service(self):
        """🛑 Stop the web service - FIXED VERSION"""
        try:
            self.web_service_log.append("🛑 Stopping web service...")
            self.web_service_status.setText("🟡 Stopping...")
            self.web_service_status.setStyleSheet("color: orange; font-weight: bold; padding: 5px;")
            
            # Try stopping via launcher first
            try:
                from desktop_web_service_launcher import FastWebServiceLauncher
                launcher = FastWebServiceLauncher()
                launcher.stop_service()
                self.web_service_log.append("✅ Service stopped via launcher")
            except Exception as e:
                self.web_service_log.append(f"⚠️ Launcher stop failed: {e}")
            
            # Kill process if exists
            if hasattr(self, 'web_service_process') and self.web_service_process:
                try:
                    self.web_service_process.terminate()
                    self.web_service_process.wait(timeout=5)
                    self.web_service_log.append("✅ Process terminated")
                except Exception as e:
                    self.web_service_log.append(f"⚠️ Process termination failed: {e}")
            
            # Update status
            self.web_service_status.setText("🔴 Stopped")
            self.web_service_status.setStyleSheet("color: red; font-weight: bold; padding: 5px;")
            self.web_service_log.append("✅ Web service stopped")
            
        except Exception as e:
            self.web_service_log.append(f"❌ Error stopping web service: {str(e)}")

    def restart_web_service(self):
        """🔄 Restart the web service"""
        self.web_service_log.append("🔄 Restarting web service...")
        self.stop_web_service()
        
        # Wait a moment before restarting
        QTimer.singleShot(2000, self.start_web_service)

    def open_web_service(self):
        """🌐 Open the web service in browser"""
        try:
            import webbrowser
            
            # Try to get the correct URL from launcher
            try:
                from desktop_web_service_launcher import FastWebServiceLauncher
                launcher = FastWebServiceLauncher()
                url = launcher.service_url
            except:
                url = "http://localhost:8080"
            
            webbrowser.open(url)
            self.web_service_log.append(f"🌐 Opened {url} in browser")
            
        except Exception as e:
            self.web_service_log.append(f"❌ Error opening browser: {str(e)}")

    def check_web_service_status(self):
        """📊 Check web service status"""
        try:
            # Try to check via launcher
            try:
                from desktop_web_service_launcher import FastWebServiceLauncher
                launcher = FastWebServiceLauncher()
                is_running = launcher.is_running()
                
                if is_running:
                    self.web_service_status.setText("🟢 Running (Verified)")
                    self.web_service_status.setStyleSheet("color: green; font-weight: bold; padding: 5px;")
                    self.web_service_log.append("✅ Service status verified: Running")
                else:
                    self.web_service_status.setText("🔴 Not Responding")
                    self.web_service_status.setStyleSheet("color: red; font-weight: bold; padding: 5px;")
                    self.web_service_log.append("⚠️ Service status: Not responding")
                    
            except Exception as e:
                self.web_service_log.append(f"⚠️ Status check failed: {e}")
                
        except Exception as e:
            self.web_service_log.append(f"❌ Error checking status: {str(e)}")


# Helper function to integrate these methods into an existing class
def integrate_web_service_methods(gui_class):
    """
    Integrate the fixed web service methods into the main GUI class.
    
    Usage:
        from fixed_web_service_methods import integrate_web_service_methods
        integrate_web_service_methods(MainWindow)
    """
    for method_name in dir(WebServiceMethods):
        if not method_name.startswith('_') or method_name.startswith('_start'):
            method = getattr(WebServiceMethods, method_name)
            if callable(method):
                setattr(gui_class, method_name, method)


if __name__ == "__main__":
    print("Fixed Web Service Methods Module")
    print("================================")
    print("This module provides corrected web service methods for GUI integration.")
    print("Import and use integrate_web_service_methods() to add to your GUI class.")