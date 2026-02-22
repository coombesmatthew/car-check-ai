"use client";

import { RangeScenario } from "@/lib/api";

interface Props {
  scenarios: RangeScenario[];
  officialRange?: number | null;
}

export default function RangeChart({ scenarios, officialRange }: Props) {
  if (!scenarios || scenarios.length === 0) return null;

  const maxRange = Math.max(
    officialRange || 0,
    ...scenarios.map((s) => s.estimated_miles || 0)
  );

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5">
      <h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
        <svg className="w-4 h-4 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
        </svg>
        Range by Scenario
      </h3>

      {officialRange && (
        <div className="mb-4 pb-3 border-b border-slate-100">
          <div className="flex justify-between text-sm mb-1">
            <span className="text-slate-500">Official WLTP Range</span>
            <span className="font-semibold">{officialRange} miles</span>
          </div>
          <div className="h-2 bg-slate-100 rounded-full">
            <div className="h-2 bg-slate-400 rounded-full" style={{ width: "100%" }} />
          </div>
        </div>
      )}

      <div className="space-y-3">
        {scenarios.map((s, i) => {
          const pct = maxRange > 0 ? ((s.estimated_miles || 0) / maxRange) * 100 : 0;
          const barColor = (s.temperature_c ?? 20) < 5 ? "bg-blue-400" : (s.temperature_c ?? 20) > 25 ? "bg-orange-400" : "bg-emerald-400";
          return (
            <div key={i}>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-slate-600">
                  {s.scenario}
                  {s.temperature_c !== null && <span className="text-slate-400 ml-1">({s.temperature_c}°C)</span>}
                </span>
                <span className="font-semibold">{s.estimated_miles || "—"} mi</span>
              </div>
              <div className="h-2 bg-slate-100 rounded-full">
                <div className={`h-2 ${barColor} rounded-full transition-all duration-500`} style={{ width: `${pct}%` }} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
