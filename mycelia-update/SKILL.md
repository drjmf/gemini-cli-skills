---
name: mycelia-update
description: Updates services in the Mycelia AI Stack while ensuring data persistence and configuration reuse. Use when the user requests updates for any service (RagFlow, Open WebUI, Langfuse, Postgres, etc.) within the /opt/mycelia-ai-stack environment.
---

# Mycelia AI Stack Update Guide

This skill ensures that Mycelia AI services are updated safely without losing data or configurations.

## Core Principles

1.  **Persistence First**: NEVER use 'docker compose down --volumes'. Always preserve volumes.
2.  **Secret Synchronization**: Always source credentials from /opt/mycelia-ai-stack/.secrets.
3.  **Service Isolation**: Update one service at a time.
4.  **Major Version Safety**: For major version jumps (e.g., Postgres 16 -> 18), check for directory structure changes.

## Workflow

### 1. Identify Target
- Determine the service and desired version.
- Verify the management script in /opt/mycelia-ai-stack/scripts/.

### 2. Update Management Script
- Use sed to update the image tag in the corresponding script.

### 3. Execute Update
- Run the management script with the 'create' command.
- This command stops the old container and replaces it while preserving volumes.

### 4. Verification
- Confirm the new version: 'docker inspect <container_name> --format {{.Config.Image}}'
- Check logs: 'docker logs <container_name> --tail 50'

