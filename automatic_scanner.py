"""
🕐 AUTOMATIC SCHEDULED SCANNING SYSTEM 🕐
==========================================

Advanced automatic network scanning and collection system with:
- Flexible scheduling (intervals, specific times, daily/weekly)
- Real-time data collection and database saving
- Parallel operation with manual scanning
- Thread-safe UI integration
- Secure authentication reuse

Author: Enhanced by GitHub Copilot for Asset Management System
"""

import os
import sys
import json
import time
import sqlite3
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

try:
    from PyQt6.QtCore import QObject, QTimer, pyqtSignal, QThread, QMutex, QMutexLocker
    from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                                QLabel, QPushButton, QLineEdit, QTextEdit, QComboBox,
                                QSpinBox, QCheckBox, QTimeEdit, QTableWidget, 
                                QTableWidgetItem, QHeaderView, QMessageBox,
                                QProgressBar, QFrame, QDialog, QInputDialog)
    from PyQt6.QtGui import QFont
    from PyQt6.QtCore import Qt, QTime
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False
    print("⚠️ PyQt6 not available for automatic scanner")

# Schedule types
class ScheduleType(Enum):
    INTERVAL = "interval"  # Every X minutes/hours
    DAILY = "daily"       # Daily at specific time
    WEEKLY = "weekly"     # Weekly on specific days
    ONCE = "once"         # Run once at specific time

@dataclass
class ScanSchedule:
    """Scan schedule configuration"""
    schedule_type: ScheduleType
    interval_minutes: int = 0  # For interval type
    daily_time: Optional[str] = None  # For daily type (HH:MM format)
    weekly_days: List[int] = None  # For weekly type (0=Monday, 6=Sunday)
    weekly_time: Optional[str] = None  # For weekly type
    once_datetime: Optional[str] = None  # For once type
    enabled: bool = True
    name: str = "Unnamed Schedule"

@dataclass
class AutoScanTarget:
    """Automatic scan target configuration"""
    name: str
    network_range: str  # e.g., "192.168.1.1-50" or "10.0.21.0/24"
    enabled: bool = True
    last_scan: Optional[str] = None
    devices_found: int = 0

class AutomaticScanner(QObject):
    """
    🚀 AUTOMATIC SCANNING ENGINE 🚀
    
    Features:
    - Thread-safe scheduled scanning
    - Real-time data collection
    - Parallel operation support
    - Database integration
    - Authentication reuse
    """
    
    # Signals for UI communication
    scan_started = pyqtSignal(str)  # target_name
    scan_completed = pyqtSignal(str, int, dict)  # target_name, devices_found, results
    scan_error = pyqtSignal(str, str)  # target_name, error_message
    status_changed = pyqtSignal(str)  # status_message
    log_message = pyqtSignal(str)  # log_message
    
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.schedules: List[ScanSchedule] = []
        self.targets: List[AutoScanTarget] = []
        self.is_running = False
        self.scan_thread = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_schedules)
        self.mutex = QMutex()
        
        # Configuration file
        self.config_file = "automatic_scanner_config.json"
        self.load_configuration()
        
    def load_configuration(self):
        """Load schedules and targets from configuration file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                
                # Load schedules
                self.schedules = []
                for sched_data in config.get('schedules', []):
                    schedule = ScanSchedule(
                        schedule_type=ScheduleType(sched_data['schedule_type']),
                        interval_minutes=sched_data.get('interval_minutes', 0),
                        daily_time=sched_data.get('daily_time'),
                        weekly_days=sched_data.get('weekly_days', []),
                        weekly_time=sched_data.get('weekly_time'),
                        once_datetime=sched_data.get('once_datetime'),
                        enabled=sched_data.get('enabled', True),
                        name=sched_data.get('name', 'Unnamed Schedule')
                    )
                    self.schedules.append(schedule)
                
                # Load targets
                self.targets = []
                for target_data in config.get('targets', []):
                    target = AutoScanTarget(
                        name=target_data['name'],
                        network_range=target_data['network_range'],
                        enabled=target_data.get('enabled', True),
                        last_scan=target_data.get('last_scan'),
                        devices_found=target_data.get('devices_found', 0)
                    )
                    self.targets.append(target)
                    
            else:
                # Create default configuration
                self.create_default_config()
                
        except Exception as e:
            self.log_message.emit(f"⚠️ Error loading auto-scan config: {e}")
            self.create_default_config()
    
    def create_default_config(self):
        """Create default configuration with sample schedule and target"""
        # Default schedule: every 30 minutes
        default_schedule = ScanSchedule(
            schedule_type=ScheduleType.INTERVAL,
            interval_minutes=30,
            enabled=False,  # Disabled by default for safety
            name="Default 30-minute scan"
        )
        self.schedules = [default_schedule]
        
        # Default target: local network
        default_target = AutoScanTarget(
            name="Local Network",
            network_range="192.168.1.1-50",
            enabled=False  # Disabled by default for safety
        )
        self.targets = [default_target]
        
        self.save_configuration()
    
    def save_configuration(self):
        """Save current schedules and targets to configuration file"""
        try:
            config = {
                'schedules': [],
                'targets': []
            }
            
            # Save schedules
            for schedule in self.schedules:
                sched_data = {
                    'schedule_type': schedule.schedule_type.value,
                    'interval_minutes': schedule.interval_minutes,
                    'daily_time': schedule.daily_time,
                    'weekly_days': schedule.weekly_days,
                    'weekly_time': schedule.weekly_time,
                    'once_datetime': schedule.once_datetime,
                    'enabled': schedule.enabled,
                    'name': schedule.name
                }
                config['schedules'].append(sched_data)
            
            # Save targets
            for target in self.targets:
                target_data = {
                    'name': target.name,
                    'network_range': target.network_range,
                    'enabled': target.enabled,
                    'last_scan': target.last_scan,
                    'devices_found': target.devices_found
                }
                config['targets'].append(target_data)
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
                
        except Exception as e:
            self.log_message.emit(f"⚠️ Error saving auto-scan config: {e}")
    
    def start_automatic_scanning(self):
        """Start the automatic scanning system"""
        if self.is_running:
            return
            
        self.is_running = True
        # Check every minute for scheduled scans
        self.timer.start(60000)  # 60 seconds
        self.status_changed.emit("🟢 Automatic scanning started")
        self.log_message.emit("🚀 Automatic scanning system started")
    
    def stop_automatic_scanning(self):
        """Stop the automatic scanning system"""
        self.is_running = False
        self.timer.stop()
        if self.scan_thread and self.scan_thread.isRunning():
            self.scan_thread.quit()
            self.scan_thread.wait(5000)  # Wait up to 5 seconds
        self.status_changed.emit("🔴 Automatic scanning stopped")
        self.log_message.emit("⏹️ Automatic scanning system stopped")
    
    def check_schedules(self):
        """Check if any scheduled scans should run now"""
        if not self.is_running:
            return
            
        current_time = datetime.now()
        
        for schedule in self.schedules:
            if not schedule.enabled:
                continue
                
            should_run = False
            
            if schedule.schedule_type == ScheduleType.INTERVAL:
                # Check interval-based schedules
                if hasattr(self, 'last_interval_check'):
                    time_diff = (current_time - self.last_interval_check).total_seconds() / 60
                    if time_diff >= schedule.interval_minutes:
                        should_run = True
                else:
                    should_run = True  # First run
                    
            elif schedule.schedule_type == ScheduleType.DAILY:
                # Check daily schedules
                if schedule.daily_time:
                    target_time = datetime.strptime(schedule.daily_time, "%H:%M").time()
                    current_time_only = current_time.time()
                    
                    # Check if we're within 1 minute of target time
                    if abs((datetime.combine(current_time.date(), current_time_only) - 
                           datetime.combine(current_time.date(), target_time)).total_seconds()) < 60:
                        # Check if we haven't run today yet
                        if not hasattr(schedule, 'last_daily_run') or \
                           schedule.last_daily_run != current_time.date():
                            should_run = True
                            schedule.last_daily_run = current_time.date()
            
            elif schedule.schedule_type == ScheduleType.WEEKLY:
                # Check weekly schedules
                if schedule.weekly_days and schedule.weekly_time:
                    current_weekday = current_time.weekday()  # 0=Monday, 6=Sunday
                    if current_weekday in schedule.weekly_days:
                        target_time = datetime.strptime(schedule.weekly_time, "%H:%M").time()
                        current_time_only = current_time.time()
                        
                        if abs((datetime.combine(current_time.date(), current_time_only) - 
                               datetime.combine(current_time.date(), target_time)).total_seconds()) < 60:
                            # Check if we haven't run this week yet
                            week_key = f"{current_time.year}-{current_time.isocalendar()[1]}"
                            if not hasattr(schedule, 'last_weekly_run') or \
                               schedule.last_weekly_run != week_key:
                                should_run = True
                                schedule.last_weekly_run = week_key
            
            elif schedule.schedule_type == ScheduleType.ONCE:
                # Check one-time schedules
                if schedule.once_datetime:
                    target_datetime = datetime.fromisoformat(schedule.once_datetime)
                    if current_time >= target_datetime and \
                       not hasattr(schedule, 'has_run'):
                        should_run = True
                        schedule.has_run = True
                        schedule.enabled = False  # Disable after running once
            
            if should_run:
                self.execute_scheduled_scan(schedule)
                if schedule.schedule_type == ScheduleType.INTERVAL:
                    self.last_interval_check = current_time
    
    def execute_scheduled_scan(self, schedule: ScanSchedule):
        """Execute a scheduled scan for all enabled targets"""
        self.log_message.emit(f"⏰ Executing scheduled scan: {schedule.name}")
        
        enabled_targets = [t for t in self.targets if t.enabled]
        if not enabled_targets:
            self.log_message.emit("⚠️ No enabled targets for scheduled scan")
            return
        
        # Start scan in separate thread to avoid UI blocking
        self.scan_thread = AutoScanThread(self.main_window, enabled_targets, self)
        self.scan_thread.finished.connect(self.on_scan_thread_finished)
        self.scan_thread.start()
    
    def on_scan_thread_finished(self):
        """Handle scan thread completion"""
        self.log_message.emit("✅ Scheduled scan completed")
    
    def manual_scan_target(self, target: AutoScanTarget):
        """Manually trigger scan for a specific target"""
        self.log_message.emit(f"🔍 Manual scan started for: {target.name}")
        
        # Start scan in separate thread
        self.scan_thread = AutoScanThread(self.main_window, [target], self)
        self.scan_thread.finished.connect(lambda: self.log_message.emit(f"✅ Manual scan completed for: {target.name}"))
        self.scan_thread.start()

class AutoScanThread(QThread):
    """
    🧵 AUTOMATIC SCAN WORKER THREAD 🧵
    
    Performs network scanning and data collection in background
    without blocking the UI. Uses same authentication as manual scans.
    """
    
    def __init__(self, main_window, targets: List[AutoScanTarget], scanner: AutomaticScanner):
        super().__init__()
        self.main_window = main_window
        self.targets = targets
        self.scanner = scanner
    
    def run(self):
        """Execute scanning for all targets"""
        try:
            for target in self.targets:
                if not target.enabled:
                    continue
                    
                self.scanner.scan_started.emit(target.name)
                
                # Use the same collection method as manual scanning
                # This ensures authentication and settings are reused
                result = self.perform_target_scan(target)
                
                if result.get('success'):
                    devices_found = len(result.get('devices', []))
                    target.devices_found = devices_found
                    target.last_scan = datetime.now().isoformat()
                    
                    self.scanner.scan_completed.emit(target.name, devices_found, result)
                    
                    # Save results to database in real-time
                    self.save_results_to_database(target, result)
                    
                else:
                    error_msg = result.get('error', 'Unknown error')
                    self.scanner.scan_error.emit(target.name, error_msg)
                
        except Exception as e:
            self.scanner.log_message.emit(f"❌ Scan thread error: {e}")
    
    def perform_target_scan(self, target: AutoScanTarget) -> Dict[str, Any]:
        """
        Perform network scan for a target using main window's collection system
        
        This reuses the same authentication, settings, and collection methods
        as the manual scanning to ensure consistency.
        """
        try:
            # Temporarily set the target in main window
            original_target = self.main_window.target_entry.text()
            self.main_window.target_entry.setText(target.network_range)
            
            # Create a mock result container
            scan_result = {
                'success': False,
                'devices': [],
                'error': None,
                'target': target.network_range
            }
            
            # Use the ultra-fast collector if available
            try:
                if hasattr(self.main_window, 'collection_worker'):
                    # Use the existing collection worker system
                    # This ensures we use the same authentication and settings
                    
                    # Import the ultra-fast collector
                    import ultra_fast_collector
                    
                    # Get authentication from main window
                    win_creds = []
                    for row in self.main_window.win_rows:
                        if row.username() and row.password():
                            win_creds.append((row.username(), row.password()))
                    
                    lin_creds = []
                    for row in self.main_window.lin_rows:
                        if row.username() and row.password():
                            lin_creds.append((row.username(), row.password()))
                    
                    # Perform the scan using the same system as manual
                    results = ultra_fast_collector.collect_all_devices(
                        targets=[target.network_range],
                        windows_credentials=win_creds,
                        linux_credentials=lin_creds,
                        use_snmp=self.main_window.chk_snmp.isChecked(),
                        use_nmap=self.main_window.chk_nmap.isChecked(),
                        max_threads=20,  # Conservative for automatic scans
                        excel_file=None,  # Database-only
                        progress_callback=None,  # No UI updates needed
                        log_callback=lambda msg: self.scanner.log_message.emit(f"📡 {msg}")
                    )
                    
                    if results and results.get('success'):
                        scan_result['success'] = True
                        scan_result['devices'] = results.get('devices', [])
                        
                        # Log success
                        device_count = len(scan_result['devices'])
                        self.scanner.log_message.emit(f"✅ Found {device_count} devices in {target.name}")
                        
                    else:
                        scan_result['error'] = results.get('error', 'Scan failed')
                        
            except ImportError:
                scan_result['error'] = "Ultra-fast collector not available"
            except Exception as e:
                scan_result['error'] = f"Collection error: {e}"
            
            # Restore original target
            self.main_window.target_entry.setText(original_target)
            
            return scan_result
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Scan execution error: {e}",
                'devices': [],
                'target': target.network_range
            }
    
    def save_results_to_database(self, target: AutoScanTarget, result: Dict[str, Any]):
        """Save scan results to database in real-time"""
        try:
            devices = result.get('devices', [])
            if not devices:
                return
            
            # Use the same database connection as main window
            db_path = "assets.db"
            
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                # Ensure assets table exists (same as manual collection)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS assets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ip_address TEXT,
                        hostname TEXT,
                        mac_address TEXT,
                        os_type TEXT,
                        os_version TEXT,
                        cpu_info TEXT,
                        ram_gb REAL,
                        hard_drives TEXT,
                        network_interfaces TEXT,
                        installed_software TEXT,
                        domain_info TEXT,
                        scan_timestamp TEXT,
                        collection_method TEXT,
                        source_scan TEXT
                    )
                ''')
                
                # Insert devices with automatic scan marker
                scan_timestamp = datetime.now().isoformat()
                
                for device in devices:
                    cursor.execute('''
                        INSERT INTO assets (
                            ip_address, hostname, mac_address, os_type, os_version,
                            cpu_info, ram_gb, hard_drives, network_interfaces,
                            installed_software, domain_info, scan_timestamp,
                            collection_method, source_scan
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        device.get('ip_address', ''),
                        device.get('hostname', ''),
                        device.get('mac_address', ''),
                        device.get('os_type', ''),
                        device.get('os_version', ''),
                        device.get('cpu_info', ''),
                        device.get('ram_gb', 0),
                        device.get('hard_drives', ''),
                        device.get('network_interfaces', ''),
                        device.get('installed_software', ''),
                        device.get('domain_info', ''),
                        scan_timestamp,
                        'automatic_scan',
                        f"Auto: {target.name}"
                    ))
                
                conn.commit()
                
                # Log database save
                device_count = len(devices)
                self.scanner.log_message.emit(f"💾 Saved {device_count} devices to database from {target.name}")
                
        except Exception as e:
            self.scanner.log_message.emit(f"❌ Database save error for {target.name}: {e}")

class AutoScanConfigDialog(QDialog):
    """
    🔧 AUTOMATIC SCAN CONFIGURATION DIALOG 🔧
    
    Advanced configuration interface for:
    - Creating/editing scan schedules
    - Managing target networks
    - Testing manual scans
    - Viewing scan history
    """
    
    def __init__(self, scanner: AutomaticScanner, parent=None):
        super().__init__(parent)
        self.scanner = scanner
        self.setWindowTitle("🔧 Configure Automatic Scanning")
        self.setGeometry(100, 100, 800, 600)
        self.setModal(True)
        
        self.init_ui()
        self.load_current_config()
    
    def init_ui(self):
        """Initialize the configuration UI"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("🕐 Automatic Scanning Configuration")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Create tabs-like sections using group boxes
        main_layout = QHBoxLayout()
        
        # Left panel - Targets
        targets_panel = self.create_targets_panel()
        main_layout.addWidget(targets_panel)
        
        # Right panel - Schedules
        schedules_panel = self.create_schedules_panel()
        main_layout.addWidget(schedules_panel)
        
        layout.addLayout(main_layout)
        
        # Bottom panel - Actions
        actions_layout = QHBoxLayout()
        
        self.btn_test_scan = QPushButton("🧪 Test Manual Scan")
        self.btn_save_config = QPushButton("💾 Save Configuration")
        self.btn_cancel = QPushButton("❌ Cancel")
        
        self.btn_test_scan.clicked.connect(self.test_manual_scan)
        self.btn_save_config.clicked.connect(self.save_configuration)
        self.btn_cancel.clicked.connect(self.reject)
        
        actions_layout.addWidget(self.btn_test_scan)
        actions_layout.addStretch()
        actions_layout.addWidget(self.btn_save_config)
        actions_layout.addWidget(self.btn_cancel)
        
        layout.addLayout(actions_layout)
        self.setLayout(layout)
    
    def create_targets_panel(self):
        """Create the targets configuration panel"""
        targets_box = QGroupBox("🎯 Scan Targets")
        layout = QVBoxLayout()
        
        # Targets table
        self.targets_table = QTableWidget()
        self.targets_table.setColumnCount(4)
        self.targets_table.setHorizontalHeaderLabels(["Name", "Network Range", "Enabled", "Last Scan"])
        self.targets_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.targets_table)
        
        # Target controls
        target_controls = QHBoxLayout()
        
        self.btn_add_target = QPushButton("➕ Add Target")
        self.btn_edit_target = QPushButton("✏️ Edit Target")
        self.btn_delete_target = QPushButton("🗑️ Delete Target")
        self.btn_manual_scan = QPushButton("🔍 Manual Scan")
        
        self.btn_add_target.clicked.connect(self.add_target)
        self.btn_edit_target.clicked.connect(self.edit_target)
        self.btn_delete_target.clicked.connect(self.delete_target)
        self.btn_manual_scan.clicked.connect(self.manual_scan_selected)
        
        target_controls.addWidget(self.btn_add_target)
        target_controls.addWidget(self.btn_edit_target)
        target_controls.addWidget(self.btn_delete_target)
        target_controls.addWidget(self.btn_manual_scan)
        
        layout.addLayout(target_controls)
        targets_box.setLayout(layout)
        return targets_box
    
    def create_schedules_panel(self):
        """Create the schedules configuration panel"""
        schedules_box = QGroupBox("⏰ Scan Schedules")
        layout = QVBoxLayout()
        
        # Schedules table
        self.schedules_table = QTableWidget()
        self.schedules_table.setColumnCount(4)
        self.schedules_table.setHorizontalHeaderLabels(["Name", "Type", "Schedule", "Enabled"])
        self.schedules_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.schedules_table)
        
        # Schedule controls
        schedule_controls = QHBoxLayout()
        
        self.btn_add_schedule = QPushButton("➕ Add Schedule")
        self.btn_edit_schedule = QPushButton("✏️ Edit Schedule")
        self.btn_delete_schedule = QPushButton("🗑️ Delete Schedule")
        
        self.btn_add_schedule.clicked.connect(self.add_schedule)
        self.btn_edit_schedule.clicked.connect(self.edit_schedule)
        self.btn_delete_schedule.clicked.connect(self.delete_schedule)
        
        schedule_controls.addWidget(self.btn_add_schedule)
        schedule_controls.addWidget(self.btn_edit_schedule)
        schedule_controls.addWidget(self.btn_delete_schedule)
        
        layout.addLayout(schedule_controls)
        
        # Quick schedule presets
        presets_layout = QHBoxLayout()
        presets_label = QLabel("Quick Presets:")
        presets_layout.addWidget(presets_label)
        
        self.btn_preset_30min = QPushButton("Every 30 min")
        self.btn_preset_hourly = QPushButton("Every hour")
        self.btn_preset_daily = QPushButton("Daily 9 AM")
        
        self.btn_preset_30min.clicked.connect(lambda: self.add_preset_schedule(30, ScheduleType.INTERVAL))
        self.btn_preset_hourly.clicked.connect(lambda: self.add_preset_schedule(60, ScheduleType.INTERVAL))
        self.btn_preset_daily.clicked.connect(lambda: self.add_preset_schedule(0, ScheduleType.DAILY, "09:00"))
        
        presets_layout.addWidget(self.btn_preset_30min)
        presets_layout.addWidget(self.btn_preset_hourly)
        presets_layout.addWidget(self.btn_preset_daily)
        
        layout.addLayout(presets_layout)
        schedules_box.setLayout(layout)
        return schedules_box
    
    def load_current_config(self):
        """Load current configuration into the UI"""
        # Load targets
        self.targets_table.setRowCount(len(self.scanner.targets))
        for row, target in enumerate(self.scanner.targets):
            self.targets_table.setItem(row, 0, QTableWidgetItem(target.name))
            self.targets_table.setItem(row, 1, QTableWidgetItem(target.network_range))
            
            enabled_item = QTableWidgetItem("✅" if target.enabled else "❌")
            self.targets_table.setItem(row, 2, enabled_item)
            
            last_scan = target.last_scan if target.last_scan else "Never"
            if target.last_scan:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(target.last_scan)
                    last_scan = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    pass
            self.targets_table.setItem(row, 3, QTableWidgetItem(last_scan))
        
        # Load schedules
        self.schedules_table.setRowCount(len(self.scanner.schedules))
        for row, schedule in enumerate(self.scanner.schedules):
            self.schedules_table.setItem(row, 0, QTableWidgetItem(schedule.name))
            self.schedules_table.setItem(row, 1, QTableWidgetItem(schedule.schedule_type.value.title()))
            
            # Format schedule description
            schedule_desc = self.format_schedule_description(schedule)
            self.schedules_table.setItem(row, 2, QTableWidgetItem(schedule_desc))
            
            enabled_item = QTableWidgetItem("✅" if schedule.enabled else "❌")
            self.schedules_table.setItem(row, 3, enabled_item)
    
    def format_schedule_description(self, schedule: ScanSchedule) -> str:
        """Format schedule description for display"""
        if schedule.schedule_type == ScheduleType.INTERVAL:
            if schedule.interval_minutes >= 60:
                hours = schedule.interval_minutes // 60
                minutes = schedule.interval_minutes % 60
                if minutes == 0:
                    return f"Every {hours} hour(s)"
                else:
                    return f"Every {hours}h {minutes}m"
            else:
                return f"Every {schedule.interval_minutes} minutes"
        elif schedule.schedule_type == ScheduleType.DAILY:
            return f"Daily at {schedule.daily_time}"
        elif schedule.schedule_type == ScheduleType.WEEKLY:
            days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            day_names = [days[d] for d in schedule.weekly_days] if schedule.weekly_days else []
            return f"Weekly on {', '.join(day_names)} at {schedule.weekly_time}"
        elif schedule.schedule_type == ScheduleType.ONCE:
            return f"Once at {schedule.once_datetime}"
        else:
            return "Unknown"
    
    def add_target(self):
        """Add a new scan target"""
        dialog = TargetEditDialog(None, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            target = dialog.get_target()
            self.scanner.targets.append(target)
            self.load_current_config()
    
    def edit_target(self):
        """Edit selected target"""
        current_row = self.targets_table.currentRow()
        if current_row < 0:
            QMessageBox.information(self, "No Selection", "Please select a target to edit.")
            return
        
        target = self.scanner.targets[current_row]
        dialog = TargetEditDialog(target, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_target = dialog.get_target()
            self.scanner.targets[current_row] = updated_target
            self.load_current_config()
    
    def delete_target(self):
        """Delete selected target"""
        current_row = self.targets_table.currentRow()
        if current_row < 0:
            QMessageBox.information(self, "No Selection", "Please select a target to delete.")
            return
        
        reply = QMessageBox.question(self, "Confirm Delete", 
                                   "Are you sure you want to delete this target?")
        if reply == QMessageBox.StandardButton.Yes:
            del self.scanner.targets[current_row]
            self.load_current_config()
    
    def manual_scan_selected(self):
        """Manually scan selected target"""
        current_row = self.targets_table.currentRow()
        if current_row < 0:
            QMessageBox.information(self, "No Selection", "Please select a target to scan.")
            return
        
        target = self.scanner.targets[current_row]
        self.scanner.manual_scan_target(target)
        QMessageBox.information(self, "Scan Started", f"Manual scan started for: {target.name}")
    
    def add_schedule(self):
        """Add a new schedule"""
        dialog = ScheduleEditDialog(None, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            schedule = dialog.get_schedule()
            self.scanner.schedules.append(schedule)
            self.load_current_config()
    
    def edit_schedule(self):
        """Edit selected schedule"""
        current_row = self.schedules_table.currentRow()
        if current_row < 0:
            QMessageBox.information(self, "No Selection", "Please select a schedule to edit.")
            return
        
        schedule = self.scanner.schedules[current_row]
        dialog = ScheduleEditDialog(schedule, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_schedule = dialog.get_schedule()
            self.scanner.schedules[current_row] = updated_schedule
            self.load_current_config()
    
    def delete_schedule(self):
        """Delete selected schedule"""
        current_row = self.schedules_table.currentRow()
        if current_row < 0:
            QMessageBox.information(self, "No Selection", "Please select a schedule to delete.")
            return
        
        reply = QMessageBox.question(self, "Confirm Delete", 
                                   "Are you sure you want to delete this schedule?")
        if reply == QMessageBox.StandardButton.Yes:
            del self.scanner.schedules[current_row]
            self.load_current_config()
    
    def add_preset_schedule(self, interval_minutes: int, schedule_type: ScheduleType, time_str: str = None):
        """Add a preset schedule"""
        if schedule_type == ScheduleType.INTERVAL:
            schedule = ScanSchedule(
                schedule_type=schedule_type,
                interval_minutes=interval_minutes,
                enabled=False,  # Disabled by default for safety
                name=f"Every {interval_minutes} minutes"
            )
        elif schedule_type == ScheduleType.DAILY:
            schedule = ScanSchedule(
                schedule_type=schedule_type,
                daily_time=time_str,
                enabled=False,  # Disabled by default for safety
                name=f"Daily at {time_str}"
            )
        
        self.scanner.schedules.append(schedule)
        self.load_current_config()
    
    def test_manual_scan(self):
        """Test manual scan with current settings"""
        if not self.scanner.targets:
            QMessageBox.information(self, "No Targets", "Please add at least one target to test scanning.")
            return
        
        # Get first enabled target or first target
        target = None
        for t in self.scanner.targets:
            if t.enabled:
                target = t
                break
        
        if not target and self.scanner.targets:
            target = self.scanner.targets[0]
        
        if target:
            QMessageBox.information(self, "Test Started", 
                                  f"Test scan started for: {target.name}\\nCheck the main window log for progress.")
            self.scanner.manual_scan_target(target)
        else:
            QMessageBox.warning(self, "No Target", "No suitable target found for testing.")
    
    def save_configuration(self):
        """Save configuration and close dialog"""
        try:
            self.scanner.save_configuration()
            QMessageBox.information(self, "Success", "Configuration saved successfully!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save configuration: {e}")

class TargetEditDialog(QDialog):
    """Dialog for editing scan targets"""
    
    def __init__(self, target: Optional[AutoScanTarget], parent=None):
        super().__init__(parent)
        self.target = target
        self.setWindowTitle("Edit Scan Target" if target else "Add Scan Target")
        self.setModal(True)
        self.init_ui()
        
        if target:
            self.load_target_data()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout()
        
        # Name
        layout.addWidget(QLabel("Target Name:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g., Office Network, Server Subnet")
        layout.addWidget(self.name_edit)
        
        # Network range
        layout.addWidget(QLabel("Network Range:"))
        self.network_edit = QLineEdit()
        self.network_edit.setPlaceholderText("e.g., 192.168.1.1-50, 10.0.21.0/24")
        layout.addWidget(self.network_edit)
        
        # Enabled checkbox
        self.enabled_check = QCheckBox("Enable this target for automatic scanning")
        layout.addWidget(self.enabled_check)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.btn_ok = QPushButton("OK")
        self.btn_cancel = QPushButton("Cancel")
        
        self.btn_ok.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.btn_ok)
        buttons_layout.addWidget(self.btn_cancel)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
    
    def load_target_data(self):
        """Load existing target data"""
        if self.target:
            self.name_edit.setText(self.target.name)
            self.network_edit.setText(self.target.network_range)
            self.enabled_check.setChecked(self.target.enabled)
    
    def get_target(self) -> AutoScanTarget:
        """Get the configured target"""
        return AutoScanTarget(
            name=self.name_edit.text().strip() or "Unnamed Target",
            network_range=self.network_edit.text().strip(),
            enabled=self.enabled_check.isChecked()
        )

class ScheduleEditDialog(QDialog):
    """Dialog for editing scan schedules"""
    
    def __init__(self, schedule: Optional[ScanSchedule], parent=None):
        super().__init__(parent)
        self.schedule = schedule
        self.setWindowTitle("Edit Schedule" if schedule else "Add Schedule")
        self.setModal(True)
        self.init_ui()
        
        if schedule:
            self.load_schedule_data()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout()
        
        # Name
        layout.addWidget(QLabel("Schedule Name:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g., Hourly scan, Daily morning scan")
        layout.addWidget(self.name_edit)
        
        # Schedule type
        layout.addWidget(QLabel("Schedule Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Interval", "Daily", "Weekly", "Once"])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        layout.addWidget(self.type_combo)
        
        # Interval settings
        self.interval_widget = QWidget()
        interval_layout = QHBoxLayout(self.interval_widget)
        interval_layout.addWidget(QLabel("Every"))
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 1440)  # 1 minute to 24 hours
        self.interval_spin.setValue(30)
        interval_layout.addWidget(self.interval_spin)
        interval_layout.addWidget(QLabel("minutes"))
        layout.addWidget(self.interval_widget)
        
        # Daily settings
        self.daily_widget = QWidget()
        daily_layout = QHBoxLayout(self.daily_widget)
        daily_layout.addWidget(QLabel("Time:"))
        self.daily_time = QTimeEdit()
        self.daily_time.setTime(QTime(9, 0))  # Default 9 AM
        daily_layout.addWidget(self.daily_time)
        layout.addWidget(self.daily_widget)
        
        # Weekly settings
        self.weekly_widget = QWidget()
        weekly_layout = QVBoxLayout(self.weekly_widget)
        weekly_layout.addWidget(QLabel("Days of week:"))
        
        days_layout = QHBoxLayout()
        self.day_checks = []
        for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
            check = QCheckBox(day)
            self.day_checks.append(check)
            days_layout.addWidget(check)
        weekly_layout.addLayout(days_layout)
        
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Time:"))
        self.weekly_time = QTimeEdit()
        self.weekly_time.setTime(QTime(9, 0))
        time_layout.addWidget(self.weekly_time)
        weekly_layout.addLayout(time_layout)
        layout.addWidget(self.weekly_widget)
        
        # Enabled checkbox
        self.enabled_check = QCheckBox("Enable this schedule")
        layout.addWidget(self.enabled_check)
        
        # Update visibility
        self.on_type_changed()
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.btn_ok = QPushButton("OK")
        self.btn_cancel = QPushButton("Cancel")
        
        self.btn_ok.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.btn_ok)
        buttons_layout.addWidget(self.btn_cancel)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
    
    def on_type_changed(self):
        """Handle schedule type change"""
        schedule_type = self.type_combo.currentText().lower()
        
        self.interval_widget.setVisible(schedule_type == "interval")
        self.daily_widget.setVisible(schedule_type == "daily")
        self.weekly_widget.setVisible(schedule_type == "weekly")
    
    def load_schedule_data(self):
        """Load existing schedule data"""
        if not self.schedule:
            return
        
        self.name_edit.setText(self.schedule.name)
        self.enabled_check.setChecked(self.schedule.enabled)
        
        # Set type and type-specific data
        type_map = {
            ScheduleType.INTERVAL: "Interval",
            ScheduleType.DAILY: "Daily", 
            ScheduleType.WEEKLY: "Weekly",
            ScheduleType.ONCE: "Once"
        }
        
        type_text = type_map.get(self.schedule.schedule_type, "Interval")
        self.type_combo.setCurrentText(type_text)
        
        if self.schedule.schedule_type == ScheduleType.INTERVAL:
            self.interval_spin.setValue(self.schedule.interval_minutes)
        elif self.schedule.schedule_type == ScheduleType.DAILY and self.schedule.daily_time:
            time_parts = self.schedule.daily_time.split(":")
            if len(time_parts) == 2:
                hour, minute = int(time_parts[0]), int(time_parts[1])
                self.daily_time.setTime(QTime(hour, minute))
        elif self.schedule.schedule_type == ScheduleType.WEEKLY:
            if self.schedule.weekly_days:
                for day_index in self.schedule.weekly_days:
                    if 0 <= day_index < len(self.day_checks):
                        self.day_checks[day_index].setChecked(True)
            if self.schedule.weekly_time:
                time_parts = self.schedule.weekly_time.split(":")
                if len(time_parts) == 2:
                    hour, minute = int(time_parts[0]), int(time_parts[1])
                    self.weekly_time.setTime(QTime(hour, minute))
    
    def get_schedule(self) -> ScanSchedule:
        """Get the configured schedule"""
        schedule_type_map = {
            "interval": ScheduleType.INTERVAL,
            "daily": ScheduleType.DAILY,
            "weekly": ScheduleType.WEEKLY,
            "once": ScheduleType.ONCE
        }
        
        schedule_type = schedule_type_map[self.type_combo.currentText().lower()]
        name = self.name_edit.text().strip() or "Unnamed Schedule"
        
        schedule = ScanSchedule(
            schedule_type=schedule_type,
            enabled=self.enabled_check.isChecked(),
            name=name
        )
        
        if schedule_type == ScheduleType.INTERVAL:
            schedule.interval_minutes = self.interval_spin.value()
        elif schedule_type == ScheduleType.DAILY:
            time = self.daily_time.time()
            schedule.daily_time = f"{time.hour():02d}:{time.minute():02d}"
        elif schedule_type == ScheduleType.WEEKLY:
            selected_days = []
            for i, check in enumerate(self.day_checks):
                if check.isChecked():
                    selected_days.append(i)
            schedule.weekly_days = selected_days
            time = self.weekly_time.time()
            schedule.weekly_time = f"{time.hour():02d}:{time.minute():02d}"
        
        return schedule

# Export the main classes
__all__ = ['AutomaticScanner', 'AutoScanTarget', 'ScanSchedule', 'ScheduleType', 'PYQT6_AVAILABLE', 'AutoScanConfigDialog']