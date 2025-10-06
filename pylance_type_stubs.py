"""
Type stubs for enhanced IDE support
"""
from typing import Optional, Dict, Any, Callable
import sqlite3

# Common type aliases
DatabaseConnection = Optional[sqlite3.Connection]
DeviceData = Dict[str, Any]
ResultCallback = Optional[Callable[[Dict[str, Any]], None]]

# Mock implementations for optional imports
class MockNetworkDeviceDialog:
    """Mock implementation for NetworkDeviceDialog when not available"""
    def __init__(self, *args, **kwargs):
        pass

class MockExcelDBSync:
    """Mock implementation for ExcelDBSync when not available"""
    def __init__(self, *args, **kwargs):
        pass

# Database operation helpers
def safe_db_operation(connection: DatabaseConnection, operation: str) -> bool:
    """Safely execute database operations with proper error handling"""
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        cursor.execute(operation)
        connection.commit()
        return True
    except Exception:
        return False

# Type-safe None handling
def safe_str(value: Optional[str], default: str = "Unknown") -> str:
    """Convert Optional[str] to str safely"""
    return value if value is not None else default

def safe_list(value: Optional[List[Any]], default: Optional[List[Any]] = None) -> List[Any]:
    """Convert Optional[List] to List safely"""
    if default is None:
        default = []
    return value if value is not None else default
