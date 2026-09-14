import uuid
from sqlalchemy import Column, String, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base

class DemoLotMapping(Base):
    """
    demo_lot_mappings table.
    
    Application-level demo mapping that transparently connects selected source records
    for demonstration purposes. WM-811K and SECOM are independent datasets, so this 
    mapping only exists to demonstrate the multimodal pipeline. 
    It NEVER stores expected predictions.
    """
    __tablename__ = "demo_lot_mappings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    
    lot_id = Column(
        String(128),
        nullable=False,
        unique=True,
        comment="Application-level identifier like LOT-001, LOT-002",
    )
    
    wafer_source_id = Column(
        String(128),
        nullable=True,
        comment="Original ID from the WM-811K dataset",
    )
    
    wafer_image_path = Column(
        String(512),
        nullable=True,
        comment="Path to the actual .npy wafer image",
    )
    
    secom_source_record_id = Column(
        String(128),
        nullable=True,
        comment="Original ID from the SECOM dataset",
    )
    
    description = Column(
        String(512),
        nullable=True,
        comment="Description of the mapped datasets",
    )
    
    source_dataset = Column(
        String(128),
        nullable=False,
        default="WM-811K + SECOM",
    )
    
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        Index("ix_demo_lot_mappings_lot_id", "lot_id"),
    )
