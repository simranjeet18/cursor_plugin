"""Recent-projects registry stored at ``~/.cursor/project-registry.json``."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any

MAX_PROJECTS = 20


def _registry_path() -> str:
    return os.path.join(os.path.expanduser("~"), ".cursor", "project-registry.json")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_registry() -> dict[str, Any]:
    path = _registry_path()
    if not os.path.isfile(path):
        return {"version": "1.0", "maxProjects": MAX_PROJECTS, "projects": {}}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
            data.setdefault("projects", {})
            return data
    except (OSError, json.JSONDecodeError):
        return {"version": "1.0", "maxProjects": MAX_PROJECTS, "projects": {}}


def save_registry(data: dict[str, Any]) -> None:
    path = _registry_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # Trim to the most recently accessed MAX_PROJECTS entries.
    projects = data.get("projects", {})
    if len(projects) > MAX_PROJECTS:
        ordered = sorted(
            projects.items(),
            key=lambda kv: kv[1].get("lastAccessed", ""),
            reverse=True,
        )
        data["projects"] = dict(ordered[:MAX_PROJECTS])
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
        fh.write("\n")


def record_access(project_root: str, summary: dict[str, Any]) -> None:
    data = load_registry()
    key = os.path.abspath(project_root)
    existing = data["projects"].get(key, {})
    data["projects"][key] = {
        "name": summary.get("name"),
        "lastAccessed": _now(),
        "accessCount": existing.get("accessCount", 0) + 1,
        "techStack": summary.get("techStack", {}).get("frameworks", []),
        "language": summary.get("techStack", {}).get("language", "python"),
        "hasCursorConfig": summary.get("hasCursorConfig", False),
        "hasKnowledgeGraph": os.path.isfile(
            os.path.join(key, ".cursor", "knowledge_graph.json")
        ),
    }
    save_registry(data)


def recent_projects() -> list[dict[str, Any]]:
    data = load_registry()
    items = sorted(
        data.get("projects", {}).items(),
        key=lambda kv: kv[1].get("lastAccessed", ""),
        reverse=True,
    )
    return [{"path": path, **meta} for path, meta in items]
