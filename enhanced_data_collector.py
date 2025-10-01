#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Enhanced Data Collector with Desktop GUI Integration
====================================================
This module integrates comprehensive data collection with the desktop GUI
providing real-time device enhancement capabilities.
نموذج جامع البيانات المحسن مع تكامل الواجهة الرسومية
"""

import sqlite3
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import socket
import subprocess
import json
import traceback
from collector_integration import CollectorIntegration

try:
    import wmi
    import paramiko
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False

log = logging.getLogger(__name__)

class EnhancedDataCollector:
    """Enhanced data collector with GUI integration"""
    
    def __init__(self, database_path="assets.db"):
        self.database_path = database_path
        self.integration = CollectorIntegration(database_path)
        
        # Set up logging
        logging.basicConfig(level=logging.INFO, 
                          format='%(asctime)s - EnhancedDataCollector - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        self.field_mapping = {
            # Core identification fields
            'computer_name': 'hostname',
            'hostname': 'hostname', 
            'ip_address': 'ip_address',
            'mac_address': 'mac_address',
            'domain_workgroup': 'domain',
            'working_user': 'working_user',
            
            # System Information
            'system_manufacturer': 'manufacturer',
            'system_model': 'model',
            'device_type': 'device_type',
            'operating_system': 'os_name',
            'os_version': 'os_version',
            'firmware_os_version': 'firmware_os_version',
            
            # Hardware Details
            'processor_name': 'processor',
            'cpu_model': 'cpu_model',
            'total_physical_memory': 'installed_ram_gb',
            'memory_gb': 'memory_gb',
            'processor_cores': 'cpu_cores',
            'processor_logical_processors': 'cpu_threads',
            'hard_drives': 'storage',
            'storage_info': 'storage_info',
            
            # Asset Management
            'serial_number': 'serial_number',
            'asset_tag': 'asset_tag',
            'location': 'location',
            'department': 'department',
            'status': 'status',
            'classification': 'classification',
            
            # Collection Metadata
            'collection_method': 'data_source',
            'collection_date': 'created_at',
            'last_update': 'last_updated',
            'scan_status': 'ping_status',
            'collector': 'created_by'
        }

def enhanced_wmi_collection(ip_address: str, username: str, password: str) -> Dict[str, Any]:
    """
    Enhanced WMI collection that gathers comprehensive system information
    and maps it to the correct database fields
    """
    if not WMI_AVAILABLE:
        return create_basic_device_data(ip_address, "WMI not available")
    
    try:
        log.info(f"🔍 Starting enhanced WMI collection for {ip_address}")
        
        # Connect to WMI
        conn = wmi.WMI(computer=ip_address, user=username, password=password)
        
        # Initialize data dictionary with proper mappings
        device_data: Dict[str, str] = {
            'ip_address': ip_address,
            'collection_method': 'WMI Enhanced',
            'data_source': 'WMI Collection',
            'status': 'Active',
            'ping_status': 'Online',
            'device_type': 'Computer',
            'classification': 'Workstation',
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'created_by': 'Enhanced Collector',
            'last_updated_by': 'Enhanced Collector'
        }
        
        # System Information
        try:
            systems = conn.Win32_ComputerSystem()
            if systems:
                system = systems[0]
                device_data.update({
                    'hostname': system.Name or f'device-{ip_address.replace(".", "-")}',
                    'computer_name': system.Name or f'device-{ip_address.replace(".", "-")}',
                    'manufacturer': system.Manufacturer or 'Unknown',
                    'model': system.Model or 'Unknown',
                    'domain': getattr(system, 'Domain', None) or getattr(system, 'Workgroup', None) or 'Unknown',
                    'memory_gb': str(round(int(system.TotalPhysicalMemory) / (1024**3), 2)) if system.TotalPhysicalMemory else '0',
                    'installed_ram_gb': str(round(int(system.TotalPhysicalMemory) / (1024**3), 2)) if system.TotalPhysicalMemory else '0'
                })
                
                # Get working user
                if hasattr(system, 'UserName') and system.UserName:
                    device_data['working_user'] = system.UserName
                else:
                    device_data['working_user'] = 'System'
                    
        except Exception as e:
            log.warning(f"Failed to get system info: {e}")
        
        # Operating System Information
        try:
            os_list = conn.Win32_OperatingSystem()
            if os_list:
                os_info = os_list[0]
                device_data.update({
                    'os_name': os_info.Caption or 'Unknown',
                    'os_version': os_info.Version or 'Unknown',
                    'firmware_os_version': f"{os_info.Caption} {os_info.Version}" if os_info.Caption and os_info.Version else 'Unknown',
                    'architecture': getattr(os_info, 'OSArchitecture', 'Unknown'),
                    'device_type': 'Server' if 'Server' in (os_info.Caption or '') else 'Workstation'
                })
        except Exception as e:
            log.warning(f"Failed to get OS info: {e}")
        
        # Processor Information
        try:
            processors = conn.Win32_Processor()
            if processors:
                proc = processors[0]
                device_data.update({
                    'processor': proc.Name or 'Unknown',
                    'cpu_model': proc.Name or 'Unknown',
                    'cpu_cores': str(getattr(proc, 'NumberOfCores', 0)),
                    'cpu_threads': str(getattr(proc, 'NumberOfLogicalProcessors', 0)),
                    'cpu_info': f"{proc.Name} ({getattr(proc, 'NumberOfCores', 0)} cores)" if proc.Name else 'Unknown'
                })
        except Exception as e:
            log.warning(f"Failed to get processor info: {e}")
        
        # BIOS/Serial Information
        try:
            bios_list = conn.Win32_BIOS()
            if bios_list:
                bios = bios_list[0]
                device_data.update({
                    'serial_number': bios.SerialNumber or 'Unknown',
                    'asset_tag': getattr(bios, 'SerialNumber', 'Unknown')  # Use serial as asset tag if not set
                })
        except Exception as e:
            log.warning(f"Failed to get BIOS info: {e}")
        
        # Network Information
        try:
            adapters = conn.Win32_NetworkAdapterConfiguration(IPEnabled=True)
            mac_addresses = []
            for adapter in adapters:
                if adapter.MACAddress and adapter.MACAddress != '00:00:00:00:00:00':
                    mac_addresses.append(adapter.MACAddress)
            
            if mac_addresses:
                device_data['mac_address'] = mac_addresses[0]  # Primary MAC
                device_data['mac_addresses'] = ', '.join(mac_addresses)  # All MACs
        except Exception as e:
            log.warning(f"Failed to get network info: {e}")
        
        # Storage Information
        try:
            drives = conn.Win32_LogicalDisk(DriveType=3)  # Fixed drives only
            storage_info = []
            total_storage_gb = 0
            
            for drive in drives:
                if drive.Size:
                    size_gb = round(int(drive.Size) / (1024**3), 1)
                    free_gb = round(int(drive.FreeSpace) / (1024**3), 1) if drive.FreeSpace else 0
                    total_storage_gb += size_gb
                    storage_info.append(f"{drive.DeviceID} {size_gb}GB ({free_gb}GB free)")
            
            if storage_info:
                device_data.update({
                    'storage': ', '.join(storage_info),
                    'storage_info': f"Total: {total_storage_gb}GB",
                    'total_storage_gb': str(total_storage_gb)  # Convert to string for consistency
                })
        except Exception as e:
            log.warning(f"Failed to get storage info: {e}")
        
        # Additional system details
        try:
            # Get current user from explorer.exe process if system user
            if device_data.get('working_user') in ['System', 'N/A', None]:
                processes = conn.Win32_Process(Name="explorer.exe")
                for proc in processes:
                    try:
                        owner = proc.GetOwner()
                        if owner and len(owner) > 0 and owner[0]:
                            device_data['working_user'] = owner[0]
                            break
                    except:
                        continue
        except Exception as e:
            log.warning(f"Failed to get process owner info: {e}")
        
        # Final data quality check
        if not device_data.get('hostname') or device_data['hostname'] == 'Unknown':
            device_data['hostname'] = f"device-{ip_address.replace('.', '-')}"
            
        if not device_data.get('working_user') or device_data['working_user'] in ['System', 'N/A', None]:
            device_data['working_user'] = 'System'
        
        log.info(f"✅ Enhanced WMI collection completed for {device_data['hostname']} ({ip_address})")
        log.info(f"   User: {device_data['working_user']}, OS: {device_data.get('os_name', 'Unknown')}")
        
        return device_data
        
    except Exception as e:
        log.error(f"❌ WMI collection failed for {ip_address}: {e}")
        return create_basic_device_data(ip_address, f"WMI Failed: {str(e)[:100]}")

def enhanced_ssh_collection(ip_address: str, username: str, password: str) -> Dict[str, Any]:
    """Enhanced SSH collection for Linux/Unix systems"""
    try:
        import paramiko
        
        log.info(f"🔍 Starting enhanced SSH collection for {ip_address}")
        
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip_address, username=username, password=password, timeout=10)
        
        device_data: Dict[str, str] = {
            'ip_address': ip_address,
            'collection_method': 'SSH Enhanced',
            'data_source': 'SSH Collection',
            'status': 'Active',
            'ping_status': 'Online',
            'device_type': 'Server',
            'classification': 'Server',
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'created_by': 'Enhanced Collector',
            'last_updated_by': 'Enhanced Collector'
        }
        
        # Get hostname
        try:
            stdin, stdout, stderr = ssh.exec_command('hostname')
            hostname = stdout.read().decode().strip()
            device_data['hostname'] = hostname or f"device-{ip_address.replace('.', '-')}"
            device_data['computer_name'] = device_data['hostname']
        except:
            device_data['hostname'] = f"device-{ip_address.replace('.', '-')}"
        
        # Get OS information
        try:
            stdin, stdout, stderr = ssh.exec_command('uname -a')
            uname_output = stdout.read().decode().strip()
            
            if 'Linux' in uname_output:
                device_data['os_name'] = 'Linux'
                device_data['device_type'] = 'Server'
            else:
                device_data['os_name'] = 'Unix'
                device_data['device_type'] = 'Server'
                
            device_data['os_version'] = uname_output
        except:
            device_data['os_name'] = 'Linux'
        
        # Get current user
        try:
            stdin, stdout, stderr = ssh.exec_command('whoami')
            current_user = stdout.read().decode().strip()
            device_data['working_user'] = current_user or username
        except:
            device_data['working_user'] = username
        
        # Get memory info
        try:
            stdin, stdout, stderr = ssh.exec_command('free -m | grep "Mem:" | awk "{print $2}"')
            memory_mb = stdout.read().decode().strip()
            if memory_mb.isdigit():
                device_data['memory_gb'] = str(round(int(memory_mb) / 1024, 2))
                device_data['installed_ram_gb'] = device_data['memory_gb']
        except:
            pass
        
        # Get CPU info
        try:
            stdin, stdout, stderr = ssh.exec_command('nproc')
            cpu_count = stdout.read().decode().strip()
            if cpu_count.isdigit():
                device_data['cpu_cores'] = str(cpu_count)
        except:
            pass
        
        ssh.close()
        
        log.info(f"✅ Enhanced SSH collection completed for {device_data['hostname']} ({ip_address})")
        return device_data
        
    except Exception as e:
        log.error(f"❌ SSH collection failed for {ip_address}: {e}")
        return create_basic_device_data(ip_address, f"SSH Failed: {str(e)[:100]}")

def create_basic_device_data(ip_address: str, error_msg: str = "") -> Dict[str, Any]:
    """Create basic device data when full collection fails"""
    
    # Try to get hostname via ping/nslookup
    hostname = f"device-{ip_address.replace('.', '-')}"
    try:
        import socket
        try:
            hostname_result = socket.gethostbyaddr(ip_address)[0]
            if hostname_result and hostname_result != ip_address:
                hostname = hostname_result
        except:
            pass
    except:
        pass
    
    device_data: Dict[str, str] = {
        'ip_address': ip_address,
        'hostname': hostname,
        'computer_name': hostname,
        'manufacturer': 'Unknown',
        'model': 'Unknown',
        'os_name': 'Unknown',
        'device_type': 'Unknown',
        'working_user': 'N/A',
        'status': 'Detected',
        'ping_status': 'Online',
        'classification': 'Other Asset',
        'collection_method': 'Basic Detection',
        'data_source': 'Network Scan',
        'created_at': datetime.now().isoformat(),
        'last_updated': datetime.now().isoformat(),
        'created_by': 'Enhanced Collector',
        'last_updated_by': 'Enhanced Collector',
        'collection_error': error_msg
    }
    return device_data

def ping_device(ip_address: str) -> bool:
    """Check if device is reachable via ping"""
    try:
        import subprocess
        import platform
        
        if platform.system().lower() == 'windows':
            cmd = ['ping', '-n', '1', '-w', '1000', ip_address]
        else:
            cmd = ['ping', '-c', '1', '-W', '1', ip_address]
        
        result = subprocess.run(cmd, capture_output=True, timeout=5)
        return result.returncode == 0
    except:
        return False

if __name__ == "__main__":
    # Test the enhanced collection
    test_ip = "10.0.21.47"  # Known working device from previous tests
    test_user = ".\\administrator"
    test_pass = "LocalAdmin"
    
    print(f"🧪 Testing enhanced collection on {test_ip}")
    
    if ping_device(test_ip):
        print(f"✅ {test_ip} is reachable")
        
        # Test enhanced WMI collection
        data = enhanced_wmi_collection(test_ip, test_user, test_pass)
        print(f"📊 Collected {len(data)} fields:")
        
        for key, value in data.items():
            if value and value != 'Unknown' and value != 'N/A':
                print(f"   {key}: {value}")
    else:
        print(f"❌ {test_ip} is not reachable")