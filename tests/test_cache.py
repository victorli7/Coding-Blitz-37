from feature_flags.cache import FlagCache
from feature_flags.models import FeatureFlag


def test_cache_miss_returns_none() -> None:
    cache = FlagCache()

    assert cache.get("dark_mode") is None


def test_cache_set_and_get(dark_mode_flag: FeatureFlag) -> None:
    cache = FlagCache()

    cache.set(dark_mode_flag)

    assert cache.get("dark_mode") == dark_mode_flag


def test_cache_invalidate_removes_flag(dark_mode_flag: FeatureFlag) -> None:
    cache = FlagCache()
    cache.set(dark_mode_flag)

    cache.invalidate("dark_mode")

    assert cache.get("dark_mode") is None


def test_cache_invalidate_missing_flag_is_noop() -> None:
    cache = FlagCache()

    cache.invalidate("missing")


def test_cache_clear_removes_all_flags(dark_mode_flag: FeatureFlag) -> None:
    cache = FlagCache()
    cache.set(dark_mode_flag)

    cache.clear()

    assert cache.get("dark_mode") is None
