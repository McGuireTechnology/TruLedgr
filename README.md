# TruLedgr

**Bonjour!** Welcome to TruLedgr - A comprehensive personal finance application suite.

## Overview

TruLedgr is designed to help you manage your personal finances with a focus on monthly cycles, extending into estate planning and tax planning. The system consists of multiple applications working together:

- **FastAPI Backend** - Core API handling financial data and business logic
- **Dashboard (Vue)** - Responsive web interface
- **Landing Page** - Marketing and project overview website
- **Landing Page** - retired; documentation and project site are served from MkDocs at the repository root and deployed to GitHub Pages
- **iOS/macOS App** - Native Apple Multiplatform application
- **Android App** - Native Android application

## Quick Start

Each application can be run independently but they work best together. Start with the FastAPI backend, then launch any of the frontend applications.

## Prerequisites

Before you begin, ensure you have the following tools installed:

### API (Backend)

- Python 3.10+
- [Poetry](https://python-poetry.org/)

### Dashboard (Web)

- [Node.js](https://nodejs.org/) (v18+ recommended)

### Apple (iOS/macOS)

- [Xcode](https://developer.apple.com/xcode/)

### Android

- [Android Studio](https://developer.android.com/studio)

### Recommended Tools

- [Homebrew](https://brew.sh/) (macOS package manager)
- [Visual Studio Code](https://code.visualstudio.com/)
- [docctl](https://github.com/docctl/docctl) (MkDocs CLI helper)
- [GitHub CLI](https://cli.github.com/) (`gh`)

### Backend API

```bash
cd api
poetry install
poetry run uvicorn api.main:app --reload
```

### Dashboard Web App

```bash
cd dashboard
npm install
npm run dev
```

### Landing Page

The previous Vue-based landing site has been retired. The project's public site is generated from the MkDocs site in the repository root and deployed to GitHub Pages (see `.github/workflows/deploy-mkdocs.yml`).

### iOS/macOS App

```bash
cd apple
swift run
```

### Android App

Open `android` in Android Studio and run the project.

## Running tests

### Backend (pytest)

```bash
cd api
poetry install
poetry run pytest
```

### Frontend (Vitest) - Dashboard

```bash
cd dashboard
npm install
npm run test
```

### Landing (Vitest)

The landing Vue tests have been removed. Documentation and site content are managed in `docs/` and built with MkDocs.

## Documentation

Full documentation is available in the `docs/` directory and can be served using MkDocs:

```bash
pip install mkdocs-material
mkdocs serve
```

## Technology Stack

- **Backend**: FastAPI (Python) with Poetry dependency management
- **Frontend Web**: Vite + Vue.js 3
- **Mobile**: SwiftUI (iOS/macOS), Jetpack Compose (Android)  
- **Database**: SQLite (development), PostgreSQL (production)
- **Documentation**: MkDocs
- **Deployment**: DigitalOcean

## Architecture

The system follows a multi-platform architecture with a central FastAPI backend serving multiple frontend applications. Each frontend can operate independently while sharing the same backend services.

## Contributing

This project uses Poetry for Python dependency management. Make sure to run `poetry install` before contributing to the backend components.

## License

[Add your license here]

## CI Badges

<!-- Add the Codecov badge after you add CODECOV_TOKEN and run main CI once -->

[![Codecov](https://img.shields.io/badge/coverage-unknown-lightgrey)](https://codecov.io/gh/<owner>/<repo>)

## Pre-commit hooks

This repository uses `pre-commit` to run linters and formatters locally. To install hooks:

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

You can run pre-commit checks in CI by adding `pre-commit run --all-files` to the workflow steps.
