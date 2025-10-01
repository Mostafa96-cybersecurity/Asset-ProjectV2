# GUI Package Initialization
"""
GUI package for Asset Management System
Contains all GUI-related modules and enhancements
"""

# Import core GUI modules for easy access
try:
    from .app import *
except ImportError:
    pass

try:
    from .thread_safe_enhancement import *
except ImportError:
    pass

try:
    from .enhanced_app import *
except ImportError:
    pass

__version__ = "1.0.0"
__author__ = "Asset Management System"