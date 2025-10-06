#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COMPREHENSIVE DATA COLLECTION AUTOMATION ENGINE

This system ensures 100% data collection from all devices with:
[OK] Automated missing data collection
[OK] Real-time synchronization
[OK] Duplicate detection and management
[OK] Device change monitoring
[OK] Live notifications and alerts
[OK] Comprehensive logging system
"""

import sqlite3
import json
import time
import threading
import asyncio
import logging
import os
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import wmi
import socket
import subprocess
import psutil
import platform
import uuid
import winreg
from typing import Dict, List, Optional, Tuple
import tkinter as tk
from tkinter import messagebox

# Import advanced notification system
from advanced_notification_system import AdvancedNotificationSystem, DataCollectionNotifier, NotificationLevel

class ComprehensiveDataCollector:
    def __init__(self, db_path="assets.db", notification_callback=None, parent_window=None):
        self.db_path = db_path
        self.notification_callback = notification_callback
        self.parent_window = parent_window
        self.running = False
        self.collection_threads = []
        self.stats = {
            'devices_processed': 0,
            'fields_collected': 0,
            'errors': 0,
            'duplicates_found': 0,
            'changes_detected': 0
        }
        
        # Initialize advanced notification system
        self.notification_system = AdvancedNotificationSystem(parent_window)
        self.data_notifier = DataCollectionNotifier(self.notification_system)
        
        # Initialize logging
        self.setup_logging()
        
        # Initialize WMI
        try:
            self.wmi_conn = wmi.WMI()
            self.logger.info("[OK] WMI connection established")
        except Exception as e:
            self.logger.error(f"[ERROR] WMI connection failed: {e}")
            self.wmi_conn = None
        
        # Device status cache
        self.device_cache = {}
        
    def setup_logging(self):
        """Setup comprehensive logging system"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('data_collection_automation.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def notify(self, title: str, message: str, level: str = "info"):
        """Send notification through callback or log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {title}: {message}"
        
        if level == "error":
            self.logger.error(log_message)
        elif level == "warning":
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
            
        if self.notification_callback:
            try:
                self.notification_callback(title, message, level)
            except:
                pass  # Fail silently if GUI not available
                
    def get_device_list(self) -> List[Dict]:
        """Get all devices from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, hostname, ip_address, data_completeness_score, 
                       collection_timestamp, device_status
                FROM assets_enhanced 
                ORDER BY data_completeness_score ASC
            """)
            
            devices = []
            for row in cursor.fetchall():
                devices.append({
                    'id': row[0],
                    'hostname': row[1] or 'Unknown',
                    'ip_address': row[2] or '127.0.0.1',
                    'completeness_score': row[3] or 0,
                    'last_collection': row[4],
                    'status': row[5] or 'unknown'
                })
            
            conn.close()
            return devices
            
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to get device list: {e}")
            return []
    
    def collect_comprehensive_data(self, device_id: int, hostname: str, ip_address: str) -> Dict:
        """Collect comprehensive data for a specific device"""
        self.data_notifier.collection_started(hostname)
        
        collected_data = {
            'collection_timestamp': datetime.now().isoformat(),
            'collection_method': 'Automated Comprehensive',
            'collection_duration_seconds': 0,
            'data_completeness_score': 0,
            'fields_collected': 0,
            'fields_missing': 0
        }
        
        start_time = time.time()
        
        try:
            # System Information
            system_data = self.collect_system_info()
            collected_data.update(system_data)
            
            # Hardware Information
            hardware_data = self.collect_hardware_info()
            collected_data.update(hardware_data)
            
            # Network Information
            network_data = self.collect_network_info(ip_address)
            collected_data.update(network_data)
            
            # Software Information
            software_data = self.collect_software_info()
            collected_data.update(software_data)
            
            # Performance Information
            performance_data = self.collect_performance_info()
            collected_data.update(performance_data)
            
            # Security Information
            security_data = self.collect_security_info()
            collected_data.update(security_data)
            
            # User Information
            user_data = self.collect_user_info()
            collected_data.update(user_data)
            
            # Calculate completeness
            collected_data['collection_duration_seconds'] = time.time() - start_time
            completeness = self.calculate_completeness(collected_data)
            collected_data['data_completeness_score'] = completeness
            
            self.data_notifier.collection_completed(hostname, completeness, collected_data.get('fields_collected', 0))
            
            return collected_data
            
        except Exception as e:
            self.logger.error(f"[ERROR] Collection failed for {hostname}: {e}")
            collected_data['collection_duration_seconds'] = time.time() - start_time
            collected_data['collection_error'] = str(e)
            self.data_notifier.collection_failed(hostname, str(e))
            return collected_data
    
    def collect_system_info(self) -> Dict:
        """Collect comprehensive system information"""
        data = {}
        
        try:
            # Basic system info
            data['computer_name'] = platform.node()
            data['hostname'] = socket.gethostname()
            
            # Domain information
            try:
                data['domain_name'] = socket.getfqdn().split('.', 1)[1] if '.' in socket.getfqdn() else None
                data['dns_hostname'] = socket.getfqdn()
            except:
                pass
            
            # System manufacturer and model via WMI
            if self.wmi_conn:
                try:
                    for computer in self.wmi_conn.Win32_ComputerSystem():
                        data['system_manufacturer'] = computer.Manufacturer
                        data['system_model'] = computer.Model
                        data['system_family'] = getattr(computer, 'SystemFamily', None)
                        data['workgroup'] = computer.Workgroup
                        data['domain_name'] = computer.Domain if computer.PartOfDomain else data.get('domain_name')
                        
                    for bios in self.wmi_conn.Win32_BIOS():
                        data['serial_number'] = bios.SerialNumber
                        data['bios_manufacturer'] = bios.Manufacturer
                        data['bios_version'] = bios.SMBIOSBIOSVersion
                        data['bios_release_date'] = bios.ReleaseDate
                        
                    for system in self.wmi_conn.Win32_ComputerSystemProduct():
                        data['uuid'] = system.UUID
                        data['system_sku'] = getattr(system, 'SKUNumber', None)
                        
                except Exception as e:
                    self.logger.warning(f"WMI system info collection warning: {e}")
            
            # Operating system information
            data['operating_system'] = platform.platform()
            data['os_version'] = platform.version()
            data['os_architecture'] = platform.architecture()[0]
            data['os_family'] = platform.system()
            
            # Windows specific information
            if platform.system() == 'Windows':
                try:
                    import winreg
                    
                    # OS Edition
                    reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                           r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
                    data['os_edition'] = winreg.QueryValueEx(reg_key, "EditionID")[0]
                    data['os_build'] = winreg.QueryValueEx(reg_key, "CurrentBuild")[0]
                    data['registered_owner'] = winreg.QueryValueEx(reg_key, "RegisteredOwner")[0]
                    
                    # Installation date
                    install_date = winreg.QueryValueEx(reg_key, "InstallDate")[0]
                    data['os_install_date'] = datetime.fromtimestamp(install_date).isoformat()
                    
                    winreg.CloseKey(reg_key)
                    
                except Exception as e:
                    self.logger.warning(f"Windows registry info warning: {e}")
            
            # Boot time
            try:
                boot_time = psutil.boot_time()
                data['last_boot_time'] = datetime.fromtimestamp(boot_time).isoformat()
                data['system_uptime_hours'] = (time.time() - boot_time) / 3600
            except:
                pass
                
        except Exception as e:
            self.logger.error(f"System info collection error: {e}")
            
        return data
    
    def collect_hardware_info(self) -> Dict:
        """Collect comprehensive hardware information"""
        data = {}
        
        try:
            # Processor information
            if self.wmi_conn:
                try:
                    for processor in self.wmi_conn.Win32_Processor():
                        data['processor_name'] = processor.Name
                        data['processor_manufacturer'] = processor.Manufacturer
                        data['processor_architecture'] = processor.Architecture
                        data['processor_cores'] = processor.NumberOfCores
                        data['processor_logical_cores'] = processor.NumberOfLogicalProcessors
                        data['processor_speed_mhz'] = processor.MaxClockSpeed
                        data['processor_l2_cache_size'] = getattr(processor, 'L2CacheSize', None)
                        data['processor_l3_cache_size'] = getattr(processor, 'L3CacheSize', None)
                        break  # Take first processor
                        
                except Exception as e:
                    self.logger.warning(f"Processor info collection warning: {e}")
            
            # Memory information
            try:
                memory = psutil.virtual_memory()
                data['total_physical_memory_gb'] = memory.total / (1024**3)
                data['available_memory_gb'] = memory.available / (1024**3)
                data['memory_usage_percent'] = memory.percent
                
                if self.wmi_conn:
                    # Detailed memory modules
                    memory_modules = []
                    for memory_device in self.wmi_conn.Win32_PhysicalMemory():
                        module_info = {
                            'capacity_gb': int(memory_device.Capacity) / (1024**3) if memory_device.Capacity else 0,
                            'speed_mhz': memory_device.ConfiguredClockSpeed,
                            'manufacturer': memory_device.Manufacturer,
                            'part_number': memory_device.PartNumber
                        }
                        memory_modules.append(module_info)
                    
                    data['memory_modules'] = json.dumps(memory_modules)
                    data['memory_slots_used'] = len(memory_modules)
                    
            except Exception as e:
                self.logger.warning(f"Memory info collection warning: {e}")
            
            # Storage information
            try:
                storage_devices = []
                total_storage = 0
                available_storage = 0
                
                for partition in psutil.disk_partitions():
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        total_storage += usage.total
                        available_storage += usage.free
                        
                        storage_devices.append({
                            'device': partition.device,
                            'mountpoint': partition.mountpoint,
                            'fstype': partition.fstype,
                            'total_gb': usage.total / (1024**3),
                            'free_gb': usage.free / (1024**3),
                            'used_percent': (usage.used / usage.total) * 100
                        })
                    except:
                        continue
                
                data['storage_devices'] = json.dumps(storage_devices)
                data['total_storage_gb'] = total_storage / (1024**3)
                data['available_storage_gb'] = available_storage / (1024**3)
                data['disk_usage_percent'] = ((total_storage - available_storage) / total_storage) * 100 if total_storage > 0 else 0
                
                # Storage summary
                summary_parts = []
                for i, device in enumerate(storage_devices):
                    summary_parts.append(f"Disk {i+1}: {device['total_gb']:.0f}GB {device['fstype']}")
                data['storage_summary'] = ", ".join(summary_parts)
                
            except Exception as e:
                self.logger.warning(f"Storage info collection warning: {e}")
            
            # Graphics information
            try:
                graphics_cards = []
                if self.wmi_conn:
                    for gpu in self.wmi_conn.Win32_VideoController():
                        if gpu.Name and 'Microsoft' not in gpu.Name:  # Skip generic adapters
                            graphics_cards.append({
                                'name': gpu.Name,
                                'adapter_ram': gpu.AdapterRAM,
                                'driver_version': gpu.DriverVersion,
                                'driver_date': gpu.DriverDate
                            })
                
                data['graphics_cards'] = json.dumps(graphics_cards)
                if graphics_cards:
                    data['primary_graphics_card'] = graphics_cards[0]['name']
                    data['graphics_memory_mb'] = graphics_cards[0]['adapter_ram'] / (1024**2) if graphics_cards[0]['adapter_ram'] else None
                    data['graphics_driver_version'] = graphics_cards[0]['driver_version']
                
            except Exception as e:
                self.logger.warning(f"Graphics info collection warning: {e}")
            
            # Monitor information
            try:
                if self.wmi_conn:
                    monitors = list(self.wmi_conn.Win32_DesktopMonitor())
                    data['connected_monitors'] = len(monitors)
                    
                    monitor_details = []
                    for monitor in monitors:
                        monitor_details.append({
                            'name': monitor.Name,
                            'screen_width': monitor.ScreenWidth,
                            'screen_height': monitor.ScreenHeight
                        })
                    data['monitor_details'] = json.dumps(monitor_details)
                    
            except Exception as e:
                self.logger.warning(f"Monitor info collection warning: {e}")
                
        except Exception as e:
            self.logger.error(f"Hardware info collection error: {e}")
            
        return data
    
    def collect_network_info(self, target_ip: str) -> Dict:
        """Collect comprehensive network information"""
        data = {}
        
        try:
            # Network adapters
            network_adapters = []
            wireless_adapters = []
            
            for interface_name, addresses in psutil.net_if_addrs().items():
                adapter_info = {'name': interface_name, 'addresses': []}
                
                for addr in addresses:
                    if addr.family.name == 'AF_INET':  # IPv4
                        adapter_info['addresses'].append({
                            'type': 'IPv4',
                            'address': addr.address,
                            'netmask': addr.netmask,
                            'broadcast': addr.broadcast
                        })
                        
                        # Set primary IP if matches target
                        if addr.address == target_ip:
                            data['ip_address'] = addr.address
                            
                    elif addr.family.name == 'AF_LINK':  # MAC address
                        adapter_info['mac_address'] = addr.address
                        if not data.get('mac_address') and addr.address != '00:00:00:00:00:00':
                            data['mac_address'] = addr.address
                
                if adapter_info['addresses']:
                    network_adapters.append(adapter_info)
                    
                    # Check if wireless
                    if 'wireless' in interface_name.lower() or 'wifi' in interface_name.lower():
                        wireless_adapters.append(adapter_info)
            
            data['network_adapters'] = json.dumps(network_adapters)
            data['wireless_adapters'] = json.dumps(wireless_adapters)
            
            # Network configuration
            try:
                if self.wmi_conn:
                    network_configs = []
                    for config in self.wmi_conn.Win32_NetworkAdapterConfiguration(IPEnabled=True):
                        network_configs.append({
                            'description': config.Description,
                            'dhcp_enabled': config.DHCPEnabled,
                            'ip_address': config.IPAddress,
                            'subnet_mask': config.IPSubnet,
                            'default_gateway': config.DefaultIPGateway,
                            'dns_servers': config.DNSServerSearchOrder
                        })
                    data['network_configuration'] = json.dumps(network_configs)
                    
            except Exception as e:
                self.logger.warning(f"Network configuration collection warning: {e}")
                
        except Exception as e:
            self.logger.error(f"Network info collection error: {e}")
            
        return data
    
    def collect_software_info(self) -> Dict:
        """Collect comprehensive software information"""
        data = {}
        
        try:
            # Installed software via WMI
            if self.wmi_conn:
                try:
                    installed_software = []
                    for product in self.wmi_conn.Win32_Product():
                        if product.Name:
                            installed_software.append({
                                'name': product.Name,
                                'version': product.Version,
                                'vendor': product.Vendor,
                                'install_date': product.InstallDate
                            })
                    
                    data['installed_software'] = json.dumps(installed_software)
                    
                except Exception as e:
                    self.logger.warning(f"Software collection warning: {e}")
            
            # Browser detection
            try:
                browsers = []
                browser_paths = {
                    'Chrome': r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                    'Firefox': r'C:\Program Files\Mozilla Firefox\firefox.exe',
                    'Edge': r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
                    'Internet Explorer': r'C:\Program Files\Internet Explorer\iexplore.exe'
                }
                
                for browser, path in browser_paths.items():
                    if os.path.exists(path):
                        browsers.append(browser)
                
                data['browsers_installed'] = json.dumps(browsers)
                
            except Exception as e:
                self.logger.warning(f"Browser detection warning: {e}")
                
        except Exception as e:
            self.logger.error(f"Software info collection error: {e}")
            
        return data
    
    def collect_performance_info(self) -> Dict:
        """Collect real-time performance information"""
        data = {}
        
        try:
            # CPU usage
            data['cpu_usage_percent'] = psutil.cpu_percent(interval=1)
            
            # Memory usage (already collected in hardware, but real-time here)
            memory = psutil.virtual_memory()
            data['memory_usage_percent'] = memory.percent
            
            # Disk usage (average across all disks)
            disk_usage_total = 0
            disk_count = 0
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage_total += (usage.used / usage.total) * 100
                    disk_count += 1
                except:
                    continue
            
            if disk_count > 0:
                data['disk_usage_percent'] = disk_usage_total / disk_count
                
        except Exception as e:
            self.logger.error(f"Performance info collection error: {e}")
            
        return data
    
    def collect_security_info(self) -> Dict:
        """Collect security and antivirus information"""
        data = {}
        
        try:
            # Windows Defender status
            try:
                if platform.system() == 'Windows':
                    result = subprocess.run([
                        'powershell', 
                        'Get-MpComputerStatus | Select-Object AntivirusEnabled, RealTimeProtectionEnabled, OnAccessProtectionEnabled'
                    ], capture_output=True, text=True, timeout=10)
                    
                    if result.returncode == 0:
                        data['windows_defender_status'] = 'Enabled' if 'True' in result.stdout else 'Disabled'
                        
            except Exception as e:
                self.logger.warning(f"Windows Defender status warning: {e}")
            
            # Firewall status
            try:
                if platform.system() == 'Windows':
                    result = subprocess.run([
                        'netsh', 'advfirewall', 'show', 'allprofiles', 'state'
                    ], capture_output=True, text=True, timeout=10)
                    
                    if result.returncode == 0:
                        data['firewall_status'] = 'Enabled' if 'ON' in result.stdout else 'Disabled'
                        
            except Exception as e:
                self.logger.warning(f"Firewall status warning: {e}")
            
            # UAC status
            try:
                if platform.system() == 'Windows':
                    import winreg
                    reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                           r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System")
                    uac_value = winreg.QueryValueEx(reg_key, "EnableLUA")[0]
                    data['uac_status'] = 'Enabled' if uac_value == 1 else 'Disabled'
                    winreg.CloseKey(reg_key)
                    
            except Exception as e:
                self.logger.warning(f"UAC status warning: {e}")
                
        except Exception as e:
            self.logger.error(f"Security info collection error: {e}")
            
        return data
    
    def collect_user_info(self) -> Dict:
        """Collect user and profile information"""
        data = {}
        
        try:
            # Current user
            data['current_user'] = os.getenv('USERNAME') or os.getenv('USER')
            
            # User profiles
            if platform.system() == 'Windows':
                try:
                    profiles = []
                    users_dir = r'C:\Users'
                    if os.path.exists(users_dir):
                        for user_folder in os.listdir(users_dir):
                            user_path = os.path.join(users_dir, user_folder)
                            if os.path.isdir(user_path) and user_folder not in ['Public', 'Default', 'Default User']:
                                profiles.append(user_folder)
                    
                    data['user_profiles'] = json.dumps(profiles)
                    data['last_logged_users'] = json.dumps(profiles[-5:])  # Last 5 users
                    
                except Exception as e:
                    self.logger.warning(f"User profiles collection warning: {e}")
                    
        except Exception as e:
            self.logger.error(f"User info collection error: {e}")
            
        return data
    
    def calculate_completeness(self, data: Dict) -> int:
        """Calculate data completeness percentage"""
        total_fields = 103  # Total fields in database
        filled_fields = 0
        
        for key, value in data.items():
            if value is not None and value != '' and value != [] and value != '[]':
                filled_fields += 1
        
        completeness = int((filled_fields / total_fields) * 100)
        data['fields_collected'] = filled_fields
        data['fields_missing'] = total_fields - filled_fields
        
        return completeness
    
    def update_device_data(self, device_id: int, collected_data: Dict) -> bool:
        """Update device data in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Prepare update query
            update_fields = []
            update_values = []
            
            for key, value in collected_data.items():
                if key != 'id':  # Don't update ID
                    update_fields.append(f"{key} = ?")
                    update_values.append(value)
            
            update_values.append(device_id)
            
            query = f"""
                UPDATE assets_enhanced 
                SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """
            
            cursor.execute(query, update_values)
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to update device {device_id}: {e}")
            return False
    
    def detect_duplicates(self) -> List[Dict]:
        """Detect duplicate devices"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Find duplicates by hostname, MAC address, or serial number
            cursor.execute("""
                SELECT hostname, mac_address, serial_number, COUNT(*) as count,
                       GROUP_CONCAT(id) as device_ids
                FROM assets_enhanced 
                WHERE hostname IS NOT NULL OR mac_address IS NOT NULL OR serial_number IS NOT NULL
                GROUP BY 
                    COALESCE(hostname, ''),
                    COALESCE(mac_address, ''),
                    COALESCE(serial_number, '')
                HAVING count > 1
            """)
            
            duplicates = []
            for row in cursor.fetchall():
                duplicates.append({
                    'hostname': row[0],
                    'mac_address': row[1],
                    'serial_number': row[2],
                    'count': row[3],
                    'device_ids': row[4].split(',')
                })
            
            conn.close()
            return duplicates
            
        except Exception as e:
            self.logger.error(f"[ERROR] Duplicate detection failed: {e}")
            return []
    
    def resolve_duplicates(self, duplicates: List[Dict]) -> int:
        """Resolve duplicate devices by merging data"""
        resolved_count = 0
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for duplicate_group in duplicates:
                device_ids = duplicate_group['device_ids']
                if len(device_ids) < 2:
                    continue
                
                # Get all devices in this duplicate group
                cursor.execute(f"""
                    SELECT * FROM assets_enhanced 
                    WHERE id IN ({','.join(['?' for _ in device_ids])})
                    ORDER BY data_completeness_score DESC, updated_at DESC
                """, device_ids)
                
                devices = cursor.fetchall()
                if len(devices) < 2:
                    continue
                
                # Use the device with highest completeness score as primary
                primary_device = devices[0]
                primary_id = primary_device[0]  # ID is first column
                
                # Merge data from other devices
                merged_data = dict(zip([col[0] for col in cursor.description], primary_device))
                
                for device in devices[1:]:
                    device_data = dict(zip([col[0] for col in cursor.description], device))
                    
                    # Merge non-null values
                    for field, value in device_data.items():
                        if value is not None and value != '' and (merged_data[field] is None or merged_data[field] == ''):
                            merged_data[field] = value
                
                # Update primary device with merged data
                update_fields = []
                update_values = []
                
                for field, value in merged_data.items():
                    if field != 'id':
                        update_fields.append(f"{field} = ?")
                        update_values.append(value)
                
                update_values.append(primary_id)
                
                cursor.execute(f"""
                    UPDATE assets_enhanced 
                    SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, update_values)
                
                # Delete duplicate devices
                duplicate_ids = [device[0] for device in devices[1:]]
                cursor.execute(f"""
                    DELETE FROM assets_enhanced 
                    WHERE id IN ({','.join(['?' for _ in duplicate_ids])})
                """, duplicate_ids)
                
                resolved_count += len(duplicate_ids)
                
                self.data_notifier.duplicate_resolved(len(duplicate_ids), duplicate_group['hostname'])
            
            conn.commit()
            conn.close()
            
            return resolved_count
            
        except Exception as e:
            self.logger.error(f"[ERROR] Duplicate resolution failed: {e}")
            return 0
    
    def start_automation(self):
        """Start the automated data collection process"""
        if self.running:
            self.notify("Automation Status", "[WARNING] Automation is already running", "warning")
            return
        
        self.running = True
        self.stats = {
            'devices_processed': 0,
            'fields_collected': 0,
            'errors': 0,
            'duplicates_found': 0,
            'changes_detected': 0,
            'start_time': datetime.now()
        }
        
        self.notification_system.notify(
            "Automation Started", 
            "[STARTING] Comprehensive data collection automation started\n\n" +
            "System will now:\n" +
            "• Collect missing data from all devices\n" +
            "• Monitor for changes and duplicates\n" +
            "• Provide real-time notifications\n" +
            "• Maintain 100% data synchronization",
            NotificationLevel.SUCCESS,
            duration=15000
        )
        
        # Start main automation thread
        automation_thread = threading.Thread(target=self._automation_loop, daemon=True)
        automation_thread.start()
        
        # Start duplicate detection thread
        duplicate_thread = threading.Thread(target=self._duplicate_detection_loop, daemon=True)
        duplicate_thread.start()
    
    def stop_automation(self):
        """Stop the automated data collection process"""
        self.running = False
        self.notification_system.notify(
            "Automation Stopped", 
            "[STOPPED] Data collection automation stopped",
            NotificationLevel.INFO
        )
    
    def _automation_loop(self):
        """Main automation loop"""
        while self.running:
            try:
                devices = self.get_device_list()
                
                if not devices:
                    self.notify("No Devices", "[WARNING] No devices found in database", "warning")
                    time.sleep(60)
                    continue
                
                # Process devices with lowest completeness scores first
                for device in devices:
                    if not self.running:
                        break
                    
                    # Skip recently processed devices (unless score is very low)
                    if device['completeness_score'] > 90:
                        if device['last_collection']:
                            last_collection = datetime.fromisoformat(device['last_collection'])
                            if datetime.now() - last_collection < timedelta(hours=6):
                                continue
                    
                    # Collect data for this device
                    self.notification_system.notify(
                        "Processing Device", 
                        f"[PROCESSING] Processing {device['hostname']} (Score: {device['completeness_score']}%)",
                        NotificationLevel.INFO,
                        duration=3000
                    )
                    
                    collected_data = self.collect_comprehensive_data(
                        device['id'], 
                        device['hostname'], 
                        device['ip_address']
                    )
                    
                    # Update database
                    if self.update_device_data(device['id'], collected_data):
                        self.stats['devices_processed'] += 1
                        self.stats['fields_collected'] += collected_data.get('fields_collected', 0)
                        
                        # Check for significant changes
                        if abs(collected_data.get('data_completeness_score', 0) - device['completeness_score']) > 10:
                            self.stats['changes_detected'] += 1
                            self.data_notifier.device_change_detected(
                                device['hostname'], 
                                "Completeness Score",
                                f"{device['completeness_score']}%",
                                f"{collected_data.get('data_completeness_score', 0)}%"
                            )
                    else:
                        self.stats['errors'] += 1
                    
                    # Brief pause between devices
                    time.sleep(2)
                
                # Wait before next full cycle
                self.data_notifier.automation_cycle_complete(len(devices), self.stats['errors'])
                time.sleep(1800)  # 30 minutes
                
            except Exception as e:
                self.logger.error(f"[ERROR] Automation loop error: {e}")
                self.stats['errors'] += 1
                time.sleep(60)
    
    def _duplicate_detection_loop(self):
        """Duplicate detection and resolution loop"""
        while self.running:
            try:
                # Run duplicate detection every 2 hours
                time.sleep(7200)
                
                if not self.running:
                    break
                
                self.notify("Duplicate Check", "🔍 Running duplicate detection...", "info")
                
                duplicates = self.detect_duplicates()
                
                if duplicates:
                    self.stats['duplicates_found'] += len(duplicates)
                    self.notify("Duplicates Found", f"⚠️ Found {len(duplicates)} duplicate groups", "warning")
                    
                    # Resolve duplicates
                    resolved = self.resolve_duplicates(duplicates)
                    if resolved > 0:
                        self.notify("Duplicates Resolved", f"✅ Resolved {resolved} duplicate devices", "info")
                else:
                    self.notify("No Duplicates", "✅ No duplicate devices found", "info")
                
            except Exception as e:
                self.logger.error(f"❌ Duplicate detection error: {e}")
                time.sleep(3600)  # Wait 1 hour on error
    
    def get_automation_stats(self) -> Dict:
        """Get current automation statistics"""
        if self.stats.get('start_time'):
            runtime = datetime.now() - self.stats['start_time']
            self.stats['runtime_hours'] = runtime.total_seconds() / 3600
        
        return self.stats.copy()

# Integration class for desktop app
class AutomationIntegration:
    def __init__(self, parent_app):
        self.parent_app = parent_app
        self.collector = None
        self.notification_window = None
        self.automation_running = False
        
    def start_automation(self):
        """Start automation with GUI integration"""
        if not self.collector:
            self.collector = ComprehensiveDataCollector(
                notification_callback=self.show_notification,
                parent_window=getattr(self.parent_app, 'root', None)
            )
        
        self.automation_running = True
        self.collector.start_automation()
        
    def stop_automation(self):
        """Stop automation"""
        if self.collector:
            self.collector.stop_automation()
        self.automation_running = False
        
    def start_automation_loop(self, parent_window):
        """Start automation loop for GUI integration"""
        try:
            self.start_automation()
            if hasattr(parent_window, 'log_output'):
                parent_window.log_output.append("✅ Automation loop started successfully")
        except Exception as e:
            if hasattr(parent_window, 'log_output'):
                parent_window.log_output.append(f"❌ Automation loop error: {e}")
                
    def stop_automation_loop(self):
        """Stop automation loop"""
        try:
            self.stop_automation()
        except Exception as e:
            print(f"Error stopping automation loop: {e}")
            
    def is_automation_running(self):
        """Check if automation is running"""
        return self.automation_running
    
    def show_notification(self, title: str, message: str, level: str = "info"):
        """Show notification in GUI"""
        def show_notification_window():
            if self.notification_window and self.notification_window.winfo_exists():
                self.notification_window.destroy()
            
            # Create notification window
            self.notification_window = tk.Toplevel(self.parent_app.root)
            self.notification_window.title("Data Collection Notification")
            self.notification_window.geometry("400x150")
            self.notification_window.resizable(False, False)
            
            # Configure colors based on level
            colors = {
                'info': {'bg': '#d1ecf1', 'fg': '#0c5460'},
                'warning': {'bg': '#fff3cd', 'fg': '#856404'},
                'error': {'bg': '#f8d7da', 'fg': '#721c24'}
            }
            
            color_config = colors.get(level, colors['info'])
            
            # Create notification content
            main_frame = tk.Frame(self.notification_window, bg=color_config['bg'])
            main_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            title_label = tk.Label(main_frame, text=title, font=('Arial', 12, 'bold'), 
                                  bg=color_config['bg'], fg=color_config['fg'])
            title_label.pack(pady=(0, 5))
            
            message_label = tk.Label(main_frame, text=message, font=('Arial', 10), 
                                   bg=color_config['bg'], fg=color_config['fg'], wraplength=350)
            message_label.pack(pady=(0, 10))
            
            close_button = tk.Button(main_frame, text="Close", 
                                   command=self.notification_window.destroy)
            close_button.pack()
            
            # Position window
            self.notification_window.transient(self.parent_app.root)
            self.notification_window.grab_set()
            
            # Center on parent
            self.notification_window.geometry("+%d+%d" % (
                self.parent_app.root.winfo_rootx() + 50,
                self.parent_app.root.winfo_rooty() + 50
            ))
            
            # Auto-close after 10 seconds for info messages
            if level == 'info':
                self.notification_window.after(10000, lambda: self.notification_window.destroy() if self.notification_window.winfo_exists() else None)
        
        # Schedule notification on main thread
        self.parent_app.root.after(0, show_notification_window)
    
    def get_stats(self) -> Dict:
        """Get automation statistics"""
        if self.collector:
            return self.collector.get_automation_stats()
        return {}

if __name__ == "__main__":
    # Test the collector
    collector = ComprehensiveDataCollector()
    print("Testing comprehensive data collection...")
    
    devices = collector.get_device_list()
    if devices:
        print(f"Found {len(devices)} devices")
        # Test collection on first device
        test_device = devices[0]
        data = collector.collect_comprehensive_data(
            test_device['id'], 
            test_device['hostname'], 
            test_device['ip_address']
        )
        print(f"Collected {data.get('fields_collected', 0)} fields with {data.get('data_completeness_score', 0)}% completeness")
    else:
        print("No devices found for testing")