# Setup Guide

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.10+
- Node.js 18+ (or 20+)
- PostgreSQL 14+ (running locally or accessible remotely)
- An IBM Cloud account with watsonx.ai access

## Environment Variables

### Backend
Navigate to `src/backend` and copy the example environment file:
```bash
cd src/backend
cp .env.example .env
```

Update the `.env` file with your credentials:
```env
WATSONX_API_KEY=your_ibm_api_key_here
WATSONX_PROJECT_ID=your_ibm_project_id_here
DATABASE_URL="postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/s1_wafer_db"
```
*(Ensure you have created a database named `s1_wafer_db` in PostgreSQL)*

## Backend Installation & Setup

1. **Navigate to backend and create virtual environment:**
```bash
cd src/backend
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run database migrations:**
```bash
alembic upgrade head
```

4. **Seed the database with demo data:**
```bash
python scripts/seed_demo_data.py
```

5. **Start the backend server:**
```bash
python -m uvicorn app.main:app --reload
```
The FastAPI server will be running at `http://127.0.0.1:8000`.

## Frontend Installation & Setup

1. **Navigate to the frontend directory:**
```bash
cd src/frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Start the frontend development server:**
```bash
npm run dev
```
The React frontend will typically be running at `http://localhost:5173`.

## Health Check & Example Analysis Request

To ensure the backend is running correctly, you can hit the health check endpoint:
- **Health Check:** `http://127.0.0.1:8000/api/health`
- **Swagger Docs:** `http://127.0.0.1:8000/docs`

**Example Analysis Request (via curl or Swagger UI):**
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/lots/LOT-2024-A100/analyze' \
  -H 'accept: application/json'
```

## Troubleshooting

| Issue | Solution |
|---|---|
| `ModuleNotFoundError` or Model Load Errors | Ensure you are using the pinned versions in `requirements.txt` (e.g., `scikit-learn==1.6.1`, `xgboost==2.0.3`). |
| Database connection refused | Verify PostgreSQL is running and the credentials/port in `DATABASE_URL` are correct. Did you create the `s1_wafer_db` database? |
| IBM watsonx.ai 401 Unauthorized | Check that `WATSONX_API_KEY` and `WATSONX_PROJECT_ID` are set correctly in your `.env` file. |
