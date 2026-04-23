"use client";

import { useState } from "react";
import {
  FinanceCheck, StolenCheck, WriteOffCheck, Valuation,
  SalvageCheck, ImportStatusCheck, PlateChangeHistory, KeeperHistory,
  HighRiskCheck, PreviousSearches,
} from "@/lib/api";
import Card from "@/components/ui/Card";
import { DetailRow, icons } from "./shared";
import PremiumPreview from "./PremiumPreview";
import TheftAlertsCarousel from "./TheftAlertsCarousel";
import { computePriceVerdict, PriceVerdictTone } from "@/lib/priceVerdict";

const VERDICT_CLASSES: Record<PriceVerdictTone, { pill: string; bar: string; deltaText: string }> = {
  emerald: {
    pill: "bg-emerald-100 text-emerald-800 border-emerald-200",
    bar: "bg-emerald-500",
    deltaText: "text-emerald-700",
  },
  blue: {
    pill: "bg-blue-100 text-blue-800 border-blue-200",
    bar: "bg-blue-500",
    deltaText: "text-blue-700",
  },
  amber: {
    pill: "bg-amber-100 text-amber-800 border-amber-200",
    bar: "bg-amber-500",
    deltaText: "text-amber-700",
  },
  red: {
    pill: "bg-red-100 text-red-800 border-red-200",
    bar: "bg-red-500",
    deltaText: "text-red-700",
  },
};

interface FullCheckSectionProps {
  finance_check: FinanceCheck | null;
  stolen_check: StolenCheck | null;
  write_off_check: WriteOffCheck | null;
  valuation: Valuation | null;
  salvage_check: SalvageCheck | null;
  import_status: ImportStatusCheck | null;
  plate_changes: PlateChangeHistory | null;
  keeper_history: KeeperHistory | null;
  high_risk: HighRiskCheck | null;
  previous_searches: PreviousSearches | null;
  listing_price?: number | null;  // pence — buyer-entered asking price
  registration: string;
}

function AskingPriceBlock({
  listingPricePence,
  valuation,
}: {
  listingPricePence: number;
  valuation: Valuation;
}) {
  const [showDetail, setShowDetail] = useState(false);
  const verdict = computePriceVerdict(listingPricePence, valuation);
  if (!verdict) return null;
  const styles = VERDICT_CLASSES[verdict.tone];
  const listingPounds = Math.round(listingPricePence / 100);

  return (
    <div className="relative -mx-4 -mt-4 mb-4 px-4 pt-4 pb-4 border-b border-slate-100 bg-slate-50/50 rounded-t-lg overflow-hidden">
      <div className={`absolute inset-y-0 left-0 w-1 ${styles.bar}`} aria-hidden="true" />
      <p className="text-xs font-semibold text-slate-600 uppercase tracking-wide">Your Asking Price</p>
      <div className="flex items-baseline gap-3 mt-1">
        <span className="text-3xl font-bold text-slate-900">£{listingPounds.toLocaleString()}</span>
        <span
          className={`inline-flex items-center font-semibold rounded-full border px-2.5 py-0.5 text-xs ${styles.pill}`}
        >
          {verdict.label}
        </span>
      </div>
      <p className={`text-sm font-semibold mt-1 ${styles.deltaText}`}>{verdict.reference}</p>
      <p className="text-xs text-slate-500 mt-1.5 leading-relaxed">{verdict.detail}</p>

      <button
        type="button"
        onClick={() => setShowDetail(!showDetail)}
        className="mt-2 inline-flex items-center gap-1 text-xs text-slate-500 hover:text-slate-700 font-medium"
      >
        <svg
          className={`w-3 h-3 transition-transform ${showDetail ? "rotate-180" : ""}`}
          fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
        </svg>
        {showDetail ? "Hide detailed comparison" : "Detailed comparison"}
      </button>

      {showDetail && (
        <div className="mt-2 space-y-1 text-xs">
          {valuation.private_sale !== null && (
            <div className="flex justify-between">
              <span className="text-slate-500">vs Private Sale (£{valuation.private_sale.toLocaleString()})</span>
              <DeltaCell delta={listingPounds - valuation.private_sale} />
            </div>
          )}
          {valuation.dealer_forecourt !== null && (
            <div className="flex justify-between">
              <span className="text-slate-500">vs Dealer (£{valuation.dealer_forecourt.toLocaleString()})</span>
              <DeltaCell delta={listingPounds - valuation.dealer_forecourt} />
            </div>
          )}
          {valuation.trade_in !== null && (
            <div className="flex justify-between">
              <span className="text-slate-500">vs Trade-in (£{valuation.trade_in.toLocaleString()})</span>
              <DeltaCell delta={listingPounds - valuation.trade_in} />
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function DeltaCell({ delta }: { delta: number }) {
  if (delta === 0) return <span className="text-slate-600 font-medium">at value</span>;
  if (delta < 0)
    return (
      <span className="text-emerald-700 font-semibold">
        −£{Math.abs(delta).toLocaleString()}
      </span>
    );
  return <span className="text-red-700 font-semibold">+£{delta.toLocaleString()}</span>;
}

export default function FullCheckSection({
  finance_check, stolen_check, write_off_check, valuation,
  salvage_check, import_status, plate_changes, keeper_history,
  high_risk, previous_searches, listing_price, registration,
}: FullCheckSectionProps) {
  const hasPremiumData = !!(
    finance_check || stolen_check || write_off_check || valuation ||
    salvage_check || import_status || plate_changes || keeper_history ||
    high_risk || previous_searches
  );

  /* Free tier: prominent upsell card */
  if (!hasPremiumData) {
    return <PremiumPreview registration={registration} />;
  }

  /* Paid tier: render actual premium data cards */
  return (
    <div className="space-y-3">
      {/* Theft & Alerts swipe carousel — groups Stolen, Finance, Write-off,
          Salvage, Import, Export into a single consolidated card. Spans
          full width. */}
      <TheftAlertsCarousel
        finance_check={finance_check}
        stolen_check={stolen_check}
        write_off_check={write_off_check}
        salvage_check={salvage_check}
        import_status={import_status}
      />

      {/* Remaining cards stack vertically at full width — simplest layout,
          no dead space, each card takes exactly the height it needs. */}
      <div className="space-y-3">
      {/* Valuation */}
      {valuation && (
        <Card title="Valuation" icon={icons.currency} status="neutral">
          {listing_price && listing_price > 0 && (
            <AskingPriceBlock listingPricePence={listing_price} valuation={valuation} />
          )}
          {valuation.private_sale !== null && (
            <DetailRow label="Private Sale" value={`£${valuation.private_sale.toLocaleString()}`} />
          )}
          {valuation.dealer_forecourt !== null && (
            <DetailRow label="Dealer Forecourt" value={`£${valuation.dealer_forecourt.toLocaleString()}`} />
          )}
          {valuation.trade_in !== null && (
            <DetailRow label="Trade-in" value={`£${valuation.trade_in.toLocaleString()}`} />
          )}
          {valuation.part_exchange !== null && (
            <DetailRow label="Part Exchange" value={`£${valuation.part_exchange.toLocaleString()}`} />
          )}
          {/* Price range bar */}
          {valuation.trade_in !== null && valuation.dealer_forecourt !== null && (
            <div className="mt-3 pt-3 border-t border-slate-100">
              <div className="flex justify-between text-xs text-slate-400 mb-1">
                <span>&pound;{valuation.trade_in.toLocaleString()}</span>
                <span>&pound;{valuation.dealer_forecourt.toLocaleString()}</span>
              </div>
              <div className="h-3 bg-gradient-to-r from-amber-200 via-emerald-300 to-blue-300 rounded-full" />
              <div className="flex justify-between text-xs text-slate-400 mt-1">
                <span>Trade-in</span>
                <span>Dealer</span>
              </div>
            </div>
          )}
          <div className="mt-3 pt-3 border-t border-slate-100">
            <DetailRow
              label="Condition"
              value={
                valuation.condition === "Mileage-adjusted"
                  ? "Average (adjusted for mileage)"
                  : valuation.condition
              }
            />
            {valuation.mileage_used !== null && (
              <DetailRow label="Mileage Used" value={`${valuation.mileage_used.toLocaleString()} miles`} />
            )}
            <DetailRow label="Valuation Date" value={valuation.valuation_date} />
          </div>

          {/* Asking-price comparison — only if buyer entered a price pre-payment */}
          <div className="mt-2 text-xs text-slate-400 bg-slate-50 rounded px-2 py-1">
            Source: {valuation.data_source}
          </div>
        </Card>
      )}

      {/* Salvage auction records (when flagged, show details here — the swipe
          card only shows the headline pill). */}
      {salvage_check && salvage_check.salvage_found && salvage_check.records.length > 0 && (
        <Card title="Salvage Records" icon={icons.alert} status="fail">
          <div className="space-y-2">
            {salvage_check.records.map((r, i) => (
              <div key={i} className="bg-slate-50 rounded-lg p-3">
                {r.auction_date && <DetailRow label="Auction Date" value={r.auction_date} />}
                {r.damage_description && <DetailRow label="Damage" value={r.damage_description} />}
                {r.category && <DetailRow label="Category" value={r.category} />}
                {r.lot_number && <DetailRow label="Lot Number" value={r.lot_number} />}
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Keeper History — per-owner timeline */}
      {keeper_history && (
        <Card title="Keeper History" icon={icons.users} status="neutral">
          {keeper_history.keeper_count !== null ? (
            <p className="text-sm text-slate-500 mb-3">
              Total Keepers: <span className="text-slate-900 font-bold text-base">{keeper_history.keeper_count}</span>
            </p>
          ) : (
            <p className="text-sm text-slate-500 mb-3">Keeper information not available</p>
          )}

          {keeper_history.keepers && keeper_history.keepers.length > 0 && (
            <div className="space-y-2">
              {keeper_history.keepers.map((k) => (
                <div
                  key={k.keeper_number}
                  className={`flex items-center gap-3 rounded-lg border px-3 py-2.5 ${
                    k.is_current
                      ? "bg-indigo-50 border-indigo-200"
                      : "bg-white border-slate-200"
                  }`}
                >
                  <span
                    className={`inline-flex items-center justify-center w-7 h-7 rounded-full text-white font-bold text-xs flex-shrink-0 ${
                      k.is_current ? "bg-blue-600" : "bg-slate-500"
                    }`}
                  >
                    {k.keeper_number}
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-slate-900 truncate">{k.label || `Keeper ${k.keeper_number}`}</p>
                    <p className="text-xs text-slate-500 truncate">
                      {k.is_current
                        ? `Since ${k.start_display || k.start_date || "unknown"}`
                        : `From ${k.start_display || k.start_date || "unknown"}`}
                    </p>
                  </div>
                  <div className="text-right flex-shrink-0">
                    {k.is_current && (
                      <span className="block bg-blue-100 text-blue-800 text-[10px] font-bold px-2 py-0.5 rounded mb-1">
                        Current
                      </span>
                    )}
                    {k.tenure_display && (
                      <span className={`text-xs font-semibold ${k.is_current ? "text-blue-800" : "text-slate-600"}`}>
                        {k.tenure_display}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {keeper_history.keeper_count !== null && keeper_history.keeper_count > 5 && (
            <div className="mt-3 flex items-start gap-2 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2">
              <svg className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
              </svg>
              <p className="text-xs text-amber-700">
                High number of keepers — may indicate issues with the vehicle or frequent reselling.
              </p>
            </div>
          )}
          <div className="mt-3 text-xs text-slate-400 bg-slate-50 rounded px-2 py-1">
            Source: {keeper_history.data_source}
          </div>
        </Card>
      )}

      {/* Plate Changes */}
      {plate_changes && (
        <Card
          title="Plate Changes"
          icon={icons.swap}
          status={plate_changes.changes_found ? "warn" : "neutral"}
        >
          <div className="mb-3">
            {plate_changes.changes_found ? (
              <div className="flex items-center gap-2 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2">
                <svg className="w-5 h-5 text-amber-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
                </svg>
                <span className="text-sm font-semibold text-amber-800">{plate_changes.record_count} plate change{plate_changes.record_count !== 1 ? "s" : ""} found</span>
              </div>
            ) : (
              <div className="flex items-center gap-2 bg-slate-50 border border-slate-200 rounded-lg px-3 py-2">
                <svg className="w-5 h-5 text-slate-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="text-sm font-semibold text-slate-600">No Plate Changes</span>
              </div>
            )}
          </div>
          {plate_changes.records.length > 0 && (
            <div className="space-y-2">
              {plate_changes.records.map((r, i) => (
                <div key={i} className="bg-slate-50 rounded-lg p-3">
                  <DetailRow
                    label="Previous Plate"
                    value={
                      <span className="inline-block bg-yellow-50 border border-yellow-300 font-mono font-bold px-2 py-0.5 rounded text-slate-900 text-xs">
                        {r.previous_plate}
                      </span>
                    }
                  />
                  <DetailRow label="Change Date" value={r.change_date} />
                </div>
              ))}
            </div>
          )}
          <div className="mt-2 text-xs text-slate-400 bg-slate-50 rounded px-2 py-1">
            Source: {plate_changes.data_source}
          </div>
        </Card>
      )}

      {/* High Risk Indicators */}
      {high_risk && (
        <Card
          title="High Risk Indicators"
          icon={icons.alert}
          status={high_risk.flagged ? "fail" : "pass"}
        >
          <div className="mb-3">
            {high_risk.flagged ? (
              <div className="flex items-center gap-2 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
                <svg className="w-5 h-5 text-red-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
                </svg>
                <span className="text-sm font-semibold text-red-800">High risk flags found</span>
              </div>
            ) : (
              <div className="flex items-center gap-2 bg-emerald-50 border border-emerald-200 rounded-lg px-3 py-2">
                <svg className="w-5 h-5 text-emerald-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="text-sm font-semibold text-emerald-800">No high risk flags</span>
              </div>
            )}
          </div>
          <p className="text-xs text-slate-500 mb-2">
            Aggregates any high-risk markers from Experian — including finance defaults, write-off records, scrappage, and police alerts — into a single flag.
          </p>
          {high_risk.records.length > 0 && (
            <div className="space-y-2">
              {high_risk.records.map((r, i) => (
                <div key={i} className="bg-red-50 rounded-lg p-3">
                  <DetailRow label="Risk Type" value={r.risk_type} />
                  {r.date && <DetailRow label="Date" value={r.date} />}
                  {r.detail && <DetailRow label="Detail" value={r.detail} />}
                  {r.company && <DetailRow label="Company" value={r.company} />}
                  {r.contact && <DetailRow label="Contact" value={r.contact} />}
                </div>
              ))}
            </div>
          )}
          <div className="mt-2 text-xs text-slate-400 bg-slate-50 rounded px-2 py-1">
            Source: {high_risk.data_source}
          </div>
        </Card>
      )}

      {/* Previous Checks */}
      {previous_searches && <PreviousChecksCard data={previous_searches} />}
      </div>
    </div>
  );
}

/* Previous Checks — grouped summary with definitions.
   Replaces the repeated "Motor trade & other" list that told users nothing.
   Pills categorise: insurer checks are the interesting signal (post-accident
   queries); trade checks are dealer/valuator routine. */
function PreviousChecksCard({ data }: { data: PreviousSearches }) {
  const [showAll, setShowAll] = useState(false);
  const records = data.records || [];

  const isInsurer = (t: string | null | undefined) =>
    !!t && t.toLowerCase().includes("insurer");

  const insurerCount = records.filter((r) => isInsurer(r.business_type)).length;
  const tradeCount = records.filter((r) => !isInsurer(r.business_type)).length;

  return (
    <Card title="Previous Checks" icon={icons.search} status="neutral">
      <p className="text-xs text-slate-500 mb-3">
        Every time a dealer, insurer, or valuator runs a history check on this vehicle, it&apos;s logged here.
      </p>

      <div className="flex items-baseline gap-3 mb-3">
        <span className="text-3xl font-bold text-slate-900">{data.search_count}</span>
        <span className="text-sm text-slate-700">
          check{data.search_count !== 1 ? "s" : ""} in the last 12 months
        </span>
      </div>

      <div className="space-y-2">
        {tradeCount > 0 && (
          <div className="flex items-start gap-2 bg-slate-50 rounded-lg px-3 py-2">
            <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-slate-200 text-slate-700 text-xs font-bold flex-shrink-0">
              {tradeCount}
            </span>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-slate-700">Trade &amp; dealer checks</p>
              <p className="text-xs text-slate-500">Routine pre-sale checks by garages or valuators.</p>
            </div>
          </div>
        )}
        {insurerCount > 0 && (
          <div className="flex items-start gap-2 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2">
            <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-amber-200 text-amber-800 text-xs font-bold flex-shrink-0">
              {insurerCount}
            </span>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-amber-800">Insurer checks</p>
              <p className="text-xs text-amber-700">Triggered by a claim — often indicates an accident or damage event.</p>
            </div>
          </div>
        )}
      </div>

      {data.search_count > 10 && (
        <p className="text-xs text-blue-700 bg-blue-50 border border-blue-200 rounded px-3 py-2 mt-3">
          High search activity — this vehicle is actively being marketed or has attracted buyer interest.
        </p>
      )}

      {records.length > 0 && (
        <>
          <button
            type="button"
            onClick={() => setShowAll(!showAll)}
            className="mt-3 inline-flex items-center gap-1 text-xs text-slate-500 hover:text-slate-700 font-medium"
          >
            <svg
              className={`w-3 h-3 transition-transform ${showAll ? "rotate-180" : ""}`}
              fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
            </svg>
            {showAll ? "Hide dates" : "Show individual dates"}
          </button>
          {showAll && (
            <div className="mt-2 space-y-1">
              {records.map((r, i) => {
                const insurer = isInsurer(r.business_type);
                return (
                  <div
                    key={i}
                    className={`flex justify-between py-1 px-2 rounded text-xs ${insurer ? "bg-amber-50" : ""}`}
                  >
                    <span className="text-slate-500">{r.date || "Unknown date"}</span>
                    <span className={insurer ? "text-amber-800 font-medium" : "text-slate-700"}>
                      {insurer ? "Insurer" : "Trade/dealer"}
                    </span>
                  </div>
                );
              })}
            </div>
          )}
        </>
      )}

      <div className="mt-3 text-xs text-slate-400 bg-slate-50 rounded px-2 py-1">
        Source: {data.data_source}
      </div>
    </Card>
  );
}
