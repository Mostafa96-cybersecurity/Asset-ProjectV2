#!/usr/bin/env python3
"""
🧹 SMART FILE CLEANUP - Only Delete Unused Files
===============================================
Analyzes import relationships and usage to safely delete only unused files
"""

import os
import ast
from pathlib import Path

def find_imports_in_file(file_path):
    """Find all imports in a Python file"""
    imports = set()
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Parse AST to find imports
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])
        except:
            pass
        
        # Also find string-based imports (like exec, __import__, etc.)
        import re
        string_imports = re.findall(r'from\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+import', content)
        string_imports += re.findall(r'import\s+([a-zA-Z_][a-zA-Z0-9_]*)', content)
        
        for imp in string_imports:
            imports.add(imp)
            
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")
    
    return imports

def analyze_file_usage():
    """Analyze which files are used in the project"""
    
    print("🔍 ANALYZING FILE USAGE...")
    print("=" * 50)
    
    # Core production files (NEVER DELETE)
    core_files = {
        'launch_original_desktop.py',
        'gui/app.py',
        'gui/error_monitor_dashboard.py',
        'core/worker.py',
        'config/settings.py',
        'collectors/snmp_collector.py',
        'collectors/ui_add_network_device.py',
        'utils/helpers.py'
    }
    
    # Web service files to analyze
    web_service_files = []
    dashboard_files = []
    
    # Find all Python files
    all_py_files = []
    for root, dirs, files in os.walk('.'):
        # Skip virtual environment and hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file).replace('\\\\', '/')
                all_py_files.append(file_path)
                
                # Categorize files
                if 'dashboard' in file or 'web_service' in file or 'portal' in file:
                    if 'dashboard' in file:
                        dashboard_files.append(file_path)
                    else:
                        web_service_files.append(file_path)
    
    # Build import graph
    import_graph = {}
    imported_modules = set()
    
    for file_path in all_py_files:
        imports = find_imports_in_file(file_path)
        import_graph[file_path] = imports
        
        # Track which local modules are imported
        for imp in imports:
            # Check if it's a local file
            possible_paths = [
                f"{imp}.py",
                f"{imp}//__init__.py",
                f"gui/{imp}.py",
                f"core/{imp}.py",
                f"collectors/{imp}.py",
                f"utils/{imp}.py"
            ]
            
            for possible_path in possible_paths:
                if os.path.exists(possible_path):
                    imported_modules.add(possible_path)
    
    print("📊 ANALYSIS RESULTS:")
    print("-" * 30)
    
    # Check web service files
    print("\\n🌐 WEB SERVICE FILES:")
    used_web_services = []
    unused_web_services = []
    
    for file_path in web_service_files + dashboard_files:
        file_name = os.path.basename(file_path)
        module_name = file_name.replace('.py', '')
        
        is_used = False
        
        # Check if imported anywhere
        if file_path in imported_modules:
            is_used = True
        
        # Check if referenced by name in other files
        for other_file in all_py_files:
            if file_path != other_file:
                try:
                    with open(other_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    if module_name in content or file_name in content:
                        is_used = True
                        break
                except:
                    pass
        
        # Special cases - check if it's a main service file
        if file_name in ['fixed_dashboard.py', 'secure_web_service.py', 'consolidated_enhanced_dashboard.py']:
            is_used = True  # Keep main dashboard files
        
        if is_used:
            used_web_services.append(file_path)
            print(f"✅ USED: {file_path}")
        else:
            unused_web_services.append(file_path)
            print(f"❌ UNUSED: {file_path}")
    
    # Check for test files and duplicates
    print("\\n🧪 TEST FILES:")
    test_files = []
    for file_path in all_py_files:
        file_name = os.path.basename(file_path)
        if any(keyword in file_name.lower() for keyword in [
            'test_', '_test', 'quick_', 'demo_', 'example_', 'temp_', 
            'backup_', 'old_', 'copy_', 'duplicate_', '_copy', '_old',
            'trial_', 'sample_'
        ]):
            # Check if it's actually used
            is_used = file_path in imported_modules
            if not is_used:
                test_files.append(file_path)
                print(f"🗑️ TEST FILE: {file_path}")
            else:
                print(f"⚠️ TEST FILE BUT USED: {file_path}")
    
    # Check for orphaned enhancement files
    print("\\n🔧 ENHANCEMENT FILES:")
    enhancement_files = []
    for file_path in all_py_files:
        file_name = os.path.basename(file_path)
        if any(keyword in file_name.lower() for keyword in [
            'enhancement', 'enhanced_', 'ultra_', 'ultimate_', 'advanced_',
            'improved_', 'optimized_', 'fast_', 'super_', 'mega_'
        ]):
            is_used = file_path in imported_modules
            
            # Also check if it's referenced in import statements
            if not is_used:
                for other_file in all_py_files:
                    if file_path != other_file:
                        try:
                            with open(other_file, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                            module_name = file_name.replace('.py', '')
                            if f"from {module_name}" in content or f"import {module_name}" in content:
                                is_used = True
                                break
                        except:
                            pass
            
            if not is_used:
                enhancement_files.append(file_path)
                print(f"🗑️ UNUSED ENHANCEMENT: {file_path}")
            else:
                print(f"✅ USED ENHANCEMENT: {file_path}")
    
    return unused_web_services, test_files, enhancement_files

def safe_cleanup():
    """Perform safe cleanup of unused files"""
    
    print("\\n🧹 STARTING SAFE CLEANUP...")
    print("=" * 50)
    
    unused_web, test_files, enhancement_files = analyze_file_usage()
    
    # Files to delete
    files_to_delete = []
    
    # Add clearly unused files
    safe_to_delete_patterns = [
        # Test and temporary files
        'test_dashboard_connection.py',
        'test_connection.py',
        'quick_test.py',
        'temp_',
        '_temp.py',
        'backup_',
        '_backup.py',
        
        # Demo and example files
        'demo_',
        'example_',
        'sample_',
        
        # Duplicate files
        'copy_',
        '_copy.py',
        'duplicate_',
        '_duplicate.py',
        
        # Old versions
        'old_',
        '_old.py',
        'legacy_',
        '_legacy.py'
    ]
    
    # Find files matching these patterns
    for file_path in Path('.').rglob('*.py'):
        file_name = file_path.name
        if any(pattern in file_name.lower() for pattern in safe_to_delete_patterns):
            # Double-check it's not imported
            is_imported = False
            try:
                for check_file in Path('.').rglob('*.py'):
                    if check_file != file_path:
                        with open(check_file, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        module_name = file_name.replace('.py', '')
                        if module_name in content and ('import' in content or 'from' in content):
                            is_imported = True
                            break
            except:
                pass
            
            if not is_imported:
                files_to_delete.append(str(file_path))
    
    # Show what will be deleted
    print(f"\\n📋 FILES TO DELETE ({len(files_to_delete)} total):")
    print("-" * 40)
    
    for file_path in files_to_delete:
        print(f"🗑️ {file_path}")
    
    # Ask for confirmation
    if files_to_delete:
        print(f"\\n⚠️ READY TO DELETE {len(files_to_delete)} FILES")
        print("These files appear to be unused based on analysis.")
        
        try:
            confirm = input("\\nProceed with deletion? (y/N): ").strip().lower()
            if confirm in ['y', 'yes']:
                deleted_count = 0
                for file_path in files_to_delete:
                    try:
                        os.remove(file_path)
                        print(f"✅ Deleted: {file_path}")
                        deleted_count += 1
                    except Exception as e:
                        print(f"❌ Failed to delete {file_path}: {e}")
                
                print(f"\\n🎉 CLEANUP COMPLETE: {deleted_count} files deleted")
            else:
                print("\\n❌ Cleanup cancelled by user")
        except (KeyboardInterrupt, EOFError):
            print("\\n❌ Cleanup cancelled")
    else:
        print("\\n✅ No unused files found - codebase is clean!")

if __name__ == "__main__":
    safe_cleanup()