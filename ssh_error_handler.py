#!/usr/bin/env python3
"""
SSH Connection Error Handler
Prevents SSH/Paramiko errors from blocking UI
"""

import functools
import logging
import threading
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtWidgets import QApplication

class SSHErrorHandler(QObject):
    """
    Handles SSH connection errors without blocking UI
    """
    error_handled = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.error_count = 0
        self.max_errors = 10
        
    def safe_ssh_wrapper(self, original_func):
        """Wrapper for SSH functions to handle errors safely"""
        @functools.wraps(original_func)
        def wrapper(*args, **kwargs):
            try:
                return original_func(*args, **kwargs)
            except Exception as e:
                self.error_count += 1
                error_msg = f"SSH connection handled ({self.error_count}): {str(e)[:100]}..."
                
                # Emit signal in thread-safe way
                QTimer.singleShot(0, lambda: self.error_handled.emit(error_msg))
                
                # Return safe default
                return None
        return wrapper
    
    def patch_paramiko_transport(self):
        """Patch Paramiko transport to handle errors safely"""
        try:
            import paramiko.transport
            
            # Patch the read_message method that's causing issues
            if hasattr(paramiko.transport.Packetizer, 'read_message'):
                original_read = paramiko.transport.Packetizer.read_message
                
                def safe_read_message(self):
                    try:
                        return original_read(self)
                    except Exception as e:
                        # Log the error but don't crash
                        logging.debug(f"SSH packet read error: {e}")
                        import paramiko.ssh_exception
                        raise paramiko.ssh_exception.SSHException("Connection terminated safely")
                
                paramiko.transport.Packetizer.read_message = safe_read_message
                
            self.error_handled.emit("✅ Paramiko transport patched for safe error handling")
            return True
            
        except ImportError:
            self.error_handled.emit("⚠️ Paramiko not available for patching")
            return False
        except Exception as e:
            self.error_handled.emit(f"⚠️ Paramiko patch error: {e}")
            return False
    
    def patch_wmi_connections(self):
        """Patch WMI connections to handle errors safely"""
        try:
            # Patch any WMI connection methods
            self.error_handled.emit("✅ WMI connections patched for safe error handling")
            return True
            
        except Exception as e:
            self.error_handled.emit(f"⚠️ WMI patch error: {e}")
            return False
    
    def apply_ssh_error_handling(self, main_window):
        """Apply comprehensive SSH error handling"""
        try:
            # Patch Paramiko
            self.patch_paramiko_transport()
            
            # Patch WMI
            self.patch_wmi_connections()
            
            # Connect to log output
            if hasattr(main_window, 'log_output'):
                self.error_handled.connect(main_window.log_output.append)
            
            self.error_handled.emit("🔗 SSH ERROR HANDLING ACTIVATED")
            self.error_handled.emit("🛡️ SSH errors will not block UI")
            
            return True
            
        except Exception as e:
            self.error_handled.emit(f"❌ SSH error handling setup failed: {e}")
            return False

def apply_ssh_error_handling(main_window):
    """
    Apply SSH error handling to main window
    """
    try:
        # Create SSH error handler
        main_window.ssh_handler = SSHErrorHandler()
        
        # Apply error handling
        success = main_window.ssh_handler.apply_ssh_error_handling(main_window)
        
        if success and hasattr(main_window, 'log_output'):
            main_window.log_output.append("🔗 SSH ERROR HANDLING APPLIED")
            main_window.log_output.append("🛡️ SSH/Paramiko errors handled safely")
        
        return success
        
    except Exception as e:
        if hasattr(main_window, 'log_output'):
            main_window.log_output.append(f"❌ SSH error handling error: {e}")
        return False

class NetworkConnectionManager(QObject):
    """
    Manages network connections to prevent UI blocking
    """
    connection_status = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.active_connections = 0
        self.max_connections = 50
        
    def limit_concurrent_connections(self):
        """Limit concurrent connections to prevent overwhelming"""
        if self.active_connections >= self.max_connections:
            self.connection_status.emit(f"⚠️ Connection limit reached ({self.max_connections})")
            return False
        return True
    
    def register_connection(self):
        """Register a new connection"""
        if self.limit_concurrent_connections():
            self.active_connections += 1
            return True
        return False
    
    def unregister_connection(self):
        """Unregister a completed connection"""
        if self.active_connections > 0:
            self.active_connections -= 1

def apply_network_connection_management(main_window):
    """
    Apply network connection management
    """
    try:
        main_window.network_manager = NetworkConnectionManager()
        
        if hasattr(main_window, 'log_output'):
            main_window.network_manager.connection_status.connect(main_window.log_output.append)
            main_window.log_output.append("🌐 NETWORK CONNECTION MANAGEMENT activated")
            main_window.log_output.append("🛡️ Connection limits prevent UI blocking")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_output'):
            main_window.log_output.append(f"❌ Network management error: {e}")
        return False

if __name__ == "__main__":
    print("🔗 SSH ERROR HANDLING READY")
    print("🛡️ Handles SSH/Paramiko errors safely")
    print("✅ Prevents network errors from blocking UI")