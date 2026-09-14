import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, lots, batches
from app.services.model_service import model_service

app = FastAPI(
    title="S1 Semiconductor AI Analyzer",
    description="Backend API for Wafer Yield Root Cause & Defect Pattern Analysis",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For demo purposes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Models on Startup
@app.on_event("startup")
def load_ml_models():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    secom_path = os.path.join(base_dir, "ml", "secom_classifier_model.pkl")
    wafermap_path = os.path.join(base_dir, "ml", "wafermap_dl_model.pth")
    
    print("Loading ML models...")
    model_service.load_models(secom_path, wafermap_path)
    print("ML models loaded successfully.")

# Include Routers
app.include_router(health.router)
app.include_router(lots.router)
app.include_router(batches.router)

if __name__ == "__main__":
    import uvicorn
    # Load .env variables before starting the server
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
    
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
