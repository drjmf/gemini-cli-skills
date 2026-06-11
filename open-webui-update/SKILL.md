---
name: open-webui-update
description: Updates OpenWebUI to a specified or latest version while persisting configuration in the mycelia-ai-stack.
---

# OpenWebUI Update

This skill automates the process of updating OpenWebUI within the `mycelia-ai-stack` environment.

## Workflow

1.  **Preparation**:
    - Locate the OpenWebUI directory (usually `/opt/mycelia-ai-stack/openwebui`).
    - Identify the current version in `docker-compose.yml`.

2.  **Backup**:
    - Create a timestamped backup of the `openwebui` directory:
      `cp -r /opt/mycelia-ai-stack/openwebui /opt/mycelia-ai-stack/openwebui_backup_$(date +%F_%H%M)`

3.  **Update Script**:
    - Determine the target version (check GitHub for the latest tag if not specified).
    - Update the version string in `/opt/mycelia-ai-stack/scripts/09-openwebui.sh` using `sed`.

4.  **Execute Update**:
    - Run the update script:
      `bash /opt/mycelia-ai-stack/scripts/09-openwebui.sh`

5.  **Verification**:
    - Confirm the container is running the new version:
      `docker inspect openwebui --format '{{.Config.Image}}'`
    - Verify connectivity via the mapped port (usually `8802`).
