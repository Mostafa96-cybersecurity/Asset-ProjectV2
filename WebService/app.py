#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INTELLIGENT ASSET MANAGEMENT WEB SERVICE - MAIN ENTRY POINT

This service provides the comprehensive intelligent asset management system.
"""

import os
import sys
import io

# Set console encoding to handle Unicode properly
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import and run intelligent service
from intelligent_app import run_intelligent_service, create_intelligent_service

# For compatibility, create app instance
app = create_intelligent_service()

if __name__ == '__main__':
    print("[STARTING] Intelligent Asset Management System...")
    run_intelligent_service()