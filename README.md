# 🚀 S1 Semiconductor AI Analyzer

---

## 👥 Team

| Field | Value |
|---|---|
| **Team Name** | VisionX |
| **Track** | AI |
| **Team Lead** | Harsh Joshi — 24dce049@charusat.edu.in |
| **Members** | Harsh Joshi, Ayaan Mansuri, Dipak Karangiya, Priyanshi Pojara |

---

## 🎯 Problem Statement

Semiconductor manufacturing yields are critically impacted by micro-defects and sensor anomalies that are difficult to trace across disparate datasets. Engineers struggle to rapidly correlate wafer defect patterns with out-of-control process sensors, leading to prolonged downtimes and reduced manufacturing efficiency.

---

## 💡 Solution

We built a multimodal AI analysis pipeline that seamlessly integrates wafer map defect classification (WM-811K) with sensor parameter risk prediction (SECOM dataset). Our solution dynamically ranks root causes using SHAP and leverages an IBM watsonx.ai LLM layer (IBM Bob) to generate actionable, human-readable insights for process engineers.

---

## ✨ Key Features

- **Feature 1:** Multimodal Orchestration: Combines a PyTorch CNN for Wafer Map Defects and an XGBoost VotingClassifier for Process Risk.
- **Feature 2:** Root Cause Analysis: Calculates SHAP feature contributions dynamically to isolate failing sensors.
- **Feature 3:** Upcoming Batch Risk Monitoring: Pre-screens scheduled lots and flags elevated failure probabilities.
- **Feature 4:** IBM Bob Intelligence Layer: Translates strict ML metrics into executive summaries without hallucinating causal claims.
- **Feature 5:** Transparent Data Mapping: Demonstrates integration across independent public datasets using application-level demo lots.

---

## 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| **Languages** | Python |
| **Frameworks** | FastAPI, PyTorch, Scikit-learn, XGBoost |
| **IBM Technologies** | watsonx.ai (IBM Bob) |
| **Databases** | PostgreSQL, SQLAlchemy |
| **Other** | Alembic, SHAP |

---

## 📁 Repository Structure

```
├── src/                  # All source code
│   └── backend/          # FastAPI backend services and DB models
├── docs/                 # Written documentation
│   ├── problem-statement.md
│   ├── solution-overview.md
│   ├── architecture.md
│   └── setup-guide.md
├── demo/                 # Demo artifacts
│   ├── screenshots/      # App screenshots
│   └── demo-video-link.txt  # Link to demo video
├── presentation/         # Slide deck
└── submission.yaml       # Structured submission metadata
```

---

## ⚡ How to Run

```bash
# 1. Clone the repo
git clone https://github.com/harsh-joshi1234-hb/-bob-ai-hackathon-VisionX.git
cd -bob-ai-hackathon-VisionX/src/backend

# 2. Install dependencies
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your values including DATABASE_URL

# 4. Run database migrations and seed data
alembic upgrade head
python scripts/seed_demo_data.py

# 5. Run the project
uvicorn app.main:app --reload
```

---

## 🖥️ Demo

| Artifact | Link |
|---|---|
| 📹 Demo Video | See demo/demo-video-link.txt |
| 🖼️ Screenshots | See demo/screenshots/ |
| 📊 Presentation | See presentation/slides.pdf |

---

## ⚠️ Known Limitations

- **Authentication:** Currently mocked and not production-ready.
- **Independent Public Datasets & Demo Lot Mappings:** The WM-811K (wafer maps) and SECOM (process sensors) datasets are fundamentally independent. Our demo mapping layers them together purely to demonstrate the multimodal capabilities of our platform via application-level demo lots.
- **Anonymous Process Features:** The SECOM dataset uses anonymized sensor features (e.g., Feature_59), meaning the LLM's recommended corrective actions are structurally sound but rely on abstract sensor names rather than specific real-world equipment tags.
- **Model Limitations:** Local execution relies on CPU inference for models; scaling would require GPU environments for real-time high-volume inference.
- **Probability Availability:** Exact failure probabilities are estimates based on the XGBoost voting classifier's calibration on the unbalanced SECOM dataset.
- **LLM Limitations:** While IBM Bob is restricted from making up causal claims, its recommendations are generated based solely on SHAP outputs. It cannot verify physical equipment state beyond the provided data metrics.

---

## 🏅 What We're Most Proud Of

We are most proud of the strict architectural separation between our deterministic Machine Learning models and the generative AI (IBM Bob) layer. By supplying only constrained, verified SHAP metrics and probabilities to the LLM, we achieved a highly interpretable, hallucination-free intelligence layer suited for strict manufacturing environments.

---

## 🔑 IBM watsonx.ai Credentials Integration

To enable the IBM Bob LLM layer, you need a free API key from IBM Cloud:
1. Sign up for a free IBM Cloud account at cloud.ibm.com.
2. Provision a watsonx.ai or Watson Machine Learning instance.
3. Create an API Key in Manage > Access (IAM) > API Keys.
4. Find your Project ID in the watsonx.ai project settings.
Add these to your `src/backend/.env` file:
```env
WATSONX_API_KEY=your_ibm_api_key_here
WATSONX_PROJECT_ID=your_ibm_project_id_here
```
