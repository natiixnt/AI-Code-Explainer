"""Code extraction utilities."""

from __future__ import annotations

import ast
from pathlib import Path

from explain_code.errors import (
    ExtractionError,
    FunctionNotFoundError,
    MultipleFunctionsFoundError,
)
from explain_code.models import CodeTarget

IGNORED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "build",
    "dist",
}


def extract_file_target(path: Path) -> CodeTarget:
    """Return a target for a full Python file."""
    resolved = path.expanduser().resolve()
    if not resolved.exists() or not resolved.is_file():
        raise ExtractionError(f"File does not exist: {path}")
    if resolved.suffix != ".py":
        raise ExtractionError(f"Only Python files are supported: {path}")

    source = resolved.read_text(encoding="utf-8")
    line_count = max(1, len(source.splitlines()))
    return CodeTarget(
        target_type="file",
        identifier=resolved.name,
        source=source,
        file_path=resolved,
        start_line=1,
        end_line=line_count,
    )


def _iter_python_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*.py"):
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        if path.is_file():
            files.append(path.resolve())
    return files


def _function_matches(file_path: Path, function_name: str) -> list[CodeTarget]:
    try:
        source = file_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []

    try:
        tree = ast.parse(source, filename=str(file_path))
    except SyntaxError:
        return []

    lines = source.splitlines()
    matches: list[CodeTarget] = []

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name != function_name:
            continue

        start = getattr(node, "lineno", None)
        end = getattr(node, "end_lineno", None)
        if start is None or end is None:
            continue

        snippet = "\n".join(lines[start - 1 : end])
        identifier = f"{function_name} ({file_path.name}:{start})"
        matches.append(
            CodeTarget(
                target_type="function",
                identifier=identifier,
                source=snippet,
                file_path=file_path,
                start_line=start,
                end_line=end,
            )
        )

    return matches


def extract_function_target(
    function_name: str, project_dir: Path, file_hint: Path | None = None
) -> CodeTarget:
    """Find and return a specific function across a project."""
    if not function_name.strip():
        raise ExtractionError("Function name cannot be empty.")

    if file_hint is not None:
        candidate_files = [file_hint.expanduser().resolve()]
        if not candidate_files[0].exists():
            raise ExtractionError(f"File does not exist: {file_hint}")
    else:
        root = project_dir.expanduser().resolve()
        if not root.exists() or not root.is_dir():
            raise ExtractionError(f"Project directory does not exist: {project_dir}")
        candidate_files = _iter_python_files(root)

    matches: list[CodeTarget] = []
    for file_path in candidate_files:
        matches.extend(_function_matches(file_path=file_path, function_name=function_name))

    if not matches:
        raise FunctionNotFoundError(
            f"Function '{function_name}' was not found in {project_dir.resolve()}."
        )
    if len(matches) > 1:
        candidates = [
            f"{target.file_path}:{target.start_line}" for target in matches[:10]
        ]
        raise MultipleFunctionsFoundError(function_name=function_name, candidates=candidates)
    return matches[0]

