#!/usr/bin/env python3
"""
ADVANCED NOTIFICATION SYSTEM

This system provides comprehensive notifications for:
✅ Data collection progress
✅ Device status changes
✅ Duplicate detection alerts
✅ System errors and warnings
✅ Automation status updates
✅ Real-time desktop notifications
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
from datetime import datetime
from typing import Dict, List, Callable, Optional
import queue
import os

class NotificationLevel:
    INFO = "info"
    SUCCESS = "success" 
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AdvancedNotificationSystem:
    def __init__(self, parent_window: tk.Tk = None):
        self.parent_window = parent_window
        self.notifications_queue = queue.Queue()
        self.active_notifications = []
        self.notification_history = []
        self.max_history = 1000
        self.running = False
        
        # Notification settings
        self.settings = {
            'show_desktop_notifications': True,
            'auto_dismiss_time': 10000,  # 10 seconds
            'max_concurrent_notifications': 5,
            'notification_position': 'top_right',
            'sound_enabled': True
        }
        
        # Color schemes for different levels
        self.color_schemes = {
            NotificationLevel.INFO: {
                'bg': '#d1ecf1', 'fg': '#0c5460', 'border': '#bee5eb',
                'icon': 'ℹ️', 'title_color': '#0c5460'
            },
            NotificationLevel.SUCCESS: {
                'bg': '#d4edda', 'fg': '#155724', 'border': '#c3e6cb',
                'icon': '✅', 'title_color': '#155724'
            },
            NotificationLevel.WARNING: {
                'bg': '#fff3cd', 'fg': '#856404', 'border': '#ffeaa7',
                'icon': '⚠️', 'title_color': '#856404'
            },
            NotificationLevel.ERROR: {
                'bg': '#f8d7da', 'fg': '#721c24', 'border': '#f5c6cb',
                'icon': '❌', 'title_color': '#721c24'
            },
            NotificationLevel.CRITICAL: {
                'bg': '#f8d7da', 'fg': '#721c24', 'border': '#dc3545',
                'icon': '🚨', 'title_color': '#721c24'
            }
        }
        
        # Start notification processor
        self.start_notification_processor()
    
    def start_notification_processor(self):
        """Start the notification processing thread"""
        if not self.running:
            self.running = True
            processor_thread = threading.Thread(target=self._process_notifications, daemon=True)
            processor_thread.start()
    
    def stop_notification_processor(self):
        """Stop the notification processing"""
        self.running = False
    
    def notify(self, title: str, message: str, level: str = NotificationLevel.INFO, 
              duration: int = None, callback: Callable = None, data: Dict = None):
        """Add a notification to the queue"""
        notification = {
            'id': f"notif_{int(time.time() * 1000)}_{len(self.notification_history)}",
            'title': title,
            'message': message,
            'level': level,
            'timestamp': datetime.now(),
            'duration': duration or self.settings['auto_dismiss_time'],
            'callback': callback,
            'data': data or {},
            'dismissed': False
        }
        
        # Add to queue and history
        self.notifications_queue.put(notification)
        self.notification_history.append(notification)
        
        # Maintain history limit
        if len(self.notification_history) > self.max_history:
            self.notification_history = self.notification_history[-self.max_history:]
    
    def _process_notifications(self):
        """Process notifications from the queue"""
        while self.running:
            try:
                # Check for new notifications
                try:
                    notification = self.notifications_queue.get(timeout=1)
                    self._show_notification(notification)
                except queue.Empty:
                    continue
                
                # Clean up expired notifications
                self._cleanup_expired_notifications()
                
            except Exception as e:
                print(f"Notification processor error: {e}")
                time.sleep(1)
    
    def _show_notification(self, notification: Dict):
        """Show a notification window"""
        if not self.settings['show_desktop_notifications']:
            return
        
        # Limit concurrent notifications
        if len(self.active_notifications) >= self.settings['max_concurrent_notifications']:
            # Remove oldest notification
            oldest = min(self.active_notifications, key=lambda n: n['show_time'])
            self._dismiss_notification(oldest['window'])
        
        # Schedule notification display on main thread
        if self.parent_window:
            self.parent_window.after(0, lambda: self._create_notification_window(notification))
    
    def _create_notification_window(self, notification: Dict):
        """Create and display notification window"""
        try:
            # Create notification window
            notif_window = tk.Toplevel(self.parent_window) if self.parent_window else tk.Tk()
            notif_window.withdraw()  # Hide initially
            
            # Configure window
            notif_window.title("Asset Management Notification")
            notif_window.resizable(False, False)
            notif_window.attributes('-topmost', True)
            
            # Get color scheme
            colors = self.color_schemes.get(notification['level'], self.color_schemes[NotificationLevel.INFO])
            
            # Create main frame
            main_frame = tk.Frame(notif_window, bg=colors['bg'], relief='solid', borderwidth=2)
            main_frame.pack(fill='both', expand=True, padx=2, pady=2)
            
            # Header frame
            header_frame = tk.Frame(main_frame, bg=colors['bg'])
            header_frame.pack(fill='x', padx=10, pady=(10, 5))
            
            # Icon and title
            icon_label = tk.Label(header_frame, text=colors['icon'], bg=colors['bg'], 
                                 font=('Arial', 14))
            icon_label.pack(side='left')
            
            title_label = tk.Label(header_frame, text=notification['title'], 
                                  bg=colors['bg'], fg=colors['title_color'],
                                  font=('Arial', 11, 'bold'))
            title_label.pack(side='left', padx=(5, 0))
            
            # Timestamp
            timestamp_text = notification['timestamp'].strftime("%H:%M:%S")
            timestamp_label = tk.Label(header_frame, text=timestamp_text,
                                      bg=colors['bg'], fg=colors['fg'],
                                      font=('Arial', 8))
            timestamp_label.pack(side='right')
            
            # Close button
            close_btn = tk.Button(header_frame, text="×", bg=colors['bg'], fg=colors['fg'],
                                 font=('Arial', 12, 'bold'), relief='flat', borderwidth=0,
                                 command=lambda: self._dismiss_notification(notif_window))
            close_btn.pack(side='right', padx=(0, 5))
            
            # Message frame
            message_frame = tk.Frame(main_frame, bg=colors['bg'])
            message_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
            
            # Message text
            message_label = tk.Label(message_frame, text=notification['message'],
                                   bg=colors['bg'], fg=colors['fg'],
                                   font=('Arial', 10), wraplength=350,
                                   justify='left')
            message_label.pack(anchor='w')
            
            # Action buttons (if callback provided)
            if notification['callback']:
                button_frame = tk.Frame(main_frame, bg=colors['bg'])
                button_frame.pack(fill='x', padx=10, pady=(0, 10))
                
                action_btn = tk.Button(button_frame, text="View Details",
                                      command=lambda: notification['callback'](notification),
                                      font=('Arial', 9))
                action_btn.pack(side='right')
            
            # Position window
            self._position_notification_window(notif_window)
            
            # Add to active notifications
            notif_data = {
                'window': notif_window,
                'notification': notification,
                'show_time': time.time()
            }
            self.active_notifications.append(notif_data)
            
            # Show window with animation
            notif_window.deiconify()
            self._animate_notification_in(notif_window)
            
            # Auto-dismiss timer
            if notification['duration'] > 0:
                notif_window.after(notification['duration'], 
                                  lambda: self._dismiss_notification(notif_window))
            
            # Play notification sound
            if self.settings['sound_enabled']:
                self._play_notification_sound(notification['level'])
                
        except Exception as e:
            print(f"Error creating notification window: {e}")
    
    def _position_notification_window(self, window: tk.Toplevel):
        """Position notification window based on settings"""
        window.update_idletasks()
        width = window.winfo_reqwidth()
        height = window.winfo_reqheight()
        
        if self.parent_window:
            parent_x = self.parent_window.winfo_rootx()
            parent_y = self.parent_window.winfo_rooty()
            parent_width = self.parent_window.winfo_width()
            parent_height = self.parent_window.winfo_height()
        else:
            parent_x = 0
            parent_y = 0
            parent_width = window.winfo_screenwidth()
            parent_height = window.winfo_screenheight()
        
        # Calculate position based on setting
        if self.settings['notification_position'] == 'top_right':
            x = parent_x + parent_width - width - 20
            y = parent_y + 20 + (len(self.active_notifications) * (height + 10))
        elif self.settings['notification_position'] == 'top_left':
            x = parent_x + 20
            y = parent_y + 20 + (len(self.active_notifications) * (height + 10))
        elif self.settings['notification_position'] == 'bottom_right':
            x = parent_x + parent_width - width - 20
            y = parent_y + parent_height - height - 20 - (len(self.active_notifications) * (height + 10))
        else:  # bottom_left
            x = parent_x + 20
            y = parent_y + parent_height - height - 20 - (len(self.active_notifications) * (height + 10))
        
        window.geometry(f"{width}x{height}+{x}+{y}")
    
    def _animate_notification_in(self, window: tk.Toplevel):
        """Animate notification entrance"""
        # Simple fade-in effect
        window.attributes('-alpha', 0.0)
        for alpha in [0.1, 0.3, 0.5, 0.7, 0.9, 1.0]:
            window.after(50, lambda a=alpha: window.attributes('-alpha', a))
    
    def _dismiss_notification(self, window: tk.Toplevel):
        """Dismiss a notification window"""
        try:
            # Find and remove from active notifications
            for notif_data in self.active_notifications[:]:
                if notif_data['window'] == window:
                    self.active_notifications.remove(notif_data)
                    notif_data['notification']['dismissed'] = True
                    break
            
            # Destroy window
            if window.winfo_exists():
                window.destroy()
                
        except Exception as e:
            print(f"Error dismissing notification: {e}")
    
    def _cleanup_expired_notifications(self):
        """Clean up expired notification windows"""
        current_time = time.time()
        for notif_data in self.active_notifications[:]:
            try:
                if not notif_data['window'].winfo_exists():
                    self.active_notifications.remove(notif_data)
            except:
                self.active_notifications.remove(notif_data)
    
    def _play_notification_sound(self, level: str):
        """Play notification sound based on level"""
        try:
            if os.name == 'nt':  # Windows
                import winsound
                if level in [NotificationLevel.ERROR, NotificationLevel.CRITICAL]:
                    winsound.MessageBeep(winsound.MB_ICONHAND)
                elif level == NotificationLevel.WARNING:
                    winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                else:
                    winsound.MessageBeep(winsound.MB_ICONASTERISK)
        except:
            pass  # Fail silently if sound not available
    
    def get_notification_history(self, limit: int = 50) -> List[Dict]:
        """Get recent notification history"""
        return self.notification_history[-limit:] if self.notification_history else []
    
    def clear_all_notifications(self):
        """Clear all active notifications"""
        for notif_data in self.active_notifications[:]:
            self._dismiss_notification(notif_data['window'])
    
    def update_settings(self, new_settings: Dict):
        """Update notification settings"""
        self.settings.update(new_settings)

class DataCollectionNotifier:
    """Specialized notifier for data collection events"""
    
    def __init__(self, notification_system: AdvancedNotificationSystem):
        self.notification_system = notification_system
    
    def collection_started(self, device_name: str):
        """Notify collection started"""
        self.notification_system.notify(
            "Data Collection Started",
            f"🔍 Starting comprehensive data collection for {device_name}",
            NotificationLevel.INFO,
            duration=5000
        )
    
    def collection_completed(self, device_name: str, completeness: int, fields_collected: int):
        """Notify collection completed"""
        level = NotificationLevel.SUCCESS if completeness >= 90 else NotificationLevel.WARNING
        self.notification_system.notify(
            "Collection Complete",
            f"✅ {device_name}: {completeness}% complete ({fields_collected} fields collected)",
            level,
            duration=8000
        )
    
    def collection_failed(self, device_name: str, error: str):
        """Notify collection failed"""
        self.notification_system.notify(
            "Collection Failed",
            f"❌ Failed to collect data from {device_name}: {error}",
            NotificationLevel.ERROR,
            duration=15000
        )
    
    def duplicate_detected(self, device_count: int, hostname: str):
        """Notify duplicate devices detected"""
        self.notification_system.notify(
            "Duplicate Devices Detected",
            f"⚠️ Found {device_count} duplicate entries for {hostname}",
            NotificationLevel.WARNING,
            duration=12000
        )
    
    def duplicate_resolved(self, merged_count: int, hostname: str):
        """Notify duplicates resolved"""
        self.notification_system.notify(
            "Duplicates Resolved",
            f"🔄 Merged {merged_count} duplicate entries for {hostname}",
            NotificationLevel.SUCCESS,
            duration=10000
        )
    
    def device_change_detected(self, device_name: str, change_type: str, old_value: str, new_value: str):
        """Notify device change detected"""
        self.notification_system.notify(
            "Device Change Detected",
            f"📈 {device_name}: {change_type} changed from '{old_value}' to '{new_value}'",
            NotificationLevel.INFO,
            duration=10000
        )
    
    def automation_cycle_complete(self, devices_processed: int, errors: int):
        """Notify automation cycle complete"""
        level = NotificationLevel.SUCCESS if errors == 0 else NotificationLevel.WARNING
        self.notification_system.notify(
            "Automation Cycle Complete",
            f"✅ Processed {devices_processed} devices with {errors} errors",
            level,
            duration=8000
        )
    
    def critical_error(self, error_type: str, details: str):
        """Notify critical error"""
        self.notification_system.notify(
            "Critical System Error",
            f"🚨 {error_type}: {details}",
            NotificationLevel.CRITICAL,
            duration=0  # Don't auto-dismiss critical errors
        )

if __name__ == "__main__":
    # Test the notification system
    root = tk.Tk()
    root.title("Notification System Test")
    root.geometry("400x300")
    
    # Create notification system
    notif_system = AdvancedNotificationSystem(root)
    data_notifier = DataCollectionNotifier(notif_system)
    
    # Test buttons
    def test_info():
        data_notifier.collection_started("TEST-PC-001")
    
    def test_success():
        data_notifier.collection_completed("TEST-PC-001", 95, 87)
    
    def test_warning():
        data_notifier.duplicate_detected(3, "TEST-PC-001")
    
    def test_error():
        data_notifier.collection_failed("TEST-PC-001", "Network timeout")
    
    def test_critical():
        data_notifier.critical_error("Database Connection", "Unable to connect to database")
    
    ttk.Button(root, text="Test Info", command=test_info).pack(pady=5)
    ttk.Button(root, text="Test Success", command=test_success).pack(pady=5)
    ttk.Button(root, text="Test Warning", command=test_warning).pack(pady=5)
    ttk.Button(root, text="Test Error", command=test_error).pack(pady=5)
    ttk.Button(root, text="Test Critical", command=test_critical).pack(pady=5)
    
    root.mainloop()