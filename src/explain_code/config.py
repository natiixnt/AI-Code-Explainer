"""Configuration and environment loading."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

from platformdirs import user_cache_dir

DEFAULT_MODEL = "gpt-4.1-mini"
DEFAULT_TEMPERATURE = 0.2
PROMPT_VERSION = "v1"


@dataclass(frozen=True)
class Settings:
    api_key: str | None
    model: str
    temperature: float
    cache_dir: Path
    prompt_version: str = PROMPT_VERSION


def load_settings(
    model: str | None = None,
    temperature: float | None = None,
    cache_dir: Path | None = None,
) -> Settings:
    selected_model = model or os.getenv("EXPLAIN_CODE_MODEL", DEFAULT_MODEL)
    selected_temperature = (
        temperature
        if temperature is not None
        else float(os.getenv("EXPLAIN_CODE_TEMPERATURE", str(DEFAULT_TEMPERATURE)))
    )
    selected_cache_dir = (
        cache_dir
        or Path(
            os.getenv(
                "EXPLAIN_CODE_CACHE_DIR",
                user_cache_dir(appname="explain-code", appauthor="explain-code"),
            )
        )
    ).expanduser()

    return Settings(
        api_key=os.getenv("OPENAI_API_KEY"),
        model=selected_model,
        temperature=selected_temperature,
        cache_dir=selected_cache_dir,
    )

