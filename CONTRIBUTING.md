# Contributing

Thanks for contributing to `explain-code`.

## Local Setup

```bash
python -m pip install -e ".[dev]"
```

## Run Tests

```bash
pytest
```

## Code Style

- Keep modules focused and testable.
- Prefer explicit error handling over silent failures.
- Keep CLI output readable in both text and JSON modes.

## Pull Requests

- Include tests for behavior changes.
- Update docs if CLI flags or output format changes.
- Keep commits focused on one logical change.

