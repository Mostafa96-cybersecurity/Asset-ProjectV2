#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Desktop Application Launcher
----------------------------------
Launches the lightweight, fast desktop application
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("Starting Fast Asset Management Desktop Application...")
print("=" * 50)

def main():
    """Main launcher function"""
    try:
        # Quick checks
        print("Checking PyQt6...")
        from PyQt6.QtWidgets import QApplication
        print("✓ PyQt6 available")
        
        print("Checking database...")
        from db.connection import connect
        with connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM assets")
            asset_count = cursor.fetchone()[0]
            print(f"✓ Database accessible - {asset_count} assets")
        
        print("Launching application...")
        from simple_fast_main import main as app_main
        return app_main()
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code or 0)
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)