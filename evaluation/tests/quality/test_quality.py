"""
Quality & Output Groundedness Test Suite (BR5, FR4, FR5, FR6)
Verifies:
- 6-Layer Output Validation passing on golden dataset cases
- Schema validity, content consistency, groundedness of justification
"""

import pytest
import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from client import SUTClient
from validators import SchemaValidator, ContentValidator, GroundednessValidator

GOLDEN_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/golden_dataset.json"))


@pytest.fixture
def sut_client():
    client = SUTClient()
    client.login("recruiter", "recruiterpass")
    return client


def test_golden_dataset_quality_and_schema(sut_client):
    with open(GOLDEN_PATH, "r", encoding="utf-8") as f:
        cases = json.load(f)

    for case in cases:
        res = sut_client.evaluate(case["jd_text"], case["resume_text"])
        assert res["status_code"] == 200
        data = res["data"]

        # Layer 1: Schema
        schema_valid, schema_errs = SchemaValidator.validate(data)
        assert schema_valid, f"Case {case['id']} Schema error: {schema_errs}"

        # Layer 2: Content & Caps
        content_valid, content_errs = ContentValidator.validate(data, case["resume_text"])
        assert content_valid, f"Case {case['id']} Content error: {content_errs}"

        # Layer 3: Groundedness
        ground_valid, ground_errs = GroundednessValidator.validate(data, case["resume_text"])
        assert ground_valid, f"Case {case['id']} Groundedness error: {ground_errs}"

        # Match Expected Outcome Bands
        exp = case["expected_outcomes"]
        assert exp["fit_score_min"] <= data["fit_score"] <= exp["fit_score_max"], \
            f"Case {case['id']} Score {data['fit_score']} outside expected band [{exp['fit_score_min']}, {exp['fit_score_max']}]"

        assert data["recommendation"] == exp["recommendation"], \
            f"Case {case['id']} Recommendation '{data['recommendation']}' != expected '{exp['recommendation']}'"
