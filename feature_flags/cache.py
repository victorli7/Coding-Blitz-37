from feature_flags.models import FeatureFlag


class FlagCache:
    def __init__(self) -> None:
        self._store: dict[str, FeatureFlag] = {}

    def get(self, name: str) -> FeatureFlag | None:
        return self._store.get(name)

    def set(self, flag: FeatureFlag) -> None:
        self._store[flag.name] = flag

    def invalidate(self, name: str) -> None:
        self._store.pop(name, None)

    def clear(self) -> None:
        self._store.clear()
