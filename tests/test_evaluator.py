from feature_flags.evaluator import evaluate
from feature_flags.models import FeatureFlag


def test_us_west_enables_dark_mode(dark_mode_flag: FeatureFlag) -> None:
    result = evaluate(
        dark_mode_flag,
        {"user_id": "u-1", "region": "us-west"},
    )

    assert result.flag == "dark_mode"
    # New semantics: requires both rollout bucket and eligible segment
    assert result.enabled is False
    assert result.source == "segment"


def test_us_east_disables_dark_mode(dark_mode_flag: FeatureFlag) -> None:
    result = evaluate(
        dark_mode_flag,
        {"user_id": "user-0", "region": "us-east"},
    )

    assert result.enabled is False
    assert result.source == "segment"


def test_rollout_enables_us_east_when_in_bucket(dark_mode_flag: FeatureFlag) -> None:
    result = evaluate(
        dark_mode_flag,
        {"user_id": "user-2", "region": "us-east"},
    )

    # New semantics: region explicitly not eligible, so rollout alone doesn't enable
    assert result.enabled is False
    assert result.source == "segment"


def test_rollout_is_deterministic(dark_mode_flag: FeatureFlag) -> None:
    context = {"user_id": "user-2", "region": "us-east"}
    first = evaluate(dark_mode_flag, context)
    second = evaluate(dark_mode_flag, context)

    assert first == second


def test_rollout_enables_unknown_region_when_in_bucket(dark_mode_flag: FeatureFlag) -> None:
    result = evaluate(
        dark_mode_flag,
        {"user_id": "user-2", "region": "eu-central"},
    )

    # New semantics: unknown region is not eligible -> falls back to default
    assert result.enabled is False
    assert result.source == "default"


def test_rollout_skipped_when_segment_enabled(dark_mode_flag: FeatureFlag) -> None:
    result = evaluate(
        dark_mode_flag,
        {"user_id": "user-2", "region": "us-west"},
    )

    # When both segment is eligible and user is in rollout, mark as segment_and_rollout
    assert result.enabled is True
    assert result.source == "segment_and_rollout"


def test_rollout_requires_user_id(dark_mode_flag: FeatureFlag) -> None:
    result = evaluate(dark_mode_flag, {"region": "us-east"})

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


def test_unknown_region_uses_default_state_when_true() -> None:
    flag = FeatureFlag(
        name="beta_feature",
        default_state=True,
        segment_key="region",
        segments={"us-west": True},
        rollout_percent=25,
    )

    result = evaluate(flag, {"region": "eu-central"})

    assert result.enabled is True
    assert result.source == "default"
