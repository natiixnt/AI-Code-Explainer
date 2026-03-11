"""Data models used across the explain-code package."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal


def _to_string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


@dataclass(frozen=True)
class CodeTarget:
    """A file or function selected for explanation."""

    target_type: Literal["file", "function"]
    identifier: str
    source: str
    file_path: Path
    start_line: int | None = None
    end_line: int | None = None

    def cache_identity(self) -> str:
        location = f"{self.file_path}:{self.start_line or ''}:{self.end_line or ''}"
        return f"{self.target_type}|{self.identifier}|{location}"


@dataclass(frozen=True)
class ComplexityReport:
    """Result of static complexity estimation."""

    score: int
    level: str
    rationale: str

    def to_dict(self) -> dict[str, Any]:
        return {"score": self.score, "level": self.level, "rationale": self.rationale}

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ComplexityReport":
        return cls(
            score=int(payload.get("score", 0)),
            level=str(payload.get("level", "unknown")),
            rationale=str(payload.get("rationale", "")),
        )


@dataclass
class ExplanationResult:
    """Structured explanation returned by the model."""

    overview: str
    key_points: list[str] = field(default_factory=list)
    complexity_estimate: str = ""
    suggestions: list[str] = field(default_factory=list)
    static_complexity: ComplexityReport | None = None
    from_cache: bool = False

    @classmethod
    def from_model_payload(
        cls, payload: dict[str, Any], static_complexity: ComplexityReport
    ) -> "ExplanationResult":
        return cls(
            overview=str(payload.get("overview", "")).strip()
            or "No overview returned.",
            key_points=_to_string_list(payload.get("key_points", [])),
            complexity_estimate=str(payload.get("complexity_estimate", "")).strip()
            or "No complexity estimate returned.",
            suggestions=_to_string_list(payload.get("suggestions", [])),
            static_complexity=static_complexity,
        )

    def to_cache_payload(self) -> dict[str, Any]:
        return {
            "overview": self.overview,
            "key_points": self.key_points,
            "complexity_estimate": self.complexity_estimate,
            "suggestions": self.suggestions,
            "static_complexity": (
                self.static_complexity.to_dict() if self.static_complexity else None
            ),
        }

    @classmethod
    def from_cache_payload(cls, payload: dict[str, Any]) -> "ExplanationResult":
        static_raw = payload.get("static_complexity")
        static_complexity = (
            ComplexityReport.from_dict(static_raw)
            if isinstance(static_raw, dict)
            else ComplexityReport(
                score=0, level="unknown", rationale="Static complexity unavailable."
            )
        )
        result = cls(
            overview=str(payload.get("overview", "")),
            key_points=_to_string_list(payload.get("key_points", [])),
            complexity_estimate=str(payload.get("complexity_estimate", "")),
            suggestions=_to_string_list(payload.get("suggestions", [])),
            static_complexity=static_complexity,
            from_cache=True,
        )
        return result

