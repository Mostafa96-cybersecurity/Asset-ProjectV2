#!/usr/bin/env python3
"""
📋 COMPREHENSIVE DATA VIEWER - WORKING VERSION
==============================================
View all collected data to verify completeness
"""

import sqlite3
from datetime import datetime, timedelta

def view_all_collected_data():
    print("=" * 100)
    print("📋 COMPREHENSIVE COLLECTED DATA VIEWER")
    print("=" * 100)
    print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    conn = sqlite3.connect('assets.db')
    cursor = conn.cursor()
    
    # Get recent collections (last 15 minutes to be safe)
    fifteen_min_ago = (datetime.now() - timedelta(minutes=15)).isoformat()
    
    print("🔍 RECENTLY COLLECTED DEVICES (Last 15 minutes)")
    print("=" * 100)
    
    # Get all key data fields for recent collections using actual column names
    cursor.execute('''
        SELECT 
            id, hostname, ip_address, collection_method, status,
            operating_system, system_manufacturer, system_model,
            processor_name, total_physical_memory, bios_serial_number,
            working_user, mac_addresses, domain_name,
            last_boot_time, os_install_date, windows_edition,
            network_adapters, total_disk_space, free_disk_space,
            created_at, device_type
        FROM assets 
        WHERE created_at > ? OR updated_at > ?
        ORDER BY created_at DESC
    ''', (fifteen_min_ago, fifteen_min_ago))
    
    recent_devices = cursor.fetchall()
    
    print(f"📊 Found {len(recent_devices)} recently collected devices")
    print()
    
    for i, device in enumerate(recent_devices, 1):
        (id, hostname, ip, method, status, os, manufacturer, model, 
         cpu, memory, bios, user, mac, domain, boot_time, install_date, 
         win_edition, network_adapter, disk_total, disk_free, created_at, device_type) = device
        
        print(f"🖥️  DEVICE #{i} (ID: {id})")
        print("-" * 80)
        print("📍 Basic Info:")
        print(f"   • Hostname: {hostname}")
        print(f"   • IP Address: {ip}")
        print(f"   • Device Type: {device_type or 'Unknown'}")
        print(f"   • Collection Method: {method}")
        print(f"   • Status: {status}")
        print(f"   • Collected At: {created_at}")
        print()
        
        print("💻 System Information:")
        print(f"   • Operating System: {os or 'Not Available'}")
        print(f"   • Windows Edition: {win_edition or 'Not Available'}")
        print(f"   • Manufacturer: {manufacturer or 'Not Available'}")
        print(f"   • Model: {model or 'Not Available'}")
        print(f"   • BIOS Serial: {bios or 'Not Available'}")
        print()
        
        print("⚡ Hardware Details:")
        print(f"   • Processor: {cpu or 'Not Available'}")
        print(f"   • Total Memory: {memory or 'Not Available'}")
        print(f"   • Total Disk Space: {disk_total or 'Not Available'}")
        print(f"   • Free Disk Space: {disk_free or 'Not Available'}")
        print()
        
        print("🌐 Network Information:")
        print(f"   • MAC Addresses: {mac or 'Not Available'}")
        print(f"   • Network Adapters: {network_adapter or 'Not Available'}")
        print(f"   • Domain: {domain or 'Not Available'}")
        print()
        
        print("👤 User Information:")
        print(f"   • Current User: {user or 'Not Available'}")
        print()
        
        print("📅 System Timing:")
        print(f"   • Last Boot Time: {boot_time or 'Not Available'}")
        print(f"   • OS Installation Date: {install_date or 'Not Available'}")
        print()
        print("=" * 80)
        print()
        
        # Show first 5 in detail, then summarize the rest
        if i == 5 and len(recent_devices) > 5:
            print(f"📋 SUMMARY OF REMAINING {len(recent_devices) - 5} DEVICES:")
            print("-" * 80)
            for j, summary_device in enumerate(recent_devices[5:], 6):
                (s_id, s_hostname, s_ip, s_method, s_status, s_os, s_manufacturer, 
                 s_model, s_cpu, s_memory, s_bios, s_user, *_) = summary_device
                
                print(f"{j:2d}. {s_hostname} ({s_ip}) - {s_method} - {s_status}")
                print(f"    👤 {s_user or 'No User'} | 🏭 {s_manufacturer or 'Unknown'} {s_model or ''}")
                print(f"    💾 {s_memory or 'Unknown Memory'} | 🔢 BIOS: {s_bios or 'N/A'}")
            print()
            break
    
    print()
    print("📊 DATA COMPLETENESS ANALYSIS")
    print("=" * 100)
    
    # Analyze data completeness for recent collections
    important_fields = [
        ('hostname', 'Device Names'),
        ('ip_address', 'IP Addresses'),
        ('operating_system', 'Operating Systems'),
        ('system_manufacturer', 'Manufacturers'),
        ('system_model', 'System Models'),
        ('processor_name', 'CPU Information'),
        ('total_physical_memory', 'Memory Information'),
        ('bios_serial_number', 'BIOS Serial Numbers'),
        ('working_user', 'Current Users'),
        ('mac_addresses', 'MAC Addresses'),
        ('domain_name', 'Domain Information'),
        ('windows_edition', 'Windows Editions'),
        ('network_adapters', 'Network Adapters'),
        ('total_disk_space', 'Disk Size Information'),
        ('last_boot_time', 'Last Boot Times'),
        ('os_install_date', 'Installation Dates')
    ]
    
    recent_count = len(recent_devices)
    
    print(f"Analysis based on {recent_count} recently collected devices:")
    print()
    
    for field, description in important_fields:
        cursor.execute(f'''
            SELECT COUNT(*) FROM assets 
            WHERE (created_at > ? OR updated_at > ?) 
            AND {field} IS NOT NULL AND {field} != ""
        ''', (fifteen_min_ago, fifteen_min_ago))
        
        populated = cursor.fetchone()[0]
        percentage = (populated / recent_count) * 100 if recent_count > 0 else 0
        
        if percentage >= 95:
            status = "✅ EXCELLENT"
        elif percentage >= 80:
            status = "✅ GOOD"
        elif percentage >= 60:
            status = "⚠️  FAIR"
        else:
            status = "❌ POOR"
        
        print(f"{status} {description}: {populated}/{recent_count} ({percentage:.1f}%)")
    
    print()
    print("🔍 DETAILED HARDWARE BREAKDOWN")
    print("=" * 100)
    
    # Hardware manufacturer breakdown
    cursor.execute('''
        SELECT system_manufacturer, COUNT(*) as count
        FROM assets 
        WHERE (created_at > ? OR updated_at > ?) 
        AND system_manufacturer IS NOT NULL
        GROUP BY system_manufacturer
        ORDER BY count DESC
    ''', (fifteen_min_ago, fifteen_min_ago))
    
    manufacturers = cursor.fetchall()
    print("🏭 Manufacturers Found:")
    for manufacturer, count in manufacturers:
        print(f"   • {manufacturer}: {count} devices")
    
    print()
    
    # Operating system breakdown
    cursor.execute('''
        SELECT operating_system, COUNT(*) as count
        FROM assets 
        WHERE (created_at > ? OR updated_at > ?) 
        AND operating_system IS NOT NULL
        GROUP BY operating_system
        ORDER BY count DESC
    ''', (fifteen_min_ago, fifteen_min_ago))
    
    operating_systems = cursor.fetchall()
    print("💿 Operating Systems Found:")
    for os, count in operating_systems:
        print(f"   • {os}: {count} devices")
    
    print()
    
    # User domain breakdown
    cursor.execute('''
        SELECT 
            CASE 
                WHEN working_user LIKE '%\\%' THEN SUBSTR(working_user, 1, INSTR(working_user, '\\') - 1)
                ELSE 'No Domain'
            END as domain,
            COUNT(*) as count
        FROM assets 
        WHERE (created_at > ? OR updated_at > ?) 
        AND working_user IS NOT NULL
        GROUP BY domain
        ORDER BY count DESC
    ''', (fifteen_min_ago, fifteen_min_ago))
    
    domains = cursor.fetchall()
    print("🌐 User Domains Found:")
    for domain, count in domains:
        print(f"   • {domain}: {count} devices")
    
    print()
    
    # Additional collected data fields
    print("🔍 ADDITIONAL DATA FIELDS COLLECTED")
    print("=" * 100)
    
    additional_fields = [
        ('bios_version', 'BIOS Versions'),
        ('motherboard_manufacturer', 'Motherboard Info'),
        ('graphics_card', 'Graphics Cards'),
        ('antivirus_product', 'Antivirus Software'),
        ('firewall_status', 'Firewall Status'),
        ('installed_software', 'Software Inventory'),
        ('running_services', 'Services Info'),
        ('user_accounts', 'User Accounts'),
        ('installed_printers', 'Printer Info'),
        ('time_zone', 'Time Zone Data')
    ]
    
    for field, description in additional_fields:
        cursor.execute(f'''
            SELECT COUNT(*) FROM assets 
            WHERE (created_at > ? OR updated_at > ?) 
            AND {field} IS NOT NULL AND {field} != ""
        ''', (fifteen_min_ago, fifteen_min_ago))
        
        populated = cursor.fetchone()[0]
        percentage = (populated / recent_count) * 100 if recent_count > 0 else 0
        
        if percentage >= 50:
            status = "✅"
        elif percentage >= 25:
            status = "⚠️ "
        else:
            status = "❌"
        
        print(f"{status} {description}: {populated}/{recent_count} ({percentage:.1f}%)")
    
    print()
    print("=" * 100)
    print("✅ DATA COLLECTION VERIFICATION COMPLETE")
    print("=" * 100)
    print("📝 Review Checklist:")
    print("   1. ✅ Are all expected devices listed above?")
    print("   2. ✅ Is the data completeness acceptable for your needs?")
    print("   3. ✅ Are there any missing critical fields?")
    print("   4. ✅ Do the hardware/OS breakdowns look correct?")
    print("   5. ✅ Is additional data (software, services, etc.) being collected?")
    print("=" * 100)
    
    conn.close()

if __name__ == "__main__":
    view_all_collected_data()