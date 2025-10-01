# -*- coding: utf-8 -*-
from __future__ import annotations
import logging
from typing import Dict, Any, Optional, List, Tuple

from db.connection import connect
from db.models import bootstrap_schema

log = logging.getLogger(__name__)

# تبويبات الإدخال اليدوي ↔ نوع الجهاز
SHEET_TO_TYPE: Dict[str, Optional[str]] = {
    "Hypervisor": "hypervisor",
    "Switches": "switch",
    "Printers": "printer",
    "Access Points": "ap",
    "Fingerprint": "fingerprint",
    "Assets": None,  # شيت الاسكان له دالة خاصة
}

# خريطة أعمدة الشيتات اليدوية ↔ أعمدة جدول assets
BASE_MAP = {
    "Asset Tag": "asset_tag",
    "Hostname": "hostname",
    "IP Address": "ip_address",
    "Model/Vendor": "model_vendor",
    "Model": "model_vendor",
    "SN": "sn",
    "Location": "location",
    "Owner": "owner",
    "Department": "department",
    "Site": "site",
    "Building": "building",
    "Floor": "floor",
    "Room": "room",
    "Status": "status",
    "Firmware Version": "firmware_os_version",
    "Firmware/OS Version": "firmware_os_version",
    "Notes": "notes",
    "Data Source": "data_source",
    "Created At": "created_at",
    "Created By": "created_by",
    "Last Updated": "updated_at",
    "Last Updated By": "updated_by",
}

TYPE_SPECIFIC_MAP = {
    "hypervisor": {
        "Cluster":"cluster","vCenter":"vcenter",
        "CPU Sockets":"cpu_sockets","CPU Cores":"cpu_cores","CPU Threads":"cpu_threads",
        "Total RAM":"total_ram","Total CPU":"total_cpu","Storage":"storage",
        "VM Count":"vm_count","Management IP":"mgmt_ip","vMotion IP":"vmotion_ip",
        "Datastores (Total/Free)":"datastores_info",
    },
    "switch": {
        "Firmware Version":"firmware_version","Ports (Total)":"ports_total","PoE":"poe",
        "Mgmt VLAN":"mgmt_vlan","Uplink To":"uplink_to","Mgmt MAC":"mgmt_mac",
    },
    "printer": {
        "Firmware Version":"firmware_version","Page Counter (Total)":"page_total",
        "Page Counter (Mono)":"page_mono","Page Counter (Color)":"page_color",
        "Supplies Status":"supplies_status",
    },
    "ap": {
        "Controller":"controller","Adopted By":"adopted_by","SSID(s)":"ssids",
        "Bands":"bands","Channel":"channel","Tx Power":"tx_power","PoE Switch/Port":"poe_port",
    },
    "fingerprint": {
        "Controller/Server IP":"controller_ip","Door/Area Name":"door_area",
        "User Capacity":"user_capacity","Log Capacity":"log_capacity","Firmware Version":"firmware_version",
    },
}

# ----------------- Helpers -----------------

def _detect_match(conn, asset_tag: str, hostname: str, ip: str) -> Optional[int]:
    cur = conn.cursor()
    if asset_tag:
        cur.execute("SELECT id FROM assets WHERE asset_tag = ?", (asset_tag,))
        r = cur.fetchone()
        if r:
            return int(r[0])
    if hostname and ip:
        cur.execute("SELECT id FROM assets WHERE hostname = ? AND ip_address = ?", (hostname, ip))
        r = cur.fetchone()
        if r:
            return int(r[0])
    return None

def _table_for_type(device_type: str) -> Optional[str]:
    return {
        "hypervisor": "hypervisors",
        "switch": "switches",
        "printer": "printers",
        "ap": "access_points",
        "fingerprint": "fingerprints",
    }.get(device_type)

# ----------------- Public APIs -----------------

def upsert_from_sheet_row(sheet_name: str, row_dict: Dict[str, Any]) -> Optional[int]:
    """
    Upsert من تبويبات الإدخال اليدوي (Hypervisor / Switches / Printers / Access Points / Fingerprint).
    يُرجع asset_id أو None.
    """
    device_type = SHEET_TO_TYPE.get(sheet_name)
    if not device_type:
        return None

    bootstrap_schema()
    base = {v: (row_dict.get(k) or "").strip() for k, v in BASE_MAP.items() if k in row_dict}
    base.setdefault("device_type", device_type)

    host = base.get("hostname", "")
    ip   = base.get("ip_address", "")
    tag  = base.get("asset_tag", "")
    
    # Handle empty asset_tag to avoid UNIQUE constraint issues
    if not tag or tag.strip() == "":
        base["asset_tag"] = None

    try:
        with connect() as conn:
            asset_id = _detect_match(conn, tag, host, ip)
            cur = conn.cursor()

            if asset_id is None:
                cols = ["device_type"] + [c for c in base.keys() if c != "device_type"]
                vals = [base.get(c, "") if c != "asset_tag" else base.get(c) for c in cols]
                cur.execute(
                    f"INSERT INTO assets ({','.join(cols)}) VALUES ({','.join(['?']*len(vals))})",
                    vals
                )
                asset_id = int(cur.lastrowid)
            else:
                sets = ",".join([f"{c}=?" for c in base.keys()])
                cur.execute(
                    f"UPDATE assets SET {sets} WHERE id=?",
                    [base[k] for k in base.keys()] + [asset_id]
                )

            # جدول النوع
            spec_map = TYPE_SPECIFIC_MAP[device_type]
            spec = {v: (row_dict.get(k) or "").strip() for k, v in spec_map.items() if k in row_dict}
            table = _table_for_type(device_type)
            if table and spec:
                cols = list(spec.keys())
                cur.execute(
                    f"UPDATE {table} SET {','.join([f'{c}=?' for c in cols])} WHERE asset_id=?",
                    [spec[c] for c in cols] + [asset_id]
                )
                if cur.rowcount == 0:
                    cur.execute(
                        f"INSERT INTO {table} (asset_id,{','.join(cols)}) VALUES ({','.join(['?']*(len(cols)+1))})",
                        [asset_id] + [spec[c] for c in cols]
                    )
            return asset_id
    except Exception as e:
        log.exception("DB upsert (manual sheet=%s) failed: %s", sheet_name, e)
        return None

# --------- شيت Assets (الاسكان) → DB ---------

_ASSETS_TO_BASE = {
    "Hostname": "hostname",
    "LAN IP Address": "ip_address",
    "Serial Number": "sn",
    "Status": "status",
    "Notes": "notes",
}

def _guess_device_type_from_infra(infra: str) -> str:
    s = (infra or "").strip().lower()
    if "hypervisor" in s:
        return "hypervisor"
    if "printer" in s:
        return "printer"
    if "ap" in s or "access point" in s or "wireless" in s or "wifi" in s:
        return "ap"
    if "switch" in s:
        return "switch"
    return "asset"

def upsert_from_assets_row(row: Dict[str, Any]) -> Optional[int]:
    """
    Upsert من شيت 'Assets' (ناتج الاسكان).
    - device_type من 'Device Infrastructure' (أو 'asset').
    - model_vendor = Manufacturer + Device Model.
    - data_source = scan:<Collector> لو متاحة.
    """
    bootstrap_schema()
    try:
        base: Dict[str, Any] = {}

        for k, dbk in _ASSETS_TO_BASE.items():
            if k in row:
                v = row.get(k, "")
                base[dbk] = (v if v is None else str(v)).strip()

        manu = (row.get("Manufacturer") or "").strip()
        model = (row.get("Device Model") or "").strip()
        base["model_vendor"] = " ".join([x for x in [manu, model] if x]).strip() or model or manu

        infra = row.get("Device Infrastructure") or ""
        base["device_type"] = _guess_device_type_from_infra(infra)

        base.setdefault("firmware_os_version", (row.get("OS Name") or "").strip())
        base.setdefault("data_source", f"scan:{(row.get('Collector') or 'Unknown')}".strip())

        hostname = base.get("hostname", "")
        ip = base.get("ip_address", "")
        asset_tag = ""

        with connect() as conn:
            asset_id = _detect_match(conn, asset_tag, hostname, ip)
            cur = conn.cursor()

            if asset_id is None:
                cols = ["device_type"] + [c for c in base.keys() if c != "device_type"]
                vals = [base.get(c, "") for c in cols]
                cur.execute(
                    f"INSERT INTO assets ({','.join(cols)}) VALUES ({','.join(['?']*len(vals))})",
                    vals
                )
                asset_id = int(cur.lastrowid)
            else:
                sets = ",".join([f"{c}=?" for c in base.keys()])
                cur.execute(
                    f"UPDATE assets SET {sets} WHERE id=?",
                    [base[k] for k in base.keys()] + [asset_id]
                )
            return asset_id
    except Exception as e:
        log.exception("DB upsert (Assets scan) failed: %s", e)
        return None


def insert_or_update_asset(data: Dict[str, Any], device_type: Optional[str] = None) -> Optional[int]:
    """Insert or update asset record, returns asset_id"""
    try:
        bootstrap_schema()
        
        # Define base fields for assets table
        base_fields = [
            "asset_tag", "hostname", "ip_address", "model_vendor", "sn", "location",
            "owner", "department", "site", "building", "floor", "room", "status",
            "firmware_os_version", "notes", "data_source", "created_at", "created_by",
            "updated_at", "updated_by", "_excel_path", "_sheet_name", "_headers",
            "_sync_pending", "_sync_attempts", "_sync_completed_at", "_sync_failed",
            # Enhanced technical fields
            "working_user", "domain_name", "device_infrastructure", "installed_ram_gb",
            "storage_info", "manufacturer", "processor_info", "system_sku", "active_gpu",
            "connected_screens", "disk_count", "mac_address", "all_mac_addresses",
            "cpu_details", "disk_details"
        ]
        
        # Extract base fields
        base = {k: v for k, v in data.items() if k in base_fields}
        
        # Ensure device_type is set (REQUIRED field)
        if device_type:
            base['device_type'] = device_type
        elif 'device_type' not in base or not base.get('device_type'):
            # Infer device type from data
            if 'device_infrastructure' in data:
                infra = data['device_infrastructure']
                if 'Server' in infra:
                    base['device_type'] = 'server'
                elif 'Network' in infra:
                    base['device_type'] = 'network'
                elif 'Printer' in infra:
                    base['device_type'] = 'printer'
                elif 'Hypervisor' in infra:
                    base['device_type'] = 'hypervisor'
                else:
                    base['device_type'] = 'workstation'
            else:
                base['device_type'] = 'workstation'  # Default fallback
        
        # Handle empty asset_tag to avoid UNIQUE constraint issues
        if 'asset_tag' in base and (not base['asset_tag'] or base['asset_tag'].strip() == ''):
            base['asset_tag'] = None
            
        # Detection logic
        host = base.get("hostname", "")
        ip = base.get("ip_address", "")
        tag = base.get("asset_tag", "")
        
        with connect() as conn:
            asset_id = _detect_match(conn, tag, host, ip)
            cur = conn.cursor()
            
            if asset_id is None:
                # Insert new record
                cols = list(base.keys())
                vals = [base.get(c, "") for c in cols]
                cur.execute(
                    f"INSERT INTO assets ({','.join(cols)}) VALUES ({','.join(['?']*len(vals))})",
                    vals
                )
                asset_id = int(cur.lastrowid)
            else:
                # Update existing record
                sets = ",".join([f"{c}=?" for c in base.keys()])
                cur.execute(
                    f"UPDATE assets SET {sets} WHERE id=?",
                    [base[k] for k in base.keys()] + [asset_id]
                )
            
            return asset_id
            
    except Exception as e:
        log.error(f"Error in insert_or_update_asset: {e}")
        return None


def map_sheet_data_to_db(sheet_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Map sheet column names to database field names"""
    result = {}
    
    # Map base fields
    for excel_col, db_col in BASE_MAP.items():
        if excel_col in data:
            result[db_col] = data[excel_col]
    
    # Map device-specific fields
    device_type = SHEET_TO_TYPE.get(sheet_name)
    if device_type and device_type in TYPE_SPECIFIC_MAP:
        spec_map = TYPE_SPECIFIC_MAP[device_type]
        for excel_col, db_col in spec_map.items():
            if excel_col in data:
                result[db_col] = data[excel_col]
    
    # Copy sync metadata
    for key in ['_excel_path', '_sheet_name', '_headers', '_sync_pending', 
                '_sync_attempts', '_created_at']:
        if key in data:
            result[key] = data[key]
    
    return result


def get_pending_sync_records(limit: int = 100) -> List[Dict[str, Any]]:
    """Get records pending sync to Excel"""
    try:
        with connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM assets 
                WHERE _sync_pending = '1' AND (_sync_attempts < 5 OR _sync_attempts IS NULL)
                ORDER BY created_at ASC
                LIMIT ?
            """, (limit,))
            
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
            
    except Exception as e:
        log.error(f"Error getting pending sync records: {e}")
        return []


def mark_records_synced(record_ids: List[int]) -> bool:
    """Mark records as successfully synced"""
    try:
        with connect() as conn:
            cursor = conn.cursor()
            from datetime import datetime
            placeholders = ','.join(['?'] * len(record_ids))
            cursor.execute(f"""
                UPDATE assets 
                SET _sync_pending = '0', _sync_completed_at = ?
                WHERE id IN ({placeholders})
            """, [datetime.now().isoformat()] + record_ids)
            conn.commit()
            return True
            
    except Exception as e:
        log.error(f"Error marking records as synced: {e}")
        return False
