# TruLedgr

A comprehensive multi-platform application suite with clean separation of concerns.

## 🏗️ Project Structure

```
truledgr/
├── api/                    # FastAPI Backend
│   ├── main.py            # FastAPI application
│   ├── requirements.txt   # Python dependencies
│   ├── runtime.txt        # Python version
│   ├── Procfile          # Process definitions
│   ├── start.sh          # Startup script
│   ├── .venv/            # Virtual environment
│   └── test_main.py      # API tests
├── dash/                  # Vue.js Frontend Dashboard
│   ├── src/              # Vue source code
│   ├── public/           # Static assets
│   ├── package.json      # Node dependencies
│   ├── vite.config.ts    # Vite configuration
│   └── dist/            # Built assets (generated)
├── docs/                 # Documentation
│   ├── mobile-integration.md
│   ├── frontend-deployment.md
│   └── domain-routing-fix.md
└── *.yaml               # Deployment configurations
```

## 🚀 Deployment Configurations

### Standard Digital Ocean Structure
Each component has its own `.do/app.yaml` deployment configuration:
- **`api/.do/app.yaml`**: API deployment → `api.truledgr.app`
- **`dash/.do/app.yaml`**: Frontend deployment → `dash.truledgr.app`

## 🔧 Development Setup

### Backend (API)
```bash
cd api
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Frontend (Dashboard)
```bash
cd dash
npm ci
npm run dev
```

## 📱 Platform Architecture

- **Backend API**: FastAPI (Python) - `api.truledgr.app`
- **Frontend Dashboard**: Vue.js + Vite (TypeScript) - `dash.truledgr.app`  
- **Mobile Apps**: iOS (Swift) + Android (Kotlin) integration guides
- **Database**: PostgreSQL (configured for production)
- **Authentication**: JWT-based with biometric support

## 🌐 Deployment

### Digital Ocean App Platform
Deploy each component separately for optimal performance and management:

1. **Deploy API**: 
   - Create App → GitHub → Select `/api` folder
   - Uses `api/.do/app.yaml` automatically  
   - Domain: `api.truledgr.app`

2. **Deploy Dashboard**:
   - Create App → GitHub → Select `/dash` folder  
   - Uses `dash/.do/app.yaml` automatically
   - Domain: `dash.truledgr.app`

## 📖 Documentation

- **Mobile Integration**: `docs/mobile-integration.md`
- **Frontend Deployment**: `docs/frontend-deployment.md`  
- **Domain Routing**: `docs/domain-routing-fix.md`

## 🔐 Security Features

- JWT authentication with refresh tokens
- CORS configuration for cross-domain requests
- Biometric authentication support (mobile)
- Secure environment variable handling

## 📈 Monitoring & Health

- Health check endpoints (`/health`)
- Logging and error tracking
- Performance monitoring ready
- Digital Ocean App Platform integration

## 🧪 Testing

```bash
# Backend tests
cd api
python -m pytest

# Frontend tests  
cd dash
npm run test:unit
npm run test:e2e
```

## Architecture Overview

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│                     │    │                     │    │                     │
│   Mobile Apps       │    │  Frontend Dashboard │    │    Backend API      │
│                     │    │                     │    │                     │
│  • iOS App          │◄──►│  Vue.js + Vite      │◄──►│   FastAPI + Python  │
│  • Android App      │    │  dash.truledgr.app  │    │  api.truledgr.app   │
│                     │    │                     │    │                     │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

## Project Structure

```
truledgr/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .do/                   # Digital Ocean App Platform configs
│   └── app.yaml          
├── frontend/              # Vue.js frontend application
│   ├── src/
│   │   ├── services/
│   │   │   └── api.ts    # API integration layer
│   │   └── components/
│   │       └── DashboardView.vue
│   ├── .env.development
│   ├── .env.production
│   └── .do/
│       └── app.yaml
├── docs/                  # Documentation
│   ├── api.md
│   ├── mobile-integration.md
│   └── deployment.md
└── README.md
```

## Quick Start

### Backend (FastAPI)
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at: http://localhost:8000
API Documentation: http://localhost:8000/docs

### Frontend (Vue.js)
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will be available at: http://localhost:5173

## Deployment

### Digital Ocean App Platform

Both the backend and frontend are configured for Digital Ocean App Platform deployment with the following domain setup:

- **Backend API**: `api.truledgr.app` (accessible on ports 80/443)
- **Frontend Dashboard**: `dash.truledgr.app` (accessible on ports 80/443)

#### Deployment Configuration
Use the main `app-platform.yaml` file for a complete single-app deployment, or use the individual configurations:

**Single App Deployment (Recommended):**
1. Create a new app in Digital Ocean App Platform
2. Connect your GitHub repository (McGuireTechnology/truledgr)
3. Use the configuration in `app-platform.yaml`
4. Configure your custom domains in the Digital Ocean console
5. Set required environment variables:
   - `APP_SECRET_KEY`
   - `JWT_SECRET`
   - Database will be auto-configured

**Separate Apps Deployment:**
- Backend: Use configuration in `.do/app.yaml`
- Frontend: Use configuration in `frontend/.do/app.yaml`

## API Endpoints

### Core Endpoints
- `GET /` - Health check
- `GET /health` - Detailed health status
- `GET /docs` - Interactive API documentation

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User authentication
- `GET /api/v1/users/me` - Get current user

### Mobile Integration
- `GET /api/v1/mobile/config` - Mobile app configuration and feature flags

## Mobile Apps

The system is designed to support native mobile applications for both iOS and Android platforms. The backend provides:

1. **RESTful API** endpoints optimized for mobile consumption
2. **JWT Authentication** for secure mobile sessions
3. **Feature flags** and configuration endpoints
4. **Offline-first** data synchronization support
5. **Push notification** infrastructure ready

See [docs/mobile-integration.md](docs/mobile-integration.md) for detailed mobile integration guidelines.

## Environment Variables

### Backend (.env)
```bash
ENVIRONMENT=development
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
DATABASE_URL=postgresql://user:pass@localhost/db
REDIS_URL=redis://localhost:6379
ALLOWED_ORIGINS=https://dash.truledgr.app
```

### Frontend (.env.production)
```bash
VITE_API_URL=https://api.truledgr.app
VITE_APP_TITLE=TruLedgr Dashboard
VITE_ENABLE_ANALYTICS=true
```

## Development

### Code Quality
- **Backend**: Uses Black, isort, and Flake8 for code formatting and linting
- **Frontend**: Uses ESLint and Prettier for code quality
- **Testing**: pytest for backend, Vitest for frontend

### Local Development Setup
1. Clone the repository
2. Set up backend (Python virtual environment)
3. Set up frontend (npm install)
4. Configure environment variables
5. Run both services locally

## Security Features

- JWT-based authentication
- CORS configuration for cross-origin requests
- Environment-based configuration
- Input validation with Pydantic
- Secure password handling with bcrypt

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions and support, please open an issue on the GitHub repository or contact the development team.
