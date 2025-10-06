# -*- coding: utf-8 -*-
"""
Threaded Enhanced Collector - High Performance with Error Prevention
==================================================================
- Multi-threaded device discovery and collection
- Real-time progress updates and status monitoring
- Intelligent resource management and load balancing
- Live device prioritization and retry mechanisms
- Advanced error recovery and quality assurance
"""

import logging
import threading
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Set
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

from core.enhanced_smart_collector import EnhancedSmartCollector
from core.advanced_duplicate_manager import DuplicateManager, DataValidator, ErrorRecovery
from collectors.wmi_collector import collect_windows_wmi
from collectors.ssh_collector import collect_linux_or_esxi_ssh

log = logging.getLogger(__name__)


class ThreadedDeviceCollector(QObject):
    """High-performance threaded device collector with real-time monitoring"""
    
    # Signals for real-time updates
    progress_updated = pyqtSignal(str, int)  # message, percentage
    device_discovered = pyqtSignal(dict, float)  # device_info, quality_score
    device_collected = pyqtSignal(dict)  # device_data
    error_occurred = pyqtSignal(str, str, str)  # severity, category, message
    collection_completed = pyqtSignal(list, dict)  # devices, stats
    
    def __init__(self, max_discovery_workers: int = 50, max_collection_workers: int = 20):
        super().__init__()
        
        # Core components
        self.smart_collector = EnhancedSmartCollector()
        self.duplicate_manager = DuplicateManager()
        self.data_validator = DataValidator()
        self.error_recovery = ErrorRecovery()
        
        # Threading configuration
        self.max_discovery_workers = max_discovery_workers
        self.max_collection_workers = max_collection_workers
        self.discovery_executor = None
        self.collection_executor = None
        
        # Collection state
        self.is_running = False
        self.should_stop = False
        self.targets = []
        self.ssh_credentials = None
        
        # Queues for different stages
        self.discovery_queue = queue.Queue()
        self.collection_queue = queue.Queue()
        self.results_queue = queue.Queue()
        
        # Real-time monitoring
        self.stats = {
            'start_time': None,
            'targets_total': 0,
            'discovery_completed': 0,
            'discovery_successful': 0,
            'collection_completed': 0,
            'collection_successful': 0,
            'errors_recovered': 0,
            'duplicates_prevented': 0,
            'quality_score': 100.0
        }
        
        # Live devices tracking
        self.live_devices = set()
        self.failed_devices = set()
        self.retry_queue = queue.Queue()
        
        # Progress monitoring timer
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self._update_progress)
        
    def start_collection(self, targets: List[str], ssh_credentials: Dict = None):
        """Start the threaded collection process"""
        if self.is_running:
            log.warning("Collection already running")
            return
        
        self.targets = targets
        self.ssh_credentials = ssh_credentials
        self.should_stop = False
        self.is_running = True
        
        # Reset statistics
        self.stats['start_time'] = datetime.now()
        self.stats['targets_total'] = len(targets)
        self.stats['discovery_completed'] = 0
        self.stats['discovery_successful'] = 0
        self.stats['collection_completed'] = 0
        self.stats['collection_successful'] = 0
        
        # Clear queues and sets
        self._clear_all_queues()
        self.live_devices.clear()
        self.failed_devices.clear()
        
        log.info(f"🚀 Starting threaded collection for {len(targets)} targets")
        self.progress_updated.emit("🚀 Initializing high-performance collection system...", 5)
        
        # Start the collection pipeline
        self._start_discovery_phase()
        
        # Start progress monitoring
        self.progress_timer.start(500)  # Update every 500ms
        
    def _clear_all_queues(self):
        """Clear all queues"""
        for q in [self.discovery_queue, self.collection_queue, self.results_queue, self.retry_queue]:
            while not q.empty():
                try:
                    q.get_nowait()
                except queue.Empty:
                    break
    
    def _start_discovery_phase(self):
        """Start the device discovery phase with threading"""
        self.progress_updated.emit("🔍 Phase 1: High-Speed Device Discovery", 10)
        
        # Create discovery thread pool
        self.discovery_executor = ThreadPoolExecutor(
            max_workers=self.max_discovery_workers,
            thread_name_prefix="DeviceDiscovery"
        )
        
        # Submit all targets for discovery
        futures = {}
        for target in self.targets:
            future = self.discovery_executor.submit(self._discover_single_device, target)
            futures[future] = target
        
        # Process discovery results
        threading.Thread(
            target=self._process_discovery_results,
            args=(futures,),
            daemon=True,
            name="DiscoveryProcessor"
        ).start()
    
    def _discover_single_device(self, target: str) -> Optional[Dict]:
        """Discover a single device with enhanced validation"""
        try:
            # Enhanced ping with detailed information
            device_info = self.smart_collector.scan_alive_devices_enhanced([target])
            
            if device_info and len(device_info) > 0:
                device = device_info[0]
                
                # Add to live devices set
                self.live_devices.add(target)
                
                # Enhanced OS detection
                os_type, confidence = self.smart_collector.detect_os_type_enhanced(device)
                device['detected_os'] = os_type
                device['os_confidence'] = confidence
                
                # Categorize device
                category = self.smart_collector.categorize_device_enhanced(device, os_type, confidence)
                device['category'] = category
                
                return device
                
        except Exception as e:
            log.debug(f"Discovery failed for {target}: {e}")
            self.failed_devices.add(target)
            
            # Add to retry queue if enabled
            if self.smart_collector.retry_failed_devices:
                self.retry_queue.put(target)
        
        return None
    
    def _process_discovery_results(self, futures: Dict):
        """Process discovery results and start collection phase"""
        discovered_devices = []
        
        try:
            for future in as_completed(futures):
                if self.should_stop:
                    break
                
                target = futures[future]
                result = future.result()
                
                self.stats['discovery_completed'] += 1
                
                if result:
                    discovered_devices.append(result)
                    self.stats['discovery_successful'] += 1
                    
                    # Emit device discovered signal
                    quality_score = self._calculate_device_quality(result)
                    self.device_discovered.emit(result, quality_score)
                    
                    # Add to collection queue
                    self.collection_queue.put(result)
                
                # Update progress
                progress = 10 + (self.stats['discovery_completed'] / self.stats['targets_total']) * 30
                self.progress_updated.emit(
                    f"🔍 Discovery: {self.stats['discovery_successful']}/{self.stats['targets_total']} devices found",
                    int(progress)
                )
        
        finally:
            # Shutdown discovery executor
            if self.discovery_executor:
                self.discovery_executor.shutdown(wait=True)
            
            # Start collection phase
            if not self.should_stop and discovered_devices:
                self._start_collection_phase(discovered_devices)
            else:
                self._finish_collection()
    
    def _start_collection_phase(self, discovered_devices: List[Dict]):
        """Start the device data collection phase"""
        self.progress_updated.emit("📊 Phase 2: High-Performance Data Collection", 45)
        
        # Create collection thread pool
        self.collection_executor = ThreadPoolExecutor(
            max_workers=self.max_collection_workers,
            thread_name_prefix="DataCollection"
        )
        
        # Submit devices for data collection
        futures = {}
        for device in discovered_devices:
            future = self.collection_executor.submit(self._collect_single_device, device)
            futures[future] = device
        
        # Process collection results
        threading.Thread(
            target=self._process_collection_results,
            args=(futures,),
            daemon=True,
            name="CollectionProcessor"
        ).start()
    
    def _collect_single_device(self, device_info: Dict) -> Optional[Dict]:
        """Collect data from a single device with error recovery"""
        ip_address = device_info.get('ip_address')
        os_type = device_info.get('detected_os', 'unknown')
        
        try:
            # Use error recovery for collection
            device_data = self.error_recovery.retry_with_backoff(
                self._collect_device_data_with_method,
                device_info, os_type, self.ssh_credentials,
                max_retries=3
            )
            
            if device_data:
                # Validate and sanitize data
                is_valid, sanitized_data, errors = self.data_validator.sanitize_device_data(device_data)
                
                if is_valid:
                    # Check for duplicates
                    is_duplicate, existing_data = self.duplicate_manager.check_duplicate(
                        sanitized_data, device_info.get('category', 'Unknown')
                    )
                    
                    if is_duplicate:
                        # Merge with existing data
                        sanitized_data = self.duplicate_manager.merge_device_data(
                            sanitized_data, existing_data
                        )
                        self.stats['duplicates_prevented'] += 1
                        log.info(f"Duplicate prevented and merged: {ip_address}")
                    
                    # Add collection metadata
                    sanitized_data.update({
                        'Collection Method': 'Threaded Enhanced',
                        'Collection Timestamp': datetime.now().isoformat(),
                        'Data Quality': 'Validated',
                        'OS Detection Confidence': device_info.get('os_confidence', 0.0)
                    })
                    
                    return sanitized_data
                else:
                    log.warning(f"Data validation failed for {ip_address}: {errors}")
                    
        except Exception as e:
            log.error(f"Collection failed for {ip_address}: {e}")
            self.error_occurred.emit('ERROR', 'collection', f"Failed to collect {ip_address}: {e}")
        
        return None
    
    def _collect_device_data_with_method(self, device_info: Dict, os_type: str, ssh_credentials: Dict) -> Optional[Dict]:
        """Collect device data using the appropriate method"""
        ip_address = device_info['ip_address']
        
        try:
            if os_type == 'windows':
                # Try WMI collection
                device_data = collect_windows_wmi(ip_address)
                if device_data:
                    return device_data
                    
            elif os_type in ['linux', 'unix'] and ssh_credentials:
                # Try SSH collection
                device_data = collect_linux_or_esxi_ssh(
                    ip_address,
                    ssh_credentials.get('username'),
                    ssh_credentials.get('password')
                )
                if device_data:
                    return device_data
            
            # Fallback to basic network info
            return {
                'Hostname': device_info.get('hostname', ip_address),
                'IP Address': ip_address,
                'Classification': device_info.get('category', 'Network Device'),
                'Status': 'Online',
                'Last Seen': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Detection Method': f'Network Scan ({os_type})',
                'Response Time (ms)': device_info.get('response_time_ms', 0)
            }
            
        except Exception as e:
            log.error(f"Data collection method failed for {ip_address}: {e}")
            raise
    
    def _process_collection_results(self, futures: Dict):
        """Process collection results and finish up"""
        collected_devices = []
        
        try:
            for future in as_completed(futures):
                if self.should_stop:
                    break
                
                device_info = futures[future]
                result = future.result()
                
                self.stats['collection_completed'] += 1
                
                if result:
                    collected_devices.append(result)
                    self.stats['collection_successful'] += 1
                    
                    # Emit device collected signal
                    self.device_collected.emit(result)
                    
                    # Add to results queue
                    self.results_queue.put(result)
                
                # Update progress
                progress = 45 + (self.stats['collection_completed'] / len(futures)) * 45
                self.progress_updated.emit(
                    f"📊 Collection: {self.stats['collection_successful']}/{len(futures)} devices processed",
                    int(progress)
                )
        
        finally:
            # Shutdown collection executor
            if self.collection_executor:
                self.collection_executor.shutdown(wait=True)
            
            # Finish collection
            self._finish_collection(collected_devices)
    
    def _finish_collection(self, collected_devices: List[Dict] = None):
        """Finish the collection process"""
        if collected_devices is None:
            collected_devices = []
        
        self.is_running = False
        self.progress_timer.stop()
        
        # Calculate final statistics
        end_time = datetime.now()
        duration = (end_time - self.stats['start_time']).total_seconds()
        
        final_stats = {
            **self.stats,
            'end_time': end_time,
            'duration_seconds': duration,
            'devices_per_minute': (self.stats['collection_successful'] / duration) * 60 if duration > 0 else 0,
            'success_rate': (self.stats['collection_successful'] / self.stats['targets_total']) * 100,
            'quality_score': self._calculate_overall_quality_score()
        }
        
        log.info(f"✅ Collection completed: {len(collected_devices)} devices in {duration:.1f}s")
        
        # Emit completion signal
        self.progress_updated.emit(
            f"✅ Collection Complete: {len(collected_devices)} devices in {duration:.1f}s",
            100
        )
        self.collection_completed.emit(collected_devices, final_stats)
    
    def _calculate_device_quality(self, device_info: Dict) -> float:
        """Calculate quality score for a discovered device"""
        score = 100.0
        
        # Deduct points for missing information
        if not device_info.get('hostname'):
            score -= 10
        if not device_info.get('detected_os'):
            score -= 15
        if device_info.get('os_confidence', 1.0) < 0.8:
            score -= 10
        if device_info.get('response_time_ms', 0) > 1000:
            score -= 5
        
        return max(0.0, score)
    
    def _calculate_overall_quality_score(self) -> float:
        """Calculate overall collection quality score"""
        if self.stats['targets_total'] == 0:
            return 100.0
        
        base_score = (self.stats['collection_successful'] / self.stats['targets_total']) * 100
        
        # Bonus for error recovery
        if self.stats['errors_recovered'] > 0:
            base_score += min(5, self.stats['errors_recovered'])
        
        # Bonus for duplicate prevention
        if self.stats['duplicates_prevented'] > 0:
            base_score += min(5, self.stats['duplicates_prevented'])
        
        return min(100.0, base_score)
    
    def _update_progress(self):
        """Update progress timer callback"""
        if not self.is_running:
            return
        
        # Calculate current progress based on completion rates
        discovery_progress = (self.stats['discovery_completed'] / self.stats['targets_total']) * 40
        collection_progress = 0
        
        if self.stats['discovery_successful'] > 0:
            collection_progress = (self.stats['collection_completed'] / self.stats['discovery_successful']) * 50
        
        total_progress = 10 + discovery_progress + collection_progress
        
        # Update quality score
        self.stats['quality_score'] = self._calculate_overall_quality_score()
    
    def stop_collection(self):
        """Stop the collection process gracefully"""
        log.info("🛑 Stopping threaded collection...")
        self.should_stop = True
        self.is_running = False
        
        # Shutdown executors
        if self.discovery_executor:
            self.discovery_executor.shutdown(wait=False)
        if self.collection_executor:
            self.collection_executor.shutdown(wait=False)
        
        self.progress_timer.stop()
        
        log.info("Collection stopped")
    
    def get_live_devices(self) -> Set[str]:
        """Get currently live devices"""
        return self.live_devices.copy()
    
    def get_failed_devices(self) -> Set[str]:
        """Get devices that failed discovery"""
        return self.failed_devices.copy()
    
    def get_statistics(self) -> Dict:
        """Get current collection statistics"""
        return self.stats.copy()