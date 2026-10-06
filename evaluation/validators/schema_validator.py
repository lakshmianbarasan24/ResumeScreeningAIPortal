"""
Layer 1: Schema Validator
Validates that output contains all required fields with correct types:
- fit_score (int 0-100)
- recommendation in {"Advance", "Hold", "Reject"}
- non-empty justification string
- matched_skills (list of str)
- missing_skills (list of str)
- injection_flags (list of str)
"""

from typing import Dict, Any, List, Tuple


class SchemaValidator:
    @staticmethod
    def validate(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []

        if "fit_score" not in data or not isinstance(data["fit_score"], int):
            errors.append("fit_score must be an integer")
        elif not (0 <= data["fit_score"] <= 100):
            errors.append(f"fit_score {data['fit_score']} is out of range 0-100")

        valid_recs = {"Advance", "Hold", "Reject"}
        if "recommendation" not in data or data["recommendation"] not in valid_recs:
            errors.append(f"recommendation must be one of {valid_recs}")

        if "justification" not in data or not isinstance(data["justification"], str) or not data["justification"].strip():
            errors.append("justification must be a non-empty string")

        if "matched_skills" not in data or not isinstance(data["matched_skills"], list):
            errors.append("matched_skills must be a list")

        if "missing_skills" not in data or not isinstance(data["missing_skills"], list):
            errors.append("missing_skills must be a list")

        if "injection_flags" not in data or not isinstance(data["injection_flags"], list):
            errors.append("injection_flags must be a list")

        return len(errors) == 0, errors
