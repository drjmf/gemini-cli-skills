---
name: langfuse-installation
description: Guide for installing and configuring Langfuse with Redis and ClickHouse on Akash. Use when setting up or repairing a Langfuse installation.
---

# Langfuse Installation & Configuration

This skill provides a step-by-step guide for installing and configuring Langfuse in a self-contained environment, specifically optimized for Akash Network deployments.

## Prerequisites

- **PostgreSQL**: Database `langfuse` and user `langfuse` must exist.
- **ClickHouse**: Must be running and accessible on port 8123.
- **Node.js**: Recommended version 24+.

## Step 1: Redis Setup (Self-Contained)

Langfuse requires Redis for its background worker. To maintain framework isolation:

1.  **Install Redis**: `apt-get install -y redis-server`
2.  **Move Binaries**: Copy `redis-server` and `redis-cli` to a local `redis/` directory within the service path.
3.  **Start Redis**:
    ```bash
    ./redis/redis-server --requirepass YOUR_PASSWORD --port 6379 --daemonize yes
    ```

## Step 2: Environment Configuration

Create or update the `.env` file in the source directory with the following mandatory variables:

- `DATABASE_URL`: PostgreSQL connection string.
- `DIRECT_URL`: Same as `DATABASE_URL` (required for Prisma migrations).
- `NEXTAUTH_URL`: The public URL of your Langfuse instance.
- `NEXTAUTH_SECRET`: Generate via `openssl rand -base64 32`.
- `SALT`: Generate via `openssl rand -base64 32`.
- `ENCRYPTION_KEY`: 64-character hex string.
- `REDIS_HOST`, `REDIS_PORT`, `REDIS_AUTH`: Redis connection details.
- `CLICKHOUSE_URL`, `CLICKHOUSE_USER`, `CLICKHOUSE_PASSWORD`: ClickHouse connection details.
- `LANGFUSE_S3_EVENT_UPLOAD_BUCKET`: Set to a placeholder value (e.g., "unused") if not using S3.

## Step 3: Database Migrations

Run Prisma migrations using the `db:deploy` command to avoid shadow database requirements:

```bash
export PATH="/path/to/nodejs/bin:$PATH"
turbo run db:deploy
```

## Step 4: Standalone Web Server Setup

Next.js standalone mode is preferred for performance. 

1.  **Link Static Assets**: Manually link `public` and `.next/static` to the `standalone/web/` directory:
    ```bash
    ln -s ../../public .next/standalone/web/public
    ln -s ../../.next/static .next/standalone/web/.next/static
    ```
2.  **Startup Script**: Create a wrapper (`start-web.sh`) that sources `.env` and executes `node web/server.js`.

## Step 5: Worker Process Setup

The worker process handles background tasks.

1.  **Startup Script**: Create a wrapper (`start-worker.sh`) that sources `.env` and executes `node dist/index.js` from the `worker/` directory.

## Step 6: Nginx Routing

Configure Nginx to proxy traffic and serve static assets directly:

```nginx
location /_next/static {
    alias /path/to/source/web/.next/static;
}

location / {
    proxy_pass http://127.0.0.1:3000;
    # ... standard proxy headers
}
```
