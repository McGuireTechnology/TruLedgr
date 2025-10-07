# API Architecture

## FastAPI Backend

The TruLedgr API is built with FastAPI, providing high-performance async endpoints with automatic OpenAPI documentation.

## Core Endpoints

### Health and Status
- `GET /` - Root endpoint with welcome message
- `GET /health` - Health check endpoint

### Authentication
- `POST /auth/login` - OAuth2 login
- `POST /auth/logout` - User logout
- `GET /auth/me` - Current user info

### Financial Data (Planned)
- `GET /accounts` - List user accounts
- `POST /accounts` - Create new account
- `GET /transactions` - List transactions
- `POST /transactions` - Create transaction
- `GET /reports/monthly` - Monthly reports

## API Design Principles

- **RESTful**: Standard HTTP methods and status codes
- **Async**: All database operations use async/await
- **Validated**: Pydantic models for request/response validation
- **Documented**: Automatic OpenAPI/Swagger documentation
- **Versioned**: API versioning for backward compatibility

## Data Models

### Core Financial Models (Planned)
```python
class Account(BaseModel):
    id: UUID
    name: str
    account_type: AccountType
    balance: Decimal
    created_at: datetime

class Transaction(BaseModel):
    id: UUID
    account_id: UUID
    amount: Decimal
    description: str
    date: date
    category: str
```

## Development Server

```bash
cd truledgr
poetry run uvicorn truledgr.main:app --reload
```

- API: `http://localhost:8000`
- Documentation: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Error Handling

The API uses standard HTTP status codes and returns consistent error responses:

```json
{
  "detail": "Error message",
  "error_code": "SPECIFIC_ERROR_CODE"
}
```

## Authentication

Supports OAuth2 with multiple providers:
- Google
- Microsoft
- GitHub
- Apple

JWT tokens are used for API authentication after initial OAuth2 flow.
