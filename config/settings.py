import os
import json
import base64

APP_NAME = "NetworkAssetsCollector"

def config_dir():
    base = os.path.join(os.path.expanduser("~"), "AppData", "Roaming") if os.name == "nt" else os.path.expanduser("~/.config")
    path = os.path.join(base, APP_NAME)
    os.makedirs(path, exist_ok=True)
    return path

def _vault_dir():
    d = os.path.join(config_dir(), "vault")
    os.makedirs(d, exist_ok=True)
    return d

def _vault_path():
    return os.path.join(_vault_dir(), "creds.vault.json")

def _vault_load():
    try:
        with open(_vault_path(), "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _vault_save(d):
    try:
        with open(_vault_path(), "w", encoding="utf-8") as f:
            json.dump(d, f, indent=2)
    except Exception:
        pass

def _vault_put(secret_id: str, value: str):
    data = _vault_load()
    data[secret_id] = base64.b64encode((value or "").encode("utf-8")).decode("ascii")
    _vault_save(data)

def _vault_get(secret_id: str) -> str:
    data = _vault_load()
    v = data.get(secret_id, "")
    try:
        return base64.b64decode(v.encode("ascii")).decode("utf-8") if v else ""
    except Exception:
        return ""

CONFIG_PATH = os.path.join(config_dir(), "config.json")

def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "windows_creds": [],
        "linux_creds": [],
        "snmp_v2c": ["public"],
        "snmp_v3": {
            "user": "", "auth_key": "", "priv_key": "",
            "auth_proto": "SHA", "priv_proto": "AES128"
        },
        "ad": {"server": "", "base_dn": "", "username": "", "secret_id": "", "use_ssl": False}
    }

def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

def set_secret(secret_id: str, password: str):
    if not secret_id: return
    _vault_put(secret_id, password or "")

def get_secret(secret_id: str) -> str:
    if not secret_id: return ""
    return _vault_get(secret_id) or ""

def new_secret_id(prefix: str, existing_ids: set) -> str:
    i = 0
    while True:
        sid = f"{prefix}:{i}"
        if sid not in existing_ids:
            return sid
        i += 1
