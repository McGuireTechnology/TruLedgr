# Multi-Host SaaS Migration Strategy

## 🎯 Overview

This document outlines strategies for running database migrations safely in a multi-host SaaS environment where multiple application instances may start simultaneously.

## ⚠️ The Problem

In a multi-host environment:
- Multiple app instances start at the same time (e.g., after deployment)
- Each instance may try to run migrations simultaneously
- Race conditions can cause:
  - Duplicate migration attempts
  - Deadlocks
  - Data corruption
  - Failed deployments

**Goal:** Ensure migrations run exactly **once**, regardless of instance count.

---

## 🏆 Strategy Comparison

| Strategy | Pros | Cons | Recommended For |
|----------|------|------|-----------------|
| **1. Separate Migration Job** | ✅ Clean separation<br>✅ No race conditions<br>✅ Easy rollback | ⚠️ Requires platform support | **Production (Best)** |
| **2. Advisory Locks** | ✅ Robust<br>✅ Built into Postgres<br>✅ No external deps | ⚠️ PostgreSQL only<br>⚠️ Adds startup complexity | **Multi-host without job support** |
| **3. Distributed Lock (Redis)** | ✅ Works with any DB<br>✅ Fast | ⚠️ Requires Redis<br>⚠️ Additional dependency | **Cross-database environments** |
| **4. Leader Election** | ✅ Automatic failover | ⚠️ Complex<br>⚠️ Requires orchestrator | **Kubernetes with StatefulSets** |

---

## 📋 Implementation Details

### **Strategy 1: Separate Migration Job (Recommended)**

Run migrations as a distinct, single-instance job **before** application deployment.

#### DigitalOcean App Platform

```yaml
# .do/app.yaml
name: truledgr-api

# Migration job runs BEFORE app instances start
jobs:
  - name: db-migrate
    kind: PRE_DEPLOY
    dockerfile_path: Dockerfile
    source_dir: /
    run_command: |
      set -e
      echo "Running database migrations..."
      ./migrate.sh upgrade head
      echo "Migrations complete!"
    envs:
      - key: DATABASE_URL
        scope: RUN_TIME
        value: ${db.DATABASE_URL}

# App instances start AFTER migration completes
services:
  - name: api
    dockerfile_path: Dockerfile
    source_dir: /
    run_command: poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000
    instance_count: 3  # Safe: migrations already ran
    envs:
      - key: DATABASE_URL
        scope: RUN_TIME
        value: ${db.DATABASE_URL}
```

#### Kubernetes

```yaml
# migration-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: truledgr-migrate-{{ .Release.Revision }}
  labels:
    app: truledgr
    component: migration
spec:
  # Only one pod runs the migration
  completions: 1
  parallelism: 1
  backoffLimit: 3
  template:
    metadata:
      labels:
        app: truledgr-migrate
    spec:
      restartPolicy: OnFailure
      containers:
      - name: migrate
        image: registry.digitalocean.com/truledgr/api:{{ .Release.Tag }}
        command: ["./migrate.sh", "upgrade", "head"]
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-credentials
              key: url
---
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: truledgr-api
spec:
  replicas: 3
  template:
    spec:
      # Wait for migration job to complete
      initContainers:
      - name: wait-for-migration
        image: bitnami/kubectl:latest
        command:
        - kubectl
        - wait
        - --for=condition=complete
        - --timeout=300s
        - job/truledgr-migrate-{{ .Release.Revision }}
      containers:
      - name: api
        image: registry.digitalocean.com/truledgr/api:{{ .Release.Tag }}
        command: ["poetry", "run", "uvicorn", "api.main:app"]
```

#### Docker Compose (Development)

```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: truledgr
      POSTGRES_USER: truledgr
      POSTGRES_PASSWORD: dev-password

  # Migration service runs first
  migrate:
    build: .
    command: ./migrate.sh upgrade head
    depends_on:
      db:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql://truledgr:dev-password@db:5432/truledgr
    restart: on-failure

  # App services start after migration
  api-1:
    build: .
    command: poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000
    depends_on:
      migrate:
        condition: service_completed_successfully
    ports:
      - "8001:8000"

  api-2:
    build: .
    command: poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000
    depends_on:
      migrate:
        condition: service_completed_successfully
    ports:
      - "8002:8000"

  api-3:
    build: .
    command: poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000
    depends_on:
      migrate:
        condition: service_completed_successfully
    ports:
      - "8003:8000"
```

---

### **Strategy 2: PostgreSQL Advisory Locks**

Use built-in PostgreSQL locks when separate jobs aren't available.

#### Implementation

See `api/migrations/lock_manager.py` for full implementation.

**Usage in FastAPI:**

```python
# api/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run migrations on startup with locking."""
    import os
    from api.migrations.lock_manager import run_migrations_with_lock
    
    database_url = os.getenv("DATABASE_URL")
    if database_url and "postgresql" in database_url:
        # Convert to async URL
        async_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
        
        # This will wait if another instance is running migrations
        await run_migrations_with_lock(async_url)
    
    yield

app = FastAPI(lifespan=lifespan)
```

**How it works:**
1. Instance A acquires PostgreSQL advisory lock
2. Instance A runs migrations
3. Instances B, C, D wait for lock
4. Instance A releases lock
5. Instances B, C, D continue (no migrations needed)

---

### **Strategy 3: Redis Distributed Lock**

Use Redis for locking when not using PostgreSQL.

```python
# api/migrations/redis_lock.py
import asyncio
from redis.asyncio import Redis
from redis.asyncio.lock import Lock

async def run_migrations_with_redis_lock(redis_url: str):
    redis = Redis.from_url(redis_url)
    
    # Try to acquire lock for 5 minutes
    async with Lock(redis, "migration_lock", timeout=300, blocking_timeout=300):
        # Run migrations
        from alembic import command
        from alembic.config import Config
        
        alembic_cfg = Config("api/alembic.ini")
        command.upgrade(alembic_cfg, "head")
    
    await redis.close()
```

---

### **Strategy 4: Kubernetes Leader Election**

Use Kubernetes leader election for StatefulSets.

```python
# api/migrations/k8s_leader.py
import os

def is_leader() -> bool:
    """Check if this pod is the leader (first in StatefulSet)."""
    hostname = os.getenv("HOSTNAME", "")
    # In StatefulSet: truledgr-api-0, truledgr-api-1, etc.
    return hostname.endswith("-0")

# In startup:
if is_leader():
    run_migrations()
else:
    wait_for_migrations_to_complete()
```

---

## 🚀 Recommended Setup for TruLedgr

### Production (DigitalOcean)

```yaml
# .do/app.yaml - Use PRE_DEPLOY job
jobs:
  - name: db-migrate
    kind: PRE_DEPLOY
    run_command: ./migrate.sh upgrade head
    envs:
      - key: DATABASE_URL
        scope: RUN_TIME

services:
  - name: api
    instance_count: 3
    # Safe: migrations already completed
```

### Staging/Development

Use advisory locks in application startup:

```python
# api/main.py
from api.migrations.startup_integration import lifespan_with_migrations

app = FastAPI(lifespan=lifespan_with_migrations)
```

---

## ✅ Best Practices

1. **Always use separate migration jobs in production**
2. **Test migrations in staging with multiple instances**
3. **Set migration timeout (5 minutes recommended)**
4. **Log migration status clearly**
5. **Monitor migration duration**
6. **Have rollback plan (downgrade scripts)**
7. **Use database backups before migrations**
8. **Consider zero-downtime migrations for large tables**

---

## 🔍 Monitoring & Troubleshooting

### Check Migration Status

```bash
# Check current migration version
./migrate.sh current

# Check if migrations are running
kubectl get jobs | grep migrate

# View migration logs
kubectl logs job/truledgr-migrate-v0.1.1
```

### Common Issues

**Issue:** Migration timeout  
**Solution:** Increase timeout, check database locks

**Issue:** Multiple instances trying to migrate  
**Solution:** Verify advisory lock implementation, check logs

**Issue:** Migration stuck  
**Solution:** Check for table locks, restart migration job

---

## 📚 References

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [PostgreSQL Advisory Locks](https://www.postgresql.org/docs/current/explicit-locking.html#ADVISORY-LOCKS)
- [Kubernetes Jobs](https://kubernetes.io/docs/concepts/workloads/controllers/job/)
- [DigitalOcean App Platform Jobs](https://docs.digitalocean.com/products/app-platform/how-to/manage-jobs/)
