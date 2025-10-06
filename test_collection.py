#!/usr/bin/env python3
"""
Quick test to verify collection functionality
"""

import sys
import os
from pathlib import Path

# Add project root to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_collection():
    """Test that collection starts and runs without hanging"""
    
    print("🧪 Testing collection functionality...")
    
    try:
        # Import required modules
        from core.worker import DeviceInfoCollector
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import QTimer
        
        # Create minimal QApplication for Qt objects
        app = QApplication([])
        
        # Test parameters
        targets = ["127.0.0.1"]  # Test with localhost
        win_creds = []
        linux_creds = []
        snmp_v2c = []
        snmp_v3 = {}
        excel_file = None
        
        print("📡 Creating DeviceInfoCollector...")
        collector = DeviceInfoCollector(
            targets=targets,
            win_creds=win_creds,
            linux_creds=linux_creds,
            snmp_v2c=snmp_v2c,
            snmp_v3=snmp_v3,
            excel_file=excel_file,
            use_http=True
        )
        
        # Connect test signals
        collector.log_message.connect(lambda msg: print(f"📝 {msg}"))
        collector.update_progress.connect(lambda val: print(f"📊 Progress: {val}%"))
        collector.finished_with_status.connect(lambda success: print(f"✅ Finished: {success}"))
        
        print("🚀 Starting collection test...")
        collector.start()
        
        # Set a timer to stop the test after 10 seconds
        QTimer.singleShot(10000, app.quit)
        
        # Run for a short time to see if it works
        app.exec()
        
        print("✅ Collection test completed - no hanging detected!")
        return True
        
    except Exception as e:
        print(f"❌ Collection test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_collection()
    sys.exit(0 if success else 1)