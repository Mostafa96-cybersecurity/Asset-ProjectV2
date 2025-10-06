# -*- coding: utf-8 -*-
"""
SSH Collector Module (smart Linux/ESXi/Network Devices) — Pro
-------------------------------------------------------------
Public API:
    collect_linux_or_esxi_ssh(
        ip, username, password=None, pkey=None, port=22, timeout=8,
        enable_password=None
    ) -> dict

Returns a dict compatible with ASSET_HEADERS:
    Hostname, Working User, Domain, Device Model, Device Infrastructure, OS Name,
    Installed RAM (GB), LAN IP Address, Storage, Manufacturer, Serial Number,
    Processor, System SKU, Active GPU, Connected Screens, Status
"""

from __future__ import annotations

import logging
import re
import time
from typing import Optional, Dict, Any, Tuple, List
import paramiko

log = logging.getLogger(__name__)

# ---------- helpers ----------

def _ssh_connect(ip, username, password=None, pkey=None, port=22, timeout=8) -> paramiko.SSHClient:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    if pkey and isinstance(pkey, str):
        try:
            pkey = paramiko.RSAKey.from_private_key_file(pkey)
        except Exception:
            pkey = None
    client.connect(
        ip,
        username=username,
        password=password,
        pkey=pkey,
        port=port,
        timeout=timeout,
        auth_timeout=timeout,
        banner_timeout=timeout,
        look_for_keys=False,
        allow_agent=False,
    )
    return client

def _run(client: paramiko.SSHClient, cmd: str, timeout: int = 8) -> str:
    try:
        stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
        out = (stdout.read() or b"").decode(errors="ignore").strip()
        if out:
            return out
        err = (stderr.read() or b"").decode(errors="ignore").strip()
        return err or ""
    except Exception:
        return ""

def _invoke_shell(client: paramiko.SSHClient, timeout: float = 3.0):
    chan = client.invoke_shell()
    chan.settimeout(timeout)
    return chan

def _read_until(chan, patterns=("#", ">", "Password:", "password:"), timeout=3.0) -> str:
    buf = ""
    end = time.time() + timeout
    while time.time() < end:
        try:
            if chan.recv_ready():
                data = chan.recv(65535).decode(errors="ignore")
                buf += data
                if any(p in buf for p in patterns):
                    break
            else:
                time.sleep(0.05)
        except Exception:
            break
    return buf

def _send_cmd(chan, cmd: str, wait=0.2, until=("#", ">"), timeout=3.0) -> str:
    if not cmd.endswith("\n"):
        cmd += "\n"
    try:
        chan.send(cmd)
    except Exception:
        return ""
    time.sleep(wait)
    return _read_until(chan, patterns=until, timeout=timeout)

def _first_nonempty(*vals) -> str:
    for v in vals:
        if v and isinstance(v, str) and v.strip():
            return v.strip()
    return ""

def _to_gb(num_bytes: int) -> int:
    try:
        gb = int(round(num_bytes / (1024**3)))
        return max(gb, 0)
    except Exception:
        return 0

def _parse_kv(text: str) -> Dict[str, str]:
    out = {}
    for line in (text or "").splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip().lower()] = v.strip()
    return out

# ---------- platform detection ----------

def _detect_platform(client) -> str:
    # Linux?
    uname = _run(client, "uname -s")
    if "Linux" in uname:
        return "linux"

    # ESXi?
    esx = _run(client, "vmware -v")
    if "VMware ESXi" in esx:
        return "esxi"
    if "VMkernel" in _run(client, "uname -a"):
        return "esxi"

    # Network vendors
    sv = _run(client, "show version")
    if sv:
        low = sv.lower()
        if any(v in low for v in ["cisco ios", "cisco nx-os", "cisco ios-xe", "ios-xe", "cisco catalyst", "cisco ios software"]):
            return "cisco"
        if "junos" in low or "juniper networks" in low:
            return "juniper"
        if "arubaos" in low or "hewlett packard enterprise" in low or "provision" in low:
            return "aruba"
        if "huawei" in low or "vrp (r)" in low or "vrp" in low:
            return "huawei"

    # FortiGate:
    gss = _run(client, "get system status")
    if "Version:" in gss and ("FortiGate" in gss or "FortiOS" in gss):
        return "fortigate"

    # MikroTik:
    mik = _run(client, "/system resource print")
    if "routeros" in mik.lower():
        return "mikrotik"

    return "unknown"

# ---------- Linux ----------

def _linux_os_name(client) -> str:
    out = _run(client, "cat /etc/os-release")
    name = ""
    if out:
        for line in out.splitlines():
            if line.startswith("PRETTY_NAME="):
                name = line.split("=", 1)[1].strip().strip('"').strip("'")
                break
    return name or _run(client, "lsb_release -d | awk -F':\\t' '{print $2}'")

def _linux_hostname(client) -> str:
    return _first_nonempty(_run(client, "hostname -f"), _run(client, "hostname"))

def _linux_domain(client) -> str:
    dom = _run(client, "dnsdomainname")
    if dom and dom.lower() != "(none)":
        return dom.strip()
    fqdn = _run(client, "hostname -f")
    if fqdn and "." in fqdn:
        return fqdn.split(".", 1)[1].strip()
    rc = _run(client, "awk '/^search/ {print $2; exit}' /etc/resolv.conf")
    return rc.strip()

def _linux_user(client) -> str:
    return _first_nonempty(_run(client, "who | awk 'NR==1{print $1}'"), _run(client, "logname"), _run(client, "whoami"))

def _linux_ip(client) -> str:
    ip = _run(client, "hostname -I | awk '{print $1}'")
    if ip:
        return ip
    ip = _run(client, "ip -4 addr show | awk '/inet /{print $2}' | awk -F/ 'NR==1{print $1}'")
    return ip

def _linux_ram_gb(client) -> int:
    mem = _run(client, "free -b | awk '/Mem:/ {print $2}'")
    try:
        return _to_gb(int(mem.strip()))
    except Exception:
        return 0

def _linux_storage_list(client) -> List[Tuple[str, int]]:
    out = _run(client, "lsblk -b -dn -o NAME,SIZE,TYPE | awk '$3==\"disk\"{print $1, $2}'")
    disks = []
    for line in (out or "").splitlines():
        parts = line.split()
        if len(parts) >= 2:
            name, size = parts[0], parts[1]
            try:
                disks.append((name, _to_gb(int(size))))
            except Exception:
                pass
    return disks

def _linux_cpu(client) -> str:
    out = _run(client, "lscpu | awk -F: '/Model name/ {print $2}'")
    return out.strip()

def _linux_gpu(client) -> str:
    out = _run(client, "lspci | awk -F': ' '/ VGA compatible controller|3D controller/ {print $2}' | head -1")
    return out.strip()

def _linux_dmi_field(client, path: str, dmidec: str) -> str:
    val = _run(client, f"cat {path} 2>/dev/null")
    if val:
        return val.strip()
    return _run(client, f"dmidecode -s {dmidec} 2>/dev/null").strip()

def _collect_linux(client) -> Dict[str, Any]:
    data: Dict[str, Any] = {}
    data["Hostname"] = _linux_hostname(client)
    data["Working User"] = _linux_user(client)
    data["Domain"] = _linux_domain(client)
    data["OS Name"] = _linux_os_name(client)
    data["Installed RAM (GB)"] = _linux_ram_gb(client)
    data["LAN IP Address"] = _linux_ip(client)
    disks = _linux_storage_list(client)
    if disks:
        data["Storage"] = "; ".join([f"{n}: {sz} GB" for n, sz in disks])
    data["Manufacturer"] = _linux_dmi_field(client, "/sys/class/dmi/id/sys_vendor", "system-manufacturer")
    data["Device Model"] = _linux_dmi_field(client, "/sys/class/dmi/id/product_name", "system-product-name")
    data["Serial Number"] = _linux_dmi_field(client, "/sys/class/dmi/id/product_serial", "system-serial-number")
    data["System SKU"] = _linux_dmi_field(client, "/sys/class/dmi/id/product_sku", "system-sku-number")
    cpu = _linux_cpu(client)
    if cpu: data["Processor"] = cpu
    gpu = _linux_gpu(client)
    if gpu: data["Active GPU"] = gpu
    data["Device Infrastructure"] = "Server" if "server" in (data.get("Device Model","")+" "+data.get("OS Name","")).lower() else "Linux"
    data["Status"] = "OK"
    return data

# ---------- ESXi ----------

def _collect_esxi(client) -> Dict[str, Any]:
    data: Dict[str, Any] = {}
    data["Hostname"] = _first_nonempty(_run(client, "esxcli system hostname get | awk '/Host Name/ {print $3}'"), _run(client, "hostname"))
    data["OS Name"] = _first_nonempty(_run(client, "vmware -v"), "VMware ESXi")
    plat = _run(client, "esxcli hardware platform get")
    kv = _parse_kv(plat)
    data["Manufacturer"] = _first_nonempty(kv.get("vendor name"), kv.get("vendorname"), kv.get("vendor"))
    data["Device Model"] = _first_nonempty(kv.get("product name"), kv.get("productname"), kv.get("product"))
    data["Serial Number"] = _first_nonempty(kv.get("serial number"), kv.get("serialnumber"), kv.get("serial"))
    mem_mb = _run(client, "esxcli hardware memory get | awk '/Physical Memory:/{print $3}'")
    try:
        data["Installed RAM (GB)"] = int(round(float(mem_mb)/1024))
    except Exception:
        pass
    data["LAN IP Address"] = _run(client, "esxcli network ip interface ipv4 get | awk 'NR>1 && $1==\"vmk0\" {print $2}'")
    ndev = _run(client, "esxcli storage core device list | grep -c '^Device:'")
    if ndev:
        data["Storage"] = f"{ndev} devices (see host for details)"
    data["Device Infrastructure"] = "Hypervisor"
    data["Status"] = "OK"
    return data

# ---------- Cisco (improved) ----------

_CISCO_INFRA_MAP = (
    ("WS-C", "Switch"), ("C9200", "Switch"), ("C9300", "Switch"), ("C9500", "Switch"),
    ("C3850", "Switch"), ("C3750", "Switch"), ("C3560", "Switch"),
    ("N9K", "Switch"), ("N3K", "Switch"), ("N7K", "Switch"),
    ("ISR", "Router"), ("ASR", "Router"), ("C8", "Router"), ("C4", "Router"), ("C29", "Router"), ("C89", "Router"),
    ("ASA", "Firewall"), ("FTD", "Firewall"),
)

def _infer_cisco_infra_from_pid(pid: str) -> str:
    p = (pid or "").upper()
    for prefix, kind in _CISCO_INFRA_MAP:
        if p.startswith(prefix):
            return kind
    # ASA/FTD may show in show version without PID
    if p.startswith("ASA") or "ASA" in p:
        return "Firewall"
    return "Network"

def _cisco_enter_enable(chan, enable_password: Optional[str], timeout=3.0):
    prompt = _read_until(chan, timeout=timeout)
    if ">" in prompt and enable_password:
        _send_cmd(chan, "enable", until=("Password:", "password:"), timeout=timeout)
        _send_cmd(chan, enable_password, until=("#", ">"), timeout=timeout)
    # turn off paging (IOS/NX-OS)
    _send_cmd(chan, "terminal length 0", until=("#", ">"), timeout=timeout)

def _cisco_pid_sn(inv_txt: str, ver_txt: str) -> Tuple[str, str]:
    pid, sn = "", ""
    # From show inventory
    for m in re.finditer(r"PID:\s*([A-Z0-9\-]+).*?SN:\s*([A-Z0-9]+)", inv_txt or "", re.IGNORECASE | re.DOTALL):
        pid = m.group(1).upper(); sn = m.group(2).upper()
        if pid and sn:
            return pid, sn
    # Some platforms only show SN in version
    m = re.search(r"Processor board ID\s+([A-Z0-9]+)", ver_txt or "", re.IGNORECASE)
    if m:
        sn = m.group(1).upper()
    # Model hint from version
    m = re.search(r"\bcisco\s+([A-Z0-9\-]+)\b", ver_txt or "", re.IGNORECASE)
    if m and not pid:
        pid = m.group(1).upper()
    m2 = re.search(r"Model number\s*:\s*([A-Z0-9\-]+)", ver_txt or "", re.IGNORECASE)
    if m2:
        pid = (m2.group(1) or pid).upper()
    return pid, sn

def _collect_cisco(client, enable_password: Optional[str]=None) -> Dict[str, Any]:
    data: Dict[str, Any] = {"Manufacturer": "Cisco", "Device Infrastructure": "Network", "OS Name": "Cisco IOS/NX-OS", "Status": "OK"}

    # shell mode for paging/enable & multiple commands
    chan = _invoke_shell(client, timeout=3.0)
    _cisco_enter_enable(chan, enable_password, timeout=3.0)

    run_cfg = _send_cmd(chan, "show running-config | include ^hostname", until=("#", ">"), timeout=3.0)
    ver_txt = _send_cmd(chan, "show version", until=("#", ">"), timeout=3.0)
    inv_txt = _send_cmd(chan, "show inventory", until=("#", ">"), timeout=3.0)

    # Hostname
    m = re.search(r"^hostname\s+([A-Za-z0-9\-\._]+)", run_cfg, re.MULTILINE)
    hostname = m.group(1).strip() if m else ""
    if not hostname:
        m = re.search(r"^([A-Za-z0-9\-\._]+)\s+uptime is", ver_txt, re.MULTILINE)
        hostname = m.group(1).strip() if m else ""

    # Version
    version = ""
    m = re.search(r"Cisco IOS[^,]*,.*Version\s+([^\s,]+)", ver_txt, re.IGNORECASE)
    if m: version = m.group(1).strip()
    if not version:
        m = re.search(r"NX-OS.*Version\s+([^\s,]+)", ver_txt, re.IGNORECASE)
        if m: version = m.group(1).strip()

    # PID / Serial
    pid, serial = _cisco_pid_sn(inv_txt, ver_txt)

    # LAN IP: try multiple families
    ip = _run(client, "show ip interface brief | include up | awk '{print $2}' | head -1")
    if not ip:
        ip = _run(client, "show interfaces vlan 1 | include Internet address | awk -F'address is' '{print $2}' | awk '{print $1}'")
    if not ip:
        ip = _run(client, "show interface | include Internet address | head -1 | awk -F'address is' '{print $2}' | awk '{print $1}'")

    # Infra from PID
    infra = _infer_cisco_infra_from_pid(pid)

    data.update({
        "Hostname": hostname or "",
        "Device Model": pid or "",
        "Serial Number": serial or "",
        "LAN IP Address": ip or "",
        "OS Name": ("Cisco IOS " + version).strip() if version else data["OS Name"],
        "System SKU": pid or "",
        "Device Infrastructure": infra,
    })
    return data

# ---------- Other Network Vendors ----------

def _collect_juniper(client) -> Dict[str, Any]:
    _run(client, "set cli screen-length 0")
    ver = _run(client, "show version")
    hw  = _run(client, "show chassis hardware")
    data: Dict[str, Any] = {"Manufacturer": "Juniper", "OS Name": "JunOS", "Device Infrastructure": "Network", "Status": "OK"}
    data["Hostname"] = _run(client, "show configuration system host-name | display set | awk '{print $3}'")
    for line in hw.splitlines():
        low = line.lower()
        if "serial number" in low:
            data["Serial Number"] = line.split()[-1]
        if "chassis" in low and "(" in line and ")" in line and not data.get("Device Model"):
            data["Device Model"] = line.strip()
    ip = _run(client, "show interfaces terse | match inet | head -1 | awk '{print $2}' | cut -d/ -f1")
    if ip: data["LAN IP Address"] = ip
    return data

def _collect_fortigate(client) -> Dict[str, Any]:
    st = _run(client, "get system status")
    data: Dict[str, Any] = {"Manufacturer": "Fortinet", "OS Name": "FortiOS", "Device Infrastructure": "Firewall", "Status": "OK"}
    data["Hostname"] = _first_nonempty(_run(client, "get system hostname"), "")
    for line in st.splitlines():
        low = line.lower()
        if "version:" in low:
            data["OS Name"] = line.strip()
        if "serial-number" in low:
            data["Serial Number"] = line.split(":",1)[-1].strip()
        if "model name" in low:
            val = line.split(":",1)[-1].strip()
            if "FortiGate" in val:
                data["Device Model"] = val
    ip = _run(client, "get system interface | grep -i address | head -1 | awk -F: '{print $2}' | awk '{print $1}'")
    if ip: data["LAN IP Address"] = ip
    return data

def _collect_mikrotik(client) -> Dict[str, Any]:
    data: Dict[str, Any] = {"Manufacturer": "MikroTik", "OS Name": "RouterOS", "Device Infrastructure": "Network", "Status": "OK"}
    rb = _run(client, "/system routerboard print")
    rs = _run(client, "/system resource print")
    for line in (rb + "\n" + rs).splitlines():
        low = line.lower()
        if "model" in low and ":" in line and not data.get("Device Model"):
            data["Device Model"] = line.split(":",1)[-1].strip()
        if "serial-number" in low:
            data["Serial Number"] = line.split(":",1)[-1].strip()
    data["Hostname"] = _run(client, "/system identity print | awk -F': ' '/name:/ {print $2}'")
    ip = _run(client, "/ip address print | awk '/ether|bridge|vlan/ {print $2}' | head -1")
    if ip: data["LAN IP Address"] = ip
    return data

def _collect_aruba(client) -> Dict[str, Any]:
    _run(client, "no paging")
    ver = _run(client, "show version")
    inv = _run(client, "show inventory")
    data: Dict[str, Any] = {"Manufacturer": "HPE/Aruba", "Device Infrastructure": "Network", "OS Name": "ArubaOS/ProVision", "Status": "OK"}
    for line in (ver + "\n" + inv).splitlines():
        low = line.lower()
        if "serial" in low and ":" in line:
            data["Serial Number"] = line.split(":",1)[-1].strip()
        if ("model" in low or "pid" in low) and ":" in line and not data.get("Device Model"):
            data["Device Model"] = line.split(":",1)[-1].strip()
    data["Hostname"] = _run(client, "show running-config | include hostname | awk '{print $2}'")
    ip = _run(client, "show ip | awk '/IP address/ {print $3; exit}'")
    if ip: data["LAN IP Address"] = ip
    return data

def _collect_huawei(client) -> Dict[str, Any]:
    _run(client, "screen-length 0 temporary")
    ver = _run(client, "display version")
    data: Dict[str, Any] = {"Manufacturer": "Huawei", "Device Infrastructure": "Network", "OS Name": "VRP", "Status": "OK"}
    for line in ver.splitlines():
        low = line.lower()
        if "version" in low and ":" in line:
            data["OS Name"] = line.strip()
        if "device model" in low or "product name" in low:
            data["Device Model"] = line.split(":",1)[-1].strip()
        if "serial number" in low:
            data["Serial Number"] = line.split(":",1)[-1].strip()
    data["Hostname"] = _run(client, "display current-configuration | include sysname | awk '{print $2}'")
    ip = _run(client, "display ip interface brief | include up | awk '{print $4}' | head -1")
    if ip: data["LAN IP Address"] = ip
    return data

# ---------- main entry ----------

def collect_linux_or_esxi_ssh(
    ip,
    username,
    password=None,
    pkey=None,
    port=22,
    timeout=8,
    enable_password: Optional[str] = None,
) -> Dict[str, Any]:
    data = {"IP Address": ip}
    client = None
    try:
        client = _ssh_connect(ip, username, password=password, pkey=pkey, port=port, timeout=timeout)
        platform = _detect_platform(client)

        if platform == "linux":
            out = _collect_linux(client)
        elif platform == "esxi":
            out = _collect_esxi(client)
        elif platform == "cisco":
            out = _collect_cisco(client, enable_password=enable_password)
        elif platform == "juniper":
            out = _collect_juniper(client)
        elif platform == "fortigate":
            out = _collect_fortigate(client)
        elif platform == "mikrotik":
            out = _collect_mikrotik(client)
        elif platform == "aruba":
            out = _collect_aruba(client)
        elif platform == "huawei":
            out = _collect_huawei(client)
        else:
            out = {}
            out["Hostname"] = _first_nonempty(_run(client, "hostname -f"), _run(client, "hostname"))
            out["OS Name"] = _first_nonempty(_run(client, "uname -a"), "Unknown")
            out["LAN IP Address"] = _first_nonempty(_run(client, "hostname -I | awk '{print $1}'"), "")
            out["Device Infrastructure"] = "Unknown"
            out["Status"] = "OK"

        # Ensure required keys exist
        out.setdefault("Hostname", "")
        out.setdefault("Working User", "")
        out.setdefault("Domain", "")
        out.setdefault("Device Model", "")
        out.setdefault("Device Infrastructure", "")
        out.setdefault("OS Name", "")
        out.setdefault("Installed RAM (GB)", 0)
        out.setdefault("LAN IP Address", "")
        out.setdefault("Storage", "")
        out.setdefault("Manufacturer", "")
        out.setdefault("Serial Number", "")
        out.setdefault("Processor", "")
        out.setdefault("System SKU", "")
        out.setdefault("Active GPU", "")
        out.setdefault("Connected Screens", "")
        out.setdefault("Status", "OK")

        out["IP Address"] = ip
        return out

    except paramiko.AuthenticationException:
        log.error(f"SSH authentication failed for {ip}.")
        return {"IP Address": ip, "Status": "Auth Failed", "Error": "SSH authentication failed."}
    except paramiko.SSHException as e:
        log.error(f"SSH connection error for {ip}: {e}")
        return {"IP Address": ip, "Status": "SSH Error", "Error": f"SSH connection error: {e}"}
    except Exception as e:
        log.error(f"Unexpected SSH error for {ip}: {e}")
        return {"IP Address": ip, "Status": "Error", "Error": f"Unexpected SSH error: {e}"}
    finally:
        try:
            if client:
                client.close()
        except Exception:
            pass
