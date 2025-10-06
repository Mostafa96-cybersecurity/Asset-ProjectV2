#!/usr/bin/env python3
"""
🔧 ENHANCED AD INTEGRATION WITH DOMAIN COMPUTERS TABLE
====================================================
Enhancement 6 & 7: AD Integration + Domain Computers Database

Features:
- Working AD Integration with LDAP
- Domain Computers table in database
- Comprehensive computer collection via LDAP
- Multithreaded performance
- Proper authentication
"""

import os
import sqlite3
import json
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

try:
    import ldap3
    from ldap3 import Server, Connection, ALL, NTLM
    LDAP3_AVAILABLE = True
except ImportError:
    LDAP3_AVAILABLE = False
    print("⚠️ ldap3 not available - install with: pip install ldap3")

class EnhancedADIntegration:
    """Enhanced Active Directory Integration with Domain Computers table"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.db_connection = None
        self.ad_connection = None
        self.domain_computers = []
        self.collection_threads = []
        self.is_collecting = False
        self.stop_event = threading.Event()
        
        # AD Configuration
        self.ad_config = {
            'server': '',
            'domain': '',
            'username': '',
            'password': '',
            'search_base': '',
            'use_ssl': True
        }
        
        # Load configuration
        self.load_ad_configuration()
        
        # Initialize database
        self.init_domain_computers_table()
    
    def _setup_logging(self):
        """Setup logging for AD integration"""
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger('ADIntegration')
    
    def load_ad_configuration(self):
        """Load AD configuration from file"""
        try:
            if os.path.exists('ad_config.json'):
                with open('ad_config.json', 'r') as f:
                    saved_config = json.load(f)
                    self.ad_config.update(saved_config)
                    self.logger.info("✅ AD configuration loaded")
            else:
                self.create_default_ad_config()
        except Exception as e:
            self.logger.error(f"❌ Error loading AD config: {e}")
            self.create_default_ad_config()
    
    def create_default_ad_config(self):
        """Create default AD configuration"""
        self.ad_config = {
            'server': 'dc.company.com',  # Replace with your domain controller
            'domain': 'COMPANY',         # Replace with your domain
            'username': 'admin',         # Replace with admin username
            'password': '',              # Will be prompted
            'search_base': 'DC=company,DC=com',  # Replace with your DN
            'use_ssl': True,
            'port': 636,  # 636 for SSL, 389 for non-SSL
            'computer_filter': '(objectClass=computer)',
            'attributes': [
                'cn', 'name', 'dNSHostName', 'operatingSystem', 
                'operatingSystemVersion', 'lastLogonTimestamp', 
                'whenCreated', 'whenChanged', 'description',
                'distinguishedName', 'objectGUID', 'sAMAccountName'
            ]
        }
        
        # Save default config
        with open('ad_config.json', 'w') as f:
            json.dump(self.ad_config, f, indent=2)
        
        self.logger.info("📝 Default AD configuration created - please update ad_config.json")
    
    def init_domain_computers_table(self):
        """Initialize Domain Computers table in database"""
        try:
            conn = sqlite3.connect('assets.db')
            cursor = conn.cursor()
            
            # Create domain_computers table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS domain_computers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    computer_name TEXT UNIQUE,
                    dns_hostname TEXT,
                    distinguished_name TEXT,
                    sam_account_name TEXT,
                    object_guid TEXT,
                    operating_system TEXT,
                    operating_system_version TEXT,
                    description TEXT,
                    last_logon_timestamp TEXT,
                    when_created TEXT,
                    when_changed TEXT,
                    enabled BOOLEAN,
                    domain_name TEXT,
                    organizational_unit TEXT,
                    computer_account_control INTEGER,
                    password_last_set TEXT,
                    last_logon TEXT,
                    logon_count INTEGER,
                    service_principal_names TEXT,
                    managed_by TEXT,
                    location TEXT,
                    
                    -- Asset Management Integration
                    asset_id INTEGER,
                    asset_matched BOOLEAN DEFAULT FALSE,
                    ip_address TEXT,
                    mac_address TEXT,
                    device_type TEXT,
                    status TEXT,
                    
                    -- Collection Metadata
                    collected_via_ldap BOOLEAN DEFAULT TRUE,
                    ldap_collection_time TEXT,
                    last_sync_time TEXT,
                    sync_status TEXT,
                    collection_errors INTEGER DEFAULT 0,
                    
                    -- Additional Properties
                    primary_group_id INTEGER,
                    member_of TEXT,  -- JSON array of groups
                    user_account_control INTEGER,
                    bad_password_count INTEGER,
                    lockout_time TEXT,
                    
                    -- Timestamps
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    
                    FOREIGN KEY (asset_id) REFERENCES assets (id)
                )
            ''')
            
            # Create indexes for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_domain_computers_name ON domain_computers(computer_name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_domain_computers_dns ON domain_computers(dns_hostname)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_domain_computers_asset ON domain_computers(asset_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_domain_computers_sync ON domain_computers(last_sync_time)')
            
            conn.commit()
            conn.close()
            
            self.logger.info("✅ Domain Computers table initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize domain_computers table: {e}")
    
    def connect_to_ad(self, username=None, password=None):
        """Connect to Active Directory using LDAP"""
        if not LDAP3_AVAILABLE:
            self.logger.error("❌ ldap3 library not available")
            return False
        
        try:
            # Use provided credentials or config
            user = username or self.ad_config['username']
            pwd = password or self.ad_config['password']
            
            if not pwd:
                self.logger.error("❌ No password provided for AD connection")
                return False
            
            # Create server connection
            server_uri = self.ad_config['server']
            port = self.ad_config.get('port', 636 if self.ad_config['use_ssl'] else 389)
            use_ssl = self.ad_config['use_ssl']
            
            server = Server(server_uri, port=port, use_ssl=use_ssl, get_info=ALL)
            
            # Create connection with NTLM authentication
            user_dn = f"{self.ad_config['domain']}\\{user}"
            
            self.ad_connection = Connection(
                server,
                user=user_dn,
                password=pwd,
                authentication=NTLM,
                auto_bind=True
            )
            
            self.logger.info(f"✅ Connected to AD server: {server_uri}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ AD connection failed: {e}")
            return False
    
    def collect_domain_computers(self, max_threads=5):
        """Collect all domain computers via LDAP with multithreading"""
        if not self.ad_connection:
            self.logger.error("❌ No AD connection available")
            return False
        
        if self.is_collecting:
            self.logger.warning("⚠️ Collection already in progress")
            return False
        
        self.logger.info("🔍 Starting domain computers collection...")
        self.is_collecting = True
        self.stop_event.clear()
        
        try:
            # Search for all computer objects
            search_base = self.ad_config['search_base']
            search_filter = self.ad_config['computer_filter']
            attributes = self.ad_config['attributes']
            
            success = self.ad_connection.search(
                search_base=search_base,
                search_filter=search_filter,
                attributes=attributes
            )
            
            if not success:
                self.logger.error(f"❌ LDAP search failed: {self.ad_connection.last_error}")
                return False
            
            entries = self.ad_connection.entries
            self.logger.info(f"📊 Found {len(entries)} domain computers")
            
            # Process computers in parallel
            self._process_computers_multithreaded(entries, max_threads)
            
            self.logger.info("✅ Domain computers collection completed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Domain computers collection failed: {e}")
            return False
        finally:
            self.is_collecting = False
    
    def _process_computers_multithreaded(self, entries, max_threads):
        """Process computer entries using multithreading"""
        
        # Divide entries into chunks for threads
        chunk_size = max(1, len(entries) // max_threads)
        chunks = [entries[i:i + chunk_size] for i in range(0, len(entries), chunk_size)]
        
        threads = []
        
        for i, chunk in enumerate(chunks):
            thread = threading.Thread(
                target=self._process_computer_chunk,
                args=(chunk, i),
                name=f"ADCollector-{i}",
                daemon=False
            )
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        self.logger.info(f"✅ Processed {len(entries)} computers using {len(threads)} threads")
    
    def _process_computer_chunk(self, entries, thread_id):
        """Process a chunk of computer entries"""
        processed = 0
        
        for entry in entries:
            if self.stop_event.is_set():
                break
                
            try:
                computer_data = self._extract_computer_data(entry)
                self._save_domain_computer(computer_data)
                processed += 1
                
            except Exception as e:
                self.logger.error(f"❌ Error processing computer in thread {thread_id}: {e}")
        
        self.logger.info(f"✅ Thread {thread_id} processed {processed} computers")
    
    def _extract_computer_data(self, entry):
        """Extract computer data from LDAP entry"""
        
        # Helper function to safely get attribute value
        def get_attr(attr_name, default=''):
            try:
                value = getattr(entry, attr_name, None)
                if value is None:
                    return default
                if isinstance(value, list):
                    return value[0] if value else default
                return str(value)
            except:
                return default
        
        # Extract basic information
        computer_data = {
            'computer_name': get_attr('cn'),
            'dns_hostname': get_attr('dNSHostName'),
            'distinguished_name': get_attr('distinguishedName'),
            'sam_account_name': get_attr('sAMAccountName'),
            'object_guid': get_attr('objectGUID'),
            'operating_system': get_attr('operatingSystem'),
            'operating_system_version': get_attr('operatingSystemVersion'),
            'description': get_attr('description'),
            'when_created': get_attr('whenCreated'),
            'when_changed': get_attr('whenChanged'),
            'domain_name': self.ad_config['domain']
        }
        
        # Process timestamps
        last_logon = get_attr('lastLogonTimestamp')
        if last_logon:
            try:
                # Convert Windows filetime to datetime
                import datetime as dt
                timestamp = int(last_logon)
                if timestamp > 0:
                    # Windows filetime epoch starts at 1601-01-01
                    epoch = dt.datetime(1601, 1, 1)
                    computer_data['last_logon_timestamp'] = (epoch + dt.timedelta(microseconds=timestamp/10)).isoformat()
            except:
                computer_data['last_logon_timestamp'] = last_logon
        
        # Extract OU from DN
        dn = computer_data['distinguished_name']
        if dn:
            ou_parts = [part for part in dn.split(',') if part.strip().startswith('OU=')]
            computer_data['organizational_unit'] = ','.join(ou_parts)
        
        # Collection metadata
        computer_data.update({
            'collected_via_ldap': True,
            'ldap_collection_time': datetime.now().isoformat(),
            'last_sync_time': datetime.now().isoformat(),
            'sync_status': 'Success',
            'collection_errors': 0,
            'status': 'Domain Computer'
        })
        
        return computer_data
    
    def _save_domain_computer(self, computer_data):
        """Save domain computer to database"""
        try:
            conn = sqlite3.connect('assets.db')
            cursor = conn.cursor()
            
            # Prepare data for insertion
            columns = list(computer_data.keys())
            placeholders = ', '.join(['?' for _ in columns])
            column_list = ', '.join(columns)
            values = [computer_data[col] for col in columns]
            
            # Insert or update
            cursor.execute(f'''
                INSERT OR REPLACE INTO domain_computers ({column_list})
                VALUES ({placeholders})
            ''', values)
            
            # Try to match with existing assets
            self._match_with_assets(cursor, computer_data)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"❌ Failed to save domain computer: {e}")
    
    def _match_with_assets(self, cursor, computer_data):
        """Match domain computer with existing assets"""
        try:
            computer_name = computer_data.get('computer_name', '')
            dns_hostname = computer_data.get('dns_hostname', '')
            
            # Try to find matching asset by hostname
            for hostname in [computer_name, dns_hostname]:
                if hostname:
                    cursor.execute('''
                        SELECT id FROM assets 
                        WHERE hostname = ? OR computer_name = ?
                    ''', (hostname, hostname))
                    
                    result = cursor.fetchone()
                    if result:
                        asset_id = result[0]
                        
                        # Update domain computer with asset link
                        cursor.execute('''
                            UPDATE domain_computers 
                            SET asset_id = ?, asset_matched = TRUE 
                            WHERE computer_name = ?
                        ''', (asset_id, computer_data['computer_name']))
                        
                        # Update asset with domain info
                        cursor.execute('''
                            UPDATE assets 
                            SET domain_name = ?, domain_workgroup = ?, 
                                operating_system = ?, os_name = ?
                            WHERE id = ?
                        ''', (
                            computer_data['domain_name'],
                            computer_data['domain_name'],
                            computer_data['operating_system'],
                            computer_data['operating_system'],
                            asset_id
                        ))
                        
                        self.logger.debug(f"✅ Matched {computer_name} with asset ID {asset_id}")
                        break
                        
        except Exception as e:
            self.logger.error(f"❌ Error matching with assets: {e}")
    
    def get_domain_computers_summary(self):
        """Get summary of domain computers"""
        try:
            conn = sqlite3.connect('assets.db')
            cursor = conn.cursor()
            
            # Get counts
            cursor.execute('SELECT COUNT(*) FROM domain_computers')
            total_computers = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM domain_computers WHERE asset_matched = TRUE')
            matched_computers = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM domain_computers WHERE operating_system LIKE "%Windows%"')
            windows_computers = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM domain_computers WHERE operating_system LIKE "%Server%"')
            server_computers = cursor.fetchone()[0]
            
            # Get recent computers
            cursor.execute('''
                SELECT computer_name, operating_system, last_sync_time, asset_matched
                FROM domain_computers 
                ORDER BY last_sync_time DESC 
                LIMIT 10
            ''')
            recent_computers = cursor.fetchall()
            
            conn.close()
            
            return {
                'total_computers': total_computers,
                'matched_computers': matched_computers,
                'windows_computers': windows_computers,
                'server_computers': server_computers,
                'match_percentage': round((matched_computers / total_computers * 100), 1) if total_computers > 0 else 0,
                'recent_computers': recent_computers
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error getting domain computers summary: {e}")
            return None
    
    def stop_collection(self):
        """Stop the collection process"""
        self.logger.info("🛑 Stopping domain computers collection...")
        self.stop_event.set()
        self.is_collecting = False
    
    def disconnect_ad(self):
        """Disconnect from Active Directory"""
        if self.ad_connection:
            try:
                self.ad_connection.unbind()
                self.ad_connection = None
                self.logger.info("✅ Disconnected from AD")
            except Exception as e:
                self.logger.error(f"❌ Error disconnecting from AD: {e}")

# Convenience functions
def setup_ad_integration(server, domain, username, password, search_base):
    """Setup AD integration with provided credentials"""
    ad_integration = EnhancedADIntegration()
    
    # Update configuration
    ad_integration.ad_config.update({
        'server': server,
        'domain': domain,
        'username': username,
        'password': password,
        'search_base': search_base
    })
    
    # Save configuration
    with open('ad_config.json', 'w') as f:
        json.dump(ad_integration.ad_config, f, indent=2)
    
    return ad_integration

def collect_domain_computers_now(username=None, password=None):
    """Collect domain computers immediately"""
    ad_integration = EnhancedADIntegration()
    
    if ad_integration.connect_to_ad(username, password):
        return ad_integration.collect_domain_computers()
    else:
        print("❌ Failed to connect to Active Directory")
        return False

if __name__ == "__main__":
    print("🔧 Enhanced AD Integration with Domain Computers Table")
    print("="*60)
    
    # Test the integration
    ad_integration = EnhancedADIntegration()
    print("✅ AD Integration initialized")
    print("📝 Please configure ad_config.json with your AD settings")
    
    # Show summary if data exists
    summary = ad_integration.get_domain_computers_summary()
    if summary:
        print(f"📊 Domain Computers Summary:")
        print(f"   Total: {summary['total_computers']}")
        print(f"   Matched with Assets: {summary['matched_computers']} ({summary['match_percentage']}%)")
        print(f"   Windows: {summary['windows_computers']}")
        print(f"   Servers: {summary['server_computers']}")