"use client";

import { useState } from "react";

/* Reusable sample card with coloured accent */
function SampleCard({ title, icon, children, accent = "emerald" }: { title: string; icon: React.ReactNode; children: React.ReactNode; accent?: "emerald" | "teal" | "amber" | "blue" | "red" }) {
  const accentMap = {
    emerald: "border-emerald-200 bg-emerald-50/30",
    teal: "border-teal-200 bg-teal-50/30",
    amber: "border-amber-200 bg-amber-50/30",
    blue: "border-blue-200 bg-blue-50/30",
    red: "border-red-200 bg-red-50/30",
  };
  return (
    <div className={`border rounded-lg overflow-hidden ${accentMap[accent]}`}>
      <div className="flex items-center gap-2 px-3 py-2 border-b border-slate-100 bg-white/60">
        <span className="text-slate-500">{icon}</span>
        <span className="text-xs font-semibold text-slate-700">{title}</span>
      </div>
      <div className="px-3 py-2.5">{children}</div>
    </div>
  );
}

const CheckIcon = ({ className }: { className?: string }) => (
  <svg className={className || "w-3 h-3"} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
  </svg>
);

/**
 * Static sample EV report — same for every vehicle.
 * Shows what EV Health Check and EV Complete reports include.
 * No personalised AI content is generated.
 */
export default function EVAIReport() {
  const [activeTab, setActiveTab] = useState<"ev" | "ev_complete">("ev");
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
      {/* Header — clickable to expand */}
      <button
        type="button"
        onClick={() => setExpanded(!expanded)}
        className="w-full text-left bg-gradient-to-r from-emerald-700 to-emerald-900 px-6 py-4 cursor-pointer hover:from-emerald-600 hover:to-emerald-800 transition-colors"
      >
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-emerald-200" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
                <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <h2 className="text-white font-semibold text-lg">
                What&apos;s Included
              </h2>
            </div>
            <p className="text-emerald-200 text-sm mt-0.5">
              {expanded ? "See exactly what you get with each report" : "Tap to see sample report data"}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="bg-emerald-500/30 text-emerald-100 text-xs font-medium px-2.5 py-1 rounded-full border border-emerald-400/30">
              PREVIEW
            </span>
            <svg
              className={`w-5 h-5 text-emerald-200 transition-transform duration-200 ${expanded ? "rotate-180" : ""}`}
              fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
            </svg>
          </div>
        </div>
      </button>

      {expanded && <>
      {/* Tab switcher */}
      <div className="flex border-b border-slate-200">
        <button
          onClick={() => setActiveTab("ev")}
          className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
            activeTab === "ev"
              ? "text-emerald-700 border-b-2 border-emerald-600 bg-emerald-50/50"
              : "text-slate-500 hover:text-slate-700"
          }`}
        >
          EV Health Check &mdash; &pound;8.99
        </button>
        <button
          onClick={() => setActiveTab("ev_complete")}
          className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
            activeTab === "ev_complete"
              ? "text-teal-700 border-b-2 border-teal-600 bg-teal-50/50"
              : "text-slate-500 hover:text-slate-700"
          }`}
        >
          EV Complete &mdash; &pound;13.99
        </button>
      </div>

      {/* Sample cards */}
      <div className="px-5 py-5 space-y-3">
        {/* Should You Buy This EV? */}
        <SampleCard
          title="Should You Buy This EV?"
          accent="emerald"
          icon={<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M6.633 10.5c.806 0 1.533-.446 2.031-1.08a9.041 9.041 0 012.861-2.4c.723-.384 1.35-.956 1.653-1.715a4.498 4.498 0 00.322-1.672V3a.75.75 0 01.75-.75A2.25 2.25 0 0116.5 4.5c0 1.152-.26 2.243-.723 3.218-.266.558.107 1.282.725 1.282h3.126c1.026 0 1.945.694 2.054 1.715.045.422.068.85.068 1.285a11.95 11.95 0 01-2.649 7.521c-.388.482-.987.729-1.605.729H13.48c-.483 0-.964-.078-1.423-.23l-3.114-1.04a4.501 4.501 0 00-1.423-.23H5.904M14.25 9h2.25M5.904 18.75c.083.205.173.405.27.602.197.4-.078.898-.523.898h-.908c-.889 0-1.713-.518-1.972-1.368a12 12 0 01-.521-3.507c0-1.553.295-3.036.831-4.398C3.387 10.203 4.167 9.75 5 9.75h1.053c.472 0 .745.556.5.96a8.958 8.958 0 00-1.302 4.665c0 1.194.232 2.333.654 3.375z" /></svg>}
        >
          <div className="bg-emerald-50 border border-emerald-200 rounded-md px-3 py-2 flex items-center gap-2 mb-2">
            <span className="text-lg font-bold text-emerald-700">BUY</span>
            <span className="text-xs text-slate-500">AI Verdict</span>
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            This 2022 Nissan Leaf is a strong buy. Battery retains 87% capacity, range is on-target for its age, and the MOT history is clean with no recurring EV-specific issues.
          </p>
        </SampleCard>

        {/* Battery Health */}
        <SampleCard
          title="Battery Health Score"
          accent="emerald"
          icon={<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M21 10.5h.375c.621 0 1.125.504 1.125 1.125v2.25c0 .621-.504 1.125-1.125 1.125H21M4.5 10.5H18V15H4.5v-4.5zM3.75 18h15A2.25 2.25 0 0021 15.75v-6a2.25 2.25 0 00-2.25-2.25h-15A2.25 2.25 0 001.5 9.75v6A2.25 2.25 0 003.75 18z" /></svg>}
        >
          <div className="flex items-center gap-4 mb-2">
            <div className="w-14 h-14 rounded-full border-[3px] border-emerald-400 flex items-center justify-center">
              <span className="text-lg font-bold text-emerald-600">87</span>
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-800">Grade A &mdash; Excellent</p>
              <p className="text-xs text-slate-500">13% degradation estimated over 3 years</p>
            </div>
          </div>
          <p className="text-xs text-slate-500">Based on ClearWatt battery telemetry data, comparing real-world range when new vs current.</p>
        </SampleCard>

        {/* Real-World Range */}
        <SampleCard
          title="Real-World Range Analysis"
          accent="emerald"
          icon={<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M9 6.75V15m6-6v8.25m.503 3.498l4.875-2.437c.381-.19.622-.58.622-1.006V4.82c0-.836-.88-1.38-1.628-1.006l-3.869 1.934c-.317.159-.69.159-1.006 0L9.503 3.252a1.125 1.125 0 00-1.006 0L3.622 5.689C3.24 5.88 3 6.27 3 6.695V19.18c0 .836.88 1.38 1.628 1.006l3.869-1.934c.317-.159.69-.159 1.006 0l4.994 2.497c.317.158.69.158 1.006 0z" /></svg>}
        >
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-xs text-slate-500">Range now</span>
              <span className="text-sm font-bold text-emerald-700">168&ndash;204 miles</span>
            </div>
            <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
              <div className="h-full bg-emerald-400 rounded-full" style={{ width: "76%" }} />
            </div>
            <div className="flex justify-between text-xs text-slate-400">
              <span>vs 220&ndash;268 miles when new</span>
              <span className="font-medium text-emerald-600">76% retained</span>
            </div>
          </div>
          <div className="mt-2 grid grid-cols-3 gap-1.5 text-center">
            <div className="bg-white rounded px-1.5 py-1.5 border border-emerald-100">
              <p className="text-[10px] text-slate-400">City (Mild)</p>
              <p className="text-xs font-semibold text-slate-800">214 mi</p>
            </div>
            <div className="bg-white rounded px-1.5 py-1.5 border border-emerald-100">
              <p className="text-[10px] text-slate-400">Combined</p>
              <p className="text-xs font-semibold text-slate-800">186 mi</p>
            </div>
            <div className="bg-white rounded px-1.5 py-1.5 border border-emerald-100">
              <p className="text-[10px] text-slate-400">Motorway (Cold)</p>
              <p className="text-xs font-semibold text-slate-800">128 mi</p>
            </div>
          </div>
        </SampleCard>

        {/* Charging Costs */}
        <SampleCard
          title="Charging Cost Breakdown"
          accent="emerald"
          icon={<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" /></svg>}
        >
          <div className="grid grid-cols-2 gap-x-3 gap-y-1 bg-white rounded-md px-2.5 py-2 border border-emerald-100 text-xs text-slate-600">
            <span>Home charging (7kW)</span><span className="font-medium text-right">5.2p/mile</span>
            <span>Public charger</span><span className="font-medium text-right">9.4p/mile</span>
            <span>Rapid DC (50kW+)</span><span className="font-medium text-right">13.8p/mile</span>
            <span className="border-t border-slate-100 pt-1">Full charge (home)</span><span className="font-medium text-right border-t border-slate-100 pt-1">&pound;9.80</span>
            <span className="font-semibold text-slate-800">vs Petrol saving</span>
            <span className="font-bold text-right text-emerald-700">&pound;1,080/yr</span>
          </div>
        </SampleCard>

        {/* Lifespan Prediction */}
        <SampleCard
          title="Vehicle Lifespan Prediction"
          accent="emerald"
          icon={<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}
        >
          <div className="flex items-center gap-3 mb-2">
            <span className="text-2xl font-bold text-emerald-700">8&ndash;10</span>
            <span className="text-xs text-slate-500">predicted years remaining</span>
          </div>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="bg-white rounded px-2 py-1.5 border border-emerald-100">
              <span className="text-slate-400">1-year survival</span>
              <p className="font-semibold text-slate-800">94%</p>
            </div>
            <div className="bg-white rounded px-2 py-1.5 border border-emerald-100">
              <span className="text-slate-400">Still on road</span>
              <p className="font-semibold text-slate-800">89% of model</p>
            </div>
          </div>
        </SampleCard>

        {/* PDF delivery */}
        <SampleCard
          title="AI Report &amp; PDF Emailed"
          accent="emerald"
          icon={<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75" /></svg>}
        >
          <p className="text-xs text-slate-600">Full AI-generated report with personalised verdict, battery analysis, and negotiation tips &mdash; delivered as a professional PDF to your inbox within 60 seconds.</p>
        </SampleCard>

        {/* --- EV Complete extras --- */}
        {activeTab === "ev_complete" && (
          <>
            <div className="flex items-center gap-2 mt-3 mb-1">
              <div className="flex-1 h-px bg-teal-200" />
              <span className="text-xs font-semibold text-teal-600 uppercase tracking-wide">EV Complete extras</span>
              <div className="flex-1 h-px bg-teal-200" />
            </div>

            {/* Finance Check */}
            <SampleCard
              title="Finance &amp; Outstanding Debt"
              accent="teal"
              icon={<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M2.25 18.75a60.07 60.07 0 0115.797 2.101c.727.198 1.453-.342 1.453-1.096V18.75M3.75 4.5v.75A.75.75 0 013 6h-.75m0 0v-.375c0-.621.504-1.125 1.125-1.125H20.25M2.25 6v9m18-10.5v.75c0 .414.336.75.75.75h.75m-1.5-1.5h.375c.621 0 1.125.504 1.125 1.125v9.75c0 .621-.504 1.125-1.125 1.125h-.375m1.5-1.5H21a.75.75 0 00-.75.75v.75m0 0H3.75m0 0h-.375a1.125 1.125 0 01-1.125-1.125V15m1.5 1.5v-.75A.75.75 0 003 15h-.75M15 10.5a3 3 0 11-6 0 3 3 0 016 0zm3 0h.008v.008H18V10.5zm-12 0h.008v.008H6V10.5z" /></svg>}
            >
              <div className="flex items-center gap-2 mb-1.5">
                <span className="w-5 h-5 rounded-full bg-emerald-100 flex items-center justify-center">
                  <CheckIcon className="w-3 h-3 text-emerald-600" />
                </span>
                <span className="text-xs font-semibold text-emerald-700">No outstanding finance</span>
              </div>
              <p className="text-xs text-slate-500">Checked against all major UK finance providers. Safe to purchase.</p>
            </SampleCard>

            {/* Stolen Check */}
            <SampleCard
              title="Stolen Vehicle Check"
              accent="teal"
              icon={<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" /></svg>}
            >
              <div className="flex items-center gap-2 mb-1.5">
                <span className="w-5 h-5 rounded-full bg-emerald-100 flex items-center justify-center">
                  <CheckIcon className="w-3 h-3 text-emerald-600" />
                </span>
                <span className="text-xs font-semibold text-emerald-700">Not reported stolen</span>
              </div>
              <p className="text-xs text-slate-500">Checked against the Police National Computer (PNC) database.</p>
            </SampleCard>

            {/* Write-off */}
            <SampleCard
              title="Write-off &amp; Salvage History"
              accent="teal"
              icon={<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" /></svg>}
            >
              <div className="flex items-center gap-2 mb-1.5">
                <span className="w-5 h-5 rounded-full bg-emerald-100 flex items-center justify-center">
                  <CheckIcon className="w-3 h-3 text-emerald-600" />
                </span>
                <span className="text-xs font-semibold text-emerald-700">No write-off history</span>
              </div>
              <p className="text-xs text-slate-500">No Category A, B, N, or S insurance write-off records found.</p>
            </SampleCard>

            {/* Valuation */}
            <SampleCard
              title="Market Valuation"
              accent="teal"
              icon={<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M12 6v12m-3-2.818l.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.45-.22-2.003-.659-1.106-.879-1.106-2.303 0-3.182s2.9-.879 4.006 0l.415.33M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}
            >
              <div className="grid grid-cols-2 gap-2">
                <div className="bg-white rounded-md px-2.5 py-2 border border-teal-100">
                  <p className="text-[10px] text-slate-400 uppercase">Private Sale</p>
                  <p className="text-sm font-bold text-slate-900">&pound;18,500</p>
                </div>
                <div className="bg-white rounded-md px-2.5 py-2 border border-teal-100">
                  <p className="text-[10px] text-slate-400 uppercase">Dealer</p>
                  <p className="text-sm font-bold text-slate-900">&pound;20,200</p>
                </div>
                <div className="bg-white rounded-md px-2.5 py-2 border border-teal-100">
                  <p className="text-[10px] text-slate-400 uppercase">Trade-in</p>
                  <p className="text-sm font-bold text-slate-900">&pound;16,100</p>
                </div>
                <div className="bg-white rounded-md px-2.5 py-2 border border-teal-100">
                  <p className="text-[10px] text-slate-400 uppercase">Part Exchange</p>
                  <p className="text-sm font-bold text-slate-900">&pound;15,300</p>
                </div>
              </div>
            </SampleCard>

            {/* Plate & Keeper */}
            <SampleCard
              title="Plate &amp; Keeper History"
              accent="teal"
              icon={<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M15 9h3.75M15 12h3.75M15 15h3.75M4.5 19.5h15a2.25 2.25 0 002.25-2.25V6.75A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25v10.5A2.25 2.25 0 004.5 19.5zm6-10.125a1.875 1.875 0 11-3.75 0 1.875 1.875 0 013.75 0zm1.294 6.336a6.721 6.721 0 01-3.17.789 6.721 6.721 0 01-3.168-.789 3.376 3.376 0 016.338 0z" /></svg>}
            >
              <div className="flex items-center gap-2 mb-1.5">
                <span className="w-5 h-5 rounded-full bg-emerald-100 flex items-center justify-center">
                  <CheckIcon className="w-3 h-3 text-emerald-600" />
                </span>
                <span className="text-xs font-semibold text-emerald-700">No plate changes found</span>
              </div>
              <p className="text-xs text-slate-500">2 registered keepers since first registration. V5C issued 8 months ago.</p>
            </SampleCard>
          </>
        )}

        {/* Upsell nudge when on EV Health tab */}
        {activeTab === "ev" && (
          <div className="mt-2 bg-teal-50 border border-teal-200 rounded-lg p-3 text-center">
            <p className="text-xs text-teal-700 font-medium mb-1">Want finance, stolen, write-off &amp; valuation checks too?</p>
            <button
              onClick={() => setActiveTab("ev_complete")}
              className="text-xs font-semibold text-teal-600 hover:text-teal-800 underline underline-offset-2"
            >
              See what EV Complete includes &rarr;
            </button>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="border-t border-slate-200 px-6 py-4 bg-slate-50">
        <p className="text-xs text-slate-400 text-center">
          Preview data shown above. Actual reports use real DVLA, DVSA, ClearWatt, EV Database, and AutoPredict data for your specific vehicle.
        </p>
      </div>
      </>}
    </div>
  );
}
