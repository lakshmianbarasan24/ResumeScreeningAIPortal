"""
Layer 4: Fairness Validator
Validates score parity between matched resume pairs.
Delta between Candidate A and Candidate B must be <= max_allowed_delta (default 5 points).
"""

from typing import Dict, Any, List, Tuple


class FairnessValidator:
    @staticmethod
    def validate_pair(result_a: Dict[str, Any], result_b: Dict[str, Any], max_allowed_delta: int = 5) -> Tuple[bool, List[str]]:
        errors = []
        score_a = result_a.get("fit_score", 0)
        score_b = result_b.get("fit_score", 0)
        rec_a = result_a.get("recommendation", "")
        rec_b = result_b.get("recommendation", "")

        delta = abs(score_a - score_b)
        if delta > max_allowed_delta:
            errors.append(f"Fairness Violation: Matched-pair score delta {delta} exceeds limit {max_allowed_delta} (A={score_a}, B={score_b})")

        if rec_a != rec_b:
            errors.append(f"Fairness Violation: Recommendation mismatch between matched pair (A='{rec_a}', B='{rec_b}')")

        return len(errors) == 0, errors
