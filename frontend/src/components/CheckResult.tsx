"use client";

import { FreeCheckResponse } from "@/lib/api";
import OverviewSections from "@/components/sections/OverviewSections";
import HistorySections from "@/components/sections/HistorySections";
import EmissionsSections from "@/components/sections/EmissionsSections";
import FullCheckSection from "@/components/sections/FullCheckSection";
import AtAGlance from "@/components/sections/AtAGlance";
import SectionNav, { SectionConfig } from "@/components/SectionNav";
import PremiumBottomBar from "@/components/PremiumBottomBar";

const FREE_SECTIONS: SectionConfig[] = [
  { id: "section-overview", label: "Overview" },
  { id: "section-history", label: "History" },
  { id: "section-emissions", label: "Emissions" },
  { id: "section-fullcheck", label: "Full Check", locked: true },
];

const REPORT_SECTIONS: SectionConfig[] = [
  { id: "section-glance", label: "At a Glance" },
  { id: "section-fullcheck", label: "Full Check" },
  { id: "section-overview", label: "Overview" },
  { id: "section-history", label: "History" },
  { id: "section-emissions", label: "Emissions" },
];

export default function CheckResult({
  data,
  reportMode = false,
}: {
  data: FreeCheckResponse;
  reportMode?: boolean;
}) {
  const {
    vehicle, mot_summary, mot_tests, clocking_analysis,
    ulez_compliance, mileage_timeline, failure_patterns,
    tax_calculation, safety_rating, vehicle_stats,
    finance_check, stolen_check, write_off_check, plate_changes, valuation,
    salvage_check, import_status, keeper_history, high_risk, previous_searches,
    listing_price,
  } = data;

  const hasPremium = !!(finance_check || stolen_check || write_off_check || valuation);

  const overview = (
    <div id="section-overview" className="space-y-3">
      <OverviewSections vehicle={vehicle} mot_summary={mot_summary} tax_calculation={tax_calculation} vehicle_stats={vehicle_stats} safety_rating={safety_rating} />
    </div>
  );

  const history = (
    <div id="section-history" className="space-y-3">
      <HistorySections mot_summary={mot_summary} clocking_analysis={clocking_analysis} mileage_timeline={mileage_timeline} failure_patterns={failure_patterns} mot_tests={mot_tests} vehicle={vehicle} />
    </div>
  );

  const emissions = (
    <div id="section-emissions" className="space-y-3">
      <EmissionsSections ulez_compliance={ulez_compliance} tax_calculation={tax_calculation} />
    </div>
  );

  const fullCheck = (
    <div id="section-fullcheck">
      <FullCheckSection
        finance_check={finance_check} stolen_check={stolen_check}
        write_off_check={write_off_check} valuation={valuation}
        salvage_check={salvage_check} import_status={import_status}
        plate_changes={plate_changes}
        keeper_history={keeper_history} high_risk={high_risk}
        previous_searches={previous_searches}
        listing_price={listing_price}
        registration={data.registration}
      />
    </div>
  );

  return (
    <div className="space-y-4 pb-20 md:pb-0">
      {/* Title bar with score gauge */}
      <div className="flex items-center justify-between bg-white border border-slate-200 rounded-xl p-6">
        <div>
          <h2 className="text-xl font-bold text-slate-900">
            {vehicle?.make || mot_summary?.make || "Vehicle"}{" "}
            {mot_summary?.model || ""}{" "}
            {vehicle?.year_of_manufacture ? `(${vehicle.year_of_manufacture})` : ""}
          </h2>
          <p className="text-sm text-slate-500 mt-1">
            Registration:{" "}
            <span className="inline-block bg-yellow-50 border border-yellow-300 font-mono font-bold px-2 py-0.5 rounded text-slate-900">
              {data.registration}
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
            <p className="text-sm text-red-700 mt-0.5">
              This vehicle has an outstanding manufacturer recall. Contact the manufacturer or an authorised dealer to arrange a free repair.
            </p>
          </div>
        </div>
      )}

      {/* Section navigation */}
      <SectionNav
        sections={reportMode ? REPORT_SECTIONS : FREE_SECTIONS}
        hasPremium={hasPremium}
      />

      {reportMode ? (
        <>
          {/* At a Glance */}
          <div id="section-glance">
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
            />
          </div>
          {fullCheck}
          {overview}
          {history}
          {emissions}
        </>
      ) : (
        <>
          {overview}
          {history}
          {emissions}
          {fullCheck}
        </>
      )}

      {/* Tier badge */}
      <div className="text-center pt-2">
        <span className="inline-block bg-slate-100 text-slate-500 text-xs px-3 py-1 rounded-full">
          {reportMode
            ? "Full Vehicle Report \u00B7 Powered by DVLA, DVSA & Experian data"
            : "Free Check \u00B7 Powered by DVLA & DVSA data"}
        </span>
      </div>

      {/* Legal disclaimer */}
      <p className="text-xs text-slate-400 text-center mt-4 max-w-2xl mx-auto">
        This report is for informational purposes only and should not be the sole basis for a purchasing decision. Data sourced from DVLA, DVSA, and third-party providers &mdash; accuracy not guaranteed. We recommend an independent mechanical inspection before purchase. See our{" "}
        <a href="/terms" className="underline hover:text-slate-600">Terms of Service</a>.
      </p>

      {/* Premium upsell bottom bar (mobile only) — hidden in reportMode since already paid */}
      {!reportMode && (
        <PremiumBottomBar hasPremium={hasPremium} registration={data.registration} />
      )}
    </div>
  );
}
