#!/usr/bin/env python3
"""
🏢 AD GUI INTEGRATION
===================
Clean AD connectivity GUI for desktop app integration
"""

import sys
import os
import json
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTextEdit, QCheckBox, QGroupBox, QFormLayout,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QProgressBar, QComboBox
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QFont

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class ADConnectionWorker(QThread):
    """Worker thread for AD operations"""
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(bool, dict)
    
    def __init__(self, operation, **kwargs):
        super().__init__()
        self.operation = operation
        self.kwargs = kwargs
    
    def run(self):
        try:
            if self.operation == "test":
                self.test_connection()
            elif self.operation == "fetch":
                self.fetch_computers()
            elif self.operation == "sync":
                self.sync_to_database()
        except Exception as e:
            self.log_signal.emit(f"❌ Error: {e}")
            self.finished_signal.emit(False, {"error": str(e)})
    
    def test_connection(self):
        """Test AD connection"""
        try:
            from ad_fetcher.ad_fetcher import test_ad_connection
            
            self.log_signal.emit("🧪 Testing AD connection...")
            self.progress_signal.emit(25)
            
            success = test_ad_connection(
                self.kwargs['server'],
                self.kwargs['base_dn'],
                self.kwargs['username'],
                self.kwargs['password'],
                self.kwargs.get('use_ssl', False)
            )
            
            self.progress_signal.emit(100)
            
            if success:
                self.log_signal.emit("✅ AD connection test successful!")
                self.finished_signal.emit(True, {"message": "Connection successful"})
            else:
                self.log_signal.emit("❌ AD connection test failed!")
                self.finished_signal.emit(False, {"error": "Connection failed"})
                
        except Exception as e:
            self.log_signal.emit(f"❌ Test error: {e}")
            self.finished_signal.emit(False, {"error": str(e)})
    
    def fetch_computers(self):
        """Fetch computers from AD"""
        try:
            from ad_fetcher.ad_fetcher import ad_fetch_computers
            
            self.log_signal.emit("🔍 Fetching computers from Active Directory...")
            self.progress_signal.emit(25)
            
            computers = ad_fetch_computers(
                self.kwargs['server'],
                self.kwargs['base_dn'],
                self.kwargs['username'],
                self.kwargs['password'],
                self.kwargs.get('use_ssl', False),
                timeout=30,
                store_in_db=True
            )
            
            self.progress_signal.emit(75)
            
            if isinstance(computers, dict) and "Error" in computers:
                self.log_signal.emit(f"❌ Fetch failed: {computers['Error']}")
                self.finished_signal.emit(False, computers)
            else:
                self.log_signal.emit(f"✅ Fetched {len(computers)} computers from AD")
                self.progress_signal.emit(100)
                self.finished_signal.emit(True, {"computers": computers, "count": len(computers)})
                
        except Exception as e:
            self.log_signal.emit(f"❌ Fetch error: {e}")
            self.finished_signal.emit(False, {"error": str(e)})
    
    def sync_to_database(self):
        """Sync AD data to main database"""
        try:
            from ad_fetcher.ad_fetcher import sync_ad_to_database
            
            self.log_signal.emit("🔄 Syncing AD data to main database...")
            self.progress_signal.emit(50)
            
            success = sync_ad_to_database()
            
            self.progress_signal.emit(100)
            
            if success:
                self.log_signal.emit("✅ AD data synced to main database!")
                self.finished_signal.emit(True, {"message": "Sync completed"})
            else:
                self.log_signal.emit("❌ AD sync failed!")
                self.finished_signal.emit(False, {"error": "Sync failed"})
                
        except Exception as e:
            self.log_signal.emit(f"❌ Sync error: {e}")
            self.finished_signal.emit(False, {"error": str(e)})


class ADTab(QWidget):
    """AD integration tab for desktop app"""
    
    def __init__(self):
        super().__init__()
        self.worker = None
        self.computers_data = []
        self.init_ui()
        self.load_saved_settings()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("🏢 Active Directory Integration")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Create tabs
        tabs = QTabWidget()
        
        # Connection tab
        connection_tab = self.create_connection_tab()
        tabs.addTab(connection_tab, "📡 Connection")
        
        # Computers tab
        computers_tab = self.create_computers_tab()
        tabs.addTab(computers_tab, "💻 Computers")
        
        # Statistics tab
        stats_tab = self.create_statistics_tab()
        tabs.addTab(stats_tab, "📊 Statistics")
        
        layout.addWidget(tabs)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Log output
        log_group = QGroupBox("📋 Activity Log")
        log_layout = QVBoxLayout()
        
        self.log_output = QTextEdit()
        self.log_output.setMaximumHeight(150)
        self.log_output.setReadOnly(True)
        log_layout.addWidget(self.log_output)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        self.setLayout(layout)
    
    def create_connection_tab(self):
        """Create AD connection configuration tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Connection settings
        conn_group = QGroupBox("🔐 AD Server Connection")
        conn_layout = QFormLayout()
        
        self.server_input = QLineEdit()
        self.server_input.setPlaceholderText("dc01.domain.com or 192.168.1.10")
        conn_layout.addRow("AD Server:", self.server_input)
        
        self.base_dn_input = QLineEdit()
        self.base_dn_input.setPlaceholderText("DC=domain,DC=com")
        conn_layout.addRow("Base DN:", self.base_dn_input)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("domain\\username or username@domain.com")
        conn_layout.addRow("Username:", self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        conn_layout.addRow("Password:", self.password_input)
        
        self.ssl_checkbox = QCheckBox("Use SSL (LDAPS)")
        conn_layout.addRow("Security:", self.ssl_checkbox)
        
        conn_group.setLayout(conn_layout)
        layout.addWidget(conn_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.test_btn = QPushButton("🧪 Test Connection")
        self.test_btn.clicked.connect(self.test_ad_connection)
        button_layout.addWidget(self.test_btn)
        
        self.fetch_btn = QPushButton("🔍 Fetch Computers")
        self.fetch_btn.clicked.connect(self.fetch_ad_computers)
        button_layout.addWidget(self.fetch_btn)
        
        self.sync_btn = QPushButton("🔄 Sync to Database")
        self.sync_btn.clicked.connect(self.sync_to_database)
        button_layout.addWidget(self.sync_btn)
        
        layout.addLayout(button_layout)
        
        # Save settings button
        save_btn = QPushButton("💾 Save Settings")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)
        
        layout.addStretch()
        widget.setLayout(layout)
        
        return widget
    
    def create_computers_tab(self):
        """Create computers display tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Info label
        info_label = QLabel("💻 Computers found in Active Directory:")
        layout.addWidget(info_label)
        
        # Computers table
        self.computers_table = QTableWidget()
        self.computers_table.setColumnCount(6)
        self.computers_table.setHorizontalHeaderLabels([
            "Hostname", "FQDN", "Operating System", "OS Version", "Created", "Last Logon"
        ])
        
        # Make table responsive
        header = self.computers_table.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.computers_table)
        
        widget.setLayout(layout)
        return widget
    
    def create_statistics_tab(self):
        """Create statistics tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Statistics display
        self.stats_output = QTextEdit()
        self.stats_output.setReadOnly(True)
        layout.addWidget(self.stats_output)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh Statistics")
        refresh_btn.clicked.connect(self.refresh_statistics)
        layout.addWidget(refresh_btn)
        
        widget.setLayout(layout)
        return widget
    
    def test_ad_connection(self):
        """Test AD connection"""
        if not self.validate_inputs():
            return
        
        self.start_operation("test")
    
    def fetch_ad_computers(self):
        """Fetch computers from AD"""
        if not self.validate_inputs():
            return
        
        self.start_operation("fetch")
    
    def sync_to_database(self):
        """Sync AD data to main database"""
        self.start_operation("sync")
    
    def validate_inputs(self):
        """Validate connection inputs"""
        if not self.server_input.text().strip():
            QMessageBox.warning(self, "Missing Input", "Please enter AD server address")
            return False
        
        if not self.base_dn_input.text().strip():
            QMessageBox.warning(self, "Missing Input", "Please enter Base DN")
            return False
        
        if not self.username_input.text().strip():
            QMessageBox.warning(self, "Missing Input", "Please enter username")
            return False
        
        if not self.password_input.text().strip():
            QMessageBox.warning(self, "Missing Input", "Please enter password")
            return False
        
        return True
    
    def start_operation(self, operation):
        """Start AD operation in worker thread"""
        if self.worker and self.worker.isRunning():
            QMessageBox.information(self, "Operation in Progress", "Please wait for current operation to complete")
            return
        
        # Disable buttons
        self.test_btn.setEnabled(False)
        self.fetch_btn.setEnabled(False)
        self.sync_btn.setEnabled(False)
        
        # Show progress bar
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Create worker
        kwargs = {
            'server': self.server_input.text().strip(),
            'base_dn': self.base_dn_input.text().strip(),
            'username': self.username_input.text().strip(),
            'password': self.password_input.text().strip(),
            'use_ssl': self.ssl_checkbox.isChecked()
        }
        
        self.worker = ADConnectionWorker(operation, **kwargs)
        self.worker.log_signal.connect(self.add_log)
        self.worker.progress_signal.connect(self.progress_bar.setValue)
        self.worker.finished_signal.connect(self.operation_finished)
        self.worker.start()
    
    def operation_finished(self, success, result):
        """Handle operation completion"""
        # Re-enable buttons
        self.test_btn.setEnabled(True)
        self.fetch_btn.setEnabled(True)
        self.sync_btn.setEnabled(True)
        
        # Hide progress bar
        self.progress_bar.setVisible(False)
        
        # Handle result
        if success and "computers" in result:
            self.update_computers_table(result["computers"])
        
        if success:
            if "count" in result:
                QMessageBox.information(self, "Success", f"Operation completed successfully!\nFetched {result['count']} computers")
            else:
                QMessageBox.information(self, "Success", "Operation completed successfully!")
        else:
            QMessageBox.warning(self, "Operation Failed", f"Operation failed: {result.get('error', 'Unknown error')}")
    
    def update_computers_table(self, computers):
        """Update computers table with fetched data"""
        self.computers_data = computers
        self.computers_table.setRowCount(len(computers))
        
        for row, computer in enumerate(computers):
            self.computers_table.setItem(row, 0, QTableWidgetItem(computer.get("Hostname", "")))
            self.computers_table.setItem(row, 1, QTableWidgetItem(computer.get("FQDN", "")))
            self.computers_table.setItem(row, 2, QTableWidgetItem(computer.get("OS Name and Version", "")))
            self.computers_table.setItem(row, 3, QTableWidgetItem(computer.get("OS Version", "")))
            self.computers_table.setItem(row, 4, QTableWidgetItem(computer.get("AD whenCreated", "")))
            self.computers_table.setItem(row, 5, QTableWidgetItem(computer.get("AD lastLogonTimestamp", "")))
    
    def refresh_statistics(self):
        """Refresh AD statistics"""
        try:
            from ad_fetcher.ad_fetcher import get_ad_statistics
            
            self.add_log("📊 Refreshing AD statistics...")
            
            stats = get_ad_statistics()
            
            if stats:
                stats_text = f"""📊 AD DATABASE STATISTICS
{'='*40}
Total AD computers: {stats['total_computers']}
Enabled computers: {stats['enabled_computers']}
Synced to assets: {stats['sync_status']['synced']}
Not synced: {stats['sync_status']['not_synced']}

By Domain:
"""
                for domain, count in stats.get('by_domain', {}).items():
                    stats_text += f"  {domain}: {count}\n"
                
                self.stats_output.setText(stats_text)
                self.add_log("✅ Statistics refreshed")
            else:
                self.stats_output.setText("❌ No statistics available")
                self.add_log("❌ Could not load statistics")
                
        except Exception as e:
            self.add_log(f"❌ Error refreshing statistics: {e}")
            self.stats_output.setText(f"❌ Error: {e}")
    
    def add_log(self, message):
        """Add message to log output"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_output.append(f"[{timestamp}] {message}")
    
    def save_settings(self):
        """Save AD connection settings"""
        try:
            import json
            
            settings = {
                'server': self.server_input.text().strip(),
                'base_dn': self.base_dn_input.text().strip(),
                'username': self.username_input.text().strip(),
                'use_ssl': self.ssl_checkbox.isChecked(),
                'saved_at': datetime.now().isoformat()
            }
            
            with open('ad_settings.json', 'w') as f:
                json.dump(settings, f, indent=2)
            
            self.add_log("💾 Settings saved to ad_settings.json")
            QMessageBox.information(self, "Settings Saved", "AD connection settings saved successfully!")
            
        except Exception as e:
            self.add_log(f"❌ Error saving settings: {e}")
            QMessageBox.warning(self, "Save Failed", f"Failed to save settings: {e}")
    
    def load_saved_settings(self):
        """Load saved AD settings"""
        try:
            import json
            
            if os.path.exists('ad_settings.json'):
                with open('ad_settings.json', 'r') as f:
                    settings = json.load(f)
                
                self.server_input.setText(settings.get('server', ''))
                self.base_dn_input.setText(settings.get('base_dn', ''))
                self.username_input.setText(settings.get('username', ''))
                self.ssl_checkbox.setChecked(settings.get('use_ssl', False))
                
                self.add_log("📂 Loaded saved AD settings")
                
        except Exception as e:
            self.add_log(f"⚠️  Could not load saved settings: {e}")


def main():
    """Test the AD GUI"""
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    ad_tab = ADTab()
    ad_tab.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()