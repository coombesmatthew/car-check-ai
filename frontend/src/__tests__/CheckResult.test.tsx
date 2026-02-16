import { render, screen } from "@testing-library/react";
import CheckResult from "@/components/CheckResult";
import { FreeCheckResponse } from "@/lib/api";

function makeResponse(overrides: Partial<FreeCheckResponse> = {}): FreeCheckResponse {
  return {
    registration: "AB12CDE",
    tier: "free",
    vehicle: {
      registration: "AB12CDE",
      make: "FORD",
      colour: "BLUE",
      fuel_type: "PETROL",
      year_of_manufacture: 2018,
      engine_capacity: 999,
      co2_emissions: 120,
      euro_status: "Euro 6",
      tax_status: "Taxed",
      tax_due_date: "2025-03-01",
      mot_status: "Valid",
      mot_expiry_date: "2025-06-15",
      date_of_last_v5c_issued: null,
      marked_for_export: false,
      type_approval: "M1",
      wheelplan: null,
    },
    mot_summary: {
      total_tests: 3,
      total_passes: 3,
      total_failures: 0,
      registration: "AB12CDE",
      make: "FORD",
      model: "FIESTA",
      first_used_date: null,
      latest_test: {
        date: "2023-03-15",
        result: "PASSED",
        odometer: "39000",
        expiry_date: "2024-03-14",
      },
      current_odometer: "39000",
    },
    clocking_analysis: {
      clocked: false,
      risk_level: "none",
      flags: [],
    },
    condition_score: 98,
    mileage_timeline: [],
    failure_patterns: [],
    ulez_compliance: {
      compliant: true,
      status: "compliant",
      reason: "Petrol vehicle with Euro 6 — meets emission requirements for all 8 zones affecting cars",
      zones: { london_ulez: true, birmingham_caz: true, bristol_caz: true },
    },
    mot_tests: [],
    tax_calculation: null,
    safety_rating: null,
    vehicle_stats: null,
    finance_check: null,
    stolen_check: null,
    write_off_check: null,
    plate_changes: null,
    valuation: null,
    checked_at: "2024-01-15T12:00:00",
    data_sources: ["DVLA VES API", "DVSA MOT History API"],
    ...overrides,
  };
}

describe("CheckResult", () => {
  it("renders vehicle make and model in heading", () => {
    render(<CheckResult data={makeResponse()} />);
    const heading = screen.getByRole("heading", { level: 2 });
    expect(heading.textContent).toContain("FORD");
    expect(heading.textContent).toContain("FIESTA");
  });

  it("renders registration number", () => {
    render(<CheckResult data={makeResponse()} />);
    expect(screen.getByText("AB12CDE")).toBeInTheDocument();
  });

  it("renders condition score", () => {
    render(<CheckResult data={makeResponse()} />);
    expect(screen.getByText("98")).toBeInTheDocument();
  });

  it("renders tax status badge", () => {
    render(<CheckResult data={makeResponse()} />);
    expect(screen.getByText("Taxed")).toBeInTheDocument();
  });

  it("renders MOT summary", () => {
    render(<CheckResult data={makeResponse()} />);
    expect(screen.getByText("MOT History")).toBeInTheDocument();
    // "3" appears multiple times (total_tests and total_passes), verify at least one exists
    expect(screen.getAllByText("3").length).toBeGreaterThanOrEqual(1);
  });

  it("shows ULEZ compliant badge", () => {
    render(<CheckResult data={makeResponse()} />);
    expect(screen.getByText("ALL ZONES CLEAR")).toBeInTheDocument();
  });

  it("shows clocking detection clean status", () => {
    render(<CheckResult data={makeResponse()} />);
    expect(screen.getByText("No Clocking Detected")).toBeInTheDocument();
  });

  it("shows clocking detected when clocked", () => {
    render(
      <CheckResult
        data={makeResponse({
          clocking_analysis: {
            clocked: true,
            risk_level: "high",
            flags: [
              {
                type: "mileage_drop",
                severity: "high",
                detail: "Mileage dropped from 60,000 to 45,000 (15,000 mile drop)",
                from_date: "2022-01-15",
                to_date: "2023-01-15",
                drop_amount: 15000,
              },
            ],
          },
        })}
      />
    );
    expect(screen.getByText("CLOCKING DETECTED")).toBeInTheDocument();
    expect(
      screen.getByText(/Mileage dropped from 60,000 to 45,000/)
    ).toBeInTheDocument();
  });

  it("shows ULEZ non-compliant with charge", () => {
    render(
      <CheckResult
        data={makeResponse({
          ulez_compliance: {
            compliant: false,
            status: "non_compliant",
            reason: "Diesel vehicle with Euro 5 — non-compliant in 7 zones",
            daily_charge: "£12.50/day (London ULEZ) · £60+ penalty (Scottish LEZs)",
            zones: { london_ulez: false, birmingham_caz: false, bristol_caz: false },
          },
        })}
      />
    );
    expect(screen.getByText("NON-COMPLIANT")).toBeInTheDocument();
    expect(screen.getByText(/£12.50/)).toBeInTheDocument();
  });

  it("renders failure patterns when present", () => {
    render(
      <CheckResult
        data={makeResponse({
          failure_patterns: [
            { category: "brake", occurrences: 3, concern_level: "medium" },
            { category: "tyre", occurrences: 5, concern_level: "high" },
          ],
        })}
      />
    );
    expect(screen.getByText("Recurring Issues")).toBeInTheDocument();
    expect(screen.getByText("brake")).toBeInTheDocument();
    expect(screen.getByText("tyre")).toBeInTheDocument();
    expect(screen.getByText("3x")).toBeInTheDocument();
    expect(screen.getByText("5x")).toBeInTheDocument();
  });

  it("shows free tier badge", () => {
    render(<CheckResult data={makeResponse()} />);
    expect(screen.getByText(/Free Check/)).toBeInTheDocument();
  });

  it("handles null vehicle gracefully", () => {
    render(<CheckResult data={makeResponse({ vehicle: null })} />);
    // Should still render without crashing
    expect(screen.getByText("AB12CDE")).toBeInTheDocument();
  });
});
