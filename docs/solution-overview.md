# Solution Overview

## What We Built
The S1 Semiconductor AI Analyzer is a multimodal orchestration platform designed to bridge the gap between spatial wafer defect data and tabular process sensor data. It provides process engineers with immediate, actionable insights into manufacturing anomalies, drastically reducing the time required for root-cause analysis.

## How It Works

1. **Wafer Analysis:** We utilize a pre-trained PyTorch Convolutional Neural Network (CNN) trained on the WM-811K dataset to classify spatial defect patterns on semiconductor wafer maps (e.g., Edge-Ring, Center, Scratch).
2. **Process Risk Analysis:** Simultaneously, an XGBoost VotingClassifier (trained on the SECOM dataset) analyzes hundreds of process and sensor signals to predict the probability of failure for a given lot.
3. **SHAP Root-Cause Analysis:** When a high risk of failure is detected, the system dynamically calculates SHAP (SHapley Additive exPlanations) values to isolate and rank the specific sensor features contributing most to the predicted failure.
4. **IBM Bob / LLM Role:** Instead of overwhelming engineers with raw SHAP metrics and probability scores, the system feeds these constrained, deterministic ML outputs into an IBM watsonx.ai LLM layer (IBM Bob). IBM Bob translates these metrics into human-readable, executive summaries and generates actionable corrective recommendations without hallucinating causal claims.
5. **Upcoming Batch Monitoring:** The platform continuously pre-screens scheduled lots and their associated process telemetry, flagging elevated failure probabilities before the wafers are fully processed, enabling proactive interventions.

## Architecture Diagram

> See [`architecture.md`](architecture.md) for the detailed diagram.

## Key Design Decisions

| Decision | Rationale |
|---|---|
| **Multimodal approach** | Wafer maps and sensor data tell two halves of the same story; analyzing them together provides a complete picture of manufacturing health. |
| **SHAP for interpretability** | Black-box ML models are untrusted in strict manufacturing environments. SHAP provides mathematical proof of *why* the model made a prediction. |
| **Strict separation of ML and LLM** | To prevent hallucinations, the LLM (IBM Bob) is not allowed to analyze raw data. It only summarizes the deterministic outputs (SHAP values, probabilities) of the ML models. |
