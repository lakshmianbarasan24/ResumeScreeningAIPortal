"""
Layer 2: Content & Internal Consistency Validator
Validates:
- Recommendation matches score band (>=80 Advance, 50-79 Hold, <50 Reject)
- Score respects business hard caps (missing >=3 required skills -> max 65, etc.)
- matched_skills and missing_skills have no overlapping items
"""

from typing import Dict, Any, List, Tuple


class ContentValidator:
    @staticmethod
    def validate(data: Dict[str, Any], resume_text: str = "") -> Tuple[bool, List[str]]:
        errors = []
        score = data.get("fit_score", 0)
        rec = data.get("recommendation", "")
        matched = set(data.get("matched_skills", []))
        missing = set(data.get("missing_skills", []))

        # Check score band alignment
        if score >= 80 and rec != "Advance":
            errors.append(f"Score {score} >= 80 requires 'Advance', got '{rec}'")
        elif 50 <= score <= 79 and rec != "Hold":
            errors.append(f"Score {score} in 50-79 requires 'Hold', got '{rec}'")
        elif score < 50 and rec != "Reject":
            errors.append(f"Score {score} < 50 requires 'Reject', got '{rec}'")

        # Check list non-overlap
        overlap = matched.intersection(missing)
        if overlap:
            errors.append(f"matched_skills and missing_skills overlap on: {list(overlap)}")

        # Check Hard Caps
        if len(missing) >= 3 and score > 65:
            errors.append(f"Hard Cap Violation: missing >=3 skills ({len(missing)}) caps score at 65, got {score}")

        if "<50%" in resume_text or len(matched) < len(missing):
            if score > 50:
                errors.append(f"Hard Cap Violation: <50% required skills matched caps score at 50, got {score}")

        return len(errors) == 0, errors
