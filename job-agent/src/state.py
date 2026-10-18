"""SQLite-backed memory so the agent never applies to the same job twice."""

from __future__ import annotations

import hashlib
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    job_key     TEXT PRIMARY KEY,   -- sha1 of canonical job URL
    url         TEXT NOT NULL,
    company     TEXT,
    title       TEXT,
    source      TEXT,               -- greenhouse | lever | ashby | web_search
    status      TEXT NOT NULL,      -- discovered | skipped | blocked | tailored
                                    -- | applied | review | failed
    fit_score   INTEGER,
    notes       TEXT,
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);
"""


def job_key(url: str) -> str:
    canonical = url.split("?")[0].rstrip("/").lower()
    return hashlib.sha1(canonical.encode()).hexdigest()


class State:
    def __init__(self, db_path: Path):
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.execute(SCHEMA)
        self.conn.commit()

    def seen(self, url: str) -> bool:
        row = self.conn.execute(
            "SELECT 1 FROM jobs WHERE job_key = ?", (job_key(url),)
        ).fetchone()
        return row is not None

    def record(
        self,
        url: str,
        status: str,
        company: str | None = None,
        title: str | None = None,
        source: str | None = None,
        fit_score: int | None = None,
        notes: str | None = None,
    ) -> None:
        now = datetime.now(timezone.utc).isoformat()
        self.conn.execute(
            """
            INSERT INTO jobs (job_key, url, company, title, source, status,
                              fit_score, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(job_key) DO UPDATE SET
                status = excluded.status,
                fit_score = COALESCE(excluded.fit_score, jobs.fit_score),
                notes = COALESCE(excluded.notes, jobs.notes),
                updated_at = excluded.updated_at
            """,
            (job_key(url), url, company, title, source, status, fit_score, notes, now, now),
        )
        self.conn.commit()

    def applied_count_today(self) -> int:
        today = datetime.now(timezone.utc).date().isoformat()
        row = self.conn.execute(
            "SELECT COUNT(*) FROM jobs WHERE status = 'applied' AND updated_at >= ?",
            (today,),
        ).fetchone()
        return row[0]

    def summary(self) -> dict[str, int]:
        rows = self.conn.execute(
            "SELECT status, COUNT(*) FROM jobs GROUP BY status"
        ).fetchall()
        return dict(rows)
