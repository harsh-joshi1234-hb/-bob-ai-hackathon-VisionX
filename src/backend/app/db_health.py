"""
db_health.py
------------
Database connectivity health-check utilities.

Used by:
  - The FastAPI startup event to confirm the DB is reachable at boot time.
  - The ``GET /health`` endpoint to expose DB status to load-balancers.
  - CLI smoke-tests (run this file directly: ``python -m app.db_health``).

Returns a structured ``HealthResult`` dataclass so the caller can decide
how to surface the information (HTTP response, log line, exit code, etc.).
"""

import time
import traceback
from dataclasses import dataclass, field
from typing import Optional

from sqlalchemy import text

import os
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
except ImportError:
    pass

from app.database import engine


@dataclass
class HealthResult:
    """Result of a single database health-check probe."""
    ok: bool
    latency_ms: float
    db_url_redacted: str          # credentials stripped, safe to log/return
    error: Optional[str] = None
    detail: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "latency_ms": round(self.latency_ms, 2),
            "db_url": self.db_url_redacted,
            "error": self.error,
            **self.detail,
        }


def _redact_url(url: str) -> str:
    """
    Strip the password from a DSN so it is safe to log or return in an API.

    'postgresql+psycopg2://user:secret@host:5432/db'
        → 'postgresql+psycopg2://user:***@host:5432/db'
    """
    try:
        from urllib.parse import urlparse, urlunparse
        parsed = urlparse(url)
        if parsed.password:
            netloc = parsed.netloc.replace(f":{parsed.password}@", ":***@")
            return urlunparse(parsed._replace(netloc=netloc))
    except Exception:
        pass
    return url


def check_database() -> HealthResult:
    """
    Perform a lightweight connectivity probe against the configured database.

    Executes ``SELECT 1`` inside a short-lived connection and measures
    round-trip latency.  Returns a HealthResult whether the probe succeeds
    or fails — it does NOT raise.
    """
    db_url = str(engine.url)
    redacted = _redact_url(db_url)
    start = time.perf_counter()

    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 AS probe"))
            row = result.fetchone()
            assert row is not None and row[0] == 1, "Unexpected probe result"

        latency_ms = (time.perf_counter() - start) * 1000
        return HealthResult(
            ok=True,
            latency_ms=latency_ms,
            db_url_redacted=redacted,
            detail={"probe": "SELECT 1 → OK"},
        )

    except Exception as exc:
        latency_ms = (time.perf_counter() - start) * 1000
        return HealthResult(
            ok=False,
            latency_ms=latency_ms,
            db_url_redacted=redacted,
            error=str(exc),
            detail={"traceback": traceback.format_exc()},
        )


def check_tables_exist() -> HealthResult:
    """
    Verify that the expected application tables exist in the database.
    Useful after running Alembic migrations to confirm they applied correctly.
    """
    expected_tables = {
        "lots",
        "process_records",
        "predictions",
        "root_cause_analysis",
        "recommendations",
        "upcoming_batches",
        "analysis_runs",
    }
    db_url = str(engine.url)
    redacted = _redact_url(db_url)
    start = time.perf_counter()

    try:
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema = 'public'"
                )
            )
            found = {row[0] for row in result}

        missing = sorted(expected_tables - found)
        latency_ms = (time.perf_counter() - start) * 1000

        if missing:
            return HealthResult(
                ok=False,
                latency_ms=latency_ms,
                db_url_redacted=redacted,
                error=f"Missing tables: {missing}",
                detail={"found_tables": sorted(found), "missing_tables": missing},
            )

        return HealthResult(
            ok=True,
            latency_ms=latency_ms,
            db_url_redacted=redacted,
            detail={
                "expected_tables": sorted(expected_tables),
                "all_present": True,
            },
        )

    except Exception as exc:
        latency_ms = (time.perf_counter() - start) * 1000
        return HealthResult(
            ok=False,
            latency_ms=latency_ms,
            db_url_redacted=redacted,
            error=str(exc),
            detail={"traceback": traceback.format_exc()},
        )


# ---------------------------------------------------------------------------
# CLI entry-point  — run with:  python -m app.db_health
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import json
    import sys

    # Load .env if python-dotenv is available
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    print("── DB connectivity probe ──────────────────────────────")
    r1 = check_database()
    print(json.dumps(r1.to_dict(), indent=2))

    print()
    print("── Table existence check ──────────────────────────────")
    r2 = check_tables_exist()
    print(json.dumps(r2.to_dict(), indent=2))

    sys.exit(0 if (r1.ok and r2.ok) else 1)
