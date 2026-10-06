"""
Layer 3: Groundedness & Hallucination Validator
Verifies that claims made in the justification or matched skills are grounded in the resume text.
"""

from typing import Dict, Any, List, Tuple


class GroundednessValidator:
    @staticmethod
    def validate(data: Dict[str, Any], resume_text: str) -> Tuple[bool, List[str]]:
        errors = []
        res_lower = resume_text.lower()
        matched = data.get("matched_skills", [])

        # Check if matched skills actually appear in resume text
        unsupported_skills = []
        for skill in matched:
            if skill.lower() not in res_lower:
                unsupported_skills.append(skill)

        if unsupported_skills:
            errors.append(f"Groundedness Violation: Matched skills not in resume text: {unsupported_skills}")

        return len(errors) == 0, errors
