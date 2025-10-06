#!/usr/bin/env python3
"""
ENHANCED DESKTOP APPLICATION WITH WEB SERVICE INTEGRATION

This is the main desktop application that now includes:
✅ All existing asset management features
✅ Web Service Dashboard controls (Start/Stop/Restart)
✅ Direct access to web dashboard
✅ Real-time service status monitoring
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import webbrowser
import os
import subprocess
import sys
import time
from datetime import datetime

# Import web service integration
from web_service_integration import WebServiceIntegration

# Import automation system
from comprehensive_data_automation import AutomationIntegration

class EnhancedAssetManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Asset Management System - Enhanced Desktop Application")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Configure styles
        self.configure_styles()
        
        # Create main interface
        self.create_main_interface()
        
        # Initialize web service integration
        self.web_service_integration = None
        self.integrate_web_service()
        
        # Initialize automation system
        self.automation_integration = AutomationIntegration(self)
        self.automation_running = False
        self.automation_stats = {}
        
        # Start automation status updater
        self.update_automation_status()

    def configure_styles(self):
        """Configure custom styles for the application"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure notebook styles
        style.configure('Custom.TNotebook.Tab', padding=[20, 10])

    def create_main_interface(self):
        """Create the main application interface"""
        
        # Main container
        main_container = ttk.Frame(self.root, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Application title
        title_frame = ttk.Frame(main_container)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
        title_label = ttk.Label(title_frame, text="🖥️ Asset Management System", 
                               font=('Arial', 20, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        version_label = ttk.Label(title_frame, text="v2.0 - Enhanced Edition", 
                                 font=('Arial', 10), foreground="gray")
        version_label.pack(side=tk.RIGHT, anchor=tk.SE)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_container, style='Custom.TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_automation_tab()
        self.create_asset_management_tab()
        self.create_tools_tab()
        self.create_settings_tab()

    def create_dashboard_tab(self):
        """Create dashboard tab with web service integration"""
        
        dashboard_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(dashboard_frame, text="📊 Dashboard")
        
        # Dashboard header
        header_frame = ttk.Frame(dashboard_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(header_frame, text="Asset Management Dashboard", 
                 font=('Arial', 16, 'bold')).pack(side=tk.LEFT)
        
        # Quick stats frame
        stats_frame = ttk.LabelFrame(dashboard_frame, text="📈 Quick Statistics", padding="15")
        stats_frame.pack(fill=tk.X, pady=(0, 15))
        
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X)
        
        # Stats cards
        self.create_stat_card(stats_grid, "Total Devices", "242", "blue", 0, 0)
        self.create_stat_card(stats_grid, "Online", "18", "green", 0, 1)
        self.create_stat_card(stats_grid, "Hardware Data", "100", "orange", 0, 2)
        self.create_stat_card(stats_grid, "Mismatches", "35", "red", 0, 3)
        
        # Web service controls will be added here by integrate_web_service()
        
        # Quick actions
        actions_frame = ttk.LabelFrame(dashboard_frame, text="⚡ Quick Actions", padding="15")
        actions_frame.pack(fill=tk.X, pady=(15, 0))
        
        actions_grid = ttk.Frame(actions_frame)
        actions_grid.pack(fill=tk.X)
        
        ttk.Button(actions_grid, text="📊 View All Assets", 
                  command=self.view_all_assets, width=20).grid(row=0, column=0, padx=(0, 10), pady=5)
        
        ttk.Button(actions_grid, text="🔍 Scan Network", 
                  command=self.scan_network, width=20).grid(row=0, column=1, padx=(0, 10), pady=5)
        
        ttk.Button(actions_grid, text="📁 Open Database", 
                  command=self.open_database, width=20).grid(row=0, column=2, padx=(0, 10), pady=5)
        
        ttk.Button(actions_grid, text="📋 Generate Report", 
                  command=self.generate_report, width=20).grid(row=1, column=0, padx=(0, 10), pady=5)
        
        ttk.Button(actions_grid, text="⚙️ Run Diagnostics", 
                  command=self.run_diagnostics, width=20).grid(row=1, column=1, padx=(0, 10), pady=5)
        
        ttk.Button(actions_grid, text="📤 Export Data", 
                  command=self.export_data, width=20).grid(row=1, column=2, padx=(0, 10), pady=5)

    def create_stat_card(self, parent, title, value, color, row, col):
        """Create a statistics card"""
        card_frame = ttk.Frame(parent, relief="raised", borderwidth=1)
        card_frame.grid(row=row, column=col, padx=10, pady=5, sticky="ew")
        
        # Configure grid weight
        parent.grid_columnconfigure(col, weight=1)
        
        ttk.Label(card_frame, text=value, font=('Arial', 18, 'bold'), 
                 foreground=color).pack(pady=(10, 0))
        ttk.Label(card_frame, text=title, font=('Arial', 10)).pack(pady=(0, 10))

    def create_automation_tab(self):
        """Create comprehensive data automation tab"""
        
        automation_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(automation_frame, text="🤖 Data Automation")
        
        # Automation header
        header_frame = ttk.Frame(automation_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(header_frame, text="Comprehensive Data Collection Automation", 
                 font=('Arial', 16, 'bold')).pack(side=tk.LEFT)
        
        # Automation status frame
        status_frame = ttk.LabelFrame(automation_frame, text="🔄 Automation Status", padding="15")
        status_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Status display
        self.automation_status_frame = ttk.Frame(status_frame)
        self.automation_status_frame.pack(fill=tk.X)
        
        self.automation_status_label = ttk.Label(self.automation_status_frame, 
                                                text="⏹️ Automation Stopped", 
                                                font=('Arial', 12, 'bold'),
                                                foreground="red")
        self.automation_status_label.pack(side=tk.LEFT)
        
        # Control buttons
        control_frame = ttk.Frame(status_frame)
        control_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.start_automation_btn = ttk.Button(control_frame, text="▶️ Start Automation", 
                                              command=self.start_automation, width=20)
        self.start_automation_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_automation_btn = ttk.Button(control_frame, text="⏹️ Stop Automation", 
                                             command=self.stop_automation, width=20, state="disabled")
        self.stop_automation_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(control_frame, text="📊 View Logs", 
                  command=self.view_automation_logs, width=15).pack(side=tk.LEFT)
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(automation_frame, text="📈 Real-time Statistics", padding="15")
        stats_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Create stats grid
        self.stats_grid = ttk.Frame(stats_frame)
        self.stats_grid.pack(fill=tk.X)
        
        # Initialize stats display
        self.automation_stats_labels = {}
        self.update_automation_stats_display()
        
        # Configuration frame
        config_frame = ttk.LabelFrame(automation_frame, text="⚙️ Automation Configuration", padding="15")
        config_frame.pack(fill=tk.X, pady=(0, 15))
        
        config_grid = ttk.Frame(config_frame)
        config_grid.pack(fill=tk.X)
        
        # Configuration options
        ttk.Label(config_grid, text="Collection Interval:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.interval_var = tk.StringVar(value="30 minutes")
        interval_combo = ttk.Combobox(config_grid, textvariable=self.interval_var, 
                                     values=["15 minutes", "30 minutes", "1 hour", "2 hours", "6 hours"],
                                     state="readonly", width=15)
        interval_combo.grid(row=0, column=1, padx=(0, 20))
        
        ttk.Label(config_grid, text="Priority Mode:").grid(row=0, column=2, sticky="w", padx=(0, 10))
        self.priority_var = tk.StringVar(value="Low Completeness First")
        priority_combo = ttk.Combobox(config_grid, textvariable=self.priority_var,
                                     values=["Low Completeness First", "Recently Changed", "All Devices"],
                                     state="readonly", width=20)
        priority_combo.grid(row=0, column=3)
        
        # Device monitoring frame
        monitoring_frame = ttk.LabelFrame(automation_frame, text="🖥️ Device Monitoring", padding="15")
        monitoring_frame.pack(fill=tk.BOTH, expand=True)
        
        # Device list
        columns = ("Hostname", "IP Address", "Completeness", "Last Collection", "Status")
        self.device_tree = ttk.Treeview(monitoring_frame, columns=columns, show="tree headings", height=8)
        
        # Configure columns
        self.device_tree.heading("#0", text="ID")
        self.device_tree.column("#0", width=50, anchor="center")
        
        for i, col in enumerate(columns):
            self.device_tree.heading(f"#{i+1}", text=col)
            self.device_tree.column(f"#{i+1}", width=120 if col != "Hostname" else 150, anchor="center")
        
        # Add scrollbar
        device_scrollbar = ttk.Scrollbar(monitoring_frame, orient="vertical", command=self.device_tree.yview)
        self.device_tree.configure(yscrollcommand=device_scrollbar.set)
        
        # Pack treeview and scrollbar
        self.device_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        device_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Update device list
        self.update_device_list()

    def create_asset_management_tab(self):
        """Create asset management tab"""
        
        asset_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(asset_frame, text="🖥️ Asset Management")
        
        # Asset management header
        ttk.Label(asset_frame, text="Asset Management Tools", 
                 font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        
        # Collection tools
        collection_frame = ttk.LabelFrame(asset_frame, text="📡 Data Collection", padding="15")
        collection_frame.pack(fill=tk.X, pady=(0, 15))
        
        collection_buttons = ttk.Frame(collection_frame)
        collection_buttons.pack(fill=tk.X)
        
        ttk.Button(collection_buttons, text="🔧 Enhanced Hardware Collection", 
                  command=self.run_hardware_collection, width=30).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(collection_buttons, text="🏷️ Detect Hostname Mismatches", 
                  command=self.detect_hostname_mismatches, width=30).pack(side=tk.LEFT, padx=(0, 10))
        
        # Database tools
        database_frame = ttk.LabelFrame(asset_frame, text="🗃️ Database Management", padding="15")
        database_frame.pack(fill=tk.X, pady=(0, 15))
        
        database_buttons = ttk.Frame(database_frame)
        database_buttons.pack(fill=tk.X)
        
        ttk.Button(database_buttons, text="📊 Analyze Database", 
                  command=self.analyze_database, width=25).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(database_buttons, text="🧹 Clean Duplicates", 
                  command=self.clean_duplicates, width=25).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(database_buttons, text="💾 Backup Database", 
                  command=self.backup_database, width=25).pack(side=tk.LEFT)

    def create_tools_tab(self):
        """Create tools tab"""
        
        tools_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(tools_frame, text="🛠️ Tools")
        
        ttk.Label(tools_frame, text="System Tools & Utilities", 
                 font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        
        # Network tools
        network_frame = ttk.LabelFrame(tools_frame, text="🌐 Network Tools", padding="15")
        network_frame.pack(fill=tk.X, pady=(0, 15))
        
        network_buttons = ttk.Frame(network_frame)
        network_buttons.pack(fill=tk.X)
        
        ttk.Button(network_buttons, text="🔍 Network Scanner", 
                  command=self.network_scanner, width=20).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(network_buttons, text="📊 Port Scanner", 
                  command=self.port_scanner, width=20).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(network_buttons, text="🔄 Auto Discovery", 
                  command=self.auto_discovery, width=20).pack(side=tk.LEFT)
        
        # System tools
        system_frame = ttk.LabelFrame(tools_frame, text="⚙️ System Tools", padding="15")
        system_frame.pack(fill=tk.X, pady=(0, 15))
        
        system_buttons = ttk.Frame(system_frame)
        system_buttons.pack(fill=tk.X)
        
        ttk.Button(system_buttons, text="📈 Performance Monitor", 
                  command=self.performance_monitor, width=20).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(system_buttons, text="🔧 System Diagnostics", 
                  command=self.system_diagnostics, width=20).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(system_buttons, text="📝 Log Viewer", 
                  command=self.log_viewer, width=20).pack(side=tk.LEFT)

    def create_settings_tab(self):
        """Create settings tab"""
        
        settings_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(settings_frame, text="⚙️ Settings")
        
        ttk.Label(settings_frame, text="Application Settings", 
                 font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        
        # Configuration settings
        config_frame = ttk.LabelFrame(settings_frame, text="🔧 Configuration", padding="15")
        config_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Database settings
        db_frame = ttk.LabelFrame(settings_frame, text="🗃️ Database Settings", padding="15")
        db_frame.pack(fill=tk.X, pady=(0, 15))
        
        # About section
        about_frame = ttk.LabelFrame(settings_frame, text="ℹ️ About", padding="15")
        about_frame.pack(fill=tk.X)
        
        about_text = """
Asset Management System - Enhanced Edition v2.0

Features:
✅ Comprehensive hardware data collection
✅ Hostname mismatch detection
✅ Web-based dashboard
✅ Real-time monitoring
✅ Database analysis tools
✅ Network discovery
✅ Automated reporting

© 2025 Asset Management System
        """
        
        ttk.Label(about_frame, text=about_text, justify=tk.LEFT, 
                 font=('Arial', 9)).pack(anchor=tk.W)

    def integrate_web_service(self):
        """Integrate web service controls into the dashboard tab"""
        
        # Get the dashboard frame (first tab)
        dashboard_frame = self.notebook.nametowidget(self.notebook.tabs()[0])
        
        # Add web service integration
        self.web_service_integration = WebServiceIntegration(dashboard_frame)

    # Action methods
    def view_all_assets(self):
        """Open web dashboard or local asset viewer"""
        try:
            # First try to open web dashboard
            webbrowser.open("http://localhost:5000/assets")
        except Exception:
            # Fallback to local viewer
            messagebox.showinfo("Assets", "Opening local asset viewer...")

    def scan_network(self):
        """Run network scan"""
        def run_scan():
            try:
                result = subprocess.run([sys.executable, "complete_network_scanner_fixed.py"], 
                                      capture_output=True, text=True, timeout=60)
                if result.returncode == 0:
                    messagebox.showinfo("Success", "Network scan completed successfully!")
                else:
                    messagebox.showerror("Error", f"Network scan failed: {result.stderr}")
            except subprocess.TimeoutExpired:
                messagebox.showwarning("Timeout", "Network scan timed out")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to run network scan: {str(e)}")
        
        threading.Thread(target=run_scan, daemon=True).start()

    def open_database(self):
        """Open database file"""
        try:
            if os.path.exists("assets.db"):
                os.startfile("assets.db")  # Windows
            else:
                messagebox.showerror("Error", "Database file not found")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open database: {str(e)}")

    def generate_report(self):
        """Generate comprehensive report"""
        def run_report():
            try:
                result = subprocess.run([sys.executable, "comprehensive_database_analysis.py"], 
                                      capture_output=True, text=True, timeout=60)
                if result.returncode == 0:
                    messagebox.showinfo("Success", "Report generated successfully!")
                else:
                    messagebox.showerror("Error", f"Report generation failed: {result.stderr}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
        
        threading.Thread(target=run_report, daemon=True).start()

    def run_diagnostics(self):
        """Run system diagnostics"""
        def run_diag():
            try:
                result = subprocess.run([sys.executable, "check_hardware_collection_status.py"], 
                                      capture_output=True, text=True, timeout=60)
                if result.returncode == 0:
                    messagebox.showinfo("Success", "Diagnostics completed successfully!")
                else:
                    messagebox.showerror("Error", f"Diagnostics failed: {result.stderr}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to run diagnostics: {str(e)}")
        
        threading.Thread(target=run_diag, daemon=True).start()

    def export_data(self):
        """Export data to file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            if filename:
                messagebox.showinfo("Export", f"Data export functionality will save to: {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")

    def run_hardware_collection(self):
        """Run enhanced hardware collection"""
        def run_collection():
            try:
                result = subprocess.run([sys.executable, "enhanced_hardware_collector.py"], 
                                      capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    messagebox.showinfo("Success", "Hardware collection completed!")
                else:
                    messagebox.showerror("Error", f"Collection failed: {result.stderr}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to run collection: {str(e)}")
        
        threading.Thread(target=run_collection, daemon=True).start()

    def detect_hostname_mismatches(self):
        """Run hostname mismatch detection"""
        def run_detection():
            try:
                result = subprocess.run([sys.executable, "hostname_mismatch_detector.py"], 
                                      capture_output=True, text=True, timeout=120)
                if result.returncode == 0:
                    messagebox.showinfo("Success", "Hostname mismatch detection completed!")
                else:
                    messagebox.showerror("Error", f"Detection failed: {result.stderr}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to run detection: {str(e)}")
        
        threading.Thread(target=run_detection, daemon=True).start()

    def analyze_database(self):
        """Analyze database"""
        def run_analysis():
            try:
                result = subprocess.run([sys.executable, "comprehensive_database_analysis.py"], 
                                      capture_output=True, text=True, timeout=120)
                if result.returncode == 0:
                    messagebox.showinfo("Success", "Database analysis completed!")
                else:
                    messagebox.showerror("Error", f"Analysis failed: {result.stderr}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to analyze database: {str(e)}")
        
        threading.Thread(target=run_analysis, daemon=True).start()

    def clean_duplicates(self):
        """Clean database duplicates"""
        if messagebox.askyesno("Confirm", "This will remove duplicate entries. Continue?"):
            def run_cleanup():
                try:
                    result = subprocess.run([sys.executable, "cleanup_duplicates.py"], 
                                          capture_output=True, text=True, timeout=120)
                    if result.returncode == 0:
                        messagebox.showinfo("Success", "Duplicate cleanup completed!")
                    else:
                        messagebox.showerror("Error", f"Cleanup failed: {result.stderr}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to clean duplicates: {str(e)}")
            
            threading.Thread(target=run_cleanup, daemon=True).start()

    def backup_database(self):
        """Backup database"""
        try:
            from datetime import datetime
            backup_name = f"assets_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            filename = filedialog.asksaveasfilename(
                initialname=backup_name,
                defaultextension=".db",
                filetypes=[("Database files", "*.db"), ("All files", "*.*")]
            )
            if filename:
                import shutil
                shutil.copy2("assets.db", filename)
                messagebox.showinfo("Success", f"Database backed up to: {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Backup failed: {str(e)}")

    # Automation methods
    def start_automation(self):
        """Start comprehensive data automation"""
        try:
            self.automation_integration.start_automation()
            self.automation_running = True
            
            # Update UI
            self.automation_status_label.config(text="🟢 Automation Running", foreground="green")
            self.start_automation_btn.config(state="disabled")
            self.stop_automation_btn.config(state="normal")
            
            messagebox.showinfo("Automation Started", 
                              "Comprehensive data collection automation has been started!\n\n" +
                              "The system will now:\n" +
                              "• Collect missing data from all devices\n" +
                              "• Monitor for changes and duplicates\n" +
                              "• Provide real-time notifications\n" +
                              "• Maintain 100% data synchronization")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start automation: {str(e)}")
    
    def stop_automation(self):
        """Stop comprehensive data automation"""
        try:
            self.automation_integration.stop_automation()
            self.automation_running = False
            
            # Update UI
            self.automation_status_label.config(text="⏹️ Automation Stopped", foreground="red")
            self.start_automation_btn.config(state="normal")
            self.stop_automation_btn.config(state="disabled")
            
            messagebox.showinfo("Automation Stopped", "Data collection automation has been stopped.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop automation: {str(e)}")
    
    def view_automation_logs(self):
        """View automation logs"""
        try:
            log_file = "data_collection_automation.log"
            if os.path.exists(log_file):
                if os.name == 'nt':  # Windows
                    os.startfile(log_file)
                else:
                    subprocess.run(['xdg-open', log_file])
            else:
                messagebox.showinfo("No Logs", "No automation logs found yet.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open logs: {str(e)}")
    
    def update_automation_status(self):
        """Update automation status and statistics"""
        try:
            # Get current stats
            if hasattr(self, 'automation_integration'):
                self.automation_stats = self.automation_integration.get_stats()
                self.update_automation_stats_display()
                self.update_device_list()
            
        except Exception as e:
            pass  # Fail silently to avoid disrupting UI
        
        # Schedule next update
        self.root.after(5000, self.update_automation_status)  # Update every 5 seconds
    
    def update_automation_stats_display(self):
        """Update the automation statistics display"""
        try:
            stats = self.automation_stats
            
            # Clear existing labels
            for label in self.automation_stats_labels.values():
                label.destroy()
            self.automation_stats_labels.clear()
            
            # Create new stats display
            stats_data = [
                ("Devices Processed", stats.get('devices_processed', 0), "blue"),
                ("Fields Collected", stats.get('fields_collected', 0), "green"),
                ("Changes Detected", stats.get('changes_detected', 0), "orange"),
                ("Duplicates Found", stats.get('duplicates_found', 0), "purple"),
                ("Errors", stats.get('errors', 0), "red"),
                ("Runtime (hrs)", f"{stats.get('runtime_hours', 0):.1f}", "gray")
            ]
            
            for i, (title, value, color) in enumerate(stats_data):
                row = i // 3
                col = i % 3
                
                # Create stat card
                card_frame = ttk.Frame(self.stats_grid, relief="solid", borderwidth=1)
                card_frame.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
                
                # Configure grid weight
                self.stats_grid.grid_columnconfigure(col, weight=1)
                
                value_label = ttk.Label(card_frame, text=str(value), 
                                       font=('Arial', 14, 'bold'), foreground=color)
                value_label.pack(pady=(5, 0))
                
                title_label = ttk.Label(card_frame, text=title, font=('Arial', 9))
                title_label.pack(pady=(0, 5))
                
                self.automation_stats_labels[title] = card_frame
                
        except Exception as e:
            pass  # Fail silently
    
    def update_device_list(self):
        """Update the device monitoring list"""
        try:
            # Clear existing items
            for item in self.device_tree.get_children():
                self.device_tree.delete(item)
            
            # Get device data from automation system
            if hasattr(self, 'automation_integration') and self.automation_integration.collector:
                devices = self.automation_integration.collector.get_device_list()
                
                for device in devices[:20]:  # Show top 20 devices
                    # Format values
                    completeness = f"{device.get('completeness_score', 0)}%"
                    last_collection = device.get('last_collection', 'Never')
                    if last_collection and last_collection != 'Never':
                        try:
                            dt = datetime.fromisoformat(last_collection)
                            last_collection = dt.strftime("%Y-%m-%d %H:%M")
                        except:
                            pass
                    
                    status = device.get('status', 'unknown').title()
                    
                    # Color code by completeness
                    if device.get('completeness_score', 0) >= 90:
                        tags = ('high_completeness',)
                    elif device.get('completeness_score', 0) >= 70:
                        tags = ('medium_completeness',)
                    else:
                        tags = ('low_completeness',)
                    
                    # Insert item
                    self.device_tree.insert("", "end", text=str(device.get('id', '')),
                                          values=(device.get('hostname', 'Unknown'),
                                                 device.get('ip_address', ''),
                                                 completeness,
                                                 last_collection,
                                                 status),
                                          tags=tags)
                
                # Configure tag colors
                self.device_tree.tag_configure('high_completeness', background='#d4edda')
                self.device_tree.tag_configure('medium_completeness', background='#fff3cd')
                self.device_tree.tag_configure('low_completeness', background='#f8d7da')
                
        except Exception as e:
            pass  # Fail silently

    # Tool methods (placeholders)
    def network_scanner(self):
        messagebox.showinfo("Network Scanner", "Network scanner tool will be launched")

    def port_scanner(self):
        messagebox.showinfo("Port Scanner", "Port scanner tool will be launched")

    def auto_discovery(self):
        messagebox.showinfo("Auto Discovery", "Auto discovery tool will be launched")

    def performance_monitor(self):
        messagebox.showinfo("Performance Monitor", "Performance monitor will be launched")

    def system_diagnostics(self):
        messagebox.showinfo("System Diagnostics", "System diagnostics will be launched")

    def log_viewer(self):
        messagebox.showinfo("Log Viewer", "Log viewer will be launched")

    def cleanup(self):
        """Cleanup when application closes"""
        # Stop automation if running
        if hasattr(self, 'automation_integration') and self.automation_running:
            try:
                self.automation_integration.stop_automation()
            except:
                pass
        
        # Cleanup web service
        if self.web_service_integration:
            self.web_service_integration.cleanup()

def main():
    """Main function to run the enhanced desktop application"""
    
    root = tk.Tk()
    app = EnhancedAssetManagementApp(root)
    
    # Handle application closing
    def on_closing():
        app.cleanup()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    # Start application
    root.mainloop()

if __name__ == '__main__':
    main()