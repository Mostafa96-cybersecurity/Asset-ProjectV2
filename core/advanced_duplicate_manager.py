# -*- coding: utf-8 -*-
"""
Advanced Duplicate Prevention & Error Handling
----------------------------------------------
- Multi-level duplicate detection
- Data validation and sanitization  
- Error recovery mechanisms
- Conflict resolution
"""

import hashlib
import re
from typing import Dict, List, Optional, Tuple, Set
from datetime import datetime
import logging

log = logging.getLogger(__name__)

class DuplicateManager:
    def __init__(self):
        self.device_fingerprints = {}
        self.seen_devices = set()
        self.conflict_resolution_rules = {
            'hostname': 'newer',      # Use newer data for hostname conflicts
            'ip_address': 'manual',   # Manual entry wins over scan
            'asset_tag': 'existing',  # Keep existing asset tag
            'serial': 'longer',       # Use longer/more complete serial
        }
    
    def generate_device_fingerprint(self, device_data: Dict) -> str:
        """Generate unique fingerprint for device identification"""
        # Collect ALL available identifiers
        identifiers = []
        
        # 1. Serial Number (most reliable unique identifier)
        serial = device_data.get('SN', device_data.get('Serial Number', device_data.get('sn', ''))).strip()
        if serial and len(serial) > 4:  # Valid serial should be longer than 4 chars
            identifiers.append(f"SN:{serial}")
        
        # 2. MAC Address (hardware-based unique identifier)
        mac = device_data.get('MAC Address', device_data.get('Mgmt MAC', device_data.get('mac_address', ''))).strip()
        if mac and self._is_valid_mac(mac):
            identifiers.append(f"MAC:{mac}")
        
        # 3. Hostname + IP combination (network-based identification)
        hostname = device_data.get('Hostname', device_data.get('hostname', '')).strip().lower()  # Normalize case
        ip = device_data.get('IP Address', device_data.get('LAN IP Address', device_data.get('ip_address', ''))).strip()
        if hostname and ip:
            identifiers.append(f"HOST:{hostname}@{ip}")
        elif ip:
            identifiers.append(f"IP:{ip}")
        
        # 4. Asset Tag (administrative identifier - less reliable for duplicates)
        asset_tag = device_data.get('Asset Tag', device_data.get('asset_tag', '')).strip()
        if asset_tag:
            identifiers.append(f"TAG:{asset_tag}")
        
        # 5. Hardware signature (Model + Manufacturer)
        model = device_data.get('Model/Vendor', device_data.get('Device Model', device_data.get('model_vendor', ''))).strip()
        manufacturer = device_data.get('Manufacturer', device_data.get('manufacturer', '')).strip()
        if model or manufacturer:
            identifiers.append(f"HW:{manufacturer}:{model}")
        
        # Create fingerprint using the most reliable identifier available
        if not identifiers:
            # Fallback: use IP if available
            if ip:
                return hashlib.md5(f"FALLBACK:{ip}".encode()).hexdigest()[:16]
            else:
                return hashlib.md5(f"UNKNOWN:{datetime.now()}".encode()).hexdigest()[:16]
        
        # Use the FIRST available identifier (now ordered by reliability)
        # Serial Number > MAC Address > Hostname+IP > Asset Tag > Hardware Signature
        primary_id = identifiers[0]
        return hashlib.md5(primary_id.encode()).hexdigest()[:16]
    
    def _is_valid_mac(self, mac: str) -> bool:
        """Validate MAC address format"""
        mac_pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
        return bool(re.match(mac_pattern, mac))
    
    def check_duplicate(self, device_data: Dict, sheet_name: str) -> Tuple[bool, Optional[Dict]]:
        """
        Check if device is duplicate and return conflict info
        Returns: (is_duplicate, existing_device_info)
        """
        fingerprint = self.generate_device_fingerprint(device_data)
        
        if fingerprint in self.device_fingerprints:
            existing = self.device_fingerprints[fingerprint]
            log.warning(f"Duplicate detected: {fingerprint} in {sheet_name}")
            return True, existing
        
        # Store new device
        self.device_fingerprints[fingerprint] = {
            'data': device_data.copy(),
            'sheet': sheet_name,
            'timestamp': datetime.now(),
            'fingerprint': fingerprint
        }
        
        return False, None
    
    def resolve_conflict(self, new_data: Dict, existing_data: Dict, field: str) -> str:
        """Resolve conflicts between new and existing data"""
        new_value = new_data.get(field, '').strip()
        existing_value = existing_data.get(field, '').strip()
        
        if not new_value:
            return existing_value
        if not existing_value:
            return new_value
        
        rule = self.conflict_resolution_rules.get(field, 'newer')
        
        if rule == 'newer':
            return new_value  # Prefer newer data
        elif rule == 'manual':
            # Check if existing is from manual entry
            if existing_data.get('Data Source', '').startswith('Manual'):
                return existing_value
            return new_value
        elif rule == 'existing':
            return existing_value
        elif rule == 'longer':
            return new_value if len(new_value) > len(existing_value) else existing_value
        
        return new_value  # Default: use newer
    
    def merge_device_data(self, new_data: Dict, existing_info: Dict) -> Dict:
        """Intelligently merge new and existing device data"""
        existing_data = existing_info['data']
        merged_data = existing_data.copy()
        
        # Merge fields with conflict resolution
        for field in new_data:
            if field in merged_data:
                merged_data[field] = self.resolve_conflict(new_data, existing_data, field)
            else:
                merged_data[field] = new_data[field]
        
        # Update metadata
        merged_data['Last Updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        merged_data['Data Source'] = f"{existing_data.get('Data Source', '')}, {new_data.get('Data Source', '')}"
        
        # Update our tracking
        fingerprint = existing_info['fingerprint']
        self.device_fingerprints[fingerprint]['data'] = merged_data
        self.device_fingerprints[fingerprint]['timestamp'] = datetime.now()
        
        log.info(f"Merged duplicate device: {merged_data.get('Hostname', 'Unknown')}")
        return merged_data


class DataValidator:
    """Enhanced data validation with sanitization"""
    
    def __init__(self):
        self.validation_rules = {
            'ip_address': self._validate_ip_address,
            'hostname': self._validate_hostname,
            'asset_tag': self._validate_asset_tag,
            'mac_address': self._validate_mac_address,
        }
        
        # Field name mappings for flexibility
        self.field_mappings = {
            'Hostname': 'hostname',
            'IP Address': 'ip_address', 
            'LAN IP Address': 'ip_address',
            'Asset Tag': 'asset_tag',
            'SN': 'sn',
            'Serial Number': 'sn',
            'MAC Address': 'mac_address',
            'Model/Vendor': 'model_vendor',
            'Device Model': 'model_vendor',
            'Manufacturer': 'manufacturer',
            'Working User': 'working_user',
            'Domain': 'domain_name',
            'OS Name': 'firmware_os_version',
            'Installed RAM (GB)': 'installed_ram_gb',
            'Storage': 'storage_info',
            'Processor': 'processor_info',
            'System SKU': 'system_sku',
            'Active GPU': 'active_gpu',
            'Connected Screens': 'connected_screens',
            'Data Source': 'data_source'
        }
    
    def sanitize_device_data(self, data: Dict) -> Tuple[bool, Dict, List[str]]:
        """Sanitize and validate device data with flexible field mapping"""
        errors = []
        sanitized = {}
        
        # Step 1: Map field names to standard format
        for key, value in data.items():
            standard_key = self.field_mappings.get(key, key.lower().replace(' ', '_'))
            sanitized[standard_key] = value
            
        # Step 2: Apply validation rules
        for field, validator in self.validation_rules.items():
            if field in sanitized:
                is_valid, cleaned_value, error_msg = validator(sanitized[field])
                if not is_valid:
                    errors.append(f"Field '{field}': {error_msg}")
                else:
                    sanitized[field] = cleaned_value
        
        # Step 3: Set default values for missing critical fields
        defaults = {
            'hostname': sanitized.get('ip_address', 'Unknown'),
            'ip_address': '0.0.0.0',
            'device_type': 'workstation',
            'status': 'Active',
            'data_source': 'Manual Entry'
        }
        
        for key, default_value in defaults.items():
            if key not in sanitized or not sanitized[key]:
                sanitized[key] = default_value
        
        is_valid = len(errors) == 0
        return is_valid, sanitized, errors
    
    def _validate_ip_address(self, ip: str) -> Tuple[bool, str, str]:
        """Validate and normalize IP address"""
        if not ip or not isinstance(ip, str):
            return False, "", "Empty IP address"
        
        ip = ip.strip()
        
        # IPv4 validation
        try:
            import ipaddress
            ipaddress.IPv4Address(ip)
            return True, ip, ""
        except Exception:
            return False, ip, f"Invalid IPv4 address: {ip}"
    
    def _validate_hostname(self, hostname: str) -> Tuple[bool, str, str]:
        """Validate and sanitize hostname"""
        if not hostname or not isinstance(hostname, str):
            return False, "", "Empty hostname"
        
        hostname = hostname.strip()
        
        # Basic hostname validation
        if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?$', hostname):
            # Try to sanitize
            sanitized = re.sub(r'[^a-zA-Z0-9\-]', '-', hostname)
            sanitized = re.sub(r'-+', '-', sanitized).strip('-')
            
            if sanitized and len(sanitized) <= 63:
                return True, sanitized, ""
            else:
                return False, hostname, f"Invalid hostname format: {hostname}"
        
        return True, hostname, ""
    
    def _validate_asset_tag(self, asset_tag: str) -> Tuple[bool, str, str]:
        """Validate and sanitize asset tag"""
        if not asset_tag or not isinstance(asset_tag, str):
            return True, "", ""  # Asset tag is optional
        
        asset_tag = asset_tag.strip().upper()
        
        # Remove invalid characters
        sanitized = re.sub(r'[^a-zA-Z0-9\-_]', '', asset_tag)
        
        if len(sanitized) > 50:  # Reasonable limit
            sanitized = sanitized[:50]
        
        return True, sanitized, ""
    
    def _validate_mac_address(self, mac: str) -> Tuple[bool, str, str]:
        """Validate and normalize MAC address"""
        if not mac or not isinstance(mac, str):
            return True, "", ""  # MAC is optional
        
        mac = mac.strip().upper()
        
        # Normalize MAC format
        mac = re.sub(r'[^0-9A-F]', '', mac)
        if len(mac) == 12:
            formatted_mac = ':'.join([mac[i:i+2] for i in range(0, 12, 2)])
            return True, formatted_mac, ""
        else:
            return False, mac, f"Invalid MAC address format: {mac}"
    
    @staticmethod
    def validate_ip_address(ip: str) -> Tuple[bool, str]:
        """Validate and normalize IP address"""
        if not ip or not isinstance(ip, str):
            return False, "Empty IP address"
        
        ip = ip.strip()
        
        # IPv4 validation
        try:
            import ipaddress
            ipaddress.IPv4Address(ip)
            return True, ip
        except Exception:
            return False, f"Invalid IPv4 address: {ip}"
    
    @staticmethod
    def validate_hostname(hostname: str) -> Tuple[bool, str]:
        """Validate and sanitize hostname"""
        if not hostname or not isinstance(hostname, str):
            return False, "Empty hostname"
        
        hostname = hostname.strip()
        
        # Basic hostname validation
        if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?$', hostname):
            # Try to sanitize
            sanitized = re.sub(r'[^a-zA-Z0-9\-]', '-', hostname)
            sanitized = re.sub(r'-+', '-', sanitized).strip('-')
            
            if sanitized and len(sanitized) <= 63:
                return True, sanitized
            else:
                return False, f"Invalid hostname format: {hostname}"
        
        return True, hostname
    
    @staticmethod
    def validate_asset_tag(asset_tag: str) -> Tuple[bool, str]:
        """Validate and sanitize asset tag"""
        if not asset_tag or not isinstance(asset_tag, str):
            return True, ""  # Asset tag is optional
        
        asset_tag = asset_tag.strip().upper()
        
        # Asset tag should be alphanumeric with some special chars
        if re.match(r'^[A-Z0-9\-_]+$', asset_tag):
            return True, asset_tag
        
        # Try to sanitize
        sanitized = re.sub(r'[^A-Z0-9\-_]', '', asset_tag)
        if sanitized:
            return True, sanitized
        
        return False, f"Invalid asset tag format: {asset_tag}"
    
    @staticmethod
    def sanitize_device_data(device_data: Dict) -> Tuple[bool, Dict, List[str]]:
        """Sanitize all device data and return validation results"""
        sanitized_data = {}
        errors = []
        
        # Validate critical fields
        for field, value in device_data.items():
            if not isinstance(value, str):
                value = str(value) if value is not None else ""
            
            # Apply field-specific validation
            if field in ['IP Address', 'LAN IP Address']:
                is_valid, result = DataValidator.validate_ip_address(value)
                if is_valid:
                    sanitized_data[field] = result
                else:
                    errors.append(f"{field}: {result}")
            
            elif field == 'Hostname':
                is_valid, result = DataValidator.validate_hostname(value)
                if is_valid:
                    sanitized_data[field] = result
                else:
                    errors.append(f"{field}: {result}")
            
            elif field == 'Asset Tag':
                is_valid, result = DataValidator.validate_asset_tag(value)
                if is_valid:
                    sanitized_data[field] = result
                else:
                    errors.append(f"{field}: {result}")
            
            else:
                # Generic sanitization
                sanitized_value = value.strip() if value else ""
                # Remove null bytes and control characters
                sanitized_value = re.sub(r'[\x00-\x1f\x7f]', '', sanitized_value)
                sanitized_data[field] = sanitized_value
        
        # Ensure required fields exist
        required_fields = ['Hostname', 'IP Address']
        for field in required_fields:
            if field not in sanitized_data or not sanitized_data[field]:
                errors.append(f"Missing required field: {field}")
        
        is_valid = len(errors) == 0
        return is_valid, sanitized_data, errors


class ErrorRecovery:
    """Advanced error recovery mechanisms"""
    
    def __init__(self):
        self.retry_attempts = 3
        self.backoff_factor = 2
        self.recoverable_errors = {
            'network_timeout': True,
            'wmi_connection': True,
            'ssh_connection': True,
            'excel_locked': True,
            'database_busy': True,
        }
    
    def is_recoverable_error(self, error: Exception) -> bool:
        """Determine if an error is recoverable"""
        error_str = str(error).lower()
        
        if 'timeout' in error_str:
            return True
        if 'connection' in error_str and 'refused' in error_str:
            return True
        if 'permission' in error_str and 'excel' in error_str:
            return True
        if 'database is locked' in error_str:
            return True
        if 'wmi' in error_str and 'rpc' in error_str:
            return True
        
        return False
    
    def get_recovery_actions(self, error_category: str) -> List[str]:
        """Get available recovery actions for error category"""
        actions = []
        
        recovery_map = {
            'network': [
                "Retry with increased timeout",
                "Try alternative connection method", 
                "Skip device and continue collection",
                "Use cached data if available"
            ],
            'database': [
                "Retry database operation",
                "Check database connection",
                "Verify schema integrity", 
                "Store data temporarily for later retry"
            ],
            'validation': [
                "Apply data sanitization",
                "Use default values for missing fields",
                "Flag data for manual review",
                "Continue with partial data"
            ],
            'integration': [
                "Check component dependencies",
                "Restart failed components", 
                "Use fallback mechanisms",
                "Continue with limited functionality"
            ]
        }
        
        if error_category in recovery_map:
            actions.extend(recovery_map[error_category])
        
        # Generic recovery actions
        actions.extend([
            "Retry operation with exponential backoff",
            "Log error for manual review",
            "Continue with degraded functionality"
        ])
        
        return actions
    
    def retry_with_backoff(self, func, *args, **kwargs):
        """Retry function with exponential backoff"""
        import time
        
        for attempt in range(self.retry_attempts):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if not self.is_recoverable_error(e) or attempt == self.retry_attempts - 1:
                    raise
                
                wait_time = (self.backoff_factor ** attempt)
                log.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
        
        raise Exception(f"All {self.retry_attempts} attempts failed")


class ConflictResolver:
    """Handle data conflicts intelligently"""
    
    def __init__(self):
        self.resolution_strategies = {
            'asset_tag': self._resolve_asset_tag,
            'hostname': self._resolve_hostname,
            'ip_address': self._resolve_ip_address,
            'serial_number': self._resolve_serial_number,
        }
    
    def _resolve_asset_tag(self, existing: str, new: str, context: Dict) -> str:
        """Resolve asset tag conflicts"""
        # Asset tags from manual entry always win
        if context.get('existing_source') == 'Manual Entry':
            return existing
        if context.get('new_source') == 'Manual Entry':
            return new
        
        # Keep existing if it exists
        return existing if existing else new
    
    def _resolve_hostname(self, existing: str, new: str, context: Dict) -> str:
        """Resolve hostname conflicts"""
        # Prefer more descriptive hostnames
        if len(new) > len(existing) and new.lower() != 'unknown':
            return new
        return existing if existing.lower() != 'unknown' else new
    
    def _resolve_ip_address(self, existing: str, new: str, context: Dict) -> str:
        """Resolve IP address conflicts"""
        # This shouldn't happen, but if it does, prefer newer
        return new
    
    def _resolve_serial_number(self, existing: str, new: str, context: Dict) -> str:
        """Resolve serial number conflicts"""
        # Prefer longer, more complete serial numbers
        if not existing:
            return new
        if not new:
            return existing
        
        # Remove common placeholders
        placeholders = ['unknown', 'n/a', 'not available', '0000000', 'default']
        
        existing_clean = existing.lower().strip()
        new_clean = new.lower().strip()
        
        if existing_clean in placeholders:
            return new
        if new_clean in placeholders:
            return existing
        
        # Prefer longer serial
        return new if len(new) > len(existing) else existing
    
    def resolve_field_conflict(self, field: str, existing: str, new: str, context: Dict = None) -> str:
        """Resolve specific field conflicts"""
        context = context or {}
        
        if field in self.resolution_strategies:
            return self.resolution_strategies[field](existing, new, context)
        
        # Default: prefer non-empty, newer values
        if not existing:
            return new
        if not new:
            return existing
        
        # If both exist, prefer newer (from context timestamp)
        return new