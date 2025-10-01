# -*- coding: utf-8 -*-
"""
Performance-Optimized Asset Management Desktop Application
----------------------------------------------------------
Enhanced version with performance improvements and proper error handling
"""

import sys
import os
import logging
import subprocess
import time
from pathlib import Path
from typing import Optional

# Set encoding environment
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging without Unicode characters to prevent encoding errors
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_app.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# PyQt6 imports
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
    QHBoxLayout, QLabel, QPushButton, QTextEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QGroupBox, QLineEdit, 
    QProgressBar, QStatusBar, QSplitter, QFrame, QComboBox,
    QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QProcess
from PyQt6.QtGui import QFont, QIcon

# Database imports
from db.connection import connect
from core.enhanced_asset_integrator import get_system_enhancement_status

log = logging.getLogger(__name__)


class WebServiceManager:
    """Manages web service startup and monitoring"""
    
    def __init__(self):
        self.process = None
        self.port = 8080
    
    def start_web_service(self) -> bool:
        """Start the web service"""
        try:
            if self.is_running():
                log.info("Web service already running")
                return True
            
            # Start the enhanced web service
            python_exe = sys.executable
            web_service_script = "enhanced_complete_web_service.py"
            
            if os.path.exists(web_service_script):
                self.process = subprocess.Popen(
                    [python_exe, web_service_script],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=os.getcwd()
                )
                
                # Wait a moment for startup
                time.sleep(2)
                
                if self.is_running():
                    log.info(f"Web service started successfully on port {self.port}")
                    return True
                else:
                    log.error("Web service failed to start")
                    return False
            else:
                log.warning(f"Web service script {web_service_script} not found")
                return False
                
        except Exception as e:
            log.error(f"Error starting web service: {e}")
            return False
    
    def is_running(self) -> bool:
        """Check if web service is running"""
        try:
            import requests
            response = requests.get(f'http://127.0.0.1:{self.port}', timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def stop_web_service(self):
        """Stop the web service"""
        try:
            if self.process:
                self.process.terminate()
                self.process.wait(timeout=5)
                self.process = None
                log.info("Web service stopped")
        except Exception as e:
            log.error(f"Error stopping web service: {e}")


class EnhancedDashboard(QWidget):
    """Enhanced dashboard with comprehensive statistics"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.start_data_update()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Enhanced Asset Management Dashboard")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Create splitter for better layout
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - Statistics
        stats_widget = QWidget()
        stats_layout = QVBoxLayout(stats_widget)
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMaximumHeight(300)
        stats_layout.addWidget(QLabel("System Statistics:"))
        stats_layout.addWidget(self.stats_text)
        
        # Right side - Enhancement status
        enhancement_widget = QWidget()
        enhancement_layout = QVBoxLayout(enhancement_widget)
        
        self.enhancement_text = QTextEdit()
        self.enhancement_text.setReadOnly(True)
        self.enhancement_text.setMaximumHeight(300)
        enhancement_layout.addWidget(QLabel("Enhancement Status:"))
        enhancement_layout.addWidget(self.enhancement_text)
        
        splitter.addWidget(stats_widget)
        splitter.addWidget(enhancement_widget)
        splitter.setSizes([500, 500])
        
        layout.addWidget(splitter)
        
        # Update button
        update_btn = QPushButton("Update All Statistics")
        update_btn.clicked.connect(self.update_all_data)
        layout.addWidget(update_btn)
    
    def start_data_update(self):
        """Start background data updates"""
        self.update_all_data()
        
        # Set up timer for periodic updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_all_data)
        self.update_timer.start(30000)  # Update every 30 seconds
    
    def update_all_data(self):
        """Update all dashboard data"""
        self.update_system_stats()
        self.update_enhancement_status()
    
    def update_system_stats(self):
        """Update system statistics"""
        try:
            with connect() as conn:
                cursor = conn.cursor()
                
                # Basic stats
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
                    SELECT COUNT(*) FROM assets 
                    WHERE working_user IS NOT NULL AND working_user != 'N/A'
                """)
                assets_with_users = cursor.fetchone()[0]
                
                # Device types
                cursor.execute("""
                    SELECT device_type, COUNT(*) 
                    FROM assets 
                    GROUP BY device_type 
                    ORDER BY COUNT(*) DESC 
                    LIMIT 5
                """)
                device_types = cursor.fetchall()
                
                # Calculate percentages
                hostname_percentage = (real_hostnames / max(total_assets, 1)) * 100
                user_percentage = (assets_with_users / max(total_assets, 1)) * 100
                
                # Build stats text
                stats_text = f"""SYSTEM OVERVIEW:
Total Assets: {total_assets}
Active Assets: {active_assets} ({(active_assets/max(total_assets,1)*100):.1f}%)

DATA QUALITY:
Real Hostnames: {real_hostnames} ({hostname_percentage:.1f}%)
Assets with Users: {assets_with_users} ({user_percentage:.1f}%)

TOP DEVICE TYPES:
"""
                
                for device_type, count in device_types:
                    percentage = (count / max(total_assets, 1)) * 100
                    stats_text += f"- {device_type}: {count} ({percentage:.1f}%)\n"
                
                stats_text += f"""
PERFORMANCE INDICATORS:
Data Quality: {'Excellent' if hostname_percentage > 70 else 'Good' if hostname_percentage > 40 else 'Needs Improvement'}
User Detection: {'Good' if user_percentage > 50 else 'Fair' if user_percentage > 20 else 'Poor'}
Coverage: {'High' if total_assets > 100 else 'Medium' if total_assets > 50 else 'Growing'}
"""
                
                self.stats_text.setText(stats_text)
                
        except Exception as e:
            log.error(f"Error updating system stats: {e}")
            self.stats_text.setText(f"Error loading statistics: {e}")
    
    def update_enhancement_status(self):
        """Update enhancement status"""
        try:
            status = get_system_enhancement_status()
            
            enhancement_text = f"""ENHANCEMENT STATUS:
Enhanced Assets: {status.get('enhanced_assets', 0)} of {status.get('total_assets', 0)}
Enhancement Rate: {status.get('enhancement_percentage', 0):.1f}%

QUALITY DISTRIBUTION:
"""
            
            quality_dist = status.get('quality_distribution', {})
            for quality, count in quality_dist.items():
                enhancement_text += f"- {quality}: {count}\n"
            
            enhancement_text += f"""
DEVICE CLASSIFICATION:
"""
            
            device_dist = status.get('device_distribution', {})
            for device_type, count in device_dist.items():
                enhancement_text += f"- {device_type}: {count}\n"
            
            enhancement_text += f"""
SUMMARY:
Real Hostname Rate: {status.get('real_hostname_percentage', 0):.1f}%
User Info Rate: {status.get('user_info_percentage', 0):.1f}%

RECOMMENDATION:
"""
            
            if status.get('enhancement_percentage', 0) < 50:
                enhancement_text += "- Consider running bulk enhancement\n"
            if status.get('real_hostname_percentage', 0) < 60:
                enhancement_text += "- Improve hostname collection\n"
            if status.get('user_info_percentage', 0) < 40:
                enhancement_text += "- Enhance user detection\n"
            
            self.enhancement_text.setText(enhancement_text)
            
        except Exception as e:
            log.error(f"Error updating enhancement status: {e}")
            self.enhancement_text.setText(f"Error loading enhancement status: {e}")


class PerformanceOptimizedAssetTable(QWidget):
    """Performance optimized asset table with lazy loading"""
    
    def __init__(self):
        super().__init__()
        self.current_page = 0
        self.page_size = 25  # Smaller page size for better performance
        self.total_assets = 0
        self.init_ui()
        self.load_page()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Controls
        controls = QHBoxLayout()
        
        # Search
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search assets...")
        self.search_box.returnPressed.connect(self.search_assets)
        controls.addWidget(QLabel("Search:"))
        controls.addWidget(self.search_box)
        
        # Filter by device type
        self.device_filter = QComboBox()
        self.device_filter.addItem("All Device Types")
        self.load_device_types()
        self.device_filter.currentTextChanged.connect(self.filter_changed)
        controls.addWidget(QLabel("Filter:"))
        controls.addWidget(self.device_filter)
        
        # Refresh button
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.load_page)
        controls.addWidget(self.refresh_btn)
        
        controls.addStretch()
        layout.addLayout(controls)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            'Hostname', 'IP', 'Type', 'OS', 'User', 'Department', 'Quality', 'Updated'
        ])
        
        # Set table properties for better performance
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        layout.addWidget(self.table)
        
        # Pagination
        pagination = QHBoxLayout()
        
        self.prev_btn = QPushButton("Previous")
        self.prev_btn.clicked.connect(self.prev_page)
        pagination.addWidget(self.prev_btn)
        
        self.page_info = QLabel("Page 1 of 1")
        pagination.addWidget(self.page_info)
        
        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.next_page)
        pagination.addWidget(self.next_btn)
        
        # Page size selector
        pagination.addWidget(QLabel("Per page:"))
        self.page_size_combo = QComboBox()
        self.page_size_combo.addItems(["25", "50", "100"])
        self.page_size_combo.currentTextChanged.connect(self.change_page_size)
        pagination.addWidget(self.page_size_combo)
        
        pagination.addStretch()
        layout.addLayout(pagination)
    
    def load_device_types(self):
        """Load device types for filter"""
        try:
            with connect() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT DISTINCT device_type 
                    FROM assets 
                    WHERE device_type IS NOT NULL 
                    ORDER BY device_type
                """)
                
                device_types = cursor.fetchall()
                for device_type, in device_types:
                    self.device_filter.addItem(device_type)
                    
        except Exception as e:
            log.error(f"Error loading device types: {e}")
    
    def filter_changed(self):
        """Handle filter change"""
        self.current_page = 0
        self.load_page()
    
    def search_assets(self):
        """Search assets"""
        self.current_page = 0
        self.load_page()
    
    def change_page_size(self, size_str: str):
        """Change page size"""
        self.page_size = int(size_str)
        self.current_page = 0
        self.load_page()
    
    def load_page(self):
        """Load current page of assets"""
        try:
            with connect() as conn:
                cursor = conn.cursor()
                
                # Build query
                base_query = """
                    SELECT hostname, ip_address, device_type, firmware_os_version,
                           working_user, department, collection_quality, updated_at
                    FROM assets
                """
                
                conditions = []
                params = []
                
                # Search filter
                search_text = self.search_box.text().strip()
                if search_text:
                    conditions.append("(hostname LIKE ? OR ip_address LIKE ? OR device_type LIKE ?)")
                    params.extend([f"%{search_text}%", f"%{search_text}%", f"%{search_text}%"])
                
                # Device type filter
                device_filter = self.device_filter.currentText()
                if device_filter != "All Device Types":
                    conditions.append("device_type = ?")
                    params.append(device_filter)
                
                # Add WHERE clause if needed
                if conditions:
                    base_query += " WHERE " + " AND ".join(conditions)
                
                # Get total count
                count_query = base_query.replace(
                    "SELECT hostname, ip_address, device_type, firmware_os_version, working_user, department, collection_quality, updated_at",
                    "SELECT COUNT(*)"
                )
                cursor.execute(count_query, params)
                self.total_assets = cursor.fetchone()[0]
                
                # Add pagination
                base_query += " ORDER BY updated_at DESC LIMIT ? OFFSET ?"
                params.extend([self.page_size, self.current_page * self.page_size])
                
                # Execute main query
                cursor.execute(base_query, params)
                assets = cursor.fetchall()
                
                # Update table
                self.table.setRowCount(len(assets))
                
                for i, asset in enumerate(assets):
                    for j, value in enumerate(asset):
                        if value is None:
                            value = "N/A"
                        elif j == 7 and value:  # Format date
                            try:
                                # Extract just date part if it's a full datetime
                                value_str = str(value)
                                value = value_str.split()[0] if ' ' in value_str else value_str
                            except:
                                value = str(value)
                        
                        item = QTableWidgetItem(str(value))
                        self.table.setItem(i, j, item)
                
                # Update pagination info
                total_pages = (self.total_assets + self.page_size - 1) // self.page_size
                self.page_info.setText(f"Page {self.current_page + 1} of {max(total_pages, 1)} ({self.total_assets} assets)")
                
                self.prev_btn.setEnabled(self.current_page > 0)
                self.next_btn.setEnabled(self.current_page < total_pages - 1)
                
                log.info(f"Loaded page {self.current_page + 1} with {len(assets)} assets")
                
        except Exception as e:
            log.error(f"Error loading assets page: {e}")
    
    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.load_page()
    
    def next_page(self):
        self.current_page += 1
        self.load_page()


class OptimizedMainWindow(QMainWindow):
    """Optimized main window with better performance"""
    
    def __init__(self):
        super().__init__()
        self.web_service_manager = WebServiceManager()
        self.init_ui()
        self.start_web_service()
    
    def init_ui(self):
        self.setWindowTitle("Enhanced Asset Management System - Performance Optimized")
        self.setGeometry(100, 100, 1400, 900)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Header
        header = QLabel("Enhanced Asset Management System")
        header.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("padding: 10px; background-color: #f0f0f0; border: 1px solid #ccc;")
        layout.addWidget(header)
        
        # Create tabs
        self.tab_widget = QTabWidget()
        
        # Dashboard
        self.dashboard = EnhancedDashboard()
        self.tab_widget.addTab(self.dashboard, "Dashboard")
        
        # Assets table
        self.assets_table = PerformanceOptimizedAssetTable()
        self.tab_widget.addTab(self.assets_table, "Assets")
        
        # Web service info
        self.web_info = self.create_web_info_tab()
        self.tab_widget.addTab(self.web_info, "Web Service")
        
        # System info
        self.system_info = self.create_system_info_tab()
        self.tab_widget.addTab(self.system_info, "System Info")
        
        layout.addWidget(self.tab_widget)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Enhanced Asset Management System - Ready")
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.auto_refresh)
        self.refresh_timer.start(60000)  # Refresh every minute
        
        log.info("Optimized main window initialized")
    
    def create_web_info_tab(self) -> QWidget:
        """Create web service information tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Title
        title = QLabel("Web Service Control")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Status
        self.web_status = QLabel("Checking web service status...")
        layout.addWidget(self.web_status)
        
        # Control buttons
        controls = QHBoxLayout()
        
        self.start_web_btn = QPushButton("Start Web Service")
        self.start_web_btn.clicked.connect(self.start_web_service)
        controls.addWidget(self.start_web_btn)
        
        self.open_web_btn = QPushButton("Open Web Interface")
        self.open_web_btn.clicked.connect(self.open_web_interface)
        controls.addWidget(self.open_web_btn)
        
        self.check_status_btn = QPushButton("Check Status")
        self.check_status_btn.clicked.connect(self.check_web_status)
        controls.addWidget(self.check_status_btn)
        
        controls.addStretch()
        layout.addLayout(controls)
        
        # Information
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setText("""
WEB SERVICE FEATURES:
• Enhanced asset discovery with real hostnames and users
• Smart device classification (Server/Workstation/Virtual)
• SNMP support for network devices (switches, firewalls, printers)
• Credential management for multiple device types
• Network range management and saving
• Department and location management
• Real-time monitoring and statistics

ACCESS URLS:
• Main Dashboard: http://127.0.0.1:8080
• Smart Discovery: http://127.0.0.1:8080/add-asset
• Credential Management: http://127.0.0.1:8080/credentials
• Network Management: http://127.0.0.1:8080/networks
• Department Management: http://127.0.0.1:8080/departments

PERFORMANCE IMPROVEMENTS:
• Optimized database queries with pagination
• Background data loading
• Lazy loading for large datasets
• Efficient memory management
• Fast response times
        """)
        layout.addWidget(info_text)
        
        # Initial status check
        QTimer.singleShot(1000, self.check_web_status)
        
        return widget
    
    def create_system_info_tab(self) -> QWidget:
        """Create system information tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Title
        title = QLabel("System Information")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # System info text
        self.system_info_text = QTextEdit()
        self.system_info_text.setReadOnly(True)
        layout.addWidget(self.system_info_text)
        
        # Update button
        update_system_btn = QPushButton("Update System Info")
        update_system_btn.clicked.connect(self.update_system_info)
        layout.addWidget(update_system_btn)
        
        # Load initial info
        self.update_system_info()
        
        return widget
    
    def start_web_service(self):
        """Start web service"""
        try:
            if self.web_service_manager.start_web_service():
                self.status_bar.showMessage("Web service started successfully")
                self.check_web_status()
            else:
                self.status_bar.showMessage("Failed to start web service")
        except Exception as e:
            log.error(f"Error starting web service: {e}")
            self.status_bar.showMessage(f"Error starting web service: {e}")
    
    def check_web_status(self):
        """Check web service status"""
        if self.web_service_manager.is_running():
            self.web_status.setText("Web Service Status: RUNNING on port 8080")
            self.web_status.setStyleSheet("color: green; font-weight: bold;")
            self.start_web_btn.setText("Restart Web Service")
        else:
            self.web_status.setText("Web Service Status: NOT RUNNING")
            self.web_status.setStyleSheet("color: red; font-weight: bold;")
            self.start_web_btn.setText("Start Web Service")
    
    def open_web_interface(self):
        """Open web interface"""
        try:
            import webbrowser
            webbrowser.open('http://127.0.0.1:8080')
            self.status_bar.showMessage("Web interface opened in browser")
        except Exception as e:
            log.error(f"Error opening web interface: {e}")
    
    def update_system_info(self):
        """Update system information display"""
        try:
            import platform
            import psutil
            
            info_text = f"""SYSTEM INFORMATION:
Operating System: {platform.system()} {platform.release()}
Python Version: {platform.python_version()}
Architecture: {platform.architecture()[0]}

HARDWARE:
CPU: {platform.processor()}
CPU Cores: {psutil.cpu_count(logical=False)} physical, {psutil.cpu_count(logical=True)} logical
Memory: {psutil.virtual_memory().total / (1024**3):.1f} GB total
Disk Space: {psutil.disk_usage('.').total / (1024**3):.1f} GB total

APPLICATION:
Working Directory: {os.getcwd()}
Python Executable: {sys.executable}
PyQt6 Version: Available
Database: SQLite (connected)

PERFORMANCE STATUS:
Memory Usage: {psutil.virtual_memory().percent:.1f}%
CPU Usage: {psutil.cpu_percent(interval=1):.1f}%
Disk Usage: {psutil.disk_usage('.').percent:.1f}%
"""
            
            self.system_info_text.setText(info_text)
            
        except ImportError:
            self.system_info_text.setText("""System information requires 'psutil' package.
To install: pip install psutil

Basic Information:
Operating System: Windows
Python Version: 3.x
Database: Connected
Application Status: Running
""")
        except Exception as e:
            log.error(f"Error updating system info: {e}")
    
    def auto_refresh(self):
        """Auto-refresh data"""
        try:
            current_tab = self.tab_widget.currentIndex()
            if current_tab == 0:  # Dashboard
                self.dashboard.update_all_data()
            elif current_tab == 1:  # Assets
                self.assets_table.load_page()
            
            # Always check web status
            self.check_web_status()
            
        except Exception as e:
            log.error(f"Error in auto-refresh: {e}")
    
    def closeEvent(self, event):
        """Handle application close"""
        try:
            self.web_service_manager.stop_web_service()
            event.accept()
        except Exception as e:
            log.error(f"Error during close: {e}")
            event.accept()


def main():
    """Main application function"""
    try:
        # Create application
        app = QApplication(sys.argv)
        app.setApplicationName("Enhanced Asset Management")
        app.setApplicationVersion("2.0")
        
        # Set application style
        app.setStyle('Fusion')
        
        # Create and show main window
        window = OptimizedMainWindow()
        window.show()
        
        log.info("Enhanced Asset Management application started successfully")
        
        # Run application
        return app.exec()
        
    except Exception as e:
        log.error(f"Application error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())