import pytest

from feature_flags.models import FeatureFlag


def test_valid_dark_mode_flag() -> None:
    flag = FeatureFlag(
        name="dark_mode",
        default_state=False,
        segment_key="region",
        segments={"us-east": False, "us-west": True},
    )

    assert flag.name == "dark_mode"


@pytest.mark.parametrize(
    "kwargs, match",
    [
        (
            {
                "name": "",
                "default_state": False,
                "segment_key": "region",
                "segments": {"us-west": True},
            },
            "name must not be empty",
        ),
        (
            {
                "name": "dark_mode",
                "default_state": False,
                "segment_key": "",
                "segments": {"us-west": True},
            },
            "segment_key must not be empty",
        ),
        (
            {
                "name": "dark_mode",
                "default_state": False,
                "segment_key": "region",
                "segments": {},
            },
            "segments must not be empty",
        ),
    ],
)
def test_invalid_flag_rejected(kwargs: dict, match: str) -> None:
    with pytest.raises(ValueError, match=match):
        FeatureFlag(**kwargs)
