# -*- coding: utf-8 -*-
"""
Real-time Error Monitor and Data Quality Dashboard
-------------------------------------------------
- Live monitoring of data collection errors
- Duplicate detection and resolution statistics  
- Data validation and quality metrics
- Automatic error recovery suggestions
- Performance optimization insights
"""

import threading
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from collections import defaultdict, deque
from PyQt6.QtCore import QTimer, QObject, pyqtSignal
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTextEdit, QProgressBar, QGroupBox,
                             QFrame, QScrollArea, QTabWidget)
from PyQt6.QtGui import QFont, QPalette, QColor
from PyQt6.QtCore import Qt

from core.advanced_duplicate_manager import DuplicateManager, DataValidator, ErrorRecovery
from db.connection import connect

log = logging.getLogger(__name__)


class ErrorMonitor(QObject):
    """Real-time error monitoring and statistics"""
    
    # Signals for UI updates
    stats_updated = pyqtSignal(dict)
    error_logged = pyqtSignal(str, str, str)  # timestamp, level, message
    quality_changed = pyqtSignal(float)  # quality score 0-100
    
    def __init__(self):
        super().__init__()
        
        # Error tracking
        self.error_log = deque(maxlen=1000)  # Keep last 1000 errors
        self.error_stats = defaultdict(int)
        
        # Performance metrics
        self.performance_metrics = {
            'total_devices_processed': 0,
            'successful_collections': 0,
            'duplicate_devices_found': 0,
            'duplicate_resolutions': 0,
            'validation_errors': 0,
            'validation_fixes': 0,
            'network_timeouts': 0,
            'database_errors': 0,
            'excel_errors': 0,
            'sync_failures': 0,
            'quality_score': 100.0
        }
        
        # Quality thresholds
        self.quality_thresholds = {
            'excellent': 95.0,
            'good': 85.0,
            'fair': 70.0,
            'poor': 50.0
        }
        
        # Start monitoring
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
    
    def log_error(self, level: str, message: str, category: str = 'general'):
        """Log an error with categorization"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        error_entry = {
            'timestamp': timestamp,
            'level': level,
            'message': message,
            'category': category
        }
        
        self.error_log.append(error_entry)
        self.error_stats[category] += 1
        
        # Update performance metrics
        if category == 'duplicate':
            self.performance_metrics['duplicate_devices_found'] += 1
        elif category == 'validation':
            self.performance_metrics['validation_errors'] += 1
        elif category == 'network':
            self.performance_metrics['network_timeouts'] += 1
        elif category == 'database':
            self.performance_metrics['database_errors'] += 1
        elif category == 'excel':
            self.performance_metrics['excel_errors'] += 1
        elif category == 'sync':
            self.performance_metrics['sync_failures'] += 1
        
        # Emit signal for UI update
        self.error_logged.emit(timestamp, level, message)
        
        # Recalculate quality score
        self._update_quality_score()
        
        log.debug(f"Error logged: [{level}] {category} - {message}")
    
    def log_success(self, category: str, details: str = ''):
        """Log successful operations"""
        if category == 'collection':
            self.performance_metrics['successful_collections'] += 1
        elif category == 'duplicate_resolution':
            self.performance_metrics['duplicate_resolutions'] += 1
        elif category == 'validation_fix':
            self.performance_metrics['validation_fixes'] += 1
        
        self.performance_metrics['total_devices_processed'] += 1
        self._update_quality_score()
    
    def _update_quality_score(self):
        """Calculate data quality score based on success/error ratios"""
        total = self.performance_metrics['total_devices_processed']
        if total == 0:
            quality = 100.0
        else:
            errors = (
                self.performance_metrics['validation_errors'] +
                self.performance_metrics['network_timeouts'] +
                self.performance_metrics['database_errors'] +
                self.performance_metrics['excel_errors'] +
                self.performance_metrics['sync_failures']
            )
            
            success_rate = (total - errors) / total
            quality = max(0.0, min(100.0, success_rate * 100))
        
        self.performance_metrics['quality_score'] = quality
        self.quality_changed.emit(quality)
    
    def get_recent_errors(self, minutes: int = 60) -> List[Dict]:
        """Get errors from the last N minutes"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        recent_errors = []
        for error in self.error_log:
            error_time = datetime.strptime(error['timestamp'], '%Y-%m-%d %H:%M:%S')
            if error_time >= cutoff_time:
                recent_errors.append(error)
        
        return recent_errors
    
    def get_stats(self) -> Dict:
        """Get comprehensive statistics"""
        stats = self.performance_metrics.copy()
        stats['error_categories'] = dict(self.error_stats)
        stats['recent_errors'] = len(self.get_recent_errors(60))
        return stats
    
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self._monitoring:
            try:
                # Emit stats update every 5 seconds
                self.stats_updated.emit(self.get_stats())
                time.sleep(5)
            except Exception as e:
                log.error(f"Monitor loop error: {e}")
                time.sleep(10)
    
    def stop_monitoring(self):
        """Stop the monitoring thread"""
        self._monitoring = False


class DataQualityDashboard(QWidget):
    """Real-time data quality and error prevention dashboard"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.error_monitor = ErrorMonitor()
        self.duplicate_manager = DuplicateManager()
        self.data_validator = DataValidator()
        self.error_recovery = ErrorRecovery()
        
        # UI update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_ui)
        self.update_timer.start(2000)  # Update every 2 seconds
        
        # Connect signals
        self.error_monitor.stats_updated.connect(self._on_stats_updated)
        self.error_monitor.error_logged.connect(self._on_error_logged)
        self.error_monitor.quality_changed.connect(self._on_quality_changed)
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the dashboard UI"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("🛡️ Data Quality & Error Prevention Dashboard")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #2C3E50; margin: 10px;")
        layout.addWidget(title)
        
        # Create tabs for different views
        tab_widget = QTabWidget()
        
        # Tab 1: Real-time Monitoring
        monitoring_tab = self._create_monitoring_tab()
        tab_widget.addTab(monitoring_tab, "📊 Live Monitor")
        
        # Tab 2: Error Management
        error_tab = self._create_error_tab()
        tab_widget.addTab(error_tab, "⚠️ Error Log")
        
        # Tab 3: Quality Metrics
        quality_tab = self._create_quality_tab()
        tab_widget.addTab(quality_tab, "📈 Quality Metrics")
        
        # Tab 4: Recovery Tools
        recovery_tab = self._create_recovery_tab()
        tab_widget.addTab(recovery_tab, "🔧 Recovery Tools")
        
        layout.addWidget(tab_widget)
        self.setLayout(layout)
    
    def _create_monitoring_tab(self) -> QWidget:
        """Create real-time monitoring tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Statistics grid
        stats_frame = QFrame()
        stats_frame.setFrameStyle(QFrame.Shape.Box)
        stats_layout = QVBoxLayout()
        
        # Quality score (prominent display)
        quality_layout = QHBoxLayout()
        self.quality_label = QLabel("Data Quality: 100%")
        self.quality_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.quality_label.setStyleSheet("color: #27AE60; padding: 10px;")
        quality_layout.addWidget(self.quality_label)
        
        self.quality_bar = QProgressBar()
        self.quality_bar.setRange(0, 100)
        self.quality_bar.setValue(100)
        self.quality_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #BDC3C7;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #27AE60;
                border-radius: 6px;
            }
        """)
        quality_layout.addWidget(self.quality_bar)
        stats_layout.addLayout(quality_layout)
        
        # Key metrics
        metrics_layout = QHBoxLayout()
        
        self.devices_processed_label = QLabel("Devices: 0")
        self.devices_processed_label.setStyleSheet("font-weight: bold; color: #3498DB;")
        metrics_layout.addWidget(self.devices_processed_label)
        
        self.duplicates_label = QLabel("Duplicates: 0")
        self.duplicates_label.setStyleSheet("font-weight: bold; color: #E67E22;")
        metrics_layout.addWidget(self.duplicates_label)
        
        self.errors_label = QLabel("Errors: 0")
        self.errors_label.setStyleSheet("font-weight: bold; color: #E74C3C;")
        metrics_layout.addWidget(self.errors_label)
        
        self.success_rate_label = QLabel("Success: 100%")
        self.success_rate_label.setStyleSheet("font-weight: bold; color: #27AE60;")
        metrics_layout.addWidget(self.success_rate_label)
        
        stats_layout.addLayout(metrics_layout)
        stats_frame.setLayout(stats_layout)
        layout.addWidget(stats_frame)
        
        # Live error feed
        self.live_errors = QTextEdit()
        self.live_errors.setMaximumHeight(200)
        self.live_errors.setStyleSheet("""
            QTextEdit {
                background-color: #2C3E50;
                color: #ECF0F1;
                border: 1px solid #34495E;
                border-radius: 4px;
                font-family: 'Consolas', monospace;
                font-size: 11px;
            }
        """)
        layout.addWidget(QLabel("Live Error Feed:"))
        layout.addWidget(self.live_errors)
        
        widget.setLayout(layout)
        return widget
    
    def _create_error_tab(self) -> QWidget:
        """Create error management tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Error controls
        controls_layout = QHBoxLayout()
        
        clear_btn = QPushButton("Clear Error Log")
        clear_btn.clicked.connect(self._clear_error_log)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #C0392B; }
        """)
        controls_layout.addWidget(clear_btn)
        
        export_btn = QPushButton("Export Error Report")
        export_btn.clicked.connect(self._export_error_report)
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #2980B9; }
        """)
        controls_layout.addWidget(export_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Detailed error log
        self.detailed_errors = QTextEdit()
        self.detailed_errors.setStyleSheet("""
            QTextEdit {
                background-color: #FFFFFF;
                border: 1px solid #BDC3C7;
                border-radius: 4px;
                font-family: 'Consolas', monospace;
                font-size: 10px;
            }
        """)
        layout.addWidget(self.detailed_errors)
        
        widget.setLayout(layout)
        return widget
    
    def _create_quality_tab(self) -> QWidget:
        """Create quality metrics tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Quality breakdown
        layout.addWidget(QLabel("Quality Metrics Breakdown:"))
        
        self.quality_breakdown = QTextEdit()
        self.quality_breakdown.setMaximumHeight(150)
        self.quality_breakdown.setReadOnly(True)
        layout.addWidget(self.quality_breakdown)
        
        # Recommendations
        layout.addWidget(QLabel("Quality Improvement Recommendations:"))
        
        self.recommendations = QTextEdit()
        self.recommendations.setReadOnly(True)
        self.recommendations.setStyleSheet("""
            QTextEdit {
                background-color: #F8F9FA;
                border: 1px solid #E9ECEF;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.recommendations)
        
        widget.setLayout(layout)
        return widget
    
    def _create_recovery_tab(self) -> QWidget:
        """Create recovery tools tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Recovery tools
        tools_layout = QVBoxLayout()
        
        # Data validation
        validate_btn = QPushButton("🔍 Run Full Data Validation")
        validate_btn.clicked.connect(self._run_full_validation)
        validate_btn.setStyleSheet(self._get_tool_button_style("#3498DB"))
        tools_layout.addWidget(validate_btn)
        
        # Duplicate cleanup
        cleanup_btn = QPushButton("🧹 Clean Up Duplicates")
        cleanup_btn.clicked.connect(self._cleanup_duplicates)
        cleanup_btn.setStyleSheet(self._get_tool_button_style("#E67E22"))
        tools_layout.addWidget(cleanup_btn)
        
        # Database repair
        repair_btn = QPushButton("🔧 Repair Database Integrity")
        repair_btn.clicked.connect(self._repair_database)
        repair_btn.setStyleSheet(self._get_tool_button_style("#9B59B6"))
        tools_layout.addWidget(repair_btn)
        
        # Reset statistics
        reset_btn = QPushButton("🔄 Reset Statistics")
        reset_btn.clicked.connect(self._reset_statistics)
        reset_btn.setStyleSheet(self._get_tool_button_style("#95A5A6"))
        tools_layout.addWidget(reset_btn)
        
        layout.addLayout(tools_layout)
        
        # Recovery log
        layout.addWidget(QLabel("Recovery Operations Log:"))
        
        self.recovery_log = QTextEdit()
        self.recovery_log.setReadOnly(True)
        self.recovery_log.setMaximumHeight(200)
        layout.addWidget(self.recovery_log)
        
        widget.setLayout(layout)
        return widget
    
    def _get_tool_button_style(self, color: str) -> str:
        """Get consistent button styling"""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                margin: 4px;
            }}
            QPushButton:hover {{
                background-color: {color}DD;
            }}
        """
    
    # Event handlers
    def _on_stats_updated(self, stats: Dict):
        """Handle statistics update"""
        try:
            # Update devices processed
            self.devices_processed_label.setText(f"Devices: {stats.get('total_devices_processed', 0)}")
            
            # Update duplicates
            duplicates = stats.get('duplicate_devices_found', 0)
            self.duplicates_label.setText(f"Duplicates: {duplicates}")
            
            # Update errors
            total_errors = (
                stats.get('validation_errors', 0) +
                stats.get('network_timeouts', 0) +
                stats.get('database_errors', 0) +
                stats.get('excel_errors', 0) +
                stats.get('sync_failures', 0)
            )
            self.errors_label.setText(f"Errors: {total_errors}")
            
            # Update success rate
            total = stats.get('total_devices_processed', 0)
            if total > 0:
                success_rate = ((total - total_errors) / total) * 100
                self.success_rate_label.setText(f"Success: {success_rate:.1f}%")
            
        except Exception as e:
            log.error(f"Error updating stats display: {e}")
    
    def _on_error_logged(self, timestamp: str, level: str, message: str):
        """Handle new error log entry"""
        try:
            # Add to live feed
            color = "#E74C3C" if level == "ERROR" else "#F39C12" if level == "WARNING" else "#3498DB"
            html = f'<span style="color: {color};">[{timestamp}] {level}: {message}</span><br>'
            
            self.live_errors.insertHtml(html)
            
            # Auto-scroll to bottom
            cursor = self.live_errors.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.live_errors.setTextCursor(cursor)
            
            # Update detailed log
            self.detailed_errors.append(f"[{timestamp}] {level}: {message}")
            
        except Exception as e:
            log.error(f"Error updating error display: {e}")
    
    def _on_quality_changed(self, quality: float):
        """Handle quality score change"""
        try:
            self.quality_label.setText(f"Data Quality: {quality:.1f}%")
            self.quality_bar.setValue(int(quality))
            
            # Update color based on quality
            if quality >= 95:
                color = "#27AE60"  # Green
            elif quality >= 85:
                color = "#F39C12"  # Orange
            elif quality >= 70:
                color = "#E67E22"  # Dark orange
            else:
                color = "#E74C3C"  # Red
            
            self.quality_label.setStyleSheet(f"color: {color}; padding: 10px; font-weight: bold;")
            
            # Update progress bar color
            self.quality_bar.setStyleSheet(f"""
                QProgressBar {{
                    border: 2px solid #BDC3C7;
                    border-radius: 8px;
                    text-align: center;
                    font-weight: bold;
                }}
                QProgressBar::chunk {{
                    background-color: {color};
                    border-radius: 6px;
                }}
            """)
            
        except Exception as e:
            log.error(f"Error updating quality display: {e}")
    
    # Tool actions
    def _clear_error_log(self):
        """Clear all error logs"""
        self.error_monitor.error_log.clear()
        self.error_monitor.error_stats.clear()
        self.live_errors.clear()
        self.detailed_errors.clear()
        self.recovery_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Error log cleared")
    
    def _export_error_report(self):
        """Export detailed error report"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"error_report_{timestamp}.txt"
            
            with open(filename, 'w') as f:
                f.write(f"Error Report Generated: {datetime.now()}\n")
                f.write("=" * 50 + "\n\n")
                
                stats = self.error_monitor.get_stats()
                f.write("STATISTICS:\n")
                for key, value in stats.items():
                    f.write(f"  {key}: {value}\n")
                
                f.write("\n\nDETAILED ERRORS:\n")
                for error in self.error_monitor.error_log:
                    f.write(f"[{error['timestamp']}] {error['level']}: {error['message']}\n")
            
            self.recovery_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Error report exported: {filename}")
            
        except Exception as e:
            log.error(f"Error exporting report: {e}")
    
    def _run_full_validation(self):
        """Run comprehensive data validation"""
        self.recovery_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Starting full data validation...")
        # Implementation would validate all database records
        # This is a placeholder for the actual validation logic
    
    def _cleanup_duplicates(self):
        """Clean up duplicate entries"""
        self.recovery_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Starting duplicate cleanup...")
        # Implementation would clean up duplicates in database
    
    def _repair_database(self):
        """Repair database integrity"""
        self.recovery_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Starting database repair...")
        # Implementation would repair database issues
    
    def _reset_statistics(self):
        """Reset all statistics"""
        self.error_monitor.performance_metrics = {
            'total_devices_processed': 0,
            'successful_collections': 0,
            'duplicate_devices_found': 0,
            'duplicate_resolutions': 0,
            'validation_errors': 0,
            'validation_fixes': 0,
            'network_timeouts': 0,
            'database_errors': 0,
            'excel_errors': 0,
            'sync_failures': 0,
            'quality_score': 100.0
        }
        self.recovery_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Statistics reset")
    
    def _update_ui(self):
        """Periodic UI updates"""
        try:
            # Update quality breakdown
            stats = self.error_monitor.get_stats()
            quality = stats.get('quality_score', 100.0)
            
            breakdown = f"""
Quality Score: {quality:.1f}%

Breakdown:
• Total Devices Processed: {stats.get('total_devices_processed', 0)}
• Successful Collections: {stats.get('successful_collections', 0)}
• Validation Errors: {stats.get('validation_errors', 0)}
• Network Timeouts: {stats.get('network_timeouts', 0)}
• Database Errors: {stats.get('database_errors', 0)}
• Excel Errors: {stats.get('excel_errors', 0)}
• Sync Failures: {stats.get('sync_failures', 0)}

Recent Activity:
• Errors in last hour: {len(self.error_monitor.get_recent_errors(60))}
• Duplicates resolved: {stats.get('duplicate_resolutions', 0)}
• Validation fixes: {stats.get('validation_fixes', 0)}
            """
            
            self.quality_breakdown.setText(breakdown.strip())
            
            # Generate recommendations
            recommendations = self._generate_recommendations(stats)
            self.recommendations.setText(recommendations)
            
        except Exception as e:
            log.error(f"Error updating UI: {e}")
    
    def _generate_recommendations(self, stats: Dict) -> str:
        """Generate quality improvement recommendations"""
        recommendations = []
        
        quality = stats.get('quality_score', 100.0)
        
        if quality < 70:
            recommendations.append("🔴 CRITICAL: Data quality is below acceptable levels")
            recommendations.append("   → Consider reviewing network connectivity and credentials")
            recommendations.append("   → Run full data validation and repair operations")
        
        if stats.get('validation_errors', 0) > 10:
            recommendations.append("⚠️  High number of validation errors detected")
            recommendations.append("   → Review data collection sources for accuracy")
            recommendations.append("   → Consider updating validation rules")
        
        if stats.get('network_timeouts', 0) > 5:
            recommendations.append("🌐 Network connectivity issues detected")
            recommendations.append("   → Check network stability and firewall settings")
            recommendations.append("   → Consider adjusting timeout values")
        
        if stats.get('duplicate_devices_found', 0) > stats.get('duplicate_resolutions', 0):
            recommendations.append("🔄 Unresolved duplicate devices found")
            recommendations.append("   → Run duplicate cleanup to resolve conflicts")
            recommendations.append("   → Review device identification logic")
        
        if not recommendations:
            recommendations.append("✅ System is operating within normal parameters")
            recommendations.append("   → Continue monitoring for optimal performance")
            recommendations.append("   → Regular maintenance recommended")
        
        return "\n".join(recommendations)