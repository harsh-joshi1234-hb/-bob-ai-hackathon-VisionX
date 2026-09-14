"""
alembic/env.py
--------------
Alembic migration environment for the S1 Semiconductor AI backend.

Key behaviours
--------------
1.  DATABASE_URL is read from the environment (via python-dotenv if installed),
    never from a hard-coded value in alembic.ini.
2.  All ORM models are imported so that Alembic's autogenerate can detect
    schema changes automatically.
3.  Both offline (SQL script) and online (live connection) modes are supported.
"""

import os
import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config, pool
from alembic import context

# ---------------------------------------------------------------------------
# Make sure 'app' is importable when running alembic from src/backend/
# ---------------------------------------------------------------------------
# alembic is run from src/backend/, so 'app' is a direct child package.
# If running from a different directory, adjust sys.path accordingly.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# ---------------------------------------------------------------------------
# Load .env so DATABASE_URL is available even when running alembic directly
# from the command line without a pre-loaded environment.
# ---------------------------------------------------------------------------
try:
    from dotenv import load_dotenv
    _env_file = Path(__file__).resolve().parent.parent / ".env"
    if _env_file.exists():
        load_dotenv(_env_file)
except ImportError:
    pass  # python-dotenv not installed; rely on the shell environment

# ---------------------------------------------------------------------------
# Import Base + all models so autogenerate sees every table.
# The import order matters: AnalysisRun references Prediction via FK, so
# both must be imported.  The models/__init__.py handles ordering correctly.
# ---------------------------------------------------------------------------
from app.database import Base  # noqa: E402  (after sys.path manipulation)
import app.models  # noqa: F401 — registers all ORM classes with Base.metadata

# ---------------------------------------------------------------------------
# Alembic Config object
# ---------------------------------------------------------------------------
config = context.config

# Inject DATABASE_URL from environment, overriding any value in alembic.ini.
_database_url = os.environ.get("DATABASE_URL")
if _database_url:
    _escaped_url = _database_url.replace('%', '%%')
    config.set_main_option("sqlalchemy.url", _escaped_url)

# Set up Python logging as configured in alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata target for autogenerate comparisons
target_metadata = Base.metadata


# ---------------------------------------------------------------------------
# Offline migration mode (generates SQL script without a live DB connection)
# ---------------------------------------------------------------------------
def run_migrations_offline() -> None:
    """
    Emit migration SQL to stdout without connecting to the database.

    Useful for reviewing what will be applied, or for DBAs who prefer to
    apply SQL manually::

        alembic upgrade head --sql > migration.sql
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Render CREATE TYPE statements for PostgreSQL enums
        include_schemas=True,
    )
    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------------------------
# Online migration mode (connects to the live database)
# ---------------------------------------------------------------------------
def run_migrations_online() -> None:
    """
    Apply migrations to the live database using a real connection.
    Uses NullPool to avoid connection-pool state leaking across migration runs.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # Compare server defaults so Alembic detects server_default changes
            compare_server_defaults=True,
            # Include PostgreSQL-specific type comparison (enums, etc.)
            include_schemas=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
