# VeriCar - Setup Checklist

## Prerequisites
- [ ] Node.js 18+ installed
- [ ] Python 3.11+ installed
- [ ] Docker Desktop installed
- [ ] Git installed

## Required API Keys
- [ ] MOT API Key (https://documentation.history.mot.api.gov.uk/)
- [ ] DVLA VES API Key (https://developer-portal.driver-vehicle-licensing.api.gov.uk/)
- [ ] Anthropic API Key (https://console.anthropic.com/)
- [ ] Stripe Test Keys (https://dashboard.stripe.com/test/keys)
- [ ] Resend API Key (https://resend.com/api-keys)

## Optional (Premium features)
- [ ] One Auto API Key (Experian, Brego, EV data)
- [ ] Sentry DSN (error tracking)

## Setup Steps

```bash
# 1. Clone repository
git clone https://github.com/coombesmatthew/car-check-ai.git
cd car-check-ai

# 2. Copy .env template and fill in your API keys
cp .env.example .env
nano .env

# 3. Start all services (Docker Compose)
make dev

# 4. Wait for services to be healthy (~30 seconds)
```

## Verification

- [ ] Frontend accessible at [http://localhost:3001](http://localhost:3001)
- [ ] Backend API docs at [http://localhost:8001/docs](http://localhost:8001/docs)
- [ ] Database connection working (check logs: `make logs`)
- [ ] Can perform a free check (enter vehicle registration)
- [ ] Stripe test checkout works (no actual charge)

## Common Make Commands

```bash
make dev              # Start all services (Docker Compose)
make stop             # Stop all services
make test-backend     # Run pytest tests
make test-frontend    # Run Jest tests
make lint             # Run code linters
make db-reset         # Reset database + run migrations
make logs             # View all service logs
```

## Troubleshooting

**Port already in use?**
```bash
# Check what's running on port 3001 or 8001
lsof -i :3001
lsof -i :8001

# Or change ports in docker-compose.yml
```

**Database connection failed?**
```bash
# Reset database and migrations
make db-reset
```

**API returning 401/403?**
- Verify API keys in `.env` are correct
- Check that API keys have proper permissions/scopes
- For DVLA/MOT APIs, ensure IPs are whitelisted if required

For deployment to production, see [DEPLOY.md](DEPLOY.md)
