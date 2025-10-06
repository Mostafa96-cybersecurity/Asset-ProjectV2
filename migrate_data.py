"""
MIGRATE EXISTING DATA TO COMPREHENSIVE DATABASE
This script migrates the 510 existing assets to the new comprehensive schema
"""

import sqlite3
from datetime import datetime

def migrate_existing_data():
    print("🔄 MIGRATING EXISTING DATA TO COMPREHENSIVE DATABASE")
    print("=" * 60)
    
    # Connect to old database (backup with data)
    old_conn = sqlite3.connect('assets.db.backup_20251005_174844')
    old_cursor = old_conn.cursor()
    
    # Get existing data
    old_cursor.execute("PRAGMA table_info(assets_enhanced)")
    old_columns = [col[1] for col in old_cursor.fetchall()]
    print(f"📊 Old database: {len(old_columns)} columns")
    
    old_cursor.execute("SELECT * FROM assets_enhanced")
    old_data = old_cursor.fetchall()
    print(f"💾 Found {len(old_data)} existing assets to migrate")
    
    # Connect to new database
    new_conn = sqlite3.connect('assets.db')
    new_cursor = new_conn.cursor()
    
    # Get new schema
    new_cursor.execute("PRAGMA table_info(assets_enhanced)")
    new_columns = [col[1] for col in new_cursor.fetchall()]
    print(f"🆕 New database: {len(new_columns)} columns")
    
    # Create column mapping
    column_mapping = {}
    for i, old_col in enumerate(old_columns):
        if old_col in new_columns:
            column_mapping[i] = new_columns.index(old_col)
    
    print(f"🔗 Mapped {len(column_mapping)} columns for migration")
    
    # Migrate data
    migrated_count = 0
    now = datetime.now().isoformat()
    
    for asset_data in old_data:
        # Create new asset record with all None values
        new_asset_data = [None] * len(new_columns)
        
        # Map existing data
        for old_index, new_index in column_mapping.items():
            new_asset_data[new_index] = asset_data[old_index]
        
        # Set timestamps
        if 'updated_at' in new_columns:
            new_asset_data[new_columns.index('updated_at')] = now
        
        # Insert into new database
        placeholders = ', '.join(['?' for _ in new_columns])
        insert_sql = f"INSERT INTO assets_enhanced VALUES ({placeholders})"
        new_cursor.execute(insert_sql, new_asset_data)
        migrated_count += 1
    
    new_conn.commit()
    print(f"✅ Successfully migrated {migrated_count} assets")
    
    # Verify migration
    new_cursor.execute("SELECT COUNT(*) FROM assets_enhanced")
    final_count = new_cursor.fetchone()[0]
    print(f"🎯 Final asset count: {final_count}")
    
    # Show sample migrated data
    new_cursor.execute("SELECT hostname, device_type, ip_address, collection_timestamp FROM assets_enhanced LIMIT 5")
    sample_data = new_cursor.fetchall()
    
    print("\n📋 Sample migrated assets:")
    for asset in sample_data:
        hostname, device_type, ip_address, timestamp = asset
        print(f"   🖥️  {hostname or 'Unknown'} | {device_type or 'Unknown Type'} | {ip_address or 'No IP'} | {timestamp or 'No timestamp'}")
    
    old_conn.close()
    new_conn.close()
    
    print("\n🎉 DATA MIGRATION COMPLETE!")
    print(f"   ✅ {final_count} assets now in comprehensive database")
    print("   ✅ 520 columns available for each asset")
    
    return final_count

if __name__ == "__main__":
    migrate_existing_data()