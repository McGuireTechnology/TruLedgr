# TruLedgr Mobile Apps - Bonjour Edition

This README explains how to run the TruLedgr mobile apps (iOS/macOS and Android) with API connectivity testing.

## What These Apps Do

Both mobile apps display "Bonjour!" and include a button to check if the TruLedgr API is running and accessible.

### Features

- 🎩 Displays "Bonjour!" greeting
- 🔌 Tests API connectivity with a button
- ✅ Shows API status (UP/DOWN)
- 📡 Displays API response messages
- 🔄 Real-time status updates

## Running the API

First, start the TruLedgr API server:

```bash
# From the project root
./start-api.sh
```

Or manually:

```bash
cd /Users/nathan/Documents/TruLedgr
poetry run python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- `http://localhost:8000` (general use)
- `http://127.0.0.1:8000` (explicit localhost)
- `http://10.0.2.2:8000` (Android emulator special address)

### API Endpoints

- `GET /` - Returns "Bonjour from TruLedgr API!"
- `GET /health` - Health check endpoint

## Running the iOS/macOS App

### Prerequisites
- Xcode 16.4 or later
- macOS 14.0+ for development

### Steps

1. **Open the project**:
   ```bash
   cd apple
   open TruLedgr.xcodeproj
   ```

2. **Select a target**:
   - iOS Simulator (iPhone 16, iOS 18.5+)
   - macOS (My Mac)
   - visionOS Simulator (optional)

3. **Run the app**:
   - Press **Cmd+R** or click the Run button
   - The app will display "Bonjour!"
   - Click "Check API Status" to test connectivity

### Network Configuration

The iOS/macOS app connects to `https://api.truledgr.app/health` (production API)

- Works on all platforms (macOS, iOS Simulator, Physical devices)
- Requires internet connectivity
- For local development, you can change the URL in `ContentView.swift` to `http://localhost:8000/health`

### Troubleshooting iOS/macOS

**App Transport Security (ATS)**:
The `Info.plist` is configured to allow local networking:
```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
    <key>NSAllowsLocalNetworking</key>
    <true/>
</dict>
```

**API Not Reachable**:
1. Make sure the API is running: `curl http://localhost:8000/health`
2. Check firewall settings
3. On physical device, use your Mac's IP instead of `localhost`

## Running the Android App

### Prerequisites
- Android Studio (latest version)
- Android SDK API 34 or higher
- Android device or emulator

### Steps

1. **Open the project in Android Studio**:
   ```bash
   cd android
   # Then open this folder in Android Studio
   ```

2. **Sync Gradle** (may happen automatically)

3. **Select a device**:
   - Android Emulator (create one if needed)
   - Physical Android device (with USB debugging enabled)

4. **Run the app**:
   - Click the Run button (green play icon)
   - Or press **Shift+F10**

5. **Test API connectivity**:
   - The app will display "Bonjour!"
   - Tap "Check API Status" to test connectivity

### Network Configuration

The Android app connects to `https://api.truledgr.app/health` (production API)

- Works on both Android Emulator and Physical devices
- Requires internet connectivity
- For local development, you can change the URL in `MainActivity.kt`:
  - Emulator: `http://10.0.2.2:8000/health` (maps to host machine's localhost)
  - Physical device: `http://YOUR_COMPUTER_IP:8000/health` (e.g., `http://192.168.1.100:8000/health`)

### Troubleshooting Android

**Internet Permission**:
The `AndroidManifest.xml` includes the required permission:
```xml
<uses-permission android:name="android.permission.INTERNET" />
```

**Connection Refused**:
1. Verify API is running: `curl http://localhost:8000/health`
2. On emulator: Use `10.0.2.2` instead of `localhost`
3. On physical device: Use your Mac's local network IP
4. Check firewall isn't blocking port 8000

**Gradle Build Issues**:
```bash
cd android
./gradlew clean
./gradlew build
```

## API Response Format

When the health check is successful, you'll see:

```json
{
  "status": "healthy",
  "message": "Bonjour, TruLedgr is running!"
}
```

## Architecture

### iOS/macOS (Swift + SwiftUI)
- **Language**: Swift 5.0
- **UI Framework**: SwiftUI
- **Networking**: URLSession
- **Min Deployment**: iOS 18.5, macOS 14.0, visionOS 2.5

### Android (Kotlin + Compose)
- **Language**: Kotlin 2.0.21
- **UI Framework**: Jetpack Compose + Material Design 3
- **Networking**: HttpURLConnection (simple GET requests)
- **Min SDK**: 24 (Android 7.0)
- **Target SDK**: 36

### Backend (Python + FastAPI)
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Server**: Uvicorn
- **CORS**: Enabled for local development

## Development Workflow

1. **Start API** (terminal 1):
   ```bash
   ./start-api.sh
   ```

2. **Run iOS app** (Xcode):
   ```bash
   cd apple
   open TruLedgr.xcodeproj
   # Then Cmd+R to run
   ```

3. **Run Android app** (Android Studio):
   ```bash
   # Open android/ folder in Android Studio
   # Click Run button
   ```

## Next Steps

This "Bonjour" version establishes the basic architecture for:
- ✅ API connectivity testing
- ✅ Cross-platform UI (SwiftUI & Compose)
- ✅ Network error handling
- ✅ Async operations (coroutines in Android, async/await in Swift)

Future enhancements:
- [ ] OAuth2 authentication
- [ ] Real financial data models
- [ ] Transaction tracking
- [ ] Monthly reports
- [ ] Data synchronization

## Troubleshooting

### "API is DOWN" on Both Platforms

1. Check if API is actually running:
   ```bash
   curl http://localhost:8000/health
   ```

2. Check the response:
   ```bash
   curl -v http://localhost:8000/health
   ```

3. Restart the API server

### Works on iOS but not Android

- Android emulator requires `10.0.2.2` instead of `localhost`
- Check Android logcat for errors: View → Tool Windows → Logcat

### Works on Android but not iOS

- Check iOS console in Xcode: View → Debug Area → Activate Console
- Verify ATS settings in Info.plist
- On physical iOS device, use your Mac's IP address

## Support

For issues or questions, refer to:
- iOS/macOS setup: `apple/README.md` (if exists)
- Android setup: `android/ANDROID_STUDIO_SETUP.md`
- API documentation: `api/README.md` (if exists)
