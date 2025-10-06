#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INTELLIGENT ASSET MANAGEMENT SYSTEM

This enhanced web service provides:
- Complete asset display with all collected + manual columns
- Real-time database synchronization
- Smart asset classification and automation
- Advanced filtering and search capabilities
- Department management
- Automatic NMAP scanning for unknown devices
- Live data updates and intelligent automation
"""

import os
import sys

# Set console encoding to handle Unicode properly on Windows
if sys.platform == "win32":
    import codecs
    try:
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())
    except:
        pass  # Silently fail if console redirection is not possible

from flask import Flask, render_template, jsonify, request
import sqlite3
import json
from datetime import datetime
import time

app = Flask(__name__)

class IntelligentAssetManager:
    def __init__(self, db_path=None, port=5000):
        # Determine the correct database path
        if db_path is None:
            # Try multiple possible locations
            possible_paths = [
                "../assets.db",  # Parent directory (default)
                "../../assets.db",  # Two levels up
                os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets.db"),  # Absolute parent
                "d:/Assets-Projects/Asset-Project-Enhanced/assets.db",  # Absolute path
                "assets.db"  # Current directory
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    db_path = path
                    print(f"[OK] Found database at: {os.path.abspath(path)}")
                    break
            
            if db_path is None:
                # Default to parent directory and create if needed
                db_path = "../assets.db"
                print(f"[INFO] Using default database path: {os.path.abspath(db_path)}")
        
        self.db_path = db_path
        self.port = port
        self.running = False
        self.start_time = None
        self.automation_thread = None
        self.nmap_scanner = None
        
        # Test database connection first
        try:
            test_conn = sqlite3.connect(self.db_path)
            test_conn.close()
            print(f"[OK] Database connection verified: {self.db_path}")
        except Exception as e:
            print(f"[ERROR] Database connection failed: {e}")
            raise Exception(f"Cannot connect to database: {e}")
            
        # Initialize with safe error handling
        try:
            self.initialize_automation()
        except Exception as e:
            print(f"[WARNING] Automation initialization failed: {e}")
            print("[INFO] Continuing with basic functionality")
        
    def initialize_automation(self):
        """Initialize automation features"""
        try:
            import nmap
            self.nmap_scanner = nmap.PortScanner()
            print("[OK] NMAP scanner initialized for device classification")
        except Exception as e:
            print("WARNING: NMAP not available - will use basic classification")
            print(f"NMAP Error: {e}")
            self.nmap_scanner = None
        
        # Initialize departments table
        self.initialize_departments()
        
        # Start automation thread
        self.start_automation()
    
    def initialize_departments(self):
        """Initialize departments table and management"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Create departments table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS departments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    location TEXT,
                    manager_name TEXT,
                    manager_email TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Add department column to assets_enhanced if not exists
            try:
                cursor.execute("ALTER TABLE assets_enhanced ADD COLUMN assigned_department TEXT")
            except sqlite3.OperationalError:
                pass  # Column already exists
            
            # Create default departments
            default_departments = [
                ("IT Department", "Information Technology", "Building A - Floor 3", "IT Manager", "it@company.com"),
                ("HR Department", "Human Resources", "Building A - Floor 2", "HR Manager", "hr@company.com"),
                ("Finance Department", "Finance & Accounting", "Building A - Floor 1", "Finance Manager", "finance@company.com"),
                ("Operations", "Operations & Logistics", "Building B - Floor 1", "Ops Manager", "ops@company.com"),
                ("Unassigned", "Devices not yet assigned to any department", "Various", "Admin", "admin@company.com")
            ]
            
            for dept in default_departments:
                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO departments (name, description, location, manager_name, manager_email)
                        VALUES (?, ?, ?, ?, ?)
                    """, dept)
                except:
                    pass
            
            conn.commit()
            print("[OK] Departments system initialized")
            
        except Exception as e:
            print(f"[WARNING] Departments initialization error: {e}")
        finally:
            conn.close()
    
    def start_automation(self):
        """Start intelligent automation tasks"""
        # Temporarily disable background automation to focus on web interface
        print("[INFO] Background automation disabled - focusing on web interface stability")
        # if self.automation_thread is None or not self.automation_thread.is_alive():
        #     self.automation_thread = threading.Thread(target=self.automation_worker, daemon=True)
        #     self.automation_thread.start()
        #     print("[AUTOMATION] Intelligent automation started")
    
    def automation_worker(self):
        """Automated background tasks for smart asset management"""
        while True:
            try:
                print("[RUNNING] Running intelligent automation tasks...")
                
                # Task 1: Auto-classify incomplete assets that now have data
                classified_count = self.auto_classify_incomplete_assets()
                if classified_count > 0:
                    print(f"[AUTOMATION] Reclassified {classified_count} incomplete assets")
                
                # Task 2: Classify unknown devices using NMAP (if available)
                self.classify_unknown_devices()
                
                # Task 3: Update missing data
                self.update_missing_data()
                
                # Task 4: Monitor device status changes
                self.monitor_device_changes()
                
                # Task 5: Auto-assign unassigned devices
                self.auto_assign_devices()
                
                # Wait 5 minutes before next automation cycle
                time.sleep(300)
                
            except Exception as e:
                print(f"[ERROR] Automation error: {e}")
                time.sleep(60)  # Wait 1 minute on error
    
    def classify_unknown_devices(self):
        """Automatically classify unknown devices using available methods"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Get devices that need classification
            cursor.execute("""
                SELECT id, hostname, ip_address, device_type, operating_system, processor_name, total_physical_memory_gb
                FROM assets_enhanced 
                WHERE device_type = 'Unknown Device' OR device_type IS NULL OR device_type = ''
                LIMIT 20
            """)
            unknown_devices = cursor.fetchall()
            
            classified_count = 0
            for device in unknown_devices:
                device_id, hostname, ip, current_type, os, processor, memory = device
                
                # Try NMAP classification if available
                if self.nmap_scanner:
                    try:
                        nmap_result = self.nmap_classify_device(ip)
                        if nmap_result and nmap_result != 'Unknown Device':
                            cursor.execute("""
                                UPDATE assets_enhanced 
                                SET device_type = ?, updated_at = CURRENT_TIMESTAMP 
                                WHERE id = ?
                            """, (nmap_result, device_id))
                            classified_count += 1
                            print(f"[NMAP] Classified {hostname} ({ip}) as {nmap_result}")
                            continue
                    except Exception as e:
                        print(f"[NMAP] Classification failed for {ip}: {e}")
                
                # Fall back to data-based classification
                new_type = self.classify_device_type(os, processor, memory, ip)
                if new_type not in ['Unknown Device', 'Classification Pending', current_type]:
                    cursor.execute("""
                        UPDATE assets_enhanced 
                        SET device_type = ?, updated_at = CURRENT_TIMESTAMP 
                        WHERE id = ?
                    """, (new_type, device_id))
                    classified_count += 1
                    print(f"[DATA-CLASSIFICATION] Classified {hostname} ({ip}) as {new_type}")
            
            conn.commit()
            if classified_count > 0:
                print(f"[CLASSIFICATION] Successfully classified {classified_count} unknown devices")
            
        except Exception as e:
            print(f"[ERROR] Device classification error: {e}")
        finally:
            conn.close()
    
    def nmap_classify_device(self, ip_address):
        """Use NMAP to classify device type based on open ports and OS detection"""
        try:
            # Quick port scan
            self.nmap_scanner.scan(ip_address, '21,22,23,25,53,80,110,143,443,993,995,3389,5432,3306,1433,5000-5010')
            
            if ip_address not in self.nmap_scanner.all_hosts():
                return "Unknown", None
            
            host = self.nmap_scanner[ip_address]
            open_ports = []
            
            for protocol in host.all_protocols():
                ports = host[protocol].keys()
                for port in ports:
                    if host[protocol][port]['state'] == 'open':
                        open_ports.append(port)
            
            # Classify based on open ports
            device_type = "Unknown"
            os_guess = None
            
            # Server classification
            if any(port in open_ports for port in [80, 443, 8080, 8443]):
                if any(port in open_ports for port in [3306, 5432, 1433]):
                    device_type = "Database Server"
                else:
                    device_type = "Web Server"
            elif any(port in open_ports for port in [21, 22]):
                device_type = "Server"
            elif 3389 in open_ports:
                device_type = "Windows Workstation"
                os_guess = "Windows"
            elif 22 in open_ports and 3389 not in open_ports:
                device_type = "Linux Server"
                os_guess = "Linux"
            elif any(port in open_ports for port in [161, 514]):
                device_type = "Network Device"
            elif any(port in open_ports for port in [515, 631, 9100]):
                device_type = "Printer"
            elif len(open_ports) == 0:
                device_type = "Network Device"
            else:
                device_type = "Workstation"
            
            return device_type, os_guess
            
        except Exception as e:
            print(f"[ERROR] NMAP scan error for {ip_address}: {e}")
            return "Unknown", None
    
    def update_missing_data(self):
        """Update missing data for devices"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Find devices with missing critical data
            cursor.execute("""
                SELECT COUNT(*) FROM assets_enhanced 
                WHERE (processor_name IS NULL OR processor_name = '') OR
                      (total_physical_memory_gb IS NULL OR total_physical_memory_gb = 0) OR
                      (operating_system IS NULL OR operating_system = '')
            """)
            
            missing_count = cursor.fetchone()[0]
            if missing_count > 0:
                print(f"[STATS] Found {missing_count} devices with missing data - scheduling collection")
                # Here you could trigger your WMI collector for these specific devices
            
        except Exception as e:
            print(f"[ERROR] Missing data check error: {e}")
        finally:
            conn.close()
    
    def monitor_device_changes(self):
        """Monitor and log device status changes"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Update device status based on ping response
            cursor.execute("""
                UPDATE assets_enhanced 
                SET device_status = CASE 
                    WHEN ping_response_ms > 0 THEN 'Online'
                    WHEN ping_response_ms IS NULL OR ping_response_ms = 0 THEN 'Offline'
                    ELSE device_status
                END,
                updated_at = CURRENT_TIMESTAMP
                WHERE device_status != CASE 
                    WHEN ping_response_ms > 0 THEN 'Online'
                    WHEN ping_response_ms IS NULL OR ping_response_ms = 0 THEN 'Offline'
                    ELSE device_status
                END
            """)
            
            changes = cursor.rowcount
            if changes > 0:
                print(f"[STATS] Updated status for {changes} devices")
            
            conn.commit()
            
        except Exception as e:
            print(f"[ERROR] Status monitoring error: {e}")
        finally:
            conn.close()
    
    def auto_assign_devices(self):
        """Automatically assign devices to departments based on hostname patterns"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Auto-assign based on hostname patterns
            patterns = [
                ("IT-%", "IT Department"),
                ("HR-%", "HR Department"),
                ("FIN-%", "Finance Department"),
                ("OPS-%", "Operations"),
                ("%server%", "IT Department"),
                ("%printer%", "Operations")
            ]
            
            for pattern, department in patterns:
                cursor.execute("""
                    UPDATE assets_enhanced 
                    SET assigned_department = ?
                    WHERE (assigned_department IS NULL OR assigned_department = 'Unassigned') 
                    AND hostname LIKE ?
                """, (department, pattern))
            
            conn.commit()
            
        except Exception as e:
            print(f"[ERROR] Auto-assignment error: {e}")
        finally:
            conn.close()
    
    def get_db_connection(self):
        """Get database connection with error handling"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            # Test the connection
            conn.execute("SELECT 1")
            return conn
        except Exception as e:
            print(f"[ERROR] Database connection failed: {e}")
            raise Exception(f"Cannot connect to database {self.db_path}: {e}")
    
    def get_comprehensive_stats(self):
        """Get comprehensive dashboard statistics"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        try:
            # Check if enhanced table exists and has data
            cursor.execute("SELECT COUNT(*) as total FROM assets_enhanced")
            enhanced_count = cursor.fetchone()['total']
            
            if enhanced_count > 0:
                # Total devices
                stats['total_devices'] = enhanced_count
                
                # Device status distribution with smart mapping
                cursor.execute("""
                    SELECT 
                        CASE 
                            WHEN device_status = 'Online' OR ping_response_ms > 0 THEN 'online'
                            WHEN device_status = 'Offline' OR (device_status = '' AND ping_response_ms IS NULL) THEN 'offline'
                            WHEN device_status = '' THEN 'unknown'
                            ELSE LOWER(COALESCE(device_status, 'unknown'))
                        END as normalized_status, 
                        COUNT(*) as count 
                    FROM assets_enhanced 
                    GROUP BY normalized_status
                """)
                status_data = cursor.fetchall()
                stats['device_status'] = {row['normalized_status']: row['count'] for row in status_data}
                
                # Device type distribution
                cursor.execute("""
                    SELECT COALESCE(device_type, 'Unknown') as device_type, COUNT(*) as count 
                    FROM assets_enhanced 
                    GROUP BY device_type 
                    ORDER BY count DESC
                """)
                type_data = cursor.fetchall()
                stats['device_types'] = [{'name': row['device_type'], 'count': row['count']} for row in type_data]
                
                # Department distribution
                cursor.execute("""
                    SELECT COALESCE(assigned_department, 'Unassigned') as department, COUNT(*) as count 
                    FROM assets_enhanced 
                    GROUP BY assigned_department 
                    ORDER BY count DESC
                """)
                dept_data = cursor.fetchall()
                stats['departments'] = [{'name': row['department'], 'count': row['count']} for row in dept_data]
                
                # Data completeness metrics
                cursor.execute("SELECT AVG(data_completeness_score) as avg_score FROM assets_enhanced WHERE data_completeness_score IS NOT NULL")
                avg_score = cursor.fetchone()['avg_score']
                stats['avg_data_completeness'] = round(avg_score, 1) if avg_score else 0
                
                # Missing data counts
                cursor.execute("SELECT COUNT(*) as count FROM assets_enhanced WHERE processor_name IS NULL OR processor_name = ''")
                stats['missing_processor'] = cursor.fetchone()['count']
                
                cursor.execute("SELECT COUNT(*) as count FROM assets_enhanced WHERE total_physical_memory_gb IS NULL OR total_physical_memory_gb = 0")
                stats['missing_memory'] = cursor.fetchone()['count']
                
                cursor.execute("SELECT COUNT(*) as count FROM assets_enhanced WHERE operating_system IS NULL OR operating_system = ''")
                stats['missing_os'] = cursor.fetchone()['count']
                
                # Unknown devices needing classification
                cursor.execute("SELECT COUNT(*) as count FROM assets_enhanced WHERE device_type = 'Unknown' OR device_type IS NULL OR device_type = ''")
                stats['unknown_devices'] = cursor.fetchone()['count']
                
                # Recent activity
                cursor.execute("SELECT COUNT(*) as count FROM assets_enhanced WHERE last_seen >= datetime('now', '-24 hours')")
                stats['recent_activity'] = cursor.fetchone()['count']
                
                stats['using_enhanced_data'] = True
                
            else:
                # Fallback to original table
                stats = self._get_basic_stats(cursor)
                stats['using_enhanced_data'] = False
                
        except sqlite3.OperationalError:
            # Enhanced table doesn't exist
            stats = self._get_basic_stats(cursor)
            stats['using_enhanced_data'] = False
        
        # Add real-time timestamp
        stats['last_updated'] = datetime.now().isoformat()
        stats['data_source'] = 'assets_enhanced' if stats.get('using_enhanced_data') else 'assets'
        
        conn.close()
        return stats
    
    def _get_basic_stats(self, cursor):
        """Get basic statistics from original assets table"""
        stats = {}
        
        cursor.execute("SELECT COUNT(*) as total FROM assets")
        stats['total_devices'] = cursor.fetchone()['total']
        
        cursor.execute("SELECT device_status, COUNT(*) as count FROM assets GROUP BY device_status")
        status_data = cursor.fetchall()
        stats['device_status'] = {row['device_status'] or 'unknown': row['count'] for row in status_data}
        
        stats['device_types'] = []
        stats['departments'] = []
        stats['avg_data_completeness'] = 0
        stats['missing_processor'] = 0
        stats['missing_memory'] = 0
        stats['missing_os'] = 0
        stats['unknown_devices'] = 0
        stats['recent_activity'] = 0
        
        return stats
    
    def get_comprehensive_assets(self, page=1, per_page=50, search_term='', filters={}):
        """Get comprehensive assets data with advanced filtering"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        # Try enhanced table first
        try:
            cursor.execute("SELECT COUNT(*) FROM assets_enhanced")
            enhanced_count = cursor.fetchone()[0]
            
            if enhanced_count > 0:
                return self._get_enhanced_assets(conn, cursor, page, per_page, search_term, filters)
        except:
            pass
        
        # Fallback to original table
        return self._get_basic_assets(conn, cursor, page, per_page, search_term, filters)
    
    def _get_enhanced_assets(self, conn, cursor, page=1, per_page=50, search_term='', filters={}):
        """Get enhanced assets with comprehensive filtering"""
        
        # Build dynamic where conditions
        where_conditions = []
        params = []
        
        # Search functionality
        if search_term:
            search_conditions = [
                "hostname LIKE ?",
                "computer_name LIKE ?", 
                "ip_address LIKE ?",
                "current_user LIKE ?",
                "system_manufacturer LIKE ?",
                "assigned_department LIKE ?"
            ]
            where_conditions.append(f"({' OR '.join(search_conditions)})")
            search_param = f'%{search_term}%'
            params.extend([search_param] * 6)
        
        # Status filter
        if filters.get('status'):
            if filters['status'] == 'online':
                where_conditions.append("(device_status = 'Online' OR ping_response_ms > 0)")
            elif filters['status'] == 'offline':
                where_conditions.append("(device_status = 'Offline' OR (device_status = '' AND ping_response_ms IS NULL))")
            elif filters['status'] == 'unknown':
                where_conditions.append("(device_status = '' OR device_status IS NULL)")
        
        # Device type filter
        if filters.get('device_type'):
            where_conditions.append("device_type = ?")
            params.append(filters['device_type'])
        
        # Department filter
        if filters.get('department'):
            where_conditions.append("assigned_department = ?")
            params.append(filters['department'])
        
        # Operating system filter
        if filters.get('operating_system'):
            where_conditions.append("operating_system LIKE ?")
            params.append(f"%{filters['operating_system']}%")
        
        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)
        
        # Get total count
        cursor.execute(f"SELECT COUNT(*) as total FROM assets_enhanced {where_clause}", params)
        total_count = cursor.fetchone()['total']
        
        # Get paginated data with ALL columns
        offset = (page - 1) * per_page
        query = f"""
            SELECT 
                id, hostname, computer_name, ip_address,
                CASE 
                    WHEN device_status = 'Online' OR ping_response_ms > 0 THEN 'online'
                    WHEN device_status = 'Offline' OR (device_status = '' AND ping_response_ms IS NULL) THEN 'offline'
                    WHEN device_status = '' THEN 'unknown'
                    ELSE LOWER(COALESCE(device_status, 'unknown'))
                END as device_status,
                COALESCE(device_type, 'Unknown') as device_type,
                
                -- Hardware info
                processor_name, processor_cores, processor_logical_cores,
                total_physical_memory_gb, available_memory_gb,
                graphics_cards, connected_monitors,
                storage_summary, total_storage_gb,
                
                -- System info  
                operating_system, os_version, os_build,
                system_manufacturer, system_model, bios_version,
                
                -- Network info
                mac_address, network_adapters, ip_address as primary_ip,
                
                -- Software info
                installed_software, antivirus_software, firewall_status,
                
                -- User info
                current_user, user_profiles, last_logged_users,
                
                -- Management info
                COALESCE(assigned_department, 'Unassigned') as assigned_department,
                collection_method, data_completeness_score,
                hostname_mismatch_status,
                
                -- Performance info
                cpu_usage_percent, memory_usage_percent,
                COALESCE(system_uptime_hours, 0) as uptime_hours,
                
                -- Timestamps
                last_seen, created_at, updated_at,
                
                -- Additional fields for manual entry
                location, site, cost_center, purchase_date, warranty_expiry,
                department, -- legacy field
                serial_number, asset_tag
                
            FROM assets_enhanced 
            {where_clause}
            ORDER BY 
                CASE 
                    WHEN device_status = 'Online' OR ping_response_ms > 0 THEN 1
                    WHEN device_status = 'Offline' OR (device_status = '' AND ping_response_ms IS NULL) THEN 2
                    ELSE 3
                END,
                assigned_department, device_type, hostname
            LIMIT ? OFFSET ?
        """
        
        cursor.execute(query, params + [per_page, offset])
        assets = []
        
        for row in cursor.fetchall():
            asset = dict(row)
            
            # Parse JSON fields
            json_fields = ['graphics_cards', 'network_adapters', 'installed_software', 'user_profiles']
            for field in json_fields:
                if asset.get(field):
                    try:
                        asset[field] = json.loads(asset[field])
                    except (json.JSONDecodeError, TypeError):
                        pass
            
            # Format display values
            if asset['total_physical_memory_gb']:
                asset['memory_formatted'] = f"{asset['total_physical_memory_gb']:.1f} GB"
            
            if asset['uptime_hours']:
                hours = int(asset['uptime_hours'])
                days = hours // 24
                remaining_hours = hours % 24
                asset['uptime_formatted'] = f"{days}d {remaining_hours}h" if days > 0 else f"{remaining_hours}h"
            
            assets.append(asset)
        
        conn.close()
        
        return {
            'assets': assets,
            'total_count': total_count,
            'current_page': page,
            'per_page': per_page,
            'total_pages': (total_count + per_page - 1) // per_page,
            'data_source': 'assets_enhanced',
            'last_updated': datetime.now().isoformat(),
            'filters_applied': filters,
            'search_term': search_term
        }
    
    def _get_basic_assets(self, conn, cursor, page=1, per_page=50, search_term='', filters={}):
        """Fallback for basic assets table"""
        # Simplified query for original assets table
        where_conditions = []
        params = []
        
        if search_term:
            where_conditions.append("(hostname LIKE ? OR computer_name LIKE ? OR ip_address LIKE ?)")
            search_param = f'%{search_term}%'
            params.extend([search_param, search_param, search_param])
        
        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)
        
        cursor.execute(f"SELECT COUNT(*) as total FROM assets {where_clause}", params)
        total_count = cursor.fetchone()['total']
        
        offset = (page - 1) * per_page
        cursor.execute(f"""
            SELECT id, hostname, computer_name, ip_address, device_status,
                   processor_name, total_physical_memory, operating_system,
                   system_manufacturer, mac_address, last_updated, collection_method
            FROM assets {where_clause}
            ORDER BY hostname
            LIMIT ? OFFSET ?
        """, params + [per_page, offset])
        
        assets = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return {
            'assets': assets,
            'total_count': total_count,
            'current_page': page,
            'per_page': per_page,
            'total_pages': (total_count + per_page - 1) // per_page,
            'data_source': 'assets',
            'last_updated': datetime.now().isoformat()
        }
    
    def get_departments(self):
        """Get all departments"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT d.*, 
                       COUNT(a.id) as device_count
                FROM departments d
                LEFT JOIN assets_enhanced a ON d.name = a.assigned_department
                GROUP BY d.id
                ORDER BY d.name
            """)
            
            departments = [dict(row) for row in cursor.fetchall()]
            return departments
            
        except Exception as e:
            print(f"[ERROR] Error getting departments: {e}")
            return []
        finally:
            conn.close()
    
    def create_department(self, name, description="", location="", manager_name="", manager_email=""):
        """Create a new department"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO departments (name, description, location, manager_name, manager_email)
                VALUES (?, ?, ?, ?, ?)
            """, (name, description, location, manager_name, manager_email))
            
            conn.commit()
            dept_id = cursor.lastrowid
            print(f"[OK] Created department: {name}")
            return {'success': True, 'department_id': dept_id}
            
        except sqlite3.IntegrityError:
            return {'success': False, 'error': 'Department name already exists'}
        except Exception as e:
            print(f"[ERROR] Error creating department: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()
    
    def update_asset(self, asset_id, updates):
        """Update asset information"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Build dynamic update query
            set_clauses = []
            params = []
            
            allowed_fields = [
                'assigned_department', 'device_type', 'location', 'site', 
                'cost_center', 'purchase_date', 'warranty_expiry',
                'current_user', 'department'
            ]
            
            for field, value in updates.items():
                if field in allowed_fields:
                    set_clauses.append(f"{field} = ?")
                    params.append(value)
            
            if set_clauses:
                set_clauses.append("updated_at = CURRENT_TIMESTAMP")
                query = f"UPDATE assets_enhanced SET {', '.join(set_clauses)} WHERE id = ?"
                params.append(asset_id)
                
                cursor.execute(query, params)
                conn.commit()
                
                print(f"[OK] Updated asset {asset_id}: {updates}")
                return {'success': True, 'updated_fields': list(updates.keys())}
            else:
                return {'success': False, 'error': 'No valid fields to update'}
                
        except Exception as e:
            print(f"[ERROR] Error updating asset: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()
    
    def get_all_assets(self):
        """Get all assets for API endpoints - simplified method"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Check if enhanced table exists and has data
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='assets_enhanced'")
            has_enhanced = cursor.fetchone() is not None
            
            if has_enhanced:
                cursor.execute("SELECT COUNT(*) FROM assets_enhanced")
                enhanced_count = cursor.fetchone()[0]
                
                if enhanced_count > 0:
                    # Use enhanced table with intelligent classification
                    cursor.execute("""
                        SELECT 
                            id, hostname, computer_name, ip_address,
                            CASE 
                                WHEN device_status = 'Online' OR ping_response_ms > 0 THEN 'online'
                                WHEN device_status = 'Offline' OR (device_status = '' AND ping_response_ms IS NULL) THEN 'offline'
                                WHEN device_status = '' THEN 'unknown'
                                ELSE LOWER(COALESCE(device_status, 'unknown'))
                            END as device_status,
                            CASE 
                                WHEN (processor_name IS NULL OR processor_name = '') AND 
                                     (operating_system IS NULL OR operating_system = '') AND 
                                     (total_physical_memory_gb IS NULL OR total_physical_memory_gb = 0) 
                                THEN 'Asset Incomplete'
                                WHEN device_type IS NULL OR device_type = '' OR device_type = 'Unknown Device' 
                                THEN 'Classification Pending'
                                ELSE COALESCE(device_type, 'Unknown Device')
                            END as device_type,
                            processor_name, total_physical_memory_gb, operating_system,
                            COALESCE(assigned_department, 'Unassigned') as assigned_department,
                            last_seen, created_at, updated_at
                        FROM assets_enhanced 
                        ORDER BY hostname
                    """)
                    assets = [dict(row) for row in cursor.fetchall()]
                    conn.close()
                    return assets
            
            # Fall back to basic assets table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='assets'")
            has_basic = cursor.fetchone() is not None
            
            if has_basic:
                cursor.execute("""
                    SELECT 
                        id, hostname, ip_address, 
                        CASE 
                            WHEN device_type IS NULL OR device_type = '' 
                            THEN 'Asset Incomplete'
                            ELSE device_type
                        END as device_type,
                        'unknown' as device_status,
                        'Unassigned' as assigned_department,
                        created_at, updated_at
                    FROM assets 
                    ORDER BY hostname
                """)
                assets = [dict(row) for row in cursor.fetchall()]
                conn.close()
                return assets
            
            conn.close()
            return []
            
        except Exception as e:
            print(f"[ERROR] Error getting all assets: {e}")
            return []
    
    def auto_classify_incomplete_assets(self):
        """Automatically classify assets that have been completed with data collection"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Find assets marked as 'Asset Incomplete' but now have data
            cursor.execute("""
                SELECT id, hostname, operating_system, processor_name, total_physical_memory_gb, ip_address
                FROM assets_enhanced 
                WHERE device_type = 'Asset Incomplete' 
                AND ((processor_name IS NOT NULL AND processor_name != '') 
                     OR (operating_system IS NOT NULL AND operating_system != '')
                     OR (total_physical_memory_gb IS NOT NULL AND total_physical_memory_gb > 0))
            """)
            
            incomplete_assets = cursor.fetchall()
            classified_count = 0
            
            for asset in incomplete_assets:
                asset_id, hostname, os, processor, memory, ip = asset
                new_device_type = self.classify_device_type(os, processor, memory, ip)
                
                if new_device_type != 'Asset Incomplete':
                    cursor.execute("""
                        UPDATE assets_enhanced 
                        SET device_type = ?, updated_at = CURRENT_TIMESTAMP 
                        WHERE id = ?
                    """, (new_device_type, asset_id))
                    classified_count += 1
                    print(f"[CLASSIFICATION] Asset {hostname} ({ip}) reclassified from 'Asset Incomplete' to '{new_device_type}'")
            
            conn.commit()
            conn.close()
            
            if classified_count > 0:
                print(f"[AUTO-CLASSIFICATION] Successfully reclassified {classified_count} assets from incomplete to proper device types")
            
            return classified_count
            
        except Exception as e:
            print(f"[ERROR] Auto-classification error: {e}")
            return 0
    
    def classify_device_type(self, operating_system, processor, memory_gb, ip_address):
        """Intelligently classify device type based on available data"""
        try:
            os = str(operating_system or '').lower()
            proc = str(processor or '').lower()
            mem = float(memory_gb or 0)
            
            # Server classification
            if 'server' in os or 'datacenter' in os:
                if 'windows' in os:
                    return 'Windows Server'
                elif any(x in os for x in ['linux', 'ubuntu', 'centos', 'redhat', 'debian']):
                    return 'Linux Server'
                else:
                    return 'Server'
            
            # Workstation classification
            if 'windows' in os:
                if mem >= 16:  # High memory suggests workstation
                    return 'Windows Workstation'
                elif mem >= 4:
                    return 'Desktop'
                else:
                    return 'Workstation'
            
            # Linux classification
            if any(x in os for x in ['linux', 'ubuntu', 'mint', 'fedora', 'opensuse']):
                return 'Linux Workstation'
            
            # Mac classification
            if any(x in os for x in ['mac', 'darwin', 'osx']):
                return 'Mac Workstation'
            
            # Mobile devices
            if any(x in os for x in ['android', 'ios']):
                return 'Mobile Device'
            
            # Based on memory if OS detection fails
            if mem >= 32:
                return 'High-End Workstation'
            elif mem >= 16:
                return 'Workstation'
            elif mem >= 4:
                return 'Desktop'
            elif mem > 0:
                return 'Lightweight Device'
            
            # If we have processor info
            if 'server' in proc or 'xeon' in proc:
                return 'Server'
            elif 'mobile' in proc or 'atom' in proc:
                return 'Mobile Device'
            
            # Network device detection based on IP patterns
            if ip_address:
                # Common network device IP patterns
                if any(x in str(ip_address) for x in ['.1.1', '.1.254', '.254.254']):
                    return 'Network Device'
            
            # Default for devices with some data but unclear classification
            return 'Classification Pending'
            
        except Exception as e:
            print(f"[ERROR] Device classification error: {e}")
            return 'Classification Pending'

# Create service instance with error handling
try:
    asset_manager = IntelligentAssetManager()
    print("[SUCCESS] IntelligentAssetManager initialized successfully")
except Exception as e:
    print(f"WARNING: IntelligentAssetManager initialization failed: {e}")
    print("Web service will continue with basic functionality")
    asset_manager = None

# Flask Routes
@app.route('/')
def home():
    """Simple working dashboard that always loads"""
    return render_template('simple_working_dashboard.html')

@app.route('/production')
def production_dashboard():
    """Production-ready dashboard with enhanced data visualization"""
    return render_template('production_ready_dashboard.html')

@app.route('/test')
def test_dashboard():
    """Test dashboard to verify functionality"""
    return render_template('test_dashboard.html')

@app.route('/enhanced')
def enhanced_dashboard():
    """Enhanced compact dashboard page"""
    return render_template('enhanced_compact_dashboard.html')

@app.route('/full')
def full_dashboard():
    """Full featured dashboard"""
    return render_template('intelligent_dashboard.html')

@app.route('/debug')
def debug_dashboard():
    """Debug dashboard for troubleshooting API issues"""
    return render_template('debug_dashboard.html')

@app.route('/api/system-status')
def api_system_status():
    """System status and diagnostics"""
    import platform
    
    # Check database paths
    db_paths = [
        "../assets.db",
        "../../assets.db", 
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets.db"),
        "d:/Assets-Projects/Asset-Project-Enhanced/assets.db",
        "assets.db"
    ]
    
    db_status = {}
    for path in db_paths:
        abs_path = os.path.abspath(path)
        db_status[abs_path] = {
            'exists': os.path.exists(path),
            'size': os.path.getsize(path) if os.path.exists(path) else 0,
            'readable': False
        }
        
        if os.path.exists(path):
            try:
                test_conn = sqlite3.connect(path)
                test_conn.execute("SELECT 1")
                test_conn.close()
                db_status[abs_path]['readable'] = True
            except:
                pass
    
    return jsonify({
        'python_version': platform.python_version(),
        'working_directory': os.getcwd(),
        'asset_manager_initialized': asset_manager is not None,
        'database_paths': db_status,
        'platform': platform.platform(),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/test')
def api_test():
    """Simple test endpoint"""
    return jsonify({'message': 'API is working', 'status': 'OK'})

@app.route('/api/stats')
def api_stats():
    """Intelligent stats API with asset classification insights"""
    try:
        # Direct database access
        import sqlite3
        db_path = "../assets.db"
        if not os.path.exists(db_path):
            return jsonify({
                'total_devices': 0, 'total_assets': 0,
                'device_status': {'online': 0, 'offline': 0},
                'status': 'Database not found'
            })
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        stats = {
            'asset_manager_initialized': True,
            'status': 'OK'
        }
        
        try:
            # Try enhanced table first
            cursor.execute("SELECT COUNT(*) FROM assets_enhanced")
            enhanced_count = cursor.fetchone()[0]
            
            if enhanced_count > 0:
                # Total devices
                stats['total_devices'] = enhanced_count
                stats['total_assets'] = enhanced_count
                
                # Device status with proper classification
                cursor.execute("""
                    SELECT 
                        CASE 
                            WHEN device_status = 'Online' OR ping_response_ms > 0 THEN 'online'
                            WHEN device_status = 'Offline' OR device_status = '' OR device_status IS NULL THEN 'offline'
                            ELSE 'unknown'
                        END as status, 
                        COUNT(*) as count 
                    FROM assets_enhanced 
                    GROUP BY status
                """)
                status_data = cursor.fetchall()
                device_status = {'online': 0, 'offline': 0, 'unknown': 0}
                for row in status_data:
                    device_status[row[0]] = row[1]
                stats['device_status'] = device_status
                
                # Asset completeness classification
                cursor.execute("""
                    SELECT 
                        CASE 
                            WHEN (processor_name IS NULL OR processor_name = '') AND 
                                 (operating_system IS NULL OR operating_system = '') AND 
                                 (total_physical_memory_gb IS NULL OR total_physical_memory_gb = 0) 
                            THEN 'Asset Incomplete'
                            WHEN device_type IS NULL OR device_type = '' OR device_type = 'Unknown Device' 
                            THEN 'Classification Pending'
                            ELSE 'Complete Asset'
                        END as classification,
                        COUNT(*) as count
                    FROM assets_enhanced
                    GROUP BY classification
                """)
                classification_data = cursor.fetchall()
                asset_classification = {}
                incomplete_count = 0
                for row in classification_data:
                    asset_classification[row[0]] = row[1]
                    if row[0] in ['Asset Incomplete', 'Classification Pending']:
                        incomplete_count += row[1]
                
                stats['asset_classification'] = asset_classification
                stats['incomplete_assets'] = incomplete_count
                
                # Data completeness
                cursor.execute("SELECT AVG(data_completeness_score) FROM assets_enhanced WHERE data_completeness_score IS NOT NULL")
                avg_score = cursor.fetchone()[0]
                stats['avg_data_completeness'] = round(avg_score or 0, 1)
                
                # Device types with intelligent classification
                cursor.execute("""
                    SELECT 
                        CASE 
                            WHEN (processor_name IS NULL OR processor_name = '') AND 
                                 (operating_system IS NULL OR operating_system = '') AND 
                                 (total_physical_memory_gb IS NULL OR total_physical_memory_gb = 0) 
                            THEN 'Asset Incomplete'
                            WHEN device_type IS NULL OR device_type = '' OR device_type = 'Unknown Device' 
                            THEN 'Classification Pending'
                            ELSE COALESCE(device_type, 'Unknown Device')
                        END as device_type,
                        COUNT(*) as count
                    FROM assets_enhanced
                    GROUP BY device_type
                    ORDER BY count DESC
                """)
                device_types = [{'name': row[0], 'count': row[1]} for row in cursor.fetchall()]
                stats['device_types'] = device_types
                
            else:
                raise Exception("Enhanced table empty")
                
        except Exception:
            # Fall back to basic assets table
            cursor.execute("SELECT COUNT(*) FROM assets")
            basic_count = cursor.fetchone()[0]
            
            stats.update({
                'total_devices': basic_count,
                'total_assets': basic_count,
                'device_status': {'online': 0, 'offline': basic_count, 'unknown': 0},
                'asset_classification': {'Asset Incomplete': basic_count},
                'incomplete_assets': basic_count,
                'avg_data_completeness': 25.0,
                'device_types': [{'name': 'Asset Incomplete', 'count': basic_count}],
                'status': 'OK - Basic table only'
            })
        
        # Additional stats
        stats['critical_issues'] = stats.get('incomplete_assets', 0)
        stats['unknown_devices'] = stats.get('device_status', {}).get('unknown', 0)
        stats['classification_system'] = 'Intelligent Asset Classification Enabled'
        
        conn.close()
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({
            'total_devices': 0, 'total_assets': 0,
            'device_status': {'online': 0, 'offline': 0, 'unknown': 0},
            'status': f'Error: {str(e)}',
            'error': str(e)
        })

@app.route('/api/assets')
def api_assets():
    """Intelligent assets API with proper classification"""
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        search_term = request.args.get('search', '')
        
        # Get filter parameters
        status_filter = request.args.get('status', '')
        device_type_filter = request.args.get('device_type', '')
        department_filter = request.args.get('department', '')
        
        # Direct database access with intelligent classification
        import sqlite3
        db_path = "../assets.db"
        if not os.path.exists(db_path):
            return jsonify({'assets': [], 'total': 0, 'pages': 0, 'status': 'Database not found'})
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Build WHERE clauses for filtering
        where_conditions = []
        params = []
        
        if search_term:
            where_conditions.append("(hostname LIKE ? OR ip_address LIKE ? OR computer_name LIKE ?)")
            search_param = f"%{search_term}%"
            params.extend([search_param, search_param, search_param])
        
        if status_filter:
            if status_filter == 'online':
                where_conditions.append("(device_status = 'Online' OR ping_response_ms > 0)")
            elif status_filter == 'offline':
                where_conditions.append("(device_status = 'Offline' OR device_status = '' OR device_status IS NULL)")
        
        if device_type_filter:
            if device_type_filter == 'Asset Incomplete':
                where_conditions.append("((processor_name IS NULL OR processor_name = '') AND (operating_system IS NULL OR operating_system = '') AND (total_physical_memory_gb IS NULL OR total_physical_memory_gb = 0))")
            else:
                where_conditions.append("device_type = ?")
                params.append(device_type_filter)
        
        if department_filter:
            where_conditions.append("assigned_department = ?")
            params.append(department_filter)
        
        where_clause = " AND ".join(where_conditions)
        if where_clause:
            where_clause = "WHERE " + where_clause
        
        # Try enhanced table first
        try:
            cursor.execute(f"SELECT COUNT(*) FROM assets_enhanced {where_clause}", params)
            total_count = cursor.fetchone()[0]
            
            if total_count > 0:
                # Calculate offset
                offset = (page - 1) * per_page
                
                # Get assets with intelligent classification
                query = f"""
                    SELECT 
                        id, hostname, computer_name, ip_address,
                        CASE 
                            WHEN device_status = 'Online' OR ping_response_ms > 0 THEN 'online'
                            WHEN device_status = 'Offline' OR device_status = '' OR device_status IS NULL THEN 'offline'
                            ELSE 'unknown'
                        END as device_status,
                        CASE 
                            WHEN (processor_name IS NULL OR processor_name = '') AND 
                                 (operating_system IS NULL OR operating_system = '') AND 
                                 (total_physical_memory_gb IS NULL OR total_physical_memory_gb = 0) 
                            THEN 'Asset Incomplete'
                            WHEN device_type IS NULL OR device_type = '' OR device_type = 'Unknown Device' 
                            THEN 'Classification Pending'
                            ELSE COALESCE(device_type, 'Unknown Device')
                        END as device_type,
                        processor_name, total_physical_memory_gb, operating_system,
                        COALESCE(assigned_department, 'Unassigned') as assigned_department,
                        data_completeness_score,
                        last_seen, created_at, updated_at
                    FROM assets_enhanced 
                    {where_clause}
                    ORDER BY 
                        CASE 
                            WHEN device_status = 'Online' OR ping_response_ms > 0 THEN 1
                            ELSE 2
                        END,
                        hostname
                    LIMIT ? OFFSET ?
                """
                
                cursor.execute(query, params + [per_page, offset])
                assets = [dict(row) for row in cursor.fetchall()]
                total = total_count
            else:
                raise Exception("Enhanced table empty for this filter")
        except Exception:
            # Fall back to basic table
            basic_where = where_clause.replace('assets_enhanced', 'assets').replace('ping_response_ms', 'response_time_ms').replace('assigned_department', 'department')
            cursor.execute(f"SELECT COUNT(*) FROM assets {basic_where}", params)
            total_count = cursor.fetchone()[0]
            
            offset = (page - 1) * per_page
            cursor.execute(f"""
                SELECT 
                    id, hostname, ip_address,
                    'unknown' as device_status,
                    CASE 
                        WHEN device_type IS NULL OR device_type = '' 
                        THEN 'Asset Incomplete'
                        ELSE device_type
                    END as device_type,
                    COALESCE(department, 'Unassigned') as assigned_department,
                    NULL as processor_name,
                    NULL as total_physical_memory_gb,
                    NULL as operating_system,
                    NULL as data_completeness_score,
                    created_at, updated_at, last_ping as last_seen
                FROM assets 
                {basic_where}
                ORDER BY hostname
                LIMIT ? OFFSET ?
            """, params + [per_page, offset])
            assets = [dict(row) for row in cursor.fetchall()]
            total = total_count
        
        conn.close()
        
        # Calculate total pages
        total_pages = (total + per_page - 1) // per_page
        
        return jsonify({
            'assets': assets,
            'total': total,
            'pages': total_pages,
            'current_page': page,
            'per_page': per_page,
            'status': 'OK',
            'classification_enabled': True
        })
        
    except Exception as e:
        return jsonify({
            'assets': [],
            'total': 0,
            'pages': 0,
            'error': str(e),
            'status': 'Error'
        })

@app.route('/api/departments')
def api_departments():
    """Get all departments"""
    try:
        if asset_manager is None:
            # Try to get basic departments from database
            try:
                # Try multiple database paths
                db_paths = [
                    "../assets.db",
                    "../../assets.db", 
                    os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets.db"),
                    "d:/Assets-Projects/Asset-Project-Enhanced/assets.db"
                ]
                
                conn = None
                for db_path in db_paths:
                    if os.path.exists(db_path):
                        try:
                            conn = sqlite3.connect(db_path)
                            conn.row_factory = sqlite3.Row
                            break
                        except:
                            continue
                
                if conn is None:
                    return jsonify([{'name': 'IT Department', 'device_count': 0, 'error': 'Database not found'}])
                
                cursor = conn.cursor()
                
                # Try to get departments from departments table first
                try:
                    cursor.execute("SELECT name, description FROM departments")
                    dept_rows = cursor.fetchall()
                    if dept_rows:
                        departments = []
                        for dept in dept_rows:
                            # Count devices in this department
                            try:
                                cursor.execute("SELECT COUNT(*) FROM assets WHERE department = ?", (dept['name'],))
                                count = cursor.fetchone()[0]
                            except:
                                count = 0
                            departments.append({'name': dept['name'], 'device_count': count})
                        conn.close()
                        return jsonify(departments)
                except:
                    pass
                
                # Fallback: get distinct departments from assets table
                cursor.execute("SELECT DISTINCT department FROM assets WHERE department IS NOT NULL AND department != ''")
                rows = cursor.fetchall()
                departments = []
                for row in rows:
                    dept_name = row[0]
                    try:
                        cursor.execute("SELECT COUNT(*) FROM assets WHERE department = ?", (dept_name,))
                        count = cursor.fetchone()[0]
                    except:
                        count = 0
                    departments.append({'name': dept_name, 'device_count': count})
                
                conn.close()
                return jsonify(departments if departments else [{'name': 'IT Department', 'device_count': 0}])
            except Exception as e:
                return jsonify([{'name': 'Default Department', 'device_count': 0, 'error': str(e)}])
        
        departments = asset_manager.get_departments()
        return jsonify(departments)
    except Exception as e:
        return jsonify([{'name': 'Default Department', 'device_count': 0, 'error': str(e)}])

@app.route('/api/departments', methods=['POST'])
def api_create_department():
    """Create new department"""
    data = request.json
    result = asset_manager.create_department(
        name=data.get('name'),
        description=data.get('description', ''),
        location=data.get('location', ''),
        manager_name=data.get('manager_name', ''),
        manager_email=data.get('manager_email', '')
    )
    return jsonify(result)

@app.route('/api/assets/<int:asset_id>', methods=['PUT'])
def api_update_asset(asset_id):
    """Update asset information"""
    updates = request.json
    result = asset_manager.update_asset(asset_id, updates)
    return jsonify(result)

@app.route('/api/device-types')
def api_device_types():
    """Get available device types"""
    device_types = [
        "Workstation", "Server", "Laptop", "Desktop", 
        "Network Device", "Printer", "Database Server", 
        "Web Server", "Linux Server", "Windows Workstation",
        "Router", "Switch", "Firewall", "Access Point",
        "Storage Device", "Virtual Machine", "Unknown"
    ]
    return jsonify(device_types)

@app.route('/api/device/<int:device_id>')
def api_device_details(device_id):
    """Get detailed information for a specific device"""
    conn = asset_manager.get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get all available columns for the device
        cursor.execute("""
            SELECT * FROM assets_enhanced 
            WHERE id = ?
        """, (device_id,))
        
        result = cursor.fetchone()
        if not result:
            return jsonify({'error': 'Device not found'}), 404
        
        device = dict(result)
        
        # Parse JSON fields safely
        json_fields = ['graphics_cards', 'network_adapters', 'installed_software', 'user_profiles']
        for field in json_fields:
            if device.get(field):
                try:
                    device[field] = json.loads(device[field])
                except (json.JSONDecodeError, TypeError):
                    pass
        
        # Format uptime if available
        if device.get('system_uptime_hours'):
            hours = int(device['system_uptime_hours'])
            days = hours // 24
            remaining_hours = hours % 24
            device['uptime_formatted'] = f"{days}d {remaining_hours}h" if days > 0 else f"{remaining_hours}h"
        
        return jsonify(device)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/scan/<int:device_id>', methods=['POST'])
def api_scan_device_simple(device_id):
    """Simple scan endpoint for device scanning"""
    return api_scan_device(device_id)

@app.route('/api/scan-device/<int:asset_id>', methods=['POST'])
def api_scan_device(asset_id):
    """Trigger NMAP scan for specific device"""
    conn = asset_manager.get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT ip_address FROM assets_enhanced WHERE id = ?", (asset_id,))
        result = cursor.fetchone()
        
        if not result:
            return jsonify({'success': False, 'error': 'Asset not found'})
        
        ip_address = result['ip_address']
        if not ip_address:
            return jsonify({'success': False, 'error': 'No IP address available'})
        
        # Perform classification
        device_type, os_guess = asset_manager.nmap_classify_device(ip_address)
        
        if device_type != "Unknown":
            # Update the asset
            cursor.execute("""
                UPDATE assets_enhanced 
                SET device_type = ?, 
                    operating_system = COALESCE(?, operating_system),
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (device_type, os_guess, asset_id))
            conn.commit()
            
            return jsonify({
                'success': True, 
                'device_type': device_type, 
                'operating_system': os_guess
            })
        else:
            return jsonify({'success': False, 'error': 'Could not classify device'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        conn.close()

@app.route('/api/device/<int:device_id>')
def api_device_detail(device_id):
    """Get comprehensive device details"""
    conn = asset_manager.get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get comprehensive device data
        cursor.execute("SELECT * FROM assets_enhanced WHERE id = ?", (device_id,))
        device_data = cursor.fetchone()
        
        if not device_data:
            return jsonify({'error': 'Device not found'}), 404
        
        # Convert to dict
        device = dict(device_data)
        
        # Parse JSON fields
        json_fields = ['graphics_cards', 'network_adapters', 'installed_software', 'user_profiles']
        for field in json_fields:
            if device.get(field):
                try:
                    device[field] = json.loads(device[field])
                except (json.JSONDecodeError, TypeError):
                    pass
        
        return jsonify(device)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/automation/status')
def api_automation_status():
    """Get automation system status"""
    if asset_manager is None:
        return jsonify({
            'automation_running': False,
            'nmap_available': False,
            'last_check': datetime.now().isoformat(),
            'service_status': 'degraded',
            'error': 'Asset manager not available'
        })
    
    return jsonify({
        'automation_running': asset_manager.automation_thread and asset_manager.automation_thread.is_alive(),
        'nmap_available': asset_manager.nmap_scanner is not None,
        'last_check': datetime.now().isoformat(),
        'service_status': 'running'
    })

def create_intelligent_service():
    """Create the intelligent asset management service"""
    app.start_time = datetime.now()
    app.config['SECRET_KEY'] = 'intelligent-asset-management-2025'
    app.config['JSON_SORT_KEYS'] = False
    return app

def run_intelligent_service():
    """Run the intelligent asset management service"""
    host = os.environ.get('WEB_SERVICE_HOST', '127.0.0.1')
    port = int(os.environ.get('WEB_SERVICE_PORT', 5000))
    
    print("[STARTING] Starting Intelligent Asset Management System...")
    print(f"[WEB] Dashboard: http://{host}:{port}")
    print("[STATS] Real-time updates: ENABLED")
    print("[AUTOMATION] Intelligent automation: ENABLED")
    nmap_status = 'ENABLED' if asset_manager and asset_manager.nmap_scanner else 'DISABLED'
    print(f"[SEARCH] NMAP classification: {nmap_status}")
    print("🏢 Department management: ENABLED")
    print("[STATS] Advanced filtering: ENABLED")
    
    # Write PID file
    try:
        with open('../web_service.pid', 'w') as f:
            f.write(str(os.getpid()))
    except:
        pass
    
    app = create_intelligent_service()
    
    try:
        app.run(host=host, port=port, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n[STOPPED] Intelligent Asset Management System stopped")
    except Exception as e:
        print(f"[ERROR] Service error: {e}")
    finally:
        try:
            if os.path.exists('../web_service.pid'):
                os.remove('../web_service.pid')
        except:
            pass

if __name__ == '__main__':
    run_intelligent_service()