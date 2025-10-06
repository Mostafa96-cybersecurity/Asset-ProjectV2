#!/usr/bin/env python3
"""
Debug Web Service Launcher
==========================
Captures output to see what's wrong
"""

import ipaddress  # For IP validation
import subprocess
import sys
import os
from pathlib import Path

def debug_start_service():
    """Start service with visible output for debugging"""
    
    venv_python = Path('.venv/Scripts/python.exe')
    python_path = str(venv_python.absolute()) if venv_python.exists() else sys.executable
    
    service_file = 'fixed_dashboard.py'
    
    print(f"🐛 DEBUG: Starting {service_file} with visible output...")
    print(f"🐛 DEBUG: Using Python: {python_path}")
    
    # Start with visible output
    process = subprocess.Popen(
        [python_path, service_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=os.getcwd()
    )
    
    # Read output line by line
    for line in process.stdout:
        print(f"📄 {line.strip()}")
        if "Server error" in line:
            print("❌ ERROR DETECTED!")
            break
        if "Starting fixed HTTP server" in line:
            print("✅ Server startup detected!")
            # Let it run for a bit to see if it stays up
            import time
            time.sleep(3)
            try:
                process.stdout.close()
                process.wait(timeout=1)
            except:
                pass

if __name__ == '__main__':
    debug_start_service()