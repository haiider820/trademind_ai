# Required Keys and Your Side Setup

## API Keys I Need From You

### Mandatory for MVP
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `BINANCE_BASE_URL` (default already set to `https://api.binance.com`)

### Mandatory for Mobile Notifications
- `FIREBASE_PROJECT_ID`
- `FIREBASE_API_KEY`
- `FIREBASE_APP_ID_ANDROID`
- `FIREBASE_APP_ID_IOS`
- `FIREBASE_SENDER_ID`
- `FIREBASE_SERVICE_ACCOUNT_PATH` (FCM v1 service account JSON path used by backend)

### Mandatory for AI (Phase 2)
- `GEMINI_API_KEY`

### Optional (Phase 2/3)
- `TWELVEDATA_API_KEY` (forex feed)
- `WHALE_ALERT_API_KEY` (whale tracking)
- `REDIS_URL` (caching/rate limiting)
- `SENTRY_DSN` (error monitoring)

## Where To Put Them

### Backend
- Fill [backend/.env.example](D:/My Projects/crypto/backend/.env.example) values into `backend/.env`.

### Flutter Run-Time
- Optional overrides with `--dart-define`:
  - `SUPABASE_URL`
  - `SUPABASE_ANON_KEY`
  - `API_BASE_URL`

If you do not pass them:
- Flutter uses the built-in public Supabase config for local development.
- Web uses `http://localhost:8000/api/v1`.
- Android emulator uses `http://10.0.2.2:8000/api/v1`.

Example:

```bash
flutter run
```

If you want to override the defaults:

```bash
flutter run \
  --dart-define=SUPABASE_URL=... \
  --dart-define=SUPABASE_ANON_KEY=... \
  --dart-define=API_BASE_URL=http://localhost:8000/api/v1
```

## What You Must Do From Your Side

1. Create Supabase project and run SQL files in order:
   - [001_initial_schema.sql](D:/My Projects/crypto/backend/sql/001_initial_schema.sql)
   - [002_runtime_updates.sql](D:/My Projects/crypto/backend/sql/002_runtime_updates.sql)
2. In Supabase Auth, enable Email provider and confirm redirect settings.
3. Create Firebase project and register Android/iOS apps.
4. Download and place:
   - `android/app/google-services.json`
   - `ios/Runner/GoogleService-Info.plist`
5. Create Gemini key (and optionally TwelveData, Whale Alert).
6. Provide the keys to me (or fill env files locally) so I can wire live integrations completely.

## Notes
- News now uses free RSS aggregation (CoinDesk, Cointelegraph, Decrypt, Binance, Reuters) through backend logic, so no paid CryptoPanic dependency is required.
- Without these keys/accounts, the app can run with scaffolded UI and fallback data, but cannot provide full production real-time behavior and notifications.
