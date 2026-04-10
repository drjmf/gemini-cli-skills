---
name: akash-services-status
description: Checks the status of all configured services and applications running on the Akash server, including PostgreSQL, Open WebUI, pgAdmin, and others.
---
# Akash Services Status

This skill provides a streamlined way to check the operational status of all services running on the Akash server.

## Checking Status

To check the status of all services, execute the bundled script:

```bash
bash scripts/check_status.sh
```

This script will:
1. Iterate through all `manager-*.sh` scripts in `/mnt/data/system/services/` and `/mnt/data/system/applications/`.
2. Run the `status` command for each service, showing if it is running or stopped.
3. Check and report the number of zombie processes currently in the system.

You can use the output of this script to quickly inform the user about the system's state.