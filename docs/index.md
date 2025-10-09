---
title: Home
description: Welcome to TruLedgr - Comprehensive personal finance application suite
---

# TruLedgr :moneybag:

<div class="grid cards" markdown>

-   :rocket: __Modern Architecture__

    ---

    Built with FastAPI, Vue 3, and native mobile apps for a seamless experience across all platforms

-   :calendar: __Monthly Cycles__

    ---

    Designed around monthly financial reporting periods with recurring transaction patterns

-   :shield: __Secure & Private__

    ---

    OAuth2 authentication, encrypted data, and user-controlled financial information

-   :chart_with_upwards_trend: __Comprehensive Planning__

    ---

    Estate planning, tax planning, and complete financial management tools

</div>

## Bonjour! Welcome to TruLedgr

TruLedgr is a **comprehensive personal finance application suite** designed to help you manage your financial life with a focus on monthly cycles, estate planning, and tax planning.

!!! success "Multi-Platform Support"
    TruLedgr runs everywhere: web browsers, iOS, macOS, and Android devices.

## :building_construction: Architecture Overview

TruLedgr consists of multiple applications working together:

=== "Backend API"

    **FastAPI Backend** (`api/`)
    
    The core API that handles all financial data and business logic
    
    - Python 3.11+ with Poetry
    - FastAPI with async/await
    - SQLAlchemy ORM
    - Pydantic models for validation

=== "Dashboard Web"

    **Dashboard (Vue)** (`dashboard/`)
    
    A responsive web interface built with Vite and Vue 3
    
    - Vue 3 Composition API
    - Vite for blazing-fast development
    - Modern responsive design
    - Real-time API integration

=== "iOS/macOS"

    **Apple Multiplatform** (`apple/`)
    
    Native application using SwiftUI
    
    - SwiftUI for native UI
    - Runs on iOS and macOS
    - Shared codebase
    - Native performance

=== "Android"

    **Android App** (`android/`)
    
    Native Android application
    
    - Jetpack Compose
    - Material Design 3
    - Native Android features
    - Optimized performance

## Quick Start

To get all applications running and saying "Bonjour":

### 1. Backend API
```bash
cd api
poetry install
poetry run uvicorn api.main:app --reload
```
The API will be available at `http://localhost:8000`

### 2. Vue.js Web App
```bash
### 2. Dashboard Web App

cd dashboard
npm install
npm run dev
```
The web app will be available at `http://localhost:3000`

### 3. iOS/macOS App
```bash
cd apple
swift run
```

### 4. Android App
Open the `android` directory in Android Studio and run the project.

## Testing the Setup

Each application includes a "Test API Connection" button that will verify connectivity to the FastAPI backend. Start the backend first, then test the connections from each frontend application.

## Next Steps

Once you have all applications running and saying "Bonjour", you're ready to start building the full personal finance features!