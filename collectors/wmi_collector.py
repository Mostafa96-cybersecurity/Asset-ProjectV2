# -*- coding: utf-8 -*-
"""
WMI Collector Module (hardened + schema-aligned)
-----------------------------------------------
Public API:
    collect_windows_wmi(
        ip: str | None = None,
        username: str | None = None,
        password: str | None = None,
        *,
        include_cpu: bool = True,
        include_memory: bool = True,
        include_storage: bool = True,
        include_nics: bool = True,
        include_gpu: bool = True,
        include_monitors: bool = True,
        namespace: str = r"root\cimv2",
    ) -> dict

Returns a dict aligned with your Excel schema:
    Hostname, Working User, Domain, Device Model, Device Infrastructure, OS Name,
    Installed RAM (GB), LAN IP Address, Storage, Manufacturer, Serial Number,
    Processor, System SKU, Active GPU, Connected Screens, Disk Count, Disks

Notes:
    - Run on Windows; remote via DCOM if ip provided (needs firewall/DCOM/permissions).
    - Never crashes: returns {"Error": {...}} on failure with clear message.
    - Requires: pywin32, WMI  (pip install pywin32 WMI)
"""

from __future__ import annotations
import logging
import platform
from typing import Any, Dict, Iterable, List, Optional

log = logging.getLogger(__name__)

# -------- Platform / Imports Guards -------- #

_WMI_IMPORT_OK = False
pythoncom = None
wmi = None

def _on_windows() -> bool:
    return platform.system().lower().startswith("win")

try:
    if _on_windows():
        import pythoncom      # from pywin32
        import wmi            # pip package: WMI
        _WMI_IMPORT_OK = True
    else:
        log.info("WMI collector disabled: non-Windows platform.")
except Exception as e:  # pragma: no cover
    log.warning("WMI collector unavailable: %s", e)
    _WMI_IMPORT_OK = False

# -------- Project Utilities -------- #

from utils.helpers import safe_first, normalize_mac
from utils.identity import valid_serial

# -------- Helpers / Constants -------- #

_EXCLUDE_NIC_KEYWORDS = tuple(
    k.lower() for k in (
        "Bluetooth", "VirtualBox", "VMware", "Hyper-V", "Wi-Fi Direct", "TAP", "Loopback",
        "Pseudo", "WAN Miniport", "Teredo", "isatap", "Npcap", "Packet Scheduler", "Container",
        "vEthernet", "QoS Packet Scheduler", "Deterministic Network Enhancer", "VPN", "WireGuard"
    )
)

_PRIVATE_V4_PREFIXES = ("10.", "192.168.", "172.16.", "172.17.", "172.18.", "172.19.",
                        "172.20.", "172.21.", "172.22.", "172.23.", "172.24.",
                        "172.25.", "172.26.", "172.27.", "172.28.", "172.29.",
                        "172.30.", "172.31.")

def _should_exclude_nic(name: Optional[str]) -> bool:
    nm = (name or "").lower()
    return any(k in nm for k in _EXCLUDE_NIC_KEYWORDS)

def _is_local_target(ip: Optional[str]) -> bool:
    if not ip:
        return True
    ip_l = str(ip).strip().lower()
    return ip_l in {"localhost", "127.0.0.1", "::1"}

def _dedup_preserve(seq: Iterable[Any]) -> List[Any]:
    seen = set()
    out: List[Any] = []
    for item in seq:
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out

def _gb(nbytes: Optional[int]) -> Optional[int]:
    try:
        return int(round((nbytes or 0) / (1024**3)))
    except Exception:
        return None

def _error(code: str, message: str, target: Optional[str] = None) -> Dict[str, Any]:
    return {"Error": {"code": code, "message": message, "target": target or "localhost"}}

# -------- COM Context Manager -------- #

class _COMContext:
    def __enter__(self):
        try:
            pythoncom.CoInitialize()
        except Exception:
            pass
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            pythoncom.CoUninitialize()
        except Exception:
            pass

# -------- Connection -------- #

def _open_wmi_connection(
    ip: Optional[str],
    username: Optional[str],
    password: Optional[str],
    namespace: str,
):
    if _is_local_target(ip):
        return wmi.WMI(namespace=namespace)
    kwargs = {"computer": ip, "namespace": namespace}
    if username:
        kwargs["user"] = username
    if password:
        kwargs["password"] = password
    return wmi.WMI(**kwargs)

# -------- Core Collectors -------- #

def _collect_system(conn) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    try:
        sysprod = safe_first(conn.Win32_ComputerSystemProduct() or [])
        cs = safe_first(conn.Win32_ComputerSystem() or [])
        os_ = safe_first(conn.Win32_OperatingSystem() or [])

        hostname = getattr(cs, "Name", "") if cs else ""
        os_caption = getattr(os_, "Caption", "") if os_ else ""
        os_version = getattr(os_, "Version", "") if os_ else ""
        os_build = getattr(os_, "BuildNumber", "") if os_ else ""
        vendor = getattr(cs, "Manufacturer", "") if cs else ""
        model = getattr(cs, "Model", "") if cs else ""
        domain = getattr(cs, "Domain", "") if cs else ""
        working_user = getattr(cs, "UserName", "") if cs else ""  # DOMAIN\User
        sku = getattr(sysprod, "Name", "") if sysprod else ""     # System SKU (often here)
        serial = (getattr(sysprod, "IdentifyingNumber", "") or "").strip() if sysprod else ""
        if serial and not valid_serial(serial):
            serial = ""

        total_ram_bytes = None
        if cs and getattr(cs, "TotalPhysicalMemory", None):
            try:
                total_ram_bytes = int(cs.TotalPhysicalMemory)
            except Exception:
                pass

        out.update({
            "Hostname": hostname,
            "OS Name": os_caption or f"Windows {os_version}",
            "OS Version": os_version,
            "OS Build": os_build,
            "Manufacturer": vendor,
            "Device Model": model,
            "Domain": domain,
            "Working User": working_user,
            "System SKU": sku,
            "Serial Number": serial,
            "Installed RAM (GB)": _gb(total_ram_bytes),
        })
    except Exception as e:
        log.debug("WMI [System/OS] error: %s", e, exc_info=True)
    return out

def _detect_infrastructure(model: str, vendor: str, conn) -> str:
    """
    Heuristic: Laptop / Desktop / Virtual / Unknown
    """
    m = (model or "").lower()
    v = (vendor or "").lower()
    # Virtual hints
    virtual_keys = ("vmware", "virtual", "hyper-v", "kvm", "virtualbox", "xen", "qemu", "azure", "aws", "google")
    if any(k in m for k in virtual_keys) or any(k in v for k in virtual_keys):
        return "Virtual"

    # Chassis type hints
    try:
        enc = safe_first(conn.Win32_SystemEnclosure() or [])
        ch = getattr(enc, "ChassisTypes", None)
        # Portable types from SMBIOS
        laptop_types = {8, 9, 10, 14, 30, 31, 32}  # Portable/Notebook/Laptop/Tablet/Convertible/Detachable/IoT
        desktop_types = {3, 4, 5, 6, 7, 15}        # Desktop/LPS/Space-saving/Mini/All-in-one
        if ch and isinstance(ch, (list, tuple)) and ch:
            s = set(int(x) for x in ch if isinstance(x, (int, float)))
            if s & laptop_types:
                return "Laptop"
            if s & desktop_types:
                return "Desktop"
    except Exception:
        pass

    # PCSystemType (1=Desktop, 2=Mobile, 3=Workstation, 4=Enterprise Server, 5=SOHO Server …)
    try:
        cs = safe_first(conn.Win32_ComputerSystem() or [])
        t = int(getattr(cs, "PCSystemType", 0) or 0)
        if t == 2:
            return "Laptop"
        if t in (1, 3):
            return "Desktop"
    except Exception:
        pass

    # Fallbacks
    if "laptop" in m or "notebook" in m or "book" in m:
        return "Laptop"
    return "Desktop"

def _collect_cpu(conn) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    try:
        cpus = conn.Win32_Processor() or []
        name = getattr(cpus[0], "Name", None) if cpus else None
        if name:
            out["Processor"] = name
        if cpus:
            out["CPUs"] = [{
                "name": getattr(c, "Name", None),
                "cores": int(getattr(c, "NumberOfCores", 0) or 0),
                "threads": int(getattr(c, "NumberOfLogicalProcessors", 0) or 0),
                "max_clock_mhz": int(getattr(c, "MaxClockSpeed", 0) or 0),
            } for c in cpus]
    except Exception as e:
        log.debug("WMI [CPU] error: %s", e, exc_info=True)
    return out

def _infer_disk_type(model: Optional[str], media_type: Optional[str], interface: Optional[str]) -> str:
    m = (model or "").lower()
    mt = (media_type or "").lower()
    itf = (interface or "").lower()
    if "nvme" in m or "nvme" in itf:
        return "NVMe SSD"
    if "ssd" in m or "solid" in mt:
        return "SSD"
    if "sas" in m or "sas" in itf:
        return "SAS HDD"
    if "sata" in m or "sata" in itf:
        return "SATA HDD"
    if "scsi" in m or "scsi" in itf:
        return "SCSI"
    # Fallbacks
    if "hdd" in m or "fixed" in mt:
        return "HDD"
    return "Unknown"

def _collect_storage(conn) -> Dict[str, Any]:
    """
    - Storage: إجمالي حجم الأقراص الثابتة (logical fixed) بالـ GB.
    - Disks: تفاصيل فيزيكال ديسك + الـ mounts اللي راكبة عليها.
    - Disk Count: عدد الأقراص الفيزيكال.
    """
    out: Dict[str, Any] = {}
    total_bytes = 0

    # 1) إجمالي السعة المنطقية (C:, D: ...) للـ fixed drives
    try:
        for ld in (conn.Win32_LogicalDisk(DriveType=3) or []):
            try:
                total_bytes += int(getattr(ld, "Size", 0) or 0)
            except Exception:
                continue
    except Exception as e:
        log.debug("WMI [Storage] logical sum error: %s", e, exc_info=True)

    # 2) DiskDrive -> Partitions -> LogicalDisks  (mount mapping)
    index_to_mounts: Dict[int, List[str]] = {}
    try:
        for dd in (conn.Win32_DiskDrive() or []):
            try:
                idx = int(getattr(dd, "Index", -1))
            except Exception:
                idx = -1
            mounts: List[str] = []
            try:
                parts = dd.associators("Win32_DiskDriveToDiskPartition") or []
            except Exception:
                parts = []
            for p in parts:
                try:
                    lds = p.associators("Win32_LogicalDiskToPartition") or []
                except Exception:
                    lds = []
                for ld in lds:
                    dl = getattr(ld, "DeviceID", None)  # like "C:"
                    if dl and isinstance(dl, str):
                        mounts.append(dl)
            index_to_mounts[idx] = sorted(set(mounts))
    except Exception as e:
        log.debug("WMI [Storage] mounts mapping error: %s", e, exc_info=True)

    # 3) تفاصيل الفيزيكال ديسكس
    disks: List[Dict[str, Any]] = []
    try:
        for d in (conn.Win32_DiskDrive() or []):
            try:
                idx = int(getattr(d, "Index", -1))
            except Exception:
                idx = -1
            model = getattr(d, "Model", None)
            interface = getattr(d, "InterfaceType", None)
            size_b = int(getattr(d, "Size", 0) or 0)
            media_type = getattr(d, "MediaType", None)
            dserial = getattr(d, "SerialNumber", None)
            dtype = _infer_disk_type(model, media_type, interface)
            disks.append({
                "index": idx,
                "model": model,
                "interface": interface,
                "size_bytes": size_b,
                "size_gb": _gb(size_b),
                "media_type": media_type,
                "type": dtype,
                "serial": dserial,
                "mounts": index_to_mounts.get(idx, []),
            })
    except Exception as e:
        log.debug("WMI [Storage] physical disks error: %s", e, exc_info=True)

    if total_bytes:
        out["Storage"] = f"{_gb(total_bytes)} GB"
    if disks:
        out["Disks"] = disks
        out["Disk Count"] = len(disks)
    else:
        out["Disk Count"] = 0

    return out

def _collect_nics_ip(conn) -> Dict[str, Any]:
    """
    LAN IP Address: أول IPv4 Private من NIC مفعّل.
    """
    out: Dict[str, Any] = {}
    try:
        cfgs = conn.Win32_NetworkAdapterConfiguration(IPEnabled=True) or []
        candidates: List[str] = []
        for cfg in cfgs:
            try:
                ips = list(getattr(cfg, "IPAddress", []) or [])
            except Exception:
                ips = []
            for ip in ips:
                if isinstance(ip, str) and ip and "." in ip:
                    if ip.startswith(_PRIVATE_V4_PREFIXES):
                        candidates.append(ip)
        if candidates:
            out["LAN IP Address"] = _dedup_preserve(candidates)[0]

        # MACs (اختياري)
        macs = []
        for cfg in cfgs:
            mac = normalize_mac(getattr(cfg, "MACAddress", None))
            if mac:
                macs.append(mac)
        if macs:
            out["MAC Address"] = macs[0]
            out["All MACs"] = ";".join(_dedup_preserve(macs))
    except Exception as e:
        log.debug("WMI [NIC/IP] error: %s", e, exc_info=True)
    return out

def _collect_gpu_monitors(conn) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    try:
        gpus = []
        for g in (conn.Win32_VideoController() or []):
            nm = getattr(g, "Name", None)
            if nm:
                gpus.append(nm)
        gpus = _dedup_preserve(gpus)
        if gpus:
            out["Active GPU"] = gpus[0]
            out["GPUs"] = gpus
    except Exception as e:
        log.debug("WMI [GPU] error: %s", e, exc_info=True)

    try:
        monitors = conn.Win32_DesktopMonitor() or []
        out["Connected Screens"] = str(len(monitors)) if monitors else "0"
    except Exception:
        out["Connected Screens"] = "0"

    return out

# -------- Public API -------- #

def collect_windows_wmi(
    ip: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    *,
    include_cpu: bool = True,
    include_memory: bool = True,   # parity; RAM GB comes from ComputerSystem
    include_storage: bool = True,
    include_nics: bool = True,
    include_gpu: bool = True,
    include_monitors: bool = True,
    namespace: str = r"root\cimv2",
) -> Dict[str, Any]:
    """
    Collect a Windows asset snapshot via WMI (local or remote via DCOM).
    Returns data aligned to your table columns.
    """
    target = ip or "localhost"

    if not _on_windows():
        return _error("PlatformNotSupported", "WMI collection supported only on Windows host.", target)

    if not _WMI_IMPORT_OK:
        return _error("DependencyMissing", "Missing dependencies: install 'pywin32' and 'WMI'.", target)

    with _COMContext():
        try:
            conn = _open_wmi_connection(ip, username, password, namespace=namespace)
        except Exception as e:
            msg = ("Failed to open WMI connection. Ensure target is reachable, DCOM enabled, "
                   "and credentials are valid. Details: %r" % (e,))
            log.debug(msg, exc_info=True)
            return _error("ConnectionFailed", msg, target)

        # Base schema container
        data: Dict[str, Any] = {
            "Target": target,
            "Collector": "WMI",
            "Asset Type": "Windows Host",
            # Pre-fill table columns with empty defaults to keep schema stable
            "Hostname": "",
            "Working User": "",
            "Domain": "",
            "Device Model": "",
            "Device Infrastructure": "",
            "OS Name": "",
            "Installed RAM (GB)": None,
            "LAN IP Address": "",
            "Storage": "",
            "Manufacturer": "",
            "Serial Number": "",
            "Processor": "",
            "System SKU": "",
            "Active GPU": "",
            "Connected Screens": "0",
        }
        if username:
            data["AuthUser"] = username

        # System/OS block
        sys_block = _collect_system(conn)
        data.update({
            "Hostname": sys_block.get("Hostname", "") or data["Hostname"],
            "OS Name": sys_block.get("OS Name", "") or data["OS Name"],
            "Manufacturer": sys_block.get("Manufacturer", "") or data["Manufacturer"],
            "Device Model": sys_block.get("Device Model", "") or data["Device Model"],
            "Domain": sys_block.get("Domain", "") or data["Domain"],
            "Working User": sys_block.get("Working User", "") or data["Working User"],
            "System SKU": sys_block.get("System SKU", "") or data["System SKU"],
            "Serial Number": sys_block.get("Serial Number", "") or data["Serial Number"],
            "Installed RAM (GB)": sys_block.get("Installed RAM (GB)", data["Installed RAM (GB)"]),
        })

        # Device Infrastructure
        try:
            data["Device Infrastructure"] = _detect_infrastructure(
                data.get("Device Model", ""), data.get("Manufacturer", ""), conn
            ) or data["Device Infrastructure"]
        except Exception:
            pass

        # CPU (Processor)
        if include_cpu:
            cpu_block = _collect_cpu(conn)
            data["Processor"] = cpu_block.get("Processor", "") or data["Processor"]
            if cpu_block:
                data.update(cpu_block)

        # Storage
        if include_storage:
            st_block = _collect_storage(conn)
            if st_block.get("Storage"):
                data["Storage"] = st_block["Storage"]
            if "Disk Count" in st_block:
                data["Disk Count"] = st_block["Disk Count"]
            if st_block.get("Disks"):
                data["Disks"] = st_block["Disks"]

        # NICs + IP
        if include_nics:
            nic_block = _collect_nics_ip(conn)
            if nic_block.get("LAN IP Address"):
                data["LAN IP Address"] = nic_block["LAN IP Address"]
            if nic_block.get("MAC Address"):
                data["MAC Address"] = nic_block["MAC Address"]
            if nic_block.get("All MACs"):
                data["All MACs"] = nic_block["All MACs"]

        # GPU + Monitors
        if include_gpu or include_monitors:
            gm_block = _collect_gpu_monitors(conn)
            if include_gpu and gm_block.get("Active GPU"):
                data["Active GPU"] = gm_block["Active GPU"]
            if include_monitors and gm_block.get("Connected Screens") is not None:
                data["Connected Screens"] = gm_block["Connected Screens"]

        return data

# Backward-compatible local snapshot (no args)
def wmi_collect_basic() -> Dict[str, Any]:
    return collect_windows_wmi()

__all__ = ["collect_windows_wmi", "wmi_collect_basic"]

