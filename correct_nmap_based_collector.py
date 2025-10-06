#!/usr/bin/env python3
"""
CORRECT NMAP-FIRST ENHANCED COLLECTOR
Fixed to follow proper NMAP-based classification strategy
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_ultimate_performance_collector import EnhancedUltimatePerformanceCollector, EnhancedDeviceInfo
import json
import sqlite3

class CorrectNmapBasedCollector(EnhancedUltimatePerformanceCollector):
    """Enhanced collector with CORRECT NMAP-first classification strategy"""
    
    def __init__(self, credentials=None, config=None):
        super().__init__(credentials, config)
        
        # NMAP Device Type mapping (PRIMARY classification source)
        self.nmap_device_mapping = {
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
        
        # OS Family to Device Type mapping (SECONDARY classification)
        self.os_family_rules = {
            'Windows': {
                'server_keywords': ['server', 'datacenter', 'enterprise'],
                'server_ports': [53, 88, 135, 389, 445, 636, 3268, 3269, 5722],
                'default': 'Workstation'
            },
            'Linux': {
                'server_ports': [22, 25, 53, 80, 443, 993, 995, 3306, 5432],
                'default': 'Workstation'
            }
        }
    
    def _enhanced_classify_device(self, device: EnhancedDeviceInfo) -> str:
        """
        🎯 CORRECT NMAP-FIRST Classification Strategy
        
        Priority order:
        1. NMAP Device Type (90% confidence) - PRIMARY
        2. NMAP OS Family + analysis (70-80% confidence) - SECONDARY  
        3. Port-based analysis (50-60% confidence) - TERTIARY
        4. Hostname patterns (30-40% confidence) - FALLBACK
        """
        
        classification_reason = []
        
        # 1. PRIMARY: NMAP Device Type (highest priority)
        if hasattr(device, 'nmap_device_type') and device.nmap_device_type:
            mapped_type = self.nmap_device_mapping.get(device.nmap_device_type)
            if mapped_type:
                self.metrics.classification_successful += 1
                self.logger.debug(f"✅ NMAP Device Type classification for {device.ip}: {device.nmap_device_type} → {mapped_type}")
                return mapped_type
        
        # Check if we have NMAP data stored differently
        nmap_device_type = getattr(device, 'nmap_device_type', None)
        if not nmap_device_type:
            # Try to get from additional data
            if hasattr(device, 'additional_data') and device.additional_data:
                nmap_device_type = device.additional_data.get('nmap_device_type')
        
        if nmap_device_type:
            mapped_type = self.nmap_device_mapping.get(nmap_device_type)
            if mapped_type:
                self.metrics.classification_successful += 1
                self.logger.debug(f"✅ NMAP Device Type classification for {device.ip}: {nmap_device_type} → {mapped_type}")
                return mapped_type
        
        # 2. SECONDARY: NMAP OS Family + Smart Analysis
        if device.os_family and device.os_family.lower() != 'unknown':
            os_family = device.os_family.lower()
            
            if 'windows' in os_family:
                device_type = self._classify_windows_by_nmap(device)
                if device_type:
                    self.metrics.classification_successful += 1
                    self.logger.debug(f"✅ Windows OS classification for {device.ip}: {device_type}")
                    return device_type
            
            elif 'linux' in os_family:
                device_type = self._classify_linux_by_nmap(device)
                if device_type:
                    self.metrics.classification_successful += 1
                    self.logger.debug(f"✅ Linux OS classification for {device.ip}: {device_type}")
                    return device_type
            
            elif any(keyword in os_family for keyword in ['cisco', 'juniper', 'hp', 'network']):
                self.metrics.classification_successful += 1
                self.logger.debug(f"✅ Network OS classification for {device.ip}: Network Device")
                return "Network Device"
        
        # 3. TERTIARY: Port-based analysis (original logic as fallback)
        device_type = self._classify_by_ports(device)
        if device_type and device_type != "Unknown":
            self.metrics.classification_successful += 1
            self.logger.debug(f"✅ Port-based classification for {device.ip}: {device_type}")
            return device_type
        
        # 4. FALLBACK: Hostname patterns (last resort)
        device_type = self._classify_by_hostname(device)
        if device_type and device_type != "Unknown":
            self.metrics.classification_successful += 1
            self.logger.debug(f"✅ Hostname-based classification for {device.ip}: {device_type}")
            return device_type
        
        # Classification failed
        self.metrics.classification_failed += 1
        self.logger.debug(f"❌ Classification failed for {device.ip}: No reliable indicators found")
        return "Unknown"
    
    def _classify_windows_by_nmap(self, device: EnhancedDeviceInfo) -> str:
        """Classify Windows device using NMAP OS data and port analysis"""
        
        # Check OS version for server indicators
        if device.os_version:
            version_lower = device.os_version.lower()
            if any(keyword in version_lower for keyword in self.os_family_rules['Windows']['server_keywords']):
                return "Server"
        
        # Check for server ports
        server_ports = set(device.open_ports) & set(self.os_family_rules['Windows']['server_ports'])
        if server_ports:
            return "Server"
        
        # Default to workstation for Windows
        return self.os_family_rules['Windows']['default']
    
    def _classify_linux_by_nmap(self, device: EnhancedDeviceInfo) -> str:
        """Classify Linux device using NMAP OS data and port analysis"""
        
        # Check for server ports
        server_ports = set(device.open_ports) & set(self.os_family_rules['Linux']['server_ports'])
        if server_ports:
            return "Server"
        
        # Default to workstation for Linux
        return self.os_family_rules['Linux']['default']
    
    def _classify_by_ports(self, device: EnhancedDeviceInfo) -> str:
        """Port-based classification as tertiary method"""
        open_ports = set(device.open_ports)
        
        # Web server indicators
        if any(port in open_ports for port in [80, 443, 8080, 8443]):
            return "Server"
        
        # Database server indicators
        if any(port in open_ports for port in [3306, 5432, 1433, 1521]):
            return "Server"
        
        # Network device indicators
        if any(port in open_ports for port in [161, 162, 23]):
            return "Network Device"
        
        # Printer indicators
        if any(port in open_ports for port in [515, 631, 9100]):
            return "Printer"
        
        return "Unknown"
    
    def _classify_by_hostname(self, device: EnhancedDeviceInfo) -> str:
        """Hostname-based classification as fallback method"""
        if not device.hostname:
            return "Unknown"
        
        hostname_lower = device.hostname.lower()
        
        # Server patterns
        if any(pattern in hostname_lower for pattern in ['server', 'srv', 'dc-', 'sql', 'web', 'mail']):
            return "Server"
        
        # Workstation patterns  
        if any(pattern in hostname_lower for pattern in ['pc-', 'ws-', 'desktop', 'workstation']):
            return "Workstation"
        
        # Network patterns
        if any(pattern in hostname_lower for pattern in ['switch', 'router', 'fw-', 'gw-']):
            return "Network Device"
        
        return "Unknown"

def fix_existing_nmap_misclassifications():
    """Fix devices that are misclassified despite having correct NMAP data"""
    print("🔧 FIXING NMAP-BASED MISCLASSIFICATIONS...")
    print("=" * 60)
    
    conn = sqlite3.connect('assets.db')
    cursor = conn.cursor()
    
    # Find devices where NMAP says "Windows Server" but device_type is "Workstation"
    cursor.execute('''
        SELECT id, hostname, device_type, nmap_device_type, nmap_os_family
        FROM assets 
        WHERE nmap_device_type = "Windows Server" AND device_type = "Workstation"
    ''')
    
    server_misclassified = cursor.fetchall()
    
    print(f"Found {len(server_misclassified)} devices misclassified as Workstation when NMAP says Windows Server:")
    
    fixes_applied = 0
    for device_id, hostname, current_type, nmap_dtype, nmap_os in server_misclassified:
        print(f"   📍 {hostname}: {current_type} → Server (NMAP: {nmap_dtype})")
        
        # Fix the classification
        cursor.execute('''
            UPDATE assets 
            SET device_type = "Server",
                notes = "Corrected based on NMAP Device Type: Windows Server"
            WHERE id = ?
        ''', (device_id,))
        fixes_applied += 1
    
    # Find any other NMAP mismatches
    cursor.execute('''
        SELECT id, hostname, device_type, nmap_device_type, nmap_os_family
        FROM assets 
        WHERE nmap_device_type IS NOT NULL 
        AND nmap_device_type != ""
        AND (
            (nmap_device_type = "Windows Computer" AND device_type NOT IN ("Workstation", "Desktop")) OR
            (nmap_device_type = "Windows Server" AND device_type != "Server")
        )
    ''')
    
    other_mismatches = cursor.fetchall()
    
    print(f"\nFound {len(other_mismatches)} other NMAP mismatches:")
    
    for device_id, hostname, current_type, nmap_dtype, nmap_os in other_mismatches:
        if nmap_dtype == "Windows Computer" and current_type not in ["Workstation", "Desktop"]:
            correct_type = "Workstation"
            print(f"   📍 {hostname}: {current_type} → {correct_type} (NMAP: {nmap_dtype})")
            
            cursor.execute('''
                UPDATE assets 
                SET device_type = ?,
                    notes = "Corrected based on NMAP Device Type: Windows Computer"
                WHERE id = ?
            ''', (correct_type, device_id))
            fixes_applied += 1
    
    conn.commit()
    
    print(f"\n✅ Applied {fixes_applied} corrections based on NMAP data")
    
    # Show final statistics
    cursor.execute('SELECT device_type, COUNT(*) FROM assets GROUP BY device_type ORDER BY COUNT(*) DESC')
    final_stats = cursor.fetchall()
    
    print("\n📊 UPDATED DEVICE TYPE DISTRIBUTION:")
    total_devices = sum(count for _, count in final_stats)
    for device_type, count in final_stats:
        percentage = (count / total_devices) * 100
        print(f"   {device_type}: {count} devices ({percentage:.1f}%)")
    
    conn.close()

if __name__ == "__main__":
    fix_existing_nmap_misclassifications()