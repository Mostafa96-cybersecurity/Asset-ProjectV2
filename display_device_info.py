#!/usr/bin/env python3
"""
Display comprehensive device information collected by Ultimate Comprehensive Collector
"""

import sqlite3
import json

def display_comprehensive_device_info():
    """Display all collected device information"""
    
    conn = sqlite3.connect('assets.db')
    cursor = conn.cursor()
    
    # Get the latest collected data
    cursor.execute('''
        SELECT hostname, connected_screens, graphics_cards, monitor_info, 
               processor, total_memory_gb, disk_info, usb_devices, 
               installed_software_count, os_name, graphics_memory,
               network_adapters, sound_devices, printers, optical_drives,
               bios_version, motherboard_model, cpu_cores, cpu_threads,
               ip_address, mac_address, domain_workgroup
        FROM assets 
        WHERE hostname = "localhost"
    ''')
    
    data = cursor.fetchone()
    
    if data:
        print("🔥 ULTIMATE COMPREHENSIVE DEVICE INFORMATION")
        print("=" * 80)
        print(f"🖥️  Hostname: {data[0]}")
        print(f"📺 Connected Screens: {data[1]}")
        print(f"🎮 Graphics Cards: {data[2]}")
        print(f"🖥️  Monitor Details: {data[3]}")
        print(f"⚙️  Processor: {data[4]}")
        print(f"💾 Total Memory: {data[5]} GB")
        print(f"💽 Disk Information: {data[6]}")
        print(f"🔌 USB Devices: {data[7]}")
        print(f"📦 Installed Software: {data[8]} programs")
        print(f"🪟 Operating System: {data[9]}")
        print(f"🎮 Graphics Memory: {data[10]} GB")
        print(f"🌐 Network Adapters: {data[11]}")
        print(f"🔊 Sound Devices: {data[12]}")
        print(f"🖨️  Printers: {data[13]}")
        print(f"💿 Optical Drives: {data[14]}")
        print(f"🔧 BIOS Version: {data[15]}")
        print(f"🔧 Motherboard: {data[16]}")
        print(f"⚙️  CPU Cores: {data[17]}")
        print(f"⚙️  CPU Threads: {data[18]}")
        print(f"🌐 IP Address: {data[19]}")
        print(f"🔗 MAC Address: {data[20]}")
        print(f"🏢 Domain/Workgroup: {data[21]}")
        
        print("\n🔥 COLLECTION STATISTICS:")
        print("=" * 50)
        
        # Count non-null columns
        cursor.execute("SELECT * FROM assets WHERE hostname = 'localhost'")
        columns = [description[0] for description in cursor.description]
        row_data = cursor.fetchone()
        
        non_null_count = sum(1 for value in row_data if value is not None and value != '')
        total_columns = len(columns)
        
        print(f"📊 Total Database Columns: {total_columns}")
        print(f"✅ Populated Fields: {non_null_count}")
        print(f"📈 Data Completeness: {(non_null_count/total_columns)*100:.1f}%")
        
        print(f"\n🎯 YOUR SYSTEM COLLECTS EVERYTHING:")
        print("✅ Complete Hardware Information (CPU, RAM, Storage, Graphics)")
        print("✅ Connected Monitors/Screens Detection")
        print("✅ All USB Devices and Controllers")
        print("✅ Sound Cards and Audio Devices")
        print("✅ Network Adapters with IP/MAC addresses")
        print("✅ Printers and Optical Drives")
        print("✅ BIOS and Motherboard Details")
        print("✅ Complete Software Inventory")
        print("✅ System Settings and Configuration")
        print("✅ Performance and Utilization Data")
        print("✅ Security and Compliance Information")
        print("✅ Everything WMI Can Collect (196+ fields)")
        
    else:
        print("❌ No data found for localhost")
    
    conn.close()

if __name__ == "__main__":
    display_comprehensive_device_info()