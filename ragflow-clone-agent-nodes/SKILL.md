---
name: ragflow-clone-agent-nodes
description: Clones a specific node (logic and visual representation) from one RagFlow agent to another using unique IDs to ensure UI visibility.
---

# RagFlow Clone Agent Nodes

This skill automates the process of copying a node from a source agent to a target agent, ensuring that the node is visible in the UI and has a unique internal ID.

## Workflow

1.  **Extract Source and Target DSLs**: Use the `ragflow-agent-repair` skill to get the HEX strings for both agents.
    - `python3 /root/.gemini/skills/ragflow-agent-repair/scripts/repair.py <source_id> get > source.hex`
    - `python3 /root/.gemini/skills/ragflow-agent-repair/scripts/repair.py <target_id> get > target.hex`

2.  **Clone the Node**: Run the bundled Python script to perform the merge.
    - `python3 /root/skills/ragflow-clone-agent-nodes/scripts/clone.py "$(cat source.hex)" "$(cat target.hex)" "<Node Name>" > updated_target.json`

3.  **Apply the Update**: Use the `ragflow-agent-repair` skill to push the updated JSON back to the target agent.
    - `python3 /root/.gemini/skills/ragflow-agent-repair/scripts/repair.py <target_id> update updated_target.json`

## Safety and Best Practices
- **Unique IDs**: The script automatically generates a new unique ID (e.g., `Categorize:b0dcb29d4934`) to prevent UI conflicts.
- **Visual Graph**: The script syncs the node in both the `components` list (logic) and `graph.nodes` list (visuals).
- **Post-Update**: Advise the user to perform a hard refresh (`Ctrl + F5`) in their browser if the node doesn't appear immediately.
