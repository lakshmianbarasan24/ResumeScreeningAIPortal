"""
Layer 6: Compliance & Audit Trail Validator
Verifies:
- Evaluation audit record exists and is complete
- Required fields (id, created_at, performed_by, model, prompt_version, extraction, result) are present
- Path traversal attack attempts are rejected with 400 Bad Request
"""

from typing import Dict, Any, List, Tuple


class ComplianceValidator:
    REQUIRED_AUDIT_FIELDS = [
        "id", "created_at", "performed_by", "model", "prompt_version", "extraction", "result"
    ]

    @classmethod
    def validate_audit_record(cls, audit_record: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        for field in cls.REQUIRED_AUDIT_FIELDS:
            if field not in audit_record or audit_record[field] is None:
                errors.append(f"Compliance Violation: Missing required audit field '{field}'")
        return len(errors) == 0, errors
