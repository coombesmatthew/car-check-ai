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
  has_outstanding_recall: string | null;
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

export interface ZoneDetail {
  zone_id: string;
  name: string;
  region: string;
  compliant: boolean;
  charge: string;
  cars_affected: boolean;
  zone_type: string;
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
  zone_details?: ZoneDetail[];
  total_zones?: number;
  compliant_zones?: number;
  non_compliant_zones?: number;
  charges_apply_zones?: number;
}

export interface MOTDefect {
  type: string;
  text: string;
}

export interface MOTTestRecord {
  test_number: number;
  test_id: string;
  date: string;
  result: string;
  odometer: number | null;
  odometer_unit: string;
  expiry_date: string | null;
  advisories: MOTDefect[];
  failures: MOTDefect[];
  dangerous: MOTDefect[];
  total_defects: number;
}

export interface TaxCalculation {
  band: string;
  band_range: string;
  co2_emissions: number;
  fuel_type: string;
  first_year_rate: number;
  annual_rate: number;
  six_month_rate: number;
  monthly_total: number;
  is_electric: boolean;
  is_diesel: boolean;
}

export interface SafetyRating {
  source: string;
  make: string;
  model: string;
  year_range: string;
  stars: number;
  adult: number;
  child: number;
  pedestrian: number;
  safety_assist: number;
  overall: number;
  test_year: number;
}

export interface VehicleStats {
  vehicle_age_years: number | null;
  year_of_manufacture: number | null;
  first_registered: string | null;
  mot_expiry_date: string | null;
  mot_days_remaining: number | null;
  mot_status_detail: string | null;
  tax_due_date: string | null;
  tax_days_remaining: number | null;
  tax_status_detail: string | null;
  v5c_issued_date: string | null;
  v5c_days_since: number | null;
  v5c_insight: string | null;
  estimated_annual_mileage: number | null;
  total_recorded_mileage: number | null;
  mileage_readings_count: number | null;
  mileage_assessment: string | null;
  total_advisory_items: number | null;
  total_failure_items: number | null;
  total_dangerous_items: number | null;
  total_major_items: number | null;
  total_minor_items: number | null;
}

export interface FinanceRecord {
  agreement_type: string;
  finance_company: string;
  agreement_date: string | null;
  agreement_term: string | null;
  contact_number: string | null;
}

export interface FinanceCheck {
  finance_outstanding: boolean;
  record_count: number;
  records: FinanceRecord[];
  data_source: string;
}

export interface StolenCheck {
  stolen: boolean;
  reported_date: string | null;
  police_force: string | null;
  reference: string | null;
  data_source: string;
}

export interface WriteOffRecord {
  category: string;
  date: string;
  loss_type: string | null;
}

export interface WriteOffCheck {
  written_off: boolean;
  record_count: number;
  records: WriteOffRecord[];
  data_source: string;
}

export interface PlateChangeRecord {
  previous_plate: string;
  change_date: string;
  change_type: string;
}

export interface PlateChangeHistory {
  changes_found: boolean;
  record_count: number;
  records: PlateChangeRecord[];
  data_source: string;
}

export interface Valuation {
  private_sale: number | null;
  dealer_forecourt: number | null;
  trade_in: number | null;
  part_exchange: number | null;
  valuation_date: string;
  mileage_used: number | null;
  condition: string;
  data_source: string;
}

export interface SalvageRecord {
  lot_number?: string;
  auction_date?: string;
  damage_description?: string;
  category?: string;
  images?: string[];
}

export interface SalvageCheck {
  salvage_found: boolean;
  records: SalvageRecord[];
  data_source: string;
}

export interface ImportStatusCheck {
  is_imported: boolean;
  is_exported: boolean;
  marked_for_export: boolean;
  data_source: string;
}

export interface KeeperRecord {
  keeper_number: number;
  start_date: string | null;
  end_date: string | null;
  is_current: boolean;
  start_display: string | null;
  end_display: string | null;
  tenure_display: string | null;
  label: string | null; // "First Owner" / "Seventh Owner" / "Keeper 8"
}

export interface KeeperHistory {
  keeper_count: number | null;
  last_change_date: string | null;
  keepers: KeeperRecord[];
  data_source: string;
}

export interface HighRiskRecord {
  risk_type: string;
  date: string | null;
  detail: string | null;
  company: string | null;
  contact: string | null;
}

export interface HighRiskCheck {
  flagged: boolean;
  records: HighRiskRecord[];
  data_source: string;
}

export interface PreviousSearchRecord {
  date: string | null;
  business_type: string | null;
}

export interface PreviousSearches {
  search_count: number;
  records: PreviousSearchRecord[];
  data_source: string;
}

export interface FreeCheckResponse {
  registration: string;
  tier: string;
  vehicle: VehicleIdentity | null;
  mot_summary: MOTSummary | null;
  mot_tests: MOTTestRecord[];
  clocking_analysis: ClockingAnalysis | null;
  condition_score: number | null;
  mileage_timeline: MileageReading[];
  failure_patterns: FailurePattern[];
  ulez_compliance: ULEZCompliance | null;
  tax_calculation: TaxCalculation | null;
  safety_rating: SafetyRating | null;
  vehicle_stats: VehicleStats | null;
  finance_check: FinanceCheck | null;
  stolen_check: StolenCheck | null;
  write_off_check: WriteOffCheck | null;
  plate_changes: PlateChangeHistory | null;
  valuation: Valuation | null;
  keeper_history: KeeperHistory | null;
  high_risk: HighRiskCheck | null;
  previous_searches: PreviousSearches | null;
  salvage_check: SalvageCheck | null;
  import_status: ImportStatusCheck | null;
  checked_at: string;
  data_sources: string[];
}

export async function captureEmail(email: string, registration: string): Promise<void> {
  try {
    await fetch(`${API_URL}/api/v1/checks/leads`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, registration }),
    });
  } catch {
    // fire-and-forget, never throw
  }
}

export async function getCheckCount(): Promise<number> {
  try {
    const res = await fetch(`${API_URL}/api/v1/checks/count`);
    if (!res.ok) return 0;
    const data = await res.json();
    return data.total_checks || 0;
  } catch {
    return 0;
  }
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

export interface CheckoutResponse {
  session_id: string;
  checkout_url: string;
}

export async function createCheckout(
  registration: string,
  email: string | null,
  tier: string = "basic",
): Promise<CheckoutResponse> {
  const body: Record<string, unknown> = { registration, tier };
  if (email) body.email = email;
  const res = await fetch(`${API_URL}/api/v1/checks/basic/checkout`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Checkout failed" }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }

  return res.json();
}

export interface FulfilmentResponse {
  registration: string;
  report_ref: string;
  email_sent: boolean;
  pdf_size_bytes: number;
  verdict: string | null;
  payment_status: string;
}

export async function fulfilReport(
  sessionId: string
): Promise<FulfilmentResponse> {
  const res = await fetch(
    `${API_URL}/api/v1/checks/basic/fulfil?session_id=${encodeURIComponent(sessionId)}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    }
  );

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Report generation failed" }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }

  return res.json();
}

/** Fire-and-forget: kick off fulfilment in the background and return fast. */
export async function triggerReportFulfilment(sessionId: string): Promise<void> {
  await fetch(
    `${API_URL}/api/v1/checks/basic/fulfil/trigger?session_id=${encodeURIComponent(sessionId)}`,
    { method: "POST" }
  );
}

/** Fetch the full report data (paid) by Stripe session_id. Used by /report page. */
export interface ReportDataResponse {
  registration: string;
  report_ref: string;
  tier: "car" | "ev";
  is_ev: boolean;
  check_data: FreeCheckResponse & EVCheckResponse; // superset — both live in check_data
}

export async function getReportData(sessionId: string): Promise<ReportDataResponse> {
  const res = await fetch(
    `${API_URL}/api/v1/checks/report/data?session_id=${encodeURIComponent(sessionId)}`,
    { method: "GET" }
  );
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

/** Poll: returns {ready, result} when fulfilment is done; {ready:false} otherwise. */
export async function getReportStatus(
  sessionId: string
): Promise<{ ready: true; result: FulfilmentResponse } | { ready: false }> {
  const res = await fetch(
    `${API_URL}/api/v1/checks/basic/status?session_id=${encodeURIComponent(sessionId)}`,
    { method: "GET" }
  );
  if (res.status === 202) return { ready: false };
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return { ready: true, result: await res.json() };
}


// --- EV Health Check ---

export interface RangeEstimate {
  estimated_range_miles: number | null;
  min_range_now_miles: number | null;
  max_range_now_miles: number | null;
  min_range_new_miles: number | null;
  max_range_new_miles: number | null;
  official_range_miles: number | null;
  range_retention_pct: number | null;
  warranty_miles_remaining: number | null;
  warranty_months_remaining: number | null;
  battery_test_available: boolean;
  battery_test_date: string | null;
  battery_test_grade: string | null;
  battery_capacity_kwh: number | null;
  usable_battery_capacity_kwh: number | null;
  data_source: string;
}

export interface RangeScenario {
  scenario: string;
  temperature_c: number | null;
  estimated_miles: number | null;
  driving_style: string | null;
}

export interface EVSpecs {
  battery_capacity_kwh: number | null;
  usable_capacity_kwh: number | null;
  battery_type: string | null;
  battery_chemistry: string | null;
  battery_architecture: string | null;
  battery_weight_kg: number | null;
  battery_warranty_years: number | null;
  battery_warranty_miles: number | null;
  charge_port: string | null;
  fast_charge_port: string | null;
  max_dc_charge_kw: number | null;
  avg_dc_charge_kw: number | null;
  max_ac_charge_kw: number | null;
  charge_time_home_mins: number | null;
  charge_time_rapid_mins: number | null;
  rapid_charge_speed_mph: number | null;
  energy_consumption_wh_per_mile: number | null;
  energy_consumption_mi_per_kwh: number | null;
  real_range_miles: number | null;
  drivetrain: string | null;
  motor_power_kw: number | null;
  motor_power_bhp: number | null;
  top_speed_mph: number | null;
  zero_to_sixty_secs: number | null;
  kerb_weight_kg: number | null;
  boot_capacity_litres: number | null;
  boot_capacity_max_litres: number | null;
  frunk_litres: number | null;
  max_towing_weight_kg: number | null;
  data_source: string;
}

export interface LifespanPrediction {
  predicted_remaining_years: number | null;
  prediction_range: string | null;
  one_year_survival_pct: number | null;
  model_avg_final_miles: number | null;
  model_avg_final_age: number | null;
  manufacturer_avg_final_miles: number | null;
  manufacturer_avg_final_age: number | null;
  pct_still_on_road: number | null;
  initially_registered: number | null;
  currently_licensed: number | null;
  data_source: string;
}

export interface BatteryHealth {
  score: number | null;
  grade: string | null;
  degradation_estimate_pct: number | null;
  summary: string | null;
  test_grade: string | null;
  test_date: string | null;
}

export interface ChargingCosts {
  home_cost_per_full_charge: number | null;
  rapid_cost_per_full_charge: number | null;
  cost_per_mile_home: number | null;
  cost_per_mile_rapid: number | null;
  cost_per_mile_public: number | null;
  annual_cost_estimate_home: number | null;
  annual_cost_estimate_rapid: number | null;
  vs_petrol_annual_saving: number | null;
}

export interface EVCheckResponse {
  registration: string;
  tier: string;
  is_electric: boolean;
  ev_type: string | null;
  vehicle: VehicleIdentity | null;
  mot_summary: MOTSummary | null;
  mot_tests: MOTTestRecord[];
  clocking_analysis: ClockingAnalysis | null;
  condition_score: number | null;
  mileage_timeline: MileageReading[];
  failure_patterns: FailurePattern[];
  ulez_compliance: ULEZCompliance | null;
  tax_calculation: TaxCalculation | null;
  safety_rating: SafetyRating | null;
  vehicle_stats: VehicleStats | null;
  range_estimate: RangeEstimate | null;
  range_scenarios: RangeScenario[];
  ev_specs: EVSpecs | null;
  lifespan_prediction: LifespanPrediction | null;
  battery_health: BatteryHealth | null;
  charging_costs: ChargingCosts | null;
  finance_check?: FinanceCheck | null;
  stolen_check?: StolenCheck | null;
  write_off_check?: WriteOffCheck | null;
  salvage_check?: SalvageCheck | null;
  import_status?: ImportStatusCheck | null;
  plate_changes?: PlateChangeHistory | null;
  keeper_history?: KeeperHistory | null;
  valuation?: Valuation | null;
  high_risk?: HighRiskCheck | null;
  previous_searches?: PreviousSearches | null;
  checked_at: string;
  data_sources: string[];
}

export async function getEVCheckCount(): Promise<number> {
  try {
    const res = await fetch(`${API_URL}/api/v1/ev/count`);
    if (!res.ok) return 0;
    const data = await res.json();
    return data.total_checks || 0;
  } catch {
    return 0;
  }
}

export async function runEVCheck(
  registration: string
): Promise<EVCheckResponse> {
  const res = await fetch(`${API_URL}/api/v1/ev/check`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ registration }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "EV check failed" }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }

  return res.json();
}

export interface EVPreviewResponse {
  registration: string;
  ev_check: EVCheckResponse | null;
  price: string;
}

export async function runEVPreview(
  registration: string
): Promise<EVPreviewResponse> {
  const res = await fetch(`${API_URL}/api/v1/ev/preview`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ registration }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "EV preview failed" }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }

  return res.json();
}

export async function createEVCheckout(
  registration: string,
  email: string | null,
  tier: "ev" | "ev_complete" = "ev"
): Promise<CheckoutResponse> {
  const body: Record<string, unknown> = { registration, tier };
  if (email) body.email = email;
  const res = await fetch(`${API_URL}/api/v1/ev/checkout`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "EV checkout failed" }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }

  return res.json();
}

export interface EVFulfilmentResponse extends FulfilmentResponse {
  ev_check: EVCheckResponse | null;
}

export async function fulfilEVReport(
  sessionId: string
): Promise<EVFulfilmentResponse> {
  const res = await fetch(
    `${API_URL}/api/v1/ev/fulfil?session_id=${encodeURIComponent(sessionId)}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    }
  );

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "EV report generation failed" }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }

  return res.json();
}

export async function triggerEVFulfilment(sessionId: string): Promise<void> {
  await fetch(
    `${API_URL}/api/v1/ev/fulfil/trigger?session_id=${encodeURIComponent(sessionId)}`,
    { method: "POST" }
  );
}

export async function getEVReportStatus(
  sessionId: string
): Promise<{ ready: true; result: EVFulfilmentResponse } | { ready: false }> {
  const res = await fetch(
    `${API_URL}/api/v1/ev/status?session_id=${encodeURIComponent(sessionId)}`,
    { method: "GET" }
  );
  if (res.status === 202) return { ready: false };
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return { ready: true, result: await res.json() };
}
