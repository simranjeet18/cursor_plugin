"""Project marker, tech-stack, and source-directory detection for Python repos."""

from __future__ import annotations

import os
import subprocess
import tomllib
from typing import Any

PROJECT_MARKERS = [
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "requirements.txt",
    "Pipfile",
    "environment.yml",
    ".git",
    "AGENTS.md",
    ".cursor",
]

FRAMEWORK_PACKAGES = {
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "streamlit": "Streamlit",
    "langchain": "LangChain",
    "llama-index": "LlamaIndex",
    "transformers": "HuggingFace Transformers",
    "torch": "PyTorch",
    "tensorflow": "TensorFlow",
    "scikit-learn": "scikit-learn",
    "pandas": "pandas",
    "celery": "Celery",
    "scrapy": "Scrapy",
    "pytest": "pytest",
}

PACKAGE_MANAGERS = [
    ("poetry.lock", "poetry"),
    ("Pipfile.lock", "pipenv"),
    ("pdm.lock", "pdm"),
    ("uv.lock", "uv"),
    ("requirements.txt", "pip"),
]


def is_project(path: str) -> bool:
    return any(os.path.exists(os.path.join(path, m)) for m in PROJECT_MARKERS)


def _read_text(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return ""


def _dependency_names(project_root: str) -> set[str]:
    deps: set[str] = set()
    pyproject = os.path.join(project_root, "pyproject.toml")
    if os.path.isfile(pyproject):
        try:
            with open(pyproject, "rb") as fh:
                data = tomllib.load(fh)
            project_deps = data.get("project", {}).get("dependencies", [])
            poetry_deps = (
                data.get("tool", {}).get("poetry", {}).get("dependencies", {})
            )
            for dep in project_deps:
                deps.add(_normalize_dep(dep))
            for dep in poetry_deps:
                deps.add(dep.lower())
        except (OSError, tomllib.TOMLDecodeError):
            pass
    req = os.path.join(project_root, "requirements.txt")
    if os.path.isfile(req):
        for line in _read_text(req).splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                deps.add(_normalize_dep(line))
    return deps


def _normalize_dep(spec: str) -> str:
    for sep in ("==", ">=", "<=", "~=", ">", "<", "[", " ", ";"):
        spec = spec.split(sep)[0]
    return spec.strip().lower()


def detect_source_dir(project_root: str) -> str:
    """Pick the most likely source directory (relative to project root)."""
    name = os.path.basename(os.path.abspath(project_root))
    candidates = ["src", name.replace("-", "_"), name]
    for cand in candidates:
        full = os.path.join(project_root, cand)
        if os.path.isdir(full) and _has_python(full):
            return cand
    # A single package dir with an __init__.py?
    for entry in sorted(os.listdir(project_root)):
        full = os.path.join(project_root, entry)
        if (
            os.path.isdir(full)
            and not entry.startswith(".")
            and os.path.isfile(os.path.join(full, "__init__.py"))
        ):
            return entry
    return ""  # fall back to project root


def _has_python(path: str) -> bool:
    for _, _, files in os.walk(path):
        if any(f.endswith(".py") for f in files):
            return True
    return False


def detect_tech_stack(project_root: str) -> dict[str, Any]:
    deps = _dependency_names(project_root)
    frameworks = sorted(
        {label for pkg, label in FRAMEWORK_PACKAGES.items() if pkg in deps}
    )
    pkg_manager = "pip"
    for fname, mgr in PACKAGE_MANAGERS:
        if os.path.isfile(os.path.join(project_root, fname)):
            pkg_manager = mgr
            break
    return {
        "language": "python",
        "frameworks": frameworks,
        "packageManager": pkg_manager,
        "dependencies": sorted(deps),
    }


def git_context(project_root: str) -> dict[str, Any]:
    def run(args: list[str]) -> str:
        try:
            out = subprocess.run(
                ["git", *args],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=10,
            )
            return out.stdout.strip()
        except (subprocess.SubprocessError, OSError):
            return ""

    if not os.path.isdir(os.path.join(project_root, ".git")):
        return {"isRepo": False}
    return {
        "isRepo": True,
        "branch": run(["branch", "--show-current"]),
        "lastCommit": run(["log", "--oneline", "-1"]),
        "dirty": bool(run(["status", "--porcelain"])),
    }


def changed_python_files(project_root: str, since_ref: str = "HEAD") -> list[str]:
    """Return repo-relative changed/untracked ``.py`` paths via git."""
    if not os.path.isdir(os.path.join(project_root, ".git")):
        return []

    def run(args: list[str]) -> list[str]:
        try:
            out = subprocess.run(
                ["git", *args],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=15,
            )
            return [ln for ln in out.stdout.splitlines() if ln.strip()]
        except (subprocess.SubprocessError, OSError):
            return []

    paths: set[str] = set()
    paths.update(run(["diff", "--name-only", since_ref]))
    paths.update(run(["diff", "--cached", "--name-only"]))
    paths.update(run(["ls-files", "--others", "--exclude-standard"]))
    return sorted(p for p in paths if p.endswith(".py"))


def project_summary(project_root: str) -> dict[str, Any]:
    """One-shot project metadata used by the load/info tools."""
    return {
        "name": os.path.basename(os.path.abspath(project_root)),
        "path": os.path.abspath(project_root),
        "isProject": is_project(project_root),
        "sourceDir": detect_source_dir(project_root),
        "techStack": detect_tech_stack(project_root),
        "git": git_context(project_root),
        "hasCursorConfig": os.path.isdir(os.path.join(project_root, ".cursor")),
    }
