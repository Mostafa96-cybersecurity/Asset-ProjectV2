#!/usr/bin/env python3
"""
Database Schema Mapper - Maps collected WMI data to actual database columns
"""

import sqlite3
import json

def get_actual_database_schema():
    """Get the actual database schema"""
    conn = sqlite3.connect('assets.db')
    cursor = conn.cursor()
    
    # Get all columns with their types
    cursor.execute("PRAGMA table_info(assets)")
    columns = cursor.fetchall()
    
    schema = {}
    for col in columns:
        col_id, col_name, col_type, not_null, default_val, pk = col
        schema[col_name] = {
            'type': col_type,
            'not_null': not_null,
            'default': default_val,
            'primary_key': pk
        }
    
    conn.close()
    return schema

def create_wmi_to_db_mapping():
    """Create mapping from WMI data to actual database columns"""
    
    schema = get_actual_database_schema()
    
    print("=" * 80)
    print("🗺️ CREATING WMI TO DATABASE MAPPING")
    print("=" * 80)
    print(f"📊 Total database columns: {len(schema)}")
    
    # Print some key columns to understand the schema
    print("\n🔍 Key Database Columns:")
    key_columns = [col for col in schema.keys() if any(keyword in col.lower() for keyword in [
        'hostname', 'ip_address', 'computer_name', 'operating_system', 'processor', 
        'memory', 'user', 'current', 'timestamp', 'date'
    ])]
    
    for col in sorted(key_columns)[:20]:
        print(f"   • {col}")
    
    # Create comprehensive mapping
    wmi_to_db_mapping = {
        # Basic identification
        'hostname': 'hostname',
        'ip_address': 'ip_address',
        'mac_address': 'mac_address',
        
        # System Information
        'computer_name': 'computer_name',
        'manufacturer': 'manufacturer',
        'model': 'model',
        'serial_number': 'serial_number',
        'asset_tag': 'asset_tag',
        'system_type': 'system_type',
        'domain_name': 'domain_name',
        'workgroup': 'workgroup',
        
        # Operating System
        'operating_system': 'operating_system',
        'os_version': 'os_version',
        'os_build_number': 'os_build_number',
        'os_architecture': 'os_architecture',
        'os_service_pack': 'os_service_pack',
        'windows_directory': 'windows_directory',
        'install_date': 'install_date',
        'last_boot_up_time': 'last_boot_up_time',
        
        # Processor
        'processor_name': 'processor_name',
        'processor_manufacturer': 'processor_manufacturer',
        'processor_cores': 'processor_cores',
        'processor_logical_processors': 'processor_logical_processors',
        'processor_speed': 'processor_speed',
        'processor_architecture': 'processor_architecture',
        
        # Memory
        'total_physical_memory': 'total_physical_memory',
        'installed_ram_gb': 'installed_ram_gb',
        'memory_gb': 'memory_gb',
        'memory_utilization': 'memory_utilization',
        'memory_type': 'memory_type',
        'memory_slots_used': 'memory_slots_used',
        'memory_slots_total': 'memory_slots_total',
        
        # BIOS
        'bios_version': 'bios_version',
        'bios_manufacturer': 'bios_manufacturer',
        'bios_serial_number': 'bios_serial_number',
        'bios_release_date': 'bios_release_date',
        
        # Motherboard
        'motherboard_manufacturer': 'motherboard_manufacturer',
        'motherboard_model': 'motherboard_model',
        'motherboard_serial': 'motherboard_serial',
        'motherboard_version': 'motherboard_version',
        
        # Storage
        'hard_drives': 'hard_drives',
        'drive_types': 'drive_types',
        'drive_sizes': 'drive_sizes',
        'drive_free_space': 'drive_free_space',
        'total_disk_space': 'total_disk_space',
        'free_disk_space': 'free_disk_space',
        
        # Network
        'network_adapters': 'network_adapters',
        'ip_addresses': 'ip_addresses',
        'mac_addresses': 'mac_addresses',
        'default_gateway': 'default_gateway',
        'dns_servers': 'dns_servers',
        'dhcp_enabled': 'dhcp_enabled',
        
        # Software
        'installed_software': 'installed_software',
        'installed_software_count': 'installed_software_count',
        
        # Services
        'services': 'services',
        'running_services': 'running_services',
        'services_running': 'services_running',
        'services_stopped': 'services_stopped',
        
        # Users
        'user_accounts': 'user_accounts',
        'user_capacity': 'user_capacity',
        'user_privileges': 'user_privileges',
        'user_profiles': 'user_profiles',
        
        # Graphics
        'graphics_card': 'graphics_card',
        'graphics_cards': 'graphics_cards',
        'graphics_memory': 'graphics_memory',
        'graphics_driver': 'graphics_driver',
        'display_resolution': 'display_resolution',
        
        # Audio
        'sound_devices': 'sound_devices',
        'audio_devices': 'audio_devices',
        
        # USB
        'usb_devices': 'usb_devices',
        'usb_controllers': 'usb_controllers',
        
        # Environment
        'environment_variables': 'environment_variables',
        
        # Collection metadata
        'data_collection_time': 'data_collection_time',
        'data_collection_method': 'data_collection_method',
        'data_fields_collected': 'data_fields_collected'
    }
    
    # Filter mapping to only include columns that exist in the database
    filtered_mapping = {}
    missing_columns = []
    
    for wmi_field, db_column in wmi_to_db_mapping.items():
        if db_column in schema:
            filtered_mapping[wmi_field] = db_column
        else:
            missing_columns.append(db_column)
    
    print(f"\n✅ Mapped fields: {len(filtered_mapping)}")
    print(f"⚠️ Missing columns: {len(missing_columns)}")
    
    if missing_columns:
        print("\n❌ Missing database columns:")
        for col in missing_columns[:10]:
            print(f"   • {col}")
        if len(missing_columns) > 10:
            print(f"   ... and {len(missing_columns) - 10} more")
    
    # Save mapping to file
    with open('wmi_to_database_mapping.json', 'w') as f:
        json.dump(filtered_mapping, f, indent=2)
    
    print(f"\n💾 Mapping saved to: wmi_to_database_mapping.json")
    
    return filtered_mapping, schema

def show_current_user_columns():
    """Show columns related to current user"""
    schema = get_actual_database_schema()
    
    user_columns = [col for col in schema.keys() if any(keyword in col.lower() for keyword in [
        'user', 'current', 'account', 'profile', 'admin', 'privilege'
    ])]
    
    print("\n👤 USER-RELATED DATABASE COLUMNS:")
    for col in sorted(user_columns):
        print(f"   • {col}")
    
    return user_columns

if __name__ == "__main__":
    mapping, schema = create_wmi_to_db_mapping()
    user_columns = show_current_user_columns()
    
    print("\n" + "=" * 80)
    print("✅ DATABASE MAPPING ANALYSIS COMPLETE!")
    print("=" * 80)
    print("🗺️ WMI to Database mapping created")
    print("👤 User-related columns identified")
    print("💾 Ready for enhanced data collection")