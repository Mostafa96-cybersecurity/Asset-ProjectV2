#!/usr/bin/env python3
"""
DATA COLLECTION ANALYSIS
Complete analysis of data collected via WMI, SSH, and SNMP
"""

import sqlite3

def analyze_collected_data():
    print("=" * 80)
    print("📊 COMPLETE DATA COLLECTION ANALYSIS")
    print("=" * 80)
    print()
    
    conn = sqlite3.connect('assets.db')
    cursor = conn.cursor()
    
    # Get database schema to see what data CAN be collected
    cursor.execute("PRAGMA table_info(assets)")
    columns = cursor.fetchall()
    
    print("🔍 DATABASE SCHEMA ANALYSIS (Available Data Fields):")
    print(f"   Total fields available: {len(columns)}")
    print()
    
    # Categorize data fields
    wmi_fields = []
    ssh_fields = []
    snmp_fields = []
    nmap_fields = []
    general_fields = []
    
    for col in columns:
        field_name = col[1].lower()
        
        if any(keyword in field_name for keyword in ['wmi_', 'windows_', 'processor_', 'memory_', 'disk_', 'installed_', 'running_', 'bios_', 'motherboard_', 'operating_system', 'computer_name', 'domain_', 'user_', 'service']):
            wmi_fields.append(col[1])
        elif any(keyword in field_name for keyword in ['ssh_', 'linux_', 'kernel_', 'distribution_', 'mount_', 'filesystem_', 'cron_', 'package']):
            ssh_fields.append(col[1])
        elif any(keyword in field_name for keyword in ['snmp_', 'interface_', 'routing_', 'arp_', 'vlan_', 'device_', 'controller_', 'switch_', 'router_']):
            snmp_fields.append(col[1])
        elif any(keyword in field_name for keyword in ['nmap_', 'open_ports', 'closed_ports', 'service_detection', 'os_fingerprint']):
            nmap_fields.append(col[1])
        else:
            general_fields.append(col[1])
    
    print(f"📡 WMI DATA FIELDS ({len(wmi_fields)} fields):")
    print("   HARDWARE INFORMATION:")
    hardware_fields = [f for f in wmi_fields if any(hw in f.lower() for hw in ['processor', 'cpu', 'memory', 'ram', 'disk', 'storage', 'motherboard', 'bios', 'graphics', 'sound', 'usb', 'monitor'])]
    for field in hardware_fields[:15]:  # Show first 15
        print(f"      • {field}")
    if len(hardware_fields) > 15:
        print(f"      ... and {len(hardware_fields) - 15} more hardware fields")
    
    print("\n   OPERATING SYSTEM INFORMATION:")
    os_fields = [f for f in wmi_fields if any(os in f.lower() for os in ['operating_system', 'windows', 'os_', 'system_', 'boot', 'uptime'])]
    for field in os_fields[:10]:
        print(f"      • {field}")
    
    print("\n   SOFTWARE & SERVICES:")
    software_fields = [f for f in wmi_fields if any(sw in f.lower() for sw in ['installed_', 'running_', 'service', 'software', 'hotfix', 'update'])]
    for field in software_fields[:10]:
        print(f"      • {field}")
    
    print("\n   NETWORK & SECURITY:")
    network_fields = [f for f in wmi_fields if any(net in f.lower() for net in ['network_', 'ip_', 'mac_', 'dns_', 'dhcp_', 'firewall', 'antivirus', 'user_', 'admin'])]
    for field in network_fields[:10]:
        print(f"      • {field}")
    
    print(f"\n🐧 SSH DATA FIELDS ({len(ssh_fields)} fields):")
    for field in ssh_fields[:15]:
        print(f"      • {field}")
    if len(ssh_fields) > 15:
        print(f"      ... and {len(ssh_fields) - 15} more SSH fields")
    
    print(f"\n📡 SNMP DATA FIELDS ({len(snmp_fields)} fields):")
    for field in snmp_fields[:15]:
        print(f"      • {field}")
    if len(snmp_fields) > 15:
        print(f"      ... and {len(snmp_fields) - 15} more SNMP fields")
    
    print(f"\n🗺️ NMAP DATA FIELDS ({len(nmap_fields)} fields):")
    for field in nmap_fields:
        print(f"      • {field}")
    
    # Check what data is actually populated
    print("\n📈 ACTUAL DATA POPULATION ANALYSIS:")
    
    # Sample a few key fields to see population rate
    key_fields = [
        'operating_system', 'processor_name', 'total_physical_memory', 
        'installed_software', 'running_services', 'network_adapters',
        'ssh_os_info', 'ssh_kernel_version', 'ssh_installed_packages',
        'snmp_sys_descr', 'snmp_sys_name', 'interface_count'
    ]
    
    cursor.execute('SELECT COUNT(*) FROM assets')
    total_devices = cursor.fetchone()[0]
    
    print(f"   Analysis based on {total_devices} total devices:")
    
    for field in key_fields:
        try:
            cursor.execute(f'SELECT COUNT(*) FROM assets WHERE {field} IS NOT NULL AND {field} != ""')
            populated = cursor.fetchone()[0]
            percentage = (populated / total_devices) * 100 if total_devices > 0 else 0
            status = "✅" if percentage > 50 else "⚠️" if percentage > 10 else "❌"
            print(f"   {status} {field}: {populated}/{total_devices} ({percentage:.1f}%)")
        except:
            print(f"   ❓ {field}: Field not found")
    
    conn.close()

def show_detailed_wmi_collection():
    print("\n" + "=" * 80)
    print("🪟 DETAILED WMI DATA COLLECTION CAPABILITIES")
    print("=" * 80)
    
    wmi_categories = {
        "SYSTEM INFORMATION": [
            "Computer Name & Domain",
            "Operating System (Name, Version, Build, Architecture)",
            "System Manufacturer & Model", 
            "Serial Number & Asset Tag",
            "System Type (Desktop/Laptop/Server)",
            "Last Boot Time & Uptime",
            "Windows Directory & System Directory",
            "Time Zone & Locale Settings"
        ],
        
        "HARDWARE SPECIFICATIONS": [
            "Processor (Name, Architecture, Cores, Threads, Speed)",
            "Motherboard (Manufacturer, Model, Serial, Version)",
            "BIOS (Version, Manufacturer, Serial, Release Date)",
            "Memory (Total RAM, Available, Speed, Type, Slots)",
            "Storage (Hard Drives, Types, Sizes, Free Space, Serial Numbers)",
            "Graphics Cards (Name, Memory, Driver Version)",
            "Network Adapters (Types, MAC Addresses, Speed)",
            "Sound Devices & Audio Hardware"
        ],
        
        "SOFTWARE INVENTORY": [
            "Installed Software & Applications",
            "Windows Updates & Hotfixes",
            "Running Services & Status",
            "Startup Programs",
            "Installed Printers",
            "Device Drivers",
            "Registry Information",
            "Environment Variables"
        ],
        
        "NETWORK CONFIGURATION": [
            "IP Addresses & Subnet Masks",
            "Default Gateway & DNS Servers", 
            "DHCP Configuration",
            "Network Adapter Details",
            "Shared Folders & Network Shares",
            "Network Speed & Utilization",
            "WiFi Configuration",
            "Network Protocols"
        ],
        
        "SECURITY & USERS": [
            "User Accounts & Profiles",
            "Local Administrators",
            "Password Policy",
            "User Privileges & Rights",
            "Antivirus Software & Status",
            "Firewall Configuration",
            "Security Patches",
            "Audit Logs & Events"
        ],
        
        "PERFORMANCE METRICS": [
            "CPU Utilization",
            "Memory Usage",
            "Disk Usage & Performance",
            "Network Utilization",
            "Performance Counters",
            "System Load",
            "Process List",
            "Resource Monitoring"
        ]
    }
    
    for category, items in wmi_categories.items():
        print(f"\n📊 {category}:")
        for item in items:
            print(f"   • {item}")

def show_detailed_ssh_collection():
    print("\n" + "=" * 80)
    print("🐧 DETAILED SSH DATA COLLECTION CAPABILITIES")
    print("=" * 80)
    
    ssh_categories = {
        "SYSTEM INFORMATION": [
            "Hostname & FQDN",
            "Operating System & Distribution",
            "Kernel Version & Architecture",
            "System Uptime & Load Average",
            "Hardware Information (CPU, Memory)",
            "Virtualization Detection",
            "Container Information",
            "System Timezone & Locale"
        ],
        
        "HARDWARE DETAILS": [
            "CPU Information (Model, Cores, Speed)",
            "Memory (Total, Used, Free, Swap)",
            "Disk Information & Mount Points",
            "Filesystem Usage & Types",
            "Network Interfaces & Configuration",
            "PCI Devices & Hardware",
            "USB Devices",
            "Hardware Sensors"
        ],
        
        "SOFTWARE & PACKAGES": [
            "Installed Packages (RPM/DEB/etc)",
            "Running Processes",
            "System Services & Status",
            "Cron Jobs & Scheduled Tasks",
            "Installed Software Versions",
            "Package Repositories",
            "System Libraries",
            "Development Tools"
        ],
        
        "NETWORK CONFIGURATION": [
            "Network Interface Configuration",
            "Routing Table",
            "ARP Table",
            "Listening Ports & Services",
            "Firewall Rules (iptables/firewalld)",
            "DNS Configuration",
            "Network Statistics",
            "Wireless Configuration"
        ],
        
        "SECURITY & USERS": [
            "User Accounts & Groups",
            "SSH Configuration",
            "Sudo Configuration",
            "Password Policies",
            "SELinux/AppArmor Status",
            "Security Updates",
            "Log Files Analysis",
            "Authentication Logs"
        ],
        
        "SYSTEM CONFIGURATION": [
            "Configuration Files",
            "Environment Variables",
            "System Logs",
            "Boot Configuration",
            "Kernel Modules",
            "System Limits",
            "Scheduled Tasks",
            "System Monitoring"
        ]
    }
    
    for category, items in ssh_categories.items():
        print(f"\n📊 {category}:")
        for item in items:
            print(f"   • {item}")

def show_detailed_snmp_collection():
    print("\n" + "=" * 80)
    print("📡 DETAILED SNMP DATA COLLECTION CAPABILITIES")
    print("=" * 80)
    
    snmp_categories = {
        "DEVICE IDENTIFICATION": [
            "System Description (sysDescr)",
            "System Name (sysName)",
            "System Location (sysLocation)",
            "System Contact (sysContact)",
            "System Object ID (sysObjectID)",
            "System Uptime (sysUpTime)",
            "System Services (sysServices)",
            "Device Vendor & Model"
        ],
        
        "NETWORK INTERFACES": [
            "Interface Count & Names",
            "Interface Types & Status",
            "Interface Speeds & MTU",
            "MAC Addresses",
            "IP Addresses & Subnets",
            "Interface Statistics (In/Out bytes/packets)",
            "Interface Errors & Discards",
            "Interface Utilization"
        ],
        
        "ROUTING & SWITCHING": [
            "Routing Table",
            "ARP Table",
            "Bridge/Switch Information",
            "VLAN Configuration",
            "Spanning Tree Protocol",
            "Port Security",
            "SNMP Communities",
            "Access Control Lists"
        ],
        
        "DEVICE PERFORMANCE": [
            "CPU Utilization",
            "Memory Usage",
            "Temperature Sensors",
            "Fan Status",
            "Power Supply Status",
            "Environmental Monitoring",
            "Device Health",
            "Error Rates"
        ],
        
        "NETWORK PROTOCOLS": [
            "SNMP Version Support",
            "Protocol Statistics",
            "Service Status",
            "Quality of Service (QoS)",
            "Bandwidth Utilization",
            "Traffic Patterns",
            "Network Topology",
            "Protocol Compliance"
        ]
    }
    
    for category, items in snmp_categories.items():
        print(f"\n📊 {category}:")
        for item in items:
            print(f"   • {item}")

if __name__ == "__main__":
    analyze_collected_data()
    show_detailed_wmi_collection()
    show_detailed_ssh_collection()
    show_detailed_snmp_collection()