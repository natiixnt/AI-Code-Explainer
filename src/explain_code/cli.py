"""Typer CLI entrypoint."""

from __future__ import annotations

import json
from enum import Enum
from pathlib import Path

import typer

from explain_code import __version__
from explain_code.cache import DiskCache
from explain_code.config import load_settings
from explain_code.errors import ExplainCodeError
from explain_code.formatter import as_json, as_text
from explain_code.openai_client import OpenAIExplainer
from explain_code.service import ExplainCodeService

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Explain complex Python code in plain English.",
)


class OutputFormat(str, Enum):
    text = "text"
    json = "json"


def _build_service(
    model: str | None,
    temperature: float | None,
    cache_dir: Path | None,
    no_cache: bool,
) -> ExplainCodeService:
    settings = load_settings(model=model, temperature=temperature, cache_dir=cache_dir)
    explainer = OpenAIExplainer(settings=settings)
    cache = None if no_cache else DiskCache(settings.cache_dir)
    return ExplainCodeService(
        settings=settings, explainer=explainer, cache=cache, use_cache=not no_cache
    )


def _render(
    output: OutputFormat,
    target,
    result,
) -> None:
    if output == OutputFormat.json:
        typer.echo(json.dumps(as_json(target, result), indent=2))
    else:
        typer.echo(as_text(target, result))


@app.command("file")
def explain_file(
    path: Path = typer.Argument(
        ...,
        exists=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        help="Path to a Python file.",
    ),
    model: str | None = typer.Option(
        None, "--model", "-m", help="OpenAI model. Default: EXPLAIN_CODE_MODEL."
    ),
    temperature: float | None = typer.Option(
        None, "--temperature", min=0.0, max=2.0, help="Sampling temperature."
    ),
    cache_dir: Path | None = typer.Option(
        None, "--cache-dir", help="Override cache directory."
    ),
    no_cache: bool = typer.Option(False, "--no-cache", help="Disable cache usage."),
    output: OutputFormat = typer.Option(
        OutputFormat.text, "--output", "-o", help="Output format."
    ),
) -> None:
    """Explain an entire Python file."""
    try:
        service = _build_service(
            model=model, temperature=temperature, cache_dir=cache_dir, no_cache=no_cache
        )
        target, result = service.explain_file(path)
        _render(output=output, target=target, result=result)
    except ExplainCodeError as exc:
        typer.secho(f"Error: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc


@app.command("function")
def explain_function(
    function_name: str = typer.Argument(..., help="Function name to explain."),
    project_dir: Path = typer.Option(
        Path("."),
        "--project-dir",
        "-p",
        exists=True,
        file_okay=False,
        readable=True,
        resolve_path=True,
        help="Project directory to search.",
    ),
    file: Path | None = typer.Option(
        None,
        "--file",
        "-f",
        exists=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        help="Optional file path to avoid searching the whole project.",
    ),
    model: str | None = typer.Option(
        None, "--model", "-m", help="OpenAI model. Default: EXPLAIN_CODE_MODEL."
    ),
    temperature: float | None = typer.Option(
        None, "--temperature", min=0.0, max=2.0, help="Sampling temperature."
    ),
    cache_dir: Path | None = typer.Option(
        None, "--cache-dir", help="Override cache directory."
    ),
    no_cache: bool = typer.Option(False, "--no-cache", help="Disable cache usage."),
    output: OutputFormat = typer.Option(
        OutputFormat.text, "--output", "-o", help="Output format."
    ),
) -> None:
    """Explain a function by name."""
    try:
        service = _build_service(
            model=model, temperature=temperature, cache_dir=cache_dir, no_cache=no_cache
        )
        target, result = service.explain_function(
            function_name=function_name, project_dir=project_dir, file_hint=file
        )
        _render(output=output, target=target, result=result)
    except ExplainCodeError as exc:
        typer.secho(f"Error: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc


@app.command("version")
def version() -> None:
    """Print installed version."""
    typer.echo(__version__)
