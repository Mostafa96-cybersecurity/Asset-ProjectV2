# -*- coding: utf-8 -*-
"""
Department Management System
---------------------------
Complete department and location management with device assignment
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QTextEdit, QTableWidget,
                             QTableWidgetItem, QGroupBox, QComboBox, QTabWidget,
                             QHeaderView, QMessageBox, QDialog, QDialogButtonBox,
                             QFormLayout, QSpinBox, QCheckBox, QListWidget,
                             QListWidgetItem, QSplitter, QProgressBar)
from PyQt6.QtGui import QFont, QIcon


class DepartmentDatabase:
    """Database operations for departments and locations"""
    
    def __init__(self, db_path: str = "assets.db"):
        self.db_path = db_path
        self.init_tables()
    
    def init_tables(self):
        """Initialize department and location tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Departments table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS departments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    manager TEXT,
                    contact_email TEXT,
                    contact_phone TEXT,
                    location TEXT,
                    budget REAL DEFAULT 0,
                    status TEXT DEFAULT 'Active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Locations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS locations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    building TEXT,
                    floor TEXT,
                    room TEXT,
                    address TEXT,
                    capacity INTEGER DEFAULT 0,
                    description TEXT,
                    status TEXT DEFAULT 'Active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Device assignments table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS device_assignments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asset_id INTEGER,
                    department_id INTEGER,
                    location_id INTEGER,
                    assigned_by TEXT,
                    assigned_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT,
                    FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE,
                    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL,
                    FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE SET NULL
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_dept_name ON departments(name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_location_name ON locations(name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_assignments_asset ON device_assignments(asset_id)")
            
            conn.commit()
    
    def add_department(self, name: str, description: str = "", manager: str = "", 
                      contact_email: str = "", contact_phone: str = "", 
                      location: str = "", budget: float = 0) -> bool:
        """Add new department"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO departments (name, description, manager, contact_email, 
                                           contact_phone, location, budget)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (name, description, manager, contact_email, contact_phone, location, budget))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False  # Department name already exists
        except Exception:
            return False
    
    def update_department(self, dept_id: int, **kwargs) -> bool:
        """Update department information"""
        try:
            if not kwargs:
                return False
                
            set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
            values = list(kwargs.values()) + [datetime.now().isoformat(), dept_id]
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"""
                    UPDATE departments 
                    SET {set_clause}, updated_at = ?
                    WHERE id = ?
                """, values)
                conn.commit()
                return cursor.rowcount > 0
        except Exception:
            return False
    
    def delete_department(self, dept_id: int) -> bool:
        """Delete department (only if no devices assigned)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if department has assigned devices
                cursor.execute("SELECT COUNT(*) FROM device_assignments WHERE department_id = ?", (dept_id,))
                if cursor.fetchone()[0] > 0:
                    return False  # Cannot delete department with assigned devices
                
                cursor.execute("DELETE FROM departments WHERE id = ?", (dept_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception:
            return False
    
    def get_departments(self) -> List[Dict]:
        """Get all departments"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT d.*, COUNT(da.asset_id) as device_count
                    FROM departments d
                    LEFT JOIN device_assignments da ON d.id = da.department_id
                    GROUP BY d.id
                    ORDER BY d.name
                """)
                
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception:
            return []
    
    def add_location(self, name: str, building: str = "", floor: str = "", 
                    room: str = "", address: str = "", capacity: int = 0, 
                    description: str = "") -> bool:
        """Add new location"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO locations (name, building, floor, room, address, capacity, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (name, building, floor, room, address, capacity, description))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False
        except Exception:
            return False
    
    def get_locations(self) -> List[Dict]:
        """Get all locations"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT l.*, COUNT(da.asset_id) as device_count
                    FROM locations l
                    LEFT JOIN device_assignments da ON l.id = da.location_id
                    GROUP BY l.id
                    ORDER BY l.name
                """)
                
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception:
            return []
    
    def assign_device(self, asset_id: int, department_id: Optional[int] = None, 
                     location_id: Optional[int] = None, assigned_by: str = "System", 
                     notes: str = "") -> bool:
        """Assign device to department and/or location"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Remove existing assignment for this device
                cursor.execute("DELETE FROM device_assignments WHERE asset_id = ?", (asset_id,))
                
                # Add new assignment
                cursor.execute("""
                    INSERT INTO device_assignments (asset_id, department_id, location_id, assigned_by, notes)
                    VALUES (?, ?, ?, ?, ?)
                """, (asset_id, department_id, location_id, assigned_by, notes))
                
                # Update assets table with department and location names
                dept_name = None
                location_name = None
                
                if department_id:
                    cursor.execute("SELECT name FROM departments WHERE id = ?", (department_id,))
                    result = cursor.fetchone()
                    dept_name = result[0] if result else None
                
                if location_id:
                    cursor.execute("SELECT name FROM locations WHERE id = ?", (location_id,))
                    result = cursor.fetchone()
                    location_name = result[0] if result else None
                
                # Update the assets table
                cursor.execute("""
                    UPDATE assets 
                    SET department = ?, location = ?, updated_at = ?
                    WHERE id = ?
                """, (dept_name, location_name, datetime.now().isoformat(), asset_id))
                
                conn.commit()
                return True
        except Exception:
            return False
    
    def get_device_assignments(self) -> List[Dict]:
        """Get all device assignments with details"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        a.id as asset_id,
                        a.hostname,
                        a.ip_address,
                        a.device_type,
                        d.name as department_name,
                        l.name as location_name,
                        da.assigned_by,
                        da.assigned_at,
                        da.notes
                    FROM assets a
                    LEFT JOIN device_assignments da ON a.id = da.asset_id
                    LEFT JOIN departments d ON da.department_id = d.id
                    LEFT JOIN locations l ON da.location_id = l.id
                    ORDER BY a.hostname
                """)
                
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception:
            return []
    
    def get_unassigned_devices(self) -> List[Dict]:
        """Get devices not assigned to any department"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT a.id, a.hostname, a.ip_address, a.device_type, a.model_vendor
                    FROM assets a
                    LEFT JOIN device_assignments da ON a.id = da.asset_id
                    WHERE da.asset_id IS NULL
                    ORDER BY a.hostname
                """)
                
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception:
            return []


class DepartmentDialog(QDialog):
    """Dialog for adding/editing departments"""
    
    def __init__(self, department: Dict = None, parent=None):
        super().__init__(parent)
        self.department = department
        self.setWindowTitle("Add Department" if not department else "Edit Department")
        self.setMinimumSize(400, 300)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Form
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.manager_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.phone_edit = QLineEdit()
        self.location_edit = QLineEdit()
        self.budget_spin = QSpinBox()
        self.budget_spin.setRange(0, 10000000)
        self.budget_spin.setSuffix(" $")
        
        form_layout.addRow("Department Name:", self.name_edit)
        form_layout.addRow("Description:", self.description_edit)
        form_layout.addRow("Manager:", self.manager_edit)
        form_layout.addRow("Contact Email:", self.email_edit)
        form_layout.addRow("Contact Phone:", self.phone_edit)
        form_layout.addRow("Location:", self.location_edit)
        form_layout.addRow("Budget:", self.budget_spin)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                     QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Load existing data
        if self.department:
            self.load_department_data()
    
    def load_department_data(self):
        """Load existing department data into form"""
        self.name_edit.setText(self.department.get('name', ''))
        self.description_edit.setText(self.department.get('description', ''))
        self.manager_edit.setText(self.department.get('manager', ''))
        self.email_edit.setText(self.department.get('contact_email', ''))
        self.phone_edit.setText(self.department.get('contact_phone', ''))
        self.location_edit.setText(self.department.get('location', ''))
        self.budget_spin.setValue(int(self.department.get('budget', 0)))
    
    def get_department_data(self) -> Dict:
        """Get department data from form"""
        return {
            'name': self.name_edit.text().strip(),
            'description': self.description_edit.toPlainText().strip(),
            'manager': self.manager_edit.text().strip(),
            'contact_email': self.email_edit.text().strip(),
            'contact_phone': self.phone_edit.text().strip(),
            'location': self.location_edit.text().strip(),
            'budget': self.budget_spin.value()
        }


class DeviceAssignmentDialog(QDialog):
    """Dialog for assigning devices to departments/locations"""
    
    def __init__(self, db: DepartmentDatabase, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Assign Devices")
        self.setMinimumSize(600, 500)
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Selection area
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Device selection
        device_group = QGroupBox("📱 Select Devices")
        device_layout = QVBoxLayout(device_group)
        
        self.device_list = QListWidget()
        self.device_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        device_layout.addWidget(self.device_list)
        
        # Assignment options
        assign_group = QGroupBox("🏢 Assignment Options")
        assign_layout = QFormLayout(assign_group)
        
        self.department_combo = QComboBox()
        self.location_combo = QComboBox()
        self.assigned_by_edit = QLineEdit("Administrator")
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(60)
        
        assign_layout.addRow("Department:", self.department_combo)
        assign_layout.addRow("Location:", self.location_combo)
        assign_layout.addRow("Assigned By:", self.assigned_by_edit)
        assign_layout.addRow("Notes:", self.notes_edit)
        
        splitter.addWidget(device_group)
        splitter.addWidget(assign_group)
        splitter.setSizes([300, 300])
        
        layout.addWidget(splitter)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.assign_btn = QPushButton("✅ Assign Selected")
        self.assign_btn.clicked.connect(self.assign_devices)
        
        self.cancel_btn = QPushButton("❌ Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.assign_btn)
        button_layout.addWidget(self.cancel_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
    
    def load_data(self):
        """Load departments, locations, and unassigned devices"""
        # Load departments
        self.department_combo.addItem("-- None --", None)
        departments = self.db.get_departments()
        for dept in departments:
            self.department_combo.addItem(dept['name'], dept['id'])
        
        # Load locations
        self.location_combo.addItem("-- None --", None)
        locations = self.db.get_locations()
        for loc in locations:
            self.location_combo.addItem(loc['name'], loc['id'])
        
        # Load unassigned devices
        unassigned = self.db.get_unassigned_devices()
        for device in unassigned:
            item_text = f"{device['hostname']} ({device['ip_address']}) - {device['device_type']}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, device['id'])
            self.device_list.addItem(item)
    
    def assign_devices(self):
        """Assign selected devices"""
        selected_items = self.device_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select at least one device.")
            return
        
        department_id = self.department_combo.currentData()
        location_id = self.location_combo.currentData()
        assigned_by = self.assigned_by_edit.text().strip()
        notes = self.notes_edit.toPlainText().strip()
        
        if not department_id and not location_id:
            QMessageBox.warning(self, "Warning", "Please select at least a department or location.")
            return
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(selected_items))
        
        assigned_count = 0
        for i, item in enumerate(selected_items):
            asset_id = item.data(Qt.ItemDataRole.UserRole)
            if self.db.assign_device(asset_id, department_id, location_id, assigned_by, notes):
                assigned_count += 1
            self.progress_bar.setValue(i + 1)
        
        self.progress_bar.setVisible(False)
        
        QMessageBox.information(self, "Success", 
                               f"Successfully assigned {assigned_count} of {len(selected_items)} devices.")
        self.accept()


class DepartmentManagementWidget(QWidget):
    """Main department management widget"""
    
    # Signals
    department_updated = pyqtSignal()
    device_assigned = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.db = DepartmentDatabase()
        self.init_ui()
        self.load_data()
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.load_data)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("🏢 Department & Location Management")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.load_data)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Main tabs
        self.tab_widget = QTabWidget()
        
        # Departments tab
        self.departments_tab = self.create_departments_tab()
        self.tab_widget.addTab(self.departments_tab, "🏢 Departments")
        
        # Locations tab
        self.locations_tab = self.create_locations_tab()
        self.tab_widget.addTab(self.locations_tab, "📍 Locations")
        
        # Device assignments tab
        self.assignments_tab = self.create_assignments_tab()
        self.tab_widget.addTab(self.assignments_tab, "📱 Device Assignments")
        
        # Statistics tab
        self.stats_tab = self.create_statistics_tab()
        self.tab_widget.addTab(self.stats_tab, "📊 Statistics")
        
        layout.addWidget(self.tab_widget)
    
    def create_departments_tab(self):
        """Create departments management tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Actions bar
        actions_layout = QHBoxLayout()
        
        self.add_dept_btn = QPushButton("➕ Add Department")
        self.add_dept_btn.clicked.connect(self.add_department)
        actions_layout.addWidget(self.add_dept_btn)
        
        self.edit_dept_btn = QPushButton("✏️ Edit Selected")
        self.edit_dept_btn.clicked.connect(self.edit_department)
        actions_layout.addWidget(self.edit_dept_btn)
        
        self.delete_dept_btn = QPushButton("🗑️ Delete Selected")
        self.delete_dept_btn.clicked.connect(self.delete_department)
        actions_layout.addWidget(self.delete_dept_btn)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
        
        # Departments table
        self.departments_table = QTableWidget()
        self.departments_table.setColumnCount(8)
        self.departments_table.setHorizontalHeaderLabels([
            'Name', 'Manager', 'Email', 'Phone', 'Location', 'Budget', 'Devices', 'Status'
        ])
        
        header = self.departments_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.departments_table)
        
        return widget
    
    def create_locations_tab(self):
        """Create locations management tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Actions bar
        actions_layout = QHBoxLayout()
        
        self.add_location_btn = QPushButton("➕ Add Location")
        self.add_location_btn.clicked.connect(self.add_location)
        actions_layout.addWidget(self.add_location_btn)
        
        self.edit_location_btn = QPushButton("✏️ Edit Selected")
        self.edit_location_btn.clicked.connect(self.edit_location)
        actions_layout.addWidget(self.edit_location_btn)
        
        self.delete_location_btn = QPushButton("🗑️ Delete Selected")
        self.delete_location_btn.clicked.connect(self.delete_location)
        actions_layout.addWidget(self.delete_location_btn)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
        
        # Locations table
        self.locations_table = QTableWidget()
        self.locations_table.setColumnCount(7)
        self.locations_table.setHorizontalHeaderLabels([
            'Name', 'Building', 'Floor', 'Room', 'Capacity', 'Devices', 'Status'
        ])
        
        header = self.locations_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.locations_table)
        
        return widget
    
    def create_assignments_tab(self):
        """Create device assignments tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Actions bar
        actions_layout = QHBoxLayout()
        
        self.assign_devices_btn = QPushButton("📱 Assign Devices")
        self.assign_devices_btn.clicked.connect(self.assign_devices)
        actions_layout.addWidget(self.assign_devices_btn)
        
        self.bulk_assign_btn = QPushButton("📦 Bulk Assignment")
        self.bulk_assign_btn.clicked.connect(self.bulk_assign_devices)
        actions_layout.addWidget(self.bulk_assign_btn)
        
        self.unassign_btn = QPushButton("❌ Unassign Selected")
        self.unassign_btn.clicked.connect(self.unassign_device)
        actions_layout.addWidget(self.unassign_btn)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
        
        # Assignments table
        self.assignments_table = QTableWidget()
        self.assignments_table.setColumnCount(8)
        self.assignments_table.setHorizontalHeaderLabels([
            'Hostname', 'IP Address', 'Device Type', 'Department', 'Location', 'Assigned By', 'Assigned At', 'Notes'
        ])
        
        header = self.assignments_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.assignments_table)
        
        return widget
    
    def create_statistics_tab(self):
        """Create statistics and overview tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Statistics display
        self.stats_display = QTextEdit()
        self.stats_display.setFont(QFont("Consolas", 10))
        self.stats_display.setReadOnly(True)
        layout.addWidget(self.stats_display)
        
        return widget
    
    def load_data(self):
        """Load all data into tables"""
        self.load_departments()
        self.load_locations()
        self.load_assignments()
        self.load_statistics()
    
    def load_departments(self):
        """Load departments into table"""
        departments = self.db.get_departments()
        self.departments_table.setRowCount(len(departments))
        
        for i, dept in enumerate(departments):
            self.departments_table.setItem(i, 0, QTableWidgetItem(dept['name']))
            self.departments_table.setItem(i, 1, QTableWidgetItem(dept.get('manager', '')))
            self.departments_table.setItem(i, 2, QTableWidgetItem(dept.get('contact_email', '')))
            self.departments_table.setItem(i, 3, QTableWidgetItem(dept.get('contact_phone', '')))
            self.departments_table.setItem(i, 4, QTableWidgetItem(dept.get('location', '')))
            self.departments_table.setItem(i, 5, QTableWidgetItem(f"${dept.get('budget', 0):,.0f}"))
            self.departments_table.setItem(i, 6, QTableWidgetItem(str(dept.get('device_count', 0))))
            self.departments_table.setItem(i, 7, QTableWidgetItem(dept.get('status', 'Active')))
            
            # Store department ID in the first item
            self.departments_table.item(i, 0).setData(Qt.ItemDataRole.UserRole, dept['id'])
    
    def load_locations(self):
        """Load locations into table"""
        locations = self.db.get_locations()
        self.locations_table.setRowCount(len(locations))
        
        for i, loc in enumerate(locations):
            self.locations_table.setItem(i, 0, QTableWidgetItem(loc['name']))
            self.locations_table.setItem(i, 1, QTableWidgetItem(loc.get('building', '')))
            self.locations_table.setItem(i, 2, QTableWidgetItem(loc.get('floor', '')))
            self.locations_table.setItem(i, 3, QTableWidgetItem(loc.get('room', '')))
            self.locations_table.setItem(i, 4, QTableWidgetItem(str(loc.get('capacity', 0))))
            self.locations_table.setItem(i, 5, QTableWidgetItem(str(loc.get('device_count', 0))))
            self.locations_table.setItem(i, 6, QTableWidgetItem(loc.get('status', 'Active')))
            
            # Store location ID in the first item
            self.locations_table.item(i, 0).setData(Qt.ItemDataRole.UserRole, loc['id'])
    
    def load_assignments(self):
        """Load device assignments into table"""
        assignments = self.db.get_device_assignments()
        self.assignments_table.setRowCount(len(assignments))
        
        for i, assignment in enumerate(assignments):
            self.assignments_table.setItem(i, 0, QTableWidgetItem(assignment.get('hostname', '')))
            self.assignments_table.setItem(i, 1, QTableWidgetItem(assignment.get('ip_address', '')))
            self.assignments_table.setItem(i, 2, QTableWidgetItem(assignment.get('device_type', '')))
            self.assignments_table.setItem(i, 3, QTableWidgetItem(assignment.get('department_name', 'Unassigned')))
            self.assignments_table.setItem(i, 4, QTableWidgetItem(assignment.get('location_name', 'Unassigned')))
            self.assignments_table.setItem(i, 5, QTableWidgetItem(assignment.get('assigned_by', '')))
            
            assigned_at = assignment.get('assigned_at', '')
            if assigned_at:
                try:
                    dt = datetime.fromisoformat(assigned_at.replace('Z', '+00:00'))
                    assigned_at = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    pass
            
            self.assignments_table.setItem(i, 6, QTableWidgetItem(assigned_at))
            self.assignments_table.setItem(i, 7, QTableWidgetItem(assignment.get('notes', '')))
            
            # Store asset ID in the first item
            self.assignments_table.item(i, 0).setData(Qt.ItemDataRole.UserRole, assignment.get('asset_id'))
    
    def load_statistics(self):
        """Load and display statistics"""
        try:
            departments = self.db.get_departments()
            locations = self.db.get_locations()
            assignments = self.db.get_device_assignments()
            unassigned = self.db.get_unassigned_devices()
            
            # Calculate statistics
            total_departments = len(departments)
            active_departments = len([d for d in departments if d.get('status') == 'Active'])
            total_locations = len(locations)
            total_assignments = len([a for a in assignments if a.get('department_name') or a.get('location_name')])
            total_unassigned = len(unassigned)
            
            # Department device distribution
            dept_distribution = {}
            for dept in departments:
                dept_distribution[dept['name']] = dept.get('device_count', 0)
            
            # Location device distribution
            location_distribution = {}
            for loc in locations:
                location_distribution[loc['name']] = loc.get('device_count', 0)
            
            # Generate statistics text
            stats_text = f"""
📊 DEPARTMENT & LOCATION STATISTICS
{'=' * 50}

📈 OVERVIEW:
  • Total Departments: {total_departments} (Active: {active_departments})
  • Total Locations: {total_locations}
  • Assigned Devices: {total_assignments}
  • Unassigned Devices: {total_unassigned}

🏢 DEPARTMENT DISTRIBUTION:
"""
            
            for dept_name, count in sorted(dept_distribution.items(), key=lambda x: x[1], reverse=True):
                if count > 0:
                    stats_text += f"  • {dept_name}: {count} devices\n"
            
            stats_text += f"\n📍 LOCATION DISTRIBUTION:\n"
            
            for loc_name, count in sorted(location_distribution.items(), key=lambda x: x[1], reverse=True):
                if count > 0:
                    stats_text += f"  • {loc_name}: {count} devices\n"
            
            # Device type analysis
            if assignments:
                device_types = {}
                for assignment in assignments:
                    device_type = assignment.get('device_type', 'Unknown')
                    device_types[device_type] = device_types.get(device_type, 0) + 1
                
                stats_text += f"\n💻 DEVICE TYPE ANALYSIS:\n"
                for device_type, count in sorted(device_types.items(), key=lambda x: x[1], reverse=True):
                    stats_text += f"  • {device_type}: {count} devices\n"
            
            # Add recommendations
            stats_text += f"\n💡 RECOMMENDATIONS:\n"
            if total_unassigned > 0:
                stats_text += f"  • {total_unassigned} devices need department/location assignment\n"
            
            if active_departments == 0:
                stats_text += f"  • Create departments to organize your devices\n"
            
            if total_locations == 0:
                stats_text += f"  • Add locations to track device physical placement\n"
            
            self.stats_display.setText(stats_text.strip())
            
        except Exception as e:
            self.stats_display.setText(f"❌ Error loading statistics: {e}")
    
    def add_department(self):
        """Add new department"""
        dialog = DepartmentDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_department_data()
            if data['name']:
                if self.db.add_department(**data):
                    QMessageBox.information(self, "Success", "Department added successfully!")
                    self.load_departments()
                    self.department_updated.emit()
                else:
                    QMessageBox.warning(self, "Error", "Failed to add department. Name might already exist.")
            else:
                QMessageBox.warning(self, "Error", "Department name is required.")
    
    def edit_department(self):
        """Edit selected department"""
        current_row = self.departments_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a department to edit.")
            return
        
        dept_id = self.departments_table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        
        # Get current department data
        departments = self.db.get_departments()
        current_dept = next((d for d in departments if d['id'] == dept_id), None)
        
        if current_dept:
            dialog = DepartmentDialog(current_dept, parent=self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                data = dialog.get_department_data()
                if data['name']:
                    if self.db.update_department(dept_id, **data):
                        QMessageBox.information(self, "Success", "Department updated successfully!")
                        self.load_departments()
                        self.department_updated.emit()
                    else:
                        QMessageBox.warning(self, "Error", "Failed to update department.")
                else:
                    QMessageBox.warning(self, "Error", "Department name is required.")
    
    def delete_department(self):
        """Delete selected department"""
        current_row = self.departments_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a department to delete.")
            return
        
        dept_name = self.departments_table.item(current_row, 0).text()
        dept_id = self.departments_table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(self, "Confirm Delete", 
                                   f"Are you sure you want to delete department '{dept_name}'?\n\n"
                                   "Note: Departments with assigned devices cannot be deleted.",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.db.delete_department(dept_id):
                QMessageBox.information(self, "Success", "Department deleted successfully!")
                self.load_departments()
                self.department_updated.emit()
            else:
                QMessageBox.warning(self, "Error", 
                                  "Cannot delete department. It may have assigned devices or other dependencies.")
    
    def add_location(self):
        """Add new location"""
        # Simple input dialog for location
        from PyQt6.QtWidgets import QInputDialog
        
        name, ok = QInputDialog.getText(self, "Add Location", "Location Name:")
        if ok and name.strip():
            if self.db.add_location(name.strip()):
                QMessageBox.information(self, "Success", "Location added successfully!")
                self.load_locations()
            else:
                QMessageBox.warning(self, "Error", "Failed to add location. Name might already exist.")
    
    def edit_location(self):
        """Edit selected location"""
        QMessageBox.information(self, "Info", "Location editing will be implemented in future updates.")
    
    def delete_location(self):
        """Delete selected location"""
        QMessageBox.information(self, "Info", "Location deletion will be implemented in future updates.")
    
    def assign_devices(self):
        """Open device assignment dialog"""
        dialog = DeviceAssignmentDialog(self.db, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_assignments()
            self.load_departments()
            self.load_locations()
            self.load_statistics()
            self.device_assigned.emit()
    
    def bulk_assign_devices(self):
        """Bulk assign devices"""
        QMessageBox.information(self, "Info", "Bulk assignment will be implemented in future updates.")
    
    def unassign_device(self):
        """Unassign selected device"""
        current_row = self.assignments_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a device to unassign.")
            return
        
        hostname = self.assignments_table.item(current_row, 0).text()
        asset_id = self.assignments_table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(self, "Confirm Unassign", 
                                   f"Are you sure you want to unassign device '{hostname}'?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            # Remove assignment by deleting from device_assignments table
            try:
                with sqlite3.connect(self.db.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM device_assignments WHERE asset_id = ?", (asset_id,))
                    cursor.execute("""
                        UPDATE assets 
                        SET department = NULL, location = NULL, updated_at = ?
                        WHERE id = ?
                    """, (datetime.now().isoformat(), asset_id))
                    conn.commit()
                
                QMessageBox.information(self, "Success", "Device unassigned successfully!")
                self.load_assignments()
                self.load_departments()
                self.load_locations()
                self.load_statistics()
                self.device_assigned.emit()
                
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to unassign device: {e}")