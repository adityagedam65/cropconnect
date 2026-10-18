# CropConnect: Caching Strategy & CDN Architecture (Layer 12)

## 1. Caching Matrix Across Layers

| Candidate Resource | Cache Layer | TTL | Cache Key Strategy | Invalidation Trigger |
|---|---|:---:|---|---|
| **Vite JS / CSS Bundles** | Browser + Global CDN (Vercel) | 1 Year (`31536000s, immutable`) | Content hash in filename (e.g. `index-B1a9f.js`) | Rebuilt automatically on new git deployment |
| **PWA Static Assets & Icons** | Browser Service Worker | 30 Days | Asset path (`/icon-192.png`, `/favicon.ico`) | Service worker update lifecycle (`skipWaiting`) |
| **Public Landing Page** | Edge CDN (Vercel) | 1 Hour (`s-maxage=3600, stale-while-revalidate=86400`) | Request path (`/`, `/terms`, `/privacy`) | On new commit / manual deployment purge |
| **Mandi Commodity Prices** | Server Memory / Redis Cache | 4 Hours (`14400s`) | `mandi:commodity:{name}:state:{state}` | Periodic background refresh or midnight rollover |
| **Open-Meteo Weather Data**| Server Memory / Redis Cache | 1 Hour (`3600s`) | `weather:lat:{round(lat,2)}:lon:{round(lon,2)}` | Time-to-Live (TTL) expiry |
| **Authenticated Tenant Dashboard** | Client SessionStorage Only | 60 Seconds | `session:auth:{user_id}` | Cleared on logout, role change, or token expiration |
| **Live Telemetry & Pump State** | 🚫 **NEVER SHARED CACHED** | 0s (`no-store, private`) | Direct database / connection pool | Real-time state required for pump actuation |

---

## 2. Critical Multi-Tenant Caching Rules

> [!CAUTION]
> Caching tenant data at a shared CDN or shared proxy layer is a catastrophic security vulnerability leading to cross-tenant data leaks.

1. **Private by Default**: All responses under `/api/sensors`, `/api/pumps`, `/api/farm`, `/api/auth` MUST emit:
   ```http
   Cache-Control: private, no-cache, no-store, must-revalidate
   Pragma: no-cache
   Expires: 0
   ```
2. **Tenant Scoping in Keys**: Any application-level cache (Redis / in-memory) holding user or farm data MUST prefix keys with `org:{org_id}:` or `user:{user_id}:`:
   ```
   cache:org:1042:pump_schedule
   cache:org:1042:daily_telemetry_summary:2026-10-18
   ```
3. **Write-Through Invalidation**: Any write operation (`POST /api/pumps/{id}/toggle`, `PATCH /api/auth/profile`) invalidates all cached entries for that organization immediately.

---

## 3. CDN & HTTP Header Configuration Examples

### Static Assets (Vite Output):
```http
HTTP/2 200 OK
Content-Type: application/javascript
Cache-Control: public, max-age=31536000, immutable
ETag: "63f8-5e8a9b2"
```

### Public Marketing Pages:
```http
HTTP/2 200 OK
Content-Type: text/html; charset=utf-8
Cache-Control: public, max-age=0, s-maxage=3600, stale-while-revalidate=86400
```

### Authenticated API Responses:
```http
HTTP/2 200 OK
Content-Type: application/json
Cache-Control: private, no-cache, no-store, must-revalidate
X-Request-Id: 7b31e9a4
```
