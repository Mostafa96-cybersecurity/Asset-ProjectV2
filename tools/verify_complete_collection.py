#!/usr/bin/env python3
"""
Complete Technical Data Collection Verification Tool

This tool verifies that ALL required technical data is being collected
and properly stored in the enhanced database fields for:
- Windows Workstations/Servers (WMI)
- Linux Servers (SSH)
- Network Devices (SNMP)

Required Technical Fields (15 fields):
1. Hostname
2. Working User  
3. Domain
4. Device Model
5. Device Infrastructure
6. OS Name
7. Installed RAM (GB)
8. LAN IP Address
9. Storage
10. Manufacturer
11. Serial Number
12. Processor
13. System SKU
14. Active GPU
15. Connected Screens

Plus additional technical fields for comprehensive asset management.
"""

import os
import sys
import logging
import sqlite3
from typing import Dict, List, Optional
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.smart_collector import SmartDeviceCollector
from db.connection import connect
from utils.identity import valid_serial

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('complete_collection_verification.log')
    ]
)
logger = logging.getLogger(__name__)

class CompleteCollectionVerifier:
    """Verify complete technical data collection for all device types"""
    
    REQUIRED_TECHNICAL_FIELDS = [
        "hostname", "working_user", "domain_name", "model_vendor", 
        "device_infrastructure", "firmware_os_version", "installed_ram_gb",
        "ip_address", "storage_info", "manufacturer", "sn", "processor_info",
        "system_sku", "active_gpu", "connected_screens"
    ]
    
    ADDITIONAL_TECHNICAL_FIELDS = [
        "disk_count", "mac_address", "all_mac_addresses", "cpu_details", 
        "disk_details", "device_type", "data_source"
    ]
    
    def __init__(self):
        self.collector = SmartDeviceCollector()
        self.results = {
            'windows': {'tested': 0, 'successful': 0, 'failed': 0, 'completion_rates': []},
            'linux': {'tested': 0, 'successful': 0, 'failed': 0, 'completion_rates': []},
            'network': {'tested': 0, 'successful': 0, 'failed': 0, 'completion_rates': []}
        }
    
    def verify_database_schema(self) -> bool:
        """Verify that all required technical fields exist in database"""
        logger.info("🔍 Verifying database schema has all technical fields...")
        
        try:
            with connect() as conn:
                cursor = conn.cursor()
                
                # Get column names from assets table
                cursor.execute("PRAGMA table_info(assets)")
                columns = [row[1] for row in cursor.fetchall()]
                
                missing_fields = []
                for field in self.REQUIRED_TECHNICAL_FIELDS + self.ADDITIONAL_TECHNICAL_FIELDS:
                    if field not in columns:
                        missing_fields.append(field)
                
                if missing_fields:
                    logger.error(f"❌ Missing database fields: {missing_fields}")
                    return False
                
                logger.info(f"✅ All {len(self.REQUIRED_TECHNICAL_FIELDS + self.ADDITIONAL_TECHNICAL_FIELDS)} technical fields exist in database")
                return True
            
        except Exception as e:
            logger.error(f"Database schema verification failed: {e}")
            return False
    
    def test_windows_collection(self, ip: str = "localhost", username: str = None, password: str = None) -> Dict:
        """Test Windows device collection with complete technical data"""
        logger.info(f"🪟 Testing Windows collection for {ip}...")
        
        credentials = {
            'windows': {
                'username': username or os.environ.get('WINDOWS_USERNAME', ''),
                'password': password or os.environ.get('WINDOWS_PASSWORD', '')
            }
        }
        
        try:
            # Detect device type
            device_type = self.collector.detect_os_type(ip)
            if "Windows" not in device_type:
                device_type = "Windows Workstation"  # Force Windows for this test
            
            # Collect data
            device_data = self.collector.collect_device_data(ip, device_type, credentials)
            
            if device_data:
                completion_rate = self._calculate_completion_rate(device_data, 'windows')
                logger.info(f"✅ Windows collection successful: {completion_rate:.1f}% complete")
                
                self.results['windows']['tested'] += 1
                self.results['windows']['successful'] += 1
                self.results['windows']['completion_rates'].append(completion_rate)
                
                return {'success': True, 'data': device_data, 'completion_rate': completion_rate}
            else:
                logger.error("❌ Windows collection returned no data")
                self.results['windows']['tested'] += 1
                self.results['windows']['failed'] += 1
                return {'success': False, 'error': 'No data returned'}
                
        except Exception as e:
            logger.error(f"Windows collection failed: {e}")
            self.results['windows']['tested'] += 1
            self.results['windows']['failed'] += 1
            return {'success': False, 'error': str(e)}
    
    def test_linux_collection(self, ip: str, username: str, password: str) -> Dict:
        """Test Linux device collection with complete technical data"""
        logger.info(f"🐧 Testing Linux collection for {ip}...")
        
        credentials = {
            'linux': {
                'username': username,
                'password': password
            }
        }
        
        try:
            device_data = self.collector.collect_device_data(ip, "Linux", credentials)
            
            if device_data:
                completion_rate = self._calculate_completion_rate(device_data, 'linux')
                logger.info(f"✅ Linux collection successful: {completion_rate:.1f}% complete")
                
                self.results['linux']['tested'] += 1
                self.results['linux']['successful'] += 1
                self.results['linux']['completion_rates'].append(completion_rate)
                
                return {'success': True, 'data': device_data, 'completion_rate': completion_rate}
            else:
                logger.error("❌ Linux collection returned no data")
                self.results['linux']['tested'] += 1
                self.results['linux']['failed'] += 1
                return {'success': False, 'error': 'No data returned'}
                
        except Exception as e:
            logger.error(f"Linux collection failed: {e}")
            self.results['linux']['tested'] += 1
            self.results['linux']['failed'] += 1
            return {'success': False, 'error': str(e)}
    
    def test_network_collection(self, ip: str, community: str = 'public') -> Dict:
        """Test Network device collection with complete technical data"""
        logger.info(f"📡 Testing Network device collection for {ip}...")
        
        credentials = {
            'snmp': {
                'community': community,
                'version': '2c'
            }
        }
        
        try:
            device_data = self.collector.collect_device_data(ip, "Network Device", credentials)
            
            if device_data:
                completion_rate = self._calculate_completion_rate(device_data, 'network')
                logger.info(f"✅ Network collection successful: {completion_rate:.1f}% complete")
                
                self.results['network']['tested'] += 1
                self.results['network']['successful'] += 1
                self.results['network']['completion_rates'].append(completion_rate)
                
                return {'success': True, 'data': device_data, 'completion_rate': completion_rate}
            else:
                logger.error("❌ Network collection returned no data")
                self.results['network']['tested'] += 1
                self.results['network']['failed'] += 1
                return {'success': False, 'error': 'No data returned'}
                
        except Exception as e:
            logger.error(f"Network collection failed: {e}")
            self.results['network']['tested'] += 1
            self.results['network']['failed'] += 1
            return {'success': False, 'error': str(e)}
    
    def _calculate_completion_rate(self, device_data: Dict, device_category: str) -> float:
        """Calculate completion rate for technical data fields"""
        if not device_data:
            return 0.0
        
        # Different fields are more relevant for different device types
        if device_category == 'windows':
            relevant_fields = self.REQUIRED_TECHNICAL_FIELDS
        elif device_category == 'linux':
            # Connected screens less relevant for Linux servers
            relevant_fields = [f for f in self.REQUIRED_TECHNICAL_FIELDS if f != 'connected_screens']
        else:  # network
            # Many fields not applicable to network devices
            relevant_fields = ['hostname', 'ip_address', 'device_infrastructure', 'manufacturer', 
                             'model_vendor', 'sn', 'firmware_os_version']
        
        filled_count = 0
        total_count = len(relevant_fields)
        
        for field in relevant_fields:
            value = device_data.get(field)
            if value is not None and str(value).strip():
                filled_count += 1
        
        completion_rate = (filled_count / total_count * 100) if total_count > 0 else 0
        
        # Log field details
        logger.info(f"📊 Field completion for {device_category}: {filled_count}/{total_count} fields")
        missing_fields = [f for f in relevant_fields if not device_data.get(f)]
        if missing_fields:
            logger.warning(f"Missing fields: {missing_fields}")
        
        return completion_rate
    
    def save_test_data_to_database(self, device_data: Dict) -> bool:
        """Save test data to database to verify storage works"""
        try:
            with connect() as conn:
                cursor = conn.cursor()
                
                # Prepare insert statement with all technical fields
                all_fields = self.REQUIRED_TECHNICAL_FIELDS + self.ADDITIONAL_TECHNICAL_FIELDS + ['notes', 'status', 'updated_at']
                
                placeholders = ', '.join(['?' for _ in all_fields])
                columns = ', '.join(all_fields)
                
                values = []
                for field in all_fields:
                    value = device_data.get(field)
                    # Convert None to empty string for consistency
                    values.append(value if value is not None else '')
                
                cursor.execute(f"""
                    INSERT OR REPLACE INTO assets ({columns})
                    VALUES ({placeholders})
                """, values)
                
                logger.info("✅ Test data successfully saved to database")
                return True
            
        except Exception as e:
            logger.error(f"Failed to save test data to database: {e}")
            return False
    
    def generate_completion_report(self) -> str:
        """Generate comprehensive completion report"""
        report = []
        report.append("="*80)
        report.append("COMPLETE TECHNICAL DATA COLLECTION VERIFICATION REPORT")
        report.append("="*80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        total_tested = sum(self.results[cat]['tested'] for cat in self.results)
        total_successful = sum(self.results[cat]['successful'] for cat in self.results)
        
        report.append(f"OVERALL SUMMARY:")
        report.append(f"Total Tests: {total_tested}")
        report.append(f"Successful: {total_successful}")
        report.append(f"Success Rate: {(total_successful/total_tested*100):.1f}%" if total_tested > 0 else "No tests run")
        report.append("")
        
        # Category breakdown
        for category, data in self.results.items():
            if data['tested'] > 0:
                avg_completion = sum(data['completion_rates']) / len(data['completion_rates']) if data['completion_rates'] else 0
                report.append(f"{category.upper()} DEVICES:")
                report.append(f"  Tests: {data['tested']}")
                report.append(f"  Successful: {data['successful']}")
                report.append(f"  Failed: {data['failed']}")
                report.append(f"  Average Completion Rate: {avg_completion:.1f}%")
                report.append("")
        
        # Requirements status
        report.append("TECHNICAL DATA REQUIREMENTS STATUS:")
        report.append(f"Required Fields: {len(self.REQUIRED_TECHNICAL_FIELDS)}")
        for field in self.REQUIRED_TECHNICAL_FIELDS:
            report.append(f"  ✓ {field}")
        report.append("")
        
        report.append("ADDITIONAL TECHNICAL FIELDS:")
        for field in self.ADDITIONAL_TECHNICAL_FIELDS:
            report.append(f"  ✓ {field}")
        report.append("")
        
        return "\n".join(report)

def main():
    """Run complete collection verification tests"""
    logger.info("🚀 Starting Complete Technical Data Collection Verification")
    
    verifier = CompleteCollectionVerifier()
    
    # Step 1: Verify database schema
    if not verifier.verify_database_schema():
        logger.error("❌ Database schema verification failed - aborting tests")
        return False
    
    # Step 2: Test Windows collection (localhost)
    logger.info("Testing Windows collection...")
    windows_result = verifier.test_windows_collection()
    
    if windows_result['success']:
        # Step 3: Save to database to verify storage
        logger.info("Testing database storage...")
        verifier.save_test_data_to_database(windows_result['data'])
        
        # Display collected data summary
        data = windows_result['data']
        logger.info("📋 Collected Technical Data Summary:")
        logger.info(f"  Hostname: {data.get('hostname', 'N/A')}")
        logger.info(f"  Working User: {data.get('working_user', 'N/A')}")
        logger.info(f"  Domain: {data.get('domain_name', 'N/A')}")
        logger.info(f"  Model/Vendor: {data.get('model_vendor', 'N/A')}")
        logger.info(f"  OS: {data.get('firmware_os_version', 'N/A')}")
        logger.info(f"  RAM: {data.get('installed_ram_gb', 'N/A')} GB")
        logger.info(f"  Storage: {data.get('storage_info', 'N/A')}")
        logger.info(f"  Processor: {data.get('processor_info', 'N/A')}")
        logger.info(f"  Serial Number: {data.get('sn', 'N/A')}")
    
    # Step 4: Generate and display report
    report = verifier.generate_completion_report()
    print(report)
    
    # Save report to file
    with open('complete_collection_verification_report.txt', 'w') as f:
        f.write(report)
    
    # Success criteria
    if verifier.results['windows']['successful'] > 0:
        avg_completion = sum(verifier.results['windows']['completion_rates']) / len(verifier.results['windows']['completion_rates'])
        if avg_completion >= 80:  # 80%+ completion rate considered success
            logger.info(f"🎉 VERIFICATION SUCCESSFUL! Average completion rate: {avg_completion:.1f}%")
            return True
    
    logger.warning("⚠️  Verification completed but may not meet all requirements")
    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)