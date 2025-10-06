#!/usr/bin/env python3
"""
Enhanced Collection Workflow
Handles both authenticated and credential-less device collection
Optimized for Smart TVs, displays, IoT devices, and traditional IT assets
"""

import logging
import json
import sqlite3
from datetime import datetime
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collectors.smart_display_collector import SmartDisplayCollector
from collectors.wmi_collector import collect_windows_wmi
from collectors.ssh_collector import collect_linux_or_esxi_ssh  
from collectors.snmp_collector import snmp_collect_basic
from core.smart_collector import SmartCollector

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedCollectionWorkflow:
    def __init__(self):
        self.display_collector = SmartDisplayCollector()
        self.smart_collector = SmartCollector()
        self.results = {
            'authenticated': [],
            'credential_less': [],
            'failed': [],
            'summary': {}
        }
    
    def discover_all_devices(self, network_range="192.168.1.0/24"):
        """Discover all types of devices on the network"""
        logger.info(f"🌐 Starting comprehensive device discovery on {network_range}")
        
        discovered = {
            'smart_displays': [],
            'network_devices': [],
            'servers': [],
            'unknown': []
        }
        
        # Step 1: Smart display discovery (credential-less)
        logger.info("📱 Phase 1: Discovering smart displays and TVs...")
        try:
            displays = self.display_collector.discover_displays(network_range)
            discovered['smart_displays'] = displays
            logger.info(f"✅ Found {len(displays)} smart displays")
        except Exception as e:
            logger.error(f"❌ Smart display discovery failed: {e}")
        
        # Step 2: General network scan
        logger.info("🔍 Phase 2: General network device discovery...")
        try:
            # Use smart collector for general discovery
            network_devices = self.smart_collector.discover_network_devices(network_range)
            for device in network_devices:
                device_type = self.classify_device(device)
                discovered[device_type].append(device)
            
            total_network = sum(len(devices) for devices in discovered.values()) - len(displays)
            logger.info(f"✅ Found {total_network} additional network devices")
            
        except Exception as e:
            logger.error(f"❌ Network discovery failed: {e}")
        
        return discovered
    
    def classify_device(self, device):
        """Classify discovered device based on characteristics"""
        ip = device.get('ip', '')
        ports = device.get('ports', [])
        
        # Server indicators
        server_ports = [22, 23, 3389, 5985, 5986]  # SSH, Telnet, RDP, WinRM
        if any(port in ports for port in server_ports):
            return 'servers'
        
        # Network device indicators  
        network_ports = [80, 161, 443, 8080]  # HTTP, SNMP, HTTPS
        if 161 in ports:  # SNMP is strong indicator of network device
            return 'network_devices'
        
        return 'unknown'
    
    def collect_credential_less_devices(self, devices):
        """Collect information from devices that don't require credentials"""
        logger.info(f"🔓 Collecting data from {len(devices)} credential-less devices...")
        
        collected = []
        
        for device in devices:
            try:
                # Enhance device information
                enhanced_device = self.display_collector.collect_device_details(device)
                
                # Add additional credential-less collection methods
                enhanced_device = self.add_snmp_public_info(enhanced_device)
                enhanced_device = self.add_http_info(enhanced_device)
                enhanced_device = self.add_upnp_info(enhanced_device)
                
                collected.append(enhanced_device)
                logger.info(f"✅ Collected: {device.get('ip_address', 'Unknown IP')}")
                
            except Exception as e:
                logger.error(f"❌ Failed to collect {device.get('ip_address', 'Unknown')}: {e}")
                device['collection_error'] = str(e)
                self.results['failed'].append(device)
        
        self.results['credential_less'] = collected
        return collected
    
    def collect_authenticated_devices(self, devices, credentials):
        """Collect information from devices requiring authentication"""
        logger.info(f"🔐 Collecting data from {len(devices)} authenticated devices...")
        
        collected = []
        
        for device in devices:
            ip = device.get('ip', device.get('ip_address', ''))
            
            # Try different collection methods
            success = False
            
            # Try WMI (Windows)
            if not success:
                for cred in credentials:
                    if cred['type'].lower() == 'windows':
                        try:
                            result = collect_windows_wmi(ip, cred['username'], cred['password'])
                            if result:
                                device.update(result)
                                device['collection_method'] = 'WMI'
                                collected.append(device)
                                success = True
                                break
                        except Exception as e:
                            logger.debug(f"WMI failed for {ip}: {e}")
            
            # Try SSH (Linux/Unix)
            if not success:
                for cred in credentials:
                    if cred['type'].lower() in ['linux', 'unix', 'esxi']:
                        try:
                            result = collect_linux_or_esxi_ssh(ip, cred['username'], cred['password'])
                            if result:
                                device.update(result)
                                device['collection_method'] = 'SSH'
                                collected.append(device)
                                success = True
                                break
                        except Exception as e:
                            logger.debug(f"SSH failed for {ip}: {e}")
            
            # Try SNMP (Network devices)
            if not success:
                for cred in credentials:
                    if cred['type'].lower() == 'snmp':
                        try:
                            result = snmp_collect_basic(ip, community=cred.get('community', 'public'))
                            if result:
                                device.update(result)
                                device['collection_method'] = 'SNMP'
                                collected.append(device)
                                success = True
                                break
                        except Exception as e:
                            logger.debug(f"SNMP failed for {ip}: {e}")
            
            if not success:
                logger.warning(f"⚠️ Could not collect data from {ip}")
                device['collection_error'] = 'Authentication failed'
                self.results['failed'].append(device)
        
        self.results['authenticated'] = collected
        return collected
    
    def add_snmp_public_info(self, device):
        """Try SNMP with public community (no authentication)"""
        try:
            ip = device.get('ip_address', '')
            snmp_result = snmp_collect_basic(ip, community='public')
            if snmp_result:
                device.update(snmp_result)
                device['snmp_public'] = True
        except Exception as e:
            logger.debug(f"Public SNMP failed for {ip}: {e}")
        
        return device
    
    def add_http_info(self, device):
        """Try HTTP-based information gathering"""
        try:
            import requests
            ip = device.get('ip_address', '')
            
            # Try common HTTP endpoints
            endpoints = ['/', '/info', '/status', '/api/info']
            
            for endpoint in endpoints:
                try:
                    url = f"http://{ip}{endpoint}"
                    response = requests.get(url, timeout=3)
                    
                    if response.status_code == 200:
                        device['http_endpoint'] = url
                        device['http_server'] = response.headers.get('Server', '')
                        
                        # Look for useful information in response
                        content = response.text.lower()
                        if 'model' in content:
                            device['has_model_info'] = True
                        if 'version' in content:
                            device['has_version_info'] = True
                        
                        break
                        
                except requests.exceptions.RequestException:
                    continue
                    
        except Exception as e:
            logger.debug(f"HTTP info gathering failed for {ip}: {e}")
        
        return device
    
    def add_upnp_info(self, device):
        """Try UPnP device information"""
        try:
            import socket
            ip = device.get('ip_address', '')
            
            # UPnP discovery
            msg = (
                'M-SEARCH * HTTP/1.1\r\n'
                'HOST: 239.255.255.250:1900\r\n'
                'MAN: "ssdp:discover"\r\n'
                'ST: upnp:rootdevice\r\n'
                'MX: 3\r\n'
                '\r\n'
            )
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(2)
            sock.sendto(msg.encode(), (ip, 1900))
            
            response, _ = sock.recvfrom(1024)
            response_text = response.decode()
            
            device['upnp_discovered'] = True
            
            # Parse response for useful info
            for line in response_text.split('\r\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower()
                    if key == 'server':
                        device['upnp_server'] = value.strip()
                    elif key == 'location':
                        device['upnp_location'] = value.strip()
            
            sock.close()
            
        except Exception as e:
            logger.debug(f"UPnP discovery failed for {ip}: {e}")
        
        return device
    
    def save_all_results(self):
        """Save all collected results to database"""
        all_devices = (
            self.results['authenticated'] + 
            self.results['credential_less']
        )
        
        if not all_devices:
            logger.warning("⚠️ No devices to save")
            return
        
        try:
            conn = sqlite3.connect('assets.db')
            cursor = conn.cursor()
            
            saved_count = 0
            updated_count = 0
            
            for device in all_devices:
                ip = device.get('ip_address', '')
                
                # Check if device exists
                cursor.execute("SELECT id FROM assets WHERE ip_address = ?", (ip,))
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing record
                    update_fields = []
                    update_values = []
                    
                    for key, value in device.items():
                        if key not in ['id', 'ip_address']:
                            update_fields.append(f"{key} = ?")
                            update_values.append(str(value) if not isinstance(value, str) else value)
                    
                    if update_fields:
                        update_values.append(ip)
                        cursor.execute(f"""
                            UPDATE assets SET {', '.join(update_fields)}, updated_at = datetime('now')
                            WHERE ip_address = ?
                        """, update_values)
                        updated_count += 1
                
                else:
                    # Insert new record
                    device['created_at'] = datetime.now().isoformat()
                    device['updated_at'] = datetime.now().isoformat()
                    
                    fields = list(device.keys())
                    values = [str(v) if not isinstance(v, str) else v for v in device.values()]
                    placeholders = ', '.join(['?'] * len(fields))
                    
                    cursor.execute(f"""
                        INSERT INTO assets ({', '.join(fields)})
                        VALUES ({placeholders})
                    """, values)
                    saved_count += 1
            
            conn.commit()
            conn.close()
            
            logger.info(f"💾 Database updated: {saved_count} new, {updated_count} updated")
            
        except Exception as e:
            logger.error(f"❌ Database save failed: {e}")
    
    def generate_summary_report(self):
        """Generate comprehensive collection summary"""
        summary = {
            'total_discovered': len(self.results['authenticated']) + len(self.results['credential_less']) + len(self.results['failed']),
            'successfully_collected': len(self.results['authenticated']) + len(self.results['credential_less']),
            'failed_collection': len(self.results['failed']),
            'authenticated_devices': len(self.results['authenticated']),
            'credential_less_devices': len(self.results['credential_less']),
            'collection_methods': {},
            'device_types': {},
            'timestamp': datetime.now().isoformat()
        }
        
        # Count collection methods
        all_successful = self.results['authenticated'] + self.results['credential_less']
        for device in all_successful:
            method = device.get('collection_method', 'Unknown')
            summary['collection_methods'][method] = summary['collection_methods'].get(method, 0) + 1
            
            device_type = device.get('device_type', 'Unknown')
            summary['device_types'][device_type] = summary['device_types'].get(device_type, 0) + 1
        
        self.results['summary'] = summary
        
        # Print summary
        print("\n" + "="*60)
        print("📊 COLLECTION SUMMARY REPORT")
        print("="*60)
        print(f"🔍 Total Discovered: {summary['total_discovered']}")
        print(f"✅ Successfully Collected: {summary['successfully_collected']}")
        print(f"❌ Failed Collection: {summary['failed_collection']}")
        print(f"🔐 Authenticated: {summary['authenticated_devices']}")
        print(f"🔓 Credential-less: {summary['credential_less_devices']}")
        
        print("\n📋 Collection Methods:")
        for method, count in summary['collection_methods'].items():
            print(f"   {method}: {count}")
        
        print("\n📱 Device Types:")
        for device_type, count in summary['device_types'].items():
            print(f"   {device_type}: {count}")
        
        if self.results['failed']:
            print("\n⚠️ Failed Devices:")
            for device in self.results['failed']:
                ip = device.get('ip_address', device.get('ip', 'Unknown'))
                error = device.get('collection_error', 'Unknown error')
                print(f"   {ip}: {error}")
        
        print("="*60)
        
        return summary

def main():
    workflow = EnhancedCollectionWorkflow()
    
    # Get network range from command line or use default
    network_range = sys.argv[1] if len(sys.argv) > 1 else "192.168.1.0/24"
    
    print("🚀 ENHANCED COLLECTION WORKFLOW")
    print(f"🌐 Target Network: {network_range}")
    print("="*60)
    
    # Step 1: Discover all devices
    discovered = workflow.discover_all_devices(network_range)
    
    # Step 2: Collect credential-less devices (Smart TVs, displays, etc.)
    credential_less = discovered['smart_displays'] + [
        device for device in discovered['network_devices'] 
        if device.get('snmp_public', False)
    ]
    
    if credential_less:
        workflow.collect_credential_less_devices(credential_less)
    
    # Step 3: For authenticated devices, you would need to provide credentials
    # This is just a demonstration - in practice, credentials would come from secure vault
    sample_credentials = [
        {'type': 'windows', 'username': 'admin', 'password': 'password'},
        {'type': 'linux', 'username': 'root', 'password': 'password'},  
        {'type': 'snmp', 'community': 'private'}
    ]
    
    authenticated_devices = discovered['servers'] + [
        device for device in discovered['network_devices']
        if not device.get('snmp_public', False)
    ]
    
    if authenticated_devices:
        print("\n⚠️ Note: Authenticated devices found but no credentials provided")
        print("   Use the GUI to add credentials for full collection")
        # workflow.collect_authenticated_devices(authenticated_devices, sample_credentials)
    
    # Step 4: Save results and generate report
    workflow.save_all_results()
    workflow.generate_summary_report()
    
    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"collection_results_{timestamp}.json"
    with open(results_file, 'w') as f:
        json.dump(workflow.results, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {results_file}")

if __name__ == "__main__":
    main()