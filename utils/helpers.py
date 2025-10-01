# -*- coding: utf-8 -*-
"""
Helper Functions Module

This module contains utility functions used across the application.
"""
import os

def safe_first(sequence, default=None):
    """
    Safely return the first element of a sequence or a default value.
    """
    try:
        return sequence[0] if sequence else default
    except Exception:
        return default

def normalize_mac(mac: str | None) -> str | None:
    """
    Normalize a MAC address to a standard format.
    """
    if not mac:
        return None
    m = mac.replace("-", ":").replace(".", ":").upper()
    m = ":".join([seg.zfill(2) for seg in m.replace(" ", "").split(":") if seg != ""])
    return m

def which(cmd: str) -> str | None:
    """
    Find the path to an executable command.
    """
    paths = os.environ.get("PATH", "").split(os.pathsep)
    exts = [""] if os.name != "nt" else ["", ".exe", ".bat", ".cmd"]
    for p in paths:
        for e in exts:
            full_path = os.path.join(p, cmd + e)
            if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                return full_path
    return None