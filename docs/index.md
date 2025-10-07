# TruLedgr Documentation

## Bonjour! Welcome to TruLedgr

TruLedgr is a comprehensive personal finance application suite designed to help you manage your financial life with a focus on monthly cycles, estate planning, and tax planning.

## Architecture Overview

TruLedgr consists of multiple applications working together:

- **FastAPI Backend** (`api/`) - The core API that handles all financial data and business logic
- **Dashboard (Vue)** (`dashboard/`) - A responsive web interface built with Vite and Vue 3
- **iOS/macOS App** (`apple/`) - Native Apple Multiplatform application using SwiftUI
- **Android App** (`android/`) - Native Android application using Jetpack Compose

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