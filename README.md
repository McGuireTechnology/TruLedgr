# TruLedgr

A modern, secure Personal Finance Application built with FastAPI and Vue.js, designed to help users track expenses, manage budgets, and gain insights into their financial health.

## 🚀 Features

### 💰 Personal Finance Management

- **Expense Tracking**: Record and categorize daily expenses
- **Budget Management**: Set and monitor spending limits by category
- **Financial Insights**: Interactive charts and spending analytics
- **Transaction History**: Comprehensive view of all financial activities
- **Category Management**: Flexible expense categorization system

### 🔒 Security & Privacy

- **Secure Authentication**: Session-based auth with TOTP support
- **Data Protection**: Encrypted storage of sensitive financial data
- **Privacy First**: Your financial data stays private and secure
- **Multi-user Support**: Individual accounts with role-based access

### 🛠 Technical Excellence

- **Modern Tech Stack**: FastAPI backend with Vue.js 3 + TypeScript frontend
- **Real-time Dashboard**: Live updates and interactive data visualization
- **Database Support**: SQLite (development) and PostgreSQL (production)
- **Developer Experience**: Hot reload, comprehensive testing, CI/CD ready
- **Production Ready**: Docker deployment and environment configuration## � Documentation

For comprehensive guides and API documentation, visit:

**📖 [docs.truledgr.app](https://docs.truledgr.app)**

### Quick Links

- **👥 User Guide**: Complete guide for using TruLedgr
- **🛠️ Developer Guide**: Technical documentation for contributors
- **🤝 Contributing**: How to contribute to the project
- **📊 API Reference**: Complete API documentation

## �📋 Prerequisites

- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Git** for version control

## 🛠 Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/McGuireTechnology/truledgr.git
cd truledgr
```

### 2. Install Dependencies

```bash
# Install all dependencies (Python + Node.js)
npm run install:all
```

### 3. Environment Configuration

```bash
# Copy environment template
cp .env.local.example .env

# Edit .env with your configuration
# Key settings: DATABASE_URL, SECRET_KEY, etc.
```

### 4. Start Development

```bash
# Start all development servers
npm run dev

# Or start individual services:
npm run dev:backend    # FastAPI on http://localhost:8000
npm run dev:dashboard  # Vue.js on http://localhost:5173
npm run dev:landing    # Landing page on http://localhost:5174
```

## 🏗 Project Structure

```bash
truledgr/
├── api/                    # FastAPI backend
│   ├── authentication/    # User authentication & security
│   ├── authorization/     # Role-based access control
│   ├── users/            # User account management
│   ├── groups/           # Household/family group management
│   ├── items/            # Financial transactions & entries
│   └── db/               # Database models and utilities
├── dashboard/            # Vue.js financial dashboard
│   ├── components/       # UI components (charts, forms, etc.)
│   ├── domains/          # Finance-specific modules
│   ├── stores/           # Financial data state management
│   └── views/            # Dashboard pages (budget, expenses, etc.)
├── frontend/             # Additional frontend applications
├── scripts/              # Database migration and utility scripts
├── tests/                # Comprehensive test suite
└── docs/                 # Documentation
```

## 🔧 Development

### Available Scripts

```bash
# Development
npm run dev                # Start all development servers
npm run dev:backend        # Backend only (FastAPI)
npm run dev:dashboard      # Dashboard only (Vue.js)
npm run dev:landing        # Landing page only

# Building
npm run build              # Build all applications
npm run build:dashboard    # Build dashboard only
npm run build:landing      # Build landing page only

# Testing
npm run test               # Run all tests
npm run test:backend       # Backend tests only
npm run test:frontend      # Frontend tests only

# Code Quality
npm run lint               # Lint all code
npm run format             # Format all code
npm run type-check         # TypeScript type checking

# Utilities
npm run clean              # Clean build artifacts
npm run migrate            # Run database migrations
```

### Backend Development

The FastAPI backend is organized into financial modules:

- **Authentication**: Secure user authentication and session management
- **Authorization**: Role-based access control for family/household accounts
- **Users**: Personal account management and preferences
- **Groups**: Household/family financial group management
- **Items**: Financial transactions, expenses, and income tracking

### Frontend Development

The Vue.js dashboard provides a comprehensive financial interface:

- **Modern Vue 3**: Composition API with TypeScript for type safety
- **Tailwind CSS**: Clean, responsive financial UI components
- **Pinia**: Centralized financial data state management
- **Vue Router**: Navigation between budget, expenses, and analytics views
- **Chart.js**: Financial data visualization and spending insights

## 🗄 Database

### SQLite (Development)

- Automatic setup with sample data
- Located at `./dev.db`

### PostgreSQL (Production)

```bash
# Install PostgreSQL dependencies
pip install asyncpg psycopg2-binary

# Update DATABASE_URL in .env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/truledgr
```

## 🔐 Authentication & Security

### Financial Data Protection

- **Encrypted Storage**: All financial data is securely encrypted
- **Session Management**: Secure session handling with configurable expiration
- **Privacy Controls**: Individual user data isolation
- **Audit Trail**: Transaction history and data access logging

### Authentication Features

- **Secure Login**: Argon2 password hashing with bcrypt fallback
- **Two-Factor Auth**: TOTP support for additional security
- **Account Recovery**: Secure password reset and backup codes
- **Family Access**: Controlled sharing within household groups

## 🚀 Deployment

### Environment Configuration

Create environment-specific files:

- `.env.dev` - Development
- `.env.stage` - Staging  
- `.env.prod` - Production

### Docker Deployment

```bash
# Build and deploy
./scripts/build.sh
./scripts/deploy.sh
```

### Manual Deployment

```bash
# Build frontend applications
npm run build

# Install Python dependencies
pip install -e .

# Run database migrations
python scripts/migrate_complete_schema.py

# Start the application
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

## 🧪 Testing

### Backend Tests

```bash
# Run all backend tests
python -m pytest tests/

# Run specific test modules
python -m pytest tests/test_authentication.py
python -m pytest tests/test_users.py
```

### Frontend Tests

```bash
# Run frontend tests
npm run test:frontend
```

### End-to-End Tests

```bash
# Run E2E tests
npm run test:e2e
```

## 📚 API Documentation

When running in development mode, API documentation is available at:

- **Swagger UI**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>
- **OpenAPI JSON**: <http://localhost:8000/openapi.json>

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use TypeScript for frontend development
- Write tests for financial calculations and data handling
- Update documentation for new financial features
- Run linting and formatting before committing
- Test financial calculations with edge cases

## 📊 Financial Features Roadmap

### Current Features

- ✅ User authentication and security
- ✅ Basic transaction tracking
- ✅ Dashboard with data visualization
- ✅ Multi-user support with groups

### Planned Features

- 📈 Advanced budgeting tools
- 💳 Bank account integration
- 📱 Mobile-responsive design
- 🏷️ Advanced categorization with tags
- 📊 Financial goal tracking
- 💸 Bill reminders and recurring transactions
- 📑 Financial report generation

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the `/docs` folder for detailed guides
- **Issues**: Report bugs and request features via GitHub Issues
- **Discussions**: Join community discussions on GitHub Discussions

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Vue.js](https://vuejs.org/) - Progressive JavaScript framework
- [SQLModel](https://sqlmodel.tiangolo.com/) - SQL databases with Python
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework
