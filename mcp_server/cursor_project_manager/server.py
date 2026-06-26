"""MCP server exposing project-management + knowledge-graph tools to Cursor.

Run via stdio: ``python -m cursor_project_manager`` (see ``__main__.py``).
Register it in ``.cursor/mcp.json`` so Cursor's agent can call these tools
regardless of which underlying model the user has.
"""

from __future__ import annotations

import os
from typing import Any

from mcp.server.fastmcp import FastMCP

from . import detect, kg, registry

mcp = FastMCP("cursor-project-manager")


def _abspath(project_path: str) -> str:
    return os.path.abspath(os.path.expanduser(project_path))


@mcp.tool()
def get_project_info(project_path: str = ".") -> dict[str, Any]:
    """Detect tech stack, source directory, and git context for a project.

    Args:
        project_path: Path to the project root (defaults to current directory).
    """
    root = _abspath(project_path)
    if not os.path.isdir(root):
        return {"error": f"Not a directory: {root}"}
    summary = detect.project_summary(root)
    graph = kg.load_graph(root)
    summary["knowledgeGraph"] = (
        {
            "exists": True,
            "generatedAt": graph["meta"].get("generatedAt"),
            "totalFiles": graph["meta"].get("totalFiles"),
            "totalSymbols": graph["meta"].get("totalSymbols"),
        }
        if graph
        else {"exists": False}
    )
    return summary


@mcp.tool()
def load_project(project_path: str = ".") -> dict[str, Any]:
    """Switch context to a project: record it, return metadata, and ensure a KG.

    Generates the knowledge graph automatically if the project has 10+ source
    files and no fresh graph exists. Use this when starting work on a project.

    Args:
        project_path: Path to the project root.
    """
    root = _abspath(project_path)
    if not os.path.isdir(root):
        return {"error": f"Not a directory: {root}"}

    summary = detect.project_summary(root)
    registry.record_access(root, summary)

    source_dir = summary["sourceDir"]
    existing = kg.load_graph(root)
    kg_status: dict[str, Any]
    if existing:
        kg_status = {
            "action": "cached",
            "totalFiles": existing["meta"]["totalFiles"],
            "totalSymbols": existing["meta"]["totalSymbols"],
        }
    else:
        source_root = os.path.join(root, source_dir) if source_dir else root
        n = len(kg.discover_source_files(source_root))
        if n >= 10:
            graph = kg.build_graph(root, source_dir)
            kg.write_graph(root, graph)
            kg_status = {
                "action": "generated",
                "totalFiles": graph["meta"]["totalFiles"],
                "totalSymbols": graph["meta"]["totalSymbols"],
            }
        else:
            kg_status = {"action": "skipped", "reason": f"only {n} source files"}

    summary["knowledgeGraph"] = kg_status
    return summary


@mcp.tool()
def generate_knowledge_graph(
    project_path: str = ".", source_dir: str = "", include_tests: bool = False
) -> dict[str, Any]:
    """Full scan: parse all Python source into .cursor/knowledge_graph.json.

    Args:
        project_path: Path to the project root.
        source_dir: Source directory relative to root. Auto-detected if empty.
        include_tests: Whether to index test files (default False).
    """
    root = _abspath(project_path)
    if not os.path.isdir(root):
        return {"error": f"Not a directory: {root}"}
    src = source_dir or detect.detect_source_dir(root)
    graph = kg.build_graph(root, src, include_tests=include_tests)
    path = kg.write_graph(root, graph)
    return {
        "written": path,
        "sourceDir": graph["meta"]["sourceDir"],
        "totalFiles": graph["meta"]["totalFiles"],
        "totalSymbols": graph["meta"]["totalSymbols"],
        "routes": len(graph.get("routes", {})),
        "parseErrors": graph["meta"].get("parseErrors", []),
    }


@mcp.tool()
def update_knowledge_graph(
    project_path: str = ".", files: list[str] | None = None
) -> dict[str, Any]:
    """Incrementally update the KG for changed files (fast; only re-parses diffs).

    Args:
        project_path: Path to the project root.
        files: Specific repo-relative file paths to update. If omitted, changed
            Python files are auto-detected via git.
    """
    root = _abspath(project_path)
    if kg.load_graph(root) is None:
        return {"error": "No knowledge graph. Run generate_knowledge_graph first."}

    changed = files if files else detect.changed_python_files(root)
    if not changed:
        return {"status": "up-to-date", "message": "No changed Python files."}

    graph = kg.update_graph(root, changed)
    summary = graph.pop("_changes", {})
    path = kg.write_graph(root, graph)
    return {
        "written": path,
        "added": summary.get("added", []),
        "removed": summary.get("removed", []),
        "modified": summary.get("modified", []),
        "totalFiles": graph["meta"]["totalFiles"],
        "totalSymbols": graph["meta"]["totalSymbols"],
    }


@mcp.tool()
def query_symbol(name: str, project_path: str = ".") -> dict[str, Any]:
    """Look up a class/function/enum: returns its file path and line range.

    Use this BEFORE reading source files so you can read only the exact lines.

    Args:
        name: Symbol name (exact or substring, case-insensitive).
        project_path: Path to the project root.
    """
    return kg.query_symbol(_abspath(project_path), name)


@mcp.tool()
def query_file(path: str, project_path: str = ".") -> dict[str, Any]:
    """Get a file's symbols, local imports, and reverse dependencies (importedBy).

    Use ``importedBy`` to find every file affected before changing this one.

    Args:
        path: File path (exact or substring) relative to the source dir.
        project_path: Path to the project root.
    """
    return kg.query_file(_abspath(project_path), path)


@mcp.tool()
def list_recent_projects() -> dict[str, Any]:
    """List recently loaded projects (most recent first) from the registry."""
    return {"projects": registry.recent_projects()}


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
