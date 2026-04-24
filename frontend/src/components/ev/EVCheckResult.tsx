"use client";

import { EVCheckResponse } from "@/lib/api";
import EVOverviewSections from "@/components/ev/sections/EVOverviewSections";
import EVBatterySections from "@/components/ev/sections/EVBatterySections";
import EVHistorySections from "@/components/ev/sections/EVHistorySections";
import EVFullCheckSection from "@/components/ev/sections/EVFullCheckSection";
import FullCheckSection from "@/components/sections/FullCheckSection";
import AtAGlance from "@/components/sections/AtAGlance";
import SectionNav, { SectionConfig } from "@/components/SectionNav";
import PremiumBottomBar from "@/components/PremiumBottomBar";

const EV_FREE_SECTIONS: SectionConfig[] = [
  { id: "ev-section-overview", label: "Overview" },
  { id: "ev-section-history", label: "History" },
  { id: "ev-section-battery", label: "EV Check", locked: true },
  { id: "ev-section-fullcheck", label: "Full Check", locked: true },
];

const EV_REPORT_SECTIONS: SectionConfig[] = [
  { id: "ev-section-glance", label: "At a Glance" },
  { id: "ev-section-battery", label: "EV Check" },
  { id: "ev-section-fullcheck", label: "Full Check" },
  { id: "ev-section-overview", label: "Overview" },
  { id: "ev-section-history", label: "History" },
];

interface Props {
  result: EVCheckResponse;
  reportMode?: boolean;
}

export default function EVCheckResult({ result, reportMode = false }: Props) {
  const {
    vehicle, mot_summary, mot_tests, clocking_analysis, ulez_compliance,
    mileage_timeline, failure_patterns, tax_calculation,
    safety_rating, vehicle_stats,
    battery_health, range_estimate, range_scenarios,
    charging_costs, ev_specs, lifespan_prediction,
    finance_check, stolen_check, write_off_check, salvage_check,
    import_status, plate_changes, keeper_history, valuation,
    high_risk, previous_searches, listing_price,
  } = result;

  const hasProvenanceData = !!(
    finance_check || stolen_check || write_off_check || salvage_check ||
    import_status || plate_changes || keeper_history || valuation ||
    high_risk || previous_searches
  );

  // Checkout flow lives in <EVUpsellSection/> rendered separately on the
  // free EV page (see EVSearchSection.tsx). This component just shows the
  // result data — no inline checkout buttons.

  const overview = (
    <div id="ev-section-overview" className="space-y-3">
      <EVOverviewSections
        vehicle={vehicle}
        mot_summary={mot_summary}
        tax_calculation={tax_calculation}
        vehicle_stats={vehicle_stats}
        safety_rating={safety_rating}
      />
    </div>
  );

  const history = (
    <div id="ev-section-history" className="space-y-3">
      <EVHistorySections
        mot_summary={mot_summary}
        clocking_analysis={clocking_analysis}
        mileage_timeline={mileage_timeline}
        failure_patterns={failure_patterns}
        mot_tests={mot_tests}
        vehicle={vehicle}
      />
    </div>
  );

  const battery = (
    <div id="ev-section-battery" className="space-y-3">
      <EVBatterySections
        battery_health={battery_health}
        range_estimate={range_estimate}
        range_scenarios={range_scenarios}
        charging_costs={charging_costs}
        ev_specs={ev_specs}
        lifespan_prediction={lifespan_prediction}
        paidTier={reportMode}
      />
    </div>
  );

  const fullCheck = (
    <div id="ev-section-fullcheck">
      {hasProvenanceData ? (
        <FullCheckSection
          finance_check={finance_check ?? null}
          stolen_check={stolen_check ?? null}
          write_off_check={write_off_check ?? null}
          valuation={valuation ?? null}
          salvage_check={salvage_check ?? null}
          import_status={import_status ?? null}
          plate_changes={plate_changes ?? null}
          keeper_history={keeper_history ?? null}
          high_risk={high_risk ?? null}
          previous_searches={previous_searches ?? null}
          listing_price={listing_price ?? null}
          registration={result.registration}
        />
      ) : (
        <EVFullCheckSection registration={result.registration} crossSell={reportMode} />
      )}
    </div>
  );

  return (
    <div className="space-y-4 pb-20 md:pb-0">
      {/* Title bar */}
      <div className="flex items-center justify-between bg-white border border-slate-200 rounded-xl p-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 bg-emerald-100 text-emerald-700 text-xs font-semibold rounded-full">
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
              </svg>
              {result.ev_type === "BEV" ? "Battery Electric" : "Plug-in Hybrid"}
            </span>
          </div>
          <h2 className="text-xl font-bold text-slate-900">
            {vehicle?.make || mot_summary?.make || "Vehicle"} {mot_summary?.model || ""} {vehicle?.year_of_manufacture ? `(${vehicle.year_of_manufacture})` : ""}
          </h2>
          <p className="text-sm text-slate-500 mt-1">
            Registration:{" "}
            <span className="inline-block bg-yellow-50 border border-yellow-300 font-mono font-bold px-2 py-0.5 rounded text-slate-900">
              {result.registration}
            </span>
          </p>
        </div>
      </div>

      {/* Outstanding Recall Warning */}
      {mot_summary?.has_outstanding_recall === "Yes" && (
        <div className="bg-red-50 border-2 border-red-300 rounded-xl p-4 flex items-start gap-3">
          <div className="w-10 h-10 rounded-full bg-red-100 flex items-center justify-center flex-shrink-0">
            <svg className="w-6 h-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
            </svg>
          </div>
          <div>
            <p className="font-bold text-red-800">Outstanding Safety Recall</p>
            <p className="text-sm text-red-700 mt-0.5">This vehicle has an outstanding manufacturer recall. Contact the manufacturer or an authorised dealer to arrange a free repair.</p>
          </div>
        </div>
      )}

      {/* Section navigation */}
      <SectionNav
        sections={reportMode ? EV_REPORT_SECTIONS : EV_FREE_SECTIONS}
        hasPremium={reportMode}
      />

      {reportMode ? (
        <>
          {/* At a Glance */}
          <div id="ev-section-glance">
            <AtAGlance
              finance_check={finance_check}
              stolen_check={stolen_check}
              write_off_check={write_off_check}
              salvage_check={salvage_check}
              clocking_analysis={clocking_analysis}
              vehicle={vehicle}
              vehicle_stats={vehicle_stats}
              ulez_compliance={ulez_compliance}
              mot_summary={mot_summary}
              battery_health={battery_health}
            />
          </div>
          {battery}
          {fullCheck}
          {overview}
          {history}
        </>
      ) : (
        <>
          {overview}
          {history}
          {battery}
          {fullCheck}
        </>
      )}

      {/* Inline upsell cards removed 2026-04-24 — EVSearchSection already
          renders <EVUpsellSection/> below this component on the free page,
          which is the single consolidated upsell (tier picker). Having two
          parallel upsells on the same scroll felt repetitive. */}

      {/* Tier badge */}
      <div className="text-center pt-2">
        <span className="inline-block bg-slate-100 text-slate-500 text-xs px-3 py-1 rounded-full">
          {reportMode
            ? "Full EV Report \u00B7 Powered by DVLA, DVSA & Experian data"
            : "Free EV Check \u00B7 Powered by DVLA & DVSA data"}
        </span>
      </div>

      {/* Legal disclaimer */}
      <p className="text-xs text-slate-400 text-center mt-4 max-w-2xl mx-auto">
        This report is for informational purposes only and should not be the sole basis for a purchasing decision. Data sourced from DVLA, DVSA, and third-party providers &mdash; accuracy not guaranteed. We recommend an independent mechanical inspection before purchase. See our{" "}
        <a href="/terms" className="underline hover:text-slate-600">Terms of Service</a>.
      </p>

      {/* Premium upsell bottom bar (mobile only) — free tier only */}
      {!reportMode && (
        <PremiumBottomBar hasPremium={false} variant="ev" registration={result.registration} />
      )}
    </div>
  );
}
