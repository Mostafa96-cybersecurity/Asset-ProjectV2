#!/usr/bin/env python3
"""
Database Cleanup Tool
Removes duplicate records while preserving the most complete data
"""

import sqlite3
from datetime import datetime

def cleanup_duplicate_records():
    """Clean up duplicate records in the database"""
    print("🧹 DATABASE CLEANUP - REMOVING DUPLICATES")
    print("=" * 50)
    
    conn = sqlite3.connect('assets.db')
    cursor = conn.cursor()
    
    # Get initial count
    cursor.execute("SELECT COUNT(*) FROM assets")
    initial_count = cursor.fetchone()[0]
    print(f"📊 Initial record count: {initial_count}")
    
    cleanup_stats = {
        'ip_duplicates_removed': 0,
        'hostname_duplicates_removed': 0,
        'total_removed': 0
    }
    
    # Clean up IP duplicates
    print("\n🌐 Cleaning IP duplicates...")
    cursor.execute("""
        SELECT ip_address, COUNT(*) as count, GROUP_CONCAT(id) as ids
        FROM assets 
        WHERE ip_address IS NOT NULL 
        GROUP BY ip_address 
        HAVING COUNT(*) > 1
    """)
    
    ip_duplicates = cursor.fetchall()
    
    for ip_address, count, ids_str in ip_duplicates:
        ids = [int(id_str) for id_str in ids_str.split(',')]
        
        # Get all records for this IP
        cursor.execute(f"SELECT * FROM assets WHERE id IN ({','.join(['?' for _ in ids])})", ids)
        records = cursor.fetchall()
        
        # Get column names
        cursor.execute("PRAGMA table_info(assets)")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Find the most complete record
        best_record = None
        best_score = -1
        
        for record in records:
            record_dict = dict(zip(columns, record))
            completeness_score = sum(1 for field, value in record_dict.items() 
                                   if value and value not in ['', 'Unknown', 'Unknown Device'])
            
            if completeness_score > best_score:
                best_score = completeness_score
                best_record = record_dict
        
        # Delete all records except the best one
        ids_to_delete = [record_dict['id'] for record_dict in 
                        [dict(zip(columns, record)) for record in records]
                        if record_dict['id'] != best_record['id']]
        
        if ids_to_delete:
            cursor.execute(f"DELETE FROM assets WHERE id IN ({','.join(['?' for _ in ids_to_delete])})", ids_to_delete)
            cleanup_stats['ip_duplicates_removed'] += len(ids_to_delete)
            print(f"   🗑️ Removed {len(ids_to_delete)} duplicates for IP {ip_address}")
    
    # Clean up hostname duplicates (only if they don't share the same IP)
    print("\n🏷️ Cleaning hostname duplicates...")
    cursor.execute("""
        SELECT hostname, COUNT(*) as count, GROUP_CONCAT(id) as ids
        FROM assets 
        WHERE hostname IS NOT NULL 
        GROUP BY hostname 
        HAVING COUNT(*) > 1
    """)
    
    hostname_duplicates = cursor.fetchall()
    
    for hostname, count, ids_str in hostname_duplicates:
        ids = [int(id_str) for id_str in ids_str.split(',')]
        
        # Get all records for this hostname
        cursor.execute(f"SELECT * FROM assets WHERE id IN ({','.join(['?' for _ in ids])})", ids)
        records = cursor.fetchall()
        
        # Check if they have different IPs
        record_dicts = [dict(zip(columns, record)) for record in records]
        unique_ips = set(record['ip_address'] for record in record_dicts if record['ip_address'])
        
        if len(unique_ips) <= 1:  # Same IP or no IP - these are true duplicates
            # Find the most complete record
            best_record = None
            best_score = -1
            
            for record_dict in record_dicts:
                completeness_score = sum(1 for field, value in record_dict.items() 
                                       if value and value not in ['', 'Unknown', 'Unknown Device'])
                
                if completeness_score > best_score:
                    best_score = completeness_score
                    best_record = record_dict
            
            # Delete all records except the best one
            ids_to_delete = [record_dict['id'] for record_dict in record_dicts
                            if record_dict['id'] != best_record['id']]
            
            if ids_to_delete:
                cursor.execute(f"DELETE FROM assets WHERE id IN ({','.join(['?' for _ in ids_to_delete])})", ids_to_delete)
                cleanup_stats['hostname_duplicates_removed'] += len(ids_to_delete)
                print(f"   🗑️ Removed {len(ids_to_delete)} duplicates for hostname {hostname}")
    
    # Commit changes
    conn.commit()
    
    # Get final count
    cursor.execute("SELECT COUNT(*) FROM assets")
    final_count = cursor.fetchone()[0]
    
    cleanup_stats['total_removed'] = initial_count - final_count
    
    conn.close()
    
    print("\n📊 CLEANUP RESULTS:")
    print(f"   📉 Initial count: {initial_count}")
    print(f"   📈 Final count: {final_count}")
    print(f"   🗑️ Total removed: {cleanup_stats['total_removed']}")
    print(f"   🌐 IP duplicates removed: {cleanup_stats['ip_duplicates_removed']}")
    print(f"   🏷️ Hostname duplicates removed: {cleanup_stats['hostname_duplicates_removed']}")
    
    return cleanup_stats

if __name__ == "__main__":
    print("🧹 DUPLICATE RECORD CLEANUP")
    print("=" * 50)
    print(f"🕐 Started: {datetime.now()}")
    print()
    
    cleanup_stats = cleanup_duplicate_records()
    
    print("\n✅ Cleanup completed successfully!")
    print(f"🕐 Finished: {datetime.now()}")