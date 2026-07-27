---
name: ragflow-agent-repair
description: Safely repairs and updates RagFlow agent DSLs (graphs) without causing UI corruption. Use when an agent is not responding, has broken node references, or disappears from the UI after an update.
---

# RagFlow Agent Repair

This skill provides a robust workflow for diagnosing and fixing RagFlow agent graph (DSL) issues while ensuring data integrity. It uses HEX injection to bypass shell escaping issues that frequently cause agent UI corruption.

## Workflow

1.  **Identify Agent ID**: Search for the agent by title using `python3 scripts/repair.py <name_fragment> list-agents`.
2.  **Extract Current DSL**: Use `python3 scripts/repair.py <agent_id> get` to retrieve the current state as a HEX string.
3.  **Decode and Fix**:
    - Use Python to decode the HEX to JSON.
    - Identify broken node references (e.g., a Message node referencing an inactive Agent node).
    - Apply the necessary fixes to the JSON structure.
4.  **Update Safely**: Use `python3 scripts/repair.py <agent_id> update <path_to_fixed_json>` to push the fix back to the database via HEX injection.
5.  **Emergency Restore**: If the agent disappears or becomes unusable, use `python3 scripts/repair.py <agent_id> restore` to revert to the last versioned state.

## Core Safety Rule
**Never update the `dsl` column directly via `UPDATE ... SET dsl = '{json}'`** in a shell command. Always use the `repair.py` script's `update` command which uses HEX encoding to prevent data corruption.

## Common Repair Patterns
- **Broken Reference**: A node output variable `{NodeID@content}` points to a non-existent or inactive node.
- **Missing Start**: The `begin` node is not connected to the expected entry point.
- **Prompt Corruption**: Control characters (`\r`, `\n`) in the system prompt being mangled by shell execution.

## Resources
- **Repair Script**: `/root/skills/ragflow-agent-repair/scripts/repair.py`
  - Handles `get`, `update`, `restore`, and `list-agents` actions.
