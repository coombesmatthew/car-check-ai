"use client";

import { useState } from "react";
import { MOTTestRecord } from "@/lib/api";
import Badge from "@/components/ui/Badge";

/* DetailRow is the ONLY component for displaying label/value data.
   Do not create custom flex layouts for numbers, prices, or stats.
   All values render as text-sm font-medium text-slate-900. */
export function DetailRow({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex justify-between py-1.5 border-b border-slate-100 last:border-0">
      <span className="text-sm text-slate-500">{label}</span>
      <span className="text-sm font-medium text-slate-900">{value ?? "N/A"}</span>
    </div>
  );
}

/* Mini SVG line chart for mileage readings with hover tooltips */
export function MileageChart({ readings }: { readings: { date: string; miles: number }[] }) {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const [tooltipPos, setTooltipPos] = useState({ x: 0, y: 0 });

  if (readings.length < 2) return null;

  const width = 300;
  const height = 160;
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
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-40" preserveAspectRatio="none">
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
            left: Math.max(60, Math.min(tooltipPos.x, 240)),
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
export function MOTPassFailBars({ passes, failures }: { passes: number; failures: number }) {
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

/* Star rating display for NCAP */
export function StarRating({ stars, max = 5 }: { stars: number; max?: number }) {
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
export function MOTTestItem({ test, defaultOpen = false }: { test: MOTTestRecord; defaultOpen?: boolean }) {
  const [open, setOpen] = useState(defaultOpen);
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

/* Collapsible recurring issue category accordion */
export function RecurringIssueItem({ category, occurrences, concernLevel, defects }: {
  category: string;
  occurrences: number;
  concernLevel: string;
  defects: { text: string; type: string; date: string }[];
}) {
  const [open, setOpen] = useState(false);

  return (
    <div className="border border-slate-100 rounded-lg overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between p-3 text-left hover:bg-slate-50 transition-colors"
      >
        <span className="text-sm font-medium capitalize text-slate-700">
          {category}
        </span>
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400">
            {occurrences} issue{occurrences !== 1 ? "s" : ""}
          </span>
          <Badge
            variant={
              concernLevel === "high"
                ? "fail"
                : concernLevel === "medium"
                ? "warn"
                : "neutral"
            }
            label={concernLevel}
          />
          <svg
            className={`w-4 h-4 text-slate-400 transition-transform ${open ? "rotate-180" : ""}`}
            fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
          </svg>
        </div>
      </button>
      {open && defects.length > 0 && (
        <div className="px-3 pb-3 space-y-1">
          {defects.map((d, j) => (
            <div key={j} className="flex items-start justify-between gap-2 text-xs px-2 py-1 bg-slate-50 rounded">
              <span className="text-slate-500 leading-snug">{d.text}</span>
              <span className="text-slate-300 whitespace-nowrap flex-shrink-0">{d.date}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/* Icons for card headers */
export const icons = {
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
