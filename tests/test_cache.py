from pathlib import Path

from explain_code.cache import DiskCache
from explain_code.models import CodeTarget


def test_cache_round_trip(tmp_path: Path) -> None:
    cache = DiskCache(cache_dir=tmp_path / "cache")
    target = CodeTarget(
        target_type="function",
        identifier="foo (x.py:1)",
        source="def foo():\n    return 1\n",
        file_path=tmp_path / "x.py",
        start_line=1,
        end_line=2,
    )
    key = cache.build_key(target=target, model="test-model", prompt_version="v1")
    payload = {"overview": "hello", "key_points": ["a"], "suggestions": ["b"]}
    cache.set(key, payload)
    assert cache.get(key) == payload


def test_cache_key_changes_with_source(tmp_path: Path) -> None:
    cache = DiskCache(cache_dir=tmp_path / "cache")
    base = CodeTarget(
        target_type="file",
        identifier="a.py",
        source="print('a')\n",
        file_path=tmp_path / "a.py",
        start_line=1,
        end_line=1,
    )
    changed = CodeTarget(
        target_type="file",
        identifier="a.py",
        source="print('b')\n",
        file_path=tmp_path / "a.py",
        start_line=1,
        end_line=1,
    )
    key1 = cache.build_key(target=base, model="test-model", prompt_version="v1")
    key2 = cache.build_key(target=changed, model="test-model", prompt_version="v1")
    assert key1 != key2

