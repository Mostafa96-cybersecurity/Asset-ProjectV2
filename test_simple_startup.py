#!/usr/bin/env python3
"""
Simple Web Service Test - No Threading Issues
============================================
Tests web service startup without Qt threading problems
"""

def test_simple_startup():
    """Test simple web service startup"""
    print("🚀 SIMPLE WEB SERVICE STARTUP TEST")
    print("=" * 45)
    
    try:
        from desktop_web_service_launcher import FastWebServiceLauncher
        
        # Create launcher
        launcher = FastWebServiceLauncher()
        print(f"✅ Launcher created for port {launcher.port}")
        
        # Start service
        print("⏳ Starting service...")
        success, message = launcher.start_service()
        
        if success:
            print(f"✅ {message}")
            
            # Test browser opening
            print("🌐 Testing browser opening...")
            browser_result = launcher.open_browser()
            if browser_result:
                print("✅ Browser opened successfully!")
            
            print("\n🎯 SUCCESS! Web service working!")
            print("📝 From Desktop App: Click 'Start Web Service' button")
            print("🌐 URL: http://localhost:3010")
            print("🔐 Login: admin/admin123")
            
        else:
            print(f"❌ {message}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    test_simple_startup()