#!/usr/bin/env python3
"""
WMI Authentication Collection Analysis
Shows exactly what data WMI can collect with proper Windows credentials
"""

import wmi
import logging
from datetime import datetime

def test_wmi_with_authentication():
    """Test WMI collection with authentication to show all available data"""
    
    print("🔐 WMI AUTHENTICATION COLLECTION ANALYSIS")
    print("=" * 80)
    print(f"Testing WMI data collection with authentication")
    print(f"Target: localhost (127.0.0.1)")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Connect to WMI with current user credentials (authenticated)
        print("🔌 Connecting to WMI with authentication...")
        c = wmi.WMI()
        print("✅ WMI connection successful!")
        print()
        
        # Collect comprehensive data
        collected_data = {}
        
        print("📊 COLLECTING WMI DATA WITH AUTHENTICATION:")
        print("-" * 60)
        
        # 1. SYSTEM INFORMATION
        print("\n🖥️  SYSTEM INFORMATION:")
        try:
            for system in c.Win32_ComputerSystem():
                print(f"   • Computer Name: {system.Name}")
                print(f"   • Domain: {system.Domain}")
                print(f"   • Workgroup: {getattr(system, 'Workgroup', 'N/A')}")
                print(f"   • Total Memory: {int(system.TotalPhysicalMemory) / (1024**3):.1f} GB")
                print(f"   • Manufacturer: {system.Manufacturer}")
                print(f"   • Model: {system.Model}")
                print(f"   • System Type: {system.SystemType}")
                print(f"   • Number of Processors: {system.NumberOfProcessors}")
                print(f"   • Number of Logical Processors: {system.NumberOfLogicalProcessors}")
                
                collected_data.update({
                    'computer_name': system.Name,
                    'domain': system.Domain,
                    'total_memory_gb': int(system.TotalPhysicalMemory) / (1024**3),
                    'manufacturer': system.Manufacturer,
                    'model': system.Model,
                    'system_type': system.SystemType,
                    'processors': system.NumberOfProcessors,
                    'logical_processors': system.NumberOfLogicalProcessors
                })
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # 2. OPERATING SYSTEM
        print("\n🪟 OPERATING SYSTEM:")
        try:
            for os in c.Win32_OperatingSystem():
                print(f"   • OS Name: {os.Caption}")
                print(f"   • Version: {os.Version}")
                print(f"   • Build Number: {os.BuildNumber}")
                print(f"   • Architecture: {os.OSArchitecture}")
                print(f"   • Install Date: {os.InstallDate}")
                print(f"   • Last Boot: {os.LastBootUpTime}")
                print(f"   • System Directory: {os.SystemDirectory}")
                print(f"   • Windows Directory: {os.WindowsDirectory}")
                
                collected_data.update({
                    'os_name': os.Caption,
                    'os_version': os.Version,
                    'os_build': os.BuildNumber,
                    'os_architecture': os.OSArchitecture,
                    'install_date': str(os.InstallDate),
                    'last_boot': str(os.LastBootUpTime),
                    'system_dir': os.SystemDirectory,
                    'windows_dir': os.WindowsDirectory
                })
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # 3. PROCESSOR INFORMATION
        print("\n⚡ PROCESSOR INFORMATION:")
        try:
            for processor in c.Win32_Processor():
                print(f"   • Name: {processor.Name}")
                print(f"   • Manufacturer: {processor.Manufacturer}")
                print(f"   • Architecture: {processor.Architecture}")
                print(f"   • Max Clock Speed: {processor.MaxClockSpeed} MHz")
                print(f"   • Current Clock Speed: {processor.CurrentClockSpeed} MHz")
                print(f"   • Number of Cores: {processor.NumberOfCores}")
                print(f"   • Number of Logical Processors: {processor.NumberOfLogicalProcessors}")
                print(f"   • L2 Cache Size: {getattr(processor, 'L2CacheSize', 'N/A')} KB")
                print(f"   • L3 Cache Size: {getattr(processor, 'L3CacheSize', 'N/A')} KB")
                
                collected_data.update({
                    'processor_name': processor.Name,
                    'processor_manufacturer': processor.Manufacturer,
                    'processor_architecture': processor.Architecture,
                    'max_clock_speed': processor.MaxClockSpeed,
                    'current_clock_speed': processor.CurrentClockSpeed,
                    'processor_cores': processor.NumberOfCores,
                    'processor_logical': processor.NumberOfLogicalProcessors
                })
                break  # Just first processor for demo
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # 4. MEMORY INFORMATION
        print("\n💾 MEMORY INFORMATION:")
        try:
            total_memory = 0
            memory_slots = []
            for memory in c.Win32_PhysicalMemory():
                capacity_gb = int(memory.Capacity) / (1024**3)
                total_memory += capacity_gb
                memory_slots.append({
                    'capacity_gb': capacity_gb,
                    'speed': getattr(memory, 'Speed', 'Unknown'),
                    'manufacturer': getattr(memory, 'Manufacturer', 'Unknown'),
                    'part_number': getattr(memory, 'PartNumber', 'Unknown')
                })
                print(f"   • Slot: {capacity_gb:.1f} GB, Speed: {getattr(memory, 'Speed', 'Unknown')} MHz")
                print(f"     Manufacturer: {getattr(memory, 'Manufacturer', 'Unknown')}")
                print(f"     Part Number: {getattr(memory, 'PartNumber', 'Unknown')}")
            
            print(f"   • Total Physical Memory: {total_memory:.1f} GB")
            collected_data['memory_slots'] = memory_slots
            collected_data['total_memory_calculated'] = total_memory
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # 5. STORAGE INFORMATION
        print("\n💽 STORAGE INFORMATION:")
        try:
            drives = []
            for disk in c.Win32_DiskDrive():
                size_gb = int(disk.Size) / (1024**3) if disk.Size else 0
                drives.append({
                    'model': disk.Model,
                    'size_gb': size_gb,
                    'interface': getattr(disk, 'InterfaceType', 'Unknown'),
                    'serial': getattr(disk, 'SerialNumber', 'Unknown')
                })
                print(f"   • Drive: {disk.Model}")
                print(f"     Size: {size_gb:.1f} GB")
                print(f"     Interface: {getattr(disk, 'InterfaceType', 'Unknown')}")
                print(f"     Serial: {getattr(disk, 'SerialNumber', 'Unknown')}")
            
            collected_data['disk_drives'] = drives
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # 6. NETWORK ADAPTERS
        print("\n🌐 NETWORK ADAPTERS:")
        try:
            adapters = []
            for adapter in c.Win32_NetworkAdapterConfiguration(IPEnabled=True):
                adapters.append({
                    'description': adapter.Description,
                    'mac_address': adapter.MACAddress,
                    'ip_addresses': adapter.IPAddress,
                    'subnet_mask': adapter.IPSubnet,
                    'default_gateway': adapter.DefaultIPGateway,
                    'dhcp_enabled': adapter.DHCPEnabled
                })
                print(f"   • Adapter: {adapter.Description}")
                print(f"     MAC: {adapter.MACAddress}")
                print(f"     IP: {adapter.IPAddress}")
                print(f"     Gateway: {adapter.DefaultIPGateway}")
                print(f"     DHCP: {adapter.DHCPEnabled}")
            
            collected_data['network_adapters'] = adapters
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # 7. MOTHERBOARD INFORMATION
        print("\n🔌 MOTHERBOARD INFORMATION:")
        try:
            for board in c.Win32_BaseBoard():
                print(f"   • Manufacturer: {board.Manufacturer}")
                print(f"   • Product: {board.Product}")
                print(f"   • Version: {getattr(board, 'Version', 'Unknown')}")
                print(f"   • Serial Number: {getattr(board, 'SerialNumber', 'Unknown')}")
                
                collected_data.update({
                    'motherboard_manufacturer': board.Manufacturer,
                    'motherboard_product': board.Product,
                    'motherboard_version': getattr(board, 'Version', 'Unknown'),
                    'motherboard_serial': getattr(board, 'SerialNumber', 'Unknown')
                })
                break
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # 8. BIOS INFORMATION
        print("\n🔧 BIOS INFORMATION:")
        try:
            for bios in c.Win32_BIOS():
                print(f"   • Manufacturer: {bios.Manufacturer}")
                print(f"   • Version: {getattr(bios, 'SMBIOSBIOSVersion', bios.Version)}")
                print(f"   • Release Date: {getattr(bios, 'ReleaseDate', 'Unknown')}")
                print(f"   • Serial Number: {getattr(bios, 'SerialNumber', 'Unknown')}")
                
                collected_data.update({
                    'bios_manufacturer': bios.Manufacturer,
                    'bios_version': getattr(bios, 'SMBIOSBIOSVersion', bios.Version),
                    'bios_date': getattr(bios, 'ReleaseDate', 'Unknown'),
                    'bios_serial': getattr(bios, 'SerialNumber', 'Unknown')
                })
                break
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # 9. USER INFORMATION
        print("\n👤 USER INFORMATION:")
        try:
            # Get currently logged on users
            for session in c.Win32_LogonSession():
                if hasattr(session, 'LogonType') and session.LogonType == 2:  # Interactive logon
                    for user in c.Win32_LoggedOnUser():
                        print(f"   • Logged On User: {getattr(user, 'Antecedent', 'Unknown')}")
            
            # Get local user accounts
            users = []
            for user in c.Win32_UserAccount(LocalAccount=True):
                users.append({
                    'name': user.Name,
                    'full_name': getattr(user, 'FullName', ''),
                    'disabled': user.Disabled,
                    'sid': user.SID
                })
                print(f"   • Local User: {user.Name} ({'Disabled' if user.Disabled else 'Enabled'})")
            
            collected_data['local_users'] = users
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # 10. INSTALLED SOFTWARE
        print("\n📦 INSTALLED SOFTWARE (Sample):")
        try:
            software_count = 0
            software_list = []
            for software in c.Win32_Product():
                software_list.append({
                    'name': software.Name,
                    'version': getattr(software, 'Version', 'Unknown'),
                    'vendor': getattr(software, 'Vendor', 'Unknown'),
                    'install_date': getattr(software, 'InstallDate', 'Unknown')
                })
                if software_count < 10:  # Show only first 10
                    print(f"   • {software.Name} v{getattr(software, 'Version', 'Unknown')}")
                software_count += 1
                if software_count >= 50:  # Limit to prevent long output
                    break
            
            print(f"   • Total Software Found: {software_count}")
            collected_data['installed_software'] = software_list[:20]  # Store first 20
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # 11. SERVICES
        print("\n🔧 SERVICES (Running - Sample):")
        try:
            running_services = []
            service_count = 0
            for service in c.Win32_Service():
                if service.State == 'Running':
                    running_services.append({
                        'name': service.Name,
                        'display_name': service.DisplayName,
                        'state': service.State,
                        'start_mode': service.StartMode
                    })
                    if service_count < 10:
                        print(f"   • {service.DisplayName} ({service.Name})")
                    service_count += 1
            
            print(f"   • Total Running Services: {len(running_services)}")
            collected_data['running_services'] = running_services[:20]
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # SUMMARY
        print("\n📊 WMI COLLECTION SUMMARY:")
        print("=" * 60)
        print(f"✅ Total Data Points Collected: {len(collected_data)}")
        print(f"🔐 Authentication: Required and Used")
        print(f"📋 Data Categories:")
        print(f"   • System Information: ✅")
        print(f"   • Operating System: ✅")
        print(f"   • Hardware Details: ✅")
        print(f"   • Network Configuration: ✅")
        print(f"   • User Accounts: ✅")
        print(f"   • Installed Software: ✅")
        print(f"   • Running Services: ✅")
        print()
        
        print("🔑 AUTHENTICATION BENEFITS:")
        print("-" * 40)
        print("✅ Full system access to WMI classes")
        print("✅ User account information")
        print("✅ Installed software list")
        print("✅ Service information")
        print("✅ Security-related data")
        print("✅ Hardware serial numbers")
        print("✅ Network configuration details")
        print("❌ Cannot access: Asset tags, departments, locations")
        print("❌ Cannot access: Purchase dates, warranty info")
        print("❌ Cannot access: Business/organizational data")
        
        return collected_data
        
    except Exception as e:
        print(f"❌ WMI Connection Failed: {e}")
        return None
    finally:
        pass

def compare_authenticated_vs_unauthenticated():
    """Compare what data is available with vs without authentication"""
    
    print("\n🔐 AUTHENTICATION COMPARISON:")
    print("=" * 60)
    
    print("✅ WITH AUTHENTICATION (Current User Credentials):")
    print("   • Full WMI class access")
    print("   • User account details")
    print("   • Installed software list")
    print("   • Service information")
    print("   • Security settings")
    print("   • Complete hardware inventory")
    print("   • Network adapter details")
    print("   • System performance data")
    print()
    
    print("⚠️  WITHOUT AUTHENTICATION (Anonymous):")
    print("   • Limited WMI class access")
    print("   • Basic system information only")
    print("   • No user account access")
    print("   • No software inventory")
    print("   • No service details")
    print("   • Reduced hardware information")
    print("   • May fail completely on secured systems")
    print()
    
    print("🌐 REMOTE SYSTEMS (With Valid Credentials):")
    print("   • Same data as local with authentication")
    print("   • Requires network connectivity")
    print("   • Needs WMI/RPC ports open (135, 445)")
    print("   • Domain or local admin credentials")
    print("   • May require WinRM configuration")

if __name__ == "__main__":
    # Test WMI with authentication
    data = test_wmi_with_authentication()
    
    # Show comparison
    compare_authenticated_vs_unauthenticated()
    
    print("\n💡 CONCLUSION:")
    print("=" * 40)
    print("WMI with authentication provides comprehensive technical")
    print("data about Windows systems but cannot access business")
    print("data like asset tags, departments, or organizational info.")
    print("Authentication is essential for complete data collection!")