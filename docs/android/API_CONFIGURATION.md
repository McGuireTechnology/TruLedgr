# Android API Configuration Guide

This guide explains how to switch between local development and production API endpoints in the TruLedgr Android app.

## Quick Start

### Switch to Local Development

1. Open `android/app/src/main/java/technology/mcguire/truledgr/MainActivity.kt`
2. Find the `companion object` at the top of `MainActivity`
3. Change `USE_LOCAL_API` to `true`:

```kotlin
companion object {
    private const val USE_LOCAL_API = true  // ← Change this
    // ...
}
```

4. Rebuild and run the app
5. The app will now use `http://10.0.2.2:8000/health` (no SSL issues!)

### Switch to Production

1. Change `USE_LOCAL_API` to `false`:

```kotlin
companion object {
    private const val USE_LOCAL_API = false  // ← Change this
    // ...
}
```

2. Rebuild and run the app
3. The app will now use `https://api.truledgr.app/health`

## Configuration Details

### Local Development Mode (`USE_LOCAL_API = true`)

**Endpoint:** `http://10.0.2.2:8000/health`

**Characteristics:**
- ✅ No SSL certificate required
- ✅ No DNS resolution needed
- ✅ Works perfectly in Android emulators
- ✅ Fast and reliable for development
- ⚠️ Requires local API server running on your Mac

**Use when:**
- Developing new API features
- Testing API changes locally
- Working offline or on slow networks
- Avoiding SSL certificate issues in emulators

**Requirements:**
- FastAPI server must be running on your Mac
- Start with: `cd /path/to/TruLedgr && ./start-api.sh`
- API will be accessible at `http://localhost:8000`
- Android emulator accesses it via `10.0.2.2` (special emulator localhost alias)

### Production Mode (`USE_LOCAL_API = false`)

**Primary Endpoint:** `https://api.truledgr.app/health`  
**Fallback Endpoint:** `https://162.159.140.98/health` (IP address with Host header)

**Characteristics:**
- ✅ Tests against real production environment
- ✅ SSL/HTTPS security
- ✅ Works on physical devices without issues
- ⚠️ May have SSL certificate validation issues in emulators
- ⚠️ Requires internet connection

**Use when:**
- Testing production-like behavior
- Testing on physical Android devices
- Preparing for release
- Verifying API is working correctly

**Note:** If you get SSL errors in the emulator, this is normal. The network security config (`network_security_config.xml`) helps, but physical devices work best for production API testing.

## Visual Indicators

The app displays the current API mode in the UI:

- **Local Development**: Yellow/amber badge at the top
- **Production**: Blue badge at the top
- The endpoint URL is displayed at the bottom

## Under the Hood

### How the Configuration Works

```kotlin
companion object {
    // Toggle flag
    private const val USE_LOCAL_API = false
    
    // Endpoint selection based on flag
    private val API_ENDPOINTS = if (USE_LOCAL_API) {
        listOf(
            "http://10.0.2.2:8000/health"  // Local
        )
    } else {
        listOf(
            "https://api.truledgr.app/health",      // Production primary
            "https://162.159.140.98/health"         // IP fallback
        )
    }
    
    private val API_DESCRIPTION = if (USE_LOCAL_API) 
        "Local Development" 
    else 
        "Production"
}
```

### Logging

The app logs which mode it's using on startup:

```
I/TruLedgr: 🔧 API Mode: Production
I/TruLedgr: 📡 Endpoints: [https://api.truledgr.app/health, https://162.159.140.98/health]
```

View logs with:
```bash
adb logcat | grep TruLedgr
```

## Troubleshooting

### Local Development Issues

**Problem:** "Connection failed" or "Connection refused"

**Solutions:**
1. Check if API server is running:
   ```bash
   curl http://localhost:8000/health
   ```

2. Start the API server:
   ```bash
   cd /path/to/TruLedgr
   ./start-api.sh
   ```

3. Verify emulator can reach your Mac:
   ```bash
   adb shell curl http://10.0.2.2:8000/health
   ```

### Production Issues

**Problem:** SSLHandshakeException in emulator

**Solutions:**
1. **Best:** Test on a physical Android device
2. Rebuild app to ensure `network_security_config.xml` is included
3. Update emulator system image to latest version
4. Switch to local development mode temporarily
5. See `ANDROID_SSL_TROUBLESHOOTING.md` for detailed SSL troubleshooting

**Problem:** "No address associated with hostname"

**Solutions:**
1. Check internet connection
2. Verify DNS works: `adb shell ping api.truledgr.app`
3. Cold boot emulator: `adb reboot`
4. The app will automatically try IP fallback

## Build Variants (Future Enhancement)

For even better configuration management, consider using Android build variants:

```kotlin
// In build.gradle.kts
android {
    buildTypes {
        debug {
            buildConfigField("String", "API_BASE_URL", "\"http://10.0.2.2:8000\"")
        }
        release {
            buildConfigField("String", "API_BASE_URL", "\"https://api.truledgr.app\"")
        }
    }
}
```

This would allow automatic switching based on debug vs release builds.

## Best Practices

1. **Development:**
   - Use local API mode for feature development
   - Faster iteration, no network latency
   - No SSL complications

2. **Testing:**
   - Test with production API before releasing
   - Always test on physical device before release
   - Verify both success and error cases

3. **Release:**
   - Always use production mode for releases
   - Never ship with `USE_LOCAL_API = true`
   - Consider adding a compile-time check

4. **Debugging:**
   - Check logcat for detailed error messages
   - Use the visual indicators in the app
   - Test both endpoints in production mode

## Security Notes

- **Local mode (HTTP):** Only for development, never in production
- **Production mode (HTTPS):** Required for release builds
- Network security config allows user certificates in debug builds only
- Production builds maintain strict certificate validation

## Related Files

- `MainActivity.kt` - Contains the configuration flag
- `network_security_config.xml` - SSL/TLS configuration
- `AndroidManifest.xml` - References network security config
- `ANDROID_SSL_TROUBLESHOOTING.md` - Detailed SSL troubleshooting
- `start-api.sh` - Script to start local API server

## Quick Reference

| Mode | Endpoint | Protocol | Use Case |
|------|----------|----------|----------|
| Local | `10.0.2.2:8000` | HTTP | Development, debugging |
| Production | `api.truledgr.app` | HTTPS | Testing, release |

## Getting Help

If you're having issues:

1. Check the logcat output: `adb logcat | grep TruLedgr`
2. Verify which mode is active (check the badge in the app)
3. See `ANDROID_SSL_TROUBLESHOOTING.md` for SSL issues
4. Try switching modes to isolate the problem
5. Test on a physical device if emulator has issues
