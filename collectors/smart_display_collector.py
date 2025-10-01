#!/usr/bin/env python3
"""
Smart Display Collector
Collects information from Smart TVs, Digital Displays, and other devices
that don't require authentication (LG, Samsung, JAC, etc.)
"""

import requests
import socket
import json
import nmap
import time
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
import ssl
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SmartDisplayCollector:
    def __init__(self):
        self.timeout = 3
        self.session = requests.Session()
        self.session.timeout = self.timeout
        
    def discover_displays(self, network_range="192.168.1.0/24"):
        """Discover smart displays and TVs on the network"""
        logger.info(f"🔍 Scanning for smart displays on {network_range}")
        
        nm = nmap.PortScanner()
        
        # Common ports for smart TVs and displays
        tv_ports = "80,443,1900,7676,8080,8443,9080,55000"  # UPnP, web interfaces
        
        try:
            nm.scan(network_range, tv_ports, arguments='-T4 --open')
            
            displays = []
            for host in nm.all_hosts():
                if nm[host].state() == 'up':
                    device_info = self.identify_display(host, nm[host])
                    if device_info:
                        displays.append(device_info)
                        logger.info(f"✅ Found display: {host} - {device_info.get('model', 'Unknown')}")
            
            return displays
            
        except Exception as e:
            logger.error(f"❌ Network scan failed: {e}")
            return []
    
    def identify_display(self, ip, nmap_data):
        """Identify if device is a smart display/TV and collect info"""
        device_info = {
            'ip_address': ip,
            'device_type': 'display',
            'hostname': ip,
            'ports': [],
            'services': [],
            'collection_method': 'smart_display_scan',
            'data_source': 'SmartDisplayCollector',
            'last_updated': datetime.now().isoformat()
        }
        
        # Check open ports
        for proto in nmap_data.all_protocols():
            ports = nmap_data[proto].keys()
            for port in ports:
                service = nmap_data[proto][port]
                device_info['ports'].append(port)
                device_info['services'].append(f"{port}/{proto}: {service['name']}")
        
        # Try different identification methods
        display_type = None
        
        # Method 1: UPnP Discovery (port 1900)
        if 1900 in device_info['ports']:
            upnp_info = self.check_upnp(ip)
            if upnp_info:
                device_info.update(upnp_info)
                display_type = "UPnP Device"
        
        # Method 2: Web interface check (ports 80, 8080, etc.)
        web_ports = [80, 8080, 443, 8443]
        for port in web_ports:
            if port in device_info['ports']:
                web_info = self.check_web_interface(ip, port)
                if web_info:
                    device_info.update(web_info)
                    if not display_type:
                        display_type = "Web-enabled Display"
        
        # Method 3: LG TV specific (port 3000, 3001)
        lg_info = self.check_lg_tv(ip)
        if lg_info:
            device_info.update(lg_info)
            display_type = "LG Smart TV"
        
        # Method 4: Samsung TV specific
        samsung_info = self.check_samsung_tv(ip)
        if samsung_info:
            device_info.update(samsung_info)
            display_type = "Samsung Smart TV"
        
        # Method 5: Generic display detection
        if not display_type:
            generic_info = self.check_generic_display(ip)
            if generic_info:
                device_info.update(generic_info)
                display_type = "Smart Display"
        
        if display_type:
            device_info['device_type'] = display_type.lower().replace(' ', '_')
            device_info['model_vendor'] = display_type
            return device_info
        
        return None
    
    def check_upnp(self, ip):
        """Check for UPnP services (Smart TVs often support this)"""
        try:
            # UPnP discovery request
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
            
            # Parse UPnP response
            info = {}
            for line in response_text.split('\r\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    
                    if key == 'server':
                        info['firmware_os_version'] = value
                    elif key == 'location':
                        info['upnp_location'] = value
            
            sock.close()
            return info
            
        except Exception as e:
            logger.debug(f"UPnP check failed for {ip}: {e}")
            return None
    
    def check_web_interface(self, ip, port=80):
        """Check for web interface and try to identify device"""
        try:
            protocols = ['http'] if port != 443 else ['https', 'http']
            
            for protocol in protocols:
                try:
                    url = f"{protocol}://{ip}:{port}"
                    response = self.session.get(url, timeout=self.timeout, verify=False)
                    
                    if response.status_code == 200:
                        content = response.text.lower()
                        headers = response.headers
                        
                        info = {'web_interface': url}
                        
                        # Check Server header
                        if 'server' in headers:
                            info['firmware_os_version'] = headers['server']
                        
                        # Brand detection in content
                        if 'lg' in content or 'webos' in content:
                            info['model_vendor'] = 'LG'
                            info['notes'] = 'LG Smart TV detected via web interface'
                        elif 'samsung' in content or 'tizen' in content:
                            info['model_vendor'] = 'Samsung'
                            info['notes'] = 'Samsung Smart TV detected via web interface'
                        elif any(brand in content for brand in ['sony', 'panasonic', 'philips', 'tcl']):
                            for brand in ['sony', 'panasonic', 'philips', 'tcl']:
                                if brand in content:
                                    info['model_vendor'] = brand.capitalize()
                                    break
                        
                        return info
                        
                except requests.exceptions.SSLError:
                    continue
                except requests.exceptions.RequestException:
                    continue
            
            return None
            
        except Exception as e:
            logger.debug(f"Web interface check failed for {ip}:{port}: {e}")
            return None
    
    def check_lg_tv(self, ip):
        """Specific check for LG Smart TVs"""
        try:
            # LG TVs often use port 3000 for WebOS
            lg_ports = [3000, 3001]
            
            for port in lg_ports:
                try:
                    url = f"http://{ip}:{port}"
                    response = self.session.get(url, timeout=self.timeout)
                    
                    if response.status_code in [200, 401, 403]:
                        return {
                            'model_vendor': 'LG',
                            'firmware_os_version': 'WebOS',
                            'device_type': 'smart_tv',
                            'notes': f'LG Smart TV detected on port {port}',
                            'lg_interface': url
                        }
                        
                except requests.exceptions.RequestException:
                    continue
            
            return None
            
        except Exception as e:
            logger.debug(f"LG TV check failed for {ip}: {e}")
            return None
    
    def check_samsung_tv(self, ip):
        """Specific check for Samsung Smart TVs"""
        try:
            # Samsung TVs often use port 8001 for remote control, 8080 for web
            samsung_ports = [8001, 8080, 55000]
            
            for port in samsung_ports:
                try:
                    # Try WebSocket connection for Samsung TV
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)
                    result = sock.connect_ex((ip, port))
                    sock.close()
                    
                    if result == 0:  # Connection successful
                        return {
                            'model_vendor': 'Samsung',
                            'firmware_os_version': 'Tizen OS',
                            'device_type': 'smart_tv',
                            'notes': f'Samsung Smart TV detected on port {port}',
                            'samsung_port': port
                        }
                        
                except Exception:
                    continue
            
            return None
            
        except Exception as e:
            logger.debug(f"Samsung TV check failed for {ip}: {e}")
            return None
    
    def check_generic_display(self, ip):
        """Generic display detection based on common patterns"""
        try:
            # Check for common display/TV patterns
            common_paths = [
                '/cgi-bin/info.cgi',
                '/api/system/info',
                '/status',
                '/info',
                '/device'
            ]
            
            for path in common_paths:
                try:
                    url = f"http://{ip}{path}"
                    response = self.session.get(url, timeout=self.timeout)
                    
                    if response.status_code == 200:
                        content = response.text.lower()
                        
                        # Look for display-related keywords
                        display_keywords = [
                            'display', 'monitor', 'screen', 'panel', 'lcd', 'led',
                            'tv', 'television', 'smart', 'digital signage'
                        ]
                        
                        if any(keyword in content for keyword in display_keywords):
                            return {
                                'device_type': 'smart_display',
                                'notes': f'Display detected via {path}',
                                'detection_url': url
                            }
                            
                except requests.exceptions.RequestException:
                    continue
            
            return None
            
        except Exception as e:
            logger.debug(f"Generic display check failed for {ip}: {e}")
            return None
    
    def collect_device_details(self, device_info):
        """Collect additional details for identified displays"""
        ip = device_info['ip_address']
        
        # Try to get hostname
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            device_info['hostname'] = hostname
        except socket.herror:
            pass
        
        # Try to get MAC address (requires ARP table access)
        try:
            import subprocess
            import re
            
            # Windows
            if hasattr(subprocess, 'run'):
                result = subprocess.run(['arp', '-a', ip], capture_output=True, text=True)
                if result.returncode == 0:
                    mac_match = re.search(r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})', result.stdout)
                    if mac_match:
                        device_info['mac_address'] = mac_match.group(0)
        except Exception:
            pass
        
        return device_info
    
    def save_to_database(self, devices):
        """Save discovered devices to database"""
        try:
            import sqlite3
            
            conn = sqlite3.connect('assets.db')
            cursor = conn.cursor()
            
            for device in devices:
                # Check if device already exists
                cursor.execute("SELECT id FROM assets WHERE ip_address = ?", (device['ip_address'],))
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing record
                    update_fields = []
                    update_values = []
                    
                    for key, value in device.items():
                        if key != 'ip_address':
                            update_fields.append(f"{key} = ?")
                            update_values.append(str(value) if not isinstance(value, str) else value)
                    
                    update_values.append(device['ip_address'])
                    
                    cursor.execute(f"""
                        UPDATE assets SET {', '.join(update_fields)}, updated_at = datetime('now')
                        WHERE ip_address = ?
                    """, update_values)
                    
                    logger.info(f"✅ Updated device: {device['ip_address']}")
                else:
                    # Insert new record
                    fields = list(device.keys()) + ['created_at', 'updated_at']
                    values = list(device.values()) + [datetime.now().isoformat(), datetime.now().isoformat()]
                    placeholders = ', '.join(['?'] * len(fields))
                    
                    cursor.execute(f"""
                        INSERT INTO assets ({', '.join(fields)})
                        VALUES ({placeholders})
                    """, [str(v) if not isinstance(v, str) else v for v in values])
                    
                    logger.info(f"✅ Added new device: {device['ip_address']}")
            
            conn.commit()
            conn.close()
            
            logger.info(f"💾 Saved {len(devices)} devices to database")
            
        except Exception as e:
            logger.error(f"❌ Database save failed: {e}")

def main():
    import sys
    
    collector = SmartDisplayCollector()
    
    if len(sys.argv) > 1:
        network_range = sys.argv[1]
    else:
        network_range = "192.168.1.0/24"
    
    print(f"🎯 SMART DISPLAY COLLECTOR")
    print(f"🔍 Scanning network: {network_range}")
    print("=" * 50)
    
    # Discover displays
    displays = collector.discover_displays(network_range)
    
    if not displays:
        print("❌ No smart displays found")
        return
    
    print(f"✅ Found {len(displays)} smart displays")
    print("=" * 50)
    
    # Collect additional details and save
    enhanced_displays = []
    for display in displays:
        enhanced = collector.collect_device_details(display)
        enhanced_displays.append(enhanced)
        
        print(f"📱 {display['ip_address']}")
        print(f"   Type: {display.get('model_vendor', 'Unknown Display')}")
        print(f"   Model: {display.get('device_type', 'display')}")
        print(f"   Ports: {', '.join(map(str, display.get('ports', [])))}")
        if 'notes' in display:
            print(f"   Notes: {display['notes']}")
        print()
    
    # Save to database
    collector.save_to_database(enhanced_displays)
    
    print(f"💾 All {len(enhanced_displays)} displays saved to database!")

if __name__ == "__main__":
    main()