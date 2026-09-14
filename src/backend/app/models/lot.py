"""
models/lot.py
-------------
LOTS table — one row per physical wafer lot submitted for analysis.
"""

import uuid
import enum
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Enum as SAEnum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class LotStatus(str, enum.Enum):
    """Lifecycle state of a lot through the analysis pipeline."""
    PENDING = "PENDING"          # received, not yet analysed
    PROCESSING = "PROCESSING"    # analysis in progress
    COMPLETE = "COMPLETE"        # analysis finished successfully
    FAILED = "FAILED"            # analysis ended with an error
    ARCHIVED = "ARCHIVED"        # moved to long-term storage


class Lot(Base):
    """
    Central entity.  Every other table foreign-keys back to this one.

    Columns
    -------
    id                 Internal UUID primary key.
    lot_id             Human-readable lot identifier supplied by the fab
                       system (e.g. "LOT-2024-001234").  Must be unique.
    wafer_image_path   Relative or absolute path to the wafer-map image
                       file stored on disk (or an object-storage key).
                       NULL when no image was provided.
    status             Current pipeline state (see LotStatus enum).
    created_at         Row insertion timestamp (auto-set by DB).
    updated_at         Last modification timestamp (auto-updated by DB).
    """

    __tablename__ = "lots"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    lot_id = Column(
        String(128),
        nullable=False,
        unique=True,
        comment="Human-readable fab lot identifier, e.g. LOT-2024-001234",
    )
    wafer_image_path = Column(
        String(512),
        nullable=True,
        comment="Path or object-storage key to the wafer-map image file",
    )
    status = Column(
        SAEnum(LotStatus, name="lot_status_enum", create_type=True),
        nullable=False,
        default=LotStatus.PENDING,
        server_default=LotStatus.PENDING.value,
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
    # Relationships (back-populated from child tables)
    # ------------------------------------------------------------------
    process_records = relationship(
        "ProcessRecord", back_populates="lot", cascade="all, delete-orphan"
    )
    predictions = relationship(
        "Prediction", back_populates="lot", cascade="all, delete-orphan"
    )
    root_cause_analyses = relationship(
        "RootCauseAnalysis", back_populates="lot", cascade="all, delete-orphan"
    )
    recommendations = relationship(
        "Recommendation", back_populates="lot", cascade="all, delete-orphan"
    )
    analysis_runs = relationship(
        "AnalysisRun", back_populates="lot", cascade="all, delete-orphan"
    )

    # ------------------------------------------------------------------
    # Indexes
    # ------------------------------------------------------------------
    __table_args__ = (
        Index("ix_lots_lot_id", "lot_id"),
        Index("ix_lots_status", "status"),
        Index("ix_lots_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Lot id={self.id} lot_id={self.lot_id!r} status={self.status}>"
