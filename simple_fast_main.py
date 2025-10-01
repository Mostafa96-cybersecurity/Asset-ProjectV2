# -*- coding: utf-8 -*-
"""
Simple Fast Asset Management Desktop Application
-----------------------------------------------
Lightweight version focused on performance and reliability
"""

import sys
import os
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# PyQt6 imports
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
    QHBoxLayout, QLabel, QPushButton, QTextEdit, QTableWidget,
    QTableWidgetItem, QGroupBox, QLineEdit, QStatusBar
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

# Database imports
from db.connection import connect

# Configure simple logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

log = logging.getLogger(__name__)


class SimpleAssetViewer(QWidget):
    """Simple asset viewer with basic functionality"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_recent_assets()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("Recent Assets")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Controls
        controls = QHBoxLayout()
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search assets...")
        controls.addWidget(QLabel("Search:"))
        controls.addWidget(self.search_box)
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.load_recent_assets)
        controls.addWidget(self.refresh_btn)
        
        controls.addStretch()
        layout.addLayout(controls)
        
        # Asset table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            'Hostname', 'IP Address', 'Device Type', 'OS', 'Status', 'Last Update'
        ])
        layout.addWidget(self.table)
    
    def load_recent_assets(self):
        """Load recent assets from database"""
        try:
            with connect() as conn:
                cursor = conn.cursor()
                
                # Get recent assets (limit to 100 for performance)
                cursor.execute("""
                    SELECT hostname, ip_address, device_type, firmware_os_version, 
                           status, updated_at
                    FROM assets 
                    ORDER BY updated_at DESC 
                    LIMIT 100
                """)
                
                assets = cursor.fetchall()
                
                # Update table
                self.table.setRowCount(len(assets))
                
                for i, asset in enumerate(assets):
                    for j, value in enumerate(asset):
                        if value is None:
                            value = "N/A"
                        item = QTableWidgetItem(str(value))
                        self.table.setItem(i, j, item)
                
                log.info(f"Loaded {len(assets)} recent assets")
                
        except Exception as e:
            log.error(f"Error loading assets: {e}")


class SimpleDashboard(QWidget):
    """Simple dashboard with basic statistics"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.update_stats()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Asset Management Dashboard")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Stats display
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMaximumHeight(300)
        layout.addWidget(self.stats_text)
        
        # Update button
        update_btn = QPushButton("Update Statistics")
        update_btn.clicked.connect(self.update_stats)
        layout.addWidget(update_btn)
    
    def update_stats(self):
        """Update statistics display"""
        try:
            with connect() as conn:
                cursor = conn.cursor()
                
                # Get basic stats
                cursor.execute("SELECT COUNT(*) FROM assets")
                total_assets = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM assets WHERE status = 'Active'")
                active_assets = cursor.fetchone()[0]
                
                cursor.execute("""
                    SELECT COUNT(*) FROM assets 
                    WHERE hostname NOT LIKE '%.%.%.%' AND hostname != ip_address
                """)
                real_hostnames = cursor.fetchone()[0]
                
                cursor.execute("""
                    SELECT device_type, COUNT(*) 
                    FROM assets 
                    GROUP BY device_type 
                    ORDER BY COUNT(*) DESC 
                    LIMIT 10
                """)
                device_types = cursor.fetchall()
                
                # Calculate percentages
                hostname_percentage = (real_hostnames / max(total_assets, 1)) * 100
                active_percentage = (active_assets / max(total_assets, 1)) * 100
                
                # Build stats text
                stats_text = f"""ASSET MANAGEMENT STATISTICS
========================================

OVERVIEW:
• Total Assets: {total_assets}
• Active Assets: {active_assets} ({active_percentage:.1f}%)
• Real Hostnames: {real_hostnames} ({hostname_percentage:.1f}%)

DEVICE TYPE DISTRIBUTION:
"""
                
                for device_type, count in device_types:
                    percentage = (count / max(total_assets, 1)) * 100
                    stats_text += f"• {device_type}: {count} ({percentage:.1f}%)\n"
                
                stats_text += f"""
DATA QUALITY:
• Hostname Quality: {'Good' if hostname_percentage > 50 else 'Needs Improvement'}
• Data Coverage: {'Excellent' if total_assets > 100 else 'Good'}

SYSTEM STATUS:
• Database: Connected
• Last Update: {cursor.execute("SELECT datetime('now')").fetchone()[0]}
"""
                
                self.stats_text.setText(stats_text)
                log.info("Statistics updated successfully")
                
        except Exception as e:
            log.error(f"Error updating statistics: {e}")
            self.stats_text.setText(f"Error loading statistics: {e}")


class SimpleWebTab(QWidget):
    """Simple web service information tab"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Web Service")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Info text
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setText("""
WEB SERVICE INFORMATION
======================

Access URLs:
• Main Dashboard: http://127.0.0.1:8080
• Asset Management: http://127.0.0.1:8080/add-asset
• Smart Discovery: http://127.0.0.1:8080/credentials
• Network Management: http://127.0.0.1:8080/networks

Features Available:
• Real-time asset discovery
• Credential management
• Network range management
• SNMP support for network devices
• Enhanced WMI collection
• Department management

Status:
The web service runs automatically when the desktop application is open.
If you see connection errors, please restart the desktop application.

Quick Start:
1. Keep this desktop application running
2. Open http://127.0.0.1:8080 in your browser
3. Use the enhanced discovery features
4. Manage credentials and networks
        """)
        layout.addWidget(info_text)
        
        # Quick action button
        open_btn = QPushButton("Open Web Interface")
        open_btn.clicked.connect(self.open_web)
        layout.addWidget(open_btn)
    
    def open_web(self):
        """Open web interface"""
        try:
            import webbrowser
            webbrowser.open('http://127.0.0.1:8080')
            log.info("Web interface opened")
        except Exception as e:
            log.error(f"Error opening web interface: {e}")


class SimpleMainWindow(QMainWindow):
    """Simple main window with essential features only"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fast Asset Management System")
        self.setGeometry(100, 100, 1000, 700)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Create tabs
        self.tab_widget = QTabWidget()
        
        # Dashboard tab
        self.dashboard = SimpleDashboard()
        self.tab_widget.addTab(self.dashboard, "Dashboard")
        
        # Assets tab
        self.assets = SimpleAssetViewer()
        self.tab_widget.addTab(self.assets, "Recent Assets")
        
        # Web service tab
        self.web_tab = SimpleWebTab()
        self.tab_widget.addTab(self.web_tab, "Web Service")
        
        layout.addWidget(self.tab_widget)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Fast Asset Management System - Ready")
        
        # Auto-refresh timer (every 2 minutes)
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.auto_refresh)
        self.refresh_timer.start(120000)
        
        log.info("Simple main window initialized")
    
    def auto_refresh(self):
        """Auto-refresh data periodically"""
        try:
            current_tab = self.tab_widget.currentIndex()
            if current_tab == 0:  # Dashboard
                self.dashboard.update_stats()
            elif current_tab == 1:  # Assets
                self.assets.load_recent_assets()
            
            self.status_bar.showMessage(f"Auto-refreshed at {QTimer().remainingTime()}")
            
        except Exception as e:
            log.error(f"Error in auto-refresh: {e}")


def main():
    """Main application function"""
    try:
        # Create application
        app = QApplication(sys.argv)
        app.setApplicationName("Fast Asset Management")
        
        # Set simple style
        app.setStyle('Fusion')
        
        # Create main window
        window = SimpleMainWindow()
        window.show()
        
        log.info("Fast Asset Management application started")
        
        # Run application
        return app.exec()
        
    except Exception as e:
        log.error(f"Application error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())