"""Static complexity estimation."""

from __future__ import annotations

import ast

from explain_code.models import ComplexityReport


class CyclomaticComplexityVisitor(ast.NodeVisitor):
    """Approximate cyclomatic complexity for Python code."""

    def __init__(self) -> None:
        self.complexity = 1

    def _bump(self, amount: int = 1) -> None:
        self.complexity += amount

    def visit_If(self, node: ast.If) -> None:
        self._bump()
        self.generic_visit(node)

    def visit_IfExp(self, node: ast.IfExp) -> None:
        self._bump()
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        self._bump()
        self.generic_visit(node)

    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        self._bump()
        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> None:
        self._bump()
        self.generic_visit(node)

    def visit_Try(self, node: ast.Try) -> None:
        self._bump(max(1, len(node.handlers)))
        self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        self._bump(max(0, len(node.values) - 1))
        self.generic_visit(node)

    def visit_With(self, node: ast.With) -> None:
        self._bump()
        self.generic_visit(node)

    def visit_AsyncWith(self, node: ast.AsyncWith) -> None:
        self._bump()
        self.generic_visit(node)

    def visit_comprehension(self, node: ast.comprehension) -> None:
        # Comprehension loops and filters introduce branching.
        self._bump(1 + len(node.ifs))
        self.generic_visit(node)

    def visit_Match(self, node: ast.Match) -> None:
        # Each extra match case adds a distinct branch path.
        self._bump(max(1, len(node.cases) - 1))
        self.generic_visit(node)


def _complexity_level(score: int) -> str:
    if score <= 5:
        return "low"
    if score <= 12:
        return "moderate"
    if score <= 20:
        return "high"
    return "very high"


def estimate_complexity(source: str) -> ComplexityReport:
    """Estimate complexity from Python source code."""
    non_empty_lines = len([line for line in source.splitlines() if line.strip()])
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return ComplexityReport(
            score=0,
            level="unknown",
            rationale="Static parser could not parse this source.",
        )

    visitor = CyclomaticComplexityVisitor()
    visitor.visit(tree)

    # Very large code blocks are harder to understand even with low branching.
    size_penalty = non_empty_lines // 50
    score = visitor.complexity + size_penalty
    level = _complexity_level(score)
    rationale = (
        f"Cyclomatic score {visitor.complexity} with {non_empty_lines} non-empty lines "
        f"(size penalty {size_penalty})."
    )
    return ComplexityReport(score=score, level=level, rationale=rationale)

