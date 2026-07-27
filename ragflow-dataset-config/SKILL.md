---
name: ragflow-dataset-config
description: Updates RagFlow dataset configurations (language, metadata generation settings) via API. Fixes the "uneditable UI" issue by using the dedicated metadata endpoint.
---

# RagFlow Dataset Configuration Skill

This skill allows you to programmatically update RagFlow dataset settings and document-level metadata.

## Available Resources

- **Dataset Update Script**: `/root/.gemini/skills/ragflow-dataset-config/scripts/update_dataset.py`
- **Document Metadata Script**: `/root/.gemini/skills/ragflow-dataset-config/scripts/update_document_metadata.py`
- **Template**: `/opt/mycelia-ai-stack/credo_pilot_configurations/ragflow_dataset_metadata_config.json`

## Workflow 1: Dataset Settings (Language & Schema)

1.  **Prepare Configuration**: 
    - Use the JSON template provided in the resources.
    - Ensure `metadata_generation_settings` use the keys: `key`, `type` (string/list/number/time), `description`, and optionally `enum`.

2.  **Execute Update**:
    - Command: `python3 /root/.gemini/skills/ragflow-dataset-config/scripts/update_dataset.py "<Dataset Name>" <config.json>`

## Workflow 2: Document-Level Metadata

1.  **Single Update**:
    - Command: `python3 /root/.gemini/skills/ragflow-dataset-config/scripts/update_document_metadata.py --dataset "<DS Name>" --doc "<Doc Name>" --meta '{"key": "value"}'`

2.  **Bulk Update**:
    - Prepare a JSON file (e.g., `metadata_update.json`) with the following format:
    ```json
    [
      {
        "dataset": "My Dataset Name",
        "document": "Filename.pdf",
        "metadata": {
          "category": "Technical",
          "author": "John Doe"
        }
      }
    ]
    ```
    - Execute Command: `python3 /root/.gemini/skills/ragflow-dataset-config/scripts/update_document_metadata.py --file metadata_update.json`

## Verification
- For Dataset Settings: Check "Dataset Settings" in the RagFlow UI.
- For Document Metadata: Use the `list_ragflow_docs.py` script or check the document details in the RagFlow UI.

## Troubleshooting: Metadata Generation Blocked

If metadata settings are configured but results show "0" in the UI after parsing:

1.  **Check for Connection Errors**: Check logs (`docker logs ragflow-ragflow-cpu-1`) for `401 Unauthorized` errors. These are often caused by a broken Langfuse integration interrupting the save process. Disable Langfuse (see `langfuse-ragflow-connection` skill).
2.  **Verify Database Flag**: Ensure the `enable_metadata` flag is set to `true` in the `knowledgebase` table.
    - **Database**: `rag_flow`
    - **Surgical Update**:
      ```bash
      # Run inside a python script or via mysql client
      UPDATE knowledgebase SET parser_config = JSON_SET(parser_config, '$.enable_metadata', true) WHERE name = 'Your Dataset Name';
      ```

## Technical Note
This skill performs two distinct API calls:
- `PUT /api/v1/datasets/<id>` for general settings (Language).
- `PUT /api/v1/datasets/<id>/metadata/config` for the schema definitions.
- **Note**: The API may successfully update the schema but fail to enable the feature flag. Use the surgical SQL update above if re-parsing does not trigger generation.
