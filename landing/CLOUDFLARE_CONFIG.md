# Cloudflare Pages Configuration for TruLedgr Landing Page

## Domain Setup

- **Apex Domain**: truledgr.com
- **WWW Domain**: `www.truledgr.com`
- **API Domain**: `api.truledgr.app`
- **Dashboard Domain**: `dash.truledgr.app`
- **Cloudflare Project**: truledgr-www

## Build Configuration

- **Build Command**: `npm run build`
- **Build Output Directory**: `dist`
- **Root Directory**: `landing`

## Redirect Rules (Configure in Cloudflare Dashboard)

### Rule 1: WWW to Apex Redirect

**Rule Type**: Redirect Rule
**Rule Name**: WWW to Apex Redirect
**When incoming requests match**:

- Field: Hostname
- Operator: equals
- Value: `www.truledgr.com`

**Then**:

- Type: Static
- URL: `https://truledgr.com`
- Status Code: 301 (Permanent Redirect)
- Preserve query string: Yes

### Rule 2: HTTPS Enforcement (if not already configured)

**Rule Type**: Redirect Rule
**Rule Name**: Force HTTPS
**When incoming requests match**:

- Field: URI Full
- Operator: matches regex
- Value: `http://truledgr\.com/.*`

**Then**:

- Type: Dynamic
- Expression: `concat("https://", http.host, http.request.uri.path, if(http.request.uri.query != "", concat("?", http.request.uri.query), ""))`
- Status Code: 301
- Preserve query string: No

## Additional Recommendations

### Custom Domain Configuration

1. Add both domains to Cloudflare Pages:
   - truledgr.com (apex)
   - `www.truledgr.com` (www)

2. Set DNS records:
   - CNAME: `www.truledgr.com` → `truledgr-www.pages.dev`
   - A/AAAA: truledgr.com → Cloudflare Pages IP

### SSL/TLS Settings

- **SSL/TLS encryption mode**: Full (strict)
- **Always Use HTTPS**: Enabled
- **Automatic HTTPS Rewrites**: Enabled

### Performance Optimizations

- **Auto Minify**: Enable for HTML, CSS, JS
- **Brotli compression**: Enabled
- **HTTP/2**: Enabled
- **HTTP/3**: Enabled

## Testing the Redirect

After configuration, test the redirect:

```bash
# Test WWW to Apex redirect
curl -I https://www.truledgr.com

# Should return:
# HTTP/2 301
# Location: https://truledgr.com/
```

## Troubleshooting

1. **DNS Propagation**: May take up to 24 hours
2. **SSL Certificate**: Cloudflare provides automatic SSL
3. **Cache Issues**: Clear Cloudflare cache if needed
4. **Redirect Loop**: Ensure apex domain points to Pages, not redirecting to itself
