# S1 Semiconductor AI Analyzer - Backend Walkthrough

This document outlines the current state of the backend API implementation, detailing the endpoints, architecture, and orchestration logic built so far. It serves as a technical walkthrough for team members who will be building on top of this foundation.

## 1. Database Layer (PostgreSQL & SQLAlchemy)
We have implemented a relational schema utilizing PostgreSQL and SQLAlchemy, managed by Alembic migrations (`alembic/versions/`).

### Core Tables:
- **`lots`**: Stores semiconductor lot identifiers and current analysis status. Includes `wafer_image_path` linking to `.npy` arrays.
- **`process_records`**: Stores the 24-feature sensor data associated with a lot.
- **`predictions`**: Stores inference results from both the SECOM Classifier and the WaferMap CNN.
- **`analysis_runs`**: Tracks the execution and status of a specific `/analyze` request.
- **`root_cause_analysis`**: Stores the top contributing sensor features responsible for a failure prediction.
- **`recommendations`**: Stores actionable insights (e.g., "Hold lot for immediate manual inspection") based on the overall risk assessment.

## 2. ML Model Service (`app/services/model_service.py`)
A singleton service manages the loading and execution of our pre-trained binaries.
- **SECOM Classifier**: A scikit-learn `VotingClassifier` loaded from `secom_classifier_model.pkl`. It expects a 24-feature vector.
- **WaferMap CNN**: A PyTorch deep learning model loaded from `wafermap_dl_model.pth`. It expects a 64x64 numpy array (with values 0, 1, 2) which it resizes and normalizes internally.

*Note: Both models are loaded into memory once during FastAPI startup to ensure low-latency inference.*

## 3. FastAPI Endpoints (`app/api/`)

The API is fully documented via Swagger UI at `/docs` when running the server.

### `GET /api/health`
Checks whether the database is successfully connected and whether the two ML models have been loaded into memory.

### `GET /api/lots`
Queries PostgreSQL to return a summary list of all available semiconductor lots.

### `GET /api/lots/{lot_id}`
Returns detailed information for a specific lot, joining against `process_records` to include the sensor feature vectors.

### `POST /api/lots/{lot_id}/analyze` (The Main Orchestrator)
This is the core business logic endpoint. Its execution flow is as follows:
1. **Data Retrieval**: Fetches the Lot and its associated Process Record from the database.
2. **Image Loading**: Loads the `.npy` wafer map file from disk.
3. **Inference Execution**:
   - Calls `model_service.predict_wafer()` to get the defect pattern (e.g., "Center", "Donut", "none") and confidence score.
   - Calls `model_service.predict_secom()` to predict "PASS" or "FAIL".
4. **Root-Cause Analysis (RCA)**: Dynamically extracts feature importances from the `RandomForest` sub-estimator within the VotingClassifier to identify the top 3 critical sensor features driving the prediction.
5. **Risk Assessment**: Computes an `overall_risk` score (Low, Medium, High) by weighting the probabilities of both models.
6. **Data Persistence**: Inserts the predictions, RCA, and generated recommendations back into the PostgreSQL database.
7. **Response**: Returns a comprehensive, Pydantic-validated JSON payload containing all analysis data.

## 4. Next Steps for Development
1. **Frontend Integration**: A React/Next.js frontend can now be built against the `GET /api/lots` and `POST /api/lots/{lot_id}/analyze` endpoints.
2. **Error Handling & Edge Cases**: Further refinement of how the orchestrator handles missing images or incomplete sensor data.
3. **Data Storage**: Transitioning `.npy` files from local disk paths to cloud Object Storage (e.g., AWS S3) if required.
