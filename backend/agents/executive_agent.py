import json
import os
from pathlib import Path

# Save metrics alongside the FAISS vector DB folder
METRICS_FILE = os.path.join(os.path.dirname(__file__), "..", "database", "metrics.json")

class ExecutiveTrackingAgent:
    def __init__(self):
        self.metrics_file = METRICS_FILE
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self.metrics_file):
            os.makedirs(os.path.dirname(self.metrics_file), exist_ok=True)
            with open(self.metrics_file, "w") as f:
                json.dump({
                    "total_interviews_conducted": 0, 
                    "evaluations": [], 
                    "average_readiness_score": 0.0
                }, f)

    def log_evaluation(self, topic: str, score: float):
        self._ensure_file_exists()
        with open(self.metrics_file, "r") as f:
            data = json.load(f)
        
        data["evaluations"].append({"topic": topic, "score": score})
        data["total_interviews_conducted"] = len(data["evaluations"])
        
        scores = [e["score"] for e in data["evaluations"]]
        data["average_readiness_score"] = round(sum(scores) / len(scores), 2) if scores else 0.0
        
        with open(self.metrics_file, "w") as f:
            json.dump(data, f, indent=4)

    def get_dashboard_metrics(self):
        self._ensure_file_exists()
        with open(self.metrics_file, "r") as f:
            return json.load(f)
