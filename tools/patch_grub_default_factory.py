# -*- coding: utf-8 -*-
"""
Patch grub.base: replace
    search_store: DfltSearchStore = DfltSearchStore()
with
    search_store: DfltSearchStore = field(default_factory=DfltSearchStore)

- يعمل Backup: base.py.bak
- يضيف: from dataclasses import field (لو ناقص)
"""
from __future__ import annotations
import os, sys, re, inspect

def find_grub_base():
    try:
        import grub.base as base
        return os.path.abspath(base.__file__)
    except Exception:
        # ابحث يدويًا في sys.path
        for p in sys.path:
            cand = os.path.join(p, "grub", "base.py")
            if os.path.isfile(cand):
                return os.path.abspath(cand)
    return None

def patch_file(path: str) -> bool:
    with open(path, "r", encoding="utf-8") as f:
        src = f.read()

    orig = src

    # 1) أضف field import لو ناقص
    if re.search(r"\bfrom\s+dataclasses\s+import\b", src):
        def add_field(m):
            line = m.group(0)
            if "field" in line:
                return line
            return line.rstrip() + ", field"
        src = re.sub(r"(?m)^\s*from\s+dataclasses\s+import\s+[^\n]+", add_field, src, count=1)
    else:
        # حط الاستيراد بعد الـ imports الأولى
        lines = src.splitlines()
        insert_at = 0
        for i, line in enumerate(lines[:20]):
            if line.strip().startswith(("from __future__", "#!", "# -*-", "# coding")):
                insert_at = i + 1
        lines.insert(insert_at, "from dataclasses import field")
        src = "\n".join(lines)

    # 2) بدّل الـ default
    # نمط دقيق لحقل search_store
    pattern = re.compile(
        r"""^(?P<i>\s*)search_store\s*:\s*(?P<t>[^\n=]+?)\s*=\s*DfltSearchStore\s*\(\s*\)\s*$""",
        re.MULTILINE
    )
    src, n1 = pattern.subn(r"\g<i>search_store: \g<t> = field(default_factory=DfltSearchStore)", src)

    changed = n1 > 0
    if not changed:
        print("No 'search_store' default pattern found in:", path)
        return False

    bak = path + ".bak"
    if not os.path.exists(bak):
        with open(bak, "w", encoding="utf-8", newline="") as f:
            f.write(orig)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)

    print(f"Patched OK: {path}  (backup: {bak})")
    return True

def main():
    base_path = find_grub_base()
    if not base_path:
        print("Could not locate grub/base.py. Is the 'grub' package installed in this venv?")
        sys.exit(1)
    patched = patch_file(base_path)
    if not patched:
        print("Nothing changed. The file may already be fixed or pattern differs.")
    else:
        print("Done.")

if __name__ == "__main__":
    main()
