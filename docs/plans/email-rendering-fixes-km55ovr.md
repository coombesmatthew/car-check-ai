# Plan: Fix three data-rendering bugs in the PREMIUM email

## Context

Customer hit three issues on a real KM55OVR PREMIUM test. API data is fine
(user confirmed SQL looks good), but the email template is misrendering
three provenance sections. The email is the customer's first and often
only view of the report — these bugs undermine trust in the product.

## Bugs (all confirmed in code)

### 1. Keeper History — blank count

The parser at `backend/app/services/data/oneauto_client.py:361` returns:

```python
{"keeper_count": item.get("number_previous_keepers"), ...}
```

And the schema `KeeperHistory` at `backend/app/schemas/check.py:246` defines the field as `keeper_count`.

But the email template at `backend/templates/email/report.html:810` reads:

```jinja
{{ keeper_history.total_keepers }}
```

Field-name mismatch. Jinja silently renders the empty string for a missing attribute → customer sees the label with a blank value.

### 2. Valuation — missing £ values

Brego's `/brego/currentandfuturevaluationsfromvrm/v2` returns:

```json
{"success": true, "result": {"valuations": [{"retail_low_valuation": 2255,
  "retail_average_valuation": 2719, "retail_high_valuation": 3193,
  "trade_low_valuation": 763, "trade_average_valuation": 1109,
  "trade_high_valuation": 1499, "current_mileage": 100440}],
  "brego_derivative_id": "...", "vehicle_identification_number": "...",
  "vehicle_desc": "MINI CONVERTIBLE DIESEL 1.6 Cooper D 2dr", ...}}
```

The valuation numbers are **nested inside a `valuations` array**. The parser at `oneauto_client.py:461-464` reads them from the top level:

```python
"private_sale": raw.get("retail_average_valuation"),   # always None
"dealer_forecourt": raw.get("retail_high_valuation"),  # always None
...
```

So every PREMIUM customer so far got a Valuation section showing only Condition / Mileage / Date — no actual £ numbers. The template's `{% if valuation.private_sale is not none %}` guards then correctly skip the value rows. The customer sees an empty shell.

### 3. Plate Changes — confusing "Marker" row

Experian's `cherished_data_items` includes non-transfer records. For KM55OVR the parser's output was:

| previous_plate | change_date | change_type |
|---|---|---|
| M8OOF | 2015-12-14 | Data Move |
| KM55OVR | 2009-04-20 | Marker |

Row 2 has the *current* plate (KM55OVR) listed as the *previous* plate, tagged "Marker". That's Experian's way of flagging the original plate history, not a genuine change event. The parser filter at `oneauto_client.py:337` (`prev != curr`) doesn't catch it because `curr` from that row refers to a different record's current plate.

Net result on the email: "2 CHANGES FOUND" with two rows, one of which makes no sense to a buyer.

## Recommended approach

Three small, independent fixes. All in one commit because they all land in the same flow (One Auto parser → email template). No schema changes, no migration.

### Fix 1: Keeper History template field

**File:** `backend/templates/email/report.html` line 810

Change:
```jinja
{{ keeper_history.total_keepers }}
```
to:
```jinja
{{ keeper_history.keeper_count or "Not available" }}
```

Also: add a `last_change_date` row right below, since the parser already surfaces it and it's meaningful to buyers (recent keeper change = flip risk).

Remove the `{% if keeper_history.keepers %}` detailed-timeline block — the parser doesn't produce per-keeper rows, so it's dead markup that never renders.

Check the PDF template (`backend/templates/pdf/report.html`) for the same bug — fix there too if present.

### Fix 2: Valuation parser — unwrap `valuations` array

**File:** `backend/app/services/data/oneauto_client.py` lines 444-469 (`parse_valuation`)

Pull the first valuation entry out of the array before reading fields:

```python
def parse_valuation(raw: Optional[Dict], mileage: int) -> Optional[Dict]:
    if raw is None:
        return None

    # Brego nests the £ figures inside a valuations[] array.
    # Pre-v2 endpoints returned them at the top level — support both shapes
    # defensively in case anything regresses.
    val_row = raw
    if isinstance(raw.get("valuations"), list) and raw["valuations"]:
        val_row = raw["valuations"][0]

    return {
        "private_sale": val_row.get("retail_average_valuation"),
        "dealer_forecourt": val_row.get("retail_high_valuation"),
        "trade_in": val_row.get("trade_average_valuation"),
        "part_exchange": val_row.get("trade_high_valuation"),
        "valuation_date": date.today().isoformat(),
        "mileage_used": val_row.get("current_mileage", mileage),
        "condition": "Mileage-adjusted",
        "data_source": "Brego",
    }
```

Also surface the low/high bracket values the template currently ignores:
- `retail_low_valuation` → could render as a range for Private Sale/Dealer
- `trade_low_valuation` → same for Trade-in

Optional follow-up, not blocking this fix.

### Fix 3: Plate Changes — filter Experian junk rows

**File:** `backend/app/services/data/oneauto_client.py` lines 327-349 (`_parse_plate_changes`)

Two additions to the filter:
1. Skip records where `previous_plate` matches the current registration (not a real transfer — Experian's way of marking the original).
2. Skip records where `transfer_type` is a non-transfer category ("Marker", "Data Move"). These are internal Experian audit events.

```python
# Accept the current registration so we can filter self-referential rows.
def _parse_plate_changes(raw: Optional[Dict], current_registration: str = "") -> Dict:
    if not raw:
        return _empty_plates()

    IGNORED_TYPES = {"Marker", "Data Move", ""}
    current = (current_registration or "").upper().replace(" ", "")

    items = raw.get("cherished_data_items") or []
    records = []
    for item in items:
        prev = item.get("previous_vehicle_registration_mark", "")
        curr = item.get("current_vehicle_registration_mark", "")
        tt = item.get("transfer_type", "Transfer")
        prev_norm = prev.upper().replace(" ", "")
        if not prev or not curr or prev == curr:
            continue
        if prev_norm == current:  # Self-referential — not a transfer
            continue
        if tt in IGNORED_TYPES:
            continue
        records.append({
            "previous_plate": prev,
            "change_date": item.get("cherished_plate_transfer_date", ""),
            "change_type": tt,
        })
    return {
        "changes_found": len(records) > 0,
        "record_count": len(records),
        "records": records,
        "data_source": "Experian",
    }
```

**Caller update:** `backend/app/services/check/orchestrator.py` already has `registration` available in `_fetch_oneauto_data`. Thread it through as `current_registration` into `parse_autocheck` → `_parse_plate_changes`. Small touch-up in 1–2 call sites.

**Email template touch-up** (`backend/templates/email/report.html` ~line 780):
Replace the header line "CHANGES FOUND" count with a clearer one-liner:

```jinja
<p>Current plate: <strong>{{ registration }}</strong>. Historical plates on record:</p>
```

Remove the "Type" column from the detail table (Experian's type codes aren't useful to buyers).

## Critical files

| File | Change |
|---|---|
| `backend/app/services/data/oneauto_client.py` | `parse_valuation` unwraps `valuations[]`; `_parse_plate_changes` gains a `current_registration` arg and filters Marker / Data Move / self-referential rows |
| `backend/app/services/check/orchestrator.py` | Thread `registration` into the plate-change parser |
| `backend/templates/email/report.html` | Keeper History: `total_keepers` → `keeper_count`; add `last_change_date`; remove dead timeline block. Plate Changes: clearer header, drop Type column. |
| `backend/templates/pdf/report.html` | Mirror any Keeper History + Plate Changes fixes if the same misrenders exist |

## Reuse

- **`KeeperHistory` schema** at `backend/app/schemas/check.py:245` — unchanged, already uses `keeper_count`. The mismatch was purely in the template.
- **`Valuation` schema** at `backend/app/schemas/check.py:223-242` — unchanged, parser fix is enough.
- **`_empty_plates()`** helper in `oneauto_client.py:441` — keep using it for the null-raw case.
- **`cache.set`** / api_calls table — already persisting the raw Brego response; once the parser is fixed, next test will re-fetch and re-cache cleanly (no migration or data fix needed).

## Verification

1. Deploy the fix. Clear the Redis cache for any previous KM55OVR entry (or wait out the TTL — DVLA 24 h, MOT 1 h) so the parser re-runs against the stored raw data.
2. Re-run the £9.99 PREMIUM checkout for KM55OVR with `TESTABC123`.
3. Read the email — verify:
   - **Keeper History** shows a number (`3` or whatever Experian returned for KM55OVR) plus the last change date.
   - **Valuation** shows four £ figures (Private Sale / Dealer Forecourt / Trade-in / Part Exchange) above the Condition / Mileage / Date rows.
   - **Plate Changes** now shows either "No plate changes recorded" or only the genuine M8OOF → KM55OVR transfer (one row, dated 2015-12-14), with the header clearly stating the current plate.
4. Query `api_calls` to cross-check the raw Brego response:

```sql
SELECT endpoint, response_body
FROM api_calls
WHERE registration = 'KM55OVR' AND endpoint LIKE '/brego/%'
ORDER BY created_at DESC LIMIT 1;
```

The raw body should contain `"valuations": [{ ... }]` with real £ figures — confirming the parser is now reaching them.

5. Run `backend/scripts/eval_reports.py --all` to verify the AI report generator's fixture-driven output hasn't regressed.

## Out of scope

- The low/high valuation bracket (could render Private Sale as a range) — noted for follow-up.
- Adding the `vehicle_desc` from Brego as a nicer vehicle label in the email header.
- Replacing the Experian-internal "Data Move" / "Marker" labels with customer-friendly descriptions in the PDF (the fix here drops them entirely from the email).
- Tightening the Verdict follow-up work from previous plans.
