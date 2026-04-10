#!/bin/bash
# repair_langflow_db.sh - Automated diagnostic and repair for Langflow migration issues

SERVICE_DIR="/mnt/data/system/services/langflow"
LOG_FILE="$SERVICE_DIR/langflow.log"
DB_NAME="langflow"
DB_USER="postgres"
PGPASSWORD="22ummel22"
export PGPASSWORD

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# 1. Diagnostic
if ! grep -q "mismatch between the models and the database" "$LOG_FILE"; then
    log "No mismatch error found in $LOG_FILE. Checking if service is running..."
    if ! netstat -tulnp | grep -q 7860; then
        log "Service is not running on 7860. Proceeding with safety check."
    else
        log "Service appears to be running on 7860. No repair needed."
        exit 0
    fi
fi

# 2. Safety Backup
BACKUP_PATH="$SERVICE_DIR/langflow_emergency_backup_$(date +%Y%m%d_%H%M%S).sql"
log "Creating emergency database backup at $BACKUP_PATH..."
if pg_dump -h localhost -U "$DB_USER" -d "$DB_NAME" > "$BACKUP_PATH"; then
    log "Backup SUCCESS."
else
    log "Backup FAILED. Aborting repair for safety."
    exit 1
fi

# 3. Attempt Standard Repair
log "Attempting standard langflow migration --fix..."
cd "$SERVICE_DIR" && source venv/bin/activate
if echo "y" | langflow migration --fix; then
    log "Standard fix SUCCESS."
else
    log "Standard fix FAILED (likely 'Ambiguous walk'). Attempting manual comment sync..."
    
    # 4. Manual Comment Sync (the 'julia-method')
    psql -h localhost -U "$DB_USER" -d "$DB_NAME" -c "COMMENT ON COLUMN flow.name IS 'Name of the flow (e.g., RAG Bot).';"
    psql -h localhost -U "$DB_USER" -d "$DB_NAME" -c "COMMENT ON COLUMN flow.description IS 'User-provided summary of the flow.';"
    psql -h localhost -U "$DB_USER" -d "$DB_NAME" -c "COMMENT ON COLUMN flow.data IS 'Visual node-and-edge graph data.';"
    psql -h localhost -U "$DB_USER" -d "$DB_NAME" -c "COMMENT ON COLUMN flow.id IS 'Unique identifier for the flow.';"
    
    log "Manual column comments applied. Clearing migration history to force re-sync..."
    psql -h localhost -U "$DB_USER" -d "$DB_NAME" -c "TRUNCATE TABLE alembic_version;"
    psql -h localhost -U "$DB_USER" -d "$DB_NAME" -c "INSERT INTO alembic_version (version_num) VALUES ('59a272d6669a');"
fi

# 5. Restart
log "Restarting Langflow service..."
"$SERVICE_DIR/manager-langflow.sh" stop
"$SERVICE_DIR/manager-langflow.sh" start
sleep 5

if netstat -tulnp | grep -q 7860; then
    log "SUCCESS: Langflow is now running on port 7860."
else
    log "FAILURE: Langflow still not running. Check $LOG_FILE for details."
    exit 1
fi
