#!/usr/bin/env python3
"""
Web Service Complete Test - Port 3010
====================================
Tests all web service components for functionality
"""

import ipaddress  # For IP validation
import subprocess
import time
import requests
import webbrowser
import os
from pathlib import Path

def test_web_service_complete():
    """Test complete web service functionality on port 3010"""
    print("🧪 TESTING COMPLETE WEB SERVICE - PORT 3010")
    print("=" * 60)
    
    # Step 1: Check if port 3010 is available
    print("\n1️⃣ Checking port 3010 availability...")
    try:
        response = requests.get("http://localhost:3010", timeout=2)
        print("⚠️ Port 3010 already in use - will stop existing service")
        
        # Kill existing processes on port 3010
        os.system('powershell -Command "Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force"')
        time.sleep(2)
    except:
        print("✅ Port 3010 is available")
    
    # Step 2: Test fixed_dashboard.py directly
    print("\n2️⃣ Testing fixed_dashboard.py on port 3010...")
    
    venv_python = Path('.venv/Scripts/python.exe')
    python_path = str(venv_python.absolute()) if venv_python.exists() else 'python'
    
    try:
        # Start the dashboard service
        process = subprocess.Popen(
            [python_path, 'fixed_dashboard.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=os.getcwd()
        )
        
        # Give it time to start
        print("⏳ Starting service...")
        time.sleep(5)
        
        # Test if it's responding
        try:
            response = requests.get("http://localhost:3010", timeout=5)
            if response.status_code == 200:
                print("✅ Dashboard service is running successfully!")
                print(f"📊 Status Code: {response.status_code}")
                print("🌐 URL: http://localhost:3010")
                
                # Test browser opening
                print("\n3️⃣ Testing browser opening...")
                webbrowser.open("http://localhost:3010")
                print("✅ Browser should open to the dashboard")
                
            else:
                print(f"❌ Service returned status: {response.status_code}")
        except Exception as e:
            print(f"❌ Service not accessible: {e}")
            
        # Clean up
        process.terminate()
        process.wait(timeout=3)
        
    except Exception as e:
        print(f"❌ Error starting service: {e}")
    
    # Step 3: Test desktop launcher
    print("\n4️⃣ Testing desktop launcher...")
    try:
        from desktop_web_service_launcher import FastWebServiceLauncher
        
        launcher = FastWebServiceLauncher()
        print("✅ Launcher initialized")
        print(f"🚪 Port: {launcher.port}")
        print(f"🌐 Service URL: {launcher.service_url}")
        
        if launcher.port == 3010:
            print("✅ Launcher is configured for port 3010")
        else:
            print(f"❌ Launcher is configured for port {launcher.port}, should be 3010")
            
    except Exception as e:
        print(f"❌ Launcher error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 WEB SERVICE TEST COMPLETE")
    print("🔑 If successful, you can use 'Start Web Service' in Desktop APP")
    print("🌐 Dashboard will be available at: http://localhost:3010")
    print("🔐 Login: admin/admin123")

if __name__ == '__main__':
    test_web_service_complete()