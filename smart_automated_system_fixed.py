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
- Smart device state tracking
- Automatic duplicate cleanup
- Intelligent data collection
- Self-optimizing database
- Built-in scheduling capability
"""

import sqlite3
import json
import ipaddress
import subprocess
import socket
import threading
import hashlib
import time
from datetime import datetime

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
        self.max_ping_timeout = 1  # seconds - fast timeout
        self.max_port_timeout = 0.5  # seconds - very fast
        self.dead_device_threshold = 3  # Mark as dead after 3 failed attempts

    def run_smart_automation_cycle(self, network_range="10.0.21.0/24"):
        """Run one complete smart automation cycle"""
        
        self.stats['scan_started'] = datetime.now()
        self.stats['automation_cycles'] += 1
        
        print(f"🤖 SMART AUTOMATION CYCLE #{self.stats['automation_cycles']}")
        print("=" * 70)
        print(f"🕐 Started: {self.stats['scan_started'].strftime('%Y-%m-%d %H:%M:%S')}")
        print("🧠 SMART: Only collect from ALIVE devices, skip DEAD ones")
        print("🔧 AUTO: Automatically detect and fix duplicates")
        
        try:
            # Phase 1: Smart device discovery (alive vs dead)
            print("\n🧠 PHASE 1: SMART DEVICE DISCOVERY")
            alive_devices, dead_devices = self.smart_device_discovery(network_range)
            
            # Phase 2: Update device states in database
            print("\n📊 PHASE 2: UPDATE DEVICE STATES")
            self.update_device_states(alive_devices, dead_devices)
            
            # Phase 3: Collect data ONLY from alive devices
            print("\n📡 PHASE 3: SMART DATA COLLECTION")
            self.smart_data_collection(alive_devices)
            
            # Phase 4: Automatic duplicate detection and fixing
            print("\n🔧 PHASE 4: AUTOMATIC DUPLICATE FIXING")
            self.automatic_duplicate_fixing()
            
            # Phase 5: Database optimization
            print("\n⚡ PHASE 5: DATABASE OPTIMIZATION")
            self.smart_database_optimization()
            
            # Phase 6: Show results
            print("\n📈 PHASE 6: CYCLE RESULTS")
            self.show_cycle_results()
            
        except Exception as e:
            print(f"❌ Automation cycle error: {str(e)}")

    def smart_device_discovery(self, network_range):
        """Smart discovery - quickly identify ALIVE vs DEAD devices"""
        
        print(f"🔍 Smart scanning: {network_range}")
        print(f"💡 Smart timeouts: ping={self.max_ping_timeout}s, port={self.max_port_timeout}s")
        print("🧠 Strategy: Find ALIVE devices fast, skip DEAD ones")
        
        alive_devices = []
        dead_devices = []
        
        try:
            network = ipaddress.IPv4Network(network_range, strict=False)
            
            # Quick parallel ping scan
            ping_results = {}
            
            def smart_ping(ip):
                """Smart ping with fast timeout"""
                try:
                    start_time = time.time()
                    result = subprocess.run(
                        ['ping', '-n', '1', '-w', '500', str(ip)],  # 500ms timeout
                        capture_output=True,
                        timeout=2
                    )
                    response_time = (time.time() - start_time) * 1000
                    
                    if result.returncode == 0:
                        ping_results[str(ip)] = {'alive': True, 'response_time': response_time}
                        print(f"      ✅ ALIVE: {ip} ({response_time:.1f}ms)")
                    else:
                        ping_results[str(ip)] = {'alive': False, 'response_time': None}
                        
                except Exception:
                    ping_results[str(ip)] = {'alive': False, 'response_time': None}
            
            # Parallel ping scanning
            threads = []
            ip_list = list(network.hosts())[:50]  # Limit for performance
            
            print(f"   🚀 Quick ping scanning {len(ip_list)} IPs...")
            
            for ip in ip_list:
                thread = threading.Thread(target=smart_ping, args=(ip,))
                thread.start()
                threads.append(thread)
                
                # Limit concurrent threads
                if len(threads) >= 20:
                    for t in threads:
                        t.join(timeout=3)
                    threads = []
            
            # Wait for remaining threads
            for t in threads:
                t.join(timeout=3)
            
            # Process results
            alive_ips = [ip for ip, result in ping_results.items() if result['alive']]
            dead_ips = [ip for ip, result in ping_results.items() if not result['alive']]
            
            print("\n   📊 DISCOVERY RESULTS:")
            print(f"      ✅ ALIVE devices: {len(alive_ips)} (will collect data)")
            print(f"      💀 DEAD devices: {len(dead_ips)} (will skip - save time)")
            
            # Gather detailed info ONLY for alive devices
            if alive_ips:
                print(f"\n   📊 Gathering details ONLY from {len(alive_ips)} ALIVE devices...")
                
                for ip in alive_ips:
                    device_info = self.gather_smart_device_info(ip, ping_results[ip]['response_time'])
                    if device_info:
                        alive_devices.append(device_info)
                        print(f"      📡 {ip} → {device_info.get('hostname', 'Unknown')} ({device_info.get('device_classification', 'Unknown')})")
            
            # Track dead devices (don't waste time collecting from them)
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
            
            print("\n🎯 SMART DISCOVERY COMPLETE:")
            print(f"   📊 Total checked: {len(ip_list)}")
            print(f"   ✅ ALIVE: {len(alive_devices)} (data collected)")
            print(f"   💀 DEAD: {len(dead_devices)} (skipped - saved time)")
            
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
                socket.setdefaulttimeout(1)
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
        """Update device states in database - mark alive/dead intelligently"""
        
        print("📊 Updating device states in database...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Add columns if they don't exist
        try:
            cursor.execute("ALTER TABLE assets ADD COLUMN device_status TEXT")
        except:
            pass
        try:
            cursor.execute("ALTER TABLE assets ADD COLUMN last_seen TEXT")
        except:
            pass
        try:
            cursor.execute("ALTER TABLE assets ADD COLUMN failed_ping_count INTEGER DEFAULT 0")
        except:
            pass
        try:
            cursor.execute("ALTER TABLE assets ADD COLUMN last_checked TEXT")
        except:
            pass
        try:
            cursor.execute("ALTER TABLE assets ADD COLUMN response_time_ms REAL")
        except:
            pass
        
        # Update alive devices
        alive_updated = 0
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
            if cursor.rowcount > 0:
                alive_updated += 1
        
        # Update dead devices
        dead_updated = 0
        for device in dead_devices:
            ip_address = device['ip_address']
            
            # Check if device exists
            cursor.execute("SELECT failed_ping_count FROM assets WHERE ip_address = ?", (ip_address,))
            existing = cursor.fetchone()
            
            if existing:
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
                
                if cursor.rowcount > 0:
                    dead_updated += 1
        
        conn.commit()
        conn.close()
        
        print(f"   ✅ Updated {alive_updated} alive devices")
        print(f"   💀 Updated {dead_updated} dead devices")
        print("   🧠 Smart: Don't waste time on dead devices")

    def smart_data_collection(self, alive_devices):
        """Collect data ONLY from alive devices - don't waste time on dead ones"""
        
        print(f"📡 Smart data collection from {len(alive_devices)} ALIVE devices...")
        print("💡 Smart strategy: Skip dead devices, focus on alive ones")
        
        if not alive_devices:
            print("   ⚠️ No alive devices found - nothing to collect")
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        new_count = 0
        updated_count = 0
        
        for device_info in alive_devices:
            ip_address = device_info['ip_address']
            
            # Check if device exists
            cursor.execute("SELECT id FROM assets WHERE ip_address = ?", (ip_address,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing alive device
                device_id = existing[0]
                self.smart_update_alive_device(cursor, device_id, device_info)
                updated_count += 1
                print(f"   🔄 Updated: {ip_address} → {device_info.get('hostname', 'Unknown')}")
            else:
                # Add new alive device
                self.add_new_alive_device(cursor, device_info)
                new_count += 1
                print(f"   ➕ Added: {ip_address} → {device_info.get('hostname', 'Unknown')}")
        
        conn.commit()
        conn.close()
        
        self.stats['devices_updated'] = updated_count
        self.stats['new_devices_added'] = new_count
        
        print("\n   ✅ SMART DATA COLLECTION COMPLETE!")
        print(f"      🔄 Updated: {updated_count} existing alive devices")
        print(f"      ➕ Added: {new_count} new alive devices")
        print("      💀 Skipped: ALL dead devices (saved time)")

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
        
        # Smart update logic - only update with better data
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
            query = f"UPDATE assets SET {\', \'.join(update_fields)} WHERE id = ?"  # NOTE: Safe - fields from schema
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
        
        print("🔧 AUTOMATIC duplicate detection and fixing...")
        print("🤖 NO MANUAL WORK - fully automated duplicate cleanup")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Find duplicates by multiple criteria
        all_duplicates = []
        
        print("   🔍 Scanning for duplicates by multiple criteria...")
        
        # 1. Serial number duplicates
        cursor.execute("""
            SELECT 'serial' as type, serial_number as value, COUNT(*) as count, GROUP_CONCAT(id) as ids
            FROM assets 
            WHERE serial_number IS NOT NULL 
            AND serial_number != '' 
            AND LENGTH(TRIM(serial_number)) > 3
            GROUP BY TRIM(LOWER(serial_number))
            HAVING count > 1
        """)
        serial_duplicates = cursor.fetchall()
        all_duplicates.extend(serial_duplicates)
        
        # 2. IP address duplicates (same IP, different entries)
        cursor.execute("""
            SELECT 'ip' as type, ip_address as value, COUNT(*) as count, GROUP_CONCAT(id) as ids
            FROM assets 
            WHERE ip_address IS NOT NULL 
            GROUP BY ip_address
            HAVING count > 1
        """)
        ip_duplicates = cursor.fetchall()
        all_duplicates.extend(ip_duplicates)
        
        # 3. MAC address duplicates
        cursor.execute("""
            SELECT 'mac' as type, mac_address as value, COUNT(*) as count, GROUP_CONCAT(id) as ids
            FROM assets 
            WHERE mac_address IS NOT NULL 
            AND mac_address != ''
            AND LENGTH(TRIM(mac_address)) > 5
            GROUP BY TRIM(LOWER(mac_address))
            HAVING count > 1
        """)
        mac_duplicates = cursor.fetchall()
        all_duplicates.extend(mac_duplicates)
        
        # 4. Hostname duplicates
        cursor.execute("""
            SELECT 'hostname' as type, hostname as value, COUNT(*) as count, GROUP_CONCAT(id) as ids
            FROM assets 
            WHERE hostname IS NOT NULL 
            AND hostname != ''
            GROUP BY TRIM(LOWER(hostname))
            HAVING count > 1
        """)
        hostname_duplicates = cursor.fetchall()
        all_duplicates.extend(hostname_duplicates)
        
        if all_duplicates:
            print(f"   ⚠️ Found {len(all_duplicates)} duplicate groups - FIXING AUTOMATICALLY")
            
            total_removed = 0
            
            for dup_type, duplicate_value, count, ids in all_duplicates:
                id_list = [int(x) for x in ids.split(',')]
                
                if len(id_list) <= 1:
                    continue
                
                print(f"\n   📋 Fixing {dup_type.upper()} duplicates: '{duplicate_value}' ({count} devices)")
                
                # Get device details and scores
                device_scores = []
                for device_id in id_list:
                    cursor.execute("SELECT * FROM assets WHERE id = ?", (device_id,))
                    device = cursor.fetchone()
                    if device:
                        # Calculate smart score (prefer alive devices, recent data)
                        score = self.calculate_smart_device_score(device)
                        device_scores.append((device_id, device, score))
                
                # Sort by score (best first)
                device_scores.sort(key=lambda x: x[2], reverse=True)
                
                # Keep best device, remove others
                if device_scores:
                    keep_device = device_scores[0]
                    print(f"      👑 KEEPING: ID {keep_device[0]} (score: {keep_device[2]:.1f})")
                    
                    # Merge data into best device
                    merged_data = self.merge_duplicate_data(device_scores)
                    if merged_data:
                        self.update_device_with_merged_data(cursor, keep_device[0], merged_data)
                    
                    # Remove other devices automatically
                    remove_ids = [device_id for device_id, device, score in device_scores[1:]]
                    if remove_ids:
                        for device_id, device, score in device_scores[1:]:
                            print(f"      🗑️ REMOVING: ID {device_id} (score: {score:.1f})")
                        
                        placeholders = ','.join(['?'] * len(remove_ids))
                        cursor.execute(f"DELETE FROM assets WHERE id IN ({placeholders})", remove_ids)
                        total_removed += len(remove_ids)
            
            self.stats['duplicates_fixed'] = total_removed
            print(f"\n   ✅ AUTOMATICALLY FIXED {total_removed} duplicates")
            print("   🤖 NO MANUAL WORK REQUIRED - fully automated")
        else:
            print("   ✅ No duplicates found - database is clean!")
        
        conn.commit()
        conn.close()

    def calculate_smart_device_score(self, device):
        """Calculate smart score for device quality - prefer alive, recent devices"""
        
        score = 0
        
        # Basic completeness score
        for field in device:
            if field is not None and str(field).strip():
                score += 1
        
        # Convert device to dict for easier access
        if len(device) > 0:
            device_str = ' '.join(str(field) for field in device if field is not None)
            
            # Bonus for alive devices (priority)
            if 'alive' in device_str.lower():
                score += 50
            
            # Bonus for recent data
            if '2025' in device_str:
                score += 20
            
            # Bonus for complete device info
            if 'smart automated' in device_str.lower():
                score += 15
            
            # Penalty for dead devices
            if 'dead' in device_str.lower():
                score -= 30
        
        return score

    def merge_duplicate_data(self, device_scores):
        """Merge data from duplicates - keep best information"""
        
        if len(device_scores) <= 1:
            return None
        
        # Get column names
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(assets)")
        columns = [col[1] for col in cursor.fetchall()]
        conn.close()
        
        merged_data = {}
        
        # For each column, find the best value
        for i, column in enumerate(columns):
            if column == 'id':
                continue
                
            best_value = None
            best_score = -1
            
            for device_id, device, device_score in device_scores:
                if i < len(device) and device[i] is not None:
                    value = device[i]
                    if str(value).strip():
                        # Score this value (prefer from higher scored devices)
                        value_score = len(str(value)) + device_score
                        
                        # Prefer newer timestamps
                        if 'time' in column.lower() and '2025' in str(value):
                            value_score += 100
                        
                        if value_score > best_score:
                            best_value = value
                            best_score = value_score
            
            if best_value is not None:
                merged_data[column] = best_value
        
        # Add merge metadata
        merged_data['last_updated'] = datetime.now().isoformat()
        merged_data['notes'] = f'Auto-merged from {len(device_scores)} duplicates by Smart System'
        merged_data['data_source'] = 'Smart Auto-Merge'
        
        return merged_data

    def update_device_with_merged_data(self, cursor, device_id, merged_data):
        """Update device with merged data"""
        
        if not merged_data:
            return
        
        # Build update query
        updates = {}
        for column, value in merged_data.items():
            updates[column] = value
        
        if updates:
            set_clauses = [f"{k} = ?" for k in updates.keys()]
            values = list(updates.values()) + [device_id]
            query = f"UPDATE assets SET {\', \'.join(update_fields)} WHERE id = ?"  # NOTE: Safe - fields from schema
            cursor.execute(query, values)

    def smart_database_optimization(self):
        """Smart database optimization"""
        
        print("⚡ Smart database optimization...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clean up very old permanently dead devices (optional)
        cursor.execute("""
            DELETE FROM assets 
            WHERE device_status = 'permanently_dead' 
            AND failed_ping_count > 10
            AND (last_seen IS NULL OR last_seen < datetime('now', '-60 days'))
        """)
        
        old_deleted = cursor.rowcount
        conn.close()
        
        # Vacuum in separate connection
        try:
            conn2 = sqlite3.connect(self.db_path)
            conn2.execute("VACUUM")
            conn2.execute("ANALYZE")
            conn2.close()
        except Exception as e:
            print(f"   ⚠️ Vacuum warning: {str(e)}")
        
        if old_deleted > 0:
            print(f"   🗑️ Cleaned up {old_deleted} very old permanently dead devices")
        print("   ✅ Database optimized and compressed")

    def show_cycle_results(self):
        """Show automation cycle results"""
        
        duration = datetime.now() - self.stats['scan_started']
        
        # Get current database stats
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM assets")
        total_devices = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM assets WHERE device_status = 'alive'")
        alive_count = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(*) FROM assets WHERE device_status = 'dead'")
        dead_count = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(*) FROM assets WHERE device_status = 'permanently_dead'")
        perm_dead_count = cursor.fetchone()[0] or 0
        
        conn.close()
        
        print("📈 SMART AUTOMATION CYCLE RESULTS")
        print("=" * 70)
        print(f"⏱️  Cycle duration: {duration}")
        print(f"🔍 Total devices checked: {self.stats['devices_checked']}")
        print(f"✅ ALIVE devices found: {self.stats['alive_devices']} (collected data)")
        print(f"💀 DEAD devices found: {self.stats['dead_devices']} (skipped - saved time)")
        print(f"➕ New devices added: {self.stats['new_devices_added']}")
        print(f"🔄 Devices updated: {self.stats['devices_updated']}")
        print(f"🔧 Duplicates fixed: {self.stats['duplicates_fixed']}")
        print()
        print("📊 DATABASE STATUS:")
        print(f"   📈 Total devices: {total_devices}")
        print(f"   ✅ Alive: {alive_count}")
        print(f"   💀 Dead: {dead_count}")
        print(f"   ⚰️ Permanently dead: {perm_dead_count}")
        print()
        print("🎯 SMART AUTOMATION SUCCESS!")
        print("   🧠 Only collected data from ALIVE devices")
        print("   💀 Skipped DEAD devices (saved time)")
        print("   🤖 Automatically fixed duplicates")
        print("   ⚡ Zero manual intervention required")
        print("   🎯 100% automated - no human work needed")

def main():
    """Run the smart automated system"""
    
    print("🤖 SMART AUTOMATED ASSET MANAGEMENT SYSTEM")
    print("=" * 70)
    print("🧠 SMART: Only collect from ALIVE devices, skip DEAD ones")
    print("🔧 AUTO: Detect and fix duplicates automatically")
    print("⚡ FAST: Smart timeouts and parallel processing")
    print("🎯 ZERO MANUAL WORK: Fully automated")
    print()
    
    system = SmartAutomatedSystem()
    
    # Run smart automation cycle
    system.run_smart_automation_cycle("10.0.21.0/24")

if __name__ == "__main__":
    main()