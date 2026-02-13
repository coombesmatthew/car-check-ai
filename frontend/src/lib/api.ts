const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

export interface VehicleIdentity {
  registration: string | null;
  make: string | null;
  colour: string | null;
  fuel_type: string | null;
  year_of_manufacture: number | null;
  engine_capacity: number | null;
  co2_emissions: number | null;
  euro_status: string | null;
  tax_status: string | null;
  tax_due_date: string | null;
  mot_status: string | null;
  mot_expiry_date: string | null;
  date_of_last_v5c_issued: string | null;
  marked_for_export: boolean | null;
  type_approval: string | null;
  wheelplan: string | null;
}

export interface LatestTest {
  date: string | null;
  result: string | null;
  odometer: string | null;
  expiry_date: string | null;
}

export interface MOTSummary {
  total_tests: number;
  total_passes: number;
  total_failures: number;
  registration: string | null;
  make: string | null;
  model: string | null;
  first_used_date: string | null;
  latest_test: LatestTest | null;
  current_odometer: string | null;
}

export interface ClockingFlag {
  type: string;
  severity: string;
  detail: string;
  from_date?: string;
  to_date?: string;
  drop_amount?: number;
}

export interface ClockingAnalysis {
  clocked: boolean;
  risk_level: string;
  reason?: string;
  flags: ClockingFlag[];
}

export interface MileageReading {
  date: string;
  miles: number;
  unit: string;
}

export interface FailurePattern {
  category: string;
  occurrences: number;
  concern_level: string;
}

export interface ULEZCompliance {
  compliant: boolean | null;
  status: string;
  reason: string;
  euro_standard?: number;
  euro_inferred?: boolean;
  fuel_type?: string;
  daily_charge?: string;
  zones: Record<string, boolean>;
}

export interface FreeCheckResponse {
  registration: string;
  tier: string;
  vehicle: VehicleIdentity | null;
  mot_summary: MOTSummary | null;
  clocking_analysis: ClockingAnalysis | null;
  condition_score: number | null;
  mileage_timeline: MileageReading[];
  failure_patterns: FailurePattern[];
  ulez_compliance: ULEZCompliance | null;
  checked_at: string;
  data_sources: string[];
}

export async function runFreeCheck(
  registration: string
): Promise<FreeCheckResponse> {
  const res = await fetch(`${API_URL}/api/v1/checks/free`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ registration }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Check failed" }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }

  return res.json();
}
