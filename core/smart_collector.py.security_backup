# -*- coding: utf-8 -*-
"""
Smart Device Collector with Advanced Error Prevention
----------------------------------------------------
1. Ping scan for alive devices only with validation
2. OS detection (Windows vs Linux) with fallback mechanisms
3. Smart categorization with conflict resolution:
   - Windows Devices (workstations)  
   - Windows Server
   - Linux Devices
4. Automatic sync to Excel when available
5. Duplicate prevention and data quality assurance
6. Error recovery and retry mechanisms
"""

import subprocess
import socket
import logging
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed


log = logging.getLogger(__name__)

class SmartDeviceCollector:
    def __init__(self):
        self.alive_devices = set()
        
    def scan_alive_devices(self, targets: List[str], max_workers: int = 50) -> List[str]:
        """
        Ping scan to find only alive devices
        """
        log.info(f"Starting ping scan for {len(targets)} targets...")
        alive_devices = []
        
        def ping_device(ip: str) -> Optional[str]:
            try:
                # Use ping command with timeout
                result = subprocess.run(
                    ["ping", "-n", "1", "-w", "1000", ip],  # Windows ping
                    capture_output=True,
                    timeout=2,
                    text=True
                )
                if result.returncode == 0:
                    return ip
            except Exception:
                pass
            return None
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(ping_device, ip): ip for ip in targets}
            
            for future in as_completed(futures):
                result = future.result()
                if result:
                    alive_devices.append(result)
                    log.info(f"✓ {result} is alive")
        
        log.info(f"Found {len(alive_devices)} alive devices out of {len(targets)} targets")
        return alive_devices
    
    def detect_os_type(self, ip: str) -> str:
        """
        Detect OS type using multiple methods
        """
        # Method 1: Try WMI connection (Windows)
        if self._test_wmi_connection(ip):
            return self._determine_windows_type(ip)
        
        # Method 2: Try SSH connection (Linux)
        if self._test_ssh_connection(ip):
            return "Linux"
            
        # Method 3: Port scanning for common services
        return self._detect_by_ports(ip)
    
    def _test_wmi_connection(self, ip: str) -> bool:
        """Test if device responds to WMI (Windows)"""
        try:
            # Test WMI ports (135, 445)
            ports = [135, 445]
            for port in ports:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((ip, port))
                sock.close()
                if result == 0:
                    return True
            return False
        except Exception:
            return False
    
    def _test_ssh_connection(self, ip: str) -> bool:
        """Test if device responds to SSH (Linux)"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((ip, 22))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    def _determine_windows_type(self, ip: str) -> str:
        """Determine if Windows device is workstation or server"""
        try:
            # Try to get OS info via WMI to determine server vs workstation
            # This is a simplified check - in real implementation you'd use WMI
            
            # For now, check common server ports
            server_ports = [3389, 53, 25, 110, 143, 993, 995]  # RDP, DNS, Mail, etc.
            
            open_server_ports = 0
            for port in server_ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    if sock.connect_ex((ip, port)) == 0:
                        open_server_ports += 1
                    sock.close()
                except Exception:
                    pass
            
            # If multiple server ports are open, likely a server
            if open_server_ports >= 2:
                return "Windows Server"
            else:
                return "Windows Workstation"
                
        except Exception:
            return "Windows Workstation"  # Default fallback
    
    def _detect_by_ports(self, ip: str) -> str:
        """Detect OS by open ports when direct methods fail"""
        common_ports = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 993, 995, 3389]
        open_ports = []
        
        for port in common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                if sock.connect_ex((ip, port)) == 0:
                    open_ports.append(port)
                sock.close()
            except Exception:
                pass
        
        # Analyze open ports to guess OS
        if 135 in open_ports or 445 in open_ports:
            return "Windows Workstation"
        elif 22 in open_ports:
            return "Linux"
        else:
            return "Unknown"  # Skip unknown devices
    
    def collect_device_data(self, ip: str, device_type: str, credentials: Dict) -> Optional[Dict]:
        """
        Collect data based on device type
        """
        try:
            if "Windows" in device_type:
                return self._collect_windows_data(ip, device_type, credentials.get('windows', {}))
            elif device_type == "Linux":
                return self._collect_linux_data(ip, credentials.get('linux', {}))
            elif device_type == "Network Device":
                return self._collect_network_data(ip, credentials.get('snmp', {}))
            else:
                return None  # Skip unknown devices
                
        except Exception as e:
            log.error(f"Failed to collect data from {ip}: {e}")
            return None
    
    def _collect_windows_data(self, ip: str, device_type: str, creds: Dict) -> Dict:
        """Collect Windows device data via advanced multi-method collection"""
        try:
            # Try advanced collection first for better success rate
            from advanced_collector import AdvancedDeviceCollector
            
            username = creds.get('username')
            password = creds.get('password')
            
            if not username:
                log.warning(f"No username provided for {ip}")
                return None
            
            log.info(f"🚀 Starting advanced Windows collection for {ip}")
            
            # Use advanced collector with multiple fallback methods
            advanced_collector = AdvancedDeviceCollector()
            result = advanced_collector.collect_device_comprehensive(ip, device_type, creds)
            
            if result and result.get('success'):
                log.info(f"✅ Advanced collection successful for {ip} using {result.get('collection_method')}")
                return result
            
            # Fallback to original WMI collection if advanced fails
            log.warning(f"🔄 Advanced collection failed for {ip}, trying legacy WMI...")
            return self._collect_windows_data_legacy(ip, device_type, creds)
                
        except Exception as e:
            log.error(f"Failed to collect Windows data from {ip}: {e}")
            # Fallback to legacy collection
            return self._collect_windows_data_legacy(ip, device_type, creds)
    
    def _collect_windows_data_legacy(self, ip: str, device_type: str, creds: Dict) -> Dict:
        """Legacy Windows device data collection via WMI with retry logic"""
        try:
            from collectors.wmi_collector import collect_windows_wmi
            import time
            
            username = creds.get('username')
            password = creds.get('password')
            
            # Enhanced collection with retry logic
            max_retries = 2
            retry_delay = 1.0
            
            for attempt in range(max_retries + 1):
                try:
                    if attempt > 0:
                        time.sleep(retry_delay)
                        log.info(f"Retry {attempt} for {ip} legacy WMI collection")
                    
                    data = collect_windows_wmi(ip, username, password)
                    
                    if isinstance(data, dict) and "Error" not in data:
                        # Success!
                        if device_type == "Windows Server":
                            return self._format_windows_server_data(data, ip)
                        else:
                            return self._format_windows_workstation_data(data, ip)
                    else:
                        error_info = data.get('Error', {}) if isinstance(data, dict) else {'message': str(data)}
                        error_code = error_info.get('code', 'Unknown')
                        error_message = error_info.get('message', 'Unknown error')
                        
                        if attempt == 0:  # Only log detailed error on first attempt
                            log.warning(f"WMI collection failed for {ip}: {error_code} - {error_message}")
                        
                        # Don't retry certain errors
                        if error_code in ['PlatformNotSupported', 'DependencyMissing']:
                            break
                            
                        # For access denied, don't retry immediately
                        if 'access_denied' in error_message.lower() and attempt == 0:
                            # Try one more time after a longer delay
                            time.sleep(2.0)
                            continue
                            
                except Exception as inner_e:
                    if attempt == 0:
                        log.error(f"Exception during WMI collection for {ip}: {inner_e}")
                    
                    # Don't retry on timeout exceptions
                    if "timeout" in str(inner_e).lower():
                        break
            
            # If we get here, all attempts failed
            log.error(f"All WMI collection attempts failed for {ip}")
            return None
                
        except Exception as e:
            log.error(f"Windows data collection failed for {ip}: {e}")
            return None

    def _collect_linux_data(self, ip: str, creds: Dict) -> Dict:
        """Collect Linux device data via SSH"""
        try:
            from collectors.ssh_collector import collect_linux_or_esxi_ssh
            
            username = creds.get('username', 'root')
            password = creds.get('password')
            
            data = collect_linux_or_esxi_ssh(ip, username, password)
            
            if "Error" in data:
                log.warning(f"SSH collection failed for {ip}: {data['Error']}")
                return None
                
            return self._format_linux_data(data, ip)
            
        except Exception as e:
            log.error(f"Linux data collection failed for {ip}: {e}")
            return None
            
    def _collect_network_data(self, ip: str, creds: Dict) -> Dict:
        """Collect Network device data via SNMP"""
        try:
            from collectors.snmp_collector import snmp_collect_basic
            
            community = creds.get('community', 'public')
            version = creds.get('version', '2c')
            
            log.info(f"📡 Collecting SNMP data from {ip} with community '{community}'")
            
            data = snmp_collect_basic(
                ip, 
                community=community, 
                version=version,
                timeout=creds.get('timeout', 3),
                retries=creds.get('retries', 1)
            )
            
            if data and isinstance(data, dict):
                log.info(f"✅ SNMP collection successful for {ip}")
                return self._format_network_data(data, ip)
            else:
                log.warning(f"No SNMP data received from {ip}")
                return None
                
        except Exception as e:
            log.error(f"SNMP data collection failed for {ip}: {e}")
            return None
    
    def _format_windows_workstation_data(self, wmi_data: Dict, ip: str) -> Dict:
        """Format data for enhanced database storage with all technical fields"""
        import json
        from datetime import datetime
        
        return {
            # Core identity
            "hostname": wmi_data.get("Hostname", ""),
            "ip_address": wmi_data.get("LAN IP Address", ip),
            "device_type": self._map_device_type(wmi_data.get("Device Infrastructure", "")),
            
            # Hardware info
            "model_vendor": f"{wmi_data.get('Manufacturer', '')} {wmi_data.get('Device Model', '')}".strip(),
            "sn": wmi_data.get("Serial Number", ""),
            "firmware_os_version": wmi_data.get("OS Name", ""),
            
            # Complete technical data
            "working_user": wmi_data.get("Working User", ""),
            "domain_name": wmi_data.get("Domain", ""),
            "device_infrastructure": wmi_data.get("Device Infrastructure", ""),
            "installed_ram_gb": wmi_data.get("Installed RAM (GB)", None),
            "storage_info": wmi_data.get("Storage", ""),
            "manufacturer": wmi_data.get("Manufacturer", ""),
            "processor_info": wmi_data.get("Processor", ""),
            "system_sku": wmi_data.get("System SKU", ""),
            "active_gpu": wmi_data.get("Active GPU", ""),
            "connected_screens": wmi_data.get("Connected Screens", None),
            "disk_count": wmi_data.get("Disk Count", None),
            "mac_address": wmi_data.get("MAC Address", ""),
            "all_mac_addresses": wmi_data.get("All MACs", ""),
            "cpu_details": json.dumps(wmi_data.get("CPUs", [])) if wmi_data.get("CPUs") else "",
            "disk_details": json.dumps(wmi_data.get("Disks", [])) if wmi_data.get("Disks") else "",
            
            # System fields
            "data_source": "Enhanced WMI Collection",
            "status": "Active",
            "updated_at": datetime.now().isoformat()
        }
    
    def _format_windows_server_data(self, wmi_data: Dict, ip: str) -> Dict:
        """Format data for enhanced database storage with all technical fields (Server)"""
        import json
        from datetime import datetime
        
        return {
            # Core identity
            "hostname": wmi_data.get("Hostname", ""),
            "ip_address": wmi_data.get("LAN IP Address", ip),
            "device_type": "server",
            
            # Hardware info
            "model_vendor": f"{wmi_data.get('Manufacturer', '')} {wmi_data.get('Device Model', '')}".strip(),
            "sn": wmi_data.get("Serial Number", ""),
            "firmware_os_version": wmi_data.get("OS Name", ""),
            
            # Complete technical data
            "working_user": wmi_data.get("Working User", ""),
            "domain_name": wmi_data.get("Domain", ""),
            "device_infrastructure": "Server",
            "installed_ram_gb": wmi_data.get("Installed RAM (GB)", None),
            "storage_info": wmi_data.get("Storage", ""),
            "manufacturer": wmi_data.get("Manufacturer", ""),
            "processor_info": wmi_data.get("Processor", ""),
            "system_sku": wmi_data.get("System SKU", ""),
            "active_gpu": wmi_data.get("Active GPU", ""),
            "connected_screens": wmi_data.get("Connected Screens", None),
            "disk_count": wmi_data.get("Disk Count", None),
            "mac_address": wmi_data.get("MAC Address", ""),
            "all_mac_addresses": wmi_data.get("All MACs", ""),
            "cpu_details": json.dumps(wmi_data.get("CPUs", [])) if wmi_data.get("CPUs") else "",
            "disk_details": json.dumps(wmi_data.get("Disks", [])) if wmi_data.get("Disks") else "",
            
            # System fields
            "data_source": "Enhanced WMI Collection (Server)",
            "status": "Active",
            "updated_at": datetime.now().isoformat()
        }
    
    def _format_linux_data(self, ssh_data: Dict, ip: str) -> Dict:
        """Format data for enhanced database storage with all technical fields (Linux)"""
        import json
        from datetime import datetime
        
        return {
            # Core identity
            "hostname": ssh_data.get("hostname", ip),
            "ip_address": ip,
            "device_type": self._map_device_type("Linux Server"),
            
            # Hardware info
            "model_vendor": f"{ssh_data.get('manufacturer', '')} {ssh_data.get('product_name', '')}".strip(),
            "sn": ssh_data.get("serial_number", ""),
            "firmware_os_version": ssh_data.get("os_version", ""),
            
            # Complete technical data
            "working_user": ssh_data.get("logged_users", ""),
            "domain_name": ssh_data.get("domain", ""),
            "device_infrastructure": "Linux Server",
            "installed_ram_gb": self._extract_ram_gb(ssh_data.get("memory_info", "")),
            "storage_info": ssh_data.get("disk_info", ""),
            "manufacturer": ssh_data.get("manufacturer", ""),
            "processor_info": ssh_data.get("cpu_info", ""),
            "system_sku": ssh_data.get("product_name", ""),
            "active_gpu": ssh_data.get("gpu_info", ""),
            "connected_screens": None,  # Not typically applicable for Linux servers
            "disk_count": self._extract_disk_count(ssh_data.get("disk_info", "")),
            "mac_address": ssh_data.get("primary_mac", ""),
            "all_mac_addresses": ssh_data.get("all_network_interfaces", ""),
            "cpu_details": json.dumps(ssh_data.get("cpu_details", [])) if ssh_data.get("cpu_details") else "",
            "disk_details": json.dumps(ssh_data.get("disk_details", [])) if ssh_data.get("disk_details") else "",
            
            # Additional Linux-specific info in notes
            "notes": json.dumps({
                "kernel_version": ssh_data.get("kernel_version", ""),
                "uptime": ssh_data.get("uptime", ""),
                "running_services": ssh_data.get("running_services", ""),
                "network_interfaces": ssh_data.get("network_interfaces", ""),
                "ssh_port": "22"
            }),
            
            # System fields
            "data_source": "Enhanced SSH Collection (Linux)",
            "status": "Active",
            "updated_at": datetime.now().isoformat()
        }
    
    def _format_network_data(self, snmp_data: Dict, ip: str) -> Dict:
        """Format data for enhanced database storage with all technical fields (Network Device)"""
        import json
        from datetime import datetime
        
        return {
            # Core identity
            "hostname": snmp_data.get("sysName", ip),
            "ip_address": ip,
            "device_type": "network",
            
            # Hardware info from SNMP
            "model_vendor": f"{snmp_data.get('vendor', '')} {snmp_data.get('model', '')}".strip(),
            "sn": snmp_data.get("serialNumber", ""),
            "firmware_os_version": snmp_data.get("sysDescr", ""),
            
            # Network device technical data
            "working_user": "",  # Not applicable for network devices
            "domain_name": snmp_data.get("domain", ""),
            "device_infrastructure": "Network Device",
            "installed_ram_gb": None,  # Not typically available via SNMP
            "storage_info": snmp_data.get("storage_info", ""),
            "manufacturer": snmp_data.get("vendor", ""),
            "processor_info": snmp_data.get("processor_info", ""),
            "system_sku": snmp_data.get("model", ""),
            "active_gpu": None,  # Not applicable for network devices
            "connected_screens": None,  # Not applicable for network devices
            "disk_count": None,  # Not applicable for network devices
            "mac_address": snmp_data.get("primary_mac", ""),
            "all_mac_addresses": snmp_data.get("all_interfaces", ""),
            "cpu_details": json.dumps(snmp_data.get("cpu_info", [])) if snmp_data.get("cpu_info") else "",
            "disk_details": "",  # Not applicable for network devices
            
            # Network-specific info in notes
            "notes": json.dumps({
                "sysDescr": snmp_data.get("sysDescr", ""),
                "sysObjectID": snmp_data.get("sysObjectID", ""),
                "sysUpTime": snmp_data.get("sysUpTime", ""),
                "sysContact": snmp_data.get("sysContact", ""),
                "sysLocation": snmp_data.get("sysLocation", ""),
                "interfaces": snmp_data.get("interfaces", []),
                "snmp_version": snmp_data.get("snmp_version", ""),
                "community_used": snmp_data.get("community_used", "")
            }),
            
            # System fields
            "data_source": "Enhanced SNMP Collection (Network Device)",
            "status": "Active",
            "updated_at": datetime.now().isoformat()
        }
    
    def save_to_appropriate_sheet(self, device_data: Dict, device_type: str, excel_path: str):
        """Save device data to the appropriate Excel sheet with auto-sync"""
        try:
            from core.excel_db_sync import get_sync_manager
            from collectors.ui_add_network_device import SHEET_SCHEMAS, ensure_workbook_tabs
            
            # Determine target sheet
            if device_type == "Windows Workstation":
                sheet_name = "Windows Devices"
            elif device_type == "Windows Server":
                sheet_name = "Windows Server"
            elif device_type == "Linux":
                sheet_name = "Linux Devices"
            elif device_type == "Network Device":
                sheet_name = "Network Devices"
            else:
                log.warning(f"Unknown device type: {device_type}")
                return False
            
            # Ensure workbook has required sheets
            ensure_workbook_tabs(excel_path)
            
            # Get headers for the sheet
            headers = SHEET_SCHEMAS.get(sheet_name, [])
            if not headers:
                log.error(f"No headers defined for sheet: {sheet_name}")
                return False
            
            # Use sync manager to save data
            sync_manager = get_sync_manager()
            added_to_excel = sync_manager.add_device_data(excel_path, sheet_name, headers, device_data)
            
            if added_to_excel:
                log.info(f"✓ Device {device_data.get('Hostname', 'Unknown')} saved to Excel sheet '{sheet_name}'")
            else:
                log.info(f"💾 Device {device_data.get('Hostname', 'Unknown')} saved to database (Excel busy) - will sync automatically")
            
            return True
            
        except Exception as e:
            log.error(f"Failed to save device data: {e}")
            return False
    
    def _map_device_type(self, device_infrastructure: str) -> str:
        """Map device infrastructure to database device_type"""
        mapping = {
            "Workstation": "workstation", 
            "Laptop": "laptop",
            "Server": "server",
            "Linux Server": "server",
            "Domain Controller": "server",
            "Network Device": "network",
            "Storage": "storage",
            "Virtual Machine": "virtual"
        }
        return mapping.get(device_infrastructure, "workstation")
    
    def _extract_ram_gb(self, memory_info: str) -> int:
        """Extract RAM in GB from memory info string"""
        if not memory_info:
            return None
        try:
            # Try to find numbers followed by GB or similar
            import re
            gb_match = re.search(r'(\d+(?:\.\d+)?)\s*GB', memory_info, re.IGNORECASE)
            if gb_match:
                return int(float(gb_match.group(1)))
            
            # Try to find MB and convert
            mb_match = re.search(r'(\d+(?:\.\d+)?)\s*MB', memory_info, re.IGNORECASE)
            if mb_match:
                return int(float(mb_match.group(1)) / 1024)
            
            # Try to extract any number (assume GB)
            num_match = re.search(r'(\d+)', memory_info)
            if num_match:
                return int(num_match.group(1))
                
            return None
        except:
            return None
    
    def _extract_disk_count(self, disk_info: str) -> int:
        """Extract number of disks from disk info"""
        if not disk_info:
            return None
        try:
            # Count disk entries, drives, or similar
            import re
            disk_patterns = [r'\bdisk\b', r'\bdrive\b', r'\bsda\b', r'\bsdb\b', r'\bsdc\b', r'C:', r'D:']
            count = 0
            for pattern in disk_patterns:
                matches = re.findall(pattern, disk_info, re.IGNORECASE)
                count += len(matches)
            return max(1, count) if count > 0 else 1
        except:
            return 1