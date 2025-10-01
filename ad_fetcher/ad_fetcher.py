# -*- coding: utf-8 -*-
"""
Active Directory Fetcher Module - Database Only

This module contains functionality for fetching data from Active Directory.
Database-focused implementation for asset management system.
"""
import ssl
import sys
import os
from datetime import datetime, date, time
from ldap3 import Server, Connection, ALL, Tls
from typing import Optional, Dict, Any, List, Union

# Add current directory to path for AD database integration
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from ad_database_integration import ADDatabase
    AD_DB_AVAILABLE = True
except ImportError:
    AD_DB_AVAILABLE = False
    print("⚠️  AD Database integration not available")

def _to_str(v):
    """Convert value to string safely"""
    try:
        if isinstance(v, (datetime, date, time)):
            return v.isoformat() if hasattr(v, 'isoformat') else str(v)
        return str(v) if v is not None else ""
    except Exception:
        return ""

def ad_fetch_computers(server_host, base_dn, username, password, use_ssl=False, timeout=8, store_in_db=True):
    """
    Enhanced AD computer fetcher with database storage support
    
    Args:
        server_host: AD server hostname/IP
        base_dn: Base Distinguished Name to search
        username: AD username
        password: AD password
        use_ssl: Use SSL connection
        timeout: Connection timeout
        store_in_db: Store results in dedicated AD database table
    
    Returns:
        List of computer items or error dict
    """
    try:
        tls = Tls(validate=ssl.CERT_NONE) if use_ssl else None
        server = Server(server_host, use_ssl=use_ssl, get_info=ALL, tls=tls, connect_timeout=timeout)
        conn = Connection(server, user=username, password=password, auto_bind='AUTO_BIND_NO_TLS')
        
        # Search for computers
        conn.search(
            search_base=base_dn,
            search_filter="(objectClass=computer)",
            attributes=["name","dNSHostName","operatingSystem","operatingSystemVersion","lastLogonTimestamp","whenCreated","distinguishedName","objectGUID","objectSid","userAccountControl","memberOf","managedBy","location","description"]
        )
        
        items = []
        ad_db = None
        
        # Initialize AD database if available and requested
        if store_in_db and AD_DB_AVAILABLE:
            try:
                ad_db = ADDatabase()
                print(f"✅ AD database connection established")
            except Exception as e:
                print(f"⚠️  AD database not available: {e}")
                ad_db = None
        
        # Process each computer entry
        for entry in conn.entries:
            e = entry.entry_attributes_as_dict
            
            def val(k):
                v = e.get(k) if isinstance(e, dict) else None
                if isinstance(v, list): 
                    v = v[0] if v else ""
                return _to_str(v)
            
            # Create computer item
            computer_item = {
                "Hostname": (val("dNSHostName") or val("name") or "").split(".")[0],
                "FQDN": val("dNSHostName"),
                "OS Name and Version": val("operatingSystem") or "",
                "OS Version": val("operatingSystemVersion") or "",
                "AD whenCreated": val("whenCreated"),
                "AD lastLogonTimestamp": val("lastLogonTimestamp"),
                "DN": val("distinguishedName"),
                "objectGUID": val("objectGUID"),
                "objectSid": val("objectSid"),
            }
            
            # Add extended attributes for database storage
            if ad_db:
                # Create extended data dict instead of using update
                extended_data = {
                    "userAccountControl": val("userAccountControl"),
                    "memberOf": str(e.get("memberOf", [])),  # Convert to string for database
                    "managedBy": val("managedBy"),
                    "location": val("location"),
                    "description": val("description"),
                    "enabled": not (int(val("userAccountControl") or "0") & 2)  # Check if account is enabled
                }
                
                # Store in database
                try:
                    computer_id = ad_db.insert_ad_computer_from_fetcher({**computer_item, **extended_data})
                    print(f"   💾 Stored: {computer_item['Hostname']} (ID: {computer_id})")
                except Exception as e:
                    print(f"   ❌ Failed to store {computer_item['Hostname']}: {e}")
            
            items.append(computer_item)
        
        print(f"\n📊 AD Collection Complete: {len(items)} computers found")
        
        if ad_db:
            print(f"   💾 Stored in AD database: {len(items)}")
            
            # Show sync option
            print(f"\n💡 Next steps:")
            print(f"   1. Run ad_db.sync_ad_to_assets_table() to sync with main assets")
            print(f"   2. Check AD statistics with ad_db.get_ad_statistics()")
        
        return items
        
    except Exception as e:
        error_result = {"Error": f"AD error: {e}"}
        print(f"❌ AD Connection Error: {e}")
        return error_result

def sync_ad_to_database():
    """Standalone function to sync AD data to main assets database"""
    if not AD_DB_AVAILABLE:
        print("❌ AD Database integration not available")
        return False
    
    try:
        ad_db = ADDatabase()
        sync_result = ad_db.sync_ad_to_assets_table()
        
        print("🔄 AD DATABASE SYNC COMPLETE")
        print("=" * 40)
        print(f"✅ Total synced: {sync_result['synced']}")
        print(f"🔄 Updated existing: {sync_result['updated']}")
        print(f"➕ New assets created: {sync_result['new']}")
        
        return True
        
    except Exception as e:
        print(f"❌ AD sync error: {e}")
        return False

def get_ad_statistics():
    """Get AD collection and sync statistics"""
    if not AD_DB_AVAILABLE:
        print("❌ AD Database integration not available")
        return None
    
    try:
        ad_db = ADDatabase()
        stats = ad_db.get_ad_statistics()
        
        print("📊 AD DATABASE STATISTICS")
        print("=" * 40)
        print(f"Total AD computers: {stats['total_computers']}")
        print(f"Enabled computers: {stats['enabled_computers']}")
        print(f"Synced to assets: {stats['sync_status']['synced']}")
        print(f"Not synced: {stats['sync_status']['not_synced']}")
        
        if stats['by_domain']:
            print("\nBy Domain:")
            for domain, count in stats['by_domain'].items():
                print(f"  {domain}: {count}")
        
        return stats
        
    except Exception as e:
        print(f"❌ Error getting AD stats: {e}")
        return None

def test_ad_connection(server_host, base_dn, username, password, use_ssl=False):
    """Test AD connection without storing data"""
    print(f"🧪 Testing AD connection to {server_host}...")
    
    try:
        # Test with store_in_db=False to avoid storing test data
        result = ad_fetch_computers(server_host, base_dn, username, password, use_ssl, timeout=10, store_in_db=False)
        
        if isinstance(result, dict) and "Error" in result:
            print(f"❌ Connection failed: {result['Error']}")
            return False
        
        print(f"✅ Connection successful! Found {len(result)} computers")
        
        # Show sample computers
        for i, comp in enumerate(result[:3]):
            print(f"  {i+1}. {comp['Hostname']} ({comp['FQDN']}) - {comp['OS Name and Version']}")
        
        if len(result) > 3:
            print(f"  ... and {len(result)-3} more")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False