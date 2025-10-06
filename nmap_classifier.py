#!/usr/bin/env python3
"""
NMAP DEVICE CLASSIFICATION SYSTEM

This module provides intelligent device classification using NMAP scanning
for unknown devices in the asset management system.
"""

import ipaddress  # For IP validation
import nmap
import subprocess
import json
import sqlite3
from datetime import datetime
import asyncio
import concurrent.futures
import socket

class NMAPDeviceClassifier:
    def __init__(self, db_path="../assets.db"):
        self.db_path = db_path
        self.scanner = None
        self.initialize_scanner()
    
    def initialize_scanner(self):
        """Initialize NMAP scanner"""
        try:
            self.scanner = nmap.PortScanner()
            print("✅ NMAP scanner initialized successfully")
            return True
        except Exception as e:
            print(f"⚠️ NMAP not available: {e}")
            print("📥 Install NMAP from: https://nmap.org/download.html")
            return False
    
    def is_nmap_available(self):
        """Check if NMAP is available"""
        try:
            subprocess.run(['nmap', '--version'], 
                         capture_output=True, check=True, timeout=5)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def classify_device_by_ports(self, ip_address, timeout=10):
        """Classify device based on open ports"""
        if not self.scanner:
            return self.fallback_classification(ip_address)
        
        try:
            print(f"🔍 Scanning {ip_address} for device classification...")
            
            # Common port ranges for different device types
            port_ranges = "21,22,23,25,53,80,110,135,139,143,443,445,993,995,1433,1521,3306,3389,5432,5900,8080,8443,9100"
            
            # Perform scan with timeout
            self.scanner.scan(ip_address, port_ranges, arguments=f'-sS -T4 --host-timeout {timeout}s')
            
            if ip_address not in self.scanner.all_hosts():
                return self.fallback_classification(ip_address)
            
            host_info = self.scanner[ip_address]
            open_ports = []
            
            # Collect open ports
            for protocol in host_info.all_protocols():
                ports = host_info[protocol].keys()
                for port in ports:
                    if host_info[protocol][port]['state'] == 'open':
                        open_ports.append(port)
            
            # Classify based on port signatures
            classification = self.classify_by_port_signature(open_ports, ip_address)
            
            print(f"✅ {ip_address} classified as: {classification['device_type']}")
            return classification
            
        except Exception as e:
            print(f"❌ NMAP scan error for {ip_address}: {e}")
            return self.fallback_classification(ip_address)
    
    def classify_by_port_signature(self, open_ports, ip_address):
        """Classify device based on open port patterns"""
        
        # Initialize classification
        classification = {
            'device_type': 'Unknown',
            'operating_system': None,
            'services': [],
            'confidence': 'Low',
            'open_ports': open_ports,
            'scan_timestamp': datetime.now().isoformat()
        }
        
        # Server classifications (highest priority)
        if self.is_database_server(open_ports):
            classification.update({
                'device_type': 'Database Server',
                'operating_system': self.guess_server_os(open_ports),
                'confidence': 'High'
            })
        elif self.is_web_server(open_ports):
            classification.update({
                'device_type': 'Web Server',
                'operating_system': self.guess_server_os(open_ports),
                'confidence': 'High'
            })
        elif self.is_file_server(open_ports):
            classification.update({
                'device_type': 'File Server',
                'operating_system': self.guess_server_os(open_ports),
                'confidence': 'High'
            })
        
        # Network infrastructure
        elif self.is_network_device(open_ports):
            classification.update({
                'device_type': 'Network Device',
                'operating_system': 'Network OS',
                'confidence': 'Medium'
            })
        elif self.is_printer(open_ports):
            classification.update({
                'device_type': 'Printer',
                'operating_system': 'Embedded',
                'confidence': 'High'
            })
        
        # Workstations and endpoints
        elif self.is_windows_workstation(open_ports):
            classification.update({
                'device_type': 'Windows Workstation',
                'operating_system': 'Windows',
                'confidence': 'High'
            })
        elif self.is_linux_workstation(open_ports):
            classification.update({
                'device_type': 'Linux Workstation',
                'operating_system': 'Linux',
                'confidence': 'Medium'
            })
        
        # Generic classifications
        elif len(open_ports) > 5:
            classification.update({
                'device_type': 'Server',
                'operating_system': self.guess_server_os(open_ports),
                'confidence': 'Low'
            })
        elif len(open_ports) > 0:
            classification.update({
                'device_type': 'Workstation',
                'confidence': 'Low'
            })
        
        # Add detected services
        classification['services'] = self.detect_services(open_ports)
        
        return classification
    
    def is_database_server(self, ports):
        """Check if device is a database server"""
        db_ports = [1433, 1521, 3306, 5432, 27017]  # SQL Server, Oracle, MySQL, PostgreSQL, MongoDB
        return any(port in ports for port in db_ports)
    
    def is_web_server(self, ports):
        """Check if device is a web server"""
        web_ports = [80, 443, 8080, 8443, 8000, 8081]
        return any(port in ports for port in web_ports)
    
    def is_file_server(self, ports):
        """Check if device is a file server"""
        file_ports = [21, 22, 139, 445, 2049]  # FTP, SSH, SMB, NFS
        smb_ports = [139, 445]
        return (any(port in ports for port in file_ports) and 
                not self.is_web_server(ports) and 
                not self.is_database_server(ports))
    
    def is_network_device(self, ports):
        """Check if device is a network device"""
        network_ports = [23, 161, 162, 514, 515]  # Telnet, SNMP, Syslog, LPD
        minimal_services = len(ports) <= 3
        return (any(port in ports for port in network_ports) and minimal_services)
    
    def is_printer(self, ports):
        """Check if device is a printer"""
        printer_ports = [515, 631, 9100, 161]  # LPD, IPP, JetDirect, SNMP
        return any(port in ports for port in printer_ports)
    
    def is_windows_workstation(self, ports):
        """Check if device is a Windows workstation"""
        windows_ports = [135, 139, 445, 3389]  # RPC, NetBIOS, SMB, RDP
        return (3389 in ports or  # RDP is strong indicator
                (135 in ports and 445 in ports))  # Windows file sharing
    
    def is_linux_workstation(self, ports):
        """Check if device is a Linux workstation"""
        linux_indicators = [22]  # SSH
        windows_indicators = [135, 139, 3389]
        
        return (22 in ports and  # SSH present
                not any(port in ports for port in windows_indicators))  # No Windows ports
    
    def guess_server_os(self, ports):
        """Guess server operating system"""
        if 3389 in ports or 135 in ports:
            return 'Windows Server'
        elif 22 in ports and 3389 not in ports:
            return 'Linux'
        elif 161 in ports:  # SNMP might indicate network device
            return 'Network OS'
        else:
            return 'Unknown Server OS'
    
    def detect_services(self, ports):
        """Detect services based on common ports"""
        service_map = {
            21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP',
            53: 'DNS', 80: 'HTTP', 110: 'POP3', 135: 'RPC',
            139: 'NetBIOS', 143: 'IMAP', 443: 'HTTPS', 445: 'SMB',
            993: 'IMAPS', 995: 'POP3S', 1433: 'SQL Server',
            1521: 'Oracle', 3306: 'MySQL', 3389: 'RDP',
            5432: 'PostgreSQL', 5900: 'VNC', 8080: 'HTTP-Alt',
            8443: 'HTTPS-Alt', 9100: 'JetDirect'
        }
        
        return [service_map.get(port, f'Port-{port}') for port in ports if port in service_map]
    
    def fallback_classification(self, ip_address):
        """Fallback classification without NMAP"""
        print(f"🔄 Using fallback classification for {ip_address}")
        
        # Try basic connectivity tests
        device_type = 'Unknown'
        os_guess = None
        
        try:
            # Quick port checks
            if self.check_port(ip_address, 3389, timeout=2):
                device_type = 'Windows Workstation'
                os_guess = 'Windows'
            elif self.check_port(ip_address, 22, timeout=2):
                device_type = 'Linux Workstation'
                os_guess = 'Linux'
            elif self.check_port(ip_address, 80, timeout=2) or self.check_port(ip_address, 443, timeout=2):
                device_type = 'Web Server'
            elif self.check_port(ip_address, 161, timeout=2):
                device_type = 'Network Device'
                os_guess = 'Network OS'
        except:
            pass
        
        return {
            'device_type': device_type,
            'operating_system': os_guess,
            'services': [],
            'confidence': 'Very Low',
            'open_ports': [],
            'scan_timestamp': datetime.now().isoformat(),
            'method': 'fallback'
        }
    
    def check_port(self, ip, port, timeout=3):
        """Quick port connectivity check"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except:
            return False
    
    async def classify_unknown_devices_batch(self, limit=5):
        """Classify multiple unknown devices in parallel"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get unknown devices
            cursor.execute("""
                SELECT id, ip_address, hostname 
                FROM assets_enhanced 
                WHERE (device_type = 'Unknown' OR device_type IS NULL OR device_type = '')
                AND ip_address IS NOT NULL 
                AND ip_address != ''
                LIMIT ?
            """, (limit,))
            
            unknown_devices = cursor.fetchall()
            
            if not unknown_devices:
                print("✅ No unknown devices found for classification")
                return []
            
            print(f"🔍 Classifying {len(unknown_devices)} unknown devices...")
            
            # Classify devices in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                classification_tasks = [
                    executor.submit(self.classify_device_by_ports, device[1])
                    for device in unknown_devices
                ]
                
                results = []
                for i, task in enumerate(concurrent.futures.as_completed(classification_tasks)):
                    try:
                        device_id, ip_address, hostname = unknown_devices[i]
                        classification = task.result()
                        
                        # Update database
                        self.update_device_classification(device_id, classification)
                        
                        results.append({
                            'device_id': device_id,
                            'ip_address': ip_address,
                            'hostname': hostname,
                            'classification': classification
                        })
                        
                    except Exception as e:
                        print(f"❌ Classification error: {e}")
            
            return results
            
        finally:
            conn.close()
    
    def update_device_classification(self, device_id, classification):
        """Update device classification in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE assets_enhanced 
                SET device_type = ?,
                    operating_system = COALESCE(?, operating_system),
                    nmap_scan_results = ?,
                    classification_confidence = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                classification['device_type'],
                classification['operating_system'],
                json.dumps(classification),
                classification['confidence'],
                device_id
            ))
            
            conn.commit()
            print(f"✅ Updated device {device_id} classification: {classification['device_type']}")
            
        except Exception as e:
            print(f"❌ Database update error: {e}")
        finally:
            conn.close()
    
    def get_classification_stats(self):
        """Get classification statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Device type distribution
            cursor.execute("""
                SELECT device_type, COUNT(*) as count
                FROM assets_enhanced 
                GROUP BY device_type 
                ORDER BY count DESC
            """)
            device_types = cursor.fetchall()
            
            # Classification confidence
            cursor.execute("""
                SELECT classification_confidence, COUNT(*) as count
                FROM assets_enhanced 
                WHERE classification_confidence IS NOT NULL
                GROUP BY classification_confidence
            """)
            confidence_levels = cursor.fetchall()
            
            # Unknown devices
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM assets_enhanced 
                WHERE device_type = 'Unknown' OR device_type IS NULL OR device_type = ''
            """)
            unknown_count = cursor.fetchone()[0]
            
            return {
                'device_types': dict(device_types),
                'confidence_levels': dict(confidence_levels),
                'unknown_devices': unknown_count,
                'nmap_available': self.scanner is not None
            }
            
        finally:
            conn.close()

def main():
    """Main function for testing"""
    classifier = NMAPDeviceClassifier()
    
    if not classifier.is_nmap_available():
        print("⚠️ NMAP is not installed or not available in PATH")
        print("📥 Please install NMAP from: https://nmap.org/download.html")
        return
    
    # Test classification
    results = asyncio.run(classifier.classify_unknown_devices_batch(3))
    
    print("\n📊 Classification Results:")
    for result in results:
        print(f"  {result['ip_address']} -> {result['classification']['device_type']}")
    
    # Show stats
    stats = classifier.get_classification_stats()
    print("\n📈 Classification Statistics:")
    print(f"  Device Types: {stats['device_types']}")
    print(f"  Unknown Devices: {stats['unknown_devices']}")
    print(f"  NMAP Available: {stats['nmap_available']}")

if __name__ == '__main__':
    main()