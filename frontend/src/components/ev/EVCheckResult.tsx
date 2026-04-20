"use client";

import { useState } from "react";
import { EVCheckResponse, captureEmail } from "@/lib/api";
import EVOverviewSections from "@/components/ev/sections/EVOverviewSections";
import EVBatterySections from "@/components/ev/sections/EVBatterySections";
import EVHistorySections from "@/components/ev/sections/EVHistorySections";
import EVFullCheckSection from "@/components/ev/sections/EVFullCheckSection";
import SectionNav, { SectionConfig } from "@/components/SectionNav";
import PremiumBottomBar from "@/components/PremiumBottomBar";

const EV_SECTIONS: SectionConfig[] = [
  { id: "ev-section-overview", label: "Overview" },
  { id: "ev-section-history", label: "History" },
  { id: "ev-section-battery", label: "EV Check", locked: true },
  { id: "ev-section-fullcheck", label: "Full Check", locked: true },
];

function EmailCapture({ registration }: { registration: string }) {
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;
    setLoading(true);
    await captureEmail(email, registration);
    setSubmitted(true);
    setLoading(false);
  };

  if (submitted) {
    return (
      <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 text-center">
        <p className="text-sm font-medium text-emerald-800">Results saved! Check your inbox for our free car buying guide.</p>
      </div>
    );
  }

  return (
    <div className="bg-slate-50 border border-slate-200 rounded-xl p-4">
      <p className="text-sm font-medium text-slate-700 mb-3">
        Get a copy of these results + a free car buying guide emailed to you
      </p>
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="your@email.com"
          required
          className="flex-1 px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-200"
        />
        <button
          type="submit"
          disabled={loading}
          className="px-4 py-2 bg-slate-800 text-white text-sm font-medium rounded-lg hover:bg-slate-700 transition-colors disabled:opacity-50 whitespace-nowrap"
        >
          {loading ? "Sending..." : "Send me this"}
        </button>
      </form>
      <p className="text-xs text-slate-400 mt-2">No spam. Unsubscribe any time.</p>
    </div>
  );
}

interface Props {
  result: EVCheckResponse;
}

export default function EVCheckResult({ result }: Props) {
  const {
    vehicle, mot_summary, mot_tests, clocking_analysis,
    mileage_timeline, failure_patterns, tax_calculation,
    safety_rating, vehicle_stats,
    battery_health, range_estimate, range_scenarios,
    charging_costs, ev_specs, lifespan_prediction,
  } = result;

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
      <SectionNav sections={EV_SECTIONS} hasPremium={false} />

      {/* Overview */}
      <div id="ev-section-overview" className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <EVOverviewSections
          vehicle={vehicle}
          mot_summary={mot_summary}
          tax_calculation={tax_calculation}
          vehicle_stats={vehicle_stats}
          safety_rating={safety_rating}
        />
      </div>

      {/* History */}
      <div id="ev-section-history" className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <EVHistorySections
          mot_summary={mot_summary}
          clocking_analysis={clocking_analysis}
          mileage_timeline={mileage_timeline}
          failure_patterns={failure_patterns}
          mot_tests={mot_tests}
          vehicle={vehicle}
        />
      </div>

      {/* EV Check (battery, range, charging, lifespan) */}
      <div id="ev-section-battery" className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <EVBatterySections
          battery_health={battery_health}
          range_estimate={range_estimate}
          range_scenarios={range_scenarios}
          charging_costs={charging_costs}
          ev_specs={ev_specs}
          lifespan_prediction={lifespan_prediction}
        />
      </div>

      {/* Full Check (finance, stolen, write-off, etc.) */}
      <div id="ev-section-fullcheck">
        <EVFullCheckSection registration={result.registration} />
      </div>

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
            {["Battery Health Score", "Real-World Range", "Charging Cost Comparison", "Lifespan Prediction", "AI Expert Verdict", "PDF Report & Email"].map((item) => (
              <div key={item} className="flex items-center gap-2">
                <svg className="w-4 h-4 text-emerald-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                </svg>
                <span className="text-sm text-slate-700">{item}</span>
              </div>
            ))}
          </div>
          <div className="mt-5 flex items-center gap-4">
            <a
              href="#unlock"
              className="inline-flex items-center gap-2 px-6 py-2.5 bg-emerald-600 text-white font-semibold rounded-lg hover:bg-emerald-700 transition-colors text-sm"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
              </svg>
              Get EV Health Check &mdash; &pound;8.99
            </a>
            <span className="text-xs text-slate-400">Delivered as PDF within 60 seconds</span>
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
          <div className="mt-5 flex items-center gap-4">
            <a
              href="#unlock"
              className="inline-flex items-center gap-2 px-6 py-2.5 bg-teal-600 text-white font-semibold rounded-lg hover:bg-teal-700 transition-colors text-sm"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
              </svg>
              Get EV Complete &mdash; &pound;13.99
            </a>
            <span className="text-xs text-slate-400">One-off payment &middot; No subscription</span>
          </div>
        </div>
      </div>

      {/* Email capture */}
      <EmailCapture registration={result.registration} />

      {/* Free tier badge */}
      <div className="text-center pt-2">
        <span className="inline-block bg-slate-100 text-slate-500 text-xs px-3 py-1 rounded-full">
          Free EV Check &middot; Powered by DVLA &amp; DVSA data
        </span>
      </div>

      {/* Legal disclaimer */}
      <p className="text-xs text-slate-400 text-center mt-4 max-w-2xl mx-auto">
        This report is for informational purposes only and should not be the sole basis for a purchasing decision. Data sourced from DVLA, DVSA, and third-party providers &mdash; accuracy not guaranteed. We recommend an independent mechanical inspection before purchase. See our{" "}
        <a href="/terms" className="underline hover:text-slate-600">Terms of Service</a>.
      </p>

      {/* Premium upsell bottom bar (mobile only) */}
      <PremiumBottomBar hasPremium={false} variant="ev" registration={result.registration} />
    </div>
  );
}
