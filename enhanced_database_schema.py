#!/usr/bin/env python3
"""
Enhanced Database Schema Creation and Management
Creates comprehensive database structure for all device fields
خلي قاعدة البيانات تحتوي علي كل الخانات
"""

import sqlite3
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - DatabaseEnhancer - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseEnhancer:
    def __init__(self, db_path="assets.db"):
        self.db_path = db_path
        self.connection = None
        
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            logger.info(f"Connected to database: {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False
    
    def backup_database(self):
        """Create backup before modifications"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"assets_backup_{timestamp}.db"
            
            # Copy current database
            import shutil
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Database backed up to: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return None
    
    def get_table_info(self, table_name):
        """Get current table structure"""
        try:
            if not self.connection:
                logger.error("No database connection available")
                return []
            cursor = self.connection.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            return [col[1] for col in columns]  # Column names only
        except Exception as e:
            logger.error(f"Failed to get table info for {table_name}: {e}")
            return []
    
    def add_column_if_not_exists(self, table_name, column_name, column_type, default_value=None):
        """Add column to table if it doesn't exist"""
        try:
            if not self.connection:
                logger.error("No database connection available")
                return False
                
            existing_columns = self.get_table_info(table_name)
            if column_name not in existing_columns:
                alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
                if default_value is not None:
                    alter_sql += f" DEFAULT '{default_value}'"
                
                cursor = self.connection.cursor()
                cursor.execute(alter_sql)
                self.connection.commit()
                logger.info(f"Added column {column_name} to {table_name}")
                return True
            else:
                logger.info(f"Column {column_name} already exists in {table_name}")
                return False
        except Exception as e:
            logger.error(f"Failed to add column {column_name} to {table_name}: {e}")
            return False
    
    def enhance_assets_table(self):
        """Add comprehensive fields to assets table"""
        logger.info("Enhancing assets table with comprehensive device fields...")
        
        # Basic Device Information
        self.add_column_if_not_exists("assets", "device_type", "TEXT", "Unknown")
        self.add_column_if_not_exists("assets", "device_model", "TEXT")
        self.add_column_if_not_exists("assets", "device_vendor", "TEXT")
        self.add_column_if_not_exists("assets", "serial_number", "TEXT")
        self.add_column_if_not_exists("assets", "asset_tag", "TEXT")
        
        # Network Information
        self.add_column_if_not_exists("assets", "mac_address", "TEXT")
        self.add_column_if_not_exists("assets", "ip_address_v6", "TEXT")
        self.add_column_if_not_exists("assets", "subnet_mask", "TEXT")
        self.add_column_if_not_exists("assets", "gateway", "TEXT")
        self.add_column_if_not_exists("assets", "dns_servers", "TEXT")
        self.add_column_if_not_exists("assets", "domain_name", "TEXT")
        self.add_column_if_not_exists("assets", "network_adapter", "TEXT")
        
        # Operating System Information
        self.add_column_if_not_exists("assets", "os_version", "TEXT")
        self.add_column_if_not_exists("assets", "os_build", "TEXT")
        self.add_column_if_not_exists("assets", "os_architecture", "TEXT")
        self.add_column_if_not_exists("assets", "os_install_date", "TEXT")
        self.add_column_if_not_exists("assets", "last_boot_time", "TEXT")
        self.add_column_if_not_exists("assets", "uptime", "TEXT")
        
        # Hardware Information
        self.add_column_if_not_exists("assets", "cpu_model", "TEXT")
        self.add_column_if_not_exists("assets", "cpu_cores", "INTEGER")
        self.add_column_if_not_exists("assets", "cpu_threads", "INTEGER")
        self.add_column_if_not_exists("assets", "cpu_speed", "TEXT")
        self.add_column_if_not_exists("assets", "total_memory", "TEXT")
        self.add_column_if_not_exists("assets", "available_memory", "TEXT")
        self.add_column_if_not_exists("assets", "memory_usage_percent", "REAL")
        
        # Storage Information
        self.add_column_if_not_exists("assets", "total_disk_space", "TEXT")
        self.add_column_if_not_exists("assets", "free_disk_space", "TEXT")
        self.add_column_if_not_exists("assets", "disk_usage_percent", "REAL")
        self.add_column_if_not_exists("assets", "disk_model", "TEXT")
        self.add_column_if_not_exists("assets", "disk_type", "TEXT")  # SSD, HDD, etc.
        
        # System Information
        self.add_column_if_not_exists("assets", "motherboard", "TEXT")
        self.add_column_if_not_exists("assets", "bios_version", "TEXT")
        self.add_column_if_not_exists("assets", "bios_date", "TEXT")
        self.add_column_if_not_exists("assets", "system_manufacturer", "TEXT")
        self.add_column_if_not_exists("assets", "system_model", "TEXT")
        
        # Network Services Information
        self.add_column_if_not_exists("assets", "running_services", "TEXT")  # JSON array
        self.add_column_if_not_exists("assets", "listening_ports", "TEXT")   # JSON array
        self.add_column_if_not_exists("assets", "open_connections", "TEXT")  # JSON array
        
        # Software Information
        self.add_column_if_not_exists("assets", "installed_software", "TEXT")  # JSON array
        self.add_column_if_not_exists("assets", "recent_software", "TEXT")     # Recently installed
        self.add_column_if_not_exists("assets", "security_software", "TEXT")   # Antivirus, etc.
        
        # User Information
        self.add_column_if_not_exists("assets", "logged_in_users", "TEXT")     # JSON array
        self.add_column_if_not_exists("assets", "last_logged_user", "TEXT")
        self.add_column_if_not_exists("assets", "user_profiles", "TEXT")       # JSON array
        
        # Performance Metrics
        self.add_column_if_not_exists("assets", "cpu_usage_percent", "REAL")
        self.add_column_if_not_exists("assets", "network_utilization", "TEXT")
        self.add_column_if_not_exists("assets", "system_load", "TEXT")
        self.add_column_if_not_exists("assets", "performance_score", "INTEGER")
        
        # Security Information
        self.add_column_if_not_exists("assets", "firewall_status", "TEXT")
        self.add_column_if_not_exists("assets", "windows_updates", "TEXT")     # Update status
        self.add_column_if_not_exists("assets", "security_patches", "TEXT")    # JSON array
        self.add_column_if_not_exists("assets", "vulnerability_scan", "TEXT")  # Last scan results
        
        # Asset Management
        self.add_column_if_not_exists("assets", "purchase_date", "TEXT")
        self.add_column_if_not_exists("assets", "warranty_expiry", "TEXT")
        self.add_column_if_not_exists("assets", "support_contact", "TEXT")
        self.add_column_if_not_exists("assets", "maintenance_schedule", "TEXT")
        
        # Collection Metadata
        self.add_column_if_not_exists("assets", "collection_method", "TEXT")   # WMI, SSH, SNMP
        self.add_column_if_not_exists("assets", "collection_source", "TEXT")   # Desktop App, Web Service
        self.add_column_if_not_exists("assets", "data_quality_score", "INTEGER")
        self.add_column_if_not_exists("assets", "collection_errors", "TEXT")   # JSON array
        
        # Compliance and Governance
        self.add_column_if_not_exists("assets", "compliance_status", "TEXT")
        self.add_column_if_not_exists("assets", "policy_violations", "TEXT")   # JSON array
        self.add_column_if_not_exists("assets", "risk_score", "INTEGER")
        self.add_column_if_not_exists("assets", "business_criticality", "TEXT")
        
        logger.info("Assets table enhancement completed!")
    
    def create_device_details_table(self):
        """Create separate table for detailed device information"""
        try:
            if not self.connection:
                logger.error("No database connection available")
                return
                
            cursor = self.connection.cursor()
            
            create_sql = """
            CREATE TABLE IF NOT EXISTS device_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_id INTEGER,
                detail_type TEXT,  -- 'hardware', 'software', 'network', 'performance'
                detail_category TEXT,  -- 'cpu', 'memory', 'disk', 'service', etc.
                detail_name TEXT,
                detail_value TEXT,
                detail_unit TEXT,  -- 'GB', 'MHz', '%', etc.
                collection_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_current BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (asset_id) REFERENCES assets (id)
            )
            """
            
            cursor.execute(create_sql)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_device_details_asset_id ON device_details(asset_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_device_details_type ON device_details(detail_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_device_details_current ON device_details(is_current)")
            
            if self.connection:
                self.connection.commit()
            logger.info("Device details table created successfully!")
            
        except Exception as e:
            logger.error(f"Failed to create device_details table: {e}")
    
    def create_network_scans_table(self):
        """Create table for network scan results"""
        try:
            if not self.connection:
                logger.error("No database connection available")
                return
                
            cursor = self.connection.cursor()
            
            create_sql = """
            CREATE TABLE IF NOT EXISTS network_scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id TEXT UNIQUE,
                scan_type TEXT,  -- 'port_scan', 'ping_sweep', 'discovery'
                target_range TEXT,
                scan_start DATETIME,
                scan_end DATETIME,
                devices_found INTEGER DEFAULT 0,
                scan_status TEXT DEFAULT 'running',
                scan_results TEXT,  -- JSON data
                created_by TEXT,
                notes TEXT
            )
            """
            
            cursor.execute(create_sql)
            if self.connection:
                self.connection.commit()
            logger.info("Network scans table created successfully!")
            
        except Exception as e:
            logger.error(f"Failed to create network_scans table: {e}")
    
    def create_system_logs_table(self):
        """Create table for system activity logs"""
        try:
            if not self.connection:
                logger.error("No database connection available")
                return
                
            cursor = self.connection.cursor()
            
            create_sql = """
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_id INTEGER,
                log_type TEXT,  -- 'access', 'error', 'warning', 'info'
                log_source TEXT,  -- 'web_service', 'desktop_app', 'auto_scan'
                message TEXT,
                details TEXT,  -- JSON data
                user_name TEXT,
                ip_address TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (asset_id) REFERENCES assets (id)
            )
            """
            
            cursor.execute(create_sql)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_system_logs_asset_id ON system_logs(asset_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_system_logs_type ON system_logs(log_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_system_logs_timestamp ON system_logs(timestamp)")
            
            if self.connection:
                self.connection.commit()
            logger.info("System logs table created successfully!")
            
        except Exception as e:
            logger.error(f"Failed to create system_logs table: {e}")
    
    def update_existing_data(self):
        """Update existing records with default values"""
        try:
            if not self.connection:
                logger.error("No database connection available")
                return
                
            cursor = self.connection.cursor()
            
            # Update device_type based on existing data
            cursor.execute("""
                UPDATE assets 
                SET device_type = CASE 
                    WHEN hostname LIKE '%server%' OR hostname LIKE '%srv%' THEN 'Server'
                    WHEN hostname LIKE '%pc%' OR hostname LIKE '%desktop%' THEN 'Desktop'
                    WHEN hostname LIKE '%laptop%' OR hostname LIKE '%notebook%' THEN 'Laptop'
                    WHEN hostname LIKE '%router%' OR hostname LIKE '%switch%' THEN 'Network Device'
                    WHEN hostname LIKE '%printer%' THEN 'Printer'
                    ELSE 'Workstation'
                END
                WHERE device_type = 'Unknown' OR device_type IS NULL
            """)
            
            # Set collection method for existing records
            cursor.execute("""
                UPDATE assets 
                SET collection_method = 'Legacy Import',
                    collection_source = 'Desktop App',
                    data_quality_score = 3
                WHERE collection_method IS NULL
            """)
            
            if self.connection:
                self.connection.commit()
            logger.info("Existing data updated with enhanced fields!")
            
        except Exception as e:
            logger.error(f"Failed to update existing data: {e}")
    
    def create_views(self):
        """Create useful database views"""
        try:
            if not self.connection:
                logger.error("No database connection available")
                return
                
            cursor = self.connection.cursor()
            
            # Create comprehensive device view
            cursor.execute("""
                CREATE VIEW IF NOT EXISTS device_summary AS
                SELECT 
                    a.id,
                    a.hostname,
                    a.ip_address,
                    a.device_type,
                    a.device_model,
                    a.device_vendor,
                    a.department,
                    a.status,
                    a.cpu_model,
                    a.total_memory,
                    a.total_disk_space,
                    a.os_name || ' ' || COALESCE(a.os_version, '') as operating_system,
                    a.last_seen,
                    a.data_quality_score,
                    a.collection_method
                FROM assets a
                ORDER BY a.hostname
            """)
            
            # Create network devices view
            cursor.execute("""
                CREATE VIEW IF NOT EXISTS network_devices AS
                SELECT 
                    id, hostname, ip_address, mac_address, device_type,
                    listening_ports, network_adapter, last_seen, status
                FROM assets 
                WHERE device_type IN ('Router', 'Switch', 'Network Device', 'Firewall')
                ORDER BY ip_address
            """)
            
            # Create security overview view
            cursor.execute("""
                CREATE VIEW IF NOT EXISTS security_overview AS
                SELECT 
                    id, hostname, ip_address, device_type,
                    firewall_status, security_software, windows_updates,
                    vulnerability_scan, risk_score, compliance_status
                FROM assets 
                WHERE firewall_status IS NOT NULL 
                   OR security_software IS NOT NULL
                ORDER BY risk_score DESC, hostname
            """)
            
            if self.connection:
                self.connection.commit()
            logger.info("Database views created successfully!")
            
        except Exception as e:
            logger.error(f"Failed to create views: {e}")
    
    def run_enhancement(self):
        """Run complete database enhancement"""
        logger.info("Starting database enhancement process...")
        
        # Connect to database
        if not self.connect():
            return False
        
        # Create backup
        backup_path = self.backup_database()
        if not backup_path:
            logger.warning("Could not create backup, continuing anyway...")
        
        try:
            # Enhance main assets table
            self.enhance_assets_table()
            
            # Create additional tables
            self.create_device_details_table()
            self.create_network_scans_table()
            self.create_system_logs_table()
            
            # Update existing data
            self.update_existing_data()
            
            # Create views
            self.create_views()
            
            logger.info("Database enhancement completed successfully!")
            logger.info(f"Backup created at: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Database enhancement failed: {e}")
            return False
        
        finally:
            if self.connection:
                self.connection.close()
    
    def generate_schema_report(self):
        """Generate detailed schema report"""
        if not self.connect():
            return
        
        try:
            if not self.connection:
                logger.error("No database connection available")
                return
                
            cursor = self.connection.cursor()
            
            print("\n" + "="*60)
            print("ENHANCED DATABASE SCHEMA REPORT")
            print("="*60)
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            for table in tables:
                table_name = table[0]
                print(f"\nTable: {table_name}")
                print("-" * 40)
                
                # Get table info
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                for col in columns:
                    col_id, name, col_type, not_null, default, pk = col
                    pk_marker = " (PK)" if pk else ""
                    not_null_marker = " NOT NULL" if not_null else ""
                    default_marker = f" DEFAULT {default}" if default else ""
                    
                    print(f"  {name:<25} {col_type:<15}{pk_marker}{not_null_marker}{default_marker}")
                
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"  Total Records: {count}")
            
            # Show views
            cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
            views = cursor.fetchall()
            
            if views:
                print("\nDatabase Views:")
                print("-" * 40)
                for view in views:
                    print(f"  - {view[0]}")
            
            print("\n" + "="*60)
            
        except Exception as e:
            logger.error(f"Failed to generate schema report: {e}")
        
        finally:
            if self.connection:
                self.connection.close()

def main():
    """Main execution function"""
    print("Enhanced Database Schema Creator")
    print("خلي قاعدة البيانات تحتوي علي كل الخانات")
    print("="*50)
    
    enhancer = DatabaseEnhancer()
    
    # Run enhancement
    success = enhancer.run_enhancement()
    
    if success:
        print("\n✅ Database enhancement completed successfully!")
        print("\nGenerating schema report...")
        enhancer.generate_schema_report()
    else:
        print("\n❌ Database enhancement failed!")
    
    return success

if __name__ == "__main__":
    main()