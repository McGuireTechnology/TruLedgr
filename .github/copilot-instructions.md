<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# TruLedgr Project Instructions

## Project Overview
This is a multi-platform application suite consisting of:
- FastAPI backend (Python) - `api.truledgr.app`
- Vue.js frontend with Vite (TypeScript) - `dash.truledgr.app`
- Mobile applications for iOS and Android ecosystems

## Architecture Guidelines
- The backend uses FastAPI with modern Python patterns
- The frontend uses Vue 3 Composition API with TypeScript
- All components should be designed for Digital Ocean App Platform deployment
- RESTful API design with JWT authentication
- Mobile-first API considerations

## Code Style and Standards
- **Python**: Use Black formatting, type hints, and Pydantic models
- **TypeScript/Vue**: Use ESLint and Prettier, strict typing
- **API Design**: Follow REST conventions, use proper HTTP status codes
- **Security**: JWT tokens, secure environment variable handling
- **CORS**: Configured for cross-origin requests between domains

## Key Features to Maintain
- JWT-based authentication system
- Mobile app configuration endpoints
- Health check and monitoring endpoints
- Biometric authentication support for mobile
- Offline-capable mobile integration
- Feature flags and configuration management

## Environment Structure
- Backend uses Python virtual environment (.venv)
- Frontend uses npm with Vite build system
- Environment variables for different deployment stages
- Digital Ocean App Platform YAML configurations

## Mobile Integration
- API endpoints should be mobile-optimized
- Secure token storage patterns
- Biometric authentication support
- Push notification infrastructure
- Feature flag system for mobile apps

When generating code:
1. Maintain consistency with existing patterns
2. Use proper TypeScript types for all Vue components
3. Include error handling and validation
4. Follow the established API endpoint patterns
5. Consider mobile app integration in backend design
6. Use secure authentication practices
7. Include appropriate CORS and security headers
