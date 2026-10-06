"""
Phase 1 — RBAC & Security Access Control Test Suite
Verifies FR11 / BR9 / NFR4 access control rules across all SUT endpoints.
"""

import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from client import SUTClient


@pytest.fixture
def sut_client():
    return SUTClient()


def test_auth_login_recruiter(sut_client):
    res = sut_client.login("recruiter", "recruiterpass")
    assert res["role"] == "recruiter"
    assert "access_token" in res


def test_auth_login_admin(sut_client):
    res = sut_client.login("admin", "adminpass")
    assert res["role"] == "admin"
    assert "access_token" in res


def test_auth_login_invalid(sut_client):
    with pytest.raises(Exception):
        sut_client.login("wronguser", "wrongpass")


def test_unauthenticated_requests(sut_client):
    # evaluate without token -> 401
    res = sut_client.evaluate("JD text", "Resume text", custom_token="")
    assert res["status_code"] == 401

    # list evaluations without token -> 401
    res = sut_client.get_evaluations(custom_token="")
    assert res["status_code"] == 401


def test_recruiter_forbidden_admin_endpoints(sut_client):
    login_res = sut_client.login("recruiter", "recruiterpass")
    recruiter_token = login_res["access_token"]

    # Recruiter trying to list all evaluations -> 403
    res = sut_client.get_evaluations(custom_token=recruiter_token)
    assert res["status_code"] == 403

    # Recruiter trying to get specific evaluation -> 403
    res = sut_client.get_evaluation_by_id("eval_1001", custom_token=recruiter_token)
    assert res["status_code"] == 403


def test_admin_access_allowed(sut_client):
    login_res = sut_client.login("admin", "adminpass")
    admin_token = login_res["access_token"]

    res = sut_client.get_evaluations(custom_token=admin_token)
    assert res["status_code"] == 200
    assert isinstance(res["data"], list)


def test_expired_and_tampered_tokens(sut_client):
    res_exp = sut_client.evaluate("JD", "Resume", custom_token="expired_token")
    assert res_exp["status_code"] == 401

    res_tamp = sut_client.evaluate("JD", "Resume", custom_token="tampered_token")
    assert res_tamp["status_code"] == 401
