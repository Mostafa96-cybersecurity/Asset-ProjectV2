def infer_infra(data: dict) -> str:
    atype = (data.get("Asset Type") or "").lower()
    descr = (data.get("sysDescr") or "").lower()
    title = (data.get("HTTP Title") or "").lower()
    manuf = (data.get("Manufacturer") or "").lower()
    model = (data.get("Device Model") or "").lower()

    if "windows" in atype: return "Windows"
    if "linux" in atype: return "Linux"
    if "hypervisor" in atype or "vmware" in descr or "esxi" in title: return "Hypervisor"

    bank = descr + " " + title + " " + manuf + " " + model
    if any(k in bank for k in ["printer", "laserjet", "officejet", "bizhub", "imageclass", "ricoh", "kyocera", "xerox", "brother", "canon", "command center"]):
        return "Printer"
    if any(k in bank for k in ["yealink", "grandstream", "polycom", "ip phone", "pbx", "3cx", "freepbx", "asterisk"]):
        return "IP Phone/PBX"
    if "fortigate" in bank or "fortios" in bank: return "Firewall"
    if "switch" in bank or "catalyst" in bank or "edgeswitch" in bank: return "Switch"
    if "router" in bank or "edgeos" in bank or "mikrotik" in bank: return "Router"
    if "ap " in bank or " access point" in bank or "fortiap" in bank or "omada" in bank: return "Access Point"
    if data.get("HTTP Type") == "Smart Display" or any(k in bank for k in ["smart tv", "webos", "bravia", "tizen", "android tv", "hisense", "philips tv"]):
        return "Smart Display"
    if atype == "snmp device": return "Network Device"
    if atype == "http device": return "HTTP Device"
    return "Unknown"
