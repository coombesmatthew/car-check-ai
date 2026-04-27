# Vericar B2B Strategy Notes

**Status:** Exploration only — no build planned yet. Marketing (B2C SEO + social) is the active workstream.
**Last updated:** 2026-04-23

---

## Competitive landscape

The UK vehicle-data B2B space is crowded at the top, thinner at the bottom.

| Tier | Players | Notes |
|---|---|---|
| Enterprise / franchise dealers | HPI Check (Solera), Experian AutoCheck, CAP HPI, Glass's, Cazana / Percayso, AutoTrader data products | Deep pockets, locked into DMS integrations (iVendi, Click Dealer, DealerWeb) |
| Mid-market / independents | Motorcheck, MyCarCheck, CarVeto | Have B2B tiers but it's not their main bet |
| **Underserved** | Small independents (10–50 car forecourts), part-time eBay / Marketplace flippers, auction buyers | Can't justify £100+/mo HPI subs; currently pay £10/check ad hoc |

---

## Why "trader subscription" doesn't work

A trader needs **provenance** (write-off, stolen, finance) — that's PREMIUM-tier data, ~£3.20/check in API costs (AutoCheck £2.00 + Brego £0.70 + CarGuide £0.50).

| Plan | Price/check | Cost/check | Margin |
|---|---|---|---|
| £49 / 50 checks | £0.98 | £3.20 | **−£2.22 (lose £111/mo)** |
| £99 / 200 checks | £0.49 | £3.20 | **−£2.71 (lose £542/mo)** |
| £160 / 50 checks | £3.20 | £3.20 | break-even |
| £320 / 50 checks | £6.40 | £3.20 | 50% — but at this price they buy HPI |

**Conclusion:** the reseller model is structurally broken at trader-friendly prices. Incumbents own the data and squeeze any reseller's margin. Stripping provenance to fix margins doesn't work either — provenance is the entire point of a trade check.

Also: One Auto's PAYG terms almost certainly prohibit B2B resale of HPI / AutoCheck / Brego data without a separate commercial agreement. Read T&Cs before doing anything past a landing page.

---

## Three B2B angles that don't fight margin

### 1. Whitelabel "trust badge" for dealers
Dealer pays 50p–£1 per car they list, embeds a "Vericar verified" report on each listing. Cost is FREE-tier (£0 — DVLA + MOT only). Margin healthy, dealer recovers it in the car price as a trust signal. Volume play.

### 2. Lead-gen flip ⭐ most promising
You don't sell *to* dealers, you sell *buyers* to them. Free B2C check → "3 dealers near you have similar cars in stock →" → revenue per click / lead. Auto Trader's whole business in miniature. Different product but uses your existing traffic — see implementation plan below.

### 3. Insurance / finance broker bundle
A broker pays you to run a soft check on every quote (cheaper than them buying HPI direct). B2B sales cycle is long but ticket is large. Save until there's traction elsewhere.

---

## Lead-gen implementation (the easy path)

### Phase 1 — Affiliate (1 day of work, zero ongoing cost)

1. Sign up to **Awin** (UK's biggest affiliate network — free, ~1 week to approve a publisher account).
2. Apply to programs for: **Motors.co.uk, Heycar, Carwow, Cinch, CarGurus**.
3. Add a CTA at the bottom of every report:
   > *"Looking for a better one? See similar [Make] [Model]s near you →"*
   Link goes through affiliate, pre-filtered by make / model / postcode where possible.
4. Affiliate network handles dealer relationships, attribution, payment.

**Payouts:** typically 50p–£2 per click, sometimes £5–15 per qualified lead. Carwow pays meaningfully more for *new car* enquiries (£100s) — not Vericar's audience.

**Realistic maths:** if 30% of report viewers click out at £1 average per click → every 100 free checks ≈ £30 of pure-margin revenue, on top of paid conversions.

### Phase 2 — Aggregator API handoff (month 3+, only if Phase 1 validates)

A few aggregators (Carwow Used, Heycar) run their own dealer panels and accept lead handoff via API — bigger payouts than vanilla affiliate but require decent volume to get a conversation.

### Phase 3 — Direct dealer relationships (don't do this yet)

Sign up dealers, take £10–15/lead, build matching + dashboard. This is Auto Trader's entire moat (30 years to build). Skip until Phase 1 + 2 prove demand.

---

## Recommendation

1. **Do affiliate now** — free to set up, small CTA addition to the report template, costs nothing if no one clicks. Validates whether the audience is in-market for a *different* car after their check fails.
2. **Don't build trader subscriptions** — unit economics are broken until Vericar has HPI-scale volume to negotiate data rates.
3. **Whitelabel widget** is the second-best option if affiliate CTR is low — pure margin, uses existing pipeline.

---

## Open questions for later

- One Auto T&Cs: what's actually permitted re. B2B resale, whitelabel embedding, lead-gen attribution?
- PostHog data: once enough traffic, measure the "free check → exits without paying" cohort — that's the affiliate target audience.
- Awin alternative: CJ Affiliate, Skimlinks, Impact — worth a comparison if Awin approval drags.
