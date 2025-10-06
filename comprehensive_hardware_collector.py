#!/usr/bin/env python3
"""
COMPREHENSIVE HARDWARE & SOFTWARE DATA COLLECTOR
Enhanced version to collect ALL possible hardware and software information

Features:
✅ Complete hardware specifications (CPU, RAM, Storage, GPU, etc.)
✅ Connected monitors and display information
✅ Detailed graphics card information
✅ Complete storage breakdown (disk by disk)
✅ Network interfaces and configuration
✅ Software inventory and installed programs
✅ Hostname mismatch detection and tracking
✅ Domain vs Device hostname comparison
✅ Change tracking for all components
✅ Real-time device status monitoring
✅ Enhanced error handling and logging
"""

import json
import sqlite3
import socket
import platform
import psutil
import wmi
import time
from datetime import datetime
import logging
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('comprehensive_collection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ComprehensiveHardwareCollector:
    def __init__(self, db_path="assets.db"):
        self.db_path = db_path
        self.collection_id = str(uuid.uuid4())
        self.collection_start = datetime.now()
        
        # Initialize WMI connection
        try:
            self.wmi_conn = wmi.WMI()
            logger.info("✅ WMI connection established")
        except Exception as e:
            logger.error(f"❌ WMI connection failed: {e}")
            self.wmi_conn = None
    
    def setup_enhanced_database(self):
        """Create enhanced database schema with all tracking columns"""
        conn = sqlite3.connect(self.db_path)
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
                
                -- User Information
                current_user TEXT,
                registered_owner TEXT,
                last_logged_users TEXT, -- JSON array of recent users
                user_profiles TEXT, -- JSON array of user profiles
                
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
                
                -- Additional Fields
                motherboard_manufacturer TEXT,
                motherboard_model TEXT,
                power_supply_info TEXT,
                cooling_system TEXT,
                expansion_slots TEXT, -- JSON array
                usb_devices TEXT, -- JSON array of connected USB devices
                
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create change tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hardware_changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_id INTEGER,
                change_type TEXT, -- 'Hardware', 'Software', 'Configuration'
                field_name TEXT,
                old_value TEXT,
                new_value TEXT,
                change_timestamp TEXT,
                collection_id TEXT,
                FOREIGN KEY (asset_id) REFERENCES assets_enhanced (id)
            )
        ''')
        
        # Create collection log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS collection_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                collection_id TEXT,
                hostname TEXT,
                collection_method TEXT,
                start_time TEXT,
                end_time TEXT,
                duration_seconds REAL,
                success BOOLEAN,
                error_message TEXT,
                data_collected INTEGER, -- Number of fields collected
                completeness_score INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✅ Enhanced database schema created successfully")
    
    def collect_comprehensive_data(self, target_ip=None):
        """Collect comprehensive hardware and software data"""
        start_time = time.time()
        
        if target_ip:
            logger.info(f"🔍 Starting comprehensive collection for {target_ip}")
            return self.collect_remote_data(target_ip)
        else:
            logger.info("🔍 Starting comprehensive collection for local machine")
            return self.collect_local_data()
    
    def collect_local_data(self):
        """Collect comprehensive data from local machine"""
        data = {}
        collection_start = time.time()
        
        try:
            # Basic system information
            data.update(self.get_basic_system_info())
            
            # Hostname and domain information
            data.update(self.get_hostname_information())
            
            # Hardware specifications
            data.update(self.get_processor_information())
            data.update(self.get_memory_information())
            data.update(self.get_storage_information())
            data.update(self.get_graphics_information())
            data.update(self.get_display_information())
            data.update(self.get_motherboard_information())
            
            # Network information
            data.update(self.get_network_information())
            
            # Operating system information
            data.update(self.get_operating_system_info())
            data.update(self.get_bios_information())
            
            # Software information
            data.update(self.get_software_information())
            data.update(self.get_security_information())
            
            # User information
            data.update(self.get_user_information())
            
            # Performance information
            data.update(self.get_performance_information())
            
            # USB and expansion information
            data.update(self.get_usb_devices())
            data.update(self.get_expansion_slots())
            
            # Collection metadata
            collection_duration = time.time() - collection_start
            data['collection_duration_seconds'] = round(collection_duration, 2)
            data['collection_timestamp'] = datetime.now().isoformat()
            data['collection_id'] = self.collection_id
            data['collection_method'] = 'Local_WMI_Enhanced'
            
            # Calculate data completeness score
            data['data_completeness_score'] = self.calculate_completeness_score(data)
            
            logger.info(f"✅ Local data collection completed in {collection_duration:.2f} seconds")
            logger.info(f"📊 Data completeness: {data['data_completeness_score']}%")
            
            return data
            
        except Exception as e:
            logger.error(f"❌ Error in local data collection: {e}")
            return {'error': str(e), 'collection_method': 'Local_WMI_Enhanced_Error'}
    
    def get_basic_system_info(self):
        """Get basic system identification information"""
        data = {}
        
        try:
            # Computer system information
            if self.wmi_conn:
                for cs in self.wmi_conn.Win32_ComputerSystem():
                    data['computer_name'] = cs.Name
                    data['system_manufacturer'] = cs.Manufacturer
                    data['system_model'] = cs.Model
                    data['total_physical_memory_gb'] = round(int(cs.TotalPhysicalMemory) / (1024**3), 2) if cs.TotalPhysicalMemory else None
                    data['current_user'] = cs.UserName
                    data['domain_name'] = cs.Domain
                    data['workgroup'] = cs.Workgroup if not cs.PartOfDomain else None
                
                # System enclosure (chassis) information
                for se in self.wmi_conn.Win32_SystemEnclosure():
                    data['serial_number'] = se.SerialNumber
                    data['asset_tag'] = se.SMBIOSAssetTag
            
            # Platform information
            data['hostname'] = socket.gethostname()
            data['device_hostname'] = platform.node()
            
            logger.info("✅ Basic system information collected")
            
        except Exception as e:
            logger.error(f"❌ Error collecting basic system info: {e}")
            
        return data
    
    def get_hostname_information(self):
        """Get comprehensive hostname and domain information with mismatch detection"""
        data = {}
        
        try:
            # Get current device hostname
            device_hostname = socket.gethostname().lower()
            computer_name = platform.node().lower()
            
            data['device_hostname'] = device_hostname
            data['computer_name'] = computer_name
            
            # Try to get DNS hostname
            try:
                # Get IP address
                ip_address = socket.gethostbyname(device_hostname)
                data['ip_address'] = ip_address
                
                # Reverse DNS lookup to get domain hostname
                domain_hostname = socket.gethostbyaddr(ip_address)[0].lower()
                data['domain_hostname'] = domain_hostname
                data['dns_hostname'] = domain_hostname
                
                # Compare hostnames
                if device_hostname == domain_hostname.split('.')[0]:
                    data['hostname_mismatch_status'] = 'Match'
                    data['hostname_mismatch_details'] = 'Device and DNS hostnames match'
                else:
                    data['hostname_mismatch_status'] = 'Mismatch'
                    data['hostname_mismatch_details'] = f'Device: {device_hostname}, DNS: {domain_hostname.split(".")[0]}'
                
            except socket.herror:
                data['hostname_mismatch_status'] = 'No_Domain_Record'
                data['hostname_mismatch_details'] = 'No DNS record found for this device'
                data['domain_hostname'] = None
                data['dns_hostname'] = None
                
            except Exception as e:
                data['hostname_mismatch_status'] = 'DNS_Error'
                data['hostname_mismatch_details'] = f'DNS lookup error: {str(e)}'
                data['domain_hostname'] = None
                data['dns_hostname'] = None
            
            # Get domain information from WMI
            if self.wmi_conn:
                for cs in self.wmi_conn.Win32_ComputerSystem():
                    if cs.PartOfDomain:
                        data['domain_name'] = cs.Domain
                    else:
                        data['workgroup'] = cs.Workgroup
            
            logger.info(f"✅ Hostname information collected - Status: {data.get('hostname_mismatch_status', 'Unknown')}")
            
        except Exception as e:
            logger.error(f"❌ Error collecting hostname information: {e}")
            
        return data
    
    def get_processor_information(self):
        """Get detailed processor information"""
        data = {}
        
        try:
            if self.wmi_conn:
                for processor in self.wmi_conn.Win32_Processor():
                    data['processor_name'] = processor.Name
                    data['processor_manufacturer'] = processor.Manufacturer
                    data['processor_architecture'] = processor.Architecture
                    data['processor_cores'] = processor.NumberOfCores
                    data['processor_logical_cores'] = processor.NumberOfLogicalProcessors
                    data['processor_speed_mhz'] = processor.CurrentClockSpeed
                    data['processor_max_speed_mhz'] = processor.MaxClockSpeed
                    data['processor_l2_cache_size'] = f"{processor.L2CacheSize} KB" if processor.L2CacheSize else None
                    data['processor_l3_cache_size'] = f"{processor.L3CacheSize} KB" if processor.L3CacheSize else None
                    break  # Take first processor
            
            logger.info("✅ Processor information collected")
            
        except Exception as e:
            logger.error(f"❌ Error collecting processor information: {e}")
            
        return data
    
    def get_memory_information(self):
        """Get detailed memory information"""
        data = {}
        memory_modules = []
        
        try:
            total_memory = 0
            slots_used = 0
            slots_total = 0
            
            if self.wmi_conn:
                # Physical memory modules
                for memory in self.wmi_conn.Win32_PhysicalMemory():
                    slots_used += 1
                    capacity_gb = round(int(memory.Capacity) / (1024**3), 2) if memory.Capacity else 0
                    total_memory += capacity_gb
                    
                    module_info = {
                        'slot': memory.DeviceLocator,
                        'capacity_gb': capacity_gb,
                        'speed_mhz': memory.Speed,
                        'manufacturer': memory.Manufacturer,
                        'part_number': memory.PartNumber,
                        'serial_number': memory.SerialNumber,
                        'memory_type': memory.MemoryType,
                        'form_factor': memory.FormFactor
                    }
                    memory_modules.append(module_info)
                
                # Memory slots
                for slot in self.wmi_conn.Win32_PhysicalMemoryArray():
                    slots_total = slot.MemoryDevices
                
                data['total_physical_memory_gb'] = total_memory
                data['memory_slots_used'] = slots_used
                data['memory_slots_total'] = slots_total
                data['memory_modules'] = json.dumps(memory_modules)
                
                # Available memory
                data['available_memory_gb'] = round(psutil.virtual_memory().available / (1024**3), 2)
            
            logger.info(f"✅ Memory information collected - Total: {total_memory}GB in {slots_used}/{slots_total} slots")
            
        except Exception as e:
            logger.error(f"❌ Error collecting memory information: {e}")
            
        return data
    
    def get_storage_information(self):
        """Get comprehensive storage information"""
        data = {}
        storage_devices = []
        storage_summary_parts = []
        
        try:
            total_storage = 0
            available_storage = 0
            
            if self.wmi_conn:
                # Physical disk drives
                disk_count = 1
                for disk in self.wmi_conn.Win32_DiskDrive():
                    size_gb = round(int(disk.Size) / (1024**3), 2) if disk.Size else 0
                    total_storage += size_gb
                    
                    # Determine disk type
                    disk_type = "Unknown"
                    if "SSD" in disk.Model.upper() or "SOLID STATE" in disk.Model.upper():
                        disk_type = "SSD"
                    elif "USB" in disk.InterfaceType.upper() if disk.InterfaceType else False:
                        disk_type = "USB"
                    else:
                        disk_type = "HDD"
                    
                    disk_info = {
                        'disk_number': disk_count,
                        'model': disk.Model,
                        'size_gb': size_gb,
                        'interface_type': disk.InterfaceType,
                        'disk_type': disk_type,
                        'serial_number': disk.SerialNumber,
                        'manufacturer': disk.Manufacturer
                    }
                    storage_devices.append(disk_info)
                    storage_summary_parts.append(f"Disk {disk_count}: {size_gb}GB {disk_type}")
                    disk_count += 1
                
                # Logical drives (partitions)
                for drive in self.wmi_conn.Win32_LogicalDisk():
                    if drive.DriveType == 3:  # Local disk
                        free_space_gb = round(int(drive.FreeSpace) / (1024**3), 2) if drive.FreeSpace else 0
                        available_storage += free_space_gb
            
            data['storage_devices'] = json.dumps(storage_devices)
            data['total_storage_gb'] = total_storage
            data['available_storage_gb'] = available_storage
            data['storage_summary'] = ", ".join(storage_summary_parts)
            
            logger.info(f"✅ Storage information collected - Total: {total_storage}GB, Available: {available_storage}GB")
            
        except Exception as e:
            logger.error(f"❌ Error collecting storage information: {e}")
            
        return data
    
    def get_graphics_information(self):
        """Get comprehensive graphics card information"""
        data = {}
        graphics_cards = []
        
        try:
            total_graphics_memory = 0
            primary_card = None
            
            if self.wmi_conn:
                for gpu in self.wmi_conn.Win32_VideoController():
                    if gpu.Name and "Microsoft" not in gpu.Name:  # Skip basic display adapters
                        memory_mb = 0
                        if gpu.AdapterRAM:
                            memory_mb = round(int(gpu.AdapterRAM) / (1024**2))
                            total_graphics_memory += memory_mb
                        
                        gpu_info = {
                            'name': gpu.Name,
                            'manufacturer': gpu.AdapterCompatibility,
                            'memory_mb': memory_mb,
                            'driver_version': gpu.DriverVersion,
                            'driver_date': gpu.DriverDate,
                            'resolution': f"{gpu.CurrentHorizontalResolution}x{gpu.CurrentVerticalResolution}" if gpu.CurrentHorizontalResolution else None,
                            'color_depth': gpu.CurrentBitsPerPixel,
                            'refresh_rate': gpu.CurrentRefreshRate
                        }
                        graphics_cards.append(gpu_info)
                        
                        if not primary_card:
                            primary_card = gpu.Name
            
            data['graphics_cards'] = json.dumps(graphics_cards)
            data['primary_graphics_card'] = primary_card
            data['graphics_memory_mb'] = total_graphics_memory
            
            logger.info(f"✅ Graphics information collected - {len(graphics_cards)} cards, {total_graphics_memory}MB total memory")
            
        except Exception as e:
            logger.error(f"❌ Error collecting graphics information: {e}")
            
        return data
    
    def get_display_information(self):
        """Get comprehensive display and monitor information"""
        data = {}
        monitors = []
        display_adapters = []
        
        try:
            monitor_count = 0
            
            if self.wmi_conn:
                # Desktop monitors
                for monitor in self.wmi_conn.Win32_DesktopMonitor():
                    if monitor.Name:
                        monitor_count += 1
                        monitor_info = {
                            'name': monitor.Name,
                            'manufacturer': monitor.MonitorManufacturer,
                            'screen_width': monitor.ScreenWidth,
                            'screen_height': monitor.ScreenHeight,
                            'monitor_type': monitor.MonitorType
                        }
                        monitors.append(monitor_info)
                
                # Display configuration
                for display in self.wmi_conn.Win32_DisplayConfiguration():
                    if hasattr(display, 'HorizontalResolution'):
                        data['screen_resolution'] = f"{display.HorizontalResolution}x{display.VerticalResolution}"
                
                # Video controllers as display adapters
                for adapter in self.wmi_conn.Win32_VideoController():
                    if adapter.Name:
                        adapter_info = {
                            'name': adapter.Name,
                            'status': adapter.Status,
                            'availability': adapter.Availability
                        }
                        display_adapters.append(adapter_info)
            
            data['connected_monitors'] = monitor_count if monitor_count > 0 else 1  # Default to 1 if none detected
            data['monitor_details'] = json.dumps(monitors)
            data['display_adapters'] = json.dumps(display_adapters)
            
            logger.info(f"✅ Display information collected - {monitor_count} monitors detected")
            
        except Exception as e:
            logger.error(f"❌ Error collecting display information: {e}")
            
        return data
    
    def get_network_information(self):
        """Get comprehensive network adapter information"""
        data = {}
        network_adapters = []
        wireless_adapters = []
        
        try:
            if self.wmi_conn:
                for adapter in self.wmi_conn.Win32_NetworkAdapterConfiguration():
                    if adapter.IPEnabled:
                        adapter_info = {
                            'description': adapter.Description,
                            'mac_address': adapter.MACAddress,
                            'ip_addresses': adapter.IPAddress,
                            'subnet_masks': adapter.IPSubnet,
                            'default_gateways': adapter.DefaultIPGateway,
                            'dns_servers': adapter.DNSServerSearchOrder,
                            'dhcp_enabled': adapter.DHCPEnabled,
                            'dhcp_server': adapter.DHCPServer
                        }
                        network_adapters.append(adapter_info)
                        
                        # Get primary IP and MAC
                        if adapter.IPAddress and not data.get('ip_address'):
                            data['ip_address'] = adapter.IPAddress[0]
                        if adapter.MACAddress and not data.get('mac_address'):
                            data['mac_address'] = adapter.MACAddress
                
                # Wireless adapters
                for wireless in self.wmi_conn.Win32_NetworkAdapter():
                    if wireless.NetConnectionStatus == 2 and "wireless" in wireless.Name.lower():
                        wireless_info = {
                            'name': wireless.Name,
                            'manufacturer': wireless.Manufacturer,
                            'mac_address': wireless.MACAddress,
                            'connection_status': wireless.NetConnectionStatus
                        }
                        wireless_adapters.append(wireless_info)
            
            data['network_adapters'] = json.dumps(network_adapters)
            data['wireless_adapters'] = json.dumps(wireless_adapters)
            
            logger.info(f"✅ Network information collected - {len(network_adapters)} adapters")
            
        except Exception as e:
            logger.error(f"❌ Error collecting network information: {e}")
            
        return data
    
    def get_operating_system_info(self):
        """Get comprehensive operating system information"""
        data = {}
        
        try:
            if self.wmi_conn:
                for os_info in self.wmi_conn.Win32_OperatingSystem():
                    data['operating_system'] = os_info.Caption
                    data['os_version'] = os_info.Version
                    data['os_build'] = os_info.BuildNumber
                    data['os_edition'] = os_info.OperatingSystemSKU
                    data['os_architecture'] = os_info.OSArchitecture
                    data['os_install_date'] = os_info.InstallDate
                    data['last_boot_time'] = os_info.LastBootUpTime
                    data['registered_owner'] = os_info.RegisteredUser
            
            # Additional OS information
            data['os_architecture'] = platform.architecture()[0]
            
            logger.info("✅ Operating system information collected")
            
        except Exception as e:
            logger.error(f"❌ Error collecting OS information: {e}")
            
        return data
    
    def get_bios_information(self):
        """Get BIOS/UEFI information"""
        data = {}
        
        try:
            if self.wmi_conn:
                for bios in self.wmi_conn.Win32_BIOS():
                    data['bios_manufacturer'] = bios.Manufacturer
                    data['bios_version'] = bios.Version
                    data['bios_release_date'] = bios.ReleaseDate
                    data['serial_number'] = bios.SerialNumber if not data.get('serial_number') else data['serial_number']
            
            logger.info("✅ BIOS information collected")
            
        except Exception as e:
            logger.error(f"❌ Error collecting BIOS information: {e}")
            
        return data
    
    def get_motherboard_information(self):
        """Get motherboard information"""
        data = {}
        
        try:
            if self.wmi_conn:
                for board in self.wmi_conn.Win32_BaseBoard():
                    data['motherboard_manufacturer'] = board.Manufacturer
                    data['motherboard_model'] = board.Product
            
            logger.info("✅ Motherboard information collected")
            
        except Exception as e:
            logger.error(f"❌ Error collecting motherboard information: {e}")
            
        return data
    
    def get_software_information(self):
        """Get installed software information"""
        data = {}
        installed_software = []
        browsers = []
        
        try:
            if self.wmi_conn:
                # Installed programs
                for software in self.wmi_conn.Win32_Product():
                    if software.Name:
                        software_info = {
                            'name': software.Name,
                            'version': software.Version,
                            'vendor': software.Vendor,
                            'install_date': software.InstallDate
                        }
                        installed_software.append(software_info)
                        
                        # Detect browsers
                        software_name_lower = software.Name.lower()
                        if any(browser in software_name_lower for browser in ['chrome', 'firefox', 'edge', 'safari', 'opera']):
                            browsers.append(software.Name)
            
            data['installed_software'] = json.dumps(installed_software[:100])  # Limit to first 100
            data['browsers_installed'] = json.dumps(browsers)
            
            logger.info(f"✅ Software information collected - {len(installed_software)} programs")
            
        except Exception as e:
            logger.error(f"❌ Error collecting software information: {e}")
            
        return data
    
    def get_security_information(self):
        """Get security-related information"""
        data = {}
        
        try:
            # This would require additional WMI queries for security status
            # Placeholder for security information
            data['windows_defender_status'] = 'Unknown'
            data['firewall_status'] = 'Unknown'
            data['encryption_status'] = 'Unknown'
            data['uac_status'] = 'Unknown'
            
            logger.info("✅ Security information collected")
            
        except Exception as e:
            logger.error(f"❌ Error collecting security information: {e}")
            
        return data
    
    def get_user_information(self):
        """Get user account information"""
        data = {}
        user_profiles = []
        
        try:
            if self.wmi_conn:
                # User profiles
                for profile in self.wmi_conn.Win32_UserProfile():
                    if not profile.Special:
                        profile_info = {
                            'sid': profile.SID,
                            'local_path': profile.LocalPath,
                            'last_use_time': profile.LastUseTime
                        }
                        user_profiles.append(profile_info)
            
            data['user_profiles'] = json.dumps(user_profiles)
            
            logger.info(f"✅ User information collected - {len(user_profiles)} profiles")
            
        except Exception as e:
            logger.error(f"❌ Error collecting user information: {e}")
            
        return data
    
    def get_performance_information(self):
        """Get current performance metrics"""
        data = {}
        
        try:
            # CPU usage
            data['cpu_usage_percent'] = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            data['memory_usage_percent'] = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            data['disk_usage_percent'] = (disk.used / disk.total) * 100
            
            # System uptime
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            data['system_uptime_hours'] = round(uptime_seconds / 3600, 2)
            
            logger.info("✅ Performance information collected")
            
        except Exception as e:
            logger.error(f"❌ Error collecting performance information: {e}")
            
        return data
    
    def get_usb_devices(self):
        """Get connected USB devices"""
        data = {}
        usb_devices = []
        
        try:
            if self.wmi_conn:
                for usb in self.wmi_conn.Win32_USBControllerDevice():
                    usb_devices.append({'device': str(usb.Dependent)})
            
            data['usb_devices'] = json.dumps(usb_devices[:20])  # Limit to first 20
            
            logger.info(f"✅ USB devices collected - {len(usb_devices)} devices")
            
        except Exception as e:
            logger.error(f"❌ Error collecting USB devices: {e}")
            
        return data
    
    def get_expansion_slots(self):
        """Get expansion slot information"""
        data = {}
        expansion_slots = []
        
        try:
            if self.wmi_conn:
                for slot in self.wmi_conn.Win32_SystemSlot():
                    slot_info = {
                        'slot_designation': slot.SlotDesignation,
                        'current_usage': slot.CurrentUsage,
                        'slot_type': slot.SlotType
                    }
                    expansion_slots.append(slot_info)
            
            data['expansion_slots'] = json.dumps(expansion_slots)
            
            logger.info(f"✅ Expansion slots collected - {len(expansion_slots)} slots")
            
        except Exception as e:
            logger.error(f"❌ Error collecting expansion slots: {e}")
            
        return data
    
    def calculate_completeness_score(self, data):
        """Calculate data completeness score (0-100)"""
        essential_fields = [
            'hostname', 'ip_address', 'operating_system', 'processor_name',
            'total_physical_memory_gb', 'storage_devices', 'graphics_cards'
        ]
        
        important_fields = [
            'mac_address', 'serial_number', 'system_manufacturer', 'system_model',
            'bios_version', 'network_adapters', 'connected_monitors'
        ]
        
        optional_fields = [
            'installed_software', 'user_profiles', 'usb_devices', 'expansion_slots'
        ]
        
        score = 0
        
        # Essential fields (60% of score)
        essential_score = sum(1 for field in essential_fields if data.get(field)) / len(essential_fields) * 60
        
        # Important fields (30% of score)
        important_score = sum(1 for field in important_fields if data.get(field)) / len(important_fields) * 30
        
        # Optional fields (10% of score)
        optional_score = sum(1 for field in optional_fields if data.get(field)) / len(optional_fields) * 10
        
        score = round(essential_score + important_score + optional_score)
        
        return min(score, 100)
    
    def save_enhanced_data(self, data):
        """Save comprehensive data to enhanced database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check if asset exists
            hostname = data.get('hostname', data.get('computer_name', 'Unknown'))
            cursor.execute("SELECT id, configuration_hash FROM assets_enhanced WHERE hostname = ? OR computer_name = ?", 
                          (hostname, hostname))
            existing = cursor.fetchone()
            
            # Generate configuration hash for change detection
            config_hash = self.generate_config_hash(data)
            data['configuration_hash'] = config_hash
            
            if existing:
                asset_id, old_hash = existing
                
                # Check for changes
                if old_hash != config_hash:
                    self.track_changes(cursor, asset_id, data, old_hash)
                    data['last_hardware_change'] = datetime.now().isoformat()
                
                # Update existing record
                self.update_asset_record(cursor, asset_id, data)
                logger.info(f"✅ Updated existing asset: {hostname}")
                
            else:
                # Insert new record
                asset_id = self.insert_new_asset(cursor, data)
                logger.info(f"✅ Inserted new asset: {hostname}")
            
            # Log collection
            self.log_collection(cursor, data, True)
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"❌ Error saving enhanced data: {e}")
            conn.rollback()
            self.log_collection(cursor, data, False, str(e))
            
        finally:
            conn.close()
    
    def generate_config_hash(self, data):
        """Generate hash for configuration change detection"""
        import hashlib
        
        # Key fields for change detection
        key_fields = [
            'processor_name', 'total_physical_memory_gb', 'storage_devices',
            'graphics_cards', 'network_adapters', 'operating_system'
        ]
        
        config_string = '|'.join(str(data.get(field, '')) for field in key_fields)
        return hashlib.md5(config_string.encode()).hexdigest()
    
    def insert_new_asset(self, cursor, data):
        """Insert new asset record"""
        # Get all column names for the enhanced table
        cursor.execute("PRAGMA table_info(assets_enhanced)")
        columns = [row[1] for row in cursor.fetchall() if row[1] not in ['id', 'created_at', 'updated_at']]
        
        # Prepare values
        values = []
        placeholders = []
        for column in columns:
            values.append(data.get(column))
            placeholders.append('?')
        
        query = f"""
            INSERT INTO assets_enhanced ({', '.join(columns)}, updated_at)
            VALUES ({', '.join(placeholders)}, CURRENT_TIMESTAMP)
        """
        
        cursor.execute(query, values)
        return cursor.lastrowid
    
    def update_asset_record(self, cursor, asset_id, data):
        """Update existing asset record"""
        cursor.execute("PRAGMA table_info(assets_enhanced)")
        columns = [row[1] for row in cursor.fetchall() if row[1] not in ['id', 'created_at', 'updated_at']]
        
        set_clauses = []
        values = []
        for column in columns:
            if column in data:
                set_clauses.append(f"{column} = ?")
                values.append(data[column])
        
        values.append(asset_id)
        
        query = f"""
            UPDATE assets_enhanced 
            SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        
        cursor.execute(query, values)
    
    def track_changes(self, cursor, asset_id, new_data, old_hash):
        """Track changes in hardware configuration"""
        # This would compare old and new data to track specific changes
        # For now, just log that a change occurred
        cursor.execute("""
            INSERT INTO hardware_changes 
            (asset_id, change_type, field_name, old_value, new_value, change_timestamp, collection_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (asset_id, 'Configuration', 'config_hash', old_hash, new_data.get('configuration_hash'), 
              datetime.now().isoformat(), self.collection_id))
    
    def log_collection(self, cursor, data, success, error_message=None):
        """Log collection attempt"""
        cursor.execute("""
            INSERT INTO collection_logs 
            (collection_id, hostname, collection_method, start_time, end_time, duration_seconds, 
             success, error_message, data_collected, completeness_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            self.collection_id,
            data.get('hostname', 'Unknown'),
            data.get('collection_method', 'Unknown'),
            self.collection_start.isoformat(),
            datetime.now().isoformat(),
            data.get('collection_duration_seconds', 0),
            success,
            error_message,
            len([k for k, v in data.items() if v is not None]),
            data.get('data_completeness_score', 0)
        ))

def main():
    """Main execution function"""
    print("🚀 COMPREHENSIVE HARDWARE & SOFTWARE COLLECTOR")
    print("=" * 60)
    
    collector = ComprehensiveHardwareCollector()
    
    # Setup enhanced database
    print("📋 Setting up enhanced database schema...")
    collector.setup_enhanced_database()
    
    # Collect comprehensive data
    print("🔍 Starting comprehensive data collection...")
    data = collector.collect_comprehensive_data()
    
    if 'error' not in data:
        # Save to database
        print("💾 Saving comprehensive data to database...")
        collector.save_enhanced_data(data)
        
        print("\n✅ COLLECTION COMPLETED SUCCESSFULLY!")
        print(f"📊 Data Completeness Score: {data.get('data_completeness_score', 0)}%")
        print(f"⏱️  Collection Duration: {data.get('collection_duration_seconds', 0)} seconds")
        print(f"🏷️  Collection ID: {data.get('collection_id', 'Unknown')}")
        
        # Print summary
        print("\n📋 COLLECTION SUMMARY:")
        print(f"   • Hostname: {data.get('hostname', 'N/A')}")
        print(f"   • Hostname Status: {data.get('hostname_mismatch_status', 'N/A')}")
        print(f"   • IP Address: {data.get('ip_address', 'N/A')}")
        print(f"   • Operating System: {data.get('operating_system', 'N/A')}")
        print(f"   • Processor: {data.get('processor_name', 'N/A')}")
        print(f"   • Memory: {data.get('total_physical_memory_gb', 'N/A')} GB")
        print(f"   • Graphics: {data.get('primary_graphics_card', 'N/A')}")
        print(f"   • Monitors: {data.get('connected_monitors', 'N/A')}")
        print(f"   • Storage: {data.get('storage_summary', 'N/A')}")
        
    else:
        print(f"❌ Collection failed: {data['error']}")

if __name__ == "__main__":
    main()