#!/usr/bin/env python3
"""
Database Monitor & Management Tool
Real-time monitoring of database status, sync operations, and data quality
"""

import sqlite3
import pandas as pd
import os
import json
from datetime import datetime
import time
from pathlib import Path
import sys

class DatabaseMonitor:
    def __init__(self, db_path='assets.db'):
        self.db_path = db_path
        
    def get_db_status(self):
        """Get comprehensive database status"""
        if not os.path.exists(self.db_path):
            return {"status": "❌ Database not found", "exists": False}
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Basic stats
            cursor.execute("SELECT COUNT(*) FROM assets")
            total_records = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM assets WHERE ip_address IS NOT NULL AND ip_address != ''")
            records_with_ip = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM assets WHERE firmware_os_version IS NOT NULL AND firmware_os_version != ''")
            records_with_os = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM assets WHERE _sync_pending = 'True'")
            pending_sync = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT data_source) FROM assets")
            data_sources = cursor.fetchone()[0]
            
            # Recent activity
            cursor.execute("SELECT COUNT(*) FROM assets WHERE updated_at > datetime('now', '-1 hour')")
            recent_updates = cursor.fetchone()[0]
            
            conn.close()
            
            db_size = os.path.getsize(self.db_path)
            
            return {
                "status": "✅ Database operational",
                "exists": True,
                "total_records": total_records,
                "records_with_ip": records_with_ip,
                "records_with_os": records_with_os,
                "pending_sync": pending_sync,
                "data_sources": data_sources,
                "recent_updates": recent_updates,
                "size_mb": round(db_size / 1024 / 1024, 2),
                "collection_rate": round((records_with_os / total_records * 100) if total_records > 0 else 0, 1)
            }
            
        except Exception as e:
            return {"status": f"❌ Database error: {str(e)}", "exists": False}
    
    def show_recent_activity(self, hours=24, limit=20):
        """Show recent database activity"""
        try:
            conn = sqlite3.connect(self.db_path)
            query = """
            SELECT ip_address, hostname, device_type, data_source, updated_at
            FROM assets 
            WHERE updated_at > datetime('now', '-{} hours')
            ORDER BY updated_at DESC
            LIMIT {}
            """.format(hours, limit)
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if df.empty:
                print(f"📊 No activity in the last {hours} hours")
                return
                
            print(f"📊 Recent Activity (Last {hours} hours):")
            print("=" * 80)
            
            for idx, row in df.iterrows():
                updated = row['updated_at']
                print(f"{idx+1:2}. {updated} | IP: {row['ip_address']:<15} | {row['hostname']:<20} | {row['data_source']}")
                
        except Exception as e:
            print(f"❌ Error showing activity: {e}")
    
    def show_collection_stats(self):
        """Show collection method statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Collection methods
            cursor.execute("SELECT data_source, COUNT(*) FROM assets GROUP BY data_source ORDER BY COUNT(*) DESC")
            sources = cursor.fetchall()
            
            # Device types
            cursor.execute("SELECT device_type, COUNT(*) FROM assets WHERE device_type IS NOT NULL GROUP BY device_type ORDER BY COUNT(*) DESC")
            types = cursor.fetchall()
            
            print("📊 Collection Statistics:")
            print("=" * 50)
            print("🔍 Data Sources:")
            for source, count in sources:
                print(f"  {source}: {count} devices")
            
            print("\n📱 Device Types:")
            for device_type, count in types[:10]:  # Top 10
                print(f"  {device_type}: {count} devices")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Error showing stats: {e}")
    
    def check_sync_status(self):
        """Check Excel-Database sync status"""
        excel_files = list(Path('.').glob('*.xlsx'))
        excel_files = [f for f in excel_files if 'backup' not in str(f)]
        
        print("📊 Sync Status:")
        print("=" * 40)
        
        if not excel_files:
            print("📊 No Excel files found")
        else:
            for excel_file in excel_files:
                try:
                    df = pd.read_excel(excel_file)
                    print(f"📊 {excel_file}: {len(df)} rows")
                except Exception as e:
                    print(f"❌ {excel_file}: Error - {e}")
        
        # Check pending sync
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM assets WHERE _sync_pending = 'True'")
            pending = cursor.fetchone()[0]
            print(f"🔄 Pending sync: {pending} records")
            conn.close()
        except Exception as e:
            print(f"❌ Error checking sync: {e}")

    def live_monitor(self):
        """Live monitoring dashboard"""
        print("🔴 LIVE DATABASE MONITOR")
        print("Press Ctrl+C to stop")
        print("=" * 60)
        
        try:
            while True:
                os.system('cls' if os.name == 'nt' else 'clear')  # Clear screen
                
                print(f"🔴 LIVE MONITOR - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("=" * 60)
                
                # Database status
                status = self.get_db_status()
                print(f"📊 Status: {status['status']}")
                
                if status['exists']:
                    print(f"📦 Total Records: {status['total_records']}")
                    print(f"🌐 Records with IP: {status['records_with_ip']}")
                    print(f"🖥️ Records with OS Info: {status['records_with_os']}")
                    print(f"🔄 Pending Sync: {status['pending_sync']}")
                    print(f"📊 Collection Rate: {status['collection_rate']}%")
                    print(f"💾 DB Size: {status['size_mb']} MB")
                    print(f"📈 Recent Updates (1h): {status['recent_updates']}")
                
                print("\n" + "=" * 60)
                print("🔄 Refreshing in 5 seconds... (Ctrl+C to stop)")
                
                time.sleep(5)
                
        except KeyboardInterrupt:
            print("\n✅ Monitor stopped")

def main():
    monitor = DatabaseMonitor()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'status':
            status = monitor.get_db_status()
            print(json.dumps(status, indent=2))
        
        elif command == 'activity':
            hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
            monitor.show_recent_activity(hours)
        
        elif command == 'stats':
            monitor.show_collection_stats()
        
        elif command == 'sync':
            monitor.check_sync_status()
        
        elif command == 'live':
            monitor.live_monitor()
        
        else:
            print("Usage: python database_monitor.py [status|activity|stats|sync|live]")
    
    else:
        # Default: show everything
        print("🎯 DATABASE STATUS REPORT")
        print("=" * 60)
        
        status = monitor.get_db_status()
        print(f"Status: {status['status']}")
        
        if status['exists']:
            print(f"📦 Total Records: {status['total_records']}")
            print(f"🌐 Records with IP: {status['records_with_ip']}")
            print(f"🖥️ Records with OS Info: {status['records_with_os']}")
            print(f"📊 Collection Rate: {status['collection_rate']}%")
            print(f"💾 DB Size: {status['size_mb']} MB")
            
            print("\n")
            monitor.show_collection_stats()
            
            print("\n")
            monitor.show_recent_activity(24, 10)
            
            print("\n")
            monitor.check_sync_status()
        
        print("\n💡 Use 'python database_monitor.py live' for real-time monitoring")

if __name__ == "__main__":
    main()