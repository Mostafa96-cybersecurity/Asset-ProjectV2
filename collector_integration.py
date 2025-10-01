#!/usr/bin/env python3
"""
Enhanced Data Collector Integration
Integrates the enhanced data collector with existing GUI
تكامل جامع البيانات المحسن مع الواجهة الرسومية
"""

import json
import logging
import sqlite3
import subprocess
import socket
import platform
import time
import requests
from datetime import datetime
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - CollectorIntegration - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CollectorIntegration:
    def __init__(self, database_path="assets.db"):
        self.database_path = database_path
        
    def enhance_existing_device_data(self, device_id):
        """Enhance existing device with comprehensive data collection"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Get current device data
            cursor.execute("SELECT * FROM assets WHERE id = ?", (device_id,))
            row = cursor.fetchone()
            
            if not row:
                logger.error(f"Device {device_id} not found")
                return False
            
            # Get column names
            cursor.execute("PRAGMA table_info(assets)")
            columns = [col[1] for col in cursor.fetchall()]
            
            device_data = dict(zip(columns, row))
            target_ip = device_data.get('ip_address')
            
            if not target_ip:
                logger.error(f"Device {device_id} has no IP address")
                return False
            
            logger.info(f"Enhancing device {device_id} ({target_ip}) with comprehensive data")
            
            # Collect enhanced data
            enhanced_data = self.collect_enhanced_data(target_ip, device_data)
            
            # Update database
            self.update_device_with_enhanced_data(device_id, enhanced_data)
            
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Enhancement failed for device {device_id}: {e}")
            return False
    
    def collect_enhanced_data(self, target_ip, existing_data):
        """Collect enhanced data for a device"""
        enhanced_data = {
            'collection_time': datetime.now().isoformat(),
            'collection_source': 'Enhanced Desktop Collector',
            'last_updated': datetime.now().isoformat()
        }
        
        # Network connectivity test
        connectivity_data = self.test_connectivity(target_ip)
        enhanced_data.update(connectivity_data)
        
        # Port scanning
        port_data = self.scan_ports(target_ip)
        enhanced_data.update(port_data)
        
        # Service detection
        service_data = self.detect_services(target_ip, port_data.get('open_ports', []))
        enhanced_data.update(service_data)
        
        # OS fingerprinting
        os_data = self.fingerprint_os(target_ip)
        enhanced_data.update(os_data)
        
        # Performance metrics (if accessible)
        perf_data = self.collect_performance_metrics(target_ip)
        enhanced_data.update(perf_data)
        
        # Security assessment
        security_data = self.assess_security(target_ip, port_data.get('open_ports', []))
        enhanced_data.update(security_data)
        
        # Calculate scores
        enhanced_data['data_quality_score'] = str(self.calculate_data_quality(enhanced_data))
        enhanced_data['performance_score'] = str(self.calculate_performance_score(enhanced_data))
        enhanced_data['risk_score'] = str(self.calculate_risk_score(enhanced_data))
        
        # Set device type if not already set
        if not existing_data.get('device_type') or existing_data.get('device_type') == 'Unknown':
            enhanced_data['device_type'] = self.determine_device_type(enhanced_data, existing_data)
        
        return enhanced_data
    
    def test_connectivity(self, target_ip):
        """Test network connectivity"""
        data = {}
        
        try:
            # Ping test with timing
            start_time = time.time()
            
            if platform.system().lower() == "windows":
                result = subprocess.run(['ping', '-n', '3', target_ip], 
                                      capture_output=True, text=True, timeout=10)
            else:
                result = subprocess.run(['ping', '-c', '3', target_ip], 
                                      capture_output=True, text=True, timeout=10)
            
            end_time = time.time()
            
            if result.returncode == 0:
                data['ping_status'] = 'Online'
                data['availability_status'] = 'Available'
                
                # Extract average response time
                output = result.stdout
                if 'time=' in output:
                    times = []
                    for line in output.split('\n'):
                        if 'time=' in line:
                            try:
                                time_part = line.split('time=')[1].split('ms')[0]
                                times.append(float(time_part))
                            except:
                                pass
                    
                    if times:
                        data['response_time_ms'] = round(sum(times) / len(times), 2)
                        data['ping_response_time'] = data['response_time_ms']
            else:
                data['ping_status'] = 'Offline'
                data['availability_status'] = 'Unavailable'
            
            data['last_ping'] = datetime.now().isoformat()
            data['last_ping_check'] = datetime.now().isoformat()
            
            # Try to resolve hostname
            try:
                hostname, aliases, ip_list = socket.gethostbyaddr(target_ip)
                current_hostname = data.get('hostname')
                if not current_hostname or (isinstance(current_hostname, str) and current_hostname.startswith('device-')):
                    data['hostname'] = hostname
                data['fqdn'] = hostname
                data['dns_names'] = json.dumps(aliases + [hostname])
            except:
                pass
            
        except Exception as e:
            logger.error(f"Connectivity test failed for {target_ip}: {e}")
            data['ping_status'] = 'Error'
            data['availability_status'] = 'Error'
        
        return data
    
    def scan_ports(self, target_ip):
        """Perform port scanning"""
        data = {}
        
        try:
            open_ports = []
            closed_ports = []
            common_ports = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 993, 995, 1433, 1521, 3306, 3389, 5432, 8080, 8443]
            
            for port in common_ports:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                
                try:
                    result = sock.connect_ex((target_ip, port))
                    if result == 0:
                        open_ports.append(port)
                    else:
                        closed_ports.append(port)
                except:
                    closed_ports.append(port)
                finally:
                    sock.close()
            
            data['open_ports'] = json.dumps(open_ports)
            data['closed_ports'] = json.dumps(closed_ports)
            data['listening_ports'] = json.dumps([{'port': p, 'protocol': 'tcp', 'state': 'open'} for p in open_ports])
            
            logger.info(f"Port scan completed for {target_ip}: {len(open_ports)} open ports")
            
        except Exception as e:
            logger.error(f"Port scan failed for {target_ip}: {e}")
        
        return data
    
    def detect_services(self, target_ip, open_ports):
        """Detect services running on open ports"""
        data = {}
        
        try:
            service_map = {
                21: 'FTP',
                22: 'SSH',
                23: 'Telnet',
                25: 'SMTP',
                53: 'DNS',
                80: 'HTTP',
                110: 'POP3',
                135: 'RPC',
                139: 'NetBIOS',
                143: 'IMAP',
                443: 'HTTPS',
                993: 'IMAPS',
                995: 'POP3S',
                1433: 'SQL Server',
                1521: 'Oracle',
                3306: 'MySQL',
                3389: 'RDP',
                5432: 'PostgreSQL',
                8080: 'HTTP-Alt',
                8443: 'HTTPS-Alt'
            }
            
            detected_services = []
            
            if isinstance(open_ports, str):
                open_ports = json.loads(open_ports)
            
            for port in open_ports:
                if port in service_map:
                    detected_services.append({
                        'port': port,
                        'service': service_map[port],
                        'state': 'running'
                    })
            
            data['service_detection'] = json.dumps(detected_services)
            
            # Try to get HTTP headers for web services
            web_services = []
            for port in [80, 443, 8080, 8443]:
                if port in open_ports:
                    try:
                        protocol = 'https' if port in [443, 8443] else 'http'
                        url = f"{protocol}://{target_ip}:{port}"
                        
                        response = requests.get(url, timeout=5, verify=False)
                        web_services.append({
                            'port': port,
                            'server': response.headers.get('Server', 'Unknown'),
                            'status_code': response.status_code
                        })
                    except:
                        pass
            
            if web_services:
                data['web_services'] = json.dumps(web_services)
            
        except Exception as e:
            logger.error(f"Service detection failed for {target_ip}: {e}")
        
        return data
    
    def fingerprint_os(self, target_ip):
        """Attempt OS fingerprinting"""
        data = {}
        
        try:
            # TTL-based OS detection
            if platform.system().lower() == "windows":
                result = subprocess.run(['ping', '-n', '1', target_ip], 
                                      capture_output=True, text=True, timeout=5)
            else:
                result = subprocess.run(['ping', '-c', '1', target_ip], 
                                      capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                output = result.stdout
                if 'TTL=' in output:
                    ttl_line = [line for line in output.split('\n') if 'TTL=' in line][0]
                    ttl = int(ttl_line.split('TTL=')[1].split()[0])
                    
                    # Common TTL values for OS detection
                    if ttl <= 64:
                        os_guess = "Linux/Unix"
                    elif ttl <= 128:
                        os_guess = "Windows"
                    else:
                        os_guess = "Unknown"
                    
                    data['os_fingerprint'] = f"TTL-based: {os_guess} (TTL={ttl})"
            
            # Check for Windows-specific ports
            open_ports_str = data.get('open_ports', '[]')
            open_ports = json.loads(open_ports_str) if isinstance(open_ports_str, str) else open_ports_str
            
            if 135 in open_ports or 3389 in open_ports:
                data['os_fingerprint'] = "Windows (RPC/RDP detected)"
            elif 22 in open_ports and 135 not in open_ports:
                data['os_fingerprint'] = "Linux/Unix (SSH detected)"
            
        except Exception as e:
            logger.error(f"OS fingerprinting failed for {target_ip}: {e}")
        
        return data
    
    def collect_performance_metrics(self, target_ip):
        """Collect basic performance metrics if possible"""
        data = {}
        
        try:
            # SNMP-based performance collection (if SNMP is available)
            # This is a simplified version
            
            # Try to get system uptime via SNMP
            try:
                import subprocess
                result = subprocess.run(['snmpget', '-v1', '-c', 'public', target_ip, '1.3.6.1.2.1.1.3.0'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    uptime_info = result.stdout
                    data['snmp_sys_uptime'] = uptime_info.strip()
            except:
                pass
            
            # Basic network performance test
            start_time = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            
            try:
                result = sock.connect_ex((target_ip, 80))
                end_time = time.time()
                
                if result == 0:
                    connection_time = round((end_time - start_time) * 1000, 2)
                    data['network_performance'] = f"Connection time: {connection_time}ms"
            except:
                pass
            finally:
                sock.close()
            
        except Exception as e:
            logger.error(f"Performance metrics collection failed for {target_ip}: {e}")
        
        return data
    
    def assess_security(self, target_ip, open_ports):
        """Perform basic security assessment"""
        data = {}
        
        try:
            security_issues = []
            security_score = 5  # Base score out of 10
            
            if isinstance(open_ports, str):
                open_ports = json.loads(open_ports)
            
            # Check for risky open ports
            risky_ports = {
                21: "FTP (unencrypted)",
                23: "Telnet (unencrypted)", 
                135: "RPC (potential attack vector)",
                139: "NetBIOS (information disclosure)",
                1433: "SQL Server (database exposure)",
                3306: "MySQL (database exposure)",
                5432: "PostgreSQL (database exposure)"
            }
            
            for port in open_ports:
                if port in risky_ports:
                    security_issues.append(f"Port {port}: {risky_ports[port]}")
                    security_score -= 0.5
            
            # Check for too many open ports
            if len(open_ports) > 10:
                security_issues.append(f"Many open ports ({len(open_ports)}) - potential attack surface")
                security_score -= 1
            
            # Check for good security practices
            if 22 in open_ports and 23 not in open_ports:
                security_score += 0.5  # SSH instead of Telnet
                
            if 443 in open_ports:
                security_score += 0.5  # HTTPS available
            
            data['security_assessment'] = json.dumps(security_issues)
            data['security_score'] = max(1, min(10, round(security_score)))
            
            # Try to detect firewall
            closed_ports_str = data.get('closed_ports', '[]')
            closed_ports = json.loads(closed_ports_str) if isinstance(closed_ports_str, str) else []
            
            if len(closed_ports) > len(open_ports):
                data['firewall_detected'] = 'Likely'
            else:
                data['firewall_detected'] = 'Unknown'
            
        except Exception as e:
            logger.error(f"Security assessment failed for {target_ip}: {e}")
        
        return data
    
    def calculate_data_quality(self, data):
        """Calculate data quality score (1-5)"""
        score = 1
        
        # Basic connectivity
        if data.get('ping_status') == 'Online':
            score += 1
        
        # Port scan results
        if data.get('open_ports'):
            score += 1
        
        # Service detection
        if data.get('service_detection'):
            score += 1
        
        # OS fingerprinting
        if data.get('os_fingerprint'):
            score += 1
        
        return min(5, score)
    
    def calculate_performance_score(self, data):
        """Calculate performance score (1-10)"""
        score = 5  # Base score
        
        # Response time factor
        response_time = data.get('response_time_ms', 100)
        if response_time < 10:
            score += 2
        elif response_time < 50:
            score += 1
        elif response_time > 200:
            score -= 1
        
        # Connection time factor
        if 'network_performance' in data:
            try:
                perf_info = data['network_performance']
                if 'Connection time:' in perf_info:
                    conn_time = float(perf_info.split('Connection time: ')[1].split('ms')[0])
                    if conn_time < 50:
                        score += 1
                    elif conn_time > 200:
                        score -= 1
            except:
                pass
        
        return max(1, min(10, score))
    
    def calculate_risk_score(self, data):
        """Calculate security risk score (1-10)"""
        score = 3  # Base score
        
        # Open ports factor
        open_ports_str = data.get('open_ports', '[]')
        try:
            open_ports = json.loads(open_ports_str) if isinstance(open_ports_str, str) else open_ports_str
            if len(open_ports) > 10:
                score += 3
            elif len(open_ports) > 5:
                score += 1
        except:
            pass
        
        # Security issues factor
        security_assessment = data.get('security_assessment', '[]')
        try:
            security_issues = json.loads(security_assessment) if isinstance(security_assessment, str) else security_assessment
            score += len(security_issues)
        except:
            pass
        
        # Firewall detection
        if data.get('firewall_detected') == 'Likely':
            score -= 1
        
        return max(1, min(10, score))
    
    def determine_device_type(self, enhanced_data, existing_data):
        """Determine device type based on enhanced data"""
        # Check service detection
        service_detection = enhanced_data.get('service_detection', '[]')
        try:
            services = json.loads(service_detection) if isinstance(service_detection, str) else service_detection
            service_names = [s.get('service', '') for s in services]
            
            if 'HTTP' in service_names or 'HTTPS' in service_names:
                if any(db in service_names for db in ['MySQL', 'PostgreSQL', 'SQL Server']):
                    return 'Server'
                else:
                    return 'Web Server'
            
            if 'SSH' in service_names:
                return 'Server'
            
            if 'RDP' in service_names:
                return 'Desktop'
            
        except:
            pass
        
        # Check OS fingerprint
        os_fingerprint = enhanced_data.get('os_fingerprint', '')
        if 'Windows' in os_fingerprint:
            return 'Desktop'
        elif 'Linux' in os_fingerprint:
            return 'Server'
        
        # Check open ports
        open_ports_str = enhanced_data.get('open_ports', '[]')
        try:
            open_ports = json.loads(open_ports_str) if isinstance(open_ports_str, str) else open_ports_str
            
            if 3389 in open_ports:  # RDP
                return 'Desktop'
            elif 80 in open_ports or 443 in open_ports:  # Web
                return 'Web Server'
            elif 22 in open_ports:  # SSH
                return 'Server'
            elif 135 in open_ports:  # Windows RPC
                return 'Desktop'
                
        except:
            pass
        
        return 'Unknown'
    
    def update_device_with_enhanced_data(self, device_id, enhanced_data):
        """Update device in database with enhanced data"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Get current column names
            cursor.execute("PRAGMA table_info(assets)")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Prepare update query
            update_fields = []
            update_values = []
            
            for key, value in enhanced_data.items():
                if key in columns:
                    update_fields.append(f"{key} = ?")
                    update_values.append(value)
            
            if update_fields:
                update_values.append(device_id)
                update_sql = f"UPDATE assets SET {', '.join(update_fields)} WHERE id = ?"
                
                cursor.execute(update_sql, update_values)
                conn.commit()
                
                logger.info(f"Enhanced data updated for device {device_id}")
            
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Database update failed for device {device_id}: {e}")
            return False

def main():
    """Test the collector integration"""
    integration = CollectorIntegration()
    
    # Test with device ID 1
    success = integration.enhance_existing_device_data(1)
    print(f"Enhancement {'successful' if success else 'failed'}")

if __name__ == "__main__":
    main()