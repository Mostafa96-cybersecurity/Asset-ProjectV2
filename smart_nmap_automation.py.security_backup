"""
SMART NMAP AUTOMATION SYSTEM
Automatically detects "Unknown Device" assets and runs nmap to identify OS type
"""

import sqlite3
import subprocess
import json
import time
from datetime import datetime
import re
from concurrent.futures import ThreadPoolExecutor

class SmartNmapAutomation:
    def __init__(self, db_path='assets.db'):
        self.db_path = db_path
        self.running = False
        self.scan_interval = 300  # 5 minutes
        self.max_concurrent_scans = 5
        
    def get_db_connection(self):
        """Get database connection"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            print(f"❌ Database connection error: {e}")
            return None
    
    def install_nmap(self):
        """Install nmap if not available"""
        try:
            subprocess.run(['nmap', '--version'], capture_output=True, check=True)
            print("✅ Nmap is already installed")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("📦 Installing nmap...")
            try:
                # Try different installation methods
                install_commands = [
                    ['choco', 'install', 'nmap', '-y'],
                    ['winget', 'install', 'Nmap.Nmap'],
                    ['scoop', 'install', 'nmap']
                ]
                
                for cmd in install_commands:
                    try:
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                        if result.returncode == 0:
                            print("✅ Nmap installed successfully")
                            return True
                    except:
                        continue
                
                print("⚠️  Could not install nmap automatically. Please install manually.")
                return False
                
            except Exception as e:
                print(f"❌ Nmap installation failed: {e}")
                return False
    
    def get_unknown_devices(self):
        """Get all devices with 'Unknown Device' type"""
        conn = self.get_db_connection()
        if not conn:
            return []
            
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, hostname, ip_address, device_type, mac_address, last_seen
                FROM assets_enhanced 
                WHERE device_type = 'Unknown Device' 
                   OR device_type IS NULL 
                   OR device_type = ''
                   OR os_family IS NULL
                   OR os_family = ''
                ORDER BY last_seen DESC
            """)
            
            unknown_devices = []
            for row in cursor.fetchall():
                unknown_devices.append({
                    'id': row['id'],
                    'hostname': row['hostname'],
                    'ip_address': row['ip_address'],
                    'device_type': row['device_type'],
                    'mac_address': row['mac_address'],
                    'last_seen': row['last_seen']
                })
            
            conn.close()
            return unknown_devices
            
        except Exception as e:
            print(f"❌ Error getting unknown devices: {e}")
            conn.close()
            return []
    
    def run_nmap_scan(self, ip_address):
        """Run comprehensive nmap scan on IP address"""
        if not ip_address or ip_address == '127.0.0.1':
            return None
            
        try:
            print(f"🔍 Running nmap scan on {ip_address}...")
            
            # Comprehensive nmap scan with OS detection, service detection, and scripts
            nmap_cmd = [
                'nmap',
                '-O',          # OS detection
                '-sV',         # Service version detection
                '-sS',         # TCP SYN scan
                '-A',          # Aggressive scan (OS, version, script, traceroute)
                '--script', 'default,discovery,safe',  # Safe scripts
                '-T4',         # Timing template (faster)
                '--max-retries', '2',
                '--host-timeout', '5m',
                ip_address
            ]
            
            result = subprocess.run(
                nmap_cmd, 
                capture_output=True, 
                text=True, 
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                scan_result = self.parse_nmap_output(result.stdout)
                print(f"✅ Nmap scan completed for {ip_address}")
                return scan_result
            else:
                print(f"❌ Nmap scan failed for {ip_address}: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print(f"⏱️  Nmap scan timeout for {ip_address}")
            return None
        except Exception as e:
            print(f"❌ Nmap scan error for {ip_address}: {e}")
            return None
    
    def parse_nmap_output(self, nmap_output):
        """Parse nmap output to extract device information"""
        scan_data = {
            'os_family': None,
            'os_version': None,
            'device_type': None,
            'services': [],
            'open_ports': [],
            'mac_address': None,
            'vendor': None,
            'device_info': None,
            'scan_timestamp': datetime.now().isoformat()
        }
        
        try:
            lines = nmap_output.split('\n')
            
            for line in lines:
                line = line.strip()
                
                # OS Detection
                if 'Running:' in line:
                    os_match = re.search(r'Running: (.+)', line)
                    if os_match:
                        scan_data['os_family'] = os_match.group(1)
                
                if 'OS details:' in line:
                    os_match = re.search(r'OS details: (.+)', line)
                    if os_match:
                        scan_data['os_version'] = os_match.group(1)
                
                # MAC Address and Vendor
                if 'MAC Address:' in line:
                    mac_match = re.search(r'MAC Address: ([0-9A-Fa-f:]{17}) \((.+)\)', line)
                    if mac_match:
                        scan_data['mac_address'] = mac_match.group(1)
                        scan_data['vendor'] = mac_match.group(2)
                
                # Open Ports and Services
                if '/tcp' in line and 'open' in line:
                    port_match = re.search(r'(\d+)/tcp\s+open\s+(\S+)(?:\s+(.+))?', line)
                    if port_match:
                        port = port_match.group(1)
                        service = port_match.group(2)
                        version = port_match.group(3) if port_match.group(3) else ''
                        
                        scan_data['open_ports'].append(port)
                        scan_data['services'].append({
                            'port': port,
                            'service': service,
                            'version': version.strip()
                        })
                
                # Device Type Detection based on services
                if any(service in line.lower() for service in ['ssh', 'telnet', 'snmp']):
                    if 'cisco' in line.lower():
                        scan_data['device_type'] = 'Network Switch'
                    elif 'hp' in line.lower() or 'jetdirect' in line.lower():
                        scan_data['device_type'] = 'Network Printer'
                    elif 'linux' in line.lower():
                        scan_data['device_type'] = 'Linux Server'
                    elif 'windows' in line.lower():
                        scan_data['device_type'] = 'Windows Server'
                
                if 'http' in line.lower() and 'web' in line.lower():
                    scan_data['device_type'] = scan_data['device_type'] or 'Web Server'
                
                if 'printer' in line.lower():
                    scan_data['device_type'] = 'Network Printer'
                
                if 'router' in line.lower():
                    scan_data['device_type'] = 'Network Router'
            
            # Determine OS family and device type from scan results
            if scan_data['os_family']:
                os_family_lower = scan_data['os_family'].lower()
                if 'windows' in os_family_lower:
                    scan_data['os_family'] = 'Windows'
                    scan_data['device_type'] = scan_data['device_type'] or 'Windows Workstation'
                elif 'linux' in os_family_lower:
                    scan_data['os_family'] = 'Linux'
                    scan_data['device_type'] = scan_data['device_type'] or 'Linux Server'
                elif 'cisco' in os_family_lower:
                    scan_data['os_family'] = 'Cisco IOS'
                    scan_data['device_type'] = 'Network Device'
                elif 'hp' in os_family_lower:
                    scan_data['device_type'] = scan_data['device_type'] or 'Network Printer'
            
            # Convert lists to JSON strings for database storage
            scan_data['services'] = json.dumps(scan_data['services'])
            scan_data['open_ports'] = json.dumps(scan_data['open_ports'])
            
            return scan_data
            
        except Exception as e:
            print(f"❌ Error parsing nmap output: {e}")
            return scan_data
    
    def update_device_info(self, device_id, scan_data):
        """Update device information in database"""
        conn = self.get_db_connection()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            
            # Prepare update data
            update_fields = []
            update_values = []
            
            if scan_data['os_family']:
                update_fields.append("os_family = ?")
                update_values.append(scan_data['os_family'])
            
            if scan_data['os_version']:
                update_fields.append("operating_system = ?")
                update_values.append(scan_data['os_version'])
            
            if scan_data['device_type']:
                update_fields.append("device_type = ?")
                update_values.append(scan_data['device_type'])
            
            if scan_data['mac_address']:
                update_fields.append("mac_address = ?")
                update_values.append(scan_data['mac_address'])
            
            if scan_data['vendor']:
                update_fields.append("system_manufacturer = ?")
                update_values.append(scan_data['vendor'])
            
            # Add scan metadata
            update_fields.extend([
                "collection_method = ?",
                "collection_timestamp = ?",
                "updated_at = ?",
                "device_status = ?",
                "last_seen = ?"
            ])
            
            update_values.extend([
                "NMAP (Smart Automation)",
                scan_data['scan_timestamp'],
                scan_data['scan_timestamp'],
                "Online",
                scan_data['scan_timestamp']
            ])
            
            # Add services and ports if available
            if scan_data['services'] != '[]':
                update_fields.append("network_services = ?")
                update_values.append(scan_data['services'])
            
            if scan_data['open_ports'] != '[]':
                update_fields.append("open_ports = ?")
                update_values.append(scan_data['open_ports'])
            
            # Execute update
            update_values.append(device_id)
            update_sql = f"UPDATE assets_enhanced SET {', '.join(update_fields)} WHERE id = ?"
            
            cursor.execute(update_sql, update_values)
            conn.commit()
            conn.close()
            
            print(f"✅ Updated device {device_id} with nmap scan results")
            return True
            
        except Exception as e:
            print(f"❌ Error updating device {device_id}: {e}")
            conn.close()
            return False
    
    def scan_unknown_device(self, device):
        """Scan a single unknown device"""
        try:
            print(f"🔍 Scanning unknown device: {device['hostname']} ({device['ip_address']})")
            
            scan_result = self.run_nmap_scan(device['ip_address'])
            
            if scan_result:
                success = self.update_device_info(device['id'], scan_result)
                if success:
                    print(f"✅ Successfully identified device {device['hostname']}")
                    print(f"   OS Family: {scan_result['os_family']}")
                    print(f"   Device Type: {scan_result['device_type']}")
                    print(f"   Vendor: {scan_result['vendor']}")
                    return True
                else:
                    print(f"❌ Failed to update device {device['hostname']}")
                    return False
            else:
                print(f"❌ Nmap scan failed for device {device['hostname']}")
                return False
                
        except Exception as e:
            print(f"❌ Error scanning device {device['hostname']}: {e}")
            return False
    
    def run_automation_cycle(self):
        """Run one cycle of smart automation"""
        print(f"\n🤖 SMART NMAP AUTOMATION CYCLE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # Get unknown devices
        unknown_devices = self.get_unknown_devices()
        
        if not unknown_devices:
            print("✅ No unknown devices found - all devices are classified!")
            return
        
        print(f"🔍 Found {len(unknown_devices)} unknown devices to scan")
        
        # Scan devices concurrently
        with ThreadPoolExecutor(max_workers=self.max_concurrent_scans) as executor:
            futures = []
            for device in unknown_devices[:10]:  # Limit to 10 devices per cycle
                future = executor.submit(self.scan_unknown_device, device)
                futures.append(future)
            
            # Wait for all scans to complete
            successful_scans = 0
            for future in futures:
                try:
                    if future.result():
                        successful_scans += 1
                except Exception as e:
                    print(f"❌ Scan future error: {e}")
        
        print("\n📊 Automation cycle completed:")
        print(f"   🎯 Devices scanned: {len(futures)}")
        print(f"   ✅ Successful identifications: {successful_scans}")
        print(f"   ❌ Failed scans: {len(futures) - successful_scans}")
        print("=" * 70)
    
    def start_automation(self):
        """Start the smart automation service"""
        print("🚀 STARTING SMART NMAP AUTOMATION SERVICE")
        print("=" * 70)
        print("🎯 Features:")
        print("   ✅ Auto-detect Unknown Devices")
        print("   ✅ OS Identification via Nmap")
        print("   ✅ Device Type Classification")
        print("   ✅ Continuous Background Monitoring")
        print("   ✅ Concurrent Scanning (5 devices)")
        print("=" * 70)
        
        # Install nmap if needed
        if not self.install_nmap():
            print("❌ Cannot start automation without nmap")
            return
        
        self.running = True
        
        while self.running:
            try:
                self.run_automation_cycle()
                
                # Wait for next cycle
                print(f"😴 Waiting {self.scan_interval} seconds for next cycle...")
                time.sleep(self.scan_interval)
                
            except KeyboardInterrupt:
                print("\n⏹️  Smart automation stopped by user")
                break
            except Exception as e:
                print(f"❌ Automation error: {e}")
                print("🔄 Continuing in 60 seconds...")
                time.sleep(60)
        
        self.running = False
        print("⏹️  Smart Nmap Automation Service Stopped")
    
    def stop_automation(self):
        """Stop the automation service"""
        self.running = False

def main():
    automation = SmartNmapAutomation()
    
    try:
        automation.start_automation()
    except KeyboardInterrupt:
        print("\n⏹️  Stopping automation...")
        automation.stop_automation()

if __name__ == "__main__":
    main()