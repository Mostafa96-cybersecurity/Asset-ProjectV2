#!/usr/bin/env python3
"""
Complete Data Collection and Smart Database Manager
Ensures complete data collection and intelligent database updates (no data replacement)
"""

import sqlite3
import subprocess
import socket
from datetime import datetime
from typing import Dict, Optional, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import ipaddress

# Try to import WMI for Windows devices
try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False

# Try to import paramiko for SSH
try:
    import paramiko
    SSH_AVAILABLE = True
except ImportError:
    SSH_AVAILABLE = False

class CompleteDataCollector:
    """Comprehensive data collector that gathers ALL available information"""
    
    def __init__(self):
        self.collection_stats = {
            'total_attempted': 0,
            'successful_collections': 0,
            'methods_used': {},
            'start_time': None,
            'end_time': None
        }
        self.wmi_connection = None
        if WMI_AVAILABLE:
            try:
                self.wmi_connection = wmi.WMI()
            except:
                pass
    
    def collect_complete_device_info(self, ip_address: str) -> Dict[str, Any]:
        """Collect ALL available information about a device"""
        device_info = {
            'ip_address': ip_address,
            'hostname': None,
            'operating_system': None,
            'os_version': None,
            'device_type': 'Unknown Device',
            'manufacturer': None,
            'model': None,
            'serial_number': None,
            'cpu_info': None,
            'cpu_cores': None,
            'ram_gb': None,
            'storage_info': None,
            'network_interfaces': [],
            'open_ports': [],
            'services': [],
            'domain': None,
            'last_boot_time': None,
            'collection_method': [],
            'collection_time': datetime.now().isoformat(),
            'collection_success': False,
            'detailed_info': {}
        }
        
        self.collection_stats['total_attempted'] += 1
        methods_attempted = []
        
        # Method 1: Basic Network Information
        try:
            hostname_info = self._collect_hostname_info(ip_address)
            device_info.update(hostname_info)
            methods_attempted.append('Hostname Resolution')
        except Exception as e:
            device_info['detailed_info']['hostname_error'] = str(e)
        
        # Method 2: Port Scanning
        try:
            port_info = self._collect_port_info(ip_address)
            device_info.update(port_info)
            methods_attempted.append('Port Scanning')
        except Exception as e:
            device_info['detailed_info']['port_scan_error'] = str(e)
        
        # Method 3: WMI Collection (Windows devices)
        if WMI_AVAILABLE and self.wmi_connection:
            try:
                wmi_info = self._collect_wmi_info(ip_address)
                if wmi_info:
                    device_info.update(wmi_info)
                    methods_attempted.append('WMI')
            except Exception as e:
                device_info['detailed_info']['wmi_error'] = str(e)
        
        # Method 4: SSH Collection (Linux/Unix devices)
        if SSH_AVAILABLE:
            try:
                ssh_info = self._collect_ssh_info(ip_address)
                if ssh_info:
                    device_info.update(ssh_info)
                    methods_attempted.append('SSH')
            except Exception as e:
                device_info['detailed_info']['ssh_error'] = str(e)
        
        # Method 5: SNMP Collection (Network devices)
        try:
            snmp_info = self._collect_snmp_info(ip_address)
            if snmp_info:
                device_info.update(snmp_info)
                methods_attempted.append('SNMP')
        except Exception as e:
            device_info['detailed_info']['snmp_error'] = str(e)
        
        # Method 6: HTTP/Banner Collection
        try:
            http_info = self._collect_http_info(ip_address)
            if http_info:
                device_info.update(http_info)
                methods_attempted.append('HTTP Banner')
        except Exception as e:
            device_info['detailed_info']['http_error'] = str(e)
        
        # Update collection statistics
        device_info['collection_method'] = methods_attempted
        if len(methods_attempted) > 0:
            device_info['collection_success'] = True
            self.collection_stats['successful_collections'] += 1
        
        # Update method statistics
        for method in methods_attempted:
            self.collection_stats['methods_used'][method] = self.collection_stats['methods_used'].get(method, 0) + 1
        
        # Intelligent device type classification
        device_info['device_type'] = self._classify_device_type(device_info)
        
        return device_info
    
    def _collect_hostname_info(self, ip_address: str) -> Dict[str, Any]:
        """Collect hostname and basic network information"""
        info = {}
        
        try:
            # Reverse DNS lookup
            hostname = socket.gethostbyaddr(ip_address)[0]
            info['hostname'] = hostname
            
            # Extract domain from hostname
            if '.' in hostname:
                domain_parts = hostname.split('.')[1:]
                info['domain'] = '.'.join(domain_parts)
        except:
            info['hostname'] = f"device-{ip_address.replace('.', '-')}"
        
        return info
    
    def _collect_port_info(self, ip_address: str) -> Dict[str, Any]:
        """Collect open ports and services"""
        info = {'open_ports': [], 'services': []}
        
        # Common ports to scan
        common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 
                       135, 139, 445, 1433, 1521, 3306, 3389, 5432, 5900, 
                       8080, 8443, 9100, 161, 162]
        
        def scan_port(port):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((ip_address, port))
                sock.close()
                return port if result == 0 else None
            except:
                return None
        
        # Scan ports with threading
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(scan_port, port): port for port in common_ports}
            for future in as_completed(futures, timeout=30):
                result = future.result()
                if result:
                    info['open_ports'].append(result)
                    info['services'].append(self._identify_service(result))
        
        return info
    
    def _collect_wmi_info(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """Collect Windows system information via WMI"""
        if not self.wmi_connection:
            return None
        
        info = {}
        
        try:
            # Try to connect to remote WMI
            # Note: This requires proper credentials and permissions
            remote_wmi = wmi.WMI(computer=ip_address)
            
            # Operating System Information
            for os_info in remote_wmi.Win32_OperatingSystem():
                info['operating_system'] = os_info.Caption
                info['os_version'] = os_info.Version
                info['last_boot_time'] = str(os_info.LastBootUpTime)
                break
            
            # Computer System Information
            for cs_info in remote_wmi.Win32_ComputerSystem():
                info['manufacturer'] = cs_info.Manufacturer
                info['model'] = cs_info.Model
                info['ram_gb'] = round(int(cs_info.TotalPhysicalMemory) / (1024**3), 2)
                info['domain'] = cs_info.Domain
                break
            
            # Processor Information
            cpu_info = []
            for cpu in remote_wmi.Win32_Processor():
                cpu_info.append(f"{cpu.Name} ({cpu.NumberOfCores} cores)")
                info['cpu_cores'] = cpu.NumberOfCores
            info['cpu_info'] = '; '.join(cpu_info)
            
            # Storage Information
            storage_info = []
            for disk in remote_wmi.Win32_LogicalDisk():
                if disk.Size:
                    size_gb = round(int(disk.Size) / (1024**3), 2)
                    free_gb = round(int(disk.FreeSpace) / (1024**3), 2)
                    storage_info.append(f"{disk.DeviceID} {size_gb}GB ({free_gb}GB free)")
            info['storage_info'] = '; '.join(storage_info)
            
            # Network Adapters
            network_adapters = []
            for adapter in remote_wmi.Win32_NetworkAdapterConfiguration():
                if adapter.IPEnabled and adapter.IPAddress:
                    network_adapters.append(f"{adapter.Description}: {adapter.IPAddress[0]}")
            info['network_interfaces'] = network_adapters
            
            return info
            
        except Exception:
            return None
    
    def _collect_ssh_info(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """Collect Linux/Unix system information via SSH"""
        if not SSH_AVAILABLE:
            return None
        
        # Common SSH credentials (should be configurable)
        ssh_credentials = [
            ('root', ''),
            ('admin', 'admin'),
            ('user', 'user'),
            ('pi', 'raspberry')  # Raspberry Pi default
        ]
        
        for username, password in ssh_credentials:
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(ip_address, username=username, password=password, timeout=10)
                
                info = {}
                
                # System information
                commands = {
                    'operating_system': 'uname -a',
                    'hostname': 'hostname',
                    'cpu_info': 'cat /proc/cpuinfo | grep "model name" | head -1',
                    'ram_info': 'free -h | grep Mem',
                    'storage_info': 'df -h'
                }
                
                for key, command in commands.items():
                    try:
                        stdin, stdout, stderr = ssh.exec_command(command)
                        output = stdout.read().decode().strip()
                        info[f'ssh_{key}'] = output
                    except:
                        continue
                
                ssh.close()
                return info
                
            except:
                continue
        
        return None
    
    def _collect_snmp_info(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """Collect SNMP information from network devices"""
        # Note: Would require pysnmp library
        # Placeholder for SNMP collection
        return None
    
    def _collect_http_info(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """Collect HTTP banner and web service information"""
        import urllib.request
        import urllib.error
        
        info = {}
        
        for port in [80, 443, 8080, 8443]:
            for protocol in ['http', 'https']:
                if (protocol == 'http' and port in [443, 8443]) or (protocol == 'https' and port in [80, 8080]):
                    continue
                
                url = f"{protocol}://{ip_address}:{port}"
                try:
                    request = urllib.request.Request(url, headers={'User-Agent': 'Asset-Scanner'})
                    with urllib.request.urlopen(request, timeout=5) as response:
                        headers = dict(response.headers)
                        info['web_server'] = headers.get('Server', 'Unknown')
                        info['web_title'] = self._extract_title(response.read().decode('utf-8', errors='ignore'))
                        return info
                except:
                    continue
        
        return None
    
    def _extract_title(self, html_content: str) -> str:
        """Extract title from HTML content"""
        try:
            import re
            title_match = re.search(r'<title>(.*?)</title>', html_content, re.IGNORECASE)
            return title_match.group(1).strip() if title_match else 'Unknown'
        except:
            return 'Unknown'
    
    def _identify_service(self, port: int) -> str:
        """Identify service based on port number"""
        service_map = {
            21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP', 53: 'DNS',
            80: 'HTTP', 110: 'POP3', 143: 'IMAP', 443: 'HTTPS',
            135: 'RPC', 139: 'NetBIOS', 445: 'SMB', 1433: 'SQL Server',
            1521: 'Oracle', 3306: 'MySQL', 3389: 'RDP', 5432: 'PostgreSQL',
            5900: 'VNC', 8080: 'HTTP-Alt', 161: 'SNMP', 9100: 'Printer'
        }
        return service_map.get(port, f'Port-{port}')
    
    def _classify_device_type(self, device_info: Dict[str, Any]) -> str:
        """Intelligently classify device type based on collected information"""
        open_ports = device_info.get('open_ports', [])
        services = device_info.get('services', [])
        hostname = device_info.get('hostname', '').lower()
        os_info = device_info.get('operating_system', '').lower()
        
        # Server classification
        if any(port in open_ports for port in [1433, 1521, 3306, 5432]):
            return 'Database Server'
        elif 3389 in open_ports or 'server' in hostname or 'srv' in hostname:
            return 'Windows Server'
        elif 22 in open_ports and any(term in os_info for term in ['linux', 'unix']):
            return 'Linux Server'
        
        # Network device classification
        elif 161 in open_ports or 'switch' in hostname or 'router' in hostname:
            return 'Network Device'
        elif 9100 in open_ports:
            return 'Printer'
        
        # Workstation classification
        elif any(term in os_info for term in ['windows 10', 'windows 11']):
            return 'Windows Workstation'
        elif 'mac' in os_info or 'darwin' in os_info:
            return 'Mac Workstation'
        
        # Special devices
        elif 'pi' in hostname or 'raspberry' in hostname:
            return 'Raspberry Pi'
        elif 'vm' in hostname or 'virtual' in hostname:
            return 'Virtual Machine'
        
        return 'Unknown Device'

class SmartDatabaseManager:
    """Manages database operations with intelligent updates and no data replacement"""
    
    def __init__(self, db_path: str = 'assets.db'):
        self.db_path = db_path
        self.update_stats = {
            'new_records': 0,
            'updated_records': 0,
            'unchanged_records': 0,
            'errors': 0
        }
    
    def save_device_data(self, device_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save device data with smart update logic"""
        result = {
            'action': 'none',
            'record_id': None,
            'updated_fields': [],
            'error': None
        }
        
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            
            # Find existing record
            ip_address = device_data.get('ip_address')
            hostname = device_data.get('hostname')
            
            existing_record = self._find_existing_record(cursor, ip_address, hostname)
            
            if existing_record:
                # Update existing record
                update_result = self._smart_update_record(cursor, existing_record[0], device_data)
                result.update(update_result)
                result['record_id'] = existing_record[0]
                self.update_stats['updated_records'] += 1
            else:
                # Insert new record
                record_id = self._insert_new_record(cursor, device_data)
                result['action'] = 'inserted'
                result['record_id'] = record_id
                self.update_stats['new_records'] += 1
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            result['error'] = str(e)
            self.update_stats['errors'] += 1
        
        return result
    
    def _find_existing_record(self, cursor, ip_address: str, hostname: str) -> Optional[Tuple]:
        """Find existing record by IP or hostname"""
        # Try to find by IP first
        if ip_address:
            cursor.execute("SELECT id FROM assets WHERE ip_address = ?", (ip_address,))
            record = cursor.fetchone()
            if record:
                return record
        
        # Try to find by hostname
        if hostname:
            cursor.execute("SELECT id FROM assets WHERE hostname = ?", (hostname,))
            record = cursor.fetchone()
            if record:
                return record
        
        return None
    
    def _smart_update_record(self, cursor, record_id: int, new_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update record only with changed data"""
        result = {'action': 'updated', 'updated_fields': []}
        
        # Get existing record
        cursor.execute("SELECT * FROM assets WHERE id = ?", (record_id,))
        existing_row = cursor.fetchone()
        
        # Get column names
        cursor.execute("PRAGMA table_info(assets)")
        columns = [row[1] for row in cursor.fetchall()]
        existing_data = dict(zip(columns, existing_row))
        
        # Compare and update only changed fields
        update_pairs = []
        values = []
        updated_fields = []
        
        for field, new_value in new_data.items():
            if field in existing_data and field != 'id':
                old_value = existing_data[field]
                
                # Update if value has changed and new value is not empty/None
                if (str(new_value) != str(old_value) and 
                    new_value not in [None, '', 'Unknown', 'Unknown Device'] and
                    new_value != old_value):
                    
                    update_pairs.append(f"{field} = ?")
                    values.append(new_value)
                    updated_fields.append(field)
        
        # Always update last_seen timestamp
        update_pairs.append("last_seen = ?")
        values.append(datetime.now().isoformat())
        updated_fields.append('last_seen')
        
        if len(update_pairs) > 1:  # More than just timestamp
            update_sql = f"UPDATE assets SET {\', \'.join(update_fields)} WHERE id = ?"  # NOTE: Safe - fields from schema
            values.append(record_id)
            cursor.execute(update_sql, values)
            result['updated_fields'] = updated_fields
        else:
            result['action'] = 'timestamp_only'
        
        return result
    
    def _insert_new_record(self, cursor, device_data: Dict[str, Any]) -> int:
        """Insert new record"""
        # Ensure required fields
        if 'last_seen' not in device_data:
            device_data['last_seen'] = datetime.now().isoformat()
        
        fields = list(device_data.keys())
        placeholders = ', '.join(['?' for _ in fields])
        values = list(device_data.values())
        
        insert_sql = f"INSERT INTO assets ({', '.join(fields)}) VALUES ({placeholders})"
        cursor.execute(insert_sql, values)
        
        return cursor.lastrowid
    
    def get_update_statistics(self) -> Dict[str, Any]:
        """Get database update statistics"""
        return self.update_stats.copy()

def run_complete_network_scan(network_range: str = "10.0.21.0/24") -> Dict[str, Any]:
    """Run complete network scan with comprehensive data collection"""
    print("🚀 STARTING COMPLETE NETWORK SCAN")
    print(f"📡 Network: {network_range}")
    print("=" * 60)
    
    start_time = datetime.now()
    
    # Initialize components
    collector = CompleteDataCollector()
    db_manager = SmartDatabaseManager()
    
    # Generate IP list
    try:
        network = ipaddress.IPv4Network(network_range, strict=False)
        ip_list = [str(ip) for ip in network.hosts()]
    except:
        print(f"❌ Invalid network range: {network_range}")
        return {}
    
    print(f"🔍 Scanning {len(ip_list)} IP addresses...")
    
    # First: Quick ping scan to find live hosts
    print("📡 Phase 1: Discovering live hosts...")
    live_hosts = []
    
    def ping_host(ip):
        try:
            result = subprocess.run(
                ['ping', '-n', '1', '-w', '1000', ip],
                capture_output=True, text=True, timeout=3
            )
            return ip if result.returncode == 0 else None
        except:
            return None
    
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(ping_host, ip): ip for ip in ip_list}
        for future in as_completed(futures, timeout=120):
            result = future.result()
            if result:
                live_hosts.append(result)
                print(f"   ✅ Live: {result}")
    
    print(f"📊 Found {len(live_hosts)} live hosts")
    
    # Second: Complete data collection on live hosts
    print("\n📊 Phase 2: Complete data collection...")
    collected_devices = []
    
    def collect_device_data(ip):
        print(f"   🔍 Collecting: {ip}")
        device_data = collector.collect_complete_device_info(ip)
        save_result = db_manager.save_device_data(device_data)
        
        status = "✅" if save_result['action'] in ['inserted', 'updated'] else "📝"
        methods = ", ".join(device_data.get('collection_method', ['Basic']))
        
        print(f"   {status} {ip} → {device_data.get('hostname', 'Unknown')} "
              f"({device_data.get('device_type', 'Unknown')}) [{methods}]")
        
        return device_data, save_result
    
    # Collect data with limited concurrency to avoid overwhelming targets
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(collect_device_data, ip): ip for ip in live_hosts}
        
        for future in as_completed(futures, timeout=600):  # 10 minutes timeout
            try:
                device_data, save_result = future.result()
                collected_devices.append((device_data, save_result))
            except Exception as e:
                ip = futures[future]
                print(f"   ❌ Failed: {ip} - {e}")
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # Generate report
    collection_stats = collector.collection_stats
    db_stats = db_manager.get_update_statistics()
    
    report = {
        'scan_info': {
            'network_range': network_range,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration,
            'total_ips_scanned': len(ip_list),
            'live_hosts_found': len(live_hosts)
        },
        'collection_stats': collection_stats,
        'database_stats': db_stats,
        'devices_collected': len(collected_devices)
    }
    
    return report

if __name__ == "__main__":
    print("🔧 COMPLETE DATA COLLECTION & SMART DATABASE MANAGER")
    print("=" * 60)
    print(f"🕐 Started: {datetime.now()}")
    print()
    
    # Run complete scan
    network = "10.0.21.0/24"  # Your main network
    report = run_complete_network_scan(network)
    
    if report:
        print("\n📋 SCAN COMPLETION REPORT")
        print("=" * 60)
        
        scan_info = report['scan_info']
        print(f"🌐 Network: {scan_info['network_range']}")
        print(f"⏱️ Duration: {scan_info['duration_seconds']:.1f} seconds")
        print(f"🔍 IPs scanned: {scan_info['total_ips_scanned']}")
        print(f"✅ Live hosts: {scan_info['live_hosts_found']}")
        print(f"📊 Devices collected: {report['devices_collected']}")
        
        db_stats = report['database_stats']
        print("\n💾 Database Operations:")
        print(f"   📝 New records: {db_stats['new_records']}")
        print(f"   ✏️ Updated records: {db_stats['updated_records']}")
        print(f"   ❌ Errors: {db_stats['errors']}")
        
        collection_stats = report['collection_stats']
        print("\n📊 Collection Methods:")
        for method, count in collection_stats.get('methods_used', {}).items():
            print(f"   • {method}: {count} devices")
    
    print(f"\n🕐 Completed: {datetime.now()}")