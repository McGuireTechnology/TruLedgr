# Debugging Android Network Issues

If the Android app shows "no address associated with hostname" or other network errors when checking API status, follow these troubleshooting steps.

## Common Issue: DNS Resolution in Emulator

The Android emulator sometimes has trouble resolving external DNS names. The app now includes automatic fallback from hostname to IP address.

### How the App Handles DNS Issues

The app tries endpoints in order:

1. **First**: `https://api.truledgr.app/health` (hostname via DNS)
2. **Fallback**: `https://162.159.140.98/health` (direct IP with Host header)

If DNS resolution fails on the hostname, it automatically tries the IP address.

## Viewing Logs

To see detailed network logs:

1. **In Android Studio**:
   - Open **Logcat** (View → Tool Windows → Logcat)
   - Filter by "TruLedgr" tag
   - Look for messages like:
     ```
     D/TruLedgr: Trying endpoint 1/2: https://api.truledgr.app/health
     D/TruLedgr: Response code: 200
     D/TruLedgr: ✅ Success: {"status":"healthy","message":"Bonjour, TruLedgr is running!"}
     ```

2. **Via ADB** (command line):
   ```bash
   adb logcat -s TruLedgr:D
   ```

## Troubleshooting Steps

### 1. Check Internet Connection

The emulator must have internet access through your computer's network.

**Test from terminal:**
```bash
# Test if your Mac can reach the API
curl https://api.truledgr.app/health

# Expected output:
# {"status":"healthy","message":"Bonjour, TruLedgr is running!"}
```

**Test from emulator:**
```bash
# Connect to emulator shell
adb shell

# Try to ping (if ping is available)
ping -c 3 8.8.8.8

# Try DNS lookup
nslookup api.truledgr.app

# Try curl (if available)
curl https://api.truledgr.app/health
```

### 2. Restart Emulator

Sometimes the emulator's network stack gets confused:

1. **Close emulator** (stop in Android Studio or `adb emu kill`)
2. **Cold Boot**:
   - In AVD Manager, click dropdown next to your device
   - Select "Cold Boot Now"
3. **Run app again**

### 3. Check Emulator Network Settings

The emulator should use your Mac's DNS settings by default:

```bash
# Check emulator DNS settings
adb shell getprop net.dns1
adb shell getprop net.dns2
```

### 4. Wipe Emulator Data

If DNS issues persist, wipe the emulator:

1. AVD Manager → Select device → Actions dropdown → "Wipe Data"
2. Cold boot the emulator
3. Run app again

### 5. Try a Different Emulator

Create a new AVD (Android Virtual Device):

1. Tools → Device Manager → Create Device
2. Choose a system image (recommend: Pixel 6, API 34+)
3. Finish and launch
4. Run app on new emulator

### 6. Test on Physical Device

To rule out emulator issues, test on a real Android phone:

1. Enable Developer Options on your phone
2. Enable USB Debugging
3. Connect via USB
4. Select your device in Android Studio
5. Run app

Physical devices rarely have DNS issues since they use cellular or WiFi DNS.

## Common Error Messages

### "no address associated with hostname"

**Cause**: DNS resolution failed  
**Solution**: App should automatically fall back to IP address. Check logs to confirm.

**Manual fix**: Edit `MainActivity.kt` to use only IP address:
```kotlin
val endpoints = listOf(
    "https://162.159.140.98/health"  // IP only
)
```

### "Connect timed out"

**Cause**: Network connectivity issue or firewall  
**Solution**:
- Check Mac's firewall isn't blocking emulator
- Verify API is accessible from terminal: `curl https://api.truledgr.app/health`
- Try increasing timeout in code (currently 5000ms)

### "SSL handshake aborted"

**Cause**: Certificate verification issues  
**Solution**: Make sure system date/time is correct in emulator

### "CLEARTEXT communication not permitted"

**Cause**: App trying to use HTTP instead of HTTPS  
**Solution**: Ensure all URLs use `https://` (not `http://`)

## Emulator DNS Workarounds

### Option 1: Use Google DNS

Set the emulator to use Google's DNS servers:

```bash
adb root
adb remount
adb shell settings put global private_dns_mode hostname
adb shell settings put global private_dns_specifier dns.google
```

### Option 2: Edit Emulator DNS

Edit `~/.android/avd/YOUR_AVD.avd/config.ini`:

```ini
hw.audioInput=yes
hw.battery=yes
# Add these lines:
dns.server=8.8.8.8
dns.server2=8.8.4.4
```

Then cold boot the emulator.

### Option 3: Use ADB Reverse Proxy

If running API locally:

```bash
# Forward emulator's localhost:8000 to Mac's localhost:8000
adb reverse tcp:8000 tcp:8000
```

Then update app to use `http://localhost:8000/health`

## Network Configuration in Code

The app is configured for secure HTTPS:

**AndroidManifest.xml:**
```xml
<uses-permission android:name="android.permission.INTERNET" />
<application android:usesCleartextTraffic="false">
```

**MainActivity.kt:**
```kotlin
// HTTPS only
val url = URL("https://api.truledgr.app/health")
val connection = url.openConnection() as HttpURLConnection

// For IP fallback, add Host header
if (endpoint.contains("162.159.140.98")) {
    connection.setRequestProperty("Host", "api.truledgr.app")
}
```

## Verifying the Fix

After troubleshooting, verify:

1. **Run the app**
2. **Tap "Check API Status"**
3. **Check Logcat** for:
   ```
   D/TruLedgr: Trying endpoint 1/2: https://api.truledgr.app/health
   D/TruLedgr: Response code: 200
   D/TruLedgr: ✅ Success: {"status":"healthy",...}
   ```
4. **App should show**: "✅ API is UP" with Bonjour message

## Still Not Working?

If none of the above helps:

1. **Check API status externally**:
   ```bash
   curl -v https://api.truledgr.app/health
   ```

2. **Verify Cloudflare IP is correct**:
   ```bash
   nslookup api.truledgr.app
   dig api.truledgr.app
   ```

3. **Check Android Studio version**: Make sure you have the latest version
   - Help → Check for Updates

4. **Check system proxy**: If your Mac uses a proxy, the emulator might need configuration
   - Settings → Proxy → Manual proxy configuration in AVD Manager

5. **Try different API 34+**: Some older system images have network bugs

## Contact Support

If issues persist, collect this info:

```bash
# Emulator info
adb shell getprop ro.build.version.release
adb shell getprop ro.product.model

# Network info
adb shell ip addr show
adb shell getprop net.dns1

# App logs
adb logcat -s TruLedgr:* *:E > truledgr_logs.txt
```

Then share `truledgr_logs.txt` with the development team.
