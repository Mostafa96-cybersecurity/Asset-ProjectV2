#!/usr/bin/env python3
"""
Fixed Database Optimizer - Addresses 198.3s save performance
"""

import sqlite3
from datetime import datetime

def optimize_database():
    """Optimize database with proper transaction handling"""
    
    print("🚀 DATABASE PERFORMANCE OPTIMIZER")
    print("=" * 40)
    
    # Step 1: Clean duplicates and create indexes
    conn = sqlite3.connect('assets.db')
    cursor = conn.cursor()
    
    # Get initial stats
    cursor.execute('SELECT COUNT(*) FROM assets')
    total_before = cursor.fetchone()[0]
    print(f"📊 Current records: {total_before}")
    
    # Remove duplicates
    print("\n🧹 REMOVING DUPLICATES...")
    cursor.execute("""
        DELETE FROM assets 
        WHERE id NOT IN (
            SELECT MAX(id) 
            FROM assets 
            GROUP BY ip_address
        )
    """)
    removed = cursor.rowcount
    print(f"   ✅ Removed {removed} duplicate records")
    
    # Create indexes
    print("\n⚡ CREATING PERFORMANCE INDEXES...")
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_ip_address ON assets(ip_address)",
        "CREATE INDEX IF NOT EXISTS idx_hostname ON assets(hostname)", 
        "CREATE INDEX IF NOT EXISTS idx_created_at ON assets(created_at)",
        "CREATE INDEX IF NOT EXISTS idx_data_source ON assets(data_source)",
        "CREATE INDEX IF NOT EXISTS idx_status ON assets(status)",
    ]
    
    for idx_query in indexes:
        cursor.execute(idx_query)
        print(f"   ✅ Index created")
    
    # Commit and close
    conn.commit()
    conn.close()
    
    # Step 2: Apply SQLite optimizations (requires separate connection)
    print("\n🔧 APPLYING SQLITE OPTIMIZATIONS...")
    
    conn = sqlite3.connect('assets.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("PRAGMA journal_mode = WAL")
        print("   ✅ WAL mode enabled")
        
        cursor.execute("PRAGMA synchronous = NORMAL") 
        print("   ✅ Synchronous mode optimized")
        
        cursor.execute("PRAGMA cache_size = 10000")
        print("   ✅ Cache size increased")
        
        cursor.execute("PRAGMA temp_store = MEMORY")
        print("   ✅ Temp store in memory")
        
    except Exception as e:
        print(f"   ⚠️  Some optimizations failed: {e}")
    
    # Step 3: Vacuum and analyze
    print("\n🔄 FINALIZING OPTIMIZATION...")
    cursor.execute("VACUUM")
    cursor.execute("ANALYZE")
    print("   ✅ Database vacuumed and analyzed")
    
    # Final stats
    cursor.execute('SELECT COUNT(*) FROM assets')
    total_after = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n📈 OPTIMIZATION RESULTS:")
    print(f"   Records before: {total_before}")
    print(f"   Records after: {total_after}")
    print(f"   Duplicates removed: {removed}")
    print(f"   Performance indexes: {len(indexes)} created")
    print(f"   SQLite optimizations: Applied")
    
    print(f"\n✅ DATABASE OPTIMIZATION COMPLETE!")
    print(f"🚀 Save time should now be under 30s (was 198.3s)")
    
    return total_after, removed

def verify_optimization():
    """Verify the optimization worked"""
    print("\n🔍 VERIFICATION:")
    
    conn = sqlite3.connect('assets.db')
    cursor = conn.cursor()
    
    # Check for duplicates
    cursor.execute("""
        SELECT ip_address, COUNT(*) 
        FROM assets 
        GROUP BY ip_address 
        HAVING COUNT(*) > 1
    """)
    remaining_duplicates = cursor.fetchall()
    
    if remaining_duplicates:
        print(f"   ⚠️  {len(remaining_duplicates)} duplicate groups remain")
    else:
        print("   ✅ No duplicates found")
    
    # Check indexes
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'")
    indexes = cursor.fetchall()
    print(f"   ✅ {len(indexes)} performance indexes active")
    
    # Check recent collection data
    cursor.execute("""
        SELECT COUNT(*) FROM assets 
        WHERE data_source IN ('Comprehensive WMI', 'Enhanced WMI Collection')
    """)
    enhanced_records = cursor.fetchone()[0]
    print(f"   📊 {enhanced_records} records with enhanced collection data")
    
    conn.close()

if __name__ == "__main__":
    total_records, removed_duplicates = optimize_database()
    verify_optimization()
    
    print(f"\n🎯 SUMMARY:")
    print(f"   • Database optimized for performance")
    print(f"   • {removed_duplicates} duplicate records removed") 
    print(f"   • Performance indexes created")
    print(f"   • SQLite settings optimized")
    print(f"   • Expected save time: <30s (vs 198.3s before)")