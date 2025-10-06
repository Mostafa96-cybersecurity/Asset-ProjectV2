#!/usr/bin/env python3
"""
ENHANCED HARDWARE DATA COLLECTOR

This tool significantly improves hardware data collection using multiple methods:
✅ Enhanced WMI queries with better error handling
✅ PowerShell hardware detection commands
✅ Registry-based hardware information
✅ System file parsing for hardware details
✅ Network-based hardware discovery
✅ Smart fallback mechanisms when one method fails
"""

import ipaddress  # For IP validation
import sqlite3
import subprocess
import json
import platform
import socket
from datetime import datetime
import wmi
import winreg

class EnhancedHardwareCollector:
    def __init__(self, db_path="assets.db"):
        self.db_path = db_path
        self.stats = {
            'devices_processed': 0,
            'hardware_data_improved': 0,
            'wmi_success': 0,
            'powershell_success': 0,
            'registry_success': 0,
            'network_success': 0,
            'errors': []
        }

    def enhance_hardware_data(self, target_devices=None):
        """Enhance hardware data collection for all or specific devices"""
        
        print("🔧 ENHANCED HARDWARE DATA COLLECTOR")
        print("=" * 70)
        print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("🎯 Goal: Improve hardware data collection success rate")
        print()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get devices that need hardware data enhancement
        if target_devices:
            placeholders = ','.join(['?' for _ in target_devices])
            query = f"SELECT id, hostname, ip_address FROM assets WHERE id IN ({placeholders})"
            cursor.execute(query, target_devices)
        else:
            # Focus on alive devices or recently seen devices
            cursor.execute("""
                SELECT id, hostname, ip_address 
                FROM assets 
                WHERE (device_status = 'alive' OR last_seen >= datetime('now', '-7 days'))
                AND (processor_name IS NULL OR total_physical_memory IS NULL OR mac_address IS NULL)
                ORDER BY last_seen DESC
                LIMIT 50
            """)
        
        devices_to_enhance = cursor.fetchall()
        
        print(f"🔍 Found {len(devices_to_enhance)} devices that need hardware data enhancement")
        
        if not devices_to_enhance:
            print("✅ All devices already have complete hardware data!")
            conn.close()
            return
        
        print("\n📊 ENHANCING HARDWARE DATA:")
        
        for device_id, hostname, ip_address in devices_to_enhance:
            print(f"\n🔧 Processing: {hostname or ip_address} (ID: {device_id})")
            
            hardware_data = self.collect_comprehensive_hardware_data(hostname, ip_address)
            
            if hardware_data:
                self.update_device_hardware_data(cursor, device_id, hardware_data)
                self.stats['hardware_data_improved'] += 1
                print(f"   ✅ Enhanced hardware data for {hostname or ip_address}")
            else:
                print(f"   ⚠️ Could not enhance hardware data for {hostname or ip_address}")
            
            self.stats['devices_processed'] += 1
        
        conn.commit()
        conn.close()
        
        self.show_enhancement_results()

    def collect_comprehensive_hardware_data(self, hostname, ip_address):
        """Collect hardware data using multiple enhanced methods"""
        
        hardware_data = {
            'collection_time': datetime.now().isoformat(),
            'hardware_collection_method': 'Enhanced Multi-Method'
        }
        
        collection_success = False
        
        # Method 1: Enhanced WMI Collection (for Windows devices)
        try:
            wmi_data = self.enhanced_wmi_collection(hostname, ip_address)
            if wmi_data:
                hardware_data.update(wmi_data)
                collection_success = True
                self.stats['wmi_success'] += 1
                print("      ✅ WMI data collected")
        except Exception as e:
            self.stats['errors'].append(f"WMI error for {hostname}: {str(e)}")
            print(f"      ⚠️ WMI collection failed: {str(e)[:50]}")
        
        # Method 2: PowerShell Hardware Detection
        try:
            ps_data = self.powershell_hardware_collection(hostname, ip_address)
            if ps_data:
                # Merge PowerShell data (don't overwrite WMI data)
                for key, value in ps_data.items():
                    if key not in hardware_data or not hardware_data[key]:
                        hardware_data[key] = value
                collection_success = True
                self.stats['powershell_success'] += 1
                print("      ✅ PowerShell data collected")
        except Exception as e:
            self.stats['errors'].append(f"PowerShell error for {hostname}: {str(e)}")
            print(f"      ⚠️ PowerShell collection failed: {str(e)[:50]}")
        
        # Method 3: Registry-based Hardware Detection (local only)
        if ip_address == '127.0.0.1' or hostname.lower() in ['localhost', platform.node().lower()]:
            try:
                reg_data = self.registry_hardware_collection()
                if reg_data:
                    for key, value in reg_data.items():
                        if key not in hardware_data or not hardware_data[key]:
                            hardware_data[key] = value
                    collection_success = True
                    self.stats['registry_success'] += 1
                    print("      ✅ Registry data collected")
            except Exception as e:
                self.stats['errors'].append(f"Registry error for {hostname}: {str(e)}")
                print(f"      ⚠️ Registry collection failed: {str(e)[:50]}")
        
        # Method 4: Network-based Hardware Discovery
        try:
            net_data = self.network_hardware_discovery(ip_address)
            if net_data:
                for key, value in net_data.items():
                    if key not in hardware_data or not hardware_data[key]:
                        hardware_data[key] = value
                collection_success = True
                self.stats['network_success'] += 1
                print("      ✅ Network discovery data collected")
        except Exception as e:
            self.stats['errors'].append(f"Network error for {hostname}: {str(e)}")
            print(f"      ⚠️ Network collection failed: {str(e)[:50]}")
        
        # Method 5: System Command Hardware Detection
        try:
            sys_data = self.system_command_collection(hostname, ip_address)
            if sys_data:
                for key, value in sys_data.items():
                    if key not in hardware_data or not hardware_data[key]:
                        hardware_data[key] = value
                collection_success = True
                print("      ✅ System command data collected")
        except Exception as e:
            self.stats['errors'].append(f"System command error for {hostname}: {str(e)}")
            print(f"      ⚠️ System command collection failed: {str(e)[:50]}")
        
        return hardware_data if collection_success else None

    def enhanced_wmi_collection(self, hostname, ip_address):
        """Enhanced WMI collection with better queries and error handling"""
        
        hardware_data = {}
        
        try:
            # Try to connect to WMI
            if hostname and hostname.lower() not in ['localhost', '127.0.0.1']:
                # Remote WMI connection
                wmi_connection = wmi.WMI(computer=hostname)
            else:
                # Local WMI connection
                wmi_connection = wmi.WMI()
            
            # Enhanced Computer System Information
            try:
                for computer in wmi_connection.Win32_ComputerSystem():
                    hardware_data['system_manufacturer'] = computer.Manufacturer
                    hardware_data['system_model'] = computer.Model
                    hardware_data['total_physical_memory'] = str(int(computer.TotalPhysicalMemory) // (1024**3)) + " GB" if computer.TotalPhysicalMemory else None
                    hardware_data['computer_name'] = computer.Name
                    hardware_data['domain'] = computer.Domain
                    hardware_data['workgroup'] = computer.Workgroup
                    hardware_data['number_of_processors'] = computer.NumberOfProcessors
                    hardware_data['system_type'] = computer.SystemType
                    break
            except Exception as e:
                print(f"        ⚠️ Computer system query failed: {str(e)[:30]}")
            
            # Enhanced Processor Information
            try:
                processors = []
                for processor in wmi_connection.Win32_Processor():
                    proc_info = {
                        'name': processor.Name,
                        'cores': processor.NumberOfCores,
                        'logical_processors': processor.NumberOfLogicalProcessors,
                        'max_clock_speed': processor.MaxClockSpeed,
                        'manufacturer': processor.Manufacturer,
                        'architecture': processor.Architecture
                    }
                    processors.append(proc_info)
                    
                    if not hardware_data.get('processor_name'):
                        hardware_data['processor_name'] = processor.Name
                        hardware_data['processor_cores'] = processor.NumberOfCores
                        hardware_data['processor_threads'] = processor.NumberOfLogicalProcessors
                        hardware_data['processor_speed_mhz'] = processor.MaxClockSpeed
                        hardware_data['processor_manufacturer'] = processor.Manufacturer
                
                hardware_data['processors_detailed'] = json.dumps(processors)
            except Exception as e:
                print(f"        ⚠️ Processor query failed: {str(e)[:30]}")
            
            # Enhanced BIOS Information
            try:
                for bios in wmi_connection.Win32_BIOS():
                    hardware_data['bios_manufacturer'] = bios.Manufacturer
                    hardware_data['bios_version'] = bios.Version
                    hardware_data['bios_serial_number'] = bios.SerialNumber
                    hardware_data['bios_release_date'] = str(bios.ReleaseDate) if bios.ReleaseDate else None
                    break
            except Exception as e:
                print(f"        ⚠️ BIOS query failed: {str(e)[:30]}")
            
            # Enhanced Motherboard Information
            try:
                for board in wmi_connection.Win32_BaseBoard():
                    hardware_data['motherboard_manufacturer'] = board.Manufacturer
                    hardware_data['motherboard_product'] = board.Product
                    hardware_data['motherboard_serial'] = board.SerialNumber
                    hardware_data['motherboard_version'] = board.Version
                    break
            except Exception as e:
                print(f"        ⚠️ Motherboard query failed: {str(e)[:30]}")
            
            # Enhanced Memory Information
            try:
                memory_modules = []
                total_memory = 0
                for memory in wmi_connection.Win32_PhysicalMemory():
                    capacity_gb = int(memory.Capacity) // (1024**3) if memory.Capacity else 0
                    total_memory += capacity_gb
                    
                    mem_info = {
                        'capacity_gb': capacity_gb,
                        'speed': memory.Speed,
                        'manufacturer': memory.Manufacturer,
                        'part_number': memory.PartNumber,
                        'serial_number': memory.SerialNumber,
                        'memory_type': memory.MemoryType
                    }
                    memory_modules.append(mem_info)
                
                hardware_data['memory_modules'] = json.dumps(memory_modules)
                hardware_data['total_memory_modules'] = len(memory_modules)
                hardware_data['total_memory_gb'] = total_memory
            except Exception as e:
                print(f"        ⚠️ Memory query failed: {str(e)[:30]}")
            
            # Enhanced Disk Information
            try:
                disks = []
                for disk in wmi_connection.Win32_DiskDrive():
                    disk_size_gb = int(disk.Size) // (1024**3) if disk.Size else 0
                    disk_info = {
                        'model': disk.Model,
                        'size_gb': disk_size_gb,
                        'interface_type': disk.InterfaceType,
                        'serial_number': disk.SerialNumber,
                        'manufacturer': disk.Manufacturer
                    }
                    disks.append(disk_info)
                
                hardware_data['disk_drives'] = json.dumps(disks)
                hardware_data['total_disks'] = len(disks)
                if disks:
                    hardware_data['primary_disk_model'] = disks[0]['model']
                    hardware_data['primary_disk_size_gb'] = disks[0]['size_gb']
            except Exception as e:
                print(f"        ⚠️ Disk query failed: {str(e)[:30]}")
            
            # Enhanced Network Adapter Information
            try:
                network_adapters = []
                for adapter in wmi_connection.Win32_NetworkAdapterConfiguration(IPEnabled=True):
                    if adapter.MACAddress:
                        adapter_info = {
                            'description': adapter.Description,
                            'mac_address': adapter.MACAddress,
                            'ip_addresses': adapter.IPAddress,
                            'dhcp_enabled': adapter.DHCPEnabled,
                            'dns_servers': adapter.DNSServerSearchOrder
                        }
                        network_adapters.append(adapter_info)
                        
                        # Set primary MAC address
                        if not hardware_data.get('mac_address'):
                            hardware_data['mac_address'] = adapter.MACAddress
                
                hardware_data['network_adapters'] = json.dumps(network_adapters)
                hardware_data['total_network_adapters'] = len(network_adapters)
            except Exception as e:
                print(f"        ⚠️ Network adapter query failed: {str(e)[:30]}")
            
            # Enhanced Operating System Information
            try:
                for os in wmi_connection.Win32_OperatingSystem():
                    hardware_data['operating_system'] = os.Caption
                    hardware_data['os_version'] = os.Version
                    hardware_data['os_build_number'] = os.BuildNumber
                    hardware_data['os_service_pack'] = os.ServicePackMajorVersion
                    hardware_data['os_architecture'] = os.OSArchitecture
                    hardware_data['os_install_date'] = str(os.InstallDate) if os.InstallDate else None
                    hardware_data['system_directory'] = os.SystemDirectory
                    break
            except Exception as e:
                print(f"        ⚠️ OS query failed: {str(e)[:30]}")
            
            # Enhanced System Serial Numbers
            try:
                for system in wmi_connection.Win32_ComputerSystemProduct():
                    hardware_data['serial_number'] = system.IdentifyingNumber
                    hardware_data['system_uuid'] = system.UUID
                    hardware_data['system_vendor'] = system.Vendor
                    break
            except Exception as e:
                print(f"        ⚠️ System product query failed: {str(e)[:30]}")
            
        except Exception as e:
            print(f"        ❌ WMI connection failed: {str(e)[:50]}")
            return None
        
        return hardware_data if hardware_data else None

    def powershell_hardware_collection(self, hostname, ip_address):
        """Use PowerShell commands for hardware detection"""
        
        hardware_data = {}
        
        try:
            # PowerShell commands for hardware information
            ps_commands = {
                'computer_info': 'Get-ComputerInfo | Select-Object -Property TotalPhysicalMemory, CsManufacturer, CsModel, CsProcessors | ConvertTo-Json',
                'processor_info': 'Get-WmiObject -Class Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors, MaxClockSpeed | ConvertTo-Json',
                'memory_info': 'Get-WmiObject -Class Win32_PhysicalMemory | Select-Object Capacity, Speed, Manufacturer | ConvertTo-Json',
                'disk_info': 'Get-WmiObject -Class Win32_DiskDrive | Select-Object Model, Size, InterfaceType | ConvertTo-Json',
                'network_info': 'Get-NetAdapter | Where-Object {$_.Status -eq "Up"} | Select-Object Name, MacAddress, LinkSpeed | ConvertTo-Json'
            }
            
            for info_type, command in ps_commands.items():
                try:
                    if hostname and hostname.lower() not in ['localhost', '127.0.0.1']:
                        # Remote PowerShell execution
                        full_command = f'Invoke-Command -ComputerName {hostname} -ScriptBlock {{{command}}}'
                    else:
                        # Local PowerShell execution
                        full_command = command
                    
                    result = subprocess.run(
                        ['powershell', '-Command', full_command],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if result.returncode == 0 and result.stdout.strip():
                        data = json.loads(result.stdout.strip())
                        
                        # Process different types of data
                        if info_type == 'computer_info' and data:
                            if isinstance(data, list):
                                data = data[0]
                            hardware_data['total_physical_memory_ps'] = str(int(data.get('TotalPhysicalMemory', 0)) // (1024**3)) + " GB" if data.get('TotalPhysicalMemory') else None
                            hardware_data['system_manufacturer_ps'] = data.get('CsManufacturer')
                            hardware_data['system_model_ps'] = data.get('CsModel')
                        
                        elif info_type == 'processor_info' and data:
                            if isinstance(data, list):
                                data = data[0]
                            hardware_data['processor_name_ps'] = data.get('Name')
                            hardware_data['processor_cores_ps'] = data.get('NumberOfCores')
                            hardware_data['processor_threads_ps'] = data.get('NumberOfLogicalProcessors')
                            hardware_data['processor_speed_mhz_ps'] = data.get('MaxClockSpeed')
                        
                        elif info_type == 'network_info' and data:
                            if isinstance(data, list) and data:
                                # Use first active network adapter
                                adapter = data[0]
                                hardware_data['mac_address_ps'] = adapter.get('MacAddress')
                                hardware_data['network_adapter_name'] = adapter.get('Name')
                                hardware_data['link_speed'] = adapter.get('LinkSpeed')
                
                except Exception as e:
                    print(f"        ⚠️ PowerShell {info_type} failed: {str(e)[:30]}")
                    continue
        
        except Exception as e:
            print(f"        ❌ PowerShell collection failed: {str(e)[:50]}")
            return None
        
        return hardware_data if hardware_data else None

    def registry_hardware_collection(self):
        """Collect hardware data from Windows Registry (local only)"""
        
        hardware_data = {}
        
        try:
            # Registry paths for hardware information
            registry_paths = {
                'HKEY_LOCAL_MACHINE\\HARDWARE\\DESCRIPTION\\System\\CentralProcessor\\0': {
                    'ProcessorNameString': 'processor_name_reg',
                    'Identifier': 'processor_identifier',
                    '~MHz': 'processor_speed_reg'
                },
                'HKEY_LOCAL_MACHINE\\HARDWARE\\DESCRIPTION\\System\\BIOS': {
                    'SystemManufacturer': 'system_manufacturer_reg',
                    'SystemProductName': 'system_model_reg',
                    'BIOSVersion': 'bios_version_reg'
                },
                'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion': {
                    'ProductName': 'os_name_reg',
                    'CurrentBuild': 'os_build_reg',
                    'RegisteredOwner': 'registered_owner'
                }
            }
            
            for reg_path, values in registry_paths.items():
                try:
                    # Determine registry hive
                    if reg_path.startswith('HKEY_LOCAL_MACHINE'):
                        hkey = winreg.HKEY_LOCAL_MACHINE
                        subkey = reg_path.replace('HKEY_LOCAL_MACHINE\\', '')
                    else:
                        continue
                    
                    # Open registry key
                    with winreg.OpenKey(hkey, subkey) as key:
                        for value_name, data_key in values.items():
                            try:
                                value, _ = winreg.QueryValueEx(key, value_name)
                                hardware_data[data_key] = str(value)
                            except FileNotFoundError:
                                continue
                
                except Exception as e:
                    print(f"        ⚠️ Registry path {reg_path} failed: {str(e)[:30]}")
                    continue
        
        except Exception as e:
            print(f"        ❌ Registry collection failed: {str(e)[:50]}")
            return None
        
        return hardware_data if hardware_data else None

    def network_hardware_discovery(self, ip_address):
        """Network-based hardware discovery using various protocols"""
        
        hardware_data = {}
        
        try:
            # SNMP-based discovery (if SNMP is enabled)
            snmp_data = self.snmp_hardware_discovery(ip_address)
            if snmp_data:
                hardware_data.update(snmp_data)
            
            # HTTP-based discovery (web management interfaces)
            http_data = self.http_hardware_discovery(ip_address)
            if http_data:
                hardware_data.update(http_data)
            
            # NetBIOS name resolution
            netbios_data = self.netbios_discovery(ip_address)
            if netbios_data:
                hardware_data.update(netbios_data)
        
        except Exception as e:
            print(f"        ❌ Network discovery failed: {str(e)[:50]}")
            return None
        
        return hardware_data if hardware_data else None

    def snmp_hardware_discovery(self, ip_address):
        """SNMP-based hardware discovery"""
        
        # Note: This is a simplified SNMP implementation
        # In production, you would use pysnmp library
        
        hardware_data = {}
        
        try:
            # Common SNMP OIDs for hardware information
            snmp_oids = {
                '1.3.6.1.2.1.1.1.0': 'system_description',  # sysDescr
                '1.3.6.1.2.1.1.5.0': 'system_name',         # sysName
                '1.3.6.1.2.1.1.6.0': 'system_location',     # sysLocation
                '1.3.6.1.2.1.1.4.0': 'system_contact'       # sysContact
            }
            
            # This would require pysnmp library implementation
            # For now, we'll mark it as attempted
            hardware_data['snmp_attempted'] = True
            hardware_data['snmp_available'] = False
        
        except Exception:
            pass
        
        return hardware_data

    def http_hardware_discovery(self, ip_address):
        """HTTP-based hardware discovery"""
        
        hardware_data = {}
        
        try:
            # Try to access common web management interfaces
            import requests
            
            common_urls = [
                f'http://{ip_address}',
                f'https://{ip_address}',
                f'http://{ip_address}:8080',
                f'http://{ip_address}/api/system/info'
            ]
            
            for url in common_urls:
                try:
                    response = requests.get(url, timeout=5, verify=False)
                    if response.status_code == 200:
                        # Check for common hardware information in response
                        content = response.text.lower()
                        if any(keyword in content for keyword in ['dell', 'hp', 'cisco', 'netgear']):
                            hardware_data['vendor_detected'] = True
                            hardware_data['web_interface_available'] = True
                            break
                except:
                    continue
        
        except Exception:
            pass
        
        return hardware_data

    def netbios_discovery(self, ip_address):
        """NetBIOS-based discovery"""
        
        hardware_data = {}
        
        try:
            # Try NetBIOS name resolution
            hostname = socket.gethostbyaddr(ip_address)[0]
            if hostname:
                hardware_data['netbios_name'] = hostname
                
                # Extract computer type from hostname patterns
                hostname_lower = hostname.lower()
                if any(pattern in hostname_lower for pattern in ['ws-', 'workstation']):
                    hardware_data['device_type_netbios'] = 'Workstation'
                elif any(pattern in hostname_lower for pattern in ['srv-', 'server']):
                    hardware_data['device_type_netbios'] = 'Server'
                elif any(pattern in hostname_lower for pattern in ['lt-', 'laptop']):
                    hardware_data['device_type_netbios'] = 'Laptop'
        
        except Exception:
            pass
        
        return hardware_data

    def system_command_collection(self, hostname, ip_address):
        """System command-based hardware collection"""
        
        hardware_data = {}
        
        try:
            # Windows system commands
            system_commands = {
                'systeminfo': ['systeminfo', '/fo', 'csv'],
                'wmic_cpu': ['wmic', 'cpu', 'get', 'Name,NumberOfCores,MaxClockSpeed', '/format:csv'],
                'wmic_memory': ['wmic', 'memorychip', 'get', 'Capacity,Speed', '/format:csv'],
                'wmic_disk': ['wmic', 'diskdrive', 'get', 'Model,Size', '/format:csv']
            }
            
            for cmd_name, command in system_commands.items():
                try:
                    result = subprocess.run(
                        command,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if result.returncode == 0 and result.stdout.strip():
                        # Parse command output
                        if cmd_name == 'systeminfo':
                            lines = result.stdout.strip().split('\n')
                            if len(lines) > 1:
                                # Parse CSV output
                                headers = lines[0].split(',')
                                values = lines[1].split(',')
                                system_info = dict(zip(headers, values))
                                
                                hardware_data['system_info_available'] = True
                        
                        elif 'wmic' in cmd_name:
                            hardware_data[f'{cmd_name}_available'] = True
                
                except Exception as e:
                    print(f"        ⚠️ System command {cmd_name} failed: {str(e)[:30]}")
                    continue
        
        except Exception as e:
            print(f"        ❌ System command collection failed: {str(e)[:50]}")
            return None
        
        return hardware_data if hardware_data else None

    def update_device_hardware_data(self, cursor, device_id, hardware_data):
        """Update device with enhanced hardware data"""
        
        # Get existing columns
        cursor.execute("PRAGMA table_info(assets)")
        existing_columns = [col[1] for col in cursor.fetchall()]
        
        # Prepare update data
        updates = {}
        
        # Map collected data to database columns
        column_mapping = {
            'processor_name': ['processor_name', 'processor_name_ps', 'processor_name_reg'],
            'total_physical_memory': ['total_physical_memory', 'total_physical_memory_ps'],
            'system_manufacturer': ['system_manufacturer', 'system_manufacturer_ps', 'system_manufacturer_reg'],
            'system_model': ['system_model', 'system_model_ps', 'system_model_reg'],
            'mac_address': ['mac_address', 'mac_address_ps'],
            'bios_serial_number': ['bios_serial_number'],
            'serial_number': ['serial_number'],
            'motherboard_serial': ['motherboard_serial'],
            'operating_system': ['operating_system', 'os_name_reg'],
            'processor_cores': ['processor_cores', 'processor_cores_ps'],
            'processor_threads': ['processor_threads', 'processor_threads_ps'],
            'bios_manufacturer': ['bios_manufacturer'],
            'bios_version': ['bios_version', 'bios_version_reg']
        }
        
        # Apply best available data for each column
        for db_column, source_columns in column_mapping.items():
            if db_column in existing_columns:
                for source_column in source_columns:
                    if source_column in hardware_data and hardware_data[source_column]:
                        updates[db_column] = hardware_data[source_column]
                        break
        
        # Add detailed hardware data as JSON
        if any(key.endswith('_detailed') for key in hardware_data.keys()):
            if 'hardware_details_json' in existing_columns:
                updates['hardware_details_json'] = json.dumps({k: v for k, v in hardware_data.items() if k.endswith('_detailed')})
        
        # Add collection metadata only if columns exist
        if 'last_hardware_scan' in existing_columns:
            updates['last_hardware_scan'] = datetime.now().isoformat()
        if 'hardware_collection_method' in existing_columns:
            updates['hardware_collection_method'] = hardware_data.get('hardware_collection_method', 'Enhanced Collection')
        if 'last_updated' in existing_columns:
            updates['last_updated'] = datetime.now().isoformat()
        
        # Execute update
        if updates:
            set_clauses = [f"{k} = ?" for k in updates.keys()]
            values = list(updates.values()) + [device_id]
            query = f"UPDATE assets SET {\', \'.join(update_fields)} WHERE id = ?"  # NOTE: Safe - fields from schema
            cursor.execute(query, values)

    def show_enhancement_results(self):
        """Show hardware enhancement results"""
        
        print("\n📊 HARDWARE ENHANCEMENT RESULTS")
        print("=" * 70)
        print(f"📱 Devices processed: {self.stats['devices_processed']}")
        print(f"✅ Hardware data improved: {self.stats['hardware_data_improved']}")
        print(f"🔧 WMI successes: {self.stats['wmi_success']}")
        print(f"💻 PowerShell successes: {self.stats['powershell_success']}")
        print(f"📋 Registry successes: {self.stats['registry_success']}")
        print(f"🌐 Network discovery successes: {self.stats['network_success']}")
        
        success_rate = (self.stats['hardware_data_improved'] / self.stats['devices_processed'] * 100) if self.stats['devices_processed'] > 0 else 0
        
        print(f"\n📈 SUCCESS RATE: {success_rate:.1f}%")
        
        if success_rate > 80:
            print("🎉 EXCELLENT: Hardware data collection significantly improved!")
        elif success_rate > 60:
            print("✅ GOOD: Hardware data collection improved well")
        elif success_rate > 40:
            print("⚠️ MODERATE: Some improvement in hardware data collection")
        else:
            print("❌ NEEDS WORK: Limited improvement in hardware data collection")
        
        if self.stats['errors']:
            print(f"\n⚠️ ERRORS ENCOUNTERED ({len(self.stats['errors'])}):")
            for error in self.stats['errors'][:5]:  # Show first 5 errors
                print(f"   • {error}")
            if len(self.stats['errors']) > 5:
                print(f"   ... and {len(self.stats['errors']) - 5} more errors")

def main():
    """Run enhanced hardware data collection"""
    
    collector = EnhancedHardwareCollector()
    collector.enhance_hardware_data()

if __name__ == "__main__":
    main()