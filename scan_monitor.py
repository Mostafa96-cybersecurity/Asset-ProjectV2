#!/usr/bin/env python3
"""
Asset Scan Monitor - Track database changes during scan
"""

import sqlite3
import json
from datetime import datetime

def get_db_stats():
    """Get current database statistics"""
    try:
        conn = sqlite3.connect('assets.db')
        cursor = conn.cursor()
        
        stats = {}
        
        # Get table counts
        tables = [
            'assets', 'security_events', 'network_ranges', 'device_types',
            'departments', 'network_profiles', 'collection_history',
            'hypervisors', 'switches', 'printers', 'access_points'
        ]
        
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats[table] = cursor.fetchone()[0]
            except:
                stats[table] = 0
        
        # Get recent additions (last 1 hour)
        cursor.execute("""
            SELECT COUNT(*) FROM assets 
            WHERE last_updated > datetime('now', '-1 hour')
        """)
        stats['recent_assets'] = cursor.fetchone()[0]
        
        # Get collection methods distribution
        cursor.execute("""
            SELECT collection_method, COUNT(*) 
            FROM assets 
            WHERE collection_method IS NOT NULL
            GROUP BY collection_method
        """)
        stats['collection_methods'] = dict(cursor.fetchall())
        
        # Get device types distribution
        cursor.execute("""
            SELECT classification, COUNT(*) 
            FROM assets 
            WHERE classification IS NOT NULL
            GROUP BY classification
        """)
        stats['device_types'] = dict(cursor.fetchall())
        
        conn.close()
        return stats
        
    except Exception as e:
        return {"error": str(e)}

def compare_stats(before, after):
    """Compare before and after statistics"""
    changes = {}
    
    if "error" in before or "error" in after:
        return {"error": "Database error occurred"}
    
    # Compare table counts (skip dict values)
    for table in before:
        if table in after and not isinstance(before[table], dict) and not isinstance(after[table], dict):
            diff = after[table] - before[table]
            if diff != 0:
                changes[f"{table}_change"] = diff
    
    return changes

def main():
    print("🔍 ASSET SCAN MONITOR")
    print("=" * 50)
    
    # Get baseline statistics
    print("📊 Getting baseline database statistics...")
    baseline = get_db_stats()
    
    if "error" in baseline:
        print(f"❌ Error: {baseline['error']}")
        return
    
    print("✅ Baseline captured:")
    print(f"   📱 Assets: {baseline.get('assets', 0)}")
    print(f"   🚨 Security Events: {baseline.get('security_events', 0)}")
    print(f"   🕐 Recent Assets (1h): {baseline.get('recent_assets', 0)}")
    
    print("\n🚀 Ready to monitor scan!")
    print("   1. Run your Asset Scan from the GUI")
    print("   2. Press Enter when scan is complete")
    
    input("\n⏳ Press Enter after scan completes...")
    
    # Get post-scan statistics
    print("\n📊 Getting post-scan statistics...")
    post_scan = get_db_stats()
    
    if "error" in post_scan:
        print(f"❌ Error: {post_scan['error']}")
        return
    
    # Compare and show changes
    changes = compare_stats(baseline, post_scan)
    
    print("\n" + "=" * 50)
    print("📈 SCAN RESULTS SUMMARY")
    print("=" * 50)
    
    print(f"📱 Total Assets: {baseline.get('assets', 0)} → {post_scan.get('assets', 0)}")
    if changes.get('assets_change', 0) > 0:
        print(f"   ✅ +{changes['assets_change']} new assets discovered!")
    elif changes.get('assets_change', 0) < 0:
        print(f"   ⚠️ {changes['assets_change']} assets removed")
    else:
        print("   📊 No new assets (existing data updated)")
    
    print(f"\n🚨 Security Events: {baseline.get('security_events', 0)} → {post_scan.get('security_events', 0)}")
    if changes.get('security_events_change', 0) > 0:
        print(f"   🔔 +{changes['security_events_change']} new security events")
    
    print(f"\n🕐 Recent Assets: {baseline.get('recent_assets', 0)} → {post_scan.get('recent_assets', 0)}")
    
    # Show collection methods
    print("\n🔧 Collection Methods:")
    for method, count in post_scan.get('collection_methods', {}).items():
        print(f"   • {method}: {count} devices")
    
    # Show device types
    print("\n🏷️ Device Types:")
    for device_type, count in post_scan.get('device_types', {}).items():
        print(f"   • {device_type}: {count} devices")
    
    # Save detailed report
    report = {
        "scan_time": datetime.now().isoformat(),
        "baseline": baseline,
        "post_scan": post_scan,
        "changes": changes
    }
    
    with open(f"scan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Detailed report saved to: scan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    print("\n✅ Scan monitoring complete!")

if __name__ == "__main__":
    main()