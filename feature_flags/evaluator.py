from feature_flags.models import EvaluationResult, FeatureFlag


def evaluate(
    flag: FeatureFlag,
    context: dict,
    *,
    db_fallback: bool = False,
) -> EvaluationResult:
    segment_value = context.get(flag.segment_key)
    if segment_value in flag.segments:
        return EvaluationResult(
            flag=flag.name,
            enabled=flag.segments[segment_value],
            source="segment",
        )

    source = "default_fallback" if db_fallback else "default"
    return EvaluationResult(
        flag=flag.name,
        enabled=flag.default_state,
        source=source,
    )
