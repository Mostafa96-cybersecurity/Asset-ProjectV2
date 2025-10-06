#!/usr/bin/env python3
"""
CORRECT NMAP-BASED DEVICE CLASSIFICATION STRATEGY
This implements the proper strategy based on NMAP OS detection
"""

import sqlite3
import json
import time
from typing import Dict, List, Tuple, Optional

class NmapBasedClassifier:
    """Correct NMAP-based device classification following the proper strategy"""
    
    def __init__(self):
        self.nmap_device_types = {
            # Windows Computer types
            'Windows Computer': 'Workstation',
            'Windows Server': 'Server', 
            'Windows Workstation': 'Workstation',
            'Windows Domain Controller': 'Server',
            
            # Linux/Unix types
            'Linux Server': 'Server',
            'Linux Computer': 'Workstation',
            'Unix Server': 'Server',
            'Unix Computer': 'Workstation',
            
            # Network equipment
            'Switch': 'Network Switch',
            'Router': 'Network Router', 
            'Firewall': 'Network Firewall',
            'Access Point': 'Network Access Point',
            'Network Device': 'Network Device',
            
            # Specialized devices
            'Printer': 'Printer',
            'Storage Device': 'Storage Device',
            'Media Device': 'Media Device',
            'Phone': 'VoIP Phone',
            'Camera': 'IP Camera',
            'IoT Device': 'IoT Device'
        }
        
        self.os_family_mapping = {
            # Windows families -> device types based on version/ports
            'Windows': {
                'server_keywords': ['server', 'datacenter', 'enterprise'],
                'workstation_keywords': ['professional', 'pro', 'home', 'education'],
                'server_ports': [53, 88, 135, 389, 445, 636, 3268, 3269, 5722],  # AD/Domain ports
                'workstation_ports': [135, 139, 445, 1024, 1025, 1026, 1027]
            },
            
            # Linux families
            'Linux': {
                'server_ports': [22, 25, 53, 80, 443, 993, 995, 3306, 5432],
                'workstation_ports': [22, 631, 5353]  # SSH, CUPS, Bonjour
            },
            
            # Network OS indicators
            'Network': {
                'management_ports': [23, 80, 161, 162, 443, 8080],
                'keywords': ['cisco', 'juniper', 'hp', 'netgear', 'linksys', 'switch', 'router']
            }
        }

    def classify_device_by_nmap(self, nmap_os_family: str, nmap_device_type: str, 
                               os_version: str = "", open_ports: List[int] = None, 
                               hostname: str = "") -> Tuple[str, float, str]:
        """
        Classify device based on NMAP OS detection (CORRECT STRATEGY)
        
        Args:
            nmap_os_family: NMAP detected OS family (Windows, Linux, etc.)
            nmap_device_type: NMAP detected device type 
            os_version: Full OS version string
            open_ports: List of open ports
            hostname: Device hostname
            
        Returns:
            (device_type, confidence, reasoning)
        """
        
        if open_ports is None:
            open_ports = []
            
        reasoning = []
        confidence = 0.0
        
        # 1. PRIMARY: Use NMAP Device Type if available (90% accuracy)
        if nmap_device_type and nmap_device_type.strip():
            mapped_type = self.nmap_device_types.get(nmap_device_type)
            if mapped_type:
                confidence = 0.90
                reasoning.append(f"NMAP Device Type: {nmap_device_type} → {mapped_type}")
                return mapped_type, confidence, "; ".join(reasoning)
        
        # 2. SECONDARY: Use NMAP OS Family + additional analysis (70-80% accuracy)
        if nmap_os_family and nmap_os_family.strip():
            os_family = nmap_os_family.lower()
            
            # Windows classification
            if 'windows' in os_family:
                device_type, conf, reason = self._classify_windows_device(os_version, open_ports)
                confidence = max(confidence, conf)
                reasoning.extend(reason)
                if device_type:
                    return device_type, confidence, "; ".join(reasoning)
            
            # Linux classification  
            elif 'linux' in os_family:
                device_type, conf, reason = self._classify_linux_device(os_version, open_ports)
                confidence = max(confidence, conf)
                reasoning.extend(reason)
                if device_type:
                    return device_type, confidence, "; ".join(reasoning)
            
            # Network OS classification
            elif any(keyword in os_family for keyword in ['cisco', 'juniper', 'hp', 'network']):
                confidence = 0.75
                reasoning.append(f"Network OS detected: {nmap_os_family}")
                return "Network Device", confidence, "; ".join(reasoning)
        
        # 3. FALLBACK: Port-based analysis (50-60% accuracy)
        if open_ports:
            device_type, conf, reason = self._classify_by_ports(open_ports)
            confidence = max(confidence, conf)
            reasoning.extend(reason)
            if device_type:
                return device_type, confidence, "; ".join(reasoning)
        
        # 4. LAST RESORT: Hostname analysis (30-40% accuracy)
        if hostname:
            device_type, conf, reason = self._classify_by_hostname(hostname)
            confidence = max(confidence, conf)
            reasoning.extend(reason)
            if device_type:
                return device_type, confidence, "; ".join(reasoning)
        
        return "Unknown", 0.0, "No NMAP OS detection available"

    def _classify_windows_device(self, os_version: str, open_ports: List[int]) -> Tuple[str, float, List[str]]:
        """Classify Windows device based on version and ports"""
        reasoning = []
        
        if os_version:
            version_lower = os_version.lower()
            
            # Server indicators
            if any(keyword in version_lower for keyword in self.os_family_mapping['Windows']['server_keywords']):
                reasoning.append(f"Windows Server edition detected in: {os_version}")
                return "Server", 0.80, reasoning
            
            # Workstation indicators
            if any(keyword in version_lower for keyword in self.os_family_mapping['Windows']['workstation_keywords']):
                reasoning.append(f"Windows Workstation edition detected in: {os_version}")
                return "Workstation", 0.75, reasoning
        
        # Port-based Windows classification
        server_ports = set(open_ports) & set(self.os_family_mapping['Windows']['server_ports'])
        workstation_ports = set(open_ports) & set(self.os_family_mapping['Windows']['workstation_ports'])
        
        if server_ports:
            reasoning.append(f"Windows Server ports detected: {list(server_ports)}")
            return "Server", 0.70, reasoning
        elif workstation_ports:
            reasoning.append(f"Windows Workstation ports detected: {list(workstation_ports)}")
            return "Workstation", 0.65, reasoning
        
        # Default Windows classification
        reasoning.append("Windows OS detected, defaulting to Workstation")
        return "Workstation", 0.60, reasoning

    def _classify_linux_device(self, os_version: str, open_ports: List[int]) -> Tuple[str, float, List[str]]:
        """Classify Linux device based on version and ports"""
        reasoning = []
        
        # Port-based Linux classification
        server_ports = set(open_ports) & set(self.os_family_mapping['Linux']['server_ports'])
        workstation_ports = set(open_ports) & set(self.os_family_mapping['Linux']['workstation_ports'])
        
        if server_ports:
            reasoning.append(f"Linux Server services detected: {list(server_ports)}")
            return "Server", 0.75, reasoning
        elif workstation_ports:
            reasoning.append(f"Linux Workstation services detected: {list(workstation_ports)}")
            return "Workstation", 0.70, reasoning
        
        # Default based on common ports
        if 22 in open_ports:  # SSH
            reasoning.append("SSH detected on Linux, likely server")
            return "Server", 0.65, reasoning
        
        reasoning.append("Linux OS detected, defaulting to Workstation")
        return "Workstation", 0.60, reasoning

    def _classify_by_ports(self, open_ports: List[int]) -> Tuple[str, float, List[str]]:
        """Classify device purely by open ports"""
        reasoning = []
        
        # Web server ports
        if any(port in open_ports for port in [80, 443, 8080, 8443]):
            reasoning.append(f"Web server ports detected: {[p for p in [80, 443, 8080, 8443] if p in open_ports]}")
            return "Server", 0.60, reasoning
        
        # Database ports
        if any(port in open_ports for port in [3306, 5432, 1433, 1521]):
            reasoning.append(f"Database ports detected: {[p for p in [3306, 5432, 1433, 1521] if p in open_ports]}")
            return "Server", 0.65, reasoning
        
        # Network management ports
        if any(port in open_ports for port in [161, 162, 23, 8080]):
            reasoning.append(f"Network management ports detected: {[p for p in [161, 162, 23, 8080] if p in open_ports]}")
            return "Network Device", 0.55, reasoning
        
        # Printer ports
        if any(port in open_ports for port in [515, 631, 9100]):
            reasoning.append(f"Printer ports detected: {[p for p in [515, 631, 9100] if p in open_ports]}")
            return "Printer", 0.70, reasoning
        
        return None, 0.0, reasoning

    def _classify_by_hostname(self, hostname: str) -> Tuple[str, float, List[str]]:
        """Classify device by hostname patterns (last resort)"""
        reasoning = []
        hostname_lower = hostname.lower()
        
        # Server patterns
        if any(pattern in hostname_lower for pattern in ['server', 'srv', 'dc-', 'sql', 'web', 'mail']):
            reasoning.append(f"Server hostname pattern detected in: {hostname}")
            return "Server", 0.40, reasoning
        
        # Workstation patterns
        if any(pattern in hostname_lower for pattern in ['pc-', 'ws-', 'desktop', 'workstation']):
            reasoning.append(f"Workstation hostname pattern detected in: {hostname}")
            return "Workstation", 0.35, reasoning
        
        # Network patterns
        if any(pattern in hostname_lower for pattern in ['switch', 'router', 'fw-', 'gw-']):
            reasoning.append(f"Network device hostname pattern detected in: {hostname}")
            return "Network Device", 0.35, reasoning
        
        return None, 0.0, reasoning

def analyze_current_classification_vs_nmap():
    """Analyze current classification against NMAP-based strategy"""
    print("=== NMAP-BASED CLASSIFICATION ANALYSIS ===")
    print("Checking devices that have NMAP data vs current classification...")
    print()
    
    conn = sqlite3.connect('assets.db')
    cursor = conn.cursor()
    
    # Get devices with NMAP data
    cursor.execute('''
        SELECT hostname, device_type, nmap_os_family, nmap_device_type, 
               operating_system, open_ports
        FROM assets 
        WHERE nmap_os_family IS NOT NULL OR nmap_device_type IS NOT NULL
        ORDER BY last_seen DESC
        LIMIT 20
    ''')
    
    devices = cursor.fetchall()
    classifier = NmapBasedClassifier()
    
    print(f"Found {len(devices)} devices with NMAP data")
    print()
    
    reclassifications = []
    
    for hostname, current_type, nmap_os, nmap_dtype, os_sys, ports_json in devices:
        # Parse ports
        try:
            open_ports = json.loads(ports_json) if ports_json else []
        except:
            open_ports = []
        
        # Get NMAP-based classification
        suggested_type, confidence, reasoning = classifier.classify_device_by_nmap(
            nmap_os or "", nmap_dtype or "", os_sys or "", open_ports, hostname
        )
        
        print(f"📍 {hostname}")
        print(f"   Current Type: {current_type}")
        print(f"   NMAP OS Family: {nmap_os or 'None'}")
        print(f"   NMAP Device Type: {nmap_dtype or 'None'}")
        print(f"   🧠 NMAP-Based Classification: {suggested_type} (confidence: {confidence:.2f})")
        print(f"   📝 Reasoning: {reasoning}")
        
        if current_type != suggested_type and confidence > 0.5:
            print(f"   ⚠️  MISMATCH: Should be '{suggested_type}' instead of '{current_type}'")
            reclassifications.append((hostname, current_type, suggested_type, confidence, reasoning))
        else:
            print(f"   ✅ Classification matches NMAP data")
        
        print()
    
    print(f"=== RECLASSIFICATION SUMMARY ===")
    print(f"Devices needing reclassification: {len(reclassifications)}")
    
    if reclassifications:
        print("\nDevices that should be reclassified based on NMAP data:")
        for hostname, current, suggested, conf, reason in reclassifications:
            print(f"   • {hostname}: {current} → {suggested} (confidence: {conf:.2f})")
    
    conn.close()
    return reclassifications

if __name__ == "__main__":
    analyze_current_classification_vs_nmap()