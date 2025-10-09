# Android Studio Setup Guide

## Creating Run/Debug Configuration

If Android Studio doesn't automatically create a run configuration, follow these steps:

### Method 1: Let Android Studio Auto-Detect (Easiest)

1. **Sync Gradle**: Click "Sync Project with Gradle Files" in the toolbar (elephant icon)
2. **Wait for indexing**: Let Android Studio finish indexing the project
3. **Restart Android Studio**: Sometimes a restart helps detect the configuration
4. The run configuration should appear automatically

### Method 2: Manual Configuration

1. Click **Run** → **Edit Configurations...** (or the dropdown next to the Run button)
2. Click the **+** button (Add New Configuration)
3. Select **Android App**
4. Configure:
   - **Name**: `app`
   - **Module**: Select `TruLedgr.app.main`
   - **Launch Options**: Select "Default Activity"
5. Click **OK**

### Method 3: Gradle Task (Alternative)

If the above methods don't work, you can run directly via Gradle:

```bash
cd /Users/nathan/Documents/TruLedgr/android
./gradlew installDebug
```

Or from Android Studio:

1. Open **Gradle** panel (usually on the right side)
2. Navigate to **TruLedgr → app → Tasks → install**
3. Double-click **installDebug**

## Troubleshooting

### Configuration Not Appearing

1. **Check Gradle Sync**: Make sure Gradle sync completed successfully
2. **Check Build**: Run **Build** → **Make Project** (Cmd+F9)
3. **Invalidate Caches**: **File** → **Invalidate Caches / Restart...**
4. **Check SDK**: Ensure Android SDK is properly configured in **Settings** → **Languages & Frameworks** → **Android SDK**

### Module Not Found

If you see "Module not specified" or module doesn't appear:

1. Close Android Studio
2. Delete these directories:

   ```bash
   rm -rf android/.idea
   rm -rf android/.gradle
   rm -rf android/build
   rm -rf android/app/build
   ```

3. Reopen the project in Android Studio
4. Let it re-import and index

### Gradle Build Fails

If Gradle build fails:

```bash
cd android
./gradlew clean
./gradlew build
```

## Running the App

### On Emulator

1. **Create AVD**: **Tools** → **Device Manager** → **Create Virtual Device**
2. Select a device (e.g., Pixel 6)
3. Select a system image (API 34 recommended)
4. Click **Finish**
5. Start the emulator
6. Click the **Run** button (green play icon)

### On Physical Device

1. Enable **Developer Options** on your Android device
2. Enable **USB Debugging**
3. Connect device via USB
4. Click **Run** and select your device

## Project Structure

```text
android/
├── app/
│   ├── src/
│   │   └── main/
│   │       ├── java/technology/mcguire/truledgr/
│   │       │   ├── MainActivity.kt          # Main entry point
│   │       │   └── ui/theme/               # Compose theme
│   │       ├── AndroidManifest.xml         # App manifest
│   │       └── res/                        # Resources
│   └── build.gradle.kts                    # App module build file
├── build.gradle.kts                        # Project build file
├── settings.gradle.kts                     # Project settings
└── gradle/libs.versions.toml              # Version catalog
```

## Current Configuration

- **Package**: `technology.mcguire.truledgr`
- **Min SDK**: 24 (Android 7.0)
- **Target SDK**: 36
- **Compile SDK**: 36
- **Kotlin**: 2.0.21
- **Compose**: Latest with Material 3
- **AGP**: 8.11.2
