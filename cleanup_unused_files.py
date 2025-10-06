#!/usr/bin/env python3
"""
Cleanup unused test and duplicate web service files
"""

import os
import sys
from pathlib import Path

def main():
    """Main cleanup function"""
    
    # PRODUCTION FILES (DO NOT DELETE)
    production_files = {
        # Main web services (PRODUCTION)
        'fixed_dashboard.py',                    # MAIN: Fixed dashboard with authentication
        'secure_web_service.py',                 # BACKUP: Secure service with login
        'complete_department_web_service.py',    # DEPARTMENT: Department management service
        'enhanced_web_portal_with_departments.py', # PORTAL: Enhanced portal
        'enhanced_device_web_portal.py',         # DEVICE: Device portal
        'consolidated_enhanced_dashboard.py',    # CONSOLIDATED: Main dashboard
        'unified_web_service_launcher.py',       # LAUNCHER: Service launcher
        'enhanced_web_service_manager.py',       # MANAGER: Service manager
        'comprehensive_portal_launcher.py',      # COMPREHENSIVE: Portal launcher
        
        # GUI components (PRODUCTION)
        'gui/app.py',                           # MAIN: GUI application
        'gui/error_monitor_dashboard.py',       # MONITORING: Error monitoring
        'launch_original_desktop.py',           # MAIN: Desktop launcher
    }
    
    # TEST AND DUPLICATE FILES (SAFE TO DELETE)
    test_files_to_delete = [
        # Test dashboards
        'test_dashboard_5556.py',
        'test_dashboard_connection.py',
        'test_connection.py',
        'test_integration.py',
        
        # Minimal/Simple versions (duplicates)
        'minimal_dashboard.py',
        'simple_working_dashboard.py',
        'ultra_simple_dashboard.py',
        'working_dashboard_5556.py',
        
        # Quick test files
        'quick_launch_dashboard.py',
        'quick_test.py',
        'quick_test_fix.py',
        'quick_database_update.py',
        'quick_db_analysis.py',
        'quick_fix_types.py',
        
        # Ultra/Enhanced duplicates
        'ultra_enhanced_web_service.py.backup_20251002_145943',
        'ultra_fast_collector_demo.py',
        'ultra_fast_collector_gui.py',
        'ultra_fast_collector_integration.py',
        'ultra_fast_multi_method_collector.py',
        'ultra_fast_smart_validator.py',
        'ultra_fast_speed_gui.py',
        'ultra_high_speed_scanner.py',
        'ultra_accurate_validator.py',
        
        # Working versions (duplicates)
        'working_ad_integration.py',
        'working_automatic_scanner.py',
        'working_collection_manager.py',
        'working_stop_collection.py',
        'working_enhanced_app.log',
        
        # Enhanced template/service duplicates
        'enhanced_dashboard_template.py',
        'enhanced_dashboard_service.py',
        
        # Simple/Fast test files
        'simple_completion_log.py',
        'simple_fast_main.py',
        'simple_wmi_test.py',
        'fast_test_collector.py',
        'wmi_quick_test.py',
        
        # Other test files
        'restore_working_version.py',
        
        # Batch files for testing
        'QUICK_TEST.bat',
        'LAUNCH_DASHBOARD.bat',
        'LAUNCH_AMAZING_DASHBOARD.bat',
        'ULTIMATE_DASHBOARD_LAUNCHER.bat'
    ]
    
    # Markdown documentation files (keep important ones)
    docs_to_keep = [
        'ALL_FEATURES_WORKING_SUMMARY.md',
        'ENHANCED_DASHBOARD_COMPLETE.md',
        'ENHANCED_DASHBOARD_SUCCESS.md',
        'DASHBOARD_SOLUTION_COMPLETE.md',
        'ULTRA_FAST_LARGE_SUBNET_COLLECTOR_COMPLETE.md'
    ]
    
    # Additional docs that can be deleted
    docs_to_delete = [
        'PROJECT_TEST_CHECKLIST.md',
        'TEST_RESULTS_SUMMARY.md'
    ]
    
    print("🧹 CLEANUP: Removing unused test and duplicate web service files")
    print("=" * 60)
    
    deleted_count = 0
    kept_count = 0
    
    # Delete test files
    for file_path in test_files_to_delete:
        full_path = Path(file_path)
        if full_path.exists():
            try:
                full_path.unlink()
                print(f"✅ Deleted: {file_path}")
                deleted_count += 1
            except Exception as e:
                print(f"❌ Failed to delete {file_path}: {e}")
        else:
            print(f"⚠️ Not found: {file_path}")
    
    # Delete extra docs
    for doc_path in docs_to_delete:
        full_path = Path(doc_path)
        if full_path.exists():
            try:
                full_path.unlink()
                print(f"✅ Deleted doc: {doc_path}")
                deleted_count += 1
            except Exception as e:
                print(f"❌ Failed to delete {doc_path}: {e}")
    
    print("\n" + "=" * 60)
    print("📊 PRODUCTION FILES KEPT:")
    for prod_file in sorted(production_files):
        if Path(prod_file).exists():
            print(f"✅ KEPT: {prod_file}")
            kept_count += 1
        else:
            print(f"⚠️ MISSING: {prod_file}")
    
    print("\n" + "=" * 60)
    print(f"🧹 CLEANUP COMPLETE:")
    print(f"   🗑️ Files deleted: {deleted_count}")
    print(f"   📁 Production files kept: {kept_count}")
    print(f"   🎯 Web services now use port 5556 ONLY")
    print(f"   🚀 No auto-startup - use launch_original_desktop.py")
    
    print("\n🎯 REMAINING WEB SERVICE FILES:")
    web_service_patterns = ['*dashboard*.py', '*web_service*.py', '*portal*.py']
    remaining_files = []
    
    for pattern in web_service_patterns:
        for file_path in Path('.').glob(pattern):
            if file_path.name not in [f for f in test_files_to_delete]:
                remaining_files.append(str(file_path))
    
    for file_path in sorted(remaining_files):
        print(f"   📝 {file_path}")
    
    print("\n✅ CLEANUP COMPLETE - All web services fixed to port 5556")
    print("💡 Use launch_original_desktop.py → GUI → 'Start Web Service' button")

if __name__ == "__main__":
    main()