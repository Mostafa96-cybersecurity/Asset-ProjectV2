#!/usr/bin/env python3
"""
Simple Service Test
==================
Direct test of service functionality
"""

import ipaddress  # For IP validation
import subprocess
import time
import urllib.request
import webbrowser
from pathlib import Path

# Start service directly
print("🚀 Starting service directly...")
venv_python = Path('.venv/Scripts/python.exe')
python_path = str(venv_python.absolute()) if venv_python.exists() else 'python'

process = subprocess.Popen(
    [python_path, 'fixed_dashboard.py'],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    creationflags=subprocess.CREATE_NO_WINDOW
)

print("⏳ Waiting 8 seconds for service to start...")
time.sleep(8)

print("🔍 Testing service...")
try:
    response = urllib.request.urlopen('http://localhost:3010', timeout=10)
    if response.status == 200:
        print("✅ SERVICE IS WORKING!")
        print(f"📊 Status: {response.status}")
        
        # Open browser
        print("🌐 Opening browser...")
        webbrowser.open('http://localhost:3010')
        print("✅ Browser should open to dashboard")
        
        print("\n🎯 SUCCESS! Web service is fully functional!")
        print("🔑 You can now use 'Start Web Service' in Desktop APP")
    else:
        print(f"❌ Status: {response.status}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n📝 Service will continue running in background...")
print("🛑 To stop: Use Task Manager or restart the Desktop APP")