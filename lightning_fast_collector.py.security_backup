#!/usr/bin/env python3
"""
Lightning-Fast Large Subnet Collector
Ultra-optimized for maximum speed with 1000+ IPs
"""

import time
import socket
import ipaddress
from typing import List, Dict, Optional, Set
from datetime import datetime
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

# Optional imports with fallbacks
try:
    import nmap
    NMAP_AVAILABLE = True
except ImportError:
    NMAP_AVAILABLE = False

try:
    import paramiko
    PARAMIKO_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False

try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False

try:
    from smart_duplicate_validator import SmartDuplicateValidator
    DUPLICATE_VALIDATOR_AVAILABLE = True
except ImportError:
    DUPLICATE_VALIDATOR_AVAILABLE = False

class LightningFastCollector:
    """Lightning-fast collector optimized for speed with large subnets"""
    
    def __init__(self, targets: List[str], credentials: Dict):
        self.targets = targets
        self.credentials = credentials
        self.batch_size = 100  # Larger batches for speed
        self.max_concurrent_threads = 200  # More threads for speed
        
        # Ultra-fast timeouts for maximum speed
        self.ping_timeout = 0.2  # 200ms ping timeout (very fast)
        self.scan_timeout = 1.0  # 1 second scan timeout
        self.collection_timeout = 5.0  # 5 second collection timeout
        
        # Speed optimizations
        self.alive_check_only = False  # Option for alive check only
        self.skip_detailed_collection = False  # Skip detailed data for speed
        
        # Real-time processing
        self.validator = SmartDuplicateValidator() if DUPLICATE_VALIDATOR_AVAILABLE else None
        self.alive_ips = set()  # Track alive IPs
        
        # Statistics
        self.stats = {
            'total_ips': 0,
            'alive_devices': 0,
            'os_detected': 0,
            'data_collected': 0,
            'saved_to_db': 0,
            'duplicates_prevented': 0,
            'method_success': {
                'ping': 0,
                'socket': 0,
                'nmap': 0,
                'wmi': 0,
                'ssh': 0,
                'snmp': 0
            },
            'timing': {
                'alive_scan_time': 0,
                'detailed_scan_time': 0,
                'total_time': 0
            }
        }
        
        logging.basicConfig(level=logging.INFO)
        self.log = logging.getLogger(__name__)

    def lightning_fast_subnet_scan(self, progress_callback=None, log_callback=None, alive_only=False):
        """Lightning-fast subnet scanning optimized for maximum speed"""
        
        start_time = time.time()
        self.log_message(log_callback, "⚡ LIGHTNING-FAST LARGE SUBNET SCANNER")
        self.log_message(log_callback, "=" * 60)
        
        # Generate all target IPs
        all_ips = self._generate_all_ips()
        self.stats['total_ips'] = len(all_ips)
        
        self.log_message(log_callback, f"📍 Target IPs: {len(all_ips)}")
        self.log_message(log_callback, f"⚡ Ultra-fast mode: {self.ping_timeout*1000:.0f}ms ping timeout")
        self.log_message(log_callback, f"🔥 Batch size: {self.batch_size} IPs per batch")
        self.log_message(log_callback, f"🚀 Concurrent threads: {self.max_concurrent_threads}")
        
        if len(all_ips) == 0:
            self.log_message(log_callback, "❌ No valid IP targets found")
            return False
        
        # Phase 1: Ultra-fast alive detection
        alive_start = time.time()
        self.log_message(log_callback, "\n⚡ PHASE 1: LIGHTNING-FAST ALIVE DETECTION")
        
        alive_ips = self._lightning_fast_alive_scan(all_ips, progress_callback, log_callback)
        alive_time = time.time() - alive_start
        self.stats['timing']['alive_scan_time'] = alive_time
        
        self.log_message(log_callback, f"✅ Alive scan completed: {len(alive_ips)}/{len(all_ips)} alive in {alive_time:.1f}s")
        self.log_message(log_callback, f"📈 Alive scan rate: {len(all_ips)/alive_time:.1f} IPs/second")
        
        if alive_only:
            total_time = time.time() - start_time
            self.stats['timing']['total_time'] = total_time
            self._log_final_statistics(total_time, log_callback)
            return len(alive_ips) > 0
        
        # Phase 2: Fast detailed collection on alive IPs only
        if alive_ips:
            detailed_start = time.time()
            self.log_message(log_callback, f"\n🔍 PHASE 2: FAST DETAILED COLLECTION ({len(alive_ips)} IPs)")
            
            detailed_results = self._fast_detailed_collection(alive_ips, progress_callback, log_callback)
            detailed_time = time.time() - detailed_start
            self.stats['timing']['detailed_scan_time'] = detailed_time
            
            self.log_message(log_callback, f"✅ Detailed collection completed: {len(detailed_results)} devices in {detailed_time:.1f}s")
        
        # Final statistics
        total_time = time.time() - start_time
        self.stats['timing']['total_time'] = total_time
        self._log_final_statistics(total_time, log_callback)
        
        return self.stats['alive_devices'] > 0

    def _lightning_fast_alive_scan(self, ip_list: List[str], progress_callback=None, log_callback=None) -> Set[str]:
        """Ultra-fast alive detection using multiple methods simultaneously"""
        
        alive_ips = set()
        
        # Create batches for maximum speed
        batches = [ip_list[i:i + self.batch_size] for i in range(0, len(ip_list), self.batch_size)]
        
        self.log_message(log_callback, f"📦 Processing {len(batches)} batches of {self.batch_size} IPs")
        
        for batch_num, ip_batch in enumerate(batches, 1):
            batch_start = time.time()
            
            # Multi-threaded alive detection for this batch
            batch_alive = self._multi_threaded_alive_check(ip_batch)
            alive_ips.update(batch_alive)
            
            batch_time = time.time() - batch_start
            rate = len(ip_batch) / batch_time if batch_time > 0 else 0
            
            self.log_message(log_callback, f"🔥 Batch {batch_num}: {len(batch_alive)}/{len(ip_batch)} alive, {rate:.1f} IPs/sec")
            
            # Update progress
            if progress_callback:
                progress = int((batch_num / len(batches)) * 50)  # 50% for alive scan
                progress_callback(progress)
        
        self.stats['alive_devices'] = len(alive_ips)
        self.alive_ips = alive_ips
        return alive_ips

    def _multi_threaded_alive_check(self, ip_batch: List[str]) -> Set[str]:
        """Multi-threaded alive checking with maximum concurrency"""
        
        alive_ips = set()
        
        # Use maximum concurrency for alive checking
        with ThreadPoolExecutor(max_workers=self.max_concurrent_threads) as executor:
            # Submit all IPs for concurrent alive checking
            future_to_ip = {
                executor.submit(self._ultra_fast_alive_check, ip): ip 
                for ip in ip_batch
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_ip, timeout=5):  # 5 second max for entire batch
                ip = future_to_ip[future]
                try:
                    is_alive = future.result(timeout=1)  # 1 second max per IP
                    if is_alive:
                        alive_ips.add(ip)
                        self.stats['method_success']['ping'] += 1
                except Exception:
                    # Silent fail for speed - don't log individual failures
                    pass
        
        return alive_ips

    def _ultra_fast_alive_check(self, ip: str) -> bool:
        """Ultra-fast alive check using multiple methods"""
        
        # Method 1: Fast socket connection test (fastest)
        if self._lightning_socket_test(ip):
            return True
        
        # Method 2: Ultra-fast ping (if socket fails)
        if self._lightning_fast_ping(ip):
            return True
        
        return False

    def _lightning_socket_test(self, ip: str) -> bool:
        """Lightning-fast socket connection test"""
        try:
            # Test common ports quickly
            ports = [80, 443, 22, 23, 135, 445]  # HTTP, HTTPS, SSH, Telnet, RPC, SMB
            
            for port in ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(self.ping_timeout)  # Very fast timeout
                    result = sock.connect_ex((ip, port))
                    sock.close()
                    
                    if result == 0:  # Connection successful
                        self.stats['method_success']['socket'] += 1
                        return True
                except Exception:
                    continue
            
            return False
            
        except Exception:
            return False

    def _lightning_fast_ping(self, ip: str) -> bool:
        """Lightning-fast ping using raw socket (no subprocess)"""
        try:
            # Use raw ICMP socket for maximum speed
            import platform
            
            if platform.system().lower() == 'windows':
                # On Windows, fall back to fast subprocess
                return self._fast_subprocess_ping(ip)
            else:
                # On Linux/Unix, use raw socket
                return self._raw_socket_ping(ip)
                
        except Exception:
            return False

    def _fast_subprocess_ping(self, ip: str) -> bool:
        """Fast subprocess ping optimized for Windows"""
        try:
            import subprocess
            
            # Very aggressive ping settings for speed
            cmd = ['ping', '-n', '1', '-w', str(int(self.ping_timeout * 1000)), ip]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=self.ping_timeout + 0.1,  # Slightly longer timeout
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            return result.returncode == 0 and 'reply from' in result.stdout.lower()
            
        except Exception:
            return False

    def _raw_socket_ping(self, ip: str) -> bool:
        """Raw socket ping for Linux/Unix (fastest method)"""
        try:
            import socket
            import struct
            import select
            
            # Create raw ICMP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            sock.settimeout(self.ping_timeout)
            
            # ICMP packet
            packet_id = os.getpid() & 0xFFFF
            packet = struct.pack('bbHHh', 8, 0, 0, packet_id, 1)
            checksum = self._calculate_checksum(packet)
            packet = struct.pack('bbHHh', 8, 0, checksum, packet_id, 1)
            
            # Send packet
            sock.sendto(packet, (ip, 0))
            
            # Wait for response
            ready = select.select([sock], [], [], self.ping_timeout)
            if ready[0]:
                recv_packet, addr = sock.recvfrom(1024)
                sock.close()
                return addr[0] == ip
            
            sock.close()
            return False
            
        except Exception:
            return False

    def _calculate_checksum(self, packet):
        """Calculate ICMP checksum"""
        countTo = (len(packet) // 2) * 2
        count = 0
        sum = 0
        
        while count < countTo:
            thisVal = packet[count+1] * 256 + packet[count]
            sum = sum + thisVal
            sum = sum & 0xffffffff
            count = count + 2
        
        if countTo < len(packet):
            sum = sum + packet[len(packet) - 1]
            sum = sum & 0xffffffff
        
        sum = (sum >> 16) + (sum & 0xffff)
        sum = sum + (sum >> 16)
        answer = ~sum
        answer = answer & 0xffff
        answer = answer >> 8 | (answer << 8 & 0xff00)
        return answer

    def _fast_detailed_collection(self, alive_ips: Set[str], progress_callback=None, log_callback=None) -> List[Dict]:
        """Fast detailed collection on alive IPs only"""
        
        if not alive_ips:
            return []
        
        results = []
        alive_list = list(alive_ips)
        
        # Process alive IPs in smaller batches for detailed collection
        detail_batch_size = min(50, len(alive_list))  # Smaller batches for detailed work
        batches = [alive_list[i:i + detail_batch_size] for i in range(0, len(alive_list), detail_batch_size)]
        
        for batch_num, ip_batch in enumerate(batches, 1):
            batch_start = time.time()
            
            # Process batch with moderate concurrency (detailed work is heavier)
            batch_results = self._process_alive_ip_batch(ip_batch, log_callback)
            results.extend(batch_results)
            
            batch_time = time.time() - batch_start
            self.log_message(log_callback, f"🔍 Detail Batch {batch_num}: {len(batch_results)}/{len(ip_batch)} collected in {batch_time:.1f}s")
            
            # Update progress (50-100% for detailed collection)
            if progress_callback:
                progress = 50 + int((batch_num / len(batches)) * 50)
                progress_callback(progress)
        
        return results

    def _process_alive_ip_batch(self, ip_batch: List[str], log_callback=None) -> List[Dict]:
        """Process batch of alive IPs for detailed collection"""
        
        batch_results = []
        
        # Use moderate concurrency for detailed collection
        max_detail_threads = min(50, self.max_concurrent_threads // 2)
        
        with ThreadPoolExecutor(max_workers=max_detail_threads) as executor:
            future_to_ip = {
                executor.submit(self._fast_detailed_collection_single, ip): ip 
                for ip in ip_batch
            }
            
            for future in as_completed(future_to_ip, timeout=30):
                ip = future_to_ip[future]
                try:
                    result = future.result(timeout=10)  # 10 second max per detailed collection
                    if result:
                        batch_results.append(result)
                        
                        # Real-time saving
                        if self._save_device_realtime(result, log_callback):
                            self.stats['saved_to_db'] += 1
                        
                        self.stats['data_collected'] += 1
                        
                except Exception:
                    # Log but don't stop for failures
                    pass
        
        return batch_results

    def _fast_detailed_collection_single(self, ip: str) -> Optional[Dict]:
        """Fast detailed collection for a single alive IP"""
        
        try:
            device_data = {
                'ip_address': ip,
                'collection_methods': [],
                'is_alive': True,
                'response_time': 'fast'
            }
            
            # Quick OS detection
            os_info = self._fast_os_detection(ip)
            if os_info:
                device_data.update(os_info)
                self.stats['os_detected'] += 1
            
            # Quick data collection based on OS
            if not self.skip_detailed_collection:
                collection_data = self._fast_data_collection(ip, device_data.get('os_type', 'unknown'))
                if collection_data:
                    device_data.update(collection_data)
            
            # Add metadata
            device_data.update({
                'created_at': datetime.now().isoformat(),
                'data_source': 'Lightning-Fast Collection',
                'collection_timestamp': datetime.now().isoformat(),
                'scan_mode': 'lightning_fast'
            })
            
            return device_data
            
        except Exception:
            return None

    def _fast_os_detection(self, ip: str) -> Optional[Dict]:
        """Fast OS detection with quick methods only"""
        
        # Quick port-based detection (fastest)
        port_result = self._quick_port_detection(ip)
        if port_result:
            return port_result
        
        # Quick NMAP if available
        if NMAP_AVAILABLE:
            nmap_result = self._quick_nmap_detection(ip)
            if nmap_result:
                return nmap_result
        
        return {
            'os_type': 'unknown',
            'os_family': 'unknown',
            'detection_methods': ['port_scan'],
            'detection_confidence': 30
        }

    def _quick_port_detection(self, ip: str) -> Optional[Dict]:
        """Quick port-based OS detection"""
        try:
            # Test key ports very quickly
            windows_ports = [135, 445]  # RPC, SMB
            linux_ports = [22]  # SSH
            web_ports = [80, 443]  # HTTP, HTTPS
            
            open_ports = []
            for port in windows_ports + linux_ports + web_ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.2)  # Very fast
                    result = sock.connect_ex((ip, port))
                    sock.close()
                    
                    if result == 0:
                        open_ports.append(port)
                except Exception:
                    continue
            
            # Quick classification
            if any(port in open_ports for port in windows_ports):
                return {
                    'os_type': 'windows',
                    'os_family': 'windows',
                    'os_details': f'Windows (ports: {open_ports})',
                    'detection_confidence': 70,
                    'detection_methods': ['port_scan']
                }
            elif 22 in open_ports:
                return {
                    'os_type': 'linux',
                    'os_family': 'linux',
                    'os_details': f'Linux/Unix (ports: {open_ports})',
                    'detection_confidence': 70,
                    'detection_methods': ['port_scan']
                }
            elif any(port in open_ports for port in web_ports):
                return {
                    'os_type': 'web_server',
                    'os_family': 'unknown',
                    'os_details': f'Web server (ports: {open_ports})',
                    'detection_confidence': 50,
                    'detection_methods': ['port_scan']
                }
            
            return None
            
        except Exception:
            return None

    def _quick_nmap_detection(self, ip: str) -> Optional[Dict]:
        """Quick NMAP detection with minimal scan"""
        try:
            import nmap
            nm = nmap.PortScanner()
            
            # Ultra-fast scan - minimal ports only
            scan_result = nm.scan(ip, '22,80,135,445', '-T5 --max-retries=1 --host-timeout=2s')
            
            if ip in scan_result['scan']:
                host_info = scan_result['scan'][ip]
                
                if 'osmatch' in host_info and host_info['osmatch']:
                    best_match = host_info['osmatch'][0]
                    os_name = best_match.get('name', '').lower()
                    confidence = int(best_match.get('accuracy', 0))
                    
                    if confidence > 50:
                        # Quick OS family classification
                        if 'windows' in os_name:
                            os_family = 'windows'
                            os_type = 'windows'
                        elif any(x in os_name for x in ['linux', 'ubuntu', 'centos']):
                            os_family = 'linux'
                            os_type = 'linux'
                        else:
                            os_family = 'unknown'
                            os_type = 'unknown'
                        
                        return {
                            'os_type': os_type,
                            'os_family': os_family,
                            'os_details': best_match.get('name', 'unknown'),
                            'detection_confidence': confidence,
                            'detection_methods': ['nmap']
                        }
            
            return None
            
        except Exception:
            return None

    def _fast_data_collection(self, ip: str, os_type: str) -> Optional[Dict]:
        """Fast data collection based on OS type"""
        
        data = {}
        
        try:
            # Quick hostname resolution
            try:
                hostname = socket.gethostbyaddr(ip)[0]
                data['hostname'] = hostname
            except Exception:
                data['hostname'] = f"host-{ip.replace('.', '-')}"
            
            # OS-specific quick collection
            if os_type == 'windows' and WMI_AVAILABLE:
                wmi_data = self._quick_wmi_collection(ip)
                if wmi_data:
                    data.update(wmi_data)
            
            elif os_type == 'linux' and PARAMIKO_AVAILABLE:
                ssh_data = self._quick_ssh_collection(ip)
                if ssh_data:
                    data.update(ssh_data)
            
            return data if data else None
            
        except Exception:
            return None

    def _quick_wmi_collection(self, ip: str) -> Optional[Dict]:
        """Quick WMI collection with minimal timeout"""
        try:
            import wmi
            connection = wmi.WMI(computer=ip, timeout_minutes=0.05)  # 3 second timeout
            
            data = {}
            
            # Get only essential info quickly
            try:
                for system in connection.Win32_ComputerSystem():
                    data.update({
                        'hostname': system.Name,
                        'manufacturer': system.Manufacturer,
                        'model': system.Model
                    })
                    break
            except Exception:
                pass
            
            return data if data else None
            
        except Exception:
            return None

    def _quick_ssh_collection(self, ip: str) -> Optional[Dict]:
        """Quick SSH collection with minimal timeout"""
        try:
            import paramiko
            
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Try very quick connection
            for cred in self.credentials.get('linux', [{'username': 'admin', 'password': 'admin'}]):
                try:
                    ssh.connect(
                        ip,
                        timeout=1,  # Very fast timeout
                        username=cred.get('username', ''),
                        password=cred.get('password', ''),
                        look_for_keys=False
                    )
                    
                    # Get basic info quickly
                    stdin, stdout, stderr = ssh.exec_command('hostname', timeout=1)
                    hostname = stdout.read().decode().strip()
                    ssh.close()
                    
                    return {'hostname': hostname} if hostname else None
                    
                except Exception:
                    continue
            
            return None
            
        except Exception:
            return None

    def _save_device_realtime(self, device_data: Dict, log_callback=None) -> bool:
        """Fast real-time saving"""
        try:
            if self.validator:
                save_result = self.validator.smart_save_device(device_data)
                return save_result.get('success', False)
            return True
        except Exception:
            return False

    def _generate_all_ips(self) -> List[str]:
        """Generate all IPs efficiently"""
        all_ips = []
        
        for target in self.targets:
            try:
                if '/' in target:  # CIDR
                    network = ipaddress.IPv4Network(target, strict=False)
                    ip_list = list(network.hosts())
                    if len(ip_list) > 5000:  # Limit very large networks
                        self.log.warning(f"Large network {target} limited to first 5000 IPs")
                        ip_list = ip_list[:5000]
                    all_ips.extend([str(ip) for ip in ip_list])
                    
                elif '-' in target:  # Range
                    base_ip, range_part = target.rsplit('.', 1)
                    if '-' in range_part:
                        start, end = map(int, range_part.split('-'))
                        for i in range(start, min(end + 1, 255)):
                            all_ips.append(f"{base_ip}.{i}")
                            
                else:  # Single IP
                    ipaddress.IPv4Address(target)
                    all_ips.append(target)
                    
            except Exception as e:
                self.log.error(f"Invalid target '{target}': {e}")
        
        return all_ips

    def _log_final_statistics(self, total_time: float, log_callback=None):
        """Log final performance statistics"""
        
        self.log_message(log_callback, "\n" + "=" * 60)
        self.log_message(log_callback, "⚡ LIGHTNING-FAST COLLECTION STATISTICS")
        self.log_message(log_callback, "=" * 60)
        
        # Performance metrics
        alive_time = self.stats['timing'].get('alive_scan_time', 0)
        detail_time = self.stats['timing'].get('detailed_scan_time', 0)
        
        self.log_message(log_callback, "🚀 SPEED PERFORMANCE:")
        self.log_message(log_callback, f"   Total time: {total_time:.1f}s")
        self.log_message(log_callback, f"   Alive scan: {alive_time:.1f}s")
        self.log_message(log_callback, f"   Detail scan: {detail_time:.1f}s")
        
        if self.stats['total_ips'] > 0:
            total_rate = self.stats['total_ips'] / total_time
            alive_rate = self.stats['total_ips'] / alive_time if alive_time > 0 else 0
            
            self.log_message(log_callback, f"   Overall rate: {total_rate:.1f} IPs/second")
            self.log_message(log_callback, f"   Alive scan rate: {alive_rate:.1f} IPs/second")
        
        self.log_message(log_callback, "\n📊 RESULTS:")
        self.log_message(log_callback, f"   Total IPs scanned: {self.stats['total_ips']}")
        self.log_message(log_callback, f"   Alive devices: {self.stats['alive_devices']}")
        self.log_message(log_callback, f"   OS detected: {self.stats['os_detected']}")
        self.log_message(log_callback, f"   Data collected: {self.stats['data_collected']}")
        self.log_message(log_callback, f"   Saved to database: {self.stats['saved_to_db']}")
        
        success_rate = (self.stats['alive_devices'] / self.stats['total_ips'] * 100) if self.stats['total_ips'] > 0 else 0
        self.log_message(log_callback, f"\n🎯 Success Rate: {success_rate:.1f}% devices alive")

    def log_message(self, callback, message: str):
        """Log message to callback and logger"""
        if callback:
            callback(message)
        clean_message = message.replace('⚡', '').replace('🚀', '').replace('✅', '').replace('🔥', '')
        self.log.info(clean_message.strip())

# Test function for lightning-fast collector
def test_lightning_fast_collector():
    """Test the lightning-fast collector"""
    
    print("⚡ TESTING LIGHTNING-FAST COLLECTOR")
    print("=" * 60)
    
    # Test with small range
    targets = ['127.0.0.1', '192.168.1.1-3']
    credentials = {}
    
    collector = LightningFastCollector(targets, credentials)
    
    def log_callback(message):
        print(message)
    
    def progress_callback(progress):
        print(f"Progress: {progress}%")
    
    # Test alive-only scan for maximum speed
    print("\n🔥 TESTING ALIVE-ONLY SCAN (MAXIMUM SPEED)")
    start_time = time.time()
    success = collector.lightning_fast_subnet_scan(progress_callback, log_callback, alive_only=True)
    test_time = time.time() - start_time
    
    print(f"\n⚡ Lightning-fast test completed in {test_time:.1f}s")
    print(f"🎯 Speed: {collector.stats['total_ips'] / test_time:.1f} IPs/second")
    print(f"✅ Success: {success}")

if __name__ == "__main__":
    test_lightning_fast_collector()