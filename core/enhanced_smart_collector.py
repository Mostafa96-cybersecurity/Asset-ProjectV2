# -*- coding: utf-8 -*-
"""
Enhanced Smart Device Collector with Advanced Error Prevention
--------------------------------------------------------------
- Comprehensive network validation and error recovery
- Multi-level duplicate detection and prevention  
- Intelligent device categorization with conflict resolution
- Performance monitoring and quality assurance
- Robust error handling and retry mechanisms
"""

import ipaddress
import subprocess
import socket
import re
import logging
import time
import threading
from typing import Dict, List, Optional, Set, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
from datetime import datetime

from collectors.wmi_collector import collect_windows_wmi
from collectors.ssh_collector import collect_linux_or_esxi_ssh
from core.advanced_duplicate_manager import DuplicateManager, DataValidator, ErrorRecovery

log = logging.getLogger(__name__)


class EnhancedSmartCollector:
    def __init__(self, progress_callback=None):
        self.progress_callback = progress_callback
        
        # Advanced features
        self.duplicate_manager = DuplicateManager()
        self.data_validator = DataValidator()
        self.error_recovery = ErrorRecovery()
        
        # Performance and reliability tracking
        self.collection_stats = {
            'devices_scanned': 0,
            'devices_alive': 0,
            'devices_collected': 0,
            'duplicates_found': 0,
            'errors_recovered': 0,
            'validation_failures': 0,
            'network_timeouts': 0,
            'successful_categorizations': 0
        }
        
        # Network validation settings
        self.max_ping_timeout = 2000  # ms
        self.max_concurrent_scans = 30  # Reduced to prevent network overload
        self.retry_failed_devices = True
        self.max_retries = 2
        
        # Device categorization rules
        self.server_indicators = {
            'hostname_patterns': [
                r'.*server.*', r'.*srv.*', r'.*dc\d*$', r'.*ad\d*$', 
                r'.*sql.*', r'.*db.*', r'.*exchange.*', r'.*share.*',
                r'.*web.*', r'.*iis.*', r'.*mail.*', r'.*file.*'
            ],
            'domain_roles': ['domain_controller', 'file_server', 'web_server', 'database_server'],
            'server_ports': [53, 88, 135, 139, 389, 445, 636, 3268, 3269, 5985, 5986],
            'service_ports': [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 1433, 3306, 3389]
        }
        
        # Device validation rules
        self.device_validators = {
            'ip_address': self._validate_ip_address,
            'hostname': self._validate_hostname,
            'mac_address': self._validate_mac_address,
            'serial_number': self._validate_serial_number
        }
    
    def scan_alive_devices_enhanced(self, targets: List[str], max_workers: int = None) -> List[Dict]:
        """
        Enhanced ping scan with validation and error recovery
        Returns detailed information about alive devices
        """
        if max_workers is None:
            max_workers = min(self.max_concurrent_scans, len(targets))
        
        log.info(f"Starting enhanced ping scan for {len(targets)} targets (max_workers={max_workers})...")
        
        alive_devices = []
        failed_devices = []
        
        def enhanced_ping(ip: str) -> Optional[Dict]:
            try:
                # Validate IP first
                is_valid, validated_ip = self.data_validator.validate_ip_address(ip)
                if not is_valid:
                    log.warning(f"Invalid IP address: {ip}")
                    return None
                
                # Enhanced ping with detailed response
                start_time = time.time()
                result = subprocess.run(
                    ["ping", "-n", "1", "-w", str(self.max_ping_timeout), validated_ip],
                    capture_output=True,
                    timeout=3,
                    text=True
                )
                
                response_time = (time.time() - start_time) * 1000
                
                if result.returncode == 0:
                    # Extract additional info from ping response
                    ping_info = self._parse_ping_response(result.stdout)
                    
                    device_info = {
                        'ip_address': validated_ip,
                        'response_time_ms': round(response_time, 2),
                        'ping_success': True,
                        'ttl': ping_info.get('ttl'),
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    # Try to resolve hostname
                    try:
                        hostname = socket.gethostbyaddr(validated_ip)[0]
                        device_info['hostname'] = hostname
                    except Exception:
                        device_info['hostname'] = None
                    
                    return device_info
                    
            except subprocess.TimeoutExpired:
                self.collection_stats['network_timeouts'] += 1
                log.debug(f"Ping timeout for {ip}")
            except Exception as e:
                log.debug(f"Ping failed for {ip}: {e}")
                
            return None
        
        # Execute ping scan with progress tracking
        self.collection_stats['devices_scanned'] = len(targets)
        processed = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(enhanced_ping, ip): ip for ip in targets}
            
            for future in as_completed(futures):
                ip = futures[future]
                result = future.result()
                processed += 1
                
                if result:
                    alive_devices.append(result)
                    self.collection_stats['devices_alive'] += 1
                else:
                    failed_devices.append(ip)
                
                # Update progress
                if self.progress_callback:
                    progress = int((processed / len(targets)) * 100)
                    self.progress_callback(f"Ping scan: {processed}/{len(targets)} ({progress}%)")
        
        # Retry failed devices if enabled
        if self.retry_failed_devices and failed_devices:
            log.info(f"Retrying {len(failed_devices)} failed devices...")
            
            retry_results = []
            with ThreadPoolExecutor(max_workers=min(10, len(failed_devices))) as executor:
                retry_futures = {executor.submit(enhanced_ping, ip): ip for ip in failed_devices}
                
                for future in as_completed(retry_futures):
                    result = future.result()
                    if result:
                        retry_results.append(result)
                        self.collection_stats['errors_recovered'] += 1
            
            alive_devices.extend(retry_results)
            log.info(f"Recovered {len(retry_results)} devices on retry")
        
        log.info(f"Ping scan completed: {len(alive_devices)} alive devices found")
        return alive_devices
    
    def _parse_ping_response(self, ping_output: str) -> Dict:
        """Extract additional information from ping response"""
        info = {}
        
        # Extract TTL
        ttl_match = re.search(r'TTL=(\d+)', ping_output, re.IGNORECASE)
        if ttl_match:
            info['ttl'] = int(ttl_match.group(1))
        
        # Extract response time
        time_match = re.search(r'time[<=](\d+)ms', ping_output, re.IGNORECASE)
        if time_match:
            info['ping_time'] = int(time_match.group(1))
        
        return info
    
    def detect_os_type_enhanced(self, device_info: Dict) -> Tuple[str, float]:
        """
        Enhanced OS detection with confidence scoring
        Returns: (os_type, confidence_score)
        """
        ip = device_info['ip_address']
        hostname = device_info.get('hostname', '')
        ttl = device_info.get('ttl')
        
        os_indicators = {
            'windows': 0.0,
            'linux': 0.0,
            'unknown': 0.0
        }
        
        # TTL-based detection (most reliable)
        if ttl:
            if ttl >= 120 and ttl <= 128:
                os_indicators['windows'] += 0.7
            elif ttl >= 60 and ttl <= 65:
                os_indicators['linux'] += 0.7
            else:
                os_indicators['unknown'] += 0.3
        
        # Hostname-based detection
        if hostname:
            hostname_lower = hostname.lower()
            
            windows_patterns = [
                r'.*-pc$', r'.*-ws\d*$', r'.*-desktop.*', r'.*-laptop.*',
                r'win.*', r'.*server.*', r'.*dc\d*$', r'.*ad\d*$'
            ]
            
            linux_patterns = [
                r'.*\.local$', r'ubuntu.*', r'centos.*', r'redhat.*',
                r'debian.*', r'.*-vm$', r'.*-lnx.*'
            ]
            
            for pattern in windows_patterns:
                if re.match(pattern, hostname_lower):
                    os_indicators['windows'] += 0.5
                    break
            
            for pattern in linux_patterns:
                if re.match(pattern, hostname_lower):
                    os_indicators['linux'] += 0.5
                    break
        
        # Port-based detection (additional validation)
        try:
            windows_ports = [135, 139, 445, 3389]  # RPC, SMB, RDP
            linux_ports = [22]  # SSH
            
            for port in windows_ports:
                if self._test_port(ip, port, timeout=1):
                    os_indicators['windows'] += 0.3
                    break
            
            for port in linux_ports:
                if self._test_port(ip, port, timeout=1):
                    os_indicators['linux'] += 0.3
                    break
                    
        except Exception as e:
            log.debug(f"Port detection failed for {ip}: {e}")
        
        # Determine best match
        max_score = max(os_indicators.values())
        if max_score < 0.3:
            return 'unknown', max_score
        
        detected_os = max(os_indicators, key=os_indicators.get)
        confidence = os_indicators[detected_os]
        
        log.debug(f"OS detection for {ip}: {detected_os} (confidence: {confidence:.2f})")
        return detected_os, confidence
    
    def _test_port(self, ip: str, port: int, timeout: float = 1.0) -> bool:
        """Test if a specific port is open"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                result = sock.connect_ex((ip, port))
                return result == 0
        except Exception:
            return False
    
    def categorize_device_enhanced(self, device_data: Dict, os_type: str, confidence: float) -> str:
        """
        Enhanced device categorization with server detection
        """
        if os_type == 'linux':
            return 'Linux Devices'
        
        if os_type != 'windows':
            # Try to detect based on available data
            hostname = device_data.get('Hostname', '').lower()
            
            # Check for Windows indicators
            if any(indicator in hostname for indicator in ['pc', 'desktop', 'laptop', 'workstation']):
                os_type = 'windows'
            elif self._test_port(device_data.get('IP Address', ''), 22):
                return 'Linux Devices'
        
        if os_type == 'windows':
            # Determine if it's a server or workstation
            if self._is_windows_server(device_data):
                self.collection_stats['successful_categorizations'] += 1
                return 'Windows Server'
            else:
                self.collection_stats['successful_categorizations'] += 1
                return 'Windows Devices'
        
        # Default fallback
        return 'Windows Devices'
    
    def _is_windows_server(self, device_data: Dict) -> bool:
        """Enhanced server detection logic"""
        hostname = device_data.get('Hostname', '').lower()
        ip_address = device_data.get('IP Address', '')
        
        # Check hostname patterns
        for pattern in self.server_indicators['hostname_patterns']:
            if re.match(pattern, hostname):
                log.debug(f"Server detected by hostname pattern: {hostname}")
                return True
        
        # Check for server roles in collected data
        device_model = device_data.get('Device Model', '').lower()
        if 'server' in device_model:
            log.debug(f"Server detected by device model: {device_model}")
            return True
        
        # Check OS information
        os_info = device_data.get('OS', '').lower()
        if 'server' in os_info:
            log.debug(f"Server detected by OS: {os_info}")
            return True
        
        # Check for server ports (more comprehensive)
        try:
            server_port_count = 0
            for port in self.server_indicators['server_ports']:
                if self._test_port(ip_address, port, timeout=0.5):
                    server_port_count += 1
                    if server_port_count >= 2:  # Multiple server ports = likely server
                        log.debug(f"Server detected by multiple open server ports: {ip_address}")
                        return True
        except Exception as e:
            log.debug(f"Port check failed for server detection: {e}")
        
        return False
    
    def collect_device_data_enhanced(self, device_info: Dict, os_type: str, 
                                   ssh_credentials: Dict = None) -> Optional[Dict]:
        """
        Enhanced device data collection with validation and error recovery
        """
        ip_address = device_info['ip_address']
        
        try:
            device_data = None
            
            if os_type == 'windows':
                device_data = self.error_recovery.retry_with_backoff(
                    self._collect_windows_data, ip_address
                )
            elif os_type == 'linux' and ssh_credentials:
                device_data = self.error_recovery.retry_with_backoff(
                    self._collect_linux_data, ip_address, ssh_credentials
                )
            
            if device_data:
                # Validate collected data
                is_valid, sanitized_data, errors = self.data_validator.sanitize_device_data(device_data)
                
                if not is_valid:
                    log.warning(f"Data validation failed for {ip_address}: {errors}")
                    self.collection_stats['validation_failures'] += 1
                    return None
                
                # Check for duplicates
                is_duplicate, existing_info = self.duplicate_manager.check_duplicate(
                    sanitized_data, self.categorize_device_enhanced(sanitized_data, os_type, 1.0)
                )
                
                if is_duplicate:
                    log.info(f"Duplicate device detected: {ip_address}, merging data")
                    sanitized_data = self.duplicate_manager.merge_device_data(sanitized_data, existing_info)
                    self.collection_stats['duplicates_found'] += 1
                
                # Add metadata
                sanitized_data['Last Updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                sanitized_data['Data Source'] = f'Smart Scan ({os_type})'
                sanitized_data['Collection Quality'] = 'Validated'
                
                self.collection_stats['devices_collected'] += 1
                return sanitized_data
                
        except Exception as e:
            log.error(f"Enhanced data collection failed for {ip_address}: {e}")
            
        return None
    
    def _collect_windows_data(self, ip_address: str) -> Dict:
        """Collect Windows device data with validation"""
        data = collect_windows_wmi(ip_address)
        
        if not data or not data.get('hostname'):
            raise Exception(f"Failed to collect valid Windows data for {ip_address}")
        
        return data
    
    def _collect_linux_data(self, ip_address: str, ssh_credentials: Dict) -> Dict:
        """Collect Linux device data with validation"""
        data = collect_linux_or_esxi_ssh(
            ip_address,
            username=ssh_credentials.get('username', 'root'),
            password=ssh_credentials.get('password', ''),
            pkey=ssh_credentials.get('key_path')
        )
        
        if not data or not data.get('hostname'):
            raise Exception(f"Failed to collect valid Linux data for {ip_address}")
        
        return data
    
    # Validation methods
    def _validate_ip_address(self, value: str) -> bool:
        try:
            ipaddress.IPv4Address(value)
            return True
        except Exception:
            return False
    
    def _validate_hostname(self, value: str) -> bool:
        if not value or len(value) > 253:
            return False
        return re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$', value) is not None
    
    def _validate_mac_address(self, value: str) -> bool:
        if not value:
            return True  # MAC is optional
        return re.match(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', value) is not None
    
    def _validate_serial_number(self, value: str) -> bool:
        if not value:
            return True  # Serial is optional
        return len(value) >= 3 and not value.lower() in ['unknown', 'n/a', 'not available']
    
    def get_collection_stats(self) -> Dict:
        """Return detailed collection statistics"""
        stats = self.collection_stats.copy()
        
        if stats['devices_scanned'] > 0:
            stats['success_rate'] = round((stats['devices_alive'] / stats['devices_scanned']) * 100, 2)
            stats['collection_rate'] = round((stats['devices_collected'] / stats['devices_alive']) * 100, 2) if stats['devices_alive'] > 0 else 0
        
        return stats