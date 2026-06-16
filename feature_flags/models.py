from dataclasses import dataclass
from typing import Literal

EvaluationSource = Literal["segment", "default", "default_fallback"]


@dataclass(frozen=True)
class FeatureFlag:
    name: str
    default_state: bool
    segment_key: str
    segments: dict[str, bool]

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


@dataclass(frozen=True)
class EvaluationResult:
    flag: str
    enabled: bool
    source: EvaluationSource
