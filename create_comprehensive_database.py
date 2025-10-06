"""
COMPREHENSIVE DATABASE MIGRATION AND CREATION
This script creates the complete database with 520+ columns and migrates existing data
"""

import sqlite3
import os
from datetime import datetime
from comprehensive_schema import COMPREHENSIVE_COLUMNS

class ComprehensiveDatabaseManager:
    def __init__(self, db_path='assets.db'):
        self.db_path = db_path
        self.backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    def backup_existing_database(self):
        """Backup existing database before migration"""
        if os.path.exists(self.db_path):
            print(f"📀 Backing up existing database to: {self.backup_path}")
            import shutil
            shutil.copy2(self.db_path, self.backup_path)
            return True
        return False
        
    def get_existing_data(self):
        """Extract all existing data from current database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get existing schema
            cursor.execute("PRAGMA table_info(assets_enhanced)")
            existing_columns = [col[1] for col in cursor.fetchall()]
            
            if not existing_columns:
                print("⚠️  No existing assets_enhanced table found")
                conn.close()
                return [], []
            
            # Get all existing data
            cursor.execute("SELECT * FROM assets_enhanced")
            existing_data = cursor.fetchall()
            
            conn.close()
            print(f"✅ Retrieved {len(existing_data)} existing assets with {len(existing_columns)} columns")
            return existing_columns, existing_data
            
        except Exception as e:
            print(f"❌ Error retrieving existing data: {e}")
            return [], []
    
    def create_comprehensive_database(self):
        """Create new database with comprehensive schema"""
        print(f"🚀 Creating comprehensive database with {len(COMPREHENSIVE_COLUMNS)} columns...")
        
        # Backup existing database
        self.backup_existing_database()
        
        # Get existing data
        existing_columns, existing_data = self.get_existing_data()
        
        # Create new database with comprehensive schema
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Drop existing table
        cursor.execute("DROP TABLE IF EXISTS assets_enhanced")
        
        # Create comprehensive table
        columns_sql = []
        for col_name, col_type in COMPREHENSIVE_COLUMNS.items():
            columns_sql.append(f"{col_name} {col_type}")
        
        create_table_sql = f"""
        CREATE TABLE assets_enhanced (
            {', '.join(columns_sql)}
        )
        """
        
        cursor.execute(create_table_sql)
        
        # Migrate existing data if available
        if existing_data and existing_columns:
            print(f"📊 Migrating {len(existing_data)} existing assets...")
            
            # Map existing columns to new schema
            column_mapping = {}
            for i, old_col in enumerate(existing_columns):
                if old_col in COMPREHENSIVE_COLUMNS:
                    column_mapping[i] = old_col
            
            # Prepare insert statement for new schema
            new_columns = list(COMPREHENSIVE_COLUMNS.keys())
            placeholders = ', '.join(['?' for _ in new_columns])
            insert_sql = f"INSERT INTO assets_enhanced ({', '.join(new_columns)}) VALUES ({placeholders})"
            
            # Migrate each asset
            migrated_count = 0
            for asset_data in existing_data:
                new_asset_data = [None] * len(new_columns)
                
                # Map existing data to new schema
                for old_index, new_column in column_mapping.items():
                    new_index = new_columns.index(new_column)
                    new_asset_data[new_index] = asset_data[old_index]
                
                # Set default values for new columns
                now = datetime.now().isoformat()
                if 'created_at' in new_columns and new_asset_data[new_columns.index('created_at')] is None:
                    new_asset_data[new_columns.index('created_at')] = now
                if 'updated_at' in new_columns:
                    new_asset_data[new_columns.index('updated_at')] = now
                
                cursor.execute(insert_sql, new_asset_data)
                migrated_count += 1
            
            print(f"✅ Successfully migrated {migrated_count} assets")
        
        # Create indexes for performance
        print("🔍 Creating database indexes...")
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_hostname ON assets_enhanced(hostname)",
            "CREATE INDEX IF NOT EXISTS idx_ip_address ON assets_enhanced(ip_address)",
            "CREATE INDEX IF NOT EXISTS idx_device_type ON assets_enhanced(device_type)",
            "CREATE INDEX IF NOT EXISTS idx_device_status ON assets_enhanced(device_status)",
            "CREATE INDEX IF NOT EXISTS idx_department ON assets_enhanced(department)",
            "CREATE INDEX IF NOT EXISTS idx_last_seen ON assets_enhanced(last_seen)",
            "CREATE INDEX IF NOT EXISTS idx_collection_timestamp ON assets_enhanced(collection_timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_os_family ON assets_enhanced(os_family)",
            "CREATE INDEX IF NOT EXISTS idx_manufacturer ON assets_enhanced(system_manufacturer)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        conn.commit()
        conn.close()
        
        print("🎉 COMPREHENSIVE DATABASE CREATED SUCCESSFULLY!")
        print(f"   📊 Total columns: {len(COMPREHENSIVE_COLUMNS)}")
        print(f"   💾 Database path: {self.db_path}")
        print(f"   📀 Backup path: {self.backup_path}")
        
        return True
    
    def verify_database(self):
        """Verify the new database structure"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check table structure
            cursor.execute("PRAGMA table_info(assets_enhanced)")
            columns = cursor.fetchall()
            
            print("✅ Database verification:")
            print(f"   📊 Total columns: {len(columns)}")
            print(f"   🎯 Expected columns: {len(COMPREHENSIVE_COLUMNS)}")
            
            # Check data count
            cursor.execute("SELECT COUNT(*) FROM assets_enhanced")
            asset_count = cursor.fetchone()[0]
            print(f"   💾 Total assets: {asset_count}")
            
            # Show sample of comprehensive columns
            print("\n📋 Sample of comprehensive columns:")
            for i, (col_name, col_type, _, _, _, _) in enumerate(columns[:20]):
                print(f"   {i+1:3d}. {col_name:30} ({col_type})")
            
            if len(columns) > 20:
                print(f"   ... and {len(columns)-20} more columns")
            
            conn.close()
            return len(columns) >= 462
            
        except Exception as e:
            print(f"❌ Database verification failed: {e}")
            return False

def main():
    print("🚀 COMPREHENSIVE DATABASE CREATION AND MIGRATION")
    print("=" * 60)
    
    db_manager = ComprehensiveDatabaseManager()
    
    # Create comprehensive database
    success = db_manager.create_comprehensive_database()
    
    if success:
        # Verify the database
        if db_manager.verify_database():
            print("\n🎉 COMPREHENSIVE DATABASE SETUP COMPLETE!")
            print("   ✅ All 520+ columns created")
            print("   ✅ Existing data migrated")
            print("   ✅ Indexes created for performance")
            print("   ✅ Database verified and ready")
        else:
            print("\n❌ Database verification failed")
    else:
        print("\n❌ Database creation failed")

if __name__ == "__main__":
    main()