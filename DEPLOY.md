# VeriCar — Deployment Guide

## Architecture

```
Cloudflare (DNS + CDN + SSL)
    ├── vericar.co.uk → Frontend (Next.js on Railway)
    └── api.vericar.co.uk → Backend (FastAPI on Railway)
                                ├── PostgreSQL (Railway addon)
                                └── Redis (Railway addon)
```

## Step 1: Railway Setup (~10 minutes)

1. Go to [railway.app](https://railway.app) and sign up with GitHub
2. Create a new project → "Deploy from GitHub repo"
3. Select the car-check-ai repo

### Create 4 services:

**Service 1: PostgreSQL**
- Click "New" → "Database" → "PostgreSQL"
- Railway auto-provisions it. Note the `DATABASE_URL` from the Variables tab.

**Service 2: Redis**
- Click "New" → "Database" → "Redis"
- Railway auto-provisions it. Note the `REDIS_URL` from the Variables tab.

**Service 3: Backend**
- Click "New" → "GitHub Repo" → select repo
- Set root directory: `backend`
- Add environment variables (see below)
- Railway auto-detects the Dockerfile

**Service 4: Frontend**
- Click "New" → "GitHub Repo" → select repo
- Set root directory: `frontend`
- Add build args: `NEXT_PUBLIC_API_URL=https://api.vericar.co.uk`
- Railway auto-detects the Dockerfile

### Backend Environment Variables

```
DATABASE_URL=<from Railway PostgreSQL>
REDIS_URL=<from Railway Redis>
DEBUG=false
SECRET_KEY=<generate: python -c "import secrets; print(secrets.token_urlsafe(32))">
ALLOWED_ORIGINS=["https://vericar.co.uk","https://www.vericar.co.uk"]
STRIPE_SECRET_KEY=<from Stripe>
STRIPE_WEBHOOK_SECRET=<from Stripe webhook setup>
RESEND_API_KEY=<from Resend>
ANTHROPIC_API_KEY=<your key>
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929
DVLA_VES_API_KEY=<when approved>
MOT_API_KEY=<when approved>
```

### Generate domains in Railway
- Backend service → Settings → Generate Domain → get `backend-xxx.up.railway.app`
- Frontend service → Settings → Generate Domain → get `frontend-xxx.up.railway.app`

## Step 2: Cloudflare DNS (~5 minutes)

Go to Cloudflare → vericar.co.uk → DNS → Add records:

| Type | Name | Content | Proxy |
|------|------|---------|-------|
| CNAME | `@` | `frontend-xxx.up.railway.app` | Proxied (orange cloud) |
| CNAME | `www` | `frontend-xxx.up.railway.app` | Proxied (orange cloud) |
| CNAME | `api` | `backend-xxx.up.railway.app` | Proxied (orange cloud) |

### Cloudflare SSL Settings
- SSL/TLS → Overview → Set to **Full (strict)**
- SSL/TLS → Edge Certificates → Always Use HTTPS: **ON**
- SSL/TLS → Edge Certificates → Minimum TLS Version: **1.2**

### Cloudflare Custom Domains in Railway
- Backend service → Settings → Custom Domain → `api.vericar.co.uk`
- Frontend service → Settings → Custom Domain → `vericar.co.uk`

## Step 3: Stripe Webhook (~2 minutes)

1. Stripe Dashboard → Developers → Webhooks → Add endpoint
2. URL: `https://api.vericar.co.uk/api/v1/checks/basic/webhook`
3. Events: `checkout.session.completed`
4. Copy the webhook signing secret → add to Railway backend env as `STRIPE_WEBHOOK_SECRET`

## Step 4: Verify

```bash
# Health check
curl https://api.vericar.co.uk/health

# Test free check
curl -X POST https://api.vericar.co.uk/api/v1/checks/free \
  -H "Content-Type: application/json" \
  -d '{"registration": "DEMO1"}'

# Visit site
open https://vericar.co.uk
```

## Costs (Monthly)

| Service | Free Tier | After Free Tier |
|---------|-----------|-----------------|
| Railway | $5 credit/month | ~$5-10/month |
| Cloudflare | Free | Free |
| Stripe | 1.4% + 20p per txn | Same |
| Resend | 3,000 emails/month free | $20/month for 50k |
| Anthropic | Pay per use (~2p per report) | Same |

**Total at launch: ~$5/month** (covered by Railway free credit)
**Break-even: 2 paid reports/month** covers hosting costs.
