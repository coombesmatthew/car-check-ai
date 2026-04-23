import Card from "@/components/ui/Card";
import { icons } from "./shared";
import { buildChecksSummary, ChecksSummaryItem, ChecksSummaryStatus } from "@/lib/checksSummary";
import type {
  FinanceCheck, StolenCheck, WriteOffCheck, SalvageCheck,
  ClockingAnalysis, ULEZCompliance, VehicleIdentity, VehicleStats,
} from "@/lib/api";

const ROW_STYLES: Record<ChecksSummaryStatus, { edge: string; bg: string; iconBg: string; iconColour: string }> = {
  pass: {
    edge: "border-l-4 border-emerald-500",
    bg: "bg-emerald-50/60",
    iconBg: "bg-emerald-100",
    iconColour: "text-emerald-600",
  },
  warn: {
    edge: "border-l-4 border-amber-500",
    bg: "bg-amber-50/80",
    iconBg: "bg-amber-100",
    iconColour: "text-amber-600",
  },
  fail: {
    edge: "border-l-4 border-red-500",
    bg: "bg-red-50/80",
    iconBg: "bg-red-100",
    iconColour: "text-red-600",
  },
};

function StatusIcon({ status }: { status: ChecksSummaryStatus }) {
  const c = ROW_STYLES[status].iconColour;
  if (status === "pass") {
    return (
      <svg className={`w-3.5 h-3.5 ${c}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
      </svg>
    );
  }
  if (status === "warn") {
    return (
      <svg className={`w-3.5 h-3.5 ${c}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
      </svg>
    );
  }
  return (
    <svg className={`w-3.5 h-3.5 ${c}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
    </svg>
  );
}

function Row({ item }: { item: ChecksSummaryItem }) {
  const style = ROW_STYLES[item.status];
  return (
    <div className={`flex items-center gap-2.5 rounded-md ${style.bg} ${style.edge} px-3 py-2`}>
      <span className={`inline-flex items-center justify-center w-6 h-6 rounded-full ${style.iconBg} flex-shrink-0`}>
        <StatusIcon status={item.status} />
      </span>
      <div className="flex-1 min-w-0 leading-tight">
        <span className="text-sm font-semibold text-slate-900">{item.label}</span>
        <span className="text-xs text-slate-500"> &middot; {item.detail}</span>
      </div>
    </div>
  );
}

interface AtAGlanceProps {
  finance_check?: FinanceCheck | null;
  stolen_check?: StolenCheck | null;
  write_off_check?: WriteOffCheck | null;
  salvage_check?: SalvageCheck | null;
  clocking_analysis?: ClockingAnalysis | null;
  vehicle?: VehicleIdentity | null;
  vehicle_stats?: VehicleStats | null;
  ulez_compliance?: ULEZCompliance | null;
}

export default function AtAGlance(props: AtAGlanceProps) {
  const items = buildChecksSummary(props);
  if (items.length === 0) return null;

  // Flags (fail/warn) up top — they're the customer's priority — then passes.
  const flags = items.filter((i) => i.status !== "pass");
  const passes = items.filter((i) => i.status === "pass");

  return (
    <Card title="At a Glance" icon={icons.shield} status="neutral">
      {flags.length > 0 && (
        <div className="space-y-1.5 mb-2">
          {flags.map((item, i) => (
            <Row key={`flag-${i}`} item={item} />
          ))}
        </div>
      )}
      {passes.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-1.5">
          {passes.map((item, i) => (
            <Row key={`pass-${i}`} item={item} />
          ))}
        </div>
      )}
    </Card>
  );
}
