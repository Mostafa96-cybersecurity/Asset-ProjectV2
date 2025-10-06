#!/usr/bin/env python3
"""
SMART AUTOMATED ASSET MANAGEMENT SYSTEM

🧠 SMART FEATURES:
- Automatically detects which devices are ALIVE vs DEAD
- Only tries to collect data from ALIVE devices
- Marks DEAD devices in database (don't waste time on them)
- Automatically detects and fixes duplicates
- Runs completely automated - no manual intervention

🤖 AUTOMATION FEATURES:
- Runs on schedule automatically
- Smart device state tracking
- Automatic duplicate cleanup
- Intelligent data collection
- Self-optimizing database
"""

import sqlite3
import json
import ipaddress
import subprocess
import socket
import threading
import hashlib
import time
import schedule
from datetime import datetime, timedelta
from collections import defaultdict

class SmartAutomatedSystem:
    def __init__(self, db_path="assets.db"):
        self.db_path = db_path
        self.stats = {
            'scan_started': None,
            'devices_checked': 0,
            'alive_devices': 0,
            'dead_devices': 0,
            'new_devices_added': 0,
            'devices_updated': 0,
            'duplicates_fixed': 0,
            'automation_cycles': 0
        }
        
        # Smart settings
        self.max_ping_timeout = 2  # seconds
        self.max_port_timeout = 1  # seconds
        self.dead_device_threshold = 3  # Mark as dead after 3 failed attempts
        
    def start_automation(self, network_range="10.0.21.0/24", schedule_minutes=30):
        """Start the automated system"""
        
        print("🤖 SMART AUTOMATED SYSTEM STARTING")
        print("=" * 70)
        print(f"🌐 Network range: {network_range}")
        print(f"⏰ Schedule: Every {schedule_minutes} minutes")
        print(f"🧠 Smart features: ALIVE/DEAD detection, Auto duplicate fixing")
        print()
        
        # Schedule the automation
        schedule.every(schedule_minutes).minutes.do(
            self.run_smart_automation_cycle, network_range
        )
        
        # Run first cycle immediately
        print("🚀 Running initial cycle...")
        self.run_smart_automation_cycle(network_range)
        
        # Start automated scheduling
        print(f"\n🔄 Starting automated scheduling (every {schedule_minutes} minutes)")
        print("💡 Press Ctrl+C to stop automation")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print(f"\n⏹️ Automation stopped by user")
            self.show_automation_summary()

    def run_smart_automation_cycle(self, network_range):
        """Run one complete smart automation cycle"""
        
        self.stats['scan_started'] = datetime.now()
        self.stats['automation_cycles'] += 1
        
        print(f"\n🔄 SMART AUTOMATION CYCLE #{self.stats['automation_cycles']}")
        print("=" * 70)
        print(f"🕐 Started: {self.stats['scan_started'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Phase 1: Smart device discovery (alive vs dead)
            print(f"\n🧠 PHASE 1: SMART DEVICE DISCOVERY")
            alive_devices, dead_devices = self.smart_device_discovery(network_range)
            
            # Phase 2: Update device states in database
            print(f"\n📊 PHASE 2: UPDATE DEVICE STATES")
            self.update_device_states(alive_devices, dead_devices)
            
            # Phase 3: Collect data ONLY from alive devices
            print(f"\n📡 PHASE 3: SMART DATA COLLECTION")
            self.smart_data_collection(alive_devices)
            
            # Phase 4: Automatic duplicate detection and fixing
            print(f"\n🔧 PHASE 4: AUTOMATIC DUPLICATE FIXING")
            self.automatic_duplicate_fixing()
            
            # Phase 5: Database optimization
            print(f"\n⚡ PHASE 5: DATABASE OPTIMIZATION")
            self.smart_database_optimization()
            
            # Phase 6: Show results
            print(f"\n📈 PHASE 6: CYCLE RESULTS")
            self.show_cycle_results()
            
        except Exception as e:
            print(f"❌ Automation cycle error: {str(e)}")

    def smart_device_discovery(self, network_range):
        """Smart discovery - quickly identify ALIVE vs DEAD devices"""
        
        print(f"🔍 Smart scanning: {network_range}")
        print(f"💡 Using smart timeouts: ping={self.max_ping_timeout}s, port={self.max_port_timeout}s")
        
        alive_devices = []
        dead_devices = []
        
        try:
            network = ipaddress.IPv4Network(network_range, strict=False)
            
            # Quick parallel ping scan
            ping_results = {}
            
            def smart_ping(ip):
                """Smart ping with timeout"""
                try:
                    start_time = time.time()
                    result = subprocess.run(
                        ['ping', '-n', '1', '-w', str(self.max_ping_timeout * 1000), str(ip)],
                        capture_output=True,
                        timeout=self.max_ping_timeout + 1
                    )
                    response_time = (time.time() - start_time) * 1000
                    
                    if result.returncode == 0:
                        ping_results[str(ip)] = {'alive': True, 'response_time': response_time}
                    else:
                        ping_results[str(ip)] = {'alive': False, 'response_time': None}
                        
                except Exception:
                    ping_results[str(ip)] = {'alive': False, 'response_time': None}
            
            # Parallel ping scanning
            threads = []
            ip_list = list(network.hosts())[:100]  # Limit for performance
            
            print(f"   🚀 Quick ping scanning {len(ip_list)} IPs...")
            
            for ip in ip_list:
                thread = threading.Thread(target=smart_ping, args=(ip,))
                thread.start()
                threads.append(thread)
                
                # Limit concurrent threads
                if len(threads) >= 30:
                    for t in threads:
                        t.join(timeout=self.max_ping_timeout + 2)
                    threads = []
            
            # Wait for remaining threads
            for t in threads:
                t.join(timeout=self.max_ping_timeout + 2)
            
            # Process results
            alive_ips = [ip for ip, result in ping_results.items() if result['alive']]
            dead_ips = [ip for ip, result in ping_results.items() if not result['alive']]
            
            print(f"   ✅ ALIVE devices: {len(alive_ips)}")
            print(f"   💀 DEAD devices: {len(dead_ips)}")
            
            # Gather detailed info ONLY for alive devices
            if alive_ips:
                print(f"\n   📊 Gathering details for {len(alive_ips)} ALIVE devices...")
                
                for ip in alive_ips:
                    device_info = self.gather_smart_device_info(ip, ping_results[ip]['response_time'])
                    if device_info:
                        alive_devices.append(device_info)
                        print(f"      ✅ {ip} → {device_info.get('hostname', 'Unknown')}")
            
            # Track dead devices
            for ip in dead_ips:
                dead_devices.append({
                    'ip_address': ip,
                    'status': 'dead',
                    'last_checked': datetime.now().isoformat(),
                    'ping_failed': True
                })
            
            self.stats['devices_checked'] = len(ip_list)
            self.stats['alive_devices'] = len(alive_devices)
            self.stats['dead_devices'] = len(dead_devices)
            
            print(f"\n🎯 Smart discovery complete:")
            print(f"   📊 Total checked: {len(ip_list)}")
            print(f"   ✅ ALIVE: {len(alive_devices)} (will collect data)")
            print(f"   💀 DEAD: {len(dead_devices)} (will skip)")
            
        except Exception as e:
            print(f"❌ Smart discovery error: {str(e)}")
        
        return alive_devices, dead_devices

    def gather_smart_device_info(self, ip_address, response_time):
        """Gather info ONLY from alive devices with smart timeouts"""
        
        device_info = {
            'ip_address': ip_address,
            'status': 'alive',
            'last_seen': datetime.now().isoformat(),
            'response_time_ms': round(response_time, 2),
            'collection_time': datetime.now().isoformat(),
            'data_source': 'Smart Automated System'
        }
        
        try:
            # Smart hostname resolution with timeout
            try:
                socket.setdefaulttimeout(2)
                hostname = socket.gethostbyaddr(ip_address)[0]
                device_info['hostname'] = hostname
            except:
                device_info['hostname'] = f"device-{ip_address.replace('.', '-')}"
            finally:
                socket.setdefaulttimeout(None)
            
            # Smart port scanning with minimal timeout
            open_ports = []
            critical_ports = [22, 80, 135, 139, 443, 445, 3389]  # Most important ports only
            
            for port in critical_ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(self.max_port_timeout)
                    if sock.connect_ex((ip_address, port)) == 0:
                        open_ports.append(port)
                    sock.close()
                except:
                    pass
            
            device_info['open_ports'] = json.dumps(open_ports)
            device_info['port_count'] = len(open_ports)
            
            # Smart device classification
            if 3389 in open_ports:
                device_info['device_classification'] = "Windows System"
            elif 22 in open_ports:
                device_info['device_classification'] = "Linux/Unix System"
            elif 80 in open_ports or 443 in open_ports:
                device_info['device_classification'] = "Web Server"
            elif len(open_ports) > 2:
                device_info['device_classification'] = "Network Server"
            else:
                device_info['device_classification'] = "Network Device"
            
            # Smart fingerprint
            fingerprint_data = f"{ip_address}_{device_info['hostname']}_{sorted(open_ports)}"
            device_info['device_fingerprint'] = hashlib.md5(fingerprint_data.encode()).hexdigest()
            
        except Exception as e:
            print(f"      ⚠️ Error gathering info for {ip_address}: {str(e)}")
        
        return device_info

    def update_device_states(self, alive_devices, dead_devices):
        """Update device states in database - mark alive/dead"""
        
        print(f"📊 Updating device states in database...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Update alive devices
        for device in alive_devices:
            ip_address = device['ip_address']
            cursor.execute("""
                UPDATE assets 
                SET device_status = 'alive', 
                    last_seen = ?, 
                    failed_ping_count = 0,
                    response_time_ms = ?
                WHERE ip_address = ?
            """, (device['last_seen'], device.get('response_time_ms'), ip_address))
        
        # Update dead devices
        for device in dead_devices:
            ip_address = device['ip_address']
            
            # Increment failed ping count
            cursor.execute("""
                UPDATE assets 
                SET device_status = 'dead',
                    last_checked = ?,
                    failed_ping_count = COALESCE(failed_ping_count, 0) + 1
                WHERE ip_address = ?
            """, (device['last_checked'], ip_address))
            
            # Mark as permanently dead if too many failures
            cursor.execute("""
                UPDATE assets 
                SET device_status = 'permanently_dead',
                    notes = 'Device not responding for ' || failed_ping_count || ' cycles'
                WHERE ip_address = ? AND failed_ping_count >= ?
            """, (ip_address, self.dead_device_threshold))
        
        conn.commit()
        conn.close()
        
        print(f"   ✅ Updated {len(alive_devices)} alive devices")
        print(f"   💀 Updated {len(dead_devices)} dead devices")

    def smart_data_collection(self, alive_devices):
        """Collect data ONLY from alive devices - don't waste time on dead ones"""
        
        print(f"📡 Smart data collection from {len(alive_devices)} ALIVE devices...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for device_info in alive_devices:
            ip_address = device_info['ip_address']
            
            # Check if device exists
            cursor.execute("SELECT id FROM assets WHERE ip_address = ?", (ip_address,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing alive device
                device_id = existing[0]
                self.smart_update_alive_device(cursor, device_id, device_info)
                self.stats['devices_updated'] += 1
                print(f"   🔄 Updated: {ip_address}")
            else:
                # Add new alive device
                self.add_new_alive_device(cursor, device_info)
                self.stats['new_devices_added'] += 1
                print(f"   ➕ Added: {ip_address}")
        
        conn.commit()
        conn.close()
        
        print(f"   ✅ Data collection complete!")
        print(f"   🔄 Updated: {self.stats['devices_updated']}")
        print(f"   ➕ Added: {self.stats['new_devices_added']}")

    def smart_update_alive_device(self, cursor, device_id, new_data):
        """Smart update for alive devices"""
        
        # Get current data
        cursor.execute("SELECT * FROM assets WHERE id = ?", (device_id,))
        current_row = cursor.fetchone()
        
        if not current_row:
            return
        
        # Get column names
        cursor.execute("PRAGMA table_info(assets)")
        columns = [col[1] for col in cursor.fetchall()]
        current_dict = dict(zip(columns, current_row))
        
        # Smart update logic
        updates = {}
        
        for key, new_value in new_data.items():
            if key in columns:
                current_value = current_dict.get(key)
                
                # Always update status and timing fields
                if key in ['device_status', 'last_seen', 'collection_time', 'response_time_ms']:
                    updates[key] = new_value
                    continue
                
                # Update if current is empty
                if current_value is None or str(current_value).strip() == '':
                    updates[key] = new_value
                    continue
                
                # Update if new data is better
                if isinstance(new_value, str) and len(new_value) > len(str(current_value)):
                    updates[key] = new_value
        
        # Always update these
        updates['last_updated'] = datetime.now().isoformat()
        updates['data_source'] = 'Smart Automated System'
        
        # Execute update
        if updates:
            set_clauses = [f"{k} = ?" for k in updates.keys()]
            values = list(updates.values()) + [device_id]
            query = f"UPDATE assets SET {', '.join(set_clauses)} WHERE id = ?"
            cursor.execute(query, values)

    def add_new_alive_device(self, cursor, device_data):
        """Add new alive device"""
        
        # Add metadata
        device_data['device_status'] = 'alive'
        device_data['created_at'] = datetime.now().isoformat()
        device_data['last_updated'] = datetime.now().isoformat()
        device_data['failed_ping_count'] = 0
        
        # Get existing columns
        cursor.execute("PRAGMA table_info(assets)")
        existing_columns = [col[1] for col in cursor.fetchall()]
        
        # Insert only existing columns
        insert_data = {k: v for k, v in device_data.items() if k in existing_columns}
        
        if insert_data:
            columns = list(insert_data.keys())
            placeholders = ['?' for _ in columns]
            values = list(insert_data.values())
            
            query = f"INSERT INTO assets ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
            cursor.execute(query, values)

    def automatic_duplicate_fixing(self):
        """Automatically detect and fix duplicates - no manual intervention"""
        
        print(f"🔧 Automatic duplicate detection and fixing...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Find duplicates by multiple criteria
        duplicate_groups = []
        
        # Serial number duplicates
        cursor.execute("""
            SELECT serial_number, COUNT(*) as count, GROUP_CONCAT(id) as ids
            FROM assets 
            WHERE serial_number IS NOT NULL 
            AND serial_number != '' 
            AND LENGTH(TRIM(serial_number)) > 3
            GROUP BY TRIM(LOWER(serial_number))
            HAVING count > 1
        """)
        
        serial_duplicates = cursor.fetchall()
        
        # IP address duplicates (same IP, different entries)
        cursor.execute("""
            SELECT ip_address, COUNT(*) as count, GROUP_CONCAT(id) as ids
            FROM assets 
            WHERE ip_address IS NOT NULL 
            GROUP BY ip_address
            HAVING count > 1
        """)
        
        ip_duplicates = cursor.fetchall()
        
        # MAC address duplicates
        cursor.execute("""
            SELECT mac_address, COUNT(*) as count, GROUP_CONCAT(id) as ids
            FROM assets 
            WHERE mac_address IS NOT NULL 
            AND mac_address != ''
            GROUP BY TRIM(LOWER(mac_address))
            HAVING count > 1
        """)
        
        mac_duplicates = cursor.fetchall()
        
        all_duplicates = list(serial_duplicates) + list(ip_duplicates) + list(mac_duplicates)
        
        if all_duplicates:
            print(f"   🔍 Found {len(all_duplicates)} duplicate groups")
            
            devices_to_remove = []
            
            for duplicate_value, count, ids in all_duplicates:
                id_list = [int(x) for x in ids.split(',')]
                
                if len(id_list) <= 1:
                    continue
                
                print(f"   📋 Fixing duplicates for '{duplicate_value}' ({count} devices)")
                
                # Get device details and scores
                device_scores = []
                for device_id in id_list:
                    cursor.execute("SELECT * FROM assets WHERE id = ?", (device_id,))
                    device = cursor.fetchone()
                    if device:
                        # Calculate smart score
                        score = self.calculate_smart_device_score(device)
                        device_scores.append((device_id, device, score))
                
                # Sort by score (best first)
                device_scores.sort(key=lambda x: x[2], reverse=True)
                
                # Keep best device, remove others
                if device_scores:
                    keep_device = device_scores[0]
                    print(f"      👑 Keeping: ID {keep_device[0]} (score: {keep_device[2]:.1f})")
                    
                    # Merge data into best device
                    merged_data = self.merge_duplicate_data(device_scores)
                    if merged_data:
                        self.update_device_with_merged_data(cursor, keep_device[0], merged_data)
                    
                    # Remove other devices
                    for device_id, device, score in device_scores[1:]:
                        devices_to_remove.append(device_id)
                        print(f"      🗑️ Removing: ID {device_id} (score: {score:.1f})")
            
            # Execute removals
            if devices_to_remove:
                placeholders = ','.join(['?'] * len(devices_to_remove))
                cursor.execute(f"DELETE FROM assets WHERE id IN ({placeholders})", devices_to_remove)
                self.stats['duplicates_fixed'] = len(devices_to_remove)
                print(f"   ✅ Automatically fixed {len(devices_to_remove)} duplicates")
        else:
            print(f"   ✅ No duplicates found - database is clean!")
        
        conn.commit()
        conn.close()

    def calculate_smart_device_score(self, device):
        """Calculate smart score for device quality"""
        
        score = 0
        
        # Basic completeness
        for field in device:
            if field is not None and str(field).strip():
                score += 1
        
        # Bonus for alive devices
        device_dict = dict(zip(range(len(device)), device))
        if 'alive' in str(device_dict.get(1, '')).lower():
            score += 20
        
        # Bonus for recent data
        for field in device:
            if field and 'time' in str(field).lower():
                try:
                    if '2025' in str(field):  # Recent data
                        score += 10
                except:
                    pass
        
        return score

    def merge_duplicate_data(self, device_scores):
        """Merge data from duplicates"""
        
        if len(device_scores) <= 1:
            return None
        
        merged_data = {}
        
        # Take best value for each field
        for i in range(len(device_scores[0][1])):  # For each column
            best_value = None
            best_score = -1
            
            for device_id, device, score in device_scores:
                if i < len(device) and device[i] is not None:
                    value = device[i]
                    if str(value).strip():
                        value_score = len(str(value)) + score
                        if value_score > best_score:
                            best_value = value
                            best_score = value_score
            
            if best_value is not None:
                merged_data[f"col_{i}"] = best_value
        
        merged_data['merge_timestamp'] = datetime.now().isoformat()
        merged_data['notes'] = f'Auto-merged from {len(device_scores)} duplicates'
        
        return merged_data

    def update_device_with_merged_data(self, cursor, device_id, merged_data):
        """Update device with merged data"""
        
        # Get column names
        cursor.execute("PRAGMA table_info(assets)")
        columns = [col[1] for col in cursor.fetchall()]
        
        updates = {}
        for i, column in enumerate(columns):
            col_key = f"col_{i}"
            if col_key in merged_data:
                updates[column] = merged_data[col_key]
        
        # Add metadata
        updates['last_updated'] = datetime.now().isoformat()
        updates['data_source'] = 'Smart Auto-Merge'
        
        if updates:
            set_clauses = [f"{k} = ?" for k in updates.keys()]
            values = list(updates.values()) + [device_id]
            query = f"UPDATE assets SET {', '.join(set_clauses)} WHERE id = ?"
            cursor.execute(query, values)

    def smart_database_optimization(self):
        """Smart database optimization"""
        
        print(f"⚡ Smart database optimization...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clean up very old dead devices (optional)
        cursor.execute("""
            DELETE FROM assets 
            WHERE device_status = 'permanently_dead' 
            AND failed_ping_count > 10
            AND last_seen < datetime('now', '-30 days')
        """)
        
        old_deleted = cursor.rowcount
        
        # Vacuum and analyze
        cursor.execute("VACUUM")
        cursor.execute("ANALYZE")
        
        conn.close()
        
        if old_deleted > 0:
            print(f"   🗑️ Cleaned up {old_deleted} very old dead devices")
        print(f"   ✅ Database optimized")

    def show_cycle_results(self):
        """Show automation cycle results"""
        
        duration = datetime.now() - self.stats['scan_started']
        
        # Get current database stats
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM assets")
        total_devices = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM assets WHERE device_status = 'alive'")
        alive_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM assets WHERE device_status = 'dead'")
        dead_count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"📈 SMART AUTOMATION CYCLE RESULTS")
        print("=" * 70)
        print(f"⏱️  Cycle duration: {duration}")
        print(f"🔍 Devices checked: {self.stats['devices_checked']}")
        print(f"✅ ALIVE devices: {self.stats['alive_devices']} (collected data)")
        print(f"💀 DEAD devices: {self.stats['dead_devices']} (skipped)")
        print(f"➕ New devices added: {self.stats['new_devices_added']}")
        print(f"🔄 Devices updated: {self.stats['devices_updated']}")
        print(f"🔧 Duplicates fixed: {self.stats['duplicates_fixed']}")
        print()
        print(f"📊 DATABASE STATUS:")
        print(f"   📈 Total devices: {total_devices}")
        print(f"   ✅ Alive: {alive_count}")
        print(f"   💀 Dead: {dead_count}")
        print()
        print("🎯 SMART AUTOMATION SUCCESS!")
        print("   🧠 Only collected from ALIVE devices")
        print("   🤖 Automatically fixed duplicates")
        print("   ⚡ Zero manual intervention required")

    def show_automation_summary(self):
        """Show overall automation summary"""
        
        print(f"\n📊 AUTOMATION SUMMARY")
        print("=" * 70)
        print(f"🔄 Total automation cycles: {self.stats['automation_cycles']}")
        print(f"🤖 Fully automated - no manual work required")
        print(f"🧠 Smart ALIVE/DEAD device detection")
        print(f"🔧 Automatic duplicate detection and fixing")
        print(f"⚡ Optimized for performance and accuracy")

def main():
    """Start the smart automated system"""
    
    system = SmartAutomatedSystem()
    
    # Start automation (runs every 30 minutes)
    system.start_automation(
        network_range="10.0.21.0/24",
        schedule_minutes=30
    )

if __name__ == "__main__":
    main()