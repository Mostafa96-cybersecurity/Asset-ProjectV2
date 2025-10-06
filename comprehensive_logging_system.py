#!/usr/bin/env python3
"""
🔥 COMPREHENSIVE LOGGING SYSTEM FOR ALL FEATURES
==============================================================
Centralized logging system for all jobs, features, and operations
with real-time monitoring and error detection.
"""

import logging
import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import threading
from queue import Queue

class FeatureLogger:
    """Centralized logger for all system features"""
    
    def __init__(self):
        self.log_directory = Path("logs")
        self.log_directory.mkdir(exist_ok=True)
        
        # Feature-specific loggers
        self.feature_loggers = {}
        self.log_queue = Queue()
        self.active_jobs = {}
        self.job_stats = {}
        
        # Setup master logger
        self.setup_master_logger()
        
        # Setup feature loggers
        self.setup_feature_loggers()
        
        # Start log processor
        self.start_log_processor()
        
    def setup_master_logger(self):
        """Setup the master system logger"""
        self.master_logger = logging.getLogger('AssetManagementSystem')
        self.master_logger.setLevel(logging.DEBUG)
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s'
        )
        
        # File handler for all logs
        all_logs_handler = logging.FileHandler(
            self.log_directory / 'system_all.log',
            encoding='utf-8'
        )
        all_logs_handler.setFormatter(detailed_formatter)
        all_logs_handler.setLevel(logging.DEBUG)
        
        # Error-only file handler
        error_handler = logging.FileHandler(
            self.log_directory / 'system_errors.log',
            encoding='utf-8'
        )
        error_handler.setFormatter(detailed_formatter)
        error_handler.setLevel(logging.ERROR)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(simple_formatter)
        console_handler.setLevel(logging.INFO)
        
        self.master_logger.addHandler(all_logs_handler)
        self.master_logger.addHandler(error_handler)
        self.master_logger.addHandler(console_handler)
        
    def setup_feature_loggers(self):
        """Setup individual feature loggers"""
        features = [
            'web_service',
            'scheduled_scanning',
            'data_collection', 
            'stop_collection',
            'duplicate_cleanup',
            'manual_network_device',
            'ad_integration',
            'multithreading_performance',
            'database_operations',
            'authentication',
            'network_validation',
            'file_operations'
        ]
        
        for feature in features:
            logger = logging.getLogger(f'AssetManagement.{feature}')
            logger.setLevel(logging.DEBUG)
            
            # Feature-specific file handler
            handler = logging.FileHandler(
                self.log_directory / f'{feature}.log',
                encoding='utf-8'
            )
            formatter = logging.Formatter(
                '%(asctime)s | %(levelname)s | %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
            self.feature_loggers[feature] = logger
            
    def start_log_processor(self):
        """Start background log processor for real-time monitoring"""
        def process_logs():
            while True:
                try:
                    if not self.log_queue.empty():
                        log_entry = self.log_queue.get(timeout=1)
                        self.process_log_entry(log_entry)
                    time.sleep(0.1)
                except:
                    time.sleep(1)
                    
        processor_thread = threading.Thread(target=process_logs, daemon=True)
        processor_thread.start()
        
    def process_log_entry(self, entry: Dict[str, Any]):
        """Process individual log entries for monitoring"""
        feature = entry.get('feature', 'unknown')
        level = entry.get('level', 'INFO')
        message = entry.get('message', '')
        timestamp = entry.get('timestamp', datetime.now())
        
        # Update job stats
        if feature not in self.job_stats:
            self.job_stats[feature] = {
                'total_logs': 0,
                'errors': 0,
                'warnings': 0,
                'last_activity': timestamp,
                'status': 'idle'
            }
            
        stats = self.job_stats[feature]
        stats['total_logs'] += 1
        stats['last_activity'] = timestamp
        
        if level == 'ERROR':
            stats['errors'] += 1
        elif level == 'WARNING':
            stats['warnings'] += 1
            
    def log_feature(self, feature: str, level: str, message: str, **kwargs):
        """Log message for specific feature"""
        try:
            logger = self.feature_loggers.get(feature, self.master_logger)
            
            # Add to queue for monitoring
            log_entry = {
                'feature': feature,
                'level': level,
                'message': message,
                'timestamp': datetime.now(),
                **kwargs
            }
            self.log_queue.put(log_entry)
            
            # Log using appropriate level
            if level == 'DEBUG':
                logger.debug(message)
            elif level == 'INFO':
                logger.info(message)
            elif level == 'WARNING':
                logger.warning(message)
            elif level == 'ERROR':
                logger.error(message)
            elif level == 'CRITICAL':
                logger.critical(message)
                
        except Exception as e:
            self.master_logger.error(f"Logging error for {feature}: {e}")
            
    def start_job(self, job_id: str, feature: str, description: str):
        """Start tracking a job"""
        self.active_jobs[job_id] = {
            'feature': feature,
            'description': description,
            'start_time': datetime.now(),
            'status': 'running',
            'progress': 0,
            'logs': []
        }
        
        self.log_feature(feature, 'INFO', f"🚀 Started job: {description}", job_id=job_id)
        
    def update_job_progress(self, job_id: str, progress: int, status_message: str = ""):
        """Update job progress"""
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            job['progress'] = progress
            job['logs'].append({
                'timestamp': datetime.now(),
                'message': status_message,
                'progress': progress
            })
            
            if status_message:
                self.log_feature(job['feature'], 'INFO', 
                               f"📊 Progress {progress}%: {status_message}", 
                               job_id=job_id)
                
    def complete_job(self, job_id: str, success: bool = True, final_message: str = ""):
        """Complete a job"""
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            job['status'] = 'completed' if success else 'failed'
            job['end_time'] = datetime.now()
            job['duration'] = job['end_time'] - job['start_time']
            
            status_icon = "✅" if success else "❌"
            result = "completed successfully" if success else "failed"
            
            message = f"{status_icon} Job {result}: {job['description']}"
            if final_message:
                message += f" - {final_message}"
                
            self.log_feature(job['feature'], 'INFO' if success else 'ERROR', 
                           message, job_id=job_id)
            
            # Move to completed jobs
            if not hasattr(self, 'completed_jobs'):
                self.completed_jobs = {}
            self.completed_jobs[job_id] = job
            del self.active_jobs[job_id]
            
    def get_feature_status(self, feature: str) -> Dict[str, Any]:
        """Get current status of a feature"""
        stats = self.job_stats.get(feature, {})
        active_jobs = [job for job in self.active_jobs.values() 
                      if job['feature'] == feature]
        
        return {
            'feature': feature,
            'status': 'active' if active_jobs else 'idle',
            'active_jobs': len(active_jobs),
            'total_logs': stats.get('total_logs', 0),
            'errors': stats.get('errors', 0),
            'warnings': stats.get('warnings', 0),
            'last_activity': stats.get('last_activity'),
            'jobs': active_jobs
        }
        
    def get_all_features_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all features"""
        return {feature: self.get_feature_status(feature) 
                for feature in self.feature_loggers.keys()}
        
    def get_recent_logs(self, feature: str = None, limit: int = 100) -> List[str]:
        """Get recent log entries"""
        try:
            if feature and feature in self.feature_loggers:
                log_file = self.log_directory / f'{feature}.log'
            else:
                log_file = self.log_directory / 'system_all.log'
                
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    return lines[-limit:] if len(lines) > limit else lines
            return []
        except Exception as e:
            return [f"Error reading logs: {e}"]
            
    def export_logs(self, feature: str = None, start_date: datetime = None) -> str:
        """Export logs to JSON format"""
        try:
            logs_data = {
                'export_timestamp': datetime.now().isoformat(),
                'feature': feature or 'all',
                'logs': self.get_recent_logs(feature, 10000)
            }
            
            if start_date:
                logs_data['start_date'] = start_date.isoformat()
                
            filename = f"logs_export_{feature or 'all'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            export_path = self.log_directory / filename
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(logs_data, f, indent=2, ensure_ascii=False)
                
            return str(export_path)
        except Exception as e:
            self.master_logger.error(f"Export failed: {e}")
            return ""

# Global logging instance
comprehensive_logger = FeatureLogger()

# Convenience functions for easy logging
def log_web_service(level: str, message: str, **kwargs):
    """Log web service activity"""
    comprehensive_logger.log_feature('web_service', level, message, **kwargs)

def log_scheduled_scan(level: str, message: str, **kwargs):
    """Log scheduled scanning activity"""
    comprehensive_logger.log_feature('scheduled_scanning', level, message, **kwargs)

def log_data_collection(level: str, message: str, **kwargs):
    """Log data collection activity"""
    comprehensive_logger.log_feature('data_collection', level, message, **kwargs)

def log_stop_collection(level: str, message: str, **kwargs):
    """Log stop collection activity"""
    comprehensive_logger.log_feature('stop_collection', level, message, **kwargs)

def log_ad_integration(level: str, message: str, **kwargs):
    """Log AD integration activity"""
    comprehensive_logger.log_feature('ad_integration', level, message, **kwargs)

def log_database_operation(level: str, message: str, **kwargs):
    """Log database operations"""
    comprehensive_logger.log_feature('database_operations', level, message, **kwargs)

def start_job(job_id: str, feature: str, description: str):
    """Start tracking a job"""
    comprehensive_logger.start_job(job_id, feature, description)

def update_job_progress(job_id: str, progress: int, status_message: str = ""):
    """Update job progress"""
    comprehensive_logger.update_job_progress(job_id, progress, status_message)

def complete_job(job_id: str, success: bool = True, final_message: str = ""):
    """Complete a job"""
    comprehensive_logger.complete_job(job_id, success, final_message)

def get_feature_status(feature: str):
    """Get feature status"""
    return comprehensive_logger.get_feature_status(feature)

def get_all_status():
    """Get all features status"""
    return comprehensive_logger.get_all_features_status()

if __name__ == "__main__":
    # Test the logging system
    print("🔥 Testing Comprehensive Logging System...")
    
    # Test feature logging
    log_web_service('INFO', 'Web service starting up')
    log_scheduled_scan('INFO', 'Scheduled scan initiated')
    log_data_collection('INFO', 'Starting device collection')
    
    # Test job tracking
    start_job('test_job_1', 'data_collection', 'Testing device collection')
    update_job_progress('test_job_1', 25, 'Found 5 devices')
    update_job_progress('test_job_1', 50, 'Found 10 devices')
    update_job_progress('test_job_1', 100, 'Collection complete')
    complete_job('test_job_1', True, 'Successfully collected 15 devices')
    
    # Show status
    status = get_all_status()
    print("\n📊 Feature Status Summary:")
    for feature, info in status.items():
        print(f"   {feature}: {info['status']} (logs: {info['total_logs']}, errors: {info['errors']})")
    
    print("\n✅ Comprehensive Logging System Ready!")