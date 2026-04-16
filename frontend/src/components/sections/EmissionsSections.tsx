"use client";

import { ULEZCompliance, TaxCalculation } from "@/lib/api";
import Badge from "@/components/ui/Badge";
import Card from "@/components/ui/Card";
import { DetailRow, icons } from "./shared";

export default function EmissionsSections({ ulez_compliance, tax_calculation }: {
  ulez_compliance: ULEZCompliance | null;
  tax_calculation: TaxCalculation | null;
}) {
  return (
    <>
      {/* Clean Air Zones */}
      {ulez_compliance && (
        <Card
          title="UK Clean Air Zones"
          icon={icons.mapPin}
          status={
            ulez_compliance.compliant === true
              ? "pass"
              : ulez_compliance.compliant === false
              ? "fail"
              : "neutral"
          }
        >
          <div className="mb-3">
            {ulez_compliance.compliant === true ? (
              <div className="flex items-center gap-2 bg-emerald-50 border border-emerald-200 rounded-lg px-3 py-2">
                <svg className="w-5 h-5 text-emerald-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="text-sm font-semibold text-emerald-800">
                  All Clean Air Zones Clear
                  {ulez_compliance.total_zones && <span className="font-normal text-emerald-600"> ({ulez_compliance.compliant_zones}/{ulez_compliance.total_zones} zones)</span>}
                </span>
              </div>
            ) : ulez_compliance.compliant === false ? (
              <div className="flex items-center gap-2 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
                <svg className="w-5 h-5 text-red-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
                </svg>
                <div>
                  <span className="text-sm font-semibold text-red-800">Non-Compliant</span>
                  {ulez_compliance.daily_charge && (
                    <span className="text-sm text-red-600"> — {ulez_compliance.daily_charge}</span>
                  )}
                </div>
              </div>
            ) : (
              <div className="flex items-center gap-2 bg-slate-50 border border-slate-200 rounded-lg px-3 py-2">
                <svg className="w-5 h-5 text-slate-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z" />
                </svg>
                <span className="text-sm font-semibold text-slate-600">Unable to determine compliance</span>
              </div>
            )}
          </div>
          {ulez_compliance.zone_details && ulez_compliance.zone_details.length > 0 ? (
            <>
              {/* Zones that affect cars */}
              <p className="text-xs font-medium text-slate-500 mb-1.5">Zones affecting private cars</p>
              <div className="space-y-1 mb-3">
                {ulez_compliance.zone_details
                  .filter((z) => z.cars_affected)
                  .map((z) => (
                    <div key={z.zone_id} className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1 py-1 text-sm">
                      <span className="text-slate-700">{z.name}</span>
                      <span className="flex items-center gap-1.5">
                        {!z.compliant && (
                          <span className="text-xs text-slate-400">{z.charge}</span>
                        )}
                        <Badge
                          variant={z.compliant ? "pass" : "fail"}
                          label={z.compliant ? "Clear" : "Charge"}
                        />
                      </span>
                    </div>
                  ))}
              </div>
            </>
          ) : (
            /* Fallback to simple zones dict */
            Object.keys(ulez_compliance.zones).length > 0 && (
              <div className="space-y-1">
                {Object.entries(ulez_compliance.zones).map(([zone, ok]) => (
                  <DetailRow
                    key={zone}
                    label={zone.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
                    value={
                      <Badge
                        variant={ok ? "pass" : "fail"}
                        label={ok ? "Pass" : "Fail"}
                      />
                    }
                  />
                ))}
              </div>
            )
          )}
        </Card>
      )}

      {/* Road Tax / VED */}
      {tax_calculation && (
        <Card title="Road Tax (VED)" icon={icons.currency} status="neutral">
          <DetailRow label="Tax Band" value={`Band ${tax_calculation.band}`} />
          <DetailRow label="CO2 Range" value={tax_calculation.band_range} />
          <DetailRow label="CO2 Emissions" value={`${tax_calculation.co2_emissions} g/km`} />
          <DetailRow label="Fuel Type" value={tax_calculation.fuel_type} />
          <div className="mt-3 pt-3 border-t border-slate-100" />
          <DetailRow label="First Year Rate" value={tax_calculation.first_year_rate === 0 ? "FREE" : `£${tax_calculation.first_year_rate}`} />
          <DetailRow label="Annual Rate (Year 2+)" value={tax_calculation.annual_rate === 0 ? "FREE" : `£${tax_calculation.annual_rate}`} />
          <DetailRow label="6-Month Payment" value={`£${tax_calculation.six_month_rate}`} />
          {tax_calculation.is_electric && (
            <div className="mt-2 text-xs text-emerald-600 bg-emerald-50 rounded px-2 py-1">
              Electric vehicle — zero emissions
            </div>
          )}
          {tax_calculation.is_diesel && (
            <div className="mt-2 text-xs text-amber-600 bg-amber-50 rounded px-2 py-1">
              Diesel supplement may apply (first year)
            </div>
          )}
        </Card>
      )}
    </>
  );
}
