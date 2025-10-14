# API Reference

Complete API documentation for the TruLedgr backend service.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://api.truledgr.app`

## Authentication

All API endpoints (except public health checks) require authentication via OAuth2 access tokens.

```http
Authorization: Bearer <access_token>
```

## API Documentation

TruLedgr uses FastAPI's automatic OpenAPI documentation:

- **Interactive Docs**: `/docs` - Swagger UI for testing endpoints
- **ReDoc**: `/redoc` - Alternative documentation interface
- **OpenAPI Schema**: `/openapi.json` - Machine-readable API specification

## Quick Reference

<div class="grid cards" markdown>

-   :material-routes: [__Endpoints__](endpoints.md)
    
    ---
    
    Complete list of available API endpoints

-   :material-code-json: [__Models__](models.md)
    
    ---
    
    Request/response schemas and data models

-   :material-key: [__Authentication__](authentication.md)
    
    ---
    
    OAuth2 flows and token management

</div>

## Common Response Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Missing or invalid token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 500 | Server Error | Internal server error |

## Rate Limiting

API requests are rate-limited to ensure fair usage:

- **Authenticated**: 1000 requests per hour
- **Unauthenticated**: 100 requests per hour

Rate limit headers are included in all responses:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1633024800
```
