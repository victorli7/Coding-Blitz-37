from feature_flags.evaluator import evaluate
from feature_flags.models import FeatureFlag


def test_us_west_enables_dark_mode(dark_mode_flag: FeatureFlag) -> None:
    result = evaluate(
        dark_mode_flag,
        {"user_id": "u-1", "region": "us-west"},
    )

    assert result.flag == "dark_mode"
    assert result.enabled is True
    assert result.source == "segment"


def test_us_east_disables_dark_mode(dark_mode_flag: FeatureFlag) -> None:
    result = evaluate(
        dark_mode_flag,
        {"user_id": "u-2", "region": "us-east"},
    )

    assert result.enabled is False
    assert result.source == "segment"


def test_unknown_region_uses_default(dark_mode_flag: FeatureFlag) -> None:
    result = evaluate(
        dark_mode_flag,
        {"user_id": "u-3", "region": "eu-central"},
    )

    assert result.enabled is False
    assert result.source == "default"


def test_missing_region_uses_default(dark_mode_flag: FeatureFlag) -> None:
    result = evaluate(dark_mode_flag, {"user_id": "u-4"})

    assert result.enabled is False
    assert result.source == "default"


def test_db_fallback_labels_default_source(dark_mode_flag: FeatureFlag) -> None:
    result = evaluate(
        dark_mode_flag,
        {"user_id": "u-5", "region": "eu-central"},
        db_fallback=True,
    )

    assert result.enabled is False
    assert result.source == "default_fallback"
