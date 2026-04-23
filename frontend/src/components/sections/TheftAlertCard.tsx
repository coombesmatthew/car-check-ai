import { ReactNode } from "react";

/* Single-status card used inside the Theft & Alerts SwipeCarousel.
   Coloured left edge + pill top-right, one-line definition, optional
   detail rows rendered below when the check is flagged. */
export interface TheftAlertCardProps {
  title: string;
  description: string;
  flagged: boolean;
  flaggedLabel: string;
  clearLabel: string;
  source: string;
  // An amber (warn) variant for flags that aren't full fails — e.g.
  // "marked for export" isn't technically a stolen-level red flag.
  severity?: "fail" | "warn";
  details?: ReactNode;
}

export default function TheftAlertCard({
  title,
  description,
  flagged,
  flaggedLabel,
  clearLabel,
  source,
  severity = "fail",
  details,
}: TheftAlertCardProps) {
  const edgeColour = flagged
    ? severity === "warn"
      ? "bg-amber-500"
      : "bg-red-500"
    : "bg-emerald-500";

  const pillClasses = flagged
    ? severity === "warn"
      ? "bg-amber-100 text-amber-800 border-amber-200"
      : "bg-red-100 text-red-800 border-red-200"
    : "bg-emerald-100 text-emerald-800 border-emerald-200";

  return (
    <div className="relative h-full bg-white border border-slate-200 rounded-lg overflow-hidden flex flex-col">
      <div className={`absolute inset-y-0 left-0 w-1 ${edgeColour}`} aria-hidden="true" />
      <div className="flex items-start justify-between gap-2 p-3 pl-4 border-b border-slate-100">
        <h4 className="text-sm font-semibold text-slate-900">{title}</h4>
        <span
          className={`inline-flex items-center font-medium rounded border px-2 py-0.5 text-xs ${pillClasses} shrink-0`}
        >
          {flagged ? flaggedLabel : clearLabel}
        </span>
      </div>
      <div className="p-3 pl-4 flex-1 flex flex-col">
        <p className="text-xs text-slate-500 mb-2">{description}</p>
        {details && <div className="mt-auto">{details}</div>}
        <div className="mt-3 text-xs text-slate-400 bg-slate-50 rounded px-2 py-1">
          Source: {source}
        </div>
      </div>
    </div>
  );
}
