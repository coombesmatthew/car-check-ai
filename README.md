# Car Check AI 🚗

AI-powered used car analysis using UK government MOT data and market intelligence.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 What It Does

Car Check AI helps UK car buyers avoid scams by:
- ✅ Detecting clocked (fraudulent) mileage using MOT history
- ✅ Identifying hidden damage from past MOT failures
- ✅ Providing accurate market valuations
- ✅ Generating negotiation strategies
- ✅ Creating inspection checklists

## 🏗️ Architecture

```
Frontend (Next.js) → API Gateway → Backend (FastAPI) → External APIs
                                          ↓
                                    PostgreSQL
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- Docker Desktop

### Setup

```bash
# Run setup script
chmod +x scripts/setup.sh
./scripts/setup.sh

# Edit .env with your API keys
nano .env

# Start development environment
make dev
```

- Frontend: http://localhost:3001
- Backend API: http://localhost:8001
- API Docs: http://localhost:8001/docs

## 📚 Documentation

- [Quick Start Guide](docs/QUICK_START.md)
- [Project Structure](docs/PROJECT_STRUCTURE.md)
- [Development Guide](docs/DEVELOPMENT.md)
- [Setup Checklist](SETUP_CHECKLIST.md)

## 🔑 Environment Variables

Required API keys:
- MOT_API_KEY - UK Government MOT History API
- OPENAI_API_KEY - OpenAI GPT-4
- STRIPE_SECRET_KEY - Stripe payments
- RESEND_API_KEY - Email service

See `.env.example` for complete list.

## 📈 Roadmap

- [x] MVP: MOT history analysis
- [x] Market price comparison
- [x] AI-powered report generation
- [ ] Mobile app
- [ ] B2B API for dealerships
- [ ] European market expansion

## 📄 License

MIT License - see [LICENSE](LICENSE)
