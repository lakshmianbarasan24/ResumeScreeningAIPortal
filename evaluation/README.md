# Resume Screening AI — Evaluation Harness & Web Portal

This directory contains the standalone **AI Evaluation Engine** and **System Under Test (SUT)** for black-box testing of the Resume Screening system.

Refer to the master [`README.md`](file:///d:/Lakshmi/Agentic-AI/Capstone-2/README.md) in the project root for full documentation, system architecture, SLA thresholds, and quickstart commands.

## Key Entrypoints:

1. **Interactive Web Portal:** `http://127.0.0.1:8000/` (served from [`frontend/index.html`](file:///d:/Lakshmi/Agentic-AI/Capstone-2/frontend/index.html))
2. **Quality Gates Engine:** `python evaluation/quality_gates.py`
3. **Pytest Suite:** `pytest evaluation/tests/`
4. **Data Generator:** `python evaluation/data/generate_golden_data.py`
5. **Post-Production Monitor:** `python evaluation/monitor.py`
