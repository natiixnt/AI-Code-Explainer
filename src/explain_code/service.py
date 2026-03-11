"""Orchestration layer for extraction, analysis, caching, and LLM calls."""

from __future__ import annotations

from pathlib import Path

from explain_code.cache import DiskCache
from explain_code.complexity import estimate_complexity
from explain_code.config import Settings
from explain_code.extractors import extract_file_target, extract_function_target
from explain_code.models import CodeTarget, ExplanationResult
from explain_code.openai_client import OpenAIExplainer


class ExplainCodeService:
    def __init__(
        self,
        settings: Settings,
        explainer: OpenAIExplainer,
        cache: DiskCache | None = None,
        use_cache: bool = True,
    ) -> None:
        self.settings = settings
        self.explainer = explainer
        self.cache = cache
        self.use_cache = use_cache and cache is not None

    def explain_file(self, path: Path) -> tuple[CodeTarget, ExplanationResult]:
        target = extract_file_target(path)
        result = self._explain_target(target)
        return target, result

    def explain_function(
        self, function_name: str, project_dir: Path, file_hint: Path | None = None
    ) -> tuple[CodeTarget, ExplanationResult]:
        target = extract_function_target(
            function_name=function_name, project_dir=project_dir, file_hint=file_hint
        )
        result = self._explain_target(target)
        return target, result

    def _explain_target(self, target: CodeTarget) -> ExplanationResult:
        static_complexity = estimate_complexity(target.source)
        cache_key: str | None = None

        if self.use_cache and self.cache:
            cache_key = self.cache.build_key(
                target=target,
                model=self.settings.model,
                prompt_version=self.settings.prompt_version,
            )
            cached_payload = self.cache.get(cache_key)
            if cached_payload:
                return ExplanationResult.from_cache_payload(cached_payload)

        result = self.explainer.explain(
            target=target, static_complexity=static_complexity
        )
        if self.use_cache and self.cache and cache_key is not None:
            self.cache.set(cache_key, result.to_cache_payload())
        return result

