# Contributing Guidelines

Thank you for your interest in contributing to TruLedgr! This guide will help you get started with contributing code, reporting issues, and improving documentation.

## 🤝 How to Contribute

There are many ways to contribute to TruLedgr:

- **💻 Code Contributions**: Bug fixes, new features, performance improvements
- **📝 Documentation**: Improve guides, add examples, fix typos
- **🐛 Bug Reports**: Report issues and help us reproduce problems
- **💡 Feature Requests**: Suggest new features and improvements
- **🧪 Testing**: Help test new features and find edge cases
- **🌍 Translations**: Help translate TruLedgr to other languages (planned)

## 🚀 Getting Started

### Development Environment

Before contributing code, set up your development environment:

1. **Fork the Repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/truledgr.git
   cd truledgr
   ```

2. **Set Up Remote**
   ```bash
   # Add upstream remote
   git remote add upstream https://github.com/McGuireTechnology/truledgr.git
   ```

3. **Install Dependencies**
   ```bash
   # Backend dependencies
   python -m venv .venv
   source .venv/bin/activate
   pip install -e ".[dev,docs]"
   
   # Frontend dependencies
   npm install
   ```

4. **Run Tests**
   ```bash
   # Verify everything works
   python -m pytest tests/
   npm run test:unit
   ```

### Development Workflow

1. **Stay Updated**
   ```bash
   # Sync with upstream before starting work
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Create Feature Branch**
   ```bash
   # Use descriptive branch names
   git checkout -b feature/expense-categories
   git checkout -b fix/authentication-bug
   git checkout -b docs/api-examples
   ```

3. **Make Changes**
   - Follow our [coding standards](code-style.md)
   - Write tests for new functionality
   - Update documentation as needed

4. **Test Your Changes**
   ```bash
   # Run all tests
   python -m pytest tests/
   npm run test:unit
   
   # Test manually in browser
   npm run dev
   ```

5. **Commit Changes**
   ```bash
   # Use conventional commit messages
   git add .
   git commit -m "feat: add expense category filtering"
   git commit -m "fix: resolve authentication timeout issue"
   git commit -m "docs: improve API documentation examples"
   ```

6. **Submit Pull Request**
   - Push your branch to your fork
   - Create pull request on GitHub
   - Fill out the pull request template
   - Wait for review and address feedback

## 📝 Commit Message Guidelines

We use [Conventional Commits](https://www.conventionalcommits.org/) for clear, consistent commit messages:

### Format
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types
- **feat**: New feature for users
- **fix**: Bug fix for users
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code changes that neither fix bugs nor add features
- **test**: Adding or updating tests
- **chore**: Maintenance tasks (dependencies, build config, etc.)

### Examples
```bash
# Good commit messages
feat(auth): add two-factor authentication support
fix(transactions): resolve duplicate transaction creation
docs(api): add examples for user endpoints
refactor(database): optimize transaction queries
test(users): add integration tests for user creation

# Bad commit messages
update stuff
fixed bug
changes
```

### Scope Guidelines
Use scopes to indicate which part of the codebase is affected:

- **auth**: Authentication and authorization
- **transactions**: Transaction management
- **budgets**: Budget functionality
- **users**: User management
- **api**: Backend API changes
- **ui**: Frontend user interface
- **docs**: Documentation
- **tests**: Testing infrastructure

## 🐛 Reporting Issues

### Before Reporting

1. **Search Existing Issues**: Check if the issue already exists
2. **Try Latest Version**: Ensure you're using the latest code
3. **Minimal Reproduction**: Create the smallest possible example
4. **Gather Information**: Collect relevant system information

### Bug Report Template

```markdown
## Bug Description
Brief description of the issue

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. Enter '...'
4. See error

## Expected Behavior
What should happen

## Actual Behavior  
What actually happens

## Environment
- OS: [e.g., macOS 12.0, Windows 11, Ubuntu 20.04]
- Browser: [e.g., Chrome 95, Firefox 94, Safari 15]
- TruLedgr Version: [e.g., v1.2.3, main branch]
- Python Version: [e.g., 3.9.7]
- Node.js Version: [e.g., 16.13.0]

## Additional Context
- Screenshots if applicable
- Console error messages
- Relevant configuration details
```

### Feature Request Template

```markdown
## Feature Summary
Brief description of the feature

## Problem Statement
What problem does this solve?

## Proposed Solution
Detailed description of your proposed solution

## Alternative Solutions
Other approaches you've considered

## Use Cases
Specific scenarios where this would be useful

## Implementation Notes
Technical considerations (optional)
```

## 🧪 Testing Guidelines

### Test Requirements

All contributions should include appropriate tests:

#### Backend Tests (Python)
- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test API endpoints and database interactions
- **Fixtures**: Reusable test data and setup

#### Frontend Tests (TypeScript)
- **Component Tests**: Test Vue.js components in isolation
- **Integration Tests**: Test component interactions
- **E2E Tests**: Test complete user workflows

### Writing Tests

#### Backend Test Example
```python
# tests/test_users.py
import pytest
from api.users.service import UserService
from api.users.schemas import UserCreate

@pytest.mark.asyncio
async def test_create_user_success(mock_user_repo):
    """Test successful user creation."""
    # Arrange
    user_service = UserService(mock_user_repo)
    user_data = UserCreate(
        email="test@example.com",
        password="secure_password",
        display_name="Test User"
    )
    
    # Act
    result = await user_service.create_user(user_data)
    
    # Assert
    assert result.email == "test@example.com"
    assert result.display_name == "Test User"
    mock_user_repo.create.assert_called_once()
```

#### Frontend Test Example
```typescript
// tests/components/TransactionForm.test.ts
import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import TransactionForm from '@/components/TransactionForm.vue'

describe('TransactionForm', () => {
  it('emits transaction data on submit', async () => {
    // Arrange
    const wrapper = mount(TransactionForm)
    
    // Act
    await wrapper.find('#amount').setValue('100.50')
    await wrapper.find('#description').setValue('Test transaction')
    await wrapper.find('form').trigger('submit')
    
    // Assert
    expect(wrapper.emitted('submit')).toBeTruthy()
    const submitData = wrapper.emitted('submit')[0][0]
    expect(submitData.amount).toBe(100.50)
    expect(submitData.description).toBe('Test transaction')
  })
})
```

### Running Tests

```bash
# Backend tests
python -m pytest tests/ -v                    # All tests
python -m pytest tests/test_users.py -v       # Specific file
python -m pytest -k "test_create_user" -v     # Specific test
python -m pytest --cov=api tests/             # With coverage

# Frontend tests
npm run test:unit                              # All unit tests
npm run test:unit -- TransactionForm          # Specific component
npm run test:e2e                               # End-to-end tests
npm run test:coverage                          # With coverage
```

## 📋 Pull Request Process

### Before Submitting

Ensure your pull request meets these requirements:

- [ ] **Follows coding standards**: Code passes linting and formatting
- [ ] **Includes tests**: New functionality has appropriate test coverage
- [ ] **Documentation updated**: README, API docs, or user guides updated
- [ ] **No breaking changes**: Or clearly documented with migration guide
- [ ] **Performance considered**: No significant performance regressions

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that causes existing functionality to change)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] New tests added for new functionality

## Screenshots (if applicable)
Add screenshots to help explain your changes

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Code is commented where necessary
- [ ] Documentation updated
- [ ] No new warnings introduced
```

### Review Process

1. **Automated Checks**: GitHub Actions run tests and linting
2. **Code Review**: Maintainers review code quality and design
3. **Testing**: Manual testing of new functionality
4. **Approval**: At least one maintainer approval required
5. **Merge**: Squash and merge to main branch

### Review Criteria

Reviewers check for:

- **Functionality**: Does the code work as intended?
- **Code Quality**: Is the code readable and maintainable?
- **Performance**: Are there any performance implications?
- **Security**: Are there any security vulnerabilities?
- **Tests**: Is there adequate test coverage?
- **Documentation**: Is the code and features documented?

## 🔧 Development Standards

### Code Quality Tools

#### Python (Backend)
```bash
# Formatting
black api/                    # Code formatting
isort api/                    # Import sorting

# Linting
pylint api/                   # Code analysis
mypy api/                     # Type checking

# Testing
pytest tests/                 # Run tests
pytest --cov=api tests/       # Coverage report
```

#### TypeScript (Frontend)
```bash
# Formatting
npm run format                # Prettier formatting
npm run lint                  # ESLint analysis
npm run lint:fix              # Auto-fix lint issues

# Type checking
npm run type-check            # TypeScript compilation

# Testing
npm run test:unit             # Unit tests
npm run test:e2e              # E2E tests
```

### Pre-commit Hooks

We use pre-commit hooks to ensure code quality:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### Continuous Integration

Our CI pipeline runs:

- **Linting**: Code style and quality checks
- **Testing**: Unit, integration, and E2E tests
- **Type Checking**: TypeScript and mypy validation
- **Security**: Dependency vulnerability scanning
- **Performance**: Basic performance regression testing

## 🌟 Recognition

We appreciate all contributions! Contributors are recognized through:

- **GitHub Contributors**: Listed in repository contributors
- **Changelog**: Significant contributions mentioned in release notes
- **Documentation**: Contributors credited in documentation
- **Community**: Recognition in discussions and social media

## 📞 Getting Help

### Development Questions

- **Documentation**: Complete guides at [docs.truledgr.app](https://docs.truledgr.app)
- **GitHub Discussions**: For general development questions
- **GitHub Issues**: For specific bugs or feature requests
- **Email**: [dev@truledgr.com](mailto:dev@truledgr.com) for private matters

### Communication Channels

- **GitHub**: Primary platform for all development communication
- **Discord**: Community chat (link coming soon)
- **Twitter**: [@TruLedgr](https://twitter.com/truledgr) for announcements

## 🎯 Contribution Areas

### High Priority Areas

We especially welcome contributions in these areas:

- **Mobile Responsiveness**: Improving mobile user experience
- **Performance Optimization**: Backend and frontend performance
- **Security Enhancements**: Authentication and data protection
- **Testing**: Increasing test coverage and quality
- **Documentation**: User guides and API documentation
- **Accessibility**: Making TruLedgr accessible to all users

### Good First Issues

New contributors should look for issues labeled:

- `good first issue`: Perfect for newcomers
- `help wanted`: Community contributions welcome
- `documentation`: Documentation improvements needed
- `frontend`: Frontend development opportunities
- `backend`: Backend development opportunities

## 📄 License

By contributing to TruLedgr, you agree that your contributions will be licensed under the same license as the project (MIT License).

## 🙏 Thank You

Thank you for contributing to TruLedgr! Your efforts help make personal finance management accessible and secure for everyone.

---

*Ready to contribute? Start by checking out our [good first issues](https://github.com/McGuireTechnology/truledgr/labels/good%20first%20issue)!* 🚀
