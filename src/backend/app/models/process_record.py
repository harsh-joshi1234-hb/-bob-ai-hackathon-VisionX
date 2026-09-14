"""
models/process_record.py
------------------------
PROCESS_RECORDS table.

Stores the 24 preprocessed SECOM sensor features associated with a lot.

Design decision
---------------
The SECOM model expects exactly 24 float features named '0'–'23' (string
integer indices — see ML_MODEL_INTEGRATION.md).  Because the real semantic
names of those columns are UNKNOWN (the preprocessing script was not saved),
we store them as generic named columns ``feature_00`` … ``feature_23``.

When/if the preprocessing artefacts are recovered and the real SECOM column
names are established, an Alembic migration can rename these columns without
changing anything else in the schema.

The ``source_record_id`` column is a string reference to the upstream system's
row identifier (e.g., the SECOM dataset row index or an ERP record ID).  It
is informational; no FK constraint is imposed because the upstream system is
external.
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ProcessRecord(Base):
    """
    One row per set of sensor measurements for a lot.

    A lot may have more than one process record when multiple wafers or
    multiple time-points are submitted together (e.g., a batch re-analysis).

    Columns
    -------
    id                Internal UUID primary key.
    lot_id            FK → lots.id.
    source_record_id  Upstream system row identifier (informational, no FK).
    feature_00 …
    feature_23        The 24 preprocessed float features the SECOM model
                      expects.  Values are z-score scaled; may be NULL when
                      raw data could not be preprocessed.
    created_at        Row insertion timestamp.
    """

    __tablename__ = "process_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)

    lot_id = Column(
        UUID(as_uuid=True),
        ForeignKey("lots.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    source_record_id = Column(
        String(256),
        nullable=True,
        comment="Upstream system row/record identifier (ERP, SECOM row index, etc.)",
    )

    # ------------------------------------------------------------------
    # The 24 SECOM model features (see ML_MODEL_INTEGRATION.md §Input).
    # Column names use zero-padded indices so they sort correctly and map
    # unambiguously to model feature positions 0–23.
    # All are nullable: a partial record can be stored and flagged later.
    # ------------------------------------------------------------------
    feature_00 = Column(Float, nullable=True, comment="SECOM model feature index 0")
    feature_01 = Column(Float, nullable=True, comment="SECOM model feature index 1")
    feature_02 = Column(Float, nullable=True, comment="SECOM model feature index 2")
    feature_03 = Column(Float, nullable=True, comment="SECOM model feature index 3")
    feature_04 = Column(Float, nullable=True, comment="SECOM model feature index 4")
    feature_05 = Column(Float, nullable=True, comment="SECOM model feature index 5")
    feature_06 = Column(Float, nullable=True, comment="SECOM model feature index 6")
    feature_07 = Column(Float, nullable=True, comment="SECOM model feature index 7")
    feature_08 = Column(Float, nullable=True, comment="SECOM model feature index 8")
    feature_09 = Column(Float, nullable=True, comment="SECOM model feature index 9")
    feature_10 = Column(Float, nullable=True, comment="SECOM model feature index 10")
    feature_11 = Column(Float, nullable=True, comment="SECOM model feature index 11")
    feature_12 = Column(Float, nullable=True, comment="SECOM model feature index 12")
    feature_13 = Column(Float, nullable=True, comment="SECOM model feature index 13")
    feature_14 = Column(Float, nullable=True, comment="SECOM model feature index 14")
    feature_15 = Column(Float, nullable=True, comment="SECOM model feature index 15")
    feature_16 = Column(Float, nullable=True, comment="SECOM model feature index 16")
    feature_17 = Column(Float, nullable=True, comment="SECOM model feature index 17")
    feature_18 = Column(Float, nullable=True, comment="SECOM model feature index 18")
    feature_19 = Column(Float, nullable=True, comment="SECOM model feature index 19")
    feature_20 = Column(Float, nullable=True, comment="SECOM model feature index 20")
    feature_21 = Column(Float, nullable=True, comment="SECOM model feature index 21")
    feature_22 = Column(Float, nullable=True, comment="SECOM model feature index 22")
    feature_23 = Column(Float, nullable=True, comment="SECOM model feature index 23")

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    lot = relationship("Lot", back_populates="process_records")

    # ------------------------------------------------------------------
    # Indexes
    # ------------------------------------------------------------------
    __table_args__ = (
        Index("ix_process_records_lot_id", "lot_id"),
        Index("ix_process_records_source_record_id", "source_record_id"),
        Index("ix_process_records_created_at", "created_at"),
    )

    # ------------------------------------------------------------------
    # Helper: convert to the ordered list the model expects
    # ------------------------------------------------------------------
    def to_feature_vector(self) -> list:
        """
        Return the 24 feature values as an ordered list [f0, f1, …, f23].
        Preserves None/NaN values — the caller is responsible for imputation.
        """
        return [
            self.feature_00, self.feature_01, self.feature_02, self.feature_03,
            self.feature_04, self.feature_05, self.feature_06, self.feature_07,
            self.feature_08, self.feature_09, self.feature_10, self.feature_11,
            self.feature_12, self.feature_13, self.feature_14, self.feature_15,
            self.feature_16, self.feature_17, self.feature_18, self.feature_19,
            self.feature_20, self.feature_21, self.feature_22, self.feature_23,
        ]

    def __repr__(self) -> str:
        return (
            f"<ProcessRecord id={self.id} lot_id={self.lot_id} "
            f"source={self.source_record_id!r}>"
        )
