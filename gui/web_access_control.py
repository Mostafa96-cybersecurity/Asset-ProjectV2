# -*- coding: utf-8 -*-
"""
Web Access Control Interface
---------------------------
Professional web database access control with ACL and service management.

Features:
🌐 Web Service Control: Start/Stop web dashboard service
🔒 Access Control Lists (ACL): IP-based access restrictions
🛡️ Security Monitoring: Real-time access logging and alerts
📊 Service Status: Live monitoring of web service health
🎯 Smart Controls: One-click service management
"""

import sys
import os
import json
import socket
import threading
import time
import ipaddress
import subprocess
from datetime import datetime
from typing import Dict, List, Set, Optional, Tuple
import logging

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QPushButton,
    QTextEdit, QLineEdit, QListWidget, QListWidgetItem, QMessageBox,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QSplitter,
    QFormLayout, QSpinBox, QCheckBox, QFrame, QProgressBar, QComboBox,
    QGridLayout
)
from PyQt6.QtCore import QTimer, pyqtSignal, QThread, QObject, Qt
from PyQt6.QtGui import QFont, QColor, QPalette

log = logging.getLogger(__name__)

class WebServiceManager(QObject):
    """Manages the web dashboard service with smart controls"""
    
    status_changed = pyqtSignal(bool, str)  # running, message
    access_log = pyqtSignal(str, str, str)  # timestamp, ip, action
    
    def __init__(self):
        super().__init__()
        self.service_thread = None
        self.service_process = None
        self.is_running = False
        self.port = 5555
        self.host = "0.0.0.0"  # Listen on all interfaces
        self.acl_enabled = True
        self.allowed_ips: Set[str] = {"127.0.0.1", "::1"}  # Default localhost
        self.blocked_ips: Set[str] = set()
        self.access_log_entries: List[Dict] = []
        self.config_file = "web_service_config.json"
        
        self.load_config()
    
    def load_config(self):
        """Load service configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.port = config.get('port', 5555)
                    self.host = config.get('host', '0.0.0.0')
                    self.acl_enabled = config.get('acl_enabled', True)
                    self.allowed_ips = set(config.get('allowed_ips', ["127.0.0.1", "::1"]))
                    self.blocked_ips = set(config.get('blocked_ips', []))
        except Exception as e:
            log.warning(f"Failed to load config: {e}")
    
    def save_config(self):
        """Save service configuration to file"""
        try:
            config = {
                'port': self.port,
                'host': self.host,
                'acl_enabled': self.acl_enabled,
                'allowed_ips': list(self.allowed_ips),
                'blocked_ips': list(self.blocked_ips)
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            log.error(f"Failed to save config: {e}")
    
    def is_ip_allowed(self, client_ip: str) -> bool:
        """Check if IP is allowed based on ACL rules"""
        if not self.acl_enabled:
            return True
        
        # Check if IP is in blocked list
        if client_ip in self.blocked_ips:
            return False
        
        # Check if IP is in allowed list or if it's a local connection
        if client_ip in self.allowed_ips:
            return True
        
        # Check for subnet matches
        try:
            client_addr = ipaddress.ip_address(client_ip)
            for allowed_ip in self.allowed_ips:
                try:
                    # Check if it's a subnet
                    if '/' in allowed_ip:
                        network = ipaddress.ip_network(allowed_ip, strict=False)
                        if client_addr in network:
                            return True
                except ValueError:
                    continue
        except ValueError:
            pass
        
        return False
    
    def log_access_attempt(self, client_ip: str, allowed: bool, user_agent: str = ""):
        """Log access attempt with details"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        action = "ALLOWED" if allowed else "BLOCKED"
        
        entry = {
            'timestamp': timestamp,
            'ip': client_ip,
            'action': action,
            'user_agent': user_agent
        }
        
        self.access_log_entries.append(entry)
        
        # Keep only last 1000 entries
        if len(self.access_log_entries) > 1000:
            self.access_log_entries = self.access_log_entries[-1000:]
        
        self.access_log.emit(timestamp, client_ip, action)
    
    def start_service(self) -> bool:
        """Start the web service"""
        if self.is_running:
            return True
        
        try:
            # Check available web service modules (priority order)
            project_root = os.path.dirname(os.path.dirname(__file__))
            
            # Enhanced Web Service (highest priority - database only, fully compatible with enhanced_main.py)
            enhanced_service_path = os.path.join(project_root, 'enhanced_web_service.py')
            # Isolated Web Service (second priority - database only, no Excel dependency)
            isolated_service_path = os.path.join(project_root, 'isolated_web_service.py')
            # Fixed Excel-Style Asset Manager (second priority - compact UI)
            fixed_excel_manager_path = os.path.join(project_root, 'fixed_excel_asset_manager.py')
            # Excel-Style Asset Manager (second priority - Excel-like interface)
            excel_manager_path = os.path.join(project_root, 'excel_style_asset_manager.py')
            # Production Asset Monitor (third priority - real data only)
            production_monitor_path = os.path.join(project_root, 'production_asset_monitor.py')
            # Smart Asset Monitor (third priority - comprehensive solution)
            smart_monitor_path = os.path.join(project_root, 'enterprise_asset_monitor.py')
            # Enterprise monitor (fourth priority)
            enterprise_path = os.path.join(project_root, 'enterprise_web_monitor_fixed.py')
            # Original production monitor (fallback)
            original_production_path = os.path.join(project_root, 'production_web_monitor.py')
            # Original monitor (last resort)
            original_path = os.path.join(project_root, 'tools', 'web_database_monitor.py')
            
            launcher_to_use = None
            service_type = None
            
            if os.path.exists(enhanced_service_path):
                launcher_to_use = enhanced_service_path
                service_type = "Enhanced Web Service (Database Only)"
                log.info("Using enhanced web service - database only, fully compatible with enhanced_main.py")
            elif os.path.exists(isolated_service_path):
                launcher_to_use = isolated_service_path
                service_type = "Isolated Web Service (Database Only)"
                log.info("Using isolated web service - database only, completely separated from desktop app")
            elif os.path.exists(fixed_excel_manager_path):
                launcher_to_use = fixed_excel_manager_path
                service_type = "Fixed Excel-Style Asset Manager"
                log.info("Using fixed Excel-style asset manager - compact UI with proper device loading")
            elif os.path.exists(excel_manager_path):
                launcher_to_use = excel_manager_path
                service_type = "Excel-Style Asset Manager"
                log.info("Using Excel-style asset manager - professional Excel-like interface")
            elif os.path.exists(production_monitor_path):
                launcher_to_use = production_monitor_path
                service_type = "Production Asset Monitor"
                log.info("Using production asset monitor - real data only, no demo data")
            elif os.path.exists(smart_monitor_path):
                launcher_to_use = smart_monitor_path
                service_type = "Enterprise Smart Asset Monitor"
                log.info("Using smart asset monitor with Excel integration and advanced analytics")
            elif os.path.exists(enterprise_path):
                launcher_to_use = enterprise_path
                service_type = "Enterprise Web Monitor"
                log.info("Using enterprise web monitor with advanced features")
            elif os.path.exists(original_production_path):
                launcher_to_use = original_production_path
                service_type = "Production Web Monitor"
                log.info("Using original production web monitor")
            elif os.path.exists(original_path):
                # Check if original is importable
                try:
                    from tools.web_database_monitor import app as test_app
                    launcher_to_use = self._create_acl_launcher()
                    service_type = "Development Web Monitor (with ACL)"
                    log.info("Using development web monitor with ACL")
                except ImportError as ie:
                    self.status_changed.emit(False, f"Missing web_database_monitor module: {ie}")
                    return False
            else:
                self.status_changed.emit(False, "No web service modules found")
                return False
            
            # Get the Python executable path
            import sys
            python_exe = sys.executable
            
            # Start the service as a subprocess
            if launcher_to_use in [enterprise_path, original_production_path, smart_monitor_path]:
                # Enterprise/Production monitors run with built-in port 5555
                self.service_process = subprocess.Popen([
                    python_exe, launcher_to_use
                ], 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    bufsize=1
                )
                # Enterprise/Production runs on port 5555
                actual_port = 5555
            else:
                # Development monitor with ACL
                self.service_process = subprocess.Popen([
                    python_exe, launcher_to_use,
                    '--port', str(self.port),
                    '--host', self.host
                ], 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    bufsize=1
                )
                actual_port = self.port
            
            # Wait a moment to see if it starts successfully
            time.sleep(3)
            
            if self.service_process.poll() is None:  # Still running
                self.is_running = True
                self.status_changed.emit(True, f"{service_type} started on {self.host}:{actual_port}")
                return True
            else:
                # Process terminated, get error details
                stdout, stderr = self.service_process.communicate(timeout=5)
                error_msg = f"Service failed to start ({service_type})"
                
                if stderr:
                    error_msg = f"Service error: {stderr[:300]}"
                elif stdout:
                    error_msg = f"Service output: {stdout[:300]}"
                
                self.status_changed.emit(False, error_msg)
                return False
                
        except Exception as e:
            self.status_changed.emit(False, f"Failed to start service: {str(e)}")
            log.error(f"Service start error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def stop_service(self) -> bool:
        """Stop the web service"""
        if not self.is_running:
            return True
        
        try:
            if self.service_process:
                self.service_process.terminate()
                
                # Wait for graceful shutdown
                try:
                    self.service_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.service_process.kill()
                
                self.service_process = None
            
            self.is_running = False
            self.status_changed.emit(False, "Web service stopped")
            return True
            
        except Exception as e:
            self.status_changed.emit(False, f"Error stopping service: {e}")
            return False
    
    def _create_acl_launcher(self) -> str:
        """Create a custom launcher script with ACL integration"""
        launcher_content = f'''# -*- coding: utf-8 -*-
"""
Web Service Launcher with ACL
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from tools.web_database_monitor import app as web_app, init_database
except ImportError:
    print("Error: Could not import web_database_monitor")
    sys.exit(1)

from flask import request, abort
import json
import ipaddress

# Load ACL configuration
acl_config = {json.dumps({
    'acl_enabled': self.acl_enabled,
    'allowed_ips': list(self.allowed_ips),
    'blocked_ips': list(self.blocked_ips)
})}

def check_acl():
    """Check ACL before processing request"""
    try:
        if not acl_config.get('acl_enabled', True):
            return True
        
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', '127.0.0.1'))
        
        # Split in case of multiple forwarded IPs
        client_ip = client_ip.split(',')[0].strip()
        
        # Check blocked IPs
        if client_ip in acl_config.get('blocked_ips', []):
            return False
        
        # Check allowed IPs
        allowed_ips = acl_config.get('allowed_ips', ['127.0.0.1', '::1'])
        
        # Direct match
        if client_ip in allowed_ips:
            return True
        
        # Subnet match
        try:
            client_addr = ipaddress.ip_address(client_ip)
            for allowed_ip in allowed_ips:
                try:
                    if '/' in allowed_ip:
                        network = ipaddress.ip_network(allowed_ip, strict=False)
                        if client_addr in network:
                            return True
                except ValueError:
                    continue
        except ValueError:
            pass
        
        return False
    except Exception as e:
        print(f"ACL check error: {{e}}")
        return True  # Allow on error to prevent lockout

# Add ACL middleware to the web app
@web_app.before_request
def acl_check():
    if not check_acl():
        abort(403)  # Forbidden

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', type=int, default=5555)
    args = parser.parse_args()
    
    print(f"Initializing database...")
    if init_database():
        print(f"Starting web service on {{args.host}}:{{args.port}}...")
        web_app.run(host=args.host, port=args.port, debug=False, use_reloader=False)
    else:
        print("Failed to initialize database")
        sys.exit(1)
'''
        
        launcher_path = "web_service_launcher.py"
        with open(launcher_path, 'w', encoding='utf-8') as f:
            f.write(launcher_content)
        
        return launcher_path
    
    def add_allowed_ip(self, ip: str) -> bool:
        """Add IP to allowed list"""
        try:
            # Validate IP or subnet
            if '/' in ip:
                ipaddress.ip_network(ip, strict=False)
            else:
                ipaddress.ip_address(ip)
            
            self.allowed_ips.add(ip)
            self.save_config()
            return True
        except ValueError:
            return False
    
    def remove_allowed_ip(self, ip: str):
        """Remove IP from allowed list"""
        self.allowed_ips.discard(ip)
        self.save_config()
    
    def add_blocked_ip(self, ip: str) -> bool:
        """Add IP to blocked list"""
        try:
            # Validate IP or subnet
            if '/' in ip:
                ipaddress.ip_network(ip, strict=False)
            else:
                ipaddress.ip_address(ip)
            
            self.blocked_ips.add(ip)
            self.save_config()
            return True
        except ValueError:
            return False
    
    def remove_blocked_ip(self, ip: str):
        """Remove IP from blocked list"""
        self.blocked_ips.discard(ip)
        self.save_config()


class WebAccessControlWidget(QWidget):
    """Professional web access control interface"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.service_manager = WebServiceManager()
        self.setup_ui()
        self.connect_signals()
        self.update_status()
        
        # Status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(3000)  # Update every 3 seconds
    
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("🌐 Web Database Access Control")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title)
        
        # Create main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Service Control
        control_panel = self.create_control_panel()
        splitter.addWidget(control_panel)
        
        # Right panel - Monitoring
        monitor_panel = self.create_monitor_panel()
        splitter.addWidget(monitor_panel)
        
        splitter.setSizes([400, 600])
        layout.addWidget(splitter)
        
        self.apply_styles()
    
    def create_control_panel(self) -> QWidget:
        """Create service control panel"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Service Status Group
        status_group = QGroupBox("🚀 Service Status")
        status_layout = QVBoxLayout(status_group)
        
        self.status_label = QLabel("🔴 Service Stopped")
        self.status_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        status_layout.addWidget(self.status_label)
        
        self.url_label = QLabel("URL: Not Available")
        self.url_label.setStyleSheet("color: #7f8c8d;")
        status_layout.addWidget(self.url_label)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("▶️ Start Service")
        self.start_btn.clicked.connect(self.start_service)
        
        self.stop_btn = QPushButton("⏹️ Stop Service")
        self.stop_btn.clicked.connect(self.stop_service)
        self.stop_btn.setEnabled(False)
        
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        status_layout.addLayout(button_layout)
        
        layout.addWidget(status_group)
        
        # Service Configuration Group
        config_group = QGroupBox("⚙️ Configuration")
        config_layout = QFormLayout(config_group)
        
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1000, 65535)
        self.port_spin.setValue(self.service_manager.port)
        self.port_spin.valueChanged.connect(self.update_config)
        
        self.acl_checkbox = QCheckBox("Enable Access Control")
        self.acl_checkbox.setChecked(self.service_manager.acl_enabled)
        self.acl_checkbox.toggled.connect(self.toggle_acl)
        
        config_layout.addRow("Port:", self.port_spin)
        config_layout.addRow("ACL:", self.acl_checkbox)
        
        layout.addWidget(config_group)
        
        # ACL Management Group
        acl_group = QGroupBox("🔒 Access Control Lists")
        acl_layout = QVBoxLayout(acl_group)
        
        # ACL Tabs
        acl_tabs = QTabWidget()
        
        # Allowed IPs tab
        allowed_tab = QWidget()
        allowed_layout = QVBoxLayout(allowed_tab)
        
        self.allowed_list = QListWidget()
        self.update_allowed_list()
        allowed_layout.addWidget(QLabel("Allowed IPs/Subnets:"))
        allowed_layout.addWidget(self.allowed_list)
        
        allowed_add_layout = QHBoxLayout()
        self.allowed_input = QLineEdit()
        self.allowed_input.setPlaceholderText("Enter IP or subnet (e.g., 192.168.1.0/24)")
        add_allowed_btn = QPushButton("➕ Add")
        add_allowed_btn.clicked.connect(self.add_allowed_ip)
        remove_allowed_btn = QPushButton("➖ Remove")
        remove_allowed_btn.clicked.connect(self.remove_allowed_ip)
        
        allowed_add_layout.addWidget(self.allowed_input)
        allowed_add_layout.addWidget(add_allowed_btn)
        allowed_add_layout.addWidget(remove_allowed_btn)
        allowed_layout.addLayout(allowed_add_layout)
        
        acl_tabs.addTab(allowed_tab, "✅ Allowed")
        
        # Blocked IPs tab
        blocked_tab = QWidget()
        blocked_layout = QVBoxLayout(blocked_tab)
        
        self.blocked_list = QListWidget()
        self.update_blocked_list()
        blocked_layout.addWidget(QLabel("Blocked IPs/Subnets:"))
        blocked_layout.addWidget(self.blocked_list)
        
        blocked_add_layout = QHBoxLayout()
        self.blocked_input = QLineEdit()
        self.blocked_input.setPlaceholderText("Enter IP or subnet to block")
        add_blocked_btn = QPushButton("➕ Block")
        add_blocked_btn.clicked.connect(self.add_blocked_ip)
        remove_blocked_btn = QPushButton("➖ Unblock")
        remove_blocked_btn.clicked.connect(self.remove_blocked_ip)
        
        blocked_add_layout.addWidget(self.blocked_input)
        blocked_add_layout.addWidget(add_blocked_btn)
        blocked_add_layout.addWidget(remove_blocked_btn)
        blocked_layout.addLayout(blocked_add_layout)
        
        acl_tabs.addTab(blocked_tab, "🚫 Blocked")
        
        acl_layout.addWidget(acl_tabs)
        layout.addWidget(acl_group)
        
        layout.addStretch()
        return widget
    
    def create_monitor_panel(self) -> QWidget:
        """Create monitoring panel"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Real-time Status
        status_group = QGroupBox("📊 Real-time Monitoring")
        status_layout = QVBoxLayout(status_group)
        
        self.service_health = QLabel("Health: Unknown")
        self.connection_count = QLabel("Active Connections: 0")
        
        status_layout.addWidget(self.service_health)
        status_layout.addWidget(self.connection_count)
        
        layout.addWidget(status_group)
        
        # Access Log
        log_group = QGroupBox("🔍 Access Log")
        log_layout = QVBoxLayout(log_group)
        
        # Log controls
        log_controls = QHBoxLayout()
        clear_log_btn = QPushButton("🗑️ Clear Log")
        clear_log_btn.clicked.connect(self.clear_access_log)
        export_log_btn = QPushButton("💾 Export Log")
        export_log_btn.clicked.connect(self.export_access_log)
        
        log_controls.addWidget(clear_log_btn)
        log_controls.addWidget(export_log_btn)
        log_controls.addStretch()
        log_layout.addLayout(log_controls)
        
        # Access log table
        self.access_log_table = QTableWidget()
        self.access_log_table.setColumnCount(4)
        self.access_log_table.setHorizontalHeaderLabels(["Timestamp", "IP Address", "Action", "Details"])
        
        header = self.access_log_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        
        log_layout.addWidget(self.access_log_table)
        
        layout.addWidget(log_group)
        
        # Quick Actions
        actions_group = QGroupBox("⚡ Quick Actions")
        actions_layout = QGridLayout(actions_group)
        
        open_browser_btn = QPushButton("🌐 Open in Browser")
        open_browser_btn.clicked.connect(self.open_in_browser)
        
        test_connection_btn = QPushButton("🔗 Test Connection")
        test_connection_btn.clicked.connect(self.test_connection)
        
        minimal_service_btn = QPushButton("🛠️ Minimal Service")
        minimal_service_btn.clicked.connect(self.start_minimal_service)
        minimal_service_btn.setToolTip("Start basic service without ACL (fallback option)")
        
        repair_service_btn = QPushButton("🔧 Repair Service")
        repair_service_btn.clicked.connect(self.repair_service)
        repair_service_btn.setToolTip("Run diagnostic and repair tool")
        
        actions_layout.addWidget(open_browser_btn, 0, 0)
        actions_layout.addWidget(test_connection_btn, 0, 1)
        actions_layout.addWidget(minimal_service_btn, 1, 0)
        actions_layout.addWidget(repair_service_btn, 1, 1)
        
        layout.addWidget(actions_group)
        
        return widget
    
    def connect_signals(self):
        """Connect service manager signals"""
        self.service_manager.status_changed.connect(self.on_status_changed)
        self.service_manager.access_log.connect(self.on_access_log)
    
    def apply_styles(self):
        """Apply professional styling"""
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
            QListWidget {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
            }
            QTableWidget {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                gridline-color: #ecf0f1;
            }
        """)
    
    def start_service(self):
        """Start the web service"""
        self.start_btn.setEnabled(False)
        self.start_btn.setText("⏳ Starting...")
        
        success = self.service_manager.start_service()
        
        if not success:
            self.start_btn.setEnabled(True)
            self.start_btn.setText("▶️ Start Service")
    
    def stop_service(self):
        """Stop the web service"""
        self.stop_btn.setEnabled(False)
        self.stop_btn.setText("⏳ Stopping...")
        
        success = self.service_manager.stop_service()
        
        if not success:
            self.stop_btn.setEnabled(True)
            self.stop_btn.setText("⏹️ Stop Service")
    
    def update_config(self):
        """Update service configuration"""
        self.service_manager.port = self.port_spin.value()
        self.service_manager.save_config()
    
    def toggle_acl(self, enabled: bool):
        """Toggle ACL functionality"""
        self.service_manager.acl_enabled = enabled
        self.service_manager.save_config()
    
    def add_allowed_ip(self):
        """Add IP to allowed list"""
        ip = self.allowed_input.text().strip()
        if ip:
            if self.service_manager.add_allowed_ip(ip):
                self.allowed_input.clear()
                self.update_allowed_list()
                QMessageBox.information(self, "Success", f"Added {ip} to allowed list")
            else:
                QMessageBox.warning(self, "Error", f"Invalid IP address or subnet: {ip}")
    
    def remove_allowed_ip(self):
        """Remove IP from allowed list"""
        current_item = self.allowed_list.currentItem()
        if current_item:
            ip = current_item.text()
            self.service_manager.remove_allowed_ip(ip)
            self.update_allowed_list()
            QMessageBox.information(self, "Success", f"Removed {ip} from allowed list")
    
    def add_blocked_ip(self):
        """Add IP to blocked list"""
        ip = self.blocked_input.text().strip()
        if ip:
            if self.service_manager.add_blocked_ip(ip):
                self.blocked_input.clear()
                self.update_blocked_list()
                QMessageBox.information(self, "Success", f"Added {ip} to blocked list")
            else:
                QMessageBox.warning(self, "Error", f"Invalid IP address or subnet: {ip}")
    
    def remove_blocked_ip(self):
        """Remove IP from blocked list"""
        current_item = self.blocked_list.currentItem()
        if current_item:
            ip = current_item.text()
            self.service_manager.remove_blocked_ip(ip)
            self.update_blocked_list()
            QMessageBox.information(self, "Success", f"Removed {ip} from blocked list")
    
    def update_allowed_list(self):
        """Update allowed IPs list widget"""
        self.allowed_list.clear()
        for ip in sorted(self.service_manager.allowed_ips):
            self.allowed_list.addItem(ip)
    
    def update_blocked_list(self):
        """Update blocked IPs list widget"""
        self.blocked_list.clear()
        for ip in sorted(self.service_manager.blocked_ips):
            self.blocked_list.addItem(ip)
    
    def clear_access_log(self):
        """Clear access log"""
        self.service_manager.access_log_entries.clear()
        self.access_log_table.setRowCount(0)
    
    def export_access_log(self):
        """Export access log to file"""
        if not self.service_manager.access_log_entries:
            QMessageBox.information(self, "Info", "No log entries to export")
            return
        
        try:
            filename = f"web_access_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(self.service_manager.access_log_entries, f, indent=2)
            
            QMessageBox.information(self, "Success", f"Log exported to {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export log: {e}")
    
    def open_in_browser(self):
        """Open web interface in browser"""
        if self.service_manager.is_running:
            import webbrowser
            
            # Determine the actual port
            project_root = os.path.dirname(os.path.dirname(__file__))
            enterprise_path = os.path.join(project_root, 'enterprise_web_monitor.py')
            production_path = os.path.join(project_root, 'production_web_monitor.py')
            
            if os.path.exists(enterprise_path):
                port = 5555  # Enterprise port
            elif os.path.exists(production_path):
                port = 5555  # Production port
            else:
                port = self.service_manager.port  # Development port
                
            url = f"http://127.0.0.1:{port}"
            webbrowser.open(url)
        else:
            QMessageBox.warning(self, "Service Not Running", "Please start the web service first")
    
    def test_connection(self):
        """Test connection to web service"""
        if not self.service_manager.is_running:
            QMessageBox.warning(self, "Service Not Running", "Please start the web service first")
            return
        
        try:
            import urllib.request
            
            # Determine the actual port
            project_root = os.path.dirname(os.path.dirname(__file__))
            enterprise_path = os.path.join(project_root, 'enterprise_web_monitor.py')
            production_path = os.path.join(project_root, 'production_web_monitor.py')
            
            if os.path.exists(enterprise_path):
                port = 5555  # Enterprise port
            elif os.path.exists(production_path):
                port = 5555  # Production port
            else:
                port = self.service_manager.port  # Development port
            
            url = f"http://127.0.0.1:{port}"
            
            response = urllib.request.urlopen(url, timeout=5)
            if response.getcode() == 200:
                QMessageBox.information(self, "Connection Test", "✅ Connection successful!")
            else:
                QMessageBox.warning(self, "Connection Test", f"⚠️ Received status code: {response.getcode()}")
        except Exception as e:
            QMessageBox.critical(self, "Connection Test", f"❌ Connection failed: {e}")
    
    def update_status(self):
        """Update service status display"""
        if self.service_manager.is_running:
            self.status_label.setText("🟢 Service Running")
            self.status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
            
            # Determine the actual port
            project_root = os.path.dirname(os.path.dirname(__file__))
            enterprise_path = os.path.join(project_root, 'enterprise_web_monitor.py')
            production_path = os.path.join(project_root, 'production_web_monitor.py')
            
            if os.path.exists(enterprise_path):
                # Enterprise service runs on port 5555
                service_port = 5555
                service_type = "Enterprise"
            elif os.path.exists(production_path):
                # Production service runs on port 5555
                service_port = 5555
                service_type = "Production"
            else:
                # Development service uses configured port
                service_port = self.service_manager.port
                service_type = "Development"
            
            self.url_label.setText(f"URL: http://{self.service_manager.host}:{service_port} ({service_type})")
            self.url_label.setStyleSheet("color: #3498db;")
            
            self.start_btn.setEnabled(False)
            self.start_btn.setText("▶️ Start Service")
            self.stop_btn.setEnabled(True)
            self.stop_btn.setText("⏹️ Stop Service")
            
            self.service_health.setText("Health: 🟢 Healthy")
            
            # Check if process is still alive
            if self.service_manager.service_process:
                if self.service_manager.service_process.poll() is not None:
                    # Process died
                    self.service_manager.is_running = False
                    self.update_status()
        else:
            self.status_label.setText("🔴 Service Stopped")
            self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
            self.url_label.setText("URL: Not Available")
            self.url_label.setStyleSheet("color: #7f8c8d;")
            
            self.start_btn.setEnabled(True)
            self.start_btn.setText("▶️ Start Service")
            self.stop_btn.setEnabled(False)
            self.stop_btn.setText("⏹️ Stop Service")
            
            self.service_health.setText("Health: 🔴 Stopped")
    
    def on_status_changed(self, running: bool, message: str):
        """Handle service status changes"""
        self.update_status()
        
        # Show status message with better formatting
        if message and not message.startswith("Web service"):  # Don't show redundant messages
            if running:
                QMessageBox.information(self, "✅ Service Started", 
                    f"Web service is now running!\n\n"
                    f"🌐 URL: http://localhost:{self.service_manager.port}\n"
                    f"🔒 ACL: {'Enabled' if self.service_manager.acl_enabled else 'Disabled'}\n"
                    f"📊 Click 'Open in Browser' to access your database")
            else:
                if "error" in message.lower() or "failed" in message.lower():
                    QMessageBox.critical(self, "❌ Service Error", 
                        f"Service failed to start:\n\n{message}\n\n"
                        f"💡 Try using the minimal launcher instead:\n"
                        f"   python minimal_web_launcher.py")
                else:
                    QMessageBox.information(self, "Service Status", message)
    
    def on_access_log(self, timestamp: str, ip: str, action: str):
        """Handle new access log entry"""
        row = self.access_log_table.rowCount()
        self.access_log_table.insertRow(row)
        
        self.access_log_table.setItem(row, 0, QTableWidgetItem(timestamp))
        self.access_log_table.setItem(row, 1, QTableWidgetItem(ip))
        
        # Color code the action
        action_item = QTableWidgetItem(action)
        if action == "ALLOWED":
            action_item.setBackground(QColor("#d5f4e6"))
        else:
            action_item.setBackground(QColor("#fadbd8"))
        
        self.access_log_table.setItem(row, 2, action_item)
        self.access_log_table.setItem(row, 3, QTableWidgetItem("Web dashboard access"))
        
        # Auto-scroll to bottom
        self.access_log_table.scrollToBottom()
        
        # Keep only last 500 entries in table
        if self.access_log_table.rowCount() > 500:
            self.access_log_table.removeRow(0)
    
    def start_minimal_service(self):
        """Start minimal service without ACL as fallback"""
        try:
            import subprocess
            import sys
            
            # Check if minimal launcher exists
            if not os.path.exists("minimal_web_launcher.py"):
                QMessageBox.warning(self, "Missing File", 
                    "Minimal launcher not found. Run the repair tool first:\n\n"
                    "python repair_web_service.py")
                return
            
            # Stop current service if running
            if self.service_manager.is_running:
                self.service_manager.stop_service()
            
            # Start minimal service
            python_exe = sys.executable
            self.minimal_process = subprocess.Popen([
                python_exe, "minimal_web_launcher.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Give it time to start
            time.sleep(2)
            
            if self.minimal_process.poll() is None:
                QMessageBox.information(self, "Minimal Service Started", 
                    "Basic web service started successfully!\n\n"
                    "🌐 URL: http://localhost:5555\n"
                    "⚠️ Note: ACL protection is disabled in minimal mode")
            else:
                QMessageBox.warning(self, "Failed", "Minimal service failed to start")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start minimal service: {e}")
    
    def repair_service(self):
        """Run the repair service tool"""
        try:
            import subprocess
            import sys
            
            # Run repair tool
            python_exe = sys.executable
            result = subprocess.run([
                python_exe, "repair_web_service.py"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                QMessageBox.information(self, "Repair Complete", 
                    "Service repair completed successfully!\n\n"
                    "Output:\n" + result.stdout[-500:])
            else:
                QMessageBox.warning(self, "Repair Issues", 
                    "Repair completed with issues:\n\n" + 
                    (result.stderr or result.stdout)[-500:])
                    
        except subprocess.TimeoutExpired:
            QMessageBox.warning(self, "Timeout", "Repair tool timed out. Try running manually:\n\npython repair_web_service.py")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to run repair tool: {e}")