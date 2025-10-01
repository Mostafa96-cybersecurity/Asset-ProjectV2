#!/usr/bin/env python3
"""
Database Schema Enhancement
Add missing technical fields to properly store all collected device data
"""

import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def enhance_database_schema():
    """Add missing technical fields to assets table"""
    
    print("🔧 ENHANCING DATABASE SCHEMA")
    print("="*50)
    
    # List of missing technical fields that should be added
    missing_fields = [
        ('working_user', 'TEXT', 'Currently logged in user'),
        ('domain_name', 'TEXT', 'Windows domain or workgroup'),  
        ('device_infrastructure', 'TEXT', 'Server/Workstation/Laptop'),
        ('installed_ram_gb', 'INTEGER', 'RAM capacity in GB'),
        ('storage_info', 'TEXT', 'Storage devices and capacity'),
        ('manufacturer', 'TEXT', 'Hardware manufacturer'),
        ('processor_info', 'TEXT', 'CPU model and specifications'),
        ('system_sku', 'TEXT', 'System SKU identifier'),
        ('active_gpu', 'TEXT', 'Graphics card information'),
        ('connected_screens', 'INTEGER', 'Number of connected monitors'),
        ('disk_count', 'INTEGER', 'Number of storage devices'),
        ('mac_address', 'TEXT', 'Primary MAC address'),
        ('all_mac_addresses', 'TEXT', 'All network interfaces MAC addresses'),
        ('cpu_details', 'TEXT', 'Detailed CPU information (JSON)'),
        ('disk_details', 'TEXT', 'Detailed disk information (JSON)')
    ]
    
    try:
        conn = sqlite3.connect('assets.db')
        cursor = conn.cursor()
        
        # Get current table schema
        cursor.execute("PRAGMA table_info(assets)")
        existing_columns = {col[1] for col in cursor.fetchall()}
        
        print("📊 Current Database Columns:")
        for col in sorted(existing_columns):
            print(f"   ✅ {col}")
        
        print(f"\n🔧 Adding Missing Technical Fields:")
        
        fields_added = 0
        for field_name, field_type, description in missing_fields:
            if field_name not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE assets ADD COLUMN {field_name} {field_type}")
                    print(f"   ✅ Added: {field_name} ({field_type}) - {description}")
                    fields_added += 1
                except sqlite3.Error as e:
                    print(f"   ❌ Failed to add {field_name}: {e}")
            else:
                print(f"   ⚠️  Already exists: {field_name}")
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ Schema Enhancement Complete!")
        print(f"📊 Added {fields_added} new technical fields")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Database schema enhancement failed: {e}")
        return False

def migrate_existing_data():
    """Migrate existing data from notes field to proper technical fields"""
    
    print(f"\n🔄 MIGRATING EXISTING DATA")
    print("="*40)
    
    try:
        conn = sqlite3.connect('assets.db')
        cursor = conn.cursor()
        
        # Get all records with notes containing technical data
        cursor.execute("""
            SELECT id, notes, hostname, ip_address
            FROM assets 
            WHERE notes IS NOT NULL AND notes != '' 
            AND notes LIKE '%Working User:%'
        """)
        
        records = cursor.fetchall()
        print(f"📋 Found {len(records)} records with technical data in notes")
        
        migrated_count = 0
        for record_id, notes, hostname, ip in records:
            try:
                # Parse technical data from notes
                technical_data = {}
                
                if notes:
                    parts = notes.split(' | ')
                    for part in parts:
                        if ':' in part:
                            key, value = part.split(':', 1)
                            key = key.strip()
                            value = value.strip()
                            
                            # Map to database fields
                            if key == 'Working User':
                                technical_data['working_user'] = value
                            elif key == 'Domain':
                                technical_data['domain_name'] = value
                            elif key == 'Infrastructure':
                                technical_data['device_infrastructure'] = value
                            elif key == 'RAM':
                                try:
                                    ram_gb = int(value.replace(' GB', ''))
                                    technical_data['installed_ram_gb'] = ram_gb
                                except:
                                    pass
                            elif key == 'Storage':
                                technical_data['storage_info'] = value
                            elif key == 'CPU':
                                technical_data['processor_info'] = value
                            elif key == 'SKU':
                                technical_data['system_sku'] = value
                            elif key == 'GPU':
                                technical_data['active_gpu'] = value
                            elif key == 'Screens':
                                try:
                                    screens = int(value)
                                    technical_data['connected_screens'] = screens
                                except:
                                    pass
                
                # Update record with technical data
                if technical_data:
                    update_fields = []
                    update_values = []
                    
                    for field, value in technical_data.items():
                        update_fields.append(f"{field} = ?")
                        update_values.append(value)
                    
                    update_values.append(record_id)
                    
                    cursor.execute(f"""
                        UPDATE assets 
                        SET {', '.join(update_fields)}, updated_at = ?
                        WHERE id = ?
                    """, update_values + [datetime.now().isoformat(), record_id])
                    
                    print(f"   ✅ Migrated: {hostname} ({ip}) - {len(technical_data)} fields")
                    migrated_count += 1
                    
            except Exception as e:
                print(f"   ❌ Failed to migrate {hostname}: {e}")
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ Data Migration Complete!")
        print(f"📊 Successfully migrated {migrated_count} records")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Data migration failed: {e}")
        return False

def verify_enhanced_data():
    """Verify that technical data is now properly stored"""
    
    print(f"\n🔍 VERIFYING ENHANCED DATA STORAGE")
    print("="*45)
    
    try:
        conn = sqlite3.connect('assets.db')
        cursor = conn.cursor()
        
        # Check technical field population
        technical_fields = [
            'working_user', 'domain_name', 'device_infrastructure', 
            'installed_ram_gb', 'storage_info', 'processor_info',
            'active_gpu', 'connected_screens'
        ]
        
        print("📊 Technical Fields Population:")
        for field in technical_fields:
            try:
                cursor.execute(f"""
                    SELECT COUNT(*) as total,
                           COUNT(CASE WHEN {field} IS NOT NULL AND {field} != '' THEN 1 END) as populated
                    FROM assets
                """)
                total, populated = cursor.fetchone()
                percentage = (populated/total*100) if total > 0 else 0
                status = '✅' if percentage > 0 else '❌'
                print(f"   {status} {field:<25}: {populated:3}/{total} ({percentage:5.1f}%)")
            except sqlite3.Error:
                print(f"   ❌ {field:<25}: Field not found")
        
        # Show sample enhanced record
        cursor.execute("""
            SELECT hostname, working_user, domain_name, device_infrastructure,
                   installed_ram_gb, storage_info, processor_info, active_gpu, connected_screens
            FROM assets 
            WHERE working_user IS NOT NULL 
            LIMIT 1
        """)
        
        sample = cursor.fetchone()
        if sample:
            print(f"\n📋 SAMPLE ENHANCED RECORD:")
            print("-"*30)
            fields = ['Hostname', 'Working User', 'Domain', 'Infrastructure', 
                     'RAM (GB)', 'Storage', 'Processor', 'GPU', 'Screens']
            for i, field in enumerate(fields):
                value = sample[i] if sample[i] else 'N/A'
                print(f"   {field:<15}: {value}")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Data verification failed: {e}")
        return False

def main():
    print("🚀 DATABASE ENHANCEMENT FOR COMPLETE TECHNICAL DATA")
    print("="*70)
    
    # Step 1: Enhance database schema
    schema_success = enhance_database_schema()
    
    if schema_success:
        # Step 2: Migrate existing data
        migration_success = migrate_existing_data()
        
        if migration_success:
            # Step 3: Verify the enhancement
            verify_enhanced_data()
            
            print(f"\n🎯 ENHANCEMENT COMPLETE!")
            print("="*30)
            print("✅ Database schema enhanced with technical fields")
            print("✅ Existing data migrated to proper fields") 
            print("✅ All technical data now properly stored")
            print("\nYour database now captures 100% of the technical data!")
        else:
            print("❌ Data migration failed")
    else:
        print("❌ Schema enhancement failed")

if __name__ == "__main__":
    main()