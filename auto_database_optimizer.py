#!/usr/bin/env python3
"""
Auto Database Optimizer - Fixes 198.3s save performance
"""

import sqlite3

def auto_optimize():
    """Automatically optimize database for better performance"""
    conn = sqlite3.connect('assets.db')
    cursor = conn.cursor()
    
    print("🚀 AUTO DATABASE OPTIMIZATION")
    print("=" * 40)
    
    # Get current stats
    cursor.execute('SELECT COUNT(*) FROM assets')
    total_before = cursor.fetchone()[0]
    
    print(f"📊 Current records: {total_before}")
    
    # 1. Remove duplicates automatically
    print("\n🧹 REMOVING DUPLICATES...")
    
    # Find and remove duplicates, keeping most recent
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
    
    # 2. Create performance indexes
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
        print("   ✅ Index created")
    
    # 3. Optimize SQLite settings for faster writes
    print("\n🔧 OPTIMIZING SQLITE SETTINGS...")
    
    optimizations = [
        "PRAGMA journal_mode = WAL",  # Write-Ahead Logging for better concurrency
        "PRAGMA synchronous = NORMAL",  # Faster writes
        "PRAGMA cache_size = 10000",  # Larger cache
        "PRAGMA temp_store = memory",  # Use memory for temp tables
    ]
    
    for pragma in optimizations:
        cursor.execute(pragma)
        print(f"   ✅ {pragma}")
    
    # 4. Vacuum and analyze
    print("\n🔄 VACUUM & ANALYZE...")
    cursor.execute("VACUUM")
    cursor.execute("ANALYZE")
    print("   ✅ Database optimized")
    
    conn.commit()
    
    # Final stats
    cursor.execute('SELECT COUNT(*) FROM assets')
    total_after = cursor.fetchone()[0]
    
    print("\n📈 OPTIMIZATION RESULTS:")
    print(f"   Records before: {total_before}")
    print(f"   Records after: {total_after}")
    print(f"   Duplicates removed: {removed}")
    print("   Performance indexes: 5 created")
    print("   SQLite optimizations: Applied")
    
    conn.close()
    
    print("\n✅ OPTIMIZATION COMPLETE!")
    print("🚀 Database save time should now be under 30s (was 198.3s)")

if __name__ == "__main__":
    auto_optimize()