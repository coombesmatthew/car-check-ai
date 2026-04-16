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
          {ulez_compliance.zone_details && ulez_compliance.zone_details.length > 0 ? (
            <>
              <div className="mb-3">
                {ulez_compliance.zone_details
                  .filter((z) => z.cars_affected)
                  .map((z) => (
                    <div key={z.zone_id} className="flex items-start justify-between py-2 border-b border-slate-50 last:border-0">
                      <div>
                        <span className="text-sm text-slate-700">{z.name}</span>
                        {!z.compliant && z.charge && (
                          <p className="text-xs text-slate-400 mt-0.5">{z.charge}</p>
                        )}
                      </div>
                      <div className="flex-shrink-0 ml-3">
                        <Badge
                          variant={z.compliant ? "pass" : "fail"}
                          label={z.compliant ? "Clear" : "Charge"}
                        />
                      </div>
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
