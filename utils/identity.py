# -*- coding: utf-8 -*-
"""
Identity Utilities Module

This module contains functions for validating and handling identity-related data.
"""

def valid_serial(s):
    """
    Validate a serial number to ensure it is not empty or a placeholder.
    """
    if not s:
        return False
    s = s.strip()
    return s and s.upper() not in ("N/A", "UNKNOWN", "TO BE FILLED BY O.E.M.", "DEFAULT STRING")

def pick_identity_from_data(data: dict):
    """
    Determine the best unique identifier from collected data.
    """
    from .helpers import normalize_mac # local import to avoid circular dependency
    uuid = (data.get("Asset UUID") or "").strip() or None
    if uuid and uuid.upper() != "N/A":
        return ("uuid", uuid)
    sn = (data.get("Serial Number") or "").strip() or None
    if sn and valid_serial(sn):
        return ("serial", sn)
    mac = normalize_mac(data.get("MAC Address"))
    if mac and mac.upper() != "NO MAC ADDRESS FOUND":
        return ("mac", mac)
    return (None, None)