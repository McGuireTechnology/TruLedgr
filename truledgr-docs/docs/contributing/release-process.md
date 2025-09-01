## Release Process

We use **tag-based releases** for deployments:

### Version Tagging

```bash
# Create and push a new tag
git tag -a v1.2.3 -m "Release version 1.2.3"
git push upstream v1.2.3
```

### Semantic Versioning

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR** version for incompatible API changes
- **MINOR** version for backwards-compatible functionality
- **PATCH** version for backwards-compatible bug fixes

### Release Notes

- Create release notes on GitHub for each tag
- Include list of new features, bug fixes, and breaking changes
- Reference relevant pull requests and contributors