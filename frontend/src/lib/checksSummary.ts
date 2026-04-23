/* Port of backend/app/services/notification/email_sender.py::_build_checks_summary
   — single source of truth for the At a Glance checklist that both the
   email and the /report page render. Keep the two in sync if one changes. */

import type {
  FinanceCheck,
  StolenCheck,
  WriteOffCheck,
  SalvageCheck,
  ClockingAnalysis,
  ULEZCompliance,
  VehicleIdentity,
  VehicleStats,
  MOTSummary,
  BatteryHealth,
} from "./api";

export type ChecksSummaryStatus = "pass" | "fail" | "warn";

export interface ChecksSummaryItem {
  status: ChecksSummaryStatus;
  label: string;
  detail: string;
}

interface SourceData {
  finance_check?: FinanceCheck | null;
  stolen_check?: StolenCheck | null;
  write_off_check?: WriteOffCheck | null;
  salvage_check?: SalvageCheck | null;
  clocking_analysis?: ClockingAnalysis | null;
  vehicle?: VehicleIdentity | null;
  vehicle_stats?: VehicleStats | null;
  ulez_compliance?: ULEZCompliance | null;
  mot_summary?: MOTSummary | null;
  battery_health?: BatteryHealth | null;
}

/* Items are ordered by severity — most critical (stolen, finance, write-off) first.
   A check only contributes a row when its source data is present; absent fields
   are silent (not rendered as "unknown"). */
export function buildChecksSummary(data: SourceData): ChecksSummaryItem[] {
  const items: ChecksSummaryItem[] = [];

  // --- Provenance checks (premium tier) ---

  if (data.stolen_check) {
    if (data.stolen_check.stolen) {
      items.push({
        status: "fail",
        label: "Reported Stolen",
        detail: "Do not purchase — this vehicle has a stolen marker",
      });
    } else {
      items.push({
        status: "pass",
        label: "Not Stolen",
        detail: "Clear — no stolen marker",
      });
    }
  }

  if (data.finance_check) {
    if (data.finance_check.finance_outstanding) {
      const count = data.finance_check.record_count || 1;
      items.push({
        status: "fail",
        label: "Finance Outstanding",
        detail: `${count} active agreement${count !== 1 ? "s" : ""} — lender may repossess`,
      });
    } else {
      items.push({
        status: "pass",
        label: "No Finance Outstanding",
        detail: "Clear — safe to purchase",
      });
    }
  }

  if (data.write_off_check) {
    if (data.write_off_check.written_off) {
      const cats = (data.write_off_check.records || [])
        .map((r) => r.category)
        .filter((c): c is string => !!c);
      const catStr = cats.length
        ? cats.map((c) => `Cat ${c}`).join(" / ")
        : "category unknown";
      items.push({
        status: "fail",
        label: "Insurance Write-Off Found",
        detail: `${catStr} — affects insurance cost and resale value`,
      });
    } else {
      items.push({
        status: "pass",
        label: "No Write-Off History",
        detail: "Clear — not written off",
      });
    }
  }

  if (data.salvage_check) {
    if (data.salvage_check.salvage_found) {
      items.push({
        status: "warn",
        label: "Salvage Records Found",
        detail: "Vehicle appears in salvage auction records",
      });
    } else {
      items.push({
        status: "pass",
        label: "No Salvage Records",
        detail: "Clear — no auction history",
      });
    }
  }

  // --- Core checks (all tiers) ---

  if (data.clocking_analysis) {
    if (data.clocking_analysis.clocked) {
      items.push({
        status: "fail",
        label: "Mileage Discrepancy Detected",
        detail: "Odometer may have been tampered with",
      });
    } else {
      items.push({
        status: "pass",
        label: "Mileage Verified",
        detail: "Consistent history — no clocking detected",
      });
    }
  }

  const motStatus = data.vehicle?.mot_status || "";
  const motDays = data.vehicle_stats?.mot_days_remaining;
  if (motStatus === "Valid") {
    if (motDays !== null && motDays !== undefined && motDays < 60) {
      items.push({
        status: "warn",
        label: "MOT Valid",
        detail: `Expires in ${motDays} days — use as negotiation leverage`,
      });
    } else {
      const detail =
        motDays !== null && motDays !== undefined
          ? `${motDays} days remaining`
          : "Currently valid";
      items.push({ status: "pass", label: "MOT Valid", detail });
    }
  } else if (motStatus) {
    items.push({
      status: "fail",
      label: "MOT Not Valid",
      detail: `Status: ${motStatus}`,
    });
  }

  // CAZ/ULEZ compliance intentionally omitted — it's a running-cost signal
  // (shown in the Emissions section) not a buy/don't-buy risk factor.

  // Outstanding safety recall — surface for any tier where we have MOT data.
  // "Yes" is a fail because it's an open manufacturer recall, not a trivia row.
  const recall = data.mot_summary?.has_outstanding_recall;
  if (recall === "Yes") {
    items.push({
      status: "fail",
      label: "Outstanding Safety Recall",
      detail: "Contact manufacturer for a free repair before purchase",
    });
  } else if (recall === "No") {
    items.push({
      status: "pass",
      label: "No Outstanding Recalls",
      detail: "Manufacturer has no open safety recalls on this vehicle",
    });
  }

  // Battery health — EV tiers only. Shown when present regardless of tier.
  const bh = data.battery_health;
  if (bh?.score != null) {
    if (bh.score >= 80) {
      items.push({
        status: "pass",
        label: `Battery Health ${bh.score}/100`,
        detail: bh.grade ? `Grade ${bh.grade} — healthy range retention` : "Healthy range retention",
      });
    } else if (bh.score >= 60) {
      items.push({
        status: "warn",
        label: `Battery Health ${bh.score}/100`,
        detail: bh.grade ? `Grade ${bh.grade} — moderate degradation` : "Moderate degradation for age",
      });
    } else {
      items.push({
        status: "fail",
        label: `Battery Health ${bh.score}/100`,
        detail: bh.grade ? `Grade ${bh.grade} — significant degradation` : "Significant degradation, expect reduced range",
      });
    }
  }

  return items;
}
