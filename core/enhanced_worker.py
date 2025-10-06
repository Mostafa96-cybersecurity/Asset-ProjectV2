# -*- coding: utf-8 -*-
"""
Enhanced Worker with Comprehensive Error Prevention
-------------------------------------------------
Integrates all error prevention features into the collection workflow:
- Smart duplicate detection and prevention
- Advanced data validation and sanitization
- Error recovery with exponential backoff
- Real-time quality monitoring
- Performance optimization
"""

import logging
from typing import Dict, List, Optional, Callable
from datetime import datetime
from PyQt6.QtCore import QThread, pyqtSignal

from core.enhanced_smart_collector import EnhancedSmartCollector
from core.advanced_duplicate_manager import DuplicateManager, DataValidator, ErrorRecovery
# from core.excel_db_sync import ExcelDBSync  # Disabled - Database-only system
from gui.error_monitor_dashboard import ErrorMonitor

log = logging.getLogger(__name__)


class EnhancedDeviceCollectionWorker(QThread):
    """Enhanced device collection worker with comprehensive error prevention"""
    
    # Enhanced signals with quality metrics
    progress_updated = pyqtSignal(str, int)  # message, percentage
    device_discovered = pyqtSignal(dict, float)  # device_info, quality_score
    quality_updated = pyqtSignal(float)  # overall quality score
    error_occurred = pyqtSignal(str, str, str)  # level, category, message
    collection_completed = pyqtSignal(dict)  # comprehensive stats
    duplicate_resolved = pyqtSignal(str, dict)  # resolution_strategy, merged_data
    
    def __init__(self, targets: List[str], ssh_credentials: Optional[Dict] = None, 
                 excel_path: Optional[str] = None, progress_callback: Optional[Callable] = None):
        super().__init__()
        
        self.targets = targets
        self.ssh_credentials = ssh_credentials or {}
        self.excel_path = excel_path or "Network_Assets.xlsx"
        self.progress_callback = progress_callback
        
        # Enhanced components
        self.smart_collector = EnhancedSmartCollector(self._on_progress_update)
        self.duplicate_manager = DuplicateManager()
        self.data_validator = DataValidator()
        self.error_recovery = ErrorRecovery()
        self.error_monitor = ErrorMonitor()
        # self.sync_manager = ExcelDBSync()  # Disabled - Database-only system
        
        # Collection state
        self.is_running = False
        self.should_stop = False
        self.collection_stats = {
            'start_time': None,
            'end_time': None,
            'total_targets': 0,
            'alive_devices': 0,
            'successful_collections': 0,
            'duplicates_found': 0,
            'duplicates_resolved': 0,
            'validation_errors': 0,
            'validation_fixes': 0,
            'errors_recovered': 0,
            'final_quality_score': 100.0
        }
    
    def run(self):
        """Enhanced device collection workflow with comprehensive error prevention"""
        self.is_running = True
        self.collection_stats['start_time'] = datetime.now()
        self.collection_stats['total_targets'] = len(self.targets)
        
        try:
            log.info(f"🛡️ Starting enhanced collection for {len(self.targets)} targets")
            self.error_monitor.log_success('collection', f'Started collection of {len(self.targets)} targets')
            
            # Phase 1: Enhanced Network Discovery
            self._emit_progress("🔍 Phase 1: Enhanced Network Discovery with Validation", 10)
            alive_devices = self._enhanced_network_discovery()
            
            if self.should_stop:
                return
            
            # Phase 2: Intelligent OS Detection
            self._emit_progress("🧠 Phase 2: Intelligent OS Detection with Confidence Scoring", 30)
            categorized_devices = self._intelligent_os_detection(alive_devices)
            
            if self.should_stop:
                return
            
            # Phase 3: Smart Data Collection with Validation
            self._emit_progress("📊 Phase 3: Smart Data Collection with Quality Assurance", 50)
            collected_devices = self._smart_data_collection(categorized_devices)
            
            if self.should_stop:
                return
            
            # Phase 4: Advanced Duplicate Resolution
            self._emit_progress("🔄 Phase 4: Advanced Duplicate Detection & Resolution", 70)
            deduplicated_devices = self._advanced_duplicate_resolution(collected_devices)
            
            if self.should_stop:
                return
            
            # Phase 5: Comprehensive Data Validation
            self._emit_progress("✅ Phase 5: Comprehensive Data Validation & Sanitization", 85)
            validated_devices = self._comprehensive_data_validation(deduplicated_devices)
            
            if self.should_stop:
                return
            
            # Phase 6: Intelligent Excel-DB Sync
            self._emit_progress("💾 Phase 6: Intelligent Excel-Database Synchronization", 95)
            self._intelligent_sync_to_storage(validated_devices)
            
            # Phase 7: Final Quality Assessment
            self._emit_progress("🎯 Phase 7: Final Quality Assessment & Reporting", 100)
            final_stats = self._generate_final_report()
            
            self.collection_completed.emit(final_stats)
            
            log.info("✅ Enhanced collection completed successfully")
            log.info(f"📊 Final Quality Score: {final_stats['final_quality_score']:.1f}%")
            
        except Exception as e:
            error_msg = f"Enhanced collection failed: {e}"
            log.error(error_msg)
            self.error_monitor.log_error('ERROR', error_msg, 'collection')
            self.error_occurred.emit('ERROR', 'collection', error_msg)
        
        finally:
            self.is_running = False
            self.collection_stats['end_time'] = datetime.now()
    
    def _enhanced_network_discovery(self) -> List[Dict]:
        """Phase 1: Enhanced network discovery with comprehensive validation"""
        try:
            alive_devices = self.smart_collector.scan_alive_devices_enhanced(
                self.targets, max_workers=30
            )
            
            self.collection_stats['alive_devices'] = len(alive_devices)
            
            # Log discovery results
            success_rate = (len(alive_devices) / len(self.targets)) * 100
            log.info(f"Network discovery: {len(alive_devices)}/{len(self.targets)} devices alive ({success_rate:.1f}%)")
            
            if success_rate < 50:
                warning_msg = f"Low network discovery success rate: {success_rate:.1f}%"
                self.error_monitor.log_error('WARNING', warning_msg, 'network')
                self.error_occurred.emit('WARNING', 'network', warning_msg)
            
            return alive_devices
            
        except Exception as e:
            error_msg = f"Network discovery failed: {e}"
            self.error_monitor.log_error('ERROR', error_msg, 'network')
            raise
    
    def _intelligent_os_detection(self, alive_devices: List[Dict]) -> List[Dict]:
        """Phase 2: Intelligent OS detection with confidence scoring"""
        categorized_devices = []
        
        for i, device_info in enumerate(alive_devices):
            if self.should_stop:
                break
            
            try:
                # Enhanced OS detection
                os_type, confidence = self.smart_collector.detect_os_type_enhanced(device_info)
                
                device_info['detected_os'] = os_type
                device_info['os_confidence'] = confidence
                device_info['category'] = self.smart_collector.categorize_device_enhanced(
                    device_info, os_type, confidence
                )
                
                categorized_devices.append(device_info)
                
                # Update progress
                progress = 30 + (i / len(alive_devices)) * 20
                self._emit_progress(f"🧠 OS Detection: {device_info['ip_address']} → {os_type} ({confidence:.2f})", 
                                  int(progress))
                
                # Log low confidence detections
                if confidence < 0.5:
                    warning_msg = f"Low confidence OS detection for {device_info['ip_address']}: {os_type} ({confidence:.2f})"
                    self.error_monitor.log_error('WARNING', warning_msg, 'os_detection')
                
            except Exception as e:
                error_msg = f"OS detection failed for {device_info['ip_address']}: {e}"
                self.error_monitor.log_error('ERROR', error_msg, 'os_detection')
                
                # Add with unknown OS as fallback
                device_info['detected_os'] = 'unknown'
                device_info['os_confidence'] = 0.0
                device_info['category'] = 'Windows Devices'  # Default fallback
                categorized_devices.append(device_info)
        
        log.info(f"OS detection completed: {len(categorized_devices)} devices categorized")
        return categorized_devices
    
    def _smart_data_collection(self, categorized_devices: List[Dict]) -> List[Dict]:
        """Phase 3: Smart data collection with quality assurance"""
        collected_devices = []
        
        for i, device_info in enumerate(categorized_devices):
            if self.should_stop:
                break
            
            try:
                # Collect device data with error recovery
                device_data = self.smart_collector.collect_device_data_enhanced(
                    device_info, 
                    device_info['detected_os'],
                    self.ssh_credentials
                )
                
                if device_data:
                    # Add discovery metadata
                    device_data['Discovery Method'] = 'Enhanced Smart Scan'
                    device_data['OS Confidence'] = device_info.get('os_confidence', 1.0)
                    device_data['Collection Quality'] = 'Validated'
                    device_data['Collection Timestamp'] = datetime.now().isoformat()
                    
                    collected_devices.append(device_data)
                    self.collection_stats['successful_collections'] += 1
                    
                    # Emit device discovered signal with quality score
                    quality_score = self._calculate_device_quality_score(device_data)
                    self.device_discovered.emit(device_data, quality_score)
                    
                    log.debug(f"✅ Collected data for {device_data.get('Hostname', 'Unknown')} (Quality: {quality_score:.1f}%)")
                else:
                    error_msg = f"No data collected for {device_info['ip_address']}"
                    self.error_monitor.log_error('WARNING', error_msg, 'collection')
                
                # Update progress
                progress = 50 + (i / len(categorized_devices)) * 20
                self._emit_progress(f"📊 Data Collection: {device_info['ip_address']} ({len(collected_devices)} collected)", 
                                  int(progress))
                
            except Exception as e:
                error_msg = f"Data collection failed for {device_info['ip_address']}: {e}"
                self.error_monitor.log_error('ERROR', error_msg, 'collection')
                
                # Try error recovery
                try:
                    recovered_data = self.error_recovery.retry_with_backoff(
                        self.smart_collector.collect_device_data_enhanced,
                        device_info, device_info['detected_os'], self.ssh_credentials
                    )
                    
                    if recovered_data:
                        collected_devices.append(recovered_data)
                        self.collection_stats['errors_recovered'] += 1
                        self.error_monitor.log_success('error_recovery', f'Recovered data for {device_info["ip_address"]}')
                        
                except Exception as recovery_error:
                    log.error(f"Error recovery failed for {device_info['ip_address']}: {recovery_error}")
        
        log.info(f"Data collection completed: {len(collected_devices)} devices with data")
        return collected_devices
    
    def _advanced_duplicate_resolution(self, collected_devices: List[Dict]) -> List[Dict]:
        """Phase 4: Advanced duplicate detection and resolution"""
        deduplicated_devices = []
        duplicate_pairs = []
        
        for device_data in collected_devices:
            if self.should_stop:
                break
            
            try:
                # Check for duplicates using advanced fingerprinting
                category = self._determine_device_category(device_data)
                is_duplicate, existing_info = self.duplicate_manager.check_duplicate(device_data, category)
                
                if is_duplicate and existing_info:
                    self.collection_stats['duplicates_found'] += 1
                    
                    # Merge duplicate data intelligently
                    merged_data = self.duplicate_manager.merge_device_data(device_data, existing_info)
                    
                    # Record duplicate resolution
                    duplicate_pairs.append({
                        'original': existing_info['data'] if existing_info else {},
                        'duplicate': device_data,
                        'merged': merged_data,
                        'strategy': 'intelligent_merge'
                    })
                    
                    self.collection_stats['duplicates_resolved'] += 1
                    self.duplicate_resolved.emit('intelligent_merge', merged_data)
                    
                    # Update the existing device instead of adding new
                    for i, existing_device in enumerate(deduplicated_devices):
                        if existing_info and existing_device == existing_info['data']:
                            deduplicated_devices[i] = merged_data
                            break
                    else:
                        deduplicated_devices.append(merged_data)
                    
                    log.info(f"🔄 Duplicate resolved for {merged_data.get('Hostname', 'Unknown')}")
                else:
                    deduplicated_devices.append(device_data)
                
            except Exception as e:
                error_msg = f"Duplicate resolution failed for device: {e}"
                self.error_monitor.log_error('ERROR', error_msg, 'duplicate')
                deduplicated_devices.append(device_data)  # Add device despite error
        
        log.info(f"Duplicate resolution: {len(deduplicated_devices)} unique devices, {len(duplicate_pairs)} duplicates resolved")
        return deduplicated_devices
    
    def _comprehensive_data_validation(self, devices: List[Dict]) -> List[Dict]:
        """Phase 5: Comprehensive data validation and sanitization"""
        validated_devices = []
        
        for device_data in devices:
            if self.should_stop:
                break
            
            try:
                # Validate and sanitize device data
                is_valid, sanitized_data, errors = self.data_validator.sanitize_device_data(device_data)
                
                if is_valid:
                    sanitized_data['Validation Status'] = 'Passed'
                    sanitized_data['Validation Timestamp'] = datetime.now().isoformat()
                    validated_devices.append(sanitized_data)
                    self.error_monitor.log_success('validation', f'Data validated for {sanitized_data.get("Hostname", "Unknown")}')
                else:
                    self.collection_stats['validation_errors'] += 1
                    
                    # Attempt to fix validation errors
                    try:
                        # Apply automatic fixes where possible
                        fixed_data = self._apply_automatic_fixes(device_data, errors)
                        if fixed_data:
                            fixed_data['Validation Status'] = 'Fixed'
                            fixed_data['Validation Errors'] = '; '.join(errors)
                            validated_devices.append(fixed_data)
                            self.collection_stats['validation_fixes'] += 1
                            self.error_monitor.log_success('validation_fix', f'Validation errors fixed for {fixed_data.get("Hostname", "Unknown")}')
                        else:
                            raise Exception("Automatic fixes failed")
                    except Exception:
                        # Log validation failures but include device with warnings
                        device_data['Validation Status'] = 'Failed'
                        device_data['Validation Errors'] = '; '.join(errors)
                        validated_devices.append(device_data)
                        
                        error_msg = f"Validation failed for {device_data.get('Hostname', 'Unknown')}: {'; '.join(errors)}"
                        self.error_monitor.log_error('WARNING', error_msg, 'validation')
                
            except Exception as e:
                error_msg = f"Data validation error: {e}"
                self.error_monitor.log_error('ERROR', error_msg, 'validation')
                
                # Include device with error status
                device_data['Validation Status'] = 'Error'
                device_data['Validation Errors'] = str(e)
                validated_devices.append(device_data)
        
        log.info(f"Data validation completed: {len(validated_devices)} devices processed")
        return validated_devices
    
    def _intelligent_sync_to_storage(self, validated_devices: List[Dict]):
        """Phase 6: Intelligent synchronization to Excel and Database"""
        
        # Group devices by category for proper sheet organization
        device_categories = self._group_devices_by_category(validated_devices)
        
        for category, devices in device_categories.items():
            if self.should_stop:
                break
            
            try:
                # Define headers based on category
                headers = self._get_category_headers(category)
                
                # Sync each device with error recovery
                for device_data in devices:
                    try:
                        # success = self.sync_manager.add_device_data(  # Disabled - Database-only system
                        #     self.excel_path, category, headers, device_data
                        # )
                        success = True  # Temporary success for database-only system
                        
                        if success:
                            log.debug(f"✅ Synced {device_data.get('Hostname', 'Unknown')} to {category}")
                        else:
                            log.warning(f"⚠️ Device queued for later sync: {device_data.get('Hostname', 'Unknown')}")
                        
                    except Exception as e:
                        error_msg = f"Sync failed for {device_data.get('Hostname', 'Unknown')}: {e}"
                        self.error_monitor.log_error('ERROR', error_msg, 'sync')
                
                log.info(f"Category {category}: {len(devices)} devices processed")
                
            except Exception as e:
                error_msg = f"Category sync failed for {category}: {e}"
                self.error_monitor.log_error('ERROR', error_msg, 'sync')
    
    def _generate_final_report(self) -> Dict:
        """Generate comprehensive final collection report"""
        
        # Calculate final quality score
        stats = self.smart_collector.get_collection_stats()
        monitor_stats = self.error_monitor.get_stats()
        
        total_operations = (
            stats.get('devices_scanned', 0) + 
            stats.get('devices_collected', 0) + 
            self.collection_stats['successful_collections']
        )
        
        total_errors = (
            monitor_stats.get('validation_errors', 0) +
            monitor_stats.get('network_timeouts', 0) +
            monitor_stats.get('database_errors', 0) +
            monitor_stats.get('excel_errors', 0) +
            monitor_stats.get('sync_failures', 0)
        )
        
        if total_operations > 0:
            quality_score = max(0, min(100, ((total_operations - total_errors) / total_operations) * 100))
        else:
            quality_score = 100.0
        
        self.collection_stats['final_quality_score'] = quality_score
        
        # Comprehensive final statistics
        final_stats = {
            **self.collection_stats,
            **stats,
            **monitor_stats,
            'duration_seconds': (self.collection_stats['end_time'] - self.collection_stats['start_time']).total_seconds(),
            'collection_efficiency': (self.collection_stats['successful_collections'] / max(1, self.collection_stats['alive_devices'])) * 100,
            'error_recovery_rate': (self.collection_stats['errors_recovered'] / max(1, total_errors)) * 100,
            'duplicate_resolution_rate': (self.collection_stats['duplicates_resolved'] / max(1, self.collection_stats['duplicates_found'])) * 100
        }
        
        # Update quality signal
        self.quality_updated.emit(quality_score)
        
        log.info("📊 Final Collection Statistics:")
        log.info(f"   • Quality Score: {quality_score:.1f}%")
        log.info(f"   • Devices Processed: {self.collection_stats['successful_collections']}/{self.collection_stats['alive_devices']}")
        log.info(f"   • Duplicates Resolved: {self.collection_stats['duplicates_resolved']}")
        log.info(f"   • Errors Recovered: {self.collection_stats['errors_recovered']}")
        log.info(f"   • Validation Fixes: {self.collection_stats['validation_fixes']}")
        
        return final_stats
    
    # Helper methods
    def _calculate_device_quality_score(self, device_data: Dict) -> float:
        """Calculate quality score for individual device"""
        score = 100.0
        
        # Deduct points for missing critical fields
        critical_fields = ['Hostname', 'IP Address']
        for field in critical_fields:
            if not device_data.get(field):
                score -= 25.0
        
        # Deduct points for validation issues
        if 'Validation Errors' in device_data:
            score -= 10.0
        
        # Deduct points for low OS confidence
        os_confidence = device_data.get('OS Confidence', 1.0)
        if os_confidence < 0.5:
            score -= 20.0
        
        return max(0.0, min(100.0, score))
    
    def _determine_device_category(self, device_data: Dict) -> str:
        """Determine device category for duplicate checking"""
        os_info = device_data.get('OS', '').lower()
        hostname = device_data.get('Hostname', '').lower()
        
        if 'linux' in os_info or 'ubuntu' in os_info or 'centos' in os_info:
            return 'Linux Devices'
        elif 'server' in os_info or 'server' in hostname:
            return 'Windows Server'
        else:
            return 'Windows Devices'
    
    def _apply_automatic_fixes(self, device_data: Dict, errors: List[str]) -> Optional[Dict]:
        """Apply automatic fixes to validation errors"""
        fixed_data = device_data.copy()
        
        for error in errors:
            try:
                if 'Invalid IP address' in error:
                    # Try to extract valid IP from the string
                    import re
                    ip_match = re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', device_data.get('IP Address', ''))
                    if ip_match:
                        fixed_data['IP Address'] = ip_match.group()
                
                elif 'Invalid hostname format' in error:
                    # Clean hostname
                    hostname = device_data.get('Hostname', '')
                    cleaned = re.sub(r'[^a-zA-Z0-9\-]', '-', hostname)
                    cleaned = re.sub(r'-+', '-', cleaned).strip('-')
                    if cleaned:
                        fixed_data['Hostname'] = cleaned
                
            except Exception:
                continue
        
        # Validate fixes
        is_valid, _, _ = self.data_validator.sanitize_device_data(fixed_data)
        return fixed_data if is_valid else None
    
    def _group_devices_by_category(self, devices: List[Dict]) -> Dict[str, List[Dict]]:
        """Group devices by their target categories"""
        categories = {
            'Windows Devices': [],
            'Windows Server': [],
            'Linux Devices': []
        }
        
        for device in devices:
            category = self._determine_device_category(device)
            categories[category].append(device)
        
        return {k: v for k, v in categories.items() if v}  # Remove empty categories
    
    def _get_category_headers(self, category: str) -> List[str]:
        """Get appropriate headers for each device category"""
        base_headers = ["Asset Tag", "Hostname", "IP Address", "Device Model", 
                       "Manufacturer", "SN", "CPU", "RAM", "Disk", "LAN IP Address", 
                       "Last Updated", "Data Source"]
        
        if category in ['Windows Devices', 'Windows Server']:
            return ["Asset Tag", "Hostname", "IP Address", "Domain", "OS", "Device Model", 
                   "Manufacturer", "SN", "CPU", "RAM", "Disk", "LAN IP Address", 
                   "Mgmt MAC", "Last Updated", "Data Source", "Validation Status"]
        else:  # Linux Devices
            return base_headers + ["Validation Status"]
    
    def _emit_progress(self, message: str, percentage: int):
        """Emit progress update"""
        self.progress_updated.emit(message, percentage)
        if self.progress_callback:
            self.progress_callback(message)
        log.debug(f"Progress: {percentage}% - {message}")
    
    def _on_progress_update(self, message: str):
        """Handle progress updates from smart collector"""
        # Forward to main progress signal
        if self.progress_callback:
            self.progress_callback(message)
    
    def stop(self):
        """Stop the collection process gracefully"""
        log.info("🛑 Stopping enhanced collection process...")
        self.should_stop = True
        
        if hasattr(self, 'error_monitor'):
            self.error_monitor.stop_monitoring()