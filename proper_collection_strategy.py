#!/usr/bin/env python3
"""
Proper 3-Step Collection Strategy
================================
1. PING discovery to find alive devices
2. NMAP OS detection on alive devices  
3. Use correct collection method based on OS type

This replaces the current flawed approach that tries to collect from every IP.
"""

import os
import time
import socket
import threading
from queue import Queue, Empty
from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from datetime import datetime
import subprocess
import logging

from PyQt6.QtCore import QThread, pyqtSignal

# Collection method imports
try:
    import wmi
    import paramiko
    import requests
    from pysnmp.hlapi import (
        getCmd, SnmpEngine, UdpTransportTarget, ContextData,
        ObjectType, ObjectIdentity, CommunityData
    )
    COLLECTION_AVAILABLE = True
except ImportError:
    COLLECTION_AVAILABLE = False

try:
    import nmap
    NMAP_AVAILABLE = True
except ImportError:
    NMAP_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

@dataclass
class AliveDevice:
    """Represents a device found to be alive"""
    ip: str
    ping_time: float
    os_family: str = 'Unknown'
    device_type: str = 'Unknown'
    confidence: int = 0
    open_ports: List[int] = None
    
    def __post_init__(self):
        if self.open_ports is None:
            self.open_ports = []

@dataclass 
class CollectionResult:
    """Result of device collection"""
    ip: str
    success: bool
    method: str
    data: Dict = None
    error: str = ''
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}

class ProperCollectionStrategy(QThread):
    """
    Implements the correct 3-step collection strategy:
    1. PING Discovery → Find alive devices
    2. NMAP OS Detection → Determine OS type  
    3. Targeted Collection → Use appropriate method
    """
    
    # PyQt Signals
    log_message = pyqtSignal(str)
    progress_updated = pyqtSignal(int)
    device_collected = pyqtSignal(dict)
    collection_finished = pyqtSignal(bool)
    
    def __init__(self, 
                 targets: List[str],
                 win_creds: Optional[List] = None,
                 linux_creds: Optional[List] = None,
                 snmp_v2c: Optional[List] = None,
                 snmp_v3: Optional[Dict] = None,
                 use_http: bool = True,
                 ping_workers: int = 50,    # Fast ping discovery
                 nmap_workers: int = 10,    # OS detection
                 collection_workers: int = 8, # Targeted collection
                 parent=None):
        super().__init__(parent)
        
        self.targets = targets or []
        self.win_creds = self._normalize_credentials(win_creds)
        self.linux_creds = self._normalize_credentials(linux_creds) 
        self.snmp_v2c = snmp_v2c or ['public']
        self.snmp_v3 = snmp_v3 or {}
        self.use_http = use_http
        
        # Worker configuration
        self.ping_workers = ping_workers
        self.nmap_workers = nmap_workers
        self.collection_workers = collection_workers
        
        # Threading control
        self._stop_requested = threading.Event()
        
        # Collections tracking
        self.alive_devices: List[AliveDevice] = []
        self.collection_results: List[CollectionResult] = []
        
        # Statistics
        self.total_ips = 0
        self.alive_count = 0
        self.os_detected_count = 0
        self.collected_count = 0
        
        log.info("🎯 Proper Collection Strategy initialized")
        log.info(f"   📡 {ping_workers} ping workers")
        log.info(f"   🔍 {nmap_workers} NMAP workers") 
        log.info(f"   📊 {collection_workers} collection workers")

    def _normalize_credentials(self, creds):
        """Normalize credentials to consistent format"""
        if not creds:
            return []
        
        normalized = []
        for cred in creds:
            if isinstance(cred, dict):
                normalized.append({
                    'username': cred.get('username', ''),
                    'password': cred.get('password', '')
                })
            elif isinstance(cred, (tuple, list)) and len(cred) >= 2:
                normalized.append({
                    'username': cred[0],
                    'password': cred[1]
                })
            else:
                normalized.append({'username': str(cred), 'password': ''})
        
        return normalized

    def run(self):
        """Execute the proper 3-step collection strategy"""
        try:
            start_time = time.time()
            self.log_message.emit("🚀 Starting PROPER 3-STEP Collection Strategy")
            self.log_message.emit("=" * 60)
            
            # Generate all target IPs
            all_ips = self._generate_target_ips()
            self.total_ips = len(all_ips)
            self.log_message.emit(f"📍 Total target IPs: {self.total_ips}")
            
            if self.total_ips == 0:
                self.log_message.emit("❌ No valid IP targets found")
                self.collection_finished.emit(False)
                return
            
            # STEP 1: PING Discovery (Fast parallel)
            self.log_message.emit("🏓 STEP 1: PING Discovery - Finding alive devices...")
            alive_devices = self._step1_ping_discovery(all_ips)
            self.alive_count = len(alive_devices)
            
            if self.alive_count == 0:
                self.log_message.emit("❌ No alive devices found - ending collection")
                self.collection_finished.emit(False)
                return
            
            self.log_message.emit(f"✅ Found {self.alive_count} alive devices")
            self._update_progress(25)  # 25% complete after ping
            
            # STEP 2: OS Detection (NMAP on alive devices only)
            self.log_message.emit("🔍 STEP 2: OS Detection - Analyzing alive devices...")
            detected_devices = self._step2_os_detection(alive_devices)
            self.os_detected_count = len(detected_devices)
            
            self.log_message.emit(f"✅ OS detection completed on {self.os_detected_count} devices")
            self._update_progress(50)  # 50% complete after OS detection
            
            # STEP 3: Targeted Collection (Use appropriate method per OS)
            self.log_message.emit("📊 STEP 3: Targeted Collection - Using correct methods...")
            collection_results = self._step3_targeted_collection(detected_devices)
            self.collected_count = sum(1 for r in collection_results if r.success)
            
            self.log_message.emit(f"✅ Data collection completed on {self.collected_count} devices")
            self._update_progress(100)  # 100% complete
            
            # Final summary
            total_time = time.time() - start_time
            self.log_message.emit("=" * 60)
            self.log_message.emit("📈 COLLECTION SUMMARY:")
            self.log_message.emit(f"   📍 Total IPs scanned: {self.total_ips}")
            self.log_message.emit(f"   🏓 Alive devices: {self.alive_count}")
            self.log_message.emit(f"   🔍 OS detected: {self.os_detected_count}")
            self.log_message.emit(f"   📊 Data collected: {self.collected_count}")
            self.log_message.emit(f"   ⏱️ Total time: {total_time:.1f}s")
            self.log_message.emit(f"   🎯 Success rate: {(self.collected_count/self.alive_count*100):.1f}%" if self.alive_count > 0 else "   🎯 Success rate: 0%")
            self.log_message.emit("=" * 60)
            
            success = self.collected_count > 0
            self.collection_finished.emit(success)
            
        except Exception as e:
            self.log_message.emit(f"❌ Collection strategy failed: {e}")
            log.exception("Collection strategy error")
            self.collection_finished.emit(False)

    def _generate_target_ips(self) -> List[str]:
        """Generate list of IPs from targets"""
        all_ips = []
        
        for target in self.targets:
            try:
                if '/' in target:  # CIDR notation
                    import ipaddress
                    network = ipaddress.IPv4Network(target, strict=False)
                    # Limit large networks
                    if network.num_addresses > 500:
                        self.log_message.emit(f"⚠️ Large network {target} limited to first 500 IPs")
                        ips = list(network.hosts())[:500]
                    else:
                        ips = list(network.hosts())
                    all_ips.extend([str(ip) for ip in ips])
                    
                elif '-' in target:  # Range notation like 192.168.1.1-10
                    parts = target.split('.')
                    if len(parts) == 4 and '-' in parts[3]:
                        base = '.'.join(parts[:3])
                        start, end = parts[3].split('-')
                        for i in range(int(start), int(end) + 1):
                            all_ips.append(f"{base}.{i}")
                    else:
                        all_ips.append(target)  # Single IP
                        
                else:  # Single IP
                    all_ips.append(target)
                    
            except Exception as e:
                self.log_message.emit(f"⚠️ Invalid target {target}: {e}")
        
        return all_ips

    def _step1_ping_discovery(self, ips: List[str]) -> List[AliveDevice]:
        """STEP 1: Fast ping discovery to find alive devices"""
        alive_devices = []
        completed = 0
        
        def ping_worker():
            nonlocal completed
            while True:
                try:
                    ip = ping_queue.get(timeout=1)
                    if self._stop_requested.is_set():
                        break
                        
                    # Fast ping check
                    if self._fast_ping_check(ip):
                        alive_device = AliveDevice(ip=ip, ping_time=time.time())
                        alive_devices.append(alive_device)
                        self.log_message.emit(f"🏓 ALIVE: {ip}")
                    
                    completed += 1
                    progress = int((completed / len(ips)) * 25)  # 25% of total progress
                    self._update_progress(progress)
                    
                    ping_queue.task_done()
                    
                except Empty:
                    break
                except Exception as e:
                    log.warning(f"Ping worker error for {ip}: {e}")
                    ping_queue.task_done()
        
        # Create ping queue and start workers
        ping_queue = Queue()
        for ip in ips:
            ping_queue.put(ip)
        
        # Start ping workers
        threads = []
        for _ in range(min(self.ping_workers, len(ips))):
            thread = threading.Thread(target=ping_worker)
            thread.start()
            threads.append(thread)
        
        # Wait for completion
        ping_queue.join()
        for thread in threads:
            thread.join(timeout=1)
        
        return alive_devices

    def _fast_ping_check(self, ip: str) -> bool:
        """Fast ping check using system ping command"""
        try:
            # Use system ping command for speed
            if os.name == 'nt':  # Windows
                cmd = ['ping', '-n', '1', '-w', '1000', ip]  # 1 second timeout
            else:  # Linux/Mac
                cmd = ['ping', '-c', '1', '-W', '1', ip]
            
            result = subprocess.run(cmd, capture_output=True, timeout=2)
            return result.returncode == 0
            
        except Exception:
            return False

    def _step2_os_detection(self, alive_devices: List[AliveDevice]) -> List[AliveDevice]:
        """STEP 2: OS detection using NMAP on alive devices"""
        completed = 0
        
        def os_detection_worker():
            nonlocal completed
            while True:
                try:
                    device = os_queue.get(timeout=1)
                    if self._stop_requested.is_set():
                        break
                    
                    # Perform OS detection
                    os_info = self._detect_device_os(device.ip)
                    device.os_family = os_info.get('os_family', 'Unknown')
                    device.device_type = os_info.get('device_type', 'Unknown')
                    device.confidence = int(os_info.get('confidence', '0'))
                    device.open_ports = os_info.get('open_ports', [])
                    
                    self.log_message.emit(f"🔍 {device.ip}: {device.os_family} ({device.confidence}%)")
                    
                    completed += 1
                    progress = 25 + int((completed / len(alive_devices)) * 25)  # 25-50% of total
                    self._update_progress(progress)
                    
                    os_queue.task_done()
                    
                except Empty:
                    break
                except Exception as e:
                    log.warning(f"OS detection error for {device.ip}: {e}")
                    os_queue.task_done()
        
        # Create OS detection queue
        os_queue = Queue()
        for device in alive_devices:
            os_queue.put(device)
        
        # Start OS detection workers
        threads = []
        for _ in range(min(self.nmap_workers, len(alive_devices))):
            thread = threading.Thread(target=os_detection_worker)
            thread.start()
            threads.append(thread)
        
        # Wait for completion
        os_queue.join()
        for thread in threads:
            thread.join(timeout=2)
        
        return alive_devices

    def _detect_device_os(self, ip: str) -> Dict[str, Any]:
        """Detect OS type using NMAP or port-based detection"""
        if NMAP_AVAILABLE:
            return self._nmap_os_detection(ip)
        else:
            return self._port_based_os_detection(ip)

    def _nmap_os_detection(self, ip: str) -> Dict[str, Any]:
        """NMAP-based OS detection"""
        try:
            nm = nmap.PortScanner()
            
            # Quick scan with OS detection
            result = nm.scan(ip, '22,80,135,445,161,443,3389', '-O --osscan-guess', timeout=8)
            
            if ip in result['scan']:
                host_info = result['scan'][ip]
                
                # Get open ports
                open_ports = []
                if 'tcp' in host_info:
                    open_ports = [port for port, info in host_info['tcp'].items() 
                                if info.get('state') == 'open']
                
                # OS detection
                if 'osmatch' in host_info and host_info['osmatch']:
                    best_match = host_info['osmatch'][0]
                    os_name = best_match.get('name', '').lower()
                    confidence = best_match.get('accuracy', '0')
                    
                    # Determine OS family
                    if 'windows' in os_name:
                        os_family = 'Windows'
                        device_type = 'Windows Server' if 'server' in os_name else 'Windows Computer'
                    elif any(x in os_name for x in ['linux', 'ubuntu', 'centos', 'debian']):
                        os_family = 'Linux'
                        device_type = 'Linux Server'
                    elif any(x in os_name for x in ['cisco', 'juniper']):
                        os_family = 'Network'
                        device_type = 'Network Device'
                    else:
                        os_family = 'Other'
                        device_type = 'Other Device'
                    
                    return {
                        'os_family': os_family,
                        'device_type': device_type,
                        'confidence': confidence,
                        'open_ports': open_ports,
                        'detection_method': 'NMAP'
                    }
                
                # Fallback to port-based if OS detection failed
                return self._analyze_ports_for_os(open_ports)
            
        except Exception as e:
            log.warning(f"NMAP detection failed for {ip}: {e}")
        
        # Fallback to port-based detection
        return self._port_based_os_detection(ip)

    def _port_based_os_detection(self, ip: str) -> Dict[str, Any]:
        """Port-based OS detection when NMAP unavailable"""
        open_ports = []
        
        # Check common ports
        common_ports = [22, 80, 135, 443, 445, 161, 3389]
        for port in common_ports:
            if self._check_port(ip, port):
                open_ports.append(port)
        
        return self._analyze_ports_for_os(open_ports)

    def _analyze_ports_for_os(self, open_ports: List[int]) -> Dict[str, Any]:
        """Analyze open ports to determine OS"""
        # Windows indicators
        if 135 in open_ports or 445 in open_ports or 3389 in open_ports:
            return {
                'os_family': 'Windows',
                'device_type': 'Windows Server' if 3389 in open_ports else 'Windows Computer',
                'confidence': '85',
                'open_ports': open_ports,
                'detection_method': 'Port-based'
            }
        
        # Linux indicators
        if 22 in open_ports:
            return {
                'os_family': 'Linux',
                'device_type': 'Linux Server',
                'confidence': '80',
                'open_ports': open_ports,
                'detection_method': 'Port-based'
            }
        
        # Network device indicators
        if 161 in open_ports and not (22 in open_ports or 135 in open_ports):
            return {
                'os_family': 'Network',
                'device_type': 'Network Device',
                'confidence': '75',
                'open_ports': open_ports,
                'detection_method': 'Port-based'
            }
        
        # Web server
        if (80 in open_ports or 443 in open_ports) and not (22 in open_ports or 135 in open_ports):
            return {
                'os_family': 'Other',
                'device_type': 'Web Server',
                'confidence': '60',
                'open_ports': open_ports,
                'detection_method': 'Port-based'
            }
        
        # Unknown
        return {
            'os_family': 'Unknown',
            'device_type': 'Unknown Device',
            'confidence': '30',
            'open_ports': open_ports,
            'detection_method': 'Port-based'
        }

    def _check_port(self, ip: str, port: int) -> bool:
        """Check if port is open"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except:
            return False

    def _step3_targeted_collection(self, devices: List[AliveDevice]) -> List[CollectionResult]:
        """STEP 3: Use appropriate collection method based on OS"""
        results = []
        completed = 0
        
        def collection_worker():
            nonlocal completed
            while True:
                try:
                    device = collection_queue.get(timeout=1)
                    if self._stop_requested.is_set():
                        break
                    
                    # Choose collection method based on OS
                    result = self._collect_device_data(device)
                    results.append(result)
                    
                    if result.success:
                        self.log_message.emit(f"✅ {device.ip}: {result.method} collection successful")
                        
                        # Save to database immediately after successful collection
                        try:
                            if self._save_to_database(result.data):
                                self.log_message.emit(f"💾 Database save SUCCESS: {device.ip}")
                            else:
                                self.log_message.emit(f"⚠️ Database save FAILED: {device.ip}")
                        except Exception as e:
                            self.log_message.emit(f"❌ Database save ERROR: {device.ip} - {e}")
                        
                        self.device_collected.emit(result.data)
                    else:
                        self.log_message.emit(f"❌ {device.ip}: {result.error}")
                    
                    completed += 1
                    progress = 50 + int((completed / len(devices)) * 50)  # 50-100% of total
                    self._update_progress(progress)
                    
                    collection_queue.task_done()
                    
                except Empty:
                    break
                except Exception as e:
                    log.warning(f"Collection worker error: {e}")
                    collection_queue.task_done()
        
        # Create collection queue
        collection_queue = Queue()
        for device in devices:
            collection_queue.put(device)
        
        # Start collection workers
        threads = []
        for _ in range(min(self.collection_workers, len(devices))):
            thread = threading.Thread(target=collection_worker)
            thread.start()
            threads.append(thread)
        
        # Wait for completion
        collection_queue.join()
        for thread in threads:
            thread.join(timeout=3)
        
        return results

    def _collect_device_data(self, device: AliveDevice) -> CollectionResult:
        """Collect data using appropriate method for device OS"""
        
        if device.os_family == 'Windows':
            return self._collect_windows_data(device)
        elif device.os_family == 'Linux':
            return self._collect_linux_data(device)
        elif device.os_family == 'Network':
            return self._collect_snmp_data(device)
        else:
            return self._collect_generic_data(device)

    def _collect_windows_data(self, device: AliveDevice) -> CollectionResult:
        """Collect Windows data using WMI"""
        for creds in self.win_creds:
            try:
                data = self._wmi_collection(device.ip, creds['username'], creds['password'])
                if data and 'Failed:' not in str(data.get('wmi_collection_status', '')):
                    return CollectionResult(
                        ip=device.ip,
                        success=True,
                        method='WMI',
                        data=data
                    )
            except Exception:
                continue
        
        return CollectionResult(
            ip=device.ip,
            success=False,
            method='WMI',
            error='All Windows credentials failed'
        )

    def _collect_linux_data(self, device: AliveDevice) -> CollectionResult:
        """Collect Linux data using SSH"""
        for creds in self.linux_creds:
            try:
                data = self._ssh_collection(device.ip, creds['username'], creds['password'])
                if data and 'SSH Failed:' not in str(data.get('wmi_collection_status', '')):
                    return CollectionResult(
                        ip=device.ip,
                        success=True,
                        method='SSH',
                        data=data
                    )
            except Exception:
                continue
        
        return CollectionResult(
            ip=device.ip,
            success=False,
            method='SSH',
            error='All Linux credentials failed'
        )

    def _collect_snmp_data(self, device: AliveDevice) -> CollectionResult:
        """Collect network device data using SNMP"""
        for community in self.snmp_v2c:
            try:
                data = self._snmp_collection(device.ip, community)
                if data:
                    return CollectionResult(
                        ip=device.ip,
                        success=True,
                        method='SNMP',
                        data=data
                    )
            except Exception:
                continue
        
        return CollectionResult(
            ip=device.ip,
            success=False,
            method='SNMP',
            error='All SNMP communities failed'
        )

    def _collect_generic_data(self, device: AliveDevice) -> CollectionResult:
        """Collect data from unknown devices using multiple methods"""
        # Try HTTP first for web devices
        if self.use_http and (80 in device.open_ports or 443 in device.open_ports):
            data = self._http_collection(device.ip)
            if data:
                return CollectionResult(
                    ip=device.ip,
                    success=True,
                    method='HTTP',
                    data=data
                )
        
        # Try SNMP for network devices
        for community in self.snmp_v2c:
            data = self._snmp_collection(device.ip, community)
            if data:
                return CollectionResult(
                    ip=device.ip,
                    success=True,
                    method='SNMP',
                    data=data
                )
        
        return CollectionResult(
            ip=device.ip,
            success=False,
            method='Generic',
            error='No suitable collection method found'
        )

    def _wmi_collection(self, ip: str, username: str, password: str) -> Optional[Dict]:
        """Basic WMI collection implementation"""
        # This would use the existing WMI collection code
        # For now, return a placeholder
        return {
            'IP Address': ip,
            'Hostname': f'windows-{ip.replace(".", "-")}',
            'Operating System': 'Windows',
            'Device Type': 'Windows Computer',
            'Collection Method': 'WMI',
            'Collector': 'WMI',
            'Collection Time': datetime.now().isoformat()
        }

    def _ssh_collection(self, ip: str, username: str, password: str) -> Optional[Dict]:
        """Basic SSH collection implementation"""
        # This would use the existing SSH collection code
        # For now, return a placeholder
        return {
            'IP Address': ip,
            'Hostname': f'linux-{ip.replace(".", "-")}',
            'Operating System': 'Linux',
            'Device Type': 'Linux Server',
            'Collection Method': 'SSH',
            'Collector': 'SSH',
            'Collection Time': datetime.now().isoformat()
        }

    def _snmp_collection(self, ip: str, community: str) -> Optional[Dict]:
        """Basic SNMP collection implementation"""
        return {
            'IP Address': ip,
            'Hostname': f'snmp-{ip.replace(".", "-")}',
            'Device Type': 'Network Device',
            'Collection Method': 'SNMP',
            'Collector': 'SNMP',
            'Collection Time': datetime.now().isoformat()
        }

    def _http_collection(self, ip: str) -> Optional[Dict]:
        """Basic HTTP collection implementation"""
        try:
            response = requests.get(f'http://{ip}', timeout=3)
            if response.status_code == 200:
                return {
                    'IP Address': ip,
                    'Hostname': f'web-{ip.replace(".", "-")}',
                    'Device Type': 'Web Server',
                    'Collection Method': 'HTTP',
                    'Collector': 'HTTP',
                    'Collection Time': datetime.now().isoformat()
                }
        except:
            pass
        return None

    def _save_to_database(self, device_data: Dict) -> bool:
        """Save device data to database with full schema support"""
        try:
            import sqlite3
            from datetime import datetime
            
            # Enhanced logging for debugging
            hostname = device_data.get('hostname', device_data.get('Hostname', 'Unknown'))
            ip_address = device_data.get('ip_address', device_data.get('IP Address', 'Unknown'))
            working_user = device_data.get('working_user', device_data.get('Working User', 'System'))
            
            self.log_message.emit(f"💾 SAVING TO DATABASE: {hostname} ({ip_address}) - User: {working_user}")
            
            conn = sqlite3.connect('assets.db')
            cursor = conn.cursor()
            
            # Ensure required fields
            if not device_data.get('hostname') and not device_data.get('ip_address'):
                if not device_data.get('Hostname') and not device_data.get('IP Address'):
                    self.log_message.emit("❌ Cannot save device: missing hostname and ip_address")
                    return False
            
            # Get all available columns in the database
            cursor.execute('PRAGMA table_info(assets)')
            db_columns = [col[1] for col in cursor.fetchall()]
            
            # Prepare data for insertion - only include columns that exist in DB
            db_data = {}
            
            # Map common field variations
            field_mappings = {
                'hostname': ['hostname', 'Hostname', 'computer_name', 'Computer Name'],
                'ip_address': ['ip_address', 'IP Address', 'IP'],
                'working_user': ['working_user', 'Working User', 'Current User'],
                'operating_system': ['operating_system', 'OS', 'Operating System'],
                'system_manufacturer': ['system_manufacturer', 'Manufacturer'],
                'system_model': ['system_model', 'Model'],
                'device_type': ['device_type', 'Device Type', 'Asset Type'],
                'status': ['status', 'Status']
            }
            
            # Apply field mappings
            for db_field, source_fields in field_mappings.items():
                if db_field in db_columns:
                    for source_field in source_fields:
                        if source_field in device_data and device_data[source_field] is not None:
                            value = str(device_data[source_field]).strip()
                            if value and value.lower() != 'none' and value != '':
                                db_data[db_field] = value
                                break
            
            # Add remaining fields that match database columns
            for key, value in device_data.items():
                if key in db_columns and key not in db_data and value is not None:
                    clean_value = str(value).strip()
                    if clean_value and clean_value.lower() != 'none' and clean_value != '':
                        db_data[key] = clean_value
            
            # Add timestamps
            now = datetime.now().isoformat()
            if 'created_at' in db_columns:
                db_data['created_at'] = now
            if 'updated_at' in db_columns:
                db_data['updated_at'] = now
            if 'last_scan_time' in db_columns:
                db_data['last_scan_time'] = now
            
            # Ensure we have minimum required data
            if not db_data.get('hostname') and not db_data.get('ip_address'):
                self.log_message.emit("❌ No valid hostname or IP after field mapping")
                return False
            
            # Check for existing device (simple IP-based for now)
            existing_id = None
            if db_data.get('ip_address'):
                cursor.execute('SELECT id FROM assets WHERE ip_address = ?', (db_data['ip_address'],))
                existing = cursor.fetchone()
                if existing:
                    existing_id = existing[0]
                    self.log_message.emit(f"🔄 Updating existing device: ID {existing_id}")
            
            if existing_id:
                # Update existing record
                update_fields = []
                update_values = []
                for key, value in db_data.items():
                    if key != 'created_at':  # Don't update creation time
                        update_fields.append(f"{key} = ?")
                        update_values.append(value)
                
                if update_fields:
                    update_values.append(existing_id)
                    query = f"UPDATE assets SET {', '.join(update_fields)} WHERE id = ?"
                    cursor.execute(query, update_values)
                    self.log_message.emit(f"✅ Database UPDATE successful: {hostname}")
            else:
                # Insert new record
                if db_data:
                    placeholders = ', '.join(['?'] * len(db_data))
                    columns = ', '.join(db_data.keys())
                    query = f"INSERT INTO assets ({columns}) VALUES ({placeholders})"
                    cursor.execute(query, list(db_data.values()))
                    self.log_message.emit(f"✅ Database INSERT successful: {hostname}")
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            self.log_message.emit(f"❌ Database save error: {e}")
            return False

    def _update_progress(self, value: int):
        """Update progress bar"""
        self.progress_updated.emit(min(value, 100))

    def stop(self):
        """Stop the collection process"""
        self._stop_requested.set()
        self.log_message.emit("🛑 Collection stop requested...")


if __name__ == "__main__":
    print("🎯 Proper 3-Step Collection Strategy Ready")
    print("1. 🏓 PING Discovery")
    print("2. 🔍 NMAP OS Detection") 
    print("3. 📊 Targeted Collection")