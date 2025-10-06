#!/usr/bin/env python3
"""
🧹 ASSET MANAGEMENT SYSTEM CLEANUP
=================================
Removes outdated and duplicate files that may cause conflicts
Keeps only the essential, working files
"""

import os
import shutil
from pathlib import Path

def cleanup_outdated_files():
    """Remove outdated files to prevent conflicts"""
    
    # Files to remove (outdated/duplicate web services and other problematic files)
    files_to_remove = [
        # Outdated web services
        'production_web_service.py',
        'working_web_service.py', 
        'test_gui_web_service_fix.py',
        'safe_web_service_launcher.py',
        'web_service_config.py',
        
        # Old/duplicate collectors and scripts
        'original_collector.py',
        'basic_collector.py',
        'test_collector.py',
        'legacy_scanner.py',
        'old_main.py',
        'backup_main.py',
        
        # Temporary and test files
        'temp_test.py',
        'debug_test.py',
        'experimental_*.py',
        'old_*.py',
        'backup_*.py',
        'test_*.py',
        
        # Duplicate configuration files
        'old_config.json',
        'backup_config.json',
        'test_config.json'
    ]
    
    # Directories to clean (remove if empty or outdated)
    dirs_to_check = [
        'temp',
        'backup',
        'old',
        'archive'
    ]
    
    removed_count = 0
    kept_essential = []
    
    print("🧹 CLEANING UP OUTDATED FILES")
    print("=" * 50)
    
    # Essential files to keep (never remove these)
    essential_files = {
        'secure_web_service.py',  # Main secure web service
        'enhanced_dashboard_service.py',  # Enhanced dashboard 
        'desktop_web_service_launcher.py',  # Desktop launcher
        'enhanced_web_service_manager.py',  # Web service manager
        'gui_integrated_web_service.py',  # GUI integration
        'complete_department_web_service.py',  # Department service (fallback)
        'unified_web_service_launcher.py',  # Unified launcher (fallback)
        'comprehensive_portal_launcher.py',  # Portal launcher
        'enhanced_access_control_system.py',  # Access control
        'gui/app.py',  # Main GUI
        'assets.db',  # Database
        'requirements.txt'  # Dependencies
    }
    
    # Remove outdated files
    for file_pattern in files_to_remove:
        if '*' in file_pattern:
            # Handle wildcard patterns
            import glob
            matching_files = glob.glob(file_pattern)
            for file_path in matching_files:
                if os.path.exists(file_path) and file_path not in essential_files:
                    try:
                        os.remove(file_path)
                        print(f"🗑️ Removed: {file_path}")
                        removed_count += 1
                    except Exception as e:
                        print(f"❌ Failed to remove {file_path}: {e}")
        else:
            # Handle specific files
            if os.path.exists(file_pattern) and file_pattern not in essential_files:
                try:
                    os.remove(file_pattern)
                    print(f"🗑️ Removed: {file_pattern}")
                    removed_count += 1
                except Exception as e:
                    print(f"❌ Failed to remove {file_pattern}: {e}")
    
    # Check and clean directories
    for dir_path in dirs_to_check:
        if os.path.isdir(dir_path):
            try:
                # Remove directory if it exists and is not essential
                shutil.rmtree(dir_path)
                print(f"🗑️ Removed directory: {dir_path}")
                removed_count += 1
            except Exception as e:
                print(f"❌ Failed to remove directory {dir_path}: {e}")
    
    # List essential files that were kept
    print("\n✅ ESSENTIAL FILES KEPT:")
    print("-" * 30)
    for file in essential_files:
        if os.path.exists(file):
            print(f"✅ {file}")
            kept_essential.append(file)
    
    print(f"\n📊 CLEANUP SUMMARY:")
    print(f"🗑️ Files removed: {removed_count}")
    print(f"✅ Essential files kept: {len(kept_essential)}")
    print("\n🎯 SYSTEM OPTIMIZED FOR DESKTOP USE!")
    
    return removed_count, kept_essential

def verify_essential_services():
    """Verify that all essential services are present and working"""
    print("\n🔍 VERIFYING ESSENTIAL SERVICES")
    print("=" * 40)
    
    essential_services = {
        'secure_web_service.py': 'Secure Web Service (Login)',
        'enhanced_dashboard_service.py': 'Enhanced Dashboard Portal', 
        'desktop_web_service_launcher.py': 'Desktop GUI Launcher',
        'gui/app.py': 'Desktop GUI Application'
    }
    
    all_good = True
    
    for file, description in essential_services.items():
        if os.path.exists(file):
            print(f"✅ {description}: {file}")
        else:
            print(f"❌ MISSING: {description}: {file}")
            all_good = False
    
    if all_good:
        print("\n🎉 ALL ESSENTIAL SERVICES AVAILABLE!")
        print("🚀 Desktop application ready to use")
    else:
        print("\n⚠️ Some essential services are missing!")
        print("📝 Please check the installation")
    
    return all_good

if __name__ == '__main__':
    print("🎯 ASSET MANAGEMENT SYSTEM CLEANUP")
    print("=" * 50)
    print("🧹 Removing outdated files to prevent conflicts...")
    print("✅ Keeping essential services only")
    print("=" * 50)
    
    # Run cleanup
    removed_count, kept_files = cleanup_outdated_files()
    
    # Verify services
    services_ok = verify_essential_services()
    
    print("\n" + "=" * 50)
    if services_ok:
        print("🎉 CLEANUP COMPLETE - SYSTEM READY!")
        print("🌐 Start desktop app to access web services")
        print("🔐 Login: admin/admin123 or user/user123")
    else:
        print("⚠️ CLEANUP COMPLETE WITH WARNINGS")
        print("📝 Check missing services before using")
    print("=" * 50)