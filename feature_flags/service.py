from feature_flags.cache import FlagCache
from feature_flags.errors import FlagConflictError, FlagNotFoundError, FlagStoreError
from feature_flags.evaluator import evaluate
from feature_flags.models import EvaluationResult, FeatureFlag
from feature_flags.store import FlagStore


class FlagService:
    def __init__(self, store: FlagStore, cache: FlagCache | None = None) -> None:
        self.store = store
        self.cache = cache or FlagCache()

    def list_flags(self) -> list[FeatureFlag]:
        return self.store.list_all()

    def create_flag(self, flag: FeatureFlag) -> FeatureFlag:
        if self.store.get(flag.name) is not None:
            raise FlagConflictError(f"flag '{flag.name}' already exists")
        created = self.store.create(flag)
        self.cache.set(created)
        return created

    def get_flag(self, name: str) -> FeatureFlag:
        flag, db_fallback = self._load_flag(name)
        if flag is None:
            if db_fallback:
                raise FlagStoreError(f"database unavailable while loading flag '{name}'")
            raise FlagNotFoundError(f"flag '{name}' not found")
        return flag

    def update_flag(self, name: str, flag: FeatureFlag) -> FeatureFlag:
        if name != flag.name:
            raise ValueError("path name must match flag name in request body")
        existing = self.store.get(name)
        if existing is None:
            raise FlagNotFoundError(f"flag '{name}' not found")
        updated = self.store.update(flag)
        if updated is None:
            raise FlagNotFoundError(f"flag '{name}' not found")
        self.cache.set(updated)
        return updated

    def delete_flag(self, name: str) -> None:
        if not self.store.delete(name):
            raise FlagNotFoundError(f"flag '{name}' not found")
        self.cache.invalidate(name)

    def evaluate_flag(self, name: str, context: dict) -> EvaluationResult:
        flag, db_fallback = self._load_flag(name)
        if flag is None:
            if db_fallback:
                return EvaluationResult(
                    flag=name,
                    enabled=False,
                    source="default_fallback",
                )
            raise FlagNotFoundError(f"flag '{name}' not found")
        return evaluate(flag, context, db_fallback=db_fallback)

    def _load_flag(self, name: str) -> tuple[FeatureFlag | None, bool]:
        cached = self.cache.get(name)
        if cached is not None:
            return cached, False

        try:
            flag = self.store.get(name)
        except FlagStoreError:
            return None, True

        if flag is not None:
            self.cache.set(flag)
        return flag, False
