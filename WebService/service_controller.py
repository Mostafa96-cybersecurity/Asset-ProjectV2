#!/usr/bin/env python3
"""
WEB SERVICE CONTROLLER

This module provides Start/Stop/Restart controls for the web service
that will be integrated into the desktop application.
"""

import subprocess
import time
import socket
import os
import threading
import signal
import sys
from datetime import datetime

class WebServiceController:
    def __init__(self, service_port=5000):
        self.service_port = service_port
        self.service_process = None
        self.service_status = 'stopped'
        self.start_time = None
        self.service_url = f"http://localhost:{service_port}"
        self.log_file = "webservice.log"

    def is_port_available(self, port):
        """Check if port is available"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                return result != 0
        except Exception:
            return False

    def is_service_running(self):
        """Check if web service is running"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(2)
                result = sock.connect_ex(('localhost', self.service_port))
                return result == 0
        except Exception:
            return False

    def start_service(self):
        """Start the web service"""
        try:
            if self.is_service_running():
                return {
                    'success': False,
                    'message': f'Service is already running on port {self.service_port}',
                    'status': 'already_running'
                }

            if not self.is_port_available(self.service_port):
                return {
                    'success': False,
                    'message': f'Port {self.service_port} is in use by another application',
                    'status': 'port_busy'
                }

            # Start the web service process
            service_script = os.path.join(os.path.dirname(__file__), 'app.py')
            
            if os.name == 'nt':  # Windows
                # Use pythonw to run without console window
                self.service_process = subprocess.Popen([
                    sys.executable, service_script
                ], 
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
            else:  # Linux/Mac
                self.service_process = subprocess.Popen([
                    sys.executable, service_script
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid
                )

            # Wait a moment for service to start
            time.sleep(3)

            # Check if service started successfully
            if self.is_service_running():
                self.service_status = 'running'
                self.start_time = datetime.now()
                
                return {
                    'success': True,
                    'message': f'Web service started successfully on port {self.service_port}',
                    'status': 'running',
                    'url': self.service_url,
                    'pid': self.service_process.pid if self.service_process else None
                }
            else:
                # Service failed to start
                error_output = ""
                if self.service_process:
                    try:
                        _, stderr = self.service_process.communicate(timeout=2)
                        error_output = stderr.decode('utf-8')
                    except subprocess.TimeoutExpired:
                        pass

                return {
                    'success': False,
                    'message': f'Failed to start web service. Error: {error_output}',
                    'status': 'failed'
                }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error starting web service: {str(e)}',
                'status': 'error'
            }

    def stop_service(self):
        """Stop the web service"""
        try:
            if not self.is_service_running():
                return {
                    'success': True,
                    'message': 'Service is already stopped',
                    'status': 'already_stopped'
                }

            # Try to terminate the process gracefully
            if self.service_process:
                try:
                    if os.name == 'nt':  # Windows
                        # Send CTRL+BREAK signal
                        self.service_process.send_signal(signal.CTRL_BREAK_EVENT)
                    else:  # Linux/Mac
                        # Send SIGTERM
                        os.killpg(os.getpgid(self.service_process.pid), signal.SIGTERM)
                    
                    # Wait for process to terminate
                    self.service_process.wait(timeout=10)
                    
                except subprocess.TimeoutExpired:
                    # Force kill if graceful shutdown failed
                    if os.name == 'nt':
                        self.service_process.terminate()
                    else:
                        os.killpg(os.getpgid(self.service_process.pid), signal.SIGKILL)
                    
                    self.service_process.wait(timeout=5)

            # If process method didn't work, try to kill by port
            if self.is_service_running():
                self._kill_process_by_port(self.service_port)

            # Wait and verify service stopped
            time.sleep(2)
            
            if not self.is_service_running():
                self.service_status = 'stopped'
                self.service_process = None
                self.start_time = None
                
                return {
                    'success': True,
                    'message': 'Web service stopped successfully',
                    'status': 'stopped'
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to stop web service completely',
                    'status': 'stop_failed'
                }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error stopping web service: {str(e)}',
                'status': 'error'
            }

    def restart_service(self):
        """Restart the web service"""
        try:
            # Stop the service first
            stop_result = self.stop_service()
            
            if not stop_result['success'] and stop_result['status'] != 'already_stopped':
                return {
                    'success': False,
                    'message': f"Failed to stop service for restart: {stop_result['message']}",
                    'status': 'restart_failed'
                }

            # Wait a moment between stop and start
            time.sleep(2)

            # Start the service
            start_result = self.start_service()
            
            if start_result['success']:
                return {
                    'success': True,
                    'message': 'Web service restarted successfully',
                    'status': 'running',
                    'url': self.service_url
                }
            else:
                return {
                    'success': False,
                    'message': f"Failed to start service after stop: {start_result['message']}",
                    'status': 'restart_failed'
                }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error restarting web service: {str(e)}',
                'status': 'error'
            }

    def get_service_status(self):
        """Get current service status"""
        try:
            is_running = self.is_service_running()
            
            if is_running:
                uptime = str(datetime.now() - self.start_time) if self.start_time else "Unknown"
                
                return {
                    'status': 'running',
                    'is_running': True,
                    'port': self.service_port,
                    'url': self.service_url,
                    'uptime': uptime,
                    'start_time': self.start_time.isoformat() if self.start_time else None,
                    'pid': self.service_process.pid if self.service_process else None
                }
            else:
                return {
                    'status': 'stopped',
                    'is_running': False,
                    'port': self.service_port,
                    'url': self.service_url,
                    'uptime': None,
                    'start_time': None,
                    'pid': None
                }

        except Exception as e:
            return {
                'status': 'error',
                'is_running': False,
                'error': str(e)
            }

    def _kill_process_by_port(self, port):
        """Kill process using specific port (Windows/Linux compatible)"""
        try:
            if os.name == 'nt':  # Windows
                # Use netstat and taskkill
                result = subprocess.run([
                    'netstat', '-ano'
                ], capture_output=True, text=True)
                
                lines = result.stdout.split('\n')
                for line in lines:
                    if f':{port}' in line and 'LISTENING' in line:
                        parts = line.split()
                        if len(parts) >= 5:
                            pid = parts[-1]
                            subprocess.run(['taskkill', '/F', '/PID', pid], 
                                         capture_output=True)
                            break
            else:  # Linux/Mac
                # Use lsof and kill
                result = subprocess.run([
                    'lsof', '-t', f'-i:{port}'
                ], capture_output=True, text=True)
                
                if result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        subprocess.run(['kill', '-9', pid], capture_output=True)

        except Exception as e:
            print(f"Error killing process by port: {e}")

def create_service_control_gui():
    """Create a simple GUI control for the web service (for desktop integration)"""
    
    import tkinter as tk
    from tkinter import ttk, messagebox
    import webbrowser
    
    class ServiceControlGUI:
        def __init__(self, root):
            self.root = root
            self.controller = WebServiceController()
            self.setup_gui()
            self.update_status()

        def setup_gui(self):
            self.root.title("Asset Management Web Service Control")
            self.root.geometry("500x400")
            self.root.resizable(False, False)

            # Main frame
            main_frame = ttk.Frame(self.root, padding="20")
            main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

            # Title
            title_label = ttk.Label(main_frame, text="Web Service Control Panel", 
                                  font=('Arial', 16, 'bold'))
            title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

            # Status section
            status_frame = ttk.LabelFrame(main_frame, text="Service Status", padding="10")
            status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))

            ttk.Label(status_frame, text="Status:").grid(row=0, column=0, sticky=tk.W)
            self.status_label = ttk.Label(status_frame, text="Checking...", 
                                        foreground="orange")
            self.status_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))

            ttk.Label(status_frame, text="URL:").grid(row=1, column=0, sticky=tk.W)
            self.url_label = ttk.Label(status_frame, text="http://localhost:5000", 
                                     foreground="blue", cursor="hand2")
            self.url_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
            self.url_label.bind("<Button-1>", self.open_dashboard)

            ttk.Label(status_frame, text="Uptime:").grid(row=2, column=0, sticky=tk.W)
            self.uptime_label = ttk.Label(status_frame, text="N/A")
            self.uptime_label.grid(row=2, column=1, sticky=tk.W, padx=(10, 0))

            # Control buttons
            button_frame = ttk.Frame(main_frame)
            button_frame.grid(row=2, column=0, columnspan=2, pady=(0, 20))

            self.start_btn = ttk.Button(button_frame, text="Start Service", 
                                      command=self.start_service, width=15)
            self.start_btn.grid(row=0, column=0, padx=(0, 10))

            self.stop_btn = ttk.Button(button_frame, text="Stop Service", 
                                     command=self.stop_service, width=15)
            self.stop_btn.grid(row=0, column=1, padx=(0, 10))

            self.restart_btn = ttk.Button(button_frame, text="Restart Service", 
                                        command=self.restart_service, width=15)
            self.restart_btn.grid(row=0, column=2)

            # Dashboard button
            dashboard_btn = ttk.Button(main_frame, text="Open Dashboard", 
                                     command=self.open_dashboard, width=20)
            dashboard_btn.grid(row=3, column=0, columnspan=2, pady=(0, 10))

            # Refresh button
            refresh_btn = ttk.Button(main_frame, text="Refresh Status", 
                                   command=self.update_status, width=20)
            refresh_btn.grid(row=4, column=0, columnspan=2, pady=(0, 20))

            # Log area
            log_frame = ttk.LabelFrame(main_frame, text="Service Log", padding="10")
            log_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))

            self.log_text = tk.Text(log_frame, height=8, width=50)
            scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
            self.log_text.configure(yscrollcommand=scrollbar.set)
            
            self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        def update_status(self):
            status = self.controller.get_service_status()
            
            if status['is_running']:
                self.status_label.config(text="Running", foreground="green")
                self.uptime_label.config(text=status.get('uptime', 'N/A'))
                self.start_btn.config(state='disabled')
                self.stop_btn.config(state='normal')
                self.restart_btn.config(state='normal')
                self.log_message("[OK] Service is running")
            else:
                self.status_label.config(text="Stopped", foreground="red")
                self.uptime_label.config(text="N/A")
                self.start_btn.config(state='normal')
                self.stop_btn.config(state='disabled')
                self.restart_btn.config(state='disabled')
                self.log_message("[ERROR] Service is stopped")

        def start_service(self):
            self.log_message("[STARTING] Starting web service...")
            result = self.controller.start_service()
            
            if result['success']:
                messagebox.showinfo("Success", result['message'])
                self.log_message(f"✅ {result['message']}")
            else:
                messagebox.showerror("Error", result['message'])
                self.log_message(f"❌ {result['message']}")
            
            self.update_status()

        def stop_service(self):
            self.log_message("🛑 Stopping web service...")
            result = self.controller.stop_service()
            
            if result['success']:
                messagebox.showinfo("Success", result['message'])
                self.log_message(f"✅ {result['message']}")
            else:
                messagebox.showerror("Error", result['message'])
                self.log_message(f"❌ {result['message']}")
            
            self.update_status()

        def restart_service(self):
            self.log_message("[RESTARTING] Restarting web service...")
            result = self.controller.restart_service()
            
            if result['success']:
                messagebox.showinfo("Success", result['message'])
                self.log_message(f"✅ {result['message']}")
            else:
                messagebox.showerror("Error", result['message'])
                self.log_message(f"❌ {result['message']}")
            
            self.update_status()

        def open_dashboard(self, event=None):
            try:
                webbrowser.open("http://localhost:5000")
                self.log_message("[WEB] Opening dashboard in browser...")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open dashboard: {e}")

        def log_message(self, message):
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.log_text.see(tk.END)

    # Create and run GUI
    root = tk.Tk()
    app = ServiceControlGUI(root)
    root.mainloop()

def main():
    """Main function for standalone testing"""
    controller = WebServiceController()
    
    print("[WEB] Asset Management Web Service Controller")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Start Service")
        print("2. Stop Service") 
        print("3. Restart Service")
        print("4. Check Status")
        print("5. Open GUI Control")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            result = controller.start_service()
            print(f"Result: {result['message']}")
            
        elif choice == '2':
            result = controller.stop_service()
            print(f"Result: {result['message']}")
            
        elif choice == '3':
            result = controller.restart_service()
            print(f"Result: {result['message']}")
            
        elif choice == '4':
            status = controller.get_service_status()
            print(f"Status: {status}")
            
        elif choice == '5':
            create_service_control_gui()
            
        elif choice == '6':
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice. Please try again.")

if __name__ == '__main__':
    main()