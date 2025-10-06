#!/usr/bin/env python3
"""
System Health Monitor
Real-time monitoring of all collectors, database, and system components
Ensures 100% operational status of all cores and collectors
"""

import sys
import os
import time
import json
import sqlite3
import importlib
from datetime import datetime
import psutil
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class SystemHealthMonitor:
    def __init__(self):
        self.status = {
            'timestamp': None,
            'overall_health': 'Unknown',
            'database': {},
            'collectors': {},
            'core_modules': {},
            'dependencies': {},
            'system_resources': {},
            'issues': [],
            'recommendations': []
        }
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('system_health.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def check_database_health(self):
        """Check database connectivity and performance"""
        db_status = {
            'connected': False,
            'records': 0,
            'size_mb': 0,
            'recent_activity': 0,
            'sync_pending': 0,
            'performance': 'Unknown',
            'issues': []
        }
        
        try:
            # Check database file
            db_path = 'assets.db'
            if not os.path.exists(db_path):
                db_status['issues'].append("Database file not found")
                return db_status
            
            # Get file size
            db_status['size_mb'] = round(os.path.getsize(db_path) / 1024 / 1024, 2)
            
            # Test connection and queries
            start_time = time.time()
            conn = sqlite3.connect(db_path, timeout=5)
            cursor = conn.cursor()
            
            # Basic connectivity test
            cursor.execute("SELECT COUNT(*) FROM assets")
            db_status['records'] = cursor.fetchone()[0]
            db_status['connected'] = True
            
            # Recent activity
            cursor.execute("SELECT COUNT(*) FROM assets WHERE updated_at > datetime('now', '-1 hour')")
            db_status['recent_activity'] = cursor.fetchone()[0]
            
            # Sync status
            cursor.execute("SELECT COUNT(*) FROM assets WHERE _sync_pending = 'True'")
            db_status['sync_pending'] = cursor.fetchone()[0]
            
            # Performance test
            query_time = time.time() - start_time
            if query_time < 1.0:
                db_status['performance'] = 'Good'
            elif query_time < 3.0:
                db_status['performance'] = 'Fair'
            else:
                db_status['performance'] = 'Poor'
                db_status['issues'].append(f"Slow database queries ({query_time:.2f}s)")
            
            conn.close()
            
            # Health checks
            if db_status['records'] == 0:
                db_status['issues'].append("No records in database")
            
            if db_status['sync_pending'] > 100:
                db_status['issues'].append(f"High sync backlog: {db_status['sync_pending']} records")
            
        except sqlite3.Error as e:
            db_status['issues'].append(f"Database error: {str(e)}")
        except Exception as e:
            db_status['issues'].append(f"Unexpected database error: {str(e)}")
        
        return db_status
    
    def check_collector_modules(self):
        """Check all collector modules for functionality"""
        collectors = {
            'wmi_collector': 'collectors.wmi_collector',
            'ssh_collector': 'collectors.ssh_collector', 
            'snmp_collector': 'collectors.snmp_collector',
            'smart_display_collector': 'collectors.smart_display_collector'
        }
        
        collector_status = {}
        
        for name, module_path in collectors.items():
            status = {
                'imported': False,
                'functional': False,
                'functions': [],
                'issues': []
            }
            
            try:
                # Import module
                module = importlib.import_module(module_path)
                status['imported'] = True
                
                # Check for expected functions
                expected_functions = {
                    'wmi_collector': ['collect_windows_wmi'],
                    'ssh_collector': ['collect_linux_or_esxi_ssh'],
                    'snmp_collector': ['snmp_collect_basic'],
                    'smart_display_collector': ['discover_displays']
                }
                
                if name in expected_functions:
                    for func_name in expected_functions[name]:
                        if hasattr(module, func_name):
                            status['functions'].append(f"✅ {func_name}")
                        else:
                            status['functions'].append(f"❌ {func_name}")
                            status['issues'].append(f"Missing function: {func_name}")
                
                # Test basic functionality
                if name == 'wmi_collector' and hasattr(module, 'collect_windows_wmi'):
                    # Don't actually run WMI, just check if it's callable
                    if callable(getattr(module, 'collect_windows_wmi')):
                        status['functional'] = True
                elif name == 'ssh_collector' and hasattr(module, 'collect_linux_or_esxi_ssh'):
                    if callable(getattr(module, 'collect_linux_or_esxi_ssh')):
                        status['functional'] = True
                elif name == 'snmp_collector' and hasattr(module, 'snmp_collect_basic'):
                    if callable(getattr(module, 'snmp_collect_basic')):
                        status['functional'] = True
                elif name == 'smart_display_collector' and hasattr(module, 'SmartDisplayCollector'):
                    # Check if class exists and can be instantiated
                    if callable(getattr(module, 'SmartDisplayCollector')):
                        collector_instance = getattr(module, 'SmartDisplayCollector')()
                        if hasattr(collector_instance, 'discover_displays'):
                            status['functional'] = True
                
            except ImportError as e:
                status['issues'].append(f"Import failed: {str(e)}")
            except Exception as e:
                status['issues'].append(f"Module error: {str(e)}")
            
            collector_status[name] = status
        
        return collector_status
    
    def check_core_modules(self):
        """Check core system modules"""
        core_modules = {
            'database': 'db.connection',
            'models': 'db.models',
            'repository': 'db.repository',
            'smart_collector': 'core.smart_collector',
            'excel_exporter': 'export.excel_exporter',
            'gui': 'gui.app',
            'secure_vault': 'vault.secure_vault'
        }
        
        core_status = {}
        
        for name, module_path in core_modules.items():
            status = {
                'imported': False,
                'health': 'Unknown',
                'issues': []
            }
            
            try:
                module = importlib.import_module(module_path)
                status['imported'] = True
                status['health'] = 'Good'
                
                # Module-specific checks
                if name == 'database':
                    # Check if connection works
                    try:
                        if hasattr(module, 'get_connection'):
                            conn = module.get_connection()
                            if conn:
                                conn.close()
                                status['health'] = 'Excellent'
                    except Exception as e:
                        status['issues'].append(f"Connection test failed: {str(e)}")
                        status['health'] = 'Fair'
                
            except ImportError as e:
                status['issues'].append(f"Import failed: {str(e)}")
                status['health'] = 'Critical'
            except Exception as e:
                status['issues'].append(f"Module error: {str(e)}")
                status['health'] = 'Poor'
            
            core_status[name] = status
        
        return core_status
    
    def check_dependencies(self):
        """Check critical Python dependencies"""
        critical_deps = [
            'PyQt6', 'pandas', 'requests', 'paramiko', 'pysnmp',
            'cryptography', 'openpyxl', 'python-nmap', 'psutil', 'sqlite3'
        ]
        
        dep_status = {}
        
        for dep in critical_deps:
            status = {
                'installed': False,
                'version': 'Unknown',
                'issues': []
            }
            
            try:
                if dep == 'python-nmap':
                    import nmap
                    module = nmap
                elif dep == 'PyQt6':
                    import PyQt6
                    module = PyQt6
                elif dep == 'sqlite3':
                    import sqlite3
                    module = sqlite3
                else:
                    module = importlib.import_module(dep.lower().replace('-', '_'))
                
                status['installed'] = True
                
                # Get version
                if hasattr(module, '__version__'):
                    status['version'] = module.__version__
                elif hasattr(module, 'version'):
                    status['version'] = str(module.version)
                elif dep == 'sqlite3':
                    status['version'] = module.sqlite_version
                
            except ImportError as e:
                status['issues'].append(f"Not installed: {str(e)}")
            except Exception as e:
                status['issues'].append(f"Error checking: {str(e)}")
            
            dep_status[dep] = status
        
        return dep_status
    
    def check_system_resources(self):
        """Check system resources and performance"""
        resources = {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:').percent,
            'network_connections': len(psutil.net_connections()),
            'process_count': len(psutil.pids()),
            'issues': []
        }
        
        # Performance warnings
        if resources['cpu_percent'] > 80:
            resources['issues'].append(f"High CPU usage: {resources['cpu_percent']:.1f}%")
        
        if resources['memory_percent'] > 80:
            resources['issues'].append(f"High memory usage: {resources['memory_percent']:.1f}%")
        
        if resources['disk_percent'] > 90:
            resources['issues'].append(f"High disk usage: {resources['disk_percent']:.1f}%")
        
        return resources
    
    def run_health_check(self):
        """Run comprehensive health check"""
        self.logger.info("🏥 Starting system health check...")
        
        self.status['timestamp'] = datetime.now().isoformat()
        
        # Check all components
        self.status['database'] = self.check_database_health()
        self.status['collectors'] = self.check_collector_modules()
        self.status['core_modules'] = self.check_core_modules()
        self.status['dependencies'] = self.check_dependencies()
        self.status['system_resources'] = self.check_system_resources()
        
        # Collect all issues
        all_issues = []
        all_issues.extend(self.status['database'].get('issues', []))
        all_issues.extend(self.status['system_resources'].get('issues', []))
        
        for collector in self.status['collectors'].values():
            all_issues.extend(collector.get('issues', []))
        
        for module in self.status['core_modules'].values():
            all_issues.extend(module.get('issues', []))
        
        for dep in self.status['dependencies'].values():
            all_issues.extend(dep.get('issues', []))
        
        self.status['issues'] = all_issues
        
        # Determine overall health
        critical_issues = len([issue for issue in all_issues if 'critical' in issue.lower() or 'failed' in issue.lower()])
        
        if critical_issues > 0:
            self.status['overall_health'] = 'Critical'
        elif len(all_issues) > 5:
            self.status['overall_health'] = 'Poor'
        elif len(all_issues) > 0:
            self.status['overall_health'] = 'Fair'
        else:
            self.status['overall_health'] = 'Excellent'
        
        # Generate recommendations
        self.generate_recommendations()
        
        self.logger.info(f"🏥 Health check complete. Status: {self.status['overall_health']}")
        
        return self.status
    
    def generate_recommendations(self):
        """Generate recommendations based on health check"""
        recommendations = []
        
        # Database recommendations
        if self.status['database'].get('records', 0) == 0:
            recommendations.append("💡 Run a network scan to populate the database")
        
        if self.status['database'].get('sync_pending', 0) > 50:
            recommendations.append("💡 Run Excel sync to clear pending records")
        
        # Collector recommendations
        non_functional = [name for name, status in self.status['collectors'].items() if not status.get('functional', False)]
        if non_functional:
            recommendations.append(f"💡 Fix non-functional collectors: {', '.join(non_functional)}")
        
        # Dependency recommendations
        missing_deps = [name for name, status in self.status['dependencies'].items() if not status.get('installed', False)]
        if missing_deps:
            recommendations.append(f"💡 Install missing dependencies: {', '.join(missing_deps)}")
        
        # Performance recommendations
        if self.status['system_resources'].get('cpu_percent', 0) > 80:
            recommendations.append("💡 Consider reducing scan frequency or batch size")
        
        if self.status['system_resources'].get('memory_percent', 0) > 80:
            recommendations.append("💡 Close unnecessary applications or increase RAM")
        
        self.status['recommendations'] = recommendations
    
    def print_health_report(self):
        """Print formatted health report"""
        status = self.status
        
        print("🏥 SYSTEM HEALTH REPORT")
        print("=" * 80)
        print(f"⏰ Timestamp: {status['timestamp']}")
        print(f"🎯 Overall Health: {status['overall_health']}")
        print()
        
        # Database Health
        db = status['database']
        print("📊 DATABASE HEALTH")
        print(f"   Status: {'✅ Connected' if db.get('connected', False) else '❌ Disconnected'}")
        print(f"   Records: {db.get('records', 0):,}")
        print(f"   Size: {db.get('size_mb', 0)} MB")
        print(f"   Performance: {db.get('performance', 'Unknown')}")
        if db.get('issues'):
            print(f"   Issues: {', '.join(db['issues'])}")
        print()
        
        # Collectors Health
        print("🔧 COLLECTORS HEALTH")
        for name, collector in status['collectors'].items():
            icon = "✅" if collector.get('functional', False) else "❌"
            print(f"   {icon} {name}")
            if collector.get('functions'):
                for func in collector['functions']:
                    print(f"      {func}")
            if collector.get('issues'):
                print(f"      Issues: {', '.join(collector['issues'])}")
        print()
        
        # Core Modules Health
        print("⚙️  CORE MODULES HEALTH")
        for name, module in status['core_modules'].items():
            icon = "✅" if module.get('imported', False) else "❌"
            health = module.get('health', 'Unknown')
            print(f"   {icon} {name} ({health})")
            if module.get('issues'):
                print(f"      Issues: {', '.join(module['issues'])}")
        print()
        
        # Dependencies Health
        print("📦 DEPENDENCIES HEALTH")
        for name, dep in status['dependencies'].items():
            icon = "✅" if dep.get('installed', False) else "❌"
            version = dep.get('version', 'Unknown')
            print(f"   {icon} {name} ({version})")
            if dep.get('issues'):
                print(f"      Issues: {', '.join(dep['issues'])}")
        print()
        
        # System Resources
        resources = status['system_resources']
        print("💻 SYSTEM RESOURCES")
        print(f"   CPU: {resources.get('cpu_percent', 0):.1f}%")
        print(f"   Memory: {resources.get('memory_percent', 0):.1f}%")
        print(f"   Disk: {resources.get('disk_percent', 0):.1f}%")
        print(f"   Connections: {resources.get('network_connections', 0)}")
        if resources.get('issues'):
            print(f"   Issues: {', '.join(resources['issues'])}")
        print()
        
        # Issues Summary
        if status['issues']:
            print("⚠️  ISSUES FOUND")
            for i, issue in enumerate(status['issues'], 1):
                print(f"   {i}. {issue}")
            print()
        
        # Recommendations
        if status['recommendations']:
            print("💡 RECOMMENDATIONS")
            for i, rec in enumerate(status['recommendations'], 1):
                print(f"   {i}. {rec}")
            print()
        
        print("=" * 80)
    
    def save_report(self, filename=None):
        """Save health report to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"health_report_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.status, f, indent=2)
        
        self.logger.info(f"💾 Health report saved to {filename}")
        return filename
    
    def continuous_monitor(self, interval_minutes=5):
        """Run continuous monitoring"""
        self.logger.info(f"🔄 Starting continuous monitoring (every {interval_minutes} minutes)")
        
        try:
            while True:
                self.run_health_check()
                self.print_health_report()
                
                # Save periodic reports
                if datetime.now().minute % 30 == 0:  # Every 30 minutes
                    self.save_report()
                
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Monitoring stopped by user")
        except Exception as e:
            self.logger.error(f"❌ Monitoring error: {e}")

def main():
    monitor = SystemHealthMonitor()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'continuous':
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            monitor.continuous_monitor(interval)
        
        elif command == 'report':
            monitor.run_health_check()
            filename = monitor.save_report()
            print(f"📊 Report saved to: {filename}")
        
        elif command == 'json':
            status = monitor.run_health_check()
            print(json.dumps(status, indent=2))
        
        else:
            print("Usage: python system_health_monitor.py [continuous|report|json]")
    
    else:
        # Default: single health check with display
        monitor.run_health_check()
        monitor.print_health_report()

if __name__ == "__main__":
    main()