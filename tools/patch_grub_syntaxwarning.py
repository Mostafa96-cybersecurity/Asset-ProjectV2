# -*- coding: utf-8 -*-
r"""
Patch grub.base SyntaxWarning: replace "\w" or '\w' with raw strings r"\w" / r'\w'
- يعمل Backup: base.py.bak
- يستخدم دالة استبدال لتفادي مشكلة backslash في re-replacement
"""
from __future__ import annotations
import os, sys, re

def find_grub_base():
    try:
        import grub.base as base
        return os.path.abspath(base.__file__)
    except Exception:
        for p in sys.path:
            cand = os.path.join(p, "grub", "base.py")
            if os.path.isfile(cand):
                return os.path.abspath(cand)
    return None

def main():
    path = find_grub_base()
    if not path:
        print("Could not locate grub/base.py in this venv.")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        src = f.read()

    bak = path + ".bak"
    if not os.path.exists(bak):
        with open(bak, "w", encoding="utf-8", newline="") as f:
            f.write(src)

    # طابق أي سلسلة فيها backslash-w: "\w" أو '\w'
    pat = re.compile(r'(?P<q>["\'])\\w(?P=q)')

    def repl(m: re.Match) -> str:
        q = m.group("q")
        return f"r{q}\\w{q}"  # نضيف بادئة r ونحتفظ بنفس نوع علامات الاقتباس

    new_src, n = pat.subn(repl, src)

    if n == 0:
        print("Nothing to change (maybe already patched).")
    else:
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(new_src)
        print(f"Patched {n} occurrence(s) in: {path}\nBackup at: {bak}")

if __name__ == "__main__":
    main()
