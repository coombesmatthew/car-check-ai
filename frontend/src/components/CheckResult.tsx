"use client";

import { FreeCheckResponse } from "@/lib/api";

function StatusBadge({
  status,
  label,
}: {
  status: "pass" | "fail" | "warn" | "neutral";
  label: string;
}) {
  const colors = {
    pass: "bg-green-100 text-green-800",
    fail: "bg-red-100 text-red-800",
    warn: "bg-amber-100 text-amber-800",
    neutral: "bg-slate-100 text-slate-700",
  };
  return (
    <span
      className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${colors[status]}`}
    >
      {label}
    </span>
  );
}

function Card({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5">
      <h3 className="font-semibold text-slate-900 mb-3">{title}</h3>
      {children}
    </div>
  );
}

function DetailRow({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex justify-between py-1.5 border-b border-slate-100 last:border-0">
      <span className="text-sm text-slate-500">{label}</span>
      <span className="text-sm font-medium text-slate-900">{value ?? "N/A"}</span>
    </div>
  );
}

export default function CheckResult({ data }: { data: FreeCheckResponse }) {
  const { vehicle, mot_summary, clocking_analysis, condition_score, ulez_compliance, mileage_timeline, failure_patterns } = data;

  return (
    <div className="space-y-4">
      {/* Title bar */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-900">
            {vehicle?.make || mot_summary?.make || "Vehicle"}{" "}
            {mot_summary?.model || ""}{" "}
            {vehicle?.year_of_manufacture ? `(${vehicle.year_of_manufacture})` : ""}
          </h2>
          <p className="text-sm text-slate-500">
            Registration: <span className="font-mono font-bold">{data.registration}</span>
            {data.data_sources.length > 0 && (
              <> &middot; Sources: {data.data_sources.join(", ")}</>
            )}
          </p>
        </div>
        {condition_score !== null && (
          <div className="text-center">
            <div
              className={`text-3xl font-bold ${
                condition_score >= 80
                  ? "text-green-600"
                  : condition_score >= 50
                  ? "text-amber-600"
                  : "text-red-600"
              }`}
            >
              {condition_score}
            </div>
            <div className="text-xs text-slate-400">Condition</div>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Vehicle Identity */}
        {vehicle && (
          <Card title="Vehicle Identity">
            <DetailRow label="Make" value={vehicle.make} />
            <DetailRow label="Colour" value={vehicle.colour} />
            <DetailRow label="Fuel Type" value={vehicle.fuel_type} />
            <DetailRow label="Year" value={vehicle.year_of_manufacture} />
            <DetailRow
              label="Engine"
              value={
                vehicle.engine_capacity
                  ? `${vehicle.engine_capacity}cc`
                  : null
              }
            />
            <DetailRow
              label="CO2"
              value={
                vehicle.co2_emissions
                  ? `${vehicle.co2_emissions} g/km`
                  : null
              }
            />
            <DetailRow label="Euro Status" value={vehicle.euro_status} />
            <DetailRow label="Type Approval" value={vehicle.type_approval} />
          </Card>
        )}

        {/* Tax & MOT Status */}
        {vehicle && (
          <Card title="Tax & MOT Status">
            <DetailRow
              label="Tax Status"
              value={
                <StatusBadge
                  status={
                    vehicle.tax_status === "Taxed" ? "pass" : "fail"
                  }
                  label={vehicle.tax_status || "Unknown"}
                />
              }
            />
            <DetailRow label="Tax Due" value={vehicle.tax_due_date} />
            <DetailRow
              label="MOT Status"
              value={
                <StatusBadge
                  status={
                    vehicle.mot_status === "Valid" ? "pass" : vehicle.mot_status === "No details held by DVLA" ? "neutral" : "fail"
                  }
                  label={vehicle.mot_status || "Unknown"}
                />
              }
            />
            <DetailRow label="MOT Expiry" value={vehicle.mot_expiry_date} />
            <DetailRow label="V5C Issued" value={vehicle.date_of_last_v5c_issued} />
            <DetailRow
              label="Export Marker"
              value={
                vehicle.marked_for_export ? (
                  <StatusBadge status="warn" label="Marked for Export" />
                ) : (
                  "No"
                )
              }
            />
          </Card>
        )}

        {/* MOT Summary */}
        {mot_summary && (
          <Card title="MOT History">
            <DetailRow label="Total Tests" value={mot_summary.total_tests} />
            <DetailRow label="Passes" value={mot_summary.total_passes} />
            <DetailRow label="Failures" value={mot_summary.total_failures} />
            <DetailRow
              label="Pass Rate"
              value={
                mot_summary.total_tests > 0
                  ? `${Math.round(
                      (mot_summary.total_passes / mot_summary.total_tests) * 100
                    )}%`
                  : "N/A"
              }
            />
            {mot_summary.latest_test && (
              <>
                <DetailRow
                  label="Latest Test"
                  value={
                    <span>
                      {mot_summary.latest_test.date}{" "}
                      <StatusBadge
                        status={
                          mot_summary.latest_test.result === "PASSED"
                            ? "pass"
                            : "fail"
                        }
                        label={mot_summary.latest_test.result || ""}
                      />
                    </span>
                  }
                />
                <DetailRow
                  label="Current Mileage"
                  value={
                    mot_summary.current_odometer
                      ? `${Number(mot_summary.current_odometer).toLocaleString()} miles`
                      : "N/A"
                  }
                />
                <DetailRow
                  label="MOT Expiry"
                  value={mot_summary.latest_test.expiry_date}
                />
              </>
            )}
          </Card>
        )}

        {/* Mileage & Clocking */}
        {clocking_analysis && (
          <Card title="Mileage Analysis">
            <div className="mb-3">
              <StatusBadge
                status={
                  clocking_analysis.clocked
                    ? "fail"
                    : clocking_analysis.risk_level === "none"
                    ? "pass"
                    : clocking_analysis.risk_level === "unknown"
                    ? "neutral"
                    : "warn"
                }
                label={
                  clocking_analysis.clocked
                    ? "CLOCKING DETECTED"
                    : clocking_analysis.risk_level === "none"
                    ? "No Issues Found"
                    : clocking_analysis.risk_level === "unknown"
                    ? "Insufficient Data"
                    : `${clocking_analysis.risk_level.toUpperCase()} RISK`
                }
              />
            </div>
            {clocking_analysis.reason && (
              <p className="text-sm text-slate-500 mb-2">
                {clocking_analysis.reason}
              </p>
            )}
            {clocking_analysis.flags.map((flag, i) => (
              <div
                key={i}
                className={`text-sm p-2 rounded mb-1 ${
                  flag.severity === "high"
                    ? "bg-red-50 text-red-800"
                    : flag.severity === "medium"
                    ? "bg-amber-50 text-amber-800"
                    : "bg-slate-50 text-slate-700"
                }`}
              >
                {flag.detail}
              </div>
            ))}
            {mileage_timeline.length > 0 && (
              <div className="mt-3 pt-3 border-t border-slate-100">
                <p className="text-xs text-slate-400 mb-2">
                  Mileage Timeline ({mileage_timeline.length} readings)
                </p>
                <div className="space-y-1 max-h-40 overflow-y-auto">
                  {mileage_timeline.map((r, i) => (
                    <div
                      key={i}
                      className="flex justify-between text-xs text-slate-600"
                    >
                      <span>{r.date}</span>
                      <span className="font-mono">
                        {r.miles.toLocaleString()} mi
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </Card>
        )}

        {/* ULEZ Compliance */}
        {ulez_compliance && (
          <Card title="ULEZ / Clean Air Zone">
            <div className="mb-3">
              <StatusBadge
                status={
                  ulez_compliance.compliant === true
                    ? "pass"
                    : ulez_compliance.compliant === false
                    ? "fail"
                    : "neutral"
                }
                label={
                  ulez_compliance.compliant === true
                    ? "COMPLIANT"
                    : ulez_compliance.compliant === false
                    ? "NON-COMPLIANT"
                    : "UNKNOWN"
                }
              />
            </div>
            <p className="text-sm text-slate-600 mb-3">
              {ulez_compliance.reason}
            </p>
            {ulez_compliance.daily_charge && (
              <p className="text-sm text-red-600 font-medium mb-2">
                Daily charge: {ulez_compliance.daily_charge}
              </p>
            )}
            {Object.keys(ulez_compliance.zones).length > 0 && (
              <div className="space-y-1">
                {Object.entries(ulez_compliance.zones).map(([zone, ok]) => (
                  <DetailRow
                    key={zone}
                    label={zone.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
                    value={
                      <StatusBadge
                        status={ok ? "pass" : "fail"}
                        label={ok ? "Pass" : "Fail"}
                      />
                    }
                  />
                ))}
              </div>
            )}
          </Card>
        )}

        {/* Failure Patterns */}
        {failure_patterns.length > 0 && (
          <Card title="Recurring Issues">
            <div className="space-y-2">
              {failure_patterns.map((p, i) => (
                <div key={i} className="flex items-center justify-between">
                  <span className="text-sm capitalize text-slate-700">
                    {p.category}
                  </span>
                  <span className="flex items-center gap-2">
                    <span className="text-xs text-slate-400">
                      {p.occurrences}x
                    </span>
                    <StatusBadge
                      status={
                        p.concern_level === "high"
                          ? "fail"
                          : p.concern_level === "medium"
                          ? "warn"
                          : "neutral"
                      }
                      label={p.concern_level}
                    />
                  </span>
                </div>
              ))}
            </div>
          </Card>
        )}
      </div>

      {/* Upsell */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-6 text-center">
        <h3 className="font-semibold text-blue-900 mb-1">
          Want the full picture?
        </h3>
        <p className="text-sm text-blue-700 mb-3">
          Get stolen vehicle check, outstanding finance, insurance write-off
          history, market valuation, and an AI-powered risk assessment.
        </p>
        <div className="flex justify-center gap-3">
          <button
            disabled
            className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium opacity-50 cursor-not-allowed"
          >
            Full Check - Coming Soon
          </button>
          <a
            href="https://ownvehicle.askmid.com/"
            target="_blank"
            rel="noopener noreferrer"
            className="px-4 py-2 border border-blue-300 text-blue-700 rounded-lg text-sm font-medium hover:bg-blue-100 transition-colors"
          >
            Check Insurance (askMID)
          </a>
        </div>
      </div>
    </div>
  );
}
