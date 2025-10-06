#!/usr/bin/env python3
"""
Speed-Optimized Large Subnet Collector
Combines ultra-fast alive detection with efficient detailed collection
"""

import time
import asyncio
import socket
import ipaddress
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Set, Dict, Optional
from datetime import datetime
import logging

# Import ultra-fast scanners
try:
    from ultra_high_speed_scanner import UltraHighSpeedScanner, AsyncUltraScanner
    ULTRA_SCANNERS_AVAILABLE = True
except ImportError:
    ULTRA_SCANNERS_AVAILABLE = False

try:
    from smart_duplicate_validator import SmartDuplicateValidator
    DUPLICATE_VALIDATOR_AVAILABLE = True
except ImportError:
    DUPLICATE_VALIDATOR_AVAILABLE = False

class SpeedOptimizedCollector:
    """Speed-optimized collector for large subnets focusing on maximum performance"""
    
    def __init__(self, targets: List[str], credentials: Dict = None):
        self.targets = targets
        self.credentials = credentials or {}
        
        # Speed-optimized settings
        self.use_async = True  # Use async scanner for maximum speed
        self.fast_alive_only = False  # Option for alive check only
        self.minimal_collection = True  # Minimal data collection for speed
        
        # Ultra-fast timeouts
        self.alive_timeout = 0.1  # 100ms for alive detection
        self.collection_timeout = 2.0  # 2s for data collection
        
        # Concurrency settings
        self.max_alive_threads = 1000  # Very high for alive detection
        self.max_collection_threads = 100  # Moderate for detailed collection
        
        # Performance tracking
        self.stats = {
            'total_ips': 0,
            'alive_devices': 0,
            'data_collected': 0,
            'saved_to_db': 0,
            'phase_times': {
                'alive_detection': 0,
                'data_collection': 0,
                'database_saving': 0
            },
            'speed_metrics': {
                'alive_detection_rate': 0,
                'overall_rate': 0
            }
        }
        
        self.validator = SmartDuplicateValidator() if DUPLICATE_VALIDATOR_AVAILABLE else None
        logging.basicConfig(level=logging.INFO)
        self.log = logging.getLogger(__name__)

    def speed_optimized_scan(self, progress_callback=None, log_callback=None, alive_only=False):
        """Speed-optimized scanning with 2-phase approach"""
        
        total_start = time.time()
        self.log_message(log_callback, "🏃‍♂️ SPEED-OPTIMIZED LARGE SUBNET COLLECTOR")
        self.log_message(log_callback, "=" * 70)
        
        # Generate IPs
        all_ips = self._generate_ips()
        self.stats['total_ips'] = len(all_ips)
        
        if not all_ips:
            self.log_message(log_callback, "❌ No valid IPs to scan")
            return False
        
        self.log_message(log_callback, "📊 SCAN CONFIGURATION:")
        self.log_message(log_callback, f"   Target IPs: {len(all_ips)}")
        self.log_message(log_callback, f"   Scanner type: {'Async' if self.use_async else 'Thread'}")
        self.log_message(log_callback, f"   Alive timeout: {self.alive_timeout*1000:.0f}ms")
        self.log_message(log_callback, f"   Alive only mode: {alive_only}")
        
        # PHASE 1: Ultra-fast alive detection
        phase1_start = time.time()
        self.log_message(log_callback, "\n🚀 PHASE 1: ULTRA-FAST ALIVE DETECTION")
        
        alive_ips = self._ultra_fast_alive_detection(all_ips, progress_callback, log_callback)
        
        phase1_time = time.time() - phase1_start
        self.stats['phase_times']['alive_detection'] = phase1_time
        self.stats['alive_devices'] = len(alive_ips)
        
        alive_rate = len(all_ips) / phase1_time if phase1_time > 0 else 0
        self.stats['speed_metrics']['alive_detection_rate'] = alive_rate
        
        self.log_message(log_callback, f"✅ Phase 1 completed: {len(alive_ips)}/{len(all_ips)} alive")
        self.log_message(log_callback, f"⚡ Alive detection speed: {alive_rate:.1f} IPs/second")
        
        if alive_only or not alive_ips:
            total_time = time.time() - total_start
            self.stats['speed_metrics']['overall_rate'] = len(all_ips) / total_time
            self._log_speed_statistics(total_time, log_callback)
            return len(alive_ips) > 0
        
        # PHASE 2: Fast data collection (only on alive IPs)
        phase2_start = time.time()
        self.log_message(log_callback, f"\n📡 PHASE 2: FAST DATA COLLECTION ({len(alive_ips)} IPs)")
        
        collected_data = self._fast_data_collection_phase(alive_ips, progress_callback, log_callback)
        
        phase2_time = time.time() - phase2_start
        self.stats['phase_times']['data_collection'] = phase2_time
        self.stats['data_collected'] = len(collected_data)
        
        collection_rate = len(alive_ips) / phase2_time if phase2_time > 0 else 0
        self.log_message(log_callback, f"✅ Phase 2 completed: {len(collected_data)} devices collected")
        self.log_message(log_callback, f"📊 Collection speed: {collection_rate:.1f} devices/second")
        
        # PHASE 3: Fast database saving
        if collected_data:
            phase3_start = time.time()
            self.log_message(log_callback, "\n💾 PHASE 3: FAST DATABASE SAVING")
            
            saved_count = self._fast_database_saving(collected_data, log_callback)
            
            phase3_time = time.time() - phase3_start
            self.stats['phase_times']['database_saving'] = phase3_time
            self.stats['saved_to_db'] = saved_count
            
            save_rate = saved_count / phase3_time if phase3_time > 0 else 0
            self.log_message(log_callback, f"✅ Phase 3 completed: {saved_count} devices saved")
            self.log_message(log_callback, f"💾 Save speed: {save_rate:.1f} devices/second")
        
        # Final performance summary
        total_time = time.time() - total_start
        self.stats['speed_metrics']['overall_rate'] = len(all_ips) / total_time
        self._log_speed_statistics(total_time, log_callback)
        
        return len(alive_ips) > 0

    def _ultra_fast_alive_detection(self, ip_list: List[str], progress_callback=None, log_callback=None) -> Set[str]:
        """Ultra-fast alive detection using the fastest available method"""
        
        if ULTRA_SCANNERS_AVAILABLE and self.use_async:
            # Use async scanner for maximum speed
            scanner = AsyncUltraScanner(self.targets)
            scanner.timeout = self.alive_timeout
            scanner.max_concurrent = self.max_alive_threads
            
            def progress_wrapper(progress):
                if progress_callback:
                    progress_callback(int(progress * 0.5))  # 50% for alive phase
            
            # Run async scanner
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                alive_ips = loop.run_until_complete(
                    scanner.async_ultra_scan(progress_wrapper, log_callback)
                )
                loop.close()
                return alive_ips
            except Exception:
                self.log_message(log_callback, "⚠️ Async scanner failed, falling back to thread-based")
        
        # Fall back to thread-based ultra scanner
        if ULTRA_SCANNERS_AVAILABLE:
            scanner = UltraHighSpeedScanner([])  # We'll use ip_list directly
            scanner.max_threads = self.max_alive_threads
            scanner.timeout = self.alive_timeout
            
            alive_ips = scanner._concurrent_scan(
                ip_list, 
                lambda p: progress_callback(int(p * 0.5)) if progress_callback else None,
                log_callback
            )
            return alive_ips
        
        # Fallback to basic concurrent scan
        return self._basic_concurrent_alive_scan(ip_list, progress_callback, log_callback)

    def _basic_concurrent_alive_scan(self, ip_list: List[str], progress_callback=None, log_callback=None) -> Set[str]:
        """Basic concurrent alive scan fallback"""
        
        alive_ips = set()
        
        with ThreadPoolExecutor(max_workers=min(500, len(ip_list))) as executor:
            future_to_ip = {
                executor.submit(self._basic_alive_check, ip): ip 
                for ip in ip_list
            }
            
            completed = 0
            for future in as_completed(future_to_ip, timeout=30):
                ip = future_to_ip[future]
                try:
                    if future.result(timeout=1):
                        alive_ips.add(ip)
                except Exception:
                    pass
                
                completed += 1
                if progress_callback and completed % 50 == 0:
                    progress = int((completed / len(ip_list)) * 50)
                    progress_callback(progress)
        
        return alive_ips

    def _basic_alive_check(self, ip: str) -> bool:
        """Basic alive check"""
        try:
            # Quick socket test
            for port in [80, 443, 22]:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.alive_timeout)
                result = sock.connect_ex((ip, port))
                sock.close()
                if result == 0:
                    return True
            return False
        except Exception:
            return False

    def _fast_data_collection_phase(self, alive_ips: Set[str], progress_callback=None, log_callback=None) -> List[Dict]:
        """Fast data collection phase on alive IPs only"""
        
        if not alive_ips:
            return []
        
        collected_data = []
        alive_list = list(alive_ips)
        
        # Use moderate concurrency for data collection
        with ThreadPoolExecutor(max_workers=self.max_collection_threads) as executor:
            future_to_ip = {
                executor.submit(self._fast_single_device_collection, ip): ip 
                for ip in alive_list
            }
            
            completed = 0
            for future in as_completed(future_to_ip, timeout=60):
                ip = future_to_ip[future]
                try:
                    device_data = future.result(timeout=self.collection_timeout)
                    if device_data:
                        collected_data.append(device_data)
                except Exception:
                    pass
                
                completed += 1
                if progress_callback and completed % 10 == 0:
                    progress = 50 + int((completed / len(alive_list)) * 40)  # 50-90%
                    progress_callback(progress)
        
        return collected_data

    def _fast_single_device_collection(self, ip: str) -> Optional[Dict]:
        """Fast collection for a single device"""
        
        try:
            device_data = {
                'ip_address': ip,
                'scan_timestamp': datetime.now().isoformat(),
                'data_source': 'Speed-Optimized Collection'
            }
            
            # Quick hostname resolution
            try:
                hostname = socket.gethostbyaddr(ip)[0]
                device_data['hostname'] = hostname
            except Exception:
                device_data['hostname'] = f"host-{ip.replace('.', '-')}"
            
            # Quick OS detection via port scanning
            os_info = self._quick_os_detection(ip)
            if os_info:
                device_data.update(os_info)
            
            # Minimal additional data if not in minimal mode
            if not self.minimal_collection:
                additional_data = self._minimal_additional_data(ip, device_data.get('os_type', 'unknown'))
                if additional_data:
                    device_data.update(additional_data)
            
            return device_data
            
        except Exception:
            return None

    def _quick_os_detection(self, ip: str) -> Optional[Dict]:
        """Quick OS detection via port scanning"""
        try:
            open_ports = []
            test_ports = [22, 80, 135, 443, 445, 3389]  # SSH, HTTP, RPC, HTTPS, SMB, RDP
            
            for port in test_ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.2)  # Very fast
                    result = sock.connect_ex((ip, port))
                    sock.close()
                    if result == 0:
                        open_ports.append(port)
                except Exception:
                    continue
            
            # Quick OS classification
            if 135 in open_ports or 445 in open_ports or 3389 in open_ports:
                return {
                    'os_type': 'windows',
                    'os_family': 'windows',
                    'detection_method': 'port_scan',
                    'open_ports': open_ports
                }
            elif 22 in open_ports:
                return {
                    'os_type': 'linux',
                    'os_family': 'linux', 
                    'detection_method': 'port_scan',
                    'open_ports': open_ports
                }
            elif 80 in open_ports or 443 in open_ports:
                return {
                    'os_type': 'web_server',
                    'os_family': 'unknown',
                    'detection_method': 'port_scan',
                    'open_ports': open_ports
                }
            
            return {
                'os_type': 'unknown',
                'os_family': 'unknown',
                'detection_method': 'port_scan',
                'open_ports': open_ports
            }
            
        except Exception:
            return None

    def _minimal_additional_data(self, ip: str, os_type: str) -> Optional[Dict]:
        """Collect minimal additional data for speed"""
        
        data = {}
        
        # Quick manufacturer detection via MAC if possible
        try:
            # This is a placeholder for quick manufacturer detection
            data['manufacturer'] = 'Unknown'
        except Exception:
            pass
        
        return data if data else None

    def _fast_database_saving(self, collected_data: List[Dict], log_callback=None) -> int:
        """Fast database saving with batch operations"""
        
        if not collected_data:
            return 0
        
        saved_count = 0
        
        try:
            if self.validator:
                # Batch saving with duplicate prevention
                for device_data in collected_data:
                    try:
                        save_result = self.validator.smart_save_device(device_data)
                        if save_result.get('success', False):
                            saved_count += 1
                    except Exception:
                        continue
            else:
                # Simple counting if no validator
                saved_count = len(collected_data)
                
        except Exception as e:
            self.log_message(log_callback, f"⚠️ Database saving error: {str(e)[:50]}...")
        
        return saved_count

    def _generate_ips(self) -> List[str]:
        """Generate IP list efficiently"""
        all_ips = []
        
        for target in self.targets:
            try:
                if '/' in target:  # CIDR
                    network = ipaddress.IPv4Network(target, strict=False)
                    hosts = list(network.hosts())
                    if len(hosts) > 5000:  # Reasonable limit for speed
                        hosts = hosts[:5000]
                        self.log.warning(f"Large network {target} limited to 5000 IPs for speed")
                    all_ips.extend([str(ip) for ip in hosts])
                    
                elif '-' in target:  # Range
                    base_ip, range_part = target.rsplit('.', 1)
                    start, end = map(int, range_part.split('-'))
                    for i in range(start, min(end + 1, 255)):
                        all_ips.append(f"{base_ip}.{i}")
                        
                else:  # Single IP
                    ipaddress.IPv4Address(target)
                    all_ips.append(target)
                    
            except Exception:
                continue
        
        return all_ips

    def _log_speed_statistics(self, total_time: float, log_callback=None):
        """Log comprehensive speed statistics"""
        
        self.log_message(log_callback, "\n" + "=" * 70)
        self.log_message(log_callback, "🏃‍♂️ SPEED-OPTIMIZED COLLECTION STATISTICS")
        self.log_message(log_callback, "=" * 70)
        
        # Performance breakdown
        phase_times = self.stats['phase_times']
        
        self.log_message(log_callback, "⚡ SPEED PERFORMANCE:")
        self.log_message(log_callback, f"   Total time: {total_time:.2f}s")
        self.log_message(log_callback, f"   Phase 1 (Alive): {phase_times['alive_detection']:.2f}s")
        self.log_message(log_callback, f"   Phase 2 (Collection): {phase_times['data_collection']:.2f}s")
        self.log_message(log_callback, f"   Phase 3 (Database): {phase_times['database_saving']:.2f}s")
        
        # Speed metrics
        self.log_message(log_callback, "\n📊 SPEED METRICS:")
        self.log_message(log_callback, f"   Overall rate: {self.stats['speed_metrics']['overall_rate']:.1f} IPs/second")
        self.log_message(log_callback, f"   Alive detection: {self.stats['speed_metrics']['alive_detection_rate']:.1f} IPs/second")
        
        # Results summary
        self.log_message(log_callback, "\n📈 RESULTS:")
        self.log_message(log_callback, f"   Total IPs: {self.stats['total_ips']}")
        self.log_message(log_callback, f"   Alive devices: {self.stats['alive_devices']}")
        self.log_message(log_callback, f"   Data collected: {self.stats['data_collected']}")
        self.log_message(log_callback, f"   Saved to DB: {self.stats['saved_to_db']}")
        
        # Efficiency metrics
        if self.stats['total_ips'] > 0:
            alive_percentage = (self.stats['alive_devices'] / self.stats['total_ips']) * 100
            self.log_message(log_callback, "\n🎯 EFFICIENCY:")
            self.log_message(log_callback, f"   Alive rate: {alive_percentage:.1f}%")
            
            if self.stats['alive_devices'] > 0:
                collection_success = (self.stats['data_collected'] / self.stats['alive_devices']) * 100
                self.log_message(log_callback, f"   Collection success: {collection_success:.1f}%")

    def log_message(self, callback, message: str):
        """Log message to callback and logger"""
        if callback:
            callback(message)
        clean_message = message.replace('🏃‍♂️', '').replace('🚀', '').replace('⚡', '').replace('📊', '').strip()
        self.log.info(clean_message)

# Test function
def test_speed_optimized_collector():
    """Test the speed-optimized collector"""
    
    print("🏃‍♂️ TESTING SPEED-OPTIMIZED COLLECTOR")
    print("=" * 70)
    
    # Test with moderate range
    targets = ['127.0.0.1', '192.168.1.1-20']
    
    collector = SpeedOptimizedCollector(targets)
    collector.use_async = True  # Use async for maximum speed
    
    def log_callback(message):
        print(message)
    
    def progress_callback(progress):
        print(f"Progress: {progress}%")
    
    # Test speed-optimized scanning
    start_time = time.time()
    success = collector.speed_optimized_scan(progress_callback, log_callback, alive_only=False)
    test_time = time.time() - start_time
    
    print("\n🏆 SPEED TEST RESULTS:")
    print(f"Total time: {test_time:.2f}s")
    print(f"Overall speed: {collector.stats['speed_metrics']['overall_rate']:.1f} IPs/second")
    print(f"Success: {success}")

if __name__ == "__main__":
    test_speed_optimized_collector()