---
name: ragflow-performance-report
description: Diagnoses and provides optimization recommendations for slow RagFlow agents by analyzing their DSL configuration for bottlenecks like TOC enhancement overhead, excessive top_k, or missing rerankers.
---

# RagFlow Performance Report

This skill automates the identification of performance bottlenecks in RagFlow agents. It specifically targets issues that cause high latency (90s+) and massive token overhead.

## Workflow

1.  **Identify Agent ID**: Obtain the agent ID from the user (e.g., `4e7fe12c665211f1815b89b948263ffa`).
2.  **Run Analysis Script**: Execute the bundled Python script to pull the Agent DSL from the database and analyze its configuration.
    *   Command: `python3 /root/.gemini/skills/ragflow-performance-report/scripts/analyze.py <agent_id>`
3.  **Analyze Findings**:
    *   **TOC Enhancement**: Check if `toc_enhance` is enabled on large manuals. This is the #1 cause of "1M+ token" context bloat.
    *   **Top_K Settings**: Check for `top_k > 512` which can slow down vector retrieval.
    *   **Rerankers**: Check if a reranker is missing, which often forces users to over-rely on TOC enhancement for quality.
4.  **Present Recommendations**: Provide a structured list of critical fixes and optimizations.

## Resources

*   **Analysis Script**: `/root/.gemini/skills/ragflow-performance-report/scripts/analyze.py`
    *   Queries `rag_flow.user_canvas` or `rag_flow.agent` tables.
    *   Extracts component parameters for all retrieval tools.
