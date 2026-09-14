"""
models/upcoming_batch.py
-------------------------
UPCOMING_BATCHES table.

Represents a scheduled future production lot that has been pre-screened
by the risk prediction pipeline before physical manufacture begins.

``process_record_id`` points to the ProcessRecord that holds the
simulated / projected sensor values used to estimate risk.

Risk levels
-----------
    HIGH   → P(FAIL) >= 0.70
    MEDIUM → P(FAIL) >= 0.40
    LOW    → P(FAIL) <  0.40
(Thresholds are applied by the business logic layer, not enforced in DB.)

Statuses
--------
    FLAGGED    → risk above threshold; requires engineer review
    CLEARED    → reviewed and approved to proceed
    ON_HOLD    → blocked pending process parameter adjustment
    CANCELLED  → batch will not be manufactured
"""

import uuid
import enum

from sqlalchemy import (
    Column,
    DateTime,
    Enum as SAEnum,
    Float,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class RiskLevel(str, enum.Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"


class BatchStatus(str, enum.Enum):
    FLAGGED = "FLAGGED"
    CLEARED = "CLEARED"
    ON_HOLD = "ON_HOLD"
    CANCELLED = "CANCELLED"


class UpcomingBatch(Base):
    """
    Columns
    -------
    id                 UUID primary key.
    batch_id           Human-readable batch identifier (fab system).
    process_record_id  FK → process_records.id — projected sensor values.
    predicted_risk     Scalar risk probability [0, 1] (P(FAIL) estimate).
    risk_level         Categorical risk tier: HIGH | MEDIUM | LOW | UNKNOWN.
    flag_reason        Free-text reason for the flag (e.g. "Feature 8 out
                       of control limit").
    status             Workflow state: FLAGGED | CLEARED | ON_HOLD | CANCELLED.
    scheduled_at       Planned manufacture / processing datetime.
    created_at         Row insertion timestamp.
    updated_at         Last modification timestamp.
    """

    __tablename__ = "upcoming_batches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)

    batch_id = Column(
        String(128),
        nullable=False,
        unique=True,
        comment="Human-readable fab batch identifier, e.g. BATCH-2024-005",
    )
    process_record_id = Column(
        UUID(as_uuid=True),
        ForeignKey("process_records.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Projected sensor values used for pre-screening",
    )

    predicted_risk = Column(
        Float,
        nullable=True,
        comment="Estimated P(FAIL) in [0, 1] produced by the SECOM classifier",
    )
    risk_level = Column(
        SAEnum(RiskLevel, name="risk_level_enum", create_type=True),
        nullable=False,
        default=RiskLevel.UNKNOWN,
        server_default=RiskLevel.UNKNOWN.value,
    )
    flag_reason = Column(
        Text,
        nullable=True,
        comment="Plain-text explanation of why the batch was flagged",
    )
    status = Column(
        SAEnum(BatchStatus, name="batch_status_enum", create_type=True),
        nullable=False,
        default=BatchStatus.FLAGGED,
        server_default=BatchStatus.FLAGGED.value,
    )
    scheduled_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Planned manufacture / processing datetime",
    )
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    process_record = relationship("ProcessRecord")

    # ------------------------------------------------------------------
    # Indexes
    # ------------------------------------------------------------------
    __table_args__ = (
        Index("ix_upcoming_batches_batch_id", "batch_id"),
        Index("ix_upcoming_batches_risk_level", "risk_level"),
        Index("ix_upcoming_batches_status", "status"),
        Index("ix_upcoming_batches_scheduled_at", "scheduled_at"),
        Index("ix_upcoming_batches_process_record_id", "process_record_id"),
    )

    def __repr__(self) -> str:
        return (
            f"<UpcomingBatch id={self.id} batch_id={self.batch_id!r} "
            f"risk={self.risk_level} status={self.status}>"
        )
