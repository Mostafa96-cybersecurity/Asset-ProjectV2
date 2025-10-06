# -*- coding: utf-8 -*-
"""
Real-time Logs Monitor
---------------------
Live monitoring of system logs with filtering and search capabilities
"""

import os
import threading
import time
from datetime import datetime
from PyQt6.QtCore import QTimer, QObject, pyqtSignal
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTextEdit, QComboBox, QLineEdit,
                             QGroupBox, QTabWidget, QTableWidget,
                             QTableWidgetItem, QHeaderView)
from PyQt6.QtGui import QFont, QTextCursor, QColor


class LogMonitor(QObject):
    """Real-time log file monitoring"""
    
    log_updated = pyqtSignal(str, str, str)  # timestamp, level, message
    
    def __init__(self):
        super().__init__()
        self.monitoring = True
        self.log_files = {
            'Enhanced Collector': 'enhanced_asset_collector.log',
            'Web Service': 'web_service.log', 
            'Production Web': 'production_web_service.log',
            'System': 'system.log'
        }
        self.file_positions = {}
        self.start_monitoring()
    
    def start_monitoring(self):
        """Start monitoring log files"""
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                for log_name, log_file in self.log_files.items():
                    if os.path.exists(log_file):
                        self._check_log_file(log_name, log_file)
                time.sleep(1)  # Check every second
            except Exception as e:
                print(f"Log monitoring error: {e}")
    
    def _check_log_file(self, log_name: str, log_file: str):
        """Check individual log file for new content"""
        try:
            current_size = os.path.getsize(log_file)
            last_position = self.file_positions.get(log_file, 0)
            
            if current_size > last_position:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    f.seek(last_position)
                    new_lines = f.readlines()
                    
                    for line in new_lines:
                        line = line.strip()
                        if line:
                            timestamp = datetime.now().strftime('%H:%M:%S')
                            level = self._extract_log_level(line)
                            message = f"[{log_name}] {line}"
                            self.log_updated.emit(timestamp, level, message)
                
                self.file_positions[log_file] = current_size
        except Exception:
            pass  # Ignore file access errors
    
    def _extract_log_level(self, line: str) -> str:
        """Extract log level from line"""
        line_upper = line.upper()
        if 'ERROR' in line_upper or 'FAIL' in line_upper:
            return 'ERROR'
        elif 'WARN' in line_upper:
            return 'WARNING'
        elif 'INFO' in line_upper or 'SUCCESS' in line_upper:
            return 'INFO'
        elif 'DEBUG' in line_upper:
            return 'DEBUG'
        else:
            return 'INFO'


class LogsMonitorWidget(QWidget):
    """Enhanced logs monitoring widget with real-time updates"""
    
    def __init__(self):
        super().__init__()
        self.log_monitor = LogMonitor()
        self.log_buffer = []
        self.max_log_entries = 5000
        self.init_ui()
        self.connect_signals()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # Control panel
        control_panel = self.create_control_panel()
        layout.addWidget(control_panel)
        
        # Create tabs for different log views
        self.tab_widget = QTabWidget()
        
        # Real-time logs tab
        self.realtime_tab = self.create_realtime_tab()
        self.tab_widget.addTab(self.realtime_tab, "📊 Real-time Logs")
        
        # System performance tab
        self.performance_tab = self.create_performance_tab()
        self.tab_widget.addTab(self.performance_tab, "⚡ Performance Monitor")
        
        # Error analysis tab
        self.error_tab = self.create_error_analysis_tab()
        self.tab_widget.addTab(self.error_tab, "🔍 Error Analysis")
        
        # Log files tab
        self.files_tab = self.create_log_files_tab()
        self.tab_widget.addTab(self.files_tab, "📁 Log Files")
        
        layout.addWidget(self.tab_widget)
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.update_performance_stats)
        self.refresh_timer.start(2000)  # Update every 2 seconds
    
    def create_control_panel(self):
        """Create control panel with filters and actions"""
        panel = QGroupBox("🎛️ Log Controls")
        layout = QHBoxLayout(panel)
        
        # Log level filter
        layout.addWidget(QLabel("Filter Level:"))
        self.level_filter = QComboBox()
        self.level_filter.addItems(['ALL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'])
        self.level_filter.currentTextChanged.connect(self.filter_logs)
        layout.addWidget(self.level_filter)
        
        # Search box
        layout.addWidget(QLabel("Search:"))
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search in logs...")
        self.search_box.textChanged.connect(self.filter_logs)
        layout.addWidget(self.search_box)
        
        # Clear button
        self.clear_btn = QPushButton("🗑️ Clear Logs")
        self.clear_btn.clicked.connect(self.clear_logs)
        layout.addWidget(self.clear_btn)
        
        # Auto-scroll checkbox
        self.auto_scroll = QPushButton("📜 Auto-scroll: ON")
        self.auto_scroll.setCheckable(True)
        self.auto_scroll.setChecked(True)
        self.auto_scroll.clicked.connect(self.toggle_auto_scroll)
        layout.addWidget(self.auto_scroll)
        
        layout.addStretch()
        return panel
    
    def create_realtime_tab(self):
        """Create real-time logs display"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Stats display
        stats_layout = QHBoxLayout()
        self.total_logs_label = QLabel("📊 Total: 0")
        self.errors_label = QLabel("❌ Errors: 0")
        self.warnings_label = QLabel("⚠️ Warnings: 0")
        self.last_update_label = QLabel("🕒 Last Update: Never")
        
        stats_layout.addWidget(self.total_logs_label)
        stats_layout.addWidget(self.errors_label)
        stats_layout.addWidget(self.warnings_label)
        stats_layout.addWidget(self.last_update_label)
        stats_layout.addStretch()
        
        layout.addLayout(stats_layout)
        
        # Log display
        self.log_display = QTextEdit()
        self.log_display.setFont(QFont("Consolas", 9))
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #3d3d3d;
            }
        """)
        layout.addWidget(self.log_display)
        
        return widget
    
    def create_performance_tab(self):
        """Create performance monitoring display"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Performance metrics
        metrics_group = QGroupBox("📈 System Performance")
        metrics_layout = QVBoxLayout(metrics_group)
        
        self.performance_display = QTextEdit()
        self.performance_display.setFont(QFont("Consolas", 9))
        self.performance_display.setReadOnly(True)
        self.performance_display.setMaximumHeight(200)
        metrics_layout.addWidget(self.performance_display)
        
        layout.addWidget(metrics_group)
        
        # Collection stats
        collection_group = QGroupBox("🔄 Collection Statistics")
        collection_layout = QVBoxLayout(collection_group)
        
        self.collection_stats = QTextEdit()
        self.collection_stats.setFont(QFont("Consolas", 9))
        self.collection_stats.setReadOnly(True)
        collection_layout.addWidget(self.collection_stats)
        
        layout.addWidget(collection_group)
        
        return widget
    
    def create_error_analysis_tab(self):
        """Create error analysis display"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Error summary
        summary_group = QGroupBox("🔍 Error Summary")
        summary_layout = QVBoxLayout(summary_group)
        
        self.error_summary = QTextEdit()
        self.error_summary.setFont(QFont("Consolas", 9))
        self.error_summary.setReadOnly(True)
        self.error_summary.setMaximumHeight(150)
        summary_layout.addWidget(self.error_summary)
        
        layout.addWidget(summary_group)
        
        # Detailed errors table
        errors_group = QGroupBox("📋 Recent Errors")
        errors_layout = QVBoxLayout(errors_group)
        
        self.error_table = QTableWidget()
        self.error_table.setColumnCount(4)
        self.error_table.setHorizontalHeaderLabels(['Time', 'Level', 'Source', 'Message'])
        header = self.error_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        errors_layout.addWidget(self.error_table)
        
        layout.addWidget(errors_group)
        
        return widget
    
    def create_log_files_tab(self):
        """Create log files management tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # File list
        files_group = QGroupBox("📁 Available Log Files")
        files_layout = QVBoxLayout(files_group)
        
        self.file_table = QTableWidget()
        self.file_table.setColumnCount(4)
        self.file_table.setHorizontalHeaderLabels(['File Name', 'Size', 'Last Modified', 'Status'])
        header = self.file_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        files_layout.addWidget(self.file_table)
        
        # File actions
        actions_layout = QHBoxLayout()
        
        self.refresh_files_btn = QPushButton("🔄 Refresh Files")
        self.refresh_files_btn.clicked.connect(self.refresh_log_files)
        actions_layout.addWidget(self.refresh_files_btn)
        
        self.open_file_btn = QPushButton("📖 Open Selected")
        self.open_file_btn.clicked.connect(self.open_selected_file)
        actions_layout.addWidget(self.open_file_btn)
        
        self.archive_btn = QPushButton("📦 Archive Old Logs")
        self.archive_btn.clicked.connect(self.archive_old_logs)
        actions_layout.addWidget(self.archive_btn)
        
        actions_layout.addStretch()
        files_layout.addLayout(actions_layout)
        
        layout.addWidget(files_group)
        
        # Load initial file list
        self.refresh_log_files()
        
        return widget
    
    def connect_signals(self):
        """Connect signals for real-time updates"""
        self.log_monitor.log_updated.connect(self.add_log_entry)
    
    def add_log_entry(self, timestamp: str, level: str, message: str):
        """Add new log entry"""
        self.log_buffer.append({
            'timestamp': timestamp,
            'level': level,
            'message': message,
            'full_timestamp': datetime.now()
        })
        
        # Limit buffer size
        if len(self.log_buffer) > self.max_log_entries:
            self.log_buffer = self.log_buffer[-self.max_log_entries:]
        
        self.update_log_display()
        self.update_stats()
        self.update_error_analysis()
    
    def update_log_display(self):
        """Update the main log display"""
        if not hasattr(self, 'log_display'):
            return
            
        # Apply filters
        filtered_logs = self.apply_filters()
        
        # Update display
        self.log_display.clear()
        for entry in filtered_logs[-1000:]:  # Show last 1000 entries
            color = self.get_level_color(entry['level'])
            formatted_line = f"[{entry['timestamp']}] {entry['level']:8} | {entry['message']}"
            
            self.log_display.setTextColor(color)
            self.log_display.append(formatted_line)
        
        # Auto-scroll if enabled
        if self.auto_scroll.isChecked():
            cursor = self.log_display.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.log_display.setTextCursor(cursor)
    
    def apply_filters(self):
        """Apply current filters to log buffer"""
        filtered = self.log_buffer
        
        # Level filter
        level_filter = self.level_filter.currentText()
        if level_filter != 'ALL':
            filtered = [entry for entry in filtered if entry['level'] == level_filter]
        
        # Search filter
        search_text = self.search_box.text().lower()
        if search_text:
            filtered = [entry for entry in filtered if search_text in entry['message'].lower()]
        
        return filtered
    
    def get_level_color(self, level: str) -> QColor:
        """Get color for log level"""
        colors = {
            'ERROR': QColor(255, 100, 100),     # Red
            'WARNING': QColor(255, 165, 0),      # Orange  
            'INFO': QColor(100, 255, 100),       # Green
            'DEBUG': QColor(150, 150, 255)       # Blue
        }
        return colors.get(level, QColor(255, 255, 255))  # White default
    
    def update_stats(self):
        """Update statistics display"""
        if not self.log_buffer:
            return
            
        total = len(self.log_buffer)
        errors = len([e for e in self.log_buffer if e['level'] == 'ERROR'])
        warnings = len([e for e in self.log_buffer if e['level'] == 'WARNING'])
        last_update = datetime.now().strftime('%H:%M:%S')
        
        self.total_logs_label.setText(f"📊 Total: {total}")
        self.errors_label.setText(f"❌ Errors: {errors}")
        self.warnings_label.setText(f"⚠️ Warnings: {warnings}")
        self.last_update_label.setText(f"🕒 Last Update: {last_update}")
    
    def update_performance_stats(self):
        """Update performance monitoring"""
        try:
            import psutil
            
            # System stats
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('.')
            
            perf_text = f"""
🖥️ CPU Usage: {cpu_percent:.1f}%
🧠 Memory Usage: {memory.percent:.1f}% ({memory.used // (1024**3):.1f} GB / {memory.total // (1024**3):.1f} GB)
💾 Disk Usage: {disk.percent:.1f}% ({disk.used // (1024**3):.1f} GB / {disk.total // (1024**3):.1f} GB)
🌡️ System Load: {'High' if cpu_percent > 80 else 'Normal' if cpu_percent > 50 else 'Low'}
            """
            
            self.performance_display.setText(perf_text.strip())
            
            # Collection stats from database
            self.update_collection_stats()
            
        except ImportError:
            self.performance_display.setText("📊 Performance monitoring requires 'psutil' package")
        except Exception as e:
            self.performance_display.setText(f"❌ Performance monitoring error: {e}")
    
    def update_collection_stats(self):
        """Update collection statistics"""
        try:
            from db.connection import connect
            
            with connect() as conn:
                cursor = conn.cursor()
                
                # Total devices
                cursor.execute("SELECT COUNT(*) FROM assets")
                total_devices = cursor.fetchone()[0]
                
                # Recent collections (last hour)
                cursor.execute("""
                    SELECT COUNT(*) FROM assets 
                    WHERE datetime(updated_at) > datetime('now', '-1 hour')
                """)
                recent_collections = cursor.fetchone()[0]
                
                # OS type distribution
                cursor.execute("""
                    SELECT device_type, COUNT(*) 
                    FROM assets 
                    GROUP BY device_type 
                    ORDER BY COUNT(*) DESC
                """)
                os_distribution = cursor.fetchall()
                
                # Data quality
                cursor.execute("""
                    SELECT COUNT(*) FROM assets 
                    WHERE hostname != ip_address AND hostname NOT LIKE '%.%.%.%'
                """)
                good_hostnames = cursor.fetchone()[0]
                
                stats_text = f"""
📊 Total Devices: {total_devices}
🔄 Recent Collections (1h): {recent_collections}
✅ Good Hostnames: {good_hostnames} / {total_devices} ({(good_hostnames/max(total_devices,1)*100):.1f}%)

📈 Device Type Distribution:
"""
                
                for device_type, count in os_distribution[:5]:
                    percentage = (count / max(total_devices, 1)) * 100
                    stats_text += f"  • {device_type}: {count} ({percentage:.1f}%)\n"
                
                self.collection_stats.setText(stats_text.strip())
                
        except Exception as e:
            self.collection_stats.setText(f"❌ Collection stats error: {e}")
    
    def update_error_analysis(self):
        """Update error analysis tab"""
        recent_errors = [e for e in self.log_buffer if e['level'] == 'ERROR'][-20:]
        
        if recent_errors:
            # Update error summary
            error_types = {}
            for error in recent_errors:
                # Extract error type from message
                if 'WMI' in error['message']:
                    error_types['WMI Connection'] = error_types.get('WMI Connection', 0) + 1
                elif 'database' in error['message'].lower():
                    error_types['Database'] = error_types.get('Database', 0) + 1
                elif 'network' in error['message'].lower():
                    error_types['Network'] = error_types.get('Network', 0) + 1
                else:
                    error_types['Other'] = error_types.get('Other', 0) + 1
            
            summary_text = "🔍 Error Categories (Last 20 errors):\n\n"
            for error_type, count in error_types.items():
                summary_text += f"• {error_type}: {count}\n"
            
            self.error_summary.setText(summary_text)
            
            # Update error table
            self.error_table.setRowCount(len(recent_errors))
            for i, error in enumerate(recent_errors):
                self.error_table.setItem(i, 0, QTableWidgetItem(error['timestamp']))
                self.error_table.setItem(i, 1, QTableWidgetItem(error['level']))
                
                # Extract source from message
                source = "System"
                if '[' in error['message'] and ']' in error['message']:
                    source = error['message'].split('[')[1].split(']')[0]
                
                self.error_table.setItem(i, 2, QTableWidgetItem(source))
                self.error_table.setItem(i, 3, QTableWidgetItem(error['message'][:100]))
    
    def refresh_log_files(self):
        """Refresh log files list"""
        log_files = []
        
        # Common log file patterns
        for file_pattern in ['*.log', '*log.txt', 'logs/*.log']:
            import glob
            log_files.extend(glob.glob(file_pattern))
        
        self.file_table.setRowCount(len(log_files))
        
        for i, file_path in enumerate(log_files):
            try:
                stat_info = os.stat(file_path)
                size_mb = stat_info.st_size / (1024 * 1024)
                modified = datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M')
                status = "✅ Active" if file_path in self.log_monitor.log_files.values() else "📄 Available"
                
                self.file_table.setItem(i, 0, QTableWidgetItem(os.path.basename(file_path)))
                self.file_table.setItem(i, 1, QTableWidgetItem(f"{size_mb:.2f} MB"))
                self.file_table.setItem(i, 2, QTableWidgetItem(modified))
                self.file_table.setItem(i, 3, QTableWidgetItem(status))
                
            except Exception as e:
                self.file_table.setItem(i, 0, QTableWidgetItem(os.path.basename(file_path)))
                self.file_table.setItem(i, 1, QTableWidgetItem("Error"))
                self.file_table.setItem(i, 2, QTableWidgetItem("Error"))
                self.file_table.setItem(i, 3, QTableWidgetItem(f"❌ {str(e)[:20]}..."))
    
    def filter_logs(self):
        """Apply filters and update display"""
        self.update_log_display()
    
    def clear_logs(self):
        """Clear log buffer and display"""
        self.log_buffer.clear()
        self.log_display.clear()
        self.update_stats()
    
    def toggle_auto_scroll(self):
        """Toggle auto-scroll functionality"""
        if self.auto_scroll.isChecked():
            self.auto_scroll.setText("📜 Auto-scroll: ON")
        else:
            self.auto_scroll.setText("📜 Auto-scroll: OFF")
    
    def open_selected_file(self):
        """Open selected log file in system editor"""
        current_row = self.file_table.currentRow()
        if current_row >= 0:
            filename = self.file_table.item(current_row, 0).text()
            try:
                import subprocess
                import sys
                if sys.platform == "win32":
                    os.startfile(filename)
                else:
                    subprocess.call(["xdg-open", filename])
            except Exception as e:
                print(f"Cannot open file: {e}")
    
    def archive_old_logs(self):
        """Archive old log files"""
        # This would implement log archiving functionality
        pass