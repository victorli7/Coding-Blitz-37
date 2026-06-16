import json
import sqlite3
from pathlib import Path
from typing import Protocol

import psycopg
from psycopg.types.json import Jsonb

from feature_flags.errors import FlagStoreError
from feature_flags.models import FeatureFlag


class FlagStore(Protocol):
    def list_all(self) -> list[FeatureFlag]: ...

    def get(self, name: str) -> FeatureFlag | None: ...

    def create(self, flag: FeatureFlag) -> FeatureFlag: ...

    def update(self, flag: FeatureFlag) -> FeatureFlag | None: ...

    def delete(self, name: str) -> bool: ...


def create_flag_store(
    *,
    database_url: str | None = None,
    db_path: str | Path | None = None,
) -> FlagStore:
    if database_url:
        return PostgresFlagStore(database_url)
    return SqliteFlagStore(db_path or "flags.db")


def _segments_from_row(value: object) -> dict[str, bool]:
    if isinstance(value, dict):
        return {str(key): bool(val) for key, val in value.items()}
    return {str(key): bool(val) for key, val in json.loads(value).items()}


class SqliteFlagStore:
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
                        segments TEXT NOT NULL,
                        rollout_percent INTEGER NOT NULL DEFAULT 0
                    )
                    """
                )
                # Ensure older DB files get the new column
                cur = conn.execute("PRAGMA table_info('flags')")
                cols = [row[1] for row in cur.fetchall()]
                if 'rollout_percent' not in cols:
                    conn.execute(
                        "ALTER TABLE flags ADD COLUMN rollout_percent INTEGER NOT NULL DEFAULT 0"
                    )
        except sqlite3.Error as exc:
            raise FlagStoreError("failed to initialize database") from exc

    def _row_to_flag(self, row: sqlite3.Row) -> FeatureFlag:
        return FeatureFlag(
            name=row["name"],
            default_state=bool(row["default_state"]),
            segment_key=row["segment_key"],
            segments=_segments_from_row(row["segments"]),
            rollout_percent=int(row["rollout_percent"] or 0),
        )

    def list_all(self) -> list[FeatureFlag]:
        try:
            with self._connect() as conn:
                rows = conn.execute(
                    "SELECT name, default_state, segment_key, segments, rollout_percent FROM flags ORDER BY name"
                ).fetchall()
        except sqlite3.Error as exc:
            raise FlagStoreError("failed to list flags") from exc
        return [self._row_to_flag(row) for row in rows]

    def get(self, name: str) -> FeatureFlag | None:
        try:
            with self._connect() as conn:
                row = conn.execute(
                    "SELECT name, default_state, segment_key, segments, rollout_percent FROM flags WHERE name = ?",
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
                    INSERT INTO flags (name, default_state, segment_key, segments, rollout_percent)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        flag.name,
                        int(flag.default_state),
                        flag.segment_key,
                        json.dumps(flag.segments),
                        int(flag.rollout_percent),
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
                    SET default_state = ?, segment_key = ?, segments = ?, rollout_percent = ?
                    WHERE name = ?
                    """,
                    (
                        int(flag.default_state),
                        flag.segment_key,
                        json.dumps(flag.segments),
                        int(flag.rollout_percent),
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


class PostgresFlagStore:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url
        self._init_db()

    def _connect(self):
        return psycopg.connect(self.database_url)

    def _init_db(self) -> None:
        try:
            with self._connect() as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS flags (
                        name TEXT PRIMARY KEY,
                        default_state BOOLEAN NOT NULL,
                        segment_key TEXT NOT NULL,
                        segments JSONB NOT NULL,
                        rollout_percent INTEGER NOT NULL DEFAULT 0
                    )
                    """
                )
                # ensure column exists for upgrades
                conn.execute(
                    "ALTER TABLE flags ADD COLUMN IF NOT EXISTS rollout_percent INTEGER NOT NULL DEFAULT 0"
                )
        except psycopg.Error as exc:
            raise FlagStoreError("failed to initialize database") from exc

    def _row_to_flag(self, row: tuple) -> FeatureFlag:
        return FeatureFlag(
            name=row[0],
            default_state=bool(row[1]),
            segment_key=row[2],
            segments=_segments_from_row(row[3]),
            rollout_percent=int(row[4] or 0),
        )

    def list_all(self) -> list[FeatureFlag]:
        try:
            with self._connect() as conn:
                rows = conn.execute(
                    "SELECT name, default_state, segment_key, segments, rollout_percent FROM flags ORDER BY name"
                ).fetchall()
        except psycopg.Error as exc:
            raise FlagStoreError("failed to list flags") from exc
        return [self._row_to_flag(row) for row in rows]

    def get(self, name: str) -> FeatureFlag | None:
        try:
            with self._connect() as conn:
                row = conn.execute(
                    "SELECT name, default_state, segment_key, segments, rollout_percent FROM flags WHERE name = %s",
                    (name,),
                ).fetchone()
        except psycopg.Error as exc:
            raise FlagStoreError(f"failed to load flag '{name}'") from exc
        if row is None:
            return None
        return self._row_to_flag(row)

    def create(self, flag: FeatureFlag) -> FeatureFlag:
        try:
            with self._connect() as conn:
                conn.execute(
                    """
                    INSERT INTO flags (name, default_state, segment_key, segments, rollout_percent)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        flag.name,
                        flag.default_state,
                        flag.segment_key,
                        Jsonb(flag.segments),
                        int(flag.rollout_percent),
                    ),
                )
        except psycopg.errors.UniqueViolation as exc:
            raise FlagStoreError(f"flag '{flag.name}' already exists") from exc
        except psycopg.Error as exc:
            raise FlagStoreError(f"failed to create flag '{flag.name}'") from exc
        return flag

    def update(self, flag: FeatureFlag) -> FeatureFlag | None:
        try:
            with self._connect() as conn:
                cursor = conn.execute(
                    """
                    UPDATE flags
                    SET default_state = %s, segment_key = %s, segments = %s, rollout_percent = %s
                    WHERE name = %s
                    """,
                    (
                        flag.default_state,
                        flag.segment_key,
                        Jsonb(flag.segments),
                        int(flag.rollout_percent),
                        flag.name,
                    ),
                )
                updated = cursor.rowcount > 0
        except psycopg.Error as exc:
            raise FlagStoreError(f"failed to update flag '{flag.name}'") from exc
        if not updated:
            return None
        return flag

    def delete(self, name: str) -> bool:
        try:
            with self._connect() as conn:
                cursor = conn.execute("DELETE FROM flags WHERE name = %s", (name,))
                deleted = cursor.rowcount > 0
        except psycopg.Error as exc:
            raise FlagStoreError(f"failed to delete flag '{name}'") from exc
        return deleted
