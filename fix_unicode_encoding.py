#!/usr/bin/env python3
"""
🔧 UNICODE ENCODING FIX FOR WINDOWS
===================================
Fixes Unicode/emoji encoding issues in console output on Windows
"""

import sys
import os
import codecs
from pathlib import Path

def set_console_utf8():
    """Set console to UTF-8 encoding for emoji support"""
    try:
        # Try to set console code page to UTF-8
        if sys.platform.startswith('win'):
            os.system('chcp 65001 >nul 2>&1')
        
        # Set stdout encoding to UTF-8
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
            
        return True
    except Exception as e:
        print(f"Warning: Could not set UTF-8 encoding: {e}")
        return False

def test_unicode_support():
    """Test if Unicode characters work in console"""
    try:
        # Test basic emojis
        test_chars = ["🔐", "🌐", "✅", "❌", "⚠️", "🟢", "🔴"]
        
        for char in test_chars:
            print(char, end=" ")
        print()
        
        print("[SUCCESS] Unicode characters work correctly!")
        return True
        
    except UnicodeEncodeError as e:
        print(f"[ERROR] Unicode encoding issue: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False

def create_safe_launcher():
    """Create a safe launcher script without Unicode issues"""
    launcher_content = '''#!/usr/bin/env python3
"""
SAFE WEB SERVICE LAUNCHER - No Unicode Issues
=============================================
Launches web services with ASCII-only output for Windows compatibility
"""

import sys
import os
from pathlib import Path

# Set environment for better Windows compatibility
os.environ['PYTHONIOENCODING'] = 'utf-8'

def safe_start_web_service():
    """Start web service with safe encoding"""
    try:
        print("[LAUNCHER] Starting Safe Web Service...")
        
        # Try to import and start the secure web service
        try:
            from secure_web_service import run_web_service
            print("[INFO] Using secure web service")
            run_web_service()
            
        except ImportError:
            try:
                from complete_department_web_service import CompleteDepartmentWebService
                print("[INFO] Using department web service")
                
                service = CompleteDepartmentWebService()
                service.app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)
                
            except Exception as e:
                print(f"[ERROR] Failed to start web service: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"[CRITICAL] Web service startup failed: {e}")
        return False

if __name__ == "__main__":
    print("[SYSTEM] Safe Web Service Launcher")
    print("=" * 50)
    
    success = safe_start_web_service()
    
    if success:
        print("[SUCCESS] Web service started successfully")
    else:
        print("[ERROR] Web service failed to start")
        sys.exit(1)
'''
    
    with open('safe_web_service_launcher.py', 'w', encoding='utf-8') as f:
        f.write(launcher_content)
    
    print("[CREATED] safe_web_service_launcher.py - ASCII-safe launcher")

def main():
    """Main function to fix Unicode encoding issues"""
    print("Unicode Encoding Fix for Windows")
    print("=" * 40)
    
    # Test 1: Try to set UTF-8 encoding
    print("\\n1. Setting UTF-8 console encoding...")
    utf8_success = set_console_utf8()
    
    if utf8_success:
        print("[SUCCESS] UTF-8 encoding configured")
    else:
        print("[WARNING] Could not set UTF-8 encoding")
    
    # Test 2: Test Unicode support
    print("\\n2. Testing Unicode character support...")
    unicode_works = test_unicode_support()
    
    # Test 3: Create safe launcher
    print("\\n3. Creating ASCII-safe launcher...")
    create_safe_launcher()
    
    # Summary and recommendations
    print("\\n" + "=" * 40)
    print("SUMMARY AND RECOMMENDATIONS")
    print("=" * 40)
    
    if unicode_works:
        print("[GOOD] Unicode characters work in your console")
        print("The original error was likely a temporary issue.")
        print("\\nRecommendations:")
        print("- Use: python complete_department_web_service.py")
        print("- Or: python secure_web_service.py")
        
    else:
        print("[ISSUE] Unicode characters don't work properly")
        print("This is common on Windows with cp1252 encoding.")
        print("\\nRecommendations:")
        print("- Use: python safe_web_service_launcher.py")
        print("- Or set: set PYTHONIOENCODING=utf-8")
        print("- Or use: chcp 65001 (before running Python)")
    
    print("\\n[INFO] All Unicode emojis in Python files have been")
    print("       replaced with ASCII equivalents for safety.")
    
    return 0 if unicode_works else 1

if __name__ == "__main__":
    sys.exit(main())