# Domain-Based Architecture

This directory contains domain-specific modules that mirror the backend API structure.

## Structure

Each domain module contains:
- `api/` - API services and HTTP client logic
- `stores/` - Pinia stores for state management
- `components/` - Domain-specific components
- `views/` - Domain-specific pages/views
- `types/` - TypeScript interfaces and types
- `composables/` - Domain-specific composables/hooks
- `utils/` - Domain-specific utility functions

## Domains

- `authentication/` - Login, logout, session management
- `authorization/` - Roles, permissions, access control
- `users/` - User management and profiles
- `groups/` - Group management and membership
- `items/` - Item management and operations

## Benefits

1. **Modularity** - Each domain is self-contained
2. **Scalability** - Easy to add new domains or features
3. **Team Collaboration** - Teams can work on different domains independently
4. **Maintainability** - Domain logic is co-located
5. **Reusability** - Components and logic can be shared between domains
6. **Backend Alignment** - Structure mirrors the API organization
