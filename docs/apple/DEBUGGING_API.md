# Debugging iOS App API Connection

If the iOS app shows "API is DOWN" but the API is actually up, follow these debugging steps:

## 1. Check Xcode Console Output

The app now prints detailed logging. To view it:

1. Run the app in Xcode (Cmd+R)
2. Open the **Debug Area**: View → Debug Area → Activate Console (Cmd+Shift+Y)
3. Click "Check API Status" button in the app
4. Look for console output like:

```
🚀 API request started to: https://api.truledgr.app/health
✅ HTTP Status: 200
📡 Response: {"status":"healthy","message":"Bonjour, TruLedgr is running!"}
```

Or error messages like:
```
❌ API Error: [NSURLErrorDomain:-1009] The Internet connection appears to be offline.
```

## 2. Common Issues and Solutions

### Issue: "NSURLErrorDomain:-1009" (No Internet)
**Symptom**: Error mentions "Internet connection appears to be offline"

**Solutions**:
- iOS Simulator might not have network access
- Check Mac's internet connection
- Try: Simulator → Device → Restart
- Try: Xcode → Product → Clean Build Folder (Cmd+Shift+K)

### Issue: "NSURLErrorDomain:-1200" (SSL Error)
**Symptom**: Error mentions SSL or certificate issues

**Solutions**:
- Certificate issue with the API server
- Try accessing https://api.truledgr.app/health in Safari
- Check if certificate is valid

### Issue: "NSURLErrorDomain:-1001" (Timeout)
**Symptom**: Request times out after 10 seconds

**Solutions**:
- API server might be slow or unreachable
- Check API server status
- Try increasing timeout in ContentView.swift

### Issue: HTTP 4xx or 5xx Status
**Symptom**: "HTTP 403", "HTTP 500", etc.

**Solutions**:
- API server returned an error
- Check API server logs
- Verify endpoint exists: `curl https://api.truledgr.app/health`

## 3. Test API from Terminal

Verify the API is accessible from your Mac:

```bash
# Basic test
curl https://api.truledgr.app/health

# Verbose test (shows full request/response)
curl -v https://api.truledgr.app/health

# Test with timeout
curl --max-time 5 https://api.truledgr.app/health
```

Expected response:
```json
{"status":"healthy","message":"Bonjour, TruLedgr is running!"}
```

## 4. Simulator Network Settings

If the simulator can't access the network:

1. **Restart Simulator**:
   - Device → Restart

2. **Reset Network Settings**:
   - Device → Erase All Content and Settings...
   - (Warning: This will reset the entire simulator)

3. **Check Mac Firewall**:
   - System Settings → Network → Firewall
   - Make sure it's not blocking the simulator

4. **Try Different Simulator**:
   - Create a new iPhone simulator
   - Or try testing on a physical device

## 5. Test with Local API

To test if the issue is with the production API or the app itself:

1. **Start local API**:
   ```bash
   cd /Users/nathan/Documents/TruLedgr
   ./start-api.sh
   ```

2. **Update ContentView.swift** (line ~97):
   ```swift
   guard let url = URL(string: "http://localhost:8000/health") else {
   ```

3. **Rebuild and test**

If local works but production doesn't:
- DNS resolution issue
- Firewall blocking external connections
- API server might be down (check externally)

## 6. Physical Device Testing

Test on a real iPhone/iPad to rule out simulator issues:

1. Connect device via USB
2. Select device in Xcode
3. Run app (Cmd+R)
4. Device must have internet connection (WiFi or cellular)

## 7. Check App Transport Security

The Info.plist should allow HTTPS connections (already configured):

```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
    <key>NSAllowsLocalNetworking</key>
    <true/>
</dict>
```

## 8. Xcode Debug Tips

**Enable Network Logging**:
1. Edit Scheme: Product → Scheme → Edit Scheme...
2. Run → Arguments → Environment Variables
3. Add: `CFNETWORK_DIAGNOSTICS` = `3`
4. This will show detailed network logs in console

**Check Network Activity**:
1. Debug Navigator (Cmd+7)
2. Network tab
3. Watch for API requests

## 9. Verify DNS Resolution

From terminal:
```bash
# Check if domain resolves
nslookup api.truledgr.app

# Test with dig
dig api.truledgr.app

# Test with ping
ping api.truledgr.app
```

Should show IP addresses like `162.159.140.98` and `172.66.0.96`

## 10. Current Code Features

The app now includes:
- ✅ 10-second timeout
- ✅ Cache policy set to ignore cache
- ✅ Detailed error logging with domain and code
- ✅ Response body logging
- ✅ Request start logging

Check the console for these logs when you tap "Check API Status"!

## Quick Checklist

- [ ] Check Xcode console for error messages (Cmd+Shift+Y)
- [ ] Verify API works from terminal: `curl https://api.truledgr.app/health`
- [ ] Try restarting the iOS Simulator
- [ ] Test on a physical device if available
- [ ] Check Mac's internet connection
- [ ] Look for firewall/antivirus blocking connections
