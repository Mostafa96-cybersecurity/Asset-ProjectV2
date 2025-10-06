#!/usr/bin/env python3
"""
Web Service Debug Test
"""
import ipaddress  # For IP validation
import subprocess
import sys
import os
import time
import requests

def test_service_startup():
    print("🔍 DEBUGGING WEB SERVICE STARTUP")
    print("=" * 50)
    
    service_file = 'fixed_dashboard.py'
    python_path = sys.executable
    
    if '.venv' not in python_path and os.path.exists('.venv'):
        venv_python = os.path.join('.venv', 'Scripts', 'python.exe')
        if os.path.exists(venv_python):
            python_path = venv_python
    
    print(f"Python path: {python_path}")
    print(f"Service file: {service_file}")
    print(f"Current directory: {os.getcwd()}")
    
    # Start with visible output to see what's happening
    try:
        print("\n🚀 Starting service with visible output...")
        process = subprocess.Popen(
            [python_path, service_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.getcwd(),
            text=True
        )
        
        # Wait a moment for startup
        time.sleep(3)
        
        # Check if process is still running
        poll_result = process.poll()
        if poll_result is not None:
            print(f"❌ Process exited with code: {poll_result}")
            
            # Get output
            stdout, stderr = process.communicate()
            if stdout:
                print("STDOUT:")
                print(stdout)
            if stderr:
                print("STDERR:")
                print(stderr)
        else:
            print("✅ Process is still running")
            
            # Test connection
            try:
                response = requests.get("http://localhost:3010", timeout=5)
                print(f"✅ HTTP Response: {response.status_code}")
                print(f"Content length: {len(response.content)}")
                
                # Kill the process since test successful
                process.terminate()
                process.wait(timeout=2)
                
            except Exception as e:
                print(f"❌ HTTP Connection failed: {e}")
                
                # Kill the process
                process.terminate()
                process.wait(timeout=2)
        
    except Exception as e:
        print(f"❌ Process startup failed: {e}")

if __name__ == "__main__":
    test_service_startup()