# TruLedgr API - Clean URL Structure

## 🚀 New Clean API Routes

Since we're using `api.truledgr.app` as our subdomain, the `/api/v1/` prefix was redundant. The API now has much cleaner, more intuitive endpoints.

### ✅ Updated Endpoints

| Old Route (Redundant) | New Clean Route | Purpose |
|----------------------|-----------------|---------|
| `/api/v1/auth/register` | `/auth/register` | User registration |
| `/api/v1/auth/login` | `/auth/login` | User authentication |  
| `/api/v1/users/me` | `/users/me` | Current user profile |
| `/api/v1/mobile/config` | `/mobile/config` | Mobile app config |
| `/api/v1/status` | `/status` | System status |

### 🌐 Live Examples

With our beautiful landing page at `https://api.truledgr.app`, users can now easily access:

- **Registration**: `POST https://api.truledgr.app/auth/register`
- **Login**: `POST https://api.truledgr.app/auth/login`
- **Profile**: `GET https://api.truledgr.app/users/me`
- **Mobile Config**: `GET https://api.truledgr.app/mobile/config`
- **Status**: `GET https://api.truledgr.app/status`

### 📱 Updated Integrations

✅ **Frontend (dash/src/services/api.ts)** - Updated all API calls
✅ **Mobile Documentation** - Updated all endpoint examples  
✅ **Landing Page** - Updated quick reference links
✅ **All Documentation** - Consistent with new structure

### 🎯 Benefits

1. **Simpler URLs**: `/auth/login` is much cleaner than `/api/v1/auth/login`
2. **Better UX**: Shorter, more memorable endpoints
3. **Consistent**: Makes sense with subdomain structure
4. **Professional**: Matches industry best practices for subdomain APIs

The API is now much more elegant and user-friendly while maintaining all functionality!
