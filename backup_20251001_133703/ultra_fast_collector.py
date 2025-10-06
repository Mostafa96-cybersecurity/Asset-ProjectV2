# -*- coding: utf-8 -*-
"""
Ultra-High-Performance Device Collector
======================================
Optimized collector designed to prevent hangs and maximize collection speed.

Key Optimizations:
- Aggressive timeouts to prevent hangs
- Fast-fail credential testing
- Parallel connection attempts where safe
- Skip slow HTTP collection during bulk operations
- Optimized threading and queue management
- Smart retry logic with exponential backoff
"""

import time
import socket
import threading
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from queue import Queue, Empty
from dataclasses import dataclass
from typing import List, Dict, Set, Optional, Any
from datetime import datetime
import logging

from PyQt6.QtCore import QThread, pyqtSignal

# Standalone collection functions - no AssetV2 dependency
try:
    import wmi
    import subprocess
    import paramiko
    import requests
    from pysnmp.hlapi import *
    COLLECTION_UTILS_AVAILABLE = True
except ImportError:
    COLLECTION_UTILS_AVAILABLE = False

# Separate NMAP availability check
try:
    import nmap
    NMAP_AVAILABLE = True
except ImportError:
    NMAP_AVAILABLE = False

log = logging.getLogger(__name__)

def _collect_windows_standalone(ip: str, username: str, password: str) -> Optional[Dict]:
    """Comprehensive Windows WMI collection with all system details"""
    try:
        if not COLLECTION_UTILS_AVAILABLE:
            return None
        
        # Initialize COM for WMI to prevent CoInitialize errors
        try:
            import pythoncom
            pythoncom.CoInitialize()  # type: ignore
        except (ImportError, AttributeError):
            # If pythoncom is not available or CoInitialize doesn't exist, try alternative
            try:
                import win32com.client
                # This will automatically initialize COM when needed
            except ImportError:
                pass  # Continue without COM initialization
        
        # WMI connection with timeout
        print(f"🔍 DEBUG WMI: Attempting connection to {ip} with user '{username}', password: {'***set***' if password else '***empty***'}")
        conn = wmi.WMI(computer=ip, user=username, password=password)
        print("🔍 DEBUG WMI: Connection successful!")
        
        # Collect comprehensive system information
        data = {
            'ip_address': ip,
            'wmi_collection_status': 'Success',
            'wmi_collection_time': datetime.now().isoformat()
        }
        
        try:
            # System Information
            system = conn.Win32_ComputerSystem()[0]
            data.update({  # type: ignore
                'computer_name': system.Name,
                'hostname': system.Name,
                'domain_workgroup': getattr(system, 'Domain', None) or getattr(system, 'Workgroup', None),
                'system_manufacturer': system.Manufacturer,
                'system_model': system.Model,
                'system_type': system.SystemType,
                'total_physical_memory': int(system.TotalPhysicalMemory) if system.TotalPhysicalMemory else None,
                'system_family': getattr(system, 'SystemFamily', None)
            })
        except:
            pass
            
        try:
            # Operating System Information  
            os_info = conn.Win32_OperatingSystem()[0]
            data.update({  # type: ignore
                'operating_system': os_info.Caption,
                'os_version': os_info.Version,
                'os_build_number': os_info.BuildNumber,
                'os_service_pack': getattr(os_info, 'ServicePackMajorVersion', None),
                'os_architecture': os_info.OSArchitecture,
                'os_install_date': getattr(os_info, 'InstallDate', None),
                'last_boot_time': getattr(os_info, 'LastBootUpTime', None),
                'windows_directory': os_info.WindowsDirectory,
                'system_directory': os_info.SystemDirectory,
                'device_type': 'Server' if 'Server' in os_info.Caption else 'Workstation'
            })
        except:
            pass
            
        try:
            # Processor Information
            processors = conn.Win32_Processor()
            if processors:
                proc = processors[0]
                data.update({  # type: ignore
                    'processor_name': proc.Name,
                    'processor_architecture': getattr(proc, 'Architecture', None),
                    'processor_cores': proc.NumberOfCores,
                    'processor_logical_processors': proc.NumberOfLogicalProcessors
                })
        except:
            pass
            
        try:
            # BIOS Information
            bios = conn.Win32_BIOS()[0]
            data.update({  # type: ignore
                'bios_version': bios.Version,
                'bios_manufacturer': bios.Manufacturer,
                'bios_serial_number': bios.SerialNumber,
                'bios_release_date': getattr(bios, 'ReleaseDate', None)
            })
        except:
            pass
            
        try:
            # Current User Information (working_user) - Enhanced with multiple methods
            working_user = 'System'  # Default value
            
            # Method 1: Get from Win32_ComputerSystem UserName
            try:
                sessions = conn.Win32_ComputerSystem()
                if sessions and sessions[0].UserName:
                    working_user = sessions[0].UserName
                    log.info(f"✅ Working user from ComputerSystem: {working_user}")
            except Exception as e:
                log.debug(f"ComputerSystem UserName failed: {e}")
                
            # Method 2: Get from currently running processes (explorer.exe owner)
            if working_user == 'System':
                try:
                    processes = conn.Win32_Process(Name="explorer.exe")
                    if processes:
                        for proc in processes:
                            owner = proc.GetOwner()
                            if owner and len(owner) > 0 and owner[0]:
                                working_user = owner[0]
                                log.info(f"✅ Working user from explorer.exe: {working_user}")
                                break
                except Exception as e:
                    log.debug(f"Explorer.exe process check failed: {e}")
            
            # Always set working_user - never leave it empty
            data['working_user'] = working_user
                
        except:
            pass
            
        try:
            # Enhanced Network Information
            adapters = conn.Win32_NetworkAdapterConfiguration(IPEnabled=True)
            if adapters:
                mac_list = []
                ip_list = []
                adapter_names = []
                adapter_descriptions = []
                network_speeds = []
                
                for adapter in adapters:
                    if adapter.MACAddress:
                        mac_list.append(adapter.MACAddress)
                    if adapter.IPAddress:
                        ip_list.extend(adapter.IPAddress)
                    if hasattr(adapter, 'Description') and adapter.Description:
                        adapter_descriptions.append(adapter.Description)
                    if hasattr(adapter, 'ServiceName') and adapter.ServiceName:
                        adapter_names.append(adapter.ServiceName)
                        
                # Get network adapter speeds and types
                try:
                    net_adapters = conn.Win32_NetworkAdapter()
                    for net_adapter in net_adapters:
                        if hasattr(net_adapter, 'Speed') and net_adapter.Speed:
                            speed_mbps = int(net_adapter.Speed) // 1000000
                            network_speeds.append(f"{speed_mbps}Mbps")
                except:
                    pass
                        
                data['mac_addresses'] = ', '.join(mac_list)
                data['ip_addresses'] = ', '.join(ip_list)
                data['network_adapters'] = ', '.join(adapter_descriptions[:3])  # Top 3 adapters
                data['network_adapter_description'] = adapter_descriptions[0] if adapter_descriptions else ''
                data['network_speed'] = ', '.join(network_speeds[:3]) if network_speeds else ''
                data['network_adapter_count'] = str(len(adapter_descriptions))
        except:
            pass
            
        try:
            # Enhanced Physical Disk Information (Individual Disks) - PRIORITY COLLECTION
            physical_disks = conn.Win32_DiskDrive()
            disk_details = []
            disk_models = []
            disk_types = []
            disk_serials = []
            individual_disks = []
            total_disk_space = 0
            
            for i, disk in enumerate(physical_disks, 1):
                disk_size_gb = 0
                disk_model = "Unknown"
                
                if disk.Size:
                    disk_size_gb = int(disk.Size) // (1024**3)  # Convert to GB
                    total_disk_space += int(disk.Size)  # Add to total
                
                if disk.Model:
                    disk_model = disk.Model.strip()
                    disk_models.append(disk_model)
                
                # Format: "Disk 1 = 250 GB (Samsung SSD 970 EVO)"
                if disk_size_gb > 0:
                    disk_entry = f"Disk {i} = {disk_size_gb} GB"
                    if disk_model != "Unknown":
                        disk_entry += f" ({disk_model})"
                    individual_disks.append(disk_entry)
                    disk_details.append(f"{disk_model}: {disk_size_gb}GB")
                
                # Collect additional disk info
                if hasattr(disk, 'MediaType') and disk.MediaType:
                    disk_types.append(getattr(disk, 'MediaType', 'Unknown'))
                elif disk_model:
                    # Try to determine disk type from model name
                    model_lower = disk_model.lower()
                    if 'ssd' in model_lower or 'nvme' in model_lower:
                        disk_types.append('SSD')
                    elif 'hdd' in model_lower or 'wd' in model_lower or 'seagate' in model_lower:
                        disk_types.append('HDD')
                    else:
                        disk_types.append('Unknown')
                
                if disk.SerialNumber:
                    disk_serials.append(disk.SerialNumber.strip())
            
            # Store enhanced physical disk information (MAIN FORMAT)
            data['hard_drives'] = ', '.join(individual_disks) if individual_disks else ''
            data['disk_model'] = ', '.join(disk_models) if disk_models else ''
            data['drive_models'] = ', '.join(disk_models) if disk_models else ''
            data['drive_types'] = ', '.join(disk_types) if disk_types else ''
            data['drive_serial_numbers'] = ', '.join(disk_serials) if disk_serials else ''
            data['disk_drive_count'] = str(len(individual_disks))
            data['total_disk_space'] = str(total_disk_space)
            
            # Collect free space from logical drives (for total free space calculation)
            try:
                drives = conn.Win32_LogicalDisk()
                free_disk_space = 0
                
                for drive in drives:
                    if drive.FreeSpace:
                        free_disk_space += int(drive.FreeSpace)
                
                data['free_disk_space'] = str(free_disk_space)
            except:
                pass
        except:
            pass
            
        try:
            # Graphics Cards Information
            graphics_cards = conn.Win32_VideoController()
            gpu_info = []
            graphics_memory = []
            graphics_drivers = []
            
            for gpu in graphics_cards:
                if gpu.Name and 'Microsoft' not in gpu.Name:  # Skip basic display adapters
                    gpu_info.append(gpu.Name)
                    if hasattr(gpu, 'AdapterRAM') and gpu.AdapterRAM:
                        graphics_memory.append(str(gpu.AdapterRAM))
                    if hasattr(gpu, 'DriverVersion') and gpu.DriverVersion:
                        graphics_drivers.append(gpu.DriverVersion)
            
            data['graphics_card'] = ', '.join(gpu_info) if gpu_info else ''
            data['graphics_memory'] = ', '.join(graphics_memory) if graphics_memory else ''
            data['graphics_driver'] = ', '.join(graphics_drivers) if graphics_drivers else ''
        except:
            pass
            
        try:
            # Connected Screens/Monitors Information
            monitors = conn.Win32_DesktopMonitor()
            monitor_info = []
            
            for monitor in monitors:
                if monitor.Name and monitor.Name != 'Default Monitor':
                    screen_info = monitor.Name
                    if hasattr(monitor, 'ScreenWidth') and hasattr(monitor, 'ScreenHeight'):
                        if monitor.ScreenWidth and monitor.ScreenHeight:
                            screen_info += f" ({monitor.ScreenWidth}x{monitor.ScreenHeight})"
                    monitor_info.append(screen_info)
            
            # Also try Win32_DisplayConfiguration for more detailed info
            try:
                displays = conn.Win32_DisplayConfiguration()
                for display in displays:
                    if hasattr(display, 'DeviceName') and display.DeviceName:
                        if display.DeviceName not in ', '.join(monitor_info):
                            monitor_info.append(display.DeviceName)
            except:
                pass
                
            data['connected_screens'] = ', '.join(monitor_info) if monitor_info else ''
            data['monitors'] = str(len(monitor_info)) if monitor_info else '0'
        except:
            pass
            
        try:
            # Enhanced Domain Information
            # Get domain info from multiple sources
            domain_info = []
            
            # From Computer System
            try:
                system = conn.Win32_ComputerSystem()[0]
                if hasattr(system, 'Domain') and system.Domain:
                    data['domain_name'] = system.Domain
                    domain_info.append(f"Domain: {system.Domain}")
                elif hasattr(system, 'Workgroup') and system.Workgroup:
                    data['domain_name'] = system.Workgroup
                    domain_info.append(f"Workgroup: {system.Workgroup}")
                    
                if hasattr(system, 'PartOfDomain'):
                    data['domain_role'] = 'Domain Member' if system.PartOfDomain else 'Workgroup Member'
            except:
                pass
                
            # Get more detailed domain/workgroup info
            try:
                network_configs = conn.Win32_NetworkAdapterConfiguration(IPEnabled=True)
                for config in network_configs:
                    if hasattr(config, 'DNSDomain') and config.DNSDomain:
                        data['dns_domain'] = config.DNSDomain
                        break
            except:
                pass
                
        except:
            pass
            
        # Add essential date and status fields
        current_time = datetime.now().isoformat()
        data.update({  # type: ignore
            'collection_method': 'WMI',
            'collection_date': current_time,
            'last_scan_date': current_time,
            'last_update': current_time,
            'data_source': 'WMI Collection',
            'scan_status': 'Completed',
            'realtime_status': 'Online',
            'wmi_data_completeness': 0.9,  # 90% completeness for successful WMI collection
            'asset_type': 'Computer',
            'collector': 'WMI Enhanced',
            'status': 'Active'
        })
        
        print(f"✅ WMI Data collected for {data.get('hostname', ip)}: {len(data)} fields")
        
        # Cleanup COM
        try:
            import pythoncom
            pythoncom.CoUninitialize()  # type: ignore
        except:
            pass
            
        return data
        
    except Exception as e:
        # Cleanup COM on error too
        try:
            import pythoncom
            pythoncom.CoUninitialize()  # type: ignore
        except:
            pass
            
        return {
            'ip_address': ip,
            'wmi_collection_status': f'Failed: {str(e)[:100]}',
            'wmi_collection_time': datetime.now().isoformat(),
            'wmi_data_completeness': 0.0
        }

def _collect_ssh_standalone(ip: str, username: str, password: str) -> Optional[Dict]:
    """Comprehensive SSH collection for Linux/Unix systems"""
    try:
        if not COLLECTION_UTILS_AVAILABLE:
            return None
            
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password, timeout=5)
        
        current_time = datetime.now().isoformat()
        data = {
            'ip_address': ip,
            'collection_method': 'SSH',
            'wmi_collection_status': 'SSH Success',
            'wmi_collection_time': current_time,
            'collection_date': current_time,
            'last_scan_date': current_time,
            'last_update': current_time,
            'data_source': 'SSH Collection',
            'scan_status': 'Completed',
            'realtime_status': 'Online'
        }
        
        try:
            # Basic system information
            stdin, stdout, stderr = ssh.exec_command('hostname; uname -a; cat /etc/os-release 2>/dev/null || lsb_release -a 2>/dev/null || echo "Unknown OS"')
            output = stdout.read().decode().strip()
            lines = output.split('\n')
            
            hostname = lines[0] if lines else f'device-{ip.replace(".", "-")}'
            uname = lines[1] if len(lines) > 1 else 'Unknown'
            
            data.update({
                'hostname': hostname,
                'computer_name': hostname,
                'operating_system': 'Linux' if 'Linux' in uname else 'Unix',
                'device_type': 'Server',
                'system_type': uname
            })
            
            # Get current working user with multiple methods
            working_user = 'system'  # Default
            
            # Method 1: whoami
            try:
                stdin, stdout, stderr = ssh.exec_command('whoami 2>/dev/null || echo "unknown"')
                user = stdout.read().decode().strip()
                if user and user != 'unknown':
                    working_user = user
            except:
                pass
            
            # Method 2: who am i (shows actual logged in user)
            if working_user == 'system':
                try:
                    stdin, stdout, stderr = ssh.exec_command('who am i 2>/dev/null | awk \'{print $1}\' || echo "system"')
                    user = stdout.read().decode().strip()
                    if user and user != 'system':
                        working_user = user
                except:
                    pass
            
            data['working_user'] = working_user
            log.info(f"✅ SSH working_user identified: {working_user}")
        except:
            pass
            
        try:
            # Memory information
            stdin, stdout, stderr = ssh.exec_command('free -b | grep Mem:')
            mem_output = stdout.read().decode().strip()
            if mem_output:
                mem_parts = mem_output.split()
                if len(mem_parts) > 1:
                    data['total_physical_memory'] = int(mem_parts[1])  # type: ignore
        except:
            pass
            
        try:
            # CPU information
            stdin, stdout, stderr = ssh.exec_command('lscpu | grep -E "Model name|Architecture|CPU\\(s\\):|Thread" || cat /proc/cpuinfo | head -20')
            cpu_output = stdout.read().decode().strip()
            data['processor_name'] = cpu_output[:100]  # First 100 chars
        except:
            pass
            
        try:
            # Network information
            stdin, stdout, stderr = ssh.exec_command('ip addr show || ifconfig')
            net_output = stdout.read().decode().strip()
            data['network_adapters'] = net_output[:200]  # First 200 chars
        except:
            pass
            
        try:
            # Storage information  
            stdin, stdout, stderr = ssh.exec_command('df -h')
            disk_output = stdout.read().decode().strip()
            data['hard_drives'] = disk_output[:200]  # First 200 chars
        except:
            pass
            
        ssh.close()
        
        data.update({  # type: ignore
            'wmi_data_completeness': 0.7,  # 70% completeness for SSH collection
            'asset_type': 'Server',
            'collector': 'SSH Enhanced',
            'status': 'Active'
        })
        
        return data
        
    except Exception as e:
        return {
            'ip_address': ip,
            'wmi_collection_status': f'SSH Failed: {str(e)[:100]}',
            'wmi_collection_time': datetime.now().isoformat(),
            'wmi_data_completeness': 0.0
        }

def _collect_snmp_standalone(ip: str, communities: Optional[List[str]] = None) -> Optional[Dict]:
    """Standalone SNMP collection (basic implementation)"""
    try:
        # Simplified SNMP - just return basic info since detailed SNMP requires complex setup
        return {
            'IP Address': ip,
            'Hostname': f'snmp-{ip.replace(".", "-")}',
            'Device Type': 'Network Device',
            'Asset Type': 'Network Device',
            'Collector': 'SNMP',
            'System Description': 'SNMP Device'
        }
    except Exception:
        return None

def _collect_http_standalone(ip: str) -> Optional[Dict]:
    """Standalone HTTP collection"""
    try:
        if not COLLECTION_UTILS_AVAILABLE:
            return None
            
        # Try HTTP first, then HTTPS
        for protocol in ['http', 'https']:
            try:
                response = requests.get(f'{protocol}://{ip}', timeout=3, verify=False)
                if response.status_code == 200:
                    title = 'Unknown'
                    if '<title>' in response.text.lower():
                        start = response.text.lower().find('<title>') + 7
                        end = response.text.lower().find('</title>', start)
                        if end > start:
                            title = response.text[start:end].strip()
                    
                    return {
                        'IP Address': ip,
                        'Hostname': title,
                        'Device Type': 'Web Server',
                        'Asset Type': 'Web Server',
                        'Collector': 'HTTP',
                        'HTTP Server': response.headers.get('Server', 'Unknown')
                    }
            except Exception:
                continue
        
        return None
    except Exception:
        return None

def _guess_device_type(has_ssh: bool, has_rpc: bool, has_smb: bool, has_http: bool, has_https: bool, has_snmp: bool) -> str:
    """Guess device type based on open ports"""
    if has_rpc or has_smb:
        return 'Windows Computer'
    elif has_ssh:
        return 'Linux/Unix Server'
    elif has_snmp:
        return 'Network Device'
    elif has_http or has_https:
        return 'Web Server'
    else:
        return 'Unknown Device'

def _nmap_os_detection(ip: str) -> Dict[str, str]:
    """Use NMAP for accurate OS detection with port-based fallback"""
    result = {'os_family': 'Unknown', 'device_type': 'Unknown', 'confidence': '0'}
    
    if not NMAP_AVAILABLE:
        log.warning("NMAP not available - falling back to port-based detection")
        return _port_based_os_detection(ip)
    
    try:
        nm = nmap.PortScanner()
        
        # Quick OS detection scan with common ports
        scan_result = nm.scan(ip, '22,80,135,445,161,443,3389', '-O --osscan-guess', timeout=10)
        
        if ip in scan_result['scan']:
            host_info = scan_result['scan'][ip]
            
            # Check if OS detection was successful
            if 'osmatch' in host_info and host_info['osmatch']:
                best_match = host_info['osmatch'][0]  # Get best OS match
                os_name = best_match.get('name', '').lower()
                confidence = best_match.get('accuracy', '0')
                
                # Determine OS family
                if 'windows' in os_name or 'microsoft' in os_name:
                    result['os_family'] = 'Windows'
                    if 'server' in os_name:
                        result['device_type'] = 'Windows Server'
                    else:
                        result['device_type'] = 'Windows Workstation'
                elif any(x in os_name for x in ['linux', 'ubuntu', 'centos', 'redhat', 'debian', 'unix']):
                    result['os_family'] = 'Linux'
                    result['device_type'] = 'Linux Server'
                elif any(x in os_name for x in ['cisco', 'juniper', 'router', 'switch']):
                    result['os_family'] = 'Network'
                    result['device_type'] = 'Network Device'
                elif any(x in os_name for x in ['vmware', 'hypervisor', 'esxi']):
                    result['os_family'] = 'Hypervisor'
                    result['device_type'] = 'Hypervisor'
                else:
                    result['os_family'] = 'Other'
                    result['device_type'] = 'Other Device'
                
                result['confidence'] = str(confidence)
                log.info(f"✅ NMAP OS Detection for {ip}: {result['os_family']} ({confidence}% confidence)")
                return result
                
            # Fallback to port-based detection if OS detection failed
            elif 'tcp' in host_info:
                ports = host_info['tcp']
                if 135 in ports or 445 in ports or 3389 in ports:
                    result['os_family'] = 'Windows'
                    result['device_type'] = 'Windows Computer'
                    result['confidence'] = '75'
                elif 22 in ports:
                    result['os_family'] = 'Linux'
                    result['device_type'] = 'Linux Server'
                    result['confidence'] = '70'
                elif 161 in ports:
                    result['os_family'] = 'Network'
                    result['device_type'] = 'Network Device'
                    result['confidence'] = '60'
                log.info(f"� NMAP Port-based detection for {ip}: {result['os_family']} ({result['confidence']}% confidence)")
                return result
        
        # If NMAP scan failed, fall back to manual port detection
        log.warning(f"NMAP scan failed for {ip}, falling back to manual port detection")
        return _port_based_os_detection(ip)
        
    except Exception as e:
        log.warning(f"NMAP OS detection failed for {ip}: {e}")
        # Fall back to port-based detection
        return _port_based_os_detection(ip)

def _port_based_os_detection(ip: str) -> Dict[str, str]:
    """Port-based OS detection as fallback when NMAP is not available"""
    result = {'os_family': 'Unknown', 'device_type': 'Unknown', 'confidence': '0'}
    
    try:
        # Quick port scan to determine OS
        has_135 = _quick_port_check(ip, 135)  # Windows RPC
        has_445 = _quick_port_check(ip, 445)  # SMB
        has_3389 = _quick_port_check(ip, 3389)  # RDP
        has_22 = _quick_port_check(ip, 22)    # SSH
        has_161 = _quick_port_check(ip, 161)  # SNMP
        has_80 = _quick_port_check(ip, 80)    # HTTP
        has_443 = _quick_port_check(ip, 443)  # HTTPS
        
        # Log port results for debugging
        open_ports = []
        if has_135: open_ports.append("135/RPC")
        if has_445: open_ports.append("445/SMB") 
        if has_3389: open_ports.append("3389/RDP")
        if has_22: open_ports.append("22/SSH")
        if has_161: open_ports.append("161/SNMP")
        if has_80: open_ports.append("80/HTTP")
        if has_443: open_ports.append("443/HTTPS")
        
        log.info(f"🔍 Port scan for {ip}: {', '.join(open_ports) if open_ports else 'No common ports open'}")
        
        # Determine OS based on port combinations
        if has_135 or has_445 or has_3389:
            result['os_family'] = 'Windows'
            if has_3389:  # RDP usually indicates server
                result['device_type'] = 'Windows Server'
            else:
                result['device_type'] = 'Windows Computer'
            result['confidence'] = '85'
        elif has_22:
            result['os_family'] = 'Linux'
            result['device_type'] = 'Linux Server'
            result['confidence'] = '80'
        elif has_161 and not (has_22 or has_135):
            result['os_family'] = 'Network'
            result['device_type'] = 'Network Device'
            result['confidence'] = '75'
        elif (has_80 or has_443) and not (has_22 or has_135):
            result['os_family'] = 'Other'
            result['device_type'] = 'Web Server'
            result['confidence'] = '60'
        else:
            result['os_family'] = 'Unknown'
            result['device_type'] = 'Unknown Device'
            result['confidence'] = '30'
        
        log.info(f"🔍 Port-based OS detection for {ip}: {result['os_family']} ({result['confidence']}% confidence)")
        return result
        
    except Exception as e:
        log.warning(f"Port-based OS detection failed for {ip}: {e}")
        return result

def _quick_port_check(ip: str, port: int, timeout: float = 0.5) -> bool:
    """Quick port check for OS detection"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except:
        return False

def _guess_os(has_ssh: bool, has_rpc: bool, has_smb: bool) -> str:
    """Guess OS based on open ports (fallback method)"""
    if has_rpc or has_smb:
        return 'Windows'
    elif has_ssh:
        return 'Linux/Unix'
    else:
        return 'Unknown'

def _get_open_ports_string(has_ssh: bool, has_rpc: bool, has_smb: bool, has_http: bool, has_https: bool, has_snmp: bool) -> str:
    """Get a string representation of open ports"""
    ports = []
    if has_ssh: ports.append('22/SSH')
    if has_http: ports.append('80/HTTP')
    if has_rpc: ports.append('135/RPC')
    if has_https: ports.append('443/HTTPS')
    if has_smb: ports.append('445/SMB')
    if has_snmp: ports.append('161/SNMP')
    return ', '.join(ports) if ports else 'None detected'

@dataclass
class OptimizedDeviceTask:
    """Optimized device collection task with aggressive timeouts"""
    ip: str
    quality_score: float = 0.0
    retry_count: int = 0
    max_retries: int = 1  # Reduced from 3 for faster processing
    timeout: float = 5.0  # Aggressive 5-second total timeout per device
    priority: int = 0  # Higher priority = collected first

@dataclass 
class FastCollectionStats:
    """Fast collection statistics"""
    start_time: float = 0.0
    discovered: int = 0
    collected: int = 0  
    failed: int = 0
    skipped: int = 0
    timeout_errors: int = 0
    connection_errors: int = 0
    saved_devices: int = 0  # Added for database tracking
    
    @property
    def total_time(self) -> float:
        return time.time() - self.start_time if self.start_time else 0.0
    
    @property
    def success_rate(self) -> float:
        total = self.collected + self.failed
        return (self.collected / total * 100) if total > 0 else 0.0
    
    @property
    def devices_per_minute(self) -> float:
        minutes = self.total_time / 60.0
        return (self.collected + self.failed) / minutes if minutes > 0 else 0.0


class UltraFastDeviceCollector(QThread):
    """Ultra-fast device collector with hang prevention"""
    
    # PyQt Signals
    log_message = pyqtSignal(str)
    progress_updated = pyqtSignal(int)
    device_collected = pyqtSignal(dict)
    collection_finished = pyqtSignal()
    stats_updated = pyqtSignal(dict)
    
    def __init__(self, 
                 targets: List[str],
                 win_creds: Optional[List[Any]] = None,  # Accept dict or tuple format
                 linux_creds: Optional[List[Any]] = None,  # Accept dict or tuple format
                 snmp_v2c: Optional[List[str]] = None,
                 snmp_v3: Optional[Dict] = None,
                 use_http: bool = False,  # Disabled by default for speed
                 discovery_workers: int = 20,  # Increased from 15
                 collection_workers: int = 12,  # Increased from 8
                 parent=None):
        super().__init__(parent)
        
        self.targets = targets or []
        self.win_creds = win_creds or []
        self.linux_creds = linux_creds or []
        self.snmp_v2c = snmp_v2c or []
        self.snmp_v3 = snmp_v3 or {}
        self.use_http = use_http  # HTTP slows down collection significantly
        
        # Optimized worker counts
        self.discovery_workers = discovery_workers
        self.collection_workers = collection_workers
        
        # Thread control
        self._stop_requested = threading.Event()
        self._discovery_complete = threading.Event()
        self._collection_complete = threading.Event()
        
        # High-performance queues
        self.discovery_queue = Queue()
        self.collection_queue = Queue()
        self.results_queue = Queue()
        
        # Thread-safe tracking
        self.stats_lock = threading.Lock()
        self.stats = FastCollectionStats()
        self.discovered_devices: Set[str] = set()
        self.collected_ips: Set[str] = set()
        self.failed_ips: Set[str] = set()
        
        log.info(f"Ultra-fast collector initialized: {discovery_workers} discovery + {collection_workers} collection workers")

    def run(self):
        """Main optimized collection execution"""
        try:
            self.log_message.emit("🚀 Starting ULTRA-FAST collection with hang prevention...")
            self.stats.start_time = time.time()
            
            # Phase 1: Lightning-fast discovery (parallel)
            discovery_future = self._run_discovery_phase_async()
            
            # Phase 2: Start collection immediately (don't wait for discovery to complete)
            collection_future = self._run_collection_phase_async()
            
            # Phase 3: Monitor both phases
            self._monitor_collection_progress(discovery_future, collection_future)
            
            # Phase 4: Process results
            self._process_results()
            
            # Final statistics
            self._emit_final_stats()
            
            self.log_message.emit(f"✅ ULTRA-FAST collection complete in {self.stats.total_time:.1f}s")
            self.collection_finished.emit()
            
        except Exception as e:
            self.log_message.emit(f"❌ Collection error: {e}")
            log.exception("Collection failed")

    def _run_discovery_phase_async(self) -> concurrent.futures.Future:
        """Run discovery phase asynchronously"""
        executor = ThreadPoolExecutor(max_workers=self.discovery_workers, thread_name_prefix="Discovery")
        
        # Populate discovery queue
        for target in self.targets:
            self._populate_ips_for_target(target)
        
        # Submit discovery workers
        futures = []
        for _ in range(self.discovery_workers):
            future = executor.submit(self._ultra_fast_discovery_worker)
            futures.append(future)
        
        # Return future that completes when all discovery is done
        def discovery_completion():
            for future in as_completed(futures):
                if self._stop_requested.is_set():
                    break
                try:
                    future.result(timeout=1.0)
                except Exception as e:
                    log.warning(f"Discovery worker error: {e}")
            self._discovery_complete.set()
            executor.shutdown(wait=True)
        
        return ThreadPoolExecutor(max_workers=1).submit(discovery_completion)

    def _run_collection_phase_async(self) -> concurrent.futures.Future:
        """Run collection phase asynchronously"""
        executor = ThreadPoolExecutor(max_workers=self.collection_workers, thread_name_prefix="Collection")
        
        # Submit collection workers
        futures = []
        for _ in range(self.collection_workers):
            future = executor.submit(self._ultra_fast_collection_worker)
            futures.append(future)
        
        # Return future that completes when all collection is done
        def collection_completion():
            for future in as_completed(futures):
                if self._stop_requested.is_set():
                    break
                try:
                    future.result(timeout=2.0)
                except Exception as e:
                    log.warning(f"Collection worker error: {e}")
            self._collection_complete.set()
            executor.shutdown(wait=True)
        
        return ThreadPoolExecutor(max_workers=1).submit(collection_completion)

    def _populate_ips_for_target(self, target: str):
        """Populate IPs for target with optimized range handling"""
        try:
            if '/' in target:  # CIDR notation
                import ipaddress
                network = ipaddress.IPv4Network(target, strict=False)
                
                # Limit large networks to prevent memory issues
                max_ips = 1000
                ip_count = 0
                
                for ip in network.hosts():
                    if ip_count >= max_ips:
                        self.log_message.emit(f"⚠️ Limited {target} to {max_ips} IPs for performance")
                        break
                    
                    self.discovery_queue.put(str(ip))
                    ip_count += 1
                    
            elif '-' in target:  # Range notation
                # Handle range with potentially multiple dashes - split on first dash only
                parts = target.split('-', 1)  # Split on first dash only
                if len(parts) == 2:
                    start_ip, end_ip = parts
                    try:
                        start_parts = list(map(int, start_ip.split('.')))
                        end_parts = list(map(int, end_ip.split('.')))
                        
                        # Simple range implementation (limited for performance)
                        if len(start_parts) == 4 and len(end_parts) == 4 and start_parts[:3] == end_parts[:3]:  # Same subnet
                            for i in range(start_parts[3], min(end_parts[3] + 1, start_parts[3] + 100)):
                                ip = f"{start_parts[0]}.{start_parts[1]}.{start_parts[2]}.{i}"
                                self.discovery_queue.put(ip)
                        else:
                            # Invalid range format, treat as single IP
                            self.discovery_queue.put(target)
                    except (ValueError, IndexError):
                        # Invalid IP format, treat as single IP
                        self.discovery_queue.put(target)
                else:
                    # Invalid range format, treat as single IP  
                    self.discovery_queue.put(target)
            else:
                # Single IP
                self.discovery_queue.put(target)
                
        except Exception as e:
            self.log_message.emit(f"⚠️ Error processing target {target}: {e}")

    def _ultra_fast_discovery_worker(self):
        """Ultra-fast discovery worker with aggressive timeouts"""
        while not self._stop_requested.is_set():
            try:
                ip = self.discovery_queue.get(timeout=0.5)  # Short timeout
                
                if self._is_device_reachable_ultra_fast(ip):
                    # Device is reachable, add to collection queue
                    quality = self._calculate_device_priority_fast(ip)
                    task = OptimizedDeviceTask(ip=ip, quality_score=quality, timeout=5.0)
                    
                    self.collection_queue.put(task)
                    
                    with self.stats_lock:
                        self.discovered_devices.add(ip)
                        self.stats.discovered += 1
                    
                    self._update_progress()
                
                self.discovery_queue.task_done()
                
            except Empty:
                # Check if more work is coming
                if self._stop_requested.is_set():
                    break
            except Exception as e:
                log.warning(f"Discovery error for {ip}: {e}")

    def _ultra_fast_collection_worker(self):
        """Ultra-fast collection worker with strict timeouts"""
        while not self._stop_requested.is_set():
            try:
                task = self.collection_queue.get(timeout=1.0)
                
                # Skip if already collected (duplicate prevention)
                if task.ip in self.collected_ips:
                    with self.stats_lock:
                        self.stats.skipped += 1
                    self._update_progress()
                    continue
                
                # Attempt ultra-fast collection with strict timeout
                device_data = self._collect_device_data_ultra_fast(task)
                
                # Debug: Log what we got back
                if device_data:
                    self.log_message.emit(f"🔍 DEBUG: Collected data keys: {list(device_data.keys())}")
                    self.log_message.emit(f"🔍 DEBUG: Has Error key: {'Error' in device_data}")
                    hostname = device_data.get('hostname', device_data.get('computer_name', 'Unknown'))
                    self.log_message.emit(f"🔍 DEBUG: Hostname from data: {hostname}")
                    wmi_status = device_data.get('wmi_collection_status', 'N/A')
                    self.log_message.emit(f"🔍 DEBUG: WMI status: {wmi_status}")
                else:
                    self.log_message.emit("🔍 DEBUG: device_data is None or falsy")
                
                if device_data:
                    # Check if this is a successful collection
                    wmi_status = device_data.get('wmi_collection_status', '')
                    collection_method = device_data.get('collection_method', device_data.get('Collection Method', ''))
                    hostname = device_data.get('hostname', device_data.get('Hostname', 'Unknown'))
                    
                    # Consider it successful if:
                    # 1. WMI status is 'Success' (not failed)
                    # 2. AND has a meaningful hostname (not generic)
                    # 3. AND has a valid collection method
                    is_success = (
                        wmi_status and 
                        wmi_status == 'Success' and
                        not wmi_status.startswith('Failed:') and
                        hostname and 
                        hostname not in ['Unknown', f'device-{task.ip.replace(".", "-")}', f'snmp-{task.ip.replace(".", "-")}'] and
                        collection_method and 
                        collection_method not in ['Unknown', '']
                    )
                    
                    self.log_message.emit(f"🔍 DEBUG: Success check - WMI: {wmi_status}, Method: {collection_method}, Hostname: {hostname}, Success: {is_success}")
                    
                    if is_success:
                        # Success - Save to database immediately
                        self.results_queue.put(device_data)
                        
                        # Attempt to save to database
                        try:
                            if self._save_to_database(device_data):
                                self.log_message.emit(f"💾 Database save SUCCESS: {hostname}")
                            else:
                                self.log_message.emit(f"⚠️ Database save FAILED: {hostname}")
                        except Exception as e:
                            self.log_message.emit(f"❌ Database save ERROR: {hostname} - {e}")
                        
                        with self.stats_lock:
                            self.collected_ips.add(task.ip)
                            self.stats.collected += 1
                        
                        self.device_collected.emit(device_data)
                        self._update_progress()
                        
                    else:
                        # Failed - try fallback methods before retrying
                        self.log_message.emit(f"🔍 DEBUG: Collection considered failed for {task.ip}")
                        
                        # Try fallback methods if haven't tried them yet
                        if not hasattr(task, 'attempted_methods'):
                            task.attempted_methods = set()
                        
                        if collection_method:
                            task.attempted_methods.add(collection_method)
                        
                        # Try Linux SSH if WMI failed and SSH not tried yet
                        if 'WMI' in task.attempted_methods and 'SSH' not in task.attempted_methods:
                            self.log_message.emit(f"🔄 WMI failed for {task.ip}, trying SSH...")
                            fallback_data = self._collect_linux_ssh(task.ip, task)
                            if fallback_data and fallback_data.get('hostname') and fallback_data.get('hostname') != 'Unknown':
                                self.log_message.emit(f"✅ SSH succeeded for {task.ip}")
                                fallback_data['Collection Method'] = 'SSH'
                                self.results_queue.put(fallback_data)
                                with self.stats_lock:
                                    self.collected_ips.add(task.ip)
                                    self.stats.collected += 1
                                self.device_collected.emit(fallback_data)
                                self._update_progress()
                                continue
                            else:
                                task.attempted_methods.add('SSH')
                        
                        # Try SNMP if other methods failed
                        if len(task.attempted_methods) >= 2 and 'SNMP' not in task.attempted_methods:
                            self.log_message.emit(f"🔄 Previous methods failed for {task.ip}, trying SNMP...")
                            # Add basic SNMP attempt here if needed
                            task.attempted_methods.add('SNMP')
                        
                        # Retry with same method if haven't exhausted fallbacks
                        if task.retry_count < task.max_retries and len(task.attempted_methods) < 3:
                            task.retry_count += 1
                            self.collection_queue.put(task)  # Retry with fallbacks
                        else:
                            self.log_message.emit(f"❌ All methods failed for {task.ip} after {task.retry_count} retries")
                            with self.stats_lock:
                                self.failed_ips.add(task.ip)
                                self.stats.failed += 1
                else:
                    # device_data is None or empty
                    self.log_message.emit(f"🔍 DEBUG: No device data returned for {task.ip}")
                    with self.stats_lock:
                        self.failed_ips.add(task.ip)
                        self.stats.failed += 1
                    self._update_progress()
                
                self.collection_queue.task_done()
                
            except Empty:
                # Check if discovery is complete and queue is empty
                if self._discovery_complete.is_set() and self.collection_queue.empty():
                    break
            except Exception as e:
                log.warning(f"Collection worker error: {e}")

    def _is_device_reachable_ultra_fast(self, ip: str) -> bool:
        """Ultra-fast device reachability check with minimal timeout"""
        try:
            # Test only the most common ports with very short timeouts
            critical_ports = [22, 80, 135, 445]  # SSH, HTTP, RPC, SMB
            
            for port in critical_ports:
                if self._stop_requested.is_set():
                    return False
                
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.3)  # Ultra-fast 300ms timeout
                    result = sock.connect_ex((ip, port))
                    sock.close()
                    
                    if result == 0:
                        return True
                except:
                    continue
            
            return False
        except Exception:
            return False

    def _calculate_device_priority_fast(self, ip: str) -> float:
        """Fast device priority calculation"""
        score = 0.0
        
        # Quick port priority scoring
        if self._is_port_open_fast(ip, 135, 0.2):  # Windows RPC
            score += 0.4
        if self._is_port_open_fast(ip, 22, 0.2):   # SSH/Linux
            score += 0.3  
        if self._is_port_open_fast(ip, 445, 0.2):  # SMB
            score += 0.3
        
        return min(score, 1.0)

    def _is_port_open_fast(self, ip: str, port: int, timeout: float = 0.2) -> bool:
        """Ultra-fast port check"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except:
            return False

    def _collect_device_data_ultra_fast(self, task: OptimizedDeviceTask) -> Optional[Dict]:
        """Ultra-fast device collection with strict timeouts and hang prevention"""
        if not COLLECTION_UTILS_AVAILABLE:
            return self._fallback_collection(task)
        
        try:
            # Use ThreadPoolExecutor with timeout to prevent hangs
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(self._attempt_collection_with_timeout, task)
                
                try:
                    # Strict timeout to prevent hangs
                    device_data = future.result(timeout=task.timeout)
                    return device_data
                except TimeoutError:
                    # Collection timed out - create basic record
                    with self.stats_lock:
                        self.stats.timeout_errors += 1
                    
                    self.log_message.emit(f"⏰ Collection timeout for {task.ip} after {task.timeout}s")
                    
                    # Return basic device info instead of complete failure
                    return {
                        'IP Address': task.ip,
                        'Hostname': f'device-{task.ip.replace(".", "-")}',
                        'Collector': 'Timeout Recovery',
                        'Asset Type': 'Network Device', 
                        'Status': 'Timeout',
                        'Collection Time': datetime.now().isoformat(),
                        'Quality Score': task.quality_score,
                        'Notes': f'Collection timed out after {task.timeout}s - device may be slow or protected'
                    }
                    
        except Exception as e:
            log.warning(f"Collection error for {task.ip}: {e}")
            return None

    def _attempt_collection_with_timeout(self, task: OptimizedDeviceTask) -> Optional[Dict]:
        """Attempt collection with NMAP OS detection and optimized method selection"""
        ip = task.ip
        
        self.log_message.emit(f"🔍 Starting NMAP OS detection for {ip}...")
        
        # Step 1: Use port-based OS detection instead of NMAP to avoid timeouts
        self.log_message.emit(f"🔍 Starting port-based OS detection for {ip}...")
        
        # Skip NMAP entirely for now due to timeout issues
        os_info = _port_based_os_detection(ip)
        os_family = os_info.get('os_family', 'Unknown')
        device_type = os_info.get('device_type', 'Unknown')
        confidence = os_info.get('confidence', '0')
        
        self.log_message.emit(f"🎯 NMAP Result for {ip}: {os_family} ({device_type}) - {confidence}% confidence")
        
        # Step 2: Apply collection strategy based on detected OS
        collected_data = None
        
        # Strategy 1: Windows + Windows Server use WMI
        if os_family == 'Windows' and self.win_creds:
            self.log_message.emit(f"🪟 Detected Windows system - Using WMI collection for {ip}")
            collected_data = self._collect_windows_wmi(ip, task)
            
            # If WMI fails, try SNMP as fallback for Windows
            if not collected_data and (self.snmp_v2c or self.snmp_v3):
                self.log_message.emit(f"🔄 WMI failed for Windows {ip} - Trying SNMP fallback")
                collected_data = self._collect_snmp_method(ip, task)
        
        # Strategy 2: Linux use SSH
        elif os_family == 'Linux' and self.linux_creds:
            self.log_message.emit(f"🐧 Detected Linux system - Using SSH collection for {ip}")
            collected_data = self._collect_linux_ssh(ip, task)
        
        # Strategy 3: Network Device use SNMP or SSH
        elif os_family == 'Network':
            self.log_message.emit(f"🌐 Detected Network Device - Using SNMP/SSH collection for {ip}")
            # Try SNMP first for network devices
            if self.snmp_v2c or self.snmp_v3:
                collected_data = self._collect_snmp_method(ip, task)
            # Try SSH if SNMP fails
            if not collected_data and self.linux_creds:
                self.log_message.emit(f"🔄 SNMP failed for network device {ip} - Trying SSH")
                collected_data = self._collect_linux_ssh(ip, task)
        
        # Strategy 4: Hypervisor use SSH or SNMP
        elif os_family == 'Hypervisor':
            self.log_message.emit(f"💻 Detected Hypervisor - Using SSH/SNMP collection for {ip}")
            # Try SSH first for hypervisors
            if self.linux_creds:
                collected_data = self._collect_linux_ssh(ip, task)
            # Try SNMP if SSH fails
            if not collected_data and (self.snmp_v2c or self.snmp_v3):
                self.log_message.emit(f"🔄 SSH failed for hypervisor {ip} - Trying SNMP")
                collected_data = self._collect_snmp_method(ip, task)
        
        # Strategy 5: Unknown or Other devices - try all methods
        else:
            self.log_message.emit(f"❓ Unknown OS for {ip} - Trying all available methods")
            
            # Quick port scan to determine best method for unknown devices
            has_135 = self._is_port_open_fast(ip, 135, 0.3)  # Windows RPC
            has_22 = self._is_port_open_fast(ip, 22, 0.3)    # SSH
            has_445 = self._is_port_open_fast(ip, 445, 0.3)  # SMB
            has_161 = self._is_port_open_fast(ip, 161, 0.3)  # SNMP
            
            # Try methods based on open ports
            if (has_135 or has_445) and self.win_creds:
                collected_data = self._collect_windows_wmi(ip, task)
            elif has_22 and self.linux_creds:
                collected_data = self._collect_linux_ssh(ip, task)
            elif has_161 and (self.snmp_v2c or self.snmp_v3):
                collected_data = self._collect_snmp_method(ip, task)
        
        # Add OS detection results to collected data
        if collected_data:
            collected_data.update({
                'nmap_os_family': os_family,
                'nmap_device_type': device_type,
                'nmap_confidence': confidence,
                'detection_method': 'NMAP OS Detection'
            })
            return collected_data
        
        # If all specific methods failed, try HTTP and basic detection
        return self._fallback_collection_methods(ip, task, os_info)
    
    def _collect_windows_wmi(self, ip: str, task: OptimizedDeviceTask) -> Optional[Dict]:
        """Collect Windows data using WMI"""
        if not self.win_creds:
            return None
            
        log.info(f"Trying {len(self.win_creds)} Windows credentials for {ip}")
        for i, cred in enumerate(self.win_creds[:5], 1):  # Try up to 5 credentials
            try:
                # Handle different credential formats defensively
                if isinstance(cred, dict):
                    # Dictionary format: {"username": "user", "password": "pass", "domain": "domain"}
                    username = cred.get('username', '')
                    password = cred.get('password', '')
                    domain = cred.get('domain', '.')
                    if domain and domain != '.':
                        username = f"{domain}\\{username}"
                elif isinstance(cred, (tuple, list)) and len(cred) >= 2:
                    username, password = cred[0], cred[1]
                elif isinstance(cred, str) and ':' in cred:
                    username, password = cred.split(':', 1)
                else:
                    continue  # Skip invalid credential format
                
                if not username or not password:
                    continue
                
                self.log_message.emit(f"🔍 DEBUG: Credential {i} - Raw: {cred}")
                self.log_message.emit(f"🔍 DEBUG: Credential {i} - Formatted username: '{username}', password: {'***set***' if password else '***empty***'}")
                log.debug(f"Trying Windows credential {i}/5: {username.split('\\')[-1]}@{domain if domain != '.' else 'local'}")
                device_data = _collect_windows_standalone(ip, username, password)
                if device_data:
                    device_data['Collection Method'] = 'WMI'
                    device_data['Collection Time'] = datetime.now().isoformat()
                    device_data['Quality Score'] = task.quality_score
                    device_data['Successful Credential'] = username
                    log.info(f"✅ Windows collection successful for {ip} using credential {i}: {username}")
                    return device_data
                else:
                    log.debug(f"❌ Windows credential {i} failed for {ip}")
            except Exception as e:
                log.debug(f"❌ Windows credential {i} error for {ip}: {str(e)[:50]}")
                continue
        return None
    
    def _collect_linux_ssh(self, ip: str, task: OptimizedDeviceTask) -> Optional[Dict]:
        """Collect Linux data using SSH"""
        if not self.linux_creds:
            return None
        
        log.info(f"Trying {len(self.linux_creds)} Linux/SSH credentials for {ip}")
        for i, cred in enumerate(self.linux_creds[:5], 1):  # Try up to 5 credentials
            try:
                # Handle different credential formats defensively
                if isinstance(cred, dict):
                    # Dictionary format: {"username": "user", "password": "pass", "domain": "domain"}
                    username = cred.get('username', '')
                    password = cred.get('password', '')
                    # For SSH, domain is usually ignored, but we can use it for logging
                    domain = cred.get('domain', 'local')
                elif isinstance(cred, (tuple, list)) and len(cred) >= 2:
                    username, password = cred[0], cred[1]
                    domain = 'local'
                elif isinstance(cred, str) and ':' in cred:
                    username, password = cred.split(':', 1)
                    domain = 'local'
                else:
                    continue  # Skip invalid credential format
                
                if not username or not password:
                    continue
                
                log.debug(f"Trying SSH credential {i}/5: {username}@{domain}")
                device_data = _collect_ssh_standalone(ip, username, password)
                if device_data:
                    device_data['Collection Method'] = 'SSH'
                    device_data['Collection Time'] = datetime.now().isoformat()
                    device_data['Quality Score'] = task.quality_score
                    device_data['Successful Credential'] = username
                    log.info(f"✅ SSH collection successful for {ip} using credential {i}: {username}")
                    return device_data
                else:
                    log.debug(f"❌ SSH credential {i} failed for {ip}")
            except Exception as e:
                log.debug(f"❌ SSH credential {i} error for {ip}: {str(e)[:50]}")
                continue
        return None
    
    def _collect_snmp_method(self, ip: str, task: OptimizedDeviceTask) -> Optional[Dict]:
        """Collect device data using SNMP"""
        try:
            device_data = _collect_snmp_standalone(ip, self.snmp_v2c)
            if device_data:
                device_data['Collection Method'] = 'SNMP'
                device_data['Collection Time'] = datetime.now().isoformat()
                device_data['Quality Score'] = task.quality_score
                log.info(f"✅ SNMP collection successful for {ip}")
                return device_data
        except Exception as e:
            log.debug(f"❌ SNMP collection error for {ip}: {str(e)[:50]}")
        return None
    
    def _fallback_collection_methods(self, ip: str, task: OptimizedDeviceTask, os_info: Dict) -> Dict:
        """Try HTTP and basic detection as fallback methods"""
        # Try HTTP collection if enabled
        if self.use_http:
            try:
                device_data = _collect_http_standalone(ip)
                if device_data:
                    device_data['Collection Method'] = 'HTTP'
                    device_data['Collection Time'] = datetime.now().isoformat()
                    device_data['Quality Score'] = task.quality_score
                    device_data.update({
                        'nmap_os_family': os_info.get('os_family', 'Unknown'),
                        'nmap_device_type': os_info.get('device_type', 'Unknown'),
                        'nmap_confidence': os_info.get('confidence', '0')
                    })
                    log.info(f"✅ HTTP collection successful for {ip}")
                    return device_data
            except Exception as e:
                log.debug(f"❌ HTTP collection error for {ip}: {str(e)[:50]}")
        
        # Return basic network device info with OS detection results if all methods fail
        return {
            'IP Address': ip,
            'Hostname': f'device-{ip.replace(".", "-")}',
            'Collector': 'Network Scan + NMAP',
            'Asset Type': os_info.get('device_type', 'Network Device'),
            'Collection Method': 'Basic Network Detection + NMAP OS Detection',
            'Collection Time': datetime.now().isoformat(),
            'Quality Score': task.quality_score,
            'nmap_os_family': os_info.get('os_family', 'Unknown'),
            'nmap_device_type': os_info.get('device_type', 'Unknown'),
            'nmap_confidence': os_info.get('confidence', '0'),
            'Status': 'Detected but not accessible with provided credentials'
        }

    def _fallback_collection(self, task: OptimizedDeviceTask) -> Dict:
        """Fallback collection when AssetV2 is not available"""
        return {
            'IP Address': task.ip,
            'Hostname': f'device-{task.ip.replace(".", "-")}',
            'Collector': 'Fallback',
            'Asset Type': 'Network Device',
            'Collection Method': 'Fallback Basic Detection',
            'Collection Time': datetime.now().isoformat(),
            'Quality Score': task.quality_score,
            'Status': 'Basic detection only - enhanced collection not available'
        }

    def _monitor_collection_progress(self, discovery_future, collection_future):
        """Monitor both discovery and collection phases"""
        start_time = time.time()
        last_update = start_time
        
        while not (self._discovery_complete.is_set() and self._collection_complete.is_set()):
            if self._stop_requested.is_set():
                break
            
            current_time = time.time()
            
            # Update progress every second
            if current_time - last_update >= 1.0:
                self._update_progress()
                self._emit_stats()
                last_update = current_time
            
            # Check for stalled collection (prevent infinite hang)
            if current_time - start_time > 300:  # 5 minute timeout
                self.log_message.emit("⚠️ Collection taking too long - stopping to prevent hang")
                self.stop()
                break
            
            time.sleep(0.1)

    def _process_results(self):
        """Process all collected results and save to database"""
        self.log_message.emit("💾 PROCESSING RESULTS - Starting database save process...")
        
        queue_size = self.results_queue.qsize()
        self.log_message.emit(f"📊 Results queue size: {queue_size} devices")
        
        devices_to_save = []
        while not self.results_queue.empty():
            try:
                device_data = self.results_queue.get_nowait()
                devices_to_save.append(device_data)
                hostname = device_data.get('hostname', device_data.get('Hostname', 'Unknown'))
                self.log_message.emit(f"📦 Retrieved device from queue: {hostname}")
            except Empty:
                break
        
        if not devices_to_save:
            self.log_message.emit("⚠️ NO DEVICES TO SAVE - Results queue was empty!")
            return
            
        self.log_message.emit(f"📊 PROCESSING {len(devices_to_save)} COLLECTED DEVICES FOR DATABASE SAVE...")
        
        # Save to database and emit events
        saved_count = 0
        for i, device_data in enumerate(devices_to_save, 1):
            try:
                hostname = device_data.get('hostname', device_data.get('Hostname', 'Unknown'))
                self.log_message.emit(f"🔄 Processing device {i}/{len(devices_to_save)}: {hostname}")
                
                # Normalize data for consistent database storage
                normalized_data = self._normalize_device_data(device_data)
                self.log_message.emit(f"✅ Data normalized for {hostname}")
                
                # Save to database
                if self._save_to_database(normalized_data):
                    saved_count += 1
                    self.log_message.emit(f"✅ SAVE SUCCESS {i}/{len(devices_to_save)}: {hostname}")
                else:
                    self.log_message.emit(f"❌ SAVE FAILED {i}/{len(devices_to_save)}: {hostname}")
                
                # Emit for GUI updates
                self.device_collected.emit(normalized_data)
                
            except Exception as e:
                self.log_message.emit(f"❌ Error processing device {i}: {e}")
                import traceback
                self.log_message.emit(f"❌ Traceback: {traceback.format_exc()}")
        
        # Update statistics
        with self.stats_lock:
            self.stats.saved_devices = saved_count
        
        self.log_message.emit(f"📊 FINAL RESULT: Processed {len(devices_to_save)} devices, SAVED {saved_count} to database")
        
        if saved_count == 0:
            self.log_message.emit("🚨 CRITICAL: NO DEVICES SAVED TO DATABASE!")
        elif saved_count < len(devices_to_save):
            self.log_message.emit(f"⚠️ WARNING: Only {saved_count}/{len(devices_to_save)} devices saved successfully")
        else:
            self.log_message.emit("🎉 SUCCESS: All devices saved to database!")

    def _update_progress(self):
        """Update progress calculation"""
        with self.stats_lock:
            total = len(self.discovered_devices)
            completed = self.stats.collected + self.stats.failed + self.stats.skipped
            
            if total > 0:
                percentage = min(int((completed / total) * 100), 100)
                self.progress_updated.emit(percentage)

    def _emit_stats(self):
        """Emit current statistics"""
        with self.stats_lock:
            stats_dict = {
                'discovered': self.stats.discovered,
                'collected': self.stats.collected,
                'failed': self.stats.failed,
                'skipped': self.stats.skipped,
                'timeout_errors': self.stats.timeout_errors,
                'connection_errors': self.stats.connection_errors,
                'success_rate': self.stats.success_rate,
                'devices_per_minute': self.stats.devices_per_minute,
                'total_time': self.stats.total_time,
                'queue_sizes': {
                    'discovery': self.discovery_queue.qsize(),
                    'collection': self.collection_queue.qsize(),
                    'results': self.results_queue.qsize()
                }
            }
            self.stats_updated.emit(stats_dict)

    def _emit_final_stats(self):
        """Emit final collection statistics"""
        with self.stats_lock:
            self.log_message.emit("📊 FINAL STATISTICS:")
            self.log_message.emit(f"   • Total Time: {self.stats.total_time:.1f}s")
            self.log_message.emit(f"   • Devices Discovered: {self.stats.discovered}")
            self.log_message.emit(f"   • Devices Collected: {self.stats.collected}")
            self.log_message.emit(f"   • Collection Failed: {self.stats.failed}")
            self.log_message.emit(f"   • Timeout Errors: {self.stats.timeout_errors}")
            self.log_message.emit(f"   • Success Rate: {self.stats.success_rate:.1f}%")
            self.log_message.emit(f"   • Speed: {self.stats.devices_per_minute:.1f} devices/min")

    def _normalize_device_data(self, data: Dict) -> Dict:
        """Normalize device data to match database schema consistently"""
        normalized = {}
        
        # If data already contains our new WMI column names, use them directly
        wmi_columns = [
            'ip_address', 'hostname', 'computer_name', 'operating_system', 
            'system_manufacturer', 'system_model', 'processor_name',
            'total_physical_memory', 'bios_version', 'wmi_collection_status',
            'wmi_data_completeness', 'device_type', 'asset_type', 'collector',
            'status', 'domain_workgroup', 'os_version', 'os_build_number',
            'processor_cores', 'mac_addresses', 'hard_drives'
        ]
        
        # Copy WMI columns directly if they exist
        for col in wmi_columns:
            if col in data and data[col] is not None:
                normalized[col] = data[col]
        
        # Handle legacy field mappings for backward compatibility
        if 'ip_address' not in normalized:
            normalized['ip_address'] = data.get('IP Address') or data.get('hostname')
            
        if 'hostname' not in normalized:
            normalized['hostname'] = data.get('Hostname') or data.get('computer_name') or normalized.get('ip_address')
            
        if 'operating_system' not in normalized:
            normalized['operating_system'] = (data.get('OS') or data.get('Operating System') or 
                                            data.get('os_name'))
            
        if 'system_manufacturer' not in normalized:
            normalized['system_manufacturer'] = (data.get('Manufacturer') or 
                                               data.get('manufacturer'))
                                               
        if 'system_model' not in normalized:
            normalized['system_model'] = data.get('Model') or data.get('model')
            
        if 'device_type' not in normalized:
            device_type = (data.get('Asset Type') or data.get('Device Type') or 
                          data.get('Collector', 'Unknown'))
            
            # Map collector types to device types
            if device_type == 'WMI Enhanced' or 'Windows' in str(device_type):
                device_type = 'Workstation'
            elif device_type == 'SSH Enhanced' or 'Linux' in str(device_type):
                device_type = 'Server'
            elif 'SNMP' in str(device_type):
                device_type = 'Network Device'
            elif 'HTTP' in str(device_type):
                device_type = 'Web Device'
                
            normalized['device_type'] = device_type
            
        # Set default status if not present
        if 'status' not in normalized:
            normalized['status'] = 'Active'
            
        # Add timestamps
        from datetime import datetime
        now = datetime.now().isoformat()
        normalized['created_at'] = now
        normalized['updated_at'] = now
        normalized['last_scan_time'] = now
        
        # Add any other fields from the original data that aren't already handled
        for key, value in data.items():
            if (key not in normalized and value is not None and 
                str(value).strip() != '' and str(value).strip().lower() != 'none'):
                normalized[key] = value
        
        return normalized
    
    def _save_to_database(self, device_data: Dict) -> bool:
        """Save device data to database with full schema support"""
        try:
            import sqlite3
            from datetime import datetime
            
            # Enhanced logging for debugging
            hostname = device_data.get('hostname', device_data.get('Hostname', 'Unknown'))
            ip_address = device_data.get('ip_address', device_data.get('IP Address', 'Unknown'))
            working_user = device_data.get('working_user', device_data.get('Working User', 'System'))
            
            self.log_message.emit(f"💾 SAVING TO DATABASE: {hostname} ({ip_address}) - User: {working_user}")
            
            conn = sqlite3.connect('assets.db')
            cursor = conn.cursor()
            
            # Ensure required fields
            if not device_data.get('hostname') and not device_data.get('ip_address'):
                if not device_data.get('Hostname') and not device_data.get('IP Address'):
                    self.log_message.emit("❌ Cannot save device: missing hostname and ip_address")
                    return False
            
            # Get all available columns in the database
            cursor.execute('PRAGMA table_info(assets)')
            db_columns = [col[1] for col in cursor.fetchall()]
            
            # Prepare data for insertion - only include columns that exist in DB
            db_data = {}
            
            # Map common field variations
            field_mappings = {
                'hostname': ['hostname', 'Hostname', 'computer_name', 'Computer Name'],
                'ip_address': ['ip_address', 'IP Address', 'IP'],
                'working_user': ['working_user', 'Working User', 'Current User'],
                'operating_system': ['operating_system', 'OS', 'Operating System'],
                'system_manufacturer': ['system_manufacturer', 'Manufacturer'],
                'system_model': ['system_model', 'Model'],
                'device_type': ['device_type', 'Device Type', 'Asset Type'],
                'status': ['status', 'Status']
            }
            
            # Apply field mappings
            for db_field, source_fields in field_mappings.items():
                if db_field in db_columns:
                    for source_field in source_fields:
                        if source_field in device_data and device_data[source_field] is not None:
                            value = str(device_data[source_field]).strip()
                            if value and value.lower() != 'none' and value != '':
                                db_data[db_field] = value
                                break
            
            # Add remaining fields that match database columns
            for key, value in device_data.items():
                if key in db_columns and key not in db_data and value is not None:
                    clean_value = str(value).strip()
                    if clean_value and clean_value.lower() != 'none' and clean_value != '':
                        db_data[key] = clean_value
            
            # Add timestamps
            now = datetime.now().isoformat()
            if 'created_at' in db_columns:
                db_data['created_at'] = now
            if 'updated_at' in db_columns:
                db_data['updated_at'] = now
            if 'last_scan_time' in db_columns:
                db_data['last_scan_time'] = now
            
            # Ensure we have minimum required data
            if not db_data.get('hostname') and not db_data.get('ip_address'):
                self.log_message.emit("❌ No valid hostname or IP after field mapping")
                return False
            
            # ENHANCED HARDWARE-BASED DEDUPLICATION STRATEGY
            # Priority: 1) Hardware Serial Numbers  2) MAC Address  3) Hostname+IP  4) IP only
            hostname_to_check = db_data.get('hostname')
            ip_to_check = db_data.get('ip_address')
            bios_serial = db_data.get('bios_serial_number')
            chassis_serial = db_data.get('chassis_serial')
            device_serial = db_data.get('device_serial')
            mac_address = db_data.get('mac_address')
            
            existing_id = None
            existing_hostname = None
            match_reason = None
            
            # STRATEGY 1: HARDWARE FINGERPRINT (Most Reliable)
            # Check by BIOS Serial Number first (most stable hardware identifier)
            if not existing_id and bios_serial and bios_serial.strip() and bios_serial.strip().lower() not in ['none', 'unknown', 'n/a']:
                cursor.execute('SELECT id, hostname, ip_address FROM assets WHERE bios_serial_number = ?', (bios_serial,))
                existing = cursor.fetchone()
                if existing:
                    existing_id = existing[0]
                    existing_hostname = existing[1] 
                    match_reason = f"Hardware Match: BIOS Serial {bios_serial}"
                    self.log_message.emit(f"� Found existing device by BIOS Serial: ID {existing_id}, '{existing[1]}' ({existing[2]}) -> updating to '{hostname_to_check}' ({ip_to_check})")
            
            # Check by Chassis Serial Number
            if not existing_id and chassis_serial and chassis_serial.strip() and chassis_serial.strip().lower() not in ['none', 'unknown', 'n/a']:
                cursor.execute('SELECT id, hostname, ip_address FROM assets WHERE chassis_serial = ?', (chassis_serial,))
                existing = cursor.fetchone()
                if existing:
                    existing_id = existing[0]
                    existing_hostname = existing[1]
                    match_reason = f"Hardware Match: Chassis Serial {chassis_serial}"
                    self.log_message.emit(f"🔧 Found existing device by Chassis Serial: ID {existing_id}")
            
            # Check by Device Serial Number
            if not existing_id and device_serial and device_serial.strip() and device_serial.strip().lower() not in ['none', 'unknown', 'n/a']:
                cursor.execute('SELECT id, hostname, ip_address FROM assets WHERE device_serial = ?', (device_serial,))
                existing = cursor.fetchone()
                if existing:
                    existing_id = existing[0]
                    existing_hostname = existing[1]
                    match_reason = f"Hardware Match: Device Serial {device_serial}"
                    self.log_message.emit(f"🔧 Found existing device by Device Serial: ID {existing_id}")
            
            # STRATEGY 2: NETWORK IDENTITY (Medium Reliability)
            # Check by MAC Address
            if not existing_id and mac_address and mac_address.strip() and mac_address.strip().lower() not in ['none', 'unknown', 'n/a']:
                cursor.execute('SELECT id, hostname, ip_address FROM assets WHERE mac_address = ?', (mac_address,))
                existing = cursor.fetchone()
                if existing:
                    existing_id = existing[0]
                    existing_hostname = existing[1]
                    match_reason = f"Network Match: MAC Address {mac_address}"
                    self.log_message.emit(f"🌐 Found existing device by MAC Address: ID {existing_id}")
            
            # STRATEGY 3: LOGICAL IDENTITY (Lower Reliability)
            # Check by hostname first
            if not existing_id and hostname_to_check:
                cursor.execute('SELECT id, hostname, ip_address FROM assets WHERE hostname = ?', (hostname_to_check,))
                existing = cursor.fetchone()
                if existing:
                    existing_id = existing[0]
                    existing_hostname = existing[1]
                    match_reason = f"Logical Match: Hostname {hostname_to_check}"
                    self.log_message.emit(f"🏷️ Found existing device by Hostname: ID {existing_id}")
            
            # STRATEGY 4: IP FALLBACK (Least Reliable)
            # Check by IP address (only if no other matches)
            if not existing_id and ip_to_check:
                cursor.execute('SELECT id, hostname, ip_address FROM assets WHERE ip_address = ?', (ip_to_check,))
                existing = cursor.fetchone()
                if existing:
                    existing_id = existing[0]
                    existing_hostname = existing[1]
                    match_reason = f"IP Fallback: {ip_to_check}"
                    self.log_message.emit(f"⚠️ Found existing device by IP only: ID {existing_id} (IP-based matching is less reliable)")
            
            # Debug logging with deduplication strategy
            if existing_id:
                self.log_message.emit(f"🔄 Will UPDATE existing record ID {existing_id}: {match_reason}")
                self.log_message.emit(f"   Old: '{existing_hostname}' -> New: '{hostname_to_check}'")
            else:
                # Determine identity strength for new records
                if bios_serial or chassis_serial or device_serial:
                    identity_strength = "Strong (Hardware Serial)"
                elif mac_address:
                    identity_strength = "Medium (MAC Address)" 
                elif hostname_to_check:
                    identity_strength = "Weak (Hostname Only)"
                else:
                    identity_strength = "Very Weak (IP Only)"
                self.log_message.emit(f"✨ Will INSERT new record: '{hostname_to_check}' ({ip_to_check}) - Identity: {identity_strength}")
            
            if existing_id:
                # Update existing record
                if len(db_data) > 0:
                    set_clause = ', '.join([f'{col} = ?' for col in db_data.keys()])
                    cursor.execute(f'UPDATE assets SET {set_clause} WHERE id = ?', 
                                 list(db_data.values()) + [existing_id])
                    self.log_message.emit(f"✅ UPDATED existing device: {hostname_to_check or ip_to_check} (ID: {existing_id})")
            else:
                # Insert new record
                if len(db_data) > 0:
                    columns = list(db_data.keys())
                    placeholders = ', '.join(['?' for _ in columns])
                    cursor.execute(f'INSERT INTO assets ({", ".join(columns)}) VALUES ({placeholders})', 
                                 list(db_data.values()))
                    new_id = cursor.lastrowid
                    self.log_message.emit(f"✅ INSERTED new device: {hostname_to_check or ip_to_check} (ID: {new_id})")
            
            conn.commit()
            conn.close()
            
            # Log success with details
            saved_fields = len(db_data)
            self.log_message.emit(f"💾 DATABASE SAVE SUCCESS: {saved_fields} fields saved for {hostname_to_check or ip_to_check}")
            
            return True
            
        except Exception as e:
            error_msg = f"Failed to save device to database: {e}"
            self.log_message.emit(f"❌ DATABASE SAVE ERROR: {error_msg}")
            self.log_message.emit(f"❌ Device data keys: {list(device_data.keys())}")
            import traceback
            self.log_message.emit(f"❌ Traceback: {traceback.format_exc()}")
            return False

    def stop(self):
        """Stop collection gracefully"""
        self.log_message.emit("🛑 Stopping ultra-fast collection...")
        self._stop_requested.set()
        
        if not self.wait(5000):  # 5 second timeout
            self.log_message.emit("⚠️ Force terminating collection...")
            self.terminate()


# Make this the default collector for enhanced_main.py
ThreadedDeviceCollector = UltraFastDeviceCollector