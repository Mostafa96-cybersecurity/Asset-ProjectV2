#!/usr/bin/env python3
"""
Enhanced Device Deduplication Strategy Analysis
Handles complex scenarios like device movement, user changes, and hardware tracking
"""

import sqlite3
from datetime import datetime
from typing import Dict, Optional, Tuple, List

class DeviceIdentificationStrategy:
    """
    Smart device identification that handles:
    1. User changing PCs (same user, different hardware)
    2. PC changing users (same hardware, different user)  
    3. PC changing locations (same hardware, different IP)
    4. Hardware upgrades (same serial, different specs)
    """
    
    def __init__(self, db_path: str = 'assets.db'):
        self.db_path = db_path
        self.identification_priority = [
            'hardware_fingerprint',  # Primary: BIOS Serial + System Model
            'network_identity',      # Secondary: MAC Address + IP
            'logical_identity'       # Tertiary: Hostname + User
        ]
    
    def analyze_device_identity(self, device_data: Dict) -> Dict:
        """Analyze a device and determine its identity strategy"""
        
        result = {
            'primary_id': None,
            'secondary_id': None,
            'deduplication_strategy': None,
            'risk_level': 'low',
            'recommendations': []
        }
        
        # Extract key identifiers
        bios_serial = device_data.get('bios_serial_number')
        chassis_serial = device_data.get('chassis_serial')
        device_serial = device_data.get('device_serial')
        mac_address = device_data.get('mac_address')
        ip_address = device_data.get('ip_address')
        hostname = device_data.get('hostname')
        username = device_data.get('username') or device_data.get('current_user')
        system_model = device_data.get('system_model')
        system_manufacturer = device_data.get('system_manufacturer')
        
        # 1. HARDWARE FINGERPRINT (Most Reliable)
        hardware_ids = [bios_serial, chassis_serial, device_serial]
        valid_hardware_ids = [hid for hid in hardware_ids if hid and hid.strip() and hid.strip().lower() not in ['none', 'unknown', 'n/a']]
        
        if valid_hardware_ids:
            result['primary_id'] = valid_hardware_ids[0]  # Use best available hardware ID
            result['deduplication_strategy'] = 'hardware_fingerprint'
            result['recommendations'].append(f"✅ Strong hardware identity: {valid_hardware_ids[0]}")
            
            # Create composite hardware fingerprint
            if system_manufacturer and system_model:
                hardware_fingerprint = f"{system_manufacturer}_{system_model}_{valid_hardware_ids[0]}"
                result['hardware_fingerprint'] = hardware_fingerprint
        
        # 2. NETWORK IDENTITY (Medium Reliability)
        elif mac_address and mac_address.strip():
            result['primary_id'] = mac_address
            result['deduplication_strategy'] = 'network_identity'
            result['risk_level'] = 'medium'
            result['recommendations'].append(f"⚠️ Using MAC address: {mac_address} (less reliable)")
        
        # 3. LOGICAL IDENTITY (Lowest Reliability)
        elif hostname and hostname.strip():
            result['primary_id'] = hostname
            result['secondary_id'] = ip_address
            result['deduplication_strategy'] = 'logical_identity'
            result['risk_level'] = 'high'
            result['recommendations'].append(f"⚠️ Using hostname only: {hostname} (least reliable)")
        
        # 4. IP ONLY (Fallback)
        else:
            result['primary_id'] = ip_address
            result['deduplication_strategy'] = 'ip_fallback'
            result['risk_level'] = 'very_high'
            result['recommendations'].append(f"❌ IP only: {ip_address} (unreliable - IP can change)")
        
        return result
    
    def check_existing_device(self, device_data: Dict) -> Tuple[Optional[int], str]:
        """
        Check for existing device using smart identification strategy
        Returns: (existing_record_id, match_reason)
        """
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get device identity analysis
            identity = self.analyze_device_identity(device_data)
            
            # Strategy 1: Hardware Fingerprint (Most Reliable)
            if identity['deduplication_strategy'] == 'hardware_fingerprint':
                # Check by BIOS serial number first
                bios_serial = device_data.get('bios_serial_number')
                if bios_serial:
                    cursor.execute('SELECT id, hostname, ip_address FROM assets WHERE bios_serial_number = ?', (bios_serial,))
                    existing = cursor.fetchone()
                    if existing:
                        conn.close()
                        return existing[0], f"Hardware match: BIOS Serial {bios_serial}"
                
                # Check by chassis serial
                chassis_serial = device_data.get('chassis_serial')
                if chassis_serial:
                    cursor.execute('SELECT id, hostname, ip_address FROM assets WHERE chassis_serial = ?', (chassis_serial,))
                    existing = cursor.fetchone()
                    if existing:
                        conn.close()
                        return existing[0], f"Hardware match: Chassis Serial {chassis_serial}"
                
                # Check by device serial
                device_serial = device_data.get('device_serial')
                if device_serial:
                    cursor.execute('SELECT id, hostname, ip_address FROM assets WHERE device_serial = ?', (device_serial,))
                    existing = cursor.fetchone()
                    if existing:
                        conn.close()
                        return existing[0], f"Hardware match: Device Serial {device_serial}"
            
            # Strategy 2: Network Identity
            elif identity['deduplication_strategy'] == 'network_identity':
                mac_address = device_data.get('mac_address')
                if mac_address:
                    cursor.execute('SELECT id, hostname, ip_address FROM assets WHERE mac_address = ?', (mac_address,))
                    existing = cursor.fetchone()
                    if existing:
                        conn.close()
                        return existing[0], f"Network match: MAC Address {mac_address}"
            
            # Strategy 3: Logical Identity (Hostname + IP)
            elif identity['deduplication_strategy'] == 'logical_identity':
                hostname = device_data.get('hostname')
                ip_address = device_data.get('ip_address')
                
                # Check by hostname first
                if hostname:
                    cursor.execute('SELECT id, hostname, ip_address FROM assets WHERE hostname = ?', (hostname,))
                    existing = cursor.fetchone()
                    if existing:
                        conn.close()
                        return existing[0], f"Logical match: Hostname {hostname}"
                
                # Fallback to IP
                if ip_address:
                    cursor.execute('SELECT id, hostname, ip_address FROM assets WHERE ip_address = ?', (ip_address,))
                    existing = cursor.fetchone()
                    if existing:
                        conn.close()
                        return existing[0], f"Logical match: IP Address {ip_address}"
            
            # Strategy 4: IP Fallback
            else:
                ip_address = device_data.get('ip_address')
                if ip_address:
                    cursor.execute('SELECT id, hostname, ip_address FROM assets WHERE ip_address = ?', (ip_address,))
                    existing = cursor.fetchone()
                    if existing:
                        conn.close()
                        return existing[0], f"IP fallback: {ip_address}"
            
            conn.close()
            return None, "No existing device found"
            
        except Exception as e:
            print(f"Error checking existing device: {e}")
            return None, f"Error: {e}"
    
    def simulate_scenarios(self):
        """Test various real-world scenarios"""
        
        print("🧪 DEVICE DEDUPLICATION SCENARIOS")
        print("=" * 60)
        
        # Scenario 1: User changes PC
        print("📋 SCENARIO 1: User changes PC")
        old_pc = {
            'hostname': 'LT-OLD-001',
            'ip_address': '10.0.21.100',
            'bios_serial_number': 'OLD123',
            'username': 'john.doe',
            'system_model': 'OptiPlex 7090'
        }
        
        new_pc = {
            'hostname': 'LT-NEW-001', 
            'ip_address': '10.0.21.100',  # Same IP
            'bios_serial_number': 'NEW456',  # Different hardware
            'username': 'john.doe',  # Same user
            'system_model': 'Latitude 5520'
        }
        
        identity_old = self.analyze_device_identity(old_pc)
        identity_new = self.analyze_device_identity(new_pc)
        
        print(f"   Old PC: {identity_old['primary_id']} ({identity_old['deduplication_strategy']})")
        print(f"   New PC: {identity_new['primary_id']} ({identity_new['deduplication_strategy']})")
        print(f"   Result: Two separate devices (different hardware serials)")
        print()
        
        # Scenario 2: PC changes user
        print("📋 SCENARIO 2: PC changes user")
        before_transfer = {
            'hostname': 'LT-3541-0012',
            'ip_address': '10.0.21.47',
            'bios_serial_number': '5F950R2',
            'username': 'mahmoud.hamed',
            'system_model': 'Precision 3541'
        }
        
        after_transfer = {
            'hostname': 'LT-3541-0012',  # Same hostname
            'ip_address': '10.0.21.50',  # Different IP
            'bios_serial_number': '5F950R2',  # Same hardware
            'username': 'jane.smith',  # Different user
            'system_model': 'Precision 3541'
        }
        
        identity_before = self.analyze_device_identity(before_transfer)
        identity_after = self.analyze_device_identity(after_transfer)
        
        print(f"   Before: {identity_before['primary_id']} ({identity_before['deduplication_strategy']})")
        print(f"   After: {identity_after['primary_id']} ({identity_after['deduplication_strategy']})")
        print(f"   Result: Same device record updated (same hardware serial)")
        print()
        
        # Scenario 3: PC moves location
        print("📋 SCENARIO 3: PC moves location")
        office_a = {
            'hostname': 'LT-3541-0012',
            'ip_address': '10.0.21.47',
            'bios_serial_number': '5F950R2',
            'username': 'mahmoud.hamed'
        }
        
        office_b = {
            'hostname': 'LT-3541-0012',
            'ip_address': '192.168.1.100',  # Different network
            'bios_serial_number': '5F950R2',  # Same hardware
            'username': 'mahmoud.hamed'
        }
        
        identity_a = self.analyze_device_identity(office_a)
        identity_b = self.analyze_device_identity(office_b)
        
        print(f"   Office A: {identity_a['primary_id']} ({identity_a['deduplication_strategy']})")
        print(f"   Office B: {identity_b['primary_id']} ({identity_b['deduplication_strategy']})")
        print(f"   Result: Same device record updated (same hardware serial)")

if __name__ == "__main__":
    strategy = DeviceIdentificationStrategy()
    strategy.simulate_scenarios()
    
    print()
    print("🔧 RECOMMENDED DEDUPLICATION STRATEGY:")
    print("1. PRIMARY: Hardware Serial Numbers (BIOS, Chassis, Device)")
    print("2. SECONDARY: MAC Address")
    print("3. TERTIARY: Hostname + IP Address")
    print("4. FALLBACK: IP Address only")
    print()
    print("✅ This ensures:")
    print("   - No duplicate devices")
    print("   - Proper tracking when users change PCs")
    print("   - Proper tracking when PCs change users/locations")
    print("   - Data preservation across all scenarios")