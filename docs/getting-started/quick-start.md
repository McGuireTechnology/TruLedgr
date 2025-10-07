# Quick Start

## Prerequisites

- Python 3.11+
- Poetry
- Node.js 18+
- Xcode (for iOS/macOS development)
- Android Studio (for Android development)

## Running All Components

### 1. Backend API

```bash
cd api
poetry install
poetry run uvicorn api.main:app --reload
```

### 2. Dashboard Web App

```bash
cd dashboard
npm install
npm run dev
```

### 3. iOS/macOS App

```bash
cd apple
swift run
```

### 4. Android App

Open in Android Studio and run.

## Verify Setup

Visit each application and test the API connection to ensure everything is working correctly.