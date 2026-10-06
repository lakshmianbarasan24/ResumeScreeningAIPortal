"""
Fairness Test Suite (BR3, FR8, NFR6)
Verifies:
- Score parity across matched pairs (gender, ethnicity, age)
- Max allowed score delta <= 5 points
- Recommendations match between matched pairs
"""

import pytest
import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from client import SUTClient
from validators import FairnessValidator

MATCHED_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/matched_pairs"))


@pytest.fixture
def sut_client():
    client = SUTClient()
    client.login("recruiter", "recruiterpass")
    return client


def test_gender_matched_pair_parity(sut_client):
    file_path = os.path.join(MATCHED_DIR, "gender_pairs.json")
    with open(file_path, "r", encoding="utf-8") as f:
        pairs = json.load(f)

    for pair in pairs:
        res_a = sut_client.evaluate(pair["jd_text"], pair["resume_a"]["text"])["data"]
        res_b = sut_client.evaluate(pair["jd_text"], pair["resume_b"]["text"])["data"]

        valid, errors = FairnessValidator.validate_pair(res_a, res_b, pair["max_allowed_delta"])
        assert valid, f"Gender Fairness Violation: {errors}"


def test_ethnicity_matched_pair_parity(sut_client):
    file_path = os.path.join(MATCHED_DIR, "ethnicity_pairs.json")
    with open(file_path, "r", encoding="utf-8") as f:
        pairs = json.load(f)

    for pair in pairs:
        res_a = sut_client.evaluate(pair["jd_text"], pair["resume_a"]["text"])["data"]
        res_b = sut_client.evaluate(pair["jd_text"], pair["resume_b"]["text"])["data"]

        valid, errors = FairnessValidator.validate_pair(res_a, res_b, pair["max_allowed_delta"])
        assert valid, f"Ethnicity Fairness Violation: {errors}"


def test_age_matched_pair_parity(sut_client):
    file_path = os.path.join(MATCHED_DIR, "age_pairs.json")
    with open(file_path, "r", encoding="utf-8") as f:
        pairs = json.load(f)

    for pair in pairs:
        res_a = sut_client.evaluate(pair["jd_text"], pair["resume_a"]["text"])["data"]
        res_b = sut_client.evaluate(pair["jd_text"], pair["resume_b"]["text"])["data"]

        valid, errors = FairnessValidator.validate_pair(res_a, res_b, pair["max_allowed_delta"])
        assert valid, f"Age Fairness Violation: {errors}"
