"use client";

import {
  FinanceCheck, StolenCheck, WriteOffCheck, Valuation,
  SalvageCheck, ImportStatusCheck, PlateChangeHistory, KeeperHistory,
  HighRiskCheck, PreviousSearches,
} from "@/lib/api";
import Card from "@/components/ui/Card";
import { DetailRow, icons } from "./shared";
import PremiumPreview from "./PremiumPreview";
import TheftAlertsCarousel from "./TheftAlertsCarousel";

function toSentenceCase(s: string | null | undefined): string {
  if (!s) return "";
  const lower = s.toLowerCase();
  return lower.charAt(0).toUpperCase() + lower.slice(1);
}

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

function formatDelta(deltaPounds: number): { label: string; className: string } {
  const absStr = `£${Math.abs(deltaPounds).toLocaleString()}`;
  if (deltaPounds === 0) return { label: `Exactly at market`, className: "text-slate-600" };
  if (deltaPounds < 0) return { label: `−${absStr}`, className: "text-emerald-700 font-semibold" };
  // Over market: amber if within 10%, red if further
  return { label: `+${absStr}`, className: "text-red-700 font-semibold" };
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

      {/* Remaining cards in a two-column grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
      {/* Valuation */}
      {valuation && (
        <Card title="Valuation" icon={icons.currency} status="neutral">
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
          {listing_price && listing_price > 0 && (
            <div className="mt-3 pt-3 border-t border-slate-100">
              <p className="text-xs font-semibold text-slate-600 uppercase tracking-wide mb-2">Your Asking Price</p>
              <DetailRow label="You entered" value={`£${Math.round(listing_price / 100).toLocaleString()}`} />
              {valuation.private_sale !== null && (
                <div className="flex justify-between py-1.5 border-b border-slate-100">
                  <span className="text-sm text-slate-500">vs Private Sale</span>
                  <span className={`text-sm ${formatDelta(Math.round(listing_price / 100) - valuation.private_sale).className}`}>
                    {formatDelta(Math.round(listing_price / 100) - valuation.private_sale).label}
                  </span>
                </div>
              )}
              {valuation.dealer_forecourt !== null && (
                <div className="flex justify-between py-1.5 border-b border-slate-100 last:border-0">
                  <span className="text-sm text-slate-500">vs Dealer</span>
                  <span className={`text-sm ${formatDelta(Math.round(listing_price / 100) - valuation.dealer_forecourt).className}`}>
                    {formatDelta(Math.round(listing_price / 100) - valuation.dealer_forecourt).label}
                  </span>
                </div>
              )}
              {valuation.trade_in !== null && (
                <div className="flex justify-between py-1.5 last:border-0">
                  <span className="text-sm text-slate-500">vs Trade-in</span>
                  <span className={`text-sm ${formatDelta(Math.round(listing_price / 100) - valuation.trade_in).className}`}>
                    {formatDelta(Math.round(listing_price / 100) - valuation.trade_in).label}
                  </span>
                </div>
              )}
            </div>
          )}

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
      {previous_searches && (
        <Card title="Previous Checks" icon={icons.search} status="neutral">
          <div className="mb-3">
            <div className="flex items-center gap-3">
              <div className="text-3xl font-bold text-slate-900">{previous_searches.search_count}</div>
              <p className="text-sm text-slate-700">
                previous check{previous_searches.search_count !== 1 ? "s" : ""} on this vehicle
              </p>
            </div>
          </div>
          {previous_searches.search_count > 10 && (
            <div className="flex items-start gap-2 bg-blue-50 border border-blue-200 rounded-lg px-3 py-2 mb-2">
              <svg className="w-4 h-4 text-blue-600 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" />
              </svg>
              <p className="text-xs text-blue-700">
                High search activity may indicate the vehicle is actively being marketed or has attracted buyer interest.
              </p>
            </div>
          )}
          {previous_searches.records.length > 0 && (
            <div className="space-y-1">
              {previous_searches.records.slice(0, 5).map((r, i) => (
                <div key={i} className="flex justify-between py-1.5 border-b border-slate-100 last:border-0">
                  <span className="text-sm text-slate-500">{r.date || "Unknown date"}</span>
                  <span className="text-sm text-slate-700">{toSentenceCase(r.business_type) || "Check"}</span>
                </div>
              ))}
              {previous_searches.records.length > 5 && (
                <p className="text-xs text-slate-400 pt-1">
                  + {previous_searches.records.length - 5} more
                </p>
              )}
            </div>
          )}
          <div className="mt-2 text-xs text-slate-400 bg-slate-50 rounded px-2 py-1">
            Source: {previous_searches.data_source}
          </div>
        </Card>
      )}
      </div>
    </div>
  );
}
