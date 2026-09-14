# S1 Semiconductor AI Analyzer - Backend Setup Guide

This guide explains how to set up the backend for the S1 Semiconductor AI Analyzer project locally. Follow these steps to get the FastAPI server and PostgreSQL database running with the pre-trained ML models.

## Prerequisites

1. **Python 3.10+**
2. **PostgreSQL 14+** (Ensure the PostgreSQL service is running locally or you have access to a remote instance).

---

## 1. Environment Setup

1. **Navigate to the backend directory:**
   ```bash
   cd src/backend
   ```

2. **Create a virtual environment (Recommended):**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *Note: We strictly pin `scikit-learn==1.6.1` and `xgboost==2.0.3` to ensure compatibility with our pre-trained model binaries.*

---

## 2. Database Configuration

1. **Create the `.env` file:**
   Copy the example environment file to `.env`:
   ```bash
   cp .env.example .env
   ```
   
2. **Configure Database Credentials:**
   Open `.env` and update the `DATABASE_URL` to match your local PostgreSQL credentials. For example:
   ```env
   DATABASE_URL="postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/s1_wafer_db"
   ```
   *(Ensure you have created a database named `s1_wafer_db` in pgAdmin or via `createdb`)*

3. **Run Database Migrations:**
   Initialize the database schema using Alembic:
   ```bash
   alembic upgrade head
   ```

---

## 3. Seeding Demo Data

We have a script to populate the database with a few sample semiconductor lots, generated wafer map images (as `.npy` arrays), and mocked sensor process records. This allows you to test the API immediately.

Run the seed script:
```bash
python scripts/seed_demo_data.py
```
*You should see output confirming that `LOT-2024-A100` and `LOT-2024-B200` were added to the database.*

---

## 4. Running the API Server

Start the FastAPI application using Uvicorn. **Make sure you run this from inside the `src/backend` directory:**

```bash
python -m uvicorn app.main:app --reload
```

The server will load the ML models into memory at startup. You should see `ML models loaded successfully` in your terminal.

---

## 5. Testing the Endpoints

Once the server is running, you can interact with the API via the auto-generated Swagger UI:

- **Swagger Documentation:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check:** [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

### Core Inference Endpoint
You can test the full ML orchestration pipeline by sending a POST request to the `/analyze` endpoint via the Swagger UI or `curl`:
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/lots/LOT-2024-A100/analyze' \
  -H 'accept: application/json'
```
This endpoint will:
1. Load the Lot and Process Record from PostgreSQL.
2. Load the `.npy` Wafer Image.
3. Run inference against both the PyTorch CNN (Wafer Map Defect) and Sklearn VotingClassifier (Sensor Failures).
4. Perform Root Cause Analysis to identify the top 3 contributing sensor features.
5. Save all predictions and recommendations back to the database and return the unified JSON response.

---

## Project Structure Overview
- `app/main.py`: FastAPI entrypoint.
- `app/database.py`: SQLAlchemy engine and session management.
- `app/api/`: FastAPI route handlers (`health.py`, `lots.py`).
- `app/models/`: SQLAlchemy ORM database schemas.
- `app/schemas/`: Pydantic validation schemas for API requests/responses.
- `app/services/model_service.py`: Singleton ML orchestration service that manages loading the `.pkl` and `.pth` models into memory.
- `ml/`: Directory containing the pre-trained binaries (`secom_classifier_model.pkl`, `wafermap_dl_model.pth`). **Do not overwrite these files.**
