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
  salvage_check: SalvageCheck | null;
  checked_at: string;
  data_sources: string[];
}

export interface BasicCheckPreviewResponse {
  registration: string;
  ai_report: string | null;
  free_check: FreeCheckResponse | null;
  price: string;
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

export async function runBasicCheckPreview(
  registration: string,
  listingUrl?: string,
  listingPrice?: number
): Promise<BasicCheckPreviewResponse> {
  const res = await fetch(`${API_URL}/api/v1/checks/basic/preview`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      registration,
      listing_url: listingUrl || null,
      listing_price: listingPrice || null,
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Report generation failed" }));
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
  email: string,
  tier: string = "basic",
  listingUrl?: string,
  listingPrice?: number
): Promise<CheckoutResponse> {
  const res = await fetch(`${API_URL}/api/v1/checks/basic/checkout`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      registration,
      email,
      tier,
      listing_url: listingUrl || null,
      listing_price: listingPrice || null,
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Checkout failed" }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }

  return res.json();
}

export interface ListingData {
  url: string;
  platform: string;
  title: string | null;
  price_pence: number | null;
  mileage: number | null;
  registration: string | null;
  description: string | null;
  seller_type: string | null;
  location: string | null;
  features: string[];
  images_count: number | null;
  scrape_success: boolean;
  scrape_errors: string[];
  demo_mode: boolean;
}

export interface ListingCheckResponse {
  listing: ListingData;
  free_check: FreeCheckResponse | null;
  ai_report: string | null;
  price_assessment: string | null;
}

export async function checkListing(
  url: string,
  registration?: string
): Promise<ListingCheckResponse> {
  const res = await fetch(`${API_URL}/api/v1/checks/listing`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, registration: registration || null }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Listing check failed" }));
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
