"""Prompt templates used for explanation requests."""

from __future__ import annotations

from explain_code.models import CodeTarget, ComplexityReport

SYSTEM_PROMPT = """\
You are a senior software engineer.
Explain source code clearly for developers in plain English.
Return ONLY valid JSON with this exact shape:
{
  "overview": "short paragraph",
  "key_points": ["step 1", "step 2", "step 3"],
  "complexity_estimate": "complexity and maintainability explanation",
  "suggestions": ["suggestion 1", "suggestion 2"]
}

Rules:
- Keep explanations precise and concrete.
- Use implementation details from the provided code.
- Avoid generic advice with no link to the code.
- Keep key_points and suggestions concise.
"""


def build_user_prompt(target: CodeTarget, complexity: ComplexityReport) -> str:
    location = str(target.file_path)
    if target.start_line is not None and target.end_line is not None:
        location = f"{location}:{target.start_line}-{target.end_line}"

    return f"""\
Target type: {target.target_type}
Target identifier: {target.identifier}
Location: {location}

Static complexity heuristic:
- Score: {complexity.score}
- Level: {complexity.level}
- Rationale: {complexity.rationale}

Explain the following Python code:
```python
{target.source}
```
"""

