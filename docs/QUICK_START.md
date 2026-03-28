# Quick Start Guide

## 60-Second Setup

```bash
# 1. Clone & enter directory
git clone https://github.com/coombesmatthew/car-check-ai.git
cd car-check-ai

# 2. Copy .env template
cp .env.example .env

# 3. Edit .env and add your API keys (see list below)
nano .env

# 4. Start everything with Docker
make dev

# 5. Open http://localhost:3001
```

## What You Need

### Required API Keys
1. **MOT API** (UK Government - free)
   - Apply: https://documentation.history.mot.api.gov.uk/
   - You'll get: `MOT_API_KEY`, `MOT_CLIENT_ID`, `MOT_CLIENT_SECRET`

2. **DVLA VES API** (UK Government - free)
   - Apply: https://developer-portal.driver-vehicle-licensing.api.gov.uk/
   - You'll get: `DVLA_VES_API_KEY`

3. **Anthropic Claude API** (for AI report generation)
   - Get key: https://console.anthropic.com/
   - You'll get: `ANTHROPIC_API_KEY`

4. **Stripe** (for payment processing)
   - Get test keys: https://dashboard.stripe.com/test/keys
   - You'll get: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`

5. **Resend** (for email delivery)
   - Get key: https://resend.com/api-keys
   - You'll get: `RESEND_API_KEY`

### Optional Keys (Premium features only)
- **One Auto API** — Experian checks, vehicle valuations, EV data
- **Sentry DSN** — error tracking (leave blank to skip)

## Access Your App

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:3001 |
| **Backend API** | http://localhost:8001 |
| **API Docs** | http://localhost:8001/docs |

## Test a Free Check

```bash
curl -X POST http://localhost:8001/api/v1/checks/free \
  -H "Content-Type: application/json" \
  -d '{"registration": "ABC1234"}'
```

Replace `ABC1234` with any UK registration plate to test.

## Available Commands

```bash
make dev            # Start all services
make stop           # Stop all services
make test-backend   # Run backend tests (pytest)
make test-frontend  # Run frontend tests (Jest)
make lint           # Run code linters
make logs           # Show live logs from all services
make db-reset       # Reset database & run migrations
make migrate        # Run pending migrations
```

## Troubleshooting

**Can't connect to API?**
- Check `docker-compose.yml` port mappings (should be 8001:8000, 3001:3000)
- Run `make logs` to check backend startup

**Database errors?**
- Run `make db-reset` to reset and re-migrate
- Check `POSTGRES_PASSWORD` in `docker-compose.yml`

**API key errors?**
- Verify keys are correctly set in `.env`
- Some APIs (MOT, DVLA) require IP whitelisting — check provider docs
- Test with `curl localhost:8001/docs` to access API documentation

For production deployment, see [DEPLOY.md](../DEPLOY.md)
