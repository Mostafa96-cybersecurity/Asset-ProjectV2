# -*- coding: utf-8 -*-
"""
Intelligent Device Collection System
===================================
Advanced device collection system with:
- Automatic OS detection via nmap
- Protocol selection based on device type (WMI/SSH/SNMP)
- Comprehensive vendor management
- Database integration with classification
- Real-time synchronization

Device Types & Collection Methods:
- Windows/Windows Server: WMI (pythoncom, wmi)
- Linux: SSH (paramiko)
- Hypervisor: SNMP (pysnmp)
- Switches: SSH/SNMP (paramiko/pysnmp)
- Access Points: SNMP (pysnmp)
- Fingerprint Devices: SNMP (pysnmp)
- Printers: SNMP (pysnmp)
"""

import socket
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

# Network and device detection
try:
    import nmap
    NMAP_AVAILABLE = True
except ImportError:
    NMAP_AVAILABLE = False

# Windows WMI support
try:
    import pythoncom
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False

# SSH support for Linux/Network devices
try:
    import paramiko
    SSH_AVAILABLE = True
except ImportError:
    SSH_AVAILABLE = False

# SNMP support for network devices
try:
    from pysnmp.hlapi import (
        getCmd, nextCmd, SnmpEngine, UdpTransportTarget, ContextData,
        ObjectType, ObjectIdentity, CommunityData
    )
    SNMP_AVAILABLE = True
except ImportError:
    SNMP_AVAILABLE = False

logger = logging.getLogger(__name__)

class IntelligentDeviceCollector:
    """Intelligent device collector with automatic protocol detection"""
    
    # Device type mapping to collection methods
    DEVICE_TYPES = {
        'Windows': 'WMI',
        'Windows Server': 'WMI', 
        'Linux': 'SSH',
        'Hypervisor': 'SNMP',
        'Switches': 'SSH/SNMP',
        'AP': 'SNMP',
        'Fingerprint': 'SNMP',
        'Printers': 'SNMP'
    }
    
    # Common vendors for dropdown
    COMMON_VENDORS = [
        'Dell', 'HP', 'Lenovo', 'Microsoft', 'Cisco', 'VMware',
        'Juniper', 'Fortinet', 'Palo Alto', 'Ubiquiti', 'Netgear',
        'D-Link', 'TP-Link', 'Canon', 'Epson', 'Xerox', 'Brother',
        'HID', 'ZKTeco', 'Suprema', 'Hikvision', 'Other'
    ]
    
    def __init__(self):
        self.nmap_scanner = None
        if NMAP_AVAILABLE:
            try:
                self.nmap_scanner = nmap.PortScanner()
                logger.info("✅ nmap scanner initialized")
            except Exception as e:
                logger.warning(f"nmap scanner initialization failed: {e}")
        else:
            logger.warning("⚠️  nmap not available - using fallback OS detection")
    
    def detect_device_os_and_type(self, ip_address: str) -> Tuple[str, str]:
        """
        Detect device OS and determine device type using nmap
        Returns: (os_name, device_type)
        """
        logger.info(f"🔍 Detecting OS and device type for {ip_address}...")
        
        try:
            # Use nmap for OS detection if available
            if self.nmap_scanner:
                return self._nmap_os_detection(ip_address)
            else:
                return self._fallback_detection(ip_address)
                
        except Exception as e:
            logger.error(f"OS detection failed for {ip_address}: {e}")
            return "Unknown", "Unknown"
    
    def _nmap_os_detection(self, ip_address: str) -> Tuple[str, str]:
        """Use nmap for comprehensive OS and device detection"""
        try:
            # Comprehensive nmap scan with OS detection
            scan_result = self.nmap_scanner.scan(
                ip_address, 
                '22,23,53,80,135,139,161,443,445,993,995,3389,5985',
                arguments='-O -sV --version-intensity 5'
            )
            
            if ip_address not in scan_result['scan']:
                return "Unknown", "Unknown"
            
            host_info = scan_result['scan'][ip_address]
            
            # Extract OS information
            os_name = "Unknown"
            device_type = "Unknown"
            
            if 'osmatch' in host_info and host_info['osmatch']:
                os_match = host_info['osmatch'][0]
                os_name = os_match.get('name', 'Unknown')
                
                # Determine device type based on OS and open ports
                device_type = self._classify_device_type(os_name, host_info.get('tcp', {}))
            
            logger.info(f"✅ Detected: {os_name} → {device_type}")
            return os_name, device_type
            
        except Exception as e:
            logger.error(f"nmap OS detection failed: {e}")
            return self._fallback_detection(ip_address)
    
    def _fallback_detection(self, ip_address: str) -> Tuple[str, str]:
        """Fallback detection using port scanning"""
        try:
            open_ports = self._simple_port_scan(ip_address)
            
            # Basic classification based on open ports
            if 135 in open_ports or 139 in open_ports or 445 in open_ports:
                if 3389 in open_ports:
                    return "Windows Server", "Windows Server"
                else:
                    return "Windows", "Windows"
            elif 22 in open_ports:
                return "Linux", "Linux"
            elif 161 in open_ports:
                if 80 in open_ports or 443 in open_ports:
                    return "Network Device", "Switches"
                else:
                    return "Network Device", "Printers"
            else:
                return "Unknown", "Unknown"
                
        except Exception as e:
            logger.error(f"Fallback detection failed: {e}")
            return "Unknown", "Unknown"
    
    def _simple_port_scan(self, ip_address: str, ports: Optional[List[int]] = None) -> List[int]:
        """Simple port scanner for fallback detection"""
        if ports is None:
            ports = [22, 23, 53, 80, 135, 139, 161, 443, 445, 3389]
        
        open_ports = []
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((ip_address, port))
                if result == 0:
                    open_ports.append(port)
                sock.close()
            except:
                pass
        
        return open_ports
    
    def _classify_device_type(self, os_name: str, open_ports: Dict) -> str:
        """Classify device type based on OS name and open ports"""
        os_lower = os_name.lower()
        
        # Windows detection
        if 'windows' in os_lower:
            if 'server' in os_lower or any(port in open_ports for port in [3389, 5985]):
                return 'Windows Server'
            else:
                return 'Windows'
        
        # Linux detection
        elif 'linux' in os_lower or 'unix' in os_lower:
            return 'Linux'
        
        # VMware/Hypervisor detection
        elif 'vmware' in os_lower or 'esx' in os_lower or 'hypervisor' in os_lower:
            return 'Hypervisor'
        
        # Network device detection
        elif any(keyword in os_lower for keyword in ['cisco', 'juniper', 'switch', 'router']):
            return 'Switches'
        
        # Printer detection
        elif any(keyword in os_lower for keyword in ['printer', 'canon', 'hp', 'epson', 'xerox']):
            return 'Printers'
        
        # Access Point detection
        elif any(keyword in os_lower for keyword in ['ubiquiti', 'unifi', 'access point', 'ap']):
            return 'AP'
        
        # Default to network device if SNMP port is open
        elif 161 in open_ports:
            return 'Switches'
        
        else:
            return 'Unknown'
    
    def collect_device_data(self, ip_address: str, device_type: Optional[str] = None, 
                          credentials: Optional[Dict] = None) -> Optional[Dict]:
        """
        Collect comprehensive device data using appropriate protocol
        """
        logger.info(f"📦 Starting data collection for {ip_address}...")
        
        # Auto-detect if device type not provided
        if not device_type or device_type == 'Unknown':
            _, device_type = self.detect_device_os_and_type(ip_address)
        
        # Select collection method based on device type
        collection_method = self.DEVICE_TYPES.get(device_type, 'SNMP')
        
        logger.info(f"📊 Using {collection_method} for {device_type} device")
        
        try:
            if collection_method == 'WMI':
                return self._collect_wmi_data(ip_address, credentials)
            elif collection_method == 'SSH':
                return self._collect_ssh_data(ip_address, credentials)
            elif collection_method in ['SNMP', 'SSH/SNMP']:
                return self._collect_snmp_data(ip_address, credentials)
            else:
                logger.warning(f"Unknown collection method: {collection_method}")
                return None
                
        except Exception as e:
            logger.error(f"Data collection failed for {ip_address}: {e}")
            return None
    
    def _collect_wmi_data(self, ip_address: str, credentials: Optional[Dict] = None) -> Optional[Dict]:
        """Collect data from Windows devices using WMI"""
        if not WMI_AVAILABLE:
            logger.error("WMI not available - install pywin32 and wmi")
            return None
        
        logger.info(f"🪟 Collecting WMI data from {ip_address}")
        
        try:
            # Initialize COM for threading
            pythoncom.CoInitialize()
            
            # Connect to WMI
            if ip_address in ['localhost', '127.0.0.1'] or not credentials:
                # Local connection
                c = wmi.WMI()
            else:
                # Remote connection
                username = credentials.get('windows', {}).get('username', '')
                password = credentials.get('windows', {}).get('password', '')
                
                c = wmi.WMI(computer=ip_address, user=username, password=password)
            
            # Comprehensive WMI data collection
            device_data = {
                'ip_address': ip_address,
                'data_source': 'WMI Collection',
                'collected_at': datetime.now().isoformat(),
                'device_type': 'Windows' if 'server' not in str(c.Win32_OperatingSystem()[0].Caption).lower() else 'Windows Server'
            }
            
            # System Information
            for system in c.Win32_ComputerSystem():
                device_data.update({
                    'hostname': system.Name,
                    'working_user': system.UserName,
                    'domain': system.Domain,
                    'model_vendor': f"{system.Manufacturer} {system.Model}",
                    'manufacturer': system.Manufacturer,
                    'total_ram_gb': int(system.TotalPhysicalMemory) // (1024**3) if system.TotalPhysicalMemory else 0
                })
            
            # Operating System
            for os_info in c.Win32_OperatingSystem():
                device_data.update({
                    'os_name': os_info.Caption,
                    'os_version': os_info.Version,
                    'os_architecture': os_info.OSArchitecture,
                    'last_boot_time': str(os_info.LastBootUpTime) if os_info.LastBootUpTime else None
                })
            
            # Processor Information
            processors = []
            for processor in c.Win32_Processor():
                processors.append({
                    'name': processor.Name,
                    'cores': processor.NumberOfCores,
                    'threads': processor.NumberOfLogicalProcessors,
                    'max_speed': processor.MaxClockSpeed
                })
            
            if processors:
                device_data['processor'] = processors[0]['name']
                device_data['cpu_cores'] = processors[0]['cores']
                device_data['cpu_threads'] = processors[0]['threads']
            
            # Memory Information
            total_memory = 0
            for memory in c.Win32_PhysicalMemory():
                if memory.Capacity:
                    total_memory += int(memory.Capacity)
            
            device_data['installed_ram_gb'] = total_memory // (1024**3) if total_memory else 0
            
            # Storage Information
            disks = []
            for disk in c.Win32_DiskDrive():
                if disk.Size:
                    size_gb = int(disk.Size) // (1024**3)
                    disks.append(f"{disk.Model} ({size_gb}GB)")
            
            device_data['storage'] = " | ".join(disks) if disks else None
            
            # Network Information
            network_adapters = []
            for adapter in c.Win32_NetworkAdapterConfiguration():
                if adapter.IPEnabled and adapter.IPAddress:
                    network_adapters.append({
                        'description': adapter.Description,
                        'ip_address': adapter.IPAddress[0] if adapter.IPAddress else None,
                        'mac_address': adapter.MACAddress
                    })
            
            if network_adapters:
                device_data['primary_mac'] = network_adapters[0].get('mac_address')
                device_data['all_mac_addresses'] = [a.get('mac_address') for a in network_adapters if a.get('mac_address')]
            
            # Graphics Information
            for gpu in c.Win32_VideoController():
                if gpu.Name:
                    device_data['active_gpu'] = gpu.Name
                    break
            
            # Serial Number
            for bios in c.Win32_BIOS():
                device_data['serial_number'] = bios.SerialNumber
                break
            
            # System SKU
            for product in c.Win32_ComputerSystemProduct():
                device_data['system_sku'] = product.UUID
                break
            
            logger.info(f"✅ WMI data collection successful for {device_data.get('hostname', ip_address)}")
            return device_data
            
        except Exception as e:
            logger.error(f"WMI collection failed for {ip_address}: {e}")
            return None
        finally:
            try:
                pythoncom.CoUninitialize()
            except:
                pass
    
    def _collect_ssh_data(self, ip_address: str, credentials: Optional[Dict] = None) -> Optional[Dict]:
        """Collect data from Linux devices using SSH"""
        if not SSH_AVAILABLE:
            logger.error("SSH not available - install paramiko")
            return None
        
        logger.info(f"🐧 Collecting SSH data from {ip_address}")
        
        if not credentials or 'linux' not in credentials:
            logger.error("Linux SSH credentials required")
            return None
        
        try:
            ssh_creds = credentials['linux']
            username = ssh_creds.get('username')
            password = ssh_creds.get('password')
            
            if not username or not password:
                logger.error("SSH username and password required")
                return None
            
            # SSH Connection
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip_address, username=username, password=password, timeout=30)
            
            device_data = {
                'ip_address': ip_address,
                'data_source': 'SSH Collection',
                'collected_at': datetime.now().isoformat(),
                'device_type': 'Linux'
            }
            
            # System Information Commands
            commands = {
                'hostname': 'hostname',
                'os_name': 'cat /etc/os-release | grep PRETTY_NAME | cut -d= -f2 | tr -d \'"\'',
                'kernel_version': 'uname -r',
                'architecture': 'uname -m',
                'cpu_info': 'cat /proc/cpuinfo | grep "model name" | head -1 | cut -d: -f2 | sed "s/^ *//"',
                'cpu_cores': 'nproc',
                'memory_info': 'cat /proc/meminfo | grep MemTotal | awk \'{print $2}\'',
                'disk_info': 'df -h | grep -v tmpfs | grep -v udev | tail -n +2',
                'network_info': 'ip addr show | grep "inet " | grep -v "127.0.0.1"',
                'uptime': 'uptime -p',
                'current_user': 'whoami'
            }
            
            # Execute commands and collect data
            for key, command in commands.items():
                try:
                    stdin, stdout, stderr = ssh.exec_command(command)
                    output = stdout.read().decode('utf-8').strip()
                    
                    if key == 'hostname':
                        device_data['hostname'] = output
                    elif key == 'os_name':
                        device_data['os_name'] = output
                    elif key == 'kernel_version':
                        device_data['os_version'] = output
                    elif key == 'architecture':
                        device_data['os_architecture'] = output
                    elif key == 'cpu_info':
                        device_data['processor'] = output
                    elif key == 'cpu_cores':
                        device_data['cpu_cores'] = int(output) if output.isdigit() else 0
                    elif key == 'memory_info':
                        # Convert KB to GB
                        mem_kb = int(output) if output.isdigit() else 0
                        device_data['installed_ram_gb'] = mem_kb // (1024 * 1024)
                    elif key == 'disk_info':
                        device_data['storage'] = output.replace('\n', ' | ')
                    elif key == 'uptime':
                        device_data['uptime'] = output
                    elif key == 'current_user':
                        device_data['working_user'] = output
                        
                except Exception as cmd_error:
                    logger.warning(f"Command '{command}' failed: {cmd_error}")
                    continue
            
            # Network interface information
            try:
                stdin, stdout, stderr = ssh.exec_command("cat /sys/class/net/*/address 2>/dev/null | head -5")
                mac_addresses = [line.strip() for line in stdout.read().decode('utf-8').split('\n') if line.strip()]
                if mac_addresses:
                    device_data['primary_mac'] = mac_addresses[0]
                    device_data['all_mac_addresses'] = mac_addresses
            except:
                pass
            
            # System manufacturer (if available)
            try:
                stdin, stdout, stderr = ssh.exec_command("sudo dmidecode -s system-manufacturer 2>/dev/null || echo 'Unknown'")
                manufacturer = stdout.read().decode('utf-8').strip()
                if manufacturer and manufacturer != 'Unknown':
                    device_data['manufacturer'] = manufacturer
            except:
                pass
            
            ssh.close()
            
            logger.info(f"✅ SSH data collection successful for {device_data.get('hostname', ip_address)}")
            return device_data
            
        except Exception as e:
            logger.error(f"SSH collection failed for {ip_address}: {e}")
            return None
    
    def _collect_snmp_data(self, ip_address: str, credentials: Optional[Dict] = None) -> Optional[Dict]:
        """Collect data from network devices using SNMP"""
        if not SNMP_AVAILABLE:
            logger.error("SNMP not available - install pysnmp")
            return None
        
        logger.info(f"📡 Collecting SNMP data from {ip_address}")
        
        community = 'public'
        if credentials and 'snmp' in credentials:
            community = credentials['snmp'].get('community', 'public')
        
        try:
            device_data = {
                'ip_address': ip_address,
                'data_source': 'SNMP Collection',
                'collected_at': datetime.now().isoformat(),
                'device_type': 'Network Device'
            }
            
            # SNMP OIDs for common device information
            oids = {
                'hostname': '1.3.6.1.2.1.1.5.0',  # sysName
                'description': '1.3.6.1.2.1.1.1.0',  # sysDescr
                'uptime': '1.3.6.1.2.1.1.3.0',  # sysUpTime
                'contact': '1.3.6.1.2.1.1.4.0',  # sysContact
                'location': '1.3.6.1.2.1.1.6.0',  # sysLocation
            }
            
            for key, oid in oids.items():
                try:
                    for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(
                        SnmpEngine(),
                        CommunityData(community),
                        UdpTransportTarget((ip_address, 161)),
                        ContextData(),
                        ObjectType(ObjectIdentity(oid)),
                        lexicographicMode=False):
                        
                        if errorIndication:
                            break
                        elif errorStatus:
                            break
                        else:
                            for varBind in varBinds:
                                value = str(varBind[1])
                                
                                if key == 'hostname':
                                    device_data['hostname'] = value
                                elif key == 'description':
                                    device_data['os_name'] = value
                                    # Try to determine device type from description
                                    desc_lower = value.lower()
                                    if 'switch' in desc_lower:
                                        device_data['device_type'] = 'Switches'
                                    elif 'printer' in desc_lower:
                                        device_data['device_type'] = 'Printers'
                                    elif 'access point' in desc_lower or 'ap' in desc_lower:
                                        device_data['device_type'] = 'AP'
                                elif key == 'uptime':
                                    device_data['uptime'] = value
                                elif key == 'contact':
                                    device_data['contact'] = value
                                elif key == 'location':
                                    device_data['site'] = value
                        break
                        
                except Exception as oid_error:
                    logger.warning(f"SNMP OID {oid} failed: {oid_error}")
                    continue
            
            logger.info(f"✅ SNMP data collection successful for {device_data.get('hostname', ip_address)}")
            return device_data
            
        except Exception as e:
            logger.error(f"SNMP collection failed for {ip_address}: {e}")
            return None
    
    def save_to_database(self, device_data: Dict, vendor: str = None) -> bool:
        """Save collected device data to database with vendor information"""
        try:
            conn = sqlite3.connect('assets.db')
            cursor = conn.cursor()
            
            # Add vendor if provided
            if vendor:
                device_data['vendor'] = vendor
            
            # Ensure required fields
            device_data.setdefault('status', 'Active')
            device_data.setdefault('created_at', datetime.now().isoformat())
            device_data.setdefault('updated_at', datetime.now().isoformat())
            
            # Map fields to database columns
            field_mapping = {
                'hostname': 'hostname',
                'ip_address': 'ip_address',
                'working_user': 'working_user',
                'domain': 'domain',
                'device_type': 'classification',
                'manufacturer': 'model_vendor',
                'vendor': 'model_vendor',
                'os_name': 'os_name',
                'os_version': 'firmware_os_version',
                'installed_ram_gb': 'installed_ram_gb',
                'storage': 'storage',
                'processor': 'processor',
                'serial_number': 'serial_number',
                'system_sku': 'system_sku',
                'active_gpu': 'active_gpu',
                'primary_mac': 'mac_address',
                'site': 'site',
                'uptime': 'uptime',
                'data_source': 'data_source',
                'status': 'status',
                'created_at': 'created_at',
                'updated_at': 'updated_at'
            }
            
            # Build INSERT query
            db_data = {}
            for source_field, db_field in field_mapping.items():
                if source_field in device_data and device_data[source_field]:
                    db_data[db_field] = device_data[source_field]
            
            if not db_data:
                logger.error("No valid data to save")
                return False
            
            columns = list(db_data.keys())
            placeholders = ', '.join(['?' for _ in columns])
            query = f'INSERT OR REPLACE INTO assets ({", ".join(columns)}) VALUES ({placeholders})'
            
            cursor.execute(query, list(db_data.values()))
            asset_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Device data saved to database with ID: {asset_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save device data to database: {e}")
            return False
    
    def get_vendor_list(self) -> List[str]:
        """Get list of available vendors"""
        return self.COMMON_VENDORS.copy()
    
    def get_device_types(self) -> List[str]:
        """Get list of supported device types"""
        return list(self.DEVICE_TYPES.keys())
    
    def get_collection_method(self, device_type: str) -> str:
        """Get collection method for device type"""
        return self.DEVICE_TYPES.get(device_type, 'SNMP')