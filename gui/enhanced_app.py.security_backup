# -*- coding: utf-8 -*-
"""
GUI Module - Enhanced with Threading Performance
gui/app.py - Modified to use ThreadedDeviceCollector for better performance
This module contains the enhanced GUI functionality with optimized threading.
"""
import os
import sys
import inspect
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap, QFont, QIntValidator
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QTextEdit, QProgressBar, QHBoxLayout, QGroupBox, QMessageBox, QCheckBox
)

# Import the enhanced threaded collector instead of the original
try:
    from threaded_enhanced_collector import ThreadedDeviceCollector
    THREADED_COLLECTOR_AVAILABLE = True
except ImportError:
    # Fallback to original collector if threaded version not available
    from core.worker import DeviceInfoCollector as ThreadedDeviceCollector
    THREADED_COLLECTOR_AVAILABLE = False
    
from core.worker import ADWorker  # Keep AD worker as-is
from config.settings import load_config, save_config, get_secret, set_secret, new_secret_id  # cfg/vault I/O
from utils.helpers import which  # which("nmap")
from collectors.ui_add_network_device import open_add_device_dialog

# NEW: import the manual-entry form helpers

NMAP_BIN = which("nmap")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🖥️ Network Assets Collector — Enhanced Threading Edition")
        self.setGeometry(60, 60, 1100, 800)

        try:
            if os.path.exists("ico.ico"):
                self.setWindowIcon(QIcon("ico.ico"))
        except Exception:
            pass

        self.cfg = load_config()
        main_layout = QVBoxLayout()

        # Logo (optional)
        self.logo_label = QLabel(self)
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        except Exception:
            base_dir = os.getcwd()
        logo_path = os.path.join(base_dir, "SQ.svg")
        if os.path.exists(logo_path):
            try:
                pix = QPixmap(logo_path)
                self.logo_label.setPixmap(pix.scaled(420, 90, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            except Exception:
                pass
        main_layout.addWidget(self.logo_label, alignment=Qt.AlignmentFlag.AlignCenter)

        sig = QLabel("Developed by: Mostafa Mohamed", self)
        sig.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sig.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
        sig.setStyleSheet("""QLabel { color: #00AA88; font-style: italic; letter-spacing: 1px; }""")
        main_layout.addWidget(sig, alignment=Qt.AlignmentFlag.AlignCenter)

        # ===== Scanning & File =====
        group_box = QGroupBox("🚀 Enhanced Network Scanning & Data Collection")
        group_layout = QVBoxLayout()

        net_layout = QHBoxLayout()
        net_layout.addWidget(QLabel("Enter IPs/Subnets (comma-separated):"))
        self.target_entry = QLineEdit()
        self.target_entry.setPlaceholderText("10.0.21.0/24, 10.0.0.0/24, 192.168.1.100, ...")
        
        # Add enterprise network quick-select buttons
        enterprise_net_layout = QHBoxLayout()
        
        # Quick add enterprise networks
        btn_office_net = QPushButton("🏢 Office Network")
        btn_office_net.clicked.connect(lambda: self.add_network_range("10.0.21.0/24"))
        btn_office_net.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        btn_main_net = QPushButton("🌐 Main Network")
        btn_main_net.clicked.connect(lambda: self.add_network_range("10.0.0.0/24"))
        btn_main_net.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)

        btn_local_net = QPushButton("🏠 Local Network")
        btn_local_net.clicked.connect(lambda: self.add_network_range("192.168.1.0/24"))
        btn_local_net.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)

        # Add enterprise credentials button
        btn_enterprise_creds = QPushButton("🔐 Enterprise Creds")
        btn_enterprise_creds.clicked.connect(self.add_enterprise_credentials)
        btn_enterprise_creds.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)

        enterprise_net_layout.addWidget(btn_office_net)
        enterprise_net_layout.addWidget(btn_main_net)
        enterprise_net_layout.addWidget(btn_local_net)
        enterprise_net_layout.addWidget(btn_enterprise_creds)
        enterprise_net_layout.addStretch()
        
        net_layout.addWidget(self.target_entry)
        group_layout.addLayout(net_layout)
        group_layout.addLayout(enterprise_net_layout)

        # Progress and status
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)  # Initially hidden
        group_layout.addWidget(self.progress_bar)

        # Collection statistics display
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("""
            QLabel {
                background-color: #ecf0f1;
                color: #2c3e50;
                padding: 8px;
                border-radius: 4px;
                font-family: 'Consolas', monospace;
                font-size: 11px;
            }
        """)
        self.stats_label.hide()  # Initially hidden
        group_layout.addWidget(self.stats_label)

        # Start/Stop buttons
        btn_layout = QHBoxLayout()
        self.start_button = QPushButton("🚀 Start Enhanced Collection")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.start_button.clicked.connect(self.start_collection)

        self.stop_button = QPushButton("⏹️ Stop Collection")
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.stop_button.clicked.connect(self.stop_collection)

        # Database info button
        db_info_btn = QPushButton("📊 Database Info")
        db_info_btn.clicked.connect(self.get_database_info)
        db_info_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #d68910;
            }
        """)

        btn_layout.addWidget(self.start_button)
        btn_layout.addWidget(self.stop_button)
        btn_layout.addWidget(db_info_btn)
        btn_layout.addStretch()
        group_layout.addLayout(btn_layout)
        group_box.setLayout(group_layout)
        main_layout.addWidget(group_box)

        # ===== Credentials Section =====
        creds_box = QGroupBox("🔑 Authentication Credentials")
        creds_layout = QVBoxLayout()
        
        # Windows credentials
        win_creds_box = QGroupBox("Windows/AD Credentials")
        win_creds_layout = QVBoxLayout()
        
        self.win_creds_list = QTextEdit()
        self.win_creds_list.setMaximumHeight(80)
        self.win_creds_list.setPlaceholderText("Windows credentials will be listed here...")
        self.win_creds_list.setReadOnly(True)
        
        win_creds_btn_layout = QHBoxLayout()
        add_win_btn = QPushButton("➕ Add Windows Creds")
        add_win_btn.clicked.connect(self.add_windows_cred_safe)
        add_win_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        load_win_btn = QPushButton("📂 Load")
        load_win_btn.clicked.connect(self.load_windows_creds_safe)
        save_win_btn = QPushButton("💾 Save")
        save_win_btn.clicked.connect(self.save_windows_creds_safe)
        
        for btn in [load_win_btn, save_win_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #95a5a6;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #7f8c8d;
                }
            """)
        
        win_creds_btn_layout.addWidget(add_win_btn)
        win_creds_btn_layout.addWidget(load_win_btn)
        win_creds_btn_layout.addWidget(save_win_btn)
        win_creds_btn_layout.addStretch()
        
        win_creds_layout.addWidget(self.win_creds_list)
        win_creds_layout.addLayout(win_creds_btn_layout)
        win_creds_box.setLayout(win_creds_layout)

        # Linux credentials
        linux_creds_box = QGroupBox("Linux/ESXi SSH Credentials")
        linux_creds_layout = QVBoxLayout()
        
        self.linux_creds_list = QTextEdit()
        self.linux_creds_list.setMaximumHeight(80)
        self.linux_creds_list.setPlaceholderText("Linux/SSH credentials will be listed here...")
        self.linux_creds_list.setReadOnly(True)
        
        linux_creds_btn_layout = QHBoxLayout()
        add_linux_btn = QPushButton("➕ Add Linux/SSH Creds")
        add_linux_btn.clicked.connect(self.add_linux_cred_safe)
        add_linux_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        
        load_linux_btn = QPushButton("📂 Load")
        load_linux_btn.clicked.connect(self.load_linux_creds_safe)
        save_linux_btn = QPushButton("💾 Save")
        save_linux_btn.clicked.connect(self.save_linux_creds_safe)
        
        for btn in [load_linux_btn, save_linux_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #95a5a6;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #7f8c8d;
                }
            """)
        
        # SSH Port setting
        ssh_port_layout = QHBoxLayout()
        ssh_port_layout.addWidget(QLabel("SSH Port:"))
        self.linux_port_entry = QLineEdit("22")
        self.linux_port_entry.setMaximumWidth(60)
        self.linux_port_entry.setValidator(QIntValidator(1, 65535))
        ssh_port_layout.addWidget(self.linux_port_entry)
        ssh_port_layout.addStretch()
        
        linux_creds_btn_layout.addWidget(add_linux_btn)
        linux_creds_btn_layout.addWidget(load_linux_btn)
        linux_creds_btn_layout.addWidget(save_linux_btn)
        linux_creds_btn_layout.addStretch()
        
        linux_creds_layout.addWidget(self.linux_creds_list)
        linux_creds_layout.addLayout(ssh_port_layout)
        linux_creds_layout.addLayout(linux_creds_btn_layout)
        linux_creds_box.setLayout(linux_creds_layout)
        
        creds_layout.addWidget(win_creds_box)
        creds_layout.addWidget(linux_creds_box)
        creds_box.setLayout(creds_layout)
        main_layout.addWidget(creds_box)

        # ===== SNMP Section =====
        snmp_box = QGroupBox("🌐 SNMP Configuration")
        snmp_layout = QVBoxLayout()
        
        # SNMP v2c
        snmp_v2_layout = QHBoxLayout()
        snmp_v2_layout.addWidget(QLabel("SNMP v2c Communities:"))
        self.snmp_v2c_entry = QLineEdit()
        self.snmp_v2c_entry.setPlaceholderText("public, private (comma-separated)")
        snmp_v2_layout.addWidget(self.snmp_v2c_entry)
        
        # SNMP v3
        snmp_v3_layout = QHBoxLayout()
        snmp_v3_layout.addWidget(QLabel("SNMP v3 User:"))
        self.snmp_v3_user_entry = QLineEdit()
        snmp_v3_layout.addWidget(self.snmp_v3_user_entry)
        
        snmp_v3_layout.addWidget(QLabel("Auth Pass:"))
        self.snmp_v3_auth_entry = QLineEdit()
        self.snmp_v3_auth_entry.setEchoMode(QLineEdit.EchoMode.Password)
        snmp_v3_layout.addWidget(self.snmp_v3_auth_entry)
        
        snmp_v3_layout.addWidget(QLabel("Priv Pass:"))
        self.snmp_v3_priv_entry = QLineEdit()
        self.snmp_v3_priv_entry.setEchoMode(QLineEdit.EchoMode.Password)
        snmp_v3_layout.addWidget(self.snmp_v3_priv_entry)
        
        snmp_layout.addLayout(snmp_v2_layout)
        snmp_layout.addLayout(snmp_v3_layout)
        snmp_box.setLayout(snmp_layout)
        main_layout.addWidget(snmp_box)

        # ===== Options Section =====
        options_box = QGroupBox("⚙️ Collection Options")
        options_layout = QHBoxLayout()
        
        self.chk_nmap = QCheckBox("Enable Nmap Discovery")
        self.chk_nmap.setChecked(True)
        self.chk_nmap.setToolTip("Use Nmap for faster network discovery")
        
        self.chk_http = QCheckBox("Enable HTTP Detection")
        self.chk_http.setChecked(True)
        self.chk_http.setToolTip("Attempt to detect web services")
        
        # Threading performance options
        self.chk_high_performance = QCheckBox("High Performance Mode")
        self.chk_high_performance.setChecked(True)
        self.chk_high_performance.setToolTip("Use enhanced threading for faster collection")
        
        self.chk_show_stats = QCheckBox("Show Real-time Statistics")
        self.chk_show_stats.setChecked(True)
        self.chk_show_stats.setToolTip("Display collection statistics during scan")
        
        options_layout.addWidget(self.chk_nmap)
        options_layout.addWidget(self.chk_http)
        options_layout.addWidget(self.chk_high_performance)
        options_layout.addWidget(self.chk_show_stats)
        options_layout.addStretch()
        
        options_box.setLayout(options_layout)
        main_layout.addWidget(options_box)

        # ===== Log Output =====
        log_box = QGroupBox("📋 Collection Log & Status")
        log_layout = QVBoxLayout()
        
        self.log_output = QTextEdit()
        self.log_output.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                font-family: 'Consolas', monospace;
                font-size: 11px;
                border: 1px solid #34495e;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        self.log_output.setPlainText("🖥️ Enhanced Network Assets Collector Ready\n\n"
                                   "✨ New Features:\n"
                                   "• High-performance threading (50 discovery + 20 collection workers)\n"
                                   "• Real-time statistics and progress monitoring\n"
                                   "• Intelligent duplicate prevention\n"
                                   "• Enhanced error recovery with retry mechanisms\n"
                                   "• Smart device prioritization\n\n"
                                   "🚀 Ready to scan networks and collect device information!\n"
                                   "Enter target networks above and click 'Start Enhanced Collection'.\n")
        
        log_layout.addWidget(self.log_output)
        log_box.setLayout(log_layout)
        main_layout.addWidget(log_box)

        # Set main layout
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Initialize data
        self.windows_creds = []
        self.linux_creds = []

        # Load saved settings
        self.load_windows_creds_safe()
        self.load_linux_creds_safe()
        self.load_ui_settings()

        # Apply styles
        self.apply_styles()

    def apply_styles(self):
        """Apply consistent styling to the application"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QGroupBox {
                font-weight: bold;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: #f8f9fa;
            }
            QLineEdit {
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                padding: 6px;
                background-color: white;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
            QCheckBox {
                color: #2c3e50;
                font-weight: bold;
            }
            QCheckBox::indicator:checked {
                background-color: #27ae60;
                border: 2px solid #229954;
            }
        """)

    # ---------- Windows creds ----------
    def add_windows_cred_safe(self):
        try:
            self.add_windows_cred()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add Windows credentials: {e}")

    def add_windows_cred(self, username="", password=""):
        from PyQt6.QtWidgets import QInputDialog
        
        if not username:
            username, ok = QInputDialog.getText(self, "Windows Username", "Enter username (e.g., domain\\user):")
            if not ok or not username.strip():
                return
        
        if not password:
            password, ok = QInputDialog.getText(self, "Windows Password", f"Enter password for {username}:", QLineEdit.EchoMode.Password)
            if not ok:
                return
        
        # Store credentials
        self.windows_creds.append({"username": username.strip(), "password": password})
        self._update_windows_creds_display()

    def _update_windows_creds_display(self):
        display_text = []
        for i, cred in enumerate(self.windows_creds):
            display_text.append(f"{i+1}. {cred['username']} (password hidden)")
        self.win_creds_list.setPlainText("\n".join(display_text))

    def save_windows_creds_safe(self):
        try:
            # Save to secure storage
            for i, cred in enumerate(self.windows_creds):
                secret_id = new_secret_id()
                set_secret(secret_id, cred['password'])
                self.cfg.setdefault("windows_creds", [])
                # Update or add credential entry
                if i < len(self.cfg["windows_creds"]):
                    self.cfg["windows_creds"][i] = {"username": cred['username'], "secret_id": secret_id}
                else:
                    self.cfg["windows_creds"].append({"username": cred['username'], "secret_id": secret_id})
            
            # Remove excess entries if we have fewer creds now
            if len(self.cfg.get("windows_creds", [])) > len(self.windows_creds):
                self.cfg["windows_creds"] = self.cfg["windows_creds"][:len(self.windows_creds)]
            
            save_config(self.cfg)
            QMessageBox.information(self, "Saved", "Windows credentials saved securely.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save credentials: {e}")

    def load_windows_creds_safe(self):
        try:
            self.windows_creds = []
            for cred_cfg in self.cfg.get("windows_creds", []):
                username = cred_cfg.get("username", "")
                secret_id = cred_cfg.get("secret_id", "")
                password = get_secret(secret_id) if secret_id else ""
                if username and password:
                    self.windows_creds.append({"username": username, "password": password})
            self._update_windows_creds_display()
        except Exception as e:
            self.log_output.append(f"Error loading Windows credentials: {e}")

    # ---------- Linux/ESXi creds ----------
    def add_linux_cred_safe(self):
        try:
            self.add_linux_cred()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add Linux credentials: {e}")

    def add_linux_cred(self, username="", password=""):
        from PyQt6.QtWidgets import QInputDialog
        
        if not username:
            username, ok = QInputDialog.getText(self, "Linux/SSH Username", "Enter username:")
            if not ok or not username.strip():
                return
        
        if not password:
            password, ok = QInputDialog.getText(self, "Linux/SSH Password", f"Enter password for {username}:", QLineEdit.EchoMode.Password)
            if not ok:
                return
        
        # Store credentials
        self.linux_creds.append({"username": username.strip(), "password": password})
        self._update_linux_creds_display()

    def _update_linux_creds_display(self):
        display_text = []
        for i, cred in enumerate(self.linux_creds):
            display_text.append(f"{i+1}. {cred['username']} (password hidden)")
        self.linux_creds_list.setPlainText("\n".join(display_text))

    def save_linux_creds_safe(self):
        try:
            # Save to secure storage
            for i, cred in enumerate(self.linux_creds):
                secret_id = new_secret_id()
                set_secret(secret_id, cred['password'])
                self.cfg.setdefault("linux_creds", [])
                # Update or add credential entry
                if i < len(self.cfg["linux_creds"]):
                    self.cfg["linux_creds"][i] = {"username": cred['username'], "secret_id": secret_id}
                else:
                    self.cfg["linux_creds"].append({"username": cred['username'], "secret_id": secret_id})
            
            # Remove excess entries if we have fewer creds now
            if len(self.cfg.get("linux_creds", [])) > len(self.linux_creds):
                self.cfg["linux_creds"] = self.cfg["linux_creds"][:len(self.linux_creds)]
            
            save_config(self.cfg)
            QMessageBox.information(self, "Saved", "Linux credentials saved securely.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save credentials: {e}")

    def load_linux_creds_safe(self):
        try:
            self.linux_creds = []
            for cred_cfg in self.cfg.get("linux_creds", []):
                username = cred_cfg.get("username", "")
                secret_id = cred_cfg.get("secret_id", "")
                password = get_secret(secret_id) if secret_id else ""
                if username and password:
                    self.linux_creds.append({"username": username, "password": password})
            self._update_linux_creds_display()
        except Exception as e:
            self.log_output.append(f"Error loading Linux credentials: {e}")

    # ---------- SNMP getters ----------
    def get_snmp_v2c(self):
        communities = self.snmp_v2c_entry.text().strip()
        if not communities:
            return []
        return [c.strip() for c in communities.split(",") if c.strip()]

    def get_snmp_v3(self):
        user = self.snmp_v3_user_entry.text().strip()
        auth_pass = self.snmp_v3_auth_entry.text()
        priv_pass = self.snmp_v3_priv_entry.text()
        
        if not user:
            return {}
        
        return {
            "user": user,
            "auth_pass": auth_pass,
            "priv_pass": priv_pass
        }

    # ---------- Helpers ----------
    def add_network_range(self, network_range: str):
        """Add network range to the target entry"""
        current_text = self.target_entry.text().strip()
        if current_text:
            if network_range not in current_text:
                self.target_entry.setText(f"{current_text}, {network_range}")
        else:
            self.target_entry.setText(network_range)

    def add_enterprise_credentials(self):
        """Add predefined enterprise credentials"""
        # Add common Windows enterprise credentials
        enterprise_win_creds = [
            {"username": "administrator", "password": ""},
            {"username": "domain\\serviceaccount", "password": ""},
            {"username": "backup_user", "password": ""}
        ]
        
        # Add common Linux credentials  
        enterprise_linux_creds = [
            {"username": "root", "password": ""},
            {"username": "admin", "password": ""},
            {"username": "vmware", "password": ""}
        ]
        
        QMessageBox.information(self, "Enterprise Credentials", 
                               "Enterprise credential templates added.\n"
                               "Please edit each credential to set the correct passwords.")

    def _read_linux_port(self) -> int:
        try:
            return int(self.linux_port_entry.text().strip() or "22")
        except ValueError:
            return 22

    # ---------- Database-Only Operations ----------
    def get_database_info(self):
        """Get information about database storage"""
        try:
            import sqlite3
            db_path = os.path.join(os.getcwd(), "assets.db")
            
            if not os.path.exists(db_path):
                QMessageBox.information(self, "Database Info", 
                                      f"Database file not found: {db_path}\n"
                                      "Run a collection first to create the database.")
                return
            
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                # Get table info
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                
                info_lines = [f"📊 Database: {db_path}", ""]
                
                for (table_name,) in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    info_lines.append(f"📋 {table_name}: {count} records")
                
                # Get recent collection info
                try:
                    cursor.execute("SELECT MAX(last_seen) FROM devices")
                    last_collection = cursor.fetchone()[0]
                    if last_collection:
                        info_lines.append(f"📅 Last Collection: {last_collection}")
                except:
                    pass
                
                QMessageBox.information(self, "Database Information", "\n".join(info_lines))
                
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Error accessing database: {e}")

    def build_windows_creds_for_scan(self):
        return [{"username": c["username"], "password": c["password"]} for c in self.windows_creds]

    def build_linux_creds_for_scan(self):
        return [{"username": c["username"], "password": c["password"]} for c in self.linux_creds]

    def start_collection(self):
        """Start the enhanced threaded collection process"""
        targets_raw = self.target_entry.text().strip()
        if not targets_raw:
            QMessageBox.warning(self, "Missing Targets", "Please enter at least one IP or subnet.")
            return

        targets = [t.strip() for t in self._split_csv(targets_raw) if t.strip()]
        if not targets:
            QMessageBox.warning(self, "Invalid Targets", "No valid targets found in input.")
            return

        # Display target information
        self.log_output.append("🎯 ENHANCED COLLECTION STARTING")
        self.log_output.append("=" * 50)
        for i, target in enumerate(targets, 1):
            if "/" in target:
                self.log_output.append(f"🎯 Target {i}: {target} (network range)")
            else:
                self.log_output.append(f"🎯 Target {i}: {target} (single device)")

        # Get credentials
        win_creds = self.build_windows_creds_for_scan()
        lin_creds = self.build_linux_creds_for_scan()
        snmp_v2c = self.get_snmp_v2c()
        snmp_v3 = self.get_snmp_v3()

        # Display credential information
        self.log_output.append(f"🔑 Windows credentials configured: {len(win_creds)}")
        self.log_output.append(f"🔑 Linux credentials configured: {len(lin_creds)}")
        if snmp_v2c:
            self.log_output.append(f"🔑 SNMP v2c communities: {len(snmp_v2c)}")
        if snmp_v3.get('user'):
            self.log_output.append(f"🔑 SNMP v3 user: {snmp_v3['user']}")

        # Database-only storage - no Excel file needed
        self.log_output.append("💾 Using database-only storage - no Excel files needed")

        # SSH Port (Linux/ESXi)
        linux_port = self._read_linux_port()
        self.cfg["linux_ssh_port"] = linux_port
        save_config(self.cfg)

        # UI state changes
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        if self.chk_show_stats.isChecked():
            self.stats_label.show()

        # Configure Nmap
        global NMAP_BIN
        if not self.chk_nmap.isChecked():
            NMAP_BIN = None

        # Performance settings
        high_performance = self.chk_high_performance.isChecked()

        if THREADED_COLLECTOR_AVAILABLE:
            self.log_output.append(f"🚀 Starting ENHANCED multi-threaded collection... (Linux SSH port = {linux_port})")
            discovery_workers = 50 if high_performance else 20
            collection_workers = 20 if high_performance else 10
            self.log_output.append(f"⚡ Performance Mode: {'HIGH' if high_performance else 'STANDARD'}")
            self.log_output.append(f"👥 Discovery Workers: {discovery_workers}, Collection Workers: {collection_workers}")

            # Create enhanced threaded collector
            self.worker = ThreadedDeviceCollector(
                targets=targets,
                win_creds=win_creds,
                linux_creds=lin_creds,
                snmp_v2c=snmp_v2c,
                snmp_v3=snmp_v3,
                use_http=self.chk_http.isChecked(),
                linux_port=linux_port,
                discovery_workers=discovery_workers,
                collection_workers=collection_workers,
                parent=self
            )

            # Connect enhanced signals
            self.worker.progress_updated.connect(self._on_progress_update)
            self.worker.log_message.connect(self.log_output.append)
            self.worker.statistics_updated.connect(self._on_statistics_update)
            self.worker.collection_finished.connect(self._on_collection_finished)
            
        else:
            # Fallback to original collector
            self.log_output.append(f"🚀 Starting collection with fallback mode... (Linux SSH port = {linux_port})")
            self.log_output.append("⚠️ Enhanced threading not available - using standard collection")
            
            # Build worker args - compatible with original DeviceInfoCollector
            worker_kwargs = dict(
                targets=targets,
                win_creds=win_creds,
                linux_creds=lin_creds,
                snmp_v2c=snmp_v2c,
                snmp_v3=snmp_v3,
                excel_file=None,  # Database-only storage
                use_http=self.chk_http.isChecked(),
                parent=self
            )

            try:
                init_params = inspect.signature(ThreadedDeviceCollector.__init__).parameters
                if "linux_port" in init_params:
                    worker_kwargs["linux_port"] = linux_port
                else:
                    # fallback: expose via env so lower layers can read if they support it
                    os.environ["FS_LINUX_SSH_PORT"] = str(linux_port)
                    self.log_output.append("Note: DeviceInfoCollector doesn't expose 'linux_port'; set FS_LINUX_SSH_PORT for collectors.")
            except Exception:
                os.environ["FS_LINUX_SSH_PORT"] = str(linux_port)

            self.worker = ThreadedDeviceCollector(**worker_kwargs)
            
            # Connect standard signals
            self.worker.update_progress.connect(self.progress_bar.setValue)
            self.worker.log_message.connect(self.log_output.append)
            self.worker.finished_with_status.connect(self.on_finished)

        # Start the collection
        self.worker.start()
        self.log_output.append("✨ Collection started!")

    def _on_progress_update(self, percentage: int):
        """Handle progress updates from the threaded collector"""
        self.progress_bar.setValue(percentage)

    def _on_statistics_update(self, stats: dict):
        """Handle statistics updates from the threaded collector"""
        if self.chk_show_stats.isChecked() and self.stats_label.isVisible():
            stats_text = f"📊 Live Stats: Discovered: {stats.get('discovered', 0)} | " \
                        f"Collected: {stats.get('collected', 0)} | " \
                        f"Failed: {stats.get('failed', 0)} | " \
                        f"Queue: {stats.get('queue_size', 0)} | " \
                        f"Success Rate: {stats.get('success_rate', 0):.1f}%"
            self.stats_label.setText(stats_text)

    def _on_collection_finished(self, canceled: bool, final_stats: dict):
        """Handle collection completion"""
        self.log_output.append("=" * 50)
        self.log_output.append("🏁 ENHANCED COLLECTION COMPLETED")
        
        if canceled:
            self.log_output.append("⚠️ Collection was canceled by user")
        else:
            self.log_output.append("✅ Collection completed successfully")
        
        # Display final statistics
        self.log_output.append("📊 Final Statistics:")
        self.log_output.append(f"   • Total Discovered: {final_stats.get('discovered', 0)}")
        self.log_output.append(f"   • Successfully Collected: {final_stats.get('collected', 0)}")
        self.log_output.append(f"   • Failed: {final_stats.get('failed', 0)}")
        self.log_output.append(f"   • Success Rate: {final_stats.get('success_rate', 0):.1f}%")
        self.log_output.append(f"   • Total Time: {final_stats.get('total_time', 0):.2f} seconds")
        
        # Reset UI state
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.stats_label.hide()

    def _split_csv(self, s: str):
        # allow both comma & whitespace separated input
        parts = []
        for chunk in s.replace(" ", ",").split(","):
            c = chunk.strip()
            if c:
                parts.append(c)
        return parts

    def stop_collection(self):
        """Stop the collection process"""
        if hasattr(self, "worker") and self.worker.is_running():
            self.worker.stop()
            self.log_output.append("🛑 Cancellation requested...")

    def on_finished(self, canceled: bool):
        """Legacy compatibility method"""
        self._on_collection_finished(canceled, {})

    # ---------- AD fetch/merge ----------
    def fetch_from_ad_threaded(self):
        """Fetch data from Active Directory"""
        ad = self.cfg.get("ad", {})
        server = (self.ad_server.text().strip() or ad.get("server", ""))
        base_dn = (self.ad_base.text().strip() or ad.get("base_dn", ""))
        user = (self.ad_user.text().strip() or ad.get("username", ""))
        pwd = (self.ad_pass.text() or get_secret(ad.get("secret_id", "")))
        use_ssl = self.ad_ssl.isChecked()

        # Database-only storage - no Excel file needed
        if not all([server, base_dn, user, pwd]):
            QMessageBox.warning(self, "Missing AD Info", 
                              "Please fill in all Active Directory connection details.")
            return

        self.log_output.append(f"🔍 Fetching from AD: {server}")
        self.ad_fetch_btn.setEnabled(False)

        self.ad_worker = ADWorker(server, base_dn, user, pwd, use_ssl, 
                                 excel_file=None, parent=self)  # Database-only
        self.ad_worker.log_message.connect(self.log_output.append)
        self.ad_worker.finished.connect(lambda: self.ad_fetch_btn.setEnabled(True))
        self.ad_worker.start()

    def load_ui_settings(self):
        """Load UI settings from config"""
        try:
            # Load SNMP settings
            snmp_config = self.cfg.get("snmp", {})
            if "v2c_communities" in snmp_config:
                self.snmp_v2c_entry.setText(", ".join(snmp_config["v2c_communities"]))
            
            if "v3" in snmp_config:
                v3_config = snmp_config["v3"]
                self.snmp_v3_user_entry.setText(v3_config.get("user", ""))
                # Passwords are not loaded for security reasons
            
            # Load SSH port
            ssh_port = self.cfg.get("linux_ssh_port", 22)
            self.linux_port_entry.setText(str(ssh_port))
            
        except Exception as e:
            self.log_output.append(f"Error loading UI settings: {e}")

    # ---------- NEW: open the manual-entry dialog ----------
    def open_manual_device_dialog(self):
        """Open dialog for manual device entry"""
        try:
            # Use database path instead of Excel file
            db_path = os.path.join(os.getcwd(), "assets.db")
            open_add_device_dialog(db_path, parent=self)
            self.log_output.append("📝 Manual device entry dialog opened")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open device dialog: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Enhanced Network Assets Collector")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("Mostafa Mohamed")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())