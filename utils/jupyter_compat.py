# -*- coding: utf-8 -*-
"""
Compat layer: list_running_servers() يعمل على Notebook 6.x و Notebook 7.x (jupyter_server).
لو الباكتجات مش موجودة، بيرجع قائمة فاضية بدل ما يكسر البرنامج.
"""
from typing import List, Dict, Any

def list_running_servers() -> List[Dict[str, Any]]:
    # Notebook 6.x
    try:
        from notebook import notebookapp as nbapp  # type: ignore
        return list(nbapp.list_running_servers())
    except Exception:
        pass
    # Notebook 7.x (moved to jupyter_server)
    try:
        from jupyter_server import serverapp as nbapp  # type: ignore
        return list(nbapp.list_running_servers())
    except Exception:
        return []
