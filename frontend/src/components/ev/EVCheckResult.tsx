"use client";

import { useState } from "react";
import { EVCheckResponse, createEVCheckout } from "@/lib/api";
import EVOverviewSections from "@/components/ev/sections/EVOverviewSections";
import EVBatterySections from "@/components/ev/sections/EVBatterySections";
import EVHistorySections from "@/components/ev/sections/EVHistorySections";
import EVFullCheckSection from "@/components/ev/sections/EVFullCheckSection";
import FullCheckSection from "@/components/sections/FullCheckSection";
import AtAGlance from "@/components/sections/AtAGlance";
import ListingPriceModal from "@/components/ListingPriceModal";
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

  const [checkoutTier, setCheckoutTier] = useState<"ev" | "ev_complete" | null>(null);
  const [checkoutError, setCheckoutError] = useState<string | null>(null);
  const [modalTier, setModalTier] = useState<"ev" | "ev_complete" | null>(null);

  const openModal = (tier: "ev" | "ev_complete") => {
    if (checkoutTier) return;
    setCheckoutError(null);
    setModalTier(tier);
  };

  const handleContinue = async (listingPricePence: number | null) => {
    if (!modalTier || checkoutTier) return;
    const tier = modalTier;
    setCheckoutError(null);
    setCheckoutTier(tier);
    try {
      const { checkout_url } = await createEVCheckout(result.registration, null, tier, listingPricePence);
      window.location.href = checkout_url;
    } catch (err) {
      setCheckoutError(err instanceof Error ? err.message : "Checkout failed");
      setCheckoutTier(null);
      setModalTier(null);
    }
  };

  const overview = (
    <div id="ev-section-overview" className="columns-1 md:columns-2 gap-3 [&>div]:break-inside-avoid [&>div]:mb-3">
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
    <div id="ev-section-history" className="columns-1 md:columns-2 gap-3 [&>div]:break-inside-avoid [&>div]:mb-3">
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
    <div id="ev-section-battery" className="columns-1 md:columns-2 gap-3 [&>div]:break-inside-avoid [&>div]:mb-3">
      <EVBatterySections
        battery_health={battery_health}
        range_estimate={range_estimate}
        range_scenarios={range_scenarios}
        charging_costs={charging_costs}
        ev_specs={ev_specs}
        lifespan_prediction={lifespan_prediction}
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
        <EVFullCheckSection registration={result.registration} />
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

      {/* Upsell cards + bottom bar — free tier only */}
      {!reportMode && (
        <>
          {/* EV Health Check upsell */}
          <div className="bg-gradient-to-br from-emerald-50 to-teal-50 border-2 border-emerald-200 rounded-xl overflow-hidden">
            <div className="bg-gradient-to-r from-emerald-700 to-emerald-800 px-5 py-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-white font-bold text-lg flex items-center gap-2">
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
                    </svg>
                    Unlock EV Health Check
                  </h3>
                  <p className="text-emerald-200 text-sm">Battery analysis, range estimates &amp; charging costs for this EV</p>
                </div>
                <span className="bg-emerald-500/30 text-white text-xs font-bold px-3 py-1 rounded-full border border-emerald-400/30">
                  &pound;8.99
                </span>
              </div>
            </div>
            <div className="p-5">
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-x-6 gap-y-2.5">
                {["Battery Health Score", "Real-World Range", "Charging Cost Comparison", "Lifespan Prediction", "Emailed & online for 30 days"].map((item) => (
                  <div key={item} className="flex items-center gap-2">
                    <svg className="w-4 h-4 text-emerald-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                    </svg>
                    <span className="text-sm text-slate-700">{item}</span>
                  </div>
                ))}
              </div>
              <div className="mt-5 flex items-center gap-4 flex-wrap">
                <button
                  onClick={() => openModal("ev")}
                  disabled={checkoutTier !== null}
                  className="inline-flex items-center gap-2 px-6 py-2.5 bg-emerald-600 text-white font-semibold rounded-lg hover:bg-emerald-700 transition-colors text-sm disabled:opacity-75 disabled:cursor-wait"
                >
                  {checkoutTier === "ev" ? (
                    <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
                    </svg>
                  ) : (
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
                    </svg>
                  )}
                  {checkoutTier === "ev" ? "Redirecting…" : <>Get EV Health Check &mdash; &pound;8.99</>}
                </button>
                <span className="text-xs text-slate-400">
                  {checkoutError ? <span className="text-red-500">{checkoutError}</span> : "Delivered as PDF within 60 seconds"}
                </span>
              </div>
            </div>
          </div>

          {/* EV Complete upsell */}
          <div className="bg-gradient-to-br from-teal-50 to-slate-50 border-2 border-teal-200 rounded-xl overflow-hidden">
            <div className="bg-gradient-to-r from-teal-700 to-teal-800 px-5 py-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-white font-bold text-lg">Unlock EV Complete</h3>
                  <p className="text-teal-200 text-sm">Everything in EV Health Check plus full ownership &amp; history checks</p>
                </div>
                <div className="text-right">
                  <span className="bg-teal-500/30 text-white text-xs font-bold px-3 py-1 rounded-full border border-teal-400/30">
                    &pound;13.99
                  </span>
                  <p className="text-teal-300 text-[10px] mt-1">Best value</p>
                </div>
              </div>
            </div>
            <div className="p-5">
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-x-6 gap-y-2.5">
                {[
                  { label: "Everything in EV Health Check", icon: "check" },
                  { label: "Finance & Outstanding Debt", icon: "shield" },
                  { label: "Stolen Vehicle Check", icon: "shield" },
                  { label: "Write-off & Salvage History", icon: "shield" },
                  { label: "Market Valuation", icon: "shield" },
                  { label: "Plate & Keeper History", icon: "shield" },
                ].map((item) => (
                  <div key={item.label} className="flex items-center gap-2">
                    <svg className={`w-4 h-4 flex-shrink-0 ${item.icon === "check" ? "text-emerald-500" : "text-teal-500"}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      {item.icon === "check" ? (
                        <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                      ) : (
                        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
                      )}
                    </svg>
                    <span className={`text-sm ${item.icon === "check" ? "text-slate-500" : "text-slate-700 font-medium"}`}>{item.label}</span>
                  </div>
                ))}
              </div>
              <div className="mt-5 flex items-center gap-4 flex-wrap">
                <button
                  onClick={() => openModal("ev_complete")}
                  disabled={checkoutTier !== null}
                  className="inline-flex items-center gap-2 px-6 py-2.5 bg-teal-600 text-white font-semibold rounded-lg hover:bg-teal-700 transition-colors text-sm disabled:opacity-75 disabled:cursor-wait"
                >
                  {checkoutTier === "ev_complete" ? (
                    <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
                    </svg>
                  ) : (
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
                    </svg>
                  )}
                  {checkoutTier === "ev_complete" ? "Redirecting…" : <>Get EV Complete &mdash; &pound;13.99</>}
                </button>
                <span className="text-xs text-slate-400">One-off payment &middot; No subscription</span>
              </div>
            </div>
          </div>
        </>
      )}

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

      <ListingPriceModal
        open={modalTier !== null}
        onClose={() => setModalTier(null)}
        onContinue={handleContinue}
        registration={result.registration}
        tierLabel={modalTier === "ev_complete" ? "EV Complete" : "EV Health Check"}
        tierPrice={modalTier === "ev_complete" ? "£13.99" : "£8.99"}
        accentColour={modalTier === "ev_complete" ? "teal" : "emerald"}
        loading={checkoutTier !== null}
      />
    </div>
  );
}
