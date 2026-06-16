from dataclasses import dataclass
from typing import Literal

EvaluationSource = Literal["segment", "default", "default_fallback", "rollout"]


@dataclass(frozen=True)
class FeatureFlag:
    name: str
    default_state: bool
    segment_key: str
    segments: dict[str, bool]
    rollout_percent: int = 0

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("name must not be empty")
        if not self.segment_key:
            raise ValueError("segment_key must not be empty")
        if not self.segments:
            raise ValueError("segments must not be empty")
        if len(self.segments) > 3:
            raise ValueError("segments supports at most 3 values")
        for key, value in self.segments.items():
            if not key:
                raise ValueError("segment keys must not be empty")
            if not isinstance(value, bool):
                raise ValueError("segment values must be booleans")
        if not isinstance(self.rollout_percent, int):
            raise ValueError("rollout_percent must be an integer")
        if not (0 <= self.rollout_percent <= 100):
            raise ValueError("rollout_percent must be between 0 and 100")


@dataclass(frozen=True)
class EvaluationResult:
    flag: str
    enabled: bool
    source: EvaluationSource
