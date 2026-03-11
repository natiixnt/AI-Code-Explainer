"""Disk caching for explanation results."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from explain_code.errors import ConfigurationError
from explain_code.models import CodeTarget


class DiskCache:
    """Simple JSON file cache keyed by target source and model metadata."""

    def __init__(self, cache_dir: Path) -> None:
        self.cache_dir = cache_dir.expanduser()
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise ConfigurationError(
                f"Cannot create cache directory at '{self.cache_dir}'. "
                "Use --cache-dir to select a writable path or --no-cache to disable caching."
            ) from exc

    def build_key(self, target: CodeTarget, model: str, prompt_version: str) -> str:
        digest = hashlib.sha256()
        digest.update(target.cache_identity().encode("utf-8"))
        digest.update(b"\0")
        digest.update(target.source.encode("utf-8"))
        digest.update(b"\0")
        digest.update(model.encode("utf-8"))
        digest.update(b"\0")
        digest.update(prompt_version.encode("utf-8"))
        return digest.hexdigest()

    def _path_for_key(self, key: str) -> Path:
        return self.cache_dir / f"{key}.json"

    def get(self, key: str) -> dict[str, Any] | None:
        path = self._path_for_key(key)
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None

    def set(self, key: str, payload: dict[str, Any]) -> None:
        path = self._path_for_key(key)
        temp_path = path.with_suffix(".tmp")
        temp_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        temp_path.replace(path)
