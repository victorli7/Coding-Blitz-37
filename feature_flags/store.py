import json
import sqlite3
from pathlib import Path

from feature_flags.errors import FlagStoreError
from feature_flags.models import FeatureFlag


class FlagStore:
    def __init__(self, db_path: str | Path = "flags.db") -> None:
        self.db_path = str(db_path)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        try:
            with self._connect() as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS flags (
                        name TEXT PRIMARY KEY,
                        default_state INTEGER NOT NULL,
                        segment_key TEXT NOT NULL,
                        segments TEXT NOT NULL
                    )
                    """
                )
        except sqlite3.Error as exc:
            raise FlagStoreError("failed to initialize database") from exc

    def _row_to_flag(self, row: sqlite3.Row) -> FeatureFlag:
        return FeatureFlag(
            name=row["name"],
            default_state=bool(row["default_state"]),
            segment_key=row["segment_key"],
            segments=json.loads(row["segments"]),
        )

    def list_all(self) -> list[FeatureFlag]:
        try:
            with self._connect() as conn:
                rows = conn.execute(
                    "SELECT name, default_state, segment_key, segments FROM flags ORDER BY name"
                ).fetchall()
        except sqlite3.Error as exc:
            raise FlagStoreError("failed to list flags") from exc
        return [self._row_to_flag(row) for row in rows]

    def get(self, name: str) -> FeatureFlag | None:
        try:
            with self._connect() as conn:
                row = conn.execute(
                    "SELECT name, default_state, segment_key, segments FROM flags WHERE name = ?",
                    (name,),
                ).fetchone()
        except sqlite3.Error as exc:
            raise FlagStoreError(f"failed to load flag '{name}'") from exc
        if row is None:
            return None
        return self._row_to_flag(row)

    def create(self, flag: FeatureFlag) -> FeatureFlag:
        try:
            with self._connect() as conn:
                conn.execute(
                    """
                    INSERT INTO flags (name, default_state, segment_key, segments)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        flag.name,
                        int(flag.default_state),
                        flag.segment_key,
                        json.dumps(flag.segments),
                    ),
                )
        except sqlite3.IntegrityError as exc:
            raise FlagStoreError(f"flag '{flag.name}' already exists") from exc
        except sqlite3.Error as exc:
            raise FlagStoreError(f"failed to create flag '{flag.name}'") from exc
        return flag

    def update(self, flag: FeatureFlag) -> FeatureFlag | None:
        try:
            with self._connect() as conn:
                cursor = conn.execute(
                    """
                    UPDATE flags
                    SET default_state = ?, segment_key = ?, segments = ?
                    WHERE name = ?
                    """,
                    (
                        int(flag.default_state),
                        flag.segment_key,
                        json.dumps(flag.segments),
                        flag.name,
                    ),
                )
        except sqlite3.Error as exc:
            raise FlagStoreError(f"failed to update flag '{flag.name}'") from exc
        if cursor.rowcount == 0:
            return None
        return flag

    def delete(self, name: str) -> bool:
        try:
            with self._connect() as conn:
                cursor = conn.execute("DELETE FROM flags WHERE name = ?", (name,))
        except sqlite3.Error as exc:
            raise FlagStoreError(f"failed to delete flag '{name}'") from exc
        return cursor.rowcount > 0
