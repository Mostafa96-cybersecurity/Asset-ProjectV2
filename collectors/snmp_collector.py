# -*- coding: utf-8 -*-
"""
SNMP Collector Module (Universal for non-Windows/Linux assets)
- Tries multiple pysnmp layouts (modern/legacy/lextudio) gracefully.
- Normalizes output to your Asset schema as much as possible.

Public API:
    snmp_collect_basic(
        ip: str,
        *,
        community: str = "public",
        version: str = "2c",  # "1" | "2c" | "3"
        timeout: int = 2,
        retries: int = 1,
        v3_user: str | None = None,
        v3_auth_key: str | None = None,
        v3_priv_key: str | None = None,
        v3_auth_proto: str = "sha",  # "md5" | "sha"
        v3_priv_proto: str = "aes",  # "aes" | "des"
        port: int = 161,
    ) -> dict | None
"""

from __future__ import annotations
import logging
from typing import Optional, Dict, Any, Iterable, List, Tuple
from utils.identity import valid_serial

_PYSNMP_OK = False
_SNMP_BACKEND = "none"

SnmpEngine = CommunityData = UdpTransportTarget = ContextData = ObjectType = ObjectIdentity = getCmd = nextCmd = None
UsmUserData = usmHMACSHAAuthProtocol = usmHMACMD5AuthProtocol = usmAesCfb128Protocol = usmDESPrivProtocol = None

log = logging.getLogger(__name__)

# Try imports in multiple patterns for robustness
def _try_imports():
    global _PYSNMP_OK, _SNMP_BACKEND
    global SnmpEngine, CommunityData, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity, getCmd, nextCmd
    global UsmUserData, usmHMACSHAAuthProtocol, usmHMACMD5AuthProtocol, usmAesCfb128Protocol, usmDESPrivProtocol

    backends: List[Tuple[str, str]] = [
        ("pysnmp.hlapi", "modern"),
        ("pysnmp.hlapi.v3arch", "v3arch"),
        ("pysnmp_lextudio.hlapi", "lextudio"),
    ]
    for modname, tag in backends:
        try:
            from importlib import import_module
            hlapi = import_module(modname)
            SnmpEngine = hlapi.SnmpEngine
            CommunityData = hlapi.CommunityData
            UdpTransportTarget = hlapi.UdpTransportTarget
            ContextData = hlapi.ContextData
            ObjectType = hlapi.ObjectType
            ObjectIdentity = hlapi.ObjectIdentity
            getCmd = hlapi.getCmd
            nextCmd = hlapi.nextCmd
            # Optional v3
            UsmUserData = getattr(hlapi, "UsmUserData", None)
            usmHMACSHAAuthProtocol = getattr(hlapi, "usmHMACSHAAuthProtocol", None)
            usmHMACMD5AuthProtocol = getattr(hlapi, "usmHMACMD5AuthProtocol", None)
            usmAesCfb128Protocol = getattr(hlapi, "usmAesCfb128Protocol", None)
            usmDESPrivProtocol = getattr(hlapi, "usmDESPrivProtocol", None)
            _PYSNMP_OK = True
            _SNMP_BACKEND = tag
            log.info("SNMP backend loaded: %s", modname)
            return
        except Exception as e:
            log.debug("SNMP import failed for %s: %s", modname, e)

_try_imports()

# Common OIDs
OID_sysDescr = "1.3.6.1.2.1.1.1.0"
OID_sysName = "1.3.6.1.2.1.1.5.0"
OID_hrMemorySize = "1.3.6.1.2.1.25.2.2.0"  # in KB
# ENTITY-MIB serials: walk entPhysicalSerialNum
OID_entPhysicalSerialNum = "1.3.6.1.2.1.47.1.1.1.1.11"
# Printer model (if available)
OID_prtGeneralPrinterName = "1.3.6.1.2.1.43.5.1.1.16.1"

# hrStorage for disks
OID_hrStorageTable = "1.3.6.1.2.1.25.2.3.1"
OID_hrStorageIndex = OID_hrStorageTable + ".1"
OID_hrStorageType = OID_hrStorageTable + ".2"
OID_hrStorageDescr = OID_hrStorageTable + ".3"
OID_hrStorageAllocationUnits = OID_hrStorageTable + ".4"
OID_hrStorageSize = OID_hrStorageTable + ".5"
OID_hrStorageUsed = OID_hrStorageTable + ".6"
# TYPE for FixedDisk
OID_hrStorageFixedDisk = "1.3.6.1.2.1.25.2.1.4"

def _v3_auth_params(v3_auth_proto: str, v3_priv_proto: str):
    auth = usmHMACSHAAuthProtocol
    if (v3_auth_proto or "").lower() == "md5":
        auth = usmHMACMD5AuthProtocol
    priv = usmAesCfb128Protocol
    if (v3_priv_proto or "").lower() == "des":
        priv = usmDESPrivProtocol
    return auth, priv

def _auth(version: str, community: str, v3_user: Optional[str], v3_auth_key: Optional[str], v3_priv_key: Optional[str], v3_auth_proto: str, v3_priv_proto: str):
    v = (version or "2c").lower()
    if v in ("1", "2", "2c"):
        return CommunityData(community, mpModel=0 if v == "1" else 1)
    # v3
    if UsmUserData is None:
        raise RuntimeError("pysnmp v3 not available in this backend")
    authProto, privProto = _v3_auth_params(v3_auth_proto, v3_priv_proto)
    if v3_user and v3_auth_key and v3_priv_key:
        return UsmUserData(v3_user, v3_auth_key, v3_priv_key, authProtocol=authProto, privProtocol=privProto)
    elif v3_user and v3_auth_key:
        return UsmUserData(v3_user, v3_auth_key, authProtocol=authProto)
    elif v3_user:
        return UsmUserData(v3_user)
    raise ValueError("SNMPv3 selected but no credentials provided")

def _snmp_get(
    ip: str,
    oids: Iterable[str],
    *,
    community: str,
    version: str,
    timeout: int,
    retries: int,
    port: int,
    v3_user: Optional[str],
    v3_auth_key: Optional[str],
    v3_priv_key: Optional[str],
    v3_auth_proto: str,
    v3_priv_proto: str,
) -> Dict[str, Any]:
    if not _PYSNMP_OK:
        raise RuntimeError("pysnmp is not available")

    engine = SnmpEngine()
    auth = _auth(version, community, v3_user, v3_auth_key, v3_priv_key, v3_auth_proto, v3_priv_proto)
    target = UdpTransportTarget((ip, port), timeout=timeout, retries=retries)
    ctx = ContextData()

    oid_objs = [ObjectType(ObjectIdentity(oid)) for oid in oids]
    result: Dict[str, Any] = {}

    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(engine, auth, target, ctx, *oid_objs)
    )

    if errorIndication:
        raise RuntimeError(f"SNMP GET error: {errorIndication}")
    if errorStatus:
        idx = int(errorIndex) - 1 if errorIndex else -1
        raise RuntimeError(f"SNMP GET error: {errorStatus.prettyPrint()} at index {idx}")

    for vb in varBinds:
        oid_str = str(vb[0])
        val = vb[1]
        result[oid_str] = _coerce_snmp_value(val)

    return result

def _snmp_walk(
    ip: str,
    base_oid: str,
    *,
    community: str,
    version: str,
    timeout: int,
    retries: int,
    port: int,
    v3_user: Optional[str],
    v3_auth_key: Optional[str],
    v3_priv_key: Optional[str],
    v3_auth_proto: str,
    v3_priv_proto: str,
) -> Dict[str, Any]:
    if not _PYSNMP_OK:
        raise RuntimeError("pysnmp is not available")

    engine = SnmpEngine()
    auth = _auth(version, community, v3_user, v3_auth_key, v3_priv_key, v3_auth_proto, v3_priv_proto)
    target = UdpTransportTarget((ip, port), timeout=timeout, retries=retries)
    ctx = ContextData()
    out: Dict[str, Any] = {}

    for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(
        engine, auth, target, ctx, ObjectType(ObjectIdentity(base_oid)), lexicographicMode=True
    ):
        if errorIndication:
            raise RuntimeError(f"SNMP WALK error: {errorIndication}")
        if errorStatus:
            idx = int(errorIndex) - 1 if errorIndex else -1
            raise RuntimeError(f"SNMP WALK error: {errorStatus.prettyPrint()} at index {idx}")
        for vb in varBinds:
            out[str(vb[0])] = _coerce_snmp_value(vb[1])
        # Stop if walked out of subtree
        if not any(str(k).startswith(base_oid + ".") or str(k) == base_oid for k in [vb[0] for vb in varBinds]):
            break
    return out

def _coerce_snmp_value(v) -> Any:
    try:
        # Try direct python value
        if hasattr(v, "prettyPrint"):
            p = v.prettyPrint()
            # Some counters return strings of digits
            try:
                if p.isdigit():
                    return int(p)
            except Exception:
                pass
            return p
        return v
    except Exception:
        try:
            return str(v)
        except Exception:
            return None

def _infer_infra(sys_descr: str) -> str:
    s = (sys_descr or "").lower()
    # Simple heuristics
    if "vmware" in s or "esxi" in s or "hypervisor" in s:
        return "Hypervisor"
    if "cisco" in s or "router" in s or "switch" in s or "ios" in s or "nx-os" in s:
        return "Network"
    if "forti" in s or "palo alto" in s or "sonicwall" in s or "checkpoint" in s:
        return "Firewall"
    if "printer" in s or "hp laserjet" in s or "epson" in s or "canon" in s or "ricoh" in s or "brother" in s:
        return "Printer"
    if "access point" in s or "wlan" in s or "wireless" in s or "ap " in s:
        return "Network"
    return "Network"  # default for non-Windows/Linux devices

def _parse_manufacturer(sys_descr: str) -> str:
    s = (sys_descr or "").lower()
    for m in ["vmware", "cisco", "hpe", "hp", "hewlett-packard", "dell", "fortinet", "palo alto", "ubiquiti", "mikrotik", "huawei", "juniper", "tp-link", "ricoh", "canon", "epson", "brother"]:
        if m in s:
            return m.title()
    return ""

def _kb_to_gb(v: Any) -> Optional[float]:
    try:
        return round(float(v) / (1024 * 1024), 2)
    except Exception:
        return None

def _summarize_storage(walk_map: Dict[str, Any]) -> str:
    """
    Summarize hrStorage for FixedDisk entries: total and used in GB.
    """
    try:
        # Build rows by index
        rows: Dict[str, Dict[str, Any]] = {}
        for oid, val in walk_map.items():
            if oid.startswith(OID_hrStorageIndex + "."):
                idx = oid.split(".")[-1]
                rows.setdefault(idx, {})["index"] = val
            elif oid.startswith(OID_hrStorageType + "."):
                idx = oid.split(".")[-1]
                rows.setdefault(idx, {})["type"] = val
            elif oid.startswith(OID_hrStorageDescr + "."):
                idx = oid.split(".")[-1]
                rows.setdefault(idx, {})["descr"] = val
            elif oid.startswith(OID_hrStorageAllocationUnits + "."):
                idx = oid.split(".")[-1]
                rows.setdefault(idx, {})["au"] = val
            elif oid.startswith(OID_hrStorageSize + "."):
                idx = oid.split(".")[-1]
                rows.setdefault(idx, {})["size"] = val
            elif oid.startswith(OID_hrStorageUsed + "."):
                idx = oid.split(".")[-1]
                rows.setdefault(idx, {})["used"] = val

        parts = []
        for idx, r in rows.items():
            if str(r.get("type", "")).endswith("." + OID_hrStorageFixedDisk.split(".")[-1]):
                au = float(r.get("au", 1) or 1.0)
                size = float(r.get("size", 0) or 0.0) * au
                used = float(r.get("used", 0) or 0.0) * au
                # to GB
                size_gb = round(size / (1024 ** 3), 2)
                used_gb = round(used / (1024 ** 3), 2)
                descr = str(r.get("descr", f"Disk{idx}"))
                parts.append(f"{descr}: {size_gb} GB ({used_gb} GB used)")
        return " | ".join(parts) if parts else ""
    except Exception:
        return ""

def _first_non_empty_serial(ent_walk: Dict[str, Any]) -> str:
    # find any entPhysicalSerialNum.* with non-empty value
    candidates = [str(v).strip() for k, v in ent_walk.items() if k.startswith(OID_entPhysicalSerialNum + ".") and str(v).strip()]
    for c in candidates:
        if valid_serial(c):
            return c
    # fallback: return first non-empty anyway
    return candidates[0] if candidates else ""

def snmp_collect_basic(
    ip: str,
    *,
    community: str = "public",
    version: str = "2c",
    timeout: int = 2,
    retries: int = 1,
    v3_user: Optional[str] = None,
    v3_auth_key: Optional[str] = None,
    v3_priv_key: Optional[str] = None,
    v3_auth_proto: str = "sha",
    v3_priv_proto: str = "aes",
    port: int = 161,
) -> Optional[Dict[str, Any]]:
    """
    Returns a dict aligned to your Excel schema for non-Windows/Linux devices.
    """
    if not _PYSNMP_OK:
        log.warning("SNMP libraries not found; cannot collect via SNMP.")
        return None

    try:
        # Basic GETs
        get_map = _snmp_get(
            ip,
            [OID_sysDescr, OID_sysName, OID_hrMemorySize, OID_prtGeneralPrinterName],
            community=community, version=version, timeout=timeout, retries=retries, port=port,
            v3_user=v3_user, v3_auth_key=v3_auth_key, v3_priv_key=v3_priv_key,
            v3_auth_proto=v3_auth_proto, v3_priv_proto=v3_priv_proto
        )
    except Exception as e:
        log.error("SNMP GET failed for %s: %s", ip, e)
        return None

    sys_descr = str(get_map.get(OID_sysDescr, "")) or ""
    sys_name = str(get_map.get(OID_sysName, "")) or ""
    printer_name = str(get_map.get(OID_prtGeneralPrinterName, "")) or ""
    mem_kb = get_map.get(OID_hrMemorySize, None)
    ram_gb = _kb_to_gb(mem_kb) if mem_kb is not None else None

    # Walk serials and storage (best-effort)
    serial = ""
    storage_summary = ""
    try:
        ent_walk = _snmp_walk(
            ip, OID_entPhysicalSerialNum,
            community=community, version=version, timeout=timeout, retries=retries, port=port,
            v3_user=v3_user, v3_auth_key=v3_auth_key, v3_priv_key=v3_priv_key,
            v3_auth_proto=v3_auth_proto, v3_priv_proto=v3_priv_proto
        )
        serial = _first_non_empty_serial(ent_walk)
    except Exception:
        pass

    try:
        hr_walk = _snmp_walk(
            ip, OID_hrStorageTable,
            community=community, version=version, timeout=timeout, retries=retries, port=port,
            v3_user=v3_user, v3_auth_key=v3_auth_key, v3_priv_key=v3_priv_key,
            v3_auth_proto=v3_auth_proto, v3_priv_proto=v3_priv_proto
        )
        storage_summary = _summarize_storage(hr_walk)
    except Exception:
        pass

    # Infer metadata
    infra = _infer_infra(sys_descr)
    manufacturer = _parse_manufacturer(sys_descr)
    model = printer_name or sys_name  # best-effort
    os_name = sys_descr.strip()

    # Normalize to your Excel schema keys
    data: Dict[str, Any] = {
        "Hostname": sys_name or ip,
        "Working User": "",                    # N/A for network/ESXi via SNMP
        "Domain": "",                          # N/A
        "Device Model": model,
        "Device Infrastructure": infra,        # e.g., Printer / Network / Firewall / Hypervisor
        "OS Name": os_name,
        "Installed RAM (GB)": ram_gb if ram_gb is not None else "",
        "LAN IP Address": ip,
        "Storage": storage_summary,            # may be empty on many network gears
        "Manufacturer": manufacturer,
        "Serial Number": serial,
        "Processor": "",                       # Not reliable over SNMP generically
        "System SKU": "",                      # N/A
        "Active GPU": "",                      # N/A
        "Connected Screens": "",               # N/A
    }
    return data
