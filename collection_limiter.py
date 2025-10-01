#!/usr/bin/env python3
"""
Collection Limiter & UI Protector
Prevents massive network scans from hanging the UI
"""

from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtWidgets import QApplication, QMessageBox
import ipaddress
import threading

class CollectionLimiter(QObject):
    """
    Limits collection scope to prevent UI hanging
    """
    scope_limited = pyqtSignal(str)
    collection_stopped = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.max_targets = 50  # Limit to 50 devices max
        self.max_concurrent = 10  # Max 10 concurrent connections
        self.timeout_seconds = 300  # 5 minute timeout
        self.stop_timer = None
        
    def limit_target_scope(self, targets_text):
        """Limit the scope of targets to prevent overload"""
        try:
            if not targets_text.strip():
                return []
            
            # Parse targets
            targets = []
            for target in targets_text.replace(" ", ",").split(","):
                target = target.strip()
                if not target:
                    continue
                    
                # Handle subnet notation
                if "/" in target:
                    try:
                        network = ipaddress.ip_network(target, strict=False)
                        # Limit subnet scans to /24 or smaller
                        if network.prefixlen < 24:
                            self.scope_limited.emit(f"⚠️ Subnet {target} too large - limiting to first /24")
                            # Take only first /24
                            first_subnet = list(network.subnets(new_prefix=24))[0]
                            targets.extend([str(ip) for ip in first_subnet.hosts()][:self.max_targets])
                        else:
                            targets.extend([str(ip) for ip in network.hosts()][:self.max_targets])
                    except ValueError:
                        targets.append(target)
                else:
                    targets.append(target)
                
                # Stop if we hit the limit
                if len(targets) >= self.max_targets:
                    break
            
            # Limit total targets
            if len(targets) > self.max_targets:
                targets = targets[:self.max_targets]
                self.scope_limited.emit(f"🛡️ Limited scan to {self.max_targets} devices to prevent UI hanging")
            
            self.scope_limited.emit(f"📊 Scanning {len(targets)} devices (limited for UI responsiveness)")
            return targets
            
        except Exception as e:
            self.scope_limited.emit(f"❌ Target parsing error: {e}")
            return []
    
    def start_collection_timeout(self):
        """Start timeout timer to prevent infinite hanging"""
        if self.stop_timer:
            self.stop_timer.stop()
        
        self.stop_timer = QTimer()
        self.stop_timer.timeout.connect(self.force_stop_collection)
        self.stop_timer.setSingleShot(True)
        self.stop_timer.start(self.timeout_seconds * 1000)
        
        self.scope_limited.emit(f"⏱️ Collection timeout set: {self.timeout_seconds} seconds")
    
    def force_stop_collection(self):
        """Force stop collection if it runs too long"""
        self.collection_stopped.emit("⏱️ Collection stopped - timeout reached to prevent hanging")
    
    def stop_timeout(self):
        """Stop the timeout timer"""
        if self.stop_timer:
            self.stop_timer.stop()

class UIProtector(QObject):
    """
    Protects UI from hanging during operations
    """
    protection_active = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.keep_alive_timer = QTimer()
        self.keep_alive_timer.timeout.connect(self.force_ui_update)
        
    def activate_protection(self):
        """Activate UI protection"""
        # Force UI updates every 100ms
        self.keep_alive_timer.start(100)
        self.protection_active.emit("🛡️ UI PROTECTION ACTIVATED - forced updates every 100ms")
    
    def deactivate_protection(self):
        """Deactivate UI protection"""
        self.keep_alive_timer.stop()
        self.protection_active.emit("✅ UI protection deactivated")
    
    def force_ui_update(self):
        """Force UI to stay responsive"""
        try:
            QApplication.processEvents()
        except Exception:
            pass

def apply_collection_limiter(main_window):
    """
    Apply collection limiter to main window
    """
    try:
        # Create limiter
        main_window.collection_limiter = CollectionLimiter()
        main_window.ui_protector = UIProtector()
        
        # Connect signals
        if hasattr(main_window, 'log_output'):
            main_window.collection_limiter.scope_limited.connect(main_window.log_output.append)
            main_window.collection_limiter.collection_stopped.connect(main_window.log_output.append)
            main_window.ui_protector.protection_active.connect(main_window.log_output.append)
        
        # Override start_collection to use limiter
        if hasattr(main_window, 'start_collection'):
            original_start = main_window.start_collection
            
            def limited_start_collection():
                """Start collection with limits"""
                try:
                    # Activate UI protection
                    main_window.ui_protector.activate_protection()
                    
                    # Get and limit targets
                    targets_raw = main_window.target_entry.text().strip()
                    if not targets_raw:
                        QMessageBox.warning(main_window, "Missing Targets", "Please enter at least one IP or subnet.")
                        main_window.ui_protector.deactivate_protection()
                        return
                    
                    # Limit scope
                    limited_targets = main_window.collection_limiter.limit_target_scope(targets_raw)
                    if not limited_targets:
                        QMessageBox.warning(main_window, "No Valid Targets", "No valid targets found.")
                        main_window.ui_protector.deactivate_protection()
                        return
                    
                    # Show confirmation for large scans
                    if len(limited_targets) > 20:
                        reply = QMessageBox.question(
                            main_window, 
                            "Large Scan Confirmation",
                            f"Scanning {len(limited_targets)} devices. This may take several minutes.\n\nContinue?",
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                        )
                        if reply != QMessageBox.StandardButton.Yes:
                            main_window.ui_protector.deactivate_protection()
                            return
                    
                    # Update target entry with limited targets
                    main_window.target_entry.setText(",".join(limited_targets[:10]) + "..." if len(limited_targets) > 10 else ",".join(limited_targets))
                    
                    # Start timeout
                    main_window.collection_limiter.start_collection_timeout()
                    
                    # Connect timeout to stop
                    main_window.collection_limiter.collection_stopped.connect(
                        lambda: main_window.stop_collection() if hasattr(main_window, 'stop_collection') else None
                    )
                    
                    # Call original start with limited scope
                    original_start()
                    
                except Exception as e:
                    main_window.log_output.append(f"❌ Limited start error: {e}")
                    main_window.ui_protector.deactivate_protection()
            
            main_window.start_collection = limited_start_collection
        
        # Override stop_collection to cleanup
        if hasattr(main_window, 'stop_collection'):
            original_stop = main_window.stop_collection
            
            def limited_stop_collection():
                """Stop collection with cleanup"""
                try:
                    main_window.collection_limiter.stop_timeout()
                    main_window.ui_protector.deactivate_protection()
                    original_stop()
                except Exception as e:
                    main_window.log_output.append(f"❌ Limited stop error: {e}")
            
            main_window.stop_collection = limited_stop_collection
        
        if hasattr(main_window, 'log_output'):
            main_window.log_output.append("🛡️ COLLECTION LIMITER ACTIVATED")
            main_window.log_output.append(f"📊 Max targets: {main_window.collection_limiter.max_targets}")
            main_window.log_output.append(f"⏱️ Timeout: {main_window.collection_limiter.timeout_seconds}s")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_output'):
            main_window.log_output.append(f"❌ Collection limiter error: {e}")
        return False

if __name__ == "__main__":
    print("🛡️ COLLECTION LIMITER READY")
    print("📊 Prevents massive scans from hanging UI")
    print("⏱️ Includes timeout protection")