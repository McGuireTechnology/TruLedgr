---
title: TruLedgr - Personal Finance Made Simple
description: Take control of your finances with TruLedgr - comprehensive budgeting, transaction tracking, and financial planning
---

# Take Control of Your Financial Future

**TruLedgr** helps you manage your money, plan your estate, and optimize your taxes - all in one powerful platform.

<div class="grid cards" markdown>

-   :material-cash-multiple: __Track Every Dollar__

    ---

    Monitor all your accounts, transactions, and spending in real-time across web and mobile

    [Learn More →](features/transactions.md){ .md-button }

-   :material-calendar-month: __Monthly Planning__

    ---

    Built around your monthly financial cycle with automatic reports and recurring budgets

    [Explore Features →](features/reports.md){ .md-button }

-   :material-shield-lock: __Secure & Private__

    ---

    Your financial data stays yours - bank-level security with full data ownership

    [Security Details →](guide/index.md){ .md-button }

-   :material-chart-line: __Future Planning__

    ---

    Estate planning and tax optimization tools to help you prepare for what's ahead

    [Get Started →](get-started/index.md){ .md-button .md-button--primary }

</div>

## Why TruLedgr?

### :material-devices: Available Everywhere

Use TruLedgr on any device - responsive web app, native iOS/macOS apps, or Android. Your financial data syncs seamlessly across all platforms.

### :material-eye-off: Privacy First

Unlike other personal finance apps that sell your data or show ads, TruLedgr puts you in control. Self-hosted option available for maximum privacy.

### :material-calendar-check: Monthly-Focused Workflows

Built around how you actually manage money - monthly paychecks, monthly bills, monthly budgets. Everything organized by the cycle that matters.

### :material-puzzle: Complete Financial Picture

Go beyond basic budgeting with integrated estate planning and tax planning tools. One platform for your entire financial life.

---

## Quick Start

<div class="grid" markdown>

=== "1. Download"

    Get TruLedgr for your device:
    
    - :material-web: [Web Dashboard](apps/web.md) - Works in any browser
    - :material-apple: [iOS & macOS](apps/apple.md) - Native Apple apps
    - :material-android: [Android](apps/android.md) - Google Play Store

=== "2. Create Account"

    Sign up with your existing account:
    
    - :material-google: Google
    - :material-microsoft: Microsoft
    - :material-github: GitHub
    - :material-apple: Apple
    
    No passwords to remember!

=== "3. Add Accounts"

    Connect your financial accounts:
    
    - Bank accounts
    - Credit cards
    - Investment accounts
    - Loans & mortgages

=== "4. Start Tracking"

    Begin managing your money:
    
    - Set monthly budgets
    - Record transactions
    - Review reports
    - Plan ahead

</div>

[Get Started Now →](get-started/index.md){ .md-button .md-button--primary .md-button--raised }

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