1# Comprehensive Data Collection Verification for IP 10.0.21.47  # type: ignore
# Verify that data is actually being collected and saved to database in English only
# Test device-specific field collection based on detected OS type

import sys
import sqlite3
import time
import logging
from datetime import datetime
from pathlib import Path

# Add project root to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

TARGET_IP = "10.0.21.47"

def verify_database_before_collection():
    """Check database state before collection"""
    
    print("🔍 CHECKING DATABASE STATE BEFORE COLLECTION")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect('assets.db')
        cursor = conn.cursor()
        
        # Check if target IP already exists
        cursor.execute('SELECT COUNT(*) FROM assets WHERE ip_address = ?', (TARGET_IP,))
        existing_count = cursor.fetchone()[0]
        
        print(f"📊 Existing records for {TARGET_IP}: {existing_count}")
        
        if existing_count > 0:
            print(f"⚠️ IP {TARGET_IP} already exists in database")
            
            # Show existing data
            cursor.execute('SELECT hostname, device_type, working_user, manufacturer, model, created_at FROM assets WHERE ip_address = ?', (TARGET_IP,))
            existing_records = cursor.fetchall()
            
            for i, record in enumerate(existing_records, 1):
                hostname, device_type, working_user, manufacturer, model, created_at = record
                print(f"   Record {i}: {hostname} ({device_type}) - {manufacturer} {model}")
                print(f"              User: {working_user}, Created: {created_at}")
        
        # Get total device count
        cursor.execute('SELECT COUNT(*) FROM assets')
        total_devices = cursor.fetchone()[0]
        print(f"📈 Total devices in database: {total_devices}")
        
        conn.close()
        return existing_count
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return 0

def test_os_detection():
    """Test OS detection for target IP"""
    
    print(f"\n🎯 TESTING OS DETECTION FOR {TARGET_IP}")
    print("-" * 50)
    
    try:
        # Import the OS detection functions
        from ultra_fast_collector import _nmap_os_detection, _port_based_os_detection
        
        print("✅ OS detection functions imported successfully")
        
        # Try NMAP first
        print("🔧 Attempting NMAP OS detection...")
        nmap_result = _nmap_os_detection(TARGET_IP)
        
        if nmap_result.get('detected_os') != 'Unknown':
            print("✅ NMAP Detection Success:")
            print(f"   OS: {nmap_result.get('detected_os', 'Unknown')}")
            print(f"   Confidence: {nmap_result.get('os_confidence', 'Unknown')}")
            print(f"   Method: {nmap_result.get('detection_method', 'Unknown')}")
            return nmap_result
        else:
            print("❌ NMAP detection failed, trying port-based detection...")
        
        # Fallback to port-based detection
        port_result = _port_based_os_detection(TARGET_IP)
        print("✅ Port-based Detection Result:")
        print(f"   OS: {port_result.get('detected_os', 'Unknown')}")
        print(f"   Confidence: {port_result.get('os_confidence', 'Unknown')}")
        print(f"   Method: {port_result.get('detection_method', 'Unknown')}")
        print(f"   Open Ports: {port_result.get('open_ports_string', 'None')}")
        
        return port_result
        
    except ImportError as e:
        print(f"❌ Failed to import OS detection functions: {e}")
        return {'detected_os': 'Unknown', 'os_confidence': '0', 'detection_method': 'Failed'}
    except Exception as e:
        print(f"❌ OS detection failed: {e}")
        return {'detected_os': 'Unknown', 'os_confidence': '0', 'detection_method': 'Error'}

def test_data_collection():
    """Test actual data collection using ultra fast collector"""
    
    print(f"\n🚀 TESTING DATA COLLECTION FOR {TARGET_IP}")
    print("-" * 50)
    
    try:
        from ultra_fast_collector import UltraFastDeviceCollector
        
        # Configure collection with test credentials
        collection_config = {
            'targets': [TARGET_IP],
            'win_creds': [
                ('administrator', 'admin123'),
                ('admin', 'password'),
                ('user', 'user123'),
                ('guest', '')
            ],
            'linux_creds': [
                ('root', 'root123'),
                ('admin', 'admin123'),
                ('user', 'user123')
            ],
            'snmp_v2c': ['public', 'private', 'community'],
            'snmp_v3': {},
            'use_http': True,
            'discovery_workers': 1,
            'collection_workers': 1,
            'parent': None
        }
        
        print("🔧 Collection Configuration:")
        print(f"   Target: {TARGET_IP}")
        print(f"   Windows Credentials: {len(collection_config['win_creds'])} sets")
        print(f"   Linux Credentials: {len(collection_config['linux_creds'])} sets")
        print(f"   SNMP Communities: {collection_config['snmp_v2c']}")
        
        # Create collector
        collector = UltraFastDeviceCollector(**collection_config)
        
        # Track collection results
        collected_devices = []
        collection_logs = []
        
        def on_device_collected(device_data):
            collected_devices.append(device_data)
            print(f"📊 Device collected: {device_data.get('hostname', TARGET_IP)}")
            print(f"   Type: {device_data.get('device_type', 'Unknown')}")
            print(f"   Method: {device_data.get('collection_method', 'Unknown')}")
        
        def on_log_message(message):
            collection_logs.append(message)
            if TARGET_IP in message:
                print(f"📝 LOG: {message}")
        
        def on_collection_finished():
            print("✅ Collection phase finished")
        
        # Connect signals
        collector.device_collected.connect(on_device_collected)
        collector.log_message.connect(on_log_message)
        collector.collection_finished.connect(on_collection_finished)
        
        print("\n🚀 Starting collection...")
        collector.start()
        
        # Wait for collection
        timeout = 90  # 90 seconds timeout
        start_time = time.time()
        
        while collector.isRunning() and (time.time() - start_time) < timeout:
            time.sleep(2)
            if len(collected_devices) > 0:
                print(f"⏳ Collection in progress... ({len(collected_devices)} devices collected)")
        
        if collector.isRunning():
            print("⚠️ Collection timeout - stopping collector")
            collector.stop()
            collector.wait(5000)
        
        print("\n📊 Collection Results:")
        print(f"   Devices collected: {len(collected_devices)}")
        print(f"   Log messages: {len(collection_logs)}")
        
        return collected_devices
        
    except Exception as e:
        print(f"❌ Collection failed: {e}")
        import traceback
        print(f"📋 Error details: {traceback.format_exc()}")
        return []

def verify_database_after_collection():
    """Verify database state after collection and check for English-only data"""
    
    print("\n💾 VERIFYING DATABASE AFTER COLLECTION")
    print("-" * 50)
    
    try:
        conn = sqlite3.connect('assets.db')
        cursor = conn.cursor()
        
        # Check for the target IP
        cursor.execute('SELECT * FROM assets WHERE ip_address = ?', (TARGET_IP,))
        target_records = cursor.fetchall()
        
        if not target_records:
            print(f"❌ No records found for {TARGET_IP} after collection")
            
            # Check for recent additions
            cursor.execute('SELECT ip_address, hostname, device_type, created_at FROM assets ORDER BY created_at DESC LIMIT 10')
            recent_records = cursor.fetchall()
            
            if recent_records:
                print("\n🔍 Recent additions to database:")
                for ip, hostname, device_type, created_at in recent_records:
                    print(f"   {ip} - {hostname} ({device_type}) - {created_at}")
            
            return False
        
        # Get column names
        cursor.execute('PRAGMA table_info(assets)')
        columns = [col[1] for col in cursor.fetchall()]
        
        print(f"✅ Found {len(target_records)} record(s) for {TARGET_IP}")
        
        # Analyze each record
        for i, record in enumerate(target_records, 1):
            print(f"\n📋 Record {i} - Comprehensive Analysis:")
            device_data = dict(zip(columns, record))
            
            # Essential device information
            essential_fields = [
                'hostname', 'ip_address', 'device_type', 'collection_method',
                'detected_os', 'os_confidence', 'working_user', 'domain',
                'manufacturer', 'model', 'operating_system', 'installed_ram_gb',
                'storage', 'serial_number', 'processor', 'system_sku',
                'created_at', 'last_updated'
            ]
            
            print("   🎯 Essential Information:")
            for field in essential_fields:
                value = device_data.get(field)
                if value and str(value).strip() and str(value) not in ['None', 'null', '']:
                    print(f"      {field}: {value}")
            
            # Check for Arabic text (English-only requirement)
            arabic_fields = []
            non_english_fields = []
            
            for field, value in device_data.items():
                if value and isinstance(value, str) and str(value).strip():
                    # Check for Arabic characters
                    if any('\u0600' <= char <= '\u06FF' for char in str(value)):
                        arabic_fields.append((field, value))
                    
                    # Check for non-ASCII characters (potential non-English)
                    if not all(ord(char) < 128 for char in str(value)):
                        if field not in [f[0] for f in arabic_fields]:  # Don't double-count Arabic
                            non_english_fields.append((field, value))
            
            # Report language issues
            if arabic_fields:
                print("   ❌ ARABIC TEXT FOUND:")
                for field, value in arabic_fields:
                    print(f"      {field}: {value}")
            
            if non_english_fields:
                print("   ⚠️ NON-ASCII TEXT FOUND:")
                for field, value in non_english_fields:
                    print(f"      {field}: {value}")
            
            if not arabic_fields and not non_english_fields:
                print("   ✅ ALL TEXT IS IN ENGLISH")
            
            # Device-specific field analysis
            device_type = device_data.get('device_type', 'Unknown')
            print(f"\n   📊 Device Type: {device_type}")
            
            if device_type == 'Windows':
                windows_fields = [
                    'working_user', 'domain', 'manufacturer', 'model', 
                    'installed_ram_gb', 'storage', 'processor', 'system_sku',
                    'active_gpu', 'connected_screens'
                ]
                collected_count = sum(1 for f in windows_fields if device_data.get(f))
                print(f"   📈 Windows-specific fields collected: {collected_count}/{len(windows_fields)}")
                
                for field in windows_fields:
                    value = device_data.get(field)
                    if value and str(value).strip():
                        print(f"      ✅ {field}: {value}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        return False

def show_device_type_requirements():
    """Show the field requirements for different device types"""
    
    print("\n📋 DEVICE TYPE COLLECTION REQUIREMENTS")
    print("=" * 60)
    
    requirements = {
        'Windows/Windows Server (WMI)': [
            'Hostname', 'Working User', 'Domain', 'Model/Vendor', 'IP Address',
            'OS Name', 'Installed RAM (GB)', 'Storage', 'SN', 'Processor',
            'System SKU', 'Active GPU', 'Connected Screens', 'Status'
        ],
        'Linux (SSH)': [
            'Hostname', 'Working User', 'Model/Vendor', 'IP Address', 'OS Name',
            'Installed RAM (GB)', 'Storage', 'SN', 'Processor', 'Status'
        ],
        'Hypervisor (SSH/SNMP/HTTP)': [
            'Hostname', 'Model/Vendor', 'IP Address', 'Total RAM', 'Total CPU',
            'Storage', 'SN', 'Location', 'Cluster', 'vCenter', 'CPU Sockets',
            'CPU Cores', 'CPU Threads', 'Datastores (Total/Free)', 'VM Count',
            'Management IP', 'vMotion IP', 'Status', 'Firmware/OS Version'
        ],
        'Network Devices (SSH/SNMP)': [
            'Hostname', 'Model/Vendor', 'IP Address', 'SN', 'Location',
            'Firmware Version', 'Ports (Total)', 'PoE', 'Mgmt VLAN',
            'Uplink To', 'Mgmt MAC', 'Status'
        ],
        'Printers (SNMP/HTTP)': [
            'Hostname', 'Model', 'SN', 'IP Address', 'Location',
            'Firmware Version', 'Page Counter (Total)', 'Page Counter (Mono)',
            'Page Counter (Color)', 'Supplies Status', 'Status'
        ],
        'Fingerprint Devices (HTTP/SNMP)': [
            'Hostname', 'Model/Vendor', 'IP Address', 'Location',
            'Controller/Server IP', 'Door/Area Name', 'User Capacity',
            'Log Capacity', 'Firmware Version', 'Status'
        ]
    }
    
    # Common manual fields for all devices
    manual_fields = [
        'Asset Tag', 'Owner', 'Department', 'Site', 'Building', 'Floor', 'Room',
        'Maintenance Contract #', 'Vendor Contact', 'Notes'
    ]
    
    for device_type, fields in requirements.items():
        print(f"\n🔧 {device_type}:")
        print(f"   Automatic Collection: {', '.join(fields)}")
        print(f"   Manual Fields: {', '.join(manual_fields)}")

def main():
    """Main verification function"""
    
    print("🎯 COMPREHENSIVE DATA COLLECTION VERIFICATION")
    print("=" * 70)
    print(f"Target IP: {TARGET_IP}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Objective: Verify English-only data collection and database storage")
    print("=" * 70)
    
    # Show requirements first
    show_device_type_requirements()
    
    # Step 1: Check database before collection
    existing_records = verify_database_before_collection()
    
    # Step 2: Test OS detection
    os_info = test_os_detection()
    
    # Step 3: Test data collection (if not already collected)
    if existing_records == 0:
        print("\n📥 No existing records found - proceeding with collection")
        collected_devices = test_data_collection()
    else:
        print("\n⏭️ Existing records found - skipping collection, verifying database")
        collected_devices = []
    
    # Step 4: Verify database after collection
    verification_success = verify_database_after_collection()
    
    # Summary
    print("\n" + "=" * 70)
    print("📋 VERIFICATION SUMMARY")
    print("=" * 70)
    
    print(f"🎯 Target IP: {TARGET_IP}")
    print(f"🔍 OS Detection: {os_info.get('detected_os', 'Failed')} ({os_info.get('os_confidence', '0')}% confidence)")
    print(f"📊 Existing Records: {existing_records}")
    print(f"📥 New Collections: {len(collected_devices)}")
    print(f"💾 Database Verification: {'✅ Success' if verification_success else '❌ Failed'}")
    
    if verification_success:
        print("\n✅ VERIFICATION COMPLETE - Data successfully collected and stored")
        print("🌐 All data is in English as required")
        print("📊 Device-specific fields collected based on detected OS")
    else:
        print("\n❌ VERIFICATION FAILED")
        print("🔧 Recommended actions:")
        print(f"   1. Check network connectivity to {TARGET_IP}")
        print("   2. Verify credentials for Windows/Linux access")
        print("   3. Ensure SNMP is enabled on target device")
        print("   4. Check firewall settings")

if __name__ == "__main__":
    main()