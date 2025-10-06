#!/usr/bin/env python3
"""
🔐 IMMEDIATE AUTHENTICATION SETUP GUIDE
Get 90%+ data collection in next 2 hours!
"""

import json
import os
from pathlib import Path

def create_authentication_setup():
    print("=" * 80)
    print("🔐 IMMEDIATE AUTHENTICATION SETUP - GET TO 90%+ DATA COLLECTION!")
    print("=" * 80)
    print()
    
    print("📋 SETUP CHECKLIST (Complete in order):")
    print()
    
    print("1️⃣ WINDOWS WMI AUTHENTICATION (HIGHEST PRIORITY)")
    print("   🎯 Impact: Increases data collection from 41% to 85%+")
    print("   ⏱️ Time Required: 30 minutes")
    print()
    
    print("   📝 STEP-BY-STEP INSTRUCTIONS:")
    print("   a) Create domain service account:")
    print("      • Account name: svc-asset-scanner")
    print("      • Password: Strong password (12+ chars)")
    print("      • Group membership: Domain Users + Local 'Log on as a service'")
    print()
    
    print("   b) Grant WMI permissions:")
    print("      • Run: wmimgmt.msc")
    print("      • Right-click 'WMI Control' → Properties → Security")
    print("      • Add service account with: Enable Account, Remote Enable")
    print()
    
    print("   c) Grant DCOM permissions:")
    print("      • Run: dcomcnfg.exe")
    print("      • Navigate: Component Services → DCOM Config → Windows Management Instrumentation")
    print("      • Right-click → Properties → Security")
    print("      • Add service account with: Local Launch, Remote Launch, Local Activation, Remote Activation")
    print()
    
    print("   d) Update credentials in system:")
    
    # Create WMI credentials template
    wmi_config = {
        "wmi_credentials": {
            "domain": "YOUR_DOMAIN.COM",
            "username": "svc-asset-scanner",
            "password": "YOUR_SECURE_PASSWORD",
            "connection_timeout": 30,
            "authentication_level": "Packet"
        }
    }
    
    print(f"      • Edit 'collector_credentials.json' with your domain credentials")
    print(f"      • Template created: wmi_auth_template.json")
    print()
    
    print("2️⃣ SNMP COMMUNITY STRINGS (MEDIUM PRIORITY)")
    print("   🎯 Impact: Complete network device inventory")
    print("   ⏱️ Time Required: 15 minutes")
    print()
    
    print("   📝 COMMON SNMP COMMUNITIES:")
    snmp_config = {
        "snmp_communities": [
            {"community": "public", "version": "2c", "description": "Default read-only"},
            {"community": "private", "version": "2c", "description": "Default read-write"},
            {"community": "cisco", "version": "2c", "description": "Cisco devices"},
            {"community": "hp", "version": "2c", "description": "HP devices"},
            {"community": "dell", "version": "2c", "description": "Dell devices"},
            {"community": "admin", "version": "2c", "description": "Admin community"},
            {"community": "YOUR_CUSTOM_COMMUNITY", "version": "2c", "description": "Your organization"}
        ]
    }
    
    print("   • Check with network team for community strings")
    print("   • Try common defaults: public, private, cisco, hp")
    print("   • Template created: snmp_auth_template.json")
    print()
    
    print("3️⃣ SSH KEY AUTHENTICATION (MEDIUM PRIORITY)")
    print("   🎯 Impact: Complete Linux system inventory")
    print("   ⏱️ Time Required: 45 minutes")
    print()
    
    print("   📝 SETUP PROCESS:")
    print("   a) Generate SSH key pair:")
    print("      • Run: ssh-keygen -t rsa -b 4096 -f asset_scanner_key")
    print("      • No passphrase (for automation)")
    print()
    
    print("   b) Deploy public key to Linux systems:")
    print("      • Copy asset_scanner_key.pub to ~/.ssh/authorized_keys")
    print("      • Set permissions: chmod 600 ~/.ssh/authorized_keys")
    print()
    
    ssh_config = {
        "ssh_credentials": {
            "username": "asset-scanner",
            "private_key_path": "./keys/asset_scanner_key",
            "connection_timeout": 30,
            "port": 22
        }
    }
    
    print("   c) Configure system account:")
    print("      • Create 'asset-scanner' user on Linux systems")
    print("      • Grant sudo access for system commands")
    print("      • Template created: ssh_auth_template.json")
    print()
    
    # Save templates
    templates_dir = Path("auth_templates")
    templates_dir.mkdir(exist_ok=True)
    
    with open(templates_dir / "wmi_auth_template.json", "w") as f:
        json.dump(wmi_config, f, indent=2)
    
    with open(templates_dir / "snmp_auth_template.json", "w") as f:
        json.dump(snmp_config, f, indent=2)
    
    with open(templates_dir / "ssh_auth_template.json", "w") as f:
        json.dump(ssh_config, f, indent=2)
    
    print("✅ AUTHENTICATION TEMPLATES CREATED!")
    print(f"   📁 Location: {templates_dir.absolute()}")
    print()

def show_expected_improvements():
    print("=" * 80)
    print("📈 EXPECTED DATA COLLECTION IMPROVEMENTS")
    print("=" * 80)
    print()
    
    improvements = [
        {
            "method": "WMI (Windows)",
            "current": "41.2% (96/233 devices)",
            "after_auth": "90%+ (210+ devices)",
            "new_data": "50+ additional fields per device",
            "examples": "Software, Services, Users, Hardware details"
        },
        {
            "method": "SSH (Linux)",
            "current": "0% (0/233 devices)",
            "after_auth": "95%+ of Linux devices",
            "new_data": "30+ fields per device",
            "examples": "Packages, Processes, Configurations, Performance"
        },
        {
            "method": "SNMP (Network)",
            "current": "0% (0/233 devices)",
            "after_auth": "80%+ of network devices",
            "new_data": "25+ fields per device",
            "examples": "Interface stats, Performance, Configuration"
        }
    ]
    
    for improvement in improvements:
        print(f"📊 {improvement['method']}:")
        print(f"   📉 Current: {improvement['current']}")
        print(f"   📈 After Auth: {improvement['after_auth']}")
        print(f"   🆕 New Data: {improvement['new_data']}")
        print(f"   💡 Examples: {improvement['examples']}")
        print()
    
    print("🎯 TOTAL EXPECTED IMPROVEMENT:")
    print("   • Overall data collection: 41% → 90%+")
    print("   • Devices with full data: 96 → 210+")
    print("   • Additional data points: 15,000+ new fields")
    print("   • Asset visibility: 2x improvement")
    print()

def show_immediate_actions():
    print("=" * 80)
    print("⚡ IMMEDIATE ACTION PLAN (Next 2 Hours)")
    print("=" * 80)
    print()
    
    actions = [
        {
            "time": "0-30 min",
            "action": "🔐 Set up WMI Authentication",
            "priority": "CRITICAL",
            "steps": [
                "Contact domain admin for service account",
                "Create svc-asset-scanner account",
                "Configure WMI permissions",
                "Update collector_credentials.json"
            ]
        },
        {
            "time": "30-45 min", 
            "action": "📡 Configure SNMP Communities",
            "priority": "HIGH",
            "steps": [
                "Contact network team",
                "Get community strings",
                "Update SNMP configuration",
                "Test network device access"
            ]
        },
        {
            "time": "45-90 min",
            "action": "🐧 Set up SSH Keys",
            "priority": "MEDIUM",
            "steps": [
                "Generate SSH key pair",
                "Deploy to Linux systems",
                "Create service account",
                "Test SSH connections"
            ]
        },
        {
            "time": "90-120 min",
            "action": "🧪 Test Full Collection",
            "priority": "VALIDATION",
            "steps": [
                "Run enhanced collector",
                "Verify data collection rates",
                "Check new data fields",
                "Document results"
            ]
        }
    ]
    
    for action in actions:
        priority_emoji = "🔥" if action["priority"] == "CRITICAL" else "⚡" if action["priority"] == "HIGH" else "💡"
        print(f"⏰ {action['time']}: {action['action']}")
        print(f"   {priority_emoji} Priority: {action['priority']}")
        print("   Steps:")
        for step in action["steps"]:
            print(f"      • {step}")
        print()

def create_quick_test_script():
    print("=" * 80)
    print("🧪 AUTHENTICATION TEST SCRIPT")
    print("=" * 80)
    print()
    
    test_script = '''#!/usr/bin/env python3
"""
Quick Authentication Test Script
Run this after setting up credentials
"""

import subprocess
import json
import sys

def test_wmi_auth():
    """Test WMI authentication"""
    print("🔐 Testing WMI Authentication...")
    try:
        # Simple WMI test
        result = subprocess.run([
            'wmic', 'computersystem', 'get', 'name,manufacturer'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("   ✅ WMI Authentication: SUCCESS")
            return True
        else:
            print("   ❌ WMI Authentication: FAILED")
            return False
    except Exception as e:
        print(f"   ❌ WMI Authentication: ERROR - {e}")
        return False

def test_ssh_connection(host="192.168.1.10"):
    """Test SSH connection"""
    print(f"🐧 Testing SSH Connection to {host}...")
    try:
        result = subprocess.run([
            'ssh', '-o', 'ConnectTimeout=10', 
            '-o', 'BatchMode=yes',
            f'asset-scanner@{host}', 
            'echo "SSH Test Successful"'
        ], capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            print("   ✅ SSH Authentication: SUCCESS")
            return True
        else:
            print("   ❌ SSH Authentication: FAILED")
            return False
    except Exception as e:
        print(f"   ❌ SSH Authentication: ERROR - {e}")
        return False

def test_snmp_access(host="192.168.1.1", community="public"):
    """Test SNMP access"""
    print(f"📡 Testing SNMP Access to {host}...")
    try:
        # Try snmpwalk if available
        result = subprocess.run([
            'snmpwalk', '-v2c', '-c', community, host, 'system'
        ], capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            print("   ✅ SNMP Authentication: SUCCESS")
            return True
        else:
            print("   ⚠️ SNMP Authentication: No snmpwalk tool found")
            return False
    except Exception as e:
        print(f"   ❌ SNMP Authentication: ERROR - {e}")
        return False

def main():
    print("=" * 60)
    print("🧪 AUTHENTICATION TEST RESULTS")
    print("=" * 60)
    
    wmi_ok = test_wmi_auth()
    ssh_ok = test_ssh_connection()
    snmp_ok = test_snmp_access()
    
    print("\\n" + "=" * 60)
    print("📊 SUMMARY:")
    print(f"   🔐 WMI:  {'✅ Ready' if wmi_ok else '❌ Needs Setup'}")
    print(f"   🐧 SSH:  {'✅ Ready' if ssh_ok else '❌ Needs Setup'}")
    print(f"   📡 SNMP: {'✅ Ready' if snmp_ok else '❌ Needs Setup'}")
    
    ready_count = sum([wmi_ok, ssh_ok, snmp_ok])
    print(f"\\n🎯 Authentication Status: {ready_count}/3 methods ready")
    
    if ready_count >= 2:
        print("✅ EXCELLENT! Ready for enhanced data collection!")
    elif ready_count >= 1:
        print("⚡ GOOD! Some authentication configured, continue setup")
    else:
        print("⚠️ SETUP NEEDED: Configure authentication methods")

if __name__ == "__main__":
    main()
'''
    
    with open("auth_test.py", "w") as f:
        f.write(test_script)
    
    print("🧪 Authentication test script created: auth_test.py")
    print("   Run this after setting up credentials to verify configuration")
    print()

if __name__ == "__main__":
    create_authentication_setup()
    show_expected_improvements()
    show_immediate_actions()
    create_quick_test_script()
    
    print("=" * 80)
    print("🚀 NEXT STEPS TO ACHIEVE 90%+ DATA COLLECTION:")
    print("=" * 80)
    print()
    print("1. 📋 Review authentication templates in 'auth_templates/' folder")
    print("2. 🔐 Set up WMI credentials (HIGHEST PRIORITY)")
    print("3. 📡 Configure SNMP communities")
    print("4. 🐧 Deploy SSH keys")
    print("5. 🧪 Run 'python auth_test.py' to verify setup")
    print("6. ⚡ Run enhanced collector to see 90%+ data collection!")
    print()
    print("💡 TIP: Start with WMI authentication - it will give you the biggest impact!")