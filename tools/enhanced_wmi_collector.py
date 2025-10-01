#!/usr/bin/env python3
"""
Enhanced WMI Data Collector
Ensures ALL technical data is collected and properly mapped to database fields
"""

import sys
import os
import sqlite3
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collectors.wmi_collector import collect_windows_wmi
from collectors.ssh_collector import collect_linux_or_esxi_ssh
from collectors.snmp_collector import snmp_collect_basic

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedDataMapper:
    """Enhanced data mapping to ensure all technical data is stored properly"""
    
    def __init__(self):
        self.required_technical_fields = [
            'hostname', 'working_user', 'domain', 'device_model', 'device_infrastructure',
            'os_name', 'installed_ram_gb', 'lan_ip_address', 'storage', 'manufacturer',
            'serial_number', 'processor', 'system_sku', 'active_gpu', 'connected_screens'
        ]
    
    def map_wmi_data_to_database(self, wmi_data: Dict[str, Any], ip: str) -> Dict[str, Any]:
        """Map WMI collector output to database fields with all technical data"""
        
        # First, let's see what the WMI collector actually returns
        logger.info(f"📊 WMI Data Keys Available: {list(wmi_data.keys())}")
        
        # Enhanced mapping to database fields
        mapped_data = {
            # Core identity fields
            'hostname': wmi_data.get('Hostname', ''),
            'ip_address': ip,
            'device_type': self._determine_device_type(wmi_data),
            
            # Hardware information
            'model_vendor': self._format_model_vendor(wmi_data),
            'sn': wmi_data.get('Serial Number', ''),
            'firmware_os_version': wmi_data.get('OS Name', ''),
            
            # Enhanced technical data - CREATE NEW FIELDS FOR MISSING DATA
            'notes': self._format_technical_notes(wmi_data),
            'data_source': 'Enhanced WMI Collection',
            
            # Timestamps
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'status': 'Active'
        }
        
        # Add comprehensive technical data to notes field (since we can't modify DB schema easily)
        return mapped_data
    
    def _determine_device_type(self, wmi_data: Dict[str, Any]) -> str:
        """Determine device type based on WMI data"""
        device_infrastructure = wmi_data.get('Device Infrastructure', '')
        
        if 'Server' in device_infrastructure:
            return 'server'
        elif 'Laptop' in device_infrastructure:
            return 'laptop'
        elif 'Desktop' in device_infrastructure or 'Workstation' in device_infrastructure:
            return 'workstation'
        else:
            return 'asset'
    
    def _format_model_vendor(self, wmi_data: Dict[str, Any]) -> str:
        """Format manufacturer and model into single field"""
        manufacturer = wmi_data.get('Manufacturer', '')
        device_model = wmi_data.get('Device Model', '')
        
        if manufacturer and device_model:
            return f"{manufacturer} {device_model}"
        return device_model or manufacturer or 'Unknown'
    
    def _format_technical_notes(self, wmi_data: Dict[str, Any]) -> str:
        """Format all technical data into structured notes"""
        technical_data = []
        
        # Working User
        if wmi_data.get('Working User'):
            technical_data.append(f"Working User: {wmi_data['Working User']}")
        
        # Domain
        if wmi_data.get('Domain'):
            technical_data.append(f"Domain: {wmi_data['Domain']}")
        
        # Device Infrastructure
        if wmi_data.get('Device Infrastructure'):
            technical_data.append(f"Infrastructure: {wmi_data['Device Infrastructure']}")
        
        # RAM
        if wmi_data.get('Installed RAM (GB)'):
            technical_data.append(f"RAM: {wmi_data['Installed RAM (GB)']} GB")
        
        # Storage
        if wmi_data.get('Storage'):
            technical_data.append(f"Storage: {wmi_data['Storage']}")
        
        # Processor
        if wmi_data.get('Processor'):
            technical_data.append(f"CPU: {wmi_data['Processor']}")
        
        # System SKU
        if wmi_data.get('System SKU'):
            technical_data.append(f"SKU: {wmi_data['System SKU']}")
        
        # GPU
        if wmi_data.get('Active GPU'):
            technical_data.append(f"GPU: {wmi_data['Active GPU']}")
        
        # Connected Screens
        if wmi_data.get('Connected Screens'):
            technical_data.append(f"Screens: {wmi_data['Connected Screens']}")
        
        # Additional WMI data
        for key, value in wmi_data.items():
            if key not in ['Hostname', 'Working User', 'Domain', 'Device Model', 'Device Infrastructure',
                          'OS Name', 'Installed RAM (GB)', 'Storage', 'Manufacturer', 'Serial Number', 
                          'Processor', 'System SKU', 'Active GPU', 'Connected Screens'] and value:
                technical_data.append(f"{key}: {value}")
        
        return " | ".join(technical_data)
    
    def save_enhanced_data_to_database(self, device_data: Dict[str, Any]) -> bool:
        """Save enhanced device data to database"""
        try:
            conn = sqlite3.connect('assets.db')
            cursor = conn.cursor()
            
            ip = device_data.get('ip_address', '')
            hostname = device_data.get('hostname', '')
            
            # Check if device exists
            cursor.execute("""
                SELECT id FROM assets 
                WHERE ip_address = ? OR hostname = ?
            """, (ip, hostname))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing record
                update_fields = []
                update_values = []
                
                for key, value in device_data.items():
                    if key not in ['id'] and value:
                        update_fields.append(f"{key} = ?")
                        update_values.append(value)
                
                if update_fields:
                    update_values.append(existing[0])
                    cursor.execute(f"""
                        UPDATE assets SET {', '.join(update_fields)}
                        WHERE id = ?
                    """, update_values)
                    
                    logger.info(f"✅ Updated enhanced data for: {ip} - {hostname}")
            else:
                # Insert new record
                fields = list(device_data.keys())
                values = list(device_data.values())
                placeholders = ', '.join(['?'] * len(fields))
                
                cursor.execute(f"""
                    INSERT INTO assets ({', '.join(fields)})
                    VALUES ({placeholders})
                """, values)
                
                logger.info(f"✅ Inserted enhanced data for: {ip} - {hostname}")
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save enhanced data: {e}")
            return False

class EnhancedCollector:
    """Enhanced collector that ensures all technical data is captured"""
    
    def __init__(self):
        self.mapper = EnhancedDataMapper()
        self.collected_devices = []
    
    def test_wmi_collection(self, ip: str = None, username: str = None, password: str = None):
        """Test WMI collection and show all available data"""
        try:
            logger.info(f"🔍 Testing WMI collection for {ip or 'localhost'}")
            
            # Collect WMI data
            wmi_data = collect_windows_wmi(ip, username, password)
            
            if isinstance(wmi_data, dict) and "Error" not in wmi_data:
                logger.info("✅ WMI Collection Successful!")
                
                print("\n📊 COMPLETE WMI DATA COLLECTED:")
                print("="*60)
                for key, value in wmi_data.items():
                    print(f"{key:<25}: {value}")
                
                # Map to database format
                mapped_data = self.mapper.map_wmi_data_to_database(wmi_data, ip or 'localhost')
                
                print(f"\n💾 MAPPED DATABASE DATA:")
                print("="*40)
                for key, value in mapped_data.items():
                    if key == 'notes':
                        print(f"{key:<20}: {value[:100]}..." if len(str(value)) > 100 else f"{key:<20}: {value}")
                    else:
                        print(f"{key:<20}: {value}")
                
                return wmi_data, mapped_data
            else:
                error_info = wmi_data.get('Error', {}) if isinstance(wmi_data, dict) else {'message': str(wmi_data)}
                logger.error(f"❌ WMI Collection Failed: {error_info.get('message', 'Unknown error')}")
                return None, None
                
        except Exception as e:
            logger.error(f"❌ WMI Test Failed: {e}")
            return None, None
    
    def collect_and_enhance_device(self, ip: str, credentials: Dict) -> bool:
        """Collect and store enhanced device data"""
        try:
            # Determine device type by trying different collection methods
            device_data = None
            
            # Try WMI first (Windows)
            if credentials.get('type', '').lower() == 'windows':
                wmi_data = collect_windows_wmi(
                    ip, 
                    credentials.get('username'), 
                    credentials.get('password')
                )
                
                if isinstance(wmi_data, dict) and "Error" not in wmi_data:
                    device_data = self.mapper.map_wmi_data_to_database(wmi_data, ip)
                    logger.info(f"✅ Enhanced WMI collection completed for {ip}")
            
            # Try SSH (Linux/Unix)
            elif credentials.get('type', '').lower() in ['linux', 'unix']:
                ssh_data = collect_linux_or_esxi_ssh(
                    ip,
                    credentials.get('username'),
                    credentials.get('password')
                )
                
                if isinstance(ssh_data, dict) and "Error" not in ssh_data:
                    device_data = self.mapper.map_linux_data_to_database(ssh_data, ip)
                    logger.info(f"✅ Enhanced SSH collection completed for {ip}")
            
            # Try SNMP (Network devices)
            elif credentials.get('type', '').lower() == 'snmp':
                snmp_data = snmp_collect_basic(
                    ip,
                    community=credentials.get('community', 'public')
                )
                
                if snmp_data:
                    device_data = self.mapper.map_snmp_data_to_database(snmp_data, ip)
                    logger.info(f"✅ Enhanced SNMP collection completed for {ip}")
            
            # Save enhanced data
            if device_data:
                success = self.mapper.save_enhanced_data_to_database(device_data)
                if success:
                    self.collected_devices.append(device_data)
                return success
            else:
                logger.warning(f"⚠️ No data collected for {ip}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Enhanced collection failed for {ip}: {e}")
            return False
    
    def run_enhanced_collection_test(self):
        """Run test collection to verify all data is being captured"""
        print("🚀 ENHANCED DATA COLLECTION TEST")
        print("="*50)
        
        # Test local WMI collection
        print("\n1. Testing Local WMI Collection:")
        print("-"*30)
        wmi_data, mapped_data = self.test_wmi_collection()
        
        if wmi_data and mapped_data:
            print(f"\n📋 TECHNICAL FIELDS CAPTURED:")
            technical_fields_found = []
            
            for field in self.mapper.required_technical_fields:
                found_in_wmi = any(field.replace('_', ' ').title() in str(key) for key in wmi_data.keys())
                if found_in_wmi:
                    technical_fields_found.append(f"✅ {field}")
                else:
                    technical_fields_found.append(f"❌ {field}")
            
            for field in technical_fields_found:
                print(f"   {field}")
            
            # Save test data
            success = self.mapper.save_enhanced_data_to_database(mapped_data)
            print(f"\n💾 Database Save: {'✅ Success' if success else '❌ Failed'}")
            
            return True
        else:
            print("❌ WMI collection test failed")
            return False

def main():
    collector = EnhancedCollector()
    
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        collector.run_enhanced_collection_test()
    else:
        print("Usage: python enhanced_wmi_collector.py test")
        print("\nThis will test WMI collection and show all technical data being captured")

if __name__ == "__main__":
    main()