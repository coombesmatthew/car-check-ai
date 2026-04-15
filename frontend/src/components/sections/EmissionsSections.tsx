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
          <div className="mb-3 flex items-center gap-3">
            <Badge
              variant={
                ulez_compliance.compliant === true
                  ? "pass"
                  : ulez_compliance.compliant === false
                  ? "fail"
                  : "neutral"
              }
              label={
                ulez_compliance.compliant === true
                  ? "ALL ZONES CLEAR"
                  : ulez_compliance.compliant === false
                  ? "NON-COMPLIANT"
                  : "UNKNOWN"
              }
              size="md"
            />
            {ulez_compliance.total_zones && (
              <span className="text-xs text-slate-400">
                {ulez_compliance.compliant_zones}/{ulez_compliance.total_zones} zones
              </span>
            )}
          </div>
          <p className="text-sm text-slate-600 mb-3">
            {ulez_compliance.reason}
          </p>
          {ulez_compliance.daily_charge && (
            <div className="text-sm text-red-600 font-medium mb-3 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
              Charges: {ulez_compliance.daily_charge}
            </div>
          )}
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
          <DetailRow
            label="First Year Rate"
            value={
              <span className="font-mono font-bold text-slate-900">
                {tax_calculation.first_year_rate === 0 ? "FREE" : `\u00A3${tax_calculation.first_year_rate}`}
              </span>
            }
          />
          <DetailRow
            label="Annual Rate (Year 2+)"
            value={
              <span className="font-mono font-bold text-slate-900">
                {tax_calculation.annual_rate === 0 ? "FREE" : `\u00A3${tax_calculation.annual_rate}`}
              </span>
            }
          />
          <DetailRow label="6-Month Payment" value={`\u00A3${tax_calculation.six_month_rate}`} />
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
