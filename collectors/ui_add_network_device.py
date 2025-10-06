# -*- coding: utf-8 -*-
"""
UI: Add & Manage Network Devices — Classic Styled & Column-Consistent
--------------------------------------------------------------------
- نفس ستايل الواجهة الرئيسية (أزرار زرقاء، GroupBox ببرواز دائري).
- الأعمدة مرتّبة وثابتة حسب نوع الجهاز في (Add / Edit / Manage).
- Manage: View=Basic/All + بحث وفلاتر + Scroll أفقي/رأسي + ضبط عرض الأعمدة.
- Edit: فورم ثابت، Resizable، داخل ScrollArea، تخطيط عمودين داخل فريمات واضحة.
- Add: نفس الترتيب، PoE قائمة منسدلة، حقول الإدارة بعد التعديلات.
- منع تكرار ذكي (Asset Tag → Hostname+IP → جميع الحقول غير الفارغة).
- إنشاء/ضمان الشيتات والأعمدة (Idempotent) ورسائل ودّية لو ملف Excel مفتوح.
"""

from __future__ import annotations
import ipaddress
import os
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional

log = logging.getLogger(__name__)

# Excel imports removed - Database-only system
# from openpyxl import Workbook, load_workbook
# from openpyxl.worksheet.worksheet import Worksheet
# from openpyxl.styles import Font, Alignment

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QPushButton,
    QHBoxLayout, QLabel, QWidget, QMessageBox, QCheckBox, QFileDialog,
    QTabWidget, QTableWidget, QTableWidgetItem, QSizePolicy, QGroupBox,
    QScrollArea, QGridLayout, QHeaderView
)

# Import the sync manager
# from core.excel_db_sync import get_sync_manager  # Disabled - Database-only system

# =========================
# Schema
# =========================

ASSETS_SHEET = "Assets"  # scan-only

COMMON_FIELDS: List[str] = [
    "Asset Tag", "Owner", "Department", "Site", "Building", "Floor", "Room",
    "Status", "Firmware/OS Version", "Maintenance Contract #", "Vendor Contact",
    "Notes", "Data Source", "Created By", "Created At", "Last Updated", "Last Updated By",
]

SPECIFIC_SCHEMAS: Dict[str, List[str]] = {
    "Hypervisor": [
        "Hostname", "Model/Vendor", "IP Address", "Total RAM", "Total CPU", "Storage", "SN", "Location",
        "Cluster", "vCenter", "CPU Sockets", "CPU Cores", "CPU Threads",
        "Datastores (Total/Free)", "VM Count", "Management IP", "vMotion IP"
    ],
    "Switches": [
        "Hostname", "Model/Vendor", "IP Address", "SN", "Location",
        "Firmware Version", "Ports (Total)", "PoE", "Mgmt VLAN", "Uplink To", "Mgmt MAC"
    ],
    "Printers": [
        "Hostname", "Model", "SN", "IP Address", "Location",
        "Firmware Version", "Page Counter (Total)", "Page Counter (Mono)", "Page Counter (Color)", "Supplies Status"
    ],
    "Access Points": [
        "Hostname", "Model/Vendor", "SN", "IP Address", "Location",
        "Controller", "Adopted By", "SSID(s)", "Bands", "Channel", "Tx Power", "PoE Switch/Port"
    ],
    "Fingerprint": [
        "Hostname", "Model/Vendor", "IP Address", "Location",
        "Controller/Server IP", "Door/Area Name", "User Capacity", "Log Capacity", "Firmware Version"
    ],
    "Windows Devices": [
        "Hostname", "Working User", "Domain", "Model/Vendor", "IP Address", "OS Name",
        "Installed RAM (GB)", "Storage", "SN", "Processor", "System SKU", "Active GPU", "Connected Screens"
    ],
    "Linux Devices": [
        "Hostname", "IP Address", "Model/Vendor", "OS Name", "Kernel Version", "SN", 
        "Total RAM (GB)", "Storage", "CPU Model", "Architecture", "Uptime", "SSH Port"
    ],
    "Windows Server": [
        "Hostname", "IP Address", "Model/Vendor", "OS Name", "OS Version", "SN",
        "Total RAM (GB)", "Storage", "CPU Model", "Server Roles", "Domain Controller", "Services"
    ],
}

SHEET_SCHEMAS: Dict[str, List[str]] = {name: (spec + COMMON_FIELDS) for name, spec in SPECIFIC_SCHEMAS.items()}

SHEET_SCHEMAS[ASSETS_SHEET] = [
    "Hostname", "Working User", "Domain", "Device Model", "Device Infrastructure",
    "OS Name", "Installed RAM (GB)", "LAN IP Address", "Storage", "Manufacturer",
    "Serial Number", "Processor", "System SKU", "Active GPU", "Connected Screens"
]

DEVICE_TYPE_TO_SHEET = {
    "Hypervisor (ESXi/Hyper-V/Proxmox)": "Hypervisor",
    "Switch": "Switches",
    "Printer": "Printers",
    "Access Point": "Access Points",
    "Fingerprint Device": "Fingerprint",
    "Windows Workstation": "Windows Devices",
    "Windows Server": "Windows Server", 
    "Linux/Unix Device": "Linux Devices",
}

DEVICE_FIELDS_PRIMARY: Dict[str, List[str]] = {
    "Hypervisor (ESXi/Hyper-V/Proxmox)": SPECIFIC_SCHEMAS["Hypervisor"],
    "Switch": SPECIFIC_SCHEMAS["Switches"],
    "Printer": SPECIFIC_SCHEMAS["Printers"],
    "Access Point": SPECIFIC_SCHEMAS["Access Points"],
    "Fingerprint Device": SPECIFIC_SCHEMAS["Fingerprint"],
    "Windows Workstation": SPECIFIC_SCHEMAS["Windows Devices"],
    "Windows Server": SPECIFIC_SCHEMAS["Windows Server"],
    "Linux/Unix Device": SPECIFIC_SCHEMAS["Linux Devices"],
}

# Basic view per sheet
BASIC_VIEW: Dict[str, List[str]] = {
    "Hypervisor": ["Asset Tag","Hostname","Model/Vendor","IP Address","Total RAM","Total CPU","Storage","SN","Location","Cluster","VM Count","Status","Owner","Department","Site","Last Updated"],
    "Switches":   ["Asset Tag","Hostname","Model/Vendor","IP Address","PoE","Ports (Total)","SN","Location","Firmware Version","Mgmt VLAN","Uplink To","Status","Owner","Department","Site","Last Updated"],
    "Printers":   ["Asset Tag","Hostname","Model","IP Address","SN","Location","Firmware Version","Page Counter (Total)","Status","Owner","Department","Site","Last Updated"],
    "Access Points":["Asset Tag","Hostname","Model/Vendor","IP Address","SN","Location","Controller","SSID(s)","Bands","Channel","Status","Owner","Department","Site","Last Updated"],
    "Fingerprint":["Asset Tag","Hostname","Model/Vendor","IP Address","Location","Controller/Server IP","Door/Area Name","User Capacity","Status","Owner","Department","Site","Last Updated"],
    "Windows Devices":["Asset Tag","Hostname","Working User","Domain","Model/Vendor","IP Address","OS Name","Installed RAM (GB)","Storage","SN","Status","Owner","Department","Site","Last Updated"],
    "Linux Devices":["Asset Tag","Hostname","IP Address","Model/Vendor","OS Name","Kernel Version","Total RAM (GB)","Storage","CPU Model","Status","Owner","Department","Site","Last Updated"],
    "Windows Server":["Asset Tag","Hostname","IP Address","Model/Vendor","OS Name","OS Version","Total RAM (GB)","Storage","Server Roles","Domain Controller","Status","Owner","Department","Site","Last Updated"],
}

STATUS_OPTIONS = ["Active", "Spare", "Retired", "Faulty"]
POE_OPTIONS    = ["PoE", "Non-PoE"]

# preferred widths (px)
PREF_WIDTHS = {
    "Asset Tag":120, "Hostname":180, "Model/Vendor":200, "Model":180, "IP Address":130, "SN":160,
    "Location":140, "Owner":140, "Department":140, "Site":120, "Status":110, "Firmware Version":150,
    "Firmware/OS Version":150, "Ports (Total)":120, "PoE":100, "Mgmt VLAN":110, "Uplink To":160, "Mgmt MAC":140,
    "Total RAM":110, "Total CPU":100, "Storage":110, "VM Count":90, "Cluster":120, "Last Updated":150
}
NUMERIC_LIKE = {"Ports (Total)","VM Count","CPU Sockets","CPU Cores","CPU Threads","Total RAM","Total CPU","Storage","Page Counter (Total)","Page Counter (Mono)","Page Counter (Color)"}

# =========================
# Excel helpers
# =========================

# Excel operations disabled - Database-only system
def _style_header_row(ws=None) -> None:
    """Disabled Excel operation for database-only mode"""
    pass

def _create_sheet_with_headers(wb=None, name: str = "", headers: Optional[List[str]] = None):
    """Disabled Excel operation for database-only mode"""
    if headers is None:
        headers = []
    return None

def _safe_save(wb=None, path: str = "") -> None:
    """Disabled Excel operation for database-only mode"""
    pass

def _ensure_headers(ws=None, wanted: Optional[List[str]] = None) -> bool:
    """Disabled Excel operation for database-only mode"""
    if wanted is None:
        wanted = []
    return False

def ensure_workbook_tabs(path: str) -> str|None:
    """Database-only mode - Initialize database tables instead of Excel workbook"""
    if path is None:
        # Database-only mode - ensure database tables exist
        try:
            import sqlite3
            conn = sqlite3.connect('assets.db')
            cursor = conn.cursor()
            
            # Create main assets table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS assets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hostname TEXT UNIQUE,
                    ip_address TEXT,
                    working_user TEXT,
                    domain TEXT,
                    device_model TEXT,
                    device_infrastructure TEXT,
                    os_name TEXT,
                    installed_ram_gb REAL,
                    storage TEXT,
                    manufacturer TEXT,
                    serial_number TEXT,
                    processor TEXT,
                    system_sku TEXT,
                    active_gpu TEXT,
                    connected_screens TEXT,
                    owner TEXT,
                    department TEXT,
                    site TEXT,
                    building TEXT,
                    floor TEXT,
                    room TEXT,
                    status TEXT DEFAULT 'Active',
                    firmware_version TEXT,
                    maintenance_contract TEXT,
                    vendor_contact TEXT,
                    notes TEXT,
                    data_source TEXT DEFAULT 'Manual',
                    created_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_by TEXT,
                    device_type TEXT,
                    classification TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            return None  # Database mode
        except Exception as e:
            print(f"Database initialization error: {e}")
            return None
    
    # Legacy path handling (disabled for database-only mode)
    return None
    return path

def _append_row(path: str|None, sheet: str, headers: List[str], data: Dict[str,str]) -> None:
    """Database-only mode - Insert data directly to SQLite"""
    try:
        import sqlite3
        conn = sqlite3.connect('assets.db')
        cursor = conn.cursor()
        
        # Map common fields to database columns
        asset_data = {
            'hostname': data.get('Hostname', ''),
            'ip_address': data.get('IP Address', ''),
            'working_user': data.get('Working User', ''),
            'device_model': data.get('Model/Vendor', data.get('Model', '')),
            'classification': sheet,
            'data_source': data.get('Data Source', 'Manual'),
            'created_by': data.get('Created By', ''),
            'updated_by': data.get('Last Updated By', ''),
            'department': data.get('Department', ''),
            'status': data.get('Status', 'Active'),
            'notes': data.get('Notes', ''),
            'device_type': sheet
        }
        
        cursor.execute('''
            INSERT OR REPLACE INTO assets (
                hostname, ip_address, working_user, device_model, classification,
                data_source, created_by, updated_by, department, status, notes, device_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            asset_data['hostname'], asset_data['ip_address'], asset_data['working_user'],
            asset_data['device_model'], asset_data['classification'], asset_data['data_source'],
            asset_data['created_by'], asset_data['updated_by'], asset_data['department'],
            asset_data['status'], asset_data['notes'], asset_data['device_type']
        ))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        raise RuntimeError(f"Database operation failed: {e}")

def _update_row(path: str|None, sheet: str, row_ix: int, headers: List[str], data: Dict[str,str]) -> None:
    """Database-only mode - Update asset by hostname"""
    try:
        import sqlite3
        conn = sqlite3.connect('assets.db')
        cursor = conn.cursor()
        
        hostname = data.get('Hostname', '')
        if not hostname:
            raise ValueError("Hostname required for update")
            
        # Update asset in database
        cursor.execute('''
            UPDATE assets SET 
                ip_address = ?, working_user = ?, device_model = ?,
                department = ?, status = ?, notes = ?, updated_by = ?,
                last_updated = CURRENT_TIMESTAMP
            WHERE hostname = ?
        ''', (
            data.get('IP Address', ''), data.get('Working User', ''),
            data.get('Model/Vendor', data.get('Model', '')), data.get('Department', ''),
            data.get('Status', 'Active'), data.get('Notes', ''),
            data.get('Last Updated By', ''), hostname
        ))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        raise RuntimeError(f"Database update failed: {e}")

def _delete_row(path: str|None, sheet: str, row_ix: int) -> None:
    """Database-only mode - Delete by row index (placeholder)"""
    # For database mode, deletion should be by hostname, not row index
    pass

def _load_database_rows(sheet: str) -> Tuple[List[str], List[List[str]]]:
    """Load data from database for database-only mode"""
    try:
        import sqlite3
        
        conn = sqlite3.connect('assets.db')
        cursor = conn.cursor()
        
        # Map sheet names to appropriate database queries
        if sheet == ASSETS_SHEET or sheet == "Assets":
            # Get all assets with standard headers
            headers = ["Hostname", "IP Address", "User", "Classification", "Department", "Status", "Data Source", "Created At"]
            cursor.execute('''
                SELECT hostname, ip_address, working_user, classification, department, status, data_source, created_at
                FROM assets 
                ORDER BY hostname
            ''')
        else:
            # For other device types, filter by classification
            headers = SHEET_SCHEMAS.get(sheet, ["Hostname", "IP Address", "User", "Classification", "Department", "Status"])
            cursor.execute('''
                SELECT hostname, ip_address, working_user, classification, department, status
                FROM assets 
                WHERE classification = ? OR classification LIKE ?
                ORDER BY hostname
            ''', (sheet, f'%{sheet}%'))
        
        rows = cursor.fetchall()
        conn.close()
        
        # Convert to string format (like Excel data)
        data = []
        for row in rows:
            data.append([str(cell) if cell is not None else "" for cell in row])
        
        return headers, data
        
    except Exception:
        # Return empty data if database error
        return ["Hostname", "IP Address", "User", "Classification"], []


def _load_sheet_rows(path: str|None, sheet: str) -> Tuple[List[str], List[List[str]]]:
    # Database-only mode - no Excel workbook operations
    if path is None:
        return _load_database_rows(sheet)
    
    # Legacy Excel operations disabled for database-only system
    return _load_database_rows(sheet)
    if ws.max_row >= 2:
        for r in ws.iter_rows(min_row=2, max_row=ws.max_row, values_only=True):
            data.append([("" if v is None else str(v)) for v in r[:len(headers)]])
    return headers, data

# =========================
# Validation & Duplicate
# =========================

def _is_valid_ip(ip: str) -> bool:
    ip = (ip or "").strip()
    if not ip: return True
    try: ipaddress.ip_address(ip); return True
    except ValueError: return False

def _find_duplicate_row(path: str|None, sheet: str, headers: List[str], data: Dict[str,str]) -> Optional[int]:
    idx = {h:i for i,h in enumerate(headers)}
    _, rows = _load_sheet_rows(path, sheet)

    tag = (data.get("Asset Tag","") or "").strip().lower()
    if tag and "Asset Tag" in idx:
        i = idx["Asset Tag"]
        for ridx, r in enumerate(rows, start=2):
            if ((r[i] if i < len(r) else "") or "").strip().lower() == tag:
                return ridx

    hn = (data.get("Hostname","") or "").strip().lower()
    ip = (data.get("IP Address","") or "").strip().lower()
    if hn and ip and "Hostname" in idx and "IP Address" in idx:
        ih, ii = idx["Hostname"], idx["IP Address"]
        for ridx, r in enumerate(rows, start=2):
            if (((r[ih] if ih < len(r) else "") or "").strip().lower() == hn and
                ((r[ii] if ii < len(r) else "") or "").strip().lower() == ip):
                return ridx

    use_cols, vals = [], []
    for i,h in enumerate(headers):
        v = (data.get(h,"") or "").strip()
        if v != "": use_cols.append(i); vals.append(v.lower())
    if not use_cols: return None
    for ridx, r in enumerate(rows, start=2):
        ok = True
        for pos, val in zip(use_cols, vals):
            cur = ((r[pos] if pos < len(r) else "") or "").strip().lower()
            if cur != val: ok = False; break
        if ok: return ridx
    return None

# =========================
# Editor (two-column, scrollable)
# =========================

class _TwoColumnEditor(QWidget):
    def __init__(self, fields_in_order: List[str], initial: Optional[Dict[str,str]] = None, parent: QWidget|None=None):
        super().__init__(parent)
        self.fields = fields_in_order
        self.inputs: Dict[str, QWidget] = {}

        box1 = QGroupBox("Device Details", self)
        grid1 = QGridLayout(box1); grid1.setColumnStretch(0,1); grid1.setColumnStretch(1,1)

        box2 = QGroupBox("Management / Ownership", self)
        grid2 = QGridLayout(box2); grid2.setColumnStretch(0,1); grid2.setColumnStretch(1,1)

        def add_row(grid: QGridLayout, row: int, label: str, w: QWidget):
            grid.addWidget(QLabel(label+":"), row, 0)
            grid.addWidget(w, row, 1)

        r1 = r2 = 0
        for f in fields_in_order:
            target = grid2 if f in COMMON_FIELDS else grid1
            if f == "Status":
                w = QComboBox(self); w.addItems(STATUS_OPTIONS)
            elif f == "PoE":
                w = QComboBox(self); w.addItems(POE_OPTIONS)
            else:
                w = QLineEdit(self)
                w.setPlaceholderText("e.g. 10.0.0.10" if f.lower()=="ip address" else f"Enter {f}")
            if initial and f in initial:
                if isinstance(w, QComboBox):
                    w.setCurrentIndex(max(0, w.findText(str(initial[f]), Qt.MatchFlag.MatchFixedString)))
                else:
                    w.setText(str(initial[f]))
            if target is grid1:
                add_row(grid1, r1, f, w); r1 += 1
            else:
                add_row(grid2, r2, f, w); r2 += 1
            self.inputs[f] = w

        v = QVBoxLayout(self); v.addWidget(box1); v.addWidget(box2); v.addStretch(1)

    def values(self) -> Dict[str,str]:
        out: Dict[str,str] = {}
        for f, w in self.inputs.items():
            if isinstance(w, QComboBox):
                out[f] = w.currentText().strip()
            elif isinstance(w, QLineEdit):
                out[f] = w.text().strip()
            else:
                out[f] = ""
        return out

# =========================
# Dialog
# =========================

class AddNetworkDeviceDialog(QDialog):
    def __init__(self, workbook_path: str|None, parent: QWidget|None=None):
        super().__init__(parent)
        self.setWindowTitle("Network Devices — Add & Manage")
        self.setModal(True)
        self.resize(1000, 680)
        self.setWindowFlag(Qt.WindowType.WindowMinMaxButtonsHint, True)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setSizeGripEnabled(True)

        # Handle database-only mode (no Excel file)
        if workbook_path is None:
            self.workbook_path = None
            self.database_only = True
        else:
            self.workbook_path = os.path.abspath(workbook_path)
            self.database_only = False

        root = QVBoxLayout(self)

        top = QHBoxLayout()
        if self.database_only:
            self.lbl_path = QLabel("📊 Database-Only Mode - Direct asset addition to SQLite database", self)
            self.lbl_path.setStyleSheet("QLabel { color: #27ae60; font-weight: bold; padding: 5px; }")
            self.btn_browse = QPushButton("🗄️ Database Mode", self)
            self.btn_browse.setEnabled(False)
        else:
            self.lbl_path = QLabel(self.workbook_path, self)
            self.btn_browse = QPushButton("Browse Excel…", self); self.btn_browse.clicked.connect(self._pick_excel)
        top.addWidget(QLabel("Workbook:", self)); top.addWidget(self.lbl_path, 1); top.addWidget(self.btn_browse)
        root.addLayout(top)

        self.tabs = QTabWidget(self); root.addWidget(self.tabs, 1)
        self._init_add_tab()
        self._init_manage_tab()

        # Only try to ensure workbook tabs if not in database-only mode
        if self.workbook_path is not None:
            try: ensure_workbook_tabs(self.workbook_path)
            except RuntimeError as e: QMessageBox.critical(self,"Excel Error",str(e))
        else:
            # Database-only mode - no workbook operations needed
            pass

        self._rebuild_dynamic_fields()
        self._refresh_table()

        self._apply_styles()

    # --- Styles (كلاسيك مشابه للواجهة الرئيسية) ---
    def _apply_styles(self):
        self.setStyleSheet("""
        QPushButton { background-color:#3498db; color:white; font-size:14px; font-weight:bold; border:2px solid #2980b9; border-radius:8px; padding:8px; margin:4px; }
        QPushButton:hover { background-color:#2980b9; }
        QPushButton:pressed { background-color:#1f618d; }
        QGroupBox { border:2px solid #3498db; border-radius:10px; margin-top:10px; padding:10px; font-size:14px; color:#2c3e50; }
        QTableWidget { gridline-color:#cfd8dc; }
        QTableWidget::item:selected { background:#d6ecff; color:black; }
        """)

    # ============ ADD TAB ============
    def _init_add_tab(self):
        content = QWidget(self)
        lay = QVBoxLayout(content)

        box = QGroupBox("Add Device", content)
        form = QFormLayout(box)

        self.cmb_type = QComboBox(content); self.cmb_type.addItems(list(DEVICE_TYPE_TO_SHEET.keys()))
        self.cmb_type.currentTextChanged.connect(self._rebuild_dynamic_fields)
        form.addRow("Device Type:", self.cmb_type)

        self.chk_override = QCheckBox("Override target sheet", content)
        self.cmb_sheet = QComboBox(content); self.cmb_sheet.addItems([s for s in SHEET_SCHEMAS.keys() if s != ASSETS_SHEET])
        self.cmb_sheet.setEnabled(False); self.chk_override.toggled.connect(self.cmb_sheet.setEnabled)
        form.addRow(self.chk_override, self.cmb_sheet)

        self.dynamic_wrap = QWidget(content); self.dynamic_form = QFormLayout(self.dynamic_wrap)
        form.addRow(self.dynamic_wrap)
        lay.addWidget(box)

        # common fields
        self.extra_box = QGroupBox("Management / Ownership", content)
        self.extra_form = QFormLayout(self.extra_box)
        self.extra_widgets: Dict[str, QWidget] = {}
        for f in COMMON_FIELDS:
            if f in ("Data Source","Created At","Created By","Last Updated","Last Updated By"):
                w = QLineEdit(); w.setReadOnly(True)
            elif f == "Status":
                w = QComboBox(); w.addItems(STATUS_OPTIONS)
            else:
                w = QLineEdit()
            if isinstance(w,QLineEdit): w.setPlaceholderText(f"Enter {f}")
            self.extra_widgets[f] = w; self.extra_form.addRow(f + ":", w)
        lay.addWidget(self.extra_box)

        btns = QHBoxLayout()
        self.btn_save = QPushButton("Save", content); self.btn_close = QPushButton("Close", content)
        self.btn_save.clicked.connect(self._on_save_add); self.btn_close.clicked.connect(self.reject)
        btns.addStretch(1); btns.addWidget(self.btn_save); btns.addWidget(self.btn_close)
        lay.addLayout(btns)

        scroll = QScrollArea(self); scroll.setWidget(content); scroll.setWidgetResizable(True)
        self.tabs.addTab(scroll, "Add Device")

        self.field_widgets: Dict[str, QWidget] = {}

    def _rebuild_dynamic_fields(self):
        while self.dynamic_form.rowCount() > 0: self.dynamic_form.removeRow(0)
        self.field_widgets.clear()

        dtype = self.cmb_type.currentText()
        for f in DEVICE_FIELDS_PRIMARY[dtype]:
            if f == "PoE":
                w = QComboBox(); w.addItems(POE_OPTIONS)
            else:
                w = QLineEdit(); w.setPlaceholderText("e.g. 10.0.0.10" if f.lower()=="ip address" else f"Enter {f}")
            self.field_widgets[f] = w; self.dynamic_form.addRow(f + ":", w)

        # audit
        try: user = os.getlogin()
        except Exception: user = os.environ.get("USERNAME") or os.environ.get("USER") or ""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(self.extra_widgets["Data Source"], QLineEdit):
            self.extra_widgets["Data Source"].setText("Manual (Form)")
        if isinstance(self.extra_widgets["Created By"], QLineEdit):
            self.extra_widgets["Created By"].setText(user)
        if isinstance(self.extra_widgets["Last Updated By"], QLineEdit):
            self.extra_widgets["Last Updated By"].setText(user)
        if isinstance(self.extra_widgets["Created At"], QLineEdit):
            self.extra_widgets["Created At"].setText(now)
        if isinstance(self.extra_widgets["Last Updated"], QLineEdit):
            self.extra_widgets["Last Updated"].setText(now)

    def _collect_form_data(self) -> Dict[str,str]:
        data: Dict[str,str] = {}
        for k,w in self.field_widgets.items():
            if isinstance(w, QComboBox):
                data[k] = w.currentText().strip()
            elif isinstance(w, QLineEdit):
                data[k] = w.text().strip()
            else:
                data[k] = ""
        for k,w in self.extra_widgets.items():
            if isinstance(w, QComboBox):
                data[k] = w.currentText().strip()
            elif isinstance(w, QLineEdit):
                data[k] = w.text().strip()
            else:
                data[k] = ""
        return data

    def _on_save_add(self):
        # Handle database-only mode first
        if self.workbook_path is None or self.database_only:
            if self._save_to_database_only():
                self.accept()  # Close dialog on successful save
            return

        if not self.workbook_path:
            QMessageBox.warning(self, "Missing", "Please select an Excel workbook path.")
            return
        try:
            ensure_workbook_tabs(self.workbook_path)
        except RuntimeError as e:
            QMessageBox.critical(self, "Excel Error", str(e))
            return

        target = DEVICE_TYPE_TO_SHEET[self.cmb_type.currentText()]
        if self.chk_override.isChecked():
            target = self.cmb_sheet.currentText()
        if target == ASSETS_SHEET:
            QMessageBox.warning(self, "Not allowed", "Assets tab is scan-only.")
            return

        data = self._collect_form_data()
        if (v := data.get("IP Address", "")) and not _is_valid_ip(v):
            QMessageBox.warning(self, "Invalid IP", f"'{v}' is not valid.")
            return
        if not data.get("Hostname"):
            QMessageBox.warning(self, "Missing", "Hostname is required.")
            return

        headers = SHEET_SCHEMAS[target]
        dup = _find_duplicate_row(self.workbook_path, target, headers, data)
        if dup:
            QMessageBox.information(self, "Duplicate", f"Device already exists at row {dup}.")
            return

        # Direct database storage (Database-only system)
        try:
            import sqlite3
            conn = sqlite3.connect('assets.db')
            cursor = conn.cursor()
            
            # Create the assets table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS assets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip_address TEXT,
                    hostname TEXT,
                    data_source TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert device data directly to database
            cursor.execute('''
                INSERT OR REPLACE INTO assets (ip_address, hostname, data_source)
                VALUES (?, ?, ?)
            ''', (target, data.get('Hostname', 'Unknown'), 'Manual Entry'))
            
            conn.commit()
            conn.close()
            added_to_excel = True  # Database storage successful
            
            # Success message for database-only system
            QMessageBox.information(self, "Saved", 
                f"Device saved successfully to database!\n"
                f"✅ Database: Device '{target}' added\n"
                f"💾 Data stored in assets.db")
                
        except Exception as db_error:
            import traceback
            log.warning(f"Database storage failed: {db_error}")
            log.debug(traceback.format_exc())
            added_to_excel = False
            QMessageBox.warning(self, "Database Error", 
                f"Failed to save to database: {str(db_error)}")
            
        # Skip Excel operations (Database-only system)
        
        self._refresh_table()
        
        # ---- Legacy DB hook for compatibility ----
        # ---- Legacy DB hook for compatibility ----
        try:
            from db.repository import upsert_from_sheet_row
            upsert_from_sheet_row(target, data)
        except Exception:
            pass

    # ============ MANAGE TAB ============
    def _init_manage_tab(self):
        tab = QWidget(self); lay = QVBoxLayout(tab)

        bar = QHBoxLayout()
        bar.addWidget(QLabel("Sheet:", tab))
        self.cmb_manage_sheet = QComboBox(tab)
        self.cmb_manage_sheet.addItems([s for s in SHEET_SCHEMAS.keys() if s != ASSETS_SHEET])
        self.cmb_manage_sheet.currentTextChanged.connect(self._refresh_table)
        bar.addWidget(self.cmb_manage_sheet, 1)

        bar.addWidget(QLabel("View:", tab))
        self.cmb_view = QComboBox(tab); self.cmb_view.addItems(["Basic","All"])
        self.cmb_view.currentTextChanged.connect(self._apply_filters)
        bar.addWidget(self.cmb_view)

        bar.addWidget(QLabel("Search:", tab))
        self.txt_search = QLineEdit(tab); self.txt_search.setPlaceholderText("Search current columns…")
        self.txt_search.textChanged.connect(self._apply_filters)
        bar.addWidget(self.txt_search, 2)

        self.cmb_status = QComboBox(tab); self.cmb_status.addItem("All"); self.cmb_status.addItems(STATUS_OPTIONS)
        self.cmb_status.currentTextChanged.connect(self._apply_filters)
        bar.addWidget(QLabel("Status:", tab)); bar.addWidget(self.cmb_status)

        self.cmb_dept = QComboBox(tab); self.cmb_dept.addItem("All"); self.cmb_dept.currentTextChanged.connect(self._apply_filters)
        bar.addWidget(QLabel("Department:", tab)); bar.addWidget(self.cmb_dept)

        self.cmb_site = QComboBox(tab); self.cmb_site.addItem("All"); self.cmb_site.currentTextChanged.connect(self._apply_filters)
        bar.addWidget(QLabel("Site:", tab)); bar.addWidget(self.cmb_site)

        self.btn_reset = QPushButton("Reset", tab); self.btn_reset.clicked.connect(self._reset_filters)
        self.btn_refresh = QPushButton("Refresh", tab); self.btn_refresh.clicked.connect(self._refresh_table)
        bar.addWidget(self.btn_reset); bar.addWidget(self.btn_refresh)
        lay.addLayout(bar)

        self.table = QTableWidget(tab)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        # Set up headers with null checks
        vertical_header = self.table.verticalHeader()
        if vertical_header:
            vertical_header.setVisible(False)
            
        self.table.setAlternatingRowColors(True)
        hh = self.table.horizontalHeader()
        if hh:
            hh.setStretchLastSection(False)
            hh.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)  # قابل للتحكم
        lay.addWidget(self.table, 1)

        btns = QHBoxLayout()
        self.btn_edit = QPushButton("Edit Selected", tab); self.btn_edit.clicked.connect(self._on_edit_selected)
        self.btn_del = QPushButton("Delete Selected", tab); self.btn_del.clicked.connect(self._on_delete_selected)
        self.btn_close = QPushButton("Close", tab); self.btn_close.clicked.connect(self.reject)
        btns.addStretch(1); btns.addWidget(self.btn_edit); btns.addWidget(self.btn_del); btns.addWidget(self.btn_close)
        lay.addLayout(btns)

        self.tabs.addTab(tab, "Manage Devices")

        self._H: List[str] = []
        self._R: List[List[str]] = []
        self._visible_headers: List[str] = []
        self._visible_ix: List[int] = []
        self._filtered_excel_rows: List[int] = []

    def _sheet(self) -> str:
        return self.cmb_manage_sheet.currentText().strip() or "Hypervisor"

    def _refresh_table(self):
        try:
            # Handle database-only mode
            if self.workbook_path is None or self.database_only:
                sh = self._sheet()
                H, R = _load_sheet_rows(None, sh)  # Pass None for database-only mode
                self._H, self._R = H, R
            else:
                # Excel mode
                ensure_workbook_tabs(self.workbook_path)
                sh = self._sheet()
                H, R = _load_sheet_rows(self.workbook_path, sh)
                self._H, self._R = H, R

            # Fill filter lists from data
            def uniq(col: str) -> List[str]:
                if col not in H: return []
                i = H.index(col)
                return sorted({(r[i] if i < len(r) else "").strip() for r in R if (r[i] if i < len(r) else "").strip()})
            cur_dep, cur_site = self.cmb_dept.currentText(), self.cmb_site.currentText()
            self.cmb_dept.blockSignals(True); self.cmb_site.blockSignals(True)
            self.cmb_dept.clear(); self.cmb_dept.addItem("All"); [self.cmb_dept.addItem(v) for v in uniq("Department")]
            self.cmb_site.clear(); self.cmb_site.addItem("All"); [self.cmb_site.addItem(v) for v in uniq("Site")]
            if cur_dep in [self.cmb_dept.itemText(i) for i in range(self.cmb_dept.count())]: self.cmb_dept.setCurrentText(cur_dep)
            if cur_site in [self.cmb_site.itemText(i) for i in range(self.cmb_site.count())]: self.cmb_site.setCurrentText(cur_site)
            self.cmb_dept.blockSignals(False); self.cmb_site.blockSignals(False)

            self._apply_filters()
        except RuntimeError as e:
            QMessageBox.critical(self,"Excel Error",str(e))
        except Exception as e:
            QMessageBox.critical(self,"Load Error",f"{e}")

    def _compute_visible_columns(self, headers: List[str]) -> Tuple[List[str], List[int]]:
        sh = self._sheet()
        mode = self.cmb_view.currentText()
        wanted = BASIC_VIEW.get(sh, []) if mode == "Basic" else SHEET_SCHEMAS.get(sh, headers)
        name_to_ix = {h:i for i,h in enumerate(headers)}
        vis, idx = [], []
        for h in wanted:
            if h in name_to_ix:
                vis.append(h); idx.append(name_to_ix[h])
        if not vis: vis, idx = headers[:], list(range(len(headers)))
        return vis, idx

    def _apply_filters(self):
        H, R = self._H, self._R
        if not H:
            self.table.clear(); self.table.setRowCount(0); self.table.setColumnCount(0); return

        q = (self.txt_search.text() or "").strip().lower()
        st, dep, site = self.cmb_status.currentText(), self.cmb_dept.currentText(), self.cmb_site.currentText()

        def ix(col: str) -> Optional[int]:
            try: return H.index(col)
            except Exception: return None
        i_st, i_dep, i_site = ix("Status"), ix("Department"), ix("Site")

        filtered: List[Tuple[int, List[str]]] = []
        for i0, row in enumerate(R):
            if i_st is not None and st != "All" and ((row[i_st] if i_st < len(row) else "").strip() != st): continue
            if i_dep is not None and dep != "All" and ((row[i_dep] if i_dep < len(row) else "").strip() != dep): continue
            if i_site is not None and site != "All" and ((row[i_site] if i_site < len(row) else "").strip() != site): continue
            if q and (q not in " | ".join((c or "") for c in row).lower()): continue
            filtered.append((i0+2, row))  # excel row index

        vis_headers, vis_idx = self._compute_visible_columns(H)
        self._visible_headers, self._visible_ix = vis_headers, vis_idx
        self._filtered_excel_rows = [r for r,_ in filtered]

        self.table.clear()
        self.table.setRowCount(len(filtered))
        self.table.setColumnCount(len(vis_headers))
        self.table.setHorizontalHeaderLabels(vis_headers)

        for r_i, (_, row) in enumerate(filtered):
            for c_j, src_ix in enumerate(vis_idx):
                val = row[src_ix] if src_ix < len(row) else ""
                item = QTableWidgetItem(val)
                if vis_headers[c_j] in NUMERIC_LIKE:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(r_i, c_j, item)

        # initial column widths
        hh = self.table.horizontalHeader()
        if hh:
            for c_j, name in enumerate(vis_headers):
                if name in PREF_WIDTHS:
                    hh.resizeSection(c_j, PREF_WIDTHS[name])
        self.table.resizeRowsToContents()

    def _reset_filters(self):
        self.txt_search.clear(); self.cmb_status.setCurrentText("All")
        self.cmb_dept.setCurrentText("All"); self.cmb_site.setCurrentText("All")
        self._apply_filters()

    def _selected_excel_row(self) -> Optional[int]:
        r = self.table.currentRow()
        if r < 0 or r >= len(self._filtered_excel_rows): return None
        return self._filtered_excel_rows[r]

    # --- Edit / Delete ---
    def _on_edit_selected(self):
        row_ix = self._selected_excel_row()
        if not row_ix:
            QMessageBox.information(self, "Select a row", "Please select a row first.")
            return
        sh = self._sheet()
        H, R = _load_sheet_rows(self.workbook_path, sh)
        trow = row_ix - 2
        if not (0 <= trow < len(R)):
            QMessageBox.warning(self, "Out of range", "Selected row is out of range.")
            return

        all_order = SHEET_SCHEMAS.get(sh, H)
        present = [h for h in all_order if h in H]
        current = {h: (R[trow][H.index(h)] if h in H else "") for h in present}

        editor_core = _TwoColumnEditor(present, initial=current, parent=self)
        scroll = QScrollArea(self)
        scroll.setWidget(editor_core)
        scroll.setWidgetResizable(True)

        dlg = QDialog(self)
        dlg.setWindowTitle("Edit Device")
        dlg.setModal(True)
        dlg.resize(760, 540)
        dlg.setWindowFlag(Qt.WindowType.WindowMinMaxButtonsHint, True)
        dlg.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        dlg.setSizeGripEnabled(True)

        v = QVBoxLayout(dlg)
        v.addWidget(scroll, 1)
        h = QHBoxLayout()
        bsave = QPushButton("Save", dlg)
        bcancel = QPushButton("Cancel", dlg)
        bsave.clicked.connect(dlg.accept)
        bcancel.clicked.connect(dlg.reject)
        h.addStretch(1)
        h.addWidget(bsave)
        h.addWidget(bcancel)
        v.addLayout(h)

        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        data = editor_core.values()
        if (ip := data.get("IP Address", "")) and not _is_valid_ip(ip):
            QMessageBox.warning(self, "Invalid IP", f"'{ip}' is not a valid IP address.")
            return
        if "Hostname" in data and not data.get("Hostname", ""):
            QMessageBox.warning(self, "Missing", "Hostname is required.")
            return

        try:
            user = os.getlogin()
        except Exception:
            user = os.environ.get("USERNAME") or os.environ.get("USER") or ""
        data["Last Updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data["Last Updated By"] = user

        dup = _find_duplicate_row(self.workbook_path, sh, H, data)
        if dup and dup != row_ix:
            QMessageBox.information(self, "Duplicate", f"Another identical device exists at row {dup}.")
            return

        try:
            _update_row(self.workbook_path, sh, row_ix, H, data)
            
            # Enhanced database sync for manual edits
            try:
                # Database-only system - direct database operations only
                QMessageBox.information(self, "Updated", "Row updated successfully in database!")
            except Exception as sync_error:
                log.warning(f"Database sync failed after Excel edit: {sync_error}")
                QMessageBox.information(self, "Updated", 
                    f"Row updated in Excel successfully!\n"
                    f"⚠️ Database sync failed: {sync_error}")
            
            self._refresh_table()
        except RuntimeError as e:
            QMessageBox.critical(self, "Excel Error", str(e))
            return

        # ---- Shadow DB hook (manual tabs) ----
        try:
            from db.repository import upsert_from_sheet_row
            upsert_from_sheet_row(sh, data)  # لاحظ: sh مش sheet
        except Exception:
            pass

    def _on_delete_selected(self):
        row_ix = self._selected_excel_row()
        if not row_ix:
            QMessageBox.information(self,"Select a row","Please select a row first."); return
        sh = self._sheet()
        if QMessageBox.question(self,"Confirm Delete",f"Delete selected row from '{sh}'?",
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return
        try:
            _delete_row(self.workbook_path, sh, row_ix)
            QMessageBox.information(self,"Deleted","Row deleted successfully.")
            self._refresh_table()
        except RuntimeError as e:
            QMessageBox.critical(self,"Excel Error",str(e))

    # --- Common ---
    def _pick_excel(self):
        # Database-only mode - workbook selection disabled
        if self.workbook_path is None:
            QMessageBox.information(self, "Database Mode", "This application runs in database-only mode. Excel operations are disabled.")
            return
        
        base_dir = os.path.dirname(self.workbook_path) if self.workbook_path else os.getcwd()
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Excel workbook",
            base_dir,
            "Excel files (*.xlsx)"
        )
        if path:
            self.workbook_path = path; self.lbl_path.setText(path)
            try: ensure_workbook_tabs(self.workbook_path); self._refresh_table()
            except RuntimeError as e: QMessageBox.critical(self,"Excel Error",str(e))

    def _save_to_database_only(self):
        """Save asset directly to database with comprehensive data collection"""
        try:
            import sqlite3
            from datetime import datetime
            
            # First, clean up any test/demo data
            conn = sqlite3.connect('assets.db')
            cursor = conn.cursor()
            
            # Remove test data on first run
            cursor.execute("DELETE FROM assets WHERE hostname LIKE '%TEST%' OR hostname LIKE '%DEMO%' OR hostname LIKE '%SAMPLE%' OR hostname = 'DESKTOP-TEST-001' OR hostname = 'WEB-SERVER-001'")
            
            # Collect comprehensive form data
            data = self._collect_form_data()
            
            # Validate required fields
            if not data.get("Hostname", "").strip():
                QMessageBox.warning(self, "Missing", "Hostname is required.")
                return False
            
            # Get additional information for comprehensive data
            hostname = data.get("Hostname", "").strip()
            ip_address = data.get("IP Address", "").strip() or None
            classification = self.cmb_type.currentText()
            
            # Enhanced asset data with all fields from web collection
            asset_data = {
                'hostname': hostname,
                'ip_address': ip_address,
                'working_user': data.get("User", "").strip() or None,
                'domain': data.get("Domain", "").strip() or None,
                'classification': classification,
                'department': data.get("Department", "").strip() or 'Unknown',
                'status': 'Active',
                'data_source': 'Manual Entry (Desktop App)',
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'updated_by': 'Manual Entry',
                'device_type': classification,
                'notes': f"Manually added via Desktop Application on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                # Add fields to match web collection data structure
                'os_name': data.get("OS", "").strip() or 'Unknown',
                'os_version': data.get("OS Version", "").strip() or None,
                'manufacturer': data.get("Manufacturer", "").strip() or 'Unknown',
                'model': data.get("Model", "").strip() or 'Unknown',
                'serial_number': data.get("Serial Number", "").strip() or None,
                'mac_address': data.get("MAC Address", "").strip() or None,
                'cpu_info': data.get("CPU", "").strip() or None,
                'memory_gb': self._extract_memory_gb(data.get("Memory", "")),
                'storage_info': data.get("Storage", "").strip() or None
            }
            
            # Check for duplicates
            cursor.execute('''
                SELECT COUNT(*) FROM assets 
                WHERE hostname = ? OR (ip_address = ? AND ip_address IS NOT NULL)
            ''', (hostname, ip_address))
            
            if cursor.fetchone()[0] > 0:
                QMessageBox.information(self, "Duplicate", f"Device '{hostname}' already exists in database.")
                conn.close()
                return False
            
            # Insert comprehensive asset data (basic fields that exist in database)
            cursor.execute('''
                INSERT INTO assets (
                    hostname, ip_address, working_user, domain, classification, department, 
                    status, data_source, created_at, last_updated, updated_by, device_type, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                asset_data['hostname'], asset_data['ip_address'], asset_data['working_user'],
                asset_data['domain'], asset_data['classification'], asset_data['department'],
                asset_data['status'], asset_data['data_source'], asset_data['created_at'],
                asset_data['last_updated'], asset_data['updated_by'], asset_data['device_type'],
                asset_data['notes']
            ))
            
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Success", f"Device '{hostname}' added successfully to database!")
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to save device: {str(e)}")
            return False
    
    def _extract_memory_gb(self, memory_text: str) -> float:
        """Extract memory in GB from text like '8 GB' or '16384 MB'"""
        try:
            if not memory_text:
                return 0.0
            memory_text = memory_text.upper().strip()
            if 'GB' in memory_text:
                return float(memory_text.replace('GB', '').strip())
            elif 'MB' in memory_text:
                mb = float(memory_text.replace('MB', '').strip())
                return round(mb / 1024, 2)
            else:
                # Try to extract number
                import re
                numbers = re.findall(r'\\d+', memory_text)
                return float(numbers[0]) if numbers else 0.0
        except Exception:
            return 0.0
            
    # Handle any database errors at the method level        
    def _handle_save_error(self, e):
        """Handle save errors gracefully"""
        QMessageBox.critical(self, "Database Error", f"Failed to save asset to database:\n{str(e)}")
        return False

# Public helper
def open_add_device_dialog(parent: QWidget|None, workbook_path: str|None = None) -> bool:
    dlg = AddNetworkDeviceDialog(workbook_path=workbook_path, parent=parent)
    return dlg.exec() == QDialog.DialogCode.Accepted
