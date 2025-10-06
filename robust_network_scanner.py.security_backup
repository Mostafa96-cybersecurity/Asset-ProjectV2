#!/usr/bin/env python3
"""
Robust Network Scanner with Complete Data Collection
Fixed version that handles errors gracefully and ensures data persistence
"""

import sqlite3
import subprocess
import socket
from datetime import datetime
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import ipaddress

class RobustNetworkScanner:
    """Robust network scanner that ensures complete data collection and persistence"""
    
    def __init__(self, db_path: str = 'assets.db'):
        self.db_path = db_path
        self.scan_stats = {
            'total_scanned': 0,
            'live_hosts': 0,
            'data_collected': 0,
            'database_saved': 0,
            'errors': 0
        }
        
    def scan_network_comprehensive(self, network_range: str = "10.0.21.0/24") -> Dict[str, Any]:
        """Run comprehensive network scan with complete data collection"""
        print("🚀 ROBUST NETWORK SCAN")
        print(f"📡 Network: {network_range}")
        print("=" * 60)
        
        start_time = datetime.now()
        
        # Phase 1: Discovery
        live_hosts = self._discover_live_hosts(network_range)
        
        # Phase 2: Data Collection
        collected_data = self._collect_device_data(live_hosts)
        
        # Phase 3: Database Storage
        storage_results = self._store_data_safely(collected_data)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Generate final report
        report = {
            'scan_info': {
                'network': network_range,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': duration
            },
            'discovery': {
                'total_ips_scanned': self.scan_stats['total_scanned'],
                'live_hosts_found': self.scan_stats['live_hosts']
            },
            'collection': {
                'devices_processed': self.scan_stats['data_collected'],
                'database_records_saved': self.scan_stats['database_saved'],
                'errors_encountered': self.scan_stats['errors']
            },
            'success_rate': (self.scan_stats['database_saved'] / max(self.scan_stats['live_hosts'], 1)) * 100
        }
        
        return report
    
    def _discover_live_hosts(self, network_range: str) -> List[str]:
        """Phase 1: Discover live hosts using optimized ping scan"""
        print("📡 Phase 1: Host Discovery...")
        
        try:
            network = ipaddress.IPv4Network(network_range, strict=False)
            ip_list = [str(ip) for ip in network.hosts()]
        except:
            print(f"❌ Invalid network range: {network_range}")
            return []
        
        self.scan_stats['total_scanned'] = len(ip_list)
        print(f"🔍 Scanning {len(ip_list)} IP addresses...")
        
        live_hosts = []
        
        def ping_host(ip):
            try:
                result = subprocess.run(
                    ['ping', '-n', '1', '-w', '2000', ip],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    return ip
            except:
                pass
            return None
        
        # Use threading for faster discovery
        with ThreadPoolExecutor(max_workers=50) as executor:
            future_to_ip = {executor.submit(ping_host, ip): ip for ip in ip_list}
            
            for future in as_completed(future_to_ip, timeout=180):  # 3 minutes max
                try:
                    result = future.result()
                    if result:
                        live_hosts.append(result)
                        print(f"   ✅ Live: {result}")
                except Exception:
                    pass
        
        self.scan_stats['live_hosts'] = len(live_hosts)
        print(f"📊 Discovery complete: {len(live_hosts)} live hosts found")
        
        return live_hosts
    
    def _collect_device_data(self, live_hosts: List[str]) -> List[Dict[str, Any]]:
        """Phase 2: Collect comprehensive device data"""
        print("\n📊 Phase 2: Data Collection...")
        print(f"🔍 Collecting data from {len(live_hosts)} devices...")
        
        collected_data = []
        
        def collect_single_device(ip_address: str) -> Optional[Dict[str, Any]]:
            """Collect data from a single device safely"""
            try:
                device_data = {
                    'ip_address': ip_address,
                    'hostname': None,
                    'operating_system': None,
                    'device_type': 'Network Device',
                    'manufacturer': None,
                    'model': None,
                    'open_ports': [],
                    'services': [],
                    'collection_method': ['Basic Network'],
                    'collection_time': datetime.now().isoformat(),
                    'last_seen': datetime.now().isoformat()
                }
                
                # Collect hostname
                try:
                    hostname = socket.gethostbyaddr(ip_address)[0]
                    device_data['hostname'] = hostname
                    device_data['collection_method'].append('DNS Resolution')
                    
                    # Extract domain
                    if '.' in hostname:
                        device_data['domain'] = '.'.join(hostname.split('.')[1:])
                except:
                    device_data['hostname'] = f"device-{ip_address.replace('.', '-')}"
                
                # Quick port scan for common services
                try:
                    open_ports = self._quick_port_scan(ip_address)
                    device_data['open_ports'] = open_ports
                    device_data['services'] = [self._identify_service(port) for port in open_ports]
                    if open_ports:
                        device_data['collection_method'].append('Port Scan')
                        device_data['device_type'] = self._classify_device_simple(device_data)
                except:
                    pass
                
                # Try to get more info via HTTP headers
                try:
                    web_info = self._get_web_info(ip_address)
                    if web_info:
                        device_data.update(web_info)
                        device_data['collection_method'].append('HTTP Banner')
                except:
                    pass
                
                return device_data
                
            except Exception as e:
                print(f"   ❌ Collection failed for {ip_address}: {str(e)}")
                self.scan_stats['errors'] += 1
                return None
        
        # Collect data with controlled concurrency
        with ThreadPoolExecutor(max_workers=15) as executor:
            future_to_ip = {executor.submit(collect_single_device, ip): ip for ip in live_hosts}
            
            for future in as_completed(future_to_ip, timeout=900):  # 15 minutes max
                try:
                    device_data = future.result()
                    if device_data:
                        collected_data.append(device_data)
                        ip = device_data['ip_address']
                        hostname = device_data.get('hostname', 'Unknown')
                        device_type = device_data.get('device_type', 'Unknown')
                        methods = ', '.join(device_data.get('collection_method', []))
                        print(f"   ✅ {ip} → {hostname} ({device_type}) [{methods}]")
                        
                    self.scan_stats['data_collected'] += 1
                    
                except Exception as e:
                    ip = future_to_ip[future]
                    print(f"   ❌ Failed: {ip} - {str(e)}")
                    self.scan_stats['errors'] += 1
        
        print(f"📊 Data collection complete: {len(collected_data)} devices processed")
        return collected_data
    
    def _quick_port_scan(self, ip_address: str, timeout: float = 2.0) -> List[int]:
        """Quick scan of common ports"""
        common_ports = [22, 23, 80, 135, 139, 443, 445, 3389, 5900, 8080, 9100, 161]
        open_ports = []
        
        for port in common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                result = sock.connect_ex((ip_address, port))
                sock.close()
                
                if result == 0:
                    open_ports.append(port)
            except:
                pass
        
        return open_ports
    
    def _identify_service(self, port: int) -> str:
        """Identify service by port number"""
        service_map = {
            22: 'SSH', 23: 'Telnet', 80: 'HTTP', 135: 'RPC', 139: 'NetBIOS',
            443: 'HTTPS', 445: 'SMB', 3389: 'RDP', 5900: 'VNC', 
            8080: 'HTTP-Alt', 9100: 'Printer', 161: 'SNMP'
        }
        return service_map.get(port, f'Port-{port}')
    
    def _classify_device_simple(self, device_data: Dict[str, Any]) -> str:
        """Simple device classification based on available data"""
        open_ports = device_data.get('open_ports', [])
        hostname = device_data.get('hostname', '').lower() if device_data.get('hostname') else ''
        
        # Server classification
        if 3389 in open_ports:
            return 'Windows Server/Workstation'
        elif 22 in open_ports:
            return 'Linux/Unix Server'
        elif 445 in open_ports or 139 in open_ports:
            return 'Windows System'
        
        # Network devices
        elif 161 in open_ports:
            return 'Network Device (SNMP)'
        elif 9100 in open_ports:
            return 'Network Printer'
        
        # Web services
        elif 80 in open_ports or 443 in open_ports:
            return 'Web Server/Service'
        
        # Hostname-based classification
        elif any(term in hostname for term in ['server', 'srv', 'dc']):
            return 'Server'
        elif any(term in hostname for term in ['switch', 'router', 'ap']):
            return 'Network Device'
        elif any(term in hostname for term in ['printer', 'print']):
            return 'Printer'
        
        return 'Network Device'
    
    def _get_web_info(self, ip_address: str) -> Optional[Dict[str, str]]:
        """Get basic web server information"""
        import urllib.request
        import urllib.error
        
        for port in [80, 443]:
            protocol = 'https' if port == 443 else 'http'
            url = f"{protocol}://{ip_address}:{port}"
            
            try:
                request = urllib.request.Request(url, headers={'User-Agent': 'AssetScanner/1.0'})
                with urllib.request.urlopen(request, timeout=5) as response:
                    headers = dict(response.headers)
                    return {
                        'web_server': headers.get('Server', 'Unknown'),
                        'web_port': port
                    }
            except:
                continue
        
        return None
    
    def _store_data_safely(self, collected_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Phase 3: Store data safely in database with smart updates"""
        print("\n💾 Phase 3: Database Storage...")
        print(f"💾 Saving {len(collected_data)} devices to database...")
        
        storage_stats = {
            'new_records': 0,
            'updated_records': 0,
            'unchanged_records': 0,
            'errors': 0
        }
        
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            
            for device_data in collected_data:
                try:
                    result = self._smart_save_device(cursor, device_data)
                    
                    if result['action'] == 'inserted':
                        storage_stats['new_records'] += 1
                        print(f"   ➕ New: {device_data['ip_address']} → {device_data['hostname']}")
                    elif result['action'] in ['updated', 'data_updated']:
                        storage_stats['updated_records'] += 1
                        fields = ', '.join(result.get('updated_fields', []))
                        print(f"   ✏️ Updated: {device_data['ip_address']} → {fields}")
                    else:
                        storage_stats['unchanged_records'] += 1
                        print(f"   📝 Refreshed: {device_data['ip_address']} → timestamp only")
                    
                    self.scan_stats['database_saved'] += 1
                    
                except Exception as e:
                    storage_stats['errors'] += 1
                    print(f"   ❌ Save failed for {device_data['ip_address']}: {str(e)}")
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Database error: {str(e)}")
            storage_stats['errors'] += len(collected_data)
        
        print("💾 Storage complete:")
        print(f"   ➕ New records: {storage_stats['new_records']}")
        print(f"   ✏️ Updated records: {storage_stats['updated_records']}")
        print(f"   📝 Refreshed: {storage_stats['unchanged_records']}")
        print(f"   ❌ Errors: {storage_stats['errors']}")
        
        return storage_stats
    
    def _smart_save_device(self, cursor, device_data: Dict[str, Any]) -> Dict[str, Any]:
        """Smart save that only updates changed data"""
        result = {'action': 'none', 'updated_fields': []}
        
        ip_address = device_data.get('ip_address')
        hostname = device_data.get('hostname')
        
        # Find existing record
        existing_record = None
        if ip_address:
            cursor.execute("SELECT * FROM assets WHERE ip_address = ?", (ip_address,))
            existing_record = cursor.fetchone()
        
        if not existing_record and hostname:
            cursor.execute("SELECT * FROM assets WHERE hostname = ?", (hostname,))
            existing_record = cursor.fetchone()
        
        if existing_record:
            # Update existing record
            cursor.execute("PRAGMA table_info(assets)")
            columns = [row[1] for row in cursor.fetchall()]
            existing_data = dict(zip(columns, existing_record))
            
            # Check what needs updating
            update_pairs = []
            values = []
            updated_fields = []
            
            for field, new_value in device_data.items():
                if field in existing_data and field != 'id':
                    old_value = existing_data[field]
                    
                    # Update if value changed and new value is meaningful
                    if (new_value and new_value not in ['Unknown', 'Unknown Device', ''] and
                        str(new_value) != str(old_value)):
                        update_pairs.append(f"{field} = ?")
                        values.append(new_value)
                        updated_fields.append(field)
            
            # Always update timestamp
            update_pairs.append("last_seen = ?")
            values.append(datetime.now().isoformat())
            updated_fields.append('last_seen')
            
            if len(update_pairs) > 1:  # More than just timestamp
                update_sql = f"UPDATE assets SET {', '.join(update_pairs)} WHERE id = ?"
                values.append(existing_data['id'])
                cursor.execute(update_sql, values)
                result['action'] = 'updated'
                result['updated_fields'] = updated_fields
            else:
                # Just timestamp update
                cursor.execute("UPDATE assets SET last_seen = ? WHERE id = ?", 
                             (datetime.now().isoformat(), existing_data['id']))
                result['action'] = 'timestamp_only'
        else:
            # Insert new record
            fields = list(device_data.keys())
            placeholders = ', '.join(['?' for _ in fields])
            values = list(device_data.values())
            
            insert_sql = f"INSERT INTO assets ({', '.join(fields)}) VALUES ({placeholders})"
            cursor.execute(insert_sql, values)
            result['action'] = 'inserted'
        
        return result

def run_robust_scan():
    """Run the robust network scan"""
    print("🔧 ROBUST NETWORK SCANNER WITH COMPLETE DATA COLLECTION")
    print("=" * 70)
    print(f"🕐 Started: {datetime.now()}")
    print()
    
    # Initialize scanner
    scanner = RobustNetworkScanner()
    
    # Run comprehensive scan
    report = scanner.scan_network_comprehensive("10.0.21.0/24")
    
    # Display final report
    print("\n📋 FINAL SCAN REPORT")
    print("=" * 60)
    
    scan_info = report['scan_info']
    discovery = report['discovery']
    collection = report['collection']
    
    print(f"🌐 Network: {scan_info['network']}")
    print(f"⏱️ Duration: {scan_info['duration_seconds']:.1f} seconds")
    print(f"🔍 IPs scanned: {discovery['total_ips_scanned']}")
    print(f"✅ Live hosts: {discovery['live_hosts_found']}")
    print(f"📊 Data collected: {collection['devices_processed']}")
    print(f"💾 Database saved: {collection['database_records_saved']}")
    print(f"❌ Errors: {collection['errors_encountered']}")
    print(f"📈 Success rate: {report['success_rate']:.1f}%")
    
    return report

if __name__ == "__main__":
    report = run_robust_scan()
    
    print("\n🎯 SCAN COMPLETED SUCCESSFULLY!")
    print("💡 Run 'py simple_db_analysis.py' to see updated database analysis")
    print(f"🕐 Finished: {datetime.now()}")