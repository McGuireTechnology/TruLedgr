
## Commit Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/) specification:

### Commit Format

```text
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Code style changes (formatting, missing semi-colons, etc)
- **refactor**: Code changes that neither fix a bug nor add a feature
- **perf**: Performance improvements
- **test**: Adding missing tests or correcting existing tests
- **chore**: Changes to build process or auxiliary tools

### Examples

```bash
feat(api): add OAuth2 authentication for Microsoft provider
fix(dash): resolve navigation issue on mobile devices
docs(contributing): update setup instructions
refactor(api): modularize settings configuration
test(api): add integration tests for user service
chore(deps): update FastAPI to version 0.104.0
```

### Scopes

Use these scopes to indicate which part of the codebase is affected:

- `api` - Backend API changes
- `dash` - Frontend application changes
- `android` - Android app changes
- `apple` - iOS app changes
- `docs` - Documentation changes
- `ci` - CI/CD pipeline changes
- `deps` - Dependency updates