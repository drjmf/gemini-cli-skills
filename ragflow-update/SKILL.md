---
name: ragflow-update
description: Updates RAGFlow to the latest version while persisting configuration in the mycelia-ai-stack.
---

# RAGFlow Update

This skill automates the process of updating RAGFlow within the `mycelia-ai-stack` environment.

## Workflow

1.  **Preparation**:
    - Locate the RAGFlow directory (usually `/opt/mycelia-ai-stack/ragflow`).
    - Verify the `.secrets` file exists in `/opt/mycelia-ai-stack/.secrets`.

2.  **Backup**:
    - Create a timestamped backup of the `ragflow` directory:
      `cp -r /opt/mycelia-ai-stack/ragflow /opt/mycelia-ai-stack/ragflow_backup_$(date +%F_%H%M)`

3.  **Download Updates**:
    - Pull the latest RAGFlow image:
      `docker pull infiniflow/ragflow:latest`

4.  **Execute Update Script**:
    - Run the provided installation script:
      `bash /opt/mycelia-ai-stack/scripts/12-ragflow.sh`
    - This script fetches official configs, updates the `.env` from secrets, and restarts services.

5.  **Verification**:
    - Check the running version:
      `docker exec ragflow-ragflow-cpu-1 cat /ragflow/VERSION`
    - Compare the new `.env` with the backup to ensure persistence.
