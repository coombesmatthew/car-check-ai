# Vericar Marketing Strategy

**Owner:** Matthew (Chairman) + Claude (CMO)
**Last updated:** 2026-04-23
**Status:** Month 1 execution plan — no paid ads

---

## 1. Positioning

**One-liner:** *Vericar is the car check that actually explains itself — DVLA, MOT, finance, write-off and valuation data, read back to you in plain English by AI, for a third of what HPI charge.*

**Who we're for:** UK private used-car buyers, £5k–£25k budget, actively shopping on AutoTrader / Gumtree / Facebook Marketplace, who either (a) don't trust the seller and don't know what to check, or (b) want a HPI-style report without paying £20.

**Why we win:**
- **Free first check** — removes friction. Lead magnet built into the product.
- **AI-written report** — easier to read than raw HPI data. Differentiator vs. HPI/AA/RAC.
- **Price** — BASIC £3.99 vs HPI £19.99. 5× cheaper for the same intent.
- **EV-specific tier** — no competitor offers a battery-health-focused check at this price.

**What we're not:** Not a dealer tool, not a trade valuation service, not a scam-reporting site. Consumer-only.

---

## 2. Channels

Two channels for month 1. No paid ads.

### 2.1 Short-form video (TikTok + Instagram Reels)
- **Cadence:** 1 reel/day, Chairman produces (Claude generates script, shot list, captions, hook variants).
- **Length:** 45–60s.
- **Format:** Real scraped listings → analyse live through Vericar → show red flags → CTA.
- **Editorial line:** We describe **data and red flags**, never accuse specific sellers of fraud. "Here's what Vericar flagged on this listing" — not "this is a scam."
- **CTA:** "Check your own car free at vericar.co.uk" in caption + bio link.

### 2.2 SEO — intent pages + evergreen guides
- **Intent pages:** Dedicated routes targeting commercial search queries. Free check form above fold. One page per intent.
- **Evergreen guides:** Blog content targeting informational queries that attach to buying intent. Internal-linked to intent pages.
- **No programmatic/per-VRM SEO** — personal-data risk, skip.
- **No listing-scrape-powered public pages** — scraping stays internal for reel content only.

---

## 3. Reel Content Engine

**Existing asset:** `backend/app/services/scraping/content_pipeline.py` already does:
1. Scrape Gumtree listings
2. Filter to those with VRMs
3. Run free Vericar check on each
4. Score for content-worthiness
5. Generate TikTok script (`app/services/ai/tiktok_script_generator.py`)

**Gap to close:** The pipeline outputs a script. We need it to output a **reel-ready brief** the Chairman can shoot from in 15 minutes.

### Reel brief format (one file per reel)
```
Listing: [anonymised — "£6,200 Ford Focus, 2014"]
Hook (pick one of 3):
  A — "This car is £2k underpriced. Here's why."
  B — "Three red flags in this listing most buyers miss."
  C — "Would you buy this? Let me check."
Shot list:
  0–3s: Hook + listing screenshot (blurred seller details)
  3–15s: Vericar tool on screen, enter VRM
  15–40s: Walk through red flags one by one
  40–55s: Verdict + "check your own at vericar.co.uk"
  55–60s: End card
Caption + hashtags: [generated]
On-screen text beats: [generated]
```

### Content rotation (so we don't look repetitive)
Week cycle, 7 post types:
1. **Mon — Red flags deep dive** (one listing, 3 issues)
2. **Tue — Explainer** ("What does Cat S actually mean?")
3. **Wed — Bargain or bin?** (would-you-buy engagement bait, comment reply fodder)
4. **Thu — Clocking spotter** (focus on mileage mismatch)
5. **Fri — EV special** (battery health, charging cost, lifespan)
6. **Sat — Comment reply** (reshoot from top comment on a previous reel)
7. **Sun — Buying tip** (non-listing, general advice — builds authority)

### Legal guardrails (NON-NEGOTIABLE)
- **Blur registration plate in every shot** — in listing photos AND in the Vericar screen.
- **Blur all seller identifiers** — name, username, phone, exact address (keep to town/region only), profile picture.
- **Never use the word "scam" about a specific listing.** Use: "red flag", "concerning", "something I'd want explained", "worth a closer look."
- **Never claim a specific seller is committing fraud.** Describe what the *data* shows, not intent.
- **Gumtree scraping stays internal.** Only the resulting reel (which is editorial commentary) is public. This is covered as fair-comment/review.

Reel briefs will carry this checklist at the top so it's on every shoot:

```
BLUR BEFORE POSTING:
☐ Reg plate (listing photos + Vericar screen)
☐ Seller name / username
☐ Phone number
☐ Exact address (town/region only)
☐ Profile picture
```

---

## 3.5 Cost-Efficient Content Sourcing

**Problem:** One Auto API calls cost ~£2–5 per vehicle. Running them on hundreds of scraped listings to *find* interesting ones would burn money fast.

**Principle:** **The free tier already is the filter.** DVLA VES + DVSA MOT are both free and surface almost every video-worthy red flag. One Auto is reserved for confirming a "hero" story, not for discovery.

### What the free APIs catch

| Red flag | Which free API shows it |
|---|---|
| **Clocking** (mileage went backwards) | DVSA MOT — full mileage history per test |
| **MOT horror show** (repeat fails, fatal defects) | DVSA MOT |
| **Plate change** (new plate hiding history) | DVLA VES — V5 change dates |
| **SORN-then-sold** (sat off-road for years) | DVLA VES |
| **Import** (Japanese/EU import = fewer records) | DVLA VES |
| **Colour change** not in listing photos | DVLA VES |
| **Tax/MOT expired**, sold anyway | Both |

### What only One Auto adds

- **Outstanding finance** (real gold for a "don't buy this" story)
- **Write-off category** (Cat N/S/B/D)
- **Stolen marker**
- **Valuation** (cheap-for-market confirmation)

### The filter stack (cheap → expensive)

```
1. SCRAPE (free)                   — ~500 listings/week
      ↓ filter: has VRM, not trade
2. LISTING HEURISTICS (free)       — ~100 listings
      ↓ flags: price outlier, "sold as seen", low pics, vague description
3. FREE CHECK (free, DVLA+MOT)     — ~30 listings get checked
      ↓ score: content-worthiness (clocking, MOT fails, plate changes)
4. TOP 7–10 → REEL BRIEFS          — 1/day for a week
5. ONE AUTO (paid, ~£2–5 each)     — 1–2/week MAX, only for hero stories
```

**Blended cost:** 30 free checks × £0 + 2 One Auto × £3 avg = **~£6/week** to fuel 7 reels. **~85p per reel in data cost.**

### Smart scraping — search queries that correlate with problem cars

The scrape step matters more than volume. Queries that over-index on reel-worthy cars:

- Self-declared write-offs: `"cat s"`, `"cat n"`, `"cat d"`, `"recorded damage"`
- Distress signals: `"quick sale"`, `"bargain"`, `"must go"`, `"spares or repairs"`, `"non-runner"`
- Protection-stripping: `"trade sale"`, `"sold as seen"`, `"export only"`, `"no px"`
- Thin listings: `"starts and drives"` (often minimal description = hiding something)
- **Price outliers:** calculate median £ per year/model from aggregate scrape, flag anything >25% below
- **Mileage outliers:** 2018 car with 200k miles (exhausted) or 20k miles (clocking risk)

### Two more free savings

1. **VRM cache** — don't re-check a VRM seen in the last 30 days. DVLA/MOT data changes rarely (MOT once/year per car). Expected 20–30% cache hit rate after a few weeks of scraping.
2. **Overnight batch** — scrape + free-check on a cron, not interactively. We're not time-sensitive.

### Rule of thumb

**One Auto is for finishing a story, not finding it.** We already suspect the car from the free check; One Auto confirms outstanding finance / write-off / stolen so the reel has a mic-drop moment. If One Auto confirms nothing surprising, don't post that one as a hero — keep it as a standard red-flag reel based on the free data.

### Scope additions (folds into §7D)

The reel brief generator needs:
- Query-pattern library (the correlates-with-problems queries above)
- Listing heuristics scorer (price outlier detection, description red-flag phrases, photo count, listing age)
- VRM cache table (`scraped_vrm_cache` — vrm, last_checked_at, last_score)
- One Auto gating: only fire when free-check score ≥ threshold AND the weekly content plan calls for a hero story

---

## 4. SEO Plan

### 4.1 Commercial intent pages (route → target query)
Priority order — build in this sequence.

| Route | Target query | Monthly UK volume (est) | Priority |
|---|---|---|---|
| `/free-car-check` | "free car check", "free vehicle check" | ~40k | P0 |
| `/mot-history-check` | "mot history check", "check mot history" | ~90k | P0 |
| `/hpi-check-alternative` | "hpi check alternative", "cheap hpi check" | ~8k | P0 |
| `/stolen-car-check` | "check if car is stolen", "stolen car check uk" | ~12k | P1 |
| `/outstanding-finance-check` | "car finance check", "outstanding finance check" | ~15k | P1 |
| `/ulez-checker` | "ulez checker", "is my car ulez compliant" | ~35k (seasonal) | P1 |
| `/ev-battery-check` | "ev battery health check", "used ev check" | ~4k (growing) | P2 |
| `/write-off-check` | "car write off check", "cat s check", "cat n check" | ~20k | P2 |

**Page template (each intent page gets):**
- H1 matching primary query exactly
- Free check form above fold (same component as homepage)
- 300–500 words of unique intent-matched copy
- FAQ schema (3–5 Q&As targeting long-tail variations)
- Internal links to 2–3 related guides
- Structured data: `WebPage` + `FAQPage` + `BreadcrumbList`
- Not duplicated from homepage — unique H1/H2/copy per page

### 4.2 Evergreen guides (`/blog/*`)
Priority order, month 1 target: 6 posts.

1. **How to spot a clocked car** — targets "how to tell if a car has been clocked"
2. **Cat N vs Cat S vs Cat B vs Cat D — what they actually mean** — write-off categories
3. **Outstanding finance on used cars — how to check and what happens if you don't** — finance intent
4. **ULEZ 2026 — what's changing and will your car still be compliant** — seasonal, high volume
5. **Used EV buying checklist — battery health, range loss, charging compatibility** — EV
6. **What is HPI and do you actually need it?** — competitor-comparison intent

Each post: 1,200–2,000 words, author + date, related-posts block, single clear CTA to free check, internal-linked to the relevant intent page.

### 4.3 Technical SEO baseline
- `robots.ts` and `sitemap.ts` already exist — verify all new routes auto-register.
- Submit sitemap to Google Search Console + Bing Webmaster Tools.
- Structured data on every page (Product/Service for tier pages, FAQPage on intent pages, Article on blog).
- Open Graph + Twitter cards on every route.
- Core Web Vitals: check against Lighthouse, aim ≥90 mobile.
- Internal linking: every blog post → at least 2 intent pages; every intent page → at least 2 blog posts.

---

## 5. Conversion Funnel

```
Reel (social)  →  bio link  →  vericar.co.uk  →  free check  →  paywall  →  paid report
SEO (organic)  →  intent page  →  free check  →  paywall  →  paid report
```

**Key metric:** free-check → paid-report conversion rate. Everything upstream is vanity until that number is known.

**Analytics needed (currently missing — build this first):**
- Page-view tracking with source attribution (UTM params on bio link + reel captions)
- Event: `free_check_submitted` with VRM source (homepage / intent page / which one)
- Event: `stripe_checkout_started`
- Event: `stripe_checkout_completed` (already logged, just needs GA/Plausible link)
- Funnel report: traffic source → free check → paid, weekly.

**Recommendation:** Plausible (privacy-first, cookie-less, £9/mo — acceptable spend because measurement is load-bearing). Alternative: GA4 (free, messier).

---

## 6. 30-Day Execution Plan

### Week 1 (Days 1–7) — Foundation
Goal: infrastructure ready, nothing posted yet.

| Day | Task | Owner |
|---|---|---|
| 1 | Analytics: set up Plausible, add conversion events | Claude |
| 1 | TikTok + Instagram business accounts, bio link, profile copy | Chairman |
| 2 | Build `/free-car-check` intent page | Claude |
| 3 | Build `/mot-history-check` intent page | Claude |
| 4 | Build `/hpi-check-alternative` intent page | Claude |
| 5 | Blog infrastructure: `/blog` MDX-based, layout, post-list, per-post route | Claude |
| 6 | Reel brief generator: extend `content_pipeline.py` to output the brief format from §3 | Claude |
| 7 | First 3 reels shot + queued (batch-produce to get ahead) | Chairman |

**End-of-week checkpoint:** 3 intent pages live, blog framework live, analytics wired, 3 reels queued.

### Week 2 (Days 8–14) — Content ramp
Goal: daily posting starts, first guides published.

| Day | Task | Owner |
|---|---|---|
| 8 | **Start daily reel posting.** 1/day from here on. | Chairman |
| 8 | Blog post: How to spot a clocked car | Claude |
| 9 | Blog post: Cat N/S/B/D explained | Claude |
| 10 | Build `/stolen-car-check` + `/outstanding-finance-check` intent pages | Claude |
| 11 | Blog post: Outstanding finance on used cars | Claude |
| 12 | Submit sitemap to Google Search Console + Bing Webmaster | Chairman |
| 13 | Review first-week reel analytics: which hooks/types got views? | Both |
| 14 | Iterate reel brief templates based on what worked | Claude |

**End-of-week checkpoint:** 5 intent pages, 3 blog posts, 7 reels posted, first week's attribution data in.

### Week 3 (Days 15–21) — Scale + iterate
Goal: double down on what worked in week 2, fill content gaps.

| Day | Task | Owner |
|---|---|---|
| 15 | Build `/ulez-checker` + `/ev-battery-check` intent pages | Claude |
| 16 | Blog post: ULEZ 2026 changes | Claude |
| 17 | Blog post: Used EV buying checklist | Claude |
| 18 | Technical SEO audit: Lighthouse, schema validation, internal links | Claude |
| 19 | Reddit + MoneySavingExpert seeding: 3 genuinely helpful replies with soft link | Chairman |
| 20 | Landing page hero A/B test based on best-performing reel hook | Claude |
| 21 | Review week 3 funnel: source → free check → paid conversion | Both |

**End-of-week checkpoint:** 7 intent pages, 5 blog posts, 14 reels posted, 2 organic channels seeded.

### Week 4 (Days 22–30) — Measure, cut, double down
Goal: know what's working, decide month 2.

| Day | Task | Owner |
|---|---|---|
| 22 | Build `/write-off-check` intent page | Claude |
| 23 | Blog post: What is HPI and do you need it | Claude |
| 24 | Keyword ranking report: which intent pages are indexed, where ranking | Claude |
| 25 | Reel content audit: top 5 by views, top 5 by clicks, pattern analysis | Claude |
| 26 | Conversion funnel report: CVR by source, by landing page, by tier | Claude |
| 27 | Chairman review: what's working, what to cut, month 2 priorities | Chairman |
| 28–30 | Backfill: finish any slipped tasks, tidy up, prep month 2 | Both |

**End-of-month output:**
- 8 intent pages live
- 6 evergreen blog posts
- ~23 reels posted
- Full attribution report: source → free check → paid CVR
- Month 2 plan based on real numbers

---

## 7. What Needs Building (Scope for Claude)

Grouped by dependency so the Chairman can see scope.

### A. Analytics + measurement (do first, day 1)
- Add Plausible tracking to `frontend/src/app/layout.tsx`
- Fire events: `free_check_submitted`, `stripe_checkout_started`, `stripe_checkout_completed`
- Document UTM scheme: `?utm_source=tiktok&utm_medium=social&utm_campaign=reel-YYYYMMDD`
- Add conversion funnel view (can start as a SQL query against Plausible export + `api_calls`/`stripe_events` tables)

### B. Intent-page framework (days 2–4, reused for remaining pages)
- New component `IntentPageLayout` — hero with free-check form, SEO copy slot, FAQ slot, internal-links slot
- Per-page content lives in MDX or structured JSON — each page is ~50 lines of content + the layout
- Structured data helper: `generateFAQSchema()`, `generateBreadcrumbSchema()`
- Build 3 pages in week 1 (free-car-check, mot-history-check, hpi-check-alternative) — proves the template

### C. Blog infrastructure (day 5)
- `/blog` uses MDX (`@next/mdx` or `contentlayer`)
- Post frontmatter: title, slug, description, date, author, cover, related
- `/blog` index (post list), `/blog/[slug]` (post page)
- Article schema on each post
- RSS feed (bonus, low-effort, useful for indexing)

### D. Reel brief generator (day 6)
- Extend `content_pipeline.py` to output `ReelBrief` object (hook variants, shot-list, caption, hashtags, on-screen text beats)
- New endpoint: `POST /internal/reel-brief` (admin-only, not public)
- CLI script: `python -m app.scripts.generate_reel_brief --query "ford focus" --top-n 5` — outputs 5 briefs as markdown
- **No public exposure** — internal tooling only

### E. Content writing (ongoing)
- Blog posts: Claude writes drafts, Chairman reviews + publishes
- Intent page copy: Claude writes per-page unique copy

---

## 8. What I Need From The Chairman (Human-Only Tasks)

Per operating framework — Claude doesn't do these:

- [ ] **TikTok Business account** — set up, link to vericar.co.uk in bio
- [ ] **Instagram Business account** — same, plus link to TikTok
- [ ] **Plausible Analytics** — sign up (£9/mo) OR tell Claude to use GA4 instead (free)
- [ ] **Google Search Console** — verify ownership of vericar.co.uk, submit sitemap
- [ ] **Bing Webmaster Tools** — same
- [ ] **Produce 1 reel/day from day 8** — Claude provides brief, Chairman shoots + edits + posts
- [ ] **Reddit/MSE seeding** — genuinely helpful replies, not spam. Claude suggests threads; Chairman posts under own account.
- [ ] **Content review** — blog drafts before publication (30 min per post)

**Money asks in this plan:**
- Plausible: £9/mo (optional — GA4 is free alternative)
- No other spend. All channels organic.

---

## 9. Risks + Mitigations

| Risk | Mitigation |
|---|---|
| **Defamation claim from named seller in a reel** | Editorial rules in §3. Blur identifying info. Never use "scam." Speak to the data, not intent. |
| **TikTok removes content for "harassment"** | Same — depersonalise listings. If a video gets removed, don't re-post; iterate tone. |
| **Gumtree ToS breach** | Scraping stays internal. Rate limit aggressive. Don't publish listing URLs or seller info. |
| **SEO doesn't land in month 1** | Expected. SEO lag is 4–12 weeks. Month 1 is infrastructure + content; ranking is a month 2–3 outcome. Reels carry traffic in month 1. |
| **Chairman burnout on daily posting** | Batch-produce. Week 1 goal is 3 reels banked before daily cadence starts. Keep a 3-reel buffer. |
| **Analytics not wired on day 1** | Everything else is vanity without it. This is the non-negotiable first task. |

---

## 10. Success Metrics (end of month 1)

**Input metrics (controllable):**
- 8 intent pages live
- 6 blog posts live
- 21+ reels posted
- Analytics + funnel reporting in place

**Output metrics (the question):**
- Total free checks run (baseline to beat in month 2)
- Traffic-source breakdown: organic / social / direct
- Free → paid CVR by source (this is the number)
- First reel to hit 10k views (signal for scale potential)
- First SEO page to rank top 10 (signal for channel viability)

**We don't optimise for follower count or views in isolation.** Only paid conversions and the funnel that produced them.

---

## 11. Month 2 Preview (not committed — depends on month 1 data)

Possible directions depending on what month 1 shows:

- **If reels convert:** double daily cadence (2/day), build reel-brief volume tooling.
- **If SEO starts ranking:** expand intent pages to long-tail (make/model specific, seasonal).
- **If neither:** reassess positioning. Probably means the free-check UX or paywall needs work, not the channels.
- **If both:** start testing low-cost paid (TikTok Spark Ads on top-performing organic reel, ~£5/day).

---

*End of document. Revise as month 1 data comes in.*
