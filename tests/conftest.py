import pytest

from feature_flags.models import FeatureFlag


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
    )
