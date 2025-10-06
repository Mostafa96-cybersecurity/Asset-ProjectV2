#!/usr/bin/env python3
"""
🔥 ENHANCED WMI COLLECTOR - PROPERLY MAPPED TO DATABASE
Collects ALL WMI data and maps to existing database columns
Includes comprehensive current user detection
"""

import wmi
import sqlite3
import json
import sys
import time
from datetime import datetime
import win32api
import os

class EnhancedMappedWMICollector:
    def __init__(self):
        self.wmi_connection = None
        self.db_connection = None
        self.collected_data = {}
        self.collection_stats = {
            'total_fields': 0,
            'successful_collections': 0,
            'failed_collections': 0,
            'collection_time': 0
        }
        
        # Load database mapping
        try:
            with open('wmi_to_database_mapping.json', 'r') as f:
                self.db_mapping = json.load(f)
        except:
            self.db_mapping = {}
    
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
    
    def get_comprehensive_user_info(self):
        """Get comprehensive current user and all user information"""
        print("👤 Collecting Comprehensive User Information...")
        user_data = {}
        
        try:
            # Current logged in user
            current_user = win32api.GetUserName()
            user_data['current_user'] = current_user
            print(f"   ✅ Current User: {current_user}")
            
            # User domain
            try:
                domain = win32api.GetUserNameEx(win32api.NameSamCompatible).split('\\')[0]
                user_data['current_user_domain'] = domain
            except:
                domain = os.environ.get('USERDOMAIN', 'Unknown')
                user_data['current_user_domain'] = domain
            
            # Check if user is admin
            try:
                import ctypes
                is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
                user_data['current_user_is_admin'] = is_admin
                print(f"   ✅ Admin Status: {is_admin}")
            except:
                user_data['current_user_is_admin'] = False
            
            # Get all local users via WMI
            try:
                local_users = []
                for user in self.wmi_connection.Win32_UserAccount(LocalAccount=True):
                    user_info = {
                        'name': user.Name,
                        'full_name': getattr(user, 'FullName', ''),
                        'description': getattr(user, 'Description', ''),
                        'disabled': getattr(user, 'Disabled', False),
                        'account_type': getattr(user, 'AccountType', 'Unknown')
                    }
                    local_users.append(user_info)
                
                user_data['local_users'] = local_users
                print(f"   ✅ Local Users Found: {len(local_users)}")
                
            except Exception as e:
                print(f"   ⚠️ Error getting local users: {e}")
                user_data['local_users'] = []
            
            # Get logged on users
            try:
                logged_users = []
                for session in self.wmi_connection.Win32_LogonSession():
                    if hasattr(session, 'LogonType') and session.LogonType == 2:  # Interactive logon
                        logged_users.append({
                            'logon_id': session.LogonId,
                            'logon_type': session.LogonType,
                            'start_time': str(session.StartTime) if session.StartTime else 'Unknown'
                        })
                
                user_data['logged_sessions'] = logged_users
                print(f"   ✅ Active Sessions: {len(logged_users)}")
                
            except Exception as e:
                print(f"   ⚠️ Error getting logged sessions: {e}")
                user_data['logged_sessions'] = []
            
            # Get user profiles
            try:
                user_profiles = []
                for profile in self.wmi_connection.Win32_UserProfile():
                    if hasattr(profile, 'LocalPath'):
                        profile_info = {
                            'local_path': profile.LocalPath,
                            'sid': getattr(profile, 'SID', 'Unknown'),
                            'loaded': getattr(profile, 'Loaded', False),
                            'special': getattr(profile, 'Special', False)
                        }
                        user_profiles.append(profile_info)
                
                user_data['user_profiles_list'] = user_profiles
                print(f"   ✅ User Profiles: {len(user_profiles)}")
                
            except Exception as e:
                print(f"   ⚠️ Error getting user profiles: {e}")
                user_data['user_profiles_list'] = []
            
        except Exception as e:
            print(f"⚠️ Error in comprehensive user collection: {e}")
        
        return user_data
    
    def collect_system_info(self):
        """Collect system information mapped to database columns"""
        print("🖥️ Collecting System Information...")
        
        try:
            for system in self.wmi_connection.Win32_ComputerSystem():
                self.collected_data.update({
                    'computer_name': getattr(system, 'Name', 'Unknown'),
                    'manufacturer': getattr(system, 'Manufacturer', 'Unknown'),
                    'model': getattr(system, 'Model', 'Unknown'),
                    'total_physical_memory': getattr(system, 'TotalPhysicalMemory', 0),
                    'domain_name': getattr(system, 'Domain', 'Unknown'),
                    'workgroup': getattr(system, 'Workgroup', 'Unknown'),
                    'system_type': getattr(system, 'SystemType', 'Unknown'),
                    'number_of_processors': getattr(system, 'NumberOfProcessors', 0),
                    'total_cpu': getattr(system, 'NumberOfLogicalProcessors', 0)
                })
                print(f"   ✅ System: {self.collected_data['manufacturer']} {self.collected_data['model']}")
                self.collection_stats['successful_collections'] += 9
                break
        except Exception as e:
            print(f"⚠️ Error collecting system info: {e}")
            self.collection_stats['failed_collections'] += 1
    
    def collect_os_info(self):
        """Collect operating system information"""
        print("🪟 Collecting Operating System Information...")
        
        try:
            for os_info in self.wmi_connection.Win32_OperatingSystem():
                self.collected_data.update({
                    'operating_system': getattr(os_info, 'Caption', 'Unknown'),
                    'os_version': getattr(os_info, 'Version', 'Unknown'),
                    'os_build_number': getattr(os_info, 'BuildNumber', 'Unknown'),
                    'os_architecture': getattr(os_info, 'OSArchitecture', 'Unknown'),
                    'os_service_pack': getattr(os_info, 'ServicePackMajorVersion', 0),
                    'windows_directory': getattr(os_info, 'WindowsDirectory', 'Unknown'),
                    'system_directory': getattr(os_info, 'SystemDirectory', 'Unknown'),
                    'boot_device': getattr(os_info, 'BootDevice', 'Unknown'),
                    'locale': getattr(os_info, 'Locale', 'Unknown'),
                    'country_code': getattr(os_info, 'CountryCode', 'Unknown'),
                    'free_physical_memory': getattr(os_info, 'FreePhysicalMemory', 0),
                    'available_memory': getattr(os_info, 'FreePhysicalMemory', 0)
                })
                print(f"   ✅ OS: {self.collected_data['operating_system']}")
                self.collection_stats['successful_collections'] += 12
                break
        except Exception as e:
            print(f"⚠️ Error collecting OS info: {e}")
            self.collection_stats['failed_collections'] += 1
    
    def collect_processor_info(self):
        """Collect processor information"""
        print("⚙️ Collecting Processor Information...")
        
        try:
            processors = []
            total_cores = 0
            total_logical = 0
            
            for cpu in self.wmi_connection.Win32_Processor():
                processor_data = {
                    'name': getattr(cpu, 'Name', 'Unknown'),
                    'manufacturer': getattr(cpu, 'Manufacturer', 'Unknown'),
                    'architecture': getattr(cpu, 'Architecture', 'Unknown'),
                    'cores': getattr(cpu, 'NumberOfCores', 0),
                    'logical_processors': getattr(cpu, 'NumberOfLogicalProcessors', 0),
                    'max_clock_speed': getattr(cpu, 'MaxClockSpeed', 0),
                    'current_clock_speed': getattr(cpu, 'CurrentClockSpeed', 0),
                    'l2_cache_size': getattr(cpu, 'L2CacheSize', 0),
                    'l3_cache_size': getattr(cpu, 'L3CacheSize', 0)
                }
                processors.append(processor_data)
                total_cores += processor_data['cores']
                total_logical += processor_data['logical_processors']
            
            if processors:
                self.collected_data.update({
                    'processor_name': processors[0]['name'],
                    'processor_manufacturer': processors[0]['manufacturer'],
                    'processor_architecture': processors[0]['architecture'],
                    'processor_cores': total_cores,
                    'processor_logical_processors': total_logical,
                    'processor_speed': processors[0]['max_clock_speed'],
                    'cpu_cores': total_cores,
                    'cpu_threads': total_logical,
                    'cpu_info': json.dumps(processors),
                    'architecture': processors[0]['architecture']
                })
                print(f"   ✅ CPU: {processors[0]['name']} ({total_cores} cores)")
                self.collection_stats['successful_collections'] += 10
        
        except Exception as e:
            print(f"⚠️ Error collecting processor info: {e}")
            self.collection_stats['failed_collections'] += 1
    
    def collect_memory_info(self):
        """Collect memory information"""
        print("🧠 Collecting Memory Information...")
        
        try:
            memory_modules = []
            total_capacity = 0
            
            for memory in self.wmi_connection.Win32_PhysicalMemory():
                capacity = getattr(memory, 'Capacity', 0)
                if capacity:
                    capacity = int(capacity)
                    total_capacity += capacity
                    
                memory_info = {
                    'manufacturer': getattr(memory, 'Manufacturer', 'Unknown'),
                    'capacity': capacity,
                    'speed': getattr(memory, 'Speed', 0),
                    'memory_type': getattr(memory, 'MemoryType', 'Unknown'),
                    'form_factor': getattr(memory, 'FormFactor', 'Unknown'),
                    'device_locator': getattr(memory, 'DeviceLocator', 'Unknown')
                }
                memory_modules.append(memory_info)
            
            # Calculate memory values
            memory_gb = round(total_capacity / (1024**3), 2) if total_capacity > 0 else 0
            
            self.collected_data.update({
                'installed_ram_gb': memory_gb,
                'memory_gb': memory_gb,
                'total_ram': memory_gb,
                'memory_type': memory_modules[0]['memory_type'] if memory_modules else 'Unknown',
                'memory_slots_used': len(memory_modules),
                'memory_slots_total': len(memory_modules),  # Approximation
                'memory_info': json.dumps(memory_modules)
            })
            
            print(f"   ✅ Memory: {memory_gb} GB ({len(memory_modules)} modules)")
            self.collection_stats['successful_collections'] += 7
            
        except Exception as e:
            print(f"⚠️ Error collecting memory info: {e}")
            self.collection_stats['failed_collections'] += 1
    
    def collect_storage_info(self):
        """Collect storage information"""
        print("💽 Collecting Storage Information...")
        
        try:
            # Physical drives
            physical_drives = []
            for drive in self.wmi_connection.Win32_DiskDrive():
                drive_info = {
                    'model': getattr(drive, 'Model', 'Unknown'),
                    'manufacturer': getattr(drive, 'Manufacturer', 'Unknown'),
                    'serial_number': getattr(drive, 'SerialNumber', 'Unknown'),
                    'size': getattr(drive, 'Size', 0),
                    'interface_type': getattr(drive, 'InterfaceType', 'Unknown'),
                    'media_type': getattr(drive, 'MediaType', 'Unknown')
                }
                physical_drives.append(drive_info)
            
            # Logical drives
            logical_drives = []
            total_size = 0
            total_free = 0
            
            for disk in self.wmi_connection.Win32_LogicalDisk():
                size = getattr(disk, 'Size', 0)
                free_space = getattr(disk, 'FreeSpace', 0)
                
                if size:
                    size = int(size)
                    total_size += size
                    
                if free_space:
                    free_space = int(free_space)
                    total_free += free_space
                
                drive_info = {
                    'device_id': getattr(disk, 'DeviceID', 'Unknown'),
                    'size': size,
                    'free_space': free_space,
                    'file_system': getattr(disk, 'FileSystem', 'Unknown'),
                    'volume_name': getattr(disk, 'VolumeName', 'Unknown'),
                    'drive_type': getattr(disk, 'DriveType', 'Unknown')
                }
                logical_drives.append(drive_info)
            
            self.collected_data.update({
                'hard_drives': json.dumps(physical_drives),
                'storage_info': json.dumps(logical_drives),
                'total_disk_space': total_size,
                'free_disk_space': total_free,
                'drive_types': ','.join([d['drive_type'] for d in logical_drives]),
                'drive_sizes': ','.join([str(d['size']) for d in logical_drives]),
                'drive_free_space': ','.join([str(d['free_space']) for d in logical_drives]),
                'drive_filesystems': ','.join([d['file_system'] for d in logical_drives])
            })
            
            print(f"   ✅ Storage: {len(physical_drives)} drives, {round(total_size/(1024**3), 1)} GB total")
            self.collection_stats['successful_collections'] += 8
            
        except Exception as e:
            print(f"⚠️ Error collecting storage info: {e}")
            self.collection_stats['failed_collections'] += 1
    
    def collect_network_info(self):
        """Collect network information"""
        print("🌐 Collecting Network Information...")
        
        try:
            adapters = []
            ip_list = []
            mac_list = []
            dns_list = []
            gateways = []
            
            # Network adapters
            for adapter in self.wmi_connection.Win32_NetworkAdapter():
                if getattr(adapter, 'NetConnectionStatus', None) is not None:
                    adapter_info = {
                        'name': getattr(adapter, 'Name', 'Unknown'),
                        'manufacturer': getattr(adapter, 'Manufacturer', 'Unknown'),
                        'adapter_type': getattr(adapter, 'AdapterType', 'Unknown'),
                        'mac_address': getattr(adapter, 'MACAddress', 'Unknown'),
                        'speed': getattr(adapter, 'Speed', 0),
                        'status': getattr(adapter, 'NetConnectionStatus', 'Unknown')
                    }
                    adapters.append(adapter_info)
                    if adapter_info['mac_address'] != 'Unknown':
                        mac_list.append(adapter_info['mac_address'])
            
            # Network configurations
            for config in self.wmi_connection.Win32_NetworkAdapterConfiguration():
                if getattr(config, 'IPEnabled', False):
                    ip_addresses = getattr(config, 'IPAddress', [])
                    dns_servers = getattr(config, 'DNSServerSearchOrder', [])
                    default_gateway = getattr(config, 'DefaultIPGateway', [])
                    
                    if ip_addresses:
                        ip_list.extend([ip for ip in ip_addresses if ip])
                    if dns_servers:
                        dns_list.extend([dns for dns in dns_servers if dns])
                    if default_gateway:
                        gateways.extend([gw for gw in default_gateway if gw])
            
            self.collected_data.update({
                'network_adapters': json.dumps(adapters),
                'ip_address': ip_list[0] if ip_list else 'Unknown',
                'ip_addresses': ','.join(ip_list),
                'mac_address': mac_list[0] if mac_list else 'Unknown',
                'mac_addresses': ','.join(mac_list),
                'dns_servers': ','.join(dns_list),
                'default_gateway': gateways[0] if gateways else 'Unknown',
                'network_adapter_types': ','.join([a['adapter_type'] for a in adapters])
            })
            
            print(f"   ✅ Network: {len(adapters)} adapters, IP: {ip_list[0] if ip_list else 'None'}")
            self.collection_stats['successful_collections'] += 8
            
        except Exception as e:
            print(f"⚠️ Error collecting network info: {e}")
            self.collection_stats['failed_collections'] += 1
    
    def collect_software_and_services(self):
        """Collect software and services information"""
        print("📦 Collecting Software and Services...")
        
        try:
            # Installed software
            software_list = []
            for software in self.wmi_connection.Win32_Product():
                software_info = {
                    'name': getattr(software, 'Name', 'Unknown'),
                    'version': getattr(software, 'Version', 'Unknown'),
                    'vendor': getattr(software, 'Vendor', 'Unknown'),
                    'install_date': str(getattr(software, 'InstallDate', 'Unknown'))
                }
                software_list.append(software_info)
            
            # Services
            services_list = []
            running_count = 0
            stopped_count = 0
            
            for service in self.wmi_connection.Win32_Service():
                service_info = {
                    'name': getattr(service, 'Name', 'Unknown'),
                    'display_name': getattr(service, 'DisplayName', 'Unknown'),
                    'status': getattr(service, 'Status', 'Unknown'),
                    'start_mode': getattr(service, 'StartMode', 'Unknown'),
                    'state': getattr(service, 'State', 'Unknown')
                }
                services_list.append(service_info)
                
                if service_info['state'] == 'Running':
                    running_count += 1
                else:
                    stopped_count += 1
            
            self.collected_data.update({
                'installed_software': json.dumps(software_list),
                'installed_software_count': len(software_list),
                'services': json.dumps(services_list),
                'running_services': json.dumps([s for s in services_list if s['state'] == 'Running']),
                'services_running': running_count,
                'services_stopped': stopped_count
            })
            
            print(f"   ✅ Software: {len(software_list)} programs, Services: {len(services_list)} total")
            self.collection_stats['successful_collections'] += 6
            
        except Exception as e:
            print(f"⚠️ Error collecting software/services: {e}")
            self.collection_stats['failed_collections'] += 1
    
    def collect_hardware_details(self):
        """Collect additional hardware details"""
        print("🔧 Collecting Hardware Details...")
        
        try:
            # BIOS
            for bios in self.wmi_connection.Win32_BIOS():
                self.collected_data.update({
                    'bios_version': getattr(bios, 'SMBIOSBIOSVersion', 'Unknown'),
                    'bios_manufacturer': getattr(bios, 'Manufacturer', 'Unknown'),
                    'bios_serial_number': getattr(bios, 'SerialNumber', 'Unknown'),
                    'bios_release_date': str(getattr(bios, 'ReleaseDate', 'Unknown')),
                    'bios_date': str(getattr(bios, 'ReleaseDate', 'Unknown'))
                })
                break
            
            # Motherboard
            for board in self.wmi_connection.Win32_BaseBoard():
                self.collected_data.update({
                    'motherboard_manufacturer': getattr(board, 'Manufacturer', 'Unknown'),
                    'motherboard_model': getattr(board, 'Product', 'Unknown'),
                    'motherboard_serial': getattr(board, 'SerialNumber', 'Unknown'),
                    'motherboard_version': getattr(board, 'Version', 'Unknown')
                })
                break
            
            # Graphics
            graphics_cards = []
            for gpu in self.wmi_connection.Win32_VideoController():
                gpu_info = {
                    'name': getattr(gpu, 'Name', 'Unknown'),
                    'adapter_ram': getattr(gpu, 'AdapterRAM', 0),
                    'driver_version': getattr(gpu, 'DriverVersion', 'Unknown'),
                    'driver_date': str(getattr(gpu, 'DriverDate', 'Unknown'))
                }
                graphics_cards.append(gpu_info)
            
            if graphics_cards:
                self.collected_data.update({
                    'graphics_card': graphics_cards[0]['name'],
                    'graphics_cards': json.dumps(graphics_cards),
                    'graphics_memory': graphics_cards[0]['adapter_ram'],
                    'graphics_driver': graphics_cards[0]['driver_version']
                })
            
            # Audio devices
            audio_devices = []
            for audio in self.wmi_connection.Win32_SoundDevice():
                audio_info = {
                    'name': getattr(audio, 'Name', 'Unknown'),
                    'manufacturer': getattr(audio, 'Manufacturer', 'Unknown'),
                    'status': getattr(audio, 'Status', 'Unknown')
                }
                audio_devices.append(audio_info)
            
            self.collected_data.update({
                'sound_devices': json.dumps(audio_devices),
                'audio_devices': json.dumps(audio_devices)
            })
            
            # USB Controllers
            usb_controllers = []
            for usb in self.wmi_connection.Win32_USBController():
                usb_info = {
                    'name': getattr(usb, 'Name', 'Unknown'),
                    'manufacturer': getattr(usb, 'Manufacturer', 'Unknown'),
                    'status': getattr(usb, 'Status', 'Unknown')
                }
                usb_controllers.append(usb_info)
            
            self.collected_data.update({
                'usb_controllers': json.dumps(usb_controllers)
            })
            
            print(f"   ✅ Hardware: BIOS, Motherboard, {len(graphics_cards)} GPU(s), {len(audio_devices)} Audio")
            self.collection_stats['successful_collections'] += 15
            
        except Exception as e:
            print(f"⚠️ Error collecting hardware details: {e}")
            self.collection_stats['failed_collections'] += 1
    
    def collect_all_data(self, hostname="localhost"):
        """Collect ALL WMI data"""
        print("=" * 80)
        print("🔥 ENHANCED WMI DATA COLLECTION - MAPPED TO DATABASE")
        print("=" * 80)
        
        start_time = time.time()
        
        # Set basic identification
        self.collected_data['hostname'] = hostname
        self.collected_data['device_type'] = 'Workstation'  # Default, can be updated
        self.collected_data['collection_timestamp'] = datetime.now().isoformat()
        
        # Get comprehensive user info
        user_data = self.get_comprehensive_user_info()
        
        # Map user data to database columns
        self.collected_data.update({
            'assigned_user': user_data.get('current_user', 'Unknown'),
            'last_logged_user': user_data.get('current_user', 'Unknown'),
            'logged_in_users': user_data.get('current_user', 'Unknown'),
            'logged_on_users': user_data.get('current_user', 'Unknown'),
            'working_user': user_data.get('current_user', 'Unknown'),
            'user_accounts': json.dumps(user_data.get('local_users', [])),
            'user_profiles': json.dumps(user_data.get('user_profiles_list', [])),
            'local_admin_users': user_data.get('current_user', 'Unknown') if user_data.get('current_user_is_admin', False) else 'None'
        })
        
        # Collect all data categories
        collection_methods = [
            self.collect_system_info,
            self.collect_os_info,
            self.collect_processor_info,
            self.collect_memory_info,
            self.collect_storage_info,
            self.collect_network_info,
            self.collect_software_and_services,
            self.collect_hardware_details
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
        """Save data to database using proper column mapping"""
        print("\n💾 Saving data to database...")
        
        try:
            cursor = self.db_connection.cursor()
            
            # Get existing database columns
            cursor.execute("PRAGMA table_info(assets)")
            db_columns = {col[1]: col[2] for col in cursor.fetchall()}
            
            # Filter collected data to only include existing columns
            filtered_data = {}
            for key, value in self.collected_data.items():
                if key in db_columns:
                    filtered_data[key] = value
            
            print(f"   📊 Mapped {len(filtered_data)} fields to database columns")
            
            # Check if record exists
            cursor.execute("SELECT id FROM assets WHERE hostname = ?", (hostname,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing record
                if filtered_data:
                    set_clause = ', '.join([f"{col} = ?" for col in filtered_data.keys()])
                    update_query = f"UPDATE assets SET {\', \'.join(update_fields)} WHERE id = ?"  # NOTE: Safe - fields from schema
                    cursor.execute(update_query, list(filtered_data.values()) + [existing[0]])
                    print(f"✅ Updated existing record for {hostname}")
                else:
                    print("⚠️ No data to update")
            else:
                # Insert new record
                if filtered_data:
                    columns = list(filtered_data.keys())
                    placeholders = ['?' for _ in columns]
                    insert_query = f"INSERT INTO assets ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
                    cursor.execute(insert_query, list(filtered_data.values()))
                    print(f"✅ Inserted new record for {hostname}")
                else:
                    print("⚠️ No data to insert")
            
            self.db_connection.commit()
            
        except Exception as e:
            print(f"❌ Error saving to database: {e}")
            import traceback
            print(traceback.format_exc())

def main():
    collector = EnhancedMappedWMICollector()
    
    print("🔥 Enhanced WMI Data Collector - Database Mapped")
    print("Collecting ALL WMI data including current user information")
    print("=" * 80)
    
    # Connect to WMI and Database
    if not collector.connect_wmi():
        sys.exit(1)
    
    if not collector.connect_database():
        sys.exit(1)
    
    # Collect all data
    hostname = "localhost"
    collected_data = collector.collect_all_data(hostname)
    
    # Save to database
    collector.save_to_database(hostname)
    
    # Save detailed data to JSON
    with open(f'enhanced_wmi_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w') as f:
        json.dump(collected_data, f, indent=2, default=str)
    
    print("\n🎉 COLLECTION COMPLETE!")
    print(f"📊 Collected {collector.collection_stats['successful_collections']} data fields")
    print(f"⏱️ Collection time: {collector.collection_stats['collection_time']:.2f} seconds")
    print(f"✅ Success rate: {(collector.collection_stats['successful_collections'] / max(1, collector.collection_stats['total_fields'])) * 100:.1f}%")
    print(f"👤 Current User: {collected_data.get('assigned_user', 'Unknown')}")

if __name__ == "__main__":
    main()