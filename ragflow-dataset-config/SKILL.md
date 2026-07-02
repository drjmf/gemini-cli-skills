---
name: ragflow-dataset-config
description: Updates RagFlow dataset configurations (language, metadata generation settings) via API. Fixes the "uneditable UI" issue by using the dedicated metadata endpoint.
---

# RagFlow Dataset Configuration Skill

This skill allows you to programmatically update RagFlow dataset settings. It solves the common issue where API-updated metadata fields appear "grayed out" or uneditable in the UI by using the correct sequence of API calls.

## Available Resources

- **Update Script**: `/root/.gemini/skills/ragflow-dataset-config/scripts/update_dataset.py`
- **Template**: `/opt/mycelia-ai-stack/credo_pilot_configurations/ragflow_dataset_metadata_config.json`

## Workflow

1.  **Prepare Configuration**: 
    - Use the JSON template provided in the resources.
    - Ensure `metadata_generation_settings` use the keys: `key`, `type` (string/list/number/time), `description`, and optionally `enum`.

2.  **Execute Update**:
    - Run the script with the dataset name and your config file.
    - Command: `python3 /root/.gemini/skills/ragflow-dataset-config/scripts/update_dataset.py "<Dataset Name>" <config.json>`

3.  **Verification**:
    - The script will report `Success` for both general and metadata updates.
    - In the RagFlow UI, go to **Dataset Settings**. Your metadata fields should be visible under "Metadata generation settings" and fully editable.

## Technical Note
This skill performs two distinct API calls:
- `PUT /api/v1/datasets/<id>` for general settings (Language).
- `PUT /api/v1/datasets/<id>/metadata/config` for the schema definitions.
