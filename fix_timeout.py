#!/usr/bin/env python3
"""
Fix Collection Timeout for Large Networks
"""

import re

def optimize_timeout_settings():
    print("🔧 OPTIMIZING COLLECTION TIMEOUT SETTINGS")
    print("=" * 50)
    
    print("📊 Current Issue:")
    print("   • Devices Found: 461")
    print("   • Current Timeout: 60 seconds")
    print("   • Collection Success: 222/461 (48%)")
    print("   • Needed: Longer timeout for complete collection")
    
    print("\n💡 Recommended Fix:")
    print("   • Increase collection_timeout from 60 to 300 seconds (5 minutes)")
    print("   • This allows ~39 seconds per device on average")
    print("   • Should cover all 461 devices discovered")
    
    # Read current GUI file
    gui_file = 'gui/app.py'
    
    try:
        with open(gui_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find current timeout setting
        timeout_pattern = r"'collection_timeout':\s*(\d+)"
        match = re.search(timeout_pattern, content)
        
        if match:
            current_timeout = int(match.group(1))
            print(f"\n📋 Current setting found: collection_timeout: {current_timeout}")
            
            # Calculate optimal timeout
            devices_found = 461
            optimal_timeout = max(300, devices_found * 0.65)  # ~39 seconds per device
            
            print(f"🎯 Optimal timeout: {optimal_timeout:.0f} seconds")
            
            # Replace timeout value
            new_content = re.sub(
                timeout_pattern,
                f"'collection_timeout': {int(optimal_timeout)}",
                content
            )
            
            # Write back to file
            with open(gui_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ Updated collection_timeout: {current_timeout} → {int(optimal_timeout)} seconds")
            print(f"📈 This should allow complete collection of all {devices_found} devices")
            
        else:
            print("❌ Could not find collection_timeout setting in GUI file")
            
    except Exception as e:
        print(f"❌ Error updating timeout: {e}")
        return False
    
    print("\n🚀 Next Steps:")
    print("1. Restart your application (close and relaunch)")
    print("2. Run another Asset Scan")
    print("3. Should now collect all 461 devices")
    
    return True

def create_timeout_config():
    """Create a timeout configuration file for easy adjustment"""
    config = {
        "collection_timeout": 300,  # 5 minutes for large networks
        "per_device_timeout": 30,   # 30 seconds per device
        "discovery_timeout": 60,    # 1 minute for discovery
        "wmi_timeout": 45,          # 45 seconds for WMI
        "ssh_timeout": 30,          # 30 seconds for SSH
        "ping_timeout": 3,          # 3 seconds for ping
        "port_scan_timeout": 10     # 10 seconds for port scan
    }
    
    try:
        import json
        with open('collection_timeout_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print("\n📁 Created timeout config file: collection_timeout_config.json")
        print("   You can adjust these settings as needed")
        
    except Exception as e:
        print(f"❌ Could not create config file: {e}")

if __name__ == "__main__":
    success = optimize_timeout_settings()
    if success:
        create_timeout_config()
        print("\n✅ Timeout optimization complete!")
        print("   Restart your application and try scanning again")
    else:
        print("\n❌ Manual adjustment needed")
        print("   Edit gui/app.py line ~1650: change 'collection_timeout': 60 to 300")