# explain-code

`explain-code` is an open source Python CLI that explains complex source code in plain English using the OpenAI API.

## Features

- Explain an entire file: `explain-code file path/to/file.py`
- Explain a function by name: `explain-code function my_function`
- Structured output with:
  - explanation overview
  - key points
  - complexity estimate
  - concrete improvement suggestions
- Local disk cache to avoid repeated API calls for unchanged code
- Modular architecture for easy extension

## Installation

### 1. Clone

```bash
git clone <your-repo-url>
cd <repo-directory>
```

### 2. Install

```bash
python -m pip install -e .
```

### 3. Configure OpenAI key

```bash
export OPENAI_API_KEY="your_api_key_here"
```

Optional environment settings:

- `EXPLAIN_CODE_MODEL` (default: `gpt-4.1-mini`)
- `EXPLAIN_CODE_TEMPERATURE` (default: `0.2`)
- `EXPLAIN_CODE_CACHE_DIR` (default: OS user cache dir)

## Usage

### Explain a file

```bash
explain-code file app.py
```

### Explain a function by name

```bash
explain-code function my_function
```

By default this searches recursively from the current directory.

### Limit search to one file

```bash
explain-code function my_function --file app.py
```

### JSON output

```bash
explain-code file app.py --output json
```

### Disable cache

```bash
explain-code file app.py --no-cache
```

## CLI Reference

See [docs/COMMANDS.md](docs/COMMANDS.md) for all options.

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for module-level design.

## Caching

- Cache key includes:
  - target identity and source code
  - selected model
  - prompt version
- If any of those change, a new explanation is generated.
- Cache lives in `EXPLAIN_CODE_CACHE_DIR` or OS default cache path.

## Development

Install dev dependencies:

```bash
python -m pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

## Project Structure

```text
.
├── docs/
│   ├── ARCHITECTURE.md
│   └── COMMANDS.md
├── src/explain_code/
│   ├── cache.py
│   ├── cli.py
│   ├── complexity.py
│   ├── config.py
│   ├── extractors.py
│   ├── formatter.py
│   ├── models.py
│   ├── openai_client.py
│   ├── prompting.py
│   └── service.py
└── tests/
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT, see [LICENSE](LICENSE).
