from explain_code.complexity import estimate_complexity


def test_complexity_low_for_simple_function() -> None:
    source = """
def add(a, b):
    return a + b
"""
    report = estimate_complexity(source)
    assert report.level in {"low", "moderate"}
    assert report.score >= 1


def test_complexity_high_for_branchy_code() -> None:
    source = """
def evaluate(items):
    result = 0
    for item in items:
        if item > 10 and item % 2 == 0:
            result += 1
        elif item > 10 and item % 3 == 0:
            result += 2
        elif item > 10:
            result += 3
        else:
            try:
                if item < 0:
                    raise ValueError("x")
            except ValueError:
                result -= 1
    return result
"""
    report = estimate_complexity(source)
    assert report.level in {"high", "very high", "moderate"}
    assert report.score >= 8

