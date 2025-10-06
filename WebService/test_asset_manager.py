#!/usr/bin/env python3
import sys
import os
sys.path.append('.')

# Test the get_all_assets method directly
from intelligent_app import IntelligentAssetManager

try:
    print("Testing IntelligentAssetManager...")
    asset_manager = IntelligentAssetManager()
    print("AssetManager created successfully")
    
    print("\nTesting get_all_assets method...")
    assets = asset_manager.get_all_assets()
    print(f"get_all_assets returned {len(assets)} assets")
    
    if assets:
        print("\nFirst asset sample:")
        print(assets[0])
    
    print("\nTesting get_comprehensive_stats method...")
    stats = asset_manager.get_comprehensive_stats()
    print(f"Stats: {stats}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

def test_database_connection():
    """Test basic database connectivity"""
    db_path = "../assets.db"
    
    print("[INFO] Testing database connection...")
    print(f"[INFO] Database path: {os.path.abspath(db_path)}")
    print(f"[INFO] Database exists: {os.path.exists(db_path)}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"[OK] Database connection successful")
        print(f"[INFO] Found {len(tables)} tables:")
        for table in tables:
            print(f"  - {table[0]}")
            
        # Test assets table
        try:
            cursor.execute("SELECT COUNT(*) FROM assets")
            asset_count = cursor.fetchone()[0]
            print(f"[OK] Assets table: {asset_count} records")
        except Exception as e:
            print(f"[WARNING] Assets table issue: {e}")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return False

def test_asset_manager_import():
    """Test importing the asset manager"""
    print("\n[INFO] Testing asset manager import...")
    
    try:
        from intelligent_app import IntelligentAssetManager
        print("[OK] IntelligentAssetManager import successful")
        return True
    except Exception as e:
        print(f"[ERROR] Import failed: {e}")
        return False

def test_asset_manager_initialization():
    """Test asset manager initialization"""
    print("\n[INFO] Testing asset manager initialization...")
    
    try:
        from intelligent_app import IntelligentAssetManager
        
        print("[INFO] Creating IntelligentAssetManager instance...")
        asset_manager = IntelligentAssetManager()
        print("[OK] IntelligentAssetManager initialized successfully")
        
        # Test basic functionality
        print("[INFO] Testing basic functionality...")
        stats = asset_manager.get_comprehensive_stats()
        print(f"[OK] Stats retrieved: {len(stats)} fields")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Asset manager initialization failed: {e}")
        print(f"[ERROR] Error type: {type(e).__name__}")
        import traceback
        print("[ERROR] Full traceback:")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("ASSET MANAGEMENT SYSTEM - DIAGNOSTICS")
    print("=" * 60)
    
    # Test 1: Database connection
    db_ok = test_database_connection()
    
    # Test 2: Import
    import_ok = test_asset_manager_import()
    
    # Test 3: Initialization (only if import works)
    init_ok = False
    if import_ok:
        init_ok = test_asset_manager_initialization()
    
    # Summary
    print("\n" + "=" * 60)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 60)
    print(f"Database Connection: {'[OK]' if db_ok else '[FAILED]'}")
    print(f"Asset Manager Import: {'[OK]' if import_ok else '[FAILED]'}")
    print(f"Asset Manager Init: {'[OK]' if init_ok else '[FAILED]'}")
    
    if db_ok and import_ok and init_ok:
        print("\n[SUCCESS] All tests passed! Asset Manager should work in web service.")
    else:
        print("\n[ERROR] Some tests failed. Web service may have issues.")
        
        if not db_ok:
            print("  - Fix database connection first")
        if not import_ok:
            print("  - Check Python dependencies and imports")
        if not init_ok:
            print("  - Check asset manager initialization code")

if __name__ == "__main__":
    main()