#!/usr/bin/env python3
"""
Database Optimization & Duplicate Cleanup Tool
Addresses the 198.3s save performance issue and removes duplicates
"""

import sqlite3

def get_database_structure():
    """Get all columns in the assets table"""
    conn = sqlite3.connect('assets.db')
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(assets)")
    columns = cursor.fetchall()
    
    print(f"📋 DATABASE STRUCTURE ({len(columns)} columns):")
    for col in columns[:20]:  # Show first 20 columns
        col_id, name, type_info, not_null, default, pk = col
        print(f"   {name} ({type_info})")
    
    if len(columns) > 20:
        print(f"   ... and {len(columns) - 20} more columns")
    
    conn.close()
    return [col[1] for col in columns]

def analyze_duplicates():
    """Analyze duplicate records"""
    conn = sqlite3.connect('assets.db')
    cursor = conn.cursor()
    
    print("\n🔍 DUPLICATE ANALYSIS:")
    
    # Find duplicates by IP
    cursor.execute("""
        SELECT ip_address, COUNT(*) as count, 
               GROUP_CONCAT(id) as record_ids,
               GROUP_CONCAT(created_at) as timestamps
        FROM assets 
        GROUP BY ip_address 
        HAVING COUNT(*) > 1
        ORDER BY count DESC
    """)
    
    duplicates = cursor.fetchall()
    
    if duplicates:
        print(f"   Found {len(duplicates)} IPs with duplicates:")
        total_duplicate_records = 0
        
        for ip, count, ids, timestamps in duplicates[:10]:  # Show top 10
            total_duplicate_records += count - 1  # Subtract 1 to keep one record
            print(f"   {ip}: {count} records (IDs: {ids[:50]}...)")
        
        print(f"\n   Total duplicate records to remove: {total_duplicate_records}")
        
        if len(duplicates) > 10:
            print(f"   ... and {len(duplicates) - 10} more duplicate groups")
    else:
        print("   No duplicates found!")
    
    conn.close()
    return duplicates

def clean_duplicates(dry_run=True):
    """Remove duplicate records, keeping the most recent one"""
    conn = sqlite3.connect('assets.db')
    cursor = conn.cursor()
    
    print(f"\n🧹 DUPLICATE CLEANUP ({'DRY RUN' if dry_run else 'LIVE RUN'}):")
    
    # Find duplicates and keep only the most recent
    cursor.execute("""
        SELECT ip_address, MAX(created_at) as latest_timestamp
        FROM assets 
        GROUP BY ip_address 
        HAVING COUNT(*) > 1
    """)
    
    duplicate_ips = cursor.fetchall()
    removed_count = 0
    
    for ip, latest_timestamp in duplicate_ips:
        # Get all records for this IP except the latest one
        cursor.execute("""
            SELECT id FROM assets 
            WHERE ip_address = ? AND created_at != ?
        """, (ip, latest_timestamp))
        
        old_records = cursor.fetchall()
        
        for (record_id,) in old_records:
            if not dry_run:
                cursor.execute("DELETE FROM assets WHERE id = ?", (record_id,))
            removed_count += 1
            print(f"   {'Would remove' if dry_run else 'Removed'} record ID {record_id} for IP {ip}")
    
    if not dry_run:
        conn.commit()
        print(f"\n✅ Removed {removed_count} duplicate records")
    else:
        print(f"\n📊 Would remove {removed_count} duplicate records")
    
    conn.close()
    return removed_count

def optimize_database():
    """Optimize database for better performance"""
    conn = sqlite3.connect('assets.db')
    cursor = conn.cursor()
    
    print("\n⚡ DATABASE OPTIMIZATION:")
    
    # Create indexes for faster queries
    indexes = [
        ("idx_ip_address", "CREATE INDEX IF NOT EXISTS idx_ip_address ON assets(ip_address)"),
        ("idx_hostname", "CREATE INDEX IF NOT EXISTS idx_hostname ON assets(hostname)"),
        ("idx_created_at", "CREATE INDEX IF NOT EXISTS idx_created_at ON assets(created_at)"),
        ("idx_data_source", "CREATE INDEX IF NOT EXISTS idx_data_source ON assets(data_source)"),
    ]
    
    for index_name, query in indexes:
        try:
            cursor.execute(query)
            print(f"   ✅ Created index: {index_name}")
        except Exception as e:
            print(f"   ⚠️  Index {index_name}: {e}")
    
    # Vacuum database to reclaim space and optimize
    print("   🔧 Running VACUUM to optimize database...")
    cursor.execute("VACUUM")
    
    # Analyze tables for query optimization
    print("   📊 Running ANALYZE for query optimization...")
    cursor.execute("ANALYZE")
    
    conn.commit()
    conn.close()
    
    print("   ✅ Database optimization complete!")

def show_collection_progress():
    """Show progress of enhanced collection features"""
    conn = sqlite3.connect('assets.db')
    cursor = conn.cursor()
    
    print("\n📈 ENHANCED COLLECTION PROGRESS:")
    
    # Check for enhanced fields
    enhanced_checks = [
        ("Graphics Cards", "SELECT COUNT(*) FROM assets WHERE gpu_name IS NOT NULL AND gpu_name != ''"),
        ("Processor Info", "SELECT COUNT(*) FROM assets WHERE processor_name IS NOT NULL AND processor_name != ''"),
        ("OS Version", "SELECT COUNT(*) FROM assets WHERE os_version IS NOT NULL AND os_version != ''"),
        ("Memory Info", "SELECT COUNT(*) FROM assets WHERE total_memory_gb IS NOT NULL"),
        ("Disk Info", "SELECT COUNT(*) FROM assets WHERE disk_space_gb IS NOT NULL"),
    ]
    
    cursor.execute("SELECT COUNT(*) FROM assets")
    total_records = cursor.fetchone()[0]
    
    for feature, query in enhanced_checks:
        try:
            cursor.execute(query)
            count = cursor.fetchone()[0]
            percentage = (count / total_records * 100) if total_records > 0 else 0
            print(f"   {feature}: {count}/{total_records} ({percentage:.1f}%)")
        except Exception as e:
            print(f"   {feature}: Column not found - {e}")
    
    conn.close()

def main():
    print("🚀 DATABASE OPTIMIZATION & CLEANUP TOOL")
    print("=" * 50)
    
    # 1. Show database structure
    columns = get_database_structure()
    
    # 2. Analyze duplicates
    duplicates = analyze_duplicates()
    
    # 3. Show collection progress
    show_collection_progress()
    
    # 4. Dry run cleanup
    if duplicates:
        print("\n" + "=" * 50)
        print("CLEANUP PREVIEW (Dry Run)")
        clean_duplicates(dry_run=True)
        
        print("\n" + "=" * 50)
        response = input("Do you want to proceed with duplicate removal? (y/N): ")
        
        if response.lower() == 'y':
            # 5. Actual cleanup
            clean_duplicates(dry_run=False)
            
            # 6. Optimize database
            optimize_database()
            
            print("\n✅ DATABASE OPTIMIZATION COMPLETE!")
            print("📊 This should significantly improve the 198.3s save time!")
        else:
            print("⏸️  Cleanup cancelled. Database unchanged.")
    else:
        # Still optimize even without duplicates
        optimize_database()
        print("\n✅ DATABASE OPTIMIZATION COMPLETE!")

if __name__ == "__main__":
    main()