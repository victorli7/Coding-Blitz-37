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
    # New semantics: a flag is enabled only when BOTH
    #  - the user falls into the rollout bucket (by user_id hash), and
    #  - the user's segment value is marked eligible (segment value exists and is True).
    # Otherwise the flag is considered disabled. We still surface default/db_fallback
    # when the segment key is missing from context or the flag cannot be loaded.
    segment_value = context.get(flag.segment_key)
    in_rollout = _in_rollout(context, getattr(flag, "rollout_percent", None))

    if segment_value in flag.segments:
        # If the segment explicitly marks eligibility, enable only when both conditions hold.
        if flag.segments[segment_value] and in_rollout:
            return EvaluationResult(flag=flag.name, enabled=True, source="segment_and_rollout")
        return EvaluationResult(flag=flag.name, enabled=False, source="segment")

    # Segment value not present in flag.segments -> treat as not eligible.
    # Return default fallback or default (disabled) depending on db availability.
    source = "default_fallback" if db_fallback else "default"
    return EvaluationResult(flag=flag.name, enabled=False, source=source)
