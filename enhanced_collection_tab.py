#!/usr/bin/env python3
"""
GUI Integration for Enhanced Main Application
تكامل الواجهة الرسومية مع التطبيق الرئيسي المحسن
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QProgressBar, QTextEdit, QGroupBox, QGridLayout,
                           QListWidget, QDialog,
                           QDialogButtonBox)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QFont
from enhanced_collector_gui import EnhancedCollectorGUI

class DeviceEnhancementWorker(QThread):
    """Worker thread for device enhancement"""
    progress = pyqtSignal(int)
    log_message = pyqtSignal(str)
    finished = pyqtSignal(dict)
    
    def __init__(self, collector, device_ids):
        super().__init__()
        self.collector = collector
        self.device_ids = device_ids
        
    def run(self):
        """Run device enhancement"""
        results = {}
        total = len(self.device_ids)
        
        for i, device_id in enumerate(self.device_ids):
            self.log_message.emit(f"Enhancing device {device_id}...")
            
            try:
                success = self.collector.enhance_existing_device(device_id)
                results[device_id] = 'Success' if success else 'Failed'
                
                if success:
                    self.log_message.emit(f"✅ Device {device_id} enhanced successfully")
                else:
                    self.log_message.emit(f"❌ Device {device_id} enhancement failed")
                    
            except Exception as e:
                results[device_id] = f'Error: {str(e)}'
                self.log_message.emit(f"⚠️ Device {device_id} error: {str(e)}")
            
            # Update progress
            progress = int((i + 1) / total * 100)
            self.progress.emit(progress)
        
        self.finished.emit(results)

class IPRangeEnhancementWorker(QThread):
    """Worker thread for IP range enhancement"""
    progress = pyqtSignal(int)
    log_message = pyqtSignal(str)
    finished = pyqtSignal(dict)
    
    def __init__(self, collector, start_ip, end_ip):
        super().__init__()
        self.collector = collector
        self.start_ip = start_ip
        self.end_ip = end_ip
        
    def run(self):
        """Run IP range enhancement"""
        results = self.collector.scan_and_enhance_range(self.start_ip, self.end_ip)
        
        for ip, status in results.items():
            if status == 'Enhanced':
                self.log_message.emit(f"✅ {ip}: Enhanced successfully")
            elif status == 'Failed':
                self.log_message.emit(f"❌ {ip}: Enhancement failed")
            else:
                self.log_message.emit(f"⚠️ {ip}: {status}")
        
        self.progress.emit(100)
        self.finished.emit(results)

class DeviceReportDialog(QDialog):
    """Dialog for displaying comprehensive device report"""
    
    def __init__(self, report, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Device Comprehensive Report - تقرير شامل للجهاز")
        self.setMinimumSize(800, 600)
        self.setup_ui(report)
        
    def setup_ui(self, report):
        layout = QVBoxLayout(self)
        
        # Basic Info Group
        basic_group = QGroupBox("Basic Information - المعلومات الأساسية")
        basic_layout = QGridLayout(basic_group)
        
        basic_info = report['basic_info']
        basic_layout.addWidget(QLabel("Hostname:"), 0, 0)
        basic_layout.addWidget(QLabel(str(basic_info['hostname'])), 0, 1)
        basic_layout.addWidget(QLabel("IP Address:"), 1, 0)
        basic_layout.addWidget(QLabel(str(basic_info['ip_address'])), 1, 1)
        basic_layout.addWidget(QLabel("Device Type:"), 2, 0)
        basic_layout.addWidget(QLabel(str(basic_info['device_type'])), 2, 1)
        basic_layout.addWidget(QLabel("Status:"), 3, 0)
        basic_layout.addWidget(QLabel(str(basic_info['status'])), 3, 1)
        
        layout.addWidget(basic_group)
        
        # Scores Group
        scores_group = QGroupBox("Quality Scores - درجات الجودة")
        scores_layout = QGridLayout(scores_group)
        
        scores = report['scores']
        scores_layout.addWidget(QLabel("Data Quality:"), 0, 0)
        scores_layout.addWidget(QLabel(f"{scores['data_quality']}/5"), 0, 1)
        scores_layout.addWidget(QLabel("Performance:"), 1, 0)
        scores_layout.addWidget(QLabel(f"{scores['performance']}/10"), 1, 1)
        scores_layout.addWidget(QLabel("Risk Score:"), 2, 0)
        scores_layout.addWidget(QLabel(f"{scores['risk']}/10"), 2, 1)
        
        layout.addWidget(scores_group)
        
        # Network Info Group
        network_group = QGroupBox("Network Information - معلومات الشبكة")
        network_layout = QVBoxLayout(network_group)
        
        network_info = report['network_info']
        network_text = f"""
Ping Status: {network_info['ping_status']}
Response Time: {network_info['response_time']} ms
Open Ports: {len(network_info.get('open_ports', []))} ports
Services: {len(network_info.get('services', []))} detected services
        """
        network_display = QTextEdit()
        network_display.setPlainText(network_text.strip())
        network_display.setMaximumHeight(100)
        network_layout.addWidget(network_display)
        
        layout.addWidget(network_group)
        
        # System Info Group
        system_group = QGroupBox("System Information - معلومات النظام")
        system_layout = QGridLayout(system_group)
        
        system_info = report['system_info']
        system_layout.addWidget(QLabel("OS:"), 0, 0)
        system_layout.addWidget(QLabel(str(system_info['os_name'])), 0, 1)
        system_layout.addWidget(QLabel("Manufacturer:"), 1, 0)
        system_layout.addWidget(QLabel(str(system_info['manufacturer'])), 1, 1)
        system_layout.addWidget(QLabel("Model:"), 2, 0)
        system_layout.addWidget(QLabel(str(system_info['model'])), 2, 1)
        system_layout.addWidget(QLabel("Processor:"), 3, 0)
        system_layout.addWidget(QLabel(str(system_info['processor'])), 3, 1)
        
        layout.addWidget(system_group)
        
        # Security Group
        security_group = QGroupBox("Security Assessment - تقييم الأمان")
        security_layout = QVBoxLayout(security_group)
        
        security = report['security']
        security_text = f"""
Security Score: {security['security_score']}/10
Firewall Detected: {security['firewall_detected']}
Security Issues: {len(security.get('security_issues', []))} issues found
        """
        security_display = QTextEdit()
        security_display.setPlainText(security_text.strip())
        security_display.setMaximumHeight(80)
        security_layout.addWidget(security_display)
        
        layout.addWidget(security_group)
        
        # Collection Info Group
        collection_group = QGroupBox("Collection Information - معلومات الجمع")
        collection_layout = QGridLayout(collection_group)
        
        collection = report['collection_info']
        collection_layout.addWidget(QLabel("Method:"), 0, 0)
        collection_layout.addWidget(QLabel(str(collection['method'])), 0, 1)
        collection_layout.addWidget(QLabel("Source:"), 1, 0)
        collection_layout.addWidget(QLabel(str(collection['source'])), 1, 1)
        collection_layout.addWidget(QLabel("Scan Date:"), 2, 0)
        collection_layout.addWidget(QLabel(str(collection['scan_date'])), 2, 1)
        
        layout.addWidget(collection_group)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

class EnhancedDataCollectionTab(QWidget):
    """Enhanced Data Collection Tab for the main GUI"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.collector = EnhancedCollectorGUI()
        self.enhancement_worker = None
        self.range_worker = None
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Enhanced Data Collection - جمع البيانات المحسن")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Device Enhancement Section
        device_group = QGroupBox("Device Enhancement - تحسين الأجهزة")
        device_layout = QVBoxLayout(device_group)
        
        # Device list and controls
        device_controls = QHBoxLayout()
        
        self.device_list = QListWidget()
        self.device_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        device_controls.addWidget(self.device_list)
        
        device_buttons = QVBoxLayout()
        self.refresh_devices_btn = QPushButton("Refresh Device List\nتحديث قائمة الأجهزة")
        self.enhance_selected_btn = QPushButton("Enhance Selected\nتحسين المحدد")
        self.enhance_all_btn = QPushButton("Enhance All Devices\nتحسين جميع الأجهزة")
        self.view_report_btn = QPushButton("View Device Report\nعرض تقرير الجهاز")
        
        device_buttons.addWidget(self.refresh_devices_btn)
        device_buttons.addWidget(self.enhance_selected_btn)
        device_buttons.addWidget(self.enhance_all_btn)
        device_buttons.addWidget(self.view_report_btn)
        device_buttons.addStretch()
        
        device_controls.addLayout(device_buttons)
        device_layout.addLayout(device_controls)
        
        layout.addWidget(device_group)
        
        # IP Range Enhancement Section
        range_group = QGroupBox("IP Range Enhancement - تحسين نطاق IP")
        range_layout = QVBoxLayout(range_group)
        
        range_controls = QHBoxLayout()
        range_controls.addWidget(QLabel("Start IP:"))
        self.start_ip_edit = QLabel("10.0.21.1")
        range_controls.addWidget(self.start_ip_edit)
        
        range_controls.addWidget(QLabel("End IP:"))
        self.end_ip_edit = QLabel("10.0.21.50")
        range_controls.addWidget(self.end_ip_edit)
        
        self.scan_range_btn = QPushButton("Scan & Enhance Range\nفحص وتحسين النطاق")
        range_controls.addWidget(self.scan_range_btn)
        range_controls.addStretch()
        
        range_layout.addLayout(range_controls)
        layout.addWidget(range_group)
        
        # Progress Section
        progress_group = QGroupBox("Enhancement Progress - تقدم التحسين")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        self.log_display = QTextEdit()
        self.log_display.setMaximumHeight(200)
        self.log_display.setPlainText("Ready for device enhancement...")
        progress_layout.addWidget(self.log_display)
        
        layout.addWidget(progress_group)
        
        # Connect signals\n        self.refresh_devices_btn.clicked.connect(self.refresh_device_list)\n        self.enhance_selected_btn.clicked.connect(self.enhance_selected_devices)\n        self.enhance_all_btn.clicked.connect(self.enhance_all_devices)\n        self.view_report_btn.clicked.connect(self.view_device_report)\n        self.scan_range_btn.clicked.connect(self.scan_ip_range)\n        \n        # Load initial device list\n        self.refresh_device_list()\n        \n    def refresh_device_list(self):\n        \"\"\"Refresh the device list from database\"\"\"\n        try:\n            self.device_list.clear()\n            \n            conn = sqlite3.connect(\"assets.db\")\n            cursor = conn.cursor()\n            \n            cursor.execute(\"\"\"\n                SELECT id, hostname, ip_address, device_type, data_quality_score, last_updated\n                FROM assets \n                ORDER BY id\n            \"\"\")\n            \n            for row in cursor.fetchall():\n                device_id, hostname, ip_address, device_type, quality_score, last_updated = row\n                \n                # Create display text\n                display_text = f\"ID: {device_id} | {hostname or 'Unknown'} ({ip_address}) | {device_type or 'Unknown'}\"\n                if quality_score:\n                    display_text += f\" | Quality: {quality_score}/5\"\n                if last_updated:\n                    display_text += f\" | Updated: {last_updated[:10]}\"\n                \n                item = QListWidgetItem(display_text)\n                item.setData(Qt.ItemDataRole.UserRole, device_id)\n                self.device_list.addItem(item)\n            \n            conn.close()\n            self.log_message(f\"Loaded {self.device_list.count()} devices from database\")\n            \n        except Exception as e:\n            self.log_message(f\"Error refreshing device list: {str(e)}\")\n    \n    def enhance_selected_devices(self):\n        \"\"\"Enhance selected devices\"\"\"\n        selected_items = self.device_list.selectedItems()\n        if not selected_items:\n            QMessageBox.warning(self, \"Warning\", \"Please select devices to enhance\")\n            return\n        \n        device_ids = [item.data(Qt.ItemDataRole.UserRole) for item in selected_items]\n        self.start_device_enhancement(device_ids)\n    \n    def enhance_all_devices(self):\n        \"\"\"Enhance all devices\"\"\"\n        device_ids = []\n        for i in range(self.device_list.count()):\n            item = self.device_list.item(i)\n            device_ids.append(item.data(Qt.ItemDataRole.UserRole))\n        \n        if not device_ids:\n            QMessageBox.warning(self, \"Warning\", \"No devices found to enhance\")\n            return\n        \n        self.start_device_enhancement(device_ids)\n    \n    def start_device_enhancement(self, device_ids):\n        \"\"\"Start device enhancement in background thread\"\"\"\n        if self.enhancement_worker and self.enhancement_worker.isRunning():\n            QMessageBox.information(self, \"Info\", \"Enhancement already in progress\")\n            return\n        \n        self.progress_bar.setVisible(True)\n        self.progress_bar.setValue(0)\n        self.log_display.clear()\n        self.log_message(f\"Starting enhancement for {len(device_ids)} devices...\")\n        \n        # Disable buttons\n        self.enhance_selected_btn.setEnabled(False)\n        self.enhance_all_btn.setEnabled(False)\n        self.scan_range_btn.setEnabled(False)\n        \n        # Start worker thread\n        self.enhancement_worker = DeviceEnhancementWorker(self.collector, device_ids)\n        self.enhancement_worker.progress.connect(self.progress_bar.setValue)\n        self.enhancement_worker.log_message.connect(self.log_message)\n        self.enhancement_worker.finished.connect(self.enhancement_finished)\n        self.enhancement_worker.start()\n    \n    def enhancement_finished(self, results):\n        \"\"\"Handle enhancement completion\"\"\"\n        self.progress_bar.setVisible(False)\n        \n        # Re-enable buttons\n        self.enhance_selected_btn.setEnabled(True)\n        self.enhance_all_btn.setEnabled(True)\n        self.scan_range_btn.setEnabled(True)\n        \n        # Show results\n        success_count = sum(1 for result in results.values() if result == 'Success')\n        total_count = len(results)\n        \n        self.log_message(f\"\\n✅ Enhancement completed: {success_count}/{total_count} devices enhanced successfully\")\n        \n        # Refresh device list to show updated data\n        self.refresh_device_list()\n        \n        QMessageBox.information(self, \"Enhancement Complete\", \n                              f\"Enhancement completed successfully!\\n{success_count}/{total_count} devices enhanced\")\n    \n    def scan_ip_range(self):\n        \"\"\"Scan and enhance IP range\"\"\"\n        if self.range_worker and self.range_worker.isRunning():\n            QMessageBox.information(self, \"Info\", \"Range scan already in progress\")\n            return\n        \n        start_ip = self.start_ip_edit.text()\n        end_ip = self.end_ip_edit.text()\n        \n        self.progress_bar.setVisible(True)\n        self.progress_bar.setValue(0)\n        self.log_display.clear()\n        self.log_message(f\"Starting IP range scan: {start_ip} to {end_ip}...\")\n        \n        # Disable buttons\n        self.enhance_selected_btn.setEnabled(False)\n        self.enhance_all_btn.setEnabled(False)\n        self.scan_range_btn.setEnabled(False)\n        \n        # Start worker thread\n        self.range_worker = IPRangeEnhancementWorker(self.collector, start_ip, end_ip)\n        self.range_worker.progress.connect(self.progress_bar.setValue)\n        self.range_worker.log_message.connect(self.log_message)\n        self.range_worker.finished.connect(self.range_scan_finished)\n        self.range_worker.start()\n    \n    def range_scan_finished(self, results):\n        \"\"\"Handle range scan completion\"\"\"\n        self.progress_bar.setVisible(False)\n        \n        # Re-enable buttons\n        self.enhance_selected_btn.setEnabled(True)\n        self.enhance_all_btn.setEnabled(True)\n        self.scan_range_btn.setEnabled(True)\n        \n        # Show results\n        if 'error' in results:\n            self.log_message(f\"❌ Range scan failed: {results['error']}\")\n            QMessageBox.warning(self, \"Scan Failed\", f\"Range scan failed: {results['error']}\")\n        else:\n            enhanced_count = sum(1 for result in results.values() if result == 'Enhanced')\n            total_count = len(results)\n            \n            self.log_message(f\"\\n✅ Range scan completed: {enhanced_count}/{total_count} devices enhanced\")\n            \n            # Refresh device list\n            self.refresh_device_list()\n            \n            QMessageBox.information(self, \"Range Scan Complete\", \n                                  f\"Range scan completed!\\n{enhanced_count}/{total_count} devices enhanced\")\n    \n    def view_device_report(self):\n        \"\"\"View detailed report for selected device\"\"\"\n        selected_items = self.device_list.selectedItems()\n        if not selected_items:\n            QMessageBox.warning(self, \"Warning\", \"Please select a device to view report\")\n            return\n        \n        if len(selected_items) > 1:\n            QMessageBox.warning(self, \"Warning\", \"Please select only one device for report\")\n            return\n        \n        device_id = selected_items[0].data(Qt.ItemDataRole.UserRole)\n        \n        try:\n            report = self.collector.get_comprehensive_device_report(device_id)\n            if report:\n                dialog = DeviceReportDialog(report, self)\n                dialog.exec()\n            else:\n                QMessageBox.warning(self, \"Error\", \"Failed to generate device report\")\n                \n        except Exception as e:\n            QMessageBox.critical(self, \"Error\", f\"Error generating report: {str(e)}\")\n    \n    def log_message(self, message):\n        \"\"\"Add message to log display\"\"\"\n        self.log_display.append(f\"[{datetime.now().strftime('%H:%M:%S')}] {message}\")\n        self.log_display.ensureCursorVisible()