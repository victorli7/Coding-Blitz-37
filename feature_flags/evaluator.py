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


def evaluate(flag: FeatureFlag, context: dict) -> EvaluationResult:
    segment_value = context.get(flag.segment_key)
    in_rollout = _in_rollout(context, flag.rollout_percent)

    if segment_value in flag.segments:
        if flag.segments[segment_value] and in_rollout:
            return EvaluationResult(flag=flag.name, enabled=True, source="segment_and_rollout")
        return EvaluationResult(flag=flag.name, enabled=False, source="segment")

    return EvaluationResult(
        flag=flag.name,
        enabled=flag.default_state,
        source="default",
    )
