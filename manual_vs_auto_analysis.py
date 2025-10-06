#!/usr/bin/env python3
"""
Manual vs Automatic Field Analysis
Shows exactly which fields need manual admin input vs automatic collection
"""

import sqlite3

def analyze_manual_vs_automatic_fields():
    """Detailed analysis of manual vs automatic data collection capabilities"""
    
    print("🔍 MANUAL vs AUTOMATIC DATA COLLECTION ANALYSIS")
    print("=" * 80)
    
    # Fields that WMI/SSH/SNMP CANNOT collect (require manual admin input)
    definitely_manual_fields = {
        # Asset Management
        'asset_tag', 'asset_tag_hw', 'asset_number', 'inventory_number',
        'purchase_date', 'warranty_expiry', 'warranty_expiration', 'lease_expiry',
        'purchase_cost', 'purchase_price', 'depreciated_value', 'purchase_order',
        'invoice_number', 'support_contract', 'maintenance_contract',
        'maintenance_schedule', 'maintenance_window',
        
        # Organizational/Business
        'department', 'cost_center', 'budget_code', 'business_function',
        'business_owner', 'technical_owner', 'assigned_user', 'project_code',
        'criticality', 'business_criticality', 'criticality_level',
        'support_level', 'compliance_requirements', 'compliance_status',
        'change_approval', 'data_classification', 'security_classification',
        
        # Physical Location
        'location', 'building', 'floor', 'room', 'desk_number', 'site',
        'rack', 'rack_position', 'barcode',
        
        # Administrative
        'notes', 'admin_notes', 'comments', 'tags',
        'custom_field_1', 'custom_field_2', 'custom_field_3', 'custom_field_4', 'custom_field_5',
        'vendor', 'vendor_contact', 'model_vendor', 'device_vendor', 'supplier',
        
        # Security & Compliance
        'encryption_status', 'backup_requirements', 'backup_schedule', 'backup_location',
        'security_classification', 'compliance_frameworks', 'policy_violations',
        'access_control', 'audit_logs',
        
        # Monitoring & Management
        'monitoring_enabled', 'alert_enabled', 'scan_frequency',
        'performance_baseline', 'threshold_breaches'
    }
    
    # Fields that can be auto-collected by WMI (Windows)
    wmi_auto_collectible = {
        # System Info
        'hostname', 'computer_name', 'working_user', 'domain', 'workgroup',
        'operating_system', 'os_version', 'os_build_number', 'os_service_pack',
        'windows_edition', 'windows_product_key', 'windows_activation_status',
        'os_install_date', 'windows_directory', 'system_directory',
        'boot_time', 'last_boot_time', 'system_uptime', 'time_zone',
        
        # Hardware
        'system_manufacturer', 'system_model', 'system_type', 'system_family',
        'system_serial_number', 'chassis_type', 'chassis_manufacturer', 'chassis_serial',
        'motherboard', 'motherboard_serial', 'motherboard_version',
        'bios_version', 'bios_date', 'firmware_version',
        
        # CPU
        'processor_name', 'processor', 'cpu_model', 'processor_architecture',
        'processor_cores', 'processor_logical_processors', 'processor_speed',
        'processor_l2_cache', 'processor_l3_cache', 'cpu_sockets', 'cpu_cores',
        'cpu_threads', 'cpu_utilization',
        
        # Memory
        'total_physical_memory', 'total_memory', 'memory_gb', 'installed_ram_gb',
        'available_physical_memory', 'memory_utilization', 'page_file_size',
        'virtual_memory_max_size', 'memory_speed', 'memory_type',
        'memory_slots_total', 'memory_slots_used', 'memory_modules',
        
        # Storage
        'hard_drives', 'storage', 'storage_info', 'total_storage_gb',
        'disk_drives', 'disk_drive_count', 'drive_sizes', 'drive_free_space',
        'drive_models', 'drive_filesystems', 'disk_model', 'disk_type',
        
        # Network
        'mac_addresses', 'mac_address', 'network_adapters', 'network_adapter',
        'network_adapter_count', 'network_adapter_types', 'network_speed',
        'default_gateway', 'gateway', 'subnet_mask', 'primary_ip', 'secondary_ips',
        
        # Software
        'installed_software', 'recent_software', 'installed_printers', 'printers',
        'antivirus_product', 'antivirus_status', 'security_software',
        'windows_updates', 'security_patches',
        
        # Users & Security
        'user_accounts', 'logged_on_users', 'logged_in_users', 'last_logged_user',
        'user_profiles', 'local_admin_users', 'user_privileges',
        
        # Services & Processes
        'services_running', 'services_stopped', 'services',
        
        # Hardware Details
        'graphics_card', 'graphics_memory', 'graphics_driver', 'active_gpu',
        'sound_devices', 'audio_devices', 'usb_devices', 'optical_drives',
        'monitors', 'connected_screens', 'display_resolution'
    }
    
    # Fields that can be auto-collected by SNMP (Network devices)
    snmp_auto_collectible = {
        'hostname', 'ip_address', 'mac_addresses', 'system_uptime',
        'snmp_sys_descr', 'snmp_sys_name', 'snmp_sys_contact', 'snmp_sys_location',
        'device_model', 'device_serial', 'hardware_version', 'firmware_version',
        'interface_count', 'interfaces_info', 'interface_names', 'interface_types',
        'interface_speeds', 'interface_status', 'network_speed',
        'device_temperature', 'power_consumption', 'fan_status', 'power_supply_status',
        'environmental_sensors', 'cpu_utilization', 'memory_utilization'
    }
    
    # Fields that can be auto-collected by SSH (Linux/Unix)
    ssh_auto_collectible = {
        'hostname', 'operating_system', 'os_version', 'kernel_version',
        'processor_name', 'cpu_info', 'processor_cores', 'processor_architecture',
        'total_physical_memory', 'available_memory', 'memory_utilization',
        'system_uptime', 'last_boot_time', 'disk_usage_percent',
        'ssh_distribution', 'ssh_distribution_version', 'ssh_uptime',
        'ssh_load_average', 'ssh_cpu_count', 'ssh_memory_total', 'ssh_memory_used',
        'ssh_disk_info', 'ssh_filesystem_usage', 'ssh_network_config',
        'ssh_users', 'ssh_groups', 'ssh_installed_packages', 'ssh_running_processes',
        'open_ports', 'listening_ports', 'ssh_listening_ports'
    }
    
    # Get actual database columns
    conn = sqlite3.connect('assets.db')
    cursor = conn.cursor()
    cursor.execute('PRAGMA table_info(assets)')
    columns = cursor.fetchall()
    
    all_columns = [col[1] for col in columns]
    
    # Categorize all columns
    manual_only = []
    auto_collectible = []
    mixed_or_unknown = []
    
    for column in all_columns:
        col_lower = column.lower()
        
        # Check if definitely manual
        is_manual = any(manual_field in col_lower or col_lower == manual_field 
                       for manual_field in definitely_manual_fields)
        
        # Check if auto-collectible
        is_wmi = any(wmi_field in col_lower or col_lower == wmi_field 
                    for wmi_field in wmi_auto_collectible)
        is_snmp = any(snmp_field in col_lower or col_lower == snmp_field 
                     for snmp_field in snmp_auto_collectible)
        is_ssh = any(ssh_field in col_lower or col_lower == ssh_field 
                    for ssh_field in ssh_auto_collectible)
        
        if is_manual:
            manual_only.append(column)
        elif is_wmi or is_snmp or is_ssh:
            methods = []
            if is_wmi:
                methods.append('WMI')
            if is_snmp:
                methods.append('SNMP')
            if is_ssh:
                methods.append('SSH')
            auto_collectible.append((column, methods))
        else:
            mixed_or_unknown.append(column)
    
    print("🔍 FIELD ANALYSIS RESULTS:")
    print(f"Total Database Columns: {len(all_columns)}")
    print(f"Manual Entry Required: {len(manual_only)} ({len(manual_only)/len(all_columns)*100:.1f}%)")
    print(f"Auto-Collectible: {len(auto_collectible)} ({len(auto_collectible)/len(all_columns)*100:.1f}%)")
    print(f"Mixed/Unknown: {len(mixed_or_unknown)} ({len(mixed_or_unknown)/len(all_columns)*100:.1f}%)")
    print()
    
    print("❌ FIELDS REQUIRING MANUAL ADMIN INPUT:")
    print("-" * 60)
    manual_categories = {
        'Asset Management': ['asset_tag', 'purchase_date', 'warranty', 'cost', 'invoice', 'contract'],
        'Organization': ['department', 'assigned_user', 'business', 'project', 'criticality'],
        'Location': ['location', 'building', 'floor', 'room', 'rack', 'site'],
        'Administrative': ['notes', 'custom_field', 'vendor', 'tags'],
        'Security/Compliance': ['encryption', 'compliance', 'classification', 'backup']
    }
    
    for category, keywords in manual_categories.items():
        print(f"\n📂 {category}:")
        category_fields = [field for field in manual_only 
                          if any(keyword in field.lower() for keyword in keywords)]
        for field in sorted(category_fields)[:10]:  # Show max 10 per category
            print(f"   • {field}")
        if len(category_fields) > 10:
            print(f"   ... and {len(category_fields) - 10} more")
    
    print("\n✅ FIELDS AUTO-COLLECTIBLE BY WMI/SSH/SNMP:")
    print("-" * 60)
    
    # Group by collection method
    wmi_fields = [field for field, methods in auto_collectible if 'WMI' in methods]
    snmp_fields = [field for field, methods in auto_collectible if 'SNMP' in methods]
    ssh_fields = [field for field, methods in auto_collectible if 'SSH' in methods]
    
    print(f"\n🪟 WMI Collectible ({len(wmi_fields)} fields):")
    for field in sorted(wmi_fields)[:15]:
        print(f"   • {field}")
    if len(wmi_fields) > 15:
        print(f"   ... and {len(wmi_fields) - 15} more")
    
    print(f"\n🌐 SNMP Collectible ({len(snmp_fields)} fields):")
    for field in sorted(snmp_fields)[:10]:
        print(f"   • {field}")
    if len(snmp_fields) > 10:
        print(f"   ... and {len(snmp_fields) - 10} more")
    
    print(f"\n🐧 SSH Collectible ({len(ssh_fields)} fields):")
    for field in sorted(ssh_fields)[:10]:
        print(f"   • {field}")
    if len(ssh_fields) > 10:
        print(f"   ... and {len(ssh_fields) - 10} more")
    
    # Check actual data population for manual fields
    print("\n📊 MANUAL FIELD POPULATION STATUS:")
    print("-" * 60)
    cursor.execute("SELECT COUNT(*) FROM assets")
    total_devices = cursor.fetchone()[0]
    
    for field in sorted(manual_only)[:15]:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM assets WHERE {field} IS NOT NULL AND {field} != ''")
            populated = cursor.fetchone()[0]
            percentage = (populated / total_devices * 100) if total_devices > 0 else 0
            status = "✅" if percentage > 0 else "❌"
            print(f"   {status} {field:<25} | {populated:>3}/{total_devices} ({percentage:>5.1f}%)")
        except:
            print(f"   ❓ {field:<25} | Query failed")
    
    if len(manual_only) > 15:
        print(f"   ... and {len(manual_only) - 15} more manual fields")
    
    conn.close()
    
    print("\n💡 SUMMARY:")
    print("=" * 60)
    print("✅ Auto-collectible data: System specs, hardware info, network config")
    print("❌ Manual entry required: Asset tags, departments, locations, business data")
    print("🔧 Recommendation: Use hierarchical collection for technical data,")
    print("   admin GUI forms for business/organizational data")

if __name__ == "__main__":
    analyze_manual_vs_automatic_fields()