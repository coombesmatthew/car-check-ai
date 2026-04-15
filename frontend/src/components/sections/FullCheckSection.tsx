"use client";

import {
  FinanceCheck, StolenCheck, WriteOffCheck, Valuation,
  SalvageCheck, PlateChangeHistory, KeeperHistory,
  HighRiskCheck, PreviousSearches,
} from "@/lib/api";
import Badge from "@/components/ui/Badge";
import Card from "@/components/ui/Card";
import { DetailRow, icons } from "./shared";
import PremiumPreview from "./PremiumPreview";

interface FullCheckSectionProps {
  finance_check: FinanceCheck | null;
  stolen_check: StolenCheck | null;
  write_off_check: WriteOffCheck | null;
  valuation: Valuation | null;
  salvage_check: SalvageCheck | null;
  plate_changes: PlateChangeHistory | null;
  keeper_history: KeeperHistory | null;
  high_risk: HighRiskCheck | null;
  previous_searches: PreviousSearches | null;
  registration: string;
}

export default function FullCheckSection({
  finance_check, stolen_check, write_off_check, valuation,
  salvage_check, plate_changes, keeper_history,
  high_risk, previous_searches, registration,
}: FullCheckSectionProps) {
  const hasPremiumData = !!(finance_check || stolen_check || write_off_check || valuation || salvage_check || plate_changes || keeper_history || high_risk || previous_searches);

  /* Free tier: prominent upsell card */
  if (!hasPremiumData) {
    return <PremiumPreview registration={registration} />;
  }

  /* Paid tier: render actual premium data cards */
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
      {/* Valuation */}
      {valuation && (
        <Card title="Valuation" icon={icons.currency} status="neutral">
          <div className="space-y-2 mb-3">
            {valuation.private_sale !== null && (
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-500">Private Sale</span>
                <span className="text-lg font-bold text-slate-900 font-mono">&pound;{valuation.private_sale.toLocaleString()}</span>
              </div>
            )}
            {valuation.dealer_forecourt !== null && (
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-500">Dealer Forecourt</span>
                <span className="text-lg font-bold text-slate-900 font-mono">&pound;{valuation.dealer_forecourt.toLocaleString()}</span>
              </div>
            )}
            {valuation.trade_in !== null && (
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-500">Trade-in</span>
                <span className="text-lg font-bold text-slate-900 font-mono">&pound;{valuation.trade_in.toLocaleString()}</span>
              </div>
            )}
            {valuation.part_exchange !== null && (
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-500">Part Exchange</span>
                <span className="text-lg font-bold text-slate-900 font-mono">&pound;{valuation.part_exchange.toLocaleString()}</span>
              </div>
            )}
          </div>
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
            <DetailRow label="Condition" value={valuation.condition} />
            {valuation.mileage_used !== null && (
              <DetailRow label="Mileage Used" value={`${valuation.mileage_used.toLocaleString()} miles`} />
            )}
            <DetailRow label="Valuation Date" value={valuation.valuation_date} />
          </div>
          <div className="mt-2 text-xs text-slate-400 bg-slate-50 rounded px-2 py-1">
            Source: {valuation.data_source}
          </div>
        </Card>
      )}

      {/* Finance Check */}
      {finance_check && (
        <Card
          title="Finance Check"
          icon={icons.document}
          status={finance_check.finance_outstanding ? "fail" : "pass"}
        >
          <div className="mb-3">
            {finance_check.finance_outstanding ? (
              <div className="flex items-center gap-2 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
                <svg className="w-5 h-5 text-red-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
                </svg>
                <span className="text-sm font-semibold text-red-800">FINANCE OUTSTANDING</span>
              </div>
            ) : (
              <div className="flex items-center gap-2 bg-emerald-50 border border-emerald-200 rounded-lg px-3 py-2">
                <svg className="w-5 h-5 text-emerald-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="text-sm font-semibold text-emerald-800">NO FINANCE</span>
              </div>
            )}
          </div>
          {finance_check.records.map((r, i) => (
            <div key={i} className="bg-slate-50 rounded-lg p-3 mb-2">
              <DetailRow label="Agreement Type" value={r.agreement_type} />
              <DetailRow label="Finance Company" value={r.finance_company} />
              {r.agreement_date && <DetailRow label="Agreement Date" value={r.agreement_date} />}
              {r.agreement_term && <DetailRow label="Term" value={r.agreement_term} />}
              {r.contact_number && <DetailRow label="Contact" value={r.contact_number} />}
            </div>
          ))}
          <div className="mt-2 text-xs text-slate-400 bg-slate-50 rounded px-2 py-1">
            Source: {finance_check.data_source}
          </div>
        </Card>
      )}

      {/* Stolen Check */}
      {stolen_check && (
        <Card
          title="Stolen Check"
          icon={icons.shield}
          status={stolen_check.stolen ? "fail" : "pass"}
        >
          <div className="mb-3">
            {stolen_check.stolen ? (
              <div className="flex items-center gap-2 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
                <svg className="w-5 h-5 text-red-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
                </svg>
                <span className="text-sm font-semibold text-red-800">REPORTED STOLEN</span>
              </div>
            ) : (
              <div className="flex items-center gap-2 bg-emerald-50 border border-emerald-200 rounded-lg px-3 py-2">
                <svg className="w-5 h-5 text-emerald-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="text-sm font-semibold text-emerald-800">NOT STOLEN</span>
              </div>
            )}
          </div>
          {stolen_check.stolen && (
            <div className="bg-slate-50 rounded-lg p-3">
              {stolen_check.reported_date && <DetailRow label="Reported Date" value={stolen_check.reported_date} />}
              {stolen_check.police_force && <DetailRow label="Police Force" value={stolen_check.police_force} />}
              {stolen_check.reference && <DetailRow label="Reference" value={stolen_check.reference} />}
            </div>
          )}
          <div className="mt-2 text-xs text-slate-400 bg-slate-50 rounded px-2 py-1">
            Source: {stolen_check.data_source}
          </div>
        </Card>
      )}

      {/* Write-off Check */}
      {write_off_check && (
        <Card
          title="Write-off Check"
          icon={icons.alert}
          status={write_off_check.written_off ? "fail" : "pass"}
        >
          <div className="mb-3">
            {write_off_check.written_off ? (
              <div className="flex items-center gap-2 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
                <svg className="w-5 h-5 text-red-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
                </svg>
                <span className="text-sm font-semibold text-red-800">INSURANCE WRITE-OFF</span>
              </div>
            ) : (
              <div className="flex items-center gap-2 bg-emerald-50 border border-emerald-200 rounded-lg px-3 py-2">
                <svg className="w-5 h-5 text-emerald-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="text-sm font-semibold text-emerald-800">NOT WRITTEN OFF</span>
              </div>
            )}
          </div>
          {write_off_check.records.map((r, i) => (
            <div key={i} className="bg-slate-50 rounded-lg p-3 mb-2">
              <div className="flex items-center gap-2 mb-2">
                <Badge
                  variant="fail"
                  label={`Cat ${r.category}`}
                  size="md"
                />
                <span className="text-xs text-slate-500">
                  {r.category === "A" && "Scrap only"}
                  {r.category === "B" && "Break for parts"}
                  {r.category === "S" && "Structural damage"}
                  {r.category === "N" && "Non-structural damage"}
                </span>
              </div>
              <DetailRow label="Date" value={r.date} />
              {r.loss_type && <DetailRow label="Loss Type" value={r.loss_type} />}
            </div>
          ))}
          <div className="mt-2 text-xs text-slate-400 bg-slate-50 rounded px-2 py-1">
            Source: {write_off_check.data_source}
          </div>
        </Card>
      )}

      {/* Salvage Auction Check */}
      {salvage_check && (
        <Card
          title="Salvage Auction Check"
          icon={icons.alert}
          status={salvage_check.salvage_found ? "fail" : "pass"}
        >
          <div className="mb-3">
            {salvage_check.salvage_found ? (
              <div className="flex items-center gap-2 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
                <svg className="w-5 h-5 text-red-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
                </svg>
                <span className="text-sm font-semibold text-red-800">SALVAGE RECORDS FOUND</span>
              </div>
            ) : (
              <div className="flex items-center gap-2 bg-emerald-50 border border-emerald-200 rounded-lg px-3 py-2">
                <svg className="w-5 h-5 text-emerald-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="text-sm font-semibold text-emerald-800">NO SALVAGE RECORDS</span>
              </div>
            )}
          </div>
          <p className="text-xs text-slate-500 mb-2">
            Checked against UK salvage auction databases for any history of this vehicle being sold as salvage.
          </p>
          {salvage_check.records.length > 0 && (
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
          )}
          <div className="mt-2 text-xs text-slate-400 bg-slate-50 rounded px-2 py-1">
            Source: {salvage_check.data_source}
          </div>
        </Card>
      )}

      {/* Keeper History */}
      {keeper_history && (
        <Card title="Keeper History" icon={icons.users} status="neutral">
          <div className="mb-3">
            {keeper_history.keeper_count !== null ? (
              <div className="flex items-center gap-3">
                <div className="text-3xl font-bold text-slate-900">{keeper_history.keeper_count}</div>
                <div>
                  <p className="text-sm font-medium text-slate-700">
                    Registered keeper{keeper_history.keeper_count !== 1 ? "s" : ""}
                  </p>
                  {keeper_history.last_change_date && (
                    <p className="text-xs text-slate-500">
                      Last change: {keeper_history.last_change_date}
                    </p>
                  )}
                </div>
              </div>
            ) : (
              <p className="text-sm text-slate-500">Keeper information not available</p>
            )}
          </div>
          {keeper_history.keeper_count !== null && keeper_history.keeper_count > 5 && (
            <div className="flex items-start gap-2 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2">
              <svg className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
              </svg>
              <p className="text-xs text-amber-700">
                High number of keepers — may indicate issues with the vehicle or frequent reselling.
              </p>
            </div>
          )}
          <div className="mt-2 text-xs text-slate-400 bg-slate-50 rounded px-2 py-1">
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
                <span className="text-sm font-semibold text-amber-800">{plate_changes.record_count} PLATE CHANGE{plate_changes.record_count !== 1 ? "S" : ""} FOUND</span>
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
                  <DetailRow label="Change Type" value={r.change_type} />
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
                <span className="text-sm font-semibold text-red-800">HIGH RISK FLAGS FOUND</span>
              </div>
            ) : (
              <div className="flex items-center gap-2 bg-emerald-50 border border-emerald-200 rounded-lg px-3 py-2">
                <svg className="w-5 h-5 text-emerald-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="text-sm font-semibold text-emerald-800">NO HIGH RISK FLAGS</span>
              </div>
            )}
          </div>
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
                  <span className="text-sm text-slate-700">{r.business_type || "Check"}</span>
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
  );
}
