#!/usr/bin/env python3
"""
COMPREHENSIVE SCAN PROCESS VERIFICATION
Ensuring the complete scan strategy works correctly:
1. Scan live devices
2. NMAP OS detection 
3. Windows → WMI + SNMP
4. Linux → SSH + SNMP  
5. Other → SSH + SNMP
6. Save with correct device type based on OS
"""

import sqlite3

def verify_scan_process():
    """Verify that the scan process follows the correct strategy"""
    print("=" * 80)
    print("🔍 COMPREHENSIVE SCAN PROCESS VERIFICATION")
    print("=" * 80)
    print()
    
    conn = sqlite3.connect('assets.db')
    cursor = conn.cursor()
    
    # 1. Check live device scanning
    print("1️⃣ LIVE DEVICE SCANNING VERIFICATION:")
    cursor.execute('SELECT COUNT(*) FROM assets WHERE ping_status = "alive"')
    alive_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM assets')
    total_count = cursor.fetchone()[0]
    
    print(f"   ✅ Total devices scanned: {total_count}")
    print(f"   ✅ Live devices detected: {alive_count}")
    print(f"   📊 Live device ratio: {(alive_count/total_count)*100:.1f}%")
    print()
    
    # 2. Check NMAP OS detection
    print("2️⃣ NMAP OS DETECTION VERIFICATION:")
    cursor.execute('SELECT COUNT(*) FROM assets WHERE nmap_os_family IS NOT NULL')
    nmap_os_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT nmap_os_family, COUNT(*) FROM assets WHERE nmap_os_family IS NOT NULL GROUP BY nmap_os_family')
    os_families = cursor.fetchall()
    
    print(f"   ✅ Devices with NMAP OS detection: {nmap_os_count}/{total_count} ({(nmap_os_count/total_count)*100:.1f}%)")
    print("   📊 OS Family Distribution:")
    for os_family, count in os_families:
        print(f"      • {os_family}: {count} devices")
    print()
    
    # 3. Check collection methods by OS type
    print("3️⃣ COLLECTION METHOD BY OS TYPE VERIFICATION:")
    
    # Windows devices - should use WMI + SNMP
    cursor.execute('''
        SELECT hostname, collection_method, wmi_collection_status, snmp_collection_status 
        FROM assets 
        WHERE nmap_os_family = "Windows" 
        LIMIT 10
    ''')
    windows_devices = cursor.fetchall()
    
    print("   🪟 WINDOWS DEVICES (should use WMI + SNMP):")
    wmi_success = 0
    snmp_success = 0
    for hostname, method, wmi_status, snmp_status in windows_devices:
        wmi_icon = "✅" if wmi_status == "success" else "❌" if wmi_status else "⚠️"
        snmp_icon = "✅" if snmp_status == "success" else "❌" if snmp_status else "⚠️"
        print(f"      {hostname}: Method={method}, WMI={wmi_icon}, SNMP={snmp_icon}")
        if wmi_status == "success": wmi_success += 1
        if snmp_status == "success": snmp_success += 1
    
    print(f"      📊 WMI Success Rate: {wmi_success}/{len(windows_devices)} ({(wmi_success/max(len(windows_devices),1))*100:.1f}%)")
    print(f"      📊 SNMP Success Rate: {snmp_success}/{len(windows_devices)} ({(snmp_success/max(len(windows_devices),1))*100:.1f}%)")
    print()
    
    # Linux devices - should use SSH + SNMP
    cursor.execute('''
        SELECT hostname, collection_method, ssh_collection_status, snmp_collection_status 
        FROM assets 
        WHERE nmap_os_family = "Linux" 
        LIMIT 10
    ''')
    linux_devices = cursor.fetchall()
    
    print("   🐧 LINUX DEVICES (should use SSH + SNMP):")
    ssh_success = 0
    snmp_success_linux = 0
    for hostname, method, ssh_status, snmp_status in linux_devices:
        ssh_icon = "✅" if ssh_status == "success" else "❌" if ssh_status else "⚠️"
        snmp_icon = "✅" if snmp_status == "success" else "❌" if snmp_status else "⚠️"
        print(f"      {hostname}: Method={method}, SSH={ssh_icon}, SNMP={snmp_icon}")
        if ssh_status == "success": ssh_success += 1
        if snmp_status == "success": snmp_success_linux += 1
    
    if linux_devices:
        print(f"      📊 SSH Success Rate: {ssh_success}/{len(linux_devices)} ({(ssh_success/len(linux_devices))*100:.1f}%)")
        print(f"      📊 SNMP Success Rate: {snmp_success_linux}/{len(linux_devices)} ({(snmp_success_linux/len(linux_devices))*100:.1f}%)")
    else:
        print("      ⚠️ No Linux devices found in sample")
    print()
    
    # 4. Check device type classification based on OS
    print("4️⃣ DEVICE TYPE CLASSIFICATION BY OS VERIFICATION:")
    cursor.execute('''
        SELECT nmap_os_family, nmap_device_type, device_type, COUNT(*) 
        FROM assets 
        WHERE nmap_os_family IS NOT NULL 
        GROUP BY nmap_os_family, nmap_device_type, device_type 
        ORDER BY COUNT(*) DESC
    ''')
    
    classification_data = cursor.fetchall()
    print("   📊 OS → Device Type Mapping:")
    for os_family, nmap_dtype, device_type, count in classification_data:
        print(f"      {os_family} + {nmap_dtype or 'N/A'} → {device_type}: {count} devices")
    print()
    
    # 5. Check for hostname mismatches
    print("5️⃣ HOSTNAME FEATURE VERIFICATION:")
    cursor.execute('''
        SELECT hostname, computer_name, dns_hostname, fqdn 
        FROM assets 
        WHERE hostname IS NOT NULL 
        AND (computer_name IS NOT NULL OR dns_hostname IS NOT NULL OR fqdn IS NOT NULL)
        LIMIT 10
    ''')
    
    hostname_data = cursor.fetchall()
    mismatches = 0
    
    print("   🏷️ Hostname Consistency Check:")
    for hostname, computer_name, dns_hostname, fqdn in hostname_data:
        hostname_variants = [hostname, computer_name, dns_hostname, fqdn]
        hostname_variants = [h for h in hostname_variants if h]
        
        # Check if all variants are similar (remove domain suffixes for comparison)
        base_names = set()
        for variant in hostname_variants:
            if variant:
                base_name = variant.split('.')[0].lower()
                base_names.add(base_name)
        
        if len(base_names) > 1:
            mismatches += 1
            print(f"      ⚠️ {hostname}: Variants={hostname_variants}")
        else:
            print(f"      ✅ {hostname}: Consistent")
    
    print(f"   📊 Hostname Mismatches: {mismatches}/{len(hostname_data)} devices")
    print()
    
    # 6. Check data collection completeness
    print("6️⃣ DATA COLLECTION COMPLETENESS:")
    
    # Check Windows data completeness
    cursor.execute('''
        SELECT 
            COUNT(*) as total,
            COUNT(operating_system) as os_data,
            COUNT(processor_name) as cpu_data,
            COUNT(total_physical_memory) as memory_data,
            COUNT(installed_software) as software_data,
            COUNT(running_services) as services_data
        FROM assets 
        WHERE nmap_os_family = "Windows"
    ''')
    
    windows_completeness = cursor.fetchone()
    if windows_completeness and windows_completeness[0] > 0:
        total_windows = windows_completeness[0]
        print(f"   🪟 Windows Data Completeness (out of {total_windows} devices):")
        print(f"      OS Info: {windows_completeness[1]} ({(windows_completeness[1]/total_windows)*100:.1f}%)")
        print(f"      CPU Info: {windows_completeness[2]} ({(windows_completeness[2]/total_windows)*100:.1f}%)")
        print(f"      Memory Info: {windows_completeness[3]} ({(windows_completeness[3]/total_windows)*100:.1f}%)")
        print(f"      Software: {windows_completeness[4]} ({(windows_completeness[4]/total_windows)*100:.1f}%)")
        print(f"      Services: {windows_completeness[5]} ({(windows_completeness[5]/total_windows)*100:.1f}%)")
    
    # Check duplicate prevention
    print()
    print("7️⃣ DUPLICATE PREVENTION VERIFICATION:")
    cursor.execute('''
        SELECT COUNT(*) as total_duplicates
        FROM assets a1
        WHERE EXISTS (
            SELECT 1 FROM assets a2 
            WHERE a2.id != a1.id 
            AND (a2.hostname = a1.hostname OR a2.ip_address = a1.ip_address)
        )
    ''')
    
    duplicates = cursor.fetchone()[0]
    print(f"   📊 Potential Duplicates: {duplicates} devices")
    
    if duplicates > 0:
        cursor.execute('''
            SELECT hostname, ip_address, COUNT(*) 
            FROM assets 
            GROUP BY hostname, ip_address 
            HAVING COUNT(*) > 1
            LIMIT 5
        ''')
        
        duplicate_examples = cursor.fetchall()
        print("   ⚠️ Duplicate Examples:")
        for hostname, ip, count in duplicate_examples:
            print(f"      {hostname} ({ip}): {count} entries")
    else:
        print("   ✅ No duplicates detected")
    
    conn.close()
    
    print()
    print("=" * 80)
    print("✅ SCAN PROCESS VERIFICATION COMPLETE")
    print("=" * 80)

def check_collection_method_distribution():
    """Check how devices are being collected by method"""
    print("\n🔍 COLLECTION METHOD DISTRIBUTION ANALYSIS:")
    print("-" * 60)
    
    conn = sqlite3.connect('assets.db')
    cursor = conn.cursor()
    
    # Get collection method distribution
    cursor.execute('SELECT collection_method, COUNT(*) FROM assets WHERE collection_method IS NOT NULL GROUP BY collection_method ORDER BY COUNT(*) DESC')
    methods = cursor.fetchall()
    
    total_with_method = sum(count for _, count in methods)
    
    for method, count in methods:
        percentage = (count / total_with_method) * 100
        print(f"   {method}: {count} devices ({percentage:.1f}%)")
    
    # Check method effectiveness by OS
    print("\n📊 COLLECTION METHOD EFFECTIVENESS BY OS:")
    cursor.execute('''
        SELECT 
            nmap_os_family,
            collection_method,
            COUNT(*) as device_count,
            AVG(CASE WHEN wmi_collection_status = "success" THEN 1 ELSE 0 END) * 100 as wmi_success_rate,
            AVG(CASE WHEN ssh_collection_status = "success" THEN 1 ELSE 0 END) * 100 as ssh_success_rate,
            AVG(CASE WHEN snmp_collection_status = "success" THEN 1 ELSE 0 END) * 100 as snmp_success_rate
        FROM assets 
        WHERE nmap_os_family IS NOT NULL AND collection_method IS NOT NULL
        GROUP BY nmap_os_family, collection_method
        ORDER BY nmap_os_family, device_count DESC
    ''')
    
    effectiveness_data = cursor.fetchall()
    
    for os_family, method, count, wmi_rate, ssh_rate, snmp_rate in effectiveness_data:
        print(f"\n   {os_family} via {method} ({count} devices):")
        if wmi_rate > 0:
            print(f"      WMI Success: {wmi_rate:.1f}%")
        if ssh_rate > 0:
            print(f"      SSH Success: {ssh_rate:.1f}%")
        if snmp_rate > 0:
            print(f"      SNMP Success: {snmp_rate:.1f}%")
    
    conn.close()

if __name__ == "__main__":
    verify_scan_process()
    check_collection_method_distribution()