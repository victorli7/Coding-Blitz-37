from feature_flags.models import EvaluationResult, FeatureFlag


def flag_to_dict(flag: FeatureFlag) -> dict:
    return {
        "name": flag.name,
        "default_state": flag.default_state,
        "segment_key": flag.segment_key,
        "segments": flag.segments,
    }


def evaluation_to_dict(result: EvaluationResult) -> dict:
    return {
        "flag": result.flag,
        "enabled": result.enabled,
        "source": result.source,
    }


def flag_from_dict(data: dict) -> FeatureFlag:
    if not isinstance(data, dict):
        raise ValueError("request body must be a JSON object")

    required_fields = ("name", "default_state", "segment_key", "segments")
    missing = [field for field in required_fields if field not in data]
    if missing:
        raise ValueError(f"missing required fields: {', '.join(missing)}")

    if not isinstance(data["default_state"], bool):
        raise ValueError("default_state must be a boolean")

    segments = data["segments"]
    if not isinstance(segments, dict):
        raise ValueError("segments must be an object")

    return FeatureFlag(
        name=str(data["name"]),
        default_state=data["default_state"],
        segment_key=str(data["segment_key"]),
        segments={str(key): bool(value) for key, value in segments.items()},
    )
