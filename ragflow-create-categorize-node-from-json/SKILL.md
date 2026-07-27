---
name: ragflow-create-categorize-node-from-json
description: Creates a new categorization node in a RagFlow agent using definitions (categories and examples) from an external JSON file. Ensures both logic and UI list items are synchronized.
---

# RagFlow Create Categorize Node from JSON

This skill automates the creation of a complex Categorize node from a JSON file. It ensures that the node is visible in the UI and correctly configured for the classification engine.

## JSON Format Requirement
The input JSON should be a list of objects with `category` (or `name`) and `examples` (string or list):
```json
[
  {
    "category": "my_category",
    "examples": "Example 1\nExample 2"
  }
]
```

## Workflow

1.  **Extract Agent DSL**: Use the `ragflow-agent-repair` skill.
    - `python3 /root/.gemini/skills/ragflow-agent-repair/scripts/repair.py <agent_id> get > agent.hex`

2.  **Generate New DSL**: Run the bundled script.
    - `python3 /root/skills/ragflow-create-categorize-node-from-json/scripts/create_node.py "$(cat agent.hex)" "/path/to/data.json" "My New Node" > updated.json`

3.  **Apply Update**: Use the `ragflow-agent-repair` skill.
    - `python3 /root/.gemini/skills/ragflow-agent-repair/scripts/repair.py <agent_id> update updated.json`

4.  **Clear Cache**: If the node doesn't appear, flush Redis and hard refresh the browser.
    - `docker exec ragflow-redis-1 redis-cli -a <password> FLUSHALL`

## Best Practices
- **Unique Naming**: Give the node a distinct name to avoid confusion.
- **Positioning**: Default position is `(-700, 300)`. You can provide custom `x` and `y` as trailing arguments to the script.
- **Browser State**: Advise the user to close any open RagFlow tabs before the update to prevent auto-save overwrites.
