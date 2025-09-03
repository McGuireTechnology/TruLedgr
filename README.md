# TruLedgr

**A comprehensive personal finance management platform with a focus on security, privacy, and user control.**

## 🏗️ Architecture: Multi-Repository Setup

TruLedgr uses a **multi-repository architecture** where each component is maintained in its own repository for better modularity, independent versioning, and focused development.

### 📦 Core Repositories

| Repository | Purpose | Technology | Status |
|------------|---------|------------|--------|
| **[truledgr](https://github.com/McGuireTechnology/truledgr)** | Main coordination hub | Documentation, Scripts | 🟢 Active |
| **[truledgr-api](https://github.com/McGuireTechnology/truledgr-api)** | Backend API server | FastAPI, Python | 🟡 In Development |
| **[truledgr-dash](https://github.com/McGuireTechnology/truledgr-dash)** | Web dashboard | Vue.js, TypeScript | 🟡 In Development |
| **[truledgr-land](https://github.com/McGuireTechnology/truledgr-land)** | Landing page | Vue.js, TypeScript | 🟡 In Development |
| **[truledgr-docs](https://github.com/McGuireTechnology/truledgr-docs)** | Documentation site | MkDocs, Markdown | 🟡 In Development |
| **[truledgr-android](https://github.com/McGuireTechnology/truledgr-android)** | Android app | Kotlin | 🔴 Planned |
| **[truledgr-apple](https://github.com/McGuireTechnology/truledgr-apple)** | iOS/macOS apps | Swift | 🔴 Planned |

## 🚀 Quick Start

### For Full-Stack Development

1. **Clone the coordination repository**:
   ```bash
   git clone https://github.com/McGuireTechnology/truledgr.git
   cd truledgr
   ```

2. **Set up the development environment**:
   ```bash
   ./scripts/setup_development.sh
   ```

3. **Clone component repositories**:
   ```bash
   ./scripts/clone_all_repos.sh
   ```

4. **Start all services**:
   ```bash
   ./scripts/start_all_services.sh
   ```

### For Component-Specific Development

If you're working on a specific component, you can clone and work with just that repository:

```bash
# Backend API development
git clone https://github.com/McGuireTechnology/truledgr-api.git

# Frontend dashboard development  
git clone https://github.com/McGuireTechnology/truledgr-dash.git

# Mobile app development
git clone https://github.com/McGuireTechnology/truledgr-android.git
```

## 🛠️ Development Tools (This Repository)

This main repository provides:

- **🧪 Integration Testing**: Cross-service testing capabilities
- **📜 Development Scripts**: Orchestration tools for multi-repo development
- **📚 Global Documentation**: Architecture, setup guides, and coordination docs
- **⚙️ VS Code Workspace**: Multi-repository development environment
- **🚀 Deployment Tools**: Coordinated deployment across services

## 🏃‍♂️ Running Services Locally

```bash
# Start individual services
npm run dev:api     # API server on :8000
npm run dev:dash    # Dashboard on :3000  
npm run dev:land    # Landing page on :3001
npm run dev:docs    # Documentation on :8001

# Start all services together
npm run dev:all

# Run integration tests
npm run test:integration
```

## 📖 Documentation

- **[Architecture Overview](./docs/architecture.md)** - System design and component interaction
- **[Development Setup](./docs/contributing/getting-started.md)** - Complete setup guide
- **[Repository Transition](./REPOSITORY_TRANSITION.md)** - Migration from monorepo to multi-repo
- **[API Documentation](https://api.truledgr.com/docs)** - Interactive API documentation
- **[User Guide](https://docs.truledgr.com)** - End-user documentation

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](./CONTRIBUTING.md) for details.

### Development Workflow

1. **Choose a component** to work on from the repositories above
2. **Fork the specific repository** you want to contribute to
3. **Set up the development environment** using this coordination repository
4. **Make your changes** in the component repository
5. **Test integration** using the tools in this repository
6. **Submit a pull request** to the component repository

## 📋 Project Status

🟡 **Currently transitioning from monorepo to multi-repository architecture**

- ✅ Repository structure planning complete
- ✅ Component separation in progress  
- 🟡 Individual repository creation pending
- 🔴 Cross-repository CI/CD setup pending

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: Please report issues in the relevant component repository
- **Discussions**: Use [GitHub Discussions](https://github.com/McGuireTechnology/truledgr/discussions) for questions and ideas
- **Security**: See [SECURITY.md](SECURITY.md) for security-related concerns

---

**Made with ❤️ by [McGuire Technology](https://mcguire.technology)**
