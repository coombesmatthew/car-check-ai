# VeriCar — AI-Powered Used Car Analysis

AI-powered used car analysis using UK government data. Detect clocked mileage, hidden damage, and get fair valuations backed by AI-generated buyer's reports.

**Live at:** [vericar.co.uk](https://vericar.co.uk)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 What It Does

VeriCar helps UK car buyers make confident purchasing decisions by:
- ✅ **Detecting clocked mileage** via DVLA + MOT history analysis
- ✅ **Identifying hidden damage** from past MOT failures and defect patterns
- ✅ **Premium vehicle checks** including finance, stolen, write-off, valuation history
- ✅ **AI-generated buyer's reports** with negotiation strategies and cost projections
- ✅ **EV health analysis** with battery lifespan, real-world range, and charging costs

## 💳 Product Tiers

| | FREE | BASIC | PREMIUM | EV Health | EV Complete |
|---|------|-------|---------|-----------|-------------|
| **Price** | £0 | £3.99 | £9.99 | £8.99 | £13.99 |
| DVLA + MOT | ✅ | ✅ | ✅ | ✅ | ✅ |
| Clocking detection | ✅ | ✅ | ✅ | ✅ | ✅ |
| AI report + PDF | ❌ | ✅ | ✅ | ✅ | ✅ |
| Finance/Stolen/Write-off | ❌ | ❌ | ✅ | ❌ | ✅ |
| Valuation | ❌ | ❌ | ✅ | ❌ | ✅ |
| EV battery analysis | ❌ | ❌ | ❌ | ✅ | ✅ |

## 🏗️ Architecture

```
Cloudflare (DNS + CDN + SSL)
    ├── vericar.co.uk → Frontend (Next.js on Railway)
    └── api.vericar.co.uk → Backend (FastAPI on Railway)
                                ├── PostgreSQL (Railway)
                                └── Redis (Railway)
```

**Tech Stack:**
- **Backend**: FastAPI (Python 3.11), PostgreSQL 15, Redis 7
- **Frontend**: Next.js 14 (App Router), Tailwind CSS
- **Payments**: Stripe (test/live modes)
- **Email**: Resend (API-based)
- **AI**: Anthropic Claude API (report generation)
- **External APIs**: DVLA VES, DVSA MOT, One Auto (Experian, Brego, EV data)

## 🚀 Quick Start (Development)

### Prerequisites
- Node.js 18+
- Python 3.11+
- Docker Desktop

### Setup

```bash
# Clone repository
git clone https://github.com/coombesmatthew/car-check-ai.git
cd car-check-ai

# Install dependencies & start Docker
make dev
```

**Access:**
- Frontend: [http://localhost:3001](http://localhost:3001)
- Backend API: [http://localhost:8001](http://localhost:8001)
- API Docs: [http://localhost:8001/docs](http://localhost:8001/docs)

**For production deployment, see [DEPLOY.md](DEPLOY.md)**

## 🔑 Environment Variables

### Required
```
MOT_API_KEY              # UK Government MOT History API
DVLA_VES_API_KEY        # DVLA Vehicle Enquiry Service
ANTHROPIC_API_KEY       # Claude API for report generation
STRIPE_SECRET_KEY       # Stripe payments (test or live)
STRIPE_WEBHOOK_SECRET   # Stripe webhook signing secret
RESEND_API_KEY          # Email service API key
```

### Optional (Premium tier)
```
ONEAUTO_API_KEY         # One Auto (Experian, Brego, EV data)
SENTRY_DSN              # Error tracking (Sentry)
```

See `.env.example` and `.env.production.example` for complete list.

## 📈 Current Status

- ✅ **Fully Live** — All products (FREE, BASIC, PREMIUM, EV Health, EV Complete)
- ✅ **Payment Integration** — Stripe checkout + fulfillment flow working
- ✅ **Email Delivery** — PDF reports sent via Resend
- ✅ **AI Reports** — Claude-powered analysis with citations and cost tables
- ✅ **EV Analysis** — Battery health, range estimates, charging costs
- ✅ **Production Monitoring** — Sentry + Railway logs configured

## 📚 Documentation

- [Deployment Guide](DEPLOY.md) — Railway + Cloudflare setup
- [Operating Framework](CLAUDE.md) — Development principles
- Setup files: `.env.example`, `.env.production.example`

## 📄 License

MIT License - see [LICENSE](LICENSE)
