import hashlib

from feature_flags.models import EvaluationResult, FeatureFlag

ROLLOUT_PERCENT = 25
ROLLOUT_KEY = "user_id"


def _rollout_bucket(user_id: str) -> int:
    digest = hashlib.sha256(user_id.encode()).hexdigest()
    return int(digest[:8], 16) % 100


def _in_rollout(context: dict, percent: int | None = None) -> bool:
    user_id = context.get(ROLLOUT_KEY)
    if user_id is None:
        return False
    pct = ROLLOUT_PERCENT if percent is None else percent
    return _rollout_bucket(str(user_id)) < int(pct)


def evaluate(
    flag: FeatureFlag,
    context: dict,
    *,
    db_fallback: bool = False,
) -> EvaluationResult:
    segment_value = context.get(flag.segment_key)
    if segment_value in flag.segments:
        if flag.segments[segment_value]:
            return EvaluationResult(
                flag=flag.name,
                enabled=True,
                source="segment",
            )
        if _in_rollout(context, getattr(flag, "rollout_percent", None)):
            return EvaluationResult(
                flag=flag.name,
                enabled=True,
                source="rollout",
            )
        return EvaluationResult(
            flag=flag.name,
            enabled=False,
            source="segment",
        )

    if flag.default_state:
        source = "default_fallback" if db_fallback else "default"
        return EvaluationResult(
            flag=flag.name,
            enabled=True,
            source=source,
        )

    if _in_rollout(context, getattr(flag, "rollout_percent", None)):
        return EvaluationResult(
            flag=flag.name,
            enabled=True,
            source="rollout",
        )

    source = "default_fallback" if db_fallback else "default"
    return EvaluationResult(
        flag=flag.name,
        enabled=False,
        source=source,
    )
