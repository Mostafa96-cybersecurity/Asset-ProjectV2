#!/usr/bin/env python3
"""
Data Collection Analysis Report
Shows exactly what data your Network Assets Collector gathers from all device types
"""

import sqlite3

def analyze_collected_data():
    print("🎯 COMPLETE DATA COLLECTION ANALYSIS")
    print("="*80)
    
    # Connect to database
    conn = sqlite3.connect('assets.db')
    cursor = conn.cursor()
    
    # Get all columns from the assets table
    cursor.execute("PRAGMA table_info(assets)")
    all_columns = [col[1] for col in cursor.fetchall()]
    
    print("📊 DATABASE SCHEMA - All Available Fields:")
    print("-"*50)
    for i, col in enumerate(all_columns, 1):
        print(f"{i:2}. {col}")
    
    # Analyze data collection by source
    print("\n🔍 DATA COLLECTION BY SOURCE:")
    print("-"*50)
    
    cursor.execute("""
        SELECT data_source, 
               COUNT(*) as total_devices,
               COUNT(CASE WHEN firmware_os_version IS NOT NULL AND firmware_os_version != '' THEN 1 END) as has_os,
               COUNT(CASE WHEN model_vendor IS NOT NULL AND model_vendor != '' THEN 1 END) as has_model,
               COUNT(CASE WHEN sn IS NOT NULL AND sn != '' THEN 1 END) as has_serial
        FROM assets 
        GROUP BY data_source 
        ORDER BY total_devices DESC
    """)
    
    sources = cursor.fetchall()
    for source, total, os_count, model_count, serial_count in sources:
        print(f"\n🔧 {source}:")
        print(f"   📱 Total Devices: {total}")
        print(f"   🖥️  OS Information: {os_count} ({os_count/total*100:.1f}%)")
        print(f"   📋 Model Information: {model_count} ({model_count/total*100:.1f}%)")
        print(f"   🏷️  Serial Numbers: {serial_count} ({serial_count/total*100:.1f}%)")
    
    # Show sample data for each collection method
    print("\n📋 SAMPLE DATA BY COLLECTION METHOD:")
    print("="*80)
    
    for source, _, _, _, _ in sources:
        print(f"\n🔍 Sample from {source}:")
        print("-"*40)
        
        cursor.execute("""
            SELECT hostname, ip_address, device_type, firmware_os_version, model_vendor, sn
            FROM assets 
            WHERE data_source = ? 
            LIMIT 3
        """, (source,))
        
        samples = cursor.fetchall()
        for sample in samples:
            hostname, ip, dev_type, os_ver, model, serial = sample
            print(f"   • Host: {hostname or 'N/A':<15} | IP: {ip or 'N/A':<15}")
            print(f"     Type: {dev_type or 'N/A':<12} | OS: {os_ver or 'N/A'}")
            print(f"     Model: {model or 'N/A':<12} | SN: {serial or 'N/A'}")
            print()
    
    conn.close()

def show_collection_capabilities():
    print("\n🚀 COLLECTION CAPABILITIES BY DEVICE TYPE:")
    print("="*80)
    
    capabilities = {
        "WMI Collection (Windows)": {
            "description": "Comprehensive Windows device information via WMI",
            "data_collected": [
                "✅ Hostname & Domain information",
                "✅ Working User (currently logged in)",
                "✅ Operating System name & version",
                "✅ Hardware manufacturer & model",
                "✅ Serial number & asset tag",
                "✅ CPU information (model, cores, speed)",
                "✅ Installed RAM (total GB)",
                "✅ Storage devices (HDDs, SSDs with sizes)",
                "✅ Network interfaces & IP addresses",
                "✅ Active GPU information",
                "✅ Connected monitors/screens",
                "✅ System SKU & BIOS info",
                "✅ Installed software inventory",
                "✅ Windows services status",
                "✅ System uptime & performance metrics"
            ],
            "device_types": ["Windows Desktops", "Windows Servers", "Windows Laptops"],
            "authentication": "Required (Username/Password or Domain credentials)"
        },
        
        "SSH Collection (Linux/Unix)": {
            "description": "Comprehensive Linux/Unix system information via SSH",
            "data_collected": [
                "✅ Hostname & domain information",
                "✅ Current logged users",
                "✅ Operating System (distribution & version)",
                "✅ Hardware information (dmidecode)",
                "✅ CPU information (/proc/cpuinfo)",
                "✅ Memory information (/proc/meminfo)",
                "✅ Disk usage & filesystem information",
                "✅ Network interfaces & IP configuration",
                "✅ Running processes & services",
                "✅ System uptime & load averages",
                "✅ Installed packages (rpm/deb)",
                "✅ Kernel version & modules",
                "✅ VMware ESXi specific information"
            ],
            "device_types": ["Linux Servers", "Unix Workstations", "VMware ESXi", "Network Appliances"],
            "authentication": "Required (SSH Username/Password or Key)"
        },
        
        "SNMP Collection (Network Devices)": {
            "description": "Network device information via SNMP protocol",
            "data_collected": [
                "✅ System description & name",
                "✅ Device manufacturer & model",
                "✅ Firmware/OS version",
                "✅ Serial numbers (if supported)",
                "✅ Network interface information",
                "✅ IP routing table",
                "✅ System uptime",
                "✅ Memory utilization",
                "✅ CPU utilization (if available)",
                "✅ Storage information",
                "✅ Port status & configuration",
                "✅ VLAN information",
                "✅ Device location (if configured)"
            ],
            "device_types": ["Routers", "Switches", "Firewalls", "Access Points", "Printers", "UPS Systems"],
            "authentication": "Community String (often 'public' for read-only)"
        },
        
        "Smart Display Collection (Credential-less)": {
            "description": "Smart TVs, displays, and IoT devices without authentication",
            "data_collected": [
                "✅ Device IP address & hostname",
                "✅ Open network ports",
                "✅ HTTP server information",
                "✅ UPnP device discovery data",
                "✅ Web interface detection",
                "✅ Brand identification (LG, Samsung, etc.)",
                "✅ Smart TV platform (WebOS, Tizen)",
                "✅ Service discovery (SSDP, mDNS)",
                "✅ MAC address (if available)",
                "✅ Device capabilities",
                "✅ Network services",
                "✅ Basic device fingerprinting"
            ],
            "device_types": ["Smart TVs", "Digital Displays", "IoT Devices", "Smart Appliances", "Media Players"],
            "authentication": "None required (uses public protocols)"
        },
        
        "Network Scanning (Basic Discovery)": {
            "description": "Basic network device discovery and port scanning",
            "data_collected": [
                "✅ Device IP addresses",
                "✅ Hostname resolution (if available)",
                "✅ Open network ports",
                "✅ Service identification",
                "✅ Response time & availability",
                "✅ Operating system fingerprinting",
                "✅ MAC address (local network)",
                "✅ Network topology mapping",
                "✅ Device classification hints"
            ],
            "device_types": ["Any network-connected device"],
            "authentication": "None (uses network protocols)"
        }
    }
    
    for method, info in capabilities.items():
        print(f"\n🔧 {method}")
        print(f"📝 {info['description']}")
        print(f"🔐 Authentication: {info['authentication']}")
        print(f"📱 Device Types: {', '.join(info['device_types'])}")
        print("\n📊 Data Collected:")
        for data_point in info['data_collected']:
            print(f"   {data_point}")
        print("-" * 60)

def show_database_fields_mapping():
    print("\n📋 DATABASE FIELD MAPPING:")
    print("="*80)
    
    field_mapping = {
        "Core Identity Fields": [
            "id - Unique database identifier",
            "asset_tag - Asset management tag/barcode",
            "hostname - Device network name", 
            "ip_address - Primary IP address",
            "device_type - Classification (server, workstation, etc.)"
        ],
        
        "Hardware Information": [
            "model_vendor - Manufacturer and model",
            "sn - Serial number",
            "firmware_os_version - Operating system/firmware version"
        ],
        
        "Location & Management": [
            "location - Physical location",
            "site - Site/campus identifier", 
            "building - Building identifier",
            "floor - Floor number",
            "room - Room identifier",
            "owner - Device owner/responsible person",
            "department - Owning department"
        ],
        
        "Operational Status": [
            "status - Active/Inactive/Maintenance",
            "notes - Additional information",
            "data_source - Collection method used"
        ],
        
        "Audit Trail": [
            "created_at - Record creation timestamp",
            "created_by - Who created the record",
            "updated_at - Last update timestamp", 
            "updated_by - Who last updated"
        ],
        
        "System Management": [
            "_excel_path - Excel file synchronization",
            "_sheet_name - Excel sheet reference",
            "_sync_pending - Sync status flag",
            "_device_fingerprint - Unique device identifier",
            "_collection_quality - Data quality score",
            "_validation_status - Data validation status",
            "_error_count - Collection error tracking"
        ]
    }
    
    for category, fields in field_mapping.items():
        print(f"\n📂 {category}:")
        for field in fields:
            print(f"   • {field}")

def main():
    analyze_collected_data()
    show_collection_capabilities()
    show_database_fields_mapping()
    
    print("\n🎯 SUMMARY:")
    print("="*50)
    print("Your Network Assets Collector can gather:")
    print("• 📊 Complete hardware inventory")
    print("• 🖥️  Operating system information") 
    print("• 🌐 Network configuration details")
    print("• 🔧 Software and service information")
    print("• 📱 Smart device capabilities")
    print("• 🏢 Asset management data")
    print("• 📈 Performance and utilization metrics")
    print("\nFrom ANY network device - with or without credentials!")

if __name__ == "__main__":
    main()