#!/usr/bin/env python3
"""
Complete Database Schema Analysis and WMI Data Collection
Collect ALL possible WMI data based on database columns
"""

import sqlite3
import json
from collections import defaultdict

def analyze_database_schema():
    print("=" * 80)
    print("🔍 COMPLETE DATABASE SCHEMA ANALYSIS")
    print("=" * 80)
    
    conn = sqlite3.connect('assets.db')
    cursor = conn.cursor()
    
    # Get all column information
    cursor.execute("PRAGMA table_info(assets)")
    columns = cursor.fetchall()
    
    print(f"📊 Total database columns: {len(columns)}")
    print()
    
    # Categorize columns by data type/source
    wmi_columns = []
    ssh_columns = []
    snmp_columns = []
    nmap_columns = []
    general_columns = []
    
    # Detailed WMI field categorization
    wmi_categories = {
        'SYSTEM_INFO': [],
        'HARDWARE': [],
        'MEMORY': [],
        'PROCESSOR': [],
        'STORAGE': [],
        'NETWORK': [],
        'SOFTWARE': [],
        'SERVICES': [],
        'SECURITY': [],
        'PERFORMANCE': [],
        'BIOS': [],
        'MOTHERBOARD': [],
        'GRAPHICS': [],
        'AUDIO': [],
        'USB': [],
        'PRINTER': [],
        'UPDATES': [],
        'USERS': [],
        'DOMAINS': [],
        'ENVIRONMENT': []
    }
    
    for col in columns:
        field_name = col[1].lower()
        field_full = col[1]
        
        # WMI field classification
        if any(keyword in field_name for keyword in [
            'operating_system', 'windows_', 'computer_name', 'domain_', 'workgroup',
            'system_', 'manufacturer', 'model', 'serial_number', 'asset_tag'
        ]):
            wmi_categories['SYSTEM_INFO'].append(field_full)
            wmi_columns.append(field_full)
            
        elif any(keyword in field_name for keyword in [
            'processor_', 'cpu_', 'cores', 'threads', 'speed', 'architecture'
        ]):
            wmi_categories['PROCESSOR'].append(field_full)
            wmi_columns.append(field_full)
            
        elif any(keyword in field_name for keyword in [
            'memory_', 'ram_', 'physical_memory', 'virtual_memory', 'page_file'
        ]):
            wmi_categories['MEMORY'].append(field_full)
            wmi_columns.append(field_full)
            
        elif any(keyword in field_name for keyword in [
            'disk_', 'storage_', 'drive_', 'hard_drive', 'volume_', 'partition_'
        ]):
            wmi_categories['STORAGE'].append(field_full)
            wmi_columns.append(field_full)
            
        elif any(keyword in field_name for keyword in [
            'network_', 'adapter_', 'ip_', 'mac_', 'dns_', 'dhcp_', 'gateway'
        ]):
            wmi_categories['NETWORK'].append(field_full)
            wmi_columns.append(field_full)
            
        elif any(keyword in field_name for keyword in [
            'installed_software', 'software_', 'application_', 'program_'
        ]):
            wmi_categories['SOFTWARE'].append(field_full)
            wmi_columns.append(field_full)
            
        elif any(keyword in field_name for keyword in [
            'service', 'running_', 'stopped_', 'startup_'
        ]):
            wmi_categories['SERVICES'].append(field_full)
            wmi_columns.append(field_full)
            
        elif any(keyword in field_name for keyword in [
            'bios_', 'firmware_'
        ]):
            wmi_categories['BIOS'].append(field_full)
            wmi_columns.append(field_full)
            
        elif any(keyword in field_name for keyword in [
            'motherboard_', 'baseboard_', 'chassis_'
        ]):
            wmi_categories['MOTHERBOARD'].append(field_full)
            wmi_columns.append(field_full)
            
        elif any(keyword in field_name for keyword in [
            'graphics_', 'video_', 'display_', 'monitor_'
        ]):
            wmi_categories['GRAPHICS'].append(field_full)
            wmi_columns.append(field_full)
            
        elif any(keyword in field_name for keyword in [
            'audio_', 'sound_'
        ]):
            wmi_categories['AUDIO'].append(field_full)
            wmi_columns.append(field_full)
            
        elif any(keyword in field_name for keyword in [
            'usb_', 'port_'
        ]):
            wmi_categories['USB'].append(field_full)
            wmi_columns.append(field_full)
            
        elif any(keyword in field_name for keyword in [
            'printer_', 'print_'
        ]):
            wmi_categories['PRINTER'].append(field_full)
            wmi_columns.append(field_full)
            
        elif any(keyword in field_name for keyword in [
            'update_', 'hotfix_', 'patch_'
        ]):
            wmi_categories['UPDATES'].append(field_full)
            wmi_columns.append(field_full)
            
        elif any(keyword in field_name for keyword in [
            'user_', 'account_', 'profile_', 'privilege_'
        ]):
            wmi_categories['USERS'].append(field_full)
            wmi_columns.append(field_full)
            
        elif any(keyword in field_name for keyword in [
            'antivirus_', 'firewall_', 'security_'
        ]):
            wmi_categories['SECURITY'].append(field_full)
            wmi_columns.append(field_full)
            
        elif any(keyword in field_name for keyword in [
            'performance_', 'utilization_', 'usage_'
        ]):
            wmi_categories['PERFORMANCE'].append(field_full)
            wmi_columns.append(field_full)
            
        elif any(keyword in field_name for keyword in [
            'environment_', 'variable_', 'path_'
        ]):
            wmi_categories['ENVIRONMENT'].append(field_full)
            wmi_columns.append(field_full)
            
        # SSH fields
        elif any(keyword in field_name for keyword in [
            'ssh_', 'linux_', 'kernel_', 'distribution_', 'mount_', 'cron_'
        ]):
            ssh_columns.append(field_full)
            
        # SNMP fields
        elif any(keyword in field_name for keyword in [
            'snmp_', 'interface_', 'switch_', 'router_', 'vlan_'
        ]):
            snmp_columns.append(field_full)
            
        # NMAP fields
        elif any(keyword in field_name for keyword in [
            'nmap_', 'open_ports', 'closed_ports', 'os_fingerprint'
        ]):
            nmap_columns.append(field_full)
            
        else:
            # Check if it might still be WMI related
            if any(wmi_keyword in field_name for wmi_keyword in [
                'installed_', 'total_', 'available_', 'free_', 'used_',
                'version_', 'name_', 'type_', 'status_', 'location_'
            ]):
                wmi_categories['SYSTEM_INFO'].append(field_full)
                wmi_columns.append(field_full)
            else:
                general_columns.append(field_full)
    
    # Display categorized WMI fields
    print("🪟 WMI DATA FIELDS BY CATEGORY:")
    print("=" * 50)
    
    total_wmi_fields = 0
    for category, fields in wmi_categories.items():
        if fields:
            print(f"\n📊 {category.replace('_', ' ')} ({len(fields)} fields):")
            for field in fields[:10]:  # Show first 10
                print(f"   • {field}")
            if len(fields) > 10:
                print(f"   ... and {len(fields) - 10} more fields")
            total_wmi_fields += len(fields)
    
    print(f"\n🔢 SUMMARY:")
    print(f"   • Total WMI fields: {total_wmi_fields}")
    print(f"   • SSH fields: {len(ssh_columns)}")
    print(f"   • SNMP fields: {len(snmp_columns)}")
    print(f"   • NMAP fields: {len(nmap_columns)}")
    print(f"   • General fields: {len(general_columns)}")
    print(f"   • TOTAL: {len(columns)} database columns")
    
    conn.close()
    return wmi_categories, wmi_columns

def create_comprehensive_wmi_mapping():
    """Create comprehensive WMI class to database field mapping"""
    
    wmi_mapping = {
        # System Information
        'Win32_ComputerSystem': {
            'computer_name': 'Name',
            'manufacturer': 'Manufacturer', 
            'model': 'Model',
            'system_type': 'SystemType',
            'total_physical_memory': 'TotalPhysicalMemory',
            'domain_name': 'Domain',
            'workgroup': 'Workgroup',
            'primary_owner_name': 'PrimaryOwnerName',
            'system_startup_options': 'SystemStartupOptions',
            'thermal_state': 'ThermalState',
            'power_state': 'PowerState'
        },
        
        # Operating System
        'Win32_OperatingSystem': {
            'operating_system': 'Caption',
            'os_version': 'Version',
            'os_build_number': 'BuildNumber',
            'os_service_pack': 'ServicePackMajorVersion',
            'os_architecture': 'OSArchitecture',
            'windows_directory': 'WindowsDirectory',
            'system_directory': 'SystemDirectory',
            'boot_device': 'BootDevice',
            'system_device': 'SystemDevice',
            'install_date': 'InstallDate',
            'last_boot_up_time': 'LastBootUpTime',
            'local_date_time': 'LocalDateTime',
            'locale': 'Locale',
            'country_code': 'CountryCode',
            'time_zone': 'CurrentTimeZone',
            'total_virtual_memory_size': 'TotalVirtualMemorySize',
            'total_visible_memory_size': 'TotalVisibleMemorySize',
            'free_physical_memory': 'FreePhysicalMemory',
            'free_virtual_memory': 'FreeVirtualMemory'
        },
        
        # Processor Information
        'Win32_Processor': {
            'processor_name': 'Name',
            'processor_manufacturer': 'Manufacturer',
            'processor_architecture': 'Architecture',
            'processor_family': 'Family',
            'processor_speed': 'MaxClockSpeed',
            'processor_cores': 'NumberOfCores',
            'processor_logical_processors': 'NumberOfLogicalProcessors',
            'processor_l2_cache_size': 'L2CacheSize',
            'processor_l3_cache_size': 'L3CacheSize',
            'processor_voltage': 'CurrentVoltage',
            'processor_description': 'Description',
            'processor_socket_designation': 'SocketDesignation'
        },
        
        # Memory Information
        'Win32_PhysicalMemory': {
            'memory_manufacturer': 'Manufacturer',
            'memory_capacity': 'Capacity',
            'memory_speed': 'Speed',
            'memory_type': 'MemoryType',
            'memory_form_factor': 'FormFactor',
            'memory_device_locator': 'DeviceLocator',
            'memory_bank_label': 'BankLabel',
            'memory_serial_number': 'SerialNumber',
            'memory_part_number': 'PartNumber'
        },
        
        # BIOS Information
        'Win32_BIOS': {
            'bios_version': 'SMBIOSBIOSVersion',
            'bios_manufacturer': 'Manufacturer',
            'bios_name': 'Name',
            'bios_description': 'Description',
            'bios_serial_number': 'SerialNumber',
            'bios_release_date': 'ReleaseDate',
            'bios_version_major': 'SMBIOSMajorVersion',
            'bios_version_minor': 'SMBIOSMinorVersion'
        },
        
        # Motherboard Information
        'Win32_BaseBoard': {
            'motherboard_manufacturer': 'Manufacturer',
            'motherboard_model': 'Product',
            'motherboard_version': 'Version',
            'motherboard_serial': 'SerialNumber',
            'motherboard_tag': 'Tag'
        },
        
        # Storage Information
        'Win32_LogicalDisk': {
            'disk_size': 'Size',
            'disk_free_space': 'FreeSpace',
            'disk_file_system': 'FileSystem',
            'disk_volume_name': 'VolumeName',
            'disk_drive_letter': 'DeviceID',
            'disk_type': 'DriveType'
        },
        
        'Win32_DiskDrive': {
            'hard_drive_model': 'Model',
            'hard_drive_manufacturer': 'Manufacturer',
            'hard_drive_serial': 'SerialNumber',
            'hard_drive_size': 'Size',
            'hard_drive_interface': 'InterfaceType',
            'hard_drive_media_type': 'MediaType'
        },
        
        # Network Information
        'Win32_NetworkAdapter': {
            'network_adapter_name': 'Name',
            'network_adapter_manufacturer': 'Manufacturer',
            'network_adapter_type': 'AdapterType',
            'network_adapter_mac': 'MACAddress',
            'network_adapter_speed': 'Speed',
            'network_adapter_status': 'NetConnectionStatus'
        },
        
        'Win32_NetworkAdapterConfiguration': {
            'ip_address': 'IPAddress',
            'subnet_mask': 'IPSubnet',
            'default_gateway': 'DefaultIPGateway',
            'dns_servers': 'DNSServerSearchOrder',
            'dhcp_enabled': 'DHCPEnabled',
            'dhcp_server': 'DHCPServer',
            'wins_primary_server': 'WINSPrimaryServer',
            'wins_secondary_server': 'WINSSecondaryServer'
        },
        
        # Graphics Information
        'Win32_VideoController': {
            'graphics_card_name': 'Name',
            'graphics_card_manufacturer': 'AdapterCompatibility',
            'graphics_card_memory': 'AdapterRAM',
            'graphics_card_driver_version': 'DriverVersion',
            'graphics_card_driver_date': 'DriverDate',
            'graphics_card_resolution': 'CurrentHorizontalResolution'
        },
        
        # Audio Information
        'Win32_SoundDevice': {
            'audio_device_name': 'Name',
            'audio_device_manufacturer': 'Manufacturer',
            'audio_device_status': 'Status'
        },
        
        # USB Information
        'Win32_USBController': {
            'usb_controller_name': 'Name',
            'usb_controller_manufacturer': 'Manufacturer',
            'usb_controller_status': 'Status'
        },
        
        # Software Information
        'Win32_Product': {
            'installed_software': 'Name',
            'software_version': 'Version',
            'software_vendor': 'Vendor',
            'software_install_date': 'InstallDate'
        },
        
        # Services Information
        'Win32_Service': {
            'service_name': 'Name',
            'service_display_name': 'DisplayName',
            'service_status': 'Status',
            'service_start_mode': 'StartMode',
            'service_path': 'PathName',
            'service_description': 'Description'
        },
        
        # User Information
        'Win32_UserAccount': {
            'user_name': 'Name',
            'user_full_name': 'FullName',
            'user_description': 'Description',
            'user_account_type': 'AccountType',
            'user_disabled': 'Disabled',
            'user_lockout': 'Lockout',
            'user_password_changeable': 'PasswordChangeable',
            'user_password_expires': 'PasswordExpires',
            'user_password_required': 'PasswordRequired'
        },
        
        # Printer Information
        'Win32_Printer': {
            'printer_name': 'Name',
            'printer_driver_name': 'DriverName',
            'printer_port_name': 'PortName',
            'printer_status': 'Status',
            'printer_shared': 'Shared',
            'printer_share_name': 'ShareName'
        },
        
        # Update Information
        'Win32_QuickFixEngineering': {
            'hotfix_id': 'HotFixID',
            'hotfix_description': 'Description',
            'hotfix_installed_by': 'InstalledBy',
            'hotfix_install_date': 'InstalledOn'
        },
        
        # Environment Variables
        'Win32_Environment': {
            'environment_variable_name': 'Name',
            'environment_variable_value': 'VariableValue',
            'environment_variable_user': 'UserName'
        },
        
        # Startup Programs
        'Win32_StartupCommand': {
            'startup_command': 'Command',
            'startup_name': 'Name',
            'startup_location': 'Location',
            'startup_user': 'User'
        }
    }
    
    return wmi_mapping

def save_wmi_mapping_to_file(wmi_mapping):
    """Save WMI mapping to JSON file for use by collector"""
    
    with open('comprehensive_wmi_mapping.json', 'w') as f:
        json.dump(wmi_mapping, f, indent=2)
    
    print(f"\n💾 WMI mapping saved to: comprehensive_wmi_mapping.json")
    print(f"   Classes: {len(wmi_mapping)}")
    print(f"   Total field mappings: {sum(len(fields) for fields in wmi_mapping.values())}")

if __name__ == "__main__":
    print("🔍 Analyzing database schema and creating comprehensive WMI mapping...")
    
    # Analyze database schema
    wmi_categories, wmi_columns = analyze_database_schema()
    
    # Create comprehensive WMI mapping
    wmi_mapping = create_comprehensive_wmi_mapping()
    
    # Save mapping to file
    save_wmi_mapping_to_file(wmi_mapping)
    
    print("\n" + "=" * 80)
    print("✅ ANALYSIS COMPLETE!")
    print("=" * 80)
    print("📊 Database has comprehensive schema for WMI data collection")
    print("🗺️ Complete WMI class mapping created")
    print("💾 Mapping saved for use by enhanced collector")
    print("\nNext: Create enhanced WMI collector using this mapping!")