#!/usr/bin/env python3
"""
INTEGRATED CORRECT SCAN STRATEGY IMPLEMENTATION
Fix the Enhanced Ultimate Performance Collector to follow the correct strategy:
1. Scan live devices
2. NMAP OS detection  
3. Windows → WMI + SNMP
4. Linux → SSH + SNMP
5. Other → SSH + SNMP
6. Save with correct device type based on OS
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_ultimate_performance_collector import EnhancedUltimatePerformanceCollector, EnhancedDeviceInfo
import sqlite3
import json

class CorrectStrategyCollector(EnhancedUltimatePerformanceCollector):
    """Enhanced collector with CORRECT comprehensive scan strategy implemented"""
    
    def __init__(self, credentials=None, config=None):
        super().__init__(credentials, config)
        
        # Override configuration for correct strategy
        self.config.update({
            'enable_correct_strategy': True,
            'prioritize_nmap_classification': True,
            'collection_by_os_type': True,
            'hostname_mismatch_resolution': True,
            'duplicate_prevention': True,
            'comprehensive_data_collection': True
        })
        
        self.logger.info("🎯 Correct Strategy Collector Initialized")
        self.logger.info("   Strategy: Live Devices → NMAP OS → OS-based Collection → NMAP Classification")
    
    def _enhanced_classify_device(self, device: EnhancedDeviceInfo) -> str:
        """
        🎯 CORRECT STRATEGY: NMAP-FIRST Classification
        
        STRATEGY HIERARCHY:
        1. NMAP Device Type (PRIMARY - 90% confidence)
        2. NMAP OS Family + Port Analysis (SECONDARY - 70-80%)  
        3. Port-based Analysis (TERTIARY - 50-60%)
        4. Hostname Patterns (FALLBACK - 30-40%)
        """
        
        self.logger.debug(f"🧠 Classifying {device.ip} using CORRECT NMAP-first strategy")
        
        # 1. PRIMARY: Use NMAP Device Type (highest priority)
        nmap_device_type = getattr(device, 'nmap_device_type', None)
        if nmap_device_type and nmap_device_type.strip():
            mapped_type = self._map_nmap_device_type(nmap_device_type)
            if mapped_type:
                self.metrics.classification_successful += 1
                self.logger.debug(f"✅ NMAP Device Type: {device.ip} → {nmap_device_type} → {mapped_type}")
                
                # Store classification details
                device.classification_details = {
                    'method': 'NMAP_DEVICE_TYPE',
                    'nmap_device_type': nmap_device_type,
                    'confidence': 0.90,
                    'reasoning': f"NMAP Device Type: {nmap_device_type}"
                }
                return mapped_type
        
        # 2. SECONDARY: NMAP OS Family with smart analysis
        if device.os_family and device.os_family.lower() != 'unknown':
            os_family = device.os_family.lower()
            
            if 'windows' in os_family:
                device_type = self._classify_windows_device_correct(device)
                if device_type:
                    self.metrics.classification_successful += 1
                    self.logger.debug(f"✅ Windows OS: {device.ip} → {device_type}")
                    return device_type
            
            elif 'linux' in os_family:
                device_type = self._classify_linux_device_correct(device) 
                if device_type:
                    self.metrics.classification_successful += 1
                    self.logger.debug(f"✅ Linux OS: {device.ip} → {device_type}")
                    return device_type
            
            elif any(keyword in os_family for keyword in ['cisco', 'juniper', 'hp', 'network']):
                self.metrics.classification_successful += 1
                self.logger.debug(f"✅ Network OS: {device.ip} → Network Device")
                device.classification_details = {
                    'method': 'NMAP_OS_FAMILY',
                    'os_family': device.os_family,
                    'confidence': 0.80,
                    'reasoning': f"Network OS Family: {device.os_family}"
                }
                return "Network Device"
        
        # 3. TERTIARY: Port-based analysis
        if device.open_ports:
            device_type = self._classify_by_ports_correct(device)
            if device_type != "Unknown":
                self.metrics.classification_successful += 1
                self.logger.debug(f"✅ Port-based: {device.ip} → {device_type}")
                return device_type
        
        # 4. FALLBACK: Hostname patterns
        if device.hostname:
            device_type = self._classify_by_hostname_correct(device)
            if device_type != "Unknown":
                self.metrics.classification_successful += 1
                self.logger.debug(f"✅ Hostname-based: {device.ip} → {device_type}")
                return device_type
        
        # Classification failed - no reliable indicators
        self.metrics.classification_failed += 1
        self.logger.debug(f"❌ Classification failed: {device.ip} - No reliable indicators")
        device.classification_details = {
            'method': 'FAILED',
            'confidence': 0.0,
            'reasoning': 'No NMAP or reliable classification data available'
        }
        return "Unknown"
    
    def _map_nmap_device_type(self, nmap_device_type: str) -> str:
        """Map NMAP device types to our device types"""
        mapping = {
            'Windows Computer': 'Workstation',
            'Windows Server': 'Server',
            'Windows Workstation': 'Workstation',
            'Windows Domain Controller': 'Server',
            'Linux Server': 'Server', 
            'Linux Computer': 'Workstation',
            'Unix Server': 'Server',
            'Unix Computer': 'Workstation',
            'Switch': 'Network Switch',
            'Router': 'Network Router',
            'Firewall': 'Network Firewall',
            'Access Point': 'Network Access Point',
            'Network Device': 'Network Device',
            'Printer': 'Printer',
            'Storage Device': 'Storage Device',
            'Phone': 'VoIP Phone',
            'Camera': 'IP Camera'
        }
        
        return mapping.get(nmap_device_type)
    
    def _classify_windows_device_correct(self, device: EnhancedDeviceInfo) -> str:
        """Correct Windows device classification using NMAP + ports"""
        
        # Check OS version for server keywords
        if device.os_version:
            version_lower = device.os_version.lower()
            server_keywords = ['server', 'datacenter', 'enterprise', 'standard']
            if any(keyword in version_lower for keyword in server_keywords):
                device.classification_details = {
                    'method': 'WINDOWS_OS_VERSION',
                    'os_version': device.os_version,
                    'confidence': 0.80,
                    'reasoning': f"Windows Server edition detected: {device.os_version}"
                }
                return "Server"
        
        # Check for Windows server ports (Active Directory, Domain Services)
        server_ports = [53, 88, 135, 389, 445, 636, 3268, 3269, 5722]
        detected_server_ports = [port for port in device.open_ports if port in server_ports]
        
        if detected_server_ports:
            device.classification_details = {
                'method': 'WINDOWS_SERVER_PORTS',
                'server_ports': detected_server_ports,
                'confidence': 0.75,
                'reasoning': f"Windows server ports detected: {detected_server_ports}"
            }
            return "Server"
        
        # Default to Workstation for Windows
        device.classification_details = {
            'method': 'WINDOWS_DEFAULT',
            'os_family': device.os_family,
            'confidence': 0.70,
            'reasoning': "Windows OS, default classification"
        }
        return "Workstation"
    
    def _classify_linux_device_correct(self, device: EnhancedDeviceInfo) -> str:
        """Correct Linux device classification using NMAP + ports"""
        
        # Check for Linux server ports
        server_ports = [22, 25, 53, 80, 443, 993, 995, 3306, 5432]
        detected_server_ports = [port for port in device.open_ports if port in server_ports]
        
        # More than just SSH indicates server
        if len(detected_server_ports) > 1 or any(port in [25, 53, 80, 443, 3306, 5432] for port in detected_server_ports):
            device.classification_details = {
                'method': 'LINUX_SERVER_PORTS',
                'server_ports': detected_server_ports,
                'confidence': 0.75,
                'reasoning': f"Linux server services detected: {detected_server_ports}"
            }
            return "Server"
        
        # Default to Workstation for Linux
        device.classification_details = {
            'method': 'LINUX_DEFAULT',
            'os_family': device.os_family,
            'confidence': 0.70,
            'reasoning': "Linux OS, default classification"
        }
        return "Workstation"
    
    def _classify_by_ports_correct(self, device: EnhancedDeviceInfo) -> str:
        """Port-based classification as tertiary method"""
        open_ports = set(device.open_ports)
        
        # Web server indicators
        web_ports = {80, 443, 8080, 8443} & open_ports
        if web_ports:
            device.classification_details = {
                'method': 'PORT_WEB_SERVER',
                'web_ports': list(web_ports),
                'confidence': 0.60,
                'reasoning': f"Web server ports detected: {list(web_ports)}"
            }
            return "Server"
        
        # Database server indicators
        db_ports = {3306, 5432, 1433, 1521} & open_ports
        if db_ports:
            device.classification_details = {
                'method': 'PORT_DATABASE_SERVER',
                'database_ports': list(db_ports),
                'confidence': 0.65,
                'reasoning': f"Database ports detected: {list(db_ports)}"
            }
            return "Server"
        
        # Network device indicators
        network_ports = {161, 162, 23} & open_ports
        if network_ports:
            device.classification_details = {
                'method': 'PORT_NETWORK_DEVICE',
                'network_ports': list(network_ports),
                'confidence': 0.55,
                'reasoning': f"Network management ports detected: {list(network_ports)}"
            }
            return "Network Device"
        
        # Printer indicators
        printer_ports = {515, 631, 9100} & open_ports
        if printer_ports:
            device.classification_details = {
                'method': 'PORT_PRINTER',
                'printer_ports': list(printer_ports),
                'confidence': 0.70,
                'reasoning': f"Printer ports detected: {list(printer_ports)}"
            }
            return "Printer"
        
        return "Unknown"
    
    def _classify_by_hostname_correct(self, device: EnhancedDeviceInfo) -> str:
        """Hostname-based classification as last resort"""
        if not device.hostname:
            return "Unknown"
        
        hostname_lower = device.hostname.lower()
        
        # Server patterns
        server_patterns = ['server', 'srv', 'dc-', 'ad-', 'sql', 'web', 'mail', 'dns', 'dhcp']
        for pattern in server_patterns:
            if pattern in hostname_lower:
                device.classification_details = {
                    'method': 'HOSTNAME_SERVER_PATTERN',
                    'hostname': device.hostname,
                    'pattern': pattern,
                    'confidence': 0.40,
                    'reasoning': f"Server hostname pattern: {pattern} in {device.hostname}"
                }
                return "Server"
        
        # Workstation patterns
        workstation_patterns = ['pc-', 'ws-', 'desktop', 'workstation', 'user', 'employee']
        for pattern in workstation_patterns:
            if pattern in hostname_lower:
                device.classification_details = {
                    'method': 'HOSTNAME_WORKSTATION_PATTERN',
                    'hostname': device.hostname,
                    'pattern': pattern,
                    'confidence': 0.35,
                    'reasoning': f"Workstation hostname pattern: {pattern} in {device.hostname}"
                }
                return "Workstation"
        
        # Network patterns
        network_patterns = ['switch', 'router', 'fw-', 'gw-', 'firewall', 'gateway']
        for pattern in network_patterns:
            if pattern in hostname_lower:
                device.classification_details = {
                    'method': 'HOSTNAME_NETWORK_PATTERN',
                    'hostname': device.hostname,
                    'pattern': pattern,
                    'confidence': 0.35,
                    'reasoning': f"Network device hostname pattern: {pattern} in {device.hostname}"
                }
                return "Network Device"
        
        return "Unknown"

def test_correct_strategy():
    """Test the correct strategy implementation"""
    print("🧪 TESTING CORRECT SCAN STRATEGY")
    print("=" * 60)
    
    # Initialize the correct strategy collector
    collector = CorrectStrategyCollector()
    
    # Test classification on existing database devices
    conn = sqlite3.connect('assets.db')
    cursor = conn.cursor()
    
    # Get devices with NMAP data for testing
    cursor.execute('''
        SELECT hostname, ip_address, nmap_os_family, nmap_device_type, 
               device_type, open_ports
        FROM assets 
        WHERE nmap_os_family IS NOT NULL 
        ORDER BY last_seen DESC 
        LIMIT 10
    ''')
    
    devices = cursor.fetchall()
    
    print(f"Testing classification on {len(devices)} devices with NMAP data:")
    print()
    
    reclassifications = []
    
    for hostname, ip, nmap_os, nmap_dtype, current_type, ports_json in devices:
        # Create device object for testing
        device = EnhancedDeviceInfo(ip=ip)
        device.hostname = hostname
        device.os_family = nmap_os or ""
        device.nmap_device_type = nmap_dtype or ""
        
        try:
            device.open_ports = json.loads(ports_json) if ports_json else []
        except:
            device.open_ports = []
        
        # Test classification
        suggested_type = collector._enhanced_classify_device(device)
        
        print(f"📍 {hostname} ({ip})")
        print(f"   Current: {current_type}")
        print(f"   NMAP OS: {nmap_os} / Device Type: {nmap_dtype}")
        print(f"   Suggested: {suggested_type}")
        
        if hasattr(device, 'classification_details'):
            details = device.classification_details
            print(f"   Method: {details.get('method', 'Unknown')}")
            print(f"   Confidence: {details.get('confidence', 0):.2f}")
            print(f"   Reasoning: {details.get('reasoning', 'None')}")
        
        if current_type != suggested_type:
            print(f"   ⚠️  WOULD RECLASSIFY: {current_type} → {suggested_type}")
            reclassifications.append((hostname, current_type, suggested_type))
        else:
            print("   ✅ Classification matches")
        
        print()
    
    print("📊 RESULTS:")
    print(f"   Total tested: {len(devices)}")
    print(f"   Would reclassify: {len(reclassifications)}")
    print(f"   Classification accuracy: {((len(devices)-len(reclassifications))/len(devices))*100:.1f}%")
    
    if reclassifications:
        print("\n🔄 Devices that would be reclassified:")
        for hostname, old, new in reclassifications:
            print(f"   • {hostname}: {old} → {new}")
    
    conn.close()

def verify_scan_strategy_compliance():
    """Verify the scan process follows the correct strategy"""
    print("\n🔍 SCAN STRATEGY COMPLIANCE VERIFICATION")
    print("=" * 60)
    
    conn = sqlite3.connect('assets.db')
    cursor = conn.cursor()
    
    # 1. Check NMAP OS detection coverage
    cursor.execute('SELECT COUNT(*) FROM assets')
    total_devices = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM assets WHERE nmap_os_family IS NOT NULL')
    nmap_coverage = cursor.fetchone()[0]
    
    print("1️⃣ NMAP OS Detection Coverage:")
    print(f"   Total devices: {total_devices}")
    print(f"   With NMAP OS data: {nmap_coverage} ({(nmap_coverage/total_devices)*100:.1f}%)")
    
    # 2. Check collection method by OS type
    print("\n2️⃣ Collection Method by OS Type:")
    
    cursor.execute('''
        SELECT nmap_os_family, 
               AVG(CASE WHEN wmi_collection_status = "success" THEN 1 ELSE 0 END) * 100 as wmi_rate,
               AVG(CASE WHEN ssh_collection_status = "success" THEN 1 ELSE 0 END) * 100 as ssh_rate,
               AVG(CASE WHEN snmp_collection_status = "success" THEN 1 ELSE 0 END) * 100 as snmp_rate,
               COUNT(*) as device_count
        FROM assets 
        WHERE nmap_os_family IS NOT NULL
        GROUP BY nmap_os_family
    ''')
    
    collection_stats = cursor.fetchall()
    
    for os_family, wmi_rate, ssh_rate, snmp_rate, count in collection_stats:
        print(f"   {os_family} ({count} devices):")
        if os_family == 'Windows':
            print("      ✅ Should use WMI + SNMP")
            print(f"      📊 WMI Success: {wmi_rate:.1f}%")
            print(f"      📊 SNMP Success: {snmp_rate:.1f}%")
        else:
            print("      ✅ Should use SSH + SNMP")
            print(f"      📊 SSH Success: {ssh_rate:.1f}%")
            print(f"      📊 SNMP Success: {snmp_rate:.1f}%")
    
    # 3. Check device type distribution
    print("\n3️⃣ Device Type Distribution (NMAP-based):")
    
    cursor.execute('''
        SELECT device_type, nmap_device_type, COUNT(*) 
        FROM assets 
        WHERE nmap_device_type IS NOT NULL
        GROUP BY device_type, nmap_device_type
        ORDER BY COUNT(*) DESC
    ''')
    
    type_distribution = cursor.fetchall()
    
    for device_type, nmap_dtype, count in type_distribution:
        compliance = "✅" if (
            (nmap_dtype == "Windows Computer" and device_type == "Workstation") or
            (nmap_dtype == "Windows Server" and device_type == "Server")
        ) else "⚠️"
        
        print(f"   {compliance} {device_type} ← {nmap_dtype}: {count} devices")
    
    # 4. Check hostname consistency  
    print("\n4️⃣ Hostname Feature Verification:")
    
    cursor.execute('''
        SELECT COUNT(*) as mismatches
        FROM assets a1
        WHERE hostname != computer_name 
        AND hostname IS NOT NULL 
        AND computer_name IS NOT NULL
        AND computer_name != ""
    ''')
    
    hostname_mismatches = cursor.fetchone()[0]
    print(f"   Hostname mismatches: {hostname_mismatches} devices")
    
    if hostname_mismatches > 0:
        print("   ⚠️ Some devices have hostname inconsistencies")
    else:
        print("   ✅ Hostname consistency maintained")
    
    conn.close()
    
    print("\n✅ STRATEGY COMPLIANCE CHECK COMPLETE")

if __name__ == "__main__":
    test_correct_strategy()
    verify_scan_strategy_compliance()