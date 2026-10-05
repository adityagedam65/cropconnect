# CropConnect Frontend

React + Vite dashboard for CropConnect farmers, sensor devices, market data, weather, AI help, and multilingual field workflows.

## Setup

```bash
npm install
cp .env.example .env
npm run dev
```

The local app runs at `http://localhost:3000`.

## Environment

```bash
VITE_BACKEND_URL=http://localhost:8001
VITE_PUBLIC_TRANSLATION_ENABLED=false
VITE_PUBLIC_TRANSLATION_FALLBACK_URL=
VITE_SENTRY_DSN=
```

Use the deployed Railway backend URL for production. Leave `VITE_SENTRY_DSN` blank to disable frontend error monitoring.

## Scripts

```bash
npm run dev
npm run build
npm run preview
npm run lint
npm run test
npm run check
```

## PWA Icons

The app includes `public/icon.svg` as the source icon. Before production release, export PNG versions to:

- `public/icon-192.png`
- `public/icon-512.png`

These PNG files are referenced by the web app manifest so Android and desktop install prompts display the correct CropConnect icon.

## Production Notes

- Sensor history is loaded from `/api/sensors/history` for the signed-in user's `sensorDeviceId`.
- Offline users see a banner and the app keeps showing the last known dashboard state.
- Sentry initializes only when `VITE_SENTRY_DSN` is configured.
- Build output is written to `build/` for Vercel.
