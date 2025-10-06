#!/usr/bin/env python3
"""
🏢 AD DATABASE INTEGRATION
========================
Creates dedicated AD table and integrates with existing ad_fetcher.py
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Any

class ADDatabase:
    """Dedicated AD database operations with isolated columns"""
    
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
                
                -- Core AD Identity (isolated columns)
                distinguished_name TEXT UNIQUE,
                common_name TEXT,
                sam_account_name TEXT,
                object_guid TEXT,
                object_sid TEXT,
                
                -- Computer Information
                hostname TEXT,
                fqdn TEXT,
                dns_hostname TEXT,
                computer_name TEXT,
                
                -- Operating System
                operating_system TEXT,
                os_version TEXT,
                os_name_and_version TEXT,
                
                -- AD Timestamps
                when_created TEXT,
                when_changed TEXT,
                last_logon_timestamp TEXT,
                password_last_set TEXT,
                
                -- AD Organizational Structure
                organizational_unit TEXT,
                domain_name TEXT,
                container_path TEXT,
                
                -- Status Information
                enabled BOOLEAN DEFAULT TRUE,
                account_locked BOOLEAN DEFAULT FALSE,
                user_account_control INTEGER,
                
                -- Network and Location
                ip_address TEXT,
                location TEXT,
                description TEXT,
                site_name TEXT,
                
                -- Group Membership and Management
                member_of TEXT, -- JSON array of groups
                managed_by TEXT,
                primary_group_id INTEGER,
                
                -- Service Information
                service_principal_names TEXT, -- JSON array
                
                -- Custom Attributes
                department TEXT,
                office TEXT,
                owner TEXT,
                cost_center TEXT,
                asset_tag TEXT,
                
                -- Collection Metadata
                ad_server TEXT,
                collection_date TEXT,
                last_sync TEXT,
                sync_status TEXT DEFAULT 'collected',
                
                -- Integration with main assets table
                assets_table_id INTEGER, -- Foreign key to assets table
                is_synced_to_assets BOOLEAN DEFAULT FALSE,
                sync_conflicts TEXT, -- JSON of any conflicts during sync
                
                -- Additional fields from your ad_fetcher
                ad_when_created TEXT,
                ad_last_logon_timestamp TEXT
            )
        ''')
        
        # Create indexes for performance
        indexes = [
            'CREATE INDEX IF NOT EXISTS idx_ad_dn ON ad_computers(distinguished_name)',
            'CREATE INDEX IF NOT EXISTS idx_ad_hostname ON ad_computers(hostname)',
            'CREATE INDEX IF NOT EXISTS idx_ad_fqdn ON ad_computers(fqdn)',
            'CREATE INDEX IF NOT EXISTS idx_ad_domain ON ad_computers(domain_name)',
            'CREATE INDEX IF NOT EXISTS idx_ad_enabled ON ad_computers(enabled)',
            'CREATE INDEX IF NOT EXISTS idx_ad_sync ON ad_computers(is_synced_to_assets)',
            'CREATE INDEX IF NOT EXISTS idx_ad_assets_id ON ad_computers(assets_table_id)'
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        conn.commit()
        conn.close()
        
        print("✅ AD computers table created with isolated columns")
    
    def insert_ad_computer_from_fetcher(self, ad_item: Dict) -> Optional[int]:
        """Insert AD computer data from your ad_fetcher format"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Map your ad_fetcher fields to our AD table
        computer_data = {
            'hostname': ad_item.get('Hostname', ''),
            'fqdn': ad_item.get('FQDN', ''),
            'dns_hostname': ad_item.get('FQDN', ''),
            'computer_name': ad_item.get('Hostname', ''),
            'operating_system': ad_item.get('OS Name and Version', ''),
            'os_version': ad_item.get('OS Version', ''),
            'os_name_and_version': ad_item.get('OS Name and Version', ''),
            'distinguished_name': ad_item.get('DN', ''),
            'object_guid': ad_item.get('objectGUID', ''),
            'object_sid': ad_item.get('objectSid', ''),
            'ad_when_created': ad_item.get('AD whenCreated', ''),
            'ad_last_logon_timestamp': ad_item.get('AD lastLogonTimestamp', ''),
            'collection_date': datetime.now().isoformat(),
            'last_sync': datetime.now().isoformat(),
            'sync_status': 'collected_from_ad_fetcher'
        }
        
        # Extract domain from FQDN
        fqdn = computer_data.get('fqdn', '')
        if '.' in fqdn:
            computer_data['domain_name'] = '.'.join(fqdn.split('.')[1:])
        
        # Remove empty values
        computer_data = {k: v for k, v in computer_data.items() if v not in ('', None)}
        
        # Dynamic insert
        columns = list(computer_data.keys())
        placeholders = ', '.join(['?' for _ in columns])
        column_names = ', '.join(columns)
        
        query = f'''
            INSERT OR REPLACE INTO ad_computers ({column_names})
            VALUES ({placeholders})
        '''
        
        try:
            cursor.execute(query, list(computer_data.values()))
            computer_id = cursor.lastrowid
            conn.commit()
            
            print(f"✅ Stored AD computer: {computer_data.get('hostname', 'Unknown')}")
            return computer_id
            
        except Exception as e:
            print(f"❌ Error storing AD computer: {e}")
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
        
        query += " ORDER BY hostname"
        
        cursor.execute(query, params)
        columns = [description[0] for description in cursor.description]
        
        results = []
        for row in cursor.fetchall():
            computer = dict(zip(columns, row))
            
            # Parse JSON fields
            if computer.get('member_of'):
                try:
                    computer['member_of'] = json.loads(computer['member_of'])
                except:
                    pass
            
            results.append(computer)
        
        conn.close()
        return results
    
    def sync_ad_to_assets_table(self) -> Dict[str, int]:
        """Sync AD computers to main assets table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get AD computers not yet synced
        cursor.execute('''
            SELECT * FROM ad_computers 
            WHERE is_synced_to_assets = FALSE OR is_synced_to_assets IS NULL
        ''')
        
        columns = [description[0] for description in cursor.description]
        ad_computers = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        synced_count = 0
        updated_count = 0
        new_count = 0
        
        for ad_comp in ad_computers:
            hostname = ad_comp.get('hostname', '')
            if not hostname:
                continue
            
            # Check if device exists in assets table
            cursor.execute('''
                SELECT id FROM assets 
                WHERE hostname = ? OR computer_name = ?
            ''', (hostname, hostname))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing asset with AD data
                assets_id = existing[0]
                
                update_data = {
                    'hostname': hostname,
                    'computer_name': hostname,
                    'domain': ad_comp.get('domain_name', ''),
                    'os_name': ad_comp.get('operating_system', ''),
                    'device_type': 'Computer',
                    'data_source': 'Active Directory',
                    'last_update': datetime.now().isoformat()
                }
                
                # Build dynamic update query
                set_clauses = []
                values = []
                for key, value in update_data.items():
                    set_clauses.append(f"{key} = ?")
                    values.append(value)
                
                values.append(assets_id)
                
                update_query = f'''
                    UPDATE assets 
                    SET {', '.join(set_clauses)}
                    WHERE id = ?
                '''
                
                cursor.execute(update_query, values)
                
                # Mark as synced in AD table
                cursor.execute('''
                    UPDATE ad_computers 
                    SET assets_table_id = ?, is_synced_to_assets = TRUE, last_sync = ?
                    WHERE id = ?
                ''', (assets_id, datetime.now().isoformat(), ad_comp['id']))
                
                updated_count += 1
                
            else:
                # Create new asset from AD data
                new_asset_data = {
                    'hostname': hostname,
                    'computer_name': hostname,
                    'domain': ad_comp.get('domain_name', ''),
                    'os_name': ad_comp.get('operating_system', ''),
                    'device_type': 'Computer',
                    'data_source': 'Active Directory',
                    'collection_method': 'AD Sync',
                    'created_at': datetime.now().isoformat(),
                    'last_update': datetime.now().isoformat(),
                    'scan_status': 'AD Only',
                    'asset_type': 'Computer'
                }
                
                # Dynamic insert
                columns = list(new_asset_data.keys())
                placeholders = ', '.join(['?' for _ in columns])
                column_names = ', '.join(columns)
                
                insert_query = f'''
                    INSERT INTO assets ({column_names})
                    VALUES ({placeholders})
                '''
                
                cursor.execute(insert_query, list(new_asset_data.values()))
                new_assets_id = cursor.lastrowid
                
                # Mark as synced in AD table
                cursor.execute('''
                    UPDATE ad_computers 
                    SET assets_table_id = ?, is_synced_to_assets = TRUE, last_sync = ?
                    WHERE id = ?
                ''', (new_assets_id, datetime.now().isoformat(), ad_comp['id']))
                
                new_count += 1
            
            synced_count += 1
        
        conn.commit()
        conn.close()
        
        return {
            'synced': synced_count,
            'updated': updated_count,
            'new': new_count
        }
    
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
        
        # By domain
        cursor.execute("""
            SELECT domain_name, COUNT(*) FROM ad_computers 
            WHERE domain_name IS NOT NULL 
            GROUP BY domain_name
        """)
        stats['by_domain'] = dict(cursor.fetchall())
        
        # Sync status
        cursor.execute("SELECT is_synced_to_assets, COUNT(*) FROM ad_computers GROUP BY is_synced_to_assets")
        sync_results = cursor.fetchall()
        stats['sync_status'] = {'synced': 0, 'not_synced': 0}
        for synced, count in sync_results:
            if synced:
                stats['sync_status']['synced'] = count
            else:
                stats['sync_status']['not_synced'] = count
        
        conn.close()
        return stats


def integrate_with_ad_fetcher():
    """Integration function for your existing ad_fetcher.py"""
    
    # Initialize AD database
    ad_db = ADDatabase()
    
    print("🏢 AD DATABASE INTEGRATION")
    print("=" * 50)
    print("✅ AD computers table ready with isolated columns")
    
    # Show current stats
    stats = ad_db.get_ad_statistics()
    print(f"📊 Current AD computers: {stats['total_computers']}")
    print(f"📊 Synced to assets: {stats['sync_status']['synced']}")
    print(f"📊 Not synced: {stats['sync_status']['not_synced']}")
    
    return ad_db


if __name__ == "__main__":
    integrate_with_ad_fetcher()