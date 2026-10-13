#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ast_checker.py
Isolated child AST checker for Gate05 R38 publisher boundaries.
Only parses AST of target file; does NOT import or execute target module.
"""

import sys
import ast
import json
import hashlib

def compute_sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest().upper()

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"status": "ERROR", "error": "Missing target path argument"}), file=sys.stderr)
        sys.exit(2)
        
    target_path = sys.argv[1]
    
    with open(target_path, "rb") as f:
        raw_bytes = f.read()
        
    sha256 = compute_sha256(raw_bytes)
    size_bytes = len(raw_bytes)
    
    try:
        tree = ast.parse(raw_bytes, filename=target_path)
    except Exception as ex:
        print(json.dumps({
            "status": "PARSE_FAILED",
            "target_path": target_path,
            "sha256": sha256,
            "size_bytes": size_bytes,
            "error": str(ex)
        }), file=sys.stderr)
        sys.exit(1)
        
    docstring = ast.get_docstring(tree)
    has_docstring = docstring is not None and len(docstring) > 0
    
    all_nodes = list(ast.walk(tree))
    total_node_count = len(all_nodes)
    
    func_nodes = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    class_nodes = [n for n in tree.body if isinstance(n, ast.ClassDef)]
    import_nodes = [n for n in all_nodes if isinstance(n, (ast.Import, ast.ImportFrom))]
    
    functions = []
    for fn in func_nodes:
        functions.append({
            "name": fn.name,
            "lineno": fn.lineno,
            "end_lineno": getattr(fn, "end_lineno", None),
            "arg_count": len(fn.args.args)
        })
        
    result = {
        "status": "AST_PARSED_SUCCESS",
        "target_path": target_path,
        "sha256": sha256,
        "size_bytes": size_bytes,
        "has_module_docstring": has_docstring,
        "docstring_len": len(docstring) if docstring else 0,
        "total_ast_nodes": total_node_count,
        "top_level_function_count": len(func_nodes),
        "top_level_class_count": len(class_nodes),
        "import_statement_count": len(import_nodes),
        "functions": functions
    }
    
    # Print formatted JSON to stdout
    print(json.dumps(result, indent=2))
    sys.exit(0)

if __name__ == "__main__":
    main()
