import os
import json
import urllib.request
import urllib.error
import urllib.parse
from typing import Dict, Any, List, Optional

class AIExplanationService:
    def __init__(self):
        self.api_key = os.getenv("WATSONX_API_KEY")
        self.project_id = os.getenv("WATSONX_PROJECT_ID")
        self.url = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29")
        self.model_id = os.getenv("WATSONX_MODEL_ID", "meta-llama/llama-3-70b-instruct") 

    def _get_iam_token(self) -> str:
        if not self.api_key:
            raise ValueError("Missing WATSONX_API_KEY")
        
        token_url = "https://iam.cloud.ibm.com/identity/token"
        data = urllib.parse.urlencode({
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": self.api_key
        }).encode("utf-8")
        
        req = urllib.request.Request(token_url, data=data)
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        req.add_header("Accept", "application/json")
        
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode("utf-8"))
                return result.get("access_token")
        except urllib.error.URLError as e:
            raise RuntimeError(f"Failed to obtain IAM token: {str(e)}")

    def _build_prompt(
        self,
        lot_id: str,
        wafer_prediction: str,
        wafer_confidence: Optional[float],
        process_prediction: str,
        process_probability: Optional[float],
        shap_rankings: List[Dict[str, Any]],
        historical_comparison: Optional[str],
        upcoming_batch_risk: Optional[float]
    ) -> str:
        prompt = f"""You are IBM Bob, the AI assistant for the S1 Semiconductor AI Analyzer.
Your task is to provide an executive summary and explanation based ONLY on the provided Machine Learning evidence.

CRITICAL RULES:
1. NEVER invent sensor values, probabilities, defect classes, model metrics, or historical records.
2. NEVER assign physical meanings (e.g. temperature, pressure) to anonymous features (e.g. Feature_059).
3. NEVER claim causal relationships; use terms like "is correlated with" or "contributed to the model's prediction".
4. If information is unavailable, explicitly state "insufficient evidence".
5. Output MUST be valid JSON.

EVIDENCE PROVIDED:
- Lot ID: {lot_id}
- Wafer Defect Prediction: {wafer_prediction} (Confidence: {wafer_confidence if wafer_confidence is not None else 'N/A'})
- Process Risk Prediction: {process_prediction} (Probability of Failure: {process_probability if process_probability is not None else 'N/A'})
- SHAP / Root-cause rankings: {json.dumps(shap_rankings)}
- Historical Comparison: {historical_comparison or 'insufficient evidence'}
- Upcoming Batch Risk: {upcoming_batch_risk if upcoming_batch_risk is not None else 'N/A'}

Respond with ONLY the following JSON structure:
{{
    "summary": "High-level executive summary.",
    "root_cause_explanation": "Explanation based on the SHAP values.",
    "evidence": ["Evidence 1", "Evidence 2"],
    "corrective_actions": ["Action 1", "Action 2"],
    "next_checks": ["Check 1", "Check 2"],
    "limitations": ["Limitation 1", "Limitation 2"]
}}
"""
        return prompt

    def generate_explanation(
        self,
        lot_id: str,
        wafer_prediction: str,
        wafer_confidence: Optional[float],
        process_prediction: str,
        process_probability: Optional[float],
        shap_rankings: List[Dict[str, Any]],
        historical_comparison: Optional[str] = None,
        upcoming_batch_risk: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Generates an explanation using IBM Watsonx.ai LLM.
        """
        if not self.api_key or not self.project_id:
            return {
                "status": "unavailable",
                "message": "IBM Watsonx API credentials are not configured. AI explanation is currently unavailable."
            }
            
        prompt = self._build_prompt(
            lot_id, wafer_prediction, wafer_confidence, 
            process_prediction, process_probability, shap_rankings, 
            historical_comparison, upcoming_batch_risk
        )
        
        try:
            token = self._get_iam_token()
            
            payload = {
                "input": prompt,
                "parameters": {
                    "decoding_method": "greedy",
                    "max_new_tokens": 800,
                    "repetition_penalty": 1.0,
                    "stop_sequences": ["}"]
                },
                "model_id": self.model_id,
                "project_id": self.project_id
            }
            
            req = urllib.request.Request(self.url, data=json.dumps(payload).encode("utf-8"))
            req.add_header("Authorization", f"Bearer {token}")
            req.add_header("Content-Type", "application/json")
            req.add_header("Accept", "application/json")
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode("utf-8"))
                generated_text = result["results"][0]["generated_text"]
                
                # Because we used stop_sequences=["}"], the JSON might lack the final closing brace
                if not generated_text.strip().endswith("}"):
                    generated_text += "}"
                
                # Find first { and last }
                start = generated_text.find("{")
                end = generated_text.rfind("}") + 1
                if start == -1 or end == 0:
                    raise RuntimeError("LLM did not return a JSON object.")
                    
                json_str = generated_text[start:end]
                explanation_data = json.loads(json_str)
                explanation_data["status"] = "success"
                return explanation_data
                
        except json.JSONDecodeError:
            return {
                "status": "unavailable",
                "message": "AI explanation failed: LLM returned malformed JSON."
            }
        except Exception as e:
            return {
                "status": "unavailable",
                "message": f"AI explanation failed or service is unavailable: {str(e)}"
            }

ai_explanation_service = AIExplanationService()
