"""
Black-box HTTP client wrapper for the Resume Screening AI System Under Test (SUT).
Enforces NFR10 (Architecture Independence): calls endpoints solely via HTTP requests over port 8000.
"""

import os
import requests
from typing import Dict, Any, Optional

DEFAULT_BASE_URL = os.getenv("SUT_BASE_URL", "http://127.0.0.1:8000")


class SUTClient:
    def __init__(self, base_url: str = DEFAULT_BASE_URL):
        self.base_url = base_url.rstrip("/")
        self.token: Optional[str] = None
        self.role: Optional[str] = None

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """POST /auth/login -> returns dict with access_token and role"""
        url = f"{self.base_url}/auth/login"
        resp = requests.post(url, json={"username": username, "password": password}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        self.token = data.get("access_token")
        self.role = data.get("role")
        return data

    def _get_headers(self, custom_token: Optional[str] = None) -> Dict[str, str]:
        token = custom_token if custom_token is not None else self.token
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def upload_resume(self, file_path: str, filename: Optional[str] = None, custom_token: Optional[str] = None) -> Dict[str, Any]:
        """POST /upload-resume -> accepts .txt, .md, .pdf, .docx"""
        url = f"{self.base_url}/upload-resume"
        fname = filename or os.path.basename(file_path)
        with open(file_path, "rb") as f:
            files = {"file": (fname, f.read())}
        resp = requests.post(url, files=files, headers=self._get_headers(custom_token), timeout=15)
        return {"status_code": resp.status_code, "data": resp.json() if resp.status_code == 200 else resp.text}

    def evaluate(self, jd_text: str, resume_text: str, custom_token: Optional[str] = None) -> Dict[str, Any]:
        """POST /evaluate -> returns EvalResult object or error"""
        url = f"{self.base_url}/evaluate"
        payload = {"jd_text": jd_text, "resume_text": resume_text}
        resp = requests.post(url, json=payload, headers=self._get_headers(custom_token), timeout=20)
        return {"status_code": resp.status_code, "data": resp.json() if resp.status_code == 200 else resp.text}

    def get_evaluations(self, custom_token: Optional[str] = None) -> Dict[str, Any]:
        """GET /evaluations -> admin only"""
        url = f"{self.base_url}/evaluations"
        resp = requests.get(url, headers=self._get_headers(custom_token), timeout=10)
        return {"status_code": resp.status_code, "data": resp.json() if resp.status_code == 200 else resp.text}

    def get_evaluation_by_id(self, eval_id: str, custom_token: Optional[str] = None) -> Dict[str, Any]:
        """GET /evaluations/{id} -> admin only, full audit record"""
        url = f"{self.base_url}/evaluations/{eval_id}"
        resp = requests.get(url, headers=self._get_headers(custom_token), timeout=10)
        return {"status_code": resp.status_code, "data": resp.json() if resp.status_code == 200 else resp.text}

    def health(self) -> Dict[str, Any]:
        """GET /health"""
        url = f"{self.base_url}/health"
        resp = requests.get(url, timeout=5)
        return {"status_code": resp.status_code, "data": resp.json()}
