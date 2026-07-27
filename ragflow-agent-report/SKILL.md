---
name: ragflow-agent-report
description: Generates a performance and diagnostic report for a RagFlow agent. Use when the user asks for logs, tool usage, or internal steps of a specific RagFlow dialogue or agent ID.
---

# RagFlow Agent Report Skill

This skill extracts and analyzes RagFlow logs and configurations to provide a detailed report on agent performance, tool usage, metadata filtering, and execution timing.

## Workflow

1. **Identify Agent ID**: Ensure you have the target RagFlow agent ID (e.g., `bd62e008795d11f1a2a4f704f892ca8d`).
2. **Identify Timezone**: Check if the user wants **UTC** (log default) or a local timezone like **Lisbon (UTC+1)**.
3. **Run Diagnostic Script**: Use the bundled Python script to map tools to datasets and fetch recent logs.
   - Command: `python3 /root/.gemini/skills/ragflow-agent-report/scripts/report.py <agent_id>`
4. **Extract Metadata Config**: Check the Agent DSL in the database to find:
   - Metadata field names (e.g., `literacy_component`, `group_level_id`).
   - Filter operators (e.g., `contains`, `equal`).
5. **Analyze Logs**: Extract the execution timeline and calculate durations:
   - Metadata filter generation duration.
   - Tool call durations.
   - Answer compilation time.
6. **Present Report**: Create a structured table including Metadata Tags and Durations.

## Resources
- **Report Script**: `/root/.gemini/skills/ragflow-agent-report/scripts/report.py`
  - Fetches tool mappings and log tails from MySQL and Docker.

## Example Report Structure

### Internal Execution Steps
| Step | Time (UTC) | Action / Tool Used | Applied Metadata Tags | Result | Duration |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | HH:MM:SS | Tool Call: search_my_dateset_N | `tag_name: value` | Found: Document X | Xs |

### Tool to Dataset Mapping
| Tool ID | Alias | Dataset Name | Metadata Fields Used |
| :--- | :--- | :--- | :--- |
| `search_my_dateset_7` | `Retrieval_Manuals` | Credo Teaching Manuals | `literacy_component`, `language` |
