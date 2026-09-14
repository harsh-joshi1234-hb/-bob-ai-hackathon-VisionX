import os
import sys

# Load env before importing app
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from fastapi.testclient import TestClient
from app.main import app, load_ml_models

# Manually trigger model loading for testing
load_ml_models()
client = TestClient(app)

def run_tests():
    print("Testing /api/health ...")
    resp = client.get("/api/health")
    print(f"Health Response: {resp.status_code}")
    print(resp.json())
    assert resp.status_code == 200

    print("\nTesting /api/lots ...")
    resp = client.get("/api/lots")
    print(f"Lots Response: {resp.status_code}")
    lots = resp.json()
    print(lots)
    assert resp.status_code == 200
    assert len(lots) > 0
    
    first_lot = lots[0]
    lot_id = first_lot["lot_id"]
    
    print(f"\nTesting /api/lots/{lot_id} ...")
    resp = client.get(f"/api/lots/{lot_id}")
    print(f"Lot Details: {resp.status_code}")
    print(resp.json())
    assert resp.status_code == 200
    
    print(f"\nTesting POST /api/lots/{lot_id}/analyze ...")
    resp = client.post(f"/api/lots/{lot_id}/analyze")
    print(f"Analysis Response: {resp.status_code}")
    if resp.status_code != 200:
        print(f"Error: {resp.text}")
    else:
        print(resp.json())
    assert resp.status_code == 200

if __name__ == "__main__":
    run_tests()
