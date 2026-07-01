# TradeMind AI MVP Build Plan

## Phase 1 Scope (2 to 3 weeks)

Goal: ship a stable, usable product with auth, market dashboard, news, and signals.

### In Scope
- Supabase email/password auth
- Dashboard with BTC/ETH price, market cap, fear/greed, and trending coins
- News feed with sentiment tag
- Signal list + signal detail + live PnL
- Basic admin workflow for signal CRUD (backend protected with admin role)
- Push notification plumbing (signal-created event only)

### Out of Scope for Phase 1
- AI chat analysis
- MTF scanner
- Whale and liquidation tracking
- Learning module
- Premium subscription/payments

## Delivery Milestones

### Milestone 1: Foundation
- Flutter folder structure + Riverpod + Dio + Hive
- FastAPI project scaffold + health endpoint
- Supabase project setup + initial schema + RLS policies

### Milestone 2: Auth + Core Data
- Supabase Auth integration in Flutter
- Profile bootstrap on first login
- Market endpoints wired from Binance + fallback cache

### Milestone 3: Signals + News
- Signals list/detail endpoints
- Admin create/update/close signal endpoints
- RSS news aggregator endpoint + sentiment field (heuristic + optional Gemini)

### Milestone 4: QA + Deploy
- Render deployment
- Supabase env integration
- Crash-free smoke testing on Android + iOS

## Acceptance Criteria
- User can sign up, verify email, log in, log out.
- User can load dashboard data in under 2.5s on average mobile network.
- User can view active and closed signals with status and PnL.
- Admin can create and close a signal.
- Backend and app run with no hardcoded secrets.

## Technical Decisions
- Flutter + Riverpod state management
- Dio for networking with retry/interceptor
- Hive for local cache
- FastAPI async endpoints
- Supabase Postgres + Auth + Realtime

## Risk Register
- Free API limits (Binance/RSS feeds): add server-side caching + rate-limit guards.
- Notification complexity: keep Phase 1 notifications minimal.
- Scope creep: freeze non-MVP modules until Phase 1 release.
