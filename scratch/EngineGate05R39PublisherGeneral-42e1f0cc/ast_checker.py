#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ast_checker.py
Isolated child AST parser for Gate05 R39 publisher verification.
Strictly parses target file text using stdlib ast.parse without importing or executing it.
"""

import os
import sys
import ast
import json
import hashlib
from datetime import datetime, timezone

def compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()

def main():
    if len(sys.argv) < 2:
        print("Usage: ast_checker.py <target_file>", file=sys.stderr)
        sys.exit(1)
        
    target_path = os.path.abspath(sys.argv[1])
    if not os.path.isfile(target_path):
        print(f"Error: Target file does not exist: {target_path}", file=sys.stderr)
        sys.exit(1)
        
    with open(target_path, "rb") as f:
        raw_bytes = f.read()
        
    source_sha = compute_sha256(raw_bytes)
    source_text = raw_bytes.decode("utf-8")
    source_lines = len(source_text.splitlines())
    
    # Parse AST
    try:
        tree = ast.parse(source_text, filename=target_path)
    except SyntaxError as ex:
        print(f"SyntaxError in {target_path}: {ex}", file=sys.stderr)
        sys.exit(2)
        
    # Walk AST nodes
    node_count = 0
    func_defs = []
    class_defs = []
    imports = []
    
    for node in ast.walk(tree):
        node_count += 1
        if isinstance(node, ast.FunctionDef):
            func_defs.append({
                "name": node.name,
                "lineno": node.lineno,
                "end_lineno": getattr(node, "end_lineno", node.lineno)
            })
        elif isinstance(node, ast.ClassDef):
            class_defs.append({
                "name": node.name,
                "lineno": node.lineno,
                "end_lineno": getattr(node, "end_lineno", node.lineno)
            })
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [a.name for a in node.names]
            mod = getattr(node, "module", None)
            imports.append({
                "module": mod,
                "names": names,
                "lineno": node.lineno
            })
            
    result = {
        "verdict": "AST_PARSED_SUCCESS",
        "target_file": target_path,
        "bytes": len(raw_bytes),
        "sha256": source_sha,
        "lines": source_lines,
        "ast_node_count": node_count,
        "function_count": len(func_defs),
        "functions": func_defs,
        "class_count": len(class_defs),
        "classes": class_defs,
        "import_count": len(imports),
        "imports": imports,
        "parsed_at_utc": datetime.now(timezone.utc).isoformat()
    }
    
    print(json.dumps(result, indent=2))
    sys.exit(0)

if __name__ == "__main__":
    main()
