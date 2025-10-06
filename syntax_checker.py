#!/usr/bin/env python3
"""Syntax Checker for Python Files"""

import os
import ast

def check_syntax_errors():
    """Check all Python files for syntax errors"""
    errors_found = []
    
    python_files = [f for f in os.listdir('.') if f.endswith('.py')]
    
    for filename in python_files:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            ast.parse(content)
            print(f"✅ {filename}: OK")
        except SyntaxError as e:
            error_msg = f"❌ {filename}: Line {e.lineno}: {e.msg}"
            print(error_msg)
            errors_found.append(error_msg)
        except UnicodeDecodeError as e:
            error_msg = f"❌ {filename}: Encoding error: {e}"
            print(error_msg)
            errors_found.append(error_msg)
        except Exception as e:
            error_msg = f"❌ {filename}: {e}"
            print(error_msg)
            errors_found.append(error_msg)
    
    print(f"\n📊 Summary: {len(errors_found)} files with syntax errors out of {len(python_files)} Python files")
    return errors_found

if __name__ == "__main__":
    check_syntax_errors()