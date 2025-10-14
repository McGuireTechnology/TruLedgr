# Android SSL/Network Troubleshooting Guide

This guide helps resolve common SSL certificate and network issues in the TruLedgr Android app.

## Common Issues

### 1. SSLHandshakeException

**Error Message:**
```
javax.net.ssl.SSLHandshakeException: java.security.cert.CertPathValidatorException: Trust anchor for certification path not found.
```

**Cause:** 
Android emulators often have trouble validating SSL certificates, especially for domains using Let's Encrypt or modern certificate authorities.

**Solutions:**

#### Option A: Test on a Physical Device (Recommended)
Physical Android devices typically have up-to-date CA certificates and will work correctly.

1. Connect your Android device via USB
2. Enable Developer Mode and USB Debugging
3. In Android Studio: Device dropdown → Select your physical device
4. Run the app

#### Option B: Use Network Security Config (Already Implemented)
We've added `network_security_config.xml` which trusts user-installed certificates in debug builds.

**File:** `android/app/src/main/res/xml/network_security_config.xml`

This configuration:
- ✅ Trusts system certificates (production)
- ✅ In debug builds, also trusts user-installed certificates
- ✅ Allows development with emulators

#### Option C: Update Emulator System Image
1. Android Studio → Tools → SDK Manager
2. SDK Platforms tab
3. Show Package Details (bottom right)
4. Select a newer system image (API 34+ recommended)
5. Install and create a new AVD with the updated image

#### Option D: Add Certificate to Emulator (Advanced)
If you need to add a specific CA certificate:

```bash
# Get the certificate
openssl s_client -showcerts -connect api.truledgr.app:443 </dev/null 2>/dev/null | \
  openssl x509 -outform PEM > truledgr_cert.pem

# Install on emulator (requires root)
adb root
adb remount
adb push truledgr_cert.pem /system/etc/security/cacerts/
adb reboot
```

### 2. UnknownHostException (DNS Errors)

**Error Message:**
```
java.net.UnknownHostException: Unable to resolve host "api.truledgr.app": No address associated with hostname
```

**Solutions:**

#### Check Emulator Network Connection
```bash
# Test DNS resolution from emulator
adb shell ping api.truledgr.app

# Test with curl
adb shell curl https://api.truledgr.app/health
```

#### Restart Emulator Networking
```bash
# Cold boot the emulator
adb reboot

# Or from Android Studio: Tools → AVD Manager → Cold Boot Now
```

#### Check Host Machine Network
```bash
# Verify API is accessible from your Mac
curl https://api.truledgr.app/health

# Check DNS resolution
nslookup api.truledgr.app
```

### 3. Certificate Pinning Issues

If you implement certificate pinning in the future, you may need to:

1. Get the certificate hash:
```bash
openssl s_client -showcerts -connect api.truledgr.app:443 </dev/null 2>/dev/null | \
  openssl x509 -outform DER | \
  openssl dgst -sha256 -binary | \
  openssl enc -base64
```

2. Add to `network_security_config.xml`:
```xml
<domain-config>
    <domain includeSubdomains="true">api.truledgr.app</domain>
    <pin-set>
        <pin digest="SHA-256">HASH_HERE</pin>
    </pin-set>
</domain-config>
```

## Debugging Tools

### View Logcat Output

```bash
# View all TruLedgr logs
adb logcat | grep TruLedgr

# View SSL-related logs
adb logcat | grep -i ssl

# View network-related logs
adb logcat | grep -E "(TruLedgr|HttpURLConnection|SSL)"
```

### Android Studio Logcat
1. View → Tool Windows → Logcat
2. Filter by "TruLedgr" tag
3. Look for error messages with 🔍, ❌, ✅ emojis

### Test with Charles Proxy or Postman
1. Set up proxy on your Mac
2. Configure emulator to use proxy:
   ```bash
   adb shell settings put global http_proxy <your_mac_ip>:8888
   ```
3. Install proxy CA certificate on emulator

## App Behavior

The app will try multiple endpoints in order:
1. `https://api.truledgr.app/health` (primary)
2. Additional fallback endpoints can be added in `MainActivity.kt`

If all endpoints fail, you'll see an error message with details.

## Configuration Files

### network_security_config.xml
Located: `android/app/src/main/res/xml/network_security_config.xml`

**Debug Configuration:**
- Trusts system CAs
- Trusts user-installed CAs (for debugging)
- Allows SSL inspection tools in debug builds

**Production Configuration:**
- Only trusts system CAs
- No cleartext traffic allowed
- Strict certificate validation

### AndroidManifest.xml
```xml
<application
    android:networkSecurityConfig="@xml/network_security_config"
    android:usesCleartextTraffic="false"
    ...>
```

## Environment-Specific Testing

### Local Development (localhost)
Not recommended for Android due to emulator networking complexity.
Use the production API or deploy to a test server.

### Staging/Production
Current setup:
- Production API: `https://api.truledgr.app`
- SSL certificate: Let's Encrypt (or similar)
- Should work on physical devices

## Best Practices

1. **Always test on physical devices before release**
   - Emulators don't perfectly replicate real-world conditions
   - SSL issues in emulators often don't occur on devices

2. **Use proper certificate validation**
   - Don't disable SSL validation in production
   - The current config is safe (only relaxed in debug mode)

3. **Monitor certificate expiration**
   - Let's Encrypt certificates expire every 90 days
   - Set up auto-renewal

4. **Use certificate pinning for high security** (future)
   - Protects against MITM attacks
   - Requires updating app when certificate changes

## Quick Reference

| Issue | Solution |
|-------|----------|
| SSLHandshakeException | Test on physical device or update emulator |
| UnknownHostException | Check network/DNS, restart emulator |
| Certificate expired | Update API server certificate |
| Self-signed cert | Add to trusted anchors (dev only) |
| Emulator can't reach internet | Cold boot emulator, check host network |

## Getting Help

If you're still experiencing issues:

1. Check Android Studio Logcat for detailed error messages
2. Run `adb logcat | grep TruLedgr` to see all app logs
3. Verify the API is accessible from your Mac: `curl https://api.truledgr.app/health`
4. Try on a physical Android device
5. Check the [Android Network Security Config documentation](https://developer.android.com/training/articles/security-config)

## Related Files

- `android/app/src/main/java/technology/mcguire/truledgr/MainActivity.kt` - API client code
- `android/app/src/main/res/xml/network_security_config.xml` - Network security configuration
- `android/app/src/main/AndroidManifest.xml` - App manifest with network config reference
- `MOBILE_APPS_README.md` - General mobile app setup guide
