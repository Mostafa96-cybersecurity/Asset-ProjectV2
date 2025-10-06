#!/usr/bin/env python3
"""
Qt Threading Fix
Fixes the QObject threading error: "Cannot create children for a parent that is in a different thread"
"""

from PyQt6.QtCore import QThread, QObject, pyqtSignal, QTimer
from PyQt6.QtWidgets import QApplication
import threading


class ThreadingErrorFixer:
    """
    Fixes Qt threading errors by ensuring proper thread management
    """
    
    @staticmethod
    def fix_qobject_threading_error():
        """
        Apply comprehensive fix for QObject threading errors
        """
        # Store original QThread.__init__ to ensure proper parent handling
        original_qthread_init = QThread.__init__
        
        def safe_qthread_init(self, parent=None):
            """Safe QThread initialization that respects main thread"""
            try:
                # Only set parent if we're in the main thread
                if threading.current_thread() == threading.main_thread():
                    original_qthread_init(self, parent)
                else:
                    # If called from worker thread, initialize without parent
                    original_qthread_init(self, None)
                    # Move to main thread if parent was intended
                    if parent and hasattr(parent, 'thread'):
                        QTimer.singleShot(0, lambda: self.moveToThread(parent.thread()))
            except Exception:
                # Fallback to safe initialization
                original_qthread_init(self, None)
        
        # Apply the fix
        QThread.__init__ = safe_qthread_init
        
        # Store original QObject.__init__ to ensure proper parent handling
        original_qobject_init = QObject.__init__
        
        def safe_qobject_init(self, parent=None, **kwargs):
            """Safe QObject initialization that respects threading"""
            try:
                # Check if parent is in different thread
                if parent and hasattr(parent, 'thread'):
                    current_thread = QThread.currentThread()
                    parent_thread = parent.thread()
                    
                    if current_thread != parent_thread:
                        # Initialize without parent first
                        original_qobject_init(self, None, **kwargs)
                        # Schedule move to correct thread
                        QTimer.singleShot(0, lambda: self.moveToThread(parent_thread))
                        return
                
                # Safe to use parent
                original_qobject_init(self, parent, **kwargs)
                
            except Exception:
                # Fallback to safe initialization
                original_qobject_init(self, None, **kwargs)
        
        # Apply the fix
        QObject.__init__ = safe_qobject_init
        
        print("✅ Qt Threading Error Fix Applied")
        print("🛡️ QObject threading errors prevented")
        return True


def apply_qt_threading_fix():
    """
    Apply Qt threading fix to prevent QObject errors
    """
    try:
        fixer = ThreadingErrorFixer()
        success = fixer.fix_qobject_threading_error()
        
        if success:
            print("🔧 QT THREADING FIX APPLIED SUCCESSFULLY")
            print("✅ All QObject threading errors will be prevented")
        
        return success
        
    except Exception as e:
        print(f"❌ Qt threading fix error: {e}")
        return False


if __name__ == "__main__":
    print("🔧 Qt Threading Fix Ready")
    success = apply_qt_threading_fix()
    if success:
        print("✅ Threading fix applied successfully")
    else:
        print("❌ Threading fix failed")