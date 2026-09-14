import os
import sys
import uuid
import random
import numpy as np

# Load .env before importing anything from app
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

# Add the src/backend directory to sys.path so we can import 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.database import engine, Base
from app.models.lot import Lot, LotStatus
from app.models.process_record import ProcessRecord

def generate_mock_wafer_image(path: str):
    """Generate a random 64x64 numpy array representing a wafer map and save it to a .npy file."""
    # 0 = background, 1 = normal die, 2 = failing die
    # Create mostly normal (1) with some background (0) and defects (2)
    wafer = np.ones((64, 64), dtype=int)
    
    # Add a circular background mask
    y, x = np.ogrid[-32:32, -32:32]
    mask = x**2 + y**2 > 30**2
    wafer[mask] = 0
    
    # Add random defects
    defect_mask = np.random.random((64, 64)) > 0.95
    wafer[defect_mask & ~mask] = 2
    
    np.save(path, wafer)

def seed_database():
    # Ensure tables are created (already done via alembic, but just in case)
    # Base.metadata.create_all(bind=engine)
    
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'demo'))
    os.makedirs(data_dir, exist_ok=True)
    
    with Session(engine) as db:
        # Check if already seeded
        if db.query(Lot).count() > 0:
            print("Database already contains lots. Skipping seed.")
            return

        print("Seeding database with demo lots...")
        
        # Lot 1
        lot1 = Lot(lot_id="LOT-2024-A100", status=LotStatus.PENDING)
        wafer_path_1 = os.path.join(data_dir, "wafer_A100.npy")
        generate_mock_wafer_image(wafer_path_1)
        lot1.wafer_image_path = wafer_path_1
        
        # Lot 2
        lot2 = Lot(lot_id="LOT-2024-B200", status=LotStatus.PENDING)
        wafer_path_2 = os.path.join(data_dir, "wafer_B200.npy")
        generate_mock_wafer_image(wafer_path_2)
        lot2.wafer_image_path = wafer_path_2

        db.add_all([lot1, lot2])
        db.commit()
        
        print(f"Added Lots: {lot1.lot_id}, {lot2.lot_id}")
        
        # Add Process Records (24 features for SECOM model)
        # Random normal distribution around 0, scaled
        pr1 = ProcessRecord(
            lot_id=lot1.id,
            source_record_id="SECOM-ROW-001",
        )
        for i in range(24):
            setattr(pr1, f"feature_{i:02d}", random.gauss(0, 1))

        pr2 = ProcessRecord(
            lot_id=lot2.id,
            source_record_id="SECOM-ROW-002",
        )
        for i in range(24):
            setattr(pr2, f"feature_{i:02d}", random.gauss(0, 1))
            
        db.add_all([pr1, pr2])
        db.commit()
        
        print("Added Process Records.")
        print("Seeding complete.")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
    seed_database()
