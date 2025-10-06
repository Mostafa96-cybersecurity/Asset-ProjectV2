# -*- coding: utf-8 -*-
"""
Universal Collector Orchestrator (Pro Edition)
---------------------------------------------
Routing order:
  1) Windows via WMI (ports 135/445 + creds_windows)
  2) Linux/ESXi via SSH (port 22 + creds_linux)
  3) Network/ESXi/Printers via SNMP (v3 preferred, then v2c)
  4) Nmap fingerprint fallback (device-type & open ports)
  5) HTTP fingerprint fallback (title/server banner)

All outputs normalized to the Excel schema you use:
  Hostname, Working User, Domain, Device Model, Device Infrastructure, OS Name,
  Installed RAM (GB), LAN IP Address, Storage, Manufacturer, Serial Number,
  Processor, System SKU, Active GPU, Connected Screens

Requires:
  - collectors.wmi_collector.collect_windows_wmi(ip, user, pass) -> dict
  - collectors.ssh_collector.collect_linux_or_esxi_ssh(ip, user, pass) -> dict
  - collectors.snmp_collector.snmp_collect_basic(...) -> dict
"""

from __future__ import ipaddress  # For IP validation
import annotations
import os
import subprocess
import socket
import re
import logging
from typing import Dict, Any, List, Optional, Set

import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning

from collectors.wmi_collector import collect_windows_wmi
from collectors.ssh_collector import collect_linux_or_esxi_ssh
from collectors.snmp_collector import snmp_collect_basic, _PYSNMP_OK
from utils.helpers import which

# ------------- Setup -------------
urllib3.disable_warnings(InsecureRequestWarning)
log = logging.getLogger(__name__)
NMAP_BIN = which("nmap")

# ------------- Basic network probes -------------

def is_alive(ip_address: str, count: int = 1, timeout_ms: int = 800) -> bool:
    """Cross-platform ping (best-effort)."""
    try:
        if os.name == 'nt':
            cmd = ["ping", "-n", str(count), "-w", str(timeout_ms), ip_address]
        else:
            timeout_s = max(1, int(round(timeout_ms / 1000)))
            cmd = ["ping", "-c", str(count), "-W", str(timeout_s), ip_address]
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return res.returncode == 0
    except Exception:
        return False


def is_tcp_open(ip: str, port: int, timeout: float = 0.8) -> bool:
    """Fast TCP connect check."""
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except Exception:
        return False

# ------------- HTTP fingerprint -------------

def _http_probe(url: str, timeout: float = 1.2):
    try:
        r = requests.get(url, timeout=timeout, verify=False, allow_redirects=True)
        return r
    except Exception:
        return None


def http_fingerprint(ip: str, timeout: float = 1.2) -> Dict[str, Any]:
    """
    Returns {"server": "...", "title": "...", "type_guess": "..."} best-effort.
    """
    out: Dict[str, Any] = {}
    r = _http_probe(f"http://{ip}", timeout=timeout) or _http_probe(f"https://{ip}", timeout=timeout)
    if not r:
        return out

    out["server"] = r.headers.get("Server", "")
    m = re.search(r"<title>(.*?)</title>", r.text, re.IGNORECASE | re.DOTALL)
    out["title"] = (m.group(1).strip() if m else "")

    body_l   = r.text.lower()
    server_l = (out.get("server") or "").lower()
    title_l  = (out.get("title") or "").lower()
    blob     = title_l + server_l + body_l

    # Smart display detection
    if any(k in blob for k in ["webos", "tizen", "bravia", "hisense", "smart tv", "android tv", "philips tv"]):
        out["type_guess"] = "Smart Display"

    # Network/Printer/Phone/Firewall hints
    hints = [
        ("HP LaserJet", "Printer"), ("Kyocera Command Center","Printer"),
        ("Ricoh Web Image Monitor","Printer"), ("Xerox","Printer"),
        ("Brother","Printer"), ("Canon","Printer"),
        ("Yealink","IP Phone"), ("Grandstream","IP Phone"), ("3CX","PBX"),
        ("Ubiquiti","Switch/Router"), ("EdgeOS","Router"), ("MikroTik","Router/Switch"),
        ("FortiGate","Firewall"), ("Cisco","Switch/Router"), ("VMware ESXi","Hypervisor"),
        ("Hikvision","NVR/DVR"), ("Dahua","NVR/DVR"),
    ]
    for k, tg in hints:
        if k.lower() in blob:
            out["type_guess"] = tg
            break

    return out


def http_guess(ip: str) -> Dict[str, Any]:
    try:
        return http_fingerprint(ip)
    except Exception:
        return {}

# ------------- Nmap discover -------------

def nmap_discover(hosts: List[str], ports: str = "22,80,135,139,161,443,445,631,8080,8443") -> Dict[str, Set[int]]:
    """
    Returns {ip: {open_port, ...}} using -oG greppable output.
    """
    results: Dict[str, Set[int]] = {}
    if not NMAP_BIN:
        return results
    try:
        cmd = [NMAP_BIN, "-n", "-Pn", "-T4", "--open", "-p", ports, "-oG", "-"] + hosts
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, timeout=180, text=True)
        for line in out.splitlines():
            if not line.startswith("Host:"):
                continue
            m = re.search(r"Host:\s+(\S+)", line)
            if not m:
                continue
            ip = m.group(1)
            ports_seg = re.search(r"Ports:\s+(.+)", line)
            open_set: Set[int] = set()
            if ports_seg:
                for p in ports_seg.group(1).split(","):
                    ps = p.strip().split("/")
                    if len(ps) >= 2 and ps[1] == "open":
                        try:
                            open_set.add(int(ps[0]))
                        except Exception:
                            pass
            if open_set:
                results[ip] = open_set
    except Exception as e:
        log.debug("nmap_discover failed: %s", e)
    return results

# ------------- Storage normalization -------------

def _format_storage_field(storage_value):
    """
    Normalize to:
      'disk 1 = 238.47 GB - disk 2 = 931.51 GB - ...'
    """
    sizes: List[str] = []

    def _parse_size_token(tok: str) -> Optional[str]:
        try:
            s = tok.strip().upper().replace("GB", "").strip()
            if not s:
                return None
            val = float(s)
            return f"{val:.2f} GB"
        except Exception:
            return None

    # list/tuple cases
    if isinstance(storage_value, (list, tuple)):
        for item in storage_value:
            if item is None:
                continue
            if isinstance(item, dict):
                gb = None
                if "size_gb" in item:
                    gb = item.get("size_gb")
                elif "gb" in item:
                    gb = item.get("gb")
                elif "size_bytes" in item:
                    gb = float(item["size_bytes"]) / (1024**3)
                elif "bytes" in item:
                    gb = float(item["bytes"]) / (1024**3)
                elif "size" in item:
                    if isinstance(item["size"], (int, float)):
                        gb = float(item["size"])
                    elif isinstance(item["size"], str):
                        parsed = _parse_size_token(item["size"])
                        if parsed:
                            sizes.append(parsed)
                            continue
                if gb is not None:
                    sizes.append(f"{float(gb):.2f} GB")
                else:
                    sizes.append(str(item))
            elif isinstance(item, (int, float)):
                sizes.append(f"{float(item):.2f} GB")
            elif isinstance(item, str):
                parts = [p for p in re.split(r"[,\s]+", item) if p] if (' ' in item or ',' in item) else [item]
                acc = []
                for p in parts:
                    parsed = _parse_size_token(p)
                    if parsed:
                        acc.append(parsed)
                if acc:
                    sizes.extend(acc)
                elif "GB" in item.upper():
                    sizes.append(item.strip())
            else:
                sizes.append(str(item))

    # single number
    elif isinstance(storage_value, (int, float)):
        sizes.append(f"{float(storage_value):.2f} GB")

    # string cases
    elif isinstance(storage_value, str):
        txt = storage_value.strip()
        if "," in txt:
            parts = [p.strip() for p in txt.split(",") if p.strip()]
            norm = []
            for p in parts:
                pp = p
                if "GB" in p.upper():
                    pp = p.upper().replace("GB", "").strip()
                parsed = _parse_size_token(pp)
                if parsed:
                    norm.append(parsed)
            if norm:
                sizes.extend(norm)
        else:
            pp = txt.upper().replace("GB", "").strip() if "GB" in txt.upper() else txt
            parsed = _parse_size_token(pp)
            if parsed:
                sizes.append(parsed)
            elif "GB" in txt.upper():
                sizes.append(txt)

    sizes = [s for s in sizes if s]
    if sizes:
        labeled = [f"disk {i} = {s}" for i, s in enumerate(sizes, start=1)]
        return " - ".join(labeled)
    return storage_value if storage_value not in (None, "") else "N/A"


def _normalize_storage_in_record(d: dict):
    """
    Mutates dict in-place to normalize 'Storage' field.
    Priority:
      1) 'Disks' list (size_gb/size_bytes/size)
      2) Alternate keys ('Disk Sizes', 'Physical Disks', 'Disk_GB_List')
      3) Existing 'Storage'
    """
    disks = d.get("Disks")
    if isinstance(disks, (list, tuple)) and disks:
        sizes = []
        for item in disks:
            if not isinstance(item, dict):
                continue
            if item.get("size_gb") is not None:
                try:
                    sizes.append(float(item["size_gb"]))
                except Exception:
                    pass
            elif item.get("size_bytes") is not None:
                try:
                    sizes.append(float(item["size_bytes"]) / (1024 ** 3))
                except Exception:
                    pass
            elif item.get("size"):
                try:
                    sizes.append(float(item["size"]))
                except Exception:
                    pass
        if sizes:
            d["Storage"] = _format_storage_field(sizes)
            return

    for alt_key in ("Disk Sizes", "Physical Disks", "Disk_GB_List"):
        if alt_key in d:
            d["Storage"] = _format_storage_field(d[alt_key])
            return

    if "Storage" in d:
        d["Storage"] = _format_storage_field(d["Storage"])

# ------------- Helpers: inference & schema fill -------------

def _infer_infra_from_ports(open_ports: Set[int]) -> str:
    """Infer device class from open ports (best-effort)."""
    if 161 in open_ports:
        return "Network (SNMP Device)"
    if 22 in open_ports and any(p in open_ports for p in (80, 443)):
        return "Network (SSH/Web)"
    if 22 in open_ports:
        return "SSH Device"
    if any(p in open_ports for p in (80, 443, 8080, 8443, 631)):
        return "Web Device"
    if 135 in open_ports or 445 in open_ports:
        return "Windows (SMB/RPC)"
    return "Network"


def _merge_http_into_record(d: Dict[str, Any], http: Dict[str, Any]):
    if not http:
        return
    d["HTTP Server"] = http.get("server", "")
    d["HTTP Title"]  = http.get("title", "")
    if http.get("type_guess"):
        # Don't overwrite an explicit SNMP-provided class like Hypervisor/Printer
        d.setdefault("Device Infrastructure", http["type_guess"])
        if d.get("Device Model", "") in ("", None):
            d["Device Model"] = http.get("title", "") or d.get("Device Model", "")


def _empty_schema(ip: str, infra: str = "Network") -> Dict[str, Any]:
    # Strictly keep your Excel headers
    return {
        "Hostname": ip,
        "Working User": "",
        "Domain": "",
        "Device Model": "",
        "Device Infrastructure": infra,
        "OS Name": "",
        "Installed RAM (GB)": "",
        "LAN IP Address": ip,
        "Storage": "",
        "Manufacturer": "",
        "Serial Number": "",
        "Processor": "",
        "System SKU": "",
        "Active GPU": "",
        "Connected Screens": "",
    }

# ------------- Main Orchestration -------------

def collect_any(
    ip: str,
    creds_windows: List[tuple],
    creds_linux: List[tuple],
    snmp_v2c: Optional[dict],
    snmp_v3: Optional[dict],
    use_http: bool = True,
) -> Dict[str, Any]:
    """
    Input shapes:
      creds_windows: list[(username, password)]
      creds_linux:   list[(username, password)]
      snmp_v2c:      {"community":"public","port":161,"version":"2c","timeout":2,"retries":1}
      snmp_v3:       {"user":"u","auth_key":"a","priv_key":"p","auth_proto":"sha|md5","priv_proto":"aes|des","port":161,"timeout":2,"retries":1}
    """
    # Quick port probes
    p22  = is_tcp_open(ip, 22, 0.7)
    p135 = is_tcp_open(ip, 135, 0.7)
    p445 = is_tcp_open(ip, 445, 0.7)
    p161 = is_tcp_open(ip, 161, 0.7)

    # ---------- Windows (WMI) ----------
    if (p135 or p445) and creds_windows:
        for u, p in creds_windows:
            try:
                d = collect_windows_wmi(ip, u, p)
                if isinstance(d, dict) and ("Error" not in d):
                    if use_http:
                        _merge_http_into_record(d, http_guess(ip))
                    _normalize_storage_in_record(d)
                    d.setdefault("LAN IP Address", ip)
                    d.setdefault("Hostname", d.get("Hostname") or ip)
                    return d
            except Exception as e:
                log.debug("WMI failed for %s with %s: %s", ip, u, e)

    # ---------- Linux/ESXi (SSH) ----------
    if p22 and creds_linux:
        for u, p in creds_linux:
            try:
                d = collect_linux_or_esxi_ssh(ip, u, p)
                if isinstance(d, dict) and ("Error" not in d):
                    if use_http:
                        _merge_http_into_record(d, http_guess(ip))
                    _normalize_storage_in_record(d)
                    d.setdefault("LAN IP Address", ip)
                    d.setdefault("Hostname", d.get("Hostname") or ip)
                    return d
            except Exception as e:
                log.debug("SSH failed for %s with %s: %s", ip, u, e)

    # ---------- SNMP (Preferred for non-Windows/Linux) ----------
    if _PYSNMP_OK and (p161 or (snmp_v3 and snmp_v3.get("user")) or snmp_v2c):
        # Prefer v3
        if isinstance(snmp_v3, dict) and snmp_v3.get("user"):
            try:
                d = snmp_collect_basic(
                    ip,
                    community="public",  # ignored for v3 internally
                    version="3",
                    timeout=int(snmp_v3.get("timeout", 2)),
                    retries=int(snmp_v3.get("retries", 1)),
                    v3_user=snmp_v3.get("user"),
                    v3_auth_key=snmp_v3.get("auth_key"),
                    v3_priv_key=snmp_v3.get("priv_key"),
                    v3_auth_proto=snmp_v3.get("auth_proto", "sha"),
                    v3_priv_proto=snmp_v3.get("priv_proto", "aes"),
                    port=int(snmp_v3.get("port", 161)),
                )
                if isinstance(d, dict) and ("Error" not in d):
                    if use_http:
                        _merge_http_into_record(d, http_guess(ip))
                    _normalize_storage_in_record(d)
                    d.setdefault("LAN IP Address", ip)
                    d.setdefault("Hostname", d.get("Hostname") or ip)
                    return d
            except Exception as e:
                log.debug("SNMP v3 failed for %s: %s", ip, e)

        # Then v2c
        if isinstance(snmp_v2c, dict):
            try:
                d = snmp_collect_basic(
                    ip,
                    community=snmp_v2c.get("community", "public"),
                    version=snmp_v2c.get("version", "2c"),
                    timeout=int(snmp_v2c.get("timeout", 2)),
                    retries=int(snmp_v2c.get("retries", 1)),
                    v3_user=None, v3_auth_key=None, v3_priv_key=None,
                    v3_auth_proto="sha", v3_priv_proto="aes",
                    port=int(snmp_v2c.get("port", 161)),
                )
                if isinstance(d, dict) and ("Error" not in d):
                    if use_http:
                        _merge_http_into_record(d, http_guess(ip))
                    _normalize_storage_in_record(d)
                    d.setdefault("LAN IP Address", ip)
                    d.setdefault("Hostname", d.get("Hostname") or ip)
                    return d
            except Exception as e:
                log.debug("SNMP v2c failed for %s: %s", ip, e)

        # If no config but port is open, still try default public
        if p161 and not (snmp_v3 or snmp_v2c):
            try:
                d = snmp_collect_basic(ip, community="public", version="2c", timeout=2, retries=1, port=161)
                if isinstance(d, dict) and ("Error" not in d):
                    if use_http:
                        _merge_http_into_record(d, http_guess(ip))
                    _normalize_storage_in_record(d)
                    d.setdefault("LAN IP Address", ip)
                    d.setdefault("Hostname", d.get("Hostname") or ip)
                    return d
            except Exception as e:
                log.debug("SNMP default public failed for %s: %s", ip, e)

    # ---------- Nmap Fallback (device type + open ports) ----------
    try:
        nm = nmap_discover([ip])
        if ip in nm and nm[ip]:
            open_ports = nm[ip]
            infra = _infer_infra_from_ports(open_ports)

            rec = _empty_schema(ip, infra=infra)
            # Attach port info as optional extras (harmless to Excel)
            rec["Open Ports"] = ",".join(str(p) for p in sorted(open_ports))

            # Try HTTP banners to enrich
            if use_http and any(p in open_ports for p in (80, 443, 8080, 8443, 631)):
                _merge_http_into_record(rec, http_guess(ip))

            return rec
    except Exception as e:
        log.debug("Nmap fallback failed for %s: %s", ip, e)

    # ---------- HTTP-only (last resort) ----------
    if use_http:
        http = http_guess(ip) or {}
        if http:
            rec = _empty_schema(ip, infra=http.get("type_guess", "HTTP Device"))
            _merge_http_into_record(rec, http)
            return rec

    # ---------- No luck ----------
    rec = _empty_schema(ip, infra="Unknown")
    rec["Collector"] = "None"
    rec["Note"] = "No suitable collector/credentials"
    return rec