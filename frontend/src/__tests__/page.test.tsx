import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import Home from "@/app/page";
import * as api from "@/lib/api";

// Mock the API module
jest.mock("@/lib/api");
const mockRunFreeCheck = api.runFreeCheck as jest.MockedFunction<
  typeof api.runFreeCheck
>;

const MOCK_RESPONSE: api.FreeCheckResponse = {
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
    date_of_last_v5c_issued: "2023-05-10",
    marked_for_export: false,
    type_approval: "M1",
    wheelplan: "2 AXLE RIGID BODY",
  },
  mot_summary: {
    total_tests: 3,
    total_passes: 3,
    total_failures: 0,
    registration: "AB12CDE",
    make: "FORD",
    model: "FIESTA",
    first_used_date: "2018.03.15",
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
  mileage_timeline: [
    { date: "2021-03-20", miles: 25000, unit: "mi" },
    { date: "2022-03-18", miles: 32000, unit: "mi" },
    { date: "2023-03-15", miles: 39000, unit: "mi" },
  ],
  failure_patterns: [],
  ulez_compliance: {
    compliant: true,
    status: "compliant",
    reason: "Petrol vehicle with Euro 6 - meets Euro 4 requirement",
    zones: { london_ulez: true, london_lez: true, clean_air_zone_d: true },
  },
  checked_at: "2024-01-15T12:00:00",
  data_sources: ["DVLA VES API", "DVSA MOT History API"],
};

describe("Home Page", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders the search form", () => {
    render(<Home />);
    expect(screen.getByPlaceholderText("AB12 CDE")).toBeInTheDocument();
    expect(screen.getByText("Check")).toBeInTheDocument();
  });

  it("renders the page heading", () => {
    render(<Home />);
    expect(
      screen.getByText("Check any UK vehicle instantly")
    ).toBeInTheDocument();
  });

  it("disables the button when input is too short", () => {
    render(<Home />);
    const button = screen.getByText("Check");
    expect(button).toBeDisabled();
  });

  it("enables the button when registration is entered", () => {
    render(<Home />);
    const input = screen.getByPlaceholderText("AB12 CDE");
    fireEvent.change(input, { target: { value: "AB12CDE" } });
    expect(screen.getByText("Check")).not.toBeDisabled();
  });

  it("uppercases the input automatically", () => {
    render(<Home />);
    const input = screen.getByPlaceholderText("AB12 CDE") as HTMLInputElement;
    fireEvent.change(input, { target: { value: "ab12cde" } });
    expect(input.value).toBe("AB12CDE");
  });

  it("shows error for very short registration", async () => {
    render(<Home />);
    const input = screen.getByPlaceholderText("AB12 CDE");
    fireEvent.change(input, { target: { value: "A" } });

    // Button should be disabled with single char
    expect(screen.getByText("Check")).toBeDisabled();
  });

  it("calls API and shows results on submit", async () => {
    mockRunFreeCheck.mockResolvedValueOnce(MOCK_RESPONSE);

    render(<Home />);
    const input = screen.getByPlaceholderText("AB12 CDE");
    fireEvent.change(input, { target: { value: "AB12CDE" } });
    fireEvent.submit(input.closest("form")!);

    await waitFor(() => {
      expect(mockRunFreeCheck).toHaveBeenCalledWith("AB12CDE");
    });

    await waitFor(() => {
      // Vehicle heading should contain make
      const heading = screen.getByRole("heading", { level: 2 });
      expect(heading.textContent).toContain("FORD");
    });
  });

  it("shows error message on API failure", async () => {
    mockRunFreeCheck.mockRejectedValueOnce(new Error("Vehicle not found"));

    render(<Home />);
    const input = screen.getByPlaceholderText("AB12 CDE");
    fireEvent.change(input, { target: { value: "ZZ99ZZZ" } });
    fireEvent.submit(input.closest("form")!);

    await waitFor(() => {
      expect(screen.getByText("Vehicle not found")).toBeInTheDocument();
    });
  });

  it("disables button during loading", async () => {
    // Use a promise that won't resolve immediately to test loading state
    mockRunFreeCheck.mockImplementationOnce(
      () => new Promise(() => {}) // Never resolves
    );

    render(<Home />);
    const input = screen.getByPlaceholderText("AB12 CDE");
    fireEvent.change(input, { target: { value: "AB12CDE" } });

    const button = screen.getByRole("button", { name: "Check" });
    fireEvent.click(button);

    await waitFor(() => {
      // Button should be disabled during loading
      expect(button).toBeDisabled();
    });
  });
});
