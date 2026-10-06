"""
Post-Production Monitor & History Logger (FR13, FR14, Section 9)
Re-runs quality checks on scheduled intervals or sampled live traffic,
appends every execution run to reports/history.jsonl, and flags SLA breaches.
"""

import os
import json
import time
import datetime
from typing import Dict, Any
from client import SUTClient

BASE_DIR = os.path.dirname(__file__)
HISTORY_PATH = os.path.join(BASE_DIR, "reports", "history.jsonl")


def run_monitoring_cycle() -> Dict[str, Any]:
    client = SUTClient()
    admin_client = SUTClient()
    admin_client.login("admin", "adminpass")

    # Fetch live evaluations
    evals_resp = admin_client.get_evaluations()
    evals = evals_resp.get("data", []) if evals_resp.get("status_code") == 200 else []

    total_evals = len(evals)
    flagged_injections = sum(1 for e in evals if len(e.get("result", {}).get("injection_flags", [])) > 0)
    scores = [e.get("result", {}).get("fit_score", 0) for e in evals]
    avg_score = sum(scores) / len(scores) if scores else 0.0

    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "monitor_run_id": f"mon_{int(time.time())}",
        "total_evaluations_monitored": total_evals,
        "average_fit_score": round(avg_score, 2),
        "flagged_injections_count": flagged_injections,
        "sla_breached": flagged_injections > 0 or (avg_score < 40 or avg_score > 90)
    }

    os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
    with open(HISTORY_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

    print(f"Monitor cycle logged: {entry}")
    return entry


if __name__ == "__main__":
    run_monitoring_cycle()
