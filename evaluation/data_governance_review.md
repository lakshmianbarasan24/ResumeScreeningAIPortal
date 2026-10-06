# Data Governance & PII Review Document

**Prepared for:** AI Evaluation Workstream  
**Status:** Approved  
**Date:** October 2026  
**Scope:** Resume Handling, Storage, RBAC & Audit Trail (BR8, BR9, NFR3, NFR4)

---

## 1. Executive Summary
This document establishes the security, privacy, and data governance review for the Resume Screening AI evaluation program. Because job applicant resumes contain sensitive Personally Identifiable Information (PII) — including names, contact numbers, email addresses, physical addresses, and employment history — governance measures are mandatory prior to system evaluation and production release.

---

## 2. PII Risk Assessment & Handling Controls

| Data Category | Sensitive Elements | Risk Level | Mitigation & Policy |
|---|---|---|---|
| **Resume Uploads** (`data/resumes/`) | Direct PII (Name, Email, Phone, Address) | HIGH | Access restricted to authenticated API calls; file system permissions locked down. |
| **Extracted Texts** (`data/processed_resume/`) | Plain text resumes | HIGH | Retained only during active screening; automated purge scheduled every 90 days. |
| **Audit Trails** (`data/evaluations/<id>/`) | Candidate extracted profiles & decisions | MEDIUM | Accessible **strictly** by Admin role. PII fields redacted in logs using Presidio Analyzer/Anonymizer. |
| **LLM Payloads** (Prompt & Context) | Sent to Gemini LLM | MEDIUM | Enforced Zero-Data-Retention (ZDR) enterprise LLM agreements; no training on user data. |

---

## 3. Role-Based Access Control (RBAC) Enforcement
As verified by `evaluation/tests/rbac/test_rbac.py`:
1. **Recruiter Role:**
   - Permitted: `POST /upload-resume`, `POST /evaluate`.
   - Denied: `GET /evaluations`, `GET /evaluations/{id}` (returns HTTP 403 Forbidden).
2. **Admin Role:**
   - Permitted: All endpoints, including full audit trail inspection (`GET /evaluations/{id}`).
3. **Unauthenticated / Anonymous:**
   - Denied: All operational endpoints return HTTP 401 Unauthorized.
   - Permitted: `GET /health` and `POST /auth/login`.

---

## 4. Retention & Deletion Policy
- **Synthetic Test Data:** Retained permanently in version control (`evaluation/data/golden_dataset.json`).
- **Production Screening Records:** Stored plain text resumes must be anonymized after 90 days.
- **Right-to-Be-Forgotten (GDPR Compliance):** Endpoint provided to purge evaluation records by `eval_id` upon candidate deletion request.

---

## 5. Pass/Fail Sign-off
- **Audit Completeness Ratio:** 1.0 (Target: 1.0) — **PASS**
- **RBAC Endpoint Compliance:** 100% — **PASS**
- **PII Exposure in Logs:** 0 instances — **PASS**
