"""
COMPREHENSIVE PRODUCTION WEB SERVICE
Advanced Flask application with comprehensive 520-column asset management
"""

from flask import Flask, render_template, jsonify, request
import sqlite3
import json
import socket
import threading
from datetime import datetime
import os
from comprehensive_schema import COMPREHENSIVE_COLUMNS
from comprehensive_collector import ComprehensiveDataCollector
from enhanced_100_percent_collector import Enhanced100PercentCollector
from smart_nmap_automation import SmartNmapAutomation

app = Flask(__name__)

class ComprehensiveAssetManager:
    def __init__(self, db_path='assets.db'):
        self.db_path = db_path
        self.collector = Enhanced100PercentCollector(db_path)  # Use enhanced collector
        self.nmap_automation = SmartNmapAutomation(db_path)
        self.automation_thread = None
        self.start_smart_automation()
        
    def start_smart_automation(self):
        """Start the smart nmap automation in background"""
        def run_automation():
            try:
                print("🤖 Starting Smart Nmap Automation...")
                self.nmap_automation.start_automation()
            except Exception as e:
                print(f"❌ Smart automation error: {e}")
        
        self.automation_thread = threading.Thread(target=run_automation, daemon=True)
        self.automation_thread.start()
        print("✅ Smart Nmap Automation started in background")
        
    def get_db_connection(self):
        """Get database connection with error handling"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            # Try alternative paths
            alt_paths = [
                'D:/Assets-Projects/Asset-Project-Enhanced/assets.db',
                '../assets.db',
                './assets.db'
            ]
            for path in alt_paths:
                try:
                    if os.path.exists(path):
                        conn = sqlite3.connect(path)
                        conn.row_factory = sqlite3.Row
                        return conn
                except:
                    continue
            raise Exception(f"Cannot connect to database: {e}")
    
    def get_comprehensive_stats(self):
        """Get comprehensive statistics for all 520 columns"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Basic counts
            cursor.execute("SELECT COUNT(*) as total FROM assets_enhanced")
            total_assets = cursor.fetchone()['total']
            
            # Device status breakdown
            cursor.execute("""
                SELECT device_status, COUNT(*) as count 
                FROM assets_enhanced 
                WHERE device_status IS NOT NULL 
                GROUP BY device_status
            """)
            device_status = {row['device_status']: row['count'] for row in cursor.fetchall()}
            
            # Device type breakdown
            cursor.execute("""
                SELECT device_type, COUNT(*) as count 
                FROM assets_enhanced 
                WHERE device_type IS NOT NULL 
                GROUP BY device_type 
                ORDER BY count DESC
            """)
            device_types = [{'name': row['device_type'], 'count': row['count']} for row in cursor.fetchall()]
            
            # OS family breakdown
            cursor.execute("""
                SELECT os_family, COUNT(*) as count 
                FROM assets_enhanced 
                WHERE os_family IS NOT NULL 
                GROUP BY os_family
            """)
            os_families = {row['os_family']: row['count'] for row in cursor.fetchall()}
            
            # Manufacturer breakdown
            cursor.execute("""
                SELECT system_manufacturer, COUNT(*) as count 
                FROM assets_enhanced 
                WHERE system_manufacturer IS NOT NULL 
                GROUP BY system_manufacturer 
                ORDER BY count DESC 
                LIMIT 10
            """)
            manufacturers = [{'name': row['system_manufacturer'], 'count': row['count']} for row in cursor.fetchall()]
            
            # Data completeness analysis
            cursor.execute("SELECT * FROM assets_enhanced LIMIT 1")
            sample_row = cursor.fetchone()
            if sample_row:
                filled_columns = sum(1 for value in sample_row if value is not None and value != "")
                total_columns = len(COMPREHENSIVE_COLUMNS)
                avg_completeness = (filled_columns / total_columns) * 100
            else:
                avg_completeness = 0
                
            # Collection method breakdown
            cursor.execute("""
                SELECT collection_method, COUNT(*) as count 
                FROM assets_enhanced 
                WHERE collection_method IS NOT NULL 
                GROUP BY collection_method
            """)
            collection_methods = {row['collection_method']: row['count'] for row in cursor.fetchall()}
            
            # Asset classification (incomplete vs complete)
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN data_completeness_score < 30 THEN 'Asset Incomplete'
                        WHEN data_completeness_score < 70 THEN 'Classification Pending'
                        ELSE 'Complete Asset'
                    END as classification,
                    COUNT(*) as count
                FROM assets_enhanced 
                GROUP BY classification
            """)
            asset_classification = {row['classification']: row['count'] for row in cursor.fetchall()}
            
            # Hardware insights
            cursor.execute("""
                SELECT 
                    AVG(CAST(total_physical_memory_gb AS FLOAT)) as avg_memory,
                    AVG(CAST(total_storage_gb AS FLOAT)) as avg_storage,
                    COUNT(DISTINCT processor_manufacturer) as unique_cpu_vendors
                FROM assets_enhanced 
                WHERE total_physical_memory_gb IS NOT NULL
            """)
            hardware_stats = cursor.fetchone()
            
            conn.close()
            
            return {
                'status': 'success',
                'total_assets': total_assets,
                'total_columns': len(COMPREHENSIVE_COLUMNS),
                'avg_data_completeness': round(avg_completeness, 1),
                'device_status': device_status,
                'device_types': device_types,
                'os_families': os_families,
                'manufacturers': manufacturers,
                'collection_methods': collection_methods,
                'asset_classification': asset_classification,
                'hardware_insights': {
                    'avg_memory_gb': round(hardware_stats['avg_memory'] or 0, 1),
                    'avg_storage_gb': round(hardware_stats['avg_storage'] or 0, 1),
                    'unique_cpu_vendors': hardware_stats['unique_cpu_vendors'] or 0
                },
                'incomplete_assets': asset_classification.get('Asset Incomplete', 0),
                'classification_enabled': True,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'total_assets': 0,
                'total_columns': len(COMPREHENSIVE_COLUMNS)
            }
    
    def get_comprehensive_assets(self, page=1, per_page=50, search=None, filter_by=None):
        """Get assets with comprehensive data"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Base query
            base_query = """
                SELECT id, hostname, ip_address, device_type, device_status, 
                       system_manufacturer, system_model, operating_system,
                       processor_name, total_physical_memory_gb, total_storage_gb,
                       last_seen, collection_timestamp, data_completeness_score,
                       department, location, asset_tag, serial_number
                FROM assets_enhanced
            """
            
            # Add filters
            where_conditions = []
            params = []
            
            if search:
                where_conditions.append("""
                    (hostname LIKE ? OR ip_address LIKE ? OR device_type LIKE ? 
                     OR system_manufacturer LIKE ? OR system_model LIKE ?)
                """)
                search_param = f"%{search}%"
                params.extend([search_param] * 5)
            
            if filter_by:
                if filter_by.get('device_type'):
                    where_conditions.append("device_type = ?")
                    params.append(filter_by['device_type'])
                if filter_by.get('manufacturer'):
                    where_conditions.append("system_manufacturer = ?")
                    params.append(filter_by['manufacturer'])
                if filter_by.get('status'):
                    where_conditions.append("device_status = ?")
                    params.append(filter_by['status'])
            
            if where_conditions:
                base_query += " WHERE " + " AND ".join(where_conditions)
            
            # Count total
            count_query = base_query.replace("SELECT id, hostname, ip_address, device_type, device_status, system_manufacturer, system_model, operating_system, processor_name, total_physical_memory_gb, total_storage_gb, last_seen, collection_timestamp, data_completeness_score, department, location, asset_tag, serial_number", "SELECT COUNT(*)")
            cursor.execute(count_query, params)
            total = cursor.fetchone()[0]
            
            # Add pagination
            offset = (page - 1) * per_page
            base_query += " ORDER BY last_seen DESC, hostname ASC LIMIT ? OFFSET ?"
            params.extend([per_page, offset])
            
            cursor.execute(base_query, params)
            assets = []
            
            for row in cursor.fetchall():
                asset = dict(row)
                # Add classification
                completeness = asset.get('data_completeness_score', 0) or 0
                if completeness < 30:
                    asset['classification'] = 'Asset Incomplete'
                elif completeness < 70:
                    asset['classification'] = 'Classification Pending'
                else:
                    asset['classification'] = 'Complete Asset'
                
                assets.append(asset)
            
            conn.close()
            
            return {
                'status': 'success',
                'assets': assets,
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': (total + per_page - 1) // per_page
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'assets': [],
                'total': 0
            }
    
    def get_asset_details(self, asset_id):
        """Get complete asset details with all 520 columns"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM assets_enhanced WHERE id = ?", (asset_id,))
            row = cursor.fetchone()
            
            if not row:
                return {'status': 'error', 'error': 'Asset not found'}
            
            asset = dict(row)
            
            # Organize data by categories
            categories = {
                'identification': {},
                'hardware_system': {},
                'processor': {},
                'memory': {},
                'storage': {},
                'network': {},
                'operating_system': {},
                'security': {},
                'performance': {},
                'management': {},
                'collection_metadata': {}
            }
            
            # Categorize fields
            for key, value in asset.items():
                if key.startswith(('hostname', 'computer_name', 'ip_address', 'mac_address', 'uuid', 'serial_number', 'asset_tag')):
                    categories['identification'][key] = value
                elif key.startswith(('system_', 'motherboard_', 'chassis_', 'bios_')):
                    categories['hardware_system'][key] = value
                elif key.startswith('processor_') or key.startswith('cpu_'):
                    categories['processor'][key] = value
                elif key.startswith('memory_') or 'memory' in key:
                    categories['memory'][key] = value
                elif key.startswith(('storage_', 'disk_', 'ssd_', 'hdd_')):
                    categories['storage'][key] = value
                elif key.startswith(('network_', 'wifi_', 'ethernet_')):
                    categories['network'][key] = value
                elif key.startswith('os_') or key == 'operating_system':
                    categories['operating_system'][key] = value
                elif key.startswith(('security_', 'antivirus_', 'firewall_', 'encryption_')):
                    categories['security'][key] = value
                elif key.startswith(('performance_', 'uptime_', 'usage_')):
                    categories['performance'][key] = value
                elif key.startswith(('department', 'location', 'cost_', 'purchase_', 'warranty_')):
                    categories['management'][key] = value
                elif key.startswith('collection_'):
                    categories['collection_metadata'][key] = value
            
            conn.close()
            
            return {
                'status': 'success',
                'asset': asset,
                'categories': categories,
                'total_fields': len(asset),
                'filled_fields': sum(1 for v in asset.values() if v is not None and v != "")
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

# Initialize asset manager
asset_manager = ComprehensiveAssetManager()

# Routes
@app.route('/')
def index():
    return render_template('comprehensive_dashboard.html')

@app.route('/production')
def production_dashboard():
    return render_template('comprehensive_dashboard.html')

@app.route('/api/stats')
def api_stats():
    return jsonify(asset_manager.get_comprehensive_stats())

@app.route('/api/assets')
def api_assets():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    search = request.args.get('search')
    
    # Parse filters
    filter_by = {}
    if request.args.get('device_type'):
        filter_by['device_type'] = request.args.get('device_type')
    if request.args.get('manufacturer'):
        filter_by['manufacturer'] = request.args.get('manufacturer')
    if request.args.get('status'):
        filter_by['status'] = request.args.get('status')
    
    return jsonify(asset_manager.get_comprehensive_assets(page, per_page, search, filter_by))

@app.route('/api/assets/<int:asset_id>')
def api_asset_details(asset_id):
    return jsonify(asset_manager.get_asset_details(asset_id))

@app.route('/api/collect/<hostname>')
def api_collect_asset(hostname):
    """Trigger comprehensive data collection for specific asset"""
    try:
        collector = ComprehensiveDataCollector()
        data = collector.collect_comprehensive_data(hostname)
        
        # Update database
        conn = asset_manager.get_db_connection()
        cursor = conn.cursor()
        
        # Check if asset exists
        cursor.execute("SELECT id FROM assets_enhanced WHERE hostname = ?", (hostname,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing asset
            update_fields = [f"{key} = ?" for key in data.keys()]
            update_query = f"UPDATE assets_enhanced SET {', '.join(update_fields)} WHERE hostname = ?"
            cursor.execute(update_query, list(data.values()) + [hostname])
        else:
            # Insert new asset
            columns = list(data.keys())
            placeholders = ', '.join(['?' for _ in columns])
            insert_query = f"INSERT INTO assets_enhanced ({', '.join(columns)}) VALUES ({placeholders})"
            cursor.execute(insert_query, list(data.values()))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'message': f'Comprehensive data collection completed for {hostname}',
            'data_completeness': data.get('data_completeness_score', 0),
            'fields_collected': len([v for v in data.values() if v is not None and v != ""])
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        })

@app.route('/api/collect-enhanced/<hostname>')
def api_collect_enhanced(hostname):
    """Trigger ENHANCED 100% data collection for specific asset"""
    try:
        collector = Enhanced100PercentCollector()
        data = collector.collect_comprehensive_data(hostname)
        
        # Update database
        conn = asset_manager.get_db_connection()
        cursor = conn.cursor()
        
        # Check if asset exists
        cursor.execute("SELECT id FROM assets_enhanced WHERE hostname = ?", (hostname,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing asset
            update_fields = [f"{key} = ?" for key in data.keys() if key in [desc[1] for desc in cursor.execute("PRAGMA table_info(assets_enhanced)").fetchall()]]
            update_values = [data[key] for key in data.keys() if key in [desc[1] for desc in cursor.execute("PRAGMA table_info(assets_enhanced)").fetchall()]]
            
            if update_fields:
                update_query = f"UPDATE assets_enhanced SET {', '.join(update_fields)} WHERE hostname = ?"
                cursor.execute(update_query, update_values + [hostname])
        else:
            # Insert new asset (simplified for existing schema)
            common_fields = ['hostname', 'ip_address', 'device_type', 'operating_system', 'collection_method', 'collection_timestamp', 'data_completeness_score']
            values = [data.get(field) for field in common_fields]
            placeholders = ', '.join(['?' for _ in common_fields])
            insert_query = f"INSERT INTO assets_enhanced ({', '.join(common_fields)}) VALUES ({placeholders})"
            cursor.execute(insert_query, values)
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'message': f'ENHANCED 100% data collection completed for {hostname}',
            'data_completeness': data.get('data_completeness_score', 0),
            'fields_collected': len([v for v in data.values() if v is not None and v != ""]),
            'collection_method': 'Enhanced 100% Collector'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        })

@app.route('/api/collect-enhanced-all')
def api_collect_enhanced_all():
    """Trigger ENHANCED 100% data collection for localhost"""
    return api_collect_enhanced(socket.gethostname())

@app.route('/api/nmap-scan/<hostname>')
def api_nmap_scan(hostname):
    """Trigger nmap scan for specific hostname"""
    try:
        # Get IP address for hostname
        conn = asset_manager.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT ip_address FROM assets_enhanced WHERE hostname = ?", (hostname,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return jsonify({
                'status': 'error',
                'error': 'Hostname not found in database'
            })
        
        ip_address = result['ip_address']
        
        # Run nmap scan
        scan_result = asset_manager.nmap_automation.run_nmap_scan(ip_address)
        
        if scan_result:
            # Update device info
            device_id = cursor.execute("SELECT id FROM assets_enhanced WHERE hostname = ?", (hostname,)).fetchone()['id']
            success = asset_manager.nmap_automation.update_device_info(device_id, scan_result)
            
            return jsonify({
                'status': 'success',
                'message': f'Nmap scan completed for {hostname}',
                'scan_result': {
                    'os_family': scan_result['os_family'],
                    'device_type': scan_result['device_type'],
                    'vendor': scan_result['vendor'],
                    'open_ports': json.loads(scan_result['open_ports']),
                    'services': json.loads(scan_result['services'])
                }
            })
        else:
            return jsonify({
                'status': 'error',
                'error': 'Nmap scan failed'
            })
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        })

@app.route('/api/check-unknown-devices')
def check_unknown_devices():
    """Check for unknown devices in the database"""
    if asset_manager.smart_automation:
        unknown_devices = asset_manager.smart_automation.get_unknown_devices()
        return jsonify({
            'success': True,
            'count': len(unknown_devices),
            'devices': unknown_devices
        })
    return jsonify({'success': False, 'error': 'Smart automation not available'})

@app.route('/api/collect-enhanced/<hostname>')
def collect_enhanced(hostname):
    """Enhanced data collection for specific hostname"""
    try:
        enhanced_collector = Enhanced100PercentCollector(asset_manager.db_path)
        result = enhanced_collector.collect_comprehensive_data(hostname)
        
        if result and result.get('success'):
            return jsonify({
                'success': True,
                'message': f'Enhanced collection completed for {hostname}',
                'data_completeness': result.get('completeness_percentage', 0),
                'columns_filled': result.get('columns_filled', 0),
                'total_columns': len(COMPREHENSIVE_COLUMNS)
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Enhanced collection failed for {hostname}',
                'details': result.get('error', 'Unknown error')
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/automation-status')
def automation_status():
    """Get status of smart automation system"""
    if asset_manager.smart_automation:
        return jsonify({
            'success': True,
            'automation_running': asset_manager.smart_automation.is_running,
            'scan_interval': 300,  # 5 minutes
            'last_scan_time': getattr(asset_manager.smart_automation, 'last_scan_time', None)
        })
    return jsonify({'success': False, 'error': 'Smart automation not available'})

@app.route('/api/nmap-scan/<hostname>')
def manual_nmap_scan(hostname):
    """Manually trigger nmap scan for specific hostname"""
    try:
        if asset_manager.smart_automation:
            result = asset_manager.smart_automation.run_nmap_scan(hostname)
            return jsonify({
                'success': True,
                'hostname': hostname,
                'scan_result': result
            })
        else:
            return jsonify({'success': False, 'error': 'Smart automation not available'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("🚀 COMPREHENSIVE PRODUCTION ASSET MANAGEMENT SYSTEM")
    print("=" * 70)
    print(f"📊 Database: {asset_manager.db_path}")
    print(f"🗃️  Total columns: {len(COMPREHENSIVE_COLUMNS)}")
    print(f"🌐 Production Dashboard: http://127.0.0.1:5000/production")
    print(f"📊 API Stats: http://127.0.0.1:5000/api/stats")
    print(f"📋 API Assets: http://127.0.0.1:5000/api/assets")
    print(f"🔍 API Asset Details: http://127.0.0.1:5000/api/assets/1")
    print(f"🔄 API Collect Asset: http://127.0.0.1:5000/api/collect/hostname")
    print(f"🚀 API Enhanced Collection: http://127.0.0.1:5000/api/collect-enhanced/hostname")
    print(f"🤖 API Automation Status: http://127.0.0.1:5000/api/automation-status")
    print("=" * 70)
    
    app.run(host='0.0.0.0', port=5000, debug=True)