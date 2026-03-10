"use client";

import { useState } from "react";
import { EVCheckResponse, MOTTestRecord, MOTDefect } from "@/lib/api";
import Badge from "@/components/ui/Badge";
import Card from "@/components/ui/Card";


interface Props {
  result: EVCheckResponse;
}

function DetailRow({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex justify-between py-1.5 border-b border-slate-100 last:border-0">
      <span className="text-sm text-slate-500">{label}</span>
      <span className="text-sm font-medium text-slate-900">{value ?? "N/A"}</span>
    </div>
  );
}

function MileageChart({ readings }: { readings: { date: string; miles: number }[] }) {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const [tooltipPos, setTooltipPos] = useState({ x: 0, y: 0 });
  if (readings.length < 2) return null;
  const width = 300, height = 160;
  const pad = { top: 8, right: 8, bottom: 8, left: 8 };
  const innerW = width - pad.left - pad.right;
  const innerH = height - pad.top - pad.bottom;
  const minM = Math.min(...readings.map((r) => r.miles));
  const maxM = Math.max(...readings.map((r) => r.miles));
  const rng = maxM - minM || 1;
  const coords = readings.map((r, i) => ({ x: pad.left + (i / (readings.length - 1)) * innerW, y: pad.top + innerH - ((r.miles - minM) / rng) * innerH }));
  const pts = coords.map((p) => `${p.x},${p.y}`);
  const area = [`${pad.left},${height - pad.bottom}`, ...pts, `${pad.left + innerW},${height - pad.bottom}`];
  const onMove = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const rx = (e.clientX - rect.left) / rect.width;
    let ci = 0, cd = Infinity;
    coords.forEach((p, i) => { const d = Math.abs(rx - p.x / width); if (d < cd) { cd = d; ci = i; } });
    setHoveredIndex(ci);
    setTooltipPos({ x: (coords[ci].x / width) * rect.width, y: (coords[ci].y / height) * rect.height });
  };
  const hovered = hoveredIndex !== null ? readings[hoveredIndex] : null;
  return (
    <div className="relative cursor-crosshair" onMouseMove={onMove} onMouseLeave={() => setHoveredIndex(null)}>
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-40" preserveAspectRatio="none">
        <polygon points={area.join(" ")} fill="url(#evMG)" />
        <polyline points={pts.join(" ")} fill="none" stroke="#059669" strokeWidth="2" strokeLinejoin="round" strokeLinecap="round" />
        <defs><linearGradient id="evMG" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#059669" stopOpacity="0.15" /><stop offset="100%" stopColor="#059669" stopOpacity="0" /></linearGradient></defs>
      </svg>
      {hoveredIndex !== null && (<><div className="absolute top-0 bottom-0 w-px bg-emerald-300 pointer-events-none" style={{ left: tooltipPos.x }} /><div className="absolute w-3 h-3 bg-emerald-600 rounded-full border-2 border-white shadow-md pointer-events-none" style={{ left: tooltipPos.x - 6, top: tooltipPos.y - 6 }} /></>)}
      {hovered && hoveredIndex !== null && (
        <div className="absolute bg-slate-900 text-white text-xs px-2.5 py-1.5 rounded-lg shadow-lg pointer-events-none whitespace-nowrap z-10" style={{ left: Math.max(60, Math.min(tooltipPos.x, 240)), top: Math.max(0, tooltipPos.y - 36), transform: "translateX(-50%)" }}>
          <span className="text-emerald-300">{new Date(hovered.date).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" })}</span>
          <span className="mx-1.5 text-slate-500">&middot;</span>
          <span className="font-semibold">{hovered.miles.toLocaleString()} mi</span>
        </div>
      )}
    </div>
  );
}

function MOTPassFailBars({ passes, failures }: { passes: number; failures: number }) {
  const total = passes + failures;
  if (total === 0) return null;
  const pct = Math.round((passes / total) * 100);
  return (
    <div className="mt-2">
      <div className="flex items-center gap-2 mb-1">
        <div className="flex-1 h-3 bg-slate-100 rounded-full overflow-hidden"><div className="h-full bg-emerald-500 rounded-full" style={{ width: `${pct}%` }} /></div>
        <span className="text-xs font-medium text-emerald-600 w-10 text-right">{pct}%</span>
      </div>
      <div className="flex justify-between text-xs text-slate-400"><span>{passes} passed</span><span>{failures} failed</span></div>
    </div>
  );
}

function StarRating({ stars, max = 5 }: { stars: number; max?: number }) {
  return (
    <div className="flex items-center gap-0.5">
      {Array.from({ length: max }, (_, i) => (
        <svg key={i} className={`w-5 h-5 ${i < stars ? "text-amber-400" : "text-slate-200"}`} fill="currentColor" viewBox="0 0 20 20">
          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
        </svg>
      ))}
    </div>
  );
}

function MOTTestItem({ test }: { test: MOTTestRecord }) {
  const [open, setOpen] = useState(false);
  const hasDefects = test.advisories.length > 0 || test.failures.length > 0 || test.dangerous.length > 0;
  return (
    <div className="border border-slate-100 rounded-lg overflow-hidden">
      <button onClick={() => setOpen(!open)} className="w-full flex items-center justify-between p-3 text-left hover:bg-slate-50 transition-colors">
        <div className="flex items-center gap-3">
          <Badge variant={test.result === "PASSED" ? "pass" : "fail"} label={test.result} />
          <span className="text-sm text-slate-700">{test.date}</span>
          {test.odometer !== null && <span className="text-xs text-slate-400 font-mono">{test.odometer.toLocaleString()} mi</span>}
        </div>
        <div className="flex items-center gap-2">
          {hasDefects && <span className="text-xs text-slate-400">{test.total_defects} item{test.total_defects !== 1 ? "s" : ""}</span>}
          <svg className={`w-4 h-4 text-slate-400 transition-transform ${open ? "rotate-180" : ""}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" /></svg>
        </div>
      </button>
      {open && hasDefects && (
        <div className="px-3 pb-3 space-y-1">
          {test.dangerous.map((d: MOTDefect, i: number) => (<div key={`d-${i}`} className="text-sm bg-red-50 text-red-800 px-2 py-1 rounded flex items-start gap-1.5"><span className="text-xs font-bold text-red-600 mt-0.5 flex-shrink-0">DANGEROUS</span><span>{d.text}</span></div>))}
          {test.failures.map((f: MOTDefect, i: number) => (<div key={`f-${i}`} className="text-sm bg-amber-50 text-amber-800 px-2 py-1 rounded flex items-start gap-1.5"><span className="text-xs font-bold text-amber-600 mt-0.5 flex-shrink-0">{f.type}</span><span>{f.text}</span></div>))}
          {test.advisories.map((a: MOTDefect, i: number) => (<div key={`a-${i}`} className="text-sm bg-blue-50 text-blue-800 px-2 py-1 rounded flex items-start gap-1.5"><span className="text-xs font-bold text-blue-600 mt-0.5 flex-shrink-0">ADVISORY</span><span>{a.text}</span></div>))}
        </div>
      )}
    </div>
  );
}

const icons = {
  car: (<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M8.25 18.75a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m3 0h6m-9 0H3.375a1.125 1.125 0 01-1.125-1.125V14.25m17.25 4.5a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m3 0H21M3.375 14.25h17.25M3.375 14.25V6.375c0-.621.504-1.125 1.125-1.125h3.026a2.999 2.999 0 012.572 1.456l.866 1.44a1 1 0 00.858.504h4.303a1.125 1.125 0 011.125 1.125V14.25" /></svg>),
  shield: (<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" /></svg>),
  document: (<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" /></svg>),
  clock: (<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>),
  wrench: (<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M11.42 15.17l-5.523 5.523a2.625 2.625 0 01-3.712-3.712l5.523-5.523m3.712 3.712a5.338 5.338 0 01-.825-7.067m.825 7.067a5.338 5.338 0 007.067.825m-7.892-7.892a5.338 5.338 0 017.067-.826" /></svg>),
  currency: (<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M14.121 7.629A3 3 0 009.017 9.43c-.023.212-.002.425.028.636l.506 3.541a4.5 4.5 0 01-.43 2.65L9 16.5l1.539-.513a2.25 2.25 0 011.422 0l.655.218a2.25 2.25 0 001.718-.122L15 15.75M8.25 12H12m9 0a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>),
  star: (<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.204-3.602a.563.563 0 01.321-.988l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z" /></svg>),
  chart: (<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" /></svg>),
  bolt: (<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" /></svg>),
};

export default function EVCheckResult({ result }: Props) {
  const { vehicle, mot_summary, mot_tests, clocking_analysis, mileage_timeline, failure_patterns, tax_calculation, safety_rating, vehicle_stats } = result;

  return (
    <div className="space-y-4">
      {/* Title bar with score gauge */}
      <div className="flex items-center justify-between bg-white border border-slate-200 rounded-xl p-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 bg-emerald-100 text-emerald-700 text-xs font-semibold rounded-full">
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" /></svg>
              {result.ev_type === "BEV" ? "Battery Electric" : "Plug-in Hybrid"}
            </span>
          </div>
          <h2 className="text-xl font-bold text-slate-900">
            {vehicle?.make || mot_summary?.make || "Vehicle"} {mot_summary?.model || ""} {vehicle?.year_of_manufacture ? `(${vehicle.year_of_manufacture})` : ""}
          </h2>
          <p className="text-sm text-slate-500 mt-1">
            Registration: <span className="inline-block bg-yellow-50 border border-yellow-300 font-mono font-bold px-2 py-0.5 rounded text-slate-900">{result.registration}</span>
            {result.data_sources.length > 0 && <span className="ml-2 text-slate-400">Sources: {result.data_sources.join(", ")}</span>}
          </p>
        </div>
      </div>

      {/* Outstanding Recall Warning */}
      {mot_summary?.has_outstanding_recall === "Yes" && (
        <div className="bg-red-50 border-2 border-red-300 rounded-xl p-4 flex items-start gap-3">
          <div className="w-10 h-10 rounded-full bg-red-100 flex items-center justify-center flex-shrink-0">
            <svg className="w-6 h-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" /></svg>
          </div>
          <div>
            <p className="font-bold text-red-800">Outstanding Safety Recall</p>
            <p className="text-sm text-red-700 mt-0.5">This vehicle has an outstanding manufacturer recall. Contact the manufacturer or an authorised dealer to arrange a free repair.</p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {/* Vehicle Identity */}
        {vehicle && (
          <Card title="Vehicle Identity" icon={icons.car} status="neutral">
            <DetailRow label="Make" value={vehicle.make} />
            <DetailRow label="Colour" value={vehicle.colour} />
            <DetailRow label="Fuel Type" value={vehicle.fuel_type} />
            <DetailRow label="Year" value={vehicle.year_of_manufacture} />
            <DetailRow label="Engine" value={vehicle.engine_capacity ? `${vehicle.engine_capacity}cc` : null} />
            <DetailRow label="CO2" value={vehicle.co2_emissions ? `${vehicle.co2_emissions} g/km` : null} />
            <DetailRow label="Euro Status" value={vehicle.euro_status} />
            <DetailRow label="Type Approval" value={vehicle.type_approval} />
          </Card>
        )}

        {/* Tax & MOT Status */}
        {vehicle && (
          <Card title="Tax & MOT Status" icon={icons.shield} status={vehicle.tax_status === "Taxed" && vehicle.mot_status === "Valid" ? "pass" : vehicle.tax_status !== "Taxed" || (vehicle.mot_status !== "Valid" && vehicle.mot_status !== "No details held by DVLA") ? "fail" : "neutral"}>
            <DetailRow label="Tax Status" value={<Badge variant={vehicle.tax_status === "Taxed" ? "pass" : "fail"} label={vehicle.tax_status || "Unknown"} />} />
            <DetailRow label="Tax Due" value={vehicle.tax_due_date} />
            <DetailRow label="MOT Status" value={<Badge variant={vehicle.mot_status === "Valid" ? "pass" : vehicle.mot_status === "No details held by DVLA" ? "neutral" : "fail"} label={vehicle.mot_status || "Unknown"} />} />
            <DetailRow label="MOT Expiry" value={vehicle.mot_expiry_date} />
            <DetailRow label="V5C (Logbook) Issued" value={vehicle.date_of_last_v5c_issued} />
            {vehicle_stats?.v5c_days_since !== null && vehicle_stats?.v5c_days_since !== undefined && vehicle_stats.v5c_days_since <= 90 && (
              <div className="flex items-start gap-2 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2 mt-1 mb-1">
                <svg className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" /></svg>
                <div><span className="text-xs font-semibold text-amber-800">Recently Issued</span><p className="text-xs text-amber-700">V5C issued {vehicle_stats.v5c_days_since} days ago &mdash; may indicate a recent ownership change.</p></div>
              </div>
            )}
            <DetailRow label="Export Marker" value={vehicle.marked_for_export ? <Badge variant="warn" label="Marked for Export" /> : "No"} />
          </Card>
        )}

        {/* MOT History */}
        {mot_summary && (
          <Card title="MOT History" icon={icons.document} status={mot_summary.total_tests > 0 ? (mot_summary.total_passes / mot_summary.total_tests >= 0.7 ? "pass" : "warn") : "neutral"}>
            <DetailRow label="Total Tests" value={mot_summary.total_tests} />
            <DetailRow label="Passes" value={mot_summary.total_passes} />
            <DetailRow label="Failures" value={mot_summary.total_failures} />
            <MOTPassFailBars passes={mot_summary.total_passes} failures={mot_summary.total_failures} />
            {mot_summary.latest_test && (
              <>
                <div className="mt-3 pt-3 border-t border-slate-100" />
                <DetailRow label="Latest Test" value={<span className="flex items-center gap-1.5">{mot_summary.latest_test.date} <Badge variant={mot_summary.latest_test.result === "PASSED" ? "pass" : "fail"} label={mot_summary.latest_test.result || ""} /></span>} />
                <DetailRow label="Current Mileage" value={mot_summary.current_odometer ? `${Number(mot_summary.current_odometer).toLocaleString()} miles` : "N/A"} />
                <DetailRow label="MOT Expiry" value={mot_summary.latest_test.expiry_date} />
              </>
            )}
          </Card>
        )}

        {/* Mileage Analysis */}
        {clocking_analysis && (
          <Card title="Mileage Analysis" icon={icons.clock} status={clocking_analysis.clocked ? "fail" : clocking_analysis.risk_level === "none" ? "pass" : clocking_analysis.risk_level === "unknown" ? "neutral" : "warn"}>
            <div className="mb-3">
              {clocking_analysis.clocked ? (
                <div className="flex items-center gap-2 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
                  <svg className="w-5 h-5 text-red-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" /></svg>
                  <span className="text-sm font-semibold text-red-800">MILEAGE DISCREPANCY FOUND</span>
                </div>
              ) : clocking_analysis.risk_level === "none" ? (
                <div className="flex items-center gap-2 bg-emerald-50 border border-emerald-200 rounded-lg px-3 py-2">
                  <svg className="w-5 h-5 text-emerald-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                  <span className="text-sm font-semibold text-emerald-800">Mileage Consistent</span>
                </div>
              ) : (
                clocking_analysis.risk_level === "unknown" ? (
                <div className="flex items-center gap-2 bg-slate-50 border border-slate-200 rounded-lg px-3 py-2">
                  <svg className="w-5 h-5 text-slate-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                  <span className="text-sm font-semibold text-slate-600">Not Enough MOT History Yet</span>
                </div>
                ) : (
                <Badge variant="warn" label={`${clocking_analysis.risk_level.toUpperCase()} RISK`} size="md" />
                )
              )}
            </div>
            {clocking_analysis.reason && <p className="text-sm text-slate-500 mb-2">{clocking_analysis.reason}</p>}
            {clocking_analysis.flags.map((flag, i) => (
              <div key={i} className={`text-sm p-2 rounded mb-1 ${flag.severity === "high" ? "bg-red-50 text-red-800" : flag.severity === "medium" ? "bg-amber-50 text-amber-800" : "bg-slate-50 text-slate-700"}`}>{flag.detail}</div>
            ))}
            {mileage_timeline.length >= 2 && (
              <div className="mt-3 pt-3 border-t border-slate-100">
                <p className="text-xs text-slate-400 mb-2">Mileage Timeline ({mileage_timeline.length} readings)</p>
                <MileageChart readings={mileage_timeline} />
                <div className="flex justify-between text-xs text-slate-400 mt-1"><span>{mileage_timeline[0]?.date}</span><span>{mileage_timeline[mileage_timeline.length - 1]?.date}</span></div>
              </div>
            )}
            {mileage_timeline.length === 1 && (() => {
              const regDate = mot_summary?.first_used_date
                || (vehicle?.year_of_manufacture ? `${vehicle.year_of_manufacture}-01-01` : null);
              const syntheticTimeline = regDate
                ? [{ date: regDate, miles: 0 }, ...mileage_timeline]
                : mileage_timeline;
              return (
                <div className="mt-3 pt-3 border-t border-slate-100">
                  <p className="text-xs text-slate-400 mb-2">Mileage Timeline (1 reading + registration)</p>
                  {syntheticTimeline.length >= 2 ? (
                    <>
                      <MileageChart readings={syntheticTimeline} />
                      <div className="flex justify-between text-xs text-slate-400 mt-1">
                        <span>{syntheticTimeline[0].date} (registered)</span>
                        <span>{syntheticTimeline[syntheticTimeline.length - 1].date}</span>
                      </div>
                    </>
                  ) : (
                    <div className="flex justify-between text-xs text-slate-600">
                      <span>{mileage_timeline[0].date}</span>
                      <span className="font-mono">{mileage_timeline[0].miles.toLocaleString()} mi</span>
                    </div>
                  )}
                </div>
              );
            })()}
          </Card>
        )}

        {/* Road Tax (VED) */}
        {tax_calculation && (
          <Card title="Road Tax (VED)" icon={icons.currency} status="neutral">
            <DetailRow label="Tax Band" value={tax_calculation.band ? `Band ${tax_calculation.band}` : null} />
            <DetailRow label="CO2 Range" value={tax_calculation.band_range} />
            <DetailRow label="CO2 Emissions" value={tax_calculation.co2_emissions ? `${tax_calculation.co2_emissions} g/km` : "0 g/km"} />
            <DetailRow label="Fuel Type" value={tax_calculation.fuel_type} />
            <div className="mt-3 pt-3 border-t border-slate-100" />
            <DetailRow label="First Year Rate" value={<span className="font-mono font-bold text-slate-900">{tax_calculation.first_year_rate === 0 ? "FREE" : `£${tax_calculation.first_year_rate}`}</span>} />
            <DetailRow label="Annual Rate (Year 2+)" value={<span className="font-mono font-bold text-slate-900">{tax_calculation.annual_rate === 0 ? "FREE" : `£${tax_calculation.annual_rate}`}</span>} />
            <DetailRow label="6-Month Payment" value={`£${tax_calculation.six_month_rate}`} />
            {tax_calculation.is_electric && <div className="mt-2 text-xs text-emerald-600 bg-emerald-50 rounded px-2 py-1">Electric vehicle — zero emissions</div>}
          </Card>
        )}

        {/* Vehicle Statistics */}
        {vehicle_stats && (
          <Card title="Vehicle Statistics" icon={icons.chart} status="neutral">
            {vehicle_stats.vehicle_age_years !== null && <DetailRow label="Vehicle Age" value={`${vehicle_stats.vehicle_age_years} years`} />}
            {vehicle_stats.estimated_annual_mileage !== null && (
              <DetailRow label="Est. Annual Mileage" value={<span className="flex items-center gap-1.5">{vehicle_stats.estimated_annual_mileage.toLocaleString()} mi/yr{vehicle_stats.mileage_assessment && <Badge variant={vehicle_stats.mileage_assessment === "High mileage" ? "warn" : vehicle_stats.mileage_assessment === "Below average mileage" ? "info" : "neutral"} label={vehicle_stats.mileage_assessment} />}</span>} />
            )}
            {vehicle_stats.total_recorded_mileage !== null && <DetailRow label="Total Recorded" value={`${vehicle_stats.total_recorded_mileage.toLocaleString()} miles`} />}
            {vehicle_stats.mileage_readings_count !== null && <DetailRow label="MOT Readings" value={vehicle_stats.mileage_readings_count} />}
            {(vehicle_stats.mot_status_detail || vehicle_stats.tax_status_detail || vehicle_stats.v5c_insight) && <div className="mt-3 pt-3 border-t border-slate-100" />}
            {vehicle_stats.mot_status_detail && <DetailRow label="MOT" value={<Badge variant={vehicle_stats.mot_days_remaining !== null && vehicle_stats.mot_days_remaining < 0 ? "fail" : vehicle_stats.mot_days_remaining !== null && vehicle_stats.mot_days_remaining <= 30 ? "warn" : "pass"} label={vehicle_stats.mot_status_detail} />} />}
            {vehicle_stats.tax_status_detail && <DetailRow label="Tax" value={<Badge variant={vehicle_stats.tax_days_remaining !== null && vehicle_stats.tax_days_remaining < 0 ? "fail" : vehicle_stats.tax_days_remaining !== null && vehicle_stats.tax_days_remaining <= 30 ? "warn" : "pass"} label={vehicle_stats.tax_status_detail} />} />}
            {vehicle_stats.v5c_insight && <DetailRow label="V5C" value={vehicle_stats.v5c_insight} />}
            {(vehicle_stats.total_advisory_items !== null || vehicle_stats.total_failure_items !== null) && (
              <>
                <div className="mt-3 pt-3 border-t border-slate-100" />
                <p className="text-xs text-slate-400 mb-2">Lifetime MOT Defect Totals</p>
                <div className="grid grid-cols-3 gap-2 text-center">
                  {vehicle_stats.total_advisory_items !== null && <div className="bg-blue-50 rounded-lg py-2"><div className="text-lg font-bold text-blue-700">{vehicle_stats.total_advisory_items}</div><div className="text-xs text-blue-500">Advisories</div></div>}
                  {vehicle_stats.total_failure_items !== null && <div className="bg-amber-50 rounded-lg py-2"><div className="text-lg font-bold text-amber-700">{vehicle_stats.total_failure_items}</div><div className="text-xs text-amber-500">Failures</div></div>}
                  {vehicle_stats.total_dangerous_items !== null && vehicle_stats.total_dangerous_items > 0 && <div className="bg-red-50 rounded-lg py-2"><div className="text-lg font-bold text-red-700">{vehicle_stats.total_dangerous_items}</div><div className="text-xs text-red-500">Dangerous</div></div>}
                </div>
              </>
            )}
          </Card>
        )}

        {/* Recurring Issues */}
        {failure_patterns.length > 0 && (
          <Card title="Recurring Issues" icon={icons.wrench} status={failure_patterns.some((p) => p.concern_level === "high") ? "fail" : failure_patterns.some((p) => p.concern_level === "medium") ? "warn" : "neutral"}>
            <div className="space-y-3">
              {failure_patterns.map((p, i) => {
                const categoryDefects: { text: string; type: string; date: string }[] = [];
                mot_tests.forEach((test) => {
                  [...test.advisories, ...test.failures, ...test.dangerous].forEach((d) => {
                    if (d.text.toLowerCase().includes(p.category.toLowerCase())) {
                      categoryDefects.push({ text: d.text, type: d.type, date: test.date });
                    }
                  });
                });
                return (
                  <div key={i}>
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="text-sm font-medium capitalize text-slate-700">{p.category}</span>
                      <span className="flex items-center gap-2"><span className="text-xs text-slate-400">{p.occurrences}x</span><Badge variant={p.concern_level === "high" ? "fail" : p.concern_level === "medium" ? "warn" : "neutral"} label={p.concern_level} /></span>
                    </div>
                    {categoryDefects.length > 0 && (
                      <div className="space-y-1 ml-1 pl-3 border-l-2 border-slate-100">
                        {categoryDefects.map((d, j) => (
                          <div key={j} className="flex items-start justify-between gap-2">
                            <span className="text-xs text-slate-500 leading-snug">{d.text}</span>
                            <span className="text-xs text-slate-300 whitespace-nowrap flex-shrink-0">{d.date}</span>
                          </div>
                        ))}
                      </div>
                    )}
                    {i < failure_patterns.length - 1 && <div className="border-b border-slate-100 mt-3" />}
                  </div>
                );
              })}
            </div>
          </Card>
        )}

        {/* Safety Rating */}
        {safety_rating && (
          <Card title="Safety Rating" icon={icons.star} status={safety_rating.stars >= 4 ? "pass" : safety_rating.stars >= 3 ? "warn" : "fail"}>
            <div className="mb-3">
              <StarRating stars={safety_rating.stars} />
              <p className="text-xs text-slate-400 mt-1">{safety_rating.source} &middot; {safety_rating.year_range} &middot; Tested {safety_rating.test_year}</p>
            </div>
            <div className="space-y-2">
              {[{ label: "Adult Occupant", value: safety_rating.adult }, { label: "Child Occupant", value: safety_rating.child }, { label: "Pedestrian", value: safety_rating.pedestrian }, { label: "Safety Assist", value: safety_rating.safety_assist }].map(({ label, value }) => (
                <div key={label}>
                  <div className="flex justify-between text-xs mb-0.5"><span className="text-slate-500">{label}</span><span className="font-medium text-slate-700">{value}%</span></div>
                  <div className="h-2 bg-slate-100 rounded-full overflow-hidden"><div className={`h-full rounded-full transition-all duration-500 ${value >= 80 ? "bg-emerald-500" : value >= 60 ? "bg-amber-400" : "bg-red-400"}`} style={{ width: `${value}%` }} /></div>
                </div>
              ))}
            </div>
          </Card>
        )}
      </div>

      {/* Full MOT History (accordion) */}
      {mot_tests && mot_tests.length > 0 && (
        <Card title={`Full MOT History (${mot_tests.length} tests)`} icon={icons.document} status="neutral">
          <div className="space-y-2">
            {mot_tests.map((test) => (<MOTTestItem key={test.test_number} test={test} />))}
          </div>
        </Card>
      )}

      {/* --- Consolidated EV Health Check upsell (£8.99) --- */}
      <div className="bg-gradient-to-br from-emerald-50 to-teal-50 border-2 border-emerald-200 rounded-xl overflow-hidden">
        <div className="bg-gradient-to-r from-emerald-700 to-emerald-800 px-5 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-white font-bold text-lg flex items-center gap-2">
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" /></svg>
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

      {/* --- Consolidated EV Complete upsell (£13.99) --- */}
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

      <div className="text-center pt-2">
        <span className="inline-block bg-slate-100 text-slate-500 text-xs px-3 py-1 rounded-full">Free EV Check &middot; Powered by DVLA &amp; DVSA data</span>
      </div>

      {/* Legal disclaimer */}
      <p className="text-xs text-slate-400 text-center mt-4 max-w-2xl mx-auto">
        This report is for informational purposes only and should not be the sole basis for a purchasing decision. Data sourced from DVLA, DVSA, and third-party providers &mdash; accuracy not guaranteed. We recommend an independent mechanical inspection before purchase. See our{" "}
        <a href="/terms" className="underline hover:text-slate-600">Terms of Service</a>.
      </p>
    </div>
  );
}
