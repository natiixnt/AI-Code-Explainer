# Architecture

## Design Goals

- Keep CLI surface small and predictable.
- Keep components modular and testable.
- Isolate OpenAI and cache concerns from extraction logic.

## Module Overview

- `cli.py`
  - Typer entrypoint and command definitions.
  - Converts CLI options into service configuration.
- `config.py`
  - Loads runtime settings from env vars and CLI overrides.
- `extractors.py`
  - Reads a full file or resolves a function across a project tree.
- `complexity.py`
  - Computes a static complexity heuristic from AST.
- `prompting.py`
  - Contains system prompt and request-building helpers.
- `openai_client.py`
  - Executes OpenAI API calls and parses JSON responses.
- `cache.py`
  - Disk-backed JSON cache keyed by target+model+prompt version.
- `service.py`
  - Orchestrates extraction, complexity analysis, cache lookup, and LLM call.
- `formatter.py`
  - Renders output as text or JSON.

## Request Flow

1. CLI command resolves target (`file` or `function`).
2. Service computes static complexity.
3. Service checks cache.
4. On cache miss, OpenAI client requests explanation JSON.
5. Service stores result in cache.
6. Formatter prints structured output.

## Error Model

- Domain-specific exceptions are defined in `errors.py`.
- CLI catches them and exits with code `1` plus a clear message.

## Extension Points

- Add new target types by extending `extractors.py`.
- Add output renderers in `formatter.py`.
- Add provider adapters next to `openai_client.py`.
- Version prompts through `PROMPT_VERSION` to invalidate stale cache.

