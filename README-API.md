# ⚡ TruLedgr API

**High-performance FastAPI backend powering the TruLedgr financial platform**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg?style=flat-square)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?style=flat-square)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791.svg?style=flat-square)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7.0+-DC382D.svg?style=flat-square)](https://redis.io)

> 🏦 **Enterprise-grade financial API** with OAuth2 authentication, real-time transaction processing, and comprehensive account management.

## 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/mcguiretechnology/truledgr-api.git
cd truledgr-api

# Install dependencies
pip install -r requirements.txt

# Set up database
alembic upgrade head

# Start development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**🌐 API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)

## ✨ Key Features

- **🔐 OAuth2 + JWT Authentication** with role-based access control
- **💳 Multi-Bank Integration** supporting 12,000+ financial institutions
- **⚡ Real-Time Processing** with WebSocket support for live updates
- **📊 Advanced Analytics** with transaction categorization and insights
- **🛡️ Enterprise Security** with audit logging and data encryption
- **📚 Interactive Docs** with OpenAPI/Swagger specification

## 🏗️ Tech Stack

- **Framework:** FastAPI with async/await support
- **Database:** PostgreSQL with SQLAlchemy ORM
- **Cache:** Redis for session management and real-time data
- **Auth:** OAuth2 with JWT tokens and refresh token rotation
- **Validation:** Pydantic models with automatic validation
- **Migration:** Alembic for database schema management

## 🔧 Configuration

```bash
# Environment variables
cp .env.example .env

# Required settings
DATABASE_URL=postgresql://user:pass@localhost/truledgr
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key-here
PLAID_CLIENT_ID=your-plaid-client-id
PLAID_SECRET=your-plaid-secret
```

## 📈 Performance

- **⚡ Sub-100ms response times** for most endpoints
- **🔄 Async processing** for I/O-bound operations
- **📊 Built-in monitoring** with Prometheus metrics
- **🚀 Auto-scaling ready** with stateless design

## 🧪 Testing

```bash
# Run test suite
pytest

# Coverage report
pytest --cov=app --cov-report=html

# Load testing
locust -f tests/load_test.py
```

## 📖 Documentation

- **[API Reference](https://api.truledgr.app/docs)** - Interactive Swagger docs
- **[Development Guide](./docs/development.md)** - Setup and contribution guide
- **[Architecture](./docs/architecture.md)** - System design and patterns
- **[Deployment](./docs/deployment.md)** - Production deployment guide

---

**Part of the [TruLedgr Platform](https://github.com/mcguiretechnology/truledgr) | Built by [McGuire Technology](https://mcguire.technology)**
