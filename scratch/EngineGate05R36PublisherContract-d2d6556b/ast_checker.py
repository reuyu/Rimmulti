#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ast_checker.py
Standalone AST parser for publish_operator_pair.py (R36).
Does NOT import or execute publish_operator_pair.py.
"""
import ast
import json
import os
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: ast_checker.py <path_to_python_file>", file=sys.stderr)
        sys.exit(1)

    target_path = sys.argv[1]
    if not os.path.isfile(target_path):
        print(f"Error: Target file not found: {target_path}", file=sys.stderr)
        sys.exit(2)

    with open(target_path, "r", encoding="utf-8") as f:
        source_code = f.read()

    # Parse AST
    tree = ast.parse(source_code, filename=target_path)

    # Collect AST statistics
    classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                imports.append(f"{module}.{alias.name}")

    summary = {
        "status": "AST_PARSE_SUCCESS",
        "target_file": os.path.abspath(target_path),
        "source_bytes": len(source_code.encode("utf-8")),
        "source_lines": len(source_code.splitlines()),
        "root_node": type(tree).__name__,
        "body_node_count": len(tree.body),
        "functions_found": functions,
        "classes_found": classes,
        "imports_found": imports
    }

    print(json.dumps(summary, indent=2))
    sys.exit(0)

if __name__ == "__main__":
    main()
