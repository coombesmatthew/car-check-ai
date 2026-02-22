"use client";

import { ChargingCosts, EVSpecs } from "@/lib/api";

interface Props {
  costs: ChargingCosts;
  specs?: EVSpecs | null;
}

export default function ChargingCard({ costs, specs }: Props) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5">
      <h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
        <svg className="w-4 h-4 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
        </svg>
        Charging Costs
      </h3>

      <div className="grid grid-cols-2 gap-4 mb-4">
        {/* Home Charging */}
        <div className="bg-emerald-50 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <svg className="w-5 h-5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 12l8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" />
            </svg>
            <span className="text-sm font-semibold text-emerald-700">Home (7kW)</span>
          </div>
          {specs?.charge_time_home_mins && (
            <p className="text-xs text-slate-500 mb-2">{Math.round(specs.charge_time_home_mins / 60)} hrs full charge</p>
          )}
          <p className="text-2xl font-bold text-emerald-700">
            {costs.cost_per_mile_home !== null ? `${costs.cost_per_mile_home}p` : "—"}
            <span className="text-xs font-normal text-slate-500">/mile</span>
          </p>
          {costs.home_cost_per_full_charge !== null && (
            <p className="text-xs text-slate-500 mt-1">£{costs.home_cost_per_full_charge.toFixed(2)} per full charge</p>
          )}
        </div>

        {/* Rapid Charging */}
        <div className="bg-amber-50 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <svg className="w-5 h-5 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
            </svg>
            <span className="text-sm font-semibold text-amber-700">Rapid DC</span>
          </div>
          {specs?.charge_time_rapid_mins && (
            <p className="text-xs text-slate-500 mb-2">{specs.charge_time_rapid_mins} mins 10-80%</p>
          )}
          <p className="text-2xl font-bold text-amber-700">
            {(costs.cost_per_mile_public ?? costs.cost_per_mile_rapid) !== null ? `${costs.cost_per_mile_public ?? costs.cost_per_mile_rapid}p` : "—"}
            <span className="text-xs font-normal text-slate-500">/mile</span>
          </p>
          {costs.rapid_cost_per_full_charge !== null && (
            <p className="text-xs text-slate-500 mt-1">£{costs.rapid_cost_per_full_charge.toFixed(2)} per full charge</p>
          )}
        </div>
      </div>

      {/* Annual savings */}
      {costs.vs_petrol_annual_saving !== null && (
        <div className="bg-slate-50 rounded-lg p-3 text-center">
          <p className="text-sm text-slate-600">
            Save up to <span className="font-bold text-emerald-600">£{costs.vs_petrol_annual_saving.toFixed(0)}/year</span> vs petrol
          </p>
          <p className="text-xs text-slate-400">Based on 10,000 miles/year at home charging rates</p>
        </div>
      )}
    </div>
  );
}
