import pytest

from feature_flags.models import FeatureFlag


DARK_MODE_PAYLOAD = {
    "name": "dark_mode",
    "default_state": False,
    "segment_key": "region",
    "segments": {
        "us-east": False,
        "us-west": True,
    },
    "rollout_percent": 25,
}


@pytest.fixture
def dark_mode_flag() -> FeatureFlag:
    return FeatureFlag(
        name="dark_mode",
        default_state=False,
        segment_key="region",
        segments={
            "us-east": False,
            "us-west": True,
        },
        rollout_percent=25,
    )
