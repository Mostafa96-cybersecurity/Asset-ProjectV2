#!/usr/bin/env python3
"""
Comprehensive Database Analysis - Check all data quality and collection status
"""

import sqlite3
import json
from datetime import datetime

def comprehensive_database_analysis():
    print("🔍 COMPREHENSIVE DATABASE ANALYSIS")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect('assets.db')
        cursor = conn.cursor()
        
        # 1. Basic Statistics
        print("📊 BASIC DATABASE STATISTICS")
        print("-" * 40)
        
        cursor.execute("SELECT COUNT(*) FROM assets")
        total_assets = cursor.fetchone()[0]
        print(f"📱 Total Assets: {total_assets}")
        
        cursor.execute("SELECT COUNT(*) FROM security_events")
        security_events = cursor.fetchone()[0]
        print(f"🚨 Security Events: {security_events}")
        
        cursor.execute("SELECT COUNT(*) FROM network_ranges")
        network_ranges = cursor.fetchone()[0]
        print(f"🌐 Network Ranges: {network_ranges}")
        
        # 2. Recent Activity Analysis
        print("\n⏰ RECENT ACTIVITY ANALYSIS")
        print("-" * 40)
        
        # Check last hour
        cursor.execute("""
            SELECT COUNT(*) FROM assets 
            WHERE last_updated > datetime('now', '-1 hour')
        """)
        last_hour = cursor.fetchone()[0]
        print(f"🕐 Updated in last hour: {last_hour}")
        
        # Check last 30 minutes
        cursor.execute("""
            SELECT COUNT(*) FROM assets 
            WHERE last_updated > datetime('now', '-30 minutes')
        """)
        last_30min = cursor.fetchone()[0]
        print(f"🕕 Updated in last 30 minutes: {last_30min}")
        
        # Check last 10 minutes
        cursor.execute("""
            SELECT COUNT(*) FROM assets 
            WHERE last_updated > datetime('now', '-10 minutes')
        """)
        last_10min = cursor.fetchone()[0]
        print(f"🕙 Updated in last 10 minutes: {last_10min}")
        
        # 3. Collection Methods Analysis
        print("\n🔧 COLLECTION METHODS ANALYSIS")
        print("-" * 40)
        
        cursor.execute("""
            SELECT collection_method, COUNT(*) 
            FROM assets 
            WHERE collection_method IS NOT NULL
            GROUP BY collection_method
            ORDER BY COUNT(*) DESC
        """)
        methods = cursor.fetchall()
        
        total_with_method = sum(count for _, count in methods)
        
        for method, count in methods:
            percentage = (count / total_with_method * 100) if total_with_method > 0 else 0
            print(f"   • {method}: {count} devices ({percentage:.1f}%)")
        
        cursor.execute("SELECT COUNT(*) FROM assets WHERE collection_method IS NULL")
        no_method = cursor.fetchone()[0]
        print(f"   • No Method: {no_method} devices")
        
        # 4. Device Classification Analysis
        print("\n🏷️ DEVICE CLASSIFICATION ANALYSIS")
        print("-" * 40)
        
        cursor.execute("""
            SELECT classification, COUNT(*) 
            FROM assets 
            WHERE classification IS NOT NULL
            GROUP BY classification
            ORDER BY COUNT(*) DESC
        """)
        classifications = cursor.fetchall()
        
        total_classified = sum(count for _, count in classifications)
        
        for classification, count in classifications:
            percentage = (count / total_classified * 100) if total_classified > 0 else 0
            print(f"   • {classification}: {count} devices ({percentage:.1f}%)")
        
        cursor.execute("SELECT COUNT(*) FROM assets WHERE classification IS NULL")
        unclassified = cursor.fetchone()[0]
        print(f"   • Unclassified: {unclassified} devices")
        
        # 5. Data Quality Analysis
        print("\n📈 DATA QUALITY ANALYSIS")
        print("-" * 40)
        
        # Check for devices with detailed info
        cursor.execute("""
            SELECT COUNT(*) FROM assets 
            WHERE operating_system IS NOT NULL AND operating_system != 'Unknown'
        """)
        with_os = cursor.fetchone()[0]
        print(f"🖥️ Devices with OS info: {with_os} ({with_os/total_assets*100:.1f}%)")
        
        cursor.execute("""
            SELECT COUNT(*) FROM assets 
            WHERE hostname IS NOT NULL AND hostname != '' AND hostname != ip_address
        """)
        with_hostname = cursor.fetchone()[0]
        print(f"🏷️ Devices with hostname: {with_hostname} ({with_hostname/total_assets*100:.1f}%)")
        
        cursor.execute("""
            SELECT COUNT(*) FROM assets 
            WHERE manufacturer IS NOT NULL AND manufacturer != 'Unknown'
        """)
        with_manufacturer = cursor.fetchone()[0]
        print(f"🏭 Devices with manufacturer: {with_manufacturer} ({with_manufacturer/total_assets*100:.1f}%)")
        
        cursor.execute("""
            SELECT COUNT(*) FROM assets 
            WHERE processor IS NOT NULL AND processor != ''
        """)
        with_processor = cursor.fetchone()[0]
        print(f"⚙️ Devices with processor info: {with_processor} ({with_processor/total_assets*100:.1f}%)")
        
        cursor.execute("""
            SELECT COUNT(*) FROM assets 
            WHERE installed_ram_gb IS NOT NULL AND installed_ram_gb > 0
        """)
        with_ram = cursor.fetchone()[0]
        print(f"💾 Devices with RAM info: {with_ram} ({with_ram/total_assets*100:.1f}%)")
        
        # 6. Network Coverage Analysis
        print("\n🌐 NETWORK COVERAGE ANALYSIS")
        print("-" * 40)
        
        cursor.execute("""
            SELECT SUBSTR(ip_address, 1, INSTR(ip_address||'.', '.', INSTR(ip_address||'.', '.', INSTR(ip_address||'.', '.')+1)+1)-1) as network,
                   COUNT(*) as device_count
            FROM assets 
            WHERE ip_address IS NOT NULL AND ip_address LIKE '%.%.%.%'
            GROUP BY network
            ORDER BY device_count DESC
            LIMIT 10
        """)
        networks = cursor.fetchall()
        
        print("Top 10 networks by device count:")
        for network, count in networks:
            print(f"   • {network}.x: {count} devices")
        
        # 7. Most Recent Devices
        print("\n🆕 MOST RECENTLY UPDATED DEVICES")
        print("-" * 40)
        
        cursor.execute("""
            SELECT hostname, ip_address, classification, operating_system, last_updated, collection_method
            FROM assets 
            ORDER BY last_updated DESC
            LIMIT 10
        """)
        recent_devices = cursor.fetchall()
        
        for i, (hostname, ip, classification, os, updated, method) in enumerate(recent_devices, 1):
            hostname = hostname or ip or "Unknown"
            classification = classification or "Unknown"
            os = os or "Unknown"
            method = method or "Unknown"
            print(f"   {i:2d}. {hostname} ({ip})")
            print(f"       Type: {classification} | OS: {os}")
            print(f"       Updated: {updated} | Method: {method}")
            print()
        
        # 8. Database Health Check
        print("\n🏥 DATABASE HEALTH CHECK")
        print("-" * 40)
        
        # Check for duplicate IPs
        cursor.execute("""
            SELECT ip_address, COUNT(*) 
            FROM assets 
            WHERE ip_address IS NOT NULL 
            GROUP BY ip_address 
            HAVING COUNT(*) > 1
        """)
        duplicates = cursor.fetchall()
        
        if duplicates:
            print(f"⚠️ Duplicate IP addresses found: {len(duplicates)}")
            for ip, count in duplicates[:5]:  # Show first 5
                print(f"   • {ip}: {count} entries")
        else:
            print("✅ No duplicate IP addresses found")
        
        # Check data completeness
        cursor.execute("""
            SELECT COUNT(*) FROM assets 
            WHERE ip_address IS NULL OR ip_address = ''
        """)
        no_ip = cursor.fetchone()[0]
        
        if no_ip > 0:
            print(f"⚠️ Devices without IP address: {no_ip}")
        else:
            print("✅ All devices have IP addresses")
        
        conn.close()
        
        # 9. Summary and Recommendations
        print("\n📋 SUMMARY AND RECOMMENDATIONS")
        print("=" * 40)
        
        print(f"📊 Database Size: {total_assets} assets")
        print(f"📈 Data Quality: {(with_hostname + with_os + with_manufacturer) / (total_assets * 3) * 100:.1f}% complete")
        print(f"🔧 Collection Coverage: {total_with_method}/{total_assets} devices have collection methods")
        print(f"🏷️ Classification: {total_classified}/{total_assets} devices classified")
        
        if last_10min > 0:
            print(f"✅ Recent activity detected: {last_10min} devices updated in last 10 minutes")
        elif last_hour > 0:
            print(f"⏰ Some recent activity: {last_hour} devices updated in last hour")
        else:
            print("⚠️ No recent updates detected - scan may not have completed")
        
        print("\n💡 Recommendations:")
        if total_assets < 400:
            print("   • Run asset scan to discover more devices (expected: 560+ devices)")
        if unclassified > total_assets * 0.2:
            print("   • Improve device classification (many unclassified devices)")
        if no_method > total_assets * 0.3:
            print("   • Enhance collection methods for better data gathering")
        
        # Save analysis report
        report = {
            "analysis_date": datetime.now().isoformat(),
            "total_assets": total_assets,
            "recent_updates": {
                "last_hour": last_hour,
                "last_30min": last_30min,
                "last_10min": last_10min
            },
            "collection_methods": dict(methods),
            "classifications": dict(classifications),
            "data_quality": {
                "with_os": with_os,
                "with_hostname": with_hostname,
                "with_manufacturer": with_manufacturer,
                "with_processor": with_processor,
                "with_ram": with_ram
            },
            "networks": dict(networks)
        }
        
        with open(f"database_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 Detailed report saved to: database_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
    except Exception as e:
        print(f"❌ Error analyzing database: {e}")

if __name__ == "__main__":
    comprehensive_database_analysis()