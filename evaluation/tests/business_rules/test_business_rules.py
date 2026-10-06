"""
Business Rules & Hard Caps Test Suite (BR1, BR2, Section 2.2)
Verifies:
- Base score calculation (% required + up to +10 preferred)
- Missing >=3 required skills -> max 65
- Domain mismatch -> max 70
- Core function last performed >= 2 years ago -> max 75
- <50% required matched -> max 50
- Score bands: >=80 Advance, 50-79 Hold, <50 Reject
"""

import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from client import SUTClient


@pytest.fixture
def sut_client():
    client = SUTClient()
    client.login("recruiter", "recruiterpass")
    return client


def test_strong_candidate_advance(sut_client):
    jd = "Seeking Python, FastAPI, SQL, Docker engineer."
    res_text = "Experienced Engineer in Python, FastAPI, SQL, Docker, AWS, Redis."
    res = sut_client.evaluate(jd, res_text)
    assert res["status_code"] == 200
    data = res["data"]
    assert data["fit_score"] >= 80
    assert data["recommendation"] == "Advance"


def test_missing_3_skills_cap(sut_client):
    jd = "Seeking Python, FastAPI, SQL, Docker, Machine Learning engineer."
    res_text = "Junior Dev with Python skill."
    res = sut_client.evaluate(jd, res_text)
    data = res["data"]
    assert data["fit_score"] <= 65
    assert len(data["missing_skills"]) >= 3


def test_domain_mismatch_cap(sut_client):
    jd = "Seeking Backend Engineer in Python, SQL."
    res_text = "Candidate from unrelated domain with Python, SQL knowledge."
    res = sut_client.evaluate(jd, res_text)
    data = res["data"]
    assert data["fit_score"] <= 70


def test_stale_skills_cap(sut_client):
    jd = "Seeking Python, SQL, Docker, FastAPI."
    res_text = "Developer in Python, SQL, Docker, FastAPI. Core function last performed: 2020."
    res = sut_client.evaluate(jd, res_text)
    data = res["data"]
    assert data["fit_score"] <= 75


def test_weak_candidate_reject(sut_client):
    jd = "Seeking Python, FastAPI, SQL, Docker."
    res_text = "Sales manager with no software background."
    res = sut_client.evaluate(jd, res_text)
    data = res["data"]
    assert data["fit_score"] < 50
    assert data["recommendation"] == "Reject"
