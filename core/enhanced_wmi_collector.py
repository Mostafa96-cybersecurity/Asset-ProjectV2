# -*- coding: utf-8 -*-
"""
Enhanced WMI Data Collector with Smart OS Detection
---------------------------------------------------
Collects comprehensive device information and assigns correct OS types
"""

import logging
import platform
import socket
from datetime import datetime
from typing import Dict, List, Optional, Any

log = logging.getLogger(__name__)

# Platform detection
_WMI_IMPORT_OK = False
pythoncom = None
wmi = None

def _on_windows() -> bool:
    return platform.system().lower().startswith("win")

try:
    if _on_windows():
        import pythoncom
        import wmi
        _WMI_IMPORT_OK = True
    else:
        log.info("WMI collector disabled: non-Windows platform.")
except Exception as e:
    log.warning("WMI collector unavailable: %s", e)
    _WMI_IMPORT_OK = False


class EnhancedWMICollector:
    """Enhanced WMI collector with smart OS detection and comprehensive data collection"""
    
    def __init__(self):
        self.connection_cache = {}
        self.device_classifications = {
            'server_keywords': ['server', 'srv', 'dc-', 'sql', 'exchange', 'sharepoint', 'domain'],
            'workstation_keywords': ['desktop', 'pc-', 'ws-', 'laptop', 'lt-', 'nb-'],
            'virtual_keywords': ['vm-', 'virtual', 'vmware', 'hyper-v', 'virtualbox', 'vbox']
        }
    
    def collect_comprehensive_data(self, ip_address: str, username: Optional[str] = None, 
                                 password: Optional[str] = None, domain: Optional[str] = None) -> Dict[str, Any]:
        """
        Collect comprehensive device data with smart OS detection
        
        Returns dict with standardized fields:
        - hostname: Real device hostname (not IP)
        - working_user: Currently logged user
        - domain: Domain information
        - device_model: Hardware model
        - device_infrastructure: Classification (Server/Workstation/Virtual)
        - os_name: Full OS name and version
        - installed_ram_gb: Memory in GB
        - lan_ip_address: IP address
        - storage: Storage information
        - manufacturer: Hardware manufacturer
        - serial_number: Serial number
        - processor: CPU information
        - system_sku: System SKU
        - active_gpu: Graphics card
        - connected_screens: Monitor count
        - device_type: Smart classification
        - collection_method: How data was collected
        """
        
        result = {
            'hostname': ip_address,
            'working_user': 'N/A',
            'domain': 'N/A',
            'device_model': 'Unknown',
            'device_infrastructure': 'Unknown',
            'os_name': 'Unknown',
            'installed_ram_gb': 0,
            'lan_ip_address': ip_address,
            'storage': 'Unknown',
            'manufacturer': 'Unknown',
            'serial_number': 'Unknown',
            'processor': 'Unknown',
            'system_sku': 'Unknown',
            'active_gpu': 'Unknown',
            'connected_screens': 0,
            'device_type': 'Unknown',
            'collection_method': 'WMI Collection',
            'collection_timestamp': datetime.now().isoformat(),
            'collection_quality': 'Standard'
        }
        
        if not _WMI_IMPORT_OK:
            result['collection_method'] = 'WMI Unavailable'
            return result
        
        try:
            # Initialize COM
            if not _WMI_IMPORT_OK:
                return {'error': 'WMI not available', 'success': False}
            
            username = username or ''
            password = password or ''
            domain = domain or ''
            
            if pythoncom:
                try:
                    # Use getattr to safely access CoInitialize
                    co_init = getattr(pythoncom, 'CoInitialize', None)
                    if co_init and callable(co_init):
                        co_init()
                    else:
                        # Alternative COM initialization method if available
                        pass
                except:
                    pass  # COM already initialized
                
            # Get WMI connection
            wmi_conn = self._get_wmi_connection(ip_address, username, password, domain)
            if not wmi_conn:
                result['collection_method'] = 'WMI Connection Failed'
                return result
            
            # Collect system information
            if hasattr(wmi_conn, 'Win32_ComputerSystem'):
                self._collect_system_info(wmi_conn, result)
            else:
                result['collection_method'] = 'WMI Connection Invalid'
                return result
            
            # Collect hardware information
            self._collect_hardware_info(wmi_conn, result)
            
            # Collect user information
            self._collect_user_info(wmi_conn, result)
            
            # Collect network information
            self._collect_network_info(wmi_conn, result)
            
            # Collect OS information
            self._collect_os_info(wmi_conn, result)
            
            # Smart device classification
            self._classify_device(result)
            
            # Quality assessment
            self._assess_collection_quality(result)
            
            result['collection_method'] = 'Enhanced WMI Collection'
            log.info(f"Successfully collected enhanced data for {result['hostname']}")
            
        except Exception as e:
            log.error(f"WMI collection error for {ip_address}: {e}")
            result['collection_method'] = f'WMI Error: {str(e)[:50]}'
        
        finally:
            try:
                if pythoncom:
                    pass  # Let COM handle cleanup automatically
            except:
                pass
        
        return result
    
    def _get_wmi_connection(self, ip_address: str, username: Optional[str] = None, 
                           password: Optional[str] = None, domain: Optional[str] = None):
        """Get WMI connection with caching"""
        
        # Use localhost connection if targeting local machine
        if ip_address in ['127.0.0.1', 'localhost', socket.gethostname()]:
            try:
                if _WMI_IMPORT_OK and wmi:
                    return wmi.WMI()
                else:
                    log.error("WMI not available for local connection")
                    return None
            except Exception as e:
                log.error(f"Local WMI connection failed: {e}")
                return None
        
        # Remote connection
        cache_key = f"{ip_address}:{username}:{domain}"
        if cache_key in self.connection_cache:
            try:
                # Test if connection is still valid
                cached_conn = self.connection_cache[cache_key]
                if cached_conn and hasattr(cached_conn, 'Win32_ComputerSystem'):
                    cached_conn.Win32_ComputerSystem()
                    return cached_conn
                else:
                    # Invalid connection, remove from cache
                    del self.connection_cache[cache_key]
            except:
                # Connection expired, remove from cache
                del self.connection_cache[cache_key]
        
        try:
            if not _WMI_IMPORT_OK or not wmi:
                log.error("WMI not available for remote connection")
                return None
                
            if username and password:
                if domain:
                    full_username = f"{domain}\\{username}"
                else:
                    full_username = username
                
                wmi_conn = wmi.WMI(computer=ip_address, 
                                  user=full_username, 
                                  password=password)
            else:
                wmi_conn = wmi.WMI(computer=ip_address)
            
            # Cache the connection
            self.connection_cache[cache_key] = wmi_conn
            return wmi_conn
            
        except Exception as e:
            log.error(f"Remote WMI connection failed for {ip_address}: {e}")
            return None
    
    def _collect_system_info(self, wmi_conn, result: Dict[str, Any]):
        """Collect basic system information"""
        try:
            # Computer system information
            for computer in wmi_conn.Win32_ComputerSystem():
                result['hostname'] = computer.Name or result['hostname']
                result['manufacturer'] = computer.Manufacturer or 'Unknown'
                result['device_model'] = computer.Model or 'Unknown'
                result['domain'] = computer.Domain or computer.Workgroup or 'N/A'
                
                # Calculate total RAM
                if computer.TotalPhysicalMemory:
                    ram_gb = int(computer.TotalPhysicalMemory) / (1024**3)
                    result['installed_ram_gb'] = round(ram_gb, 2)
                
                # System type detection
                if computer.SystemType:
                    if 'server' in computer.SystemType.lower():
                        result['device_infrastructure'] = 'Server'
                    elif any(keyword in computer.SystemType.lower() for keyword in ['x64', 'x86']):
                        result['device_infrastructure'] = 'Workstation'
            
            # BIOS information for serial number and more details
            for bios in wmi_conn.Win32_BIOS():
                if bios.SerialNumber and bios.SerialNumber.strip():
                    result['serial_number'] = bios.SerialNumber.strip()
                if bios.SMBIOSBIOSVersion:
                    result['bios_version'] = bios.SMBIOSBIOSVersion
            
            # Motherboard information
            for board in wmi_conn.Win32_BaseBoard():
                if board.SerialNumber and board.SerialNumber.strip() and result['serial_number'] == 'Unknown':
                    result['serial_number'] = board.SerialNumber.strip()
                if board.Product:
                    result['motherboard_model'] = board.Product
            
            # System enclosure for additional serial
            for enclosure in wmi_conn.Win32_SystemEnclosure():
                if enclosure.SerialNumber and enclosure.SerialNumber.strip() and result['serial_number'] == 'Unknown':
                    result['serial_number'] = enclosure.SerialNumber.strip()
                if enclosure.SMBIOSAssetTag:
                    result['asset_tag'] = enclosure.SMBIOSAssetTag
            
        except Exception as e:
            log.error(f"Error collecting system info: {e}")
    
    def _collect_hardware_info(self, wmi_conn, result: Dict[str, Any]):
        """Collect detailed hardware information"""
        try:
            # Processor information
            processors = []
            for processor in wmi_conn.Win32_Processor():
                if processor.Name:
                    processors.append(processor.Name.strip())
                if processor.NumberOfCores:
                    result['cpu_cores'] = processor.NumberOfCores
                if processor.NumberOfLogicalProcessors:
                    result['cpu_logical_processors'] = processor.NumberOfLogicalProcessors
            
            if processors:
                result['processor'] = '; '.join(set(processors))
            
            # Memory modules
            memory_modules = []
            total_memory = 0
            for memory in wmi_conn.Win32_PhysicalMemory():
                if memory.Capacity:
                    capacity_gb = int(memory.Capacity) / (1024**3)
                    total_memory += capacity_gb
                    
                    speed = f" {memory.Speed}MHz" if memory.Speed else ""
                    manufacturer = f" {memory.Manufacturer}" if memory.Manufacturer else ""
                    module_info = f"{capacity_gb:.0f}GB{speed}{manufacturer}"
                    memory_modules.append(module_info)
            
            if memory_modules:
                result['memory_modules'] = '; '.join(memory_modules)
                result['installed_ram_gb'] = round(total_memory, 2)
            
            # Storage information
            storage_devices = []
            total_storage = 0
            for disk in wmi_conn.Win32_DiskDrive():
                if disk.Size:
                    size_gb = int(disk.Size) / (1024**3)
                    total_storage += size_gb
                    
                    model = disk.Model or "Unknown Drive"
                    interface = f" ({disk.InterfaceType})" if disk.InterfaceType else ""
                    storage_info = f"{model}: {size_gb:.0f}GB{interface}"
                    storage_devices.append(storage_info)
            
            if storage_devices:
                result['storage'] = '; '.join(storage_devices)
                result['total_storage_gb'] = round(total_storage, 2)
            
            # Graphics cards
            gpu_cards = []
            for gpu in wmi_conn.Win32_VideoController():
                if gpu.Name and 'microsoft' not in gpu.Name.lower():
                    gpu_info = gpu.Name
                    if gpu.AdapterRAM:
                        gpu_ram_mb = int(gpu.AdapterRAM) / (1024**2)
                        if gpu_ram_mb > 100:  # Only show if significant
                            gpu_info += f" ({gpu_ram_mb:.0f}MB)"
                    gpu_cards.append(gpu_info)
            
            if gpu_cards:
                result['active_gpu'] = '; '.join(gpu_cards)
            
            # Monitor count
            monitor_count = 0
            monitors = []
            for monitor in wmi_conn.Win32_DesktopMonitor():
                if monitor.Name:
                    monitor_count += 1
                    monitors.append(monitor.Name)
            
            result['connected_screens'] = monitor_count
            if monitors:
                result['monitor_details'] = '; '.join(monitors)
            
        except Exception as e:
            log.error(f"Error collecting hardware info: {e}")
    
    def _collect_user_info(self, wmi_conn, result: Dict[str, Any]):
        """Collect current user information"""
        try:
            # Currently logged on users
            logged_users = []
            for session in wmi_conn.Win32_LogonSession():
                if session.LogonType == 2:  # Interactive logon
                    for user in wmi_conn.Win32_LoggedOnUser():
                        if user.Dependent.LogonId == session.LogonId:
                            username = user.Antecedent.Name
                            domain = user.Antecedent.Domain
                            if username and username.lower() not in ['system', 'local service', 'network service']:
                                if domain and domain.lower() != 'nt authority':
                                    logged_users.append(f"{domain}\\{username}")
                                else:
                                    logged_users.append(username)
            
            if logged_users:
                result['working_user'] = '; '.join(set(logged_users))
            
            # Alternative method for current user
            if result['working_user'] == 'N/A':
                try:
                    for process in wmi_conn.Win32_Process():
                        if process.Name == 'explorer.exe':
                            owner = process.GetOwner()
                            if owner and owner[0]:
                                user = owner[0]
                                domain = owner[1] if owner[1] else ''
                                if domain:
                                    result['working_user'] = f"{domain}\\{user}"
                                else:
                                    result['working_user'] = user
                                break
                except:
                    pass
            
        except Exception as e:
            log.error(f"Error collecting user info: {e}")
    
    def _collect_network_info(self, wmi_conn, result: Dict[str, Any]):
        """Collect network configuration information"""
        try:
            network_adapters = []
            for adapter in wmi_conn.Win32_NetworkAdapterConfiguration():
                if adapter.IPEnabled and adapter.IPAddress:
                    adapter_info = {
                        'description': adapter.Description,
                        'ip_addresses': adapter.IPAddress,
                        'mac_address': adapter.MACAddress,
                        'dhcp_enabled': adapter.DHCPEnabled,
                        'dns_servers': adapter.DNSServerSearchOrder
                    }
                    network_adapters.append(adapter_info)
                    
                    # Update main IP if this is a primary adapter
                    if adapter.IPAddress and adapter.IPAddress[0] != '127.0.0.1':
                        result['lan_ip_address'] = adapter.IPAddress[0]
                        if adapter.MACAddress:
                            result['mac_address'] = adapter.MACAddress
            
            result['network_adapters'] = network_adapters
            result['network_adapter_count'] = len(network_adapters)
            
        except Exception as e:
            log.error(f"Error collecting network info: {e}")
    
    def _collect_os_info(self, wmi_conn, result: Dict[str, Any]):
        """Collect operating system information"""
        try:
            for os in wmi_conn.Win32_OperatingSystem():
                if os.Caption:
                    os_name = os.Caption
                    if os.Version:
                        os_name += f" (Version {os.Version})"
                    if os.ServicePackMajorVersion:
                        os_name += f" SP{os.ServicePackMajorVersion}"
                    result['os_name'] = os_name
                
                if os.TotalVirtualMemorySize and os.TotalVisibleMemorySize:
                    virtual_memory_gb = int(os.TotalVirtualMemorySize) / (1024**2)
                    result['virtual_memory_gb'] = round(virtual_memory_gb, 2)
                
                if os.InstallDate:
                    result['os_install_date'] = os.InstallDate
                
                if os.LastBootUpTime:
                    result['last_boot_time'] = os.LastBootUpTime
                
                # Architecture
                if os.OSArchitecture:
                    result['os_architecture'] = os.OSArchitecture
                
        except Exception as e:
            log.error(f"Error collecting OS info: {e}")
    
    def _classify_device(self, result: Dict[str, Any]):
        """Smart device classification based on collected data"""
        hostname = result.get('hostname', '').lower()
        os_name = result.get('os_name', '').lower()
        device_model = result.get('device_model', '').lower()
        
        # Virtual machine detection
        if any(keyword in hostname for keyword in self.device_classifications['virtual_keywords']) or \
           any(keyword in device_model for keyword in ['virtual', 'vmware', 'hyper-v']):
            result['device_infrastructure'] = 'Virtual Machine'
            result['device_type'] = 'Virtual Machine'
            return
        
        # Server detection
        if 'server' in os_name or \
           any(keyword in hostname for keyword in self.device_classifications['server_keywords']):
            result['device_infrastructure'] = 'Server'
            
            # Determine server type
            if 'domain controller' in os_name or 'dc-' in hostname:
                result['device_type'] = 'Domain Controller'
            elif 'sql' in hostname or 'database' in hostname:
                result['device_type'] = 'Database Server'
            elif 'exchange' in hostname or 'mail' in hostname:
                result['device_type'] = 'Mail Server'
            elif 'web' in hostname or 'iis' in hostname:
                result['device_type'] = 'Web Server'
            else:
                result['device_type'] = 'Server'
            return
        
        # Workstation detection
        if any(keyword in hostname for keyword in self.device_classifications['workstation_keywords']) or \
           'windows 10' in os_name or 'windows 11' in os_name:
            result['device_infrastructure'] = 'Workstation'
            
            # Determine workstation type
            if 'laptop' in device_model.lower() or 'notebook' in device_model.lower() or \
               'lt-' in hostname or 'nb-' in hostname:
                result['device_type'] = 'Laptop'
            else:
                result['device_type'] = 'Desktop'
            return
        
        # Default classification
        if 'windows' in os_name:
            if 'server' in os_name:
                result['device_infrastructure'] = 'Server'
                result['device_type'] = 'Server'
            else:
                result['device_infrastructure'] = 'Workstation'
                result['device_type'] = 'Workstation'
        else:
            result['device_infrastructure'] = 'Unknown'
            result['device_type'] = 'Unknown'
    
    def _assess_collection_quality(self, result: Dict[str, Any]):
        """Assess the quality of collected data"""
        quality_score = 0
        max_score = 10
        
        # Check key fields
        if result['hostname'] != result['lan_ip_address'] and not result['hostname'].replace('.', '').isdigit():
            quality_score += 2  # Real hostname
        
        if result['working_user'] != 'N/A':
            quality_score += 2  # User information
        
        if result['serial_number'] != 'Unknown':
            quality_score += 1  # Serial number
        
        if result['manufacturer'] != 'Unknown':
            quality_score += 1  # Manufacturer
        
        if result['device_model'] != 'Unknown':
            quality_score += 1  # Device model
        
        if result['processor'] != 'Unknown':
            quality_score += 1  # Processor info
        
        if result['installed_ram_gb'] > 0:
            quality_score += 1  # Memory info
        
        if result['storage'] != 'Unknown':
            quality_score += 1  # Storage info
        
        # Quality assessment
        quality_percentage = (quality_score / max_score) * 100
        
        if quality_percentage >= 80:
            result['collection_quality'] = 'Excellent'
        elif quality_percentage >= 60:
            result['collection_quality'] = 'Good'
        elif quality_percentage >= 40:
            result['collection_quality'] = 'Fair'
        else:
            result['collection_quality'] = 'Poor'
        
        result['quality_score'] = quality_percentage


# Global instance
enhanced_wmi_collector = EnhancedWMICollector()

def collect_enhanced_wmi_data(ip_address: str, username: Optional[str] = None, 
                             password: Optional[str] = None, domain: Optional[str] = None) -> Dict[str, Any]:
    """
    Main function to collect enhanced WMI data
    
    Returns comprehensive device information with smart OS detection
    """
    return enhanced_wmi_collector.collect_comprehensive_data(ip_address, username, password, domain)


def test_enhanced_collection():
    """Test the enhanced collection on local machine"""
    print("🔍 Testing Enhanced WMI Collection...")
    
    # Test local collection
    result = collect_enhanced_wmi_data('127.0.0.1')
    
    print(f"\n📊 Collection Results:")
    print(f"🖥️  Hostname: {result['hostname']}")
    print(f"👤 Working User: {result['working_user']}")
    print(f"🏢 Domain: {result['domain']}")
    print(f"💻 Device Model: {result['device_model']}")
    print(f"🏗️  Infrastructure: {result['device_infrastructure']}")
    print(f"🔧 Device Type: {result['device_type']}")
    print(f"💿 OS: {result['os_name']}")
    print(f"🧠 RAM: {result['installed_ram_gb']} GB")
    print(f"🏭 Manufacturer: {result['manufacturer']}")
    print(f"🔢 Serial: {result['serial_number']}")
    print(f"⚡ Processor: {result['processor']}")
    print(f"🎮 GPU: {result['active_gpu']}")
    print(f"📺 Screens: {result['connected_screens']}")
    print(f"💾 Storage: {result['storage']}")
    print(f"📊 Quality: {result['collection_quality']} ({result.get('quality_score', 0):.1f}%)")
    print(f"🔧 Method: {result['collection_method']}")
    
    return result


if __name__ == "__main__":
    test_enhanced_collection()