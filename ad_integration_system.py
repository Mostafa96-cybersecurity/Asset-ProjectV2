#!/usr/bin/env python3
"""
🏢 ACTIVE DIRECTORY INTEGRATION SYSTEM
=====================================
Complete AD connectivity with dedicated database table
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ActiveDirectoryDatabase:
    """Dedicated AD database operations"""
    
    def __init__(self, db_path: str = "assets.db"):
        self.db_path = db_path
        self.create_ad_table()
    
    def create_ad_table(self):
        """Create dedicated AD computers table with isolated columns"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create AD computers table with comprehensive fields
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ad_computers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                
                -- Core AD Identity
                distinguished_name TEXT UNIQUE NOT NULL,
                common_name TEXT,
                sam_account_name TEXT,
                canonical_name TEXT,
                object_guid TEXT,
                object_sid TEXT,
                
                -- Computer Information
                computer_name TEXT,
                dns_hostname TEXT,
                ip_address TEXT,
                operating_system TEXT,
                os_version TEXT,
                os_service_pack TEXT,
                
                -- AD Organizational Structure
                organizational_unit TEXT,
                domain_name TEXT,
                site_name TEXT,
                container_path TEXT,
                
                -- Status and Timestamps
                enabled BOOLEAN,
                account_locked BOOLEAN,
                password_last_set TEXT,
                last_logon TEXT,
                last_logon_timestamp TEXT,
                when_created TEXT,
                when_changed TEXT,
                
                -- Hardware Information (from AD attributes)
                manufacturer TEXT,
                model TEXT,
                serial_number TEXT,
                asset_tag TEXT,
                
                -- Network Configuration
                primary_group_id INTEGER,
                member_of TEXT, -- JSON array of groups
                managed_by TEXT,
                location TEXT,
                description TEXT,
                
                -- Trust and Security
                trust_attributes INTEGER,
                user_account_control INTEGER,
                service_principal_names TEXT, -- JSON array
                
                -- Custom Attributes
                department TEXT,
                office TEXT,
                phone_number TEXT,
                owner TEXT,
                cost_center TEXT,
                
                -- Collection Metadata
                ad_server TEXT,
                collection_date TEXT,
                last_sync TEXT,
                sync_status TEXT,
                error_message TEXT,
                
                -- Integration with main assets table
                assets_table_id INTEGER, -- Foreign key to assets table
                is_synced BOOLEAN DEFAULT FALSE,
                sync_conflicts TEXT -- JSON of any conflicts during sync
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ad_dn ON ad_computers(distinguished_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ad_name ON ad_computers(computer_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ad_ip ON ad_computers(ip_address)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ad_domain ON ad_computers(domain_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ad_enabled ON ad_computers(enabled)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ad_sync ON ad_computers(is_synced)')
        
        conn.commit()
        conn.close()
        
        logger.info("✅ AD computers table created with isolated columns")
    
    def insert_ad_computer(self, computer_data: Dict[str, Any]) -> int:
        """Insert AD computer data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Prepare data with current timestamp
        computer_data['collection_date'] = datetime.now().isoformat()
        computer_data['last_sync'] = datetime.now().isoformat()
        computer_data['sync_status'] = 'collected'
        
        # Convert arrays to JSON strings
        if 'member_of' in computer_data and isinstance(computer_data['member_of'], list):
            computer_data['member_of'] = json.dumps(computer_data['member_of'])
        
        if 'service_principal_names' in computer_data and isinstance(computer_data['service_principal_names'], list):
            computer_data['service_principal_names'] = json.dumps(computer_data['service_principal_names'])
        
        # Dynamic insert based on available data
        columns = list(computer_data.keys())
        placeholders = ', '.join(['?' for _ in columns])
        column_names = ', '.join(columns)
        
        query = f'''
            INSERT OR REPLACE INTO ad_computers ({column_names})
            VALUES ({placeholders})
        '''
        
        try:
            cursor.execute(query, list(computer_data.values()))
            computer_id = cursor.lastrowid or -1
            conn.commit()
            
            logger.info(f"✅ Inserted AD computer: {computer_data.get('computer_name', 'Unknown')}")
            return computer_id
            
        except Exception as e:
            logger.error(f"❌ Error inserting AD computer: {e}")
            conn.rollback()
            return -1
        finally:
            conn.close()
    
    def get_ad_computers(self, filters: Optional[Dict] = None) -> List[Dict]:
        """Get AD computers with optional filters"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM ad_computers"
        params = []
        
        if filters:
            conditions = []
            for key, value in filters.items():
                if value is not None:
                    conditions.append(f"{key} = ?")
                    params.append(value)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY computer_name"
        
        cursor.execute(query, params)
        columns = [description[0] for description in cursor.description]
        
        results = []
        for row in cursor.fetchall():
            computer = dict(zip(columns, row))
            
            # Parse JSON fields back to lists
            if computer.get('member_of'):
                try:
                    computer['member_of'] = json.loads(computer['member_of'])
                except:
                    pass
            
            if computer.get('service_principal_names'):
                try:
                    computer['service_principal_names'] = json.loads(computer['service_principal_names'])
                except:
                    pass
            
            results.append(computer)
        
        conn.close()
        return results
    
    def get_ad_statistics(self) -> Dict[str, Any]:
        """Get AD collection statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Total computers
        cursor.execute("SELECT COUNT(*) FROM ad_computers")
        stats['total_computers'] = cursor.fetchone()[0]
        
        # Enabled vs disabled
        cursor.execute("SELECT COUNT(*) FROM ad_computers WHERE enabled = 1")
        stats['enabled_computers'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM ad_computers WHERE enabled = 0")
        stats['disabled_computers'] = cursor.fetchone()[0]
        
        # By domain
        cursor.execute("SELECT domain_name, COUNT(*) FROM ad_computers GROUP BY domain_name")
        stats['by_domain'] = dict(cursor.fetchall())
        
        # Operating systems
        cursor.execute("SELECT operating_system, COUNT(*) FROM ad_computers WHERE operating_system IS NOT NULL GROUP BY operating_system")
        stats['by_os'] = dict(cursor.fetchall())
        
        # Sync status
        cursor.execute("SELECT is_synced, COUNT(*) FROM ad_computers GROUP BY is_synced")
        sync_results = cursor.fetchall()
        stats['sync_status'] = {'synced': 0, 'not_synced': 0}
        for synced, count in sync_results:
            if synced:
                stats['sync_status']['synced'] = count
            else:
                stats['sync_status']['not_synced'] = count
        
        # Recent collections
        cursor.execute("""
            SELECT COUNT(*) FROM ad_computers 
            WHERE collection_date > datetime('now', '-24 hours')
        """)
        stats['collected_last_24h'] = cursor.fetchone()[0]
        
        conn.close()
        return stats


class ActiveDirectoryConnector:
    """AD connection and data collection"""
    
    def __init__(self, ad_database: ActiveDirectoryDatabase):
        self.ad_db = ad_database
        self.connection = None
        self.server_info = {}
    
    def connect_to_ad(self, server: str, username: str, password: str, 
                     domain: Optional[str] = None, use_ssl: bool = True, port: Optional[int] = None) -> bool:
        """Connect to Active Directory using LDAP3"""
        try:
            from ldap3 import Server, Connection, ALL, NTLM, ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES
            
            # Determine port
            if port is None:
                port = 636 if use_ssl else 389
            
            # Create server object
            server_obj = Server(
                server, 
                port=port, 
                use_ssl=use_ssl, 
                get_info=ALL
            )
            
            # Format username
            if domain and '\\' not in username and '@' not in username:
                username = f"{domain}\\{username}"
            
            # Create connection
            self.connection = Connection(
                server_obj,
                user=username,
                password=password,
                authentication=NTLM,
                auto_bind='AUTO_BIND_NONE'
            )
            
            # Manually bind
            self.connection.bind()
            
            if self.connection.bound:
                self.server_info = {
                    'server': server,
                    'port': port,
                    'ssl': use_ssl,
                    'domain': domain,
                    'connected_at': datetime.now().isoformat(),
                    'server_info': str(server_obj.info) if server_obj.info else None
                }
                
                logger.info(f"✅ Connected to AD server: {server}:{port}")
                return True
            else:
                logger.error(f"❌ Failed to bind to AD server: {server}")
                return False
                
        except ImportError:
            logger.error("❌ ldap3 library not installed. Run: pip install ldap3")
            return False
        except Exception as e:
            logger.error(f"❌ AD connection error: {e}")
            return False
    
    def get_domain_computers(self, base_dn: Optional[str] = None, 
                           computer_filter: Optional[str] = None) -> List[Dict]:
        """Get all computers from Active Directory"""
        if not self.connection or not self.connection.bound:
            logger.error("❌ Not connected to AD")
            return []
        
        try:
            from ldap3 import ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES
            
            # Auto-detect base DN if not provided
            if not base_dn:
                if self.connection.server.info and self.connection.server.info.naming_contexts:
                    base_dn = self.connection.server.info.naming_contexts[0]
                else:
                    # Fallback: construct from domain
                    domain = self.server_info.get('domain', '')
                    if domain:
                        base_dn = ','.join([f'DC={part}' for part in domain.split('.')])
                    else:
                        logger.error("❌ Cannot determine base DN")
                        return []
            
            # Default computer filter
            if not computer_filter:
                computer_filter = '(&(objectClass=computer)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))'  # Enabled computers
            
            logger.info(f"🔍 Searching AD computers in: {base_dn}")
            logger.info(f"🔍 Filter: {computer_filter}")
            
            # Search for computers
            success = self.connection.search(
                search_base=base_dn,
                search_filter=computer_filter,
                attributes=[
                    ALL_ATTRIBUTES,
                    ALL_OPERATIONAL_ATTRIBUTES
                ]
            )
            
            if not success:
                logger.error(f"❌ AD search failed: {self.connection.result}")
                return []
            
            computers = []
            for entry in self.connection.entries:
                computer_data = self._parse_ad_computer_entry(entry)
                if computer_data:
                    computers.append(computer_data)
            
            logger.info(f"✅ Found {len(computers)} computers in AD")
            return computers
            
        except Exception as e:
            logger.error(f"❌ Error querying AD computers: {e}")
            return []
    
    def _parse_ad_computer_entry(self, entry) -> Optional[Dict]:
        """Parse AD entry into computer data"""
        try:
            computer_data = {
                'ad_server': self.server_info.get('server', ''),
                'domain_name': self.server_info.get('domain', '')
            }
            
            # Basic identity
            computer_data['distinguished_name'] = str(entry.distinguishedName) if hasattr(entry, 'distinguishedName') else ''
            computer_data['common_name'] = str(entry.cn) if hasattr(entry, 'cn') else ''
            computer_data['sam_account_name'] = str(entry.sAMAccountName) if hasattr(entry, 'sAMAccountName') else ''
            computer_data['canonical_name'] = str(entry.canonicalName) if hasattr(entry, 'canonicalName') else ''
            
            # GUIDs and SIDs
            if hasattr(entry, 'objectGUID'):
                computer_data['object_guid'] = str(entry.objectGUID)
            if hasattr(entry, 'objectSid'):
                computer_data['object_sid'] = str(entry.objectSid)
            
            # Computer information
            computer_data['computer_name'] = str(entry.name) if hasattr(entry, 'name') else ''
            computer_data['dns_hostname'] = str(entry.dNSHostName) if hasattr(entry, 'dNSHostName') else ''
            
            # Operating system
            computer_data['operating_system'] = str(entry.operatingSystem) if hasattr(entry, 'operatingSystem') else ''
            computer_data['os_version'] = str(entry.operatingSystemVersion) if hasattr(entry, 'operatingSystemVersion') else ''
            computer_data['os_service_pack'] = str(entry.operatingSystemServicePack) if hasattr(entry, 'operatingSystemServicePack') else ''
            
            # Organizational structure
            dn = computer_data['distinguished_name']
            if dn:
                # Extract OU from DN
                dn_parts = dn.split(',')
                ou_parts = [part.strip() for part in dn_parts if part.strip().startswith('OU=')]
                computer_data['organizational_unit'] = ','.join([part[3:] for part in ou_parts])
                computer_data['container_path'] = ','.join(dn_parts[1:])  # Everything except CN
            
            # Status
            uac = entry.userAccountControl.value if hasattr(entry, 'userAccountControl') else 0
            computer_data['user_account_control'] = uac
            computer_data['enabled'] = not bool(uac & 2)  # ADS_UF_ACCOUNTDISABLE = 2
            computer_data['account_locked'] = bool(uac & 16)  # ADS_UF_LOCKOUT = 16
            
            # Timestamps
            if hasattr(entry, 'pwdLastSet'):
                computer_data['password_last_set'] = str(entry.pwdLastSet)
            if hasattr(entry, 'lastLogon'):
                computer_data['last_logon'] = str(entry.lastLogon)
            if hasattr(entry, 'lastLogonTimestamp'):
                computer_data['last_logon_timestamp'] = str(entry.lastLogonTimestamp)
            if hasattr(entry, 'whenCreated'):
                computer_data['when_created'] = str(entry.whenCreated)
            if hasattr(entry, 'whenChanged'):
                computer_data['when_changed'] = str(entry.whenChanged)
            
            # Groups and management
            if hasattr(entry, 'memberOf'):
                computer_data['member_of'] = [str(group) for group in entry.memberOf]
            if hasattr(entry, 'managedBy'):
                computer_data['managed_by'] = str(entry.managedBy)
            
            # Service Principal Names
            if hasattr(entry, 'servicePrincipalName'):
                computer_data['service_principal_names'] = [str(spn) for spn in entry.servicePrincipalName]
            
            # Location and description
            computer_data['location'] = str(entry.location) if hasattr(entry, 'location') else ''
            computer_data['description'] = str(entry.description) if hasattr(entry, 'description') else ''
            
            # Custom attributes (if they exist)
            computer_data['department'] = str(entry.department) if hasattr(entry, 'department') else ''
            computer_data['office'] = str(entry.physicalDeliveryOfficeName) if hasattr(entry, 'physicalDeliveryOfficeName') else ''
            
            # Remove empty strings and None values
            computer_data = {k: v for k, v in computer_data.items() if v not in ('', None, [])}
            
            return computer_data
            
        except Exception as e:
            logger.error(f"❌ Error parsing AD entry: {e}")
            return None
    
    def collect_and_store_computers(self, base_dn: Optional[str] = None, 
                                  computer_filter: Optional[str] = None) -> int:
        """Collect computers from AD and store in database"""
        computers = self.get_domain_computers(base_dn, computer_filter)
        
        stored_count = 0
        for computer in computers:
            computer_id = self.ad_db.insert_ad_computer(computer)
            if computer_id > 0:
                stored_count += 1
        
        logger.info(f"✅ Stored {stored_count} computers in AD database")
        return stored_count
    
    def disconnect(self):
        """Disconnect from AD"""
        if self.connection:
            self.connection.unbind()
            self.connection = None
            logger.info("✅ Disconnected from AD")


class ADIntegrationManager:
    """Main AD integration class"""
    
    def __init__(self, db_path: str = "assets.db"):
        self.ad_db = ActiveDirectoryDatabase(db_path)
        self.ad_connector = ActiveDirectoryConnector(self.ad_db)
        self.config_file = "ad_config.json"
    
    def save_ad_configuration(self, config: Dict):
        """Save AD configuration"""
        config['saved_at'] = datetime.now().isoformat()
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info("✅ AD configuration saved")
    
    def load_ad_configuration(self) -> Optional[Dict]:
        """Load AD configuration"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"❌ Error loading AD config: {e}")
        return None
    
    def test_ad_connection(self, server: str, username: str, password: str, 
                          domain: Optional[str] = None) -> bool:
        """Test AD connection"""
        logger.info(f"🧪 Testing AD connection to {server}...")
        
        success = self.ad_connector.connect_to_ad(
            server=server,
            username=username,
            password=password,
            domain=domain
        )
        
        if success:
            # Test search
            try:
                computers = self.ad_connector.get_domain_computers()
                logger.info(f"✅ Test successful: Found {len(computers)} computers")
                self.ad_connector.disconnect()
                return True
            except Exception as e:
                logger.error(f"❌ Test search failed: {e}")
                self.ad_connector.disconnect()
                return False
        
        return False
    
    def full_ad_sync(self, server: str, username: str, password: str, 
                    domain: Optional[str] = None, base_dn: Optional[str] = None) -> Dict[str, Any]:
        """Perform full AD synchronization"""
        result = {
            'success': False,
            'computers_collected': 0,
            'errors': [],
            'start_time': datetime.now().isoformat()
        }
        
        try:
            # Connect
            if not self.ad_connector.connect_to_ad(server, username, password, domain):
                result['errors'].append("Failed to connect to AD")
                return result
            
            # Collect and store
            computers_count = self.ad_connector.collect_and_store_computers(base_dn)
            result['computers_collected'] = computers_count
            result['success'] = True
            
            # Save configuration for future use
            config = {
                'server': server,
                'domain': domain,
                'base_dn': base_dn,
                'last_sync': datetime.now().isoformat(),
                'last_sync_count': computers_count
            }
            self.save_ad_configuration(config)
            
        except Exception as e:
            result['errors'].append(str(e))
        finally:
            self.ad_connector.disconnect()
            result['end_time'] = datetime.now().isoformat()
        
        return result


def main():
    """Test AD integration"""
    print("🏢 ACTIVE DIRECTORY INTEGRATION SYSTEM")
    print("=" * 60)
    
    # Initialize
    ad_manager = ADIntegrationManager()
    
    # Test database creation
    print("📊 Testing database setup...")
    stats = ad_manager.ad_db.get_ad_statistics()
    print(f"✅ AD database ready. Current computers: {stats['total_computers']}")
    
    print("\n💡 AD Integration ready!")
    print("Next steps:")
    print("1. Configure AD connection in GUI")
    print("2. Test connection")
    print("3. Sync computers from domain")
    print("4. Integrate with main assets collection")


if __name__ == "__main__":
    main()