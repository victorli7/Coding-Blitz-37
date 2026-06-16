class FlagError(Exception):
    """Base error for flag service operations."""


class FlagNotFoundError(FlagError):
    pass


class FlagConflictError(FlagError):
    pass


class FlagStoreError(FlagError):
    pass
