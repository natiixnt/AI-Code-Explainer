"""Formatting helpers for CLI output."""

from __future__ import annotations

from typing import Any

from explain_code.models import CodeTarget, ExplanationResult


def as_text(target: CodeTarget, result: ExplanationResult) -> str:
    lines: list[str] = []
    lines.append("== Explain Code ==")
    lines.append(f"Target: {target.target_type} | {target.identifier}")
    lines.append(f"File: {target.file_path}")
    if target.start_line is not None and target.end_line is not None:
        lines.append(f"Lines: {target.start_line}-{target.end_line}")
    lines.append(f"Cache: {'hit' if result.from_cache else 'miss'}")
    lines.append("")

    lines.append("Overview")
    lines.append(result.overview)
    lines.append("")

    lines.append("Key Points")
    if result.key_points:
        for point in result.key_points:
            lines.append(f"- {point}")
    else:
        lines.append("- No key points provided.")
    lines.append("")

    lines.append("Complexity Estimate")
    lines.append(result.complexity_estimate)
    if result.static_complexity:
        lines.append(
            f"Static score: {result.static_complexity.score} "
            f"({result.static_complexity.level})"
        )
        lines.append(f"Static details: {result.static_complexity.rationale}")
    lines.append("")

    lines.append("Suggestions")
    if result.suggestions:
        for suggestion in result.suggestions:
            lines.append(f"- {suggestion}")
    else:
        lines.append("- No suggestions provided.")

    return "\n".join(lines)


def as_json(target: CodeTarget, result: ExplanationResult) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "target": {
            "type": target.target_type,
            "identifier": target.identifier,
            "file_path": str(target.file_path),
            "start_line": target.start_line,
            "end_line": target.end_line,
        },
        "overview": result.overview,
        "key_points": result.key_points,
        "complexity_estimate": result.complexity_estimate,
        "suggestions": result.suggestions,
        "cache_hit": result.from_cache,
    }
    if result.static_complexity:
        payload["static_complexity"] = result.static_complexity.to_dict()
    return payload

