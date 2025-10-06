#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web Service Control GUI
Professional Web Service Management Interface
===========================================
Complete GUI for web service control and monitoring
"""

import sys
import os
import json
import time
import threading
from datetime import datetime
from typing import Dict, List, Any

try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
except ImportError:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *

from web_service_manager import WebServiceManager

class WebServiceControlWidget(QWidget):
    """Professional Web Service Control Interface"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.manager = WebServiceManager()
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(5000)  # Update every 5 seconds
        
        self.init_ui()
        self.update_status()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # Main title
        title = QLabel("🌐 Web Service Control Center")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin: 10px;")
        layout.addWidget(title)
        
        # Create tab widget for organized sections
        tab_widget = QTabWidget()
        
        # Service Control Tab
        tab_widget.addTab(self.create_service_control_tab(), "🚀 Service Control")
        
        # Security & ACL Tab
        tab_widget.addTab(self.create_security_tab(), "🔒 Security & ACL")
        
        # Monitoring & Logs Tab
        tab_widget.addTab(self.create_monitoring_tab(), "📊 Monitoring & Logs")
        
        # Configuration Tab
        tab_widget.addTab(self.create_configuration_tab(), "⚙️ Configuration")
        
        layout.addWidget(tab_widget)
        
    def create_service_control_tab(self):
        """Create the service control tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Service Status Section
        status_group = QGroupBox("📊 Service Status")
        status_layout = QVBoxLayout()
        
        # Status display
        status_info_layout = QHBoxLayout()
        
        self.status_label = QLabel("Status: Checking...")
        self.status_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        status_info_layout.addWidget(self.status_label)
        
        status_info_layout.addStretch()
        
        self.uptime_label = QLabel("Uptime: N/A")
        status_info_layout.addWidget(self.uptime_label)
        
        status_layout.addLayout(status_info_layout)
        
        # Detailed status
        details_layout = QGridLayout()
        
        self.pid_label = QLabel("PID: N/A")
        self.host_label = QLabel("Host: N/A")
        self.port_label = QLabel("Port: N/A")
        self.memory_label = QLabel("Memory: N/A")
        self.cpu_label = QLabel("CPU: N/A")
        self.connections_label = QLabel("Connections: N/A")
        
        details_layout.addWidget(QLabel("Process ID:"), 0, 0)
        details_layout.addWidget(self.pid_label, 0, 1)
        details_layout.addWidget(QLabel("Host:"), 0, 2)
        details_layout.addWidget(self.host_label, 0, 3)
        details_layout.addWidget(QLabel("Port:"), 1, 0)
        details_layout.addWidget(self.port_label, 1, 1)
        details_layout.addWidget(QLabel("Memory Usage:"), 1, 2)
        details_layout.addWidget(self.memory_label, 1, 3)
        details_layout.addWidget(QLabel("CPU Usage:"), 2, 0)
        details_layout.addWidget(self.cpu_label, 2, 1)
        details_layout.addWidget(QLabel("Connections:"), 2, 2)
        details_layout.addWidget(self.connections_label, 2, 3)
        
        status_layout.addLayout(details_layout)
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Service Control Buttons
        control_group = QGroupBox("🎮 Service Control")
        control_layout = QVBoxLayout()
        
        buttons_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("🚀 Start Service")
        self.start_btn.setStyleSheet("QPushButton { background-color: #27ae60; color: white; font-weight: bold; padding: 8px; }")
        self.start_btn.clicked.connect(self.start_service)
        
        self.stop_btn = QPushButton("⏹️ Stop Service")
        self.stop_btn.setStyleSheet("QPushButton { background-color: #e74c3c; color: white; font-weight: bold; padding: 8px; }")
        self.stop_btn.clicked.connect(self.stop_service)
        
        self.restart_btn = QPushButton("🔄 Restart Service")
        self.restart_btn.setStyleSheet("QPushButton { background-color: #f39c12; color: white; font-weight: bold; padding: 8px; }")
        self.restart_btn.clicked.connect(self.restart_service)
        
        buttons_layout.addWidget(self.start_btn)
        buttons_layout.addWidget(self.stop_btn)
        buttons_layout.addWidget(self.restart_btn)
        
        control_layout.addLayout(buttons_layout)
        
        # Quick Actions
        quick_actions_layout = QHBoxLayout()
        
        clear_cache_btn = QPushButton("🧹 Clear Cache")
        clear_cache_btn.clicked.connect(self.clear_cache)
        
        clear_sessions_btn = QPushButton("👥 Clear Sessions")
        clear_sessions_btn.clicked.connect(self.clear_sessions)
        
        clear_connections_btn = QPushButton("🔌 Clear Connections")
        clear_connections_btn.clicked.connect(self.clear_connections)
        
        quick_actions_layout.addWidget(clear_cache_btn)
        quick_actions_layout.addWidget(clear_sessions_btn)
        quick_actions_layout.addWidget(clear_connections_btn)
        
        control_layout.addLayout(quick_actions_layout)
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # Service URL Access
        access_group = QGroupBox("🌐 Service Access")
        access_layout = QVBoxLayout()
        
        self.service_url_label = QLabel("Service URL: Not Running")
        access_layout.addWidget(self.service_url_label)
        
        url_buttons_layout = QHBoxLayout()
        
        self.open_browser_btn = QPushButton("🌍 Open in Browser")
        self.open_browser_btn.clicked.connect(self.open_in_browser)
        self.open_browser_btn.setEnabled(False)
        
        self.copy_url_btn = QPushButton("📋 Copy URL")
        self.copy_url_btn.clicked.connect(self.copy_url)
        self.copy_url_btn.setEnabled(False)
        
        url_buttons_layout.addWidget(self.open_browser_btn)
        url_buttons_layout.addWidget(self.copy_url_btn)
        url_buttons_layout.addStretch()
        
        access_layout.addLayout(url_buttons_layout)
        access_group.setLayout(access_layout)
        layout.addWidget(access_group)
        
        layout.addStretch()
        return widget
        
    def create_security_tab(self):
        """Create the security and ACL tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # User Management Section
        users_group = QGroupBox("👥 User Management")
        users_layout = QVBoxLayout()
        
        # User list
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(5)
        self.users_table.setHorizontalHeaderLabels(["Username", "Role", "Permissions", "Last Login", "Status"])
        self.users_table.horizontalHeader().setStretchLastSection(True)
        users_layout.addWidget(self.users_table)
        
        # User management buttons
        user_buttons_layout = QHBoxLayout()
        
        add_user_btn = QPushButton("➕ Add User")
        add_user_btn.clicked.connect(self.add_user_dialog)
        
        edit_user_btn = QPushButton("✏️ Edit User")
        edit_user_btn.clicked.connect(self.edit_user_dialog)
        
        remove_user_btn = QPushButton("❌ Remove User")
        remove_user_btn.clicked.connect(self.remove_user)
        
        user_buttons_layout.addWidget(add_user_btn)
        user_buttons_layout.addWidget(edit_user_btn)
        user_buttons_layout.addWidget(remove_user_btn)
        user_buttons_layout.addStretch()
        
        users_layout.addLayout(user_buttons_layout)
        users_group.setLayout(users_layout)
        layout.addWidget(users_group)
        
        # IP Restrictions Section
        ip_group = QGroupBox("🛡️ IP Access Control")
        ip_layout = QVBoxLayout()
        
        # Allowed IPs
        allowed_layout = QVBoxLayout()
        allowed_layout.addWidget(QLabel("Allowed IP Addresses:"))
        
        self.allowed_ips_text = QTextEdit()
        self.allowed_ips_text.setMaximumHeight(100)
        self.allowed_ips_text.setPlaceholderText("Enter allowed IP addresses, one per line (e.g., 192.168.1.100, 10.0.0.0/24)")
        allowed_layout.addWidget(self.allowed_ips_text)
        
        # Blocked IPs
        blocked_layout = QVBoxLayout()
        blocked_layout.addWidget(QLabel("Blocked IP Addresses:"))
        
        self.blocked_ips_text = QTextEdit()
        self.blocked_ips_text.setMaximumHeight(100)
        self.blocked_ips_text.setPlaceholderText("Enter blocked IP addresses, one per line")
        blocked_layout.addWidget(self.blocked_ips_text)
        
        ip_content_layout = QHBoxLayout()
        ip_content_layout.addLayout(allowed_layout)
        ip_content_layout.addLayout(blocked_layout)
        
        ip_layout.addLayout(ip_content_layout)
        
        # IP control buttons
        ip_buttons_layout = QHBoxLayout()
        
        update_ips_btn = QPushButton("💾 Update IP Restrictions")
        update_ips_btn.clicked.connect(self.update_ip_restrictions)
        
        disable_ip_restrictions_btn = QPushButton("🔓 Disable IP Restrictions")
        disable_ip_restrictions_btn.clicked.connect(self.disable_ip_restrictions)
        
        ip_buttons_layout.addWidget(update_ips_btn)
        ip_buttons_layout.addWidget(disable_ip_restrictions_btn)
        ip_buttons_layout.addStretch()
        
        ip_layout.addLayout(ip_buttons_layout)
        ip_group.setLayout(ip_layout)
        layout.addWidget(ip_group)
        
        # Security Settings
        security_group = QGroupBox("🔐 Security Settings")
        security_layout = QVBoxLayout()
        
        # Security options
        self.auth_required_cb = QCheckBox("Require Authentication")
        self.rate_limiting_cb = QCheckBox("Enable Rate Limiting")
        self.ssl_enabled_cb = QCheckBox("Enable SSL/HTTPS")
        
        security_layout.addWidget(self.auth_required_cb)
        security_layout.addWidget(self.rate_limiting_cb)
        security_layout.addWidget(self.ssl_enabled_cb)
        
        # Security parameters
        security_params_layout = QGridLayout()
        
        security_params_layout.addWidget(QLabel("Session Timeout (seconds):"), 0, 0)
        self.session_timeout_spin = QSpinBox()
        self.session_timeout_spin.setRange(300, 86400)  # 5 minutes to 24 hours
        self.session_timeout_spin.setValue(3600)
        security_params_layout.addWidget(self.session_timeout_spin, 0, 1)
        
        security_params_layout.addWidget(QLabel("Max Login Attempts:"), 1, 0)
        self.max_attempts_spin = QSpinBox()
        self.max_attempts_spin.setRange(1, 20)
        self.max_attempts_spin.setValue(5)
        security_params_layout.addWidget(self.max_attempts_spin, 1, 1)
        
        security_params_layout.addWidget(QLabel("Rate Limit (req/min):"), 2, 0)
        self.rate_limit_spin = QSpinBox()
        self.rate_limit_spin.setRange(1, 1000)
        self.rate_limit_spin.setValue(60)
        security_params_layout.addWidget(self.rate_limit_spin, 2, 1)
        
        security_layout.addLayout(security_params_layout)
        
        # Save security settings
        save_security_btn = QPushButton("💾 Save Security Settings")
        save_security_btn.clicked.connect(self.save_security_settings)
        security_layout.addWidget(save_security_btn)
        
        security_group.setLayout(security_layout)
        layout.addWidget(security_group)
        
        layout.addStretch()
        return widget
        
    def create_monitoring_tab(self):
        """Create the monitoring and logs tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Real-time Logs Section
        logs_group = QGroupBox("📋 Real-time Service Logs")
        logs_layout = QVBoxLayout()
        
        # Log display
        self.logs_text = QTextEdit()
        self.logs_text.setFont(QFont("Consolas", 10))
        self.logs_text.setStyleSheet("background-color: #2c3e50; color: #ecf0f1;")
        self.logs_text.setPlaceholderText("Service logs will appear here...")
        logs_layout.addWidget(self.logs_text)
        
        # Log controls
        log_controls_layout = QHBoxLayout()
        
        refresh_logs_btn = QPushButton("🔄 Refresh Logs")
        refresh_logs_btn.clicked.connect(self.refresh_logs)
        
        clear_logs_btn = QPushButton("🧹 Clear Logs")
        clear_logs_btn.clicked.connect(self.clear_logs)
        
        export_logs_btn = QPushButton("📤 Export Logs")
        export_logs_btn.clicked.connect(self.export_logs)
        
        # Log level filter
        log_controls_layout.addWidget(QLabel("Show:"))
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["All", "ERROR", "WARNING", "INFO", "DEBUG"])
        self.log_level_combo.currentTextChanged.connect(self.filter_logs)
        
        log_controls_layout.addWidget(self.log_level_combo)
        log_controls_layout.addStretch()
        log_controls_layout.addWidget(refresh_logs_btn)
        log_controls_layout.addWidget(clear_logs_btn)
        log_controls_layout.addWidget(export_logs_btn)
        
        logs_layout.addLayout(log_controls_layout)
        logs_group.setLayout(logs_layout)
        layout.addWidget(logs_group)
        
        # Performance Metrics Section
        metrics_group = QGroupBox("📈 Performance Metrics")
        metrics_layout = QVBoxLayout()
        
        # Metrics display
        metrics_grid = QGridLayout()
        
        self.requests_total_label = QLabel("Total Requests: 0")
        self.requests_per_minute_label = QLabel("Requests/min: 0")
        self.response_time_label = QLabel("Avg Response Time: 0ms")
        self.error_rate_label = QLabel("Error Rate: 0%")
        self.active_sessions_label = QLabel("Active Sessions: 0")
        self.bandwidth_label = QLabel("Bandwidth: 0 KB/s")
        
        metrics_grid.addWidget(self.requests_total_label, 0, 0)
        metrics_grid.addWidget(self.requests_per_minute_label, 0, 1)
        metrics_grid.addWidget(self.response_time_label, 1, 0)
        metrics_grid.addWidget(self.error_rate_label, 1, 1)
        metrics_grid.addWidget(self.active_sessions_label, 2, 0)
        metrics_grid.addWidget(self.bandwidth_label, 2, 1)
        
        metrics_layout.addLayout(metrics_grid)
        
        # Reset metrics button
        reset_metrics_btn = QPushButton("🔄 Reset Metrics")
        reset_metrics_btn.clicked.connect(self.reset_metrics)
        metrics_layout.addWidget(reset_metrics_btn)
        
        metrics_group.setLayout(metrics_layout)
        layout.addWidget(metrics_group)
        
        layout.addStretch()
        return widget
        
    def create_configuration_tab(self):
        """Create the configuration tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Service Configuration Section
        service_group = QGroupBox("⚙️ Service Configuration")
        service_layout = QVBoxLayout()
        
        # Basic settings
        basic_layout = QGridLayout()
        
        basic_layout.addWidget(QLabel("Host:"), 0, 0)
        self.host_edit = QLineEdit()
        self.host_edit.setPlaceholderText("127.0.0.1")
        basic_layout.addWidget(self.host_edit, 0, 1)
        
        basic_layout.addWidget(QLabel("Port:"), 0, 2)
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(5000)
        basic_layout.addWidget(self.port_spin, 0, 3)
        
        basic_layout.addWidget(QLabel("Max Connections:"), 1, 0)
        self.max_connections_spin = QSpinBox()
        self.max_connections_spin.setRange(1, 1000)
        self.max_connections_spin.setValue(100)
        basic_layout.addWidget(self.max_connections_spin, 1, 1)
        
        basic_layout.addWidget(QLabel("Timeout (seconds):"), 1, 2)
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 300)
        self.timeout_spin.setValue(30)
        basic_layout.addWidget(self.timeout_spin, 1, 3)
        
        service_layout.addLayout(basic_layout)
        
        # Advanced settings
        advanced_layout = QVBoxLayout()
        
        self.debug_mode_cb = QCheckBox("Debug Mode")
        self.auto_start_cb = QCheckBox("Auto-start with system")
        
        advanced_layout.addWidget(self.debug_mode_cb)
        advanced_layout.addWidget(self.auto_start_cb)
        
        service_layout.addLayout(advanced_layout)
        
        # Configuration buttons
        config_buttons_layout = QHBoxLayout()
        
        save_config_btn = QPushButton("💾 Save Configuration")
        save_config_btn.clicked.connect(self.save_configuration)
        
        reset_config_btn = QPushButton("🔄 Reset to Defaults")
        reset_config_btn.clicked.connect(self.reset_configuration)
        
        config_buttons_layout.addWidget(save_config_btn)
        config_buttons_layout.addWidget(reset_config_btn)
        config_buttons_layout.addStretch()
        
        service_layout.addLayout(config_buttons_layout)
        service_group.setLayout(service_layout)
        layout.addWidget(service_group)
        
        # Import/Export Section
        import_export_group = QGroupBox("📁 Import/Export Configuration")
        import_export_layout = QVBoxLayout()
        
        import_export_buttons_layout = QHBoxLayout()
        
        export_config_btn = QPushButton("📤 Export Configuration")
        export_config_btn.clicked.connect(self.export_configuration)
        
        import_config_btn = QPushButton("📥 Import Configuration")
        import_config_btn.clicked.connect(self.import_configuration)
        
        backup_config_btn = QPushButton("💾 Backup Configuration")
        backup_config_btn.clicked.connect(self.backup_configuration)
        
        import_export_buttons_layout.addWidget(export_config_btn)
        import_export_buttons_layout.addWidget(import_config_btn)
        import_export_buttons_layout.addWidget(backup_config_btn)
        import_export_buttons_layout.addStretch()
        
        import_export_layout.addLayout(import_export_buttons_layout)
        import_export_group.setLayout(import_export_layout)
        layout.addWidget(import_export_group)
        
        layout.addStretch()
        return widget
        
    def update_status(self):
        """Update service status display"""
        try:
            status = self.manager.get_service_status()
            
            if status.get("running", False):
                self.status_label.setText("Status: 🟢 Running")
                self.status_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #27ae60;")
                
                self.start_btn.setEnabled(False)
                self.stop_btn.setEnabled(True)
                self.restart_btn.setEnabled(True)
                self.open_browser_btn.setEnabled(True)
                self.copy_url_btn.setEnabled(True)
                
                # Update details
                self.pid_label.setText(str(status.get("pid", "N/A")))
                self.host_label.setText(status.get("host", "N/A"))
                self.port_label.setText(str(status.get("port", "N/A")))
                self.uptime_label.setText(f"Uptime: {status.get('uptime', 'N/A')}")
                
                if status.get("memory_usage"):
                    self.memory_label.setText(f"{status['memory_usage']:.1f} MB")
                if status.get("cpu_usage"):
                    self.cpu_label.setText(f"{status['cpu_usage']:.1f}%")
                    
                self.connections_label.setText(str(status.get("connections", 0)))
                
                # Update service URL
                host = status.get("host", "127.0.0.1")
                port = status.get("port", 5000)
                self.service_url_label.setText(f"Service URL: http://{host}:{port}")
                
            else:
                self.status_label.setText("Status: 🔴 Stopped")
                self.status_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #e74c3c;")
                
                self.start_btn.setEnabled(True)
                self.stop_btn.setEnabled(False)
                self.restart_btn.setEnabled(False)
                self.open_browser_btn.setEnabled(False)
                self.copy_url_btn.setEnabled(False)
                
                # Clear details
                self.pid_label.setText("N/A")
                self.memory_label.setText("N/A")
                self.cpu_label.setText("N/A")
                self.connections_label.setText("N/A")
                self.uptime_label.setText("Uptime: N/A")
                
                self.service_url_label.setText("Service URL: Not Running")
                
        except Exception as e:
            self.status_label.setText(f"Status: ❌ Error: {str(e)}")
            self.status_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #e74c3c;")
            
    def start_service(self):
        """Start the web service"""
        try:
            self.start_btn.setEnabled(False)
            self.start_btn.setText("🔄 Starting...")
            
            result = self.manager.start_service()
            
            if result.get("success", False):
                QMessageBox.information(self, "Success", f"Service started successfully!\nPID: {result.get('pid')}")
            else:
                QMessageBox.critical(self, "Error", f"Failed to start service:\n{result.get('message')}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start service: {str(e)}")
        finally:
            self.start_btn.setText("🚀 Start Service")
            self.update_status()
            
    def stop_service(self):
        """Stop the web service"""
        try:
            reply = QMessageBox.question(self, "Confirm", "Are you sure you want to stop the web service?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply != QMessageBox.StandardButton.Yes:
                return
                
            self.stop_btn.setEnabled(False)
            self.stop_btn.setText("🔄 Stopping...")
            
            result = self.manager.stop_service()
            
            if result.get("success", False):
                QMessageBox.information(self, "Success", "Service stopped successfully!")
            else:
                QMessageBox.critical(self, "Error", f"Failed to stop service:\n{result.get('message')}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to stop service: {str(e)}")
        finally:
            self.stop_btn.setText("⏹️ Stop Service")
            self.update_status()
            
    def restart_service(self):
        """Restart the web service"""
        try:
            self.restart_btn.setEnabled(False)
            self.restart_btn.setText("🔄 Restarting...")
            
            result = self.manager.restart_service()
            
            if result.get("success", False):
                QMessageBox.information(self, "Success", "Service restarted successfully!")
            else:
                QMessageBox.critical(self, "Error", f"Failed to restart service:\n{result.get('message')}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to restart service: {str(e)}")
        finally:
            self.restart_btn.setText("🔄 Restart Service")
            self.update_status()
            
    def clear_cache(self):
        """Clear service cache"""
        try:
            result = self.manager.clear_cache()
            if result.get("success", False):
                QMessageBox.information(self, "Success", f"Cache cleared successfully!\n{result.get('items_removed', 0)} items removed")
            else:
                QMessageBox.critical(self, "Error", f"Failed to clear cache:\n{result.get('message')}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to clear cache: {str(e)}")
            
    def clear_sessions(self):
        """Clear active sessions"""
        try:
            result = self.manager.clear_sessions()
            if result.get("success", False):
                QMessageBox.information(self, "Success", "All sessions cleared successfully!")
            else:
                QMessageBox.critical(self, "Error", f"Failed to clear sessions:\n{result.get('message')}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to clear sessions: {str(e)}")
            
    def clear_connections(self):
        """Clear connections"""
        try:
            result = self.manager.clear_connections()
            if result.get("success", False):
                QMessageBox.information(self, "Success", f"Connections cleared successfully!\n{result.get('message')}")
            else:
                QMessageBox.critical(self, "Error", f"Failed to clear connections:\n{result.get('message')}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to clear connections: {str(e)}")
            
    def open_in_browser(self):
        """Open service URL in browser"""
        try:
            status = self.manager.get_service_status()
            if status.get("running", False):
                host = status.get("host", "127.0.0.1")
                port = status.get("port", 5000)
                url = f"http://{host}:{port}"
                
                import webbrowser
                webbrowser.open(url)
            else:
                QMessageBox.warning(self, "Warning", "Service is not running!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open browser: {str(e)}")
            
    def copy_url(self):
        """Copy service URL to clipboard"""
        try:
            status = self.manager.get_service_status()
            if status.get("running", False):
                host = status.get("host", "127.0.0.1")
                port = status.get("port", 5000)
                url = f"http://{host}:{port}"
                
                QApplication.clipboard().setText(url)
                QMessageBox.information(self, "Success", f"URL copied to clipboard:\n{url}")
            else:
                QMessageBox.warning(self, "Warning", "Service is not running!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to copy URL: {str(e)}")
            
    def refresh_logs(self):
        """Refresh log display"""
        try:
            logs = self.manager.get_logs(lines=500)
            log_text = "\n".join(logs)
            self.logs_text.setPlainText(log_text)
            
            # Scroll to bottom
            cursor = self.logs_text.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.logs_text.setTextCursor(cursor)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to refresh logs: {str(e)}")
            
    def clear_logs(self):
        """Clear logs"""
        try:
            reply = QMessageBox.question(self, "Confirm", "Are you sure you want to clear all logs?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply != QMessageBox.StandardButton.Yes:
                return
                
            result = self.manager.clear_logs()
            if result.get("success", False):
                self.logs_text.clear()
                QMessageBox.information(self, "Success", "Logs cleared successfully!")
            else:
                QMessageBox.critical(self, "Error", f"Failed to clear logs:\n{result.get('message')}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to clear logs: {str(e)}")
            
    def export_logs(self):
        """Export logs to file"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Logs", f"web_service_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                "Text Files (*.txt);;All Files (*)"
            )
            
            if file_path:
                logs = self.manager.get_logs(lines=10000)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("\n".join(logs))
                    
                QMessageBox.information(self, "Success", f"Logs exported to:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export logs: {str(e)}")
            
    def filter_logs(self):
        """Filter logs by level"""
        try:
            level = self.log_level_combo.currentText()
            logs = self.manager.get_logs(lines=500)
            
            if level != "All":
                filtered_logs = [log for log in logs if level in log]
                log_text = "\n".join(filtered_logs)
            else:
                log_text = "\n".join(logs)
                
            self.logs_text.setPlainText(log_text)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to filter logs: {str(e)}")
            
    def reset_metrics(self):
        """Reset performance metrics"""
        try:
            # Reset displayed metrics
            self.requests_total_label.setText("Total Requests: 0")
            self.requests_per_minute_label.setText("Requests/min: 0")
            self.response_time_label.setText("Avg Response Time: 0ms")
            self.error_rate_label.setText("Error Rate: 0%")
            self.active_sessions_label.setText("Active Sessions: 0")
            self.bandwidth_label.setText("Bandwidth: 0 KB/s")
            
            QMessageBox.information(self, "Success", "Performance metrics reset!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to reset metrics: {str(e)}")
            
    def add_user_dialog(self):
        """Show add user dialog"""
        dialog = AddUserDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            user_data = dialog.get_user_data()
            result = self.manager.add_user(**user_data)
            
            if result.get("success", False):
                QMessageBox.information(self, "Success", result.get("message"))
                self.update_users_table()
            else:
                QMessageBox.critical(self, "Error", result.get("message"))
                
    def edit_user_dialog(self):
        """Show edit user dialog"""
        # Implementation for editing users
        QMessageBox.information(self, "Feature", "Edit user functionality coming soon!")
        
    def remove_user(self):
        """Remove selected user"""
        current_row = self.users_table.currentRow()
        if current_row >= 0:
            username = self.users_table.item(current_row, 0).text()
            
            reply = QMessageBox.question(self, "Confirm", f"Are you sure you want to remove user '{username}'?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                result = self.manager.remove_user(username)
                
                if result.get("success", False):
                    QMessageBox.information(self, "Success", result.get("message"))
                    self.update_users_table()
                else:
                    QMessageBox.critical(self, "Error", result.get("message"))
        else:
            QMessageBox.warning(self, "Warning", "Please select a user to remove")
            
    def update_users_table(self):
        """Update the users table"""
        try:
            users = self.manager.acl.get("users", {})
            self.users_table.setRowCount(len(users))
            
            for row, (username, user_data) in enumerate(users.items()):
                self.users_table.setItem(row, 0, QTableWidgetItem(username))
                self.users_table.setItem(row, 1, QTableWidgetItem(user_data.get("role", "user")))
                self.users_table.setItem(row, 2, QTableWidgetItem(", ".join(user_data.get("permissions", []))))
                self.users_table.setItem(row, 3, QTableWidgetItem(user_data.get("last_login", "Never")))
                
                status = "Locked" if user_data.get("locked_until") else "Active"
                self.users_table.setItem(row, 4, QTableWidgetItem(status))
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update users table: {str(e)}")
            
    def update_ip_restrictions(self):
        """Update IP restrictions"""
        try:
            allowed_ips = [ip.strip() for ip in self.allowed_ips_text.toPlainText().split('\n') if ip.strip()]
            blocked_ips = [ip.strip() for ip in self.blocked_ips_text.toPlainText().split('\n') if ip.strip()]
            
            result = self.manager.update_ip_restrictions(allowed_ips, blocked_ips)
            
            if result.get("success", False):
                QMessageBox.information(self, "Success", result.get("message"))
            else:
                QMessageBox.critical(self, "Error", result.get("message"))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update IP restrictions: {str(e)}")
            
    def disable_ip_restrictions(self):
        """Disable IP restrictions"""
        try:
            self.manager.acl["ip_restrictions"]["enabled"] = False
            self.manager.save_acl()
            QMessageBox.information(self, "Success", "IP restrictions disabled")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to disable IP restrictions: {str(e)}")
            
    def save_security_settings(self):
        """Save security settings"""
        try:
            self.manager.config["security"]["auth_required"] = self.auth_required_cb.isChecked()
            self.manager.config["security"]["rate_limiting"] = self.rate_limiting_cb.isChecked()
            self.manager.config["service"]["ssl_enabled"] = self.ssl_enabled_cb.isChecked()
            self.manager.config["security"]["session_timeout"] = self.session_timeout_spin.value()
            self.manager.config["security"]["max_login_attempts"] = self.max_attempts_spin.value()
            self.manager.config["security"]["max_requests_per_minute"] = self.rate_limit_spin.value()
            
            if self.manager.save_config():
                QMessageBox.information(self, "Success", "Security settings saved successfully!")
            else:
                QMessageBox.critical(self, "Error", "Failed to save security settings")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save security settings: {str(e)}")
            
    def save_configuration(self):
        """Save service configuration"""
        try:
            self.manager.config["service"]["host"] = self.host_edit.text() or "127.0.0.1"
            self.manager.config["service"]["port"] = self.port_spin.value()
            self.manager.config["service"]["max_connections"] = self.max_connections_spin.value()
            self.manager.config["service"]["timeout"] = self.timeout_spin.value()
            self.manager.config["service"]["debug"] = self.debug_mode_cb.isChecked()
            self.manager.config["service"]["auto_start"] = self.auto_start_cb.isChecked()
            
            if self.manager.save_config():
                QMessageBox.information(self, "Success", "Configuration saved successfully!")
            else:
                QMessageBox.critical(self, "Error", "Failed to save configuration")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save configuration: {str(e)}")
            
    def reset_configuration(self):
        """Reset configuration to defaults"""
        try:
            reply = QMessageBox.question(self, "Confirm", "Are you sure you want to reset to default configuration?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.manager.config = self.manager.default_config.copy()
                self.manager.save_config()
                self.load_configuration()
                QMessageBox.information(self, "Success", "Configuration reset to defaults!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to reset configuration: {str(e)}")
            
    def export_configuration(self):
        """Export configuration to file"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Configuration", f"web_service_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "JSON Files (*.json);;All Files (*)"
            )
            
            if file_path:
                result = self.manager.export_config(file_path)
                if result.get("success", False):
                    QMessageBox.information(self, "Success", result.get("message"))
                else:
                    QMessageBox.critical(self, "Error", result.get("message"))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export configuration: {str(e)}")
            
    def import_configuration(self):
        """Import configuration from file"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Import Configuration", "",
                "JSON Files (*.json);;All Files (*)"
            )
            
            if file_path:
                result = self.manager.import_config(file_path)
                if result.get("success", False):
                    self.load_configuration()
                    QMessageBox.information(self, "Success", result.get("message"))
                else:
                    QMessageBox.critical(self, "Error", result.get("message"))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to import configuration: {str(e)}")
            
    def backup_configuration(self):
        """Backup current configuration"""
        try:
            backup_path = f"web_service_config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            result = self.manager.export_config(backup_path)
            
            if result.get("success", False):
                QMessageBox.information(self, "Success", f"Configuration backed up to:\n{backup_path}")
            else:
                QMessageBox.critical(self, "Error", result.get("message"))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to backup configuration: {str(e)}")
            
    def load_configuration(self):
        """Load configuration into UI"""
        try:
            config = self.manager.config
            
            # Service settings
            self.host_edit.setText(config["service"].get("host", "127.0.0.1"))
            self.port_spin.setValue(config["service"].get("port", 5000))
            self.max_connections_spin.setValue(config["service"].get("max_connections", 100))
            self.timeout_spin.setValue(config["service"].get("timeout", 30))
            self.debug_mode_cb.setChecked(config["service"].get("debug", False))
            self.auto_start_cb.setChecked(config["service"].get("auto_start", False))
            
            # Security settings
            self.auth_required_cb.setChecked(config["security"].get("auth_required", True))
            self.rate_limiting_cb.setChecked(config["security"].get("rate_limiting", True))
            self.ssl_enabled_cb.setChecked(config["service"].get("ssl_enabled", False))
            self.session_timeout_spin.setValue(config["security"].get("session_timeout", 3600))
            self.max_attempts_spin.setValue(config["security"].get("max_login_attempts", 5))
            self.rate_limit_spin.setValue(config["security"].get("max_requests_per_minute", 60))
            
            # Load IP restrictions
            ip_restrictions = self.manager.acl.get("ip_restrictions", {})
            allowed_ips = ip_restrictions.get("allowed_ips", [])
            blocked_ips = ip_restrictions.get("blocked_ips", [])
            
            self.allowed_ips_text.setPlainText('\n'.join(allowed_ips))
            self.blocked_ips_text.setPlainText('\n'.join(blocked_ips))
            
            # Update users table
            self.update_users_table()
            
            # Refresh logs
            self.refresh_logs()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load configuration: {str(e)}")


class AddUserDialog(QDialog):
    """Dialog for adding new users"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add User")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # User details
        form_layout = QFormLayout()
        
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Enter username")
        form_layout.addRow("Username:", self.username_edit)
        
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setPlaceholderText("Enter password")
        form_layout.addRow("Password:", self.password_edit)
        
        self.role_combo = QComboBox()
        self.role_combo.addItems(["user", "admin", "moderator"])
        form_layout.addRow("Role:", self.role_combo)
        
        layout.addLayout(form_layout)
        
        # Permissions
        permissions_group = QGroupBox("Permissions")
        permissions_layout = QVBoxLayout()
        
        self.read_cb = QCheckBox("Read")
        self.read_cb.setChecked(True)
        self.write_cb = QCheckBox("Write")
        self.admin_cb = QCheckBox("Admin")
        
        permissions_layout.addWidget(self.read_cb)
        permissions_layout.addWidget(self.write_cb)
        permissions_layout.addWidget(self.admin_cb)
        
        permissions_group.setLayout(permissions_layout)
        layout.addWidget(permissions_group)
        
        # Allowed IPs
        ip_layout = QFormLayout()
        self.allowed_ips_edit = QLineEdit()
        self.allowed_ips_edit.setPlaceholderText("* for any IP, or specific IPs separated by commas")
        self.allowed_ips_edit.setText("*")
        ip_layout.addRow("Allowed IPs:", self.allowed_ips_edit)
        layout.addLayout(ip_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        add_btn = QPushButton("Add User")
        add_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(add_btn)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
        
    def get_user_data(self):
        """Get user data from dialog"""
        permissions = []
        if self.read_cb.isChecked():
            permissions.append("read")
        if self.write_cb.isChecked():
            permissions.append("write")
        if self.admin_cb.isChecked():
            permissions.append("admin")
            
        allowed_ips = [ip.strip() for ip in self.allowed_ips_edit.text().split(',') if ip.strip()]
        
        return {
            "username": self.username_edit.text(),
            "password": self.password_edit.text(),
            "role": self.role_combo.currentText(),
            "permissions": permissions,
            "allowed_ips": allowed_ips
        }