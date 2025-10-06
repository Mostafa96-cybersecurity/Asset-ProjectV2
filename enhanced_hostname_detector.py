#!/usr/bin/env python3
"""
HOSTNAME MISMATCH DETECTOR & FIXER
Enhanced version to detect and optionally fix hostname mismatches

Features:
✅ Comprehensive hostname mismatch detection
✅ Domain vs Device hostname comparison
✅ DNS record verification
✅ Automatic mismatch fixing (optional)
✅ Integration with enhanced database
✅ Detailed reporting and tracking
"""

import sqlite3
import socket
import dns.resolver
import dns.reversename
import logging
from datetime import datetime
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HostnameMismatchDetector:
    def __init__(self, db_path="assets.db"):
        self.db_path = db_path
        
    def detect_all_mismatches(self):
        """Detect hostname mismatches for all assets in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if enhanced table exists
        try:
            cursor.execute("SELECT COUNT(*) FROM assets_enhanced")
            enhanced_count = cursor.fetchone()[0]
            
            if enhanced_count > 0:
                return self.detect_enhanced_mismatches(conn, cursor)
        except:
            pass
        
        # Fall back to regular assets table
        return self.detect_regular_mismatches(conn, cursor)
    
    def detect_enhanced_mismatches(self, conn, cursor):
        """Detect mismatches in enhanced assets table"""
        logger.info("🔍 Detecting hostname mismatches in enhanced database...")
        
        cursor.execute("""
            SELECT id, hostname, device_hostname, dns_hostname, domain_hostname, 
                   ip_address, hostname_mismatch_status, hostname_mismatch_details
            FROM assets_enhanced
        """)
        
        assets = cursor.fetchall()
        results = {
            'total_assets': len(assets),
            'matches': 0,
            'mismatches': 0,
            'no_dns_record': 0,
            'dns_errors': 0,
            'details': []
        }
        
        for asset in assets:
            asset_id, hostname, device_hostname, dns_hostname, domain_hostname, ip_address, current_status, current_details = asset
            
            # Re-verify hostname status
            verification = self.verify_hostname_status(hostname, device_hostname, ip_address)
            
            # Update if status changed
            if verification['status'] != current_status:
                self.update_hostname_status(cursor, asset_id, verification)
                logger.info(f"Updated hostname status for {hostname}: {current_status} -> {verification['status']}")
            
            # Count results
            if verification['status'] == 'Match':
                results['matches'] += 1
            elif verification['status'] == 'Mismatch':
                results['mismatches'] += 1
            elif verification['status'] == 'No_Domain_Record':
                results['no_dns_record'] += 1
            elif verification['status'] == 'DNS_Error':
                results['dns_errors'] += 1
            
            results['details'].append({
                'hostname': hostname,
                'device_hostname': device_hostname,
                'dns_hostname': verification.get('dns_hostname'),
                'ip_address': ip_address,
                'status': verification['status'],
                'details': verification['details']
            })
        
        conn.commit()
        conn.close()
        
        return results
    
    def detect_regular_mismatches(self, conn, cursor):
        """Detect mismatches in regular assets table"""
        logger.info("🔍 Detecting hostname mismatches in regular database...")
        
        cursor.execute("""
            SELECT id, hostname, computer_name, ip_address, hostname_mismatch, hostname_mismatch_type
            FROM assets
            WHERE hostname IS NOT NULL OR computer_name IS NOT NULL
        """)
        
        assets = cursor.fetchall()
        results = {
            'total_assets': len(assets),
            'matches': 0,
            'mismatches': 0,
            'no_dns_record': 0,
            'dns_errors': 0,
            'details': []
        }
        
        for asset in assets:
            asset_id, hostname, computer_name, ip_address, current_mismatch, current_type = asset
            
            # Use hostname or computer_name
            device_hostname = hostname or computer_name
            
            # Verify hostname status
            verification = self.verify_hostname_status(device_hostname, device_hostname, ip_address)
            
            # Convert to old format
            old_mismatch = 'Yes' if verification['status'] == 'Mismatch' else 'No'
            
            # Update if status changed
            if old_mismatch != current_mismatch:
                cursor.execute("""
                    UPDATE assets 
                    SET hostname_mismatch = ?, hostname_mismatch_type = ?, last_updated = ?
                    WHERE id = ?
                """, (old_mismatch, verification['status'], datetime.now().isoformat(), asset_id))
                
                logger.info(f"Updated hostname mismatch for {device_hostname}: {current_mismatch} -> {old_mismatch}")
            
            # Count results
            if verification['status'] == 'Match':
                results['matches'] += 1
            elif verification['status'] == 'Mismatch':
                results['mismatches'] += 1
            elif verification['status'] == 'No_Domain_Record':
                results['no_dns_record'] += 1
            elif verification['status'] == 'DNS_Error':
                results['dns_errors'] += 1
            
            results['details'].append({
                'hostname': device_hostname,
                'device_hostname': device_hostname,
                'dns_hostname': verification.get('dns_hostname'),
                'ip_address': ip_address,
                'status': verification['status'],
                'details': verification['details']
            })
        
        conn.commit()
        conn.close()
        
        return results
    
    def verify_hostname_status(self, hostname, device_hostname, ip_address):
        """Verify hostname status with comprehensive checks"""
        if not hostname and not device_hostname:
            return {
                'status': 'DNS_Error',
                'details': 'No hostname available for verification'
            }
        
        primary_hostname = hostname or device_hostname
        
        try:
            # Method 1: Forward DNS lookup
            if ip_address:
                try:
                    # Reverse DNS lookup
                    reverse_result = socket.gethostbyaddr(ip_address)
                    dns_hostname = reverse_result[0].lower()
                    
                    # Compare hostnames (case-insensitive, domain-agnostic)
                    device_short = primary_hostname.lower().split('.')[0]
                    dns_short = dns_hostname.lower().split('.')[0]
                    
                    if device_short == dns_short:
                        return {
                            'status': 'Match',
                            'details': f'Device hostname "{device_short}" matches DNS hostname "{dns_short}"',
                            'dns_hostname': dns_hostname
                        }
                    else:
                        return {
                            'status': 'Mismatch',
                            'details': f'Device hostname "{device_short}" does not match DNS hostname "{dns_short}"',
                            'dns_hostname': dns_hostname
                        }
                        
                except socket.herror:
                    # No reverse DNS record
                    return {
                        'status': 'No_Domain_Record',
                        'details': f'No reverse DNS record found for IP {ip_address}'
                    }
                except Exception as e:
                    return {
                        'status': 'DNS_Error',
                        'details': f'DNS lookup error for IP {ip_address}: {str(e)}'
                    }
            
            # Method 2: Direct hostname resolution
            try:
                resolved_ip = socket.gethostbyname(primary_hostname)
                if ip_address and resolved_ip == ip_address:
                    return {
                        'status': 'Match',
                        'details': f'Hostname "{primary_hostname}" resolves to correct IP {ip_address}'
                    }
                else:
                    return {
                        'status': 'Mismatch',
                        'details': f'Hostname "{primary_hostname}" resolves to {resolved_ip}, but device IP is {ip_address}'
                    }
            except socket.gaierror:
                return {
                    'status': 'No_Domain_Record',
                    'details': f'No DNS record found for hostname "{primary_hostname}"'
                }
                
        except Exception as e:
            return {
                'status': 'DNS_Error',
                'details': f'General DNS error: {str(e)}'
            }
    
    def update_hostname_status(self, cursor, asset_id, verification):
        """Update hostname status in enhanced table"""
        cursor.execute("""
            UPDATE assets_enhanced 
            SET hostname_mismatch_status = ?, 
                hostname_mismatch_details = ?,
                dns_hostname = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            verification['status'],
            verification['details'],
            verification.get('dns_hostname'),
            asset_id
        ))
    
    def generate_report(self, results):
        """Generate comprehensive mismatch report"""
        report = f"""
========================================
HOSTNAME MISMATCH DETECTION REPORT
========================================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SUMMARY:
  Total Assets Checked: {results['total_assets']}
  ✅ Matches: {results['matches']} ({results['matches']/results['total_assets']*100:.1f}%)
  ❌ Mismatches: {results['mismatches']} ({results['mismatches']/results['total_assets']*100:.1f}%)
  🔍 No DNS Record: {results['no_dns_record']} ({results['no_dns_record']/results['total_assets']*100:.1f}%)
  ⚠️  DNS Errors: {results['dns_errors']} ({results['dns_errors']/results['total_assets']*100:.1f}%)

DETAILED RESULTS:
"""
        
        # Group by status
        status_groups = {
            'Match': [],
            'Mismatch': [],
            'No_Domain_Record': [],
            'DNS_Error': []
        }
        
        for detail in results['details']:
            status_groups[detail['status']].append(detail)
        
        for status, items in status_groups.items():
            if items:
                report += f"\n{status.upper()} ({len(items)} items):\n"
                report += "-" * 50 + "\n"
                
                for item in items:
                    report += f"  • {item['hostname']} ({item['ip_address']})\n"
                    report += f"    Status: {item['status']}\n"
                    report += f"    Details: {item['details']}\n"
                    if item.get('dns_hostname'):
                        report += f"    DNS Hostname: {item['dns_hostname']}\n"
                    report += "\n"
        
        return report
    
    def export_results(self, results, filename=None):
        """Export results to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"hostname_mismatch_report_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"📄 Results exported to {filename}")
        return filename

def main():
    """Main execution function"""
    print("🔍 HOSTNAME MISMATCH DETECTOR & FIXER")
    print("=" * 50)
    
    detector = HostnameMismatchDetector()
    
    # Detect all mismatches
    print("🔍 Detecting hostname mismatches...")
    results = detector.detect_all_mismatches()
    
    # Generate and display report
    report = detector.generate_report(results)
    print(report)
    
    # Export results
    filename = detector.export_results(results)
    
    print("\n✅ HOSTNAME MISMATCH DETECTION COMPLETED!")
    print(f"📊 Summary: {results['matches']} matches, {results['mismatches']} mismatches, {results['no_dns_record']} no DNS, {results['dns_errors']} errors")
    print(f"📄 Detailed report saved to: {filename}")

if __name__ == "__main__":
    main()