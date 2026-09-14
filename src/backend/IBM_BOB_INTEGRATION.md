# IBM Bob Intelligence Layer Integration

This document describes how the "IBM Bob" LLM layer is integrated into the S1 Semiconductor AI Analyzer. 

## Role of IBM Bob

IBM Bob acts strictly as an **intelligence summarization and explanation layer**, bridging the gap between raw machine learning output and actionable engineering insights. 

**Crucially, IBM Bob DOES NOT make numerical ML predictions.** 
All numerical predictions, probabilities, and risk levels are generated exclusively by the deterministic, pre-trained ML models (`secom_classifier_model.pkl` and `wafermap_dl_model.pth`).

IBM Bob's role is to:
1. Provide a human-readable **executive summary** of the lot/batch's status.
2. Formulate a **root cause explanation** translating the quantitative SHAP values (feature importance) into a narrative context.
3. Consolidate **evidence** supporting the explanation.
4. Suggest **corrective actions** and **next checks** based purely on the provided data context.
5. Provide a **limitations** statement to ensure engineers understand the boundaries of the analysis.

## Safety and Hallucination Prevention

To prevent hallucination and ensure absolute reliability in a manufacturing context, the integration adheres to strict constraints:
- **Strict Prompting constraints:** The LLM is explicitly instructed never to invent sensor values, probabilities, defect classes, model metrics, historical records, or physical meanings for anonymous sensors (e.g., `Feature_059`).
- **No Causal Claims:** The LLM is forbidden from claiming causal relationships from correlation alone (e.g., it will state "is historically correlated with" rather than "caused").
- **Structured JSON Output:** The LLM output is strictly bounded to a predefined JSON schema.
- **Fail-Safe Mechanism:** If the LLM service is unavailable, or credentials are missing, the system catches the failure gracefully and returns a clear `service-unavailable` JSON state. It **never** fakes an LLM response.

## Integration Architecture

1. **Service Class:** `src/backend/app/services/ai_explanation_service.py`
2. **API Interaction:** The service interacts with IBM watsonx.ai REST API via standard `urllib.request`. It authenticates using an IAM token generated from an API Key.
3. **Data Flow:**
    - The core analysis orchestrator (e.g., `/analyze` endpoint) runs the deterministic ML models and computes SHAP feature rankings.
    - These verified metrics are assembled into a strict textual payload.
    - The payload is sent to IBM Bob (Watsonx LLM) via the `generate_explanation` method.
    - The JSON response is parsed, appended to the final response, and returned to the frontend dashboard.

## Configuring IBM Bob Credentials

To enable this feature, configure the `.env` file in the backend directory. 

### How to get a free API key:
1. Sign up for a free IBM Cloud account at [cloud.ibm.com](https://cloud.ibm.com).
2. Provision a **watsonx.ai** or **Watson Machine Learning** instance.
3. Navigate to **Manage > Access (IAM) > API Keys** to generate an API key (`WATSONX_API_KEY`).
4. In your watsonx.ai project settings, locate your Project ID (`WATSONX_PROJECT_ID`).

Add these to your `src/backend/.env` file:
```env
WATSONX_API_KEY=your_ibm_api_key_here
WATSONX_PROJECT_ID=your_ibm_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29
WATSONX_MODEL_ID=meta-llama/llama-3-70b-instruct
```
