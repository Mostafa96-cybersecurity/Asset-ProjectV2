#!/usr/bin/env python3
"""
Enhanced Collection Strategy with Proper Device Types & Maximum Data Collection
تحسين استراتيجية الجمع مع أنواع الأجهزة الصحيحة وجمع أقصى بيانات ممكنة
"""

import time
import threading
import ipaddress
import subprocess
import socket
from queue import Queue, Empty
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import logging
import nmap
import requests
from requests.auth import HTTPBasicAuth

from PyQt6.QtCore import QThread, pyqtSignal, QObject

# Optional imports for enhanced collection
try:
    import paramiko
    PARAMIKO_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False

try:
    from pysnmp.hlapi import (
        nextCmd, SnmpEngine, CommunityData, UdpTransportTarget, 
        ContextData, ObjectType, ObjectIdentity
    )
    PYSNMP_AVAILABLE = True
except ImportError:
    PYSNMP_AVAILABLE = False

try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False

# Setup logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

@dataclass
class AliveDevice:
    """Enhanced device information with proper classification"""
    ip: str
    ping_time: float = 0.0
    os_family: str = 'Unknown'
    device_type: str = 'Unknown'  # Will be one of the 10 proper types
    device_subtype: str = 'Unknown'
    open_ports: List[int] = None
    services: Dict[str, str] = None
    os_details: Dict[str, str] = None
    confidence: int = 0
    
    def __post_init__(self):
        if self.open_ports is None:
            self.open_ports = []
        if self.services is None:
            self.services = {}
        if self.os_details is None:
            self.os_details = {}

@dataclass
class CollectionResult:
    """Enhanced collection result with comprehensive data"""
    ip: str
    success: bool
    method: str
    device_type: str = 'Unknown'
    data: Optional[Dict] = None
    error: Optional[str] = None
    collection_time: float = 0.0
    data_completeness: float = 0.0

class EnhancedCollectionStrategy(QThread):
    """
    Enhanced 3-Step Collection Strategy with Maximum Data Collection
    استراتيجية جمع محسنة بثلاث خطوات مع جمع أقصى بيانات
    """
    
    # Qt signals
    log_message = pyqtSignal(str)
    device_collected = pyqtSignal(dict)
    collection_finished = pyqtSignal(bool)
    progress_updated = pyqtSignal(int)
    
    # Proper Device Types (10 categories as requested)
    DEVICE_TYPES = {
        'WORKSTATION': 'Workstations',
        'LAPTOP': 'Laptops', 
        'WINDOWS_SERVER': 'Windows Servers',
        'LINUX_SERVER': 'Linux Servers',
        'FIREWALL': 'Firewalls',
        'SWITCH': 'Switches',
        'ACCESS_POINT': 'Access Points',
        'HYPERVISOR': 'Hypervisors',
        'FINGERPRINT': 'Finger Prints',
        'PRINTER': 'Printers'
    }
    
    # Port signatures for device type detection
    PORT_SIGNATURES = {
        'WINDOWS_SERVER': [3389, 135, 445, 53, 88],  # RDP, RPC, SMB, DNS, Kerberos
        'LINUX_SERVER': [22, 80, 443, 25, 21],       # SSH, HTTP, HTTPS, SMTP, FTP
        'FIREWALL': [22, 443, 8080, 4343],           # SSH, HTTPS, Web UI
        'SWITCH': [22, 23, 80, 443, 161],            # SSH, Telnet, HTTP, HTTPS, SNMP
        'ACCESS_POINT': [22, 80, 443, 161],          # SSH, HTTP, HTTPS, SNMP
        'HYPERVISOR': [22, 80, 443, 902, 5988],      # SSH, HTTP, HTTPS, VMware, WinRM
        'PRINTER': [9100, 631, 80, 443, 161],        # IPP, CUPS, HTTP, HTTPS, SNMP
        'FINGERPRINT': [80, 443, 4370]               # HTTP, HTTPS, Bio devices
    }

    def __init__(self, targets: List[str], credentials: Dict, parent=None):
        super().__init__(parent)
        
        self.targets = targets
        self.win_creds = self._normalize_credentials(credentials.get('windows', []))
        self.linux_creds = self._normalize_credentials(credentials.get('linux', []))
        self.snmp_v2c = credentials.get('snmp_v2c', ['public', 'private'])
        self.snmp_v3 = credentials.get('snmp_v3', [])
        self.use_http = credentials.get('use_http', True)
        
        # Enhanced worker configuration for maximum performance
        self.ping_workers = 100      # Fast ping discovery
        self.nmap_workers = 20       # Comprehensive port scanning
        self.collection_workers = 15 # Maximum data collection
        
        # Collection statistics
        self.total_ips = 0
        self.alive_count = 0
        self.os_detected_count = 0
        self.collected_count = 0
        
        self._stop_requested = threading.Event()
        
        self.log_message.emit("🚀 Enhanced Collection Strategy Initialized")
        self.log_message.emit(f"   🎯 Proper Device Types: {len(self.DEVICE_TYPES)}")
        self.log_message.emit(f"   📡 Ping workers: {self.ping_workers}")
        self.log_message.emit(f"   🔍 NMAP workers: {self.nmap_workers}")
        self.log_message.emit(f"   📊 Collection workers: {self.collection_workers}")

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
        """Execute enhanced 3-step collection strategy"""
        try:
            start_time = time.time()
            self.log_message.emit("🚀 ENHANCED 3-STEP COLLECTION STRATEGY")
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
            
            self.log_message.emit(f"✅ Alive devices found: {self.alive_count}")
            self._update_progress(25)  # 25% complete after ping
            
            # STEP 2: Enhanced OS & Device Type Detection
            self.log_message.emit("🔍 STEP 2: Enhanced OS & Device Type Detection...")
            detected_devices = self._step2_enhanced_detection(alive_devices)
            self.os_detected_count = len([d for d in detected_devices if d.os_family != 'Unknown'])
            
            self.log_message.emit(f"✅ Device type detection completed on {len(detected_devices)} devices")
            self._update_progress(50)  # 50% complete after detection
            
            # STEP 3: Maximum Data Collection (Enhanced Strategy)
            self.log_message.emit("📊 STEP 3: Maximum Data Collection - Enhanced strategy...")
            collection_results = self._step3_maximum_collection(detected_devices)
            self.collected_count = sum(1 for r in collection_results if r.success)
            
            self.log_message.emit(f"✅ Data collection completed on {self.collected_count} devices")
            self._update_progress(100)  # 100% complete
            
            # Enhanced summary with device type breakdown
            total_time = time.time() - start_time
            self.log_message.emit("=" * 60)
            self.log_message.emit("📈 ENHANCED COLLECTION SUMMARY:")
            self.log_message.emit(f"   📍 Total IPs scanned: {self.total_ips}")
            self.log_message.emit(f"   🏓 Alive devices: {self.alive_count}")
            self.log_message.emit(f"   🔍 Device types detected: {self.os_detected_count}")
            self.log_message.emit(f"   📊 Data collected: {self.collected_count}")
            self.log_message.emit(f"   ⏱️ Total time: {total_time:.1f}s")
            self.log_message.emit(f"   🎯 Success rate: {(self.collected_count/self.alive_count*100):.1f}%" if self.alive_count > 0 else "   🎯 Success rate: 0%")
            
            # Device type breakdown
            type_counts = {}
            for result in collection_results:
                device_type = result.device_type
                type_counts[device_type] = type_counts.get(device_type, 0) + 1
            
            self.log_message.emit("   📱 Device Types Found:")
            for device_type, count in sorted(type_counts.items()):
                self.log_message.emit(f"     • {device_type}: {count} devices")
            
            self.log_message.emit("=" * 60)
            
            success = self.collected_count > 0
            self.collection_finished.emit(success)
            
        except Exception as e:
            self.log_message.emit(f"❌ Enhanced collection strategy failed: {e}")
            log.exception("Enhanced collection strategy error")
            self.collection_finished.emit(False)

    def _generate_target_ips(self) -> List[str]:
        """Generate list of IPs from targets"""
        all_ips = []
        
        for target in self.targets:
            try:
                if '/' in target:  # CIDR notation
                    network = ipaddress.IPv4Network(target, strict=False)
                    all_ips.extend([str(ip) for ip in network.hosts()])
                elif '-' in target:  # Range notation (e.g., 192.168.1.1-50)
                    base_ip, range_part = target.rsplit('.', 1)
                    if '-' in range_part:
                        start, end = map(int, range_part.split('-'))
                        for i in range(start, end + 1):
                            all_ips.append(f"{base_ip}.{i}")
                else:  # Single IP
                    ipaddress.IPv4Address(target)  # Validate
                    all_ips.append(target)
            except Exception as e:
                self.log_message.emit(f"⚠️ Invalid target '{target}': {e}")
        
        return all_ips

    def _step1_ping_discovery(self, all_ips: List[str]) -> List[AliveDevice]:
        """Step 1: Fast ping discovery to find alive devices"""
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
                    start_time = time.time()
                    if self._fast_ping(ip):
                        ping_time = (time.time() - start_time) * 1000
                        device = AliveDevice(ip=ip, ping_time=ping_time)
                        alive_devices.append(device)
                        self.log_message.emit(f"🟢 {ip} alive ({ping_time:.1f}ms)")
                    
                    completed += 1
                    progress = int((completed / len(all_ips)) * 25)  # 0-25% of total
                    self._update_progress(progress)
                    
                    ping_queue.task_done()
                    
                except Empty:
                    break
                except Exception as e:
                    log.warning(f"Ping worker error: {e}")
                    ping_queue.task_done()
        
        # Create ping queue
        ping_queue = Queue()
        for ip in all_ips:
            ping_queue.put(ip)
        
        # Start ping workers
        threads = []
        for _ in range(min(self.ping_workers, len(all_ips))):
            thread = threading.Thread(target=ping_worker)
            thread.start()
            threads.append(thread)
        
        # Wait for completion
        ping_queue.join()
        for thread in threads:
            thread.join(timeout=3)
        
        return alive_devices

    def _step2_enhanced_detection(self, devices: List[AliveDevice]) -> List[AliveDevice]:
        """Step 2: Enhanced OS and device type detection using NMAP"""
        detected_devices = []
        completed = 0
        
        def detection_worker():
            nonlocal completed
            while True:
                try:
                    device = detection_queue.get(timeout=1)
                    if self._stop_requested.is_set():
                        break
                    
                    # Enhanced NMAP scan for OS and service detection
                    nmap_result = self._enhanced_nmap_scan(device.ip)
                    if nmap_result:
                        # Update device information
                        device.os_family = nmap_result.get('os_family', 'Unknown')
                        device.open_ports = nmap_result.get('open_ports', [])
                        device.services = nmap_result.get('services', {})
                        device.os_details = nmap_result.get('os_details', {})
                        
                        # Classify device using enhanced classification
                        device_info = {
                            'open_ports': device.open_ports,
                            'services': list(device.services.keys()),
                            'os_family': device.os_family,
                            'hostname': nmap_result.get('hostname', ''),
                            'ip': device.ip
                        }
                        device.device_type = self.classify_device(device_info)
                        device.confidence = nmap_result.get('confidence', 0)
                        
                        self.log_message.emit(f"🔍 {device.ip}: {device.device_type} ({device.os_family}) - {len(device.open_ports)} ports")
                    
                    detected_devices.append(device)
                    
                    completed += 1
                    progress = 25 + int((completed / len(devices)) * 25)  # 25-50% of total
                    self._update_progress(progress)
                    
                    detection_queue.task_done()
                    
                except Empty:
                    break
                except Exception as e:
                    log.warning(f"Detection worker error: {e}")
                    detection_queue.task_done()
        
        # Create detection queue
        detection_queue = Queue()
        for device in devices:
            detection_queue.put(device)
        
        # Start detection workers
        threads = []
        for _ in range(min(self.nmap_workers, len(devices))):
            thread = threading.Thread(target=detection_worker)
            thread.start()
            threads.append(thread)
        
        # Wait for completion
        detection_queue.join()
        for thread in threads:
            thread.join(timeout=5)
        
        return detected_devices

    def classify_device(self, device_info: Dict) -> str:
        """
        Classify device into one of 10 proper device types
        تصنيف الجهاز إلى أحد أنواع الأجهزة العشرة الصحيحة
        """
        open_ports = device_info.get('open_ports', [])
        services = device_info.get('services', [])
        os_family = device_info.get('os_family', '').lower()
        hostname = device_info.get('hostname', '').lower()
        
        # Score each device type based on port signatures and OS
        scores = {}
        
        # Windows Server vs Workstation detection
        if any(port in open_ports for port in [135, 445]) and 'windows' in os_family:
            # Check for server-specific ports first
            if any(port in open_ports for port in [3389, 53, 88, 389, 636]):  # RDP, DNS, Kerberos, LDAP
                scores['WINDOWS_SERVER'] = 90
            elif any(word in hostname for word in ['server', 'srv', 'dc', 'domain', 'exchange', 'sql']):
                scores['WINDOWS_SERVER'] = 85
            else:
                # Likely a workstation/laptop
                if 'laptop' in hostname or 'mobile' in hostname or 'book' in hostname:
                    scores['LAPTOP'] = 70
                else:
                    scores['WORKSTATION'] = 70
        
        # Linux Server detection
        if 22 in open_ports and ('linux' in os_family or 'unix' in os_family):
            scores['LINUX_SERVER'] = 70
            if any(port in open_ports for port in [80, 443, 25, 21, 53]):  # Web, mail, DNS
                scores['LINUX_SERVER'] += 30
        
        # Network device detection
        if 161 in open_ports:  # SNMP
            if 23 in open_ports:  # Telnet - likely switch
                scores['SWITCH'] = 70
            elif any(word in hostname for word in ['ap', 'wifi', 'wireless', 'access']):
                scores['ACCESS_POINT'] = 80
            else:
                scores['SWITCH'] = 50
        
        # Firewall detection
        if any(port in open_ports for port in [8080, 4343, 8443]) and 22 in open_ports:
            scores['FIREWALL'] = 70
            if any(word in hostname for word in ['fw', 'firewall', 'asa', 'palo', 'fortinet']):
                scores['FIREWALL'] += 30
        
        # Hypervisor detection
        if any(port in open_ports for port in [902, 5988, 8006, 9440]):
            scores['HYPERVISOR'] = 80
            if any(word in hostname for word in ['esxi', 'vcenter', 'hyper', 'xen', 'proxmox']):
                scores['HYPERVISOR'] += 20
        
        # Printer detection
        if any(port in open_ports for port in [9100, 631]):
            scores['PRINTER'] = 90
            if any(word in hostname for word in ['printer', 'hp', 'canon', 'epson', 'lexmark']):
                scores['PRINTER'] += 10
        
        # Fingerprint device detection
        if 4370 in open_ports or any(word in hostname for word in ['finger', 'bio', 'zk']):
            scores['FINGERPRINT'] = 85
        
        # Return the highest scoring device type
        if scores:
            best_type = max(scores.items(), key=lambda x: x[1])
            if best_type[1] >= 50:  # Minimum confidence threshold
                return self.DEVICE_TYPES[best_type[0]]
        
        return 'Unknown Device'

    def _enhanced_nmap_scan(self, ip: str) -> Optional[Dict]:
        """Enhanced NMAP scan for comprehensive device detection"""
        try:
            nm = nmap.PortScanner()
            
            # Comprehensive scan: OS detection, service detection, aggressive timing
            scan_result = nm.scan(
                ip, 
                '21,22,23,25,53,80,135,139,443,445,993,995,3389,5985,5986,8080,9100,161,162,902,4343,4370,631',
                arguments='-O -sV -sS --osscan-guess --max-os-tries=2 -T4'
            )
            
            if ip not in scan_result['scan']:
                return None
            
            host_info = scan_result['scan'][ip]
            result = {
                'os_family': 'Unknown',
                'open_ports': [],
                'services': {},
                'os_details': {},
                'confidence': 0,
                'hostname': ''
            }
            
            # Extract open ports and services
            if 'tcp' in host_info:
                for port, info in host_info['tcp'].items():
                    if info.get('state') == 'open':
                        result['open_ports'].append(port)
                        result['services'][port] = {
                            'name': info.get('name', ''),
                            'product': info.get('product', ''),
                            'version': info.get('version', ''),
                            'extrainfo': info.get('extrainfo', ''),
                            'conf': info.get('conf', 0)
                        }
            
            # Extract hostname
            if 'hostnames' in host_info and host_info['hostnames']:
                result['hostname'] = host_info['hostnames'][0].get('name', '')
            
            # OS detection
            if 'osmatch' in host_info and host_info['osmatch']:
                best_match = host_info['osmatch'][0]
                os_name = best_match.get('name', '').lower()
                result['confidence'] = int(best_match.get('accuracy', 0))
                
                # Enhanced OS family classification
                if any(x in os_name for x in ['windows', 'microsoft']):
                    result['os_family'] = 'Windows'
                elif any(x in os_name for x in ['linux', 'ubuntu', 'centos', 'debian', 'redhat', 'suse']):
                    result['os_family'] = 'Linux'
                elif any(x in os_name for x in ['vmware', 'esxi', 'xenserver', 'hyper-v']):
                    result['os_family'] = 'Hypervisor'
                elif any(x in os_name for x in ['cisco', 'juniper', 'fortinet', 'palo alto', 'checkpoint']):
                    result['os_family'] = 'Network'
                
                result['os_details'] = {
                    'name': best_match.get('name', ''),
                    'accuracy': best_match.get('accuracy', 0),
                    'line': best_match.get('line', 0),
                    'osclass': host_info.get('osclass', [])
                }
            
            return result
            
        except Exception as e:
            self.log_message.emit(f"NMAP scan error for {ip}: {e}")
            return None

    def _step3_maximum_collection(self, devices: List[AliveDevice]) -> List[CollectionResult]:
        """Step 3: Maximum data collection using enhanced strategy"""
        results = []
        completed = 0
        
        def collection_worker():
            nonlocal completed
            while True:
                try:
                    device = collection_queue.get(timeout=1)
                    if self._stop_requested.is_set():
                        break
                    
                    # Enhanced collection strategy based on device type
                    result = self._enhanced_device_collection(device)
                    results.append(result)
                    
                    if result.success:
                        self.log_message.emit(f"✅ {device.ip}: {result.method} collection successful ({result.data_completeness:.1f}% complete)")
                        
                        # Save to database immediately
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
            thread.join(timeout=10)
        
        return results

    def _enhanced_device_collection(self, device: AliveDevice) -> CollectionResult:
        """Enhanced data collection strategy based on device type and OS"""
        start_time = time.time()
        
        # Collection strategy based on device type
        if device.device_type in ['Workstations', 'Laptops', 'Windows Servers']:
            # Windows devices: WMI first, then SNMP if fails
            result = self._windows_maximum_collection(device)
            if not result.success:
                result = self._snmp_fallback_collection(device)
        
        elif device.device_type in ['Linux Servers', 'Hypervisors']:
            # Linux/Hypervisor: SSH first, then SNMP if fails
            result = self._linux_maximum_collection(device)
            if not result.success:
                result = self._snmp_fallback_collection(device)
        
        elif device.device_type in ['Firewalls', 'Switches', 'Access Points']:
            # Network devices: SSH first, then SNMP if fails
            result = self._network_device_collection(device)
            if not result.success:
                result = self._snmp_fallback_collection(device)
        
        elif device.device_type in ['Printers', 'Finger Prints']:
            # Special devices: SNMP first, then SSH if available
            result = self._snmp_fallback_collection(device)
            if not result.success and 22 in device.open_ports:
                result = self._ssh_fallback_collection(device)
        
        else:
            # Unknown devices: Try SSH first, then SNMP, finally HTTP for service detection
            result = self._unknown_device_collection(device)
        
        result.collection_time = time.time() - start_time
        result.device_type = device.device_type
        
        return result

    def _windows_maximum_collection(self, device: AliveDevice) -> CollectionResult:
        """Maximum WMI data collection for Windows devices"""
        try:
            # Comprehensive WMI collection
            data = self._comprehensive_wmi_collection(device.ip)
            if data:
                # Calculate data completeness
                completeness = self._calculate_data_completeness(data, 'windows')
                return CollectionResult(
                    ip=device.ip,
                    success=True,
                    method='Comprehensive WMI',
                    data=data,
                    data_completeness=completeness
                )
        except Exception as e:
            pass
        
        return CollectionResult(
            ip=device.ip,
            success=False,
            method='WMI',
            error='WMI collection failed'
        )

    def _linux_maximum_collection(self, device: AliveDevice) -> CollectionResult:
        """Maximum SSH data collection for Linux devices"""
        for creds in self.linux_creds:
            try:
                data = self._comprehensive_ssh_collection(device.ip, creds['username'], creds['password'])
                if data:
                    completeness = self._calculate_data_completeness(data, 'linux')
                    return CollectionResult(
                        ip=device.ip,
                        success=True,
                        method='Comprehensive SSH',
                        data=data,
                        data_completeness=completeness
                    )
            except Exception as e:
                continue
        
        return CollectionResult(
            ip=device.ip,
            success=False,
            method='SSH',
            error='All SSH credentials failed'
        )

    def _network_device_collection(self, device: AliveDevice) -> CollectionResult:
        """SSH then SNMP collection for network devices"""
        # Try SSH first (many modern network devices support SSH)
        for creds in self.linux_creds:
            try:
                data = self._network_ssh_collection(device.ip, creds['username'], creds['password'])
                if data:
                    completeness = self._calculate_data_completeness(data, 'network')
                    return CollectionResult(
                        ip=device.ip,
                        success=True,
                        method='Network SSH',
                        data=data,
                        data_completeness=completeness
                    )
            except Exception as e:
                continue
        
        # Fallback to SNMP
        return self._snmp_fallback_collection(device)

    def _snmp_fallback_collection(self, device: AliveDevice) -> CollectionResult:
        """Comprehensive SNMP data collection"""
        for community in self.snmp_v2c:
            try:
                data = self._comprehensive_snmp_collection(device.ip, community)
                if data:
                    completeness = self._calculate_data_completeness(data, 'snmp')
                    return CollectionResult(
                        ip=device.ip,
                        success=True,
                        method='Comprehensive SNMP',
                        data=data,
                        data_completeness=completeness
                    )
            except Exception as e:
                continue
        
        return CollectionResult(
            ip=device.ip,
            success=False,
            method='SNMP',
            error='All SNMP communities failed'
        )

    def _ssh_fallback_collection(self, device: AliveDevice) -> CollectionResult:
        """SSH fallback for special devices"""
        for creds in self.linux_creds:
            try:
                data = self._basic_ssh_collection(device.ip, creds['username'], creds['password'])
                if data:
                    completeness = self._calculate_data_completeness(data, 'basic')
                    return CollectionResult(
                        ip=device.ip,
                        success=True,
                        method='SSH Fallback',
                        data=data,
                        data_completeness=completeness
                    )
            except Exception as e:
                continue
        
        return CollectionResult(
            ip=device.ip,
            success=False,
            method='SSH',
            error='SSH fallback failed'
        )

    def _unknown_device_collection(self, device: AliveDevice) -> CollectionResult:
        """Collection strategy for unknown devices"""
        # Try SSH first
        if 22 in device.open_ports:
            result = self._ssh_fallback_collection(device)
            if result.success:
                return result
        
        # Try SNMP
        result = self._snmp_fallback_collection(device)
        if result.success:
            return result
        
        # Finally, HTTP for service detection only
        if self.use_http and (80 in device.open_ports or 443 in device.open_ports):
            try:
                data = self._http_service_detection(device.ip)
                if data:
                    return CollectionResult(
                        ip=device.ip,
                        success=True,
                        method='HTTP Service Detection',
                        data=data,
                        data_completeness=10.0  # Very basic data
                    )
            except Exception as e:
                pass
        
        return CollectionResult(
            ip=device.ip,
            success=False,
            method='Unknown',
            error='All collection methods failed'
        )

    def _comprehensive_wmi_collection(self, ip: str) -> Optional[Dict]:
        """Comprehensive WMI collection - everything WMI can provide"""
        try:
            import wmi
            
            # Try different connection methods
            for creds in self.win_creds:
                try:
                    # Connect to WMI
                    if creds['username'] and creds['password']:
                        conn = wmi.WMI(computer=ip, user=creds['username'], password=creds['password'])
                    else:
                        conn = wmi.WMI(computer=ip)
                    
                    data = {
                        'IP Address': ip,
                        'Collection Method': 'Comprehensive WMI',
                        'Collection Time': datetime.now().isoformat()
                    }
                    
                    # SYSTEM INFORMATION (Maximum Detail)
                    try:
                        for cs in conn.Win32_ComputerSystem():
                            data.update({
                                'Hostname': cs.Name,
                                'Computer Name': cs.Name,
                                'Domain': cs.Domain,
                                'Workgroup': cs.Workgroup,
                                'System Manufacturer': cs.Manufacturer,
                                'System Model': cs.Model,
                                'System Type': cs.SystemType,
                                'System Family': cs.SystemFamily,
                                'Total Physical Memory': cs.TotalPhysicalMemory,
                                'Current User': cs.UserName,  # Current logged user
                                'Primary Owner': cs.PrimaryOwnerName,
                                'Domain Role': cs.DomainRole,
                                'Part Of Domain': cs.PartOfDomain,
                                'Network Server Mode': cs.NetworkServerModeEnabled,
                                'Boot ROM Supported': cs.BootROMSupported,
                                'Boot Up State': cs.BootupState,
                                'Chassis Boot Up State': cs.ChassisBootupState,
                                'Thermal State': cs.ThermalState,
                                'Power State': cs.PowerState,
                                'Power Management Supported': cs.PowerManagementSupported,
                                'Reset Capability': cs.ResetCapability,
                                'Status': cs.Status,
                                'System Startup Delay': cs.SystemStartupDelay,
                                'System Startup Options': str(cs.SystemStartupOptions) if cs.SystemStartupOptions else None,
                                'System Startup Setting': cs.SystemStartupSetting,
                                'Wake Up Type': cs.WakeUpType
                            })
                    except Exception as e:
                        data['WMI_ComputerSystem_Error'] = str(e)
                    
                    # OPERATING SYSTEM (Complete Details)
                    try:
                        for os in conn.Win32_OperatingSystem():
                            data.update({
                                'Operating System': os.Name.split('|')[0] if '|' in os.Name else os.Name,
                                'OS Version': os.Version,
                                'OS Build Number': os.BuildNumber,
                                'OS Service Pack': os.ServicePackMajorVersion,
                                'OS Architecture': os.OSArchitecture,
                                'OS Language': os.OSLanguage,
                                'OS Install Date': os.InstallDate,
                                'Last Boot Time': os.LastBootUpTime,
                                'System Uptime': os.LocalDateTime,
                                'Windows Directory': os.WindowsDirectory,
                                'System Directory': os.SystemDirectory,
                                'Boot Device': os.BootDevice,
                                'System Device': os.SystemDevice,
                                'System Drive': os.SystemDrive,
                                'Country Code': os.CountryCode,
                                'Code Set': os.CodeSet,
                                'Locale': os.Locale,
                                'Time Zone': os.CurrentTimeZone,
                                'Daylight In Effect': os.DaylightInEffect,
                                'Free Physical Memory': os.FreePhysicalMemory,
                                'Free Virtual Memory': os.FreeVirtualMemory,
                                'Available Memory': os.AvailableVirtualMemory,
                                'Total Virtual Memory Size': os.TotalVirtualMemorySize,
                                'Total Visible Memory Size': os.TotalVisibleMemorySize,
                                'Free Space In Paging Files': os.FreeSpaceInPagingFiles,
                                'Size Stored In Paging Files': os.SizeStoredInPagingFiles,
                                'Number Of Licensed Users': os.NumberOfLicensedUsers,
                                'Number Of Processes': os.NumberOfProcesses,
                                'Number Of Users': os.NumberOfUsers,
                                'Max Number Of Processes': os.MaxNumberOfProcesses,
                                'Max Process Memory Size': os.MaxProcessMemorySize,
                                'Distributed': os.Distributed,
                                'Debug': os.Debug,
                                'Portable': os.Portable,
                                'Primary': os.Primary,
                                'Product Type': os.ProductType,
                                'Suite Mask': os.SuiteMask,
                                'OS Type': os.OSType,
                                'OS Product Suite': os.OSProductSuite,
                                'Plus Product ID': os.PlusProductID,
                                'Plus Version Number': os.PlusVersionNumber,
                                'Registered User': os.RegisteredUser,
                                'Serial Number': os.SerialNumber,
                                'Version': os.Version,
                                'Manufacturer': os.Manufacturer,
                                'Organization': os.Organization
                            })
                    except Exception as e:
                        data['WMI_OperatingSystem_Error'] = str(e)
                    
                    # PROCESSOR INFORMATION (Complete Details)
                    try:
                        processors = []
                        for cpu in conn.Win32_Processor():
                            cpu_info = {
                                'Name': cpu.Name,
                                'Manufacturer': cpu.Manufacturer,
                                'Architecture': cpu.Architecture,
                                'Family': cpu.Family,
                                'Model': cpu.Model,
                                'Stepping': cpu.Stepping,
                                'Max Clock Speed': cpu.MaxClockSpeed,
                                'Current Clock Speed': cpu.CurrentClockSpeed,
                                'External Clock': cpu.ExtClock,
                                'Number Of Cores': cpu.NumberOfCores,
                                'Number Of Logical Processors': cpu.NumberOfLogicalProcessors,
                                'Thread Count': cpu.ThreadCount,
                                'L2 Cache Size': cpu.L2CacheSize,
                                'L3 Cache Size': cpu.L3CacheSize,
                                'Data Width': cpu.DataWidth,
                                'Address Width': cpu.AddressWidth,
                                'Voltage': cpu.CurrentVoltage,
                                'Power Management Supported': cpu.PowerManagementSupported,
                                'Status': cpu.Status,
                                'CPU Status': cpu.CpuStatus,
                                'Load Percentage': cpu.LoadPercentage,
                                'Device ID': cpu.DeviceID,
                                'Socket Designation': cpu.SocketDesignation,
                                'Processor Type': cpu.ProcessorType,
                                'Processor ID': cpu.ProcessorId,
                                'Revision': cpu.Revision,
                                'Role': cpu.Role,
                                'Level': cpu.Level,
                                'Characteristics': cpu.Characteristics
                            }
                            processors.append(cpu_info)
                        
                        if processors:
                            # Set primary processor info
                            primary_cpu = processors[0]
                            data.update({
                                'Processor Name': primary_cpu['Name'],
                                'Processor Manufacturer': primary_cpu['Manufacturer'],
                                'Processor Architecture': primary_cpu['Architecture'],
                                'Processor Cores': primary_cpu['Number Of Cores'],
                                'Processor Logical Processors': primary_cpu['Number Of Logical Processors'],
                                'Processor Speed': primary_cpu['Max Clock Speed'],
                                'Processor L2 Cache': primary_cpu['L2 Cache Size'],
                                'Processor L3 Cache': primary_cpu['L3 Cache Size'],
                                'Processor Socket': primary_cpu['Socket Designation']
                            })
                            # Store all processors
                            data['All Processors'] = processors
                    except Exception as e:
                        data['WMI_Processor_Error'] = str(e)
                    
                    # MEMORY INFORMATION (Detailed)
                    try:
                        memory_modules = []
                        total_memory = 0
                        for mem in conn.Win32_PhysicalMemory():
                            mem_info = {
                                'Capacity': mem.Capacity,
                                'Bank Label': mem.BankLabel,
                                'Device Locator': mem.DeviceLocator,
                                'Memory Type': mem.MemoryType,
                                'Type Detail': mem.TypeDetail,
                                'Speed': mem.Speed,
                                'Manufacturer': mem.Manufacturer,
                                'Part Number': mem.PartNumber,
                                'Serial Number': mem.SerialNumber,
                                'Data Width': mem.DataWidth,
                                'Total Width': mem.TotalWidth,
                                'Form Factor': mem.FormFactor,
                                'Hot Swappable': mem.HotSwappable,
                                'Removable': mem.Removable,
                                'Replaceable': mem.Replaceable,
                                'Status': mem.Status
                            }
                            if mem.Capacity:
                                total_memory += int(mem.Capacity)
                            memory_modules.append(mem_info)
                        
                        data.update({
                            'Memory Modules': memory_modules,
                            'Total Memory Installed': total_memory,
                            'Memory Module Count': len(memory_modules)
                        })
                        
                        if memory_modules:
                            primary_mem = memory_modules[0]
                            data.update({
                                'Memory Speed': primary_mem['Speed'],
                                'Memory Type': primary_mem['Memory Type'],
                                'Memory Manufacturer': primary_mem['Manufacturer']
                            })
                    except Exception as e:
                        data['WMI_Memory_Error'] = str(e)
                    
                    # STORAGE INFORMATION (Complete Details)
                    try:
                        storage_devices = []
                        total_storage = 0
                        for disk in conn.Win32_DiskDrive():
                            disk_info = {
                                'Model': disk.Model,
                                'Size': disk.Size,
                                'Interface Type': disk.InterfaceType,
                                'Media Type': disk.MediaType,
                                'Serial Number': disk.SerialNumber,
                                'Firmware Revision': disk.FirmwareRevision,
                                'Manufacturer': disk.Manufacturer,
                                'Partitions': disk.Partitions,
                                'Signature': disk.Signature,
                                'Status': disk.Status,
                                'Capabilities': disk.Capabilities,
                                'Capability Descriptions': disk.CapabilityDescriptions,
                                'Compression Method': disk.CompressionMethod,
                                'Device ID': disk.DeviceID,
                                'Index': disk.Index,
                                'SCSI Bus': disk.SCSIBus,
                                'SCSI Logical Unit': disk.SCSILogicalUnit,
                                'SCSI Port': disk.SCSIPort,
                                'SCSI Target ID': disk.SCSITargetId,
                                'Sectors Per Track': disk.SectorsPerTrack,
                                'Tracks Per Cylinder': disk.TracksPerCylinder,
                                'Total Cylinders': disk.TotalCylinders,
                                'Total Heads': disk.TotalHeads,
                                'Total Sectors': disk.TotalSectors,
                                'Total Tracks': disk.TotalTracks,
                                'Bytes Per Sector': disk.BytesPerSector
                            }
                            if disk.Size:
                                total_storage += int(disk.Size)
                            storage_devices.append(disk_info)
                        
                        # Get disk partitions and logical disks
                        partitions = []
                        for partition in conn.Win32_DiskPartition():
                            part_info = {
                                'Device ID': partition.DeviceID,
                                'Size': partition.Size,
                                'Start Offset': partition.StartingOffset,
                                'Type': partition.Type,
                                'Bootable': partition.Bootable,
                                'Boot Partition': partition.BootPartition,
                                'Primary Partition': partition.PrimaryPartition,
                                'Description': partition.Description,
                                'Purpose': partition.Purpose,
                                'Status': partition.Status
                            }
                            partitions.append(part_info)
                        
                        logical_disks = []
                        for ldisk in conn.Win32_LogicalDisk():
                            ldisk_info = {
                                'Device ID': ldisk.DeviceID,
                                'Size': ldisk.Size,
                                'Free Space': ldisk.FreeSpace,
                                'File System': ldisk.FileSystem,
                                'Volume Name': ldisk.VolumeName,
                                'Volume Serial Number': ldisk.VolumeSerialNumber,
                                'Drive Type': ldisk.DriveType,
                                'Description': ldisk.Description,
                                'Provider Name': ldisk.ProviderName,
                                'Compressed': ldisk.Compressed,
                                'Supports Disk Quotas': ldisk.SupportsDiskQuotas,
                                'Supports File Based Compression': ldisk.SupportsFileBasedCompression,
                                'Status': ldisk.Status
                            }
                            logical_disks.append(ldisk_info)
                        
                        data.update({
                            'Storage Devices': storage_devices,
                            'Disk Partitions': partitions,
                            'Logical Disks': logical_disks,
                            'Total Storage': total_storage,
                            'Storage Device Count': len(storage_devices)
                        })
                        
                        # Summary storage info
                        if storage_devices:
                            storage_summary = []
                            for i, disk in enumerate(storage_devices, 1):
                                size_gb = int(disk['Size']) // (1024**3) if disk['Size'] else 0
                                storage_summary.append(f"Disk {i} = {size_gb} GB ({disk['Model']})")
                            data['Storage Summary'] = ', '.join(storage_summary)
                    except Exception as e:
                        data['WMI_Storage_Error'] = str(e)
                    
                    # NETWORK INFORMATION (Complete Details)
                    try:
                        network_adapters = []
                        for adapter in conn.Win32_NetworkAdapter():
                            if adapter.PhysicalAdapter:
                                adapter_info = {
                                    'Name': adapter.Name,
                                    'Description': adapter.Description,
                                    'MAC Address': adapter.MACAddress,
                                    'Adapter Type': adapter.AdapterType,
                                    'Manufacturer': adapter.Manufacturer,
                                    'Product Name': adapter.ProductName,
                                    'Speed': adapter.Speed,
                                    'Max Speed': adapter.MaxSpeed,
                                    'Network Addresses': adapter.NetworkAddresses,
                                    'Permanent Address': adapter.PermanentAddress,
                                    'Physical Adapter': adapter.PhysicalAdapter,
                                    'Status': adapter.NetConnectionStatus,
                                    'Connection ID': adapter.NetConnectionID,
                                    'Device ID': adapter.DeviceID,
                                    'GUID': adapter.GUID,
                                    'Index': adapter.Index,
                                    'Interface Index': adapter.InterfaceIndex,
                                    'Service Name': adapter.ServiceName,
                                    'System Name': adapter.SystemName,
                                    'Time Of Last Reset': adapter.TimeOfLastReset
                                }
                                network_adapters.append(adapter_info)
                        
                        # Network configuration
                        network_configs = []
                        for config in conn.Win32_NetworkAdapterConfiguration():
                            if config.IPEnabled:
                                config_info = {
                                    'Description': config.Description,
                                    'IP Address': config.IPAddress,
                                    'Subnet Mask': config.IPSubnet,
                                    'Default Gateway': config.DefaultIPGateway,
                                    'DNS Domain': config.DNSDomain,
                                    'DNS Server': config.DNSServerSearchOrder,
                                    'DHCP Enabled': config.DHCPEnabled,
                                    'DHCP Server': config.DHCPServer,
                                    'WINS Primary Server': config.WINSPrimaryServer,
                                    'WINS Secondary Server': config.WINSSecondaryServer,
                                    'Database Path': config.DatabasePath,
                                    'Domain DNS Registration Enabled': config.DomainDNSRegistrationEnabled,
                                    'Full DNS Registration Enabled': config.FullDNSRegistrationEnabled,
                                    'DHCP Lease Expires': config.DHCPLeaseExpires,
                                    'DHCP Lease Obtained': config.DHCPLeaseObtained,
                                    'Index': config.Index,
                                    'Interface Index': config.InterfaceIndex,
                                    'IP Connection Metric': config.IPConnectionMetric,
                                    'IP Enabled': config.IPEnabled,
                                    'IP Filter Security Enabled': config.IPFilterSecurityEnabled,
                                    'IP Port Security Enabled': config.IPPortSecurityEnabled,
                                    'IP Security Permitted IP Protocols': config.IPSecPermittedIPProtocols,
                                    'IP Security Permitted TCP Ports': config.IPSecPermittedTCPPorts,
                                    'IP Security Permitted UDP Ports': config.IPSecPermittedUDPPorts,
                                    'IP Use Zero Broadcast': config.IPUseZeroBroadcast,
                                    'IPX Address': config.IPXAddress,
                                    'IPX Enabled': config.IPXEnabled,
                                    'IPX Frame Type': config.IPXFrameType,
                                    'IPX Media Type': config.IPXMediaType,
                                    'IPX Network Number': config.IPXNetworkNumber,
                                    'IPX Virtual Net Number': config.IPXVirtualNetNumber,
                                    'Keep Alive Interval': config.KeepAliveInterval,
                                    'Keep Alive Time': config.KeepAliveTime,
                                    'MAC Address': config.MACAddress,
                                    'MTU': config.MTU,
                                    'Num Forward Packets': config.NumForwardPackets,
                                    'PMTU BH Detect Enabled': config.PMTUBHDetectEnabled,
                                    'PMTU Discovery Enabled': config.PMTUDiscoveryEnabled,
                                    'Service Name': config.ServiceName,
                                    'Setting ID': config.SettingID,
                                    'TCPIP NetBIOS Options': config.TcpipNetbiosOptions,
                                    'TCP Max Connect Retransmissions': config.TcpMaxConnectRetransmissions,
                                    'TCP Max Data Retransmissions': config.TcpMaxDataRetransmissions,
                                    'TCP Num Connections': config.TcpNumConnections,
                                    'TCP Use RFC1122 Urgent Pointer': config.TcpUseRFC1122UrgentPointer,
                                    'TCP Window Size': config.TcpWindowSize,
                                    'WINs Enable LMHosts Lookup': config.WINSEnableLMHostsLookup,
                                    'WINs Host Lookup File': config.WINSHostLookupFile,
                                    'WINs Scope ID': config.WINSScopeID
                                }
                                network_configs.append(config_info)
                        
                        data.update({
                            'Network Adapters': network_adapters,
                            'Network Configurations': network_configs,
                            'Network Adapter Count': len(network_adapters)
                        })
                        
                        # Summary network info
                        if network_adapters:
                            primary_adapter = network_adapters[0]
                            data.update({
                                'Primary Network Adapter': primary_adapter['Name'],
                                'Primary MAC Address': primary_adapter['MAC Address'],
                                'Primary Network Speed': primary_adapter['Speed']
                            })
                        
                        if network_configs:
                            primary_config = network_configs[0]
                            data.update({
                                'Primary IP Address': str(primary_config['IP Address']),
                                'Primary Subnet Mask': str(primary_config['Subnet Mask']),
                                'Primary Default Gateway': str(primary_config['Default Gateway']),
                                'Primary DNS Servers': str(primary_config['DNS Server'])
                            })
                    except Exception as e:
                        data['WMI_Network_Error'] = str(e)
                    
                    # GRAPHICS/VIDEO INFORMATION (Complete Details)
                    try:
                        video_controllers = []
                        for video in conn.Win32_VideoController():
                            video_info = {
                                'Name': video.Name,
                                'Description': video.Description,
                                'Video Processor': video.VideoProcessor,
                                'Adapter RAM': video.AdapterRAM,
                                'Adapter DAC Type': video.AdapterDACType,
                                'Video Mode Description': video.VideoModeDescription,
                                'Current Refresh Rate': video.CurrentRefreshRate,
                                'Current Horizontal Resolution': video.CurrentHorizontalResolution,
                                'Current Vertical Resolution': video.CurrentVerticalResolution,
                                'Current Bits Per Pixel': video.CurrentBitsPerPixel,
                                'Current Number Of Colors': video.CurrentNumberOfColors,
                                'Current Scan Mode': video.CurrentScanMode,
                                'Driver Date': video.DriverDate,
                                'Driver Version': video.DriverVersion,
                                'INF Filename': video.InfFilename,
                                'INF Section': video.InfSection,
                                'Installed Display Drivers': video.InstalledDisplayDrivers,
                                'Max Memory Supported': video.MaxMemorySupported,
                                'Max Number Controlled': video.MaxNumberControlled,
                                'Max Refresh Rate': video.MaxRefreshRate,
                                'Min Refresh Rate': video.MinRefreshRate,
                                'Monochrome': video.Monochrome,
                                'Number Of Video Pages': video.NumberOfVideoPages,
                                'PNP Device ID': video.PNPDeviceID,
                                'Status': video.Status,
                                'System Name': video.SystemName,
                                'Video Architecture': video.VideoArchitecture,
                                'Video Memory Type': video.VideoMemoryType
                            }
                            video_controllers.append(video_info)
                        
                        data.update({
                            'Video Controllers': video_controllers,
                            'Video Controller Count': len(video_controllers)
                        })
                        
                        # Summary graphics info
                        if video_controllers:
                            primary_video = video_controllers[0]
                            data.update({
                                'Primary Graphics Card': primary_video['Name'],
                                'Graphics Memory': primary_video['Adapter RAM'],
                                'Graphics Driver Version': primary_video['Driver Version'],
                                'Current Resolution': f"{primary_video['Current Horizontal Resolution']}x{primary_video['Current Vertical Resolution']}" if primary_video['Current Horizontal Resolution'] else None,
                                'Current Refresh Rate': primary_video['Current Refresh Rate']
                            })
                            
                            # Create graphics summary
                            graphics_summary = []
                            for i, video in enumerate(video_controllers, 1):
                                ram_mb = int(video['Adapter RAM']) // (1024*1024) if video['Adapter RAM'] else 0
                                graphics_summary.append(f"GPU {i} = {video['Name']} ({ram_mb} MB)")
                            data['Graphics Summary'] = ', '.join(graphics_summary)
                    except Exception as e:
                        data['WMI_Graphics_Error'] = str(e)
                    
                    # BIOS INFORMATION (Complete Details)
                    try:
                        for bios in conn.Win32_BIOS():
                            data.update({
                                'BIOS Version': bios.Version,
                                'BIOS Manufacturer': bios.Manufacturer,
                                'BIOS Serial Number': bios.SerialNumber,
                                'BIOS Release Date': bios.ReleaseDate,
                                'BIOS Name': bios.Name,
                                'BIOS Description': bios.Description,
                                'BIOS Status': bios.Status,
                                'BIOS Characteristics': bios.BiosCharacteristics,
                                'BIOS Major Version': bios.BIOSVersion,
                                'BIOS Language Edition': bios.LanguageEdition,
                                'Current Language': bios.CurrentLanguage,
                                'Installable Languages': bios.InstallableLanguages,
                                'SMBIOS BIOS Version': bios.SMBIOSBIOSVersion,
                                'SMBIOS Major Version': bios.SMBIOSMajorVersion,
                                'SMBIOS Minor Version': bios.SMBIOSMinorVersion,
                                'SMBIOS Present': bios.SMBIOSPresent,
                                'Build Number': bios.BuildNumber,
                                'Code Set': bios.CodeSet,
                                'Identification Code': bios.IdentificationCode,
                                'Install Date': bios.InstallDate,
                                'Primary BIOS': bios.PrimaryBIOS,
                                'Software Element ID': bios.SoftwareElementID,
                                'Software Element State': bios.SoftwareElementState,
                                'Target Operating System': bios.TargetOperatingSystem
                            })
                    except Exception as e:
                        data['WMI_BIOS_Error'] = str(e)
                    
                    # USER INFORMATION (Complete Details)
                    try:
                        user_accounts = []
                        for user in conn.Win32_UserAccount():
                            if not user.Domain or user.Domain == data.get('Computer Name', ''):
                                user_info = {
                                    'Name': user.Name,
                                    'Full Name': user.FullName,
                                    'Description': user.Description,
                                    'Domain': user.Domain,
                                    'Disabled': user.Disabled,
                                    'Lockout': user.Lockout,
                                    'Password Changeable': user.PasswordChangeable,
                                    'Password Expires': user.PasswordExpires,
                                    'Password Required': user.PasswordRequired,
                                    'Account Type': user.AccountType,
                                    'Caption': user.Caption,
                                    'Install Date': user.InstallDate,
                                    'Local Account': user.LocalAccount,
                                    'SID': user.SID,
                                    'SID Type': user.SIDType,
                                    'Status': user.Status
                                }
                                user_accounts.append(user_info)
                        
                        # Logged on users
                        logged_users = []
                        for logon in conn.Win32_LoggedOnUser():
                            logged_users.append({
                                'Antecedent': logon.Antecedent,
                                'Dependent': logon.Dependent
                            })
                        
                        # User profiles
                        user_profiles = []
                        for profile in conn.Win32_UserProfile():
                            profile_info = {
                                'Local Path': profile.LocalPath,
                                'SID': profile.SID,
                                'Special': profile.Special,
                                'Loaded': profile.Loaded,
                                'Last Use Time': profile.LastUseTime,
                                'Status': profile.Status
                            }
                            user_profiles.append(profile_info)
                        
                        data.update({
                            'User Accounts': user_accounts,
                            'Logged On Users': logged_users,
                            'User Profiles': user_profiles,
                            'User Account Count': len(user_accounts)
                        })
                    except Exception as e:
                        data['WMI_User_Error'] = str(e)
                    
                    # SYSTEM PERFORMANCE (Real-time Data)
                    try:
                        for perf in conn.Win32_PerfRawData_PerfOS_System():
                            data.update({
                                'System Up Time': perf.SystemUpTime,
                                'System Calls Per Sec': perf.SystemCallsPerSec,
                                'Context Switches Per Sec': perf.ContextSwitchesPerSec,
                                'Processes': perf.Processes,
                                'Threads': perf.Threads,
                                'File Read Operations Per Sec': perf.FileReadOperationsPerSec,
                                'File Write Operations Per Sec': perf.FileWriteOperationsPerSec,
                                'File Control Operations Per Sec': perf.FileControlOperationsPerSec,
                                'File Read Bytes Per Sec': perf.FileReadBytesPerSec,
                                'File Write Bytes Per Sec': perf.FileWriteBytesPerSec,
                                'File Control Bytes Per Sec': perf.FileControlBytesPerSec,
                                'Available Bytes': perf.AvailableBytes,
                                'Committed Bytes': perf.CommittedBytes,
                                'Pool Paged Bytes': perf.PoolPagedBytes,
                                'Pool Nonpaged Bytes': perf.PoolNonpagedBytes,
                                'System Cache Resident Bytes': perf.SystemCacheResidentBytes,
                                'System Code Total Bytes': perf.SystemCodeTotalBytes,
                                'System Code Resident Bytes': perf.SystemCodeResidentBytes,
                                'System Driver Total Bytes': perf.SystemDriverTotalBytes,
                                'System Driver Resident Bytes': perf.SystemDriverResidentBytes,
                                'Processor Queue Length': perf.ProcessorQueueLength
                            })
                    except Exception as e:
                        data['WMI_Performance_Error'] = str(e)
                    
                    # INSTALLED SOFTWARE (Complete List)
                    try:
                        installed_software = []
                        for software in conn.Win32_Product():
                            software_info = {
                                'Name': software.Name,
                                'Version': software.Version,
                                'Vendor': software.Vendor,
                                'Install Date': software.InstallDate,
                                'Install Location': software.InstallLocation,
                                'Install Source': software.InstallSource,
                                'Install State': software.InstallState,
                                'Package Cache': software.PackageCache,
                                'Package Code': software.PackageCode,
                                'Package Name': software.PackageName,
                                'Product ID': software.ProductID,
                                'Reg Company': software.RegCompany,
                                'Reg Owner': software.RegOwner,
                                'SKU Number': software.SKUNumber,
                                'Transforms': software.Transforms,
                                'URL Info About': software.URLInfoAbout,
                                'URL Update Info': software.URLUpdateInfo,
                                'Word Count': software.WordCount
                            }
                            installed_software.append(software_info)
                        
                        data.update({
                            'Installed Software': installed_software,
                            'Installed Software Count': len(installed_software)
                        })
                    except Exception as e:
                        data['WMI_Software_Error'] = str(e)
                    
                    # SERVICES (Complete List)
                    try:
                        services = []
                        for service in conn.Win32_Service():
                            service_info = {
                                'Name': service.Name,
                                'Display Name': service.DisplayName,
                                'Description': service.Description,
                                'State': service.State,
                                'Status': service.Status,
                                'Start Mode': service.StartMode,
                                'Service Type': service.ServiceType,
                                'Path Name': service.PathName,
                                'Started': service.Started,
                                'Start Name': service.StartName,
                                'System Name': service.SystemName,
                                'Tag ID': service.TagId,
                                'Wait Hint': service.WaitHint,
                                'Accept Pause': service.AcceptPause,
                                'Accept Stop': service.AcceptStop,
                                'Can Pause And Continue': service.CanPauseAndContinue,
                                'Can Stop': service.CanStop,
                                'Check Point': service.CheckPoint,
                                'Desktop Interact': service.DesktopInteract,
                                'Error Control': service.ErrorControl,
                                'Exit Code': service.ExitCode,
                                'Install Date': service.InstallDate,
                                'Process Id': service.ProcessId,
                                'Service Specific Exit Code': service.ServiceSpecificExitCode
                            }
                            services.append(service_info)
                        
                        data.update({
                            'Services': services,
                            'Service Count': len(services),
                            'Running Services': [s for s in services if s['State'] == 'Running'],
                            'Stopped Services': [s for s in services if s['State'] == 'Stopped']
                        })
                    except Exception as e:
                        data['WMI_Services_Error'] = str(e)
                    
                    # SUCCESS - Return comprehensive data
                    return data
                    
                except Exception as e:
                    continue
            
            return None
            
        except Exception as e:
            return None

    def _comprehensive_ssh_collection(self, ip: str, username: str, password: str) -> Optional[Dict]:
        """Comprehensive SSH data collection for Linux/Unix systems"""
        if not PARAMIKO_AVAILABLE:
            return None
            
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, username=username, password=password, timeout=30)
            
            data = {
                'IP Address': ip,
                'Collection Method': 'Comprehensive SSH',
                'Collection Time': datetime.now().isoformat(),
                'SSH Username': username
            }
            
            # System Information commands
            commands = {
                'hostname': 'hostname',
                'uptime': 'uptime',
                'uname': 'uname -a',
                'os_release': 'cat /etc/os-release 2>/dev/null || cat /etc/redhat-release 2>/dev/null || cat /etc/issue',
                'kernel_version': 'uname -r',
                'architecture': 'uname -m',
                'cpu_info': 'cat /proc/cpuinfo',
                'memory_info': 'cat /proc/meminfo',
                'disk_info': 'df -h',
                'network_interfaces': 'ip addr show',
                'route_table': 'route -n',
                'listening_ports': 'netstat -tuln',
                'running_processes': 'ps aux | head -20',
                'installed_packages': 'dpkg -l 2>/dev/null || rpm -qa 2>/dev/null | head -50',
                'who': 'who',
                'load_average': 'cat /proc/loadavg',
                'hardware_info': 'lshw -short 2>/dev/null || dmidecode -s system-manufacturer 2>/dev/null'
            }
            
            for key, command in commands.items():
                try:
                    stdin, stdout, stderr = ssh.exec_command(command)
                    output = stdout.read().decode('utf-8', errors='ignore').strip()
                    if output:
                        data[key] = output[:2000]  # Limit output size
                except Exception as e:
                    data[f'{key}_error'] = str(e)
            
            # Parse and enhance the collected data
            if 'hostname' in data:
                data['Hostname'] = data['hostname']
            
            # Parse CPU information
            if 'cpu_info' in data:
                cpu_lines = data['cpu_info'].split('\n')
                cpu_count = 0
                cpu_model = ''
                for line in cpu_lines:
                    if 'processor' in line:
                        cpu_count += 1
                    elif 'model name' in line and not cpu_model:
                        cpu_model = line.split(':')[1].strip()
                
                data.update({
                    'CPU Count': cpu_count,
                    'CPU Model': cpu_model,
                    'Processor Name': cpu_model
                })
            
            # Parse memory information
            if 'memory_info' in data:
                mem_lines = data['memory_info'].split('\n')
                for line in mem_lines:
                    if 'MemTotal:' in line:
                        mem_kb = int(line.split()[1])
                        data['Total Memory KB'] = mem_kb
                        data['Total Memory GB'] = round(mem_kb / 1024 / 1024, 2)
                    elif 'MemFree:' in line:
                        free_kb = int(line.split()[1])
                        data['Free Memory KB'] = free_kb
            
            # Parse OS information
            if 'os_release' in data:
                data['Operating System'] = data['os_release'].split('\n')[0]
            
            ssh.close()
            return data
            
        except Exception as e:
            return None

    def _comprehensive_snmp_collection(self, ip: str, community: str) -> Optional[Dict]:
        """Comprehensive SNMP data collection"""
        if not PYSNMP_AVAILABLE:
            return None
            
        try:
            data = {
                'IP Address': ip,
                'Collection Method': 'Comprehensive SNMP',
                'Collection Time': datetime.now().isoformat(),
                'SNMP Community': community
            }
            
            # Standard SNMP OIDs for comprehensive data collection
            oids = {
                'system_description': '1.3.6.1.2.1.1.1.0',
                'system_name': '1.3.6.1.2.1.1.5.0',
                'system_location': '1.3.6.1.2.1.1.6.0',
                'system_uptime': '1.3.6.1.2.1.1.3.0',
                'if_number': '1.3.6.1.2.1.2.1.0'
            }
            
            for key, oid in oids.items():
                try:
                    for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(
                        SnmpEngine(),
                        CommunityData(community),
                        UdpTransportTarget((ip, 161)),
                        ContextData(),
                        ObjectType(ObjectIdentity(oid)),
                        lexicographicMode=False,
                        maxRows=1):
                        
                        if errorIndication or errorStatus:
                            break
                        
                        for varBind in varBinds:
                            value = str(varBind[1])
                            if value and value != 'No Such Object currently exists at this OID':
                                data[key] = value
                        break
                except Exception:
                    pass
            
            # Extract and format key information
            if 'system_name' in data:
                data['Hostname'] = data['system_name']
            
            if 'system_description' in data:
                data['Device Description'] = data['system_description']
                # Try to determine device type from description
                desc_lower = data['system_description'].lower()
                if any(x in desc_lower for x in ['switch', 'catalyst']):
                    data['Device Type'] = 'Switches'
                elif any(x in desc_lower for x in ['access point', 'wireless', 'ap']):
                    data['Device Type'] = 'Access Points'
                elif any(x in desc_lower for x in ['firewall', 'asa', 'fortigate']):
                    data['Device Type'] = 'Firewalls'
                elif any(x in desc_lower for x in ['printer', 'laserjet', 'inkjet']):
                    data['Device Type'] = 'Printers'
            
            return data if len(data) > 4 else None  # Return only if we got actual data
            
        except Exception as e:
            return None

    def _http_service_detection(self, ip: str) -> Optional[Dict]:
        """HTTP service detection for basic service identification"""
        try:
            data = {
                'IP Address': ip,
                'Collection Method': 'HTTP Service Detection',
                'Collection Time': datetime.now().isoformat()
            }
            
            # Try HTTP and HTTPS
            protocols = ['http', 'https']
            
            for protocol in protocols:
                try:
                    url = f"{protocol}://{ip}"
                    response = requests.get(url, timeout=10, verify=False)
                    
                    data[f'{protocol.upper()} Status Code'] = response.status_code
                    
                    # Try to identify service type from headers and content
                    content = response.text[:1000]  # First 1KB
                    headers = response.headers
                    
                    # Device type detection from HTTP response
                    if 'server' in headers:
                        server = headers['server'].lower()
                        if any(x in server for x in ['printer', 'cups']):
                            data['Device Type'] = 'Printers'
                    
                    # Check for common device web interfaces
                    if any(x in content.lower() for x in ['printer', 'canon', 'hp', 'epson']):
                        data['Device Type'] = 'Printers'
                    elif any(x in content.lower() for x in ['switch', 'cisco', 'netgear']):
                        data['Device Type'] = 'Switches'
                    elif any(x in content.lower() for x in ['access point', 'wireless', 'wifi']):
                        data['Device Type'] = 'Access Points'
                    elif any(x in content.lower() for x in ['firewall', 'security']):
                        data['Device Type'] = 'Firewalls'
                    
                    break  # Success on first working protocol
                    
                except Exception:
                    pass
            
            return data if 'Device Type' in data or any('Status Code' in k for k in data.keys()) else None
            
        except Exception as e:
            return None

    def _calculate_data_completeness(self, data: Dict, collection_type: str) -> float:
        """Calculate data completeness percentage"""
        if not data:
            return 0.0
        
        # Define expected fields for each collection type
        expected_fields = {
            'windows': [
                'Hostname', 'IP Address', 'Operating System', 'System Manufacturer',
                'System Model', 'Processor Name', 'Total Physical Memory', 'BIOS Serial Number',
                'Current User', 'Storage Summary', 'Graphics Summary', 'Primary Network Adapter'
            ],
            'linux': [
                'hostname', 'ip_address', 'operating_system', 'kernel_version',
                'cpu_info', 'memory_total', 'disk_info', 'network_interfaces'
            ],
            'network': [
                'hostname', 'ip_address', 'device_type', 'manufacturer',
                'model', 'interfaces', 'firmware_version'
            ],
            'snmp': [
                'hostname', 'ip_address', 'system_description', 'system_object_id',
                'system_uptime', 'interfaces_info'
            ],
            'basic': [
                'hostname', 'ip_address', 'device_type', 'status'
            ]
        }
        
        required_fields = expected_fields.get(collection_type, expected_fields['basic'])
        populated_fields = 0
        
        for field in required_fields:
            if field in data and data[field] is not None and str(data[field]).strip() != '':
                populated_fields += 1
        
        return (populated_fields / len(required_fields)) * 100.0