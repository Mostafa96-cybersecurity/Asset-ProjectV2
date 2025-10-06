#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SAFE WEB SERVICE LAUNCHER
========================
Starts the web service with proper error handling and encoding support.
"""

import os
import sys
import io

def setup_console_encoding():
    """Setup console encoding to handle Unicode properly on Windows"""
    if sys.platform == "win32":
        try:
            import codecs
            sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
            sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())
            print("[ENCODING] Console encoding set to UTF-8")
        except Exception as e:
            print(f"[WARNING] Could not set UTF-8 encoding: {e}")
            print("[INFO] Continuing with system default encoding")

def safe_start_web_service():
    """Safely start the web service with error handling"""
    try:
        # Setup encoding first
        setup_console_encoding()
        
        print("[STARTING] Safe Web Service Launcher")
        print("[INFO] Setting up web service environment...")
        
        # Add WebService directory to path
        web_service_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, web_service_dir)
        
        # Try to import and start the intelligent service
        print("[LOADING] Importing intelligent app...")
        from intelligent_app import run_intelligent_service
        
        print("[SUCCESS] Web service modules loaded")
        print("[STARTING] Launching intelligent asset management system...")
        
        # Start the service
        run_intelligent_service()
        
    except ImportError as e:
        print(f"[ERROR] Failed to import web service modules: {e}")
        print("[INFO] Check if all required modules are installed")
        return False
    except UnicodeEncodeError as e:
        print(f"[ERROR] Unicode encoding error: {e}")
        print("[INFO] The web service contains characters that cannot be displayed in this console")
        print("[INFO] The service may still be running in the background")
        return False
    except Exception as e:
        print(f"[ERROR] Web service startup failed: {e}")
        print("[INFO] Check the error details above")
        return False

if __name__ == '__main__':
    success = safe_start_web_service()
    if not success:
        print("[NOTICE] Web service startup encountered issues")
        print("[NOTICE] Desktop application with automation is still available")
        input("Press Enter to continue...")