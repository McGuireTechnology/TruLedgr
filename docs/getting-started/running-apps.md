# Running the Applications

## Development Environment

All TruLedgr applications can be run locally for development. Make sure you have the required dependencies installed first.

## Starting the Backend API

The FastAPI backend must be running for the frontend applications to function properly.

```bash
cd api
poetry run uvicorn api.main:app --reload
```

The API will be available at `http://localhost:8000`

- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

## Starting the Web Application

```bash
cd dashboard
npm install  # First time only
npm run dev
```

The web application will be available at `http://localhost:3000`

## Running the iOS/macOS Application

```bash
cd apple
swift run
```

This will build and run the native Apple application.

## Running the Android Application

1. Open Android Studio
2. Open the `android` directory as a project
3. Wait for Gradle sync to complete
4. Run the application using the play button or `Shift + F10`

## Running Documentation

```bash
poetry run mkdocs serve
```

Documentation will be available at `http://localhost:8001`

## Testing API Connectivity

Each frontend application includes a "Test API Connection" button. Make sure the backend API is running first, then test the connection from each application to verify everything is working correctly.