#!/usr/bin/env python3
"""
Backup File Cleanup Tool
------------------------
Clean up excessive Excel backup files created by the synchronization system.
Keeps only the most recent 3 backups per file.
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

def setup_logging():
    """Setup logging for cleanup operations"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('backup_cleanup.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def find_backup_files(directory: str) -> List[str]:
    """Find all backup files in the directory"""
    backup_files = []
    
    try:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if '.backup_' in file and file.endswith(('.xlsx', '.xls')):
                    full_path = os.path.join(root, file)
                    backup_files.append(full_path)
                elif file.endswith('.backup_20'):  # Common timestamp pattern
                    full_path = os.path.join(root, file)
                    backup_files.append(full_path)
    except Exception as e:
        print(f"Error scanning directory {directory}: {e}")
    
    return backup_files

def group_backups_by_original(backup_files: List[str]) -> dict:
    """Group backup files by their original file"""
    groups = {}
    
    for backup_path in backup_files:
        # Extract original filename
        backup_name = os.path.basename(backup_path)
        
        if '.backup_' in backup_name:
            original_name = backup_name.split('.backup_')[0]
            if '.xlsx' not in original_name and '.xls' not in original_name:
                original_name += '.xlsx'  # Add extension if missing
        else:
            # Handle other backup patterns
            original_name = backup_name.replace('.backup_', '.')
        
        if original_name not in groups:
            groups[original_name] = []
        
        groups[original_name].append(backup_path)
    
    return groups

def get_file_info(file_path: str) -> Tuple[datetime, int]:
    """Get file modification time and size"""
    try:
        stat = os.stat(file_path)
        return datetime.fromtimestamp(stat.st_mtime), stat.st_size
    except:
        return datetime.min, 0

def cleanup_backup_group(original_file: str, backup_files: List[str], keep_count: int = 3, dry_run: bool = False) -> dict:
    """Cleanup backups for a specific original file"""
    log = logging.getLogger(__name__)
    
    if len(backup_files) <= keep_count:
        log.info(f"📁 {original_file}: {len(backup_files)} backups (keeping all)")
        return {'kept': len(backup_files), 'removed': 0, 'size_freed': 0}
    
    # Sort by modification time (newest first)
    file_info = [(path, *get_file_info(path)) for path in backup_files]
    file_info.sort(key=lambda x: x[1], reverse=True)
    
    # Keep the newest files, remove the rest
    to_keep = file_info[:keep_count]
    to_remove = file_info[keep_count:]
    
    removed_count = 0
    size_freed = 0
    
    for file_path, mod_time, file_size in to_remove:
        try:
            if dry_run:
                log.info(f"🔍 Would remove: {file_path} ({file_size:,} bytes, {mod_time})")
            else:
                os.remove(file_path)
                log.info(f"🗑️ Removed: {file_path} ({file_size:,} bytes)")
                removed_count += 1
                size_freed += file_size
        except Exception as e:
            log.error(f"❌ Failed to remove {file_path}: {e}")
    
    log.info(f"📁 {original_file}: Kept {len(to_keep)}, Removed {removed_count}, Freed {size_freed:,} bytes")
    
    return {
        'kept': len(to_keep),
        'removed': removed_count,
        'size_freed': size_freed
    }

def main():
    """Main cleanup function"""
    log = setup_logging()
    
    # Get the current project directory
    project_dir = Path(__file__).parent.parent
    
    print("🧹 Excel Backup File Cleanup Tool")
    print("=" * 40)
    print(f"📂 Scanning directory: {project_dir}")
    
    # Find all backup files
    backup_files = find_backup_files(str(project_dir))
    
    if not backup_files:
        print("✅ No backup files found!")
        return
    
    print(f"🔍 Found {len(backup_files)} backup files")
    
    # Group backups by original file
    backup_groups = group_backups_by_original(backup_files)
    
    print(f"📊 Backup files grouped into {len(backup_groups)} original files")
    print()
    
    # Show what would be cleaned up
    print("🔍 DRY RUN - What would be removed:")
    print("-" * 50)
    
    total_stats = {'kept': 0, 'removed': 0, 'size_freed': 0}
    
    for original_file, file_list in backup_groups.items():
        stats = cleanup_backup_group(original_file, file_list, keep_count=3, dry_run=True)
        for key in total_stats:
            total_stats[key] += stats[key]
    
    print()
    print("📊 Summary (DRY RUN):")
    print(f"   Files to keep: {total_stats['kept']}")
    print(f"   Files to remove: {total_stats['removed']}")
    print(f"   Space to free: {total_stats['size_freed']:,} bytes ({total_stats['size_freed']/1024/1024:.1f} MB)")
    
    # Ask for confirmation
    if total_stats['removed'] > 0:
        print()
        response = input("🤔 Do you want to proceed with cleanup? (y/N): ").strip().lower()
        
        if response in ['y', 'yes']:
            print()
            print("🧹 ACTUAL CLEANUP - Removing old backup files:")
            print("-" * 50)
            
            actual_stats = {'kept': 0, 'removed': 0, 'size_freed': 0}
            
            for original_file, file_list in backup_groups.items():
                stats = cleanup_backup_group(original_file, file_list, keep_count=3, dry_run=False)
                for key in actual_stats:
                    actual_stats[key] += stats[key]
            
            print()
            print("✅ CLEANUP COMPLETE!")
            print(f"   Files kept: {actual_stats['kept']}")
            print(f"   Files removed: {actual_stats['removed']}")
            print(f"   Space freed: {actual_stats['size_freed']:,} bytes ({actual_stats['size_freed']/1024/1024:.1f} MB)")
            
        else:
            print("❌ Cleanup cancelled by user")
    else:
        print("✅ No cleanup needed!")

if __name__ == "__main__":
    main()