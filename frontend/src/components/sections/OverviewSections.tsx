"use client";

import { VehicleIdentity, MOTSummary, TaxCalculation, VehicleStats, SafetyRating } from "@/lib/api";
import Badge from "@/components/ui/Badge";
import Card from "@/components/ui/Card";
import { DetailRow, StarRating, icons } from "./shared";

export default function OverviewSections({ vehicle, mot_summary, tax_calculation, vehicle_stats, safety_rating }: {
  vehicle: VehicleIdentity | null;
  mot_summary: MOTSummary | null;
  tax_calculation: TaxCalculation | null;
  vehicle_stats: VehicleStats | null;
  safety_rating: SafetyRating | null;
}) {
  return (
    <>
      {/* Vehicle Identity */}
      {vehicle && (
        <Card title="Vehicle Identity" icon={icons.car} status="neutral">
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
        <Card
          title="Tax & MOT Status"
          icon={icons.shield}
          status={
            vehicle.tax_status === "Taxed" && vehicle.mot_status === "Valid"
              ? "pass"
              : vehicle.tax_status !== "Taxed" || (vehicle.mot_status !== "Valid" && vehicle.mot_status !== "No details held by DVLA")
              ? "fail"
              : "neutral"
          }
        >
          <DetailRow
            label="Tax Status"
            value={
              <Badge
                variant={
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
              <Badge
                variant={
                  vehicle.mot_status === "Valid" ? "pass" : vehicle.mot_status === "No details held by DVLA" ? "neutral" : "fail"
                }
                label={vehicle.mot_status || "Unknown"}
              />
            }
          />
          <DetailRow label="MOT Expiry" value={vehicle.mot_expiry_date} />
          <DetailRow
            label="V5C (Logbook) Issued"
            value={vehicle.date_of_last_v5c_issued}
          />
          {vehicle_stats?.v5c_days_since !== null && vehicle_stats?.v5c_days_since !== undefined && vehicle_stats.v5c_days_since <= 90 && (
            <div className="flex items-start gap-2 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2 mt-1 mb-1">
              <svg className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
              </svg>
              <div>
                <span className="text-xs font-semibold text-amber-800">Recently Issued</span>
                <p className="text-xs text-amber-700">V5C issued {vehicle_stats.v5c_days_since} days ago &mdash; may indicate a recent ownership change. Ask the seller how long they&apos;ve owned the car.</p>
              </div>
            </div>
          )}
          <DetailRow
            label="Export Marker"
            value={
              vehicle.marked_for_export ? (
                <Badge variant="warn" label="Marked for Export" />
              ) : (
                "No"
              )
            }
          />
        </Card>
      )}

      {/* Vehicle Statistics */}
      {vehicle_stats && (
        <Card title="Vehicle Statistics" icon={icons.chart} status="neutral">
          {vehicle_stats.vehicle_age_years !== null && (
            <DetailRow label="Vehicle Age" value={`${vehicle_stats.vehicle_age_years} years`} />
          )}
          {vehicle_stats.total_recorded_mileage !== null && (
            <DetailRow label="Total Mileage" value={`${vehicle_stats.total_recorded_mileage.toLocaleString()} miles`} />
          )}
          {vehicle_stats.estimated_annual_mileage !== null && (
            <DetailRow label="Annual Average" value={`${vehicle_stats.estimated_annual_mileage.toLocaleString()} mi/yr`} />
          )}
          {vehicle_stats.mileage_assessment && (
            <div className={`mt-2 text-xs font-medium px-2.5 py-1.5 rounded-lg flex items-center gap-1.5 ${
              vehicle_stats.mileage_assessment === "High mileage"
                ? "bg-amber-50 text-amber-700 border border-amber-200"
                : vehicle_stats.mileage_assessment === "Below average mileage"
                ? "bg-blue-50 text-blue-700 border border-blue-200"
                : "bg-slate-50 text-slate-600 border border-slate-200"
            }`}>
              {vehicle_stats.mileage_assessment === "High mileage" ? (
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126z" /></svg>
              ) : (
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              )}
              {vehicle_stats.mileage_assessment}
            </div>
          )}
          {vehicle_stats.mileage_readings_count !== null && (
            <DetailRow label="MOT Readings" value={vehicle_stats.mileage_readings_count} />
          )}
          {(vehicle_stats.mot_status_detail || vehicle_stats.tax_status_detail || vehicle_stats.v5c_insight) && (
            <div className="mt-3 pt-3 border-t border-slate-100" />
          )}
          {vehicle_stats.mot_status_detail && (
            <DetailRow
              label="MOT"
              value={
                <Badge
                  variant={vehicle_stats.mot_days_remaining !== null && vehicle_stats.mot_days_remaining < 0 ? "fail" : vehicle_stats.mot_days_remaining !== null && vehicle_stats.mot_days_remaining <= 30 ? "warn" : "pass"}
                  label={vehicle_stats.mot_status_detail}
                />
              }
            />
          )}
          {vehicle_stats.tax_status_detail && (
            <DetailRow
              label="Tax"
              value={
                <Badge
                  variant={vehicle_stats.tax_days_remaining !== null && vehicle_stats.tax_days_remaining < 0 ? "fail" : vehicle_stats.tax_days_remaining !== null && vehicle_stats.tax_days_remaining <= 30 ? "warn" : "pass"}
                  label={vehicle_stats.tax_status_detail}
                />
              }
            />
          )}
          {vehicle_stats.v5c_insight && (
            <DetailRow label="V5C" value={vehicle_stats.v5c_insight} />
          )}
          {(vehicle_stats.total_advisory_items !== null || vehicle_stats.total_failure_items !== null) && (
            <>
              <div className="mt-3 pt-3 border-t border-slate-100" />
              <p className="text-xs text-slate-400 mb-2">Lifetime MOT Defect Totals</p>
              <div className="grid grid-cols-3 gap-2 text-center">
                {vehicle_stats.total_advisory_items !== null && (
                  <div className="bg-blue-50 rounded-lg py-2">
                    <div className="text-lg font-bold text-blue-700">{vehicle_stats.total_advisory_items}</div>
                    <div className="text-xs text-blue-500">Advisories</div>
                  </div>
                )}
                {vehicle_stats.total_failure_items !== null && (
                  <div className="bg-amber-50 rounded-lg py-2">
                    <div className="text-lg font-bold text-amber-700">{vehicle_stats.total_failure_items}</div>
                    <div className="text-xs text-amber-500">Failures</div>
                  </div>
                )}
                {vehicle_stats.total_dangerous_items !== null && vehicle_stats.total_dangerous_items > 0 && (
                  <div className="bg-red-50 rounded-lg py-2">
                    <div className="text-lg font-bold text-red-700">{vehicle_stats.total_dangerous_items}</div>
                    <div className="text-xs text-red-500">Dangerous</div>
                  </div>
                )}
              </div>
            </>
          )}
        </Card>
      )}

      {/* Safety Rating */}
      {safety_rating && (
        <Card title="Safety Rating" icon={icons.star} status={safety_rating.stars >= 4 ? "pass" : safety_rating.stars >= 3 ? "warn" : "fail"}>
          <div className="mb-3">
            <StarRating stars={safety_rating.stars} />
            <p className="text-xs text-slate-400 mt-1">
              {safety_rating.source} &middot; {safety_rating.year_range} &middot; Tested {safety_rating.test_year}
            </p>
          </div>
          <div className="space-y-2">
            {[
              { label: "Adult Occupant", value: safety_rating.adult },
              { label: "Child Occupant", value: safety_rating.child },
              { label: "Pedestrian", value: safety_rating.pedestrian },
              { label: "Safety Assist", value: safety_rating.safety_assist },
            ].map(({ label, value }) => (
              <div key={label}>
                <div className="flex justify-between text-xs mb-0.5">
                  <span className="text-slate-500">{label}</span>
                  <span className="font-medium text-slate-700">{value}%</span>
                </div>
                <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      value >= 80 ? "bg-emerald-500" : value >= 60 ? "bg-amber-400" : "bg-red-400"
                    }`}
                    style={{ width: `${value}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </>
  );
}
