#!/usr/bin/env python3
"""
Enhanced Hierarchical Collection Strategy
========================================
Implements intelligent OS-based collection strategy:

1. Network Scan (NMAP) → Detect alive devices
2. OS Detection (NMAP) → Determine device type  
3. Hierarchical Collection:
   - Windows: WMI → SNMP (fallback)
   - Linux: SSH → SNMP (fallback)
   - Other: SNMP → SSH (fallback)
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

log = logging.getLogger(__name__)

@dataclass
class CollectionResult:
    """Result of data collection attempt"""
    success: bool
    method: str
    data: Dict[str, Any]
    confidence: float
    error: Optional[str] = None
    collection_time: float = 0.0

@dataclass
class DeviceProfile:
    """Device profile from OS detection"""
    ip: str
    os_family: str  # Windows, Linux, Network, Other, Unknown
    device_type: str  # Windows Server, Linux Server, Network Device, etc.
    confidence: int  # 0-100
    open_ports: List[int]
    detection_method: str  # NMAP, Port-based
    alive: bool = True

class HierarchicalCollector:
    """Enhanced collector implementing hierarchical collection strategy"""
    
    def __init__(self, win_creds=None, linux_creds=None, snmp_communities=None):
        self.win_creds = win_creds or []
        self.linux_creds = linux_creds or []
        self.snmp_communities = snmp_communities or ['public', 'private']
        
    def collect_device_data(self, device_profile: DeviceProfile) -> CollectionResult:
        """
        Main collection method implementing hierarchical strategy
        
        Strategy:
        - Windows: WMI → SNMP
        - Linux: SSH → SNMP  
        - Other: SNMP → SSH
        """
        start_time = time.time()
        
        log.info(f"🎯 Starting hierarchical collection for {device_profile.ip}")
        log.info(f"   OS: {device_profile.os_family} ({device_profile.confidence}% confidence)")
        log.info(f"   Type: {device_profile.device_type}")
        
        # Strategy selection based on OS
        if device_profile.os_family == 'Windows':
            result = self._collect_windows_hierarchy(device_profile)
        elif device_profile.os_family == 'Linux':
            result = self._collect_linux_hierarchy(device_profile)
        else:
            result = self._collect_other_hierarchy(device_profile)
        
        result.collection_time = time.time() - start_time
        
        log.info(f"📊 Collection completed for {device_profile.ip}: {result.method} "
                f"({'SUCCESS' if result.success else 'FAILED'}) in {result.collection_time:.2f}s")
        
        return result
    
    def _collect_windows_hierarchy(self, profile: DeviceProfile) -> CollectionResult:
        """Windows: WMI → SNMP fallback"""
        log.info(f"🪟 Windows collection strategy for {profile.ip}")
        
        # Method 1: WMI Collection
        log.info("   1️⃣  Attempting WMI collection...")
        wmi_result = self._try_wmi_collection(profile)
        if wmi_result.success:
            log.info("   ✅ WMI collection successful!")
            return wmi_result
        else:
            log.warning(f"   ❌ WMI failed: {wmi_result.error}")
        
        # Method 2: SNMP Fallback
        log.info("   2️⃣  Attempting SNMP fallback...")
        snmp_result = self._try_snmp_collection(profile)
        if snmp_result.success:
            log.info("   ✅ SNMP fallback successful!")
            return snmp_result
        else:
            log.warning(f"   ❌ SNMP fallback failed: {snmp_result.error}")
        
        # Return best attempt
        return wmi_result if wmi_result.confidence > snmp_result.confidence else snmp_result
    
    def _collect_linux_hierarchy(self, profile: DeviceProfile) -> CollectionResult:
        """Linux: SSH → SNMP fallback"""
        log.info(f"🐧 Linux collection strategy for {profile.ip}")
        
        # Method 1: SSH Collection
        log.info("   1️⃣  Attempting SSH collection...")
        ssh_result = self._try_ssh_collection(profile)
        if ssh_result.success:
            log.info("   ✅ SSH collection successful!")
            return ssh_result
        else:
            log.warning(f"   ❌ SSH failed: {ssh_result.error}")
        
        # Method 2: SNMP Fallback
        log.info("   2️⃣  Attempting SNMP fallback...")
        snmp_result = self._try_snmp_collection(profile)
        if snmp_result.success:
            log.info("   ✅ SNMP fallback successful!")
            return snmp_result
        else:
            log.warning(f"   ❌ SNMP fallback failed: {snmp_result.error}")
        
        # Return best attempt
        return ssh_result if ssh_result.confidence > snmp_result.confidence else snmp_result
    
    def _collect_other_hierarchy(self, profile: DeviceProfile) -> CollectionResult:
        """Other devices: SNMP → SSH fallback"""
        log.info(f"🔧 Other device collection strategy for {profile.ip}")
        
        # Method 1: SNMP Collection
        log.info("   1️⃣  Attempting SNMP collection...")
        snmp_result = self._try_snmp_collection(profile)
        if snmp_result.success:
            log.info("   ✅ SNMP collection successful!")
            return snmp_result
        else:
            log.warning(f"   ❌ SNMP failed: {snmp_result.error}")
        
        # Method 2: SSH Fallback
        log.info("   2️⃣  Attempting SSH fallback...")
        ssh_result = self._try_ssh_collection(profile)
        if ssh_result.success:
            log.info("   ✅ SSH fallback successful!")
            return ssh_result
        else:
            log.warning(f"   ❌ SSH fallback failed: {ssh_result.error}")
        
        # Method 3: HTTP/HTTPS for web devices
        if 80 in profile.open_ports or 443 in profile.open_ports:
            log.info("   3️⃣  Attempting HTTP collection...")
            http_result = self._try_http_collection(profile)
            if http_result.success:
                log.info("   ✅ HTTP collection successful!")
                return http_result
        
        # Return best attempt
        best_result = snmp_result
        if ssh_result.confidence > best_result.confidence:
            best_result = ssh_result
            
        return best_result
    
    def _try_wmi_collection(self, profile: DeviceProfile) -> CollectionResult:
        """Attempt WMI collection with credentials"""
        from ultra_fast_collector import _collect_windows_standalone
        
        # Try each credential set
        for i, creds in enumerate(self.win_creds):
            try:
                username = creds.get('username', '')
                password = creds.get('password', '')
                
                log.debug(f"      Trying WMI credentials {i+1}/{len(self.win_creds)}")
                
                data = _collect_windows_standalone(profile.ip, username, password)
                
                if data and data.get('wmi_collection_status') == 'Success':
                    # Add OS detection info to data
                    data.update({
                        'detection_method': profile.detection_method,
                        'os_detection_confidence': profile.confidence,
                        'nmap_os_family': profile.os_family,
                        'nmap_device_type': profile.device_type,
                        'collection_strategy': 'Windows Hierarchical (WMI Primary)'
                    })
                    
                    return CollectionResult(
                        success=True,
                        method='WMI',
                        data=data,
                        confidence=0.9,
                        error=None
                    )
                    
            except Exception as e:
                log.debug(f"      WMI credential {i+1} failed: {e}")
                continue
        
        return CollectionResult(
            success=False,
            method='WMI', 
            data={},
            confidence=0.0,
            error="All WMI credentials failed or no credentials provided"
        )
    
    def _try_ssh_collection(self, profile: DeviceProfile) -> CollectionResult:
        """Attempt SSH collection with credentials"""
        from ultra_fast_collector import _collect_ssh_standalone
        
        # Try each credential set
        for i, creds in enumerate(self.linux_creds):
            try:
                username = creds.get('username', '')
                password = creds.get('password', '')
                
                log.debug(f"      Trying SSH credentials {i+1}/{len(self.linux_creds)}")
                
                data = _collect_ssh_standalone(profile.ip, username, password)
                
                if data and data.get('wmi_collection_status') != 'SSH Failed':
                    # Add OS detection info to data
                    data.update({
                        'detection_method': profile.detection_method,
                        'os_detection_confidence': profile.confidence,
                        'nmap_os_family': profile.os_family,
                        'nmap_device_type': profile.device_type,
                        'collection_strategy': 'Linux Hierarchical (SSH Primary)'
                    })
                    
                    return CollectionResult(
                        success=True,
                        method='SSH',
                        data=data,
                        confidence=0.8,
                        error=None
                    )
                    
            except Exception as e:
                log.debug(f"      SSH credential {i+1} failed: {e}")
                continue
        
        return CollectionResult(
            success=False,
            method='SSH',
            data={},
            confidence=0.0,
            error="All SSH credentials failed or no credentials provided"
        )
    
    def _try_snmp_collection(self, profile: DeviceProfile) -> CollectionResult:
        """Attempt SNMP collection with communities"""
        from ultra_fast_collector import _collect_snmp_standalone
        
        # Try each community string
        for community in self.snmp_communities:
            try:
                log.debug(f"      Trying SNMP community: {community}")
                
                data = _collect_snmp_standalone(profile.ip, [community])
                
                if data:
                    # Add OS detection info to data
                    data.update({
                        'detection_method': profile.detection_method,
                        'os_detection_confidence': profile.confidence,
                        'nmap_os_family': profile.os_family,
                        'nmap_device_type': profile.device_type,
                        'collection_strategy': 'SNMP Hierarchical',
                        'snmp_community': community
                    })
                    
                    return CollectionResult(
                        success=True,
                        method='SNMP',
                        data=data,
                        confidence=0.6,
                        error=None
                    )
                    
            except Exception as e:
                log.debug(f"      SNMP community {community} failed: {e}")
                continue
        
        return CollectionResult(
            success=False,
            method='SNMP',
            data={},
            confidence=0.0,
            error="All SNMP communities failed"
        )
    
    def _try_http_collection(self, profile: DeviceProfile) -> CollectionResult:
        """Attempt HTTP collection for web devices"""
        from ultra_fast_collector import _collect_http_standalone
        
        try:
            data = _collect_http_standalone(profile.ip)
            
            if data:
                # Add OS detection info to data
                data.update({
                    'detection_method': profile.detection_method,
                    'os_detection_confidence': profile.confidence,
                    'nmap_os_family': profile.os_family,
                    'nmap_device_type': profile.device_type,
                    'collection_strategy': 'HTTP Hierarchical'
                })
                
                return CollectionResult(
                    success=True,
                    method='HTTP',
                    data=data,
                    confidence=0.4,
                    error=None
                )
                
        except Exception as e:
            log.debug(f"      HTTP collection failed: {e}")
        
        return CollectionResult(
            success=False,
            method='HTTP',
            data={},
            confidence=0.0,
            error="HTTP collection failed"
        )

def enhanced_network_discovery_and_collection(
    targets: List[str],
    win_creds: Optional[List[Dict]] = None,
    linux_creds: Optional[List[Dict]] = None,
    snmp_communities: Optional[List[str]] = None,
    max_workers: int = 10
) -> List[CollectionResult]:
    """
    Complete enhanced strategy implementation:
    1. Network discovery
    2. OS detection
    3. Hierarchical collection
    """
    
    log.info("🚀 Starting Enhanced Hierarchical Collection Strategy")
    log.info(f"   Targets: {len(targets)}")
    log.info("   Strategy: Network Scan → OS Detection → Hierarchical Collection")
    
    # Step 1: Network Discovery & OS Detection
    log.info("🔍 Step 1: Network Discovery & OS Detection")
    device_profiles = []
    
    from ultra_fast_collector import _nmap_os_detection, _quick_port_check
    
    for target in targets:
        log.info(f"   Detecting: {target}")
        
        # Quick alive check
        if not _quick_port_check(target, 80, 0.5) and not _quick_port_check(target, 22, 0.5) and not _quick_port_check(target, 135, 0.5):
            log.warning(f"   {target}: Not responding to common ports")
            continue
        
        # OS Detection
        os_info = _nmap_os_detection(target)
        
        # Get open ports
        open_ports = []
        common_ports = [22, 80, 135, 161, 443, 445, 3389]
        for port in common_ports:
            if _quick_port_check(target, port, 0.3):
                open_ports.append(port)
        
        profile = DeviceProfile(
            ip=target,
            os_family=os_info['os_family'],
            device_type=os_info['device_type'],
            confidence=int(os_info['confidence']),
            open_ports=open_ports,
            detection_method=os_info.get('detection_method', 'Port-based')
        )
        
        device_profiles.append(profile)
        log.info(f"   ✅ {target}: {profile.os_family} ({profile.confidence}% confidence)")
    
    log.info(f"📊 Discovery complete: {len(device_profiles)} alive devices detected")
    
    # Step 2: Hierarchical Collection
    log.info("📡 Step 2: Hierarchical Data Collection")
    
    collector = HierarchicalCollector(
        win_creds=win_creds,
        linux_creds=linux_creds, 
        snmp_communities=snmp_communities
    )
    
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_profile = {
            executor.submit(collector.collect_device_data, profile): profile
            for profile in device_profiles
        }
        
        for future in as_completed(future_to_profile):
            profile = future_to_profile[future]
            try:
                result = future.result()
                results.append(result)
                
                status = "✅ SUCCESS" if result.success else "❌ FAILED"
                log.info(f"   {profile.ip}: {status} via {result.method}")
                
            except Exception as e:
                log.error(f"   {profile.ip}: Exception during collection: {e}")
                results.append(CollectionResult(
                    success=False,
                    method='Exception',
                    data={},
                    confidence=0.0,
                    error=str(e)
                ))
    
    # Summary
    successful = sum(1 for r in results if r.success)
    log.info("🎉 Collection Strategy Complete:")
    log.info(f"   Total Devices: {len(results)}")
    log.info(f"   Successful: {successful}/{len(results)} ({successful/len(results)*100:.1f}%)")
    
    return results

if __name__ == "__main__":
    # Test the enhanced strategy
    test_targets = ['127.0.0.1', '10.0.21.2']
    
    # Example credentials (replace with real ones)
    win_creds = [
        {'username': '', 'password': ''},  # Current user
        {'username': 'admin', 'password': 'admin'},
        {'username': 'administrator', 'password': ''}
    ]
    
    linux_creds = [
        {'username': 'root', 'password': ''},
        {'username': 'admin', 'password': 'admin'},
        {'username': 'user', 'password': 'user'}
    ]
    
    snmp_communities = ['public', 'private', 'community']
    
    results = enhanced_network_discovery_and_collection(
        targets=test_targets,
        win_creds=win_creds,
        linux_creds=linux_creds,
        snmp_communities=snmp_communities
    )
    
    print("\n📊 STRATEGY RESULTS:")
    for result in results:
        print(f"  {result.data.get('ip_address', 'Unknown')}: {result.method} ({'SUCCESS' if result.success else 'FAILED'})")