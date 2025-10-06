#!/usr/bin/env python3
"""
Simple test for web service startup
"""

import ipaddress  # For IP validation
import subprocess
import os
import time
import requests

def test_simple_startup():
    """Test simple subprocess startup"""
    
    python_path = r"D:\Assets-Projects\Asset-Project-Enhanced\.venv\Scripts\python.exe"
    service_file = 'fixed_dashboard.py'
    
    print("Testing subprocess startup...")
    print(f"Python: {python_path}")
    print(f"Service: {service_file}")
    
    try:
        # Start the service
        process = subprocess.Popen(
            [python_path, service_file],
            cwd=os.getcwd()
        )
        
        print(f"Process started with PID: {process.pid}")
        
        # Wait longer for service to fully start
        print("Waiting for service to start...")
        time.sleep(8)  # Wait 8 seconds instead of 3
        
        # Check if process is still running
        poll_result = process.poll()
        if poll_result is None:
            print("Process is still running!")
            
            # Test if service responds
            try:
                response = requests.get("http://localhost:5556", timeout=15)  # Increased timeout
                print(f"Service responded with status: {response.status_code}")
                
                # Stop the process
                process.terminate()
                process.wait(timeout=5)
                print("Process terminated successfully")
                
                return True
            except requests.exceptions.RequestException as e:
                print(f"Service not accessible: {e}")
                process.terminate()
                return False
        else:
            print(f"Process exited with code: {poll_result}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    result = test_simple_startup()
    print(f"Test result: {result}")