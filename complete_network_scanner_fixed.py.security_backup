#!/usr/bin/env python3
"""
Complete Network Scanner with Robust Data Persistence

This scanner collects comprehensive network data and ensures all data 
is properly saved to the database using the robust data saver.
"""

import subprocess
import socket
import threading
import time
from datetime import datetime
from robust_data_saver import RobustDataSaver

class CompleteNetworkScanner:
    def __init__(self, network="10.0.21.0/24"):
        self.network = network
        self.live_hosts = []
        self.device_data = {}
        self.data_saver = RobustDataSaver()
        
    def ping_host(self, ip):
        """Ping a single host to check if it's alive"""
        try:
            result = subprocess.run(['ping', '-n', '1', '-w', '1000', ip], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def get_hostname(self, ip):
        """Get hostname via DNS lookup"""
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            return hostname
        except:
            return f"device-{ip.replace('.', '-')}"
    
    def scan_ports(self, ip, ports=[22, 23, 53, 80, 135, 139, 443, 445, 993, 995, 3389]):
        """Scan common ports on a host"""
        open_ports = []
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                result = sock.connect_ex((ip, port))
                if result == 0:
                    open_ports.append(port)
                sock.close()
            except:
                pass
        return open_ports
    
    def get_http_banner(self, ip, port=80):
        """Get HTTP banner if web server is running"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect((ip, port))
            sock.send(b"HEAD / HTTP/1.0\r\n\r\n")
            banner = sock.recv(1024).decode('utf-8', errors='ignore')
            sock.close()
            return banner.split('\n')[0] if banner else None
        except:
            return None
    
    def classify_device(self, ip, hostname, open_ports, http_banner=None):
        """Classify device based on available information"""
        
        # Windows indicators
        if any(port in open_ports for port in [135, 139, 445, 3389]):
            if 3389 in open_ports:
                return "Windows Server/Workstation"
            else:
                return "Windows System"
        
        # Web server indicators
        if 80 in open_ports or 443 in open_ports:
            if http_banner and any(server in http_banner.lower() for server in ['apache', 'nginx', 'iis']):
                return "Web Server/Service"
            elif any(port in open_ports for port in [22, 23]):
                return "Linux/Unix Server"
        
        # SSH indicates Linux/Unix
        if 22 in open_ports:
            return "Linux/Unix Server"
        
        # Printer indicators
        if hostname and 'hp' in hostname.lower() and 80 in open_ports:
            return "Network Printer"
        
        # Network device indicators
        if 23 in open_ports or (not open_ports and hostname):
            return "Network Device"
        
        return "Unknown Device"
    
    def collect_device_data(self, ip):
        """Collect comprehensive data for a device"""
        try:
            # Basic network data
            hostname = self.get_hostname(ip)
            open_ports = self.scan_ports(ip)
            
            # HTTP banner if web server
            http_banner = None
            if 80 in open_ports:
                http_banner = self.get_http_banner(ip, 80)
            
            # Device classification
            device_type = self.classify_device(ip, hostname, open_ports, http_banner)
            
            # Collection methods used
            collection_methods = ["Basic Network", "DNS Resolution"]
            if open_ports:
                collection_methods.append("Port Scan")
            if http_banner:
                collection_methods.append("HTTP Banner")
            
            # Build device data
            device_data = {
                'ip_address': ip,
                'hostname': hostname,
                'device_classification': device_type,
                'open_ports': open_ports,
                'http_banner': http_banner,
                'collection_methods': collection_methods,
                'collection_time': datetime.now().isoformat(),
                'status': 'active',
                'ping_status': 'up',
                'last_ping_check': datetime.now().isoformat()
            }
            
            return device_data
            
        except Exception as e:
            print(f"   Error collecting data for {ip}: {e}")
            return None
    
    def discover_network(self):
        """Discover all live hosts in the network"""
        print("Phase 1: Network Discovery...")
        print(f"Scanning network: {self.network}")
        
        # Extract network range
        base_ip = self.network.split('/')[0]
        base_octets = base_ip.split('.')
        base = '.'.join(base_octets[:3])
        
        # Ping sweep
        threads = []
        results = {}
        
        def ping_worker(ip):
            if self.ping_host(ip):
                results[ip] = True
                print(f"   Live: {ip}")
        
        # Create threads for parallel pinging
        for i in range(1, 255):
            ip = f"{base}.{i}"
            thread = threading.Thread(target=ping_worker, args=(ip,))
            threads.append(thread)
            thread.start()
            
            # Limit concurrent threads
            if len(threads) >= 50:
                for t in threads:
                    t.join()
                threads = []
        
        # Wait for remaining threads
        for thread in threads:
            thread.join()
        
        self.live_hosts = list(results.keys())
        print(f"Discovery complete: {len(self.live_hosts)} live hosts found")
        
        return len(self.live_hosts)
    
    def collect_data(self):
        """Collect data from all discovered hosts"""
        print("\nPhase 2: Data Collection...")
        print(f"Collecting data from {len(self.live_hosts)} devices...")
        
        collected_count = 0
        
        for ip in self.live_hosts:
            device_data = self.collect_device_data(ip)
            if device_data:
                self.device_data[ip] = device_data
                collected_count += 1
                
                # Show collection status
                methods = device_data.get('collection_methods', [])
                device_type = device_data.get('device_classification', 'Unknown')
                hostname = device_data.get('hostname', ip)
                
                print(f"   {ip} -> {hostname} ({device_type}) [{', '.join(methods)}]")
        
        print(f"Data collection complete: {collected_count} devices processed")
        return collected_count
    
    def save_to_database(self):
        """Save all collected data to database using robust saver"""
        print("\nPhase 3: Database Storage...")
        print(f"Saving {len(self.device_data)} devices to database...")
        
        success_count = 0
        
        for ip, device_data in self.device_data.items():
            if self.data_saver.save_device_data(device_data):
                success_count += 1
        
        # Get summary
        summary = self.data_saver.get_summary()
        
        print("Storage complete:")
        print(f"   New records: {summary['new_records']}")
        print(f"   Updated records: {summary['updated_records']}")
        print(f"   Refreshed: {len(self.device_data) - summary['new_records'] - summary['updated_records']}")
        print(f"   Errors: {summary['errors']}")
        
        return summary
    
    def run_complete_scan(self):
        """Run complete network scan with data collection and storage"""
        start_time = time.time()
        
        print("COMPLETE NETWORK SCAN WITH DATA PERSISTENCE")
        print("=" * 60)
        print(f"Network: {self.network}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Phase 1: Discovery
        discovered = self.discover_network()
        
        # Phase 2: Data Collection
        collected = self.collect_data()
        
        # Phase 3: Database Storage
        summary = self.save_to_database()
        
        # Final report
        duration = time.time() - start_time
        success_rate = (summary['new_records'] + summary['updated_records']) / len(self.device_data) * 100 if self.device_data else 0
        
        print("\nFINAL SCAN REPORT")
        print("=" * 60)
        print(f"Network: {self.network}")
        print(f"Duration: {duration:.1f} seconds")
        print("IPs scanned: 254")
        print(f"Live hosts: {discovered}")
        print(f"Data collected: {collected}")
        print(f"Database saved: {summary['new_records'] + summary['updated_records']}")
        print(f"Errors: {summary['errors']}")
        print(f"Success rate: {success_rate:.1f}%")
        print()
        print("SCAN COMPLETED SUCCESSFULLY!")
        print("Run 'py database_integrity_validator.py' to verify data persistence")
        print(f"Finished: {datetime.now()}")

def main():
    """Main function"""
    scanner = CompleteNetworkScanner("10.0.21.0/24")
    scanner.run_complete_scan()

if __name__ == "__main__":
    main()