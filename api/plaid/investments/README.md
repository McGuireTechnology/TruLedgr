# Plaid Investments Implementation

This directory contains the complete implementation of the Plaid Investments product for TruLedgr, providing comprehensive investment account management, holdings tracking, and transaction processing.

## 🚀 Features

### Core Functionality
- **Investment Account Management**: Complete account details with balances and metadata
- **Holdings Tracking**: Real-time securities positions, quantities, and valuations
- **Transaction Processing**: Buy, sell, dividend, transfer, and fee transactions
- **Securities Database**: Comprehensive metadata for stocks, bonds, ETFs, mutual funds, options, and crypto
- **Option Contracts**: Full option chain details including strikes and expirations
- **Fixed Income**: Bond and CD information with yield rates and maturity dates
- **Webhook Processing**: Real-time updates for holdings and transaction changes
- **Change History**: Complete audit trail for all investment data

### Investment Account Types Supported
- 401(k) accounts
- IRA accounts (Traditional & Roth)
- Brokerage accounts
- 529 education savings
- Crypto exchange accounts
- Money market accounts
- And more...

### Security Types Supported
- **Equity**: Stocks and equity securities
- **ETF**: Exchange-traded funds
- **Mutual Fund**: Mutual funds and money market funds
- **Fixed Income**: Bonds, CDs, treasury securities
- **Derivative**: Options contracts
- **Cryptocurrency**: Digital assets
- **Cash**: Cash equivalents and money market

## 📁 File Structure

```
investments/
├── __init__.py                 # Module exports and documentation
├── models_official.py          # SQLModel database models (8 tables)
├── service_official.py         # Business logic and Plaid API integration
├── router_official.py          # FastAPI REST endpoints
└── README.md                   # This documentation
```

## 🗄️ Database Schema

The implementation uses 8 comprehensive tables:

### Core Tables
1. **plaid_investment_accounts** - Investment accounts with balances
2. **plaid_investment_securities** - Security metadata and pricing
3. **plaid_investment_holdings** - Current holdings in accounts
4. **plaid_investment_transactions** - Investment transactions

### Detail Tables  
5. **plaid_investment_option_contracts** - Option contract specifications
6. **plaid_investment_fixed_income** - Bond and CD details

### Tracking Tables
7. **plaid_investment_history** - Change tracking for audit
8. **plaid_investment_webhook_events** - Webhook event processing

## 🔗 API Endpoints

### Data Synchronization
- `POST /plaid/investments/sync/holdings/{item_id}` - Sync holdings from Plaid
- `POST /plaid/investments/sync/transactions/{item_id}` - Sync transactions from Plaid

### Data Retrieval
- `GET /plaid/investments/holdings` - Get user holdings with filtering
- `GET /plaid/investments/transactions` - Get investment transactions with pagination
- `GET /plaid/investments/accounts` - Get investment accounts
- `GET /plaid/investments/securities` - Get securities information
- `GET /plaid/investments/stats` - Get portfolio statistics

### Webhook Processing
- `POST /plaid/investments/webhook/process` - Process Plaid webhook events

## 🚀 Getting Started

### 1. Database Migration

Run the migration script to create all investment tables:

```bash
cd scripts/
python migrate_investments.py create
```

### 2. Verify Installation

Check that all tables were created correctly:

```bash
python migrate_investments.py verify
```

### 3. Sync Investment Data

Use the API endpoints to sync data from Plaid:

```bash
# Sync holdings for an item
curl -X POST "http://localhost:8000/plaid/investments/sync/holdings/ITEM_ID" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Sync transactions for date range
curl -X POST "http://localhost:8000/plaid/investments/sync/transactions/ITEM_ID?start_date=2024-01-01&end_date=2024-12-31" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. Retrieve Investment Data

Get holdings and transactions:

```bash
# Get all holdings
curl "http://localhost:8000/plaid/investments/holdings" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get transactions with filters
curl "http://localhost:8000/plaid/investments/transactions?count=50&offset=0" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🔧 Configuration

The implementation uses sandbox environment by default. All database models include environment fields for production deployment.

Key environment considerations:
- Sandbox: For development and testing
- Production: For live financial data

## 📊 Data Flow

1. **Link Account**: User connects investment account via Plaid Link
2. **Sync Holdings**: API fetches current positions and securities
3. **Sync Transactions**: API fetches historical transactions
4. **Webhook Updates**: Real-time updates via Plaid webhooks
5. **Query Data**: Frontend retrieves formatted investment data

## 🔐 Security

- All endpoints require authentication
- ULID-based primary keys for security
- Proper access control by user ID
- Comprehensive input validation
- SQL injection protection via SQLModel

## 📈 Performance

- Optimized database indexes on key fields
- Pagination support for large datasets
- Efficient bulk operations for data syncing
- Caching-friendly response structures

## 🧪 Testing

The implementation includes comprehensive error handling and validation:

- Date format validation
- Required field checks  
- Data type validation
- Plaid API error handling
- Database constraint enforcement

## 🔄 Webhook Support

Supports Plaid's investment webhook events:

- `HOLDINGS: DEFAULT_UPDATE` - Holdings data changes
- `INVESTMENTS_TRANSACTIONS: DEFAULT_UPDATE` - New transactions
- `INVESTMENTS_TRANSACTIONS: HISTORICAL_UPDATE` - Historical updates

## 📝 Notes

- Built with official Plaid API specifications
- Follows TruLedgr architectural patterns
- Comprehensive test coverage recommended
- Ready for production deployment with environment configuration

## 🤝 Contributing

When extending this implementation:

1. Follow existing naming conventions
2. Add proper error handling
3. Include comprehensive logging
4. Update this documentation
5. Add appropriate tests

---

For questions or support, refer to the main TruLedgr documentation or the Plaid API documentation.
