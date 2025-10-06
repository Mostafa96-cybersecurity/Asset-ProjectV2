#!/usr/bin/env python3
"""
🚀 ENHANCED ULTIMATE PERFORMANCE COLLECTOR WITH SMART CLASSIFICATION
====================================================================

This enhanced version combines:
✅ Ultimate Performance (31.9+ devices/second validation)
✅ Smart Classification Strategy (proper device types detection)  
✅ Your proven accuracy standards (100% validation accuracy)
✅ Modern 2025 implementation techniques

Key Enhancements:
- Enhanced device classification with smart scoring
- Multi-method OS detection with confidence scoring
- Proper device type mapping (10 categories)
- Advanced port signature analysis
- Hostname pattern recognition
- Service fingerprinting for device identification
"""

import asyncio
import socket
import time
import logging
import subprocess
import platform
import concurrent.futures
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Any

# Enhanced imports
try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False

try:
    import paramiko
    PARAMIKO_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False

try:
    import nmap
    NMAP_AVAILABLE = True
except ImportError:
    NMAP_AVAILABLE = False

# Import our ultimate performance validator
try:
    from ultimate_performance_validator import UltimatePerformanceValidator, DeviceStatus, ValidationResult
except ImportError:
    print("⚠️  Warning: UltimatePerformanceValidator not found. Using basic validation.")
    UltimatePerformanceValidator = None

@dataclass
class EnhancedDeviceInfo:
    """Enhanced device information with comprehensive hardware collection"""
    # Basic Identification
    ip: str
    hostname: str = ""
    computer_name: str = ""
    device_hostname: str = ""
    domain_hostname: str = ""
    dns_hostname: str = ""
    mac_address: str = ""
    
    # Hostname Tracking
    hostname_mismatch_status: str = ""  # 'Match', 'Mismatch', 'No_Domain_Record', 'DNS_Error'
    hostname_mismatch_details: str = ""
    domain_name: str = ""
    workgroup: str = ""
    
    # Hardware Specifications
    system_manufacturer: str = ""
    system_model: str = ""
    system_family: str = ""
    system_sku: str = ""
    serial_number: str = ""
    asset_tag: str = ""
    uuid: str = ""
    
    # Processor Information
    processor_name: str = ""
    processor_manufacturer: str = ""
    processor_architecture: str = ""
    processor_cores: int = 0
    processor_logical_cores: int = 0
    processor_speed_mhz: int = 0
    processor_max_speed_mhz: int = 0
    processor_l2_cache_size: str = ""
    processor_l3_cache_size: str = ""
    
    # Memory Information (Enhanced)
    total_physical_memory_gb: float = 0.0
    available_memory_gb: float = 0.0
    memory_slots_used: int = 0
    memory_slots_total: int = 0
    memory_modules: List[Dict] = None  # JSON array of memory modules
    
    # Storage Information (Enhanced)
    storage_devices: List[Dict] = None  # JSON array of all storage devices
    total_storage_gb: float = 0.0
    available_storage_gb: float = 0.0
    storage_summary: str = ""  # "Disk 1: 250GB SSD, Disk 2: 500GB HDD"
    
    # Graphics Information (Enhanced)
    graphics_cards: List[Dict] = None  # Enhanced JSON array with full specs
    primary_graphics_card: str = ""
    graphics_memory_mb: int = 0
    graphics_driver_version: str = ""
    
    # Display Information (NEW)
    connected_monitors: int = 0
    monitor_details: List[Dict] = None  # JSON array of monitor information
    screen_resolution: str = ""
    display_adapters: List[Dict] = None  # JSON array of display adapters
    
    # Network Information (Enhanced)
    network_adapters: List[Dict] = None  # JSON array of network adapters
    wireless_adapters: List[Dict] = None  # JSON array of wireless adapters
    network_configuration: Dict = None  # JSON of IP config
    
    # Operating System (Enhanced)
    os_family: str = ""
    operating_system: str = ""
    os_version: str = ""
    os_build: str = ""
    os_edition: str = ""
    os_architecture: str = ""
    os_install_date: str = ""
    last_boot_time: str = ""
    
    # BIOS/UEFI Information (NEW)
    bios_manufacturer: str = ""
    bios_version: str = ""
    bios_release_date: str = ""
    firmware_type: str = ""  # BIOS or UEFI
    
    # Software Information (NEW)
    installed_software: List[Dict] = None  # JSON array of installed programs
    installed_updates: List[Dict] = None  # JSON array of Windows updates
    antivirus_software: str = ""
    browsers_installed: List[str] = None  # JSON array of browsers
    
    # User Information (ENHANCED)
    current_user: str = ""
    current_logged_user: str = ""  # Currently logged in user
    interactive_user: str = ""  # User at console
    registered_owner: str = ""
    last_logged_users: List[str] = None  # JSON array of recent users
    user_profiles: List[Dict] = None  # JSON array of user profiles with privileges
    user_groups: List[Dict] = None  # JSON array of user groups
    local_users: List[Dict] = None  # JSON array of all local users
    domain_users: List[Dict] = None  # JSON array of domain users
    admin_users: List[str] = None  # List of users with admin privileges
    login_sessions: List[Dict] = None  # JSON array of current login sessions
    
    # System Performance (NEW)
    cpu_usage_percent: float = 0.0
    memory_usage_percent: float = 0.0
    disk_usage_percent: float = 0.0
    system_uptime_hours: float = 0.0
    
    # Security Information (NEW)
    windows_defender_status: str = ""
    firewall_status: str = ""
    encryption_status: str = ""
    uac_status: str = ""
    
    # Asset Management (NEW)
    department: str = ""
    location: str = ""
    site: str = ""
    cost_center: str = ""
    purchase_date: str = ""
    warranty_expiry: str = ""
    
    # Original Classification Fields
    device_type: str = "Unknown Device"
    device_subtype: str = ""
    manufacturer: str = ""
    model: str = ""
    processor: str = ""  # Kept for backward compatibility
    memory_gb: float = 0.0  # Kept for backward compatibility
    disk_info: str = ""  # Kept for backward compatibility
    open_ports: List[int] = None
    services: List[str] = None
    collection_method: str = ""
    collection_time: float = 0.0
    confidence: float = 0.0
    last_seen: float = 0.0
    classification_details: Dict[str, Any] = None
    
    # Collection Metadata (NEW)
    collection_timestamp: str = ""
    collection_duration_seconds: float = 0.0
    collection_id: str = ""
    data_completeness_score: int = 0  # 0-100 based on fields collected
    
    # Change Tracking (NEW)
    last_hardware_change: str = ""
    last_software_change: str = ""
    configuration_hash: str = ""
    change_history: List[Dict] = None  # JSON array of changes
    
    # Device Status (NEW)
    device_status: str = ""  # 'Online', 'Offline', 'Unknown'
    ping_response_ms: int = 0
    
    def __post_init__(self):
        """Initialize all list and dict fields to prevent None values"""
        if self.memory_modules is None:
            self.memory_modules = []
        if self.storage_devices is None:
            self.storage_devices = []
        if self.graphics_cards is None:
            self.graphics_cards = []
        if self.monitor_details is None:
            self.monitor_details = []
        if self.display_adapters is None:
            self.display_adapters = []
        if self.network_adapters is None:
            self.network_adapters = []
        if self.wireless_adapters is None:
            self.wireless_adapters = []
        if self.network_configuration is None:
            self.network_configuration = {}
        if self.installed_software is None:
            self.installed_software = []
        if self.installed_updates is None:
            self.installed_updates = []
        if self.browsers_installed is None:
            self.browsers_installed = []
        if self.last_logged_users is None:
            self.last_logged_users = []
        if self.user_profiles is None:
            self.user_profiles = []
        if self.user_groups is None:
            self.user_groups = []
        if self.local_users is None:
            self.local_users = []
        if self.domain_users is None:
            self.domain_users = []
        if self.admin_users is None:
            self.admin_users = []
        if self.login_sessions is None:
            self.login_sessions = []
        if self.change_history is None:
            self.change_history = []
        if self.open_ports is None:
            self.open_ports = []
        if self.services is None:
            self.services = []
        if self.classification_details is None:
            self.classification_details = {}

class EnhancedUltimatePerformanceCollector:
    """
    🚀 Enhanced Ultimate Performance Collector with Smart Classification
    
    Combines maximum performance with intelligent device classification
    based on your proven strategies and modern 2025 techniques.
    """
    
    # Enhanced Device Classification Map (10 proper types)
    DEVICE_TYPES = {
        'WINDOWS_WORKSTATION': 'Windows Workstation',
        'WINDOWS_SERVER': 'Windows Server',
        'LINUX_WORKSTATION': 'Linux Workstation', 
        'LINUX_SERVER': 'Linux Server',
        'MAC_WORKSTATION': 'Mac Workstation',
        'NETWORK_SWITCH': 'Network Switch',
        'NETWORK_ROUTER': 'Network Router',
        'NETWORK_FIREWALL': 'Network Firewall',
        'PRINTER': 'Printer',
        'UNKNOWN': 'Unknown Device'
    }
    
    # Enhanced Port Signatures for Smart Classification
    PORT_SIGNATURES = {
        # Windows signatures
        'windows_workstation': [135, 139, 445],
        'windows_server': [135, 445, 3389, 53, 88, 389],
        'windows_rdp': [3389],
        'windows_winrm': [5985, 5986],
        
        # Linux/Unix signatures  
        'linux_ssh': [22],
        'linux_web': [80, 443],
        'linux_mail': [25, 110, 143, 993, 995],
        'linux_dns': [53],
        'linux_ftp': [21],
        
        # Network equipment signatures
        'network_snmp': [161, 162],
        'network_web_mgmt': [80, 443, 8080, 8443],
        'network_ssh': [22],
        'network_telnet': [23],
        
        # Service signatures
        'printer_ports': [515, 631, 9100],
        'database_ports': [1433, 1521, 3306, 5432],
        'web_ports': [80, 443, 8080, 8443],
        'mail_ports': [25, 110, 143, 993, 995],
    }
    
    # Enhanced Hostname Patterns
    HOSTNAME_PATTERNS = {
        'server_patterns': ['srv', 'server', 'dc-', 'ad-', 'sql', 'web', 'mail', 'dns', 'dhcp', 'file'],
        'workstation_patterns': ['pc-', 'ws-', 'desktop', 'workstation', 'user'],
        'laptop_patterns': ['laptop', 'mobile', 'book', 'portable', 'lt-', 'nb-'],
        'switch_patterns': ['sw-', 'switch', 'core', 'access', 'dist'],
        'router_patterns': ['rtr', 'router', 'gw', 'gateway'],
        'firewall_patterns': ['fw', 'firewall', 'asa', 'palo', 'fortinet'],
        'printer_patterns': ['printer', 'hp-', 'canon', 'epson', 'lexmark', 'print']
    }
    
    def __init__(self, credentials: Dict = None, config: Dict = None):
        """Initialize Enhanced Ultimate Performance Collector"""
        
        # Configuration
        self.config = {
            'max_workers': 200,
            'max_collection_concurrent': 50,  # Reduced for stability
            'collection_timeout': 7200,  # 2 hours - unlimited collection for large networks
            'enable_wmi_collection': True,
            'enable_ssh_collection': False,  # Disable SSH to avoid errors
            'enable_nmap_scanning': True,
            'enable_enhanced_classification': True,
            'classification_confidence_threshold': 0.5,  # Lower threshold for better classification
            **(config or {})
        }
        
        # Credentials
        self.credentials = credentials or {}
        
        # Performance settings
        self.max_workers = self.config['max_workers']
        self.max_collection_concurrent = self.config['max_collection_concurrent']
        
        # Initialize validator with ultimate performance
        if UltimatePerformanceValidator:
            self.validator = UltimatePerformanceValidator(
                max_workers=self.max_workers
            )
        else:
            self.validator = None
        
        # Metrics tracking
        self.metrics = type('Metrics', (), {
            'total_ips': 0,
            'validated_alive': 0,
            'collection_attempted': 0,
            'collection_successful': 0,
            'collection_failed': 0,
            'classification_successful': 0,
            'classification_failed': 0,
            'start_time': 0,
            'validation_time': 0,
            'collection_time': 0
        })()
        
        # Threading
        self.collection_executor = None
        
        # Logging
        self.logger = self._setup_logging()
        
        self.logger.info("🚀 Enhanced Ultimate Performance Collector initialized")
        self.logger.info(f"   ⚡ Max workers: {self.max_workers}")
        self.logger.info(f"   🔧 WMI available: {WMI_AVAILABLE}")
        self.logger.info(f"   🔑 SSH available: {PARAMIKO_AVAILABLE}")
        self.logger.info(f"   🗺️  NMAP available: {NMAP_AVAILABLE}")
        self.logger.info(f"   🧠 Enhanced Classification: {self.config['enable_enhanced_classification']}")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup enhanced logging"""
        logger = logging.getLogger('EnhancedUltimatePerformanceCollector')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def setup_enhanced_database(self, db_path: str = "assets.db"):
        """Create enhanced database schema with comprehensive tracking columns"""
        import sqlite3
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create enhanced assets table with comprehensive columns
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assets_enhanced (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                
                -- Basic Identification
                hostname TEXT,
                computer_name TEXT,
                device_hostname TEXT,
                domain_hostname TEXT,
                dns_hostname TEXT,
                ip_address TEXT,
                mac_address TEXT,
                
                -- Hostname Tracking
                hostname_mismatch_status TEXT, -- 'Match', 'Mismatch', 'No_Domain_Record', 'DNS_Error'
                hostname_mismatch_details TEXT,
                domain_name TEXT,
                workgroup TEXT,
                
                -- Hardware Specifications
                system_manufacturer TEXT,
                system_model TEXT,
                system_family TEXT,
                system_sku TEXT,
                serial_number TEXT,
                asset_tag TEXT,
                uuid TEXT,
                
                -- Processor Information
                processor_name TEXT,
                processor_manufacturer TEXT,
                processor_architecture TEXT,
                processor_cores INTEGER,
                processor_logical_cores INTEGER,
                processor_speed_mhz INTEGER,
                processor_max_speed_mhz INTEGER,
                processor_l2_cache_size TEXT,
                processor_l3_cache_size TEXT,
                
                -- Memory Information
                total_physical_memory_gb REAL,
                available_memory_gb REAL,
                memory_slots_used INTEGER,
                memory_slots_total INTEGER,
                memory_modules TEXT, -- JSON array of memory modules
                
                -- Storage Information
                storage_devices TEXT, -- JSON array of all storage devices
                total_storage_gb REAL,
                available_storage_gb REAL,
                storage_summary TEXT, -- "Disk 1: 250GB SSD, Disk 2: 500GB HDD"
                
                -- Graphics Information
                graphics_cards TEXT, -- JSON array of all graphics cards
                primary_graphics_card TEXT,
                graphics_memory_mb INTEGER,
                graphics_driver_version TEXT,
                
                -- Display Information
                connected_monitors INTEGER,
                monitor_details TEXT, -- JSON array of monitor information
                screen_resolution TEXT,
                display_adapters TEXT, -- JSON array of display adapters
                
                -- Network Information
                network_adapters TEXT, -- JSON array of network adapters
                wireless_adapters TEXT, -- JSON array of wireless adapters
                network_configuration TEXT, -- JSON of IP config
                
                -- Operating System
                operating_system TEXT,
                os_version TEXT,
                os_build TEXT,
                os_edition TEXT,
                os_architecture TEXT,
                os_install_date TEXT,
                last_boot_time TEXT,
                
                -- BIOS/UEFI Information
                bios_manufacturer TEXT,
                bios_version TEXT,
                bios_release_date TEXT,
                firmware_type TEXT, -- BIOS or UEFI
                
                -- Software Information
                installed_software TEXT, -- JSON array of installed programs
                installed_updates TEXT, -- JSON array of Windows updates
                antivirus_software TEXT,
                browsers_installed TEXT, -- JSON array of browsers
                
                -- User Information (Enhanced)
                current_user TEXT,
                current_logged_user TEXT,
                interactive_user TEXT,
                registered_owner TEXT,
                last_logged_users TEXT, -- JSON array of recent users
                user_profiles TEXT, -- JSON array of user profiles with privileges
                user_groups TEXT, -- JSON array of user groups
                local_users TEXT, -- JSON array of all local users
                domain_users TEXT, -- JSON array of domain users
                admin_users TEXT, -- JSON array of admin users
                login_sessions TEXT, -- JSON array of current login sessions
                
                -- System Performance
                cpu_usage_percent REAL,
                memory_usage_percent REAL,
                disk_usage_percent REAL,
                system_uptime_hours REAL,
                
                -- Security Information
                windows_defender_status TEXT,
                firewall_status TEXT,
                encryption_status TEXT,
                uac_status TEXT,
                
                -- Asset Management
                department TEXT,
                location TEXT,
                site TEXT,
                cost_center TEXT,
                purchase_date TEXT,
                warranty_expiry TEXT,
                
                -- Original fields for backward compatibility
                os_family TEXT,
                device_type TEXT,
                manufacturer TEXT,
                model TEXT,
                processor TEXT,
                memory_gb REAL,
                disk_info TEXT,
                
                -- Collection Metadata
                collection_method TEXT,
                collection_timestamp TEXT,
                collection_duration_seconds REAL,
                collection_id TEXT,
                data_completeness_score INTEGER, -- 0-100 based on fields collected
                
                -- Change Tracking
                last_hardware_change TEXT,
                last_software_change TEXT,
                configuration_hash TEXT,
                change_history TEXT, -- JSON array of changes
                
                -- Device Status
                device_status TEXT, -- 'Online', 'Offline', 'Unknown'
                last_seen TEXT,
                ping_response_ms INTEGER,
                
                -- Timestamps
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create index on IP address for faster lookups
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ip_address ON assets_enhanced(ip_address)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_hostname ON assets_enhanced(hostname)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_device_status ON assets_enhanced(device_status)')
        
        conn.commit()
        conn.close()
        
        self.logger.info("✅ Enhanced database schema created successfully")
    
    def save_device_to_enhanced_db(self, device: EnhancedDeviceInfo, db_path: str = "assets.db"):
        """Save comprehensive device data to enhanced database"""
        import sqlite3
        import json
        import hashlib
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Convert lists and dicts to JSON strings
            memory_modules_json = json.dumps(device.memory_modules) if device.memory_modules else "[]"
            storage_devices_json = json.dumps(device.storage_devices) if device.storage_devices else "[]"
            graphics_cards_json = json.dumps(device.graphics_cards) if device.graphics_cards else "[]"
            monitor_details_json = json.dumps(device.monitor_details) if device.monitor_details else "[]"
            display_adapters_json = json.dumps(device.display_adapters) if device.display_adapters else "[]"
            network_adapters_json = json.dumps(device.network_adapters) if device.network_adapters else "[]"
            wireless_adapters_json = json.dumps(device.wireless_adapters) if device.wireless_adapters else "[]"
            network_configuration_json = json.dumps(device.network_configuration) if device.network_configuration else "{}"
            installed_software_json = json.dumps(device.installed_software) if device.installed_software else "[]"
            installed_updates_json = json.dumps(device.installed_updates) if device.installed_updates else "[]"
            browsers_installed_json = json.dumps(device.browsers_installed) if device.browsers_installed else "[]"
            last_logged_users_json = json.dumps(device.last_logged_users) if device.last_logged_users else "[]"
            user_profiles_json = json.dumps(device.user_profiles) if device.user_profiles else "[]"
            change_history_json = json.dumps(device.change_history) if device.change_history else "[]"
            
            # Create configuration hash for change tracking
            config_data = f"{device.processor_name}{device.total_physical_memory_gb}{device.total_storage_gb}{device.operating_system}"
            configuration_hash = hashlib.md5(config_data.encode()).hexdigest()
            
            # Check if device exists
            cursor.execute('SELECT id, configuration_hash FROM assets_enhanced WHERE ip_address = ?', (device.ip,))
            existing = cursor.fetchone()
            
            current_time = time.strftime('%Y-%m-%d %H:%M:%S')
            
            if existing:
                # Update existing device - simplified update for key fields only
                cursor.execute('''
                    UPDATE assets_enhanced SET
                        hostname = ?, computer_name = ?, system_manufacturer = ?, system_model = ?,
                        processor_name = ?, total_physical_memory_gb = ?, storage_summary = ?,
                        operating_system = ?, os_family = ?, device_type = ?,
                        collection_method = ?, collection_timestamp = ?, data_completeness_score = ?,
                        device_status = ?, last_seen = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE ip_address = ?
                ''', (
                    device.hostname, device.computer_name, device.system_manufacturer, device.system_model,
                    device.processor_name, device.total_physical_memory_gb, device.storage_summary,
                    device.operating_system, device.os_family, device.device_type,
                    device.collection_method, device.collection_timestamp, device.data_completeness_score,
                    device.device_status, current_time, device.ip
                ))
                
                self.logger.info(f"✅ Updated device {device.ip} in enhanced database")
            else:
                # Insert new device - simplified insert for key fields
                cursor.execute('''
                    INSERT INTO assets_enhanced (
                        hostname, computer_name, ip_address, mac_address,
                        system_manufacturer, system_model, processor_name,
                        total_physical_memory_gb, storage_summary, graphics_cards,
                        operating_system, os_family, device_type,
                        collection_method, collection_timestamp, collection_duration_seconds,
                        data_completeness_score, device_status, last_seen
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    device.hostname, device.computer_name, device.ip, device.mac_address,
                    device.system_manufacturer, device.system_model, device.processor_name,
                    device.total_physical_memory_gb, device.storage_summary, graphics_cards_json,
                    device.operating_system, device.os_family, device.device_type,
                    device.collection_method, device.collection_timestamp, device.collection_duration_seconds,
                    device.data_completeness_score, device.device_status, current_time
                ))
                
                self.logger.info(f"✅ Inserted new device {device.ip} into enhanced database")
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"❌ Failed to save device {device.ip} to enhanced database: {e}")
            if 'conn' in locals():
                conn.close()
    
    def _get_hostname(self, ip: str) -> str:
        """Enhanced hostname resolution"""
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            return hostname.lower()  # Normalize for pattern matching
        except (socket.herror, socket.gaierror):
            return ""
    
    def _get_mac_address(self, ip: str) -> str:
        """Enhanced MAC address discovery"""
        try:
            if platform.system().lower() == 'windows':
                result = subprocess.run(['arp', '-a', ip], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if ip in line and 'dynamic' in line.lower():
                            parts = line.split()
                            for part in parts:
                                if '-' in part and len(part) == 17:  # MAC format xx-xx-xx-xx-xx-xx
                                    return part.replace('-', ':')
            else:
                result = subprocess.run(['arp', '-n', ip], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if ip in line:
                            parts = line.split()
                            if len(parts) >= 3:
                                mac = parts[2]
                                if ':' in mac and len(mac) == 17:
                                    return mac
        except Exception:
            pass
        return ""
    
    def _enhanced_nmap_scan(self, ip: str) -> Tuple[List[int], List[str], str, str, Dict]:
        """Enhanced NMAP scanning with detailed analysis"""
        if not NMAP_AVAILABLE:
            return [], [], "", "", {}
        
        try:
            nm = nmap.PortScanner()
            
            # Comprehensive scan with OS detection and service enumeration
            scan_args = '-sS -O --osscan-guess -sV --version-intensity 5'
            port_range = '22,23,25,53,80,110,135,139,143,443,445,515,631,993,995,1433,1521,3306,3389,5432,5985,5986,8080,8443,9100'
            
            result = nm.scan(ip, port_range, arguments=scan_args)
            
            if ip in result['scan']:
                host_info = result['scan'][ip]
                
                # Extract open ports and services
                open_ports = []
                services = []
                service_details = {}
                
                if 'tcp' in host_info:
                    for port, port_info in host_info['tcp'].items():
                        if port_info['state'] == 'open':
                            open_ports.append(port)
                            
                            service_name = port_info.get('name', f'port_{port}')
                            service_product = port_info.get('product', '')
                            service_version = port_info.get('version', '')
                            
                            if service_name != f'port_{port}':
                                service_desc = f"{service_name}({port})"
                                if service_product:
                                    service_desc += f" - {service_product}"
                                    if service_version:
                                        service_desc += f" {service_version}"
                                services.append(service_desc)
                                
                                service_details[port] = {
                                    'name': service_name,
                                    'product': service_product,
                                    'version': service_version
                                }
                
                # Enhanced OS detection
                os_family = ""
                os_version = ""
                os_details = {}
                
                if 'osmatch' in host_info and host_info['osmatch']:
                    best_match = host_info['osmatch'][0]
                    os_name = best_match.get('name', '')
                    os_accuracy = best_match.get('accuracy', 0)
                    
                    os_details['accuracy'] = os_accuracy
                    os_details['full_name'] = os_name
                    
                    # Smart OS family detection
                    os_name_lower = os_name.lower()
                    if any(keyword in os_name_lower for keyword in ['windows', 'microsoft']):
                        os_family = 'Windows'
                    elif any(keyword in os_name_lower for keyword in ['linux', 'ubuntu', 'centos', 'redhat', 'debian']):
                        os_family = 'Linux'
                    elif any(keyword in os_name_lower for keyword in ['mac', 'darwin', 'osx']):
                        os_family = 'macOS'
                    elif any(keyword in os_name_lower for keyword in ['cisco', 'juniper', 'hp']):
                        os_family = 'Network OS'
                    else:
                        os_family = 'Unknown'
                    
                    os_version = os_name
                
                return open_ports, services, os_family, os_version, {
                    'service_details': service_details,
                    'os_details': os_details
                }
        
        except Exception as e:
            self.logger.debug(f"Enhanced NMAP scan failed for {ip}: {e}")
        
        return [], [], "", "", {}
    
    def _enhanced_classify_device(self, device: EnhancedDeviceInfo) -> str:
        """
        🧠 Enhanced Smart Device Classification
        
        Uses multiple classification strategies:
        1. Port signature analysis
        2. Hostname pattern recognition  
        3. OS family identification
        4. Service fingerprinting
        5. Confidence scoring
        """
        
        if not self.config['enable_enhanced_classification']:
            return self._basic_classify_device(device)
        
        # Classification scores for each device type
        scores = {}
        classification_details = {}
        
        # Initialize scores
        for device_type in self.DEVICE_TYPES.keys():
            scores[device_type] = 0.0
        
        # 1. Port Signature Analysis (40% weight)
        port_scores = self._analyze_port_signatures(device)
        for device_type, score in port_scores.items():
            scores[device_type] += score * 0.4
            classification_details[f'{device_type}_port_score'] = score
        
        # 2. Hostname Pattern Recognition (25% weight)
        hostname_scores = self._analyze_hostname_patterns(device)
        for device_type, score in hostname_scores.items():
            scores[device_type] += score * 0.25
            classification_details[f'{device_type}_hostname_score'] = score
        
        # 3. OS Family Identification (20% weight)
        os_scores = self._analyze_os_family(device)
        for device_type, score in os_scores.items():
            scores[device_type] += score * 0.20
            classification_details[f'{device_type}_os_score'] = score
        
        # 4. Service Fingerprinting (15% weight)
        service_scores = self._analyze_services(device)
        for device_type, score in service_scores.items():
            scores[device_type] += score * 0.15
            classification_details[f'{device_type}_service_score'] = score
        
        # Store classification details
        device.classification_details = classification_details
        
        # Find best classification
        if scores:
            best_type, best_score = max(scores.items(), key=lambda x: x[1])
            
            # Apply confidence threshold
            if best_score >= self.config['classification_confidence_threshold']:
                self.metrics.classification_successful += 1
                self.logger.debug(f"Enhanced classification for {device.ip}: {self.DEVICE_TYPES[best_type]} (confidence: {best_score:.2f})")
                return self.DEVICE_TYPES[best_type]
        
        # Fallback to basic classification
        self.metrics.classification_failed += 1
        return self._basic_classify_device(device)
    
    def _analyze_port_signatures(self, device: EnhancedDeviceInfo) -> Dict[str, float]:
        """Analyze port signatures for device classification"""
        scores = {}
        open_ports = set(device.open_ports)
        
        # Windows Workstation signatures
        if self.PORT_SIGNATURES['windows_workstation']:
            windows_ws_ports = set(self.PORT_SIGNATURES['windows_workstation'])
            match_ratio = len(open_ports & windows_ws_ports) / len(windows_ws_ports)
            if match_ratio > 0:
                scores['WINDOWS_WORKSTATION'] = min(match_ratio * 100, 80)
        
        # Windows Server signatures
        if self.PORT_SIGNATURES['windows_server']:
            windows_srv_ports = set(self.PORT_SIGNATURES['windows_server'])
            match_ratio = len(open_ports & windows_srv_ports) / len(windows_srv_ports)
            if match_ratio > 0:
                scores['WINDOWS_SERVER'] = min(match_ratio * 100, 90)
        
        # Linux SSH detection
        if 22 in open_ports:
            scores['LINUX_SERVER'] = 70
            scores['LINUX_WORKSTATION'] = 50
            # Boost server score if other server ports present
            server_ports = set(self.PORT_SIGNATURES['linux_web'] + self.PORT_SIGNATURES['linux_mail'])
            if open_ports & server_ports:
                scores['LINUX_SERVER'] += 20
        
        # Network equipment detection
        if 161 in open_ports or 162 in open_ports:  # SNMP
            scores['NETWORK_SWITCH'] = 85
            scores['NETWORK_ROUTER'] = 75
            
            # Web management interface boosts network score
            if any(port in open_ports for port in [80, 443, 8080]):
                scores['NETWORK_SWITCH'] += 10
                scores['NETWORK_ROUTER'] += 10
        
        # Printer detection
        printer_ports = set(self.PORT_SIGNATURES['printer_ports'])
        if open_ports & printer_ports:
            scores['PRINTER'] = 90
        
        return scores
    
    def _analyze_hostname_patterns(self, device: EnhancedDeviceInfo) -> Dict[str, float]:
        """Analyze hostname patterns for device classification"""
        scores = {}
        hostname = device.hostname.lower()
        
        if not hostname:
            return scores
        
        # Server patterns
        for pattern in self.HOSTNAME_PATTERNS['server_patterns']:
            if pattern in hostname:
                scores['WINDOWS_SERVER'] = scores.get('WINDOWS_SERVER', 0) + 15
                scores['LINUX_SERVER'] = scores.get('LINUX_SERVER', 0) + 15
        
        # Workstation patterns
        for pattern in self.HOSTNAME_PATTERNS['workstation_patterns']:
            if pattern in hostname:
                scores['WINDOWS_WORKSTATION'] = scores.get('WINDOWS_WORKSTATION', 0) + 20
                scores['LINUX_WORKSTATION'] = scores.get('LINUX_WORKSTATION', 0) + 15
        
        # Laptop patterns
        for pattern in self.HOSTNAME_PATTERNS['laptop_patterns']:
            if pattern in hostname:
                scores['WINDOWS_WORKSTATION'] = scores.get('WINDOWS_WORKSTATION', 0) + 25
                scores['MAC_WORKSTATION'] = scores.get('MAC_WORKSTATION', 0) + 20
        
        # Network equipment patterns
        for pattern in self.HOSTNAME_PATTERNS['switch_patterns']:
            if pattern in hostname:
                scores['NETWORK_SWITCH'] = scores.get('NETWORK_SWITCH', 0) + 30
        
        for pattern in self.HOSTNAME_PATTERNS['router_patterns']:
            if pattern in hostname:
                scores['NETWORK_ROUTER'] = scores.get('NETWORK_ROUTER', 0) + 30
        
        for pattern in self.HOSTNAME_PATTERNS['firewall_patterns']:
            if pattern in hostname:
                scores['NETWORK_FIREWALL'] = scores.get('NETWORK_FIREWALL', 0) + 30
        
        # Printer patterns
        for pattern in self.HOSTNAME_PATTERNS['printer_patterns']:
            if pattern in hostname:
                scores['PRINTER'] = scores.get('PRINTER', 0) + 25
        
        return scores
    
    def _analyze_os_family(self, device: EnhancedDeviceInfo) -> Dict[str, float]:
        """Analyze OS family for device classification"""
        scores = {}
        os_family = device.os_family.lower()
        
        if 'windows' in os_family:
            if 'server' in device.os_version.lower():
                scores['WINDOWS_SERVER'] = 50
            else:
                scores['WINDOWS_WORKSTATION'] = 40
        
        elif 'linux' in os_family:
            # Determine if server or workstation based on services
            if any(port in device.open_ports for port in [80, 443, 25, 53, 21]):
                scores['LINUX_SERVER'] = 45
            else:
                scores['LINUX_WORKSTATION'] = 30
        
        elif 'mac' in os_family or 'darwin' in os_family:
            scores['MAC_WORKSTATION'] = 40
        
        elif 'network' in os_family or any(vendor in os_family for vendor in ['cisco', 'juniper', 'hp']):
            scores['NETWORK_SWITCH'] = 35
            scores['NETWORK_ROUTER'] = 35
        
        return scores
    
    def _analyze_services(self, device: EnhancedDeviceInfo) -> Dict[str, float]:
        """Analyze running services for device classification"""
        scores = {}
        services = [service.lower() for service in device.services]
        
        # Web services
        if any('http' in service or 'web' in service for service in services):
            scores['LINUX_SERVER'] = scores.get('LINUX_SERVER', 0) + 15
            scores['WINDOWS_SERVER'] = scores.get('WINDOWS_SERVER', 0) + 10
        
        # Database services
        if any('sql' in service or 'mysql' in service or 'postgres' in service for service in services):
            scores['LINUX_SERVER'] = scores.get('LINUX_SERVER', 0) + 20
            scores['WINDOWS_SERVER'] = scores.get('WINDOWS_SERVER', 0) + 20
        
        # Mail services
        if any('smtp' in service or 'pop' in service or 'imap' in service for service in services):
            scores['LINUX_SERVER'] = scores.get('LINUX_SERVER', 0) + 15
            scores['WINDOWS_SERVER'] = scores.get('WINDOWS_SERVER', 0) + 15
        
        # Print services
        if any('print' in service or 'lp' in service for service in services):
            scores['PRINTER'] = scores.get('PRINTER', 0) + 20
        
        # Network management services
        if any('snmp' in service for service in services):
            scores['NETWORK_SWITCH'] = scores.get('NETWORK_SWITCH', 0) + 15
            scores['NETWORK_ROUTER'] = scores.get('NETWORK_ROUTER', 0) + 15
        
        return scores
    
    def _basic_classify_device(self, device: EnhancedDeviceInfo) -> str:
        """Basic device classification as fallback"""
        
        # Basic port-based classification
        open_ports = device.open_ports
        hostname = device.hostname.lower()
        os_family = device.os_family.lower()
        
        # Windows detection
        if any(port in open_ports for port in [135, 445]):
            if any(port in open_ports for port in [3389, 53, 88]) or 'server' in hostname:
                return "Windows Server"
            return "Windows Workstation"
        
        # Linux detection
        if 22 in open_ports:
            if any(port in open_ports for port in [80, 443, 25]) or 'server' in hostname:
                return "Linux Server"
            return "Linux Workstation"
        
        # Network equipment
        if 161 in open_ports:
            return "Network Switch"
        
        # Printer
        if any(port in open_ports for port in [515, 631, 9100]):
            return "Printer"
        
        # OS-based fallback
        if 'windows' in os_family:
            return "Windows Workstation"
        elif 'linux' in os_family:
            return "Linux Server"
        elif 'mac' in os_family:
            return "Mac Workstation"
        
        return "Unknown Device"
    
    def _collect_single_device(self, ip: str, validation_result: DeviceStatus) -> Optional[EnhancedDeviceInfo]:
        """Collect comprehensive information for a single device with enhanced classification"""
        
        self.logger.debug(f"Enhanced collection for {ip}")
        
        try:
            device = None
            
            # Try WMI collection first (most comprehensive for Windows)
            if self.config['enable_wmi_collection'] and WMI_AVAILABLE:
                device = self._wmi_collect(ip)
            
            # Try SSH collection (comprehensive for Linux/Unix)
            if not device and self.config['enable_ssh_collection'] and PARAMIKO_AVAILABLE:
                device = self._ssh_collect(ip)
            
            # Fallback to enhanced basic collection
            if not device:
                device = self._enhanced_basic_collect(ip, validation_result)
            
            if device:
                # Apply enhanced classification
                device.device_type = self._enhanced_classify_device(device)
                device.last_seen = time.time()
                
                self.metrics.collection_successful += 1
                self.logger.debug(f"Enhanced collection successful: {device.device_type} at {ip}")
                return device
            else:
                self.metrics.collection_failed += 1
                return None
        
        except Exception as e:
            self.logger.error(f"Enhanced collection failed for {ip}: {e}")
            self.metrics.collection_failed += 1
            return None
    
    def _enhanced_basic_collect(self, ip: str, validation_result: DeviceStatus) -> EnhancedDeviceInfo:
        """Enhanced basic collection with comprehensive analysis"""
        start_time = time.time()
        
        device = EnhancedDeviceInfo(ip=ip)
        device.confidence = validation_result.confidence
        
        # Get hostname and MAC with enhanced methods
        device.hostname = self._get_hostname(ip)
        device.mac_address = self._get_mac_address(ip)
        
        # Enhanced NMAP scanning
        if self.config['enable_nmap_scanning'] and NMAP_AVAILABLE:
            open_ports, services, os_family, os_version, scan_details = self._enhanced_nmap_scan(ip)
            device.open_ports = open_ports
            device.services = services
            device.os_family = os_family or "Unknown"
            device.os_version = os_version or ""
            
            # Store additional scan details
            if scan_details:
                device.classification_details.update(scan_details)
        
        device.collection_method = "Enhanced Basic"
        device.collection_time = time.time() - start_time
        
        return device
    
    def _wmi_collect(self, ip: str) -> Optional[EnhancedDeviceInfo]:
        """COMPREHENSIVE WMI collection with all hardware and software data"""
        if not WMI_AVAILABLE:
            return None
        
        try:
            # Initialize COM for thread-safe WMI operations
            import pythoncom
            pythoncom.CoInitialize()
            
            start_time = time.time()
            collection_id = f"enhanced_{int(time.time())}"
            
            # WMI connection with credentials
            username = self.credentials.get('username', '')
            password = self.credentials.get('password', '')
            domain = self.credentials.get('domain', '')
            
            if username and password:
                if domain:
                    user_string = f"{domain}\\{username}"
                else:
                    user_string = username
                c = wmi.WMI(computer=ip, user=user_string, password=password)
            else:
                c = wmi.WMI(computer=ip)
            
            device = EnhancedDeviceInfo(ip=ip)
            device.collection_timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            device.collection_id = collection_id
            device.device_status = "Online"
            
            # === BASIC IDENTIFICATION ===
            try:
                for system in c.Win32_ComputerSystem():
                    device.hostname = (system.Name or "").lower()
                    device.computer_name = system.Name or ""
                    device.device_hostname = system.Name or ""
                    device.domain_name = system.Domain or ""
                    device.workgroup = system.Workgroup or ""
                    device.system_manufacturer = system.Manufacturer or ""
                    device.system_model = system.Model or ""
                    device.system_family = system.SystemFamily or ""
                    device.total_physical_memory_gb = float(system.TotalPhysicalMemory or 0) / (1024**3)
                    device.memory_gb = device.total_physical_memory_gb  # Backward compatibility
                    device.current_user = system.UserName or ""
                    break
            except Exception as e:
                self.logger.debug(f"System info collection failed: {e}")
            
            # === HOSTNAME MISMATCH DETECTION ===
            try:
                # Get DNS hostname
                import socket
                try:
                    device.dns_hostname = socket.gethostbyaddr(ip)[0].lower()
                    device.domain_hostname = device.dns_hostname
                    
                    # Compare hostnames
                    if device.device_hostname.lower() == device.dns_hostname.lower():
                        device.hostname_mismatch_status = "Match"
                        device.hostname_mismatch_details = "Device and DNS hostnames match"
                    else:
                        device.hostname_mismatch_status = "Mismatch"
                        device.hostname_mismatch_details = f"Device: {device.device_hostname}, DNS: {device.dns_hostname}"
                except:
                    device.hostname_mismatch_status = "No_Domain_Record"
                    device.hostname_mismatch_details = "No DNS record found for device IP"
            except Exception:
                device.hostname_mismatch_status = "DNS_Error"
                device.hostname_mismatch_details = "Error resolving DNS hostname"
            
            # === SYSTEM DETAILS ===
            try:
                for cs_product in c.Win32_ComputerSystemProduct():
                    device.uuid = cs_product.UUID or ""
                    device.serial_number = cs_product.IdentifyingNumber or ""
                    break
            except Exception:
                pass
            
            # === PROCESSOR INFORMATION ===
            try:
                processors = []
                total_cores = 0
                total_logical = 0
                max_speed = 0
                
                for processor in c.Win32_Processor():
                    device.processor_name = processor.Name or ""
                    device.processor_manufacturer = processor.Manufacturer or ""
                    device.processor_architecture = processor.Architecture or ""
                    device.processor_cores = processor.NumberOfCores or 0
                    device.processor_logical_cores = processor.NumberOfLogicalProcessors or 0
                    device.processor_speed_mhz = processor.CurrentClockSpeed or 0
                    device.processor_max_speed_mhz = processor.MaxClockSpeed or 0
                    device.processor_l2_cache_size = str(processor.L2CacheSize or 0) + " KB"
                    device.processor_l3_cache_size = str(processor.L3CacheSize or 0) + " KB"
                    
                    total_cores += processor.NumberOfCores or 0
                    total_logical += processor.NumberOfLogicalProcessors or 0
                    max_speed = max(max_speed, processor.MaxClockSpeed or 0)
                    
                    processors.append(f"{processor.Name} ({processor.NumberOfCores} cores)")
                
                device.processor = "; ".join(processors)  # Backward compatibility
            except Exception as e:
                self.logger.debug(f"Processor info collection failed: {e}")
            
            # === MEMORY INFORMATION ===
            try:
                memory_modules = []
                memory_slots_used = 0
                total_slots = 0
                
                for memory in c.Win32_PhysicalMemory():
                    memory_slots_used += 1
                    capacity_gb = float(memory.Capacity or 0) / (1024**3)
                    
                    memory_module = {
                        "slot": memory.DeviceLocator or f"Slot {memory_slots_used}",
                        "capacity_gb": capacity_gb,
                        "speed_mhz": memory.Speed or 0,
                        "manufacturer": memory.Manufacturer or "",
                        "part_number": memory.PartNumber or "",
                        "type": memory.MemoryType or "Unknown"
                    }
                    memory_modules.append(memory_module)
                
                # Get total slots from motherboard
                try:
                    for board in c.Win32_BaseBoard():
                        total_slots = getattr(board, 'MaxMemorySupported', memory_slots_used)
                        break
                except:
                    total_slots = memory_slots_used
                
                device.memory_modules = memory_modules
                device.memory_slots_used = memory_slots_used
                device.memory_slots_total = total_slots
                
                # Available memory
                for os_info in c.Win32_OperatingSystem():
                    device.available_memory_gb = float(os_info.FreePhysicalMemory or 0) / (1024**2)
                    device.memory_usage_percent = ((device.total_physical_memory_gb - device.available_memory_gb) / device.total_physical_memory_gb) * 100 if device.total_physical_memory_gb > 0 else 0
                    break
                    
            except Exception as e:
                self.logger.debug(f"Memory info collection failed: {e}")
            
            # === STORAGE INFORMATION ===
            try:
                storage_devices = []
                disk_summaries = []
                total_storage = 0
                available_storage = 0
                disk_count = 0
                
                # Physical drives
                for disk in c.Win32_DiskDrive():
                    disk_count += 1
                    size_gb = float(disk.Size or 0) / (1024**3)
                    total_storage += size_gb
                    
                    storage_device = {
                        "device_id": disk.DeviceID or f"Disk {disk_count}",
                        "model": disk.Model or "",
                        "size_gb": size_gb,
                        "media_type": disk.MediaType or "",
                        "interface_type": disk.InterfaceType or "",
                        "manufacturer": getattr(disk, 'Manufacturer', '') or ""
                    }
                    storage_devices.append(storage_device)
                    
                    # Create summary (Disk 1: 250GB SSD, Disk 2: 500GB HDD)
                    media_type = "SSD" if "SSD" in (disk.Model or "") else "HDD"
                    disk_summaries.append(f"Disk {disk_count}: {size_gb:.0f}GB {media_type}")
                
                # Logical drives for available space
                for drive in c.Win32_LogicalDisk():
                    if drive.DriveType == 3:  # Fixed disk
                        available_storage += float(drive.FreeSpace or 0) / (1024**3)
                
                device.storage_devices = storage_devices
                device.total_storage_gb = total_storage
                device.available_storage_gb = available_storage
                device.storage_summary = ", ".join(disk_summaries)
                device.disk_info = device.storage_summary  # Backward compatibility
                device.disk_usage_percent = ((total_storage - available_storage) / total_storage) * 100 if total_storage > 0 else 0
                
            except Exception as e:
                self.logger.debug(f"Storage info collection failed: {e}")
            
            # === GRAPHICS INFORMATION ===
            try:
                graphics_cards = []
                graphics_list = []  # For backward compatibility
                total_vram = 0
                
                for gpu in c.Win32_VideoController():
                    if gpu.Name and 'Microsoft Basic' not in gpu.Name:
                        vram_mb = 0
                        try:
                            vram_mb = int(gpu.AdapterRAM or 0) / (1024**2)
                        except:
                            pass
                            
                        graphics_card = {
                            "name": gpu.Name or "",
                            "adapter_ram_mb": vram_mb,
                            "driver_version": gpu.DriverVersion or "",
                            "driver_date": gpu.DriverDate or "",
                            "resolution": f"{gpu.CurrentHorizontalResolution}x{gpu.CurrentVerticalResolution}" if gpu.CurrentHorizontalResolution else "",
                            "refresh_rate": gpu.CurrentRefreshRate or 0
                        }
                        graphics_cards.append(graphics_card)
                        graphics_list.append(gpu.Name)
                        total_vram += vram_mb
                        
                        if not device.primary_graphics_card:
                            device.primary_graphics_card = gpu.Name or ""
                            device.graphics_driver_version = gpu.DriverVersion or ""
                
                device.graphics_cards = graphics_cards
                device.graphics_memory_mb = int(total_vram)
                
            except Exception as e:
                self.logger.debug(f"Graphics info collection failed: {e}")
            
            # === DISPLAY INFORMATION ===
            try:
                monitor_details = []
                display_adapters = []
                connected_monitors = 0
                
                for monitor in c.Win32_DesktopMonitor():
                    connected_monitors += 1
                    monitor_info = {
                        "name": monitor.Name or f"Monitor {connected_monitors}",
                        "manufacturer": getattr(monitor, 'MonitorManufacturer', '') or "",
                        "model": getattr(monitor, 'MonitorType', '') or "",
                        "screen_width": monitor.ScreenWidth or 0,
                        "screen_height": monitor.ScreenHeight or 0
                    }
                    monitor_details.append(monitor_info)
                
                # Get display adapters
                for adapter in c.Win32_DisplayConfiguration():
                    adapter_info = {
                        "device_name": adapter.DeviceName or "",
                        "adapter_string": getattr(adapter, 'AdapterString', '') or ""
                    }
                    display_adapters.append(adapter_info)
                
                device.connected_monitors = connected_monitors
                device.monitor_details = monitor_details
                device.display_adapters = display_adapters
                
                # Set screen resolution from first graphics card
                if graphics_cards and graphics_cards[0].get("resolution"):
                    device.screen_resolution = graphics_cards[0]["resolution"]
                    
            except Exception as e:
                self.logger.debug(f"Display info collection failed: {e}")
            
            # === NETWORK INFORMATION ===
            try:
                network_adapters = []
                wireless_adapters = []
                network_config = {}
                
                for adapter in c.Win32_NetworkAdapterConfiguration():
                    if adapter.IPEnabled and adapter.Description:
                        adapter_info = {
                            "description": adapter.Description or "",
                            "mac_address": adapter.MACAddress or "",
                            "ip_addresses": adapter.IPAddress or [],
                            "subnet_masks": adapter.IPSubnet or [],
                            "default_gateways": adapter.DefaultIPGateway or [],
                            "dns_servers": adapter.DNSServerSearchOrder or [],
                            "dhcp_enabled": adapter.DHCPEnabled or False,
                            "dhcp_server": adapter.DHCPServer or ""
                        }
                        network_adapters.append(adapter_info)
                        
                        # Check if this adapter serves our IP
                        if adapter.IPAddress and ip in adapter.IPAddress:
                            device.mac_address = adapter.MACAddress or ""
                            network_config = adapter_info
                        
                        # Check if wireless
                        if adapter.Description and any(term in adapter.Description.lower() for term in ['wireless', 'wi-fi', 'wifi', '802.11']):
                            wireless_adapters.append(adapter_info)
                
                device.network_adapters = network_adapters
                device.wireless_adapters = wireless_adapters
                device.network_configuration = network_config
                
            except Exception as e:
                self.logger.debug(f"Network info collection failed: {e}")
            
            # === OPERATING SYSTEM ===
            try:
                for os_info in c.Win32_OperatingSystem():
                    device.os_family = "Windows"
                    device.operating_system = os_info.Caption or ""
                    device.os_version = os_info.Version or ""
                    device.os_build = os_info.BuildNumber or ""
                    device.os_edition = os_info.OperatingSystemSKU or ""
                    device.os_architecture = os_info.OSArchitecture or ""
                    device.os_install_date = os_info.InstallDate or ""
                    device.last_boot_time = os_info.LastBootUpTime or ""
                    device.registered_owner = os_info.RegisteredUser or ""
                    
                    # Calculate uptime
                    try:
                        if os_info.LastBootUpTime:
                            boot_time = time.strptime(os_info.LastBootUpTime[:14], '%Y%m%d%H%M%S')
                            boot_timestamp = time.mktime(boot_time)
                            device.system_uptime_hours = (time.time() - boot_timestamp) / 3600
                    except:
                        pass
                    break
            except Exception as e:
                self.logger.debug(f"OS info collection failed: {e}")
            
            # === BIOS/UEFI INFORMATION ===
            try:
                for bios in c.Win32_BIOS():
                    device.bios_manufacturer = bios.Manufacturer or ""
                    device.bios_version = bios.Version or ""
                    device.bios_release_date = bios.ReleaseDate or ""
                    device.firmware_type = "UEFI" if hasattr(bios, 'SMBIOSBIOSVERSION') else "BIOS"
                    break
            except Exception:
                pass
            
            # === INSTALLED SOFTWARE ===
            try:
                installed_software = []
                software_count = 0
                browsers = []
                
                for product in c.Win32_Product():
                    software_count += 1
                    if software_count > 100:  # Limit to prevent timeout
                        break
                        
                    software_info = {
                        "name": product.Name or "",
                        "version": product.Version or "",
                        "vendor": product.Vendor or "",
                        "install_date": product.InstallDate or ""
                    }
                    installed_software.append(software_info)
                    
                    # Detect browsers
                    if product.Name and any(browser in product.Name.lower() for browser in ['chrome', 'firefox', 'edge', 'safari', 'opera']):
                        browsers.append(product.Name)
                
                device.installed_software = installed_software
                device.browsers_installed = browsers
                
            except Exception as e:
                self.logger.debug(f"Software collection failed: {e}")
            
            # === SECURITY INFORMATION ===
            try:
                # Windows Defender
                for defender in c.AntiVirusProduct():
                    if "windows defender" in (defender.displayName or "").lower():
                        device.windows_defender_status = "Enabled"
                        device.antivirus_software = defender.displayName or ""
                        break
                else:
                    device.windows_defender_status = "Unknown"
                
                # Firewall status
                for firewall in c.Win32_SystemEnclosure():
                    device.firewall_status = "Unknown"  # WMI doesn't easily provide firewall status
                    break
                    
            except Exception:
                pass
            
            # === PERFORMANCE METRICS ===
            try:
                # CPU usage
                for processor in c.Win32_PerfRawData_PerfOS_Processor():
                    if processor.Name == "_Total":
                        device.cpu_usage_percent = float(processor.PercentProcessorTime or 0)
                        break
            except Exception:
                pass
            
            # === COMPREHENSIVE USER INFORMATION & PRIVILEGES ===
            try:
                self.logger.debug("🔐 Starting comprehensive user information collection...")
                # Current logged-in users and sessions
                login_sessions = []
                logged_users = []
                
                # Get active login sessions
                session_count = 0
                for session in c.Win32_LogonSession():
                    if session.LogonType in [2, 10, 11]:  # Interactive, RemoteInteractive, CachedInteractive
                        session_count += 1
                        session_info = {
                            "session_id": session.LogonId or "",
                            "logon_type": session.LogonType or 0,
                            "logon_type_name": {
                                2: "Interactive",
                                3: "Network", 
                                4: "Batch",
                                5: "Service",
                                7: "Unlock",
                                8: "NetworkCleartext",
                                9: "NewCredentials",
                                10: "RemoteInteractive",
                                11: "CachedInteractive"
                            }.get(session.LogonType, "Unknown"),
                            "start_time": session.StartTime or "",
                            "authentication_package": session.AuthenticationPackage or ""
                        }
                        login_sessions.append(session_info)
                
                device.login_sessions = login_sessions
                self.logger.debug(f"🔐 Found {session_count} interactive login sessions")
                
                # Get currently logged-in interactive user
                for process in c.Win32_Process():
                    if process.Name and process.Name.lower() == "explorer.exe":
                        # Explorer.exe runs for logged-in users
                        try:
                            owner = process.GetOwner()
                            if owner and len(owner) >= 2:
                                interactive_user = f"{owner[0]}\\{owner[1]}" if owner[0] else owner[1]
                                device.interactive_user = interactive_user
                                device.current_logged_user = interactive_user
                                logged_users.append(interactive_user)
                                break
                        except:
                            pass
                
                # Get all local user accounts with detailed information
                local_users = []
                local_user_count = 0
                for user in c.Win32_UserAccount():
                    if user.LocalAccount:  # Only local accounts
                        local_user_count += 1
                        user_info = {
                            "username": user.Name or "",
                            "full_name": user.FullName or "",
                            "description": user.Description or "",
                            "disabled": user.Disabled or False,
                            "locked_out": user.Lockout or False,
                            "password_required": user.PasswordRequired or False,
                            "password_changeable": user.PasswordChangeable or False,
                            "password_expires": user.PasswordExpires or False,
                            "account_type": user.AccountType or 0,
                            "sid": user.SID or "",
                            "domain": user.Domain or "",
                            "status": user.Status or ""
                        }
                        local_users.append(user_info)
                
                device.local_users = local_users
                self.logger.debug(f"👤 Found {local_user_count} local user accounts")
                
                # Get domain users (if domain-joined)
                domain_users = []
                for user in c.Win32_UserAccount():
                    if not user.LocalAccount:  # Domain accounts
                        user_info = {
                            "username": user.Name or "",
                            "full_name": user.FullName or "",
                            "description": user.Description or "",
                            "domain": user.Domain or "",
                            "sid": user.SID or "",
                            "status": user.Status or ""
                        }
                        domain_users.append(user_info)
                
                device.domain_users = domain_users
                
                # Get user groups and privileges
                user_groups = []
                admin_users = []
                
                for group in c.Win32_Group():
                    group_info = {
                        "name": group.Name or "",
                        "description": group.Description or "",
                        "domain": group.Domain or "",
                        "sid": group.SID or "",
                        "group_type": group.GroupType or 0,
                        "local_group": group.LocalAccount or False
                    }
                    user_groups.append(group_info)
                    
                    # Identify admin groups
                    if group.Name and group.Name.lower() in ['administrators', 'domain admins', 'enterprise admins']:
                        try:
                            # Get group members
                            for member in c.Win32_GroupUser():
                                if member.GroupComponent and member.GroupComponent.Name == group.Name:
                                    admin_user = member.PartComponent.Name if member.PartComponent else ""
                                    if admin_user and admin_user not in admin_users:
                                        admin_users.append(admin_user)
                        except:
                            pass
                
                device.user_groups = user_groups
                device.admin_users = admin_users
                
                # Get user profiles with detailed information
                user_profiles = []
                for profile in c.Win32_UserProfile():
                    profile_info = {
                        "sid": profile.SID or "",
                        "local_path": profile.LocalPath or "",
                        "loaded": profile.Loaded or False,
                        "roaming": profile.RoamingConfigured or False,
                        "roaming_path": profile.RoamingPath or "",
                        "roaming_preference": profile.RoamingPreference or 0,
                        "status": profile.Status or "",
                        "last_use_time": profile.LastUseTime or "",
                        "special": profile.Special or False
                    }
                    
                    # Try to get username from SID
                    try:
                        for user in c.Win32_UserAccount():
                            if user.SID == profile.SID:
                                profile_info["username"] = user.Name or ""
                                profile_info["domain"] = user.Domain or ""
                                break
                    except:
                        pass
                    
                    user_profiles.append(profile_info)
                
                device.user_profiles = user_profiles
                
                # Get recent logon users from event logs (if accessible)
                recent_users = []
                try:
                    for event in c.Win32_NTLogEvent():
                        if event.EventCode in [4624, 528]:  # Successful logon events
                            if event.User and event.User not in recent_users:
                                recent_users.append(event.User)
                            if len(recent_users) >= 10:  # Limit to recent 10
                                break
                except:
                    pass
                
                # Combine all logged users
                all_recent_users = list(set(logged_users + recent_users))
                device.last_logged_users = all_recent_users
                
                self.logger.debug(f"Collected user info: {len(local_users)} local users, {len(domain_users)} domain users, {len(admin_users)} admin users")
                
            except Exception as e:
                self.logger.debug(f"User information collection failed: {e}")
            
            # === COLLECTION METADATA ===
            device.collection_method = "WMI (Comprehensive)"
            device.collection_time = time.time() - start_time
            device.collection_duration_seconds = device.collection_time
            device.confidence = 0.98  # High confidence for comprehensive WMI collection
            
            # Calculate data completeness score
            total_fields = 100  # Approximate total important fields
            filled_fields = 0
            
            # Count filled fields
            for field_name, field_value in device.__dict__.items():
                if field_value and field_value != "" and field_value != 0 and field_value != []:
                    filled_fields += 1
            
            device.data_completeness_score = min(int((filled_fields / total_fields) * 100), 100)
            
            self.logger.info(f"✅ Comprehensive WMI collection completed for {ip} - {device.data_completeness_score}% complete in {device.collection_time:.2f}s")
            
            # Cleanup COM
            pythoncom.CoUninitialize()
            
            return device
        
        except Exception as e:
            self.logger.debug(f"Comprehensive WMI collection failed for {ip}: {e}")
            
            # Cleanup COM
            try:
                pythoncom.CoUninitialize()
            except:
                pass
                
            return None
    
    def _ssh_collect(self, ip: str) -> Optional[EnhancedDeviceInfo]:
        """Enhanced SSH collection for Linux/Unix systems"""
        if not PARAMIKO_AVAILABLE:
            return None
        
        try:
            start_time = time.time()
            
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # SSH credentials
            username = self.credentials.get('ssh_username', 'root')
            password = self.credentials.get('ssh_password', '')
            key_file = self.credentials.get('ssh_key_file', '')
            
            # Connect
            if key_file:
                ssh.connect(ip, username=username, key_filename=key_file, timeout=15)
            elif password:
                ssh.connect(ip, username=username, password=password, timeout=15)
            else:
                return None
            
            device = EnhancedDeviceInfo(ip=ip)
            
            # Hostname
            stdin, stdout, stderr = ssh.exec_command('hostname')
            device.hostname = stdout.read().decode().strip().lower()
            
            # OS detection
            stdin, stdout, stderr = ssh.exec_command('uname -a')
            uname_output = stdout.read().decode().strip()
            if 'linux' in uname_output.lower():
                device.os_family = "Linux"
            elif 'darwin' in uname_output.lower():
                device.os_family = "macOS"
            else:
                device.os_family = "Unix"
            
            # OS version
            for cmd in ['lsb_release -d 2>/dev/null', 'cat /etc/os-release 2>/dev/null | head -1', 'cat /etc/redhat-release 2>/dev/null']:
                try:
                    stdin, stdout, stderr = ssh.exec_command(cmd)
                    output = stdout.read().decode().strip()
                    if output:
                        device.os_version = output.split('\n')[0]
                        break
                except:
                    continue
            
            # CPU info
            stdin, stdout, stderr = ssh.exec_command('cat /proc/cpuinfo 2>/dev/null | grep "model name" | head -1')
            cpu_output = stdout.read().decode().strip()
            if cpu_output and ':' in cpu_output:
                device.processor = cpu_output.split(':', 1)[1].strip()
            
            # Memory
            stdin, stdout, stderr = ssh.exec_command('cat /proc/meminfo 2>/dev/null | grep MemTotal')
            mem_output = stdout.read().decode().strip()
            if mem_output:
                try:
                    mem_kb = int(mem_output.split()[1])
                    device.memory_gb = mem_kb / (1024 * 1024)
                except:
                    pass
            
            # Disk info
            stdin, stdout, stderr = ssh.exec_command('df -h 2>/dev/null | grep -E "^/dev"')
            disk_output = stdout.read().decode().strip()
            if disk_output:
                disks = []
                for line in disk_output.split('\n'):
                    parts = line.split()
                    if len(parts) >= 6:
                        disks.append(f"{parts[0]} = {parts[1]}")
                device.disk_info = ", ".join(disks)
            
            ssh.close()
            
            device.collection_method = "SSH"
            device.collection_time = time.time() - start_time
            device.confidence = 0.9
            
            return device
        
        except Exception as e:
            self.logger.debug(f"SSH collection failed for {ip}: {e}")
            return None
    
    async def collect_devices_async(self, ip_addresses: List[str], 
                                  progress_callback=None,
                                  device_callback=None) -> Dict[str, EnhancedDeviceInfo]:
        """
        🚀 Enhanced Ultimate Performance Device Collection
        
        Combines ultimate speed with smart classification
        """
        
        if not ip_addresses:
            return {}
        
        self.logger.info("🚀 Starting Enhanced Ultimate Performance Collection")
        self.logger.info(f"   ⚡ Devices to process: {len(ip_addresses)}")
        self.logger.info(f"   🧠 Enhanced Classification: {self.config['enable_enhanced_classification']}")
        self.logger.info(f"   🔧 Collection methods: WMI={WMI_AVAILABLE}, SSH={PARAMIKO_AVAILABLE}, NMAP={NMAP_AVAILABLE}")
        
        # ENHANCED: Setup enhanced database schema
        try:
            self.setup_enhanced_database()
            self.logger.info("📊 Enhanced database schema ready for comprehensive data collection")
        except Exception as e:
            self.logger.warning(f"⚠️ Enhanced database setup failed: {e} - continuing with collection only")
        
        # Initialize metrics
        self.metrics.total_ips = len(ip_addresses)
        self.metrics.start_time = time.time()
        
        # Phase 1: Ultimate Performance Validation
        validation_start = time.time()
        self.logger.info("📡 Phase 1: Ultimate performance validation...")
        
        if self.validator:
            validation_results = await self.validator.validate_devices_async(
                ip_addresses,
                progress_callback=lambda p: progress_callback(p * 0.3) if progress_callback else None
            )
        else:
            # Fallback validation
            validation_results = {}
            for ip in ip_addresses:
                validation_results[ip] = DeviceStatus(ip, ValidationResult.ALIVE, 0.8)
        
        self.metrics.validation_time = time.time() - validation_start
        
        # Filter alive devices
        alive_devices = {
            ip: result for ip, result in validation_results.items() 
            if result.status == ValidationResult.ALIVE
        }
        
        self.metrics.validated_alive = len(alive_devices)
        self.logger.info(f"   ✅ Validation complete: {len(alive_devices)} alive devices found")
        
        if not alive_devices:
            return {}
        
        # Phase 2: Enhanced Collection with Smart Classification
        collection_start = time.time()
        self.logger.info("📊 Phase 2: Enhanced collection with smart classification...")
        
        self.metrics.collection_attempted = len(alive_devices)
        
        # Create thread pool
        self.collection_executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_collection_concurrent
        )
        
        try:
            # Submit collection tasks
            future_to_ip = {}
            for ip, validation_result in alive_devices.items():
                future = self.collection_executor.submit(
                    self._collect_single_device, ip, validation_result
                )
                future_to_ip[future] = ip
            
            # Process results with streaming and timeout handling
            collected_devices = {}
            completed = 0
            
            try:
                for future in concurrent.futures.as_completed(future_to_ip, timeout=None):  # No timeout limit
                    ip = future_to_ip[future]
                    completed += 1
                    
                    try:
                        device = future.result(timeout=self.config['collection_timeout'])
                        if device:
                            collected_devices[ip] = device
                            
                            # ENHANCED: Save comprehensive data to enhanced database
                            try:
                                self.save_device_to_enhanced_db(device)
                                self.logger.debug(f"✅ Saved comprehensive data for {ip} to enhanced database")
                            except Exception as e:
                                self.logger.warning(f"⚠️ Failed to save {ip} to enhanced database: {e}")
                            
                            # Real-time device callback
                            if device_callback:
                                device_callback(device)
                            
                            self.logger.debug(f"Enhanced collection: {device.device_type} at {ip}")
                    
                    except concurrent.futures.TimeoutError:
                        self.logger.warning(f"Collection timeout for {ip}")
                        self.metrics.collection_failed += 1
                    except Exception as e:
                        self.logger.error(f"Collection error for {ip}: {e}")
                        self.metrics.collection_failed += 1
                    
                    # Progress update
                    if progress_callback:
                        overall_progress = 30 + (completed / len(alive_devices)) * 70
                        progress_callback(overall_progress)
                    
                    # Periodic progress logging
                    if completed % 10 == 0:
                        collection_speed = completed / (time.time() - collection_start)
                        self.logger.info(f"   📊 Progress: {completed}/{len(alive_devices)} ({collection_speed:.1f} devices/sec)")
            
            except concurrent.futures.TimeoutError:
                self.logger.warning(f"Collection completed with timeout after {completed}/{len(alive_devices)} devices")
                # Continue with collected devices
        
        finally:
            self.collection_executor.shutdown(wait=True)
        
        self.metrics.collection_time = time.time() - collection_start
        
        # Final statistics
        total_time = time.time() - self.metrics.start_time
        self.logger.info("🏆 Enhanced Ultimate Performance Collection Complete!")
        self.logger.info(f"   📊 Collected: {len(collected_devices)}/{len(alive_devices)} devices")
        self.logger.info(f"   ⚡ Collection speed: {len(collected_devices) / self.metrics.collection_time:.1f} devices/sec")
        self.logger.info(f"   🧠 Classification success: {self.metrics.classification_successful}/{len(collected_devices)}")
        self.logger.info(f"   ⏱️  Total time: {total_time:.1f} seconds")
        
        return collected_devices
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get enhanced performance metrics"""
        return {
            'total_ips': self.metrics.total_ips,
            'validated_alive': self.metrics.validated_alive,
            'collection_attempted': self.metrics.collection_attempted,
            'collection_successful': self.metrics.collection_successful,
            'collection_failed': self.metrics.collection_failed,
            'classification_successful': self.metrics.classification_successful,
            'classification_failed': self.metrics.classification_failed,
            'validation_time': self.metrics.validation_time,
            'collection_time': self.metrics.collection_time,
            'devices_per_second': self.metrics.collection_successful / max(self.metrics.collection_time, 0.1),
            'success_rate': self.metrics.collection_successful / max(self.metrics.collection_attempted, 1) * 100,
            'classification_success_rate': self.metrics.classification_successful / max(self.metrics.collection_successful, 1) * 100
        }

# Test the enhanced collector
if __name__ == "__main__":
    async def test_enhanced_collector():
        """Test the enhanced ultimate performance collector"""
        print("🧪 Testing Enhanced Ultimate Performance Collector...")
        
        # Test configuration
        config = {
            'enable_enhanced_classification': True,
            'classification_confidence_threshold': 0.6,
            'max_workers': 100
        }
        
        collector = EnhancedUltimatePerformanceCollector(config=config)
        
        # Test with a small subnet
        test_ips = [f"192.168.1.{i}" for i in range(1, 21)]
        
        def progress_callback(progress):
            print(f"Progress: {progress:.1f}%")
        
        def device_callback(device):
            print(f"✅ Collected: {device.device_type} at {device.ip} (confidence: {device.confidence:.2f})")
        
        # Run collection
        results = await collector.collect_devices_async(
            test_ips,
            progress_callback=progress_callback,
            device_callback=device_callback
        )
        
        # Show results
        print("\n🏆 Enhanced Collection Results:")
        print(f"Devices collected: {len(results)}")
        
        # Show device types
        device_types = {}
        for device in results.values():
            device_type = device.device_type
            device_types[device_type] = device_types.get(device_type, 0) + 1
        
        print("Device Type Distribution:")
        for device_type, count in device_types.items():
            print(f"  {device_type}: {count}")
        
        # Performance metrics
        metrics = collector.get_performance_metrics()
        print("\n📊 Performance Metrics:")
        print(f"  Collection speed: {metrics['devices_per_second']:.1f} devices/sec")
        print(f"  Success rate: {metrics['success_rate']:.1f}%")
        print(f"  Classification success: {metrics['classification_success_rate']:.1f}%")
    
    # Run test
    asyncio.run(test_enhanced_collector())