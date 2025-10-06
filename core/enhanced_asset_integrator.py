# -*- coding: utf-8 -*-
"""
Asset Collection Integration with Enhanced WMI and Department Management
-----------------------------------------------------------------------
Integrates enhanced WMI collection and department management with existing system
"""

import sqlite3
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from core.enhanced_wmi_collector import collect_enhanced_wmi_data
from db.connection import connect

log = logging.getLogger(__name__)


class EnhancedAssetIntegrator:
    """Integrates enhanced WMI collection with existing asset management"""
    
    def __init__(self):
        self.init_enhanced_tables()
    
    def init_enhanced_tables(self):
        """Initialize enhanced tables for better data management"""
        try:
            with connect() as conn:
                cursor = conn.cursor()
                
                # Add new columns to assets table if they don't exist
                new_columns = [
                    ('working_user', 'TEXT'),
                    ('domain', 'TEXT'),
                    ('device_infrastructure', 'TEXT'),
                    ('installed_ram_gb', 'REAL'),
                    ('processor', 'TEXT'),
                    ('active_gpu', 'TEXT'),
                    ('connected_screens', 'INTEGER'),
                    ('collection_method', 'TEXT'),
                    ('collection_quality', 'TEXT'),
                    ('quality_score', 'REAL'),
                    ('last_wmi_collection', 'TEXT'),
                    ('mac_address', 'TEXT'),
                    ('total_storage_gb', 'REAL'),
                    ('memory_modules', 'TEXT'),
                    ('network_adapter_count', 'INTEGER'),
                    ('bios_version', 'TEXT'),
                    ('os_architecture', 'TEXT'),
                    ('asset_tag_hw', 'TEXT')
                ]
                
                # Get existing columns
                cursor.execute("PRAGMA table_info(assets)")
                existing_columns = [row[1] for row in cursor.fetchall()]
                
                # Add missing columns
                for column_name, column_type in new_columns:
                    if column_name not in existing_columns:
                        try:
                            cursor.execute(f"ALTER TABLE assets ADD COLUMN {column_name} {column_type}")
                            log.info(f"Added column {column_name} to assets table")
                        except sqlite3.OperationalError as e:
                            if "duplicate column name" not in str(e).lower():
                                log.warning(f"Failed to add column {column_name}: {e}")
                
                conn.commit()
                log.info("Enhanced asset tables initialized successfully")
                
        except Exception as e:
            log.error(f"Error initializing enhanced tables: {e}")
    
    def enhance_asset_collection(self, ip_address: str, username: str = None, 
                                password: str = None, domain: str = None) -> Dict[str, Any]:
        """
        Perform enhanced asset collection using new WMI collector
        
        Returns enhanced asset data with smart OS detection and classification
        """
        log.info(f"Starting enhanced collection for {ip_address}")
        
        try:
            # Use enhanced WMI collector
            enhanced_data = collect_enhanced_wmi_data(ip_address, username, password, domain)
            
            # Map to database fields
            asset_data = self._map_enhanced_data_to_db(enhanced_data)
            
            # Store in database
            asset_id = self._store_enhanced_asset(asset_data)
            
            if asset_id:
                log.info(f"✅ Enhanced collection successful for {enhanced_data['hostname']} (ID: {asset_id})")
                enhanced_data['asset_id'] = asset_id
                return enhanced_data
            else:
                log.error(f"❌ Failed to store enhanced data for {ip_address}")
                return enhanced_data
                
        except Exception as e:
            log.error(f"❌ Enhanced collection failed for {ip_address}: {e}")
            return {
                'hostname': ip_address,
                'ip_address': ip_address,
                'collection_method': f'Enhanced Collection Error: {str(e)[:50]}',
                'collection_quality': 'Failed'
            }
    
    def _map_enhanced_data_to_db(self, enhanced_data: Dict[str, Any]) -> Dict[str, Any]:
        """Map enhanced WMI data to database fields"""
        
        # Core mapping to existing schema
        asset_data = {
            # Standard fields
            'hostname': enhanced_data.get('hostname', 'Unknown'),
            'ip_address': enhanced_data.get('lan_ip_address', enhanced_data.get('hostname', 'Unknown')),
            'device_type': enhanced_data.get('device_type', 'Unknown'),
            'model_vendor': f"{enhanced_data.get('manufacturer', 'Unknown')} {enhanced_data.get('device_model', 'Unknown')}".strip(),
            'serial_number': enhanced_data.get('serial_number', 'Unknown'),
            'firmware_os_version': enhanced_data.get('os_name', 'Unknown'),
            'status': 'Active',
            'data_source': 'Enhanced WMI Collection',
            'updated_at': datetime.now().isoformat(),
            
            # Enhanced fields
            'working_user': enhanced_data.get('working_user', 'N/A'),
            'domain': enhanced_data.get('domain', 'N/A'),
            'device_infrastructure': enhanced_data.get('device_infrastructure', 'Unknown'),
            'installed_ram_gb': enhanced_data.get('installed_ram_gb', 0),
            'processor': enhanced_data.get('processor', 'Unknown'),
            'active_gpu': enhanced_data.get('active_gpu', 'Unknown'),
            'connected_screens': enhanced_data.get('connected_screens', 0),
            'collection_method': enhanced_data.get('collection_method', 'Enhanced WMI'),
            'collection_quality': enhanced_data.get('collection_quality', 'Standard'),
            'quality_score': enhanced_data.get('quality_score', 0),
            'last_wmi_collection': datetime.now().isoformat(),
            
            # Additional hardware details
            'mac_address': enhanced_data.get('mac_address', ''),
            'total_storage_gb': enhanced_data.get('total_storage_gb', 0),
            'memory_modules': enhanced_data.get('memory_modules', ''),
            'network_adapter_count': enhanced_data.get('network_adapter_count', 0),
            'bios_version': enhanced_data.get('bios_version', ''),
            'os_architecture': enhanced_data.get('os_architecture', ''),
            'asset_tag_hw': enhanced_data.get('asset_tag', '')
        }
        
        # Clean up storage field
        if enhanced_data.get('storage'):
            asset_data['location'] = enhanced_data['storage'][:100]  # Truncate if too long
        
        return asset_data
    
    def _store_enhanced_asset(self, asset_data: Dict[str, Any]) -> Optional[int]:
        """Store enhanced asset data in database"""
        try:
            with connect() as conn:
                cursor = conn.cursor()
                
                # Check if asset already exists
                cursor.execute("""
                    SELECT id FROM assets 
                    WHERE hostname = ? OR ip_address = ?
                    ORDER BY updated_at DESC
                    LIMIT 1
                """, (asset_data['hostname'], asset_data['ip_address']))
                
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing asset
                    asset_id = existing[0]
                    
                    # Prepare update query
                    update_fields = []
                    update_values = []
                    
                    for field, value in asset_data.items():
                        if field != 'id':
                            update_fields.append(f"{field} = ?")
                            update_values.append(value)
                    
                    update_values.append(asset_id)
                    
                    cursor.execute(f"""
                        UPDATE assets 
                        SET {', '.join(update_fields)}
                        WHERE id = ?
                    """, update_values)
                    
                    log.info(f"Updated existing asset {asset_data['hostname']} (ID: {asset_id})")
                    
                else:
                    # Insert new asset
                    fields = list(asset_data.keys())
                    placeholders = ', '.join(['?' for _ in fields])
                    values = list(asset_data.values())
                    
                    cursor.execute(f"""
                        INSERT INTO assets ({', '.join(fields)})
                        VALUES ({placeholders})
                    """, values)
                    
                    asset_id = cursor.lastrowid
                    log.info(f"Inserted new asset {asset_data['hostname']} (ID: {asset_id})")
                
                conn.commit()
                return asset_id
                
        except Exception as e:
            log.error(f"Error storing enhanced asset data: {e}")
            return None
    
    def bulk_enhance_existing_assets(self, limit: int = 50) -> Dict[str, int]:
        """
        Enhance existing assets in database with improved WMI collection
        
        Args:
            limit: Maximum number of assets to enhance in one run
            
        Returns:
            Dictionary with enhancement statistics
        """
        
        stats = {
            'total_processed': 0,
            'successful_enhancements': 0,
            'failed_enhancements': 0,
            'skipped_assets': 0
        }
        
        try:
            with connect() as conn:
                cursor = conn.cursor()
                
                # Get assets that need enhancement (missing enhanced data)
                cursor.execute("""
                    SELECT id, hostname, ip_address, device_type
                    FROM assets 
                    WHERE (collection_method IS NULL OR collection_method != 'Enhanced WMI Collection')
                    AND (hostname NOT LIKE '%.%.%.%')  -- Skip IP-only hostnames
                    AND status = 'Active'
                    ORDER BY updated_at DESC
                    LIMIT ?
                """, (limit,))
                
                assets_to_enhance = cursor.fetchall()
                
                log.info(f"Found {len(assets_to_enhance)} assets to enhance")
                
                for asset_id, hostname, ip_address, device_type in assets_to_enhance:
                    stats['total_processed'] += 1
                    
                    try:
                        # Attempt enhanced collection
                        enhanced_data = self.enhance_asset_collection(ip_address)
                        
                        if enhanced_data.get('collection_quality') != 'Failed':
                            stats['successful_enhancements'] += 1
                            log.info(f"✅ Enhanced {hostname} ({ip_address})")
                        else:
                            stats['failed_enhancements'] += 1
                            log.warning(f"⚠️ Enhancement failed for {hostname} ({ip_address})")
                            
                    except Exception as e:
                        stats['failed_enhancements'] += 1
                        log.error(f"❌ Enhancement error for {hostname} ({ip_address}): {e}")
                
                log.info(f"Bulk enhancement completed: {stats}")
                return stats
                
        except Exception as e:
            log.error(f"Error in bulk enhancement: {e}")
            return stats
    
    def get_enhancement_summary(self) -> Dict[str, Any]:
        """Get summary of enhanced assets"""
        try:
            with connect() as conn:
                cursor = conn.cursor()
                
                # Total assets
                cursor.execute("SELECT COUNT(*) FROM assets")
                total_assets = cursor.fetchone()[0]
                
                # Enhanced assets
                cursor.execute("""
                    SELECT COUNT(*) FROM assets 
                    WHERE collection_method = 'Enhanced WMI Collection'
                """)
                enhanced_assets = cursor.fetchone()[0]
                
                # Quality distribution
                cursor.execute("""
                    SELECT collection_quality, COUNT(*) 
                    FROM assets 
                    WHERE collection_quality IS NOT NULL
                    GROUP BY collection_quality
                    ORDER BY COUNT(*) DESC
                """)
                quality_distribution = dict(cursor.fetchall())
                
                # Device type distribution
                cursor.execute("""
                    SELECT device_type, COUNT(*) 
                    FROM assets 
                    WHERE collection_method = 'Enhanced WMI Collection'
                    GROUP BY device_type
                    ORDER BY COUNT(*) DESC
                """)
                device_distribution = dict(cursor.fetchall())
                
                # Assets with real hostnames (not IPs)
                cursor.execute("""
                    SELECT COUNT(*) FROM assets 
                    WHERE hostname NOT LIKE '%.%.%.%' 
                    AND hostname != ip_address
                """)
                real_hostnames = cursor.fetchone()[0]
                
                # Assets with user information
                cursor.execute("""
                    SELECT COUNT(*) FROM assets 
                    WHERE working_user IS NOT NULL 
                    AND working_user != 'N/A'
                """)
                assets_with_users = cursor.fetchone()[0]
                
                return {
                    'total_assets': total_assets,
                    'enhanced_assets': enhanced_assets,
                    'enhancement_percentage': (enhanced_assets / max(total_assets, 1)) * 100,
                    'quality_distribution': quality_distribution,
                    'device_distribution': device_distribution,
                    'real_hostnames': real_hostnames,
                    'assets_with_users': assets_with_users,
                    'real_hostname_percentage': (real_hostnames / max(total_assets, 1)) * 100,
                    'user_info_percentage': (assets_with_users / max(total_assets, 1)) * 100
                }
                
        except Exception as e:
            log.error(f"Error getting enhancement summary: {e}")
            return {}


# Global integrator instance
asset_integrator = EnhancedAssetIntegrator()


def enhance_single_asset(ip_address: str, username: str = None, 
                        password: str = None, domain: str = None) -> Dict[str, Any]:
    """
    Enhance a single asset with comprehensive WMI collection
    
    This is the main function to use for enhanced asset collection
    """
    return asset_integrator.enhance_asset_collection(ip_address, username, password, domain)


def bulk_enhance_assets(limit: int = 50) -> Dict[str, int]:
    """
    Enhance multiple existing assets in the database
    
    Args:
        limit: Maximum number of assets to enhance
        
    Returns:
        Enhancement statistics
    """
    return asset_integrator.bulk_enhance_existing_assets(limit)


def get_system_enhancement_status() -> Dict[str, Any]:
    """Get comprehensive enhancement status"""
    return asset_integrator.get_enhancement_summary()


def test_enhanced_integration():
    """Test the enhanced integration"""
    print("🔧 Testing Enhanced Asset Integration...")
    
    # Test local machine enhancement
    result = enhance_single_asset('127.0.0.1')
    
    print("\n📊 Enhancement Results:")
    print(f"🖥️  Hostname: {result.get('hostname', 'N/A')}")
    print(f"👤 Working User: {result.get('working_user', 'N/A')}")
    print(f"🔧 Device Type: {result.get('device_type', 'N/A')}")
    print(f"🏗️  Infrastructure: {result.get('device_infrastructure', 'N/A')}")
    print(f"📊 Quality: {result.get('collection_quality', 'N/A')}")
    print(f"🔧 Method: {result.get('collection_method', 'N/A')}")
    
    # Get system status
    status = get_system_enhancement_status()
    print("\n📈 System Enhancement Status:")
    print(f"Total Assets: {status.get('total_assets', 0)}")
    print(f"Enhanced Assets: {status.get('enhanced_assets', 0)} ({status.get('enhancement_percentage', 0):.1f}%)")
    print(f"Real Hostnames: {status.get('real_hostnames', 0)} ({status.get('real_hostname_percentage', 0):.1f}%)")
    print(f"Assets with Users: {status.get('assets_with_users', 0)} ({status.get('user_info_percentage', 0):.1f}%)")


if __name__ == "__main__":
    test_enhanced_integration()