"""FastAPI dependencies for TruLedgr API.

These dependencies are used via Depends() in routers to inject:
- Database sessions and Unit of Work
- Current authenticated user
- Authorization checks
- Pagination parameters
"""
