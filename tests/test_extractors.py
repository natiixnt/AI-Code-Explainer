from pathlib import Path

import pytest

from explain_code.errors import FunctionNotFoundError, MultipleFunctionsFoundError
from explain_code.extractors import extract_file_target, extract_function_target


def test_extract_file_target(tmp_path: Path) -> None:
    file_path = tmp_path / "sample.py"
    file_path.write_text("def hello():\n    return 'hi'\n", encoding="utf-8")
    target = extract_file_target(file_path)

    assert target.target_type == "file"
    assert target.file_path == file_path.resolve()
    assert "def hello" in target.source
    assert target.start_line == 1


def test_extract_function_target(tmp_path: Path) -> None:
    file_path = tmp_path / "sample.py"
    file_path.write_text(
        "def unrelated():\n    return 1\n\n"
        "def my_function(x):\n    return x * 2\n",
        encoding="utf-8",
    )
    target = extract_function_target("my_function", project_dir=tmp_path)

    assert target.target_type == "function"
    assert target.start_line == 4
    assert "return x * 2" in target.source


def test_extract_function_not_found(tmp_path: Path) -> None:
    file_path = tmp_path / "sample.py"
    file_path.write_text("def foo():\n    return 1\n", encoding="utf-8")
    with pytest.raises(FunctionNotFoundError):
        extract_function_target("bar", project_dir=tmp_path)


def test_extract_function_ambiguous(tmp_path: Path) -> None:
    file_a = tmp_path / "a.py"
    file_b = tmp_path / "b.py"
    file_a.write_text("def dup():\n    return 1\n", encoding="utf-8")
    file_b.write_text("def dup():\n    return 2\n", encoding="utf-8")

    with pytest.raises(MultipleFunctionsFoundError):
        extract_function_target("dup", project_dir=tmp_path)

