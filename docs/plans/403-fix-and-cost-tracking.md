# Plan: Diagnose One Auto 403s + Build API Cost Tracking

## Context

Two related issues surfaced during the end-to-end test:

**(1) Three One Auto endpoints returned 403 for EA11OSE** (live registration, production):
- `/experian/autocheck/v3`
- `/brego/currentandfuturevaluationsfromvrm/v2`
- `/carguide/salvagecheck/v2`

We can't tell *why* they 403'd because the client at `backend/app/services/data/oneauto_client.py:31-43` swallows all errors into `None` and only logs the exception string — never the HTTP status or the response body. One Auto's response bodies normally carry an actionable message (e.g. `Product not enabled on account`, `IP not whitelisted`, `Key expired`).

Confirmed via Railway variables (read-only check):
- `ONEAUTO_API_URL=https://api.oneautoapi.com` (production, correct)
- `ONEAUTO_API_KEY` is set

So it's **not** a sandbox/prod URL mix-up. The 403 is coming from production, meaning the account, key, IP, or per-product subscription is the problem.

Compounding issue (separately flagged earlier, same day): when the 403 happens, the parsers at `oneauto_client.py:192-247` fall through to `_empty_finance()`, `_empty_stolen()`, `_empty_writeoff()`, `parse_salvage()`. Those stubs assert `finance_outstanding=False`, `stolen=False`, `written_off=False`, `salvage_found=False` — so the customer's PDF and email show ✅ "No Finance Outstanding — Clear — safe to purchase" even though **we never checked**. This is a customer-trust and potentially legal-liability bug.

**(2) No per-call cost visibility.** We burn One Auto and Anthropic credit on every paid check, and Anthropic calls silently on every eval run, but there's no log of "how much did today cost", "which registrations cost the most", or "is my margin on PREMIUM actually ~£6 or am I losing money on high-mileage vehicles with big MOT histories that use more tokens". Right now the only way to know spend is to log into each vendor dashboard.

## Recommended approach

**Ship A1, A2, and the DB persistence layer in this session.** Defer the admin cost-rollup endpoint and the refund-on-degraded logic until we've got eyes on the problem.

Execution order:
1. Copy this plan into the repo at `docs/plans/403-fix-and-cost-tracking.md` so it's persisted.
2. Ship the four things below together in one commit:
   - **A1** Log raw status + response body on One Auto non-2xx
   - **A2** Parsers return None on raw=None (kill the false-"Clear" fallback)
   - **B1** `api_calls` table + Alembic migration
   - **B2** Async DB session helper (`app/core/db.py`)
   - **B3** `record_api_call()` helper + wire into `_get()` in `oneauto_client.py` so every One Auto call persists: timestamp, endpoint, registration, HTTP status, response-body snippet, duration, error message
3. Chairman verifies the dashboard (One Auto Account → Your Plan; API Admin → API Keys → settings cog). See Phase A4 in the appendix.
4. Re-run end-to-end test with `TESTABC123`. Query `api_calls` directly in Postgres to see exactly what One Auto returned.
5. Deferred: refund-on-degraded (A3), cost tracking for other services (B4–B6), admin endpoint + auth (B7).

### Documented 403 causes (from [One Auto docs](https://docs.oneautoapi.com/knowledgebase/limiting-api-keys-to-specific-services/))

403 is returned in exactly one documented case: *"When calls are made to disabled services using a restricted key"*. Two dashboard places to check:

1. **Account → Your Plan** — per-service toggles for AutoCheck / Brego / CarGuide.
2. **API Admin → API Keys → settings cog → Services** — if "Restrict the API key to specific services" is on, the three failing services must be in the allowed list.

Third possibility not covered by this 403 docs page: IP restriction on the key (same settings cog, "Restrict by IP"). Railway Hobby doesn't have static egress IPs, so this must be OFF for the backend key.

**Parameters are correct.** Code was verified against the [One Auto docs](https://docs.oneautoapi.com/); endpoint paths and query params match the spec.

---

## Phase A: Diagnose & harden the One Auto client

### A1. Log raw response on non-2xx

**File:** `backend/app/services/data/oneauto_client.py:31-43`

Currently:
```python
async def _get(self, path: str, params: Dict) -> Optional[Dict]:
    try:
        resp = await self._client.get(path, params=params)
        data = resp.json()
        if data.get("success"):
            return data.get("result")
        error = data.get("result", {}).get("error") or data.get("error")
        logger.warning(f"One Auto API error on {path}: {error}")
        return None
    except Exception as e:
        logger.error(f"One Auto API request failed on {path}: {e}")
        return None
```

Change to check status code *before* JSON parsing and log the raw body text when it's not 200. Still returns `None` on failure (caller contract unchanged), but now we'll see exactly what 403 tells us:

```python
resp = await self._client.get(path, params=params)
if resp.status_code != 200:
    logger.error(
        f"One Auto {path} HTTP {resp.status_code}: {resp.text[:500]}"
    )
    return None
data = resp.json()
...
```

### A2. Stop the false "Clear" fallback

**File:** `backend/app/services/data/oneauto_client.py`

Parsers at lines 192 (`parse_autocheck`), 389 (`parse_valuation`), 415 (`parse_salvage`) must return `None` when `raw is None`, not the `_empty_*()` stubs. The stubs are only legitimate when the API responded but *that specific field* was missing — not when the whole call failed.

Targeted change:
```python
def parse_autocheck(raw: Optional[Dict]) -> Optional[Dict]:
    if raw is None:
        return None
    return { ... existing ... }

def parse_valuation(raw: Optional[Dict], mileage: int) -> Optional[Dict]:
    if raw is None:
        return None
    ... existing ...

def parse_salvage(raw: Optional[Dict]) -> Optional[Dict]:
    if raw is None:
        return None
    ... existing ...
```

Downstream (`check/orchestrator.py:397-465` `_build_provenance_from_raw`) already guards every field with `if fc:` / `if sc:` / `if val:` so None flows through safely. The email sender (`notification/email_sender.py:27-71`) and AI report generator (`ai/report_generator.py`) both treat `check_data.get("finance_check")` with explicit `if finance:` guards, so no cascade of changes is needed.

Net effect when One Auto 403s: the PDF/email omit the provenance section entirely rather than lying.

### A3. Auto-refund if a paid tier can't deliver its headline data

**File:** `backend/app/services/fulfilment.py` `_run_car_pipeline` and `_run_ev_pipeline`

If `tier == "premium"` and all of `finance_check`, `valuation`, `stolen_check` came back None, the customer paid £9.99 for a BASIC-quality report. Same for `ev_complete` — if provenance is missing, they paid £13.99 for an EV Health-quality report.

Detect this at end of the pipeline and:
1. Log a `paid_tier_degraded` error
2. Call `stripe.Refund.create(payment_intent=...)` via a new helper in `stripe_service.py`
3. Send a *different* email apologising + promising a retry later (or attach the degraded report with a note explaining the refund)
4. Still return success to the frontend trigger so the success page doesn't hang

New helper: `stripe_service.refund_session(session_id)`.

### A4. Chairman action (human — do in parallel)

Log into the One Auto dashboard and confirm, for live mode:
- Is the key `ctTBWM…8Vv` active?
- Are the three products explicitly enabled: AutoCheck v3, Brego current+future valuation, CarGuide salvage?
- Is the deployment's outbound IP whitelisted (if IP restrictions are enabled)?
- Is there billing/credit available for these products?

One Auto support may also flip a switch — worth pinging them with the exact 403 body once A1 ships and we can see it.

### A5. Verification

1. Deploy → retrigger a fulfilment (use `TESTABC123` promo code again).
2. `mcp__railway-mcp-server__get-logs` — the error log line now shows `HTTP 403: {...body...}` with the actual One Auto message. Paste that into the One Auto dashboard/support ticket.
3. Check the regenerated PDF for EA11OSE — the provenance section is either populated (if A4 fixed the root cause) or *absent* (not falsely green).
4. Confirm Stripe dashboard shows a refund for the test session if provenance was missing.

---

## Phase B: API cost tracking — DEFERRED (not in this session)

The design below is preserved for the follow-up session. Do not start this until Phase A is shipped, verified, and One Auto is healthy.

### B1. New model: `ApiCall`

**File:** `backend/app/models/api_call.py` (new)

```python
class ApiCall(Base):
    __tablename__ = "api_calls"
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), index=True)
    service: Mapped[str] = mapped_column(String(32), index=True)       # "oneauto", "anthropic", "dvla", "mot", "stripe", "resend"
    endpoint: Mapped[str] = mapped_column(String(128))                 # "/experian/autocheck/v3", "messages.create sonnet", ...
    status_code: Mapped[Optional[int]]
    duration_ms: Mapped[Optional[int]]
    cost_gbp: Mapped[Decimal] = mapped_column(Numeric(10, 4), default=0)
    registration: Mapped[Optional[str]] = mapped_column(String(16), index=True)
    tier: Mapped[Optional[str]] = mapped_column(String(16))            # "free" / "basic" / "premium" / "ev_health" / "ev_complete"
    session_id: Mapped[Optional[str]] = mapped_column(String(128))     # Stripe checkout session, for cost-per-customer rollup
    error: Mapped[Optional[str]] = mapped_column(String(512))
    tokens_in: Mapped[Optional[int]] = mapped_column(default=None)     # Anthropic only
    tokens_out: Mapped[Optional[int]] = mapped_column(default=None)
```

### B2. Alembic migration

**File:** `backend/alembic/versions/002_add_api_calls.py` (new)

Create the table with indexes on `created_at`, `service`, `registration`.

### B3. Async DB session helper

**File:** `backend/app/core/db.py` (new)

Use `sqlalchemy.ext.asyncio.async_sessionmaker` bound to `settings.DATABASE_URL` (converted to `postgresql+asyncpg://`). Expose a `get_session()` async context manager. Today there's no session helper — models exist at `app/models/check.py` but nothing persists them.

### B4. Billing cost lookup

**File:** `backend/app/core/billing.py` (new)

Simple dict keyed by `(service, endpoint)` returning the cost in GBP:

```python
COST_GBP = {
    ("oneauto", "/experian/autocheck/v3"): Decimal("2.00"),
    ("oneauto", "/brego/currentandfuturevaluationsfromvrm/v2"): Decimal("0.70"),
    ("oneauto", "/carguide/salvagecheck/v2"): Decimal("0.50"),
    ("oneauto", "/clearwatt/batteryhealth/v1"): Decimal("1.50"),
    ("oneauto", "/evdb/..."): Decimal("0.50"),
    ("oneauto", "/autopredict/..."): Decimal("0.35"),
    ("anthropic", "claude-sonnet-4-6"): "_calc_anthropic",   # per-token
    ("anthropic", "claude-haiku-4-5-20251001"): "_calc_anthropic",
    ("resend", "emails.send"): Decimal("0.001"),
    ("dvla", "*"): Decimal("0"),
    ("mot", "*"): Decimal("0"),
    ("stripe", "*"): Decimal("0"),
}
```

Per-token Anthropic cost: use published 2026 rates (Sonnet 4.6: $3/Mtok in, $15/Mtok out; Haiku 4.5: $0.80/Mtok in, $4/Mtok out). Convert to GBP at a fixed rate in config (`GBP_USD_RATE: float = 0.78`), revisit quarterly.

Pull rates from `CLAUDE.md`/`MEMORY.md` product-tier table — the per-call rates there are the source of truth.

### B5. Tracking decorator

**File:** `backend/app/core/tracking.py` (new)

```python
@asynccontextmanager
async def track_api_call(
    service: str,
    endpoint: str,
    *,
    registration: str | None = None,
    tier: str | None = None,
    session_id: str | None = None,
):
    start = time.perf_counter()
    record = {"service": service, "endpoint": endpoint, ...}
    try:
        yield record   # caller can set status_code, tokens, error
    finally:
        record["duration_ms"] = int((time.perf_counter() - start) * 1000)
        record["cost_gbp"] = lookup_cost(service, endpoint, record)
        await persist_api_call(record)  # fire-and-forget DB insert
```

### B6. Instrument outbound clients

Wrap the 6 cost-bearing call sites:

| File | Line | Service | Endpoint |
|---|---|---|---|
| `oneauto_client.py` | `_get` wrapper, all 6 endpoints | `oneauto` | path arg |
| `ai/report_generator.py` | 810 | `anthropic` | model name |
| `ai/ev_report_generator.py` | 396, 634 | `anthropic` | model name |
| `ai/tiktok_script_generator.py` | 89 | `anthropic` | model name |
| `notification/email_sender.py` | 234 | `resend` | `emails.send` |
| `scripts/eval_reports.py` (judge call) | `_judge` | `anthropic` | model name |

Free services (DVLA/MOT/Stripe) can be tracked too with cost=0 for a complete audit trail — optional, do last.

### B7. Admin endpoint

**File:** `backend/app/api/v1/endpoints/admin.py` (new)

```
GET /admin/costs?window=24h|7d|30d
Authorization: Bearer {ADMIN_API_KEY}
```

Response:
```json
{
  "window": "24h",
  "total_gbp": "4.73",
  "by_service": { "anthropic": "0.62", "oneauto": "3.98", "resend": "0.13" },
  "by_tier": { "free": "0.00", "premium": "2.94", "ev_complete": "1.79" },
  "call_count": 127,
  "top_registrations": [ {"registration": "EA11OSE", "cost_gbp": "3.58", "calls": 5}, ... ]
}
```

New env var: `ADMIN_API_KEY` (32-byte urlsafe token). Dependency `Depends(require_admin)` at the top of the admin router compares the bearer token in constant time.

Register router in `backend/app/api/v1/router.py`.

### B8. Verification

1. `alembic upgrade head` in Railway deployment succeeds, `api_calls` table exists.
2. Run a PREMIUM check end-to-end, query: `SELECT service, endpoint, cost_gbp, duration_ms FROM api_calls ORDER BY created_at DESC LIMIT 20;` — see one row per outbound call.
3. `curl -H "Authorization: Bearer $ADMIN_API_KEY" https://api.vericar.co.uk/api/v1/admin/costs?window=24h` returns the rollup JSON.
4. Run `eval_reports.py --all` and verify the 3 Sonnet calls + 3 Haiku judge calls appear as `anthropic` entries with non-zero `cost_gbp`.

---

## Critical files

Phase A:
| File | Change |
|---|---|
| `backend/app/services/data/oneauto_client.py` | Log raw body on non-2xx; parsers return None on raw=None |
| `backend/app/services/fulfilment.py` | Detect degraded paid-tier and trigger refund |
| `backend/app/services/payment/stripe_service.py` | Add `refund_session(session_id)` helper |

Phase B:
| File | Change |
|---|---|
| `backend/app/models/api_call.py` | NEW — ApiCall ORM model |
| `backend/alembic/versions/002_add_api_calls.py` | NEW — migration |
| `backend/app/core/db.py` | NEW — async session helper |
| `backend/app/core/billing.py` | NEW — cost lookup |
| `backend/app/core/tracking.py` | NEW — `track_api_call` context manager |
| `backend/app/core/config.py` | `ADMIN_API_KEY`, `GBP_USD_RATE` |
| `backend/app/api/v1/endpoints/admin.py` | NEW — admin routes |
| `backend/app/api/v1/router.py` | Register admin router |
| `backend/app/services/data/oneauto_client.py` | Wrap `_get` with tracker |
| `backend/app/services/ai/report_generator.py` | Wrap `messages.create` |
| `backend/app/services/ai/ev_report_generator.py` | Wrap 2 `messages.create` sites |
| `backend/app/services/notification/email_sender.py` | Wrap `Emails.send` |

## Reuse

- **Alembic** already configured (`backend/alembic/env.py`, `alembic.ini`). One migration exists (`001_add_product_column.py`).
- **`Base`** from `app/models/base.py:1-5` — extend for `ApiCall`.
- **`CacheService.increment`** at `app/core/cache.py:77-85` — reuse if we want a fast in-memory "today's spend" counter alongside DB persistence.
- **Session-ID fallback** in `fulfilment.py` — already tracks Stripe `session_id`; pipe through to `track_api_call`.
- **`settings` pattern** — add `ADMIN_API_KEY`, `GBP_USD_RATE`, `ONEAUTO_API_URL` overrides here.
- **Bearer-token pattern** — FastAPI `HTTPBearer` security dependency, standard pattern, no library needed.

## Phase A vs B ordering

Phase A is the bug fix. Phase B is a build. Ship A first (today), then plan B as a separate commit — they don't share code.

## Out of scope

- Dashboard UI for `/admin/costs` — JSON response is enough for now; can add a minimal HTML admin page later.
- Cost forecasting / budgeting alerts (e.g. "alert me if daily spend >£50").
- Per-customer margin tracking (would need linking `api_calls.session_id` to `payments.amount`).
- Tracking the frontend side's Claude Code tool calls (this is Vericar's own product spend only).
- Tracking DVLA/MOT/Stripe — free services, worth a follow-up for complete audit but not urgent.
