#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Enhanced Web Service Launcher
----------------------------
Simple launcher that avoids Unicode encoding issues
for integration with desktop app.
"""

import sys
import os

# Set UTF-8 encoding environment variables
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONPATH'] = os.getcwd()

# Import and run the enhanced web service
if __name__ == '__main__':
    try:
        from enhanced_complete_web_service import EnhancedCompleteDepartmentWebService
        
        print("Starting Enhanced Web Service...")
        print("URL: http://127.0.0.1:8080")
        print("Features: Edit, Auto-refresh, Database monitoring, Asset control")
        
        service = EnhancedCompleteDepartmentWebService()
        service.run(debug=False)  # Disable debug to avoid encoding issues
        
    except Exception as e:
        print(f"Error starting web service: {e}")
        sys.exit(1)