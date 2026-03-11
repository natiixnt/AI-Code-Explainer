# Command Reference

## `explain-code file`

Explain a Python file.

```bash
explain-code file PATH [OPTIONS]
```

Options:

- `--model, -m TEXT` OpenAI model override
- `--temperature FLOAT` Sampling temperature (`0.0` to `2.0`)
- `--cache-dir PATH` Override cache directory
- `--no-cache` Disable cache lookup and writes
- `--output, -o [text|json]` Output format

Examples:

```bash
explain-code file app.py
explain-code file app.py --output json
explain-code file app.py --no-cache --model gpt-4.1
```

## `explain-code function`

Explain a Python function by name.

```bash
explain-code function FUNCTION_NAME [OPTIONS]
```

Options:

- `--project-dir, -p PATH` Directory to search recursively (default: `.`)
- `--file, -f PATH` Optional single file to search
- `--model, -m TEXT` OpenAI model override
- `--temperature FLOAT` Sampling temperature (`0.0` to `2.0`)
- `--cache-dir PATH` Override cache directory
- `--no-cache` Disable cache lookup and writes
- `--output, -o [text|json]` Output format

Examples:

```bash
explain-code function my_function
explain-code function my_function --file src/core.py
explain-code function my_function -p src --output json
```

## `explain-code version`

Print the installed version.

```bash
explain-code version
```

