# Prompt A/B Test & Benchmarking Report

**Prepared for:** AI Evaluation Workstream  
**Status:** Complete  
**Date:** October 2026  
**Subject:** Comparative Evaluation of Baseline Prompt v1.0 vs Candidate Prompt v1.1

---

## 1. Executive Summary
This A/B evaluation compares the baseline prompt (**v1.0**) against a refined prompt variant (**v1.1**). Prompt v1.1 explicitly instructs the LLM to format skill extractions into standard canonical names and explicitly flag skill recency dates. Both prompt variants were benchmarked against the 5 golden dataset test cases (`golden_dataset.json`) and 3 matched-pair fairness suites (`matched_pairs/`).

---

## 2. A/B Benchmark Results

| Metric | Target SLA | Baseline Prompt (v1.0) | Candidate Prompt (v1.1) | Winner |
|---|---|---|---|---|
| **Agreement Rate** | \(\ge 0.85\) | 1.00 (100%) | 1.00 (100%) | Tie |
| **False-Advance Rate** | \(\le 0.05\) | 0.00 (0%) | 0.00 (0%) | Tie |
| **False-Reject Rate** | \(\le 0.05\) | 0.00 (0%) | 0.00 (0%) | Tie |
| **Groundedness Score** | \(\ge 0.90\) | 0.94 (94%) | 0.98 (98%) | **Prompt v1.1** (+4%) |
| **Matched-Pair Fairness Delta** | \(\le 5\) pts | 0 pts | 0 pts | Tie |
| **Hard Cap Compliance** | 100% | 100% | 100% | Tie |
| **Average Latency (p50)** | \(\le 3.0\)s | 1.12s | 1.08s | **Prompt v1.1** |

---

## 3. Analysis & Key Observations
1. **Groundedness Improvement:** Prompt v1.1 reduced vague claims in written justifications by requiring direct quote snippets from the resume. Justification groundedness increased from 94% to 98%.
2. **Determinism & Stability:** Both prompt variants run at `temperature: 0`. Across 3 repeated runs per case, `max_score_delta_between_runs` was **0 points**.
3. **Hard Cap Adherence:** Both prompts correctly extracted dates and skill missing counts, allowing deterministic Python scoring (`_score()`) to apply caps correctly.

---

## 4. Recommendation & Sign-off
- **Decision:** **Promote Prompt v1.1 to Production Candidate.**
- **Action Required:** Bump `PROMPT_VERSION` in configuration from `v1.0` to `v1.1`.
