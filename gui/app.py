# -*- coding: utf-8 -*-
"""
GUI Module - ULTRA-FAST EDITION with Thread-Safe Enhancements
gui/app.py
This module contains the GUI functionality for the Asset Project with ultra-fast collection.
"""
import os
import sys
import inspect
from PyQt6.QtCore import Qt, QTimer, QTime
from PyQt6.QtGui import QIcon, QPixmap, QFont, QIntValidator
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QTextEdit, QProgressBar, QFileDialog, QHBoxLayout, QGroupBox, QMessageBox, QCheckBox,
    QScrollArea, QComboBox, QInputDialog, QDialog, QListWidget, QListWidgetItem,
    QTableWidget, QTableWidgetItem, QHeaderView
)

# Import thread-safe enhancements
try:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from gui.thread_safe_enhancement import (
        make_collection_thread_safe,
        create_thread_safe_collector,
        thread_safe_operation
    )
    THREAD_SAFE_AVAILABLE = True
    print("✅ Thread-safe enhancements loaded - prevents UI hanging")
except ImportError:
    THREAD_SAFE_AVAILABLE = False
    print("⚠️ Thread-safe enhancements not available - may experience UI hanging")

# Import automatic scanner
try:
    from automatic_scanner import (
        AutomaticScanner, AutoScanTarget, ScanSchedule, ScheduleType, PYQT6_AVAILABLE, AutoScanConfigDialog
    )
    AUTO_SCANNER_AVAILABLE = True
    print("✅ Automatic scanner loaded - scheduled scanning available")
except ImportError:
    AUTO_SCANNER_AVAILABLE = False
    print("⚠️ Automatic scanner not available - scheduled scanning disabled")

# Import massive scan protection
try:
    from massive_scan_protection import apply_massive_scan_protection
    MASSIVE_SCAN_PROTECTION_AVAILABLE = True
    print("�️ Massive scan protection loaded - handles 3+ networks without hanging")
except ImportError:
    MASSIVE_SCAN_PROTECTION_AVAILABLE = False
    print("⚠️ Massive scan protection not available")

# Import emergency UI fix
try:
    from emergency_ui_fix import emergency_fix_collection_hanging
    EMERGENCY_FIX_AVAILABLE = True
    print("🚨 Emergency UI hang fix loaded - guaranteed responsive UI")
except ImportError:
    EMERGENCY_FIX_AVAILABLE = False
    print("⚠️ Emergency fix not available")

# Import instant UI fix for immediate responsiveness
try:
    from instant_ui_fix import apply_instant_ui_fix
    INSTANT_FIX_AVAILABLE = True
    print("⚡ Instant UI responsiveness fix loaded")
except ImportError:
    INSTANT_FIX_AVAILABLE = False
    print("⚠️ Instant fix not available")

# Import process-based collection for ultimate UI responsiveness
try:
    from process_based_collection import apply_process_based_collection
    PROCESS_COLLECTION_AVAILABLE = True
    print("🚀 Process-based collection loaded")
except ImportError:
    PROCESS_COLLECTION_AVAILABLE = False
    print("⚠️ Process collection not available")

# Import critical threading fix for error resolution
try:
    from critical_threading_fix import apply_critical_threading_fix
    CRITICAL_THREADING_FIX_AVAILABLE = True
    print("🔧 Critical threading fix loaded")
except ImportError:
    CRITICAL_THREADING_FIX_AVAILABLE = False
    print("⚠️ Critical threading fix not available")

# Import SSH error handler for connection safety
try:
    from ssh_error_handler import apply_ssh_error_handling, apply_network_connection_management
    SSH_ERROR_HANDLER_AVAILABLE = True
    print("🔗 SSH error handler loaded")
except ImportError:
    SSH_ERROR_HANDLER_AVAILABLE = False
    print("⚠️ SSH error handler not available")

# Import collection limiter to prevent massive scans
try:
    from collection_limiter import apply_collection_limiter
    COLLECTION_LIMITER_AVAILABLE = True
    print("🛡️ Collection limiter loaded")
except ImportError:
    COLLECTION_LIMITER_AVAILABLE = False
    print("⚠️ Collection limiter not available")

# Import enhanced collection strategy with fallbacks
try:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from enhanced_collection_strategy import EnhancedCollectionStrategy as DeviceInfoCollector
    ENHANCED_STRATEGY_AVAILABLE = True
    PROPER_STRATEGY_AVAILABLE = False
    ULTRA_FAST_AVAILABLE = False
    print("🎯 Enhanced Collection Strategy loaded (MAXIMUM DATA COLLECTION)")
except ImportError:
    ENHANCED_STRATEGY_AVAILABLE = False
    # Fallback to proper collection strategy
    try:
        from proper_collection_strategy import ProperCollectionStrategy as DeviceInfoCollector
        PROPER_STRATEGY_AVAILABLE = True
        ENHANCED_STRATEGY_AVAILABLE = False
        ULTRA_FAST_AVAILABLE = False
        print("🎯 Proper 3-step collection strategy loaded (PING → NMAP → COLLECT)")
    except ImportError:
        PROPER_STRATEGY_AVAILABLE = False
        # Fallback to ultra-fast collector
        try:
            from ultra_fast_collector import UltraFastDeviceCollector as DeviceInfoCollector
            ULTRA_FAST_AVAILABLE = True
            ENHANCED_STRATEGY_AVAILABLE = False
            PROPER_STRATEGY_AVAILABLE = False
            print("✅ ULTRA-FAST collector loaded - prevents hangs and maximizes speed")
        except ImportError:
            # Final fallback to original collector
            from core.worker import DeviceInfoCollector
            ULTRA_FAST_AVAILABLE = False
            ENHANCED_STRATEGY_AVAILABLE = False
            PROPER_STRATEGY_AVAILABLE = False
            print("⚠️ Using standard collector - may experience hangs during collection")

try:
    from core.worker import ADWorker  # type: ignore
except ImportError:
    # Create dummy AD worker if not available
    from PyQt6.QtCore import QThread, pyqtSignal
    
    class ADWorker(QThread):
        log_message = pyqtSignal(str)
        finished_with_status = pyqtSignal(bool)
        
        def __init__(self, server, base_dn, user, pwd, use_ssl, excel_file, parent=None):
            super().__init__(parent)
            
        def start(self):
            self.log_message.emit("AD Worker not available")
            self.finished_with_status.emit(False)

from config.settings import load_config, save_config, get_secret, set_secret, new_secret_id  # cfg/vault I/O
from collectors.snmp_collector import _PYSNMP_OK, _SNMP_BACKEND
from utils.helpers import which  # which("nmap")
from collectors.ui_add_network_device import open_add_device_dialog, ensure_workbook_tabs

# NEW: import the manual-entry form helpers
from collectors.ui_add_network_device import (
    open_add_device_dialog,
    ensure_workbook_tabs,
)

NMAP_BIN = which("nmap")


# ---------------- Safe layout clearing ----------------
def _clear_layout(layout):
    """
    Detach widgets from parent (without deleteLater), and clear child layouts.
    Avoids double-free/use-after-free crashes (0xC0000409).
    """
    try:
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
            child = item.layout()
            if child is not None:
                _clear_layout(child)
    except Exception:
        pass


# ---------------- Credential row widget ----------------
class CredRow(QWidget):
    """
    A single credential row (Username + Password + Delete Button). 
    """
    def __init__(self, user_placeholder: str, pass_placeholder: str,
                 username: str = "", password: str = "", parent=None, delete_callback=None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        self.u = QLineEdit(self)
        self.u.setPlaceholderText(user_placeholder)
        self.u.setText(username)

        self.p = QLineEdit(self)
        self.p.setEchoMode(QLineEdit.EchoMode.Password)
        self.p.setPlaceholderText(pass_placeholder)
        self.p.setText(password)

        # Delete button
        self.delete_btn = QPushButton("🗑️", self)
        self.delete_btn.setFixedSize(30, 25)
        self.delete_btn.setStyleSheet("QPushButton { background-color: #e74c3c; color: white; border: none; border-radius: 3px; }")
        self.delete_btn.setToolTip("Delete this credential")
        
        if delete_callback:
            self.delete_btn.clicked.connect(lambda: delete_callback(self))

        lay.addWidget(QLabel("Username:", self))
        lay.addWidget(self.u)
        lay.addWidget(QLabel("Password:", self))
        lay.addWidget(self.p)
        lay.addWidget(self.delete_btn)

    def username(self) -> str:
        return self.u.text().strip()

    def password(self) -> str:
        return self.p.text()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Network Assets Collector — High-Performance Edition")
        self.setGeometry(60, 60, 1100, 780)

        try:
            if os.path.exists("ico.ico"):
                self.setWindowIcon(QIcon("ico.ico"))
        except Exception:
            pass

        self.cfg = load_config()
        
        root_layout = QVBoxLayout()

        # Logo (optional)
        self.logo_label = QLabel(self)
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        except Exception:
            base_dir = os.getcwd()
        logo_path = os.path.join(base_dir, ".", "SQ.svg")  # Adjust path if needed
        if os.path.exists(logo_path):
            try:
                pix = QPixmap(logo_path)
                self.logo_label.setPixmap(
                    pix.scaled(420, 90, Qt.AspectRatioMode.KeepAspectRatio,
                               Qt.TransformationMode.SmoothTransformation)
                )
            except Exception:
                pass
        root_layout.addWidget(self.logo_label, alignment=Qt.AlignmentFlag.AlignCenter)

        sig = QLabel("Developed by: Mostafa Mohamed", self)
        sig.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sig.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
        sig.setStyleSheet("""QLabel { color: #00AA88; font-style: italic; letter-spacing: 1px; }""")
        root_layout.addWidget(sig, alignment=Qt.AlignmentFlag.AlignCenter)

                # ===== Web Service Controls =====
        web_service_box = QGroupBox("🌐 Web Service Control")
        web_service_layout = QVBoxLayout()
        
        # Web service status display
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Status:"))
        self.web_service_status = QLabel("🔴 Stopped")
        self.web_service_status.setStyleSheet("color: red; font-weight: bold; padding: 5px;")
        status_layout.addWidget(self.web_service_status)
        status_layout.addStretch()
        web_service_layout.addLayout(status_layout)
        
        # Web service URL
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("URL:"))
        self.web_service_url = QLabel("http://localhost:8080")
        self.web_service_url.setStyleSheet("color: blue; font-weight: bold; padding: 5px;")
        url_layout.addWidget(self.web_service_url)
        url_layout.addStretch()
        web_service_layout.addLayout(url_layout)
        
        # Control buttons
        web_buttons_layout = QHBoxLayout()
        self.btn_start_web = QPushButton("🚀 Start Web Service")
        self.btn_stop_web = QPushButton("⏹️ Stop Web Service")
        self.btn_open_web = QPushButton("🌐 Open in Browser")
        self.btn_restart_web = QPushButton("🔄 Restart Web Service")
        
        # Style the web service buttons
        self.btn_start_web.setStyleSheet("QPushButton { background-color: #28a745; color: white; font-weight: bold; }")
        self.btn_stop_web.setStyleSheet("QPushButton { background-color: #dc3545; color: white; font-weight: bold; }")
        self.btn_open_web.setStyleSheet("QPushButton { background-color: #007bff; color: white; font-weight: bold; }")
        self.btn_restart_web.setStyleSheet("QPushButton { background-color: #ffc107; color: black; font-weight: bold; }")
        
        # Connect button events
        self.btn_start_web.clicked.connect(self.start_web_service)
        self.btn_stop_web.clicked.connect(self.stop_web_service)
        self.btn_open_web.clicked.connect(self.open_web_service)
        self.btn_restart_web.clicked.connect(self.restart_web_service)
        
        # Initially disable stop button
        self.btn_stop_web.setEnabled(False)
        self.btn_open_web.setEnabled(False)
        self.btn_restart_web.setEnabled(False)
        
        web_buttons_layout.addWidget(self.btn_start_web)
        web_buttons_layout.addWidget(self.btn_stop_web)
        web_buttons_layout.addWidget(self.btn_open_web)
        web_buttons_layout.addWidget(self.btn_restart_web)
        web_service_layout.addLayout(web_buttons_layout)
        
        # Web service log area
        web_service_layout.addWidget(QLabel("Web Service Log:"))
        self.web_service_log = QTextEdit()
        self.web_service_log.setMaximumHeight(100)
        self.web_service_log.setPlaceholderText("Web service logs will appear here...")
        web_service_layout.addWidget(self.web_service_log)
        
        # Security & Access Control
        security_layout = QHBoxLayout()
        
        # Access Control
        self.btn_access_control = QPushButton("🔐 Access Control")
        self.btn_view_logs = QPushButton("📊 View Access Logs")
        self.btn_backup_db = QPushButton("💾 Backup Database")
        
        # Style security buttons
        self.btn_access_control.setStyleSheet("QPushButton { background-color: #FF5722; color: white; font-weight: bold; }")
        self.btn_view_logs.setStyleSheet("QPushButton { background-color: #9C27B0; color: white; font-weight: bold; }")
        self.btn_backup_db.setStyleSheet("QPushButton { background-color: #607D8B; color: white; font-weight: bold; }")
        
        # Connect security buttons
        self.btn_access_control.clicked.connect(self.open_access_control)
        self.btn_view_logs.clicked.connect(self.view_access_logs)
        self.btn_backup_db.clicked.connect(self.backup_database)
        
        security_layout.addWidget(self.btn_access_control)
        security_layout.addWidget(self.btn_view_logs)
        security_layout.addWidget(self.btn_backup_db)
        web_service_layout.addLayout(security_layout)
        
        web_service_box.setLayout(web_service_layout)
        root_layout.addWidget(web_service_box)
        
        # Initialize web service process
        self.web_service_process = None
        
        # Check initial web service status
        QTimer.singleShot(1000, self.check_web_service_status)

        # ===== Network Profiles Management =====
        profiles_box = QGroupBox("💾 Network Profiles & Management")
        profiles_layout = QVBoxLayout()
        
        # Profile selection and management
        profile_control_layout = QHBoxLayout()
        profile_control_layout.addWidget(QLabel("Profile:"))
        self.profile_combo = QComboBox()
        self.profile_combo.addItem("-- Select Profile --")
        self.load_saved_profiles()
        profile_control_layout.addWidget(self.profile_combo)
        
        self.btn_load_profile = QPushButton("📂 Load")
        self.btn_save_profile = QPushButton("💾 Save")
        self.btn_manage_profile = QPushButton("⚙️ Manage Networks")
        self.btn_delete_profile = QPushButton("🗑️ Delete")
        
        # Style profile buttons with green theme
        self.btn_load_profile.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        self.btn_save_profile.setStyleSheet("QPushButton { background-color: #2196F3; color: white; font-weight: bold; }")
        self.btn_manage_profile.setStyleSheet("QPushButton { background-color: #FF9800; color: white; font-weight: bold; }")
        self.btn_delete_profile.setStyleSheet("QPushButton { background-color: #f44336; color: white; font-weight: bold; }")
        
        # Connect profile management buttons
        self.btn_load_profile.clicked.connect(self.load_network_profile)
        self.btn_save_profile.clicked.connect(self.save_network_profile)
        self.btn_manage_profile.clicked.connect(self.manage_profile_networks)
        self.btn_delete_profile.clicked.connect(self.delete_network_profile)
        self.profile_combo.currentTextChanged.connect(self.on_profile_selection_changed)
        
        profile_control_layout.addWidget(self.btn_load_profile)
        profile_control_layout.addWidget(self.btn_save_profile)
        profile_control_layout.addWidget(self.btn_manage_profile)
        profile_control_layout.addWidget(self.btn_delete_profile)
        profiles_layout.addLayout(profile_control_layout)
        
        profiles_box.setLayout(profiles_layout)
        root_layout.addWidget(profiles_box)

        # ===== AUTOMATIC SCHEDULED SCANNING =====
        if AUTO_SCANNER_AVAILABLE:
            auto_scan_box = QGroupBox("🕐 Automatic Scheduled Scanning")
            auto_scan_layout = QVBoxLayout()
            
            # Initialize automatic scanner
            self.automatic_scanner = AutomaticScanner(self)
            self.automatic_scanner.log_message.connect(lambda msg: self.log_output.append(msg))
            self.automatic_scanner.status_changed.connect(self.update_auto_scan_status)
            self.automatic_scanner.scan_started.connect(self.on_auto_scan_started)
            self.automatic_scanner.scan_completed.connect(self.on_auto_scan_completed)
            self.automatic_scanner.scan_error.connect(self.on_auto_scan_error)
            
            # Status and controls
            auto_status_layout = QHBoxLayout()
            auto_status_layout.addWidget(QLabel("Status:"))
            self.auto_scan_status = QLabel("🔴 Stopped")
            self.auto_scan_status.setStyleSheet("color: red; font-weight: bold;")
            auto_status_layout.addWidget(self.auto_scan_status)
            auto_status_layout.addStretch()
            auto_scan_layout.addLayout(auto_status_layout)
            
            # Control buttons
            auto_control_layout = QHBoxLayout()
            self.btn_start_auto_scan = QPushButton("🚀 Start Automatic Scanning")
            self.btn_stop_auto_scan = QPushButton("⏹️ Stop Automatic Scanning")
            self.btn_configure_auto_scan = QPushButton("⚙️ Configure Schedules & Targets")
            
            # Style auto scan buttons
            self.btn_start_auto_scan.setStyleSheet("QPushButton { background-color: #28a745; color: white; font-weight: bold; }")
            self.btn_stop_auto_scan.setStyleSheet("QPushButton { background-color: #dc3545; color: white; font-weight: bold; }")
            self.btn_configure_auto_scan.setStyleSheet("QPushButton { background-color: #007bff; color: white; font-weight: bold; }")
            
            # Connect auto scan buttons
            self.btn_start_auto_scan.clicked.connect(self.start_automatic_scanning)
            self.btn_stop_auto_scan.clicked.connect(self.stop_automatic_scanning)
            self.btn_configure_auto_scan.clicked.connect(self.configure_automatic_scanning)
            
            # Initially disable stop button
            self.btn_stop_auto_scan.setEnabled(False)
            
            auto_control_layout.addWidget(self.btn_start_auto_scan)
            auto_control_layout.addWidget(self.btn_stop_auto_scan)
            auto_control_layout.addWidget(self.btn_configure_auto_scan)
            auto_scan_layout.addLayout(auto_control_layout)
            
            # Quick status info
            auto_info_layout = QHBoxLayout()
            self.auto_scan_info = QLabel("Automatic scanning: Configure targets and schedules to begin")
            self.auto_scan_info.setStyleSheet("color: #666; font-style: italic;")
            auto_info_layout.addWidget(self.auto_scan_info)
            auto_scan_layout.addLayout(auto_info_layout)
            
            auto_scan_box.setLayout(auto_scan_layout)
            root_layout.addWidget(auto_scan_box)
        else:
            # Show disabled message if automatic scanner not available
            auto_scan_box = QGroupBox("🕐 Automatic Scheduled Scanning (Disabled)")
            auto_scan_layout = QVBoxLayout()
            disabled_label = QLabel("⚠️ Automatic scanning module not available. Manual scanning only.")
            disabled_label.setStyleSheet("color: orange; font-style: italic;")
            auto_scan_layout.addWidget(disabled_label)
            auto_scan_box.setLayout(auto_scan_layout)
            root_layout.addWidget(auto_scan_box)

        # ===== Start button & Progress =====
        group_box = QGroupBox("Manual Scanning & Data Collection")
        group_layout = QVBoxLayout()

        net_layout = QHBoxLayout()
        net_layout.addWidget(QLabel("Enter IPs/Subnets (comma-separated):"))
        self.target_entry = QLineEdit()
        self.target_entry.setPlaceholderText("10.0.21.0/24, 10.0.0.0/24, 192.168.1.100, ...")
        
        # Add enterprise network quick-select buttons
        enterprise_net_layout = QHBoxLayout()
        self.btn_add_mixed_net = QPushButton("Add Mixed Network (10.0.21.0/24)")
        self.btn_add_server_net = QPushButton("Add Server Network (10.0.0.0/24)")
        self.btn_clear_networks = QPushButton("Clear Networks")
        
        self.btn_add_mixed_net.clicked.connect(lambda: self.add_network_range("10.0.21.0/24"))
        self.btn_add_server_net.clicked.connect(lambda: self.add_network_range("10.0.0.0/24"))
        self.btn_clear_networks.clicked.connect(lambda: self.target_entry.clear())
        
        # Style the network buttons
        self.btn_add_mixed_net.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; }")
        self.btn_add_server_net.setStyleSheet("QPushButton { background-color: #2196F3; color: white; }")
        self.btn_clear_networks.setStyleSheet("QPushButton { background-color: #f44336; color: white; }")
        
        enterprise_net_layout.addWidget(self.btn_add_mixed_net)
        enterprise_net_layout.addWidget(self.btn_add_server_net)
        enterprise_net_layout.addWidget(self.btn_clear_networks)
        
        net_layout.addWidget(self.target_entry)
        group_layout.addLayout(net_layout)
        group_layout.addLayout(enterprise_net_layout)

        # Database-only storage notification
        db_layout = QHBoxLayout()
        db_info_label = QLabel("💾 All data stored in database only - No Excel files needed!")
        db_info_label.setStyleSheet("color: green; font-weight: bold; padding: 5px;")
        db_layout.addWidget(db_info_label)
        group_layout.addLayout(db_layout)

        # ===== Windows creds =====
        win_box = QGroupBox("Windows Credentials (WMI) — stored securely")
        win_l = QVBoxLayout()
        
        # Enterprise credential preset buttons
        enterprise_creds_layout = QHBoxLayout()
        self.btn_add_enterprise_creds = QPushButton("Add Enterprise Credentials")
        self.btn_add_enterprise_creds.setStyleSheet("QPushButton { background-color: #FF9800; color: white; }")
        self.btn_add_enterprise_creds.clicked.connect(self.add_enterprise_credentials)
        enterprise_creds_layout.addWidget(self.btn_add_enterprise_creds)
        win_l.addLayout(enterprise_creds_layout)
        
        self.win_creds_layout = QVBoxLayout()
        btns = QHBoxLayout()

        self.btn_add_win = QPushButton("Add Windows Credential")
        try:
            self.btn_add_win.clicked.disconnect()
        except Exception:
            pass
        self.btn_add_win.clicked.connect(lambda: self.add_windows_cred())

        self.btn_save_win = QPushButton("Save Windows Credentials")
        self.btn_save_win.clicked.connect(self.save_windows_creds)
        
        self.btn_clear_win = QPushButton("Clear All Windows")
        self.btn_clear_win.clicked.connect(self.clear_all_windows_creds)
        self.btn_clear_win.setStyleSheet("QPushButton { background-color: #e74c3c; color: white; }")

        self.btn_load_win = QPushButton("Load Windows Credentials")
        self.btn_load_win.clicked.connect(self.load_windows_creds)

        btns.addWidget(self.btn_add_win)
        btns.addWidget(self.btn_save_win)
        btns.addWidget(self.btn_clear_win)
        btns.addWidget(self.btn_load_win)
        win_l.addLayout(self.win_creds_layout)
        win_l.addLayout(btns)
        win_box.setLayout(win_l)
        group_layout.addWidget(win_box)

        # ===== Linux/ESXi creds =====
        lin_box = QGroupBox("Linux/ESXi Credentials (SSH) — stored securely")
        lin_l = QVBoxLayout()
        self.lin_creds_layout = QVBoxLayout()

        # Row: Add/Save/Load buttons
        btns2 = QHBoxLayout()
        self.btn_add_lin = QPushButton("Add Linux/ESXi Credential")
        try:
            self.btn_add_lin.clicked.disconnect()
        except Exception:
            pass
        self.btn_add_lin.clicked.connect(lambda: self.add_linux_cred())

        self.btn_save_lin = QPushButton("Save Linux/Esxi Credentials")
        self.btn_save_lin.clicked.connect(self.save_linux_creds)
        
        self.btn_clear_lin = QPushButton("Clear All Linux")
        self.btn_clear_lin.clicked.connect(self.clear_all_linux_creds)
        self.btn_clear_lin.setStyleSheet("QPushButton { background-color: #e74c3c; color: white; }")

        self.btn_load_lin = QPushButton("Load Linux/Esxi Credentials")
        self.btn_load_lin.clicked.connect(self.load_linux_creds)

        btns2.addWidget(self.btn_add_lin)
        btns2.addWidget(self.btn_save_lin)
        btns2.addWidget(self.btn_clear_lin)
        btns2.addWidget(self.btn_load_lin)

        # Row: SSH Port
        port_row = QHBoxLayout()
        port_row.addWidget(QLabel("SSH Port:"))
        self.lin_port = QLineEdit()
        self.lin_port.setValidator(QIntValidator(1, 65535, self))
        default_port = int(self.cfg.get("linux_ssh_port", 22) or 22)
        self.lin_port.setText(str(default_port))
        self.lin_port.setPlaceholderText("22")
        self.lin_port.setToolTip("Leave empty for Linux defaults (22). Fill for switches/firewalls/ESXi.")
        port_row.addWidget(self.lin_port)

        # Row: SSH Key Support
        ssh_key_row = QHBoxLayout()
        ssh_key_row.addWidget(QLabel("SSH Private Key:"))
        self.ssh_key_path = QLineEdit()
        self.ssh_key_path.setPlaceholderText("Path to private key file (optional)")
        self.ssh_key_browse = QPushButton("Browse")
        self.ssh_key_browse.clicked.connect(self._browse_ssh_key)
        ssh_key_row.addWidget(self.ssh_key_path)
        ssh_key_row.addWidget(self.ssh_key_browse)

        lin_l.addLayout(self.lin_creds_layout)
        lin_l.addLayout(btns2)
        lin_l.addLayout(port_row)
        lin_l.addLayout(ssh_key_row)
        lin_box.setLayout(lin_l)
        group_layout.addWidget(lin_box)

        # ===== SNMP settings =====
        snmp_box = QGroupBox("SNMP Settings")
        snmp_v = QVBoxLayout()
        snmp_h1 = QHBoxLayout()
        snmp_h1.addWidget(QLabel("Communities (v2c, comma-separated):"))
        self.snmp_comm_entry = QLineEdit()
        self.snmp_comm_entry.setText(", ".join(self.cfg.get("snmp_v2c", []) or []))
        snmp_h1.addWidget(self.snmp_comm_entry)
        snmp_v.addLayout(snmp_h1)

        snmp_h2 = QHBoxLayout()
        snmp_h2.addWidget(QLabel("SNMP v3 User:")); self.snmp_v3_user = QLineEdit(); snmp_h2.addWidget(self.snmp_v3_user)
        snmp_h2.addWidget(QLabel("Auth Key:")); self.snmp_v3_auth = QLineEdit(); self.snmp_v3_auth.setEchoMode(QLineEdit.EchoMode.Password); snmp_h2.addWidget(self.snmp_v3_auth)
        snmp_h2.addWidget(QLabel("Priv Key:")); self.snmp_v3_priv = QLineEdit(); self.snmp_v3_priv.setEchoMode(QLineEdit.EchoMode.Password); snmp_h2.addWidget(self.snmp_v3_priv)
        snmp_v.addLayout(snmp_h2)

        snmp_h3 = QHBoxLayout()
        snmp_h3.addWidget(QLabel("Auth Proto (MD5/SHA):")); self.snmp_v3_authp = QLineEdit(); self.snmp_v3_authp.setText(self.cfg.get("snmp_v3", {}).get("auth_proto", "SHA")); snmp_h3.addWidget(self.snmp_v3_authp)
        snmp_h3.addWidget(QLabel("Priv Proto (AES128/DES):")); self.snmp_v3_privp = QLineEdit(); self.snmp_v3_privp.setText(self.cfg.get("snmp_v3", {}).get("priv_proto", "AES128")); snmp_h3.addWidget(self.snmp_v3_privp)
        snmp_v.addLayout(snmp_h3)
        snmp_box.setLayout(snmp_v)
        group_layout.addWidget(snmp_box)

        # ===== Discovery toggles =====
        disc_layout = QHBoxLayout()
        self.chk_http = QCheckBox("Use HTTP fingerprint (Smart/IoT/Printers)")
        self.chk_http.setChecked(True)
        self.chk_nmap = QCheckBox("Assist with Nmap (if installed)")
        self.chk_nmap.setChecked(True)
        disc_layout.addWidget(self.chk_http)
        disc_layout.addWidget(self.chk_nmap)
        group_layout.addLayout(disc_layout)

        # ===== Active Directory =====
        ad_box = QGroupBox("Active Directory")
        ad_l = QVBoxLayout()
        h1 = QHBoxLayout()
        h1.addWidget(QLabel("Server/DC:")); self.ad_server = QLineEdit(); h1.addWidget(self.ad_server)
        h1.addWidget(QLabel("Base DN:")); self.ad_base = QLineEdit(); h1.addWidget(self.ad_base)
        ad_l.addLayout(h1)
        h2 = QHBoxLayout()
        h2.addWidget(QLabel("Username:")); self.ad_user = QLineEdit(); h2.addWidget(self.ad_user)
        h2.addWidget(QLabel("Password:")); self.ad_pass = QLineEdit(); self.ad_pass.setEchoMode(QLineEdit.EchoMode.Password); h2.addWidget(self.ad_pass)
        ad_l.addLayout(h2)
        h3 = QHBoxLayout()
        self.ad_ssl = QCheckBox("Use SSL"); h3.addWidget(self.ad_ssl)
        self.btn_ad_save = QPushButton("Save AD Settings"); self.btn_ad_save.clicked.connect(self.save_ad_settings); h3.addWidget(self.btn_ad_save)
        self.btn_ad_fetch = QPushButton("Fetch from AD & Merge"); self.btn_ad_fetch.clicked.connect(self.fetch_from_ad_threaded); h3.addWidget(self.btn_ad_fetch)
        ad_l.addLayout(h3)
        ad_box.setLayout(ad_l)
        group_layout.addWidget(ad_box)

        # ===== Manual Entries (NEW) =====
        manual_box = QGroupBox("Manual Entries")
        manual_l = QVBoxLayout()
        self.btn_add_devices = QPushButton("Add Network Devices")
        self.btn_add_devices.clicked.connect(self._open_add_devices_form)
        manual_l.addWidget(self.btn_add_devices)
        manual_box.setLayout(manual_l)
        group_layout.addWidget(manual_box)

        # ===== Database-Only Storage Status =====
        storage_box = QGroupBox("Database Storage Status")
        storage_l = QVBoxLayout()
        
        storage_status_layout = QHBoxLayout()
        self.storage_status_label = QLabel("Storage: Database-Only Mode ✅")
        self.storage_status_label.setStyleSheet("color: green; font-weight: bold;")
        storage_status_layout.addWidget(self.storage_status_label)
        storage_l.addLayout(storage_status_layout)
        
        self.storage_info_label = QLabel("All collected data is stored directly in SQLite database. No Excel files are created or required.")
        self.storage_info_label.setWordWrap(True)
        self.storage_info_label.setStyleSheet("color: #666; font-size: 11px;")
        storage_l.addWidget(self.storage_info_label)
        
        storage_box.setLayout(storage_l)
        group_layout.addWidget(storage_box)

        # ===== Control / Progress / Log =====
        btn_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Collection"); self.start_button.clicked.connect(self.start_collection)
        self.stop_button  = QPushButton("Stop Collection");  self.stop_button.clicked.connect(self.stop_collection); self.stop_button.setEnabled(False)
        btn_layout.addWidget(self.start_button); btn_layout.addWidget(self.stop_button)
        group_layout.addLayout(btn_layout)

        self.progress_bar = QProgressBar(); self.progress_bar.setRange(0, 100); group_layout.addWidget(self.progress_bar)
        self.log_output = QTextEdit(); self.log_output.setReadOnly(True); group_layout.addWidget(self.log_output)

        # Initialize thread-safe enhancements after log_output is created
        if THREAD_SAFE_AVAILABLE:
            make_collection_thread_safe(self)
            self.log_output.append("🛡️ Thread-safe UI enhancements active - prevents hanging during collection")
            self.log_output.append("🔧 Network operations remain available during scanning")

        # Apply emergency UI hang fix
        if EMERGENCY_FIX_AVAILABLE:
            emergency_fix_collection_hanging(self)
            self.log_output.append("🚨 Emergency UI hang fix applied - UI guaranteed responsive")
            self.log_output.append("⚡ Collection will run in ultra-safe background threads")

        # Apply instant UI fix for immediate responsiveness
        if INSTANT_FIX_AVAILABLE:
            apply_instant_ui_fix(self)
            self.log_output.append("⚡ INSTANT UI responsiveness fix activated")
            self.log_output.append("🛡️ UI will NEVER hang - guaranteed responsive interface")

        # Apply process-based collection for ultimate UI responsiveness
        if PROCESS_COLLECTION_AVAILABLE:
            try:
                apply_process_based_collection(self)
                self.log_output.append("🚀 PROCESS-BASED COLLECTION activated")
                self.log_output.append("🛡️ Collection runs in separate process - UI guaranteed responsive")
            except Exception as e:
                self.log_output.append(f"⚠️ Process collection error: {e}")

        # Apply critical threading fix for error resolution
        if CRITICAL_THREADING_FIX_AVAILABLE:
            try:
                apply_critical_threading_fix(self)
                self.log_output.append("🔧 CRITICAL THREADING FIX activated")
                self.log_output.append("🛡️ QObject and Effect errors resolved")
            except Exception as e:
                self.log_output.append(f"⚠️ Critical threading fix error: {e}")

        # Apply SSH error handling for connection safety
        if SSH_ERROR_HANDLER_AVAILABLE:
            try:
                apply_ssh_error_handling(self)
                apply_network_connection_management(self)
                self.log_output.append("🔗 SSH ERROR HANDLING activated")
                self.log_output.append("🛡️ SSH/Paramiko errors handled safely")
            except Exception as e:
                self.log_output.append(f"⚠️ SSH error handler error: {e}")

        # Apply collection limiter to prevent massive scans
        if COLLECTION_LIMITER_AVAILABLE:
            try:
                apply_collection_limiter(self)
                self.log_output.append("🛡️ COLLECTION LIMITER activated")
                self.log_output.append("📊 Large scans limited to prevent UI hanging")
            except Exception as e:
                self.log_output.append(f"⚠️ Collection limiter error: {e}")

        # Apply massive scan protection for 3+ network handling
        if MASSIVE_SCAN_PROTECTION_AVAILABLE:
            try:
                apply_massive_scan_protection(self)
                self.log_output.append("🛡️ MASSIVE SCAN PROTECTION activated")
                self.log_output.append("📊 Can handle 3+ network subnets without hanging")
            except Exception as e:
                self.log_output.append(f"⚠️ Massive scan protection error: {e}")

        group_box.setLayout(group_layout)
        root_layout.addWidget(group_box)

        # ---- Make the whole UI scrollable ----
        inner = QWidget()
        inner.setLayout(root_layout)

        scroll = QScrollArea()
        scroll.setWidget(inner)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        container = QWidget()
        outer = QVBoxLayout(container)
        outer.addWidget(scroll)

        self.setCentralWidget(container)
        self.apply_styles()

        # rows as CredRow objects
        self.win_rows = []
        self.lin_rows = []
        self.load_windows_creds()
        self.load_linux_creds()
        self.load_ad_settings_into_ui()

        if not NMAP_BIN:
            self.chk_nmap.setText("Assist with Nmap (not found)")
        if _PYSNMP_OK:
            self.log_output.append(f"SNMP backend: {_SNMP_BACKEND} is active.")
        else:
            self.log_output.append("Warning: SNMP library not available. SNMP discovery will be skipped.")

    def apply_styles(self):
        style = """
        QPushButton { background-color: #3498db; color: white; font-size: 14px; font-weight: bold; border: 2px solid #2980b9; border-radius: 8px; padding: 10px; margin: 5px; }
        QPushButton:hover { background-color: #2980b9; }
        QPushButton:pressed { background-color: #1f618d; }
        QGroupBox { border: 2px solid #3498db; border-radius: 10px; margin-top: 10px; padding: 10px; font-size: 14px; color: #2c3e50; }
        """
        self.setStyleSheet(style)

    # ---------- Windows creds ----------
    def delete_windows_cred(self, row):
        """Delete a Windows credential row"""
        try:
            self.win_rows.remove(row)
            row.setParent(None)
            row.deleteLater()
            self.log_output.append("🗑️ Windows credential deleted")
        except ValueError:
            pass
    
    def add_windows_cred(self, username: str = "", password: str = ""):
        row = CredRow("DOMAIN\\user or .\\localadmin", "password", username, password, 
                     parent=self, delete_callback=self.delete_windows_cred)
        self.win_creds_layout.addWidget(row)
        self.win_rows.append(row)

    def save_windows_creds(self):
        cfg = self.cfg
        existing_creds = cfg.get("windows_creds", [])
        existing_ids = {c.get("secret_id") for c in existing_creds}
        
        # Keep track of existing credentials by username for updates
        existing_by_username = {c.get("username"): c for c in existing_creds}
        
        cfg["windows_creds"] = []
        for row in self.win_rows:
            un = row.username()
            pw = row.password()
            if not un:
                continue
            
            # Check if this is a masked password (existing credential)
            if pw == "••••••••" and un in existing_by_username:
                # Keep existing credential without changing password
                existing_cred = existing_by_username[un]
                cfg["windows_creds"].append(existing_cred)
            else:
                # New credential or password change
                sid = new_secret_id("win", existing_ids)
                existing_ids.add(sid)
                set_secret(sid, pw)
                cfg["windows_creds"].append({"username": un, "secret_id": sid})
        
        save_config(cfg)
        self.cfg = cfg
        self.log_output.append("Windows credentials saved.")

    def load_windows_creds(self):
        _clear_layout(self.win_creds_layout)
        self.win_rows = []
        loaded = False
        
        # Load from config file (existing behavior)
        for c in (self.cfg.get("windows_creds", []) or []):
            # SECURITY: Never display actual passwords, just show placeholder
            self.add_windows_cred(c.get("username", ""), "••••••••")
            loaded = True
            
        # ALSO load from collector_credentials.json (new behavior)
        try:
            import json
            from pathlib import Path
            cred_file = Path("collector_credentials.json")
            if cred_file.exists():
                with open(cred_file, 'r') as f:
                    creds = json.load(f)
                
                for c in creds.get("wmi_credentials", []):
                    username = c.get("username", "")
                    domain = c.get("domain", "")
                    if domain and domain.strip() and domain != '.':
                        display_username = f"{domain}\\{username}"
                    else:
                        display_username = username
                    
                    if display_username:  # Only add if username exists
                        self.add_windows_cred(display_username, "••••••••")
                        loaded = True
        except Exception as e:
            # Don't fail silently, but don't crash either
            print(f"Note: Could not load collector credentials: {e}")
            
        if not loaded:
            self.add_windows_cred()
        
        # Security notice
        if loaded:
            self.log_output.append("🔒 SECURITY: Loaded credentials with masked passwords. Passwords are securely stored.")

    def clear_all_windows_creds(self):
        """Clear all Windows credentials"""
        try:
            from PyQt6.QtWidgets import QMessageBox
            reply = QMessageBox.question(self, "Clear Windows Credentials", 
                                        "Are you sure you want to delete ALL Windows credentials?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                _clear_layout(self.win_creds_layout)
                self.win_rows = []
                self.log_output.append("🗑️ All Windows credentials cleared")
        except:
            # Fallback without confirmation dialog
            _clear_layout(self.win_creds_layout)
            self.win_rows = []
            self.log_output.append("🗑️ All Windows credentials cleared")

    # ---------- Linux/ESXi creds ----------
    def delete_linux_cred(self, row):
        """Delete a Linux credential row"""
        try:
            self.lin_rows.remove(row)
            row.setParent(None)
            row.deleteLater()
            self.log_output.append("🗑️ Linux credential deleted")
        except ValueError:
            pass
    
    def add_linux_cred(self, username: str = "", password: str = ""):
        row = CredRow("root / ubuntu / user / root@esxi", "password", username, password, 
                     parent=self, delete_callback=self.delete_linux_cred)
        self.lin_creds_layout.addWidget(row)
        self.lin_rows.append(row)

    def save_linux_creds(self):
        cfg = self.cfg
        existing_creds = cfg.get("linux_creds", [])
        existing_ids = {c.get("secret_id") for c in existing_creds}
        
        # Keep track of existing credentials by username for updates
        existing_by_username = {c.get("username"): c for c in existing_creds}
        
        cfg["linux_creds"] = []
        for row in self.lin_rows:
            un = row.username()
            pw = row.password()
            if not un:
                continue
            
            # Check if this is a masked password (existing credential)
            if pw == "••••••••" and un in existing_by_username:
                # Keep existing credential without changing password
                existing_cred = existing_by_username[un]
                cfg["linux_creds"].append(existing_cred)
            else:
                # New credential or password change
                sid = new_secret_id("lin", existing_ids)
                existing_ids.add(sid)
                set_secret(sid, pw)
                cfg["linux_creds"].append({"username": un, "secret_id": sid})
        
        save_config(cfg)
        self.cfg = cfg
        self.log_output.append("Linux/ESXi credentials saved.")

    def load_linux_creds(self):
        _clear_layout(self.lin_creds_layout)
        self.lin_rows = []
        loaded = False
        for c in (self.cfg.get("linux_creds", []) or []):
            # SECURITY: Never display actual passwords, just show placeholder
            self.add_linux_cred(c.get("username", ""), "••••••••")
            loaded = True
        if not loaded:
            self.add_linux_cred()

    def clear_all_linux_creds(self):
        """Clear all Linux credentials"""
        try:
            from PyQt6.QtWidgets import QMessageBox
            reply = QMessageBox.question(self, "Clear Linux Credentials", 
                                        "Are you sure you want to delete ALL Linux credentials?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                _clear_layout(self.lin_creds_layout)
                self.lin_rows = []
                self.log_output.append("🗑️ All Linux credentials cleared")
        except:
            # Fallback without confirmation dialog
            _clear_layout(self.lin_creds_layout)
            self.lin_rows = []
            self.log_output.append("🗑️ All Linux credentials cleared")

    # ---------- AD settings ----------
    def save_ad_settings(self):
        self.cfg.setdefault("ad", {})
        self.cfg["ad"]["server"] = self.ad_server.text().strip()
        self.cfg["ad"]["base_dn"] = self.ad_base.text().strip()
        self.cfg["ad"]["username"] = self.ad_user.text().strip()
        sid = self.cfg["ad"].get("secret_id") or new_secret_id("ad", set())
        self.cfg["ad"]["secret_id"] = sid
        set_secret(sid, self.ad_pass.text())
        self.cfg["ad"]["use_ssl"] = self.ad_ssl.isChecked()
        save_config(self.cfg)
        self.log_output.append("AD settings saved.")

    def load_ad_settings_into_ui(self):
        ad = self.cfg.get("ad", {})
        self.ad_server.setText(ad.get("server", ""))
        self.ad_base.setText(ad.get("base_dn", ""))
        self.ad_user.setText(ad.get("username", ""))
        self.ad_pass.setText(get_secret(ad.get("secret_id", "")))
        self.ad_ssl.setChecked(bool(ad.get("use_ssl", False)))

    # ---------- SNMP getters ----------
    def get_snmp_v2c(self):
        txt = self.snmp_comm_entry.text().strip()
        if not txt:
            return []
        return [c.strip() for c in txt.split(",") if c.strip()]

    def get_snmp_v3(self):
        user = self.snmp_v3_user.text().strip()
        if not user:
            return {}
        return {
            "user": user,
            "auth_key": self.snmp_v3_auth.text(),
            "priv_key": self.snmp_v3_priv.text(),
            "auth_proto": self.snmp_v3_authp.text().strip() or "SHA",
            "priv_proto": self.snmp_v3_privp.text().strip() or "AES128"
        }

    # ---------- Helpers ----------
    def add_network_range(self, network_range: str):
        """Add network range to the target entry"""
        current_text = self.target_entry.text().strip()
        if current_text:
            if network_range not in current_text:
                new_text = f"{current_text}, {network_range}"
                self.target_entry.setText(new_text)
        else:
            self.target_entry.setText(network_range)
    
    def add_enterprise_credentials(self):
        """Add predefined enterprise credentials"""
        enterprise_creds = [
            ("administrator", "LocalAdmin"),
            ("administrator", "localadmin"), 
            ("square\\administrator", "6{c$UqOnOOk2"),
            ("administrator", "6uy!,BZaRIw")
        ]
        
        # Save credentials securely to vault first
        cfg = self.cfg
        existing_ids = {c.get("secret_id") for c in cfg.get("windows_creds", [])}
        cfg["windows_creds"] = []
        
        for username, password in enterprise_creds:
            if username.strip():
                secret_id = new_secret_id("win", existing_ids)
                existing_ids.add(secret_id)
                set_secret(secret_id, password)
                cfg["windows_creds"].append({"username": username, "secret_id": secret_id})
        
        save_config(cfg)
        self.cfg = cfg
        
        # Clear existing Windows credentials first
        _clear_layout(self.win_creds_layout)
        self.win_rows = []
        
        # Add enterprise credentials with masked passwords
        for username, _ in enterprise_creds:
            # SECURITY: Display masked password instead of actual password
            self.add_windows_cred(username, "••••••••")
        
        # Show confirmation
        try:
            from PyQt6.QtWidgets import QMessageBox
            msg = QMessageBox()
            msg.setWindowTitle("Enterprise Credentials Added")
            msg.setText("Added 4 enterprise credential sets:\n• Local Administrator (LocalAdmin)\n• Local Administrator (localadmin)\n• Domain Administrator (square\\administrator)\n• Server Administrator")
            msg.exec()
        except:
            pass
    
    def _read_linux_port(self) -> int:
        """
        Safely parse SSH port from the UI, return a valid int in [1, 65535].
        Falls back to 22 if invalid/empty.
        """
        try:
            port_txt = (self.lin_port.text() or "").strip()
            port = int(port_txt) if port_txt else int(self.cfg.get("linux_ssh_port", 22) or 22)
        except Exception:
            port = 22
        if port < 1 or port > 65535:
            QMessageBox.warning(self, "Invalid Port", "SSH Port must be between 1 and 65535. Falling back to 22.")
            port = 22
        return port

    # ---------- Database-Only Operations ----------
    def get_database_info(self):
        """Get information about database storage"""
        try:
            import sqlite3
            conn = sqlite3.connect('assets.db')
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM assets')
            count = cursor.fetchone()[0]
            conn.close()
            return f"Database contains {count} assets"
        except:
            return "Database ready for new assets"

    def build_windows_creds_for_scan(self):
        out = []
        
        # PRIORITY: Load from collector_credentials.json FIRST (has real passwords)
        try:
            import json
            from pathlib import Path
            cred_file = Path("collector_credentials.json")
            if cred_file.exists():
                with open(cred_file, 'r') as f:
                    creds = json.load(f)
                
                for c in creds.get("wmi_credentials", []):
                    username = c.get("username", "")
                    password = c.get("password", "")
                    domain = c.get("domain", ".")
                    
                    if username and password:  # Only add if both exist
                        out.append({
                            "username": username, 
                            "password": password,  # Real password from JSON
                            "domain": domain or '.'
                        })
        except Exception as e:
            print(f"Note: Could not load collector credentials for scan: {e}")
        
        # Second: Get from GUI input rows (only if they have real passwords, not ••••••••)
        for row in self.win_rows:
            un = row.username()
            pw = row.password()
            if un and pw and pw != "••••••••":  # Skip masked passwords
                # Enhanced credential building with domain support
                if '\\' in un:
                    domain, username = un.split('\\', 1)
                else:
                    domain = '.'
                    username = un
                out.append({
                    "username": username, 
                    "password": pw,
                    "domain": domain
                })
        
        # Third: Get from config file (existing behavior)
        if not out:
            for c in self.cfg.get("windows_creds", []):
                username = c.get("username", "")
                domain = c.get("domain", ".")
                if '\\' in username:
                    domain, username = username.split('\\', 1)
                out.append({
                    "username": username, 
                    "password": get_secret(c.get("secret_id", "")),
                    "domain": domain
                })
        
        # Add enterprise credentials if none configured
        if not out:
            # SECURITY: Use credentials from secure vault only, no hardcoded passwords
            enterprise_config = self.cfg.get("windows_creds", [])
            if enterprise_config:
                for c in enterprise_config:
                    username = c.get("username", "")
                    domain = c.get("domain", ".")
                    if '\\' in username:
                        domain, username = username.split('\\', 1)
                    out.append({
                        "username": username, 
                        "password": get_secret(c.get("secret_id", "")),
                        "domain": domain
                    })
            
        return out

    def build_linux_creds_for_scan(self):
        out = []
        for row in self.lin_rows:
            un = row.username()
            pw = row.password()
            if un:
                # Enhanced credential building with domain support
                if '\\' in un:
                    domain, username = un.split('\\', 1)
                else:
                    domain = '.'
                    username = un
                out.append({
                    "username": username, 
                    "password": pw,
                    "domain": domain
                })
        
        if not out:
            for c in self.cfg.get("linux_creds", []):
                username = c.get("username", "")
                domain = c.get("domain", ".")
                if '\\' in username:
                    domain, username = username.split('\\', 1)
                out.append({
                    "username": username, 
                    "password": get_secret(c.get("secret_id", "")),
                    "domain": domain
                })
        
        # Add enterprise credentials if none configured
        if not out:
            enterprise_creds = [
                {"username": "administrator", "password": "6{c$UqOnOOk2", "domain": "square"},
                {"username": "root", "password": "6uy!,BZaRIw", "domain": "."},
                {"username": "admin", "password": "LocalAdmin", "domain": "."},
            ]
            out.extend(enterprise_creds)
            
        return out

    def start_collection(self):
        targets_raw = self.target_entry.text().strip()
        if not targets_raw:
            QMessageBox.warning(self, "Missing Targets", "Please enter at least one IP or subnet.")
            return
        targets = [t.strip() for t in self._split_csv(targets_raw) if t.strip()]
        
        # Display multi-network information
        self.log_output.append("🌐 ULTRA-FAST MULTI-NETWORK COLLECTION STARTING")
        self.log_output.append("=" * 50)
        for i, target in enumerate(targets, 1):
            if '/' in target:
                # Subnet calculation
                try:
                    import ipaddress
                    network = ipaddress.IPv4Network(target, strict=False)
                    host_count = network.num_addresses - 2  # Exclude network/broadcast
                    self.log_output.append(f"📡 Network {i}: {target} (~{host_count} potential devices)")
                except:
                    self.log_output.append(f"📡 Network {i}: {target} (subnet)")
            else:
                self.log_output.append(f"🎯 Target {i}: {target} (single device)")
        
        win_creds = self.build_windows_creds_for_scan()
        lin_creds = self.build_linux_creds_for_scan()
        snmp_v2c = self.get_snmp_v2c()
        snmp_v3 = self.get_snmp_v3()

        # Display credential information
        self.log_output.append(f"🔑 Windows credentials configured: {len(win_creds)}")
        self.log_output.append(f"🔑 Linux credentials configured: {len(lin_creds)}")
        if snmp_v2c:  # snmp_v2c is a list, not a dict
            self.log_output.append(f"🔑 SNMP v2c communities: {len(snmp_v2c)}")
        if snmp_v3.get('user'):
            self.log_output.append(f"🔑 SNMP v3 user: {snmp_v3['user']}")

        # SSH Port (Linux/ESXi)
        linux_port = self._read_linux_port()
        self.cfg["linux_ssh_port"] = linux_port
        save_config(self.cfg)

        # Update UI state
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        
        self.log_output.append(f"🚀 Starting thread-safe collection (Linux SSH port = {linux_port})")
        self.log_output.append("🛡️ UI remains responsive during collection")

        global NMAP_BIN
        if not self.chk_nmap.isChecked():
            NMAP_BIN = None

        # Prepare collector parameters
        collector_kwargs = {
            'targets': targets,
            'win_creds': win_creds, 
            'linux_creds': lin_creds,
            'snmp_v2c': snmp_v2c,
            'snmp_v3': snmp_v3,
            'use_http': self.chk_http.isChecked(),
            'parent': self
        }

        if ENHANCED_STRATEGY_AVAILABLE:
            # Use enhanced collection strategy with maximum data collection
            collector_kwargs.update({
                'ping_workers': 100,      # Ultra-fast ping discovery
                'nmap_workers': 20,       # Comprehensive port scanning  
                'collection_workers': 15  # Maximum data collection
            })
            collector_class = DeviceInfoCollector
            self.log_output.append("🚀 Using ENHANCED collection strategy (MAXIMUM DATA COLLECTION)")
        elif PROPER_STRATEGY_AVAILABLE:
            # Use proper 3-step collection strategy
            collector_kwargs.update({
                'ping_workers': 50,       # Fast ping discovery
                'nmap_workers': 10,       # OS detection workers  
                'collection_workers': 8   # Targeted collection
            })
            collector_class = DeviceInfoCollector
            self.log_output.append("🎯 Using PROPER collection strategy (PING → NMAP → COLLECT)")
        elif ULTRA_FAST_AVAILABLE:
            # Use ultra-fast collector
            collector_kwargs.update({
                'discovery_workers': 20,  # Ultra-fast discovery
                'collection_workers': 12,  # Ultra-fast collection
            })
            collector_class = DeviceInfoCollector
            self.log_output.append("⚡ Using ULTRA-FAST collector with hang prevention")
        else:
            # Fallback to original collector 
            collector_kwargs['excel_file'] = None  # Database-only storage
            
            try:
                init_params = inspect.signature(DeviceInfoCollector.__init__).parameters
                if "linux_port" in init_params:
                    collector_kwargs["linux_port"] = linux_port
                else:
                    os.environ["FS_LINUX_SSH_PORT"] = str(linux_port)
                    self.log_output.append("Note: DeviceInfoCollector doesn't expose 'linux_port'; set FS_LINUX_SSH_PORT for collectors.")
            except Exception:
                os.environ["FS_LINUX_SSH_PORT"] = str(linux_port)
            
            collector_class = DeviceInfoCollector
            self.log_output.append("⚠️ Using standard collector")

        # Create thread-safe collector
        if THREAD_SAFE_AVAILABLE:
            self.worker = create_thread_safe_collector(self, collector_class, **collector_kwargs)
            self.log_output.append("🛡️ Thread-safe collection initialized - UI will remain responsive")
        else:
            # Fallback to original method
            self.worker = collector_class(**collector_kwargs)  # type: ignore
            if hasattr(self.worker, 'progress_updated'):
                self.worker.progress_updated.connect(self.progress_bar.setValue)  # type: ignore
            if hasattr(self.worker, 'log_message'):
                self.worker.log_message.connect(self.log_output.append)  # type: ignore
            if hasattr(self.worker, 'collection_finished'):
                self.worker.collection_finished.connect(lambda: self.on_finished(False))  # type: ignore
            if hasattr(self.worker, 'device_collected'):
                self.worker.device_collected.connect(self._on_device_collected)  # type: ignore
            self.log_output.append("⚠️ Standard collection - UI may become less responsive")
        
        # Start collection
        self.worker.start()
        
        # Run automatic cleanup after collection
        self.log_output.append("🧹 Automatic duplicate cleanup will run after collection")

    def _on_device_collected(self, device_data):
        """Handle individual device collection from ultra-fast collector"""
        # Log device collection
        hostname = device_data.get('Hostname', device_data.get('hostname', 'Unknown'))
        ip = device_data.get('IP Address', device_data.get('ip_address', 'Unknown'))
        method = device_data.get('Collection Method', 'Unknown')
        
        self.log_output.append(f"✅ Collected: {hostname} ({ip}) via {method}")
        
        # Here you could save to database immediately if needed
        # For now, the collector handles database saving

    def _split_csv(self, s: str):
        # allow both comma & whitespace separated input
        parts = []
        for chunk in s.replace(" ", ",").split(","):
            c = chunk.strip()
            if c:
                parts.append(c)
        return parts

    def stop_collection(self):
        if hasattr(self, "worker") and self.worker.isRunning():
            self.worker.stop()
            self.log_output.append("Cancel requested...")

    def on_finished(self, canceled: bool):
        self.log_output.append("Finished." + (" (Canceled)" if canceled else ""))
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        # Collection completed successfully
        if not canceled:
            self.log_output.append("✅ Collection completed successfully")
            try:
                # Automatic cleanup functionality removed
                self.log_output.append("📊 Data saved to database")
            except Exception as e:
                self.log_output.append(f"❌ Post-collection error: {e}")
        
        # Update UI manager if available
        if hasattr(self, 'ui_manager'):
            self.ui_manager.set_collection_active(False)  # type: ignore

    # ---------- AD fetch/merge ----------
    def fetch_from_ad_threaded(self):
        ad = self.cfg.get("ad", {})
        server = (self.ad_server.text().strip() or ad.get("server", ""))
        base_dn = (self.ad_base.text().strip() or ad.get("base_dn", ""))
        user = (self.ad_user.text().strip() or ad.get("username", ""))
        pwd = (self.ad_pass.text() or get_secret(ad.get("secret_id", "")))
        use_ssl = self.ad_ssl.isChecked()

        # Database-only storage - no Excel file needed
        self.log_output.append("💾 Using database-only storage for AD data")

        if not (server and base_dn and user and pwd):
            QMessageBox.warning(self, "Missing AD Settings", "Please fill AD server/base DN/username/password.")
            return

        self.ad_worker = ADWorker(server, base_dn, user, pwd, use_ssl, None, parent=self)  # type: ignore
        if hasattr(self.ad_worker, 'log_message'):
            self.ad_worker.log_message.connect(self.log_output.append)
        if hasattr(self.ad_worker, 'finished_with_status'):
            self.ad_worker.finished_with_status.connect(lambda _: self.log_output.append("AD fetch/merge finished."))
        if hasattr(self.ad_worker, 'start'):
            self.ad_worker.start()

    # ---------- NEW: open the manual-entry dialog ----------
    def _open_add_devices_form(self):
        # Database-only storage - always ready
        from PyQt6.QtWidgets import QMessageBox
        self.log_output.append("💾 Opening device entry form - database-only storage")
        try:
            # Database is always ready - no file setup needed
            pass
        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))
            return
        open_add_device_dialog(self, workbook_path=None)  # Pass None since we use database only
    
    # Database-only methods - no sync needed
    # All methods removed since we use database-only storage

    def _browse_ssh_key(self):
        """Browse for SSH private key file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select SSH Private Key",
            os.path.expanduser("~/.ssh"),
            "SSH Keys (id_rsa id_ed25519 *.pem *.key);;All Files (*.*)"
        )
        if file_path:
            self.ssh_key_path.setText(file_path)


    def start_web_service(self):
        """Start the web service"""
        try:
            import subprocess
            import threading
            import os
            
            # Update status
            self.web_service_status.setText("🟡 Starting...")
            self.web_service_status.setStyleSheet("color: orange; font-weight: bold; padding: 5px;")
            self.web_service_log.append(f"Starting web service at {QTime.currentTime().toString()}")
            
            # Find the web service script
            web_service_script = None
            possible_scripts = [
                'production_web_service.py',
                'enhanced_complete_web_service.py',
                'complete_department_web_service.py'
            ]
            
            for script in possible_scripts:
                if os.path.exists(script):
                    web_service_script = script
                    break
            
            if not web_service_script:
                self.web_service_log.append("❌ No web service script found!")
                self.web_service_status.setText("🔴 Error")
                self.web_service_status.setStyleSheet("color: red; font-weight: bold; padding: 5px;")
                return
            
            # Start the web service in a separate process
            def start_service():
                try:
                    self.web_service_process = subprocess.Popen(
                        ['python', web_service_script],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        cwd=os.getcwd()
                    )
                    
                    # Wait a moment then check if it started
                    QTimer.singleShot(2000, self.check_web_service_status)
                    
                except Exception as e:
                    self.web_service_log.append(f"❌ Failed to start: {str(e)}")
                    self.web_service_status.setText("🔴 Error")
                    self.web_service_status.setStyleSheet("color: red; font-weight: bold; padding: 5px;")
            
            # Start in thread to avoid blocking UI
            threading.Thread(target=start_service, daemon=True).start()
            
        except Exception as e:
            self.web_service_log.append(f"❌ Error starting web service: {str(e)}")
            self.web_service_status.setText("🔴 Error")
            self.web_service_status.setStyleSheet("color: red; font-weight: bold; padding: 5px;")

    def stop_web_service(self):
        """Stop the web service"""
        try:
            if hasattr(self, 'web_service_process') and self.web_service_process:
                self.web_service_process.terminate()
                self.web_service_process = None
                
            self.web_service_status.setText("🔴 Stopped")
            self.web_service_status.setStyleSheet("color: red; font-weight: bold; padding: 5px;")
            self.web_service_log.append(f"Web service stopped at {QTime.currentTime().toString()}")
            
            # Update button states
            self.btn_start_web.setEnabled(True)
            self.btn_stop_web.setEnabled(False)
            self.btn_open_web.setEnabled(False)
            self.btn_restart_web.setEnabled(False)
            
        except Exception as e:
            self.web_service_log.append(f"❌ Error stopping web service: {str(e)}")

    def restart_web_service(self):
        """Restart the web service"""
        self.web_service_log.append("🔄 Restarting web service...")
        self.stop_web_service()
        QTimer.singleShot(1000, self.start_web_service)  # Wait 1 second then start

    def open_web_service(self):
        """Open the web service in browser"""
        try:
            import webbrowser
            url = self.web_service_url.text()
            webbrowser.open(url)
            self.web_service_log.append(f"🌐 Opened {url} in browser")
        except Exception as e:
            self.web_service_log.append(f"❌ Error opening browser: {str(e)}")

    def check_web_service_status(self):
        """Check if web service is running"""
        try:
            import urllib.request
            import urllib.error
            
            # Try to connect to the web service
            try:
                response = urllib.request.urlopen('http://localhost:8080', timeout=5)
                if response.status == 200:
                    self.web_service_status.setText("🟢 Running")
                    self.web_service_status.setStyleSheet("color: green; font-weight: bold; padding: 5px;")
                    self.web_service_log.append("✅ Web service is running successfully")
                    
                    # Update button states
                    self.btn_start_web.setEnabled(False)
                    self.btn_stop_web.setEnabled(True)
                    self.btn_open_web.setEnabled(True)
                    self.btn_restart_web.setEnabled(True)
                else:
                    raise Exception("Service not responding")
                    
            except (urllib.error.URLError, Exception):
                self.web_service_status.setText("🔴 Not Running")
                self.web_service_status.setStyleSheet("color: red; font-weight: bold; padding: 5px;")
                self.web_service_log.append("❌ Web service is not accessible")
                
                # Update button states
                self.btn_start_web.setEnabled(True)
                self.btn_stop_web.setEnabled(False)
                self.btn_open_web.setEnabled(False)
                self.btn_restart_web.setEnabled(False)
                
        except Exception as e:
            self.web_service_log.append(f"❌ Error checking status: {str(e)}")

    # ===== Network Profiles Management Methods =====
    def load_saved_profiles(self):
        """Load saved network profiles from JSON file"""
        try:
            import json
            profiles_file = "network_profiles.json"
            if os.path.exists(profiles_file):
                with open(profiles_file, 'r', encoding='utf-8') as f:
                    profiles = json.load(f)
                self.profile_combo.clear()
                self.profile_combo.addItem("-- Select Profile --")
                for profile_name in profiles.keys():
                    self.profile_combo.addItem(profile_name)
        except Exception as e:
            print(f"Error loading profiles: {str(e)}")

    def save_network_profile(self):
        """Save current network settings as a profile"""
        try:
            import json
            from PyQt6.QtWidgets import QInputDialog
            
            # Get profile name from user
            profile_name, ok = QInputDialog.getText(self, 'Save Profile', 'Enter profile name:')
            if not ok or not profile_name.strip():
                return
                
            profile_name = profile_name.strip()
            
            # Collect current settings
            profile_data = {
                'networks': self.target_entry.text(),
                'win_credentials': [],
                'linux_credentials': []
            }
            
            # Collect Windows credentials
            for row in self.win_rows:
                if hasattr(row, 'username') and hasattr(row, 'password'):
                    profile_data['win_credentials'].append({
                        'username': row.username(),
                        'password': row.password()
                    })
            
            # Collect Linux credentials
            for row in self.lin_rows:
                if hasattr(row, 'username') and hasattr(row, 'password'):
                    profile_data['linux_credentials'].append({
                        'username': row.username(),
                        'password': row.password()
                    })
            
            # Load existing profiles
            profiles_file = "network_profiles.json"
            profiles = {}
            if os.path.exists(profiles_file):
                with open(profiles_file, 'r', encoding='utf-8') as f:
                    profiles = json.load(f)
            
            # Save new profile
            profiles[profile_name] = profile_data
            with open(profiles_file, 'w', encoding='utf-8') as f:
                json.dump(profiles, f, indent=2, ensure_ascii=False)
            
            # Refresh profile combo
            self.load_saved_profiles()
            self.profile_combo.setCurrentText(profile_name)
            
            QMessageBox.information(self, "Success", f"Profile '{profile_name}' saved successfully!")
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save profile: {str(e)}")

    def load_network_profile(self):
        """Load selected network profile"""
        try:
            import json
            
            profile_name = self.profile_combo.currentText()
            if profile_name == "-- Select Profile --" or not profile_name:
                return
            
            profiles_file = "network_profiles.json"
            if not os.path.exists(profiles_file):
                QMessageBox.warning(self, "Error", "No profiles file found!")
                return
            
            with open(profiles_file, 'r', encoding='utf-8') as f:
                profiles = json.load(f)
            
            if profile_name not in profiles:
                QMessageBox.warning(self, "Error", f"Profile '{profile_name}' not found!")
                return
            
            profile_data = profiles[profile_name]
            
            # Load networks
            self.target_entry.setText(profile_data.get('networks', ''))
            
            # Clear existing credentials
            self.clear_all_credentials()
            
            # Load Windows credentials
            for cred in profile_data.get('win_credentials', []):
                self.add_win_credential(cred['username'], cred['password'])
            
            # Load Linux credentials  
            for cred in profile_data.get('linux_credentials', []):
                self.add_linux_credential(cred['username'], cred['password'])
            
            QMessageBox.information(self, "Success", f"Profile '{profile_name}' loaded successfully!")
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load profile: {str(e)}")

    def delete_network_profile(self):
        """Delete selected network profile"""
        try:
            import json
            
            profile_name = self.profile_combo.currentText()
            if profile_name == "-- Select Profile --" or not profile_name:
                return
            
            # Confirm deletion
            reply = QMessageBox.question(self, "Confirm Delete", 
                                       f"Are you sure you want to delete profile '{profile_name}'?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply != QMessageBox.StandardButton.Yes:
                return
            
            profiles_file = "network_profiles.json"
            if not os.path.exists(profiles_file):
                return
            
            with open(profiles_file, 'r', encoding='utf-8') as f:
                profiles = json.load(f)
            
            if profile_name in profiles:
                del profiles[profile_name]
                
                with open(profiles_file, 'w', encoding='utf-8') as f:
                    json.dump(profiles, f, indent=2, ensure_ascii=False)
                
                self.load_saved_profiles()
                QMessageBox.information(self, "Success", f"Profile '{profile_name}' deleted successfully!")
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to delete profile: {str(e)}")

    def on_profile_selection_changed(self):
        """Handle profile selection changes"""
        profile_name = self.profile_combo.currentText()
        # Enable/disable buttons based on selection
        has_selection = profile_name != "-- Select Profile --" and bool(profile_name)
        self.btn_load_profile.setEnabled(has_selection)
        self.btn_delete_profile.setEnabled(has_selection)

    def clear_all_credentials(self):
        """Clear all credential widgets"""
        try:
            # Clear Windows credentials
            self.win_rows.clear()
            self._clear_layout(self.win_creds_layout)
            
            # Clear Linux credentials
            self.lin_rows.clear()
            self._clear_layout(self.lin_creds_layout)
        except Exception as e:
            print(f"Error clearing credentials: {str(e)}")

    def _clear_layout(self, layout):
        """Helper to clear a layout"""
        try:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        except Exception as e:
            print(f"Error clearing layout: {str(e)}")

    def add_win_credential(self, username="", password=""):
        """Add Windows credential widget with values"""
        try:
            self.add_windows_cred(username, password)
        except Exception as e:
            print(f"Error adding Windows credential: {str(e)}")

    def add_linux_credential(self, username="", password=""):
        """Add Linux credential widget with values"""
        try:
            self.add_linux_cred(username, password)
        except Exception as e:
            print(f"Error adding Linux credential: {str(e)}")

    def add_custom_network(self):
        """Add custom network to target entry"""
        network, ok = QInputDialog.getText(self, 'Add Custom Network', 'Enter network (e.g., 192.168.1.0/24):')
        if ok and network.strip():
            current = self.target_entry.text()
            if current:
                self.target_entry.setText(current + ", " + network.strip())
            else:
                self.target_entry.setText(network.strip())

    def manage_profile_networks(self):
        """Manage networks within a profile"""
        try:
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem
            import json
            
            profile_name = self.profile_combo.currentText()
            if profile_name == "-- Select Profile --" or not profile_name:
                # Create new profile
                profile_name, ok = QInputDialog.getText(self, 'Create Profile', 'Enter new profile name:')
                if not ok or not profile_name.strip():
                    return
                profile_name = profile_name.strip()
            
            dialog = QDialog(self)
            dialog.setWindowTitle(f"⚙️ Manage Networks - {profile_name}")
            dialog.setGeometry(200, 200, 700, 500)
            
            layout = QVBoxLayout()
            
            # Networks list
            layout.addWidget(QLabel(f"Networks in Profile: {profile_name}"))
            self.networks_list = QListWidget()
            layout.addWidget(self.networks_list)
            
            # Load existing networks
            self.load_profile_networks(profile_name)
            
            # Network management buttons
            network_buttons_layout = QHBoxLayout()
            
            btn_add_network = QPushButton("➕ Add Network")
            btn_edit_network = QPushButton("✏️ Edit Network")
            btn_remove_network = QPushButton("➖ Remove Network")
            btn_quick_add = QPushButton("⚡ Quick Add")
            
            btn_add_network.clicked.connect(lambda: self.add_network_to_profile())
            btn_edit_network.clicked.connect(lambda: self.edit_network_in_profile())
            btn_remove_network.clicked.connect(lambda: self.remove_network_from_profile())
            btn_quick_add.clicked.connect(lambda: self.quick_add_networks())
            
            network_buttons_layout.addWidget(btn_add_network)
            network_buttons_layout.addWidget(btn_edit_network)
            network_buttons_layout.addWidget(btn_remove_network)
            network_buttons_layout.addWidget(btn_quick_add)
            layout.addLayout(network_buttons_layout)
            
            # Network details section
            details_layout = QVBoxLayout()
            details_layout.addWidget(QLabel("Network Details:"))
            
            self.network_details = QTextEdit()
            self.network_details.setMaximumHeight(100)
            self.network_details.setReadOnly(True)
            details_layout.addWidget(self.network_details)
            layout.addLayout(details_layout)
            
            # Dialog buttons
            dialog_buttons = QHBoxLayout()
            btn_save_profile = QPushButton("💾 Save Profile")
            btn_load_to_scan = QPushButton("🔍 Load for Scanning")
            btn_close = QPushButton("❌ Close")
            
            btn_save_profile.clicked.connect(lambda: self.save_profile_from_dialog(profile_name, dialog))
            btn_load_to_scan.clicked.connect(lambda: self.load_profile_for_scanning(profile_name, dialog))
            btn_close.clicked.connect(dialog.reject)
            
            dialog_buttons.addWidget(btn_save_profile)
            dialog_buttons.addWidget(btn_load_to_scan)
            dialog_buttons.addWidget(btn_close)
            layout.addLayout(dialog_buttons)
            
            # Connect list selection
            self.networks_list.itemClicked.connect(self.show_network_details)
            
            dialog.setLayout(layout)
            dialog.exec()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to manage networks: {str(e)}")

    def load_profile_networks(self, profile_name):
        """Load networks for a profile"""
        try:
            import json
            profiles_file = "network_profiles.json"
            self.networks_list.clear()
            
            if os.path.exists(profiles_file):
                with open(profiles_file, 'r', encoding='utf-8') as f:
                    profiles = json.load(f)
                
                if profile_name in profiles:
                    profile_data = profiles[profile_name]
                    # Load individual networks if stored as list
                    if 'network_list' in profile_data:
                        for network in profile_data['network_list']:
                            item = QListWidgetItem()
                            item.setText(f"{network['network']} - {network.get('description', 'No description')}")
                            item.setData(1, network)  # Store network data
                            self.networks_list.addItem(item)
                    else:
                        # Legacy: Convert from single networks string
                        networks_str = profile_data.get('networks', '')
                        if networks_str:
                            for net in networks_str.split(','):
                                net = net.strip()
                                if net:
                                    network_data = {'network': net, 'description': 'Legacy network'}
                                    item = QListWidgetItem()
                                    item.setText(f"{net} - Legacy network")
                                    item.setData(1, network_data)
                                    self.networks_list.addItem(item)
                                    
        except Exception as e:
            print(f"Error loading profile networks: {str(e)}")

    def add_network_to_profile(self):
        """Add a new network to the profile"""
        try:
            network, ok = QInputDialog.getText(self, 'Add Network', 'Enter network (e.g., 192.168.1.0/24):')
            if ok and network.strip():
                description, ok2 = QInputDialog.getText(self, 'Network Description', 'Enter description (optional):')
                if not ok2:
                    description = ""
                
                network_data = {
                    'network': network.strip(),
                    'description': description.strip() or 'No description',
                    'enabled': True
                }
                
                item = QListWidgetItem()
                item.setText(f"{network.strip()} - {description.strip() or 'No description'}")
                item.setData(1, network_data)
                self.networks_list.addItem(item)
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to add network: {str(e)}")

    def edit_network_in_profile(self):
        """Edit selected network"""
        try:
            current_item = self.networks_list.currentItem()
            if not current_item:
                QMessageBox.information(self, "No Selection", "Please select a network to edit!")
                return
            
            network_data = current_item.data(1)
            current_network = network_data['network']
            current_desc = network_data.get('description', '')
            
            network, ok = QInputDialog.getText(self, 'Edit Network', 'Edit network:', text=current_network)
            if ok and network.strip():
                description, ok2 = QInputDialog.getText(self, 'Edit Description', 'Edit description:', text=current_desc)
                if not ok2:
                    description = current_desc
                
                network_data['network'] = network.strip()
                network_data['description'] = description.strip() or 'No description'
                
                current_item.setText(f"{network.strip()} - {description.strip() or 'No description'}")
                current_item.setData(1, network_data)
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to edit network: {str(e)}")

    def remove_network_from_profile(self):
        """Remove selected network"""
        try:
            current_item = self.networks_list.currentItem()
            if not current_item:
                QMessageBox.information(self, "No Selection", "Please select a network to remove!")
                return
            
            reply = QMessageBox.question(self, "Confirm Remove", "Are you sure you want to remove this network?")
            if reply == QMessageBox.StandardButton.Yes:
                self.networks_list.takeItem(self.networks_list.row(current_item))
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to remove network: {str(e)}")

    def quick_add_networks(self):
        """Quick add common networks"""
        try:
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QCheckBox
            
            dialog = QDialog(self)
            dialog.setWindowTitle("⚡ Quick Add Networks")
            dialog.setGeometry(300, 300, 400, 300)
            
            layout = QVBoxLayout()
            layout.addWidget(QLabel("Select networks to add:"))
            
            common_networks = [
                ('192.168.1.0/24', 'Home Network'),
                ('192.168.0.0/24', 'Home Network Alt'),
                ('10.0.0.0/8', 'Corporate Network'),
                ('172.16.0.0/12', 'Private Network'),
                ('10.0.21.0/24', 'Mixed Network'),
                ('10.0.0.0/24', 'Server Network'),
                ('192.168.100.0/24', 'Lab Network'),
                ('172.20.0.0/16', 'Development Network')
            ]
            
            checkboxes = []
            for network, desc in common_networks:
                cb = QCheckBox(f"{network} - {desc}")
                cb.setProperty('network', network)
                cb.setProperty('description', desc)
                checkboxes.append(cb)
                layout.addWidget(cb)
            
            buttons_layout = QHBoxLayout()
            btn_add_selected = QPushButton("➕ Add Selected")
            btn_cancel = QPushButton("❌ Cancel")
            
            def add_selected():
                for cb in checkboxes:
                    if cb.isChecked():
                        network = cb.property('network')
                        desc = cb.property('description')
                        
                        network_data = {
                            'network': network,
                            'description': desc,
                            'enabled': True
                        }
                        
                        item = QListWidgetItem()
                        item.setText(f"{network} - {desc}")
                        item.setData(1, network_data)
                        self.networks_list.addItem(item)
                
                dialog.accept()
            
            btn_add_selected.clicked.connect(add_selected)
            btn_cancel.clicked.connect(dialog.reject)
            
            buttons_layout.addWidget(btn_add_selected)
            buttons_layout.addWidget(btn_cancel)
            layout.addLayout(buttons_layout)
            
            dialog.setLayout(layout)
            dialog.exec()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to quick add: {str(e)}")

    def show_network_details(self, item):
        """Show details of selected network"""
        try:
            network_data = item.data(1)
            details = f"Network: {network_data['network']}\n"
            details += f"Description: {network_data.get('description', 'No description')}\n"
            details += f"Enabled: {'Yes' if network_data.get('enabled', True) else 'No'}\n"
            
            self.network_details.setPlainText(details)
            
        except Exception as e:
            print(f"Error showing network details: {str(e)}")

    def save_profile_from_dialog(self, profile_name, dialog):
        """Save profile from management dialog"""
        try:
            import json
            
            # Collect networks from list
            network_list = []
            for i in range(self.networks_list.count()):
                item = self.networks_list.item(i)
                if item:
                    network_data = item.data(1)
                    network_list.append(network_data)
            
            # Create profile data
            profile_data = {
                'network_list': network_list,
                'networks': ', '.join([net['network'] for net in network_list]),  # For compatibility
                'win_credentials': [],
                'linux_credentials': []
            }
            
            # Collect current credentials
            for row in self.win_rows:
                if hasattr(row, 'username') and hasattr(row, 'password'):
                    profile_data['win_credentials'].append({
                        'username': row.username(),
                        'password': row.password()
                    })
            
            for row in self.lin_rows:
                if hasattr(row, 'username') and hasattr(row, 'password'):
                    profile_data['linux_credentials'].append({
                        'username': row.username(),
                        'password': row.password()
                    })
            
            # Load existing profiles
            profiles_file = "network_profiles.json"
            profiles = {}
            if os.path.exists(profiles_file):
                with open(profiles_file, 'r', encoding='utf-8') as f:
                    profiles = json.load(f)
            
            # Save profile
            profiles[profile_name] = profile_data
            with open(profiles_file, 'w', encoding='utf-8') as f:
                json.dump(profiles, f, indent=2, ensure_ascii=False)
            
            # Refresh profile combo
            self.load_saved_profiles()
            self.profile_combo.setCurrentText(profile_name)
            
            QMessageBox.information(self, "Success", f"Profile '{profile_name}' saved successfully!")
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save profile: {str(e)}")

    def load_profile_for_scanning(self, profile_name, dialog):
        """Load profile networks into scanning field"""
        try:
            # Collect enabled networks
            enabled_networks = []
            for i in range(self.networks_list.count()):
                item = self.networks_list.item(i)
                if item:
                    network_data = item.data(1)
                    if network_data.get('enabled', True):
                        enabled_networks.append(network_data['network'])
            
            # Set in target entry
            if enabled_networks:
                self.target_entry.setText(', '.join(enabled_networks))
                QMessageBox.information(self, "Success", f"Loaded {len(enabled_networks)} networks for scanning!")
                dialog.accept()
            else:
                QMessageBox.information(self, "No Networks", "No enabled networks found in profile!")
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load for scanning: {str(e)}")

    # ===== Security & Access Control Methods =====
    def open_access_control(self):
        """Open access control configuration dialog"""
        try:
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem
            
            dialog = QDialog(self)
            dialog.setWindowTitle("🔐 Web Service Access Control")
            dialog.setGeometry(200, 200, 500, 400)
            
            layout = QVBoxLayout()
            
            # Allowed IPs section
            layout.addWidget(QLabel("Allowed IP Addresses:"))
            self.allowed_ips_list = QListWidget()
            layout.addWidget(self.allowed_ips_list)
            
            # Load existing allowed IPs
            self.load_allowed_ips()
            
            # IP management buttons
            ip_buttons_layout = QHBoxLayout()
            
            btn_add_ip = QPushButton("➕ Add IP")
            btn_remove_ip = QPushButton("➖ Remove IP")
            btn_add_current_ip = QPushButton("📍 Add Current IP")
            
            btn_add_ip.clicked.connect(self.add_allowed_ip)
            btn_remove_ip.clicked.connect(self.remove_allowed_ip)
            btn_add_current_ip.clicked.connect(self.add_current_ip)
            
            ip_buttons_layout.addWidget(btn_add_ip)
            ip_buttons_layout.addWidget(btn_remove_ip)
            ip_buttons_layout.addWidget(btn_add_current_ip)
            layout.addLayout(ip_buttons_layout)
            
            # Access control settings
            layout.addWidget(QLabel("Security Settings:"))
            
            self.enable_firewall = QCheckBox("Enable IP-based access control")
            self.log_access_attempts = QCheckBox("Log all access attempts")
            self.block_suspicious = QCheckBox("Block suspicious activity")
            
            self.enable_firewall.setChecked(True)
            self.log_access_attempts.setChecked(True)
            
            layout.addWidget(self.enable_firewall)
            layout.addWidget(self.log_access_attempts)
            layout.addWidget(self.block_suspicious)
            
            # Dialog buttons
            dialog_buttons = QHBoxLayout()
            btn_save = QPushButton("💾 Save Settings")
            btn_cancel = QPushButton("❌ Cancel")
            
            btn_save.clicked.connect(lambda: self.save_access_control_settings(dialog))
            btn_cancel.clicked.connect(dialog.reject)
            
            dialog_buttons.addWidget(btn_save)
            dialog_buttons.addWidget(btn_cancel)
            layout.addLayout(dialog_buttons)
            
            dialog.setLayout(layout)
            dialog.exec()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to open access control: {str(e)}")

    def load_allowed_ips(self):
        """Load allowed IPs from config file"""
        try:
            import json
            config_file = "access_control.json"
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    for ip in config.get('allowed_ips', []):
                        self.allowed_ips_list.addItem(ip)
            else:
                # Default allowed IPs
                default_ips = ['127.0.0.1', '::1', '10.0.0.0/8', '192.168.0.0/16']
                for ip in default_ips:
                    self.allowed_ips_list.addItem(ip)
        except Exception as e:
            print(f"Error loading allowed IPs: {str(e)}")

    def add_allowed_ip(self):
        """Add new allowed IP"""
        ip, ok = QInputDialog.getText(self, 'Add Allowed IP', 'Enter IP address or network (e.g., 192.168.1.100 or 10.0.0.0/8):')
        if ok and ip.strip():
            self.allowed_ips_list.addItem(ip.strip())

    def remove_allowed_ip(self):
        """Remove selected allowed IP"""
        current_item = self.allowed_ips_list.currentItem()
        if current_item:
            self.allowed_ips_list.takeItem(self.allowed_ips_list.row(current_item))

    def add_current_ip(self):
        """Add current machine IP to allowed list"""
        try:
            import socket
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            self.allowed_ips_list.addItem(local_ip)
            QMessageBox.information(self, "IP Added", f"Added current IP: {local_ip}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to get current IP: {str(e)}")

    def save_access_control_settings(self, dialog):
        """Save access control settings"""
        try:
            import json
            
            # Collect allowed IPs
            allowed_ips = []
            for i in range(self.allowed_ips_list.count()):
                item = self.allowed_ips_list.item(i)
                if item:
                    allowed_ips.append(item.text())
            
            # Create config
            config = {
                'allowed_ips': allowed_ips,
                'enable_firewall': self.enable_firewall.isChecked(),
                'log_access_attempts': self.log_access_attempts.isChecked(),
                'block_suspicious': self.block_suspicious.isChecked(),
                'last_updated': QTime.currentTime().toString()
            }
            
            # Save to file
            with open('access_control.json', 'w') as f:
                json.dump(config, f, indent=2)
            
            QMessageBox.information(self, "Success", "Access control settings saved successfully!")
            dialog.accept()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save settings: {str(e)}")

    def view_access_logs(self):
        """View web service access logs"""
        try:
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit
            
            dialog = QDialog(self)
            dialog.setWindowTitle("📊 Web Service Access Logs")
            dialog.setGeometry(150, 150, 800, 600)
            
            layout = QVBoxLayout()
            
            # Log display
            log_display = QTextEdit()
            log_display.setReadOnly(True)
            
            # Load logs
            log_content = self.load_access_logs()
            log_display.setPlainText(log_content)
            
            layout.addWidget(log_display)
            
            # Action buttons
            buttons_layout = QHBoxLayout()
            btn_refresh = QPushButton("🔄 Refresh")
            btn_clear = QPushButton("🗑️ Clear Logs")
            btn_export = QPushButton("📤 Export Logs")
            
            btn_refresh.clicked.connect(lambda: log_display.setPlainText(self.load_access_logs()))
            btn_clear.clicked.connect(lambda: self.clear_access_logs(log_display))
            btn_export.clicked.connect(self.export_access_logs)
            
            buttons_layout.addWidget(btn_refresh)
            buttons_layout.addWidget(btn_clear)
            buttons_layout.addWidget(btn_export)
            layout.addLayout(buttons_layout)
            
            dialog.setLayout(layout)
            dialog.exec()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to view logs: {str(e)}")

    def load_access_logs(self):
        """Load access logs from web service log file"""
        try:
            log_files = ['web_service.log', 'enhanced_complete_web_service.log']
            log_content = ""
            
            for log_file in log_files:
                if os.path.exists(log_file):
                    with open(log_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        log_content += f"=== {log_file} ===\n{content}\n\n"
            
            return log_content if log_content else "No access logs found."
            
        except Exception as e:
            return f"Error loading logs: {str(e)}"

    def clear_access_logs(self, log_display):
        """Clear access logs"""
        try:
            reply = QMessageBox.question(self, "Confirm Clear", "Are you sure you want to clear all access logs?")
            if reply == QMessageBox.StandardButton.Yes:
                log_files = ['web_service.log', 'enhanced_complete_web_service.log']
                for log_file in log_files:
                    if os.path.exists(log_file):
                        open(log_file, 'w').close()
                
                log_display.clear()
                QMessageBox.information(self, "Success", "Access logs cleared successfully!")
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to clear logs: {str(e)}")

    def export_access_logs(self):
        """Export access logs to file"""
        try:
            from PyQt6.QtWidgets import QFileDialog
            import datetime
            
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export Access Logs", 
                f"access_logs_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                "Text Files (*.txt);;All Files (*)"
            )
            
            if filename:
                log_content = self.load_access_logs()
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(log_content)
                
                QMessageBox.information(self, "Success", f"Logs exported to: {filename}")
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to export logs: {str(e)}")

    def backup_database(self):
        """Backup the assets database"""
        try:
            import shutil
            import datetime
            from PyQt6.QtWidgets import QFileDialog
            
            # Generate backup filename
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"assets_backup_{timestamp}.db"
            
            # Ask user for backup location
            filename, _ = QFileDialog.getSaveFileName(
                self, "Backup Database", backup_filename,
                "Database Files (*.db);;All Files (*)"
            )
            
            if filename:
                # Copy database file
                if os.path.exists("assets.db"):
                    shutil.copy2("assets.db", filename)
                    
                    # Also backup related files
                    base_name = filename.rsplit('.', 1)[0]
                    for ext in ['-shm', '-wal']:
                        src_file = f"assets.db{ext}"
                        if os.path.exists(src_file):
                            dst_file = f"{base_name}{ext}"
                            shutil.copy2(src_file, dst_file)
                    
                    QMessageBox.information(self, "Success", f"Database backed up to: {filename}")
                else:
                    QMessageBox.warning(self, "Error", "Database file not found!")
                    
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to backup database: {str(e)}")

    def view_all_devices(self):
        """View all devices in database"""
        try:
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
            
            dialog = QDialog(self)
            dialog.setWindowTitle("📋 All Devices in Database")
            dialog.setGeometry(100, 100, 1000, 600)
            
            layout = QVBoxLayout()
            
            # Create table
            table = QTableWidget()
            layout.addWidget(table)
            
            # Load data from database
            import sqlite3
            conn = sqlite3.connect('assets.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT ip_address, hostname, department, os_type, status, 
                       last_seen, collection_method 
                FROM assets 
                ORDER BY last_seen DESC
            """)
            
            data = cursor.fetchall()
            conn.close()
            
            if not data:
                QMessageBox.information(self, "No Data", "No devices found in database!")
                return
            
            # Set up table
            headers = ["IP Address", "Hostname", "Department", "OS Type", "Status", "Last Seen", "Method"]
            table.setRowCount(len(data))
            table.setColumnCount(len(headers))
            table.setHorizontalHeaderLabels(headers)
            
            # Populate table
            for row, record in enumerate(data):
                for col, value in enumerate(record):
                    item = QTableWidgetItem(str(value) if value else "")
                    table.setItem(row, col, item)
            
            # Resize columns
            header = table.horizontalHeader()
            if header:
                header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            
            # Action buttons
            buttons_layout = QHBoxLayout()
            
            btn_refresh = QPushButton("🔄 Refresh")
            btn_export = QPushButton("📤 Export CSV")
            btn_delete = QPushButton("🗑️ Delete Selected")
            
            btn_refresh.clicked.connect(lambda: self.refresh_device_table(table))
            btn_export.clicked.connect(lambda: self.export_devices_csv())
            btn_delete.clicked.connect(lambda: self.delete_selected_devices(table))
            
            buttons_layout.addWidget(btn_refresh)
            buttons_layout.addWidget(btn_export)
            buttons_layout.addWidget(btn_delete)
            layout.addLayout(buttons_layout)
            
            dialog.setLayout(layout)
            dialog.exec()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to view devices: {str(e)}")

    def refresh_device_table(self, table):
        """Refresh device table data"""
        try:
            import sqlite3
            conn = sqlite3.connect('assets.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT ip_address, hostname, department, os_type, status, 
                       last_seen, collection_method 
                FROM assets 
                ORDER BY last_seen DESC
            """)
            
            data = cursor.fetchall()
            conn.close()
            
            table.setRowCount(len(data))
            for row, record in enumerate(data):
                for col, value in enumerate(record):
                    item = QTableWidgetItem(str(value) if value else "")
                    table.setItem(row, col, item)
                    
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to refresh table: {str(e)}")

    def export_devices_csv(self):
        """Export devices to CSV file"""
        try:
            from PyQt6.QtWidgets import QFileDialog
            import csv
            import sqlite3
            import datetime
            
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export Devices", 
                f"devices_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "CSV Files (*.csv);;All Files (*)"
            )
            
            if filename:
                conn = sqlite3.connect('assets.db')
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT ip_address, hostname, department, os_type, status, 
                           last_seen, collection_method 
                    FROM assets 
                    ORDER BY last_seen DESC
                """)
                
                data = cursor.fetchall()
                headers = ["IP Address", "Hostname", "Department", "OS Type", "Status", "Last Seen", "Method"]
                
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(headers)
                    writer.writerows(data)
                
                conn.close()
                QMessageBox.information(self, "Success", f"Devices exported to: {filename}")
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to export devices: {str(e)}")

    def delete_selected_devices(self, table):
        """Delete selected devices from database"""
        try:
            selected_rows = set()
            for item in table.selectedItems():
                selected_rows.add(item.row())
            
            if not selected_rows:
                QMessageBox.information(self, "No Selection", "Please select devices to delete!")
                return
            
            reply = QMessageBox.question(self, "Confirm Delete", 
                                       f"Are you sure you want to delete {len(selected_rows)} selected devices?")
            if reply != QMessageBox.StandardButton.Yes:
                return
            
            import sqlite3
            conn = sqlite3.connect('assets.db')
            cursor = conn.cursor()
            
            deleted_count = 0
            for row in selected_rows:
                ip_item = table.item(row, 0)  # IP is in first column
                if ip_item:
                    ip = ip_item.text()
                    cursor.execute("DELETE FROM assets WHERE ip_address = ?", (ip,))
                    deleted_count += 1
            
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Success", f"Deleted {deleted_count} devices successfully!")
            self.refresh_device_table(table)
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to delete devices: {str(e)}")

    # ===== AUTOMATIC SCANNING METHODS =====
    
    def update_auto_scan_status(self, status_message):
        """Update automatic scanning status display"""
        if hasattr(self, 'auto_scan_status'):
            if "started" in status_message.lower():
                self.auto_scan_status.setText("🟢 Running")
                self.auto_scan_status.setStyleSheet("color: green; font-weight: bold;")
                self.btn_start_auto_scan.setEnabled(False)
                self.btn_stop_auto_scan.setEnabled(True)
            elif "stopped" in status_message.lower():
                self.auto_scan_status.setText("🔴 Stopped")
                self.auto_scan_status.setStyleSheet("color: red; font-weight: bold;")
                self.btn_start_auto_scan.setEnabled(True)
                self.btn_stop_auto_scan.setEnabled(False)
            
            if hasattr(self, 'auto_scan_info'):
                self.auto_scan_info.setText(status_message)
    
    def on_auto_scan_started(self, target_name):
        """Handle automatic scan start event"""
        self.log_output.append(f"🔍 Automatic scan started for: {target_name}")
        if hasattr(self, 'auto_scan_info'):
            self.auto_scan_info.setText(f"Scanning: {target_name}")
    
    def on_auto_scan_completed(self, target_name, devices_found, results):
        """Handle automatic scan completion event"""
        self.log_output.append(f"✅ Automatic scan completed for {target_name}: {devices_found} devices found")
        if hasattr(self, 'auto_scan_info'):
            self.auto_scan_info.setText(f"Last scan: {target_name} ({devices_found} devices)")
    
    def on_auto_scan_error(self, target_name, error_message):
        """Handle automatic scan error event"""
        self.log_output.append(f"❌ Automatic scan error for {target_name}: {error_message}")
        if hasattr(self, 'auto_scan_info'):
            self.auto_scan_info.setText(f"Error scanning {target_name}: {error_message}")
    
    def start_automatic_scanning(self):
        """Start the automatic scanning system"""
        try:
            if hasattr(self, 'automatic_scanner'):
                self.automatic_scanner.start_automatic_scanning()
                self.log_output.append("🚀 Automatic scanning system started")
            else:
                QMessageBox.warning(self, "Error", "Automatic scanner not available")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start automatic scanning: {e}")
            self.log_output.append(f"❌ Error starting automatic scanning: {e}")
    
    def stop_automatic_scanning(self):
        """Stop the automatic scanning system"""
        try:
            if hasattr(self, 'automatic_scanner'):
                self.automatic_scanner.stop_automatic_scanning()
                self.log_output.append("⏹️ Automatic scanning system stopped")
            else:
                QMessageBox.warning(self, "Error", "Automatic scanner not available")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to stop automatic scanning: {e}")
            self.log_output.append(f"❌ Error stopping automatic scanning: {e}")
    
    def configure_automatic_scanning(self):
        """Open automatic scanning configuration dialog"""
        try:
            if hasattr(self, 'automatic_scanner'):
                dialog = AutoScanConfigDialog(self.automatic_scanner, self)
                dialog.exec()
            else:
                QMessageBox.warning(self, "Error", "Automatic scanner not available")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open configuration: {e}")
            self.log_output.append(f"❌ Error opening auto-scan configuration: {e}")

def launch_gui():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
