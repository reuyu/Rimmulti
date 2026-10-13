# -*- coding: utf-8 -*-
"""
ast_checker.py
Child AST verification script for Gate05 R37.
Reads and parses the target Python source using standard library ast.parse.
DOES NOT import or execute the target module.
Outputs AST metadata JSON to stdout.
"""
import ast
import json
import sys
import os

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing target file path argument"}), file=sys.stderr)
        sys.exit(1)
        
    target_path = sys.argv[1]
    if not os.path.isfile(target_path):
        print(json.dumps({"error": f"Target file not found: {target_path}"}), file=sys.stderr)
        sys.exit(2)
        
    with open(target_path, "rb") as f:
        source_bytes = f.read()
        
    try:
        source_text = source_bytes.decode("utf-8")
        tree = ast.parse(source_text, filename=target_path)
    except Exception as ex:
        err_info = {
            "status": "SYNTAX_ERROR",
            "error_type": type(ex).__name__,
            "error_message": str(ex)
        }
        print(json.dumps(err_info, indent=2), file=sys.stderr)
        sys.exit(3)
        
    body_nodes = len(tree.body)
    functions = []
    classes = []
    imports = []
    
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            functions.append(node.name)
        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            for alias in node.names:
                imports.append(f"{mod}.{alias.name}")
                
    result = {
        "status": "SYNTAX_PASS",
        "target_file": target_path,
        "bytes": len(source_bytes),
        "body_node_count": body_nodes,
        "function_count": len(functions),
        "functions": functions,
        "class_count": len(classes),
        "classes": classes,
        "imports": imports,
        "child_sys_path": sys.path,
        "child_modules_loaded": sorted(list(sys.modules.keys()))
    }
    
    print(json.dumps(result, indent=2))
    sys.exit(0)

if __name__ == "__main__":
    main()
