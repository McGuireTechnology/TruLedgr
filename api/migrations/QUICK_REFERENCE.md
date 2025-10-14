# Multi-Host Migration Quick Reference

## 🎯 TL;DR

**For TruLedgr Production (DigitalOcean):**
```yaml
# Use PRE_DEPLOY job in .do/app.yaml
jobs:
  - name: db-migrate
    kind: PRE_DEPLOY
    run_command: ./migrate.sh upgrade head
```

**For Development/Staging:**
```python
# Use advisory locks in api/main.py
from api.migrations.startup_integration import lifespan_with_migrations
app = FastAPI(lifespan=lifespan_with_migrations)
```

---

## 📋 Decision Matrix

Choose your strategy:

```
Are you using DigitalOcean/Kubernetes/similar?
├─ YES → Use PRE_DEPLOY job (Strategy 1) ✅ RECOMMENDED
└─ NO → Do you use PostgreSQL?
    ├─ YES → Use advisory locks (Strategy 2)
    ├─ NO (SQLite/MySQL) → Use Redis locks (Strategy 3)
    └─ Kubernetes only? → Use leader election (Strategy 4)
```

---

## 🚀 Implementation Checklist

### Production Setup (DigitalOcean)

- [ ] Create `.do/app.yaml` with PRE_DEPLOY job
- [ ] Test migration job in staging
- [ ] Set up database backup before migrations
- [ ] Configure migration timeout (5 min recommended)
- [ ] Add monitoring/alerts for migration failures
- [ ] Document rollback procedure

### Alternative: Advisory Locks

- [ ] Add `lock_manager.py` to project
- [ ] Update `api/main.py` with lifespan handler
- [ ] Test with multiple instances locally
- [ ] Verify timeout behavior
- [ ] Add logging for migration status

---

## 🧪 Testing Multi-Host Migrations

### Local Test with Docker Compose

```bash
# Start 3 app instances simultaneously
docker-compose up --scale api=3

# Check logs - only ONE should run migrations
docker-compose logs | grep "Running migrations"
```

### DigitalOcean Test

```bash
# Deploy with 3 instances
doctl apps update $APP_ID --spec .do/app.yaml

# Check migration job logs
doctl apps logs $APP_ID --type job --follow
```

---

## 🔧 Files Reference

| File | Purpose |
|------|---------|
| `MULTI_HOST_STRATEGY.md` | Complete strategy guide |
| `lock_manager.py` | PostgreSQL advisory lock implementation |
| `startup_integration.py` | FastAPI integration examples |
| `.do/app.yaml` | DigitalOcean deployment config |
| `migrate.sh` | Migration helper script |

---

## ⚠️ Common Pitfalls

1. **Not testing with multiple instances** → Always test with 2+ instances
2. **Missing timeout** → Set explicit timeout (5 minutes)
3. **No monitoring** → Add logging and alerts
4. **Forgetting SQLite doesn't support locks** → Use separate job or skip locks
5. **Race conditions** → Always use one of the four strategies

---

## 📞 Emergency Procedures

### Migration Stuck?

```bash
# Check PostgreSQL locks
SELECT * FROM pg_locks WHERE locktype = 'advisory';

# Release stuck advisory lock (emergency only!)
SELECT pg_advisory_unlock_all();

# Restart migration
./migrate.sh upgrade head
```

### Rollback Migration

```bash
# Check current version
./migrate.sh current

# Rollback one version
./migrate.sh downgrade -1

# Rollback to specific version
./migrate.sh downgrade <revision_id>
```

---

## 📚 Next Steps

1. Read `MULTI_HOST_STRATEGY.md` for detailed implementation
2. Choose strategy based on your deployment platform
3. Implement chosen strategy
4. Test with multiple instances
5. Set up monitoring and alerts
6. Document your specific deployment procedure
