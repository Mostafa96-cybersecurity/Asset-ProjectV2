#!/usr/bin/env python3
"""
Simple Database Analysis - Fixed version
"""

import sqlite3

def simple_database_analysis():
    print("🔍 DATABASE ANALYSIS REPORT")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('assets.db')
        cursor = conn.cursor()
        
        # Basic Stats
        cursor.execute("SELECT COUNT(*) FROM assets")
        total_assets = cursor.fetchone()[0]
        print(f"📱 Total Assets: {total_assets}")
        
        # Recent Activity
        cursor.execute("""
            SELECT COUNT(*) FROM assets 
            WHERE last_updated > datetime('now', '-1 hour')
        """)
        recent = cursor.fetchone()[0]
        print(f"🕐 Updated in last hour: {recent}")
        
        # Collection Methods
        print("\n🔧 COLLECTION METHODS:")
        cursor.execute("""
            SELECT collection_method, COUNT(*) 
            FROM assets 
            WHERE collection_method IS NOT NULL
            GROUP BY collection_method
            ORDER BY COUNT(*) DESC
        """)
        methods = cursor.fetchall()
        for method, count in methods:
            percentage = (count / total_assets * 100)
            print(f"   • {method}: {count} devices ({percentage:.1f}%)")
        
        # Device Types
        print("\n🏷️ DEVICE TYPES:")
        cursor.execute("""
            SELECT classification, COUNT(*) 
            FROM assets 
            WHERE classification IS NOT NULL
            GROUP BY classification
            ORDER BY COUNT(*) DESC
        """)
        types = cursor.fetchall()
        for device_type, count in types:
            percentage = (count / total_assets * 100)
            print(f"   • {device_type}: {count} devices ({percentage:.1f}%)")
        
        # Data Quality
        print("\n📊 DATA QUALITY:")
        
        cursor.execute("SELECT COUNT(*) FROM assets WHERE operating_system IS NOT NULL AND operating_system != 'Unknown'")
        with_os = cursor.fetchone()[0]
        print(f"   🖥️ OS Information: {with_os}/{total_assets} ({with_os/total_assets*100:.1f}%)")
        
        cursor.execute("SELECT COUNT(*) FROM assets WHERE hostname IS NOT NULL AND hostname != ''")
        with_hostname = cursor.fetchone()[0]
        print(f"   🏷️ Hostname: {with_hostname}/{total_assets} ({with_hostname/total_assets*100:.1f}%)")
        
        cursor.execute("SELECT COUNT(*) FROM assets WHERE manufacturer IS NOT NULL AND manufacturer != 'Unknown'")
        with_manufacturer = cursor.fetchone()[0]
        print(f"   🏭 Manufacturer: {with_manufacturer}/{total_assets} ({with_manufacturer/total_assets*100:.1f}%)")
        
        # Network Analysis (simplified)
        print("\n🌐 NETWORK COVERAGE:")
        cursor.execute("""
            SELECT ip_address FROM assets 
            WHERE ip_address IS NOT NULL 
            ORDER BY ip_address
        """)
        ips = [row[0] for row in cursor.fetchall()]
        
        # Count networks by first 3 octets
        networks = {}
        for ip in ips:
            if '.' in ip:
                network = '.'.join(ip.split('.')[:3]) + '.x'
                networks[network] = networks.get(network, 0) + 1
        
        print("   Top networks:")
        for network, count in sorted(networks.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   • {network}: {count} devices")
        
        # Recent Devices
        print("\n🆕 RECENTLY UPDATED DEVICES:")
        cursor.execute("""
            SELECT hostname, ip_address, classification, operating_system, last_updated
            FROM assets 
            ORDER BY last_updated DESC
            LIMIT 5
        """)
        recent_devices = cursor.fetchall()
        
        for i, (hostname, ip, classification, os, updated) in enumerate(recent_devices, 1):
            hostname = hostname or ip or "Unknown"
            classification = classification or "Unknown"
            os = os or "Unknown"
            print(f"   {i}. {hostname} ({ip})")
            print(f"      Type: {classification} | OS: {os} | Updated: {updated}")
        
        # Check for scan progress
        print("\n📈 SCAN STATUS ANALYSIS:")
        if recent > 0:
            print(f"   ✅ Active: {recent} devices updated recently")
        else:
            print("   ⚠️ No recent updates - scan may not be running")
        
        if total_assets < 400:
            print(f"   📊 Expected Growth: {total_assets} → 560+ devices (scan discovery)")
        
        # Sample detailed device info
        print("\n🔍 SAMPLE DEVICE DETAILS:")
        cursor.execute("""
            SELECT hostname, ip_address, operating_system, manufacturer, model, 
                   processor, installed_ram_gb, storage, collection_method
            FROM assets 
            WHERE operating_system IS NOT NULL AND operating_system != 'Unknown'
            LIMIT 3
        """)
        detailed_devices = cursor.fetchall()
        
        for device in detailed_devices:
            hostname, ip, os, manufacturer, model, processor, ram, storage, method = device
            print(f"   Device: {hostname or ip}")
            print(f"   • OS: {os}")
            print(f"   • Hardware: {manufacturer or 'Unknown'} {model or ''}")
            print(f"   • CPU: {processor or 'Unknown'}")
            print(f"   • RAM: {ram or 'Unknown'} GB")
            print(f"   • Storage: {storage or 'Unknown'}")
            print(f"   • Collection: {method}")
            print()
        
        conn.close()
        
        print("📋 SUMMARY:")
        print(f"   • Database contains {total_assets} devices")
        print(f"   • Data quality: {(with_os + with_hostname + with_manufacturer)/(total_assets*3)*100:.1f}% complete")
        print(f"   • Collection methods: {len(methods)} different types")
        print(f"   • Network coverage: {len(networks)} different subnets")
        
        if total_assets == 222:
            print("\n💡 RECOMMENDATION:")
            print("   Your database shows 222 devices, but scans discovered 560+ devices.")
            print("   This suggests the unlimited scan hasn't run yet or is still in progress.")
            print("   Run an Asset Scan to collect all discovered devices!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    simple_database_analysis()