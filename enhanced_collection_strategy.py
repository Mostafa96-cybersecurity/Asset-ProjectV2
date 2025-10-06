#!/usr/bin/env python3
"""
Enhanced Collection Strategy with Proper Device Types & Maximum Data Collection
تحسين استراتيجية الجمع مع أنواع الأجهزة الصحيحة وجمع أقصى بيانات ممكنة
"""

import time
import threading
import ipaddress
from queue import Queue, Empty
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime
import logging
import nmap
import requests

from PyQt6.QtCore import QThread, pyqtSignal

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

# Import our smart duplicate validator
try:
    from smart_duplicate_validator import SmartDuplicateValidator
    DUPLICATE_VALIDATOR_AVAILABLE = True
except ImportError:
    DUPLICATE_VALIDATOR_AVAILABLE = False

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
        
        # Initialize smart duplicate prevention
        if DUPLICATE_VALIDATOR_AVAILABLE:
            self.log_message.emit("   🛡️ Smart Duplicate Prevention: ENABLED")
            self.log_message.emit("   🔍 Real-time validation: Serial + MAC + Hardware fingerprinting")
        else:
            self.log_message.emit("   ⚠️ Smart Duplicate Prevention: DISABLED (validator not available)")

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
            
            # Debug logging
            self.log_message.emit("📊 Detection Results:")
            for device in detected_devices:
                self.log_message.emit(f"   🔍 {device.ip}: {device.device_type} ({device.os_family}) - {len(device.open_ports)} ports")
            
            self.log_message.emit(f"✅ Device type detection completed on {len(detected_devices)} devices")
            self._update_progress(50)  # 50% complete after detection
            
            # STEP 3: Maximum Data Collection (Enhanced Strategy)
            self.log_message.emit("📊 STEP 3: Maximum Data Collection - Enhanced strategy...")
            self.log_message.emit(f"   🎯 Starting collection on {len(detected_devices)} detected devices")
            
            if len(detected_devices) == 0:
                self.log_message.emit("   ⚠️ No devices to collect from - detection phase may have failed")
                collection_results = []
            else:
                collection_results = self._step3_maximum_collection(detected_devices)
            
            self.collected_count = sum(1 for r in collection_results if r.success)
            
            self.log_message.emit(f"✅ Data collection completed on {self.collected_count} devices")
            if self.collected_count == 0 and len(detected_devices) > 0:
                self.log_message.emit("   ⚠️ Collection failed on all devices - check credentials and connectivity")
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

    def _secure_reliable_ping(self, ip: str) -> bool:
        """
        Secure and reliable ping implementation with multiple verification methods
        This ensures devices are truly alive and responding properly
        """
        try:
            
            # Method 1: System ICMP Ping (Most Reliable)
            icmp_success = self._icmp_ping_verification(ip)
            
            # Method 2: TCP Socket Test on common ports (Secondary verification)
            tcp_success = self._tcp_port_verification(ip)
            
            # Method 3: ARP table check for local network devices
            arp_success = self._arp_table_verification(ip) if self._is_local_network(ip) else False
            
            # Comprehensive decision logic
            if icmp_success:
                log.debug(f"{ip}: ICMP ping successful ✅")
                return True
            elif tcp_success:
                log.debug(f"{ip}: TCP port verification successful ✅")
                return True
            elif arp_success:
                log.debug(f"{ip}: ARP table verification successful ✅")
                return True
            else:
                log.debug(f"{ip}: All ping methods failed ❌")
                return False
                
        except Exception as e:
            log.debug(f"Secure ping error for {ip}: {e}")
            return False
    
    def _icmp_ping_verification(self, ip: str) -> bool:
        """ICMP ping with strict verification"""
        try:
            import platform
            import subprocess
            
            system = platform.system().lower()
            
            if system == 'windows':
                # Windows: More strict ping parameters
                cmd = ['ping', '-n', '2', '-w', '3000', '-l', '32', ip]
            else:
                # Linux/Unix: Strict ping with packet size
                cmd = ['ping', '-c', '2', '-W', '3', '-s', '32', ip]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                timeout=8,  # Longer timeout for reliability
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if system == 'windows' else 0
            )
            
            if result.returncode == 0:
                output = result.stdout.lower()
                
                if system == 'windows':
                    # Windows verification: Look for successful replies
                    success_indicators = ['reply from', 'bytes=32']
                    failure_indicators = ['request timed out', 'destination unreachable', 'general failure']
                    
                    has_success = any(indicator in output for indicator in success_indicators)
                    has_failure = any(indicator in output for indicator in failure_indicators)
                    
                    # Must have success indicators and no failure indicators
                    return has_success and not has_failure
                    
                else:
                    # Linux verification: Look for successful ping responses
                    success_indicators = ['bytes from', '64 bytes', 'icmp_seq=']
                    failure_indicators = ['unreachable', 'no route to host', '100% packet loss']
                    
                    has_success = any(indicator in output for indicator in success_indicators)
                    has_failure = any(indicator in output for indicator in failure_indicators)
                    
                    return has_success and not has_failure
            
            return False
            
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, Exception):
            return False
    
    def _tcp_port_verification(self, ip: str) -> bool:
        """TCP port verification on common service ports"""
        try:
            import socket
            
            # Common ports that indicate an alive device
            common_ports = [80, 443, 22, 23, 21, 25, 53, 135, 139, 445, 3389]
            
            for port in common_ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2.0)  # 2 second timeout per port
                    result = sock.connect_ex((ip, port))
                    sock.close()
                    
                    if result == 0:
                        log.debug(f"{ip}: TCP port {port} open")
                        return True
                        
                except Exception:
                    continue
            
            return False
            
        except Exception:
            return False
    
    def _arp_table_verification(self, ip: str) -> bool:
        """Check ARP table for device presence (local network only)"""
        try:
            import subprocess
            import platform
            
            system = platform.system().lower()
            
            if system == 'windows':
                cmd = ['arp', '-a']
            else:
                cmd = ['arp', '-a']
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                timeout=5,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if system == 'windows' else 0
            )
            
            if result.returncode == 0:
                # Check if IP appears in ARP table
                return ip in result.stdout
                
            return False
            
        except Exception:
            return False
    
    def _is_local_network(self, ip: str) -> bool:
        """Check if IP is in local network range"""
        try:
            import ipaddress
            
            ip_obj = ipaddress.IPv4Address(ip)
            
            # Common local network ranges
            local_networks = [
                ipaddress.IPv4Network('192.168.0.0/16'),
                ipaddress.IPv4Network('10.0.0.0/8'),
                ipaddress.IPv4Network('172.16.0.0/12'),
                ipaddress.IPv4Network('169.254.0.0/16'),  # Link-local
                ipaddress.IPv4Network('127.0.0.0/8'),     # Loopback
            ]
            
            return any(ip_obj in network for network in local_networks)
            
        except Exception:
            return False

    def _fast_ping(self, ip: str) -> bool:
        """
        Legacy method name - now calls secure reliable ping
        Maintained for backward compatibility
        """
        return self._secure_reliable_ping(ip)

    def _update_progress(self, progress: int):
        """Update progress bar if available"""
        try:
            if hasattr(self, 'progress_updated'):
                self.progress_updated.emit(progress)
        except Exception:
            pass  # Silently ignore if no progress signal available

    def _step1_ping_discovery(self, all_ips: List[str]) -> List[AliveDevice]:
        """Step 1: Secure ping discovery to find truly alive devices"""
        alive_devices = []
        completed = 0
        failed_ips = []
        
        def secure_ping_worker():
            nonlocal completed
            while True:
                try:
                    ip = ping_queue.get(timeout=1)
                    if self._stop_requested.is_set():
                        break
                    
                    # Secure ping check with detailed timing
                    start_time = time.time()
                    self.log_message.emit(f"🔍 Testing {ip}...")
                    
                    if self._secure_reliable_ping(ip):
                        ping_time = (time.time() - start_time) * 1000
                        device = AliveDevice(ip=ip, ping_time=ping_time)
                        alive_devices.append(device)
                        self.log_message.emit(f"✅ {ip} VERIFIED ALIVE ({ping_time:.1f}ms)")
                    else:
                        ping_time = (time.time() - start_time) * 1000
                        failed_ips.append(ip)
                        self.log_message.emit(f"❌ {ip} not responding ({ping_time:.1f}ms)")
                    
                    completed += 1
                    progress = int((completed / len(all_ips)) * 25)  # 0-25% of total
                    self._update_progress(progress)
                    
                    ping_queue.task_done()
                    
                except Empty:
                    break
                except Exception as e:
                    log.warning(f"Secure ping worker error: {e}")
                    completed += 1
                    ping_queue.task_done()
        
        # Log start of ping discovery
        self.log_message.emit(f"🔍 SECURE PING DISCOVERY: Testing {len(all_ips)} IP addresses...")
        self.log_message.emit("🛡️ Using multi-method verification (ICMP + TCP + ARP)")
        
        # Create ping queue
        ping_queue = Queue()
        for ip in all_ips:
            ping_queue.put(ip)
        
        # Start secure ping workers (fewer workers for more reliable results)
        max_workers = min(5, len(all_ips))  # Limit to 5 concurrent workers for reliability
        threads = []
        for _ in range(max_workers):
            thread = threading.Thread(target=secure_ping_worker, name=f"SecurePing-{_}")
            thread.start()
            threads.append(thread)
        
        # Wait for completion
        ping_queue.join()
        for thread in threads:
            thread.join(timeout=5)
        
        # Log summary
        self.log_message.emit("🏁 PING DISCOVERY COMPLETE:")
        self.log_message.emit(f"   ✅ Alive devices: {len(alive_devices)}")
        self.log_message.emit(f"   ❌ Unresponsive: {len(failed_ips)}")
        self.log_message.emit(f"   📊 Success rate: {(len(alive_devices)/len(all_ips)*100):.1f}%")
        
        if len(alive_devices) == 0:
            self.log_message.emit("⚠️ No devices found alive - verify network connectivity")
        
        return alive_devices
        for thread in threads:
            thread.join(timeout=3)
        
        return alive_devices

    def _step2_enhanced_detection(self, devices: List[AliveDevice]) -> List[AliveDevice]:
        """Step 2: Enhanced OS and device type detection using NMAP"""
        detected_devices = []
        completed = 0
        detection_lock = threading.Lock()  # Thread safety for detected_devices list
        
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
                        services_list = []
                        if isinstance(device.services, dict):
                            services_list = list(device.services.keys())
                        elif isinstance(device.services, list):
                            services_list = device.services
                        
                        device_info = {
                            'open_ports': device.open_ports,
                            'services': services_list,
                            'os_family': device.os_family,
                            'hostname': nmap_result.get('hostname', ''),
                            'ip': device.ip
                        }
                        device.device_type = self.classify_device(device_info)
                        device.confidence = nmap_result.get('confidence', 0)
                        
                        self.log_message.emit(f"🔍 {device.ip}: {device.device_type} ({device.os_family}) - {len(device.open_ports)} ports")
                    
                    # Thread-safe addition to detected_devices list
                    with detection_lock:
                        detected_devices.append(device)
                        completed += 1
                    
                    progress = 25 + int((completed / len(devices)) * 25)  # 25-50% of total
                    self._update_progress(progress)
                    
                    detection_queue.task_done()
                    
                except Empty:
                    break
                except Exception as e:
                    log.warning(f"Detection worker error: {e}")
                    # Still add the device even if detection failed
                    with detection_lock:
                        detected_devices.append(device)
                        completed += 1
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

    def _enhanced_fallback_scan(self, ip: str) -> Optional[Dict]:
        """Enhanced fallback scanning with DNS hostname validation"""
        try:
            result = {
                'ip': ip,
                'hostname': 'unknown',
                'dns_hostname': None,
                'dns_status': 'none',
                'os_family': 'unknown',
                'open_ports': [],
                'services': [],
                'scan_method': 'fallback'
            }
            
            # 1. DNS Hostname Collection and Validation
            try:
                import socket
                
                # Get DNS domain record for the IP
                try:
                    dns_hostname = socket.gethostbyaddr(ip)[0]
                    result['dns_hostname'] = dns_hostname
                    result['hostname'] = dns_hostname  # Use DNS name as primary hostname
                    self.log_message.emit(f"   � {ip}: DNS domain record → {dns_hostname}")
                    
                    # Since we're using DNS as primary source in fallback, mark as 'ok'
                    result['dns_status'] = 'ok'
                    self.log_message.emit(f"   ✅ {ip}: DNS hostname collected successfully")
                    
                except socket.herror:
                    # No DNS record found
                    result['dns_hostname'] = None
                    result['dns_status'] = 'none'
                    result['hostname'] = f'device-{ip.replace(".", "-")}'
                    self.log_message.emit(f"   ❌ {ip}: No DNS record in domain")
                    
                except Exception as e:
                    result['dns_hostname'] = None
                    result['dns_status'] = 'error'
                    result['hostname'] = f'device-{ip.replace(".", "-")}'
                    self.log_message.emit(f"   ⚠️ {ip}: DNS lookup error: {str(e)[:50]}")
                    
            except Exception:
                result['dns_hostname'] = None
                result['dns_status'] = 'error'
                result['hostname'] = f'device-{ip.replace(".", "-")}'
            
            # 2. Port scanning on common ports
            common_ports = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 993, 995, 3389, 5432, 3306, 1433, 161, 9100, 631]
            open_ports = []
            
            for port in common_ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1.0)
                    result_code = sock.connect_ex((ip, port))
                    sock.close()
                    
                    if result_code == 0:
                        open_ports.append(port)
                        self.log_message.emit(f"   🔌 {ip}: Port {port} open")
                except Exception:
                    continue
            
            result['open_ports'] = open_ports
            
            # 3. OS Detection based on open ports
            if 135 in open_ports or 139 in open_ports or 445 in open_ports:
                result['os_family'] = 'windows'
                self.log_message.emit(f"   🖥️ {ip}: Detected as Windows (SMB ports)")
            elif 22 in open_ports:
                result['os_family'] = 'linux'
                self.log_message.emit(f"   🐧 {ip}: Detected as Linux (SSH port)")
            elif 161 in open_ports:
                result['os_family'] = 'network_device'
                self.log_message.emit(f"   🌐 {ip}: Detected as Network Device (SNMP)")
            elif 9100 in open_ports or 631 in open_ports:
                result['os_family'] = 'printer'
                self.log_message.emit(f"   🖨️ {ip}: Detected as Printer")
            
            # 4. Service detection
            service_map = {
                21: 'ftp', 22: 'ssh', 23: 'telnet', 25: 'smtp', 53: 'dns',
                80: 'http', 110: 'pop3', 135: 'rpc', 139: 'netbios', 143: 'imap',
                443: 'https', 445: 'smb', 993: 'imaps', 995: 'pop3s',
                3389: 'rdp', 5432: 'postgresql', 3306: 'mysql', 1433: 'mssql',
                161: 'snmp', 9100: 'printer', 631: 'ipp'
            }
            
            services = [service_map.get(port, f'port-{port}') for port in open_ports]
            result['services'] = services
            
            if len(open_ports) > 0:
                self.log_message.emit(f"   ✅ {ip}: Fallback scan successful ({len(open_ports)} ports, {result['os_family']})")
                return result
            else:
                self.log_message.emit(f"   ⚠️ {ip}: No open ports found")
                return result
                
        except Exception as e:
            self.log_message.emit(f"   ❌ {ip}: Fallback scan failed: {e}")
            return None
    def _enhanced_nmap_scan(self, ip: str) -> Optional[Dict]:
        """NMAP scan optimized for OS detection only (not full port scanning)"""
        try:
            # Try to use nmap python library with proper error handling
            import nmap
            nm = nmap.PortScanner()
            
            self.log_message.emit(f"   🔍 {ip}: Running NMAP OS detection (optimized for speed)...")
            
            # Use minimal port scan with aggressive OS detection - focus on OS detection not port scanning
            try:
                # Fast OS detection scan - only scan essential ports for OS fingerprinting
                scan_result = nm.scan(ip, '22,80,135,139,443,445', '-O --osscan-guess --osscan-limit -T4')
            except Exception:
                try:
                    # Fallback without osscan-limit
                    scan_result = nm.scan(ip, '22,80,135,139,443,445', '-O --osscan-guess -T4')
                except Exception:
                    # Final fallback - minimal scan for basic OS detection
                    scan_result = nm.scan(ip, '80,443', '-O')
            
            if ip in scan_result['scan']:
                host_info = scan_result['scan'][ip]
                
                # Extract hostname from nmap results
                hostnames = host_info.get('hostnames', [])
                hostname = 'unknown'
                if hostnames:
                    for hn in hostnames:
                        if hn.get('name') and hn.get('name') != '':
                            hostname = hn.get('name')
                            break
                
                # Extract OS information with high confidence
                os_family = self._extract_os_family(host_info)
                
                # Get minimal port info (since we're focusing on OS detection)
                open_ports = []
                services = {}
                if 'tcp' in host_info:
                    for port, port_info in host_info['tcp'].items():
                        if port_info.get('state') == 'open':
                            open_ports.append(port)
                            service_name = port_info.get('name', f'port-{port}')
                            services[port] = service_name
                
                # Extract NMAP OS details for database
                nmap_os_details = self._extract_nmap_os_details(host_info)
                
                result = {
                    'ip': ip,
                    'hostname': hostname,
                    'os_family': os_family,
                    'open_ports': open_ports,
                    'services': services,
                    'scan_method': 'nmap_os_detection',
                    'confidence': 85,  # Higher confidence for OS-focused scan
                    'nmap_os_family': nmap_os_details.get('os_family'),
                    'nmap_device_type': nmap_os_details.get('device_type'),
                    'nmap_confidence': nmap_os_details.get('confidence'),
                    'os_fingerprint': nmap_os_details.get('fingerprint'),
                    'detection_method': 'NMAP OS Detection'
                }
                
                self.log_message.emit(f"   ✅ {ip}: NMAP OS detection - {os_family} (confidence: {nmap_os_details.get('confidence', 0)}%)")
                if hostname != 'unknown':
                    self.log_message.emit(f"   🏷️ {ip}: NMAP hostname: {hostname}")
                
                return result
                
        except ImportError:
            self.log_message.emit(f"   ⚠️ {ip}: python-nmap library not available")
        except Exception as e:
            error_msg = str(e)
            if 'not found in path' in error_msg.lower():
                self.log_message.emit(f"   ⚠️ {ip}: NMAP not installed or not in PATH")
            else:
                self.log_message.emit(f"   ⚠️ {ip}: NMAP error: {error_msg[:50]}...")
        
        # Fallback to enhanced port scanning
        return self._enhanced_fallback_scan(ip)

    def _extract_os_family(self, host_info: Dict) -> str:
        """Extract OS family from NMAP scan results"""
        try:
            # Check if OS detection results are available
            if 'osmatch' in host_info and host_info['osmatch']:
                # Get the best OS match
                best_match = host_info['osmatch'][0]
                os_name = best_match.get('name', '').lower()
                
                # Classify based on OS name
                if any(word in os_name for word in ['windows', 'microsoft']):
                    return 'windows'
                elif any(word in os_name for word in ['linux', 'ubuntu', 'debian', 'centos', 'redhat', 'fedora']):
                    return 'linux'
                elif any(word in os_name for word in ['unix', 'solaris', 'aix', 'hp-ux']):
                    return 'unix'
                elif any(word in os_name for word in ['mac', 'darwin', 'osx']):
                    return 'macos'
                elif any(word in os_name for word in ['freebsd', 'openbsd', 'netbsd']):
                    return 'bsd'
                elif any(word in os_name for word in ['cisco', 'juniper', 'router', 'switch']):
                    return 'network_device'
                else:
                    return 'unknown'
            
            # Fallback: Try to determine OS from open ports and services
            open_ports = list(host_info.get('tcp', {}).keys())
            
            # Windows indicators
            if any(port in open_ports for port in [135, 139, 445, 3389]):
                return 'windows'
            
            # Linux/Unix indicators
            if 22 in open_ports and not any(port in open_ports for port in [135, 139, 445]):
                return 'linux'
            
            # Network device indicators
            if 161 in open_ports or (22 in open_ports and 80 in open_ports):
                return 'network_device'
            
            return 'unknown'
            
        except Exception as e:
            self.log_message.emit(f"   ⚠️ OS extraction error: {str(e)[:50]}")
            return 'unknown'

    def _extract_nmap_os_details(self, host_info: Dict) -> Dict:
        """Extract detailed OS information from NMAP scan for database storage"""
        os_details = {
            'os_family': 'unknown',
            'device_type': 'unknown', 
            'confidence': 0,
            'fingerprint': 'unknown'
        }
        
        try:
            # Extract OS matches with confidence scores
            if 'osmatch' in host_info:
                for match in host_info['osmatch']:
                    accuracy = int(match.get('accuracy', 0))
                    if accuracy > os_details['confidence']:
                        os_details['confidence'] = accuracy
                        os_name = match.get('name', '').lower()
                        
                        # Determine OS family
                        if any(term in os_name for term in ['windows', 'microsoft']):
                            os_details['os_family'] = 'windows'
                        elif any(term in os_name for term in ['linux', 'ubuntu', 'centos', 'redhat', 'debian']):
                            os_details['os_family'] = 'linux'
                        elif any(term in os_name for term in ['macos', 'mac os', 'darwin']):
                            os_details['os_family'] = 'macos'
                        elif any(term in os_name for term in ['freebsd', 'openbsd', 'netbsd']):
                            os_details['os_family'] = 'bsd'
                        elif any(term in os_name for term in ['solaris', 'sunos']):
                            os_details['os_family'] = 'solaris'
                        elif any(term in os_name for term in ['cisco', 'juniper', 'pfsense']):
                            os_details['os_family'] = 'network_os'
                        
                        # Determine device type
                        if any(term in os_name for term in ['server', 'datacenter']):
                            os_details['device_type'] = 'server'
                        elif any(term in os_name for term in ['router', 'switch', 'firewall']):
                            os_details['device_type'] = 'network_device'
                        elif any(term in os_name for term in ['printer']):
                            os_details['device_type'] = 'printer'
                        elif any(term in os_name for term in ['workstation', 'desktop', 'laptop']):
                            os_details['device_type'] = 'workstation'
                        
                        os_details['fingerprint'] = match.get('name', 'unknown')
                        break
                        
            # Fallback to port-based detection
            if os_details['os_family'] == 'unknown':
                os_details.update(self._port_based_os_detection(host_info))
                
        except Exception as e:
            self.log_message.emit(f"   ⚠️ OS detail extraction error: {str(e)[:50]}")
            
        return os_details

    def _port_based_os_detection(self, host_info: Dict) -> Dict:
        """Fallback OS detection based on open ports"""
        os_info = {'os_family': 'unknown', 'device_type': 'unknown', 'confidence': 30}
        
        try:
            open_ports = []
            if 'tcp' in host_info:
                open_ports = [port for port, info in host_info['tcp'].items() 
                             if info.get('state') == 'open']
            
            # Windows detection
            if any(port in open_ports for port in [135, 139, 445]):
                os_info['os_family'] = 'windows'
                os_info['confidence'] = 60
                
                if 3389 in open_ports:  # RDP
                    os_info['device_type'] = 'server'
                else:
                    os_info['device_type'] = 'workstation'
                    
            # Linux detection  
            elif 22 in open_ports:  # SSH
                os_info['os_family'] = 'linux'
                os_info['confidence'] = 50
                
                if any(port in open_ports for port in [80, 443, 25, 53]):
                    os_info['device_type'] = 'server'
                else:
                    os_info['device_type'] = 'workstation'
                    
            # Network device detection
            elif 161 in open_ports:  # SNMP
                os_info['os_family'] = 'network_os'
                os_info['device_type'] = 'network_device'
                os_info['confidence'] = 70
                
            # Printer detection
            elif any(port in open_ports for port in [9100, 631]):
                os_info['os_family'] = 'embedded'
                os_info['device_type'] = 'printer'
                os_info['confidence'] = 80
                
        except Exception:
            pass
            
        return os_info

    def _enhanced_nmap_scan_original(self, ip: str) -> Optional[Dict]:
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
        
        self.log_message.emit(f"   🎯 Starting collection on {device.ip} ({device.device_type})")
        
        # Collection strategy based on device type
        if device.device_type in ['Workstations', 'Laptops', 'Windows Servers']:
            # Windows devices: WMI first, then SNMP if fails
            self.log_message.emit(f"   🖥️ {device.ip}: Trying Windows WMI collection...")
            result = self._windows_maximum_collection(device)
            if not result.success:
                self.log_message.emit(f"   📡 {device.ip}: WMI failed, trying SNMP fallback...")
                result = self._snmp_fallback_collection(device)
        
        elif device.device_type in ['Linux Servers', 'Hypervisors']:
            # Linux/Hypervisor: SSH first, then SNMP if fails
            self.log_message.emit(f"   🐧 {device.ip}: Trying Linux SSH collection...")
            result = self._linux_maximum_collection(device)
            if not result.success:
                self.log_message.emit(f"   📡 {device.ip}: SSH failed, trying SNMP fallback...")
                result = self._snmp_fallback_collection(device)
        
        elif device.device_type in ['Firewalls', 'Switches', 'Access Points']:
            # Network devices: SSH first, then SNMP if fails
            self.log_message.emit(f"   🌐 {device.ip}: Trying network device collection...")
            result = self._network_device_collection(device)
            if not result.success:
                self.log_message.emit(f"   📡 {device.ip}: Network SSH failed, trying SNMP fallback...")
                result = self._snmp_fallback_collection(device)
        
        elif device.device_type in ['Printers', 'Finger Prints']:
            # Special devices: SNMP first, then SSH if available
            self.log_message.emit(f"   🖨️ {device.ip}: Trying printer/special device collection...")
            result = self._snmp_fallback_collection(device)
            if not result.success and 22 in device.open_ports:
                self.log_message.emit(f"   🔗 {device.ip}: SNMP failed, trying SSH fallback...")
                result = self._ssh_fallback_collection(device)
        
        else:
            # Unknown devices: Try all methods
            self.log_message.emit(f"   ❓ {device.ip}: Trying unknown device collection...")
            result = self._unknown_device_collection(device)
        
        result.collection_time = time.time() - start_time
        result.device_type = device.device_type
        
        if result.success:
            self.log_message.emit(f"   ✅ {device.ip}: Collection successful via {result.method}")
        else:
            self.log_message.emit(f"   ❌ {device.ip}: All collection methods failed - {result.error}")
        
        return result

    def _windows_maximum_collection(self, device: AliveDevice) -> CollectionResult:
        """Maximum WMI data collection for Windows devices"""
        try:
            # Comprehensive WMI collection
            self.log_message.emit(f"   🔍 {device.ip}: Attempting WMI connection...")
            data = self._comprehensive_wmi_collection(device.ip)
            if data:
                # Calculate data completeness
                completeness = self._calculate_data_completeness(data, 'windows')
                self.log_message.emit(f"   ✅ {device.ip}: WMI data collected ({len(data)} fields, {completeness:.1f}% complete)")
                return CollectionResult(
                    ip=device.ip,
                    success=True,
                    method='Comprehensive WMI',
                    data=data,
                    data_completeness=completeness
                )
            else:
                self.log_message.emit(f"   ⚠️ {device.ip}: WMI returned no data (may need admin rights)")
        except Exception as e:
            self.log_message.emit(f"   ❌ {device.ip}: WMI collection error: {str(e)[:100]}")
        
        return CollectionResult(
            ip=device.ip,
            success=False,
            method='WMI',
            error='WMI collection failed - check credentials and admin rights'
        )

    def _linux_maximum_collection(self, device: AliveDevice) -> CollectionResult:
        """Maximum SSH data collection for Linux devices"""
        for i, creds in enumerate(self.linux_creds):
            try:
                self.log_message.emit(f"   🔑 {device.ip}: Trying SSH credentials {i+1}/{len(self.linux_creds)}...")
                data = self._comprehensive_ssh_collection(device.ip, creds['username'], creds['password'])
                if data:
                    completeness = self._calculate_data_completeness(data, 'linux')
                    self.log_message.emit(f"   ✅ {device.ip}: SSH data collected ({len(data)} fields, {completeness:.1f}% complete)")
                    return CollectionResult(
                        ip=device.ip,
                        success=True,
                        method='Comprehensive SSH',
                        data=data,
                        data_completeness=completeness
                    )
                else:
                    self.log_message.emit(f"   ⚠️ {device.ip}: SSH connected but no data returned")
            except Exception as e:
                self.log_message.emit(f"   ❌ {device.ip}: SSH error with creds {i+1}: {str(e)[:50]}")
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
            except Exception:
                continue
        
        # Fallback to SNMP
        return self._snmp_fallback_collection(device)

    def _snmp_fallback_collection(self, device: AliveDevice) -> CollectionResult:
        """Comprehensive SNMP data collection"""
        if not PYSNMP_AVAILABLE:
            self.log_message.emit(f"   ⚠️ {device.ip}: SNMP library not available, using basic fallback")
            return self._basic_fallback_collection(device)
        
        for i, community in enumerate(self.snmp_v2c):
            try:
                self.log_message.emit(f"   📡 {device.ip}: Trying SNMP community {i+1}/{len(self.snmp_v2c)}...")
                data = self._comprehensive_snmp_collection(device.ip, community)
                if data:
                    completeness = self._calculate_data_completeness(data, 'snmp')
                    self.log_message.emit(f"   ✅ {device.ip}: SNMP data collected ({len(data)} fields, {completeness:.1f}% complete)")
                    return CollectionResult(
                        ip=device.ip,
                        success=True,
                        method='Comprehensive SNMP',
                        data=data,
                        data_completeness=completeness
                    )
                else:
                    self.log_message.emit(f"   ⚠️ {device.ip}: SNMP connected but no data returned")
            except Exception as e:
                self.log_message.emit(f"   ❌ {device.ip}: SNMP error with community {i+1}: {str(e)[:50]}")
                continue
        
        self.log_message.emit(f"   🔄 {device.ip}: All SNMP attempts failed, using basic fallback")
        return self._basic_fallback_collection(device)

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
            except Exception:
                continue
        
        return CollectionResult(
            ip=device.ip,
            success=False,
            method='SSH',
            error='SSH fallback failed'
        )

    def _basic_fallback_collection(self, device: AliveDevice) -> CollectionResult:
        """Basic fallback collection that always provides some data"""
        try:
            self.log_message.emit(f"   🎯 {device.ip}: Using basic fallback collection...")
            
            # Create basic device data from what we already know
            data = {
                'ip_address': device.ip,
                'device_type': device.device_type,
                'os_family': device.os_family,
                'ping_time': device.ping_time,
                'open_ports': device.open_ports,
                'services': device.services,
                'confidence': device.confidence,
                'collection_method': 'Basic Fallback',
                'scan_timestamp': datetime.now().isoformat(),
                'port_count': len(device.open_ports),
                'status': 'alive'
            }
            
            # Try to get hostname using multiple methods for the TARGET device
            try:
                import socket
                import os
                
                # Method 1: DNS reverse lookup for the TARGET IP
                try:
                    dns_hostname = socket.gethostbyaddr(device.ip)[0]
                    data['dns_hostname'] = dns_hostname
                    self.log_message.emit(f"   🏷️ {device.ip}: DNS reverse lookup: {dns_hostname}")
                except Exception:
                    data['dns_hostname'] = 'unknown'
                
                # Method 2: Only use local hostname methods if scanning localhost/local network
                if device.ip in ['127.0.0.1', 'localhost']:
                    try:
                        # Get local machine hostname only for localhost
                        current_hostname = socket.gethostname()
                        data['current_hostname'] = current_hostname
                        
                        # Get environment COMPUTERNAME only for localhost
                        env_computername = os.environ.get('COMPUTERNAME')
                        if env_computername:
                            data['computername'] = env_computername
                        
                        # Use the best available hostname for localhost
                        if current_hostname:
                            data['hostname'] = current_hostname
                            self.log_message.emit(f"   🏷️ {device.ip}: Local hostname: {current_hostname}")
                        elif env_computername:
                            data['hostname'] = env_computername
                            self.log_message.emit(f"   🏷️ {device.ip}: Local COMPUTERNAME: {env_computername}")
                        else:
                            data['hostname'] = data['dns_hostname']
                            
                    except Exception:
                        data['hostname'] = data['dns_hostname']
                else:
                    # For remote devices, only use DNS/network-based methods
                    if data['dns_hostname'] != 'unknown':
                        data['hostname'] = data['dns_hostname']
                        self.log_message.emit(f"   🏷️ {device.ip}: Remote hostname: {data['dns_hostname']}")
                    else:
                        data['hostname'] = f'device-{device.ip.replace(".", "-")}'
                        self.log_message.emit(f"   🏷️ {device.ip}: Generated hostname: {data['hostname']}")
                    
            except Exception:
                data['hostname'] = f'device-{device.ip.replace(".", "-")}'
            
            # Add port-based service detection
            service_map = {
                22: 'SSH', 80: 'HTTP', 443: 'HTTPS', 23: 'Telnet',
                21: 'FTP', 25: 'SMTP', 53: 'DNS', 110: 'POP3',
                135: 'RPC', 139: 'NetBIOS', 445: 'SMB', 3389: 'RDP',
                161: 'SNMP', 9100: 'Printer', 631: 'IPP'
            }
            
            detected_services = []
            for port in device.open_ports:
                if port in service_map:
                    detected_services.append(f"{service_map[port]} ({port})")
                else:
                    detected_services.append(f"Port {port}")
            
            data['detected_services'] = detected_services
            data['service_count'] = len(detected_services)
            
            completeness = 25.0  # Basic data always provides 25% completeness
            self.log_message.emit(f"   ✅ {device.ip}: Basic fallback successful ({len(data)} fields, {completeness:.1f}% complete)")
            
            return CollectionResult(
                ip=device.ip,
                success=True,
                method='Basic Fallback',
                data=data,
                data_completeness=completeness
            )
            
        except Exception as e:
            self.log_message.emit(f"   ❌ {device.ip}: Basic fallback failed: {e}")
            return CollectionResult(
                ip=device.ip,
                success=False,
                method='Basic Fallback',
                error=f'Basic fallback failed: {e}'
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
            except Exception:
                pass
        
        return self._basic_fallback_collection(device)

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
                                'NetBIOS Name': cs.Name,  # Domain registered name
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
                    
                    # ADDITIONAL HOSTNAME COLLECTION (For Remote Device)
                    try:
                        # Get hostname from the REMOTE device via WMI, not local machine
                        
                        # Method 1: WMI Win32_ComputerSystem for remote hostname
                        try:
                            for cs in conn.Win32_ComputerSystem():
                                if cs.Name:
                                    data['Remote NetBIOS Name'] = cs.Name
                                    data['Remote Computer Name'] = cs.Name
                                    self.log_message.emit(f"   🏷️ {ip}: Remote NetBIOS name: {cs.Name}")
                        except Exception:
                            pass
                        
                        # Method 2: WMI Win32_NetworkAdapterConfiguration for DNS hostname
                        try:
                            for config in conn.Win32_NetworkAdapterConfiguration():
                                if config.DNSHostName and config.DNSHostName.strip():
                                    data['Remote DNS Hostname'] = config.DNSHostName
                                    self.log_message.emit(f"   🏷️ {ip}: Remote DNS hostname: {config.DNSHostName}")
                                    break
                        except Exception:
                            pass
                        
                        # Method 3: DNS Forward/Reverse Lookup for DOMAIN DNS RECORD
                        dns_hostname = None
                        dns_status = 'none'
                        try:
                            import socket
                            
                            # Forward DNS lookup - get hostname from DNS domain record
                            try:
                                dns_hostname = socket.gethostbyaddr(ip)[0]
                                data['DNS Hostname'] = dns_hostname
                                self.log_message.emit(f"   🌐 {ip}: DNS domain record: {dns_hostname}")
                                
                                # Check if DNS record matches device hostname
                                device_hostname = data.get('Remote Computer Name') or data.get('Remote NetBIOS Name')
                                if device_hostname and dns_hostname:
                                    # Compare hostnames (case insensitive, handle FQDN vs short name)
                                    device_short = device_hostname.split('.')[0].lower()
                                    dns_short = dns_hostname.split('.')[0].lower()
                                    
                                    if device_short == dns_short:
                                        dns_status = 'ok'
                                        self.log_message.emit(f"   ✅ {ip}: DNS record matches device hostname")
                                    else:
                                        dns_status = 'mismatch'
                                        self.log_message.emit(f"   ⚠️ {ip}: DNS mismatch - Device: {device_hostname}, DNS: {dns_hostname}")
                                else:
                                    dns_status = 'partial'
                                    
                            except socket.herror:
                                # No DNS record found in domain
                                data['DNS Hostname'] = None
                                dns_status = 'none'
                                self.log_message.emit(f"   ❌ {ip}: No DNS record found in domain")
                            except Exception as e:
                                data['DNS Hostname'] = None
                                dns_status = 'error'
                                self.log_message.emit(f"   ⚠️ {ip}: DNS lookup error: {str(e)[:50]}")
                                
                            data['DNS Status'] = dns_status
                                
                        except Exception:
                            data['DNS Hostname'] = None
                            data['DNS Status'] = 'error'
                        
                        # Method 4: Try reverse DNS lookup for additional validation
                        try:
                            reverse_dns = socket.gethostbyaddr(ip)[0]
                            data['Reverse DNS'] = reverse_dns
                            self.log_message.emit(f"   🔄 {ip}: Reverse DNS: {reverse_dns}")
                        except Exception:
                            pass
                        
                        # Method 5: WMI Win32_Environment for COMPUTERNAME on remote machine
                        try:
                            for env in conn.Win32_Environment():
                                if env.Name == 'COMPUTERNAME' and env.VariableValue:
                                    data['Remote COMPUTERNAME'] = env.VariableValue
                                    self.log_message.emit(f"   🏷️ {ip}: Remote COMPUTERNAME: {env.VariableValue}")
                                    break
                        except Exception:
                            pass
                        
                        # Determine the best hostname for the REMOTE device
                        hostname_priority = [
                            data.get('Remote COMPUTERNAME'),     # Best - actual machine name
                            data.get('Remote DNS Hostname'),     # Good - DNS registered name
                            data.get('Remote NetBIOS Name'),     # OK - NetBIOS name
                            data.get('DNS Hostname'),            # Domain DNS record
                            data.get('Reverse DNS'),             # Fallback - DNS reverse lookup
                            data.get('Remote Computer Name')     # Last resort
                        ]
                        
                        for hostname in hostname_priority:
                            if hostname and hostname.strip() and hostname.lower() not in ['unknown', 'localhost']:
                                data['Hostname'] = hostname.strip()
                                self.log_message.emit(f"   🎯 {ip}: Selected hostname: {data['Hostname']}")
                                break
                        
                        if not data.get('Hostname'):
                            data['Hostname'] = f'device-{ip.replace(".", "-")}'
                            self.log_message.emit(f"   ⚠️ {ip}: Using generated hostname: {data['Hostname']}")
                        
                        # DNS Validation Summary
                        if dns_status == 'ok':
                            self.log_message.emit(f"   ✅ {ip}: DNS validation PASSED - hostname matches domain record")
                        elif dns_status == 'mismatch':
                            self.log_message.emit(f"   ⚠️ {ip}: DNS validation WARNING - hostname/DNS mismatch detected")
                        elif dns_status == 'none':
                            self.log_message.emit(f"   ❌ {ip}: DNS validation FAILED - no domain record found")
                        
                    except Exception as e:
                        data['Hostname_Collection_Error'] = str(e)
                        data['Hostname'] = f'device-{ip.replace(".", "-")}'
                        data['DNS Hostname'] = None
                        data['DNS Status'] = 'error'
                        self.log_message.emit(f"   ❌ {ip}: Hostname collection error: {str(e)[:50]}")
                    
                    # OPERATING SYSTEM (Complete Details) - 100% COMPREHENSIVE
                    try:
                        for os in conn.Win32_OperatingSystem():
                            # Clean OS name
                            os_name_clean = os.Name.split('|')[0] if '|' in os.Name else os.Name
                            
                            # Format OS version comprehensively
                            os_version_full = f"{os.Version} (Build {os.BuildNumber})"
                            if os.ServicePackMajorVersion:
                                os_version_full += f" SP{os.ServicePackMajorVersion}"
                            
                            data.update({
                                # Database fields for OS
                                'os_name': os_name_clean,  # Main DB field
                                'os_version': os_version_full,  # Main DB field
                                'os_build_number': os.BuildNumber,  # Main DB field
                                'os_architecture': os.OSArchitecture,  # Main DB field
                                'os_service_pack': os.ServicePackMajorVersion,
                                'os_install_date': os.InstallDate,
                                'os_manufacturer': os.Manufacturer,
                                'os_serial_number': os.SerialNumber,
                                'os_registered_user': os.RegisteredUser,
                                'os_organization': os.Organization,
                                'operating_system': os_name_clean,  # Alternative field
                                'system_type': os.OSType,
                                
                                # Legacy/detailed fields
                                'Operating System': os_name_clean,
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
                                'available_memory': os.AvailableVirtualMemory,  # DB field
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
                                'Organization': os.Organization,
                                
                                # Memory utilization calculation
                                'memory_utilization': ((os.TotalVisibleMemorySize - os.FreePhysicalMemory) / os.TotalVisibleMemorySize * 100) if os.TotalVisibleMemorySize else 0,
                                'uptime_days': None  # Will calculate if needed
                            })
                            
                            self.log_message.emit(f"   🖥️ {ip}: OS: {os_name_clean} {os.Version} ({os.OSArchitecture})")
                            
                    except Exception as e:
                        data['WMI_OperatingSystem_Error'] = str(e)
                        data['os_name'] = 'Collection failed'
                        data['os_version'] = 'Unknown'
                    
                    # ===== MAXIMUM DATA COLLECTION FOR ALL 440 DATABASE COLUMNS =====
                    
                    # BIOS INFORMATION (Comprehensive)
                    try:
                        for bios in conn.Win32_BIOS():
                            data.update({
                                'bios_version': bios.Version,
                                'bios_manufacturer': bios.Manufacturer,
                                'bios_serial_number': bios.SerialNumber,
                                'bios_release_date': bios.ReleaseDate,
                                'bios_date': bios.ReleaseDate,
                                'firmware_version': bios.Version,
                                'system_sku': bios.SerialNumber
                            })
                    except Exception as e:
                        data['WMI_BIOS_Error'] = str(e)
                    
                    # MOTHERBOARD/BASEBOARD (Complete Details)
                    try:
                        for board in conn.Win32_BaseBoard():
                            data.update({
                                'motherboard_manufacturer': board.Manufacturer,
                                'motherboard_model': board.Product,
                                'motherboard_serial': board.SerialNumber,
                                'motherboard_version': board.Version,
                                'motherboard': f"{board.Manufacturer} {board.Product}"
                            })
                    except Exception as e:
                        data['WMI_BaseBoard_Error'] = str(e)
                    
                    # CHASSIS INFORMATION
                    try:
                        for chassis in conn.Win32_SystemEnclosure():
                            data.update({
                                'chassis_manufacturer': chassis.Manufacturer,
                                'chassis_serial': chassis.SerialNumber,
                                'chassis_type': chassis.ChassisTypes[0] if chassis.ChassisTypes else None,
                                'system_family': chassis.Model,
                                'asset_tag_hw': chassis.SMBIOSAssetTag,
                                'barcode': chassis.SMBIOSAssetTag
                            })
                    except Exception as e:
                        data['WMI_Chassis_Error'] = str(e)
                    
                    # PROCESSOR INFORMATION (Complete Details) - 100% COMPREHENSIVE
                    try:
                        processors = []
                        total_cores = 0
                        total_logical = 0
                        
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
                                'Characteristics': cpu.Characteristics,
                                'Description': cpu.Description,
                                'Unique ID': cpu.UniqueId,
                                'Upgrade Method': cpu.UpgradeMethod,
                                'Version': cpu.Version,
                                'Availability': cpu.Availability,
                                'Config Manager Error Code': cpu.ConfigManagerErrorCode,
                                'Config Manager User Config': cpu.ConfigManagerUserConfig,
                                'Creation Class Name': cpu.CreationClassName,
                                'Error Cleared': cpu.ErrorCleared,
                                'Error Description': cpu.ErrorDescription,
                                'Install Date': cpu.InstallDate,
                                'Last Error Code': cpu.LastErrorCode,
                                'PNP Device ID': cpu.PNPDeviceID,
                                'Power Management Capabilities': cpu.PowerManagementCapabilities,
                                'Status Info': cpu.StatusInfo,
                                'System Creation Class Name': cpu.SystemCreationClassName,
                                'System Name': cpu.SystemName
                            }
                            processors.append(cpu_info)
                            
                            # Accumulate core counts
                            if cpu.NumberOfCores:
                                total_cores += cpu.NumberOfCores
                            if cpu.NumberOfLogicalProcessors:
                                total_logical += cpu.NumberOfLogicalProcessors
                        
                        if processors:
                            # Set comprehensive processor info for ALL database fields
                            primary_cpu = processors[0]
                            
                            # Format processor speed
                            speed_mhz = primary_cpu['Max Clock Speed'] if primary_cpu['Max Clock Speed'] else 0
                            speed_ghz = speed_mhz / 1000 if speed_mhz > 1000 else speed_mhz
                            speed_unit = 'GHz' if speed_mhz > 1000 else 'MHz'
                            
                            data.update({
                                # Database fields for processor
                                'processor_name': primary_cpu['Name'],  # Main DB field
                                'processor_cores': total_cores,  # Main DB field
                                'processor_speed': f"{speed_ghz:.2f} {speed_unit}",  # Formatted speed
                                'processor_architecture': primary_cpu['Architecture'],
                                'processor_manufacturer': primary_cpu['Manufacturer'],
                                'processor_logical_processors': total_logical,
                                'cpu_name': primary_cpu['Name'],  # Alternative field
                                'cpu_cores': total_cores,  # Alternative field
                                'cpu_threads': total_logical,  # Alternative field
                                'cpu_speed_mhz': speed_mhz,  # Raw speed
                                'cpu_socket': primary_cpu['Socket Designation'],
                                'cpu_cache_l2': primary_cpu['L2 Cache Size'],
                                'cpu_cache_l3': primary_cpu['L3 Cache Size'],
                                'cpu_voltage': primary_cpu['Voltage'],
                                'cpu_load_percentage': primary_cpu['Load Percentage'],
                                
                                # Legacy fields
                                'Processor Name': primary_cpu['Name'],
                                'Processor Manufacturer': primary_cpu['Manufacturer'],
                                'Processor Architecture': primary_cpu['Architecture'],
                                'Processor Cores': total_cores,
                                'Processor Logical Processors': total_logical,
                                'Processor Speed': primary_cpu['Max Clock Speed'],
                                'Processor L2 Cache': primary_cpu['L2 Cache Size'],
                                'Processor L3 Cache': primary_cpu['L3 Cache Size'],
                                'Processor Socket': primary_cpu['Socket Designation']
                            })
                            
                            # Store all processors
                            data['All Processors'] = processors
                            data['Total Processor Count'] = len(processors)
                            data['Total Physical Cores'] = total_cores
                            data['Total Logical Processors'] = total_logical
                            
                            # Processor summary
                            data['Processor Summary'] = f"{len(processors)}x {primary_cpu['Name']} ({total_cores} cores, {total_logical} threads)"
                            
                            self.log_message.emit(f"   💻 {ip}: CPU: {primary_cpu['Name']} ({total_cores} cores, {total_logical} threads)")
                        
                    except Exception as e:
                        data['WMI_Processor_Error'] = str(e)
                        data['processor_name'] = 'Collection failed'
                        data['processor_cores'] = 0
                    
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
                        
                        # Enhanced storage summary with EXACT formatting as requested: "Disk 1 = 250 GB, Disk 2 = 500 GB"
                        if storage_devices:
                            storage_summary = []
                            total_storage_gb = 0
                            
                            for i, disk in enumerate(storage_devices, 1):
                                size_bytes = int(disk['Size']) if disk['Size'] else 0
                                size_gb = size_bytes // (1024**3)
                                total_storage_gb += size_gb
                                
                                # Format EXACTLY as requested
                                storage_summary.append(f"Disk {i} = {size_gb} GB")
                            
                            # Set database fields
                            data['disk_info'] = ', '.join(storage_summary)  # Main DB field
                            data['Storage Summary'] = ', '.join(storage_summary)  # Legacy field
                            data['total_storage_gb'] = total_storage_gb
                            data['storage_device_count'] = len(storage_devices)
                            data['hard_drive_capacity'] = f"{total_storage_gb} GB"
                            
                            # Enhanced disk details for database
                            if storage_devices:
                                primary_disk = storage_devices[0]
                                data.update({
                                    'primary_disk_model': primary_disk['Model'],
                                    'primary_disk_interface': primary_disk['Interface Type'],
                                    'primary_disk_serial': primary_disk['Serial Number'],
                                    'primary_disk_firmware': primary_disk['Firmware Revision']
                                })
                            
                            self.log_message.emit(f"   💾 {ip}: Storage: {data['disk_info']} (Total: {total_storage_gb} GB)")
                        else:
                            data['disk_info'] = 'No disks detected'
                            data['total_storage_gb'] = 0
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
                    
                    # GRAPHICS/VIDEO INFORMATION (Complete Details) - 100% COMPREHENSIVE
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
                                'Video Memory Type': video.VideoMemoryType,
                                'Device ID': video.DeviceID,
                                'Caption': video.Caption,
                                'Device Specific Pens': video.DeviceSpecificPens,
                                'Dither Type': video.DitherType,
                                'ICM Intent': video.ICMIntent,
                                'ICM Method': video.ICMMethod,
                                'Reserved System Palette Entries': video.ReservedSystemPaletteEntries,
                                'Specification Version': video.SpecificationVersion,
                                'System Palette Entries': video.SystemPaletteEntries
                            }
                            video_controllers.append(video_info)
                        
                        # CONNECTED MONITORS/SCREENS (Complete Details)
                        monitors = []
                        try:
                            for monitor in conn.Win32_DesktopMonitor():
                                monitor_info = {
                                    'Name': monitor.Name,
                                    'Description': monitor.Description,
                                    'Monitor Type': monitor.MonitorType,
                                    'Monitor Manufacturer': monitor.MonitorManufacturer,
                                    'Screen Height': monitor.ScreenHeight,
                                    'Screen Width': monitor.ScreenWidth,
                                    'Pixels Per X Logical Inch': monitor.PixelsPerXLogicalInch,
                                    'Pixels Per Y Logical Inch': monitor.PixelsPerYLogicalInch,
                                    'Device ID': monitor.DeviceID,
                                    'PNP Device ID': monitor.PNPDeviceID,
                                    'Status': monitor.Status,
                                    'Availability': monitor.Availability,
                                    'Is Locked': monitor.IsLocked,
                                    'Display Type': monitor.DisplayType
                                }
                                monitors.append(monitor_info)
                        except Exception:
                            # Fallback to Win32_PnPEntity for monitor detection
                            try:
                                for device in conn.Win32_PnPEntity():
                                    if device.Name and 'monitor' in device.Name.lower():
                                        monitor_info = {
                                            'Name': device.Name,
                                            'Description': device.Description,
                                            'Device ID': device.DeviceID,
                                            'Manufacturer': device.Manufacturer,
                                            'Status': device.Status,
                                            'Hardware ID': device.HardwareID,
                                            'Compatible ID': device.CompatibleID,
                                            'Service': device.Service,
                                            'Class': device.Class,
                                            'Class GUID': device.ClassGuid
                                        }
                                        monitors.append(monitor_info)
                            except Exception:
                                pass
                        
                        data.update({
                            'Video Controllers': video_controllers,
                            'Connected Monitors': monitors,
                            'Video Controller Count': len(video_controllers),
                            'Connected Monitor Count': len(monitors)
                        })
                        
                        # Enhanced graphics summary with ALL details
                        if video_controllers:
                            primary_video = video_controllers[0]
                            data.update({
                                'graphics_cards': primary_video['Name'],  # Database field
                                'video_memory': primary_video['Adapter RAM'],  # Database field
                                'graphics_driver_version': primary_video['Driver Version'],  # Database field
                                'Primary Graphics Card': primary_video['Name'],
                                'Graphics Memory': primary_video['Adapter RAM'],
                                'Graphics Driver Version': primary_video['Driver Version'],
                                'Current Resolution': f"{primary_video['Current Horizontal Resolution']}x{primary_video['Current Vertical Resolution']}" if primary_video['Current Horizontal Resolution'] else None,
                                'Current Refresh Rate': primary_video['Current Refresh Rate'],
                                'processor_name': primary_video['Video Processor']  # Additional processor info
                            })
                            
                            # Create comprehensive graphics summary
                            graphics_summary = []
                            for i, video in enumerate(video_controllers, 1):
                                ram_mb = int(video['Adapter RAM']) // (1024*1024) if video['Adapter RAM'] else 0
                                ram_gb = ram_mb / 1024 if ram_mb > 1024 else ram_mb
                                unit = 'GB' if ram_mb > 1024 else 'MB'
                                resolution = f"{video['Current Horizontal Resolution']}x{video['Current Vertical Resolution']}" if video['Current Horizontal Resolution'] else 'Unknown'
                                graphics_summary.append(f"GPU {i} = {video['Name']} ({ram_gb:.1f} {unit}, {resolution})")
                            data['Graphics Summary'] = ', '.join(graphics_summary)
                        
                        # Connected monitors summary
                        if monitors:
                            monitor_summary = []
                            for i, monitor in enumerate(monitors, 1):
                                resolution = f"{monitor['Screen Width']}x{monitor['Screen Height']}" if monitor.get('Screen Width') else 'Unknown'
                                monitor_summary.append(f"Monitor {i} = {monitor['Name']} ({resolution})")
                            data['Connected Screens'] = ', '.join(monitor_summary)
                            data['connected_monitors'] = len(monitors)  # Database field
                            data['monitor_resolution'] = f"{monitors[0]['Screen Width']}x{monitors[0]['Screen Height']}" if monitors and monitors[0].get('Screen Width') else None
                        else:
                            data['Connected Screens'] = 'No monitors detected'
                            data['connected_monitors'] = 0
                        
                        self.log_message.emit(f"   🎮 {ip}: Graphics: {len(video_controllers)} GPUs, {len(monitors)} monitors")
                        
                    except Exception as e:
                        data['WMI_Graphics_Error'] = str(e)
                        data['graphics_cards'] = 'Collection failed'
                        data['connected_monitors'] = 0
                    
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
                    
                    # ===== ADDITIONAL COMPREHENSIVE HARDWARE COLLECTION (100% POWER) =====
                    
                    # USB DEVICES (Complete Details)
                    try:
                        usb_devices = []
                        for usb in conn.Win32_USBControllerDevice():
                            try:
                                dependent = usb.Dependent
                                if dependent:
                                    # Get USB device details
                                    device_path = dependent.split('=')[1].strip('"')
                                    for pnp in conn.Win32_PnPEntity():
                                        if pnp.DeviceID == device_path:
                                            usb_info = {
                                                'Name': pnp.Name,
                                                'Description': pnp.Description,
                                                'Device ID': pnp.DeviceID,
                                                'Manufacturer': pnp.Manufacturer,
                                                'Status': pnp.Status,
                                                'Hardware ID': pnp.HardwareID,
                                                'Service': pnp.Service,
                                                'Class': pnp.Class
                                            }
                                            usb_devices.append(usb_info)
                                            break
                            except Exception:
                                pass
                        
                        data.update({
                            'USB Devices': usb_devices,
                            'USB Device Count': len(usb_devices)
                        })
                        
                        if usb_devices:
                            usb_summary = [f"USB {i}: {usb['Name']}" for i, usb in enumerate(usb_devices[:5], 1)]
                            data['USB Summary'] = ', '.join(usb_summary)
                        
                    except Exception as e:
                        data['WMI_USB_Error'] = str(e)
                    
                    # SOUND DEVICES (Complete Details)
                    try:
                        sound_devices = []
                        for sound in conn.Win32_SoundDevice():
                            sound_info = {
                                'Name': sound.Name,
                                'Description': sound.Description,
                                'Manufacturer': sound.Manufacturer,
                                'Status': sound.Status,
                                'Device ID': sound.DeviceID,
                                'PNP Device ID': sound.PNPDeviceID,
                                'DMA Buffer Size': sound.DMABufferSize,
                                'Power Management Supported': sound.PowerManagementSupported
                            }
                            sound_devices.append(sound_info)
                        
                        data.update({
                            'Sound Devices': sound_devices,
                            'Sound Device Count': len(sound_devices),
                            'audio_devices': len(sound_devices)  # Database field
                        })
                        
                        if sound_devices:
                            data['Primary Sound Device'] = sound_devices[0]['Name']
                            data['audio_device_name'] = sound_devices[0]['Name']
                        
                    except Exception as e:
                        data['WMI_Sound_Error'] = str(e)
                    
                    # KEYBOARD AND MOUSE (Complete Details)
                    try:
                        keyboards = []
                        for keyboard in conn.Win32_Keyboard():
                            kb_info = {
                                'Name': keyboard.Name,
                                'Description': keyboard.Description,
                                'Device ID': keyboard.DeviceID,
                                'Layout': keyboard.Layout,
                                'Number Of Function Keys': keyboard.NumberOfFunctionKeys,
                                'Status': keyboard.Status,
                                'PNP Device ID': keyboard.PNPDeviceID
                            }
                            keyboards.append(kb_info)
                        
                        mice = []
                        for mouse in conn.Win32_PointingDevice():
                            mouse_info = {
                                'Name': mouse.Name,
                                'Description': mouse.Description,
                                'Device ID': mouse.DeviceID,
                                'Manufacturer': mouse.Manufacturer,
                                'Number Of Buttons': mouse.NumberOfButtons,
                                'Pointing Type': mouse.PointingType,
                                'Resolution': mouse.Resolution,
                                'Status': mouse.Status,
                                'PNP Device ID': mouse.PNPDeviceID
                            }
                            mice.append(mouse_info)
                        
                        data.update({
                            'Keyboards': keyboards,
                            'Mice': mice,
                            'Keyboard Count': len(keyboards),
                            'Mouse Count': len(mice),
                            'input_devices': len(keyboards) + len(mice)  # Database field
                        })
                        
                    except Exception as e:
                        data['WMI_Input_Error'] = str(e)
                    
                    # OPTICAL DRIVES (CD/DVD/Blu-ray)
                    try:
                        optical_drives = []
                        for cdrom in conn.Win32_CDROMDrive():
                            drive_info = {
                                'Name': cdrom.Name,
                                'Description': cdrom.Description,
                                'Device ID': cdrom.DeviceID,
                                'Manufacturer': cdrom.Manufacturer,
                                'Media Type': cdrom.MediaType,
                                'Size': cdrom.Size,
                                'Transfer Rate': cdrom.TransferRate,
                                'Capabilities': cdrom.Capabilities,
                                'Status': cdrom.Status,
                                'Drive': cdrom.Drive
                            }
                            optical_drives.append(drive_info)
                        
                        data.update({
                            'Optical Drives': optical_drives,
                            'Optical Drive Count': len(optical_drives),
                            'optical_drives': len(optical_drives)  # Database field
                        })
                        
                    except Exception as e:
                        data['WMI_Optical_Error'] = str(e)
                    
                    # PRINTERS (Complete Details)
                    try:
                        printers = []
                        for printer in conn.Win32_Printer():
                            printer_info = {
                                'Name': printer.Name,
                                'Description': printer.Description,
                                'Device ID': printer.DeviceID,
                                'Location': printer.Location,
                                'Port Name': printer.PortName,
                                'Driver Name': printer.DriverName,
                                'Print Processor': printer.PrintProcessor,
                                'Resolution': printer.HorizontalResolution,
                                'Status': printer.PrinterStatus,
                                'Shared': printer.Shared,
                                'Network': printer.Network,
                                'Local': printer.Local,
                                'Default': printer.Default
                            }
                            printers.append(printer_info)
                        
                        data.update({
                            'Printers': printers,
                            'Printer Count': len(printers),
                            'installed_printers': len(printers)  # Database field
                        })
                        
                    except Exception as e:
                        data['WMI_Printer_Error'] = str(e)
                    
                    # INSTALLED SOFTWARE (Enhanced Collection)
                    try:
                        software_list = []
                        for software in conn.Win32_Product():
                            if software.Name and software.Name.strip():
                                software_info = {
                                    'Name': software.Name,
                                    'Version': software.Version,
                                    'Vendor': software.Vendor,
                                    'Install Date': software.InstallDate,
                                    'Install Location': software.InstallLocation,
                                    'Package Cache': software.PackageCache,
                                    'Package Code': software.PackageCode,
                                    'Package Name': software.PackageName,
                                    'Identifying Number': software.IdentifyingNumber
                                }
                                software_list.append(software_info)
                        
                        data.update({
                            'Installed Software': software_list[:100],  # Limit to first 100
                            'Software Count': len(software_list),
                            'installed_software_count': len(software_list)  # Database field
                        })
                        
                        # Create software summary
                        if software_list:
                            software_names = [sw['Name'] for sw in software_list[:20]]
                            data['installed_software'] = ', '.join(software_names)
                        
                    except Exception as e:
                        data['WMI_Software_Error'] = str(e)
                    
                    # SYSTEM FANS AND TEMPERATURE (If available)
                    try:
                        fans = []
                        for fan in conn.Win32_Fan():
                            fan_info = {
                                'Name': fan.Name,
                                'Description': fan.Description,
                                'Device ID': fan.DeviceID,
                                'Status': fan.Status,
                                'Active Cooling': fan.ActiveCooling,
                                'Variable Speed': fan.VariableSpeed
                            }
                            fans.append(fan_info)
                        
                        temperatures = []
                        for temp in conn.Win32_TemperatureProbe():
                            temp_info = {
                                'Name': temp.Name,
                                'Description': temp.Description,
                                'Current Reading': temp.CurrentReading,
                                'Status': temp.Status
                            }
                            temperatures.append(temp_info)
                        
                        data.update({
                            'System Fans': fans,
                            'Temperature Probes': temperatures,
                            'Fan Count': len(fans),
                            'Temperature Probe Count': len(temperatures)
                        })
                        
                    except Exception as e:
                        data['WMI_Thermal_Error'] = str(e)
                    
                    # POWER SUPPLY (If available)
                    try:
                        power_supplies = []
                        for ps in conn.Win32_PowerSupply():
                            ps_info = {
                                'Name': ps.Name,
                                'Description': ps.Description,
                                'Device ID': ps.DeviceID,
                                'Status': ps.Status
                            }
                            power_supplies.append(ps_info)
                        
                        data.update({
                            'Power Supplies': power_supplies,
                            'Power Supply Count': len(power_supplies)
                        })
                        
                    except Exception as e:
                        data['WMI_Power_Error'] = str(e)
                    
                    # COLLECTION QUALITY METRICS
                    try:
                        # Calculate comprehensive collection success rate
                        collection_categories = [
                            'System Information', 'Operating System', 'Processor', 'Memory', 
                            'Storage', 'Network', 'Graphics', 'BIOS', 'Users'
                        ]
                        
                        successful_categories = 0
                        for category in collection_categories:
                            if any(key.startswith(category.replace(' ', '')) for key in data.keys()):
                                successful_categories += 1
                        
                        collection_quality = (successful_categories / len(collection_categories)) * 100
                        
                        data.update({
                            'collection_quality': 'high' if collection_quality > 80 else 'medium' if collection_quality > 50 else 'low',
                            'quality_score': collection_quality,
                            'wmi_collection_status': 'success',
                            'wmi_collection_time': datetime.now().isoformat(),
                            'data_completeness': collection_quality
                        })
                        
                        self.log_message.emit(f"   ✅ {ip}: WMI collection completed - {collection_quality:.1f}% comprehensive")
                        
                    except Exception as e:
                        data['WMI_Quality_Error'] = str(e)
                    
                    # SUCCESS - Return comprehensive data
                    return data
                    
                except Exception:
                    continue
            
            return None
            
        except Exception:
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
            
        except Exception:
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
            
        except Exception:
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
            
        except Exception:
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

    def _save_to_database(self, data: Dict) -> bool:
        """Smart database save with duplicate prevention using enterprise-grade validation"""
        try:
            # Initialize smart duplicate validator if available
            if DUPLICATE_VALIDATOR_AVAILABLE:
                validator = SmartDuplicateValidator()
                
                # Use smart save with duplicate prevention
                save_result = validator.smart_save_device(data)
                
                if save_result['success']:
                    action = save_result['action']
                    device_id = save_result['device_id']
                    duplicate_info = save_result['duplicate_info']
                    
                    # Log the smart save result
                    if action == 'insert':
                        self.log_message.emit(f"   💾 NEW DEVICE: {data.get('ip_address', 'unknown')} (ID: {device_id})")
                    elif action == 'update':
                        confidence = duplicate_info.get('confidence', 0)
                        match_type = duplicate_info.get('match_type', 'unknown')
                        self.log_message.emit(f"   🔄 UPDATED: {data.get('ip_address', 'unknown')} (ID: {device_id}, {match_type}, {confidence:.0%} confidence)")
                    elif action == 'merge':
                        self.log_message.emit(f"   🔀 MERGED: {data.get('ip_address', 'unknown')} (ID: {device_id}, enhanced with new data)")
                    
                    return True
                else:
                    self.log_message.emit(f"   ❌ SAVE FAILED: {save_result.get('message', 'Unknown error')}")
                    return False
            
            else:
                # Fallback to legacy save method if validator not available
                self.log_message.emit("   ⚠️ Smart duplicate validator not available, using legacy save")
                return self._legacy_save_to_database(data)
                
        except Exception as e:
            self.log_message.emit(f"   ❌ Smart save error: {str(e)[:100]}...")
            # Fallback to legacy save
            return self._legacy_save_to_database(data)

    def _legacy_save_to_database(self, data: Dict) -> bool:
        """Legacy database save method (fallback)"""
        try:
            import sqlite3
            from datetime import datetime
            
            conn = sqlite3.connect('assets.db')
            cursor = conn.cursor()
            
            # Prepare comprehensive data mapping for ALL 440+ database columns
            db_data = {
                # Basic identification
                'hostname': data.get('Hostname') or data.get('hostname') or data.get('Remote Computer Name') or data.get('Remote NetBIOS Name'),
                'ip_address': data.get('IP Address') or data.get('ip') or data.get('IP'),
                'dns_hostname': data.get('DNS Hostname') or data.get('dns_hostname') or data.get('Reverse DNS'),  # Enhanced DNS mapping
                'dns_status': data.get('DNS Status') or data.get('dns_status'),  # Enhanced DNS status mapping
                
                # System information
                'computer_name': data.get('Computer Name') or data.get('NetBIOS Name'),
                'domain': data.get('Domain'),
                'domain_workgroup': data.get('Workgroup') or data.get('Domain'),
                'operating_system': data.get('Operating System'),
                'os_name': data.get('Operating System'),
                'os_version': data.get('OS Version'),
                'os_build_number': data.get('OS Build Number'),
                'os_architecture': data.get('OS Architecture'),
                'os_install_date': data.get('OS Install Date'),
                'last_boot_time': data.get('Last Boot Time'),
                'system_uptime': data.get('System Uptime'),
                
                # Hardware information
                'system_manufacturer': data.get('System Manufacturer'),
                'manufacturer': data.get('System Manufacturer'),
                'system_model': data.get('System Model'),
                'model': data.get('System Model'),
                'model_vendor': data.get('System Manufacturer'),
                'system_type': data.get('System Type'),
                'system_family': data.get('System Family'),
                'serial_number': data.get('Serial Number'),
                
                # BIOS information
                'bios_version': data.get('bios_version'),
                'bios_manufacturer': data.get('bios_manufacturer'),
                'bios_serial_number': data.get('bios_serial_number'),
                'bios_release_date': data.get('bios_release_date'),
                'bios_date': data.get('bios_date'),
                'firmware_version': data.get('firmware_version'),
                
                # Motherboard information
                'motherboard_manufacturer': data.get('motherboard_manufacturer'),
                'motherboard_model': data.get('motherboard_model'),
                'motherboard_serial': data.get('motherboard_serial'),
                'motherboard_version': data.get('motherboard_version'),
                'motherboard': data.get('motherboard'),
                
                # Chassis information
                'chassis_manufacturer': data.get('chassis_manufacturer'),
                'chassis_serial': data.get('chassis_serial'),
                'chassis_type': data.get('chassis_type'),
                'asset_tag_hw': data.get('asset_tag_hw'),
                'barcode': data.get('barcode'),
                
                # Processor information
                'processor_name': data.get('Processor Name'),
                'processor_manufacturer': data.get('Processor Manufacturer'),
                'processor_architecture': data.get('Processor Architecture'),
                'processor_cores': data.get('Processor Cores'),
                'processor_logical_processors': data.get('Processor Logical Processors'),
                'processor_speed': data.get('Processor Speed'),
                'processor_l2_cache': data.get('Processor L2 Cache'),
                'processor_l3_cache': data.get('Processor L3 Cache'),
                'cpu_info': data.get('Processor Name'),
                'cpu_model': data.get('Processor Name'),
                'cpu_cores': data.get('Processor Cores'),
                'cpu_threads': data.get('Processor Logical Processors'),
                'cpu_speed': str(data.get('Processor Speed')) if data.get('Processor Speed') else None,
                
                # Memory information
                'total_physical_memory': data.get('Total Physical Memory'),
                'total_memory': str(data.get('Total Physical Memory')) if data.get('Total Physical Memory') else None,
                'memory_gb': float(data.get('Total Physical Memory')) / (1024**3) if data.get('Total Physical Memory') and str(data.get('Total Physical Memory')).isdigit() else None,
                'installed_ram_gb': int(float(data.get('Total Physical Memory')) / (1024**3)) if data.get('Total Physical Memory') and str(data.get('Total Physical Memory')).isdigit() else None,
                'available_memory': data.get('Available Memory'),
                'memory_utilization': data.get('Memory Utilization'),
                
                # Network information
                'mac_address': data.get('mac_address'),
                'mac_addresses': data.get('mac_addresses'),
                'ip_addresses': data.get('ip_addresses'),
                'subnet_mask': data.get('subnet_mask'),
                'subnet_masks': data.get('subnet_masks'),
                'default_gateway': data.get('default_gateway'),
                'gateway': data.get('gateway'),
                'dns_servers': data.get('dns_servers'),
                'dhcp_enabled': data.get('dhcp_enabled'),
                'network_adapters': data.get('network_adapters'),
                'network_adapter': data.get('network_adapter'),
                'network_speed': data.get('network_speed'),
                'network_adapter_types': data.get('network_adapter_types'),
                'network_adapter_count': data.get('network_adapter_count'),
                'primary_ip': data.get('primary_ip'),
                'secondary_ips': data.get('secondary_ips'),
                
                # Collection metadata
                'device_type': data.get('Device Type') or data.get('device_type'),
                'collection_method': data.get('Collection Method'),
                'data_source': data.get('Collection Method'),
                'collection_timestamp': data.get('Collection Time') or datetime.now().isoformat(),
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'created_by': 'Enhanced Collection Strategy',
                'last_updated_by': 'Enhanced Collection Strategy',
                'wmi_collection_status': 'success' if data.get('Collection Method') == 'Comprehensive WMI' else 'not_attempted',
                'wmi_collection_time': data.get('Collection Time'),
                'collection_quality': 'high' if len([v for v in data.values() if v]) > 50 else 'medium',
                'quality_score': min(100.0, len([v for v in data.values() if v]) * 2),  # Rough quality score
                
                # Status and validation
                'status': 'active',
                'ping_status': 'online',
                'last_ping': datetime.now().isoformat(),
                'last_seen': datetime.now().isoformat(),
                'availability_status': 'available',
                'health_status': 'healthy',
                'realtime_status': 'online',
                
                # NMAP data if available
                'nmap_os_family': data.get('nmap_os_family'),
                'nmap_device_type': data.get('nmap_device_type'), 
                'nmap_confidence': data.get('nmap_confidence'),
                'os_fingerprint': data.get('os_fingerprint'),
                'detection_method': data.get('detection_method'),
                'os_detection_confidence': data.get('confidence'),
                
                # Open ports and services
                'open_ports': str(data.get('open_ports')) if data.get('open_ports') else None,
                'listening_ports': str(data.get('open_ports')) if data.get('open_ports') else None,
                'services': str(data.get('services')) if data.get('services') else None,
                'service_detection': str(data.get('services')) if data.get('services') else None,
                
                # Additional fields that might be collected
                'working_user': data.get('Current User'),
                'assigned_user': data.get('Current User'),
                'logged_on_users': data.get('Current User'),
                'last_logged_user': data.get('Current User'),
                'windows_directory': data.get('Windows Directory'),
                'system_directory': data.get('System Directory'),
                'time_zone': data.get('Time Zone'),
                'country_code': data.get('Country Code'),
                'system_locale': data.get('Locale')
            }
            
            # Remove None values to avoid database issues
            db_data = {k: v for k, v in db_data.items() if v is not None}
            
            # Create INSERT statement with all available columns
            columns = list(db_data.keys())
            placeholders = ['?' for _ in columns]
            values = [db_data[col] for col in columns]
            
            insert_sql = f"""
                INSERT OR REPLACE INTO assets ({', '.join(columns)})
                VALUES ({', '.join(placeholders)})
            """
            
            cursor.execute(insert_sql, values)
            conn.commit()
            conn.close()
            
            self.log_message.emit(f"💾 {data.get('IP Address', 'Unknown')}: Saved {len(db_data)} fields to database")
            return True
            
        except Exception as e:
            self.log_message.emit(f"❌ Database save error: {str(e)[:100]}")
            return False