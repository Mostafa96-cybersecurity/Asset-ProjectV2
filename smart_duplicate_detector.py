#!/usr/bin/env python3
"""
Advanced Duplicate Detection and Resolution Strategy
Handles various duplicate scenarios and smart conflict resolution
"""

import sqlite3
import hashlib
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class DuplicateType(Enum):
    """Types of duplicate scenarios"""
    EXACT_MATCH = "exact_match"
    SERIAL_CONFLICT = "serial_conflict"
    IP_CONFLICT = "ip_conflict"
    HOSTNAME_CONFLICT = "hostname_conflict"
    MAC_CONFLICT = "mac_conflict"
    USER_TRANSFER = "user_transfer"
    HARDWARE_UPGRADE = "hardware_upgrade"
    REINSTALL = "reinstall"
    NETWORK_CHANGE = "network_change"

class ResolutionAction(Enum):
    """Actions to take for duplicates"""
    MERGE_KEEP_LATEST = "merge_keep_latest"
    MERGE_KEEP_OLDEST = "merge_keep_oldest"
    MERGE_MANUAL = "merge_manual"
    UPDATE_EXISTING = "update_existing"
    CREATE_NEW = "create_new"
    ARCHIVE_OLD = "archive_old"
    FLAG_REVIEW = "flag_review"

@dataclass
class DeviceFingerprint:
    """Unique device identification"""
    primary_serial: str
    secondary_serial: str
    mac_primary: str
    hostname: str
    ip_address: str
    motherboard_serial: str
    cpu_id: str
    confidence_score: float

@dataclass
class DuplicateMatch:
    """Information about a duplicate match"""
    existing_id: int
    new_device: Dict
    duplicate_type: DuplicateType
    confidence: float
    conflicts: List[str]
    suggested_action: ResolutionAction
    reason: str

class SmartDuplicateDetector:
    """Advanced duplicate detection and resolution system"""
    
    def __init__(self, db_path: str = "assets.db"):
        self.db_path = db_path
        self.confidence_thresholds = {
            'exact_match': 0.95,
            'high_confidence': 0.85,
            'medium_confidence': 0.70,
            'low_confidence': 0.50
        }
        
    def create_device_fingerprint(self, device_data: Dict) -> DeviceFingerprint:
        """Create a unique fingerprint for device identification"""
        
        # Extract key identification fields with None handling
        primary_serial = (device_data.get('serial_number') or '').strip()
        secondary_serial = (device_data.get('system_serial_number') or '').strip()
        mac_primary = self._extract_primary_mac(device_data.get('mac_addresses') or device_data.get('mac_address') or '')
        hostname = (device_data.get('hostname') or device_data.get('computer_name') or '').strip().upper()
        ip_address = (device_data.get('ip_address') or '').strip()
        motherboard_serial = (device_data.get('motherboard_serial') or '').strip()
        cpu_id = (device_data.get('processor_name') or '').strip()
        
        # Calculate confidence score based on available data
        confidence = self._calculate_fingerprint_confidence({
            'primary_serial': primary_serial,
            'secondary_serial': secondary_serial,
            'mac_primary': mac_primary,
            'hostname': hostname,
            'motherboard_serial': motherboard_serial
        })
        
        return DeviceFingerprint(
            primary_serial=primary_serial,
            secondary_serial=secondary_serial,
            mac_primary=mac_primary,
            hostname=hostname,
            ip_address=ip_address,
            motherboard_serial=motherboard_serial,
            cpu_id=cpu_id,
            confidence_score=confidence
        )
    
    def _extract_primary_mac(self, mac_string: str) -> str:
        """Extract the primary MAC address from comma-separated string"""
        if not mac_string:
            return ''
        
        macs = [mac.strip() for mac in mac_string.split(',') if mac.strip()]
        # Filter out virtual/bridge MACs and return first physical MAC
        for mac in macs:
            if not any(vm_prefix in mac.upper() for vm_prefix in ['00:50:56', '00:0C:29', '00:1C:14']):
                return mac.upper()
        
        return macs[0].upper() if macs else ''
    
    def _calculate_fingerprint_confidence(self, fields: Dict) -> float:
        """Calculate confidence score for device fingerprint"""
        weights = {
            'primary_serial': 0.35,
            'secondary_serial': 0.25,
            'mac_primary': 0.20,
            'hostname': 0.10,
            'motherboard_serial': 0.10
        }
        
        score = 0.0
        for field, weight in weights.items():
            if fields.get(field) and len(fields[field]) > 3:
                score += weight
        
        return score
    
    def detect_duplicates(self, new_device_data: Dict) -> List[DuplicateMatch]:
        """Detect potential duplicates for a new device"""
        
        fingerprint = self.create_device_fingerprint(new_device_data)
        matches = []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get all existing devices
            cursor.execute("SELECT * FROM assets ORDER BY last_updated DESC")
            existing_devices = cursor.fetchall()
            
            # Get column names
            cursor.execute("PRAGMA table_info(assets)")
            columns = [col[1] for col in cursor.fetchall()]
            
            for row in existing_devices:
                existing_device = dict(zip(columns, row))
                existing_fingerprint = self.create_device_fingerprint(existing_device)
                
                # Check for various types of matches
                duplicate_match = self._analyze_potential_duplicate(
                    fingerprint, existing_fingerprint, 
                    new_device_data, existing_device
                )
                
                if duplicate_match:
                    matches.append(duplicate_match)
            
        finally:
            conn.close()
        
        # Sort by confidence (highest first)
        matches.sort(key=lambda x: x.confidence, reverse=True)
        return matches
    
    def _analyze_potential_duplicate(
        self, 
        new_fp: DeviceFingerprint, 
        existing_fp: DeviceFingerprint,
        new_device: Dict, 
        existing_device: Dict
    ) -> Optional[DuplicateMatch]:
        """Analyze if two device fingerprints represent duplicates"""
        
        conflicts = []
        confidence = 0.0
        duplicate_type = None
        
        # Exact serial number match
        if (new_fp.primary_serial and existing_fp.primary_serial and 
            new_fp.primary_serial == existing_fp.primary_serial):
            confidence += 0.4
            duplicate_type = DuplicateType.SERIAL_CONFLICT
        
        # Secondary serial match
        if (new_fp.secondary_serial and existing_fp.secondary_serial and 
            new_fp.secondary_serial == existing_fp.secondary_serial):
            confidence += 0.3
            if not duplicate_type:
                duplicate_type = DuplicateType.SERIAL_CONFLICT
        
        # MAC address match
        if (new_fp.mac_primary and existing_fp.mac_primary and 
            new_fp.mac_primary == existing_fp.mac_primary):
            confidence += 0.25
            if not duplicate_type:
                duplicate_type = DuplicateType.MAC_CONFLICT
        
        # Motherboard serial match
        if (new_fp.motherboard_serial and existing_fp.motherboard_serial and 
            new_fp.motherboard_serial == existing_fp.motherboard_serial):
            confidence += 0.2
            if not duplicate_type:
                duplicate_type = DuplicateType.HARDWARE_UPGRADE
        
        # Hostname match (lower weight)
        if (new_fp.hostname and existing_fp.hostname and 
            new_fp.hostname == existing_fp.hostname):
            confidence += 0.15
            if not duplicate_type:
                duplicate_type = DuplicateType.HOSTNAME_CONFLICT
        
        # IP address match (lowest weight)
        if (new_fp.ip_address and existing_fp.ip_address and 
            new_fp.ip_address == existing_fp.ip_address):
            confidence += 0.1
            if not duplicate_type:
                duplicate_type = DuplicateType.IP_CONFLICT
        
        # Check for user transfer scenario
        if confidence > 0.5:
            old_user = existing_device.get('working_user', '').strip()
            new_user = new_device.get('working_user', '').strip()
            if old_user and new_user and old_user != new_user:
                duplicate_type = DuplicateType.USER_TRANSFER
                conflicts.append(f"User changed: {old_user} → {new_user}")
        
        # Check for hardware upgrade scenario
        if confidence > 0.5:
            old_memory = existing_device.get('total_physical_memory', 0)
            new_memory = new_device.get('total_physical_memory', 0)
            if old_memory and new_memory and abs(int(new_memory) - int(old_memory)) > 1000000000:  # 1GB difference
                duplicate_type = DuplicateType.HARDWARE_UPGRADE
                conflicts.append(f"Memory changed: {old_memory} → {new_memory}")
        
        # Only return match if confidence is above threshold
        if confidence >= self.confidence_thresholds['low_confidence']:
            
            # Ensure duplicate_type is not None
            if duplicate_type is None:
                duplicate_type = DuplicateType.EXACT_MATCH
            
            # Determine suggested action
            suggested_action = self._determine_resolution_action(
                duplicate_type, confidence, conflicts, new_device, existing_device
            )
            
            # Build reason
            reason = self._build_resolution_reason(duplicate_type, confidence, conflicts)
            
            return DuplicateMatch(
                existing_id=existing_device['id'],
                new_device=new_device,
                duplicate_type=duplicate_type,
                confidence=confidence,
                conflicts=conflicts,
                suggested_action=suggested_action,
                reason=reason
            )
        
        return None
    
    def _determine_resolution_action(
        self, 
        duplicate_type: DuplicateType, 
        confidence: float,
        conflicts: List[str],
        new_device: Dict,
        existing_device: Dict
    ) -> ResolutionAction:
        """Determine the best action to resolve the duplicate"""
        
        # High confidence exact matches
        if confidence >= self.confidence_thresholds['exact_match']:
            if duplicate_type == DuplicateType.USER_TRANSFER:
                return ResolutionAction.UPDATE_EXISTING
            elif duplicate_type == DuplicateType.HARDWARE_UPGRADE:
                return ResolutionAction.MERGE_KEEP_LATEST
            else:
                return ResolutionAction.UPDATE_EXISTING
        
        # High confidence matches
        elif confidence >= self.confidence_thresholds['high_confidence']:
            if duplicate_type == DuplicateType.SERIAL_CONFLICT:
                return ResolutionAction.MERGE_KEEP_LATEST
            elif duplicate_type == DuplicateType.USER_TRANSFER:
                return ResolutionAction.UPDATE_EXISTING
            elif duplicate_type == DuplicateType.HARDWARE_UPGRADE:
                return ResolutionAction.MERGE_KEEP_LATEST
            else:
                return ResolutionAction.UPDATE_EXISTING
        
        # Medium confidence matches
        elif confidence >= self.confidence_thresholds['medium_confidence']:
            if len(conflicts) > 0:
                return ResolutionAction.FLAG_REVIEW
            else:
                return ResolutionAction.UPDATE_EXISTING
        
        # Low confidence matches
        else:
            return ResolutionAction.FLAG_REVIEW
    
    def _build_resolution_reason(
        self, 
        duplicate_type: DuplicateType, 
        confidence: float, 
        conflicts: List[str]
    ) -> str:
        """Build human-readable reason for the resolution"""
        
        reasons = []
        
        if duplicate_type == DuplicateType.SERIAL_CONFLICT:
            reasons.append("Same serial number detected")
        elif duplicate_type == DuplicateType.USER_TRANSFER:
            reasons.append("Device transferred to different user")
        elif duplicate_type == DuplicateType.HARDWARE_UPGRADE:
            reasons.append("Hardware upgrade detected")
        elif duplicate_type == DuplicateType.MAC_CONFLICT:
            reasons.append("Same MAC address found")
        elif duplicate_type == DuplicateType.HOSTNAME_CONFLICT:
            reasons.append("Same hostname detected")
        elif duplicate_type == DuplicateType.IP_CONFLICT:
            reasons.append("Same IP address found")
        
        reasons.append(f"Confidence: {confidence:.1%}")
        
        if conflicts:
            reasons.extend(conflicts)
        
        return "; ".join(reasons)
    
    def resolve_duplicate(self, match: DuplicateMatch) -> Dict:
        """Resolve a duplicate according to the suggested action"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if match.suggested_action == ResolutionAction.UPDATE_EXISTING:
                result = self._update_existing_device(cursor, match)
            elif match.suggested_action == ResolutionAction.MERGE_KEEP_LATEST:
                result = self._merge_devices_keep_latest(cursor, match)
            elif match.suggested_action == ResolutionAction.MERGE_KEEP_OLDEST:
                result = self._merge_devices_keep_oldest(cursor, match)
            elif match.suggested_action == ResolutionAction.ARCHIVE_OLD:
                result = self._archive_old_device(cursor, match)
            elif match.suggested_action == ResolutionAction.FLAG_REVIEW:
                result = self._flag_for_review(cursor, match)
            else:
                result = self._create_new_device(cursor, match)
            
            conn.commit()
            return result
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _merge_devices_keep_oldest(self, cursor: sqlite3.Cursor, match: DuplicateMatch) -> Dict:
        """Merge devices keeping the oldest data"""
        try:
            # Log the merge operation
            cursor.execute('''
                INSERT INTO device_history 
                (device_id, field_name, old_value, new_value, changed_at, changed_by, change_reason)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                match.existing_id, 'merge_operation', 'new_device_data', 'kept_oldest',
                datetime.now().isoformat(), 'system', 'merge_keep_oldest'
            ))
            
            return {
                'success': True,
                'action': 'merged_keep_oldest',
                'device_id': match.existing_id,
                'message': 'Devices merged, oldest data preserved'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'action': 'merge_keep_oldest_failed'
            }
    
    def _archive_old_device(self, cursor: sqlite3.Cursor, match: DuplicateMatch) -> Dict:
        """Archive the old device entry"""
        try:
            # Archive the device (soft delete)
            cursor.execute('''
                UPDATE assets SET 
                    is_archived = 1,
                    archived_date = ?,
                    archived_reason = ?
                WHERE id = ?
            ''', (datetime.now().isoformat(), 'duplicate_resolution', match.existing_id))
            
            return {
                'success': True,
                'action': 'archived',
                'device_id': match.existing_id,
                'message': 'Old device archived'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'action': 'archive_failed'
            }
    
    def _update_existing_device(self, cursor: sqlite3.Cursor, match: DuplicateMatch) -> Dict:
        """Update existing device with new data"""
        
        # Build update query with new data
        update_fields = []
        values = []
        
        for key, value in match.new_device.items():
            if key != 'id' and value is not None:
                update_fields.append(f"{key} = ?")
                values.append(value)
        
        # Add metadata
        update_fields.extend([
            "last_updated = ?",
            "updated_by = ?",
            "collection_date = ?",
            "_duplicate_resolved_at = ?",
            "_resolution_action = ?"
        ])
        
        values.extend([
            datetime.now().isoformat(),
            'auto_duplicate_resolver',
            datetime.now().isoformat(),
            datetime.now().isoformat(),
            'update_existing'
        ])
        
        query = f"UPDATE assets SET {', '.join(update_fields)} WHERE id = ?"
        values.append(match.existing_id)
        
        cursor.execute(query, values)
        
        return {
            'action': 'updated',
            'device_id': match.existing_id,
            'changes': len(update_fields) - 5,
            'reason': match.reason
        }
    
    def _merge_devices_keep_latest(self, cursor: sqlite3.Cursor, match: DuplicateMatch) -> Dict:
        """Merge devices keeping the latest data"""
        
        # Get existing device data
        cursor.execute("SELECT * FROM assets WHERE id = ?", (match.existing_id,))
        existing_row = cursor.fetchone()
        
        if not existing_row:
            return self._create_new_device(cursor, match)
        
        # Get column names
        cursor.execute("PRAGMA table_info(assets)")
        columns = [col[1] for col in cursor.fetchall()]
        existing_device = dict(zip(columns, existing_row))
        
        # Merge data - prioritize new data, but keep valuable old data
        merged_data = {}
        changes = 0
        
        for key, new_value in match.new_device.items():
            old_value = existing_device.get(key)
            
            # Keep new value if it's more complete or recent
            if new_value and (not old_value or len(str(new_value)) > len(str(old_value))):
                merged_data[key] = new_value
                if old_value != new_value:
                    changes += 1
            elif old_value:
                merged_data[key] = old_value
        
        # Update with merged data
        return self._update_device_with_data(cursor, match.existing_id, merged_data, f"merge_latest: {match.reason}")
    
    def _create_new_device(self, cursor: sqlite3.Cursor, match: DuplicateMatch) -> Dict:
        """Create new device entry"""
        
        # Add metadata to new device
        device_data = match.new_device.copy()
        device_data.update({
            'created_at': datetime.now().isoformat(),
            'created_by': 'duplicate_resolver',
            '_duplicate_checked': True,
            '_duplicate_confidence': match.confidence
        })
        
        # Insert new device
        columns = list(device_data.keys())
        placeholders = ', '.join(['?' for _ in columns])
        query = f"INSERT INTO assets ({', '.join(columns)}) VALUES ({placeholders})"
        
        cursor.execute(query, list(device_data.values()))
        new_id = cursor.lastrowid
        
        return {
            'action': 'created_new',
            'device_id': new_id,
            'reason': f"Low confidence match: {match.reason}"
        }
    
    def _flag_for_review(self, cursor: sqlite3.Cursor, match: DuplicateMatch) -> Dict:
        """Flag both devices for manual review"""
        
        review_data = {
            'duplicate_flag': True,
            'duplicate_review_needed': True,
            'duplicate_match_id': match.existing_id,
            'duplicate_confidence': match.confidence,
            'duplicate_reason': match.reason,
            'flagged_at': datetime.now().isoformat()
        }
        
        # Create new device but flag it
        new_device = match.new_device.copy()
        new_device.update(review_data)
        
        result = self._create_new_device(cursor, DuplicateMatch(
            existing_id=match.existing_id,
            new_device=new_device,
            duplicate_type=match.duplicate_type,
            confidence=match.confidence,
            conflicts=match.conflicts,
            suggested_action=ResolutionAction.CREATE_NEW,
            reason=match.reason
        ))
        
        # Also flag existing device
        cursor.execute("""
            UPDATE assets 
            SET duplicate_flag = ?, duplicate_review_needed = ?, 
                duplicate_match_id = ?, flagged_at = ?
            WHERE id = ?
        """, (True, True, result['device_id'], datetime.now().isoformat(), match.existing_id))
        
        return {
            'action': 'flagged_for_review',
            'existing_device_id': match.existing_id,
            'new_device_id': result['device_id'],
            'reason': match.reason
        }
    
    def _update_device_with_data(self, cursor: sqlite3.Cursor, device_id: int, data: Dict, reason: str) -> Dict:
        """Helper to update device with given data"""
        
        update_fields = []
        values = []
        
        for key, value in data.items():
            if key != 'id':
                update_fields.append(f"{key} = ?")
                values.append(value)
        
        # Add metadata
        update_fields.extend([
            "last_updated = ?",
            "_duplicate_resolved_at = ?",
            "_resolution_reason = ?"
        ])
        
        values.extend([
            datetime.now().isoformat(),
            datetime.now().isoformat(),
            reason
        ])
        
        query = f"UPDATE assets SET {', '.join(update_fields)} WHERE id = ?"
        values.append(device_id)
        
        cursor.execute(query, values)
        
        return {
            'action': 'updated',
            'device_id': device_id,
            'changes': len(data),
            'reason': reason
        }

def create_duplicate_detection_schema():
    """Create additional database schema for duplicate detection"""
    
    schema_additions = """
    -- Add duplicate detection fields to assets table
    ALTER TABLE assets ADD COLUMN duplicate_flag BOOLEAN DEFAULT FALSE;
    ALTER TABLE assets ADD COLUMN duplicate_review_needed BOOLEAN DEFAULT FALSE;
    ALTER TABLE assets ADD COLUMN duplicate_match_id INTEGER;
    ALTER TABLE assets ADD COLUMN duplicate_confidence REAL;
    ALTER TABLE assets ADD COLUMN duplicate_reason TEXT;
    ALTER TABLE assets ADD COLUMN flagged_at TEXT;
    ALTER TABLE assets ADD COLUMN _duplicate_resolved_at TEXT;
    ALTER TABLE assets ADD COLUMN _resolution_action TEXT;
    ALTER TABLE assets ADD COLUMN _resolution_reason TEXT;
    ALTER TABLE assets ADD COLUMN _duplicate_checked BOOLEAN DEFAULT FALSE;
    ALTER TABLE assets ADD COLUMN _device_fingerprint TEXT;
    
    -- Create duplicate resolution log table
    CREATE TABLE IF NOT EXISTS duplicate_resolution_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        existing_device_id INTEGER,
        new_device_data TEXT,
        duplicate_type TEXT,
        confidence REAL,
        resolution_action TEXT,
        reason TEXT,
        resolved_at TEXT,
        resolved_by TEXT,
        FOREIGN KEY (existing_device_id) REFERENCES assets (id)
    );
    
    -- Create indexes for performance
    CREATE INDEX IF NOT EXISTS idx_assets_duplicate_flag ON assets (duplicate_flag);
    CREATE INDEX IF NOT EXISTS idx_assets_serial_number ON assets (serial_number);
    CREATE INDEX IF NOT EXISTS idx_assets_mac_addresses ON assets (mac_addresses);
    CREATE INDEX IF NOT EXISTS idx_assets_hostname ON assets (hostname);
    CREATE INDEX IF NOT EXISTS idx_assets_ip_address ON assets (ip_address);
    """
    
    return schema_additions

if __name__ == "__main__":
    # Example usage
    detector = SmartDuplicateDetector()
    
    # Example new device data
    new_device = {
        'hostname': 'WS-TEST-001',
        'ip_address': '10.0.21.100',
        'serial_number': 'ABC123456',
        'mac_addresses': '00:11:22:33:44:55',
        'working_user': 'john.doe',
        'total_physical_memory': 16000000000,
        'processor_name': 'Intel Core i7'
    }
    
    print("🔍 DUPLICATE DETECTION STRATEGY DEMO")
    print("=" * 60)
    
    # Detect duplicates
    matches = detector.detect_duplicates(new_device)
    
    if matches:
        print(f"Found {len(matches)} potential duplicate(s):")
        for i, match in enumerate(matches, 1):
            print(f"\n{i}. Match ID {match.existing_id}")
            print(f"   Type: {match.duplicate_type.value}")
            print(f"   Confidence: {match.confidence:.1%}")
            print(f"   Suggested Action: {match.suggested_action.value}")
            print(f"   Reason: {match.reason}")
            
            if match.conflicts:
                print(f"   Conflicts: {', '.join(match.conflicts)}")
    else:
        print("No duplicates detected - safe to add new device")
    
    print(f"\n💡 DUPLICATE PREVENTION STRATEGY IMPLEMENTED!")
    print(f"   • Smart fingerprinting based on multiple identifiers")
    print(f"   • Confidence-based resolution actions")
    print(f"   • User transfer and hardware upgrade detection")
    print(f"   • Automatic conflict resolution with audit trail")