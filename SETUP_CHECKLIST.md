# Car Check AI - Setup Checklist

## Prerequisites
- [ ] Node.js 18+ installed
- [ ] Python 3.11+ installed
- [ ] Docker Desktop installed
- [ ] Git installed

## API Keys Needed
- [ ] MOT API Key (https://documentation.history.mot.api.gov.uk/)
- [ ] OpenAI API Key (https://platform.openai.com/)
- [ ] Stripe Keys (https://stripe.com/)
- [ ] Resend API Key (https://resend.com/)

## Setup Steps
1. [ ] Clone repository
2. [ ] Run `./scripts/setup.sh`
3. [ ] Edit `.env` with your API keys
4. [ ] Run `make dev`
5. [ ] Open http://localhost:3000

## Verification
- [ ] Frontend accessible at localhost:3000
- [ ] Backend API docs at localhost:8000/docs
- [ ] Database connection working
- [ ] Can create test check

For detailed instructions, see docs/QUICK_START.md
