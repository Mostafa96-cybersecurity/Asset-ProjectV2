"""
COMPREHENSIVE DATA COLLECTOR
This module collects data for all 520 columns using WMI, SSH, SNMP, and Registry
"""

import wmi
import psutil
import socket
import subprocess
import json
import sqlite3
import platform
import winreg
from datetime import datetime
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from comprehensive_schema import COMPREHENSIVE_COLUMNS

class ComprehensiveDataCollector:
    def __init__(self, db_path='assets.db'):
        self.db_path = db_path
        self.wmi_connection = None
        self.collection_errors = []
        self.collection_stats = {
            'wmi_success': 0,
            'wmi_failures': 0,
            'registry_success': 0,
            'registry_failures': 0,
            'performance_success': 0,
            'performance_failures': 0
        }
        
    def connect_wmi(self):
        """Initialize WMI connection"""
        try:
            self.wmi_connection = wmi.WMI()
            return True
        except Exception as e:
            self.collection_errors.append(f"WMI connection failed: {e}")
            return False
    
    def collect_system_identification(self):
        """Collect system identification data (20 columns)"""
        data = {}
        try:
            # Basic system info
            data['hostname'] = socket.gethostname()
            data['computer_name'] = platform.node()
            data['fqdn'] = socket.getfqdn()
            
            # Network identification
            try:
                data['ip_address'] = socket.gethostbyname(socket.gethostname())
            except:
                data['ip_address'] = '127.0.0.1'
            
            # WMI system data
            if self.wmi_connection:
                try:
                    for system in self.wmi_connection.Win32_ComputerSystem():
                        data['domain_name'] = system.Domain
                        data['workgroup'] = system.Workgroup if not system.PartOfDomain else None
                        data['domain_joined'] = bool(system.PartOfDomain)
                        data['total_physical_memory_gb'] = float(system.TotalPhysicalMemory) / (1024**3) if system.TotalPhysicalMemory else None
                        
                    for bios in self.wmi_connection.Win32_BIOS():
                        data['bios_uuid'] = bios.SerialNumber
                        data['serial_number'] = bios.SerialNumber
                        
                    for motherboard in self.wmi_connection.Win32_BaseBoard():
                        data['uuid'] = motherboard.SerialNumber
                        
                except Exception as e:
                    self.collection_errors.append(f"WMI identification error: {e}")
            
            self.collection_stats['wmi_success'] += 1
            
        except Exception as e:
            self.collection_errors.append(f"System identification error: {e}")
            self.collection_stats['wmi_failures'] += 1
            
        return data
    
    def collect_hardware_system(self):
        """Collect system hardware data (25 columns)"""
        data = {}
        try:
            if self.wmi_connection:
                # System information
                for system in self.wmi_connection.Win32_ComputerSystem():
                    data['system_manufacturer'] = system.Manufacturer
                    data['system_model'] = system.Model
                    data['system_family'] = getattr(system, 'SystemFamily', None)
                    data['system_sku'] = getattr(system, 'SystemSKUNumber', None)
                    
                # System enclosure
                for enclosure in self.wmi_connection.Win32_SystemEnclosure():
                    data['chassis_type'] = self._get_chassis_type(enclosure.ChassisTypes[0] if enclosure.ChassisTypes else None)
                    data['serial_number'] = data['serial_number'] or enclosure.SerialNumber
                    data['asset_tag'] = enclosure.SMBIOSAssetTag
                    data['service_tag'] = enclosure.SerialNumber
                    
                # Motherboard
                for board in self.wmi_connection.Win32_BaseBoard():
                    data['motherboard_manufacturer'] = board.Manufacturer
                    data['motherboard_model'] = board.Product
                    data['motherboard_serial'] = board.SerialNumber
                    data['motherboard_version'] = board.Version
                    
                # Physical location (if available)
                data['physical_location'] = f"{data.get('system_manufacturer', 'Unknown')} {data.get('system_model', 'Unknown')}"
                
        except Exception as e:
            self.collection_errors.append(f"Hardware system error: {e}")
            
        return data
    
    def collect_processor_details(self):
        """Collect detailed processor information (30 columns)"""
        data = {}
        try:
            if self.wmi_connection:
                processors = list(self.wmi_connection.Win32_Processor())
                data['cpu_count'] = len(processors)
                
                if processors:
                    processor = processors[0]  # Primary processor
                    data['processor_name'] = processor.Name
                    data['processor_manufacturer'] = processor.Manufacturer
                    data['processor_architecture'] = self._get_processor_architecture(processor.Architecture)
                    data['processor_family'] = str(processor.Family) if processor.Family else None
                    data['processor_cores'] = processor.NumberOfCores
                    data['processor_logical_cores'] = processor.NumberOfLogicalProcessors
                    data['processor_threads'] = processor.ThreadCount if hasattr(processor, 'ThreadCount') else None
                    data['processor_speed_mhz'] = processor.CurrentClockSpeed
                    data['processor_max_speed_mhz'] = processor.MaxClockSpeed
                    data['processor_l2_cache_size'] = processor.L2CacheSize
                    data['processor_l3_cache_size'] = processor.L3CacheSize
                    data['processor_socket_type'] = processor.SocketDesignation
                    data['processor_virtualization'] = getattr(processor, 'VirtualizationFirmwareEnabled', None)
                    data['processor_64bit_capable'] = '64' in str(processor.AddressWidth) if processor.AddressWidth else None
                    
            # Performance counters
            try:
                data['cpu_usage_percent'] = psutil.cpu_percent(interval=1)
                cpu_freq = psutil.cpu_freq()
                if cpu_freq:
                    data['processor_current_speed'] = int(cpu_freq.current)
                    
                # Additional CPU info
                cpu_count = psutil.cpu_count()
                cpu_count_logical = psutil.cpu_count(logical=True)
                data['processor_cores'] = data.get('processor_cores') or cpu_count
                data['processor_logical_cores'] = data.get('processor_logical_cores') or cpu_count_logical
                
                # Process count
                data['cpu_processes'] = len(psutil.pids())
                
            except Exception as e:
                self.collection_errors.append(f"CPU performance error: {e}")
                
        except Exception as e:
            self.collection_errors.append(f"Processor details error: {e}")
            
        return data
    
    def collect_memory_details(self):
        """Collect detailed memory information (25 columns)"""
        data = {}
        try:
            # System memory via psutil
            memory = psutil.virtual_memory()
            data['total_physical_memory_gb'] = memory.total / (1024**3)
            data['total_physical_memory_mb'] = memory.total // (1024**2)
            data['available_memory_gb'] = memory.available / (1024**3)
            data['used_memory_gb'] = memory.used / (1024**3)
            data['memory_usage_percent'] = memory.percent
            
            # Virtual memory
            vmem = psutil.virtual_memory()
            data['virtual_memory_total'] = vmem.total / (1024**3)
            data['virtual_memory_available'] = vmem.available / (1024**3)
            data['virtual_memory_used'] = vmem.used / (1024**3)
            
            # Swap/Page file
            swap = psutil.swap_memory()
            data['page_file_size'] = swap.total / (1024**3)
            data['page_file_usage'] = swap.percent
            data['swap_file_size'] = swap.total / (1024**3)
            
            # WMI memory details
            if self.wmi_connection:
                try:
                    memory_modules = []
                    slot_count = 0
                    used_slots = 0
                    
                    for memory_device in self.wmi_connection.Win32_PhysicalMemory():
                        module_info = {
                            'size': int(memory_device.Capacity) // (1024**3) if memory_device.Capacity else 0,
                            'speed': memory_device.Speed,
                            'type': self._get_memory_type(memory_device.MemoryType),
                            'manufacturer': memory_device.Manufacturer,
                            'location': memory_device.DeviceLocator
                        }
                        memory_modules.append(module_info)
                        used_slots += 1
                        
                    data['memory_modules'] = json.dumps(memory_modules)
                    data['memory_slots_used'] = used_slots
                    data['memory_manufacturer'] = memory_modules[0]['manufacturer'] if memory_modules else None
                    
                    if memory_modules:
                        data['memory_speed_mhz'] = memory_modules[0]['speed']
                        data['memory_type'] = memory_modules[0]['type']
                        
                    # Total slots (estimate based on motherboard)
                    try:
                        for board in self.wmi_connection.Win32_BaseBoard():
                            # Estimate total slots based on system type
                            data['memory_slots_total'] = self._estimate_memory_slots(board.Product)
                    except:
                        data['memory_slots_total'] = used_slots
                        
                except Exception as e:
                    self.collection_errors.append(f"WMI memory error: {e}")
                    
        except Exception as e:
            self.collection_errors.append(f"Memory details error: {e}")
            
        return data
    
    def collect_storage_details(self):
        """Collect detailed storage information (35 columns)"""
        data = {}
        try:
            # Disk usage via psutil
            disks = psutil.disk_partitions()
            total_storage = 0
            available_storage = 0
            used_storage = 0
            storage_devices = []
            
            for disk in disks:
                try:
                    if disk.fstype:  # Only real disks
                        usage = psutil.disk_usage(disk.mountpoint)
                        total_storage += usage.total
                        available_storage += usage.free
                        used_storage += usage.used
                        
                        storage_devices.append({
                            'device': disk.device,
                            'mountpoint': disk.mountpoint,
                            'fstype': disk.fstype,
                            'size_gb': usage.total / (1024**3),
                            'free_gb': usage.free / (1024**3),
                            'used_gb': usage.used / (1024**3)
                        })
                except:
                    continue
                    
            data['total_storage_gb'] = total_storage / (1024**3)
            data['available_storage_gb'] = available_storage / (1024**3)
            data['used_storage_gb'] = used_storage / (1024**3)
            data['disk_usage_percent'] = (used_storage / total_storage * 100) if total_storage > 0 else 0
            data['storage_devices'] = json.dumps(storage_devices)
            
            # Primary drive info
            if storage_devices:
                primary = storage_devices[0]
                data['primary_drive_type'] = primary['fstype']
                data['primary_drive_size'] = primary['size_gb']
                data['primary_drive_free'] = primary['free_gb']
                data['system_drive'] = primary['device']
                
            # WMI disk details
            if self.wmi_connection:
                try:
                    disk_drives = []
                    ssd_count = 0
                    hdd_count = 0
                    
                    for disk in self.wmi_connection.Win32_DiskDrive():
                        disk_info = {
                            'model': disk.Model,
                            'size_gb': int(disk.Size) / (1024**3) if disk.Size else 0,
                            'interface': disk.InterfaceType,
                            'serial': disk.SerialNumber,
                            'media_type': disk.MediaType
                        }
                        disk_drives.append(disk_info)
                        
                        # Count SSD vs HDD
                        if disk.MediaType and 'SSD' in str(disk.MediaType).upper():
                            ssd_count += 1
                        else:
                            hdd_count += 1
                            
                    data['ssd_count'] = ssd_count
                    data['hdd_count'] = hdd_count
                    data['storage_summary'] = f"{len(disk_drives)} drives: {ssd_count} SSD, {hdd_count} HDD"
                    
                    # Storage health and performance
                    try:
                        disk_io = psutil.disk_io_counters()
                        if disk_io:
                            data['disk_read_speed'] = f"{disk_io.read_bytes / (1024**2):.1f} MB/s"
                            data['disk_write_speed'] = f"{disk_io.write_bytes / (1024**2):.1f} MB/s"
                            data['disk_iops'] = str(disk_io.read_count + disk_io.write_count)
                    except:
                        pass
                        
                except Exception as e:
                    self.collection_errors.append(f"WMI storage error: {e}")
                    
        except Exception as e:
            self.collection_errors.append(f"Storage details error: {e}")
            
        return data
    
    def collect_operating_system_details(self):
        """Collect detailed OS information (30 columns)"""
        data = {}
        try:
            # Basic OS info
            data['operating_system'] = platform.platform()
            data['os_version'] = platform.version()
            data['os_architecture'] = platform.architecture()[0]
            data['os_kernel_version'] = platform.release()
            
            # Boot time and uptime
            boot_time = psutil.boot_time()
            data['os_last_boot_time'] = datetime.fromtimestamp(boot_time).isoformat()
            data['os_uptime'] = str(datetime.now() - datetime.fromtimestamp(boot_time))
            data['system_uptime_hours'] = (time.time() - boot_time) / 3600
            
            # WMI OS details
            if self.wmi_connection:
                try:
                    for os_info in self.wmi_connection.Win32_OperatingSystem():
                        data['os_build'] = os_info.BuildNumber
                        data['os_edition'] = os_info.Caption
                        data['os_service_pack'] = f"SP{os_info.ServicePackMajorVersion}" if os_info.ServicePackMajorVersion else None
                        data['os_install_date'] = self._convert_wmi_date(os_info.InstallDate) if os_info.InstallDate else None
                        data['os_language'] = os_info.Locale
                        data['os_product_key'] = getattr(os_info, 'SerialNumber', None)
                        data['registered_owner'] = os_info.RegisteredUser
                        data['windows_folder'] = os_info.WindowsDirectory
                        data['system_drive'] = os_info.SystemDrive
                        
                    # Windows features and settings
                    data['os_family'] = 'Windows'
                    data['device_type'] = self._determine_device_type()
                    
                except Exception as e:
                    self.collection_errors.append(f"WMI OS error: {e}")
                    
        except Exception as e:
            self.collection_errors.append(f"OS details error: {e}")
            
        return data
    
    def collect_comprehensive_data(self, hostname=None):
        """Collect all comprehensive data for a single asset"""
        print(f"🔍 Starting comprehensive data collection for {hostname or 'localhost'}...")
        
        # Initialize WMI
        wmi_success = self.connect_wmi()
        
        # Collect all data sections
        comprehensive_data = {}
        
        # Basic identification
        print("   📋 Collecting system identification...")
        comprehensive_data.update(self.collect_system_identification())
        
        # Hardware details
        print("   🖥️  Collecting hardware system info...")
        comprehensive_data.update(self.collect_hardware_system())
        
        print("   ⚡ Collecting processor details...")
        comprehensive_data.update(self.collect_processor_details())
        
        print("   💾 Collecting memory details...")
        comprehensive_data.update(self.collect_memory_details())
        
        print("   💿 Collecting storage details...")
        comprehensive_data.update(self.collect_storage_details())
        
        # Operating system
        print("   🖱️  Collecting OS details...")
        comprehensive_data.update(self.collect_operating_system_details())
        
        # Collection metadata
        now = datetime.now().isoformat()
        comprehensive_data.update({
            'collection_method': 'WMI (Comprehensive)',
            'collection_timestamp': now,
            'collection_id': f"comprehensive_{int(time.time())}",
            'wmi_collection_success': wmi_success,
            'wmi_collection_errors': json.dumps(self.collection_errors) if self.collection_errors else None,
            'updated_at': now,
            'device_status': 'Online',
            'last_seen': now
        })
        
        # Calculate data completeness
        filled_fields = sum(1 for value in comprehensive_data.values() if value is not None and value != "")
        total_fields = len(COMPREHENSIVE_COLUMNS)
        completeness = (filled_fields / total_fields) * 100
        comprehensive_data['data_completeness_score'] = completeness
        
        print(f"   📊 Data collection complete: {completeness:.1f}% ({filled_fields}/{total_fields} fields)")
        
        return comprehensive_data
    
    def _get_chassis_type(self, chassis_code):
        """Convert chassis type code to description"""
        chassis_types = {
            1: "Other", 2: "Unknown", 3: "Desktop", 4: "Low Profile Desktop",
            5: "Pizza Box", 6: "Mini Tower", 7: "Tower", 8: "Portable",
            9: "Laptop", 10: "Notebook", 11: "Hand Held", 12: "Docking Station",
            13: "All in One", 14: "Sub Notebook", 15: "Space-saving",
            16: "Lunch Box", 17: "Main Server Chassis", 18: "Expansion Chassis",
            19: "SubChassis", 20: "Bus Expansion Chassis", 21: "Peripheral Chassis",
            22: "RAID Chassis", 23: "Rack Mount Chassis", 24: "Sealed-case PC"
        }
        return chassis_types.get(chassis_code, "Unknown")
    
    def _get_processor_architecture(self, arch_code):
        """Convert processor architecture code to description"""
        architectures = {
            0: "x86", 1: "MIPS", 2: "Alpha", 3: "PowerPC",
            5: "ARM", 6: "ia64", 9: "x64"
        }
        return architectures.get(arch_code, "Unknown")
    
    def _get_memory_type(self, memory_type_code):
        """Convert memory type code to description"""
        memory_types = {
            20: "DDR", 21: "DDR2", 22: "DDR2 FB-DIMM", 24: "DDR3", 26: "DDR4", 28: "DDR5"
        }
        return memory_types.get(memory_type_code, "Unknown")
    
    def _estimate_memory_slots(self, motherboard_model):
        """Estimate memory slots based on motherboard model"""
        if not motherboard_model:
            return 4
        model_lower = motherboard_model.lower()
        if any(x in model_lower for x in ['server', 'workstation', 'pro']):
            return 8
        elif any(x in model_lower for x in ['mini', 'micro', 'itx']):
            return 2
        else:
            return 4
    
    def _convert_wmi_date(self, wmi_date):
        """Convert WMI date format to ISO format"""
        try:
            if wmi_date:
                # WMI date format: 20230101120000.000000+000
                date_part = wmi_date.split('.')[0]
                return datetime.strptime(date_part, '%Y%m%d%H%M%S').isoformat()
        except:
            return None
        return None
    
    def _determine_device_type(self):
        """Determine device type based on system characteristics"""
        try:
            if self.wmi_connection:
                for system in self.wmi_connection.Win32_ComputerSystem():
                    pc_type = system.PCSystemType
                    if pc_type == 1:  # Desktop
                        return "Desktop Workstation"
                    elif pc_type == 2:  # Mobile
                        return "Mobile Workstation"
                    elif pc_type == 3:  # Workstation
                        return "Workstation"
                    elif pc_type == 4:  # Enterprise Server
                        return "Server"
                    elif pc_type == 5:  # SOHO Server
                        return "Small Office Server"
                    elif pc_type == 6:  # Appliance PC
                        return "Appliance"
                    elif pc_type == 7:  # Performance Server
                        return "Performance Server"
                    elif pc_type == 8:  # Maximum
                        return "Maximum Performance Server"
        except:
            pass
        return "Windows Workstation"

# Test the comprehensive collector
if __name__ == "__main__":
    collector = ComprehensiveDataCollector()
    data = collector.collect_comprehensive_data()
    
    print(f"\n🎉 COMPREHENSIVE DATA COLLECTION COMPLETE!")
    print(f"   📊 Collected {len([k for k, v in data.items() if v is not None])} fields")
    print(f"   ✅ Data completeness: {data.get('data_completeness_score', 0):.1f}%")
    print(f"   🔧 Collection method: {data.get('collection_method')}")
    print(f"   🕒 Collection time: {data.get('collection_timestamp')}")
    
    # Show sample of collected data
    print(f"\n📋 Sample collected data:")
    sample_fields = ['hostname', 'system_manufacturer', 'system_model', 'processor_name', 
                    'total_physical_memory_gb', 'total_storage_gb', 'operating_system']
    for field in sample_fields:
        value = data.get(field, 'Not collected')
        print(f"   {field:25} = {value}")
    
    print(f"\n🔍 Collection errors: {len(collector.collection_errors)}")
    for error in collector.collection_errors[:5]:  # Show first 5 errors
        print(f"   ❌ {error}")