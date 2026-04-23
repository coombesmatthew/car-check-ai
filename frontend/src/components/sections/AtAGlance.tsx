import Card from "@/components/ui/Card";
import { icons } from "./shared";
import { buildChecksSummary, ChecksSummaryItem, ChecksSummaryStatus } from "@/lib/checksSummary";
import type {
  FinanceCheck, StolenCheck, WriteOffCheck, SalvageCheck,
  ClockingAnalysis, ULEZCompliance, VehicleIdentity, VehicleStats,
} from "@/lib/api";

const EDGE_BY_STATUS: Record<ChecksSummaryStatus, string> = {
  pass: "bg-emerald-500",
  warn: "bg-amber-500",
  fail: "bg-red-500",
};

const BG_BY_STATUS: Record<ChecksSummaryStatus, string> = {
  pass: "bg-emerald-50",
  warn: "bg-amber-50",
  fail: "bg-red-50",
};

const TEXT_BY_STATUS: Record<ChecksSummaryStatus, string> = {
  pass: "text-emerald-800",
  warn: "text-amber-800",
  fail: "text-red-800",
};

function StatusIcon({ status }: { status: ChecksSummaryStatus }) {
  if (status === "pass") {
    return (
      <svg className="w-4 h-4 text-emerald-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
      </svg>
    );
  }
  if (status === "warn") {
    return (
      <svg className="w-4 h-4 text-amber-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
      </svg>
    );
  }
  return (
    <svg className="w-4 h-4 text-red-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
    </svg>
  );
}

function Row({ item }: { item: ChecksSummaryItem }) {
  return (
    <div
      className={`flex items-center gap-3 rounded-md overflow-hidden border-l-4 ${EDGE_BY_STATUS[item.status]} ${BG_BY_STATUS[item.status]} px-3 py-2`}
    >
      <StatusIcon status={item.status} />
      <div className="flex-1 min-w-0">
        <span className={`text-sm font-semibold ${TEXT_BY_STATUS[item.status]}`}>{item.label}</span>
        <span className="text-sm text-slate-500"> — {item.detail}</span>
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

  return (
    <Card title="At a Glance" icon={icons.shield} status="neutral">
      <div className="space-y-2">
        {items.map((item, i) => (
          <Row key={i} item={item} />
        ))}
      </div>
    </Card>
  );
}
