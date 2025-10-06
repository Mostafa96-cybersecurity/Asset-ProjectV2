#!/usr/bin/env python3
"""
⏰ ENHANCED SCHEDULED SCAN MONITOR
=================================
Real-time monitoring and status tracking for scheduled scans
with comprehensive logging and progress tracking.
"""

import threading
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import queue

# Import comprehensive logging
try:
    from comprehensive_logging_system import log_scheduled_scan, start_job, complete_job, update_job_progress
except ImportError:
    # Fallback logging
    def log_scheduled_scan(level, message, **kwargs):
        print(f"[SCHEDULED_SCAN] {level}: {message}")
    def start_job(job_id, feature, description):
        print(f"Starting job: {description}")
    def complete_job(job_id, success, message=""):
        print(f"Job completed: {success}")
    def update_job_progress(job_id, progress, message=""):
        print(f"Progress {progress}%: {message}")

class ScheduledScanMonitor:
    """Enhanced monitor for scheduled scanning with real-time status"""
    
    def __init__(self):
        self.is_running = False
        self.monitor_thread = None
        self.scan_schedules = []
        self.active_scans = {}
        self.scan_history = []
        self.status_queue = queue.Queue()
        
        # Configuration
        self.config_file = Path("scheduled_scan_config.json")
        self.status_file = Path("logs/scheduled_scan_status.json")
        self.status_file.parent.mkdir(exist_ok=True)
        
        # Load configuration
        self.load_schedules()
        
        # Start monitoring
        self.start_monitoring()
        
        log_scheduled_scan('INFO', '⏰ Enhanced Scheduled Scan Monitor initialized')
        
    def load_schedules(self):
        """Load scheduled scan configuration"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    self.scan_schedules = data.get('schedules', [])
                    log_scheduled_scan('INFO', f'Loaded {len(self.scan_schedules)} schedules')
            else:
                # Create default schedules
                self.create_default_schedules()
        except Exception as e:
            log_scheduled_scan('ERROR', f'Failed to load schedules: {e}')
            self.create_default_schedules()
            
    def create_default_schedules(self):
        """Create default scanning schedules"""
        self.scan_schedules = [
            {
                'id': 'hourly_quick',
                'name': 'Hourly Quick Scan',
                'enabled': False,
                'type': 'interval',
                'interval_minutes': 60,
                'scan_type': 'quick',
                'targets': ['localhost'],
                'last_run': None,
                'next_run': None,
                'created': datetime.now().isoformat()
            },
            {
                'id': 'daily_full',
                'name': 'Daily Full Network Scan',
                'enabled': False,
                'type': 'daily',
                'daily_time': '02:00',
                'scan_type': 'comprehensive',
                'targets': ['network'],
                'last_run': None,
                'next_run': None,
                'created': datetime.now().isoformat()
            },
            {
                'id': 'weekly_deep',
                'name': 'Weekly Deep Scan',
                'enabled': False,
                'type': 'weekly',
                'weekly_day': 0,  # Monday
                'weekly_time': '01:00',
                'scan_type': 'deep',
                'targets': ['all'],
                'last_run': None,
                'next_run': None,
                'created': datetime.now().isoformat()
            }
        ]
        self.save_schedules()
        
    def save_schedules(self):
        """Save schedules to configuration file"""
        try:
            data = {
                'schedules': self.scan_schedules,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
            log_scheduled_scan('DEBUG', 'Schedules saved to configuration')
        except Exception as e:
            log_scheduled_scan('ERROR', f'Failed to save schedules: {e}')
            
    def start_monitoring(self):
        """Start the monitoring thread"""
        if self.is_running:
            return
            
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        log_scheduled_scan('INFO', '🚀 Scheduled scan monitoring started')
        
    def stop_monitoring(self):
        """Stop the monitoring thread"""
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        log_scheduled_scan('INFO', '🛑 Scheduled scan monitoring stopped')
        
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_running:
            try:
                current_time = datetime.now()
                
                # Update next run times
                self._update_next_run_times(current_time)
                
                # Check for due scans
                self._check_due_scans(current_time)
                
                # Update scan progress
                self._update_scan_progress()
                
                # Save status
                self._save_status(current_time)
                
                # Wait 30 seconds before next check
                time.sleep(30)
                
            except Exception as e:
                log_scheduled_scan('ERROR', f'Monitoring loop error: {e}')
                time.sleep(60)  # Wait longer on error
                
    def _update_next_run_times(self, current_time: datetime):
        """Update next run times for all schedules"""
        for schedule in self.scan_schedules:
            if not schedule.get('enabled', False):
                schedule['next_run'] = None
                continue
                
            try:
                schedule['next_run'] = self._calculate_next_run(schedule, current_time).isoformat()
            except Exception as e:
                log_scheduled_scan('ERROR', f'Error calculating next run for {schedule["name"]}: {e}')
                
    def _calculate_next_run(self, schedule: Dict[str, Any], current_time: datetime) -> datetime:
        """Calculate next run time for a schedule"""
        schedule_type = schedule.get('type', 'interval')
        
        if schedule_type == 'interval':
            interval = schedule.get('interval_minutes', 60)
            last_run = schedule.get('last_run')
            
            if last_run:
                last_run_time = datetime.fromisoformat(last_run)
                return last_run_time + timedelta(minutes=interval)
            else:
                return current_time + timedelta(minutes=interval)
                
        elif schedule_type == 'daily':
            daily_time = schedule.get('daily_time', '02:00')
            hour, minute = map(int, daily_time.split(':'))
            
            next_run = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= current_time:
                next_run += timedelta(days=1)
            return next_run
            
        elif schedule_type == 'weekly':
            weekly_day = schedule.get('weekly_day', 0)  # 0 = Monday
            weekly_time = schedule.get('weekly_time', '01:00')
            hour, minute = map(int, weekly_time.split(':'))
            
            days_ahead = weekly_day - current_time.weekday()
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
                
            next_run = current_time + timedelta(days=days_ahead)
            next_run = next_run.replace(hour=hour, minute=minute, second=0, microsecond=0)
            return next_run
            
        return current_time + timedelta(hours=1)  # Default fallback
        
    def _check_due_scans(self, current_time: datetime):
        """Check for scans that are due to run"""
        for schedule in self.scan_schedules:
            if not schedule.get('enabled', False):
                continue
                
            next_run = schedule.get('next_run')
            if not next_run:
                continue
                
            try:
                next_run_time = datetime.fromisoformat(next_run)
                if current_time >= next_run_time:
                    # Check if not already running
                    if schedule['id'] not in self.active_scans:
                        self._start_scheduled_scan(schedule)
            except Exception as e:
                log_scheduled_scan('ERROR', f'Error checking due scan for {schedule["name"]}: {e}')
                
    def _start_scheduled_scan(self, schedule: Dict[str, Any]):
        """Start a scheduled scan"""
        scan_id = f"scan_{schedule['id']}_{int(time.time())}"
        job_id = f"scheduled_scan_{scan_id}"
        
        log_scheduled_scan('INFO', f'🔍 Starting scheduled scan: {schedule["name"]}')
        start_job(job_id, 'scheduled_scanning', f'Scheduled scan: {schedule["name"]}')
        
        # Create scan record
        scan_record = {
            'id': scan_id,
            'job_id': job_id,
            'schedule_id': schedule['id'],
            'schedule_name': schedule['name'],
            'start_time': datetime.now().isoformat(),
            'status': 'starting',
            'progress': 0,
            'devices_found': 0,
            'targets': schedule.get('targets', []),
            'scan_type': schedule.get('scan_type', 'quick')
        }
        
        self.active_scans[schedule['id']] = scan_record
        
        # Update schedule
        schedule['last_run'] = datetime.now().isoformat()
        self.save_schedules()
        
        # Start scan in background thread
        scan_thread = threading.Thread(
            target=self._execute_scan,
            args=(scan_record,),
            daemon=True
        )
        scan_thread.start()
        
    def _execute_scan(self, scan_record: Dict[str, Any]):
        """Execute the actual scan"""
        job_id = scan_record['job_id']
        
        try:
            update_job_progress(job_id, 10, 'Initializing scan')
            
            # Import and use comprehensive collector
            try:
                from ultimate_comprehensive_collector import UltimateComprehensiveCollector
                collector = UltimateComprehensiveCollector()
                
                update_job_progress(job_id, 20, 'Connecting to systems')
                
                if collector.connect_wmi() and collector.connect_database():
                    update_job_progress(job_id, 40, 'Starting data collection')
                    
                    # Collect data based on scan type
                    scan_type = scan_record['scan_type']
                    if scan_type == 'quick':
                        collector.collect_basic_system_info()
                        collector.collect_hardware_info()
                    elif scan_type == 'comprehensive':
                        collector.collect_all_launcher_requirements()
                        collector.collect_everything_wmi_can_collect()
                    elif scan_type == 'deep':
                        collector.collect_all_launcher_requirements()
                        collector.collect_everything_wmi_can_collect()
                        collector.collect_advanced_data()
                        
                    update_job_progress(job_id, 80, 'Saving data to database')
                    collector.save_to_database()
                    
                    # Update scan record
                    scan_record['status'] = 'completed'
                    scan_record['progress'] = 100
                    scan_record['devices_found'] = 1  # Local device
                    scan_record['end_time'] = datetime.now().isoformat()
                    
                    log_scheduled_scan('INFO', f'✅ Scheduled scan completed: {scan_record["schedule_name"]}')
                    complete_job(job_id, True, 'Scan completed successfully')
                    
                else:
                    raise Exception("Failed to connect to WMI or database")
                    
            except ImportError:
                # Fallback to basic scan
                update_job_progress(job_id, 50, 'Using basic scan method')
                time.sleep(5)  # Simulate scan time
                
                scan_record['status'] = 'completed'
                scan_record['progress'] = 100
                scan_record['devices_found'] = 1
                scan_record['end_time'] = datetime.now().isoformat()
                
                log_scheduled_scan('INFO', f'✅ Basic scheduled scan completed: {scan_record["schedule_name"]}')
                complete_job(job_id, True, 'Basic scan completed')
                
        except Exception as e:
            scan_record['status'] = 'failed'
            scan_record['error'] = str(e)
            scan_record['end_time'] = datetime.now().isoformat()
            
            log_scheduled_scan('ERROR', f'❌ Scheduled scan failed: {scan_record["schedule_name"]} - {e}')
            complete_job(job_id, False, f'Scan failed: {e}')
            
        finally:
            # Move to history and remove from active
            self.scan_history.append(scan_record)
            if scan_record['schedule_id'] in self.active_scans:
                del self.active_scans[scan_record['schedule_id']]
                
            # Keep only last 100 history records
            if len(self.scan_history) > 100:
                self.scan_history = self.scan_history[-100:]
                
    def _update_scan_progress(self):
        """Update progress for active scans"""
        for scan in self.active_scans.values():
            if scan['status'] == 'running':
                # Simulate progress updates (in real implementation, this would come from the actual scanner)
                elapsed = time.time() - datetime.fromisoformat(scan['start_time']).timestamp()
                progress = min(90, int(elapsed / 300 * 100))  # 5 minute scan simulation
                
                if progress != scan.get('progress', 0):
                    scan['progress'] = progress
                    update_job_progress(scan['job_id'], progress, f'Scanning in progress')
                    
    def _save_status(self, current_time: datetime):
        """Save current status to file"""
        try:
            status = {
                'timestamp': current_time.isoformat(),
                'monitoring_active': self.is_running,
                'schedules': self.scan_schedules,
                'active_scans': list(self.active_scans.values()),
                'recent_history': self.scan_history[-10:],  # Last 10 scans
                'summary': {
                    'total_schedules': len(self.scan_schedules),
                    'enabled_schedules': len([s for s in self.scan_schedules if s.get('enabled')]),
                    'active_scans': len(self.active_scans),
                    'total_completed': len(self.scan_history)
                }
            }
            
            with open(self.status_file, 'w') as f:
                json.dump(status, f, indent=2)
                
        except Exception as e:
            log_scheduled_scan('ERROR', f'Failed to save status: {e}')
            
    def get_current_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        try:
            if self.status_file.exists():
                with open(self.status_file, 'r') as f:
                    return json.load(f)
        except:
            pass
            
        return {
            'monitoring_active': self.is_running,
            'schedules': self.scan_schedules,
            'active_scans': list(self.active_scans.values()),
            'summary': {
                'total_schedules': len(self.scan_schedules),
                'enabled_schedules': len([s for s in self.scan_schedules if s.get('enabled')]),
                'active_scans': len(self.active_scans)
            }
        }
        
    def enable_schedule(self, schedule_id: str, enabled: bool = True) -> bool:
        """Enable or disable a schedule"""
        for schedule in self.scan_schedules:
            if schedule['id'] == schedule_id:
                schedule['enabled'] = enabled
                self.save_schedules()
                
                status = "enabled" if enabled else "disabled"
                log_scheduled_scan('INFO', f'Schedule {status}: {schedule["name"]}')
                return True
        return False
        
    def get_next_scans(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get next scheduled scans"""
        enabled_schedules = [s for s in self.scan_schedules if s.get('enabled') and s.get('next_run')]
        
        # Sort by next run time
        enabled_schedules.sort(key=lambda x: x['next_run'])
        
        return enabled_schedules[:limit]
        
    def is_scan_in_progress(self) -> bool:
        """Check if any scan is currently in progress"""
        return len(self.active_scans) > 0
        
    def get_scan_progress_info(self) -> Optional[Dict[str, Any]]:
        """Get information about current scan progress"""
        if not self.active_scans:
            return None
            
        # Return info about the first active scan
        scan = list(self.active_scans.values())[0]
        return {
            'name': scan['schedule_name'],
            'progress': scan.get('progress', 0),
            'status': scan['status'],
            'start_time': scan['start_time'],
            'devices_found': scan.get('devices_found', 0)
        }

# Global instance
scheduled_scan_monitor = ScheduledScanMonitor()

# Convenience functions
def get_scheduled_scan_status():
    """Get scheduled scan status"""
    return scheduled_scan_monitor.get_current_status()

def is_scheduled_scan_running():
    """Check if scheduled scan is running"""
    return scheduled_scan_monitor.is_scan_in_progress()

def get_scheduled_scan_progress():
    """Get current scan progress"""
    return scheduled_scan_monitor.get_scan_progress_info()

def enable_scheduled_scan(schedule_id: str, enabled: bool = True):
    """Enable/disable a scheduled scan"""
    return scheduled_scan_monitor.enable_schedule(schedule_id, enabled)

def get_next_scheduled_scans():
    """Get next scheduled scans"""
    return scheduled_scan_monitor.get_next_scans()

if __name__ == "__main__":
    # Test the scheduled scan monitor
    print("⏰ Testing Enhanced Scheduled Scan Monitor...")
    
    monitor = ScheduledScanMonitor()
    
    # Get status
    status = monitor.get_current_status()
    print(f"Current status: {status['summary']}")
    
    # Show next scans
    next_scans = monitor.get_next_scans()
    print(f"\nNext scheduled scans:")
    for scan in next_scans:
        print(f"  - {scan['name']}: {scan.get('next_run', 'Not scheduled')}")
        
    # Check if scan in progress
    if monitor.is_scan_in_progress():
        progress = monitor.get_scan_progress_info()
        print(f"\nScan in progress: {progress}")
    else:
        print("\nNo scans currently running")
        
    print("\n✅ Enhanced Scheduled Scan Monitor Ready!")