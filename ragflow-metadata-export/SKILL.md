# RagFlow Metadata Export Skill

This skill allows you to export all document names and their current metadata fields from RagFlow datasets into a JSON file for easy editing and bulk updating.

## Available Resources

- **Export Script**: `/root/.gemini/skills/ragflow-metadata-export/scripts/export_metadata.py`
- **Default Export Path**: `/opt/mycelia-ai-stack/scripts/ragflow_metadata_export.json`

## Workflow: Exporting Metadata

1.  **Export All Metadata**:
    - Command: `python3 /root/.gemini/skills/ragflow-metadata-export/scripts/export_metadata.py`

2.  **Export with Dataset Prefix (e.g., "en")**:
    - Command: `python3 /root/.gemini/skills/ragflow-metadata-export/scripts/export_metadata.py --prefix "en"`

3.  **Export to Specific File**:
    - Command: `python3 /root/.gemini/skills/ragflow-metadata-export/scripts/export_metadata.py --output "/path/to/your/file.json"`

## JSON Format
The exported JSON follows this structure:
```json
[
  {
    "dataset_name": "...",
    "dataset_id": "...",
    "document_name": "...",
    "document_id": "...",
    "metadata": {
      "key": "value",
      ...
    }
  }
]
```

## Bulk Updating After Export
After editing the exported JSON file, you can push the changes back to RagFlow using the `bulk_update_metadata.py` script:
- Command: `python3 /opt/mycelia-ai-stack/scripts/bulk_update_metadata.py /opt/mycelia-ai-stack/scripts/ragflow_metadata_export.json`

## Troubleshooting
- **API Key**: Ensure `RAGFLOW_API_KEY` is present in `/opt/mycelia-ai-stack/.secrets`.
- **Pagination**: The script handles up to 100 datasets and correctly paginates through documents within each dataset.
