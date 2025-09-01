
## Pull Request Process

### Before Submitting

1. **Sync with Main**

   ```bash
   git checkout main
   git pull upstream main
   git checkout feature/your-feature-name
   git rebase main
   ```

2. **Run Tests**

   ```bash
   # API tests
   cd truledgr-api
   python -m pytest
   
   # Frontend tests
   cd ../truledgr-dash
   npm test
   ```

3. **Check Code Quality**

   ```bash
   # Python linting
   cd truledgr-api
   ruff check .
   black --check .
   
   # TypeScript linting
   cd ../truledgr-dash
   npm run lint
   ```

### Pull Request Template

When creating a PR, include:

1. **Description**: Clear description of what changes you've made
2. **Motivation**: Why this change is needed
3. **Testing**: How you've tested your changes
4. **Screenshots**: For UI changes, include before/after screenshots
5. **Breaking Changes**: List any breaking changes
6. **Related Issues**: Reference any related GitHub issues

### Review Process

1. **Automated Checks**: All CI checks must pass
2. **Code Review**: At least one approval from a maintainer
3. **Testing**: Ensure all tests pass and new tests are added for new features
4. **Documentation**: Update documentation if needed