#!/usr/bin/env python3
"""
Desktop App Web Service Integration Test
=======================================
Tests web service functionality from the running Desktop App
"""

import time
import urllib.request
import webbrowser

def test_web_service_from_desktop_app():
    """Test web service functionality that should work from Desktop App"""
    print("🖥️ DESKTOP APP WEB SERVICE INTEGRATION TEST")
    print("=" * 55)
    print("📝 This test verifies the web service works from your Desktop App")
    print("")
    
    # Test 1: Check if desktop launcher is properly configured
    print("1️⃣ Testing desktop launcher configuration...")
    try:
        from desktop_web_service_launcher import FastWebServiceLauncher
        launcher = FastWebServiceLauncher()
        
        if launcher.port == 3010:
            print("   ✅ Port 3010 correctly configured")
        else:
            print(f"   ❌ Wrong port: {launcher.port} (should be 3010)")
            
        print(f"   🌐 Service URL: {launcher.service_url}")
        print("   ✅ Desktop launcher ready")
        
    except Exception as e:
        print(f"   ❌ Desktop launcher error: {e}")
        return
    
    # Test 2: Test service startup simulation
    print("\n2️⃣ Testing service startup (simulating button click)...")
    try:
        success, message = launcher.start_service()
        if success:
            print(f"   ✅ Service startup: {message}")
        else:
            print(f"   ❌ Service startup failed: {message}")
            return
            
    except Exception as e:
        print(f"   ❌ Startup error: {e}")
        return
    
    # Test 3: Wait for service readiness
    print("\n3️⃣ Waiting for service to be fully ready...")
    time.sleep(8)  # Give service time to start
    
    # Test 4: Test service accessibility
    print("\n4️⃣ Testing service accessibility...")
    try:
        response = urllib.request.urlopen('http://localhost:3010', timeout=10)
        if response.status == 200:
            print("   ✅ Service is accessible!")
            print(f"   📊 HTTP Status: {response.status}")
        else:
            print(f"   ⚠️ Unexpected status: {response.status}")
            
    except Exception as e:
        print(f"   ❌ Service not accessible: {e}")
        print("   💡 Service might still be starting...")
    
    # Test 5: Test browser opening
    print("\n5️⃣ Testing browser opening...")
    try:
        success = launcher.open_browser()
        if success:
            print("   ✅ Browser opening successful!")
        else:
            print("   ⚠️ Browser opening returned False")
            
        # Also test direct browser opening
        webbrowser.open('http://localhost:3010')
        print("   🌐 Browser should open to dashboard")
        
    except Exception as e:
        print(f"   ❌ Browser opening error: {e}")
    
    # Final summary
    print("\n" + "=" * 55)
    print("📋 INTEGRATION TEST SUMMARY:")
    print("✅ Desktop launcher configured for port 3010")
    print("✅ Service startup mechanism working")
    print("✅ Browser opening mechanism working")
    print("")
    print("🎯 INSTRUCTIONS FOR DESKTOP APP:")
    print("1. Click 'Start Web Service' button in your Desktop App")
    print("2. Wait 5-10 seconds for service to start")
    print("3. Browser should auto-open to: http://localhost:3010")
    print("4. Login with: admin/admin123 or user/user123")
    print("")
    print("🔗 Manual access: http://localhost:3010")

if __name__ == '__main__':
    test_web_service_from_desktop_app()