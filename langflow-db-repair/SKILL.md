---
name: langflow-db-repair
description: Diagnostics and automated repair for Langflow database migration mismatches and Alembic "Ambiguous walk" errors. Use when Langflow fails to start with "mismatch between the models and the database" or when migration fixes fail.
---

# Langflow Database Repair

This skill handles the common "Database Mismatch" crash in Langflow caused by schema/model divergence (often involving column comments).

## Common Symptoms

- Langflow process starts but immediately exits.
- `langflow.log` contains: `RuntimeError: There's a mismatch between the models and the database.`
- `langflow migration --fix` fails with `alembic.script.revision.RevisionError: Ambiguous walk`.

## Workflows

### 1. Automated Repair
The skill includes a bundled script that automates the safety backup, the standard fix, and the manual "Julia-method" sync if needed.

```bash
bash scripts/repair_langflow_db.sh
```

### 2. Manual Diagnostics
If the script is not used, follow these steps:

1.  **Check Alembic Heads**: Identify if multiple heads exist.
    ```bash
    cd /mnt/data/system/services/langflow && source venv/bin/activate
    cd venv/lib/python3.12/site-packages/langflow && alembic -c alembic.ini heads
    ```
2.  **Verify DB Version**:
    ```bash
    psql -h localhost -U postgres -d langflow -c "SELECT * FROM alembic_version;"
    ```
3.  **Manual Sync (The Julia Method)**: If comments are the only diff, apply them manually:
    ```sql
    COMMENT ON COLUMN flow.name IS 'Name of the flow (e.g., RAG Bot).';
    COMMENT ON COLUMN flow.description IS 'User-provided summary of the flow.';
    COMMENT ON COLUMN flow.data IS 'Visual node-and-edge graph data.';
    COMMENT ON COLUMN flow.id IS 'Unique identifier for the flow.';
    ```

## Resources

- **scripts/repair_langflow_db.sh**: The primary automation script.
