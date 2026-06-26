"""Deterministic Python source parser built on the standard library ``ast``.

Unlike LLM-based parsers, this produces exact line ranges, symbol kinds, and
local import edges by walking the real abstract syntax tree. It is fully
model-agnostic: the MCP server calls it directly, so the knowledge graph is the
same regardless of which model the Cursor user has.
"""

from __future__ import annotations

import ast
import os
from typing import Any


def _first_doc_line(node: ast.AST) -> str:
    """Return a one-line description from a node's docstring, if any."""
    doc = ast.get_docstring(node)
    if not doc:
        return ""
    return doc.strip().splitlines()[0].strip()


def _end_line(node: ast.AST, fallback: int) -> int:
    """End line of a node, tolerating older nodes without end_lineno."""
    return int(getattr(node, "end_lineno", None) or fallback)


def _decorator_names(node: ast.AST) -> list[str]:
    names: list[str] = []
    for dec in getattr(node, "decorator_list", []) or []:
        names.append(_name_of(dec))
    return [n for n in names if n]


def _name_of(node: ast.AST) -> str:
    """Best-effort dotted name for an expression node (decorators, bases)."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _name_of(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    if isinstance(node, ast.Call):
        return _name_of(node.func)
    if isinstance(node, ast.Subscript):
        return _name_of(node.value)
    return ""


def _is_property(member: ast.AST) -> bool:
    return any(
        d in ("property", "cached_property", "functools.cached_property")
        for d in _decorator_names(member)
    )


def _member_kind(member: ast.AST, parent: ast.ClassDef) -> str:
    decs = _decorator_names(member)
    if "staticmethod" in decs:
        return "static"
    if "classmethod" in decs:
        return "classmethod"
    if _is_property(member):
        return "getter"
    if isinstance(member, ast.FunctionDef) and member.name == "__init__":
        return "constructor"
    return "method"


def _skip_member(name: str) -> bool:
    """Skip trivial dunders that add noise without aiding navigation."""
    return name in {
        "__repr__",
        "__str__",
        "__hash__",
        "__eq__",
        "__ne__",
        "__len__",
    }


def _parse_class(node: ast.ClassDef, file_rel: str) -> dict[str, Any]:
    members: dict[str, Any] = {}
    is_enum = any("Enum" in _name_of(b) for b in node.bases)
    for child in node.body:
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if _skip_member(child.name):
                continue
            # Skip private helpers unless dunder constructor.
            if child.name.startswith("_") and child.name != "__init__":
                continue
            members[child.name] = {
                "kind": _member_kind(child, node),
                "lines": [child.lineno, _end_line(child, child.lineno)],
            }
    return {
        "kind": "enum" if is_enum else "class",
        "file": file_rel,
        "lines": [node.lineno, _end_line(node, node.lineno)],
        "extends": [_name_of(b) for b in node.bases if _name_of(b)],
        "description": _first_doc_line(node),
        "members": members,
    }


def _resolve_relative_import(
    node: ast.ImportFrom, file_rel: str, source_root: str
) -> str | None:
    """Resolve a ``from . import x`` style relative import to a repo-relative path."""
    pkg_dir = os.path.dirname(file_rel)
    level = node.level or 0
    for _ in range(level - 1):
        pkg_dir = os.path.dirname(pkg_dir)
    target = node.module.replace(".", "/") if node.module else ""
    rel = os.path.normpath(os.path.join(pkg_dir, target)) if target else pkg_dir
    return _module_to_path(rel, source_root)


def _module_to_path(rel_no_ext: str, source_root: str) -> str | None:
    """Map a module path (no extension) to an existing local source file."""
    candidates = [f"{rel_no_ext}.py", os.path.join(rel_no_ext, "__init__.py")]
    for cand in candidates:
        if os.path.isfile(os.path.join(source_root, cand)):
            return cand.replace(os.sep, "/")
    return None


def parse_python_file(abs_path: str, source_root: str) -> dict[str, Any]:
    """Parse a single Python file into knowledge-graph file + symbol entries.

    Returns a dict with keys: ``file`` (the repo-relative key), ``file_entry``,
    ``symbols`` (mapping of symbol name -> entry), and ``error`` if parsing
    failed. ``imports`` in the file entry contains only local project imports.
    """
    file_rel = os.path.relpath(abs_path, source_root).replace(os.sep, "/")
    try:
        with open(abs_path, "r", encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        return {"file": file_rel, "error": f"read failed: {exc}"}

    line_count = text.count("\n") + (0 if text.endswith("\n") else 1) if text else 0

    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        return {
            "file": file_rel,
            "file_entry": {
                "description": f"(unparseable: {exc.msg})",
                "lines": line_count,
                "symbols": [],
                "imports": [],
            },
            "symbols": {},
            "error": f"syntax error: {exc.msg}",
        }

    symbols: dict[str, Any] = {}
    imports: set[str] = set()

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            symbols[node.name] = _parse_class(node, file_rel)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith("_"):
                continue
            symbols[node.name] = {
                "kind": "function",
                "file": file_rel,
                "lines": [node.lineno, _end_line(node, node.lineno)],
                "description": _first_doc_line(node),
            }
        elif isinstance(node, ast.Import):
            for alias in node.names:
                resolved = _module_to_path(
                    alias.name.replace(".", "/"), source_root
                )
                if resolved:
                    imports.add(resolved)
        elif isinstance(node, ast.ImportFrom):
            if node.level and node.level > 0:
                resolved = _resolve_relative_import(node, file_rel, source_root)
                if resolved:
                    imports.add(resolved)
            elif node.module:
                resolved = _module_to_path(
                    node.module.replace(".", "/"), source_root
                )
                if resolved:
                    imports.add(resolved)

    module_doc = _first_doc_line(tree)
    description = module_doc or _infer_description(file_rel, symbols)

    return {
        "file": file_rel,
        "file_entry": {
            "description": description,
            "lines": line_count,
            "symbols": sorted(symbols.keys()),
            "imports": sorted(imports),
        },
        "symbols": symbols,
        "error": None,
    }


def _infer_description(file_rel: str, symbols: dict[str, Any]) -> str:
    """Fallback file description when there's no module docstring."""
    base = os.path.basename(file_rel)
    if base == "__init__.py":
        return f"Package init for {os.path.dirname(file_rel) or 'root'}"
    classes = [n for n, s in symbols.items() if s.get("kind") in ("class", "enum")]
    if classes:
        return f"Defines {', '.join(classes[:3])}"
    funcs = [n for n, s in symbols.items() if s.get("kind") == "function"]
    if funcs:
        return f"Functions: {', '.join(funcs[:3])}"
    return base
