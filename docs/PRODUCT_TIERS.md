# VeriCar Product Tiers & Cost Breakdown

Last updated: 2026-04-14

## Tier Summary

| Tier | Price | API Cost | Margin | Target |
|------|-------|----------|--------|--------|
| **FREE** | £0.00 | £0.00 | N/A | Lead generation |
| **BASIC** | £3.99 | ~£0.04 | ~£3.95 (99%) | Entry-level paid |
| **PREMIUM** | £9.99 | ~£3.58 | ~£6.41 (64%) | Full provenance |
| **EV Health** | £8.99 | ~£2.35 | ~£6.64 (74%) | EV battery focus |
| **EV Complete** | £13.99 | ~£5.95 | ~£8.04 (57%) | EV + full history |

## Data Sources Per Tier

### FREE (£0.00)
| Data Source | API | Cost | What It Provides |
|-------------|-----|------|-----------------|
| DVLA VES | gov.uk | Free | Make, model, year, colour, fuel, tax/MOT status, V5C date, CO2, Euro standard |
| DVSA MOT History | gov.uk | Free | Full MOT test history, mileage readings, advisories, failures, dangerous items |
| **Derived (no API)** | Internal | Free | Clocking detection, condition score, ULEZ/CAZ compliance, road tax calc, mileage timeline |

**Total API cost: £0.00**

---

### BASIC (£3.99)
| Data Source | API | Cost | What It Provides |
|-------------|-----|------|-----------------|
| Everything in FREE | | £0.00 | |
| Claude AI Report | Anthropic | ~£0.02 | 6-section buyer's report: condition assessment, value analysis, risk factors, repair budget, running costs, negotiation guidance |
| PDF Generation | WeasyPrint | Free | Branded PDF with cover, At a Glance checklist, AI sections, MOT history table, citations |
| Email Delivery | Resend | Free (3k/mo) | PDF attachment + HTML summary email |
| Stripe Processing | Stripe | ~£0.026 (1.4% + 20p) | Payment processing |

**Total API cost: ~£0.04**
**Gross margin: ~£3.95 (99%)**

Note: BASIC does NOT include Brego valuation. The AI report's value section uses available MOT/DVLA data only.

---

### PREMIUM (£9.99)
| Data Source | API | Cost | What It Provides |
|-------------|-----|------|-----------------|
| Everything in BASIC | | ~£0.04 | |
| Experian AutoCheck v3 | One Auto | ~£2.00 | Finance check, stolen check, write-off history, plate changes, keeper history, high-risk flags, previous searches |
| Brego Valuation | One Auto | ~£0.70 | Private sale, dealer forecourt, trade-in, part exchange valuations |
| CarGuide Salvage | One Auto | ~£0.50 | Salvage auction history |
| Stripe Processing | Stripe | ~£0.34 (1.4% + 20p) | Payment processing |

**Total API cost: ~£3.58**
**Gross margin: ~£6.41 (64%)**

PDF includes: full At a Glance checklist (7 items: stolen, finance, write-off, salvage, clocking, MOT, ULEZ), valuation table, provenance sections.

---

### EV Health (£8.99)
| Data Source | API | Cost | What It Provides |
|-------------|-----|------|-----------------|
| Everything in FREE | | £0.00 | |
| ClearWatt | One Auto | £1.50 | Battery health score, degradation %, real-world range estimate, warranty info |
| EVDB Pence Per Mile | One Auto | £0.50 | 9 range scenarios (3 temps x 3 driving styles), pence-per-mile charging costs |
| Claude AI Report (EV) | Anthropic | ~£0.02 | 7-section EV report: verdict, battery health, range reality, charging costs, ownership forecast, negotiation, final verdict |
| PDF + Email | | Free | Unified PDF template with EV sections (battery, range, charging, specs, lifespan) |
| Stripe Processing | Stripe | ~£0.33 (1.4% + 20p) | Payment processing |

**Total API cost: ~£2.35**
**Gross margin: ~£6.64 (74%)**

PDF includes: 3-item At a Glance (clocking, MOT, ULEZ), battery health card, range scenarios table, charging cost comparison.

Does NOT include: provenance checks, valuation, salvage, EV specs (EVDB Core Data not enabled), lifespan (AutoPredict not enabled).

---

### EV Complete (£13.99)
| Data Source | API | Cost | What It Provides |
|-------------|-----|------|-----------------|
| Everything in EV Health | | £2.35 | |
| Experian AutoCheck v3 | One Auto | ~£2.00 | Finance, stolen, write-off, plate changes, keeper history, high-risk, previous searches |
| Brego Valuation | One Auto | ~£0.70 | Private sale, dealer, trade-in, part exchange valuations |
| CarGuide Salvage | One Auto | ~£0.50 | Salvage auction history |
| Stripe Processing | Stripe | ~£0.40 (1.4% + 20p) | Payment processing |

**Total API cost: ~£5.95**
**Gross margin: ~£8.04 (57%)**

PDF includes: full At a Glance (7 items), ALL EV sections, provenance, valuation table, keeper history.

---

## What Each PDF Contains

### Report Sections (AI-Generated)

| Section | FREE | BASIC | PREMIUM | EV Health | EV Complete |
|---------|:----:|:-----:|:-------:|:---------:|:-----------:|
| Cover Page + Verdict | - | Yes | Yes | Yes | Yes |
| Vehicle Summary | - | Yes | Yes | Yes | Yes |
| At a Glance Checklist | - | 3 items | 7 items | 3 items | 7 items |
| 1. Overall Condition Assessment | - | Yes | Yes | - | - |
| 2. Value Analysis | - | Yes | Yes (richer) | - | - |
| 3. Risk Factors | - | Yes | Yes | - | - |
| 4. Repair Budget | - | Yes | Yes | - | - |
| 5. Running Costs | - | Yes | Yes | - | - |
| 6. Negotiation Guidance | - | Yes | Yes | - | - |
| Should You Buy This EV? | - | - | - | Yes | Yes |
| Battery Health Verdict | - | - | - | Yes | Yes |
| Range Reality Check | - | - | - | Yes | Yes |
| Charging & Running Costs | - | - | - | Yes | Yes |
| Ownership Forecast | - | - | - | Yes | Yes |
| Negotiation Points (EV) | - | - | - | Yes | Yes |

### Data Sections (Rendered from API data)

| Section | FREE | BASIC | PREMIUM | EV Health | EV Complete |
|---------|:----:|:-----:|:-------:|:---------:|:-----------:|
| Valuation Table | - | - | Yes | - | Yes |
| Battery Health Card | - | - | - | Yes | Yes |
| Range Estimate + Scenarios | - | - | - | Yes | Yes |
| Charging Costs Table | - | - | - | Yes | Yes |
| EV Specifications | - | - | - | Yes | Yes |
| Lifespan Prediction | - | - | - | Yes | Yes |
| MOT History Table | - | Yes | Yes | Yes | Yes |
| Mileage Timeline | - | Yes | Yes | Yes | Yes |
| Safety Rating | - | Yes | Yes | Yes | Yes |
| Data Sources + Citations | - | Yes | Yes | Yes | Yes |

---

## Unified Pipeline (As of 2026-04-14)

All paid tiers now use the same pipeline:

```
Orchestrator (tier-aware data fetching)
    |
AI Report Generator (Claude — different prompts for standard vs EV)
    |
PDF Generator (shared report.html template, sections appear/hide based on data)
    |
Email Sender (shared email template, tier badge varies)
```

### Key Files
- **Standard orchestrator**: `backend/app/services/check/orchestrator.py`
- **EV orchestrator**: `backend/app/services/ev/orchestrator.py`
- **Standard AI report**: `backend/app/services/ai/report_generator.py`
- **EV AI report**: `backend/app/services/ai/ev_report_generator.py`
- **Unified PDF**: `backend/app/services/report/pdf_generator.py` + `backend/templates/pdf/report.html`
- **Email**: `backend/app/services/notification/email_sender.py` + `backend/templates/email/report.html`
- **Stripe config**: `backend/app/services/payment/stripe_service.py` (TIER_CONFIG dict)
- **Schemas**: `backend/app/schemas/check.py`, `backend/app/schemas/ev.py`

### Stripe Tier Names
| Stripe Key | Orchestrator Tier | Price |
|------------|-------------------|-------|
| `basic` | `basic` | £3.99 (499p) |
| `premium` | `premium` | £9.99 (999p) |
| `ev` | `ev_health` | £8.99 (899p) |
| `ev_complete` | `ev_complete` | £13.99 (1399p) |

---

## One Auto API Pricing Reference

Source: `backend/fixtures/EV_API_Analysis.csv`

| Endpoint | Cost | Status | Used By |
|----------|------|--------|---------|
| Experian AutoCheck v3 | ~£2.00 | Active | PREMIUM, EV Complete |
| Brego Valuation | ~£0.70 | Active | PREMIUM, EV Complete |
| CarGuide Salvage | ~£0.50 | Active | PREMIUM, EV Complete |
| ClearWatt | £1.50 | Active | EV Health, EV Complete |
| EVDB Pence Per Mile | £0.50 | Active | EV Health, EV Complete |
| EVDB ID Search | £0.50 | Not enabled | - |
| EVDB Core Data | £0.50 | Not enabled | - |
| EVDB Range & Efficiency | £0.50 | Not enabled | - |
| EVDB Fast Charging | £0.50 | Not enabled | - |
| EVDB Onboard Charging | £0.50 | Not enabled | - |
| EVDB Vehicle Data | £0.50 | Not enabled | - |
| EVDB Bi-Directional | £0.50 | Not enabled (not relevant 2026) | - |
| EVDB Pricing/Grants | £0.50 | Not enabled | - |
| AutoPredict Predict | £0.10 | Not enabled | - |
| AutoPredict Statistics | £0.10 | Not enabled | - |

### Potential additions (would require One Auto plan upgrade)
- **EVDB Core Data (£0.50)**: Would populate EV Specs section in PDF (battery capacity, charge speeds, consumption)
- **AutoPredict Predict + Statistics (£0.20)**: Would populate Lifespan Prediction section in PDF
- Adding both to EV Health: cost goes from £2.35 → £3.05, margin drops from 74% → 66%

## Action Items

- [ ] Consider enabling EVDB Core Data (£0.50) — fills empty EV Specs section, high customer value
- [ ] Consider enabling AutoPredict (£0.20 total) — fills empty Lifespan section, medium value
- [ ] Consider adding Brego valuation to BASIC tier — would reduce margin to ~£3.25 but add perceived value
