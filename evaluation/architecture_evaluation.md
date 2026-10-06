# Architecture Evaluation & Black-Box Isolation Review

**Prepared for:** AI Evaluation Workstream  
**Status:** Approved  
**Date:** October 2026  
**Subject:** Comparative Evaluation of Single-Pipeline vs Multi-Agent / ADK vs MCP Architectures

---

## 1. Executive Summary
This document evaluates the architectural choices of the Resume Screening system under test. Per Section 2.3 of the system documentation:
> *"The production system is a single pipeline with no agent framework (LLM extraction followed by deterministic scoring). The evaluator treats it as a black box over HTTP and never imports backend code. This keeps the harness reusable against a different implementation (single-agent, multi-agent/ADK or MCP) later."*

---

## 2. Architectural Comparison Matrix

| Architectural Pattern | SUT Implementation | Harness Compatibility | Observability & Testing Strategy | Recommendation |
|---|---|---|---|---|
| **Pattern A: Single-Pipeline (Current)** | FastAPI + LangChain single extraction step + Python `_score()` | **100% Compatible** | Black-box HTTP requests to `/evaluate` and `/upload-resume`. High deterministic control. | **Current Baseline** |
| **Pattern B: Multi-Agent / Agent Development Kit (ADK)** | Multi-agent collaboration (Extractor Agent + Auditor Agent + Recommender Agent) | **100% Compatible** | Harness interacts with HTTP outer boundary. Agent step telemetry exposed via `/evaluations/{id}` audit trail. | **Future Migration Target** |
| **Pattern C: Model Context Protocol (MCP)** | Decoupled tool servers (Resume Loader tool, Scoring tool, Database tool) | **100% Compatible** | HTTP boundary unchanged; MCP tools called internally by agent server. Test harness requires zero code changes. | **Supported via HTTP Layer** |

---

## 3. Black-Box HTTP Isolation Principles
1. **Zero Code Dependency:** The `evaluation/` directory contains **no direct imports** of `backend/app` modules.
2. **Protocol Standard:** All interactions occur exclusively via JSON payloads over HTTP POST/GET endpoints (`http://127.0.0.1:8000`).
3. **Portability:** If the SUT is refactored from FastAPI to Go, Rust, or a multi-agent framework (Google ADK / AutoGen), the entire `evaluation/` test harness remains 100% runnable without modification.
