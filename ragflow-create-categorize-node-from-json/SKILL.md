---
name: ragflow-create-categorize-node-from-json
description: Creates or updates a categorization node in a RagFlow agent using definitions (categories, examples, and descriptions) from an external JSON file. Ensures both logic and UI list items are synchronized.
---

# RagFlow Create/Update Categorize Node from JSON

This skill automates the creation and synchronization of complex Categorize nodes from a JSON file. It handles both fresh node creation and updating existing nodes by name, ensuring descriptions and examples are perfectly in sync.

## JSON Format Requirement
The input JSON should be a list of objects with `category` (or `name`), `description` (optional), and `examples` (string or list):
```json
[
  {
    "category": "my_category",
    "description": "Specific guidance for this category",
    "examples": "Example 1\nExample 2"
  }
]
```

## Workflow

1.  **Extract Agent DSL**: Use the `ragflow-agent-repair` skill.
    - `python3 /root/.gemini/skills/ragflow-agent-repair/scripts/repair.py <agent_id> get > agent.hex`

2.  **Generate/Update DSL**: Run the bundled script via a Python wrapper (to avoid shell limits on DSL size).
    ```python
    import sys
    sys.path.append("/root/skills/ragflow-create-categorize-node-from-json/scripts")
    from create_node import create_categorize_node
    
    with open('agent.hex', 'r') as f: hex_data = f.read().strip()
    updated_dsl = create_categorize_node(hex_data, "/path/to/data.json", "Node Name")
    with open('updated.json', 'w') as f: f.write(updated_dsl)
    ```

3.  **Apply Update**: Use the `ragflow-agent-repair` skill.
    - `python3 /root/.gemini/skills/ragflow-agent-repair/scripts/repair.py <agent_id> update updated.json`

4.  **Clear Cache**: Flush Redis and hard refresh the browser.
    - `docker exec ragflow-redis-1 redis-cli -a <password> FLUSHALL`

## Key Improvements
- **Update Mode**: If a node with the same name exists, it reuses the ID and visual position, updating only the content and parameters.
- **Explicit Descriptions**: Uses the `description` field from JSON if available, improving classification accuracy.
- **Connection Preservation**: Preserves existing upstream/downstream connections when updating.
