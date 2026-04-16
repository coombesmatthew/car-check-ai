"use client";

import { BatteryHealth, RangeEstimate, RangeScenario, ChargingCosts, EVSpecs, LifespanPrediction } from "@/lib/api";
import Card from "@/components/ui/Card";
import { DetailRow, icons } from "@/components/sections/shared";
import BatteryHealthGauge from "../BatteryHealthGauge";
import RangeChart from "../RangeChart";
import ChargingCard from "../ChargingCard";

/* bolt icon for EV-specific cards */
const boltIcon = (
  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
  </svg>
);

export default function EVBatterySections({ battery_health, range_estimate, range_scenarios, charging_costs, ev_specs, lifespan_prediction }: {
  battery_health: BatteryHealth | null;
  range_estimate: RangeEstimate | null;
  range_scenarios: RangeScenario[];
  charging_costs: ChargingCosts | null;
  ev_specs: EVSpecs | null;
  lifespan_prediction: LifespanPrediction | null;
}) {
  return (
    <>
      {/* Battery Health */}
      {battery_health && battery_health.score !== null && battery_health.grade !== null && (
        <Card title="Battery Health" icon={boltIcon} status={battery_health.score >= 80 ? "pass" : battery_health.score >= 60 ? "warn" : "fail"}>
          <div className="flex justify-center mb-4">
            <BatteryHealthGauge score={battery_health.score} grade={battery_health.grade} />
          </div>
          {battery_health.degradation_estimate_pct !== null && (
            <DetailRow label="Degradation" value={`${battery_health.degradation_estimate_pct}%`} />
          )}
          {battery_health.test_grade && (
            <DetailRow label="Test Grade" value={battery_health.test_grade} />
          )}
          {battery_health.test_date && (
            <DetailRow label="Test Date" value={battery_health.test_date} />
          )}
          {battery_health.summary && (
            <p className="text-sm text-slate-500 mt-2">{battery_health.summary}</p>
          )}
        </Card>
      )}

      {/* Range Estimate */}
      {range_estimate && (
        <Card title="Range Estimate" icon={icons.chart} status="neutral">
          {range_estimate.estimated_range_miles !== null && (
            <DetailRow label="Estimated Range" value={`${range_estimate.estimated_range_miles} miles`} />
          )}
          {range_estimate.official_range_miles !== null && (
            <DetailRow label="Official WLTP Range" value={`${range_estimate.official_range_miles} miles`} />
          )}
          {range_estimate.range_retention_pct !== null && (
            <DetailRow label="Range Retention" value={`${range_estimate.range_retention_pct}%`} />
          )}
          {range_estimate.min_range_now_miles !== null && range_estimate.max_range_now_miles !== null && (
            <DetailRow label="Current Range" value={`${range_estimate.min_range_now_miles}–${range_estimate.max_range_now_miles} miles`} />
          )}
          {range_estimate.battery_capacity_kwh !== null && (
            <DetailRow label="Battery Capacity" value={`${range_estimate.battery_capacity_kwh} kWh`} />
          )}
          {range_estimate.warranty_months_remaining !== null && (
            <DetailRow label="Warranty Remaining" value={`${range_estimate.warranty_months_remaining} months`} />
          )}
        </Card>
      )}

      {/* Range by Scenario */}
      {range_scenarios.length > 0 && (
        <div className="md:col-span-2">
          <RangeChart scenarios={range_scenarios} officialRange={range_estimate?.official_range_miles} />
        </div>
      )}

      {/* Charging Costs */}
      {charging_costs && (
        <div className="md:col-span-2">
          <ChargingCard costs={charging_costs} specs={ev_specs} />
        </div>
      )}

      {/* EV Specs */}
      {ev_specs && (
        <Card title="EV Specifications" icon={boltIcon} status="neutral">
          {ev_specs.battery_capacity_kwh !== null && (
            <DetailRow label="Battery Capacity" value={`${ev_specs.battery_capacity_kwh} kWh`} />
          )}
          {ev_specs.usable_capacity_kwh !== null && (
            <DetailRow label="Usable Capacity" value={`${ev_specs.usable_capacity_kwh} kWh`} />
          )}
          {ev_specs.battery_type && (
            <DetailRow label="Battery Type" value={ev_specs.battery_type} />
          )}
          {ev_specs.battery_chemistry && (
            <DetailRow label="Chemistry" value={ev_specs.battery_chemistry} />
          )}
          {ev_specs.real_range_miles !== null && (
            <DetailRow label="Real-World Range" value={`${ev_specs.real_range_miles} miles`} />
          )}
          {ev_specs.energy_consumption_mi_per_kwh !== null && (
            <DetailRow label="Efficiency" value={`${ev_specs.energy_consumption_mi_per_kwh} mi/kWh`} />
          )}
          {(ev_specs.max_dc_charge_kw !== null || ev_specs.max_ac_charge_kw !== null) && (
            <div className="mt-3 pt-3 border-t border-slate-100" />
          )}
          {ev_specs.max_dc_charge_kw !== null && (
            <DetailRow label="Max DC Charge" value={`${ev_specs.max_dc_charge_kw} kW`} />
          )}
          {ev_specs.max_ac_charge_kw !== null && (
            <DetailRow label="Max AC Charge" value={`${ev_specs.max_ac_charge_kw} kW`} />
          )}
          {ev_specs.charge_port && (
            <DetailRow label="Charge Port" value={ev_specs.charge_port} />
          )}
          {ev_specs.fast_charge_port && (
            <DetailRow label="Fast Charge Port" value={ev_specs.fast_charge_port} />
          )}
          {(ev_specs.motor_power_bhp !== null || ev_specs.drivetrain) && (
            <div className="mt-3 pt-3 border-t border-slate-100" />
          )}
          {ev_specs.motor_power_bhp !== null && (
            <DetailRow label="Power" value={`${ev_specs.motor_power_bhp} bhp`} />
          )}
          {ev_specs.drivetrain && (
            <DetailRow label="Drivetrain" value={ev_specs.drivetrain} />
          )}
          {ev_specs.zero_to_sixty_secs !== null && (
            <DetailRow label="0-60 mph" value={`${ev_specs.zero_to_sixty_secs}s`} />
          )}
          {ev_specs.top_speed_mph !== null && (
            <DetailRow label="Top Speed" value={`${ev_specs.top_speed_mph} mph`} />
          )}
          {ev_specs.kerb_weight_kg !== null && (
            <DetailRow label="Kerb Weight" value={`${ev_specs.kerb_weight_kg} kg`} />
          )}
          {ev_specs.battery_warranty_years !== null && (
            <DetailRow label="Battery Warranty" value={`${ev_specs.battery_warranty_years} years / ${ev_specs.battery_warranty_miles?.toLocaleString() ?? "—"} miles`} />
          )}
        </Card>
      )}

      {/* Lifespan Prediction */}
      {lifespan_prediction && (
        <Card title="Lifespan Prediction" icon={icons.clock} status="neutral">
          {lifespan_prediction.predicted_remaining_years !== null && (
            <DetailRow label="Predicted Remaining" value={`${lifespan_prediction.predicted_remaining_years} years`} />
          )}
          {lifespan_prediction.prediction_range && (
            <DetailRow label="Prediction Range" value={lifespan_prediction.prediction_range} />
          )}
          {lifespan_prediction.one_year_survival_pct !== null && (
            <DetailRow label="1-Year Survival" value={`${lifespan_prediction.one_year_survival_pct}%`} />
          )}
          {lifespan_prediction.pct_still_on_road !== null && (
            <DetailRow label="Still on Road" value={`${lifespan_prediction.pct_still_on_road}%`} />
          )}
          {lifespan_prediction.model_avg_final_miles !== null && (
            <DetailRow label="Model Avg Final Miles" value={`${lifespan_prediction.model_avg_final_miles.toLocaleString()} miles`} />
          )}
          {lifespan_prediction.model_avg_final_age !== null && (
            <DetailRow label="Model Avg Final Age" value={`${lifespan_prediction.model_avg_final_age} years`} />
          )}
          {lifespan_prediction.initially_registered !== null && lifespan_prediction.currently_licensed !== null && (
            <div className="mt-3 pt-3 border-t border-slate-100">
              <DetailRow label="Initially Registered" value={lifespan_prediction.initially_registered.toLocaleString()} />
              <DetailRow label="Currently Licensed" value={lifespan_prediction.currently_licensed.toLocaleString()} />
            </div>
          )}
        </Card>
      )}
    </>
  );
}
