"use client";

import { useState } from "react";
import { FreeCheckResponse, MOTTestRecord, SalvageCheck, KeeperHistory, HighRiskCheck, PreviousSearches } from "@/lib/api";
import Badge from "@/components/ui/Badge";
import Card from "@/components/ui/Card";
import ScoreGauge from "@/components/ui/ScoreGauge";

/* Locked/blurred preview card for paid tier data */
function LockedCard({
  title,
  icon,
  tier,
  children,
}: {
  title: string;
  icon: JSX.Element;
  tier: "basic" | "premium";
  children: React.ReactNode;
}) {
  const isPremium = tier === "premium";
  const tierLabel = isPremium ? "Premium" : "Full Report";
  const tierPrice = isPremium ? "\u00A39.99" : "\u00A33.99";

  return (
    <div className="relative bg-white border border-slate-200 rounded-xl overflow-hidden">
      {/* Card header */}
      <div className="flex items-center gap-2 px-4 py-3 border-b border-slate-100 bg-slate-50">
        <span className="text-slate-400">{icon}</span>
        <h3 className="text-sm font-semibold text-slate-400">{title}</h3>
        <span className={`ml-auto text-xs font-medium px-2 py-0.5 rounded-full ${isPremium ? "bg-purple-100 text-purple-700" : "bg-blue-100 text-blue-700"}`}>
          {tierLabel}
        </span>
      </div>
      {/* Blurred content */}
      <div className="p-4 select-none" style={{ filter: "blur(5px)" }}>
        {children}
      </div>
      {/* Unlock overlay */}
      <div className="absolute inset-0 top-[44px] bg-gradient-to-t from-white via-white/90 to-white/60 flex flex-col items-center justify-center">
        <svg className={`w-8 h-8 mb-2 ${isPremium ? "text-purple-400" : "text-blue-400"}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
        </svg>
        <a
          href="#full-report"
          className={`px-4 py-2 text-white text-xs font-semibold rounded-lg transition-colors ${isPremium ? "bg-purple-600 hover:bg-purple-700" : "bg-blue-600 hover:bg-blue-700"}`}
        >
          Unlock with {tierLabel} &mdash; {tierPrice}
        </a>
      </div>
    </div>
  );
}

function DetailRow({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex justify-between py-1.5 border-b border-slate-100 last:border-0">
      <span className="text-sm text-slate-500">{label}</span>
      <span className="text-sm font-medium text-slate-900">{value ?? "N/A"}</span>
    </div>
  );
}

/* Mini SVG line chart for mileage readings with hover tooltips */
function MileageChart({ readings }: { readings: { date: string; miles: number }[] }) {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const [tooltipPos, setTooltipPos] = useState({ x: 0, y: 0 });

  if (readings.length < 2) return null;

  const width = 300;
  const height = 80;
  const padding = { top: 8, right: 8, bottom: 8, left: 8 };
  const innerW = width - padding.left - padding.right;
  const innerH = height - padding.top - padding.bottom;

  const minMiles = Math.min(...readings.map((r) => r.miles));
  const maxMiles = Math.max(...readings.map((r) => r.miles));
  const range = maxMiles - minMiles || 1;

  const pointCoords = readings.map((r, i) => ({
    x: padding.left + (i / (readings.length - 1)) * innerW,
    y: padding.top + innerH - ((r.miles - minMiles) / range) * innerH,
  }));

  const points = pointCoords.map((p) => `${p.x},${p.y}`);

  const areaPoints = [
    `${padding.left},${height - padding.bottom}`,
    ...points,
    `${padding.left + innerW},${height - padding.bottom}`,
  ];

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const relativeX = (e.clientX - rect.left) / rect.width;

    let closestIdx = 0;
    let closestDist = Infinity;
    pointCoords.forEach((p, i) => {
      const dist = Math.abs(relativeX - p.x / width);
      if (dist < closestDist) {
        closestDist = dist;
        closestIdx = i;
      }
    });

    setHoveredIndex(closestIdx);
    setTooltipPos({
      x: (pointCoords[closestIdx].x / width) * rect.width,
      y: (pointCoords[closestIdx].y / height) * rect.height,
    });
  };

  const hovered = hoveredIndex !== null ? readings[hoveredIndex] : null;

  return (
    <div
      className="relative cursor-crosshair"
      onMouseMove={handleMouseMove}
      onMouseLeave={() => setHoveredIndex(null)}
    >
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-20" preserveAspectRatio="none">
        <polygon points={areaPoints.join(" ")} fill="url(#mileageGradient)" />
        <polyline points={points.join(" ")} fill="none" stroke="#2563eb" strokeWidth="2" strokeLinejoin="round" strokeLinecap="round" />
        <defs>
          <linearGradient id="mileageGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#2563eb" stopOpacity="0.15" />
            <stop offset="100%" stopColor="#2563eb" stopOpacity="0" />
          </linearGradient>
        </defs>
      </svg>

      {hoveredIndex !== null && (
        <>
          {/* Vertical guide line */}
          <div
            className="absolute top-0 bottom-0 w-px bg-blue-300 pointer-events-none"
            style={{ left: tooltipPos.x }}
          />
          {/* Dot on data point */}
          <div
            className="absolute w-3 h-3 bg-blue-600 rounded-full border-2 border-white shadow-md pointer-events-none"
            style={{ left: tooltipPos.x - 6, top: tooltipPos.y - 6 }}
          />
        </>
      )}

      {hovered && hoveredIndex !== null && (
        <div
          className="absolute bg-slate-900 text-white text-xs px-2.5 py-1.5 rounded-lg shadow-lg pointer-events-none whitespace-nowrap z-10"
          style={{
            left: Math.max(60, Math.min(tooltipPos.x, (typeof window !== "undefined" ? 240 : 240))),
            top: Math.max(0, tooltipPos.y - 36),
            transform: "translateX(-50%)",
          }}
        >
          <span className="text-blue-300">
            {new Date(hovered.date).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" })}
          </span>
          <span className="mx-1.5 text-slate-500">&middot;</span>
          <span className="font-semibold">{hovered.miles.toLocaleString()} mi</span>
        </div>
      )}
    </div>
  );
}

/* Mini bar chart for MOT pass/fail history */
function MOTPassFailBars({ passes, failures }: { passes: number; failures: number }) {
  const total = passes + failures;
  if (total === 0) return null;
  const passPercent = Math.round((passes / total) * 100);

  return (
    <div className="mt-2">
      <div className="flex items-center gap-2 mb-1">
        <div className="flex-1 h-3 bg-slate-100 rounded-full overflow-hidden">
          <div
            className="h-full bg-emerald-500 rounded-full transition-all duration-500"
            style={{ width: `${passPercent}%` }}
          />
        </div>
        <span className="text-xs font-medium text-emerald-600 w-10 text-right">{passPercent}%</span>
      </div>
      <div className="flex justify-between text-xs text-slate-400">
        <span>{passes} passed</span>
        <span>{failures} failed</span>
      </div>
    </div>
  );
}

/* Icons for card headers */
const icons = {
  car: (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 18.75a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m3 0h6m-9 0H3.375a1.125 1.125 0 01-1.125-1.125V14.25m17.25 4.5a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m3 0H21M3.375 14.25h17.25M3.375 14.25V6.375c0-.621.504-1.125 1.125-1.125h3.026a2.999 2.999 0 012.572 1.456l.866 1.44a1 1 0 00.858.504h4.303a1.125 1.125 0 011.125 1.125V14.25" />
    </svg>
  ),
  shield: (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
    </svg>
  ),
  document: (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
    </svg>
  ),
  clock: (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  ),
  mapPin: (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z" />
      <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z" />
    </svg>
  ),
  wrench: (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M11.42 15.17l-5.523 5.523a2.625 2.625 0 01-3.712-3.712l5.523-5.523m3.712 3.712a5.338 5.338 0 01-.825-7.067m.825 7.067a5.338 5.338 0 007.067.825m-7.892-7.892a5.338 5.338 0 017.067-.826" />
    </svg>
  ),
  currency: (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M14.121 7.629A3 3 0 009.017 9.43c-.023.212-.002.425.028.636l.506 3.541a4.5 4.5 0 01-.43 2.65L9 16.5l1.539-.513a2.25 2.25 0 011.422 0l.655.218a2.25 2.25 0 001.718-.122L15 15.75M8.25 12H12m9 0a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  ),
  star: (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.204-3.602a.563.563 0 01.321-.988l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z" />
    </svg>
  ),
  chart: (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
    </svg>
  ),
  alert: (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
    </svg>
  ),
  swap: (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 21L3 16.5m0 0L7.5 12M3 16.5h13.5m0-13.5L21 7.5m0 0L16.5 12M21 7.5H7.5" />
    </svg>
  ),
  users: (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z" />
    </svg>
  ),
  search: (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
    </svg>
  ),
};

/* Star rating display for NCAP */
function StarRating({ stars, max = 5 }: { stars: number; max?: number }) {
  return (
    <div className="flex items-center gap-0.5">
      {Array.from({ length: max }, (_, i) => (
        <svg
          key={i}
          className={`w-5 h-5 ${i < stars ? "text-amber-400" : "text-slate-200"}`}
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
        </svg>
      ))}
    </div>
  );
}

/* Individual MOT test accordion item */
function MOTTestItem({ test }: { test: MOTTestRecord }) {
  const [open, setOpen] = useState(false);
  const hasDefects = test.advisories.length > 0 || test.failures.length > 0 || test.dangerous.length > 0;

  return (
    <div className="border border-slate-100 rounded-lg overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between p-3 text-left hover:bg-slate-50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <Badge
            variant={test.result === "PASSED" ? "pass" : "fail"}
            label={test.result}
          />
          <span className="text-sm text-slate-700">{test.date}</span>
          {test.odometer !== null && (
            <span className="text-xs text-slate-400 font-mono">
              {test.odometer.toLocaleString()} mi
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {hasDefects && (
            <span className="text-xs text-slate-400">{test.total_defects} item{test.total_defects !== 1 ? "s" : ""}</span>
          )}
          <svg
            className={`w-4 h-4 text-slate-400 transition-transform ${open ? "rotate-180" : ""}`}
            fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
          </svg>
        </div>
      </button>
      {open && hasDefects && (
        <div className="px-3 pb-3 space-y-1">
          {test.dangerous.map((d, i) => (
            <div key={`d-${i}`} className="text-sm bg-red-50 text-red-800 px-2 py-1 rounded flex items-start gap-1.5">
              <span className="text-xs font-bold text-red-600 mt-0.5 flex-shrink-0">DANGEROUS</span>
              <span>{d.text}</span>
            </div>
          ))}
          {test.failures.map((f, i) => (
            <div key={`f-${i}`} className="text-sm bg-amber-50 text-amber-800 px-2 py-1 rounded flex items-start gap-1.5">
              <span className="text-xs font-bold text-amber-600 mt-0.5 flex-shrink-0">{f.type}</span>
              <span>{f.text}</span>
            </div>
          ))}
          {test.advisories.map((a, i) => (
            <div key={`a-${i}`} className="text-sm bg-blue-50 text-blue-800 px-2 py-1 rounded flex items-start gap-1.5">
              <span className="text-xs font-bold text-blue-600 mt-0.5 flex-shrink-0">ADVISORY</span>
              <span>{a.text}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function CheckResult({ data }: { data: FreeCheckResponse }) {
  const {
    vehicle, mot_summary, mot_tests, clocking_analysis, condition_score,
    ulez_compliance, mileage_timeline, failure_patterns,
    tax_calculation, safety_rating, vehicle_stats,
    finance_check, stolen_check, write_off_check, plate_changes, valuation,
    salvage_check, keeper_history, high_risk, previous_searches,
  } = data;

  return (
    <div className="space-y-6">
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
            {data.data_sources.length > 0 && (
              <span className="ml-2 text-slate-400">
                Sources: {data.data_sources.join(", ")}
              </span>
            )}
          </p>
        </div>
        {condition_score !== null && (
          <ScoreGauge score={condition_score} size={110} />
        )}
      </div>

      {/* EV Cross-sell Banner */}
      {vehicle?.fuel_type && ["ELECTRICITY", "ELECTRIC DIESEL", "ELECTRIC PETROL"].includes(vehicle.fuel_type.toUpperCase()) && (
        <a
          href="/ev"
          className="block bg-emerald-50 border border-emerald-200 rounded-xl p-4 hover:bg-emerald-100 transition-colors group"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-emerald-100 flex items-center justify-center flex-shrink-0">
              <svg className="w-5 h-5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
              </svg>
            </div>
            <div className="flex-1">
              <p className="font-semibold text-emerald-800">This is an electric vehicle</p>
              <p className="text-sm text-emerald-700 mt-0.5">
                Try our EV Health Check for battery health, real-world range, and charging cost analysis.
              </p>
            </div>
            <svg className="w-5 h-5 text-emerald-400 group-hover:translate-x-1 transition-transform flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
            </svg>
          </div>
        </a>
      )}

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

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* 1. Vehicle Identity */}
        {vehicle && (
          <Card title="Vehicle Identity" icon={icons.car} status="neutral">
            <DetailRow label="Make" value={vehicle.make} />
            <DetailRow label="Colour" value={vehicle.colour} />
            <DetailRow label="Fuel Type" value={vehicle.fuel_type} />
            <DetailRow label="Year" value={vehicle.year_of_manufacture} />
            <DetailRow
              label="Engine"
              value={
                vehicle.engine_capacity
                  ? `${vehicle.engine_capacity}cc`
                  : null
              }
            />
            <DetailRow
              label="CO2"
              value={
                vehicle.co2_emissions
                  ? `${vehicle.co2_emissions} g/km`
                  : null
              }
            />
            <DetailRow label="Euro Status" value={vehicle.euro_status} />
            <DetailRow label="Type Approval" value={vehicle.type_approval} />
          </Card>
        )}

        {/* 2. Valuation */}
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

        {/* 3. Tax & MOT Status */}
        {vehicle && (
          <Card
            title="Tax & MOT Status"
            icon={icons.shield}
            status={
              vehicle.tax_status === "Taxed" && vehicle.mot_status === "Valid"
                ? "pass"
                : vehicle.tax_status !== "Taxed" || (vehicle.mot_status !== "Valid" && vehicle.mot_status !== "No details held by DVLA")
                ? "fail"
                : "neutral"
            }
          >
            <DetailRow
              label="Tax Status"
              value={
                <Badge
                  variant={
                    vehicle.tax_status === "Taxed" ? "pass" : "fail"
                  }
                  label={vehicle.tax_status || "Unknown"}
                />
              }
            />
            <DetailRow label="Tax Due" value={vehicle.tax_due_date} />
            <DetailRow
              label="MOT Status"
              value={
                <Badge
                  variant={
                    vehicle.mot_status === "Valid" ? "pass" : vehicle.mot_status === "No details held by DVLA" ? "neutral" : "fail"
                  }
                  label={vehicle.mot_status || "Unknown"}
                />
              }
            />
            <DetailRow label="MOT Expiry" value={vehicle.mot_expiry_date} />
            <DetailRow
              label="V5C (Logbook) Issued"
              value={vehicle.date_of_last_v5c_issued}
            />
            {vehicle_stats?.v5c_days_since !== null && vehicle_stats?.v5c_days_since !== undefined && vehicle_stats.v5c_days_since <= 90 && (
              <div className="flex items-start gap-2 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2 mt-1 mb-1">
                <svg className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
                </svg>
                <div>
                  <span className="text-xs font-semibold text-amber-800">Recently Issued</span>
                  <p className="text-xs text-amber-700">V5C issued {vehicle_stats.v5c_days_since} days ago &mdash; may indicate a recent ownership change. Ask the seller how long they&apos;ve owned the car.</p>
                </div>
              </div>
            )}
            <DetailRow
              label="Export Marker"
              value={
                vehicle.marked_for_export ? (
                  <Badge variant="warn" label="Marked for Export" />
                ) : (
                  "No"
                )
              }
            />
          </Card>
        )}

        {/* 4. Finance Check */}
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

        {/* 5. Stolen Check */}
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

        {/* 6. Write-off Check */}
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

        {/* 6b. Salvage Check */}
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

        {/* 6c. Keeper History */}
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

        {/* 6d. High Risk Indicators */}
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

        {/* 6e. Previous Searches */}
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

        {/* 7. MOT Summary */}
        {mot_summary && (
          <Card
            title="MOT History"
            icon={icons.document}
            status={
              mot_summary.total_tests > 0
                ? mot_summary.total_passes / mot_summary.total_tests >= 0.7
                  ? "pass"
                  : "warn"
                : "neutral"
            }
          >
            <DetailRow label="Total Tests" value={mot_summary.total_tests} />
            <DetailRow label="Passes" value={mot_summary.total_passes} />
            <DetailRow label="Failures" value={mot_summary.total_failures} />
            <MOTPassFailBars passes={mot_summary.total_passes} failures={mot_summary.total_failures} />
            {mot_summary.latest_test && (
              <>
                <div className="mt-3 pt-3 border-t border-slate-100" />
                <DetailRow
                  label="Latest Test"
                  value={
                    <span className="flex items-center gap-1.5">
                      {mot_summary.latest_test.date}{" "}
                      <Badge
                        variant={
                          mot_summary.latest_test.result === "PASSED"
                            ? "pass"
                            : "fail"
                        }
                        label={mot_summary.latest_test.result || ""}
                      />
                    </span>
                  }
                />
                <DetailRow
                  label="Current Mileage"
                  value={
                    mot_summary.current_odometer
                      ? `${Number(mot_summary.current_odometer).toLocaleString()} miles`
                      : "N/A"
                  }
                />
                <DetailRow
                  label="MOT Expiry"
                  value={mot_summary.latest_test.expiry_date}
                />
              </>
            )}
          </Card>
        )}

        {/* 8. Mileage & Clocking */}
        {clocking_analysis && (
          <Card
            title="Mileage Analysis"
            icon={icons.clock}
            status={
              clocking_analysis.clocked
                ? "fail"
                : clocking_analysis.risk_level === "none"
                ? "pass"
                : clocking_analysis.risk_level === "unknown"
                ? "neutral"
                : "warn"
            }
          >
            <div className="mb-3">
              {clocking_analysis.clocked ? (
                <div className="flex items-center gap-2 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
                  <svg className="w-5 h-5 text-red-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
                  </svg>
                  <span className="text-sm font-semibold text-red-800">MILEAGE DISCREPANCY FOUND</span>
                </div>
              ) : clocking_analysis.risk_level === "none" ? (
                <div className="flex items-center gap-2 bg-emerald-50 border border-emerald-200 rounded-lg px-3 py-2">
                  <svg className="w-5 h-5 text-emerald-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span className="text-sm font-semibold text-emerald-800">Mileage Consistent</span>
                </div>
              ) : (
                <Badge
                  variant={
                    clocking_analysis.risk_level === "unknown"
                      ? "neutral"
                      : "warn"
                  }
                  label={
                    clocking_analysis.risk_level === "unknown"
                      ? "Insufficient Data"
                      : `${clocking_analysis.risk_level.toUpperCase()} RISK`
                  }
                  size="md"
                />
              )}
            </div>
            {clocking_analysis.reason && (
              <p className="text-sm text-slate-500 mb-2">
                {clocking_analysis.reason}
              </p>
            )}
            {clocking_analysis.flags.map((flag, i) => (
              <div
                key={i}
                className={`text-sm p-2 rounded mb-1 ${
                  flag.severity === "high"
                    ? "bg-red-50 text-red-800"
                    : flag.severity === "medium"
                    ? "bg-amber-50 text-amber-800"
                    : "bg-slate-50 text-slate-700"
                }`}
              >
                {flag.detail}
              </div>
            ))}
            {mileage_timeline.length >= 2 && (
              <div className="mt-3 pt-3 border-t border-slate-100">
                <p className="text-xs text-slate-400 mb-2">
                  Mileage Timeline ({mileage_timeline.length} readings)
                </p>
                <MileageChart readings={mileage_timeline} />
                <div className="flex justify-between text-xs text-slate-400 mt-1">
                  <span>{mileage_timeline[0]?.date}</span>
                  <span>{mileage_timeline[mileage_timeline.length - 1]?.date}</span>
                </div>
              </div>
            )}
            {mileage_timeline.length === 1 && (
              <div className="mt-3 pt-3 border-t border-slate-100">
                <p className="text-xs text-slate-400 mb-2">
                  Mileage Timeline (1 reading)
                </p>
                <div className="flex justify-between text-xs text-slate-600">
                  <span>{mileage_timeline[0].date}</span>
                  <span className="font-mono">{mileage_timeline[0].miles.toLocaleString()} mi</span>
                </div>
              </div>
            )}
          </Card>
        )}

        {/* 9. Plate Changes */}
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
                {write_off_check?.written_off && (
                  <div className="text-xs text-red-600 bg-red-50 rounded px-2 py-1 font-medium">
                    Plate change after insurance write-off — potential red flag
                  </div>
                )}
              </div>
            )}
            <div className="mt-2 text-xs text-slate-400 bg-slate-50 rounded px-2 py-1">
              Source: {plate_changes.data_source}
            </div>
          </Card>
        )}

        {/* 10. Clean Air Zones */}
        {ulez_compliance && (
          <Card
            title="UK Clean Air Zones"
            icon={icons.mapPin}
            status={
              ulez_compliance.compliant === true
                ? "pass"
                : ulez_compliance.compliant === false
                ? "fail"
                : "neutral"
            }
          >
            <div className="mb-3 flex items-center gap-3">
              <Badge
                variant={
                  ulez_compliance.compliant === true
                    ? "pass"
                    : ulez_compliance.compliant === false
                    ? "fail"
                    : "neutral"
                }
                label={
                  ulez_compliance.compliant === true
                    ? "ALL ZONES CLEAR"
                    : ulez_compliance.compliant === false
                    ? "NON-COMPLIANT"
                    : "UNKNOWN"
                }
                size="md"
              />
              {ulez_compliance.total_zones && (
                <span className="text-xs text-slate-400">
                  {ulez_compliance.compliant_zones}/{ulez_compliance.total_zones} zones
                </span>
              )}
            </div>
            <p className="text-sm text-slate-600 mb-3">
              {ulez_compliance.reason}
            </p>
            {ulez_compliance.daily_charge && (
              <div className="text-sm text-red-600 font-medium mb-3 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
                Charges: {ulez_compliance.daily_charge}
              </div>
            )}
            {ulez_compliance.zone_details && ulez_compliance.zone_details.length > 0 ? (
              <>
                {/* Zones that affect cars */}
                <p className="text-xs font-medium text-slate-500 mb-1.5">Zones affecting private cars</p>
                <div className="space-y-1 mb-3">
                  {ulez_compliance.zone_details
                    .filter((z) => z.cars_affected)
                    .map((z) => (
                      <div key={z.zone_id} className="flex items-center justify-between text-sm">
                        <span className="text-slate-700">{z.name}</span>
                        <span className="flex items-center gap-1.5">
                          {!z.compliant && (
                            <span className="text-xs text-slate-400">{z.charge}</span>
                          )}
                          <Badge
                            variant={z.compliant ? "pass" : "fail"}
                            label={z.compliant ? "Clear" : "Charge"}
                          />
                        </span>
                      </div>
                    ))}
                </div>
                {/* Zones that don't affect cars (collapsed) */}
                <p className="text-xs font-medium text-slate-400 mb-1.5">Commercial-only zones (cars exempt)</p>
                <div className="space-y-1">
                  {ulez_compliance.zone_details
                    .filter((z) => !z.cars_affected)
                    .map((z) => (
                      <div key={z.zone_id} className="flex items-center justify-between text-sm">
                        <span className="text-slate-400">{z.name}</span>
                        <Badge variant="neutral" label="Exempt" />
                      </div>
                    ))}
                </div>
              </>
            ) : (
              /* Fallback to simple zones dict */
              Object.keys(ulez_compliance.zones).length > 0 && (
                <div className="space-y-1">
                  {Object.entries(ulez_compliance.zones).map(([zone, ok]) => (
                    <DetailRow
                      key={zone}
                      label={zone.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
                      value={
                        <Badge
                          variant={ok ? "pass" : "fail"}
                          label={ok ? "Pass" : "Fail"}
                        />
                      }
                    />
                  ))}
                </div>
              )
            )}
          </Card>
        )}

        {/* 11. Road Tax / VED */}
        {tax_calculation && (
          <Card title="Road Tax (VED)" icon={icons.currency} status="neutral">
            <DetailRow label="Tax Band" value={`Band ${tax_calculation.band}`} />
            <DetailRow label="CO2 Range" value={tax_calculation.band_range} />
            <DetailRow label="CO2 Emissions" value={`${tax_calculation.co2_emissions} g/km`} />
            <DetailRow label="Fuel Type" value={tax_calculation.fuel_type} />
            <div className="mt-3 pt-3 border-t border-slate-100" />
            <DetailRow
              label="First Year Rate"
              value={
                <span className="font-mono font-bold text-slate-900">
                  {tax_calculation.first_year_rate === 0 ? "FREE" : `£${tax_calculation.first_year_rate}`}
                </span>
              }
            />
            <DetailRow
              label="Annual Rate (Year 2+)"
              value={
                <span className="font-mono font-bold text-slate-900">
                  {tax_calculation.annual_rate === 0 ? "FREE" : `£${tax_calculation.annual_rate}`}
                </span>
              }
            />
            <DetailRow label="6-Month Payment" value={`£${tax_calculation.six_month_rate}`} />
            {tax_calculation.is_electric && (
              <div className="mt-2 text-xs text-emerald-600 bg-emerald-50 rounded px-2 py-1">
                Electric vehicle — zero emissions
              </div>
            )}
            {tax_calculation.is_diesel && (
              <div className="mt-2 text-xs text-amber-600 bg-amber-50 rounded px-2 py-1">
                Diesel supplement may apply (first year)
              </div>
            )}
          </Card>
        )}

        {/* 12. Safety Rating */}
        {safety_rating && (
          <Card title="Safety Rating" icon={icons.star} status={safety_rating.stars >= 4 ? "pass" : safety_rating.stars >= 3 ? "warn" : "fail"}>
            <div className="mb-3">
              <StarRating stars={safety_rating.stars} />
              <p className="text-xs text-slate-400 mt-1">
                {safety_rating.source} &middot; {safety_rating.year_range} &middot; Tested {safety_rating.test_year}
              </p>
            </div>
            <div className="space-y-2">
              {[
                { label: "Adult Occupant", value: safety_rating.adult },
                { label: "Child Occupant", value: safety_rating.child },
                { label: "Pedestrian", value: safety_rating.pedestrian },
                { label: "Safety Assist", value: safety_rating.safety_assist },
              ].map(({ label, value }) => (
                <div key={label}>
                  <div className="flex justify-between text-xs mb-0.5">
                    <span className="text-slate-500">{label}</span>
                    <span className="font-medium text-slate-700">{value}%</span>
                  </div>
                  <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${
                        value >= 80 ? "bg-emerald-500" : value >= 60 ? "bg-amber-400" : "bg-red-400"
                      }`}
                      style={{ width: `${value}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </Card>
        )}

        {/* 13. Vehicle Statistics */}
        {vehicle_stats && (
          <Card title="Vehicle Statistics" icon={icons.chart} status="neutral">
            {vehicle_stats.vehicle_age_years !== null && (
              <DetailRow label="Vehicle Age" value={`${vehicle_stats.vehicle_age_years} years`} />
            )}
            {vehicle_stats.estimated_annual_mileage !== null && (
              <DetailRow
                label="Est. Annual Mileage"
                value={
                  <span className="flex items-center gap-1.5">
                    {vehicle_stats.estimated_annual_mileage.toLocaleString()} mi/yr
                    {vehicle_stats.mileage_assessment && (
                      <Badge
                        variant={
                          vehicle_stats.mileage_assessment === "High mileage" ? "warn"
                            : vehicle_stats.mileage_assessment === "Below average mileage" ? "info"
                            : "neutral"
                        }
                        label={vehicle_stats.mileage_assessment}
                      />
                    )}
                  </span>
                }
              />
            )}
            {vehicle_stats.total_recorded_mileage !== null && (
              <DetailRow label="Total Recorded" value={`${vehicle_stats.total_recorded_mileage.toLocaleString()} miles`} />
            )}
            {vehicle_stats.mileage_readings_count !== null && (
              <DetailRow label="MOT Readings" value={vehicle_stats.mileage_readings_count} />
            )}
            {(vehicle_stats.mot_status_detail || vehicle_stats.tax_status_detail || vehicle_stats.v5c_insight) && (
              <div className="mt-3 pt-3 border-t border-slate-100" />
            )}
            {vehicle_stats.mot_status_detail && (
              <DetailRow
                label="MOT"
                value={
                  <Badge
                    variant={vehicle_stats.mot_days_remaining !== null && vehicle_stats.mot_days_remaining < 0 ? "fail" : vehicle_stats.mot_days_remaining !== null && vehicle_stats.mot_days_remaining <= 30 ? "warn" : "pass"}
                    label={vehicle_stats.mot_status_detail}
                  />
                }
              />
            )}
            {vehicle_stats.tax_status_detail && (
              <DetailRow
                label="Tax"
                value={
                  <Badge
                    variant={vehicle_stats.tax_days_remaining !== null && vehicle_stats.tax_days_remaining < 0 ? "fail" : vehicle_stats.tax_days_remaining !== null && vehicle_stats.tax_days_remaining <= 30 ? "warn" : "pass"}
                    label={vehicle_stats.tax_status_detail}
                  />
                }
              />
            )}
            {vehicle_stats.v5c_insight && (
              <DetailRow label="V5C" value={vehicle_stats.v5c_insight} />
            )}
            {(vehicle_stats.total_advisory_items !== null || vehicle_stats.total_failure_items !== null) && (
              <>
                <div className="mt-3 pt-3 border-t border-slate-100" />
                <p className="text-xs text-slate-400 mb-2">Lifetime MOT Defect Totals</p>
                <div className="grid grid-cols-3 gap-2 text-center">
                  {vehicle_stats.total_advisory_items !== null && (
                    <div className="bg-blue-50 rounded-lg py-2">
                      <div className="text-lg font-bold text-blue-700">{vehicle_stats.total_advisory_items}</div>
                      <div className="text-xs text-blue-500">Advisories</div>
                    </div>
                  )}
                  {vehicle_stats.total_failure_items !== null && (
                    <div className="bg-amber-50 rounded-lg py-2">
                      <div className="text-lg font-bold text-amber-700">{vehicle_stats.total_failure_items}</div>
                      <div className="text-xs text-amber-500">Failures</div>
                    </div>
                  )}
                  {vehicle_stats.total_dangerous_items !== null && vehicle_stats.total_dangerous_items > 0 && (
                    <div className="bg-red-50 rounded-lg py-2">
                      <div className="text-lg font-bold text-red-700">{vehicle_stats.total_dangerous_items}</div>
                      <div className="text-xs text-red-500">Dangerous</div>
                    </div>
                  )}
                </div>
              </>
            )}
          </Card>
        )}

        {/* 14. Recurring Issues */}
        {failure_patterns.length > 0 && (
          <Card
            title="Recurring Issues"
            icon={icons.wrench}
            status={
              failure_patterns.some((p) => p.concern_level === "high")
                ? "fail"
                : failure_patterns.some((p) => p.concern_level === "medium")
                ? "warn"
                : "neutral"
            }
          >
            <div className="space-y-2">
              {failure_patterns.map((p, i) => (
                <div key={i} className="flex items-center justify-between">
                  <span className="text-sm capitalize text-slate-700">
                    {p.category}
                  </span>
                  <span className="flex items-center gap-2">
                    <span className="text-xs text-slate-400">
                      {p.occurrences}x
                    </span>
                    <Badge
                      variant={
                        p.concern_level === "high"
                          ? "fail"
                          : p.concern_level === "medium"
                          ? "warn"
                          : "neutral"
                      }
                      label={p.concern_level}
                    />
                  </span>
                </div>
              ))}
            </div>
          </Card>
        )}
        {/* --- Locked premium previews (shown when data not present) --- */}

        {!finance_check && (
          <LockedCard title="Finance Check" icon={icons.document} tier="premium">
            <div className="flex items-center gap-2 bg-emerald-50 border border-emerald-200 rounded-lg px-3 py-2 mb-3">
              <span className="text-sm font-semibold text-emerald-800">NO FINANCE OUTSTANDING</span>
            </div>
            <div className="space-y-1.5">
              <div className="flex justify-between py-1.5"><span className="text-sm text-slate-500">Agreement Type</span><span className="text-sm text-slate-700">Hire Purchase</span></div>
              <div className="flex justify-between py-1.5"><span className="text-sm text-slate-500">Finance Company</span><span className="text-sm text-slate-700">Close Brothers Ltd</span></div>
              <div className="flex justify-between py-1.5"><span className="text-sm text-slate-500">Agreement Date</span><span className="text-sm text-slate-700">14/03/2022</span></div>
            </div>
          </LockedCard>
        )}

        {!stolen_check && (
          <LockedCard title="Stolen Vehicle Check" icon={icons.shield} tier="premium">
            <div className="flex items-center gap-2 bg-emerald-50 border border-emerald-200 rounded-lg px-3 py-2 mb-3">
              <span className="text-sm font-semibold text-emerald-800">NOT REPORTED STOLEN</span>
            </div>
            <div className="space-y-1.5">
              <div className="flex justify-between py-1.5"><span className="text-sm text-slate-500">Police Database</span><span className="text-sm text-slate-700">Checked</span></div>
              <div className="flex justify-between py-1.5"><span className="text-sm text-slate-500">Status</span><span className="text-sm text-slate-700">Clear</span></div>
            </div>
          </LockedCard>
        )}

        {!write_off_check && (
          <LockedCard title="Write-off &amp; Insurance" icon={icons.alert} tier="premium">
            <div className="flex items-center gap-2 bg-emerald-50 border border-emerald-200 rounded-lg px-3 py-2 mb-3">
              <span className="text-sm font-semibold text-emerald-800">NOT WRITTEN OFF</span>
            </div>
            <div className="space-y-1.5">
              <div className="flex justify-between py-1.5"><span className="text-sm text-slate-500">Category</span><span className="text-sm text-slate-700">None</span></div>
              <div className="flex justify-between py-1.5"><span className="text-sm text-slate-500">Insurance Claims</span><span className="text-sm text-slate-700">0 records</span></div>
            </div>
          </LockedCard>
        )}

        {!valuation && (
          <LockedCard title="Market Valuation" icon={icons.currency} tier="premium">
            <div className="space-y-2 mb-3">
              <div className="flex items-center justify-between"><span className="text-sm text-slate-500">Private Sale</span><span className="text-lg font-bold text-slate-900">&pound;8,450</span></div>
              <div className="flex items-center justify-between"><span className="text-sm text-slate-500">Dealer Forecourt</span><span className="text-lg font-bold text-slate-900">&pound;10,200</span></div>
              <div className="flex items-center justify-between"><span className="text-sm text-slate-500">Trade-in</span><span className="text-lg font-bold text-slate-900">&pound;7,100</span></div>
            </div>
            <div className="h-3 bg-gradient-to-r from-amber-200 via-emerald-300 to-blue-300 rounded-full" />
          </LockedCard>
        )}

        {!salvage_check && (
          <LockedCard title="Salvage Auction Check" icon={icons.alert} tier="premium">
            <div className="flex items-center gap-2 bg-emerald-50 border border-emerald-200 rounded-lg px-3 py-2 mb-3">
              <span className="text-sm font-semibold text-emerald-800">NO SALVAGE RECORDS</span>
            </div>
            <p className="text-xs text-slate-500">Checked against UK salvage auction databases.</p>
          </LockedCard>
        )}

        {!plate_changes && (
          <LockedCard title="Plate Change History" icon={icons.swap} tier="premium">
            <div className="space-y-1.5">
              <div className="flex justify-between py-1.5"><span className="text-sm text-slate-500">Plate Changes</span><span className="text-sm text-slate-700">1 change found</span></div>
              <div className="flex justify-between py-1.5"><span className="text-sm text-slate-500">Previous Plate</span><span className="inline-block bg-yellow-50 border border-yellow-300 font-mono font-bold px-2 py-0.5 rounded text-slate-900 text-xs">AB18 XYZ</span></div>
              <div className="flex justify-between py-1.5"><span className="text-sm text-slate-500">Change Date</span><span className="text-sm text-slate-700">12/06/2023</span></div>
            </div>
          </LockedCard>
        )}

        {!keeper_history && (
          <LockedCard title="Keeper History" icon={icons.users} tier="premium">
            <div className="space-y-1.5">
              <div className="flex justify-between py-1.5"><span className="text-sm text-slate-500">Registered Keepers</span><span className="text-sm text-slate-700">3 keepers</span></div>
              <div className="flex justify-between py-1.5"><span className="text-sm text-slate-500">Last Change</span><span className="text-sm text-slate-700">12/06/2023</span></div>
            </div>
          </LockedCard>
        )}

        {!high_risk && (
          <LockedCard title="High Risk Indicators" icon={icons.alert} tier="premium">
            <div className="flex items-center gap-2 bg-emerald-50 border border-emerald-200 rounded-lg px-3 py-2 mb-3">
              <span className="text-sm font-semibold text-emerald-800">NO HIGH RISK FLAGS</span>
            </div>
            <div className="space-y-1.5">
              <div className="flex justify-between py-1.5"><span className="text-sm text-slate-500">Scrapped Marker</span><span className="text-sm text-slate-700">Clear</span></div>
              <div className="flex justify-between py-1.5"><span className="text-sm text-slate-500">Import/Export</span><span className="text-sm text-slate-700">Clear</span></div>
            </div>
          </LockedCard>
        )}

        {!previous_searches && (
          <LockedCard title="Previous Checks" icon={icons.search} tier="premium">
            <div className="space-y-1.5">
              <div className="flex justify-between py-1.5"><span className="text-sm text-slate-500">Previous Checks</span><span className="text-sm text-slate-700">7 checks found</span></div>
              <div className="flex justify-between py-1.5"><span className="text-sm text-slate-500">Last Checked</span><span className="text-sm text-slate-700">14/01/2025</span></div>
              <div className="flex justify-between py-1.5"><span className="text-sm text-slate-500">Checked By</span><span className="text-sm text-slate-700">Dealer / Finance</span></div>
            </div>
          </LockedCard>
        )}
      </div>

      {/* Full MOT Test History */}
      {mot_tests && mot_tests.length > 0 && (
        <Card title={`Full MOT History (${mot_tests.length} tests)`} icon={icons.document} status="neutral">
          <div className="space-y-2">
            {mot_tests.map((test) => (
              <MOTTestItem key={test.test_number} test={test} />
            ))}
          </div>
        </Card>
      )}

      {/* Free tier badge */}
      <div className="text-center pt-2">
        <span className="inline-block bg-slate-100 text-slate-500 text-xs px-3 py-1 rounded-full">
          Free Check &middot; Powered by DVLA &amp; DVSA data
        </span>
      </div>
    </div>
  );
}
