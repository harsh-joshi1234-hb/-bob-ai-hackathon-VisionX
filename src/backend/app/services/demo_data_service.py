import os
import uuid
import random
import numpy as np
from sqlalchemy.orm import Session
from app.models.demo_lot_mapping import DemoLotMapping
from app.models.lot import Lot, LotStatus
from app.models.process_record import ProcessRecord

class DemoDataService:
    def __init__(self):
        self.demo_lots = [
            {
                "lot_id": "LOT-001",
                "wafer_source_id": "WM811K-0012",
                "secom_source_record_id": "SECOM-ROW-45",
                "description": "High risk pattern with correlated sensor anomalies."
            },
            {
                "lot_id": "LOT-002",
                "wafer_source_id": "WM811K-4421",
                "secom_source_record_id": "SECOM-ROW-91",
                "description": "Normal batch with center defect pattern."
            },
            {
                "lot_id": "LOT-003",
                "wafer_source_id": "WM811K-1002",
                "secom_source_record_id": "SECOM-ROW-03",
                "description": "Clear wafer map but failed sensor checks."
            }
        ]

    def _generate_mock_wafer_image(self, path: str):
        """Generates a random mock wafer image if one doesn't exist."""
        if os.path.exists(path):
            return
            
        os.makedirs(os.path.dirname(path), exist_ok=True)
        wafer = np.ones((64, 64), dtype=int)
        y, x = np.ogrid[-32:32, -32:32]
        mask = x**2 + y**2 > 30**2
        wafer[mask] = 0
        defect_mask = np.random.random((64, 64)) > 0.95
        wafer[defect_mask & ~mask] = 2
        np.save(path, wafer)

    def seed_demo_mappings(self, db: Session, data_dir: str):
        """
        Populate the database with the application-level demo mappings.
        """
        for demo in self.demo_lots:
            # Check if mapping already exists
            existing_mapping = db.query(DemoLotMapping).filter(DemoLotMapping.lot_id == demo["lot_id"]).first()
            if not existing_mapping:
                wafer_path = os.path.join(data_dir, f"wafer_{demo['lot_id']}.npy")
                self._generate_mock_wafer_image(wafer_path)
                
                mapping = DemoLotMapping(
                    lot_id=demo["lot_id"],
                    wafer_source_id=demo["wafer_source_id"],
                    wafer_image_path=wafer_path,
                    secom_source_record_id=demo["secom_source_record_id"],
                    description=demo["description"]
                )
                db.add(mapping)
                
            # Also create the corresponding Lot and ProcessRecord objects if they don't exist
            # So the rest of the system can function normally.
            existing_lot = db.query(Lot).filter(Lot.lot_id == demo["lot_id"]).first()
            if not existing_lot:
                lot = Lot(lot_id=demo["lot_id"], status=LotStatus.PENDING)
                lot.wafer_image_path = os.path.join(data_dir, f"wafer_{demo['lot_id']}.npy")
                db.add(lot)
                db.flush() # get lot id
                
                pr = ProcessRecord(
                    lot_id=lot.id,
                    source_record_id=demo["secom_source_record_id"]
                )
                # Seed random 24 features
                for i in range(24):
                    setattr(pr, f"feature_{i:02d}", random.gauss(0, 1))
                db.add(pr)
                
        db.commit()

demo_data_service = DemoDataService()
