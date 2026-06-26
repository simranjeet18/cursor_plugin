"""Knowledge graph assembly, persistence, incremental update, and querying.

The graph schema mirrors the original Claude ``project-manager`` plugin so the
two are interoperable, but it is written to ``.cursor/knowledge_graph.json`` and
generated deterministically from the Python AST parser.
"""

from __future__ import annotations

import ast
import json
import os
from datetime import datetime, timezone
from typing import Any

from .parser import parse_python_file

SCHEMA_VERSION = "1.0.0"
GRAPH_FILENAME = "knowledge_graph.json"

# Directories that never contain first-party source worth indexing.
SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    "node_modules",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "build",
    "dist",
    ".eggs",
    "site-packages",
    ".tox",
    ".cursor",
    ".claude",
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def graph_path(project_root: str) -> str:
    return os.path.join(project_root, ".cursor", GRAPH_FILENAME)


def _is_test_file(rel: str) -> bool:
    base = os.path.basename(rel)
    return (
        base.startswith("test_")
        or base.endswith("_test.py")
        or "/tests/" in f"/{rel}"
        or rel.startswith("tests/")
    )


def discover_source_files(source_root: str, include_tests: bool = False) -> list[str]:
    """Return absolute paths of all indexable ``.py`` files under ``source_root``."""
    found: list[str] = []
    for dirpath, dirnames, filenames in os.walk(source_root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            if not fname.endswith(".py"):
                continue
            abs_path = os.path.join(dirpath, fname)
            rel = os.path.relpath(abs_path, source_root).replace(os.sep, "/")
            if not include_tests and _is_test_file(rel):
                continue
            found.append(abs_path)
    return sorted(found)


def _rebuild_imported_by(files: dict[str, Any]) -> None:
    for entry in files.values():
        entry["importedBy"] = []
    for importer, entry in files.items():
        for target in entry.get("imports", []):
            if target in files:
                files[target]["importedBy"].append(importer)
    for entry in files.values():
        entry["importedBy"] = sorted(set(entry["importedBy"]))


def _build_directories(files: dict[str, Any]) -> dict[str, Any]:
    dirs: dict[str, int] = {}
    for rel in files:
        d = os.path.dirname(rel)
        key = (d + "/") if d else "./"
        dirs[key] = dirs.get(key, 0) + 1
    return {
        k: {"description": _describe_dir(k), "fileCount": v}
        for k, v in sorted(dirs.items())
    }


def _describe_dir(key: str) -> str:
    name = key.rstrip("/").split("/")[-1] or "root"
    hints = {
        "models": "Data models",
        "schemas": "Pydantic / serialization schemas",
        "services": "Business logic services",
        "api": "API layer",
        "routes": "Route handlers",
        "routers": "Route handlers",
        "views": "View / endpoint handlers",
        "controllers": "Request controllers",
        "utils": "Utility helpers",
        "core": "Core configuration and primitives",
        "db": "Database access",
        "tests": "Tests",
        "migrations": "Database migrations",
    }
    return hints.get(name, f"{name} module")


def _detect_routes(files_abs: dict[str, str]) -> dict[str, str]:
    """Detect FastAPI/Flask route decorators across the source files.

    ``files_abs`` maps repo-relative path -> absolute path. Returns a mapping of
    ``"METHOD /path" -> "file:function"``.
    """
    routes: dict[str, str] = {}
    http_methods = {"get", "post", "put", "delete", "patch", "options", "head"}
    for rel, abs_path in files_abs.items():
        try:
            with open(abs_path, "r", encoding="utf-8") as fh:
                tree = ast.parse(fh.read())
        except (OSError, SyntaxError):
            continue
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for dec in node.decorator_list:
                if not isinstance(dec, ast.Call):
                    continue
                func = dec.func
                method = getattr(func, "attr", None)
                if method not in http_methods:
                    continue
                path = ""
                if dec.args and isinstance(dec.args[0], ast.Constant):
                    path = str(dec.args[0].value)
                if path:
                    routes[f"{method.upper()} {path}"] = f"{rel}:{node.name}"
    return routes


def build_graph(
    project_root: str, source_dir: str, include_tests: bool = False
) -> dict[str, Any]:
    """Full scan: parse every source file and assemble a complete graph."""
    source_root = os.path.join(project_root, source_dir) if source_dir else project_root
    abs_files = discover_source_files(source_root, include_tests)

    files: dict[str, Any] = {}
    symbols: dict[str, Any] = {}
    files_abs: dict[str, str] = {}
    errors: list[str] = []

    for abs_path in abs_files:
        result = parse_python_file(abs_path, source_root)
        rel = result["file"]
        files_abs[rel] = abs_path
        if result.get("error") and "file_entry" not in result:
            errors.append(f"{rel}: {result['error']}")
            continue
        files[rel] = result["file_entry"]
        for name, sym in result.get("symbols", {}).items():
            symbols[name] = sym

    _rebuild_imported_by(files)
    routes = _detect_routes(files_abs)

    graph: dict[str, Any] = {
        "meta": {
            "version": SCHEMA_VERSION,
            "generatedAt": _now(),
            "generator": "cursor-project-manager/kg",
            "projectRoot": os.path.abspath(project_root),
            "language": "python",
            "sourceDir": (source_dir.rstrip("/") + "/") if source_dir else "./",
            "totalFiles": len(files),
            "totalSymbols": len(symbols),
        },
        "directories": _build_directories(files),
        "files": files,
        "symbols": symbols,
    }
    if routes:
        graph["routes"] = routes
    if errors:
        graph["meta"]["parseErrors"] = errors
    return graph


def write_graph(project_root: str, graph: dict[str, Any]) -> str:
    path = graph_path(project_root)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(graph, fh, indent=2)
        fh.write("\n")
    return path


def load_graph(project_root: str) -> dict[str, Any] | None:
    path = graph_path(project_root)
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return None


def update_graph(
    project_root: str, changed_rel_paths: list[str]
) -> dict[str, Any]:
    """Incrementally update the graph for a set of changed files.

    ``changed_rel_paths`` are paths relative to the project root. Files that no
    longer exist are removed from the graph. Returns the updated graph along with
    a ``_changes`` summary block (stripped before writing).
    """
    graph = load_graph(project_root)
    if graph is None:
        raise FileNotFoundError("No knowledge graph found. Generate one first.")

    source_dir = graph["meta"].get("sourceDir", "./").rstrip("/")
    source_root = os.path.join(project_root, source_dir) if source_dir else project_root

    files = graph["files"]
    symbols = graph["symbols"]
    imports_changed = False
    summary = {"added": [], "removed": [], "modified": []}

    for changed in changed_rel_paths:
        abs_path = os.path.join(project_root, changed)
        # Normalize to source-root-relative key.
        rel = os.path.relpath(abs_path, source_root).replace(os.sep, "/")
        old_entry = files.get(rel)
        old_symbols = set(old_entry.get("symbols", [])) if old_entry else set()

        if not os.path.isfile(abs_path):
            if old_entry is not None:
                for name in old_symbols:
                    symbols.pop(name, None)
                files.pop(rel, None)
                imports_changed = True
                summary["removed"].append(rel)
            continue

        result = parse_python_file(abs_path, source_root)
        if "file_entry" not in result:
            continue
        new_entry = result["file_entry"]
        new_symbols = set(new_entry.get("symbols", []))

        # Drop symbols that disappeared from this file.
        for name in old_symbols - new_symbols:
            symbols.pop(name, None)
        for name, sym in result.get("symbols", {}).items():
            symbols[name] = sym

        if not old_entry or old_entry.get("imports") != new_entry.get("imports"):
            imports_changed = True
        files[rel] = new_entry
        summary["added" if old_entry is None else "modified"].append(rel)

    if imports_changed:
        _rebuild_imported_by(files)

    graph["directories"] = _build_directories(files)
    graph["meta"]["generatedAt"] = _now()
    graph["meta"]["totalFiles"] = len(files)
    graph["meta"]["totalSymbols"] = len(symbols)
    graph["_changes"] = summary
    return graph


def query_symbol(project_root: str, name: str) -> dict[str, Any]:
    """Look up a symbol (case-insensitive, substring-tolerant)."""
    graph = load_graph(project_root)
    if graph is None:
        return {"error": "No knowledge graph found."}
    symbols = graph.get("symbols", {})
    if name in symbols:
        return {"match": name, "symbol": symbols[name]}
    lowered = name.lower()
    partial = {k: v for k, v in symbols.items() if lowered in k.lower()}
    if not partial:
        return {"error": f"No symbol matching '{name}'."}
    if len(partial) == 1:
        k, v = next(iter(partial.items()))
        return {"match": k, "symbol": v}
    return {"candidates": sorted(partial.keys())}


def query_file(project_root: str, path: str) -> dict[str, Any]:
    graph = load_graph(project_root)
    if graph is None:
        return {"error": "No knowledge graph found."}
    files = graph.get("files", {})
    norm = path.replace(os.sep, "/")
    if norm in files:
        return {"match": norm, "file": files[norm]}
    matches = {k: v for k, v in files.items() if norm in k}
    if not matches:
        return {"error": f"No file matching '{path}'."}
    if len(matches) == 1:
        k, v = next(iter(matches.items()))
        return {"match": k, "file": v}
    return {"candidates": sorted(matches.keys())}
