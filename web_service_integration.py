#!/usr/bin/env python3
"""
DESKTOP INTEGRATION FOR WEB SERVICE

This module integrates web service controls into the main desktop application.
It provides buttons to Start/Stop/Restart the web service directly from the desktop app.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import threading
import time
from datetime import datetime
import sys
import os

# Add WebService directory to path to import service_controller
sys.path.append(os.path.join(os.path.dirname(__file__), 'WebService'))

try:
    from WebService.service_controller import WebServiceController
except ImportError:
    # Fallback import
    import importlib.util
    spec = importlib.util.spec_from_file_location("service_controller", "WebService/service_controller.py")
    service_controller = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(service_controller)
    WebServiceController = service_controller.WebServiceController

class WebServiceIntegration:
    """Web Service Integration for Desktop Application"""
    
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.controller = WebServiceController()
        self.status_update_thread = None
        self.running = True
        self.setup_web_service_panel()
        self.start_status_monitoring()

    def setup_web_service_panel(self):
        """Create web service control panel"""
        
        # Main web service frame
        self.web_service_frame = ttk.LabelFrame(self.parent_frame, text="🌐 Web Service Dashboard", padding="15")
        self.web_service_frame.pack(fill=tk.X, pady=(10, 0))

        # Status indicator row
        status_row = ttk.Frame(self.web_service_frame)
        status_row.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(status_row, text="Service Status:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        
        self.status_indicator = ttk.Label(status_row, text="●", foreground="red", font=('Arial', 14))
        self.status_indicator.pack(side=tk.LEFT, padx=(5, 0))
        
        self.status_text = ttk.Label(status_row, text="Stopped", foreground="red", font=('Arial', 10, 'bold'))
        self.status_text.pack(side=tk.LEFT, padx=(5, 0))

        self.uptime_label = ttk.Label(status_row, text="", foreground="gray")
        self.uptime_label.pack(side=tk.RIGHT)

        # Control buttons row
        button_row = ttk.Frame(self.web_service_frame)
        button_row.pack(fill=tk.X, pady=(0, 10))

        # Start button
        self.start_btn = ttk.Button(button_row, text="🚀 Start Service", 
                                   command=self.start_service_async, 
                                   style="Success.TButton", width=15)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 5))

        # Stop button  
        self.stop_btn = ttk.Button(button_row, text="🛑 Stop Service", 
                                  command=self.stop_service_async, 
                                  style="Danger.TButton", width=15)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 5))

        # Restart button
        self.restart_btn = ttk.Button(button_row, text="🔄 Restart", 
                                     command=self.restart_service_async, 
                                     style="Warning.TButton", width=15)
        self.restart_btn.pack(side=tk.LEFT, padx=(0, 5))

        # Dashboard button
        self.dashboard_btn = ttk.Button(button_row, text="📊 Open Dashboard", 
                                       command=self.open_dashboard, 
                                       style="Info.TButton", width=18)
        self.dashboard_btn.pack(side=tk.RIGHT)

        # Info row
        info_row = ttk.Frame(self.web_service_frame)
        info_row.pack(fill=tk.X)

        self.url_label = ttk.Label(info_row, text="Dashboard URL: http://localhost:5000", 
                                  foreground="blue", cursor="hand2", font=('Arial', 9))
        self.url_label.pack(side=tk.LEFT)
        self.url_label.bind("<Button-1>", lambda e: self.open_dashboard())

        self.port_label = ttk.Label(info_row, text="Port: 5000", foreground="gray", font=('Arial', 9))
        self.port_label.pack(side=tk.RIGHT)

        # Configure button styles
        self.configure_button_styles()

        # Initial status update
        self.update_service_status()

    def configure_button_styles(self):
        """Configure custom button styles"""
        style = ttk.Style()
        
        # Success style (green)
        style.configure("Success.TButton", foreground="green")
        
        # Danger style (red)  
        style.configure("Danger.TButton", foreground="red")
        
        # Warning style (orange)
        style.configure("Warning.TButton", foreground="orange")
        
        # Info style (blue)
        style.configure("Info.TButton", foreground="blue")

    def start_status_monitoring(self):
        """Start background thread to monitor service status"""
        def monitor():
            while self.running:
                try:
                    self.update_service_status()
                    time.sleep(5)  # Check every 5 seconds
                except Exception as e:
                    print(f"Status monitoring error: {e}")
                    time.sleep(10)  # Wait longer on error

        self.status_update_thread = threading.Thread(target=monitor, daemon=True)
        self.status_update_thread.start()

    def update_service_status(self):
        """Update service status display"""
        try:
            status = self.controller.get_service_status()
            
            if status.get('is_running', False):
                # Service is running
                self.status_indicator.config(foreground="green")
                self.status_text.config(text="Running", foreground="green")
                
                uptime = status.get('uptime', 'Unknown')
                if uptime != 'Unknown':
                    self.uptime_label.config(text=f"Uptime: {uptime}")
                else:
                    self.uptime_label.config(text="")
                
                # Update button states
                self.start_btn.config(state='disabled')
                self.stop_btn.config(state='normal')
                self.restart_btn.config(state='normal')
                self.dashboard_btn.config(state='normal')
                
            else:
                # Service is stopped
                self.status_indicator.config(foreground="red")
                self.status_text.config(text="Stopped", foreground="red")
                self.uptime_label.config(text="")
                
                # Update button states
                self.start_btn.config(state='normal')
                self.stop_btn.config(state='disabled')
                self.restart_btn.config(state='disabled')
                self.dashboard_btn.config(state='disabled')

        except Exception as e:
            # Error state
            self.status_indicator.config(foreground="orange")
            self.status_text.config(text="Error", foreground="orange")
            self.uptime_label.config(text=f"Error: {str(e)[:30]}")

    def start_service_async(self):
        """Start service in background thread"""
        def start_service():
            try:
                self.start_btn.config(text="⏳ Starting...", state='disabled')
                result = self.controller.start_service()
                
                if result['success']:
                    self.show_success_message("Web Service Started", result['message'])
                else:
                    self.show_error_message("Start Failed", result['message'])
                    
            except Exception as e:
                self.show_error_message("Start Error", f"Error starting service: {str(e)}")
            finally:
                self.start_btn.config(text="🚀 Start Service")
                self.update_service_status()

        threading.Thread(target=start_service, daemon=True).start()

    def stop_service_async(self):
        """Stop service in background thread"""
        def stop_service():
            try:
                self.stop_btn.config(text="⏳ Stopping...", state='disabled')
                result = self.controller.stop_service()
                
                if result['success']:
                    self.show_success_message("Web Service Stopped", result['message'])
                else:
                    self.show_error_message("Stop Failed", result['message'])
                    
            except Exception as e:
                self.show_error_message("Stop Error", f"Error stopping service: {str(e)}")
            finally:
                self.stop_btn.config(text="🛑 Stop Service")
                self.update_service_status()

        threading.Thread(target=stop_service, daemon=True).start()

    def restart_service_async(self):
        """Restart service in background thread"""
        def restart_service():
            try:
                self.restart_btn.config(text="⏳ Restarting...", state='disabled')
                result = self.controller.restart_service()
                
                if result['success']:
                    self.show_success_message("Web Service Restarted", result['message'])
                else:
                    self.show_error_message("Restart Failed", result['message'])
                    
            except Exception as e:
                self.show_error_message("Restart Error", f"Error restarting service: {str(e)}")
            finally:
                self.restart_btn.config(text="🔄 Restart")
                self.update_service_status()

        threading.Thread(target=restart_service, daemon=True).start()

    def open_dashboard(self):
        """Open dashboard in web browser"""
        try:
            webbrowser.open("http://localhost:5000")
            self.show_info_message("Dashboard Opening", "Opening Asset Management Dashboard in your web browser...")
        except Exception as e:
            self.show_error_message("Browser Error", f"Failed to open dashboard: {str(e)}")

    def show_success_message(self, title, message):
        """Show success message"""
        messagebox.showinfo(title, message)

    def show_error_message(self, title, message):
        """Show error message"""
        messagebox.showerror(title, message)

    def show_info_message(self, title, message):
        """Show info message"""
        messagebox.showinfo(title, message)

    def cleanup(self):
        """Cleanup when application closes"""
        self.running = False
        if self.status_update_thread and self.status_update_thread.is_alive():
            self.status_update_thread.join(timeout=1)

def integrate_web_service_to_desktop_app(parent_widget):
    """
    Function to integrate web service controls into an existing desktop application
    
    Args:
        parent_widget: The parent tkinter widget where web service controls should be added
        
    Returns:
        WebServiceIntegration: The integration object for further control
    """
    return WebServiceIntegration(parent_widget)

def create_standalone_web_service_gui():
    """Create standalone web service control GUI"""
    
    root = tk.Tk()
    root.title("Asset Management - Web Service Control")
    root.geometry("600x300")
    root.resizable(True, False)

    # Configure styles
    style = ttk.Style()
    style.theme_use('clam')

    # Main container
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Title
    title_label = ttk.Label(main_frame, text="Asset Management System", 
                           font=('Arial', 18, 'bold'))
    title_label.pack(pady=(0, 10))

    subtitle_label = ttk.Label(main_frame, text="Web Service Control Panel", 
                              font=('Arial', 12), foreground="gray")
    subtitle_label.pack(pady=(0, 20))

    # Integrate web service controls
    web_service_integration = integrate_web_service_to_desktop_app(main_frame)

    # Instructions
    instructions_frame = ttk.LabelFrame(main_frame, text="📖 Instructions", padding="10")
    instructions_frame.pack(fill=tk.X, pady=(20, 0))

    instructions_text = """
• Click 'Start Service' to launch the web dashboard
• Once started, click 'Open Dashboard' to view your assets in the browser  
• The dashboard shows all 242 devices with hardware data and hostname mismatches
• Use 'Stop Service' when you're done, or 'Restart' if you need to reload
• The service runs on http://localhost:5000
    """

    instructions_label = ttk.Label(instructions_frame, text=instructions_text, 
                                  font=('Arial', 9), justify=tk.LEFT)
    instructions_label.pack(anchor=tk.W)

    # Cleanup on close
    def on_closing():
        web_service_integration.cleanup()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")

    return root, web_service_integration

def main():
    """Main function to run standalone web service GUI"""
    root, integration = create_standalone_web_service_gui()
    root.mainloop()

if __name__ == '__main__':
    main()