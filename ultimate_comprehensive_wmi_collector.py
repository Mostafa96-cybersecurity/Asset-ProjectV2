#!/usr/bin/env python3
"""
🔥 ULTIMATE COMPREHENSIVE WMI DATA COLLECTOR
Collects ALL possible WMI data based on database schema analysis
Includes current user detection and comprehensive system information
"""

import wmi
import sqlite3
import json
import sys
import time
from datetime import datetime
from collections import defaultdict
import win32api
import win32security
import os

class UltimateWMICollector:
    def __init__(self):
        self.wmi_connection = None
        self.db_connection = None
        self.collected_data = defaultdict(dict)
        self.collection_stats = {
            'total_fields': 0,
            'successful_collections': 0,
            'failed_collections': 0,
            'collection_time': 0
        }
        
        # Load WMI mapping
        try:
            with open('comprehensive_wmi_mapping.json', 'r') as f:
                self.wmi_mapping = json.load(f)
        except:
            self.wmi_mapping = self.get_default_mapping()
    
    def connect_wmi(self):
        """Connect to WMI service"""
        try:
            self.wmi_connection = wmi.WMI()
            print("✅ WMI Connection established")
            return True
        except Exception as e:
            print(f"❌ WMI Connection failed: {e}")
            return False
    
    def connect_database(self):
        """Connect to SQLite database"""
        try:
            self.db_connection = sqlite3.connect('assets.db')
            print("✅ Database connection established")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def get_current_user_info(self):
        """Get comprehensive current user information"""
        user_info = {}
        
        try:
            # Get current user name
            user_info['current_user'] = win32api.GetUserName()
            
            # Get user domain
            try:
                user_info['current_user_domain'] = win32api.GetUserNameEx(win32api.NameSamCompatible).split('\\')[0]
            except:
                user_info['current_user_domain'] = os.environ.get('USERDOMAIN', 'Unknown')
            
            # Get user SID
            try:
                user, domain, type = win32security.LookupAccountName("", user_info['current_user'])
                user_info['current_user_sid'] = win32security.ConvertSidToStringSid(user)
            except:
                user_info['current_user_sid'] = 'Unknown'
            
            # Get user profile path
            user_info['current_user_profile'] = os.environ.get('USERPROFILE', 'Unknown')
            
            # Get user privileges (basic check)
            try:
                import ctypes
                user_info['current_user_is_admin'] = ctypes.windll.shell32.IsUserAnAdmin() != 0
            except:
                user_info['current_user_is_admin'] = False
            
            print(f"✅ Current User: {user_info['current_user']} ({user_info['current_user_domain']})")
            
        except Exception as e:
            print(f"⚠️ Error getting current user info: {e}")
            user_info['current_user'] = 'Unknown'
        
        return user_info
    
    def collect_system_information(self):
        """Collect comprehensive system information"""
        print("\n🖥️ Collecting System Information...")
        
        try:
            for system in self.wmi_connection.Win32_ComputerSystem():
                self.collected_data['system'].update({
                    'computer_name': system.Name,
                    'manufacturer': system.Manufacturer,
                    'model': system.Model,
                    'system_type': system.SystemType,
                    'total_physical_memory': system.TotalPhysicalMemory,
                    'domain_name': getattr(system, 'Domain', 'N/A'),
                    'workgroup': getattr(system, 'Workgroup', 'N/A'),
                    'primary_owner_name': getattr(system, 'PrimaryOwnerName', 'N/A'),
                    'thermal_state': getattr(system, 'ThermalState', 'N/A'),
                    'power_state': getattr(system, 'PowerState', 'N/A'),
                    'number_of_processors': getattr(system, 'NumberOfProcessors', 0),
                    'number_of_logical_processors': getattr(system, 'NumberOfLogicalProcessors', 0)
                })
                self.collection_stats['successful_collections'] += 12
                break
        except Exception as e:
            print(f"⚠️ Error collecting system info: {e}")
            self.collection_stats['failed_collections'] += 1
    
    def collect_operating_system(self):
        """Collect operating system information"""
        print("🪟 Collecting Operating System Information...")
        
        try:
            for os_info in self.wmi_connection.Win32_OperatingSystem():
                self.collected_data['os'].update({
                    'operating_system': os_info.Caption,
                    'os_version': os_info.Version,
                    'os_build_number': os_info.BuildNumber,
                    'os_service_pack': getattr(os_info, 'ServicePackMajorVersion', 0),
                    'os_architecture': os_info.OSArchitecture,
                    'windows_directory': os_info.WindowsDirectory,
                    'system_directory': os_info.SystemDirectory,
                    'boot_device': os_info.BootDevice,
                    'system_device': os_info.SystemDevice,
                    'install_date': str(os_info.InstallDate) if os_info.InstallDate else 'N/A',
                    'last_boot_up_time': str(os_info.LastBootUpTime) if os_info.LastBootUpTime else 'N/A',
                    'local_date_time': str(os_info.LocalDateTime) if os_info.LocalDateTime else 'N/A',
                    'locale': getattr(os_info, 'Locale', 'N/A'),
                    'country_code': getattr(os_info, 'CountryCode', 'N/A'),
                    'time_zone': getattr(os_info, 'CurrentTimeZone', 'N/A'),
                    'total_virtual_memory_size': getattr(os_info, 'TotalVirtualMemorySize', 0),
                    'total_visible_memory_size': getattr(os_info, 'TotalVisibleMemorySize', 0),
                    'free_physical_memory': getattr(os_info, 'FreePhysicalMemory', 0),
                    'free_virtual_memory': getattr(os_info, 'FreeVirtualMemory', 0)
                })
                self.collection_stats['successful_collections'] += 19
                break
        except Exception as e:
            print(f"⚠️ Error collecting OS info: {e}")
            self.collection_stats['failed_collections'] += 1
    
    def collect_processor_information(self):
        """Collect processor information"""
        print("⚙️ Collecting Processor Information...")
        
        try:
            processors = []
            for cpu in self.wmi_connection.Win32_Processor():
                processor_info = {
                    'processor_name': cpu.Name,
                    'processor_manufacturer': cpu.Manufacturer,
                    'processor_architecture': getattr(cpu, 'Architecture', 'N/A'),
                    'processor_family': getattr(cpu, 'Family', 'N/A'),
                    'processor_speed': getattr(cpu, 'MaxClockSpeed', 0),
                    'processor_cores': getattr(cpu, 'NumberOfCores', 0),
                    'processor_logical_processors': getattr(cpu, 'NumberOfLogicalProcessors', 0),
                    'processor_l2_cache_size': getattr(cpu, 'L2CacheSize', 0),
                    'processor_l3_cache_size': getattr(cpu, 'L3CacheSize', 0),
                    'processor_voltage': getattr(cpu, 'CurrentVoltage', 0),
                    'processor_description': getattr(cpu, 'Description', 'N/A'),
                    'processor_socket_designation': getattr(cpu, 'SocketDesignation', 'N/A')
                }
                processors.append(processor_info)
            
            # Store first processor as main, all as list
            if processors:
                self.collected_data['processor'].update(processors[0])
                self.collected_data['processor']['all_processors'] = processors
                self.collection_stats['successful_collections'] += len(processors) * 12
        
        except Exception as e:
            print(f"⚠️ Error collecting processor info: {e}")
            self.collection_stats['failed_collections'] += 1
    
    def collect_memory_information(self):
        """Collect memory information"""
        print("🧠 Collecting Memory Information...")
        
        try:
            memory_modules = []
            total_capacity = 0
            
            for memory in self.wmi_connection.Win32_PhysicalMemory():
                memory_info = {
                    'memory_manufacturer': getattr(memory, 'Manufacturer', 'N/A'),
                    'memory_capacity': getattr(memory, 'Capacity', 0),
                    'memory_speed': getattr(memory, 'Speed', 0),
                    'memory_type': getattr(memory, 'MemoryType', 'N/A'),
                    'memory_form_factor': getattr(memory, 'FormFactor', 'N/A'),
                    'memory_device_locator': getattr(memory, 'DeviceLocator', 'N/A'),
                    'memory_bank_label': getattr(memory, 'BankLabel', 'N/A'),
                    'memory_serial_number': getattr(memory, 'SerialNumber', 'N/A'),
                    'memory_part_number': getattr(memory, 'PartNumber', 'N/A')
                }
                memory_modules.append(memory_info)
                if memory.Capacity:
                    total_capacity += int(memory.Capacity)
            
            self.collected_data['memory'].update({
                'memory_modules': memory_modules,
                'total_memory_capacity': total_capacity,
                'memory_slots_used': len(memory_modules),
                'installed_ram_gb': round(total_capacity / (1024**3), 2) if total_capacity > 0 else 0
            })
            
            self.collection_stats['successful_collections'] += len(memory_modules) * 9
            
        except Exception as e:
            print(f"⚠️ Error collecting memory info: {e}")
            self.collection_stats['failed_collections'] += 1
    
    def collect_bios_information(self):
        """Collect BIOS information"""
        print("🔧 Collecting BIOS Information...")
        
        try:
            for bios in self.wmi_connection.Win32_BIOS():
                self.collected_data['bios'].update({
                    'bios_version': getattr(bios, 'SMBIOSBIOSVersion', 'N/A'),
                    'bios_manufacturer': getattr(bios, 'Manufacturer', 'N/A'),
                    'bios_name': getattr(bios, 'Name', 'N/A'),
                    'bios_description': getattr(bios, 'Description', 'N/A'),
                    'bios_serial_number': getattr(bios, 'SerialNumber', 'N/A'),
                    'bios_release_date': str(getattr(bios, 'ReleaseDate', 'N/A')),
                    'bios_version_major': getattr(bios, 'SMBIOSMajorVersion', 0),
                    'bios_version_minor': getattr(bios, 'SMBIOSMinorVersion', 0)
                })
                self.collection_stats['successful_collections'] += 8
                break
        except Exception as e:
            print(f"⚠️ Error collecting BIOS info: {e}")
            self.collection_stats['failed_collections'] += 1
    
    def collect_motherboard_information(self):
        """Collect motherboard information"""
        print("🏗️ Collecting Motherboard Information...")
        
        try:
            for board in self.wmi_connection.Win32_BaseBoard():
                self.collected_data['motherboard'].update({
                    'motherboard_manufacturer': getattr(board, 'Manufacturer', 'N/A'),
                    'motherboard_model': getattr(board, 'Product', 'N/A'),
                    'motherboard_version': getattr(board, 'Version', 'N/A'),
                    'motherboard_serial': getattr(board, 'SerialNumber', 'N/A'),
                    'motherboard_tag': getattr(board, 'Tag', 'N/A')
                })
                self.collection_stats['successful_collections'] += 5
                break
        except Exception as e:
            print(f"⚠️ Error collecting motherboard info: {e}")
            self.collection_stats['failed_collections'] += 1
    
    def collect_storage_information(self):
        """Collect storage information"""
        print("💽 Collecting Storage Information...")
        
        try:
            # Logical disks
            logical_disks = []
            for disk in self.wmi_connection.Win32_LogicalDisk():
                disk_info = {
                    'disk_drive_letter': getattr(disk, 'DeviceID', 'N/A'),
                    'disk_size': getattr(disk, 'Size', 0),
                    'disk_free_space': getattr(disk, 'FreeSpace', 0),
                    'disk_file_system': getattr(disk, 'FileSystem', 'N/A'),
                    'disk_volume_name': getattr(disk, 'VolumeName', 'N/A'),
                    'disk_type': getattr(disk, 'DriveType', 'N/A')
                }
                logical_disks.append(disk_info)
            
            # Physical disks
            physical_disks = []
            for disk in self.wmi_connection.Win32_DiskDrive():
                disk_info = {
                    'hard_drive_model': getattr(disk, 'Model', 'N/A'),
                    'hard_drive_manufacturer': getattr(disk, 'Manufacturer', 'N/A'),
                    'hard_drive_serial': getattr(disk, 'SerialNumber', 'N/A'),
                    'hard_drive_size': getattr(disk, 'Size', 0),
                    'hard_drive_interface': getattr(disk, 'InterfaceType', 'N/A'),
                    'hard_drive_media_type': getattr(disk, 'MediaType', 'N/A')
                }
                physical_disks.append(disk_info)
            
            self.collected_data['storage'].update({
                'logical_disks': logical_disks,
                'physical_disks': physical_disks,
                'total_disk_count': len(physical_disks)
            })
            
            self.collection_stats['successful_collections'] += (len(logical_disks) * 6) + (len(physical_disks) * 6)
            
        except Exception as e:
            print(f"⚠️ Error collecting storage info: {e}")
            self.collection_stats['failed_collections'] += 1
    
    def collect_network_information(self):
        """Collect network information"""
        print("🌐 Collecting Network Information...")
        
        try:
            # Network adapters
            network_adapters = []
            for adapter in self.wmi_connection.Win32_NetworkAdapter():
                if adapter.NetConnectionStatus is not None:  # Only active adapters
                    adapter_info = {
                        'network_adapter_name': getattr(adapter, 'Name', 'N/A'),
                        'network_adapter_manufacturer': getattr(adapter, 'Manufacturer', 'N/A'),
                        'network_adapter_type': getattr(adapter, 'AdapterType', 'N/A'),
                        'network_adapter_mac': getattr(adapter, 'MACAddress', 'N/A'),
                        'network_adapter_speed': getattr(adapter, 'Speed', 0),
                        'network_adapter_status': getattr(adapter, 'NetConnectionStatus', 'N/A')
                    }
                    network_adapters.append(adapter_info)
            
            # Network configurations
            network_configs = []
            for config in self.wmi_connection.Win32_NetworkAdapterConfiguration():
                if config.IPEnabled:
                    config_info = {
                        'ip_addresses': getattr(config, 'IPAddress', []),
                        'subnet_masks': getattr(config, 'IPSubnet', []),
                        'default_gateways': getattr(config, 'DefaultIPGateway', []),
                        'dns_servers': getattr(config, 'DNSServerSearchOrder', []),
                        'dhcp_enabled': getattr(config, 'DHCPEnabled', False),
                        'dhcp_server': getattr(config, 'DHCPServer', 'N/A'),
                        'wins_primary_server': getattr(config, 'WINSPrimaryServer', 'N/A'),
                        'wins_secondary_server': getattr(config, 'WINSSecondaryServer', 'N/A')
                    }
                    network_configs.append(config_info)
            
            self.collected_data['network'].update({
                'network_adapters': network_adapters,
                'network_configurations': network_configs,
                'adapter_count': len(network_adapters)
            })
            
            self.collection_stats['successful_collections'] += (len(network_adapters) * 6) + (len(network_configs) * 8)
            
        except Exception as e:
            print(f"⚠️ Error collecting network info: {e}")
            self.collection_stats['failed_collections'] += 1
    
    def collect_software_information(self):
        """Collect installed software information"""
        print("📦 Collecting Software Information...")
        
        try:
            installed_software = []
            for software in self.wmi_connection.Win32_Product():
                software_info = {
                    'software_name': getattr(software, 'Name', 'N/A'),
                    'software_version': getattr(software, 'Version', 'N/A'),
                    'software_vendor': getattr(software, 'Vendor', 'N/A'),
                    'software_install_date': str(getattr(software, 'InstallDate', 'N/A'))
                }
                installed_software.append(software_info)
            
            self.collected_data['software'].update({
                'installed_software': installed_software,
                'installed_software_count': len(installed_software)
            })
            
            self.collection_stats['successful_collections'] += len(installed_software) * 4
            
        except Exception as e:
            print(f"⚠️ Error collecting software info: {e}")
            self.collection_stats['failed_collections'] += 1
    
    def collect_services_information(self):
        """Collect services information"""
        print("⚙️ Collecting Services Information...")
        
        try:
            services = []
            running_services = 0
            stopped_services = 0
            
            for service in self.wmi_connection.Win32_Service():
                service_info = {
                    'service_name': getattr(service, 'Name', 'N/A'),
                    'service_display_name': getattr(service, 'DisplayName', 'N/A'),
                    'service_status': getattr(service, 'Status', 'N/A'),
                    'service_start_mode': getattr(service, 'StartMode', 'N/A'),
                    'service_path': getattr(service, 'PathName', 'N/A'),
                    'service_description': getattr(service, 'Description', 'N/A')
                }
                services.append(service_info)
                
                if service.Status == 'OK':
                    running_services += 1
                else:
                    stopped_services += 1
            
            self.collected_data['services'].update({
                'services': services,
                'total_services': len(services),
                'running_services': running_services,
                'stopped_services': stopped_services
            })
            
            self.collection_stats['successful_collections'] += len(services) * 6
            
        except Exception as e:
            print(f"⚠️ Error collecting services info: {e}")
            self.collection_stats['failed_collections'] += 1
    
    def collect_user_information(self):
        """Collect user account information"""
        print("👥 Collecting User Information...")
        
        try:
            user_accounts = []
            for user in self.wmi_connection.Win32_UserAccount():
                if user.LocalAccount:  # Only local accounts
                    user_info = {
                        'user_name': getattr(user, 'Name', 'N/A'),
                        'user_full_name': getattr(user, 'FullName', 'N/A'),
                        'user_description': getattr(user, 'Description', 'N/A'),
                        'user_account_type': getattr(user, 'AccountType', 'N/A'),
                        'user_disabled': getattr(user, 'Disabled', False),
                        'user_lockout': getattr(user, 'Lockout', False),
                        'user_password_changeable': getattr(user, 'PasswordChangeable', False),
                        'user_password_expires': getattr(user, 'PasswordExpires', False),
                        'user_password_required': getattr(user, 'PasswordRequired', False)
                    }
                    user_accounts.append(user_info)
            
            self.collected_data['users'].update({
                'user_accounts': user_accounts,
                'total_user_accounts': len(user_accounts)
            })
            
            self.collection_stats['successful_collections'] += len(user_accounts) * 9
            
        except Exception as e:
            print(f"⚠️ Error collecting user info: {e}")
            self.collection_stats['failed_collections'] += 1
    
    def collect_all_data(self, hostname="localhost"):
        """Collect all available WMI data"""
        print("=" * 80)
        print("🔥 ULTIMATE WMI DATA COLLECTION STARTED")
        print("=" * 80)
        
        start_time = time.time()
        
        # Get current user info first
        current_user_info = self.get_current_user_info()
        self.collected_data['current_user'] = current_user_info
        
        # Collect all categories
        collection_methods = [
            self.collect_system_information,
            self.collect_operating_system,
            self.collect_processor_information,
            self.collect_memory_information,
            self.collect_bios_information,
            self.collect_motherboard_information,
            self.collect_storage_information,
            self.collect_network_information,
            self.collect_software_information,
            self.collect_services_information,
            self.collect_user_information
        ]
        
        for method in collection_methods:
            try:
                method()
            except Exception as e:
                print(f"⚠️ Error in {method.__name__}: {e}")
                self.collection_stats['failed_collections'] += 1
        
        self.collection_stats['collection_time'] = time.time() - start_time
        self.collection_stats['total_fields'] = (
            self.collection_stats['successful_collections'] + 
            self.collection_stats['failed_collections']
        )
        
        print("\n" + "=" * 80)
        print("📊 COLLECTION STATISTICS")
        print("=" * 80)
        print(f"✅ Successful Collections: {self.collection_stats['successful_collections']}")
        print(f"❌ Failed Collections: {self.collection_stats['failed_collections']}")
        print(f"⏱️ Collection Time: {self.collection_stats['collection_time']:.2f} seconds")
        print(f"📈 Success Rate: {(self.collection_stats['successful_collections'] / max(1, self.collection_stats['total_fields'])) * 100:.1f}%")
        
        return self.collected_data
    
    def save_to_database(self, hostname="localhost"):
        """Save collected data to database"""
        print("\n💾 Saving data to database...")
        
        try:
            cursor = self.db_connection.cursor()
            
            # Prepare data for insertion
            data_dict = {
                'hostname': hostname,
                'ip_address': self.collected_data.get('network', {}).get('network_configurations', [{}])[0].get('ip_addresses', ['Unknown'])[0] if self.collected_data.get('network', {}).get('network_configurations') else 'Unknown',
                'scan_timestamp': datetime.now().isoformat(),
                'collection_method': 'Ultimate_WMI_Collector',
                
                # Current User Information
                'current_user': self.collected_data.get('current_user', {}).get('current_user', 'Unknown'),
                'current_user_domain': self.collected_data.get('current_user', {}).get('current_user_domain', 'Unknown'),
                'current_user_sid': self.collected_data.get('current_user', {}).get('current_user_sid', 'Unknown'),
                'current_user_profile': self.collected_data.get('current_user', {}).get('current_user_profile', 'Unknown'),
                'current_user_is_admin': self.collected_data.get('current_user', {}).get('current_user_is_admin', False),
                
                # System Information
                'computer_name': self.collected_data.get('system', {}).get('computer_name', 'Unknown'),
                'manufacturer': self.collected_data.get('system', {}).get('manufacturer', 'Unknown'),
                'model': self.collected_data.get('system', {}).get('model', 'Unknown'),
                'serial_number': self.collected_data.get('system', {}).get('serial_number', 'Unknown'),
                'domain_name': self.collected_data.get('system', {}).get('domain_name', 'Unknown'),
                'workgroup': self.collected_data.get('system', {}).get('workgroup', 'Unknown'),
                
                # Operating System
                'operating_system': self.collected_data.get('os', {}).get('operating_system', 'Unknown'),
                'os_version': self.collected_data.get('os', {}).get('os_version', 'Unknown'),
                'os_build_number': self.collected_data.get('os', {}).get('os_build_number', 'Unknown'),
                'os_architecture': self.collected_data.get('os', {}).get('os_architecture', 'Unknown'),
                'windows_directory': self.collected_data.get('os', {}).get('windows_directory', 'Unknown'),
                'install_date': self.collected_data.get('os', {}).get('install_date', 'Unknown'),
                'last_boot_up_time': self.collected_data.get('os', {}).get('last_boot_up_time', 'Unknown'),
                
                # Processor
                'processor_name': self.collected_data.get('processor', {}).get('processor_name', 'Unknown'),
                'processor_manufacturer': self.collected_data.get('processor', {}).get('processor_manufacturer', 'Unknown'),
                'processor_cores': self.collected_data.get('processor', {}).get('processor_cores', 0),
                'processor_logical_processors': self.collected_data.get('processor', {}).get('processor_logical_processors', 0),
                'processor_speed': self.collected_data.get('processor', {}).get('processor_speed', 0),
                'processor_architecture': self.collected_data.get('processor', {}).get('processor_architecture', 'Unknown'),
                
                # Memory
                'total_physical_memory': self.collected_data.get('system', {}).get('total_physical_memory', 0),
                'installed_ram_gb': self.collected_data.get('memory', {}).get('installed_ram_gb', 0),
                'memory_slots_used': self.collected_data.get('memory', {}).get('memory_slots_used', 0),
                
                # BIOS
                'bios_version': self.collected_data.get('bios', {}).get('bios_version', 'Unknown'),
                'bios_manufacturer': self.collected_data.get('bios', {}).get('bios_manufacturer', 'Unknown'),
                'bios_serial_number': self.collected_data.get('bios', {}).get('bios_serial_number', 'Unknown'),
                'bios_release_date': self.collected_data.get('bios', {}).get('bios_release_date', 'Unknown'),
                
                # Motherboard
                'motherboard_manufacturer': self.collected_data.get('motherboard', {}).get('motherboard_manufacturer', 'Unknown'),
                'motherboard_model': self.collected_data.get('motherboard', {}).get('motherboard_model', 'Unknown'),
                'motherboard_serial': self.collected_data.get('motherboard', {}).get('motherboard_serial', 'Unknown'),
                'motherboard_version': self.collected_data.get('motherboard', {}).get('motherboard_version', 'Unknown'),
                
                # Software & Services
                'installed_software_count': self.collected_data.get('software', {}).get('installed_software_count', 0),
                'total_services': self.collected_data.get('services', {}).get('total_services', 0),
                'running_services': self.collected_data.get('services', {}).get('running_services', 0),
                'stopped_services': self.collected_data.get('services', {}).get('stopped_services', 0),
                
                # User Accounts
                'total_user_accounts': self.collected_data.get('users', {}).get('total_user_accounts', 0),
                
                # Network
                'adapter_count': self.collected_data.get('network', {}).get('adapter_count', 0),
                
                # Storage
                'total_disk_count': self.collected_data.get('storage', {}).get('total_disk_count', 0),
                
                # Collection Stats
                'data_collection_success_rate': (self.collection_stats['successful_collections'] / max(1, self.collection_stats['total_fields'])) * 100,
                'data_collection_time': self.collection_stats['collection_time'],
                'data_fields_collected': self.collection_stats['successful_collections']
            }
            
            # Build INSERT query dynamically
            columns = list(data_dict.keys())
            placeholders = ['?' for _ in columns]
            values = [data_dict[col] for col in columns]
            
            # Check if record exists
            cursor.execute("SELECT id FROM assets WHERE hostname = ? AND ip_address = ?", 
                          (hostname, data_dict['ip_address']))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing record
                set_clause = ', '.join([f"{col} = ?" for col in columns])
                update_query = f"UPDATE assets SET {\', \'.join(update_fields)} WHERE id = ?"  # NOTE: Safe - fields from schema
                cursor.execute(update_query, values + [existing[0]])
                print(f"✅ Updated existing record for {hostname}")
            else:
                # Insert new record
                insert_query = f"INSERT INTO assets ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
                cursor.execute(insert_query, values)
                print(f"✅ Inserted new record for {hostname}")
            
            self.db_connection.commit()
            
        except Exception as e:
            print(f"❌ Error saving to database: {e}")
    
    def get_default_mapping(self):
        """Default WMI mapping if file not available"""
        return {
            'Win32_ComputerSystem': {'computer_name': 'Name'},
            'Win32_OperatingSystem': {'operating_system': 'Caption'},
            'Win32_Processor': {'processor_name': 'Name'}
        }

def main():
    collector = UltimateWMICollector()
    
    print("🔥 Ultimate WMI Data Collector")
    print("Collecting ALL possible WMI data including current user information")
    print("=" * 80)
    
    # Connect to WMI and Database
    if not collector.connect_wmi():
        sys.exit(1)
    
    if not collector.connect_database():
        sys.exit(1)
    
    # Collect all data
    hostname = "localhost"  # Can be parameterized
    collected_data = collector.collect_all_data(hostname)
    
    # Save to database
    collector.save_to_database(hostname)
    
    # Save detailed data to JSON for analysis
    with open(f'complete_wmi_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w') as f:
        json.dump(collected_data, f, indent=2, default=str)
    
    print("\n🎉 COLLECTION COMPLETE!")
    print(f"📊 Collected {collector.collection_stats['successful_collections']} data fields")
    print(f"⏱️ Collection time: {collector.collection_stats['collection_time']:.2f} seconds")
    print(f"✅ Success rate: {(collector.collection_stats['successful_collections'] / max(1, collector.collection_stats['total_fields'])) * 100:.1f}%")

if __name__ == "__main__":
    main()