"use client";

import { EVCheckResponse } from "@/lib/api";

interface Props {
  result: EVCheckResponse;
}

export default function EVCheckResult({ result }: Props) {
  const { vehicle, mot_summary, clocking_analysis, condition_score } = result;

  return (
    <div className="space-y-4">
      {/* EV Badge */}
      <div className="flex items-center gap-3 mb-2">
        <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-emerald-100 text-emerald-700 text-sm font-semibold rounded-full">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
          </svg>
          {result.ev_type === "BEV" ? "Battery Electric" : "Plug-in Hybrid"}
        </span>
        {condition_score !== null && (
          <span className={`px-3 py-1 text-sm font-semibold rounded-full ${
            condition_score >= 70 ? "bg-emerald-100 text-emerald-700" :
            condition_score >= 40 ? "bg-amber-100 text-amber-700" :
            "bg-red-100 text-red-700"
          }`}>
            Condition: {condition_score}/100
          </span>
        )}
      </div>

      {/* Vehicle Identity Card */}
      {vehicle && (
        <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
          <div className="bg-emerald-600 px-5 py-3">
            <h3 className="text-white font-semibold flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 18.75a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m3 0h6m-9 0H3.375a1.125 1.125 0 01-1.125-1.125V14.25m17.25 4.5a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m3 0h1.125c.621 0 1.129-.504 1.09-1.124a17.902 17.902 0 00-3.213-9.193 2.056 2.056 0 00-1.58-.86H14.25M16.5 18.75h-2.25m0-11.177v-.958c0-.568-.422-1.048-.987-1.106a48.554 48.554 0 00-10.026 0 1.106 1.106 0 00-.987 1.106v7.635m12-6.677v6.677m0 4.5v-4.5m0 0h-12" />
              </svg>
              Vehicle Details
            </h3>
          </div>
          <div className="p-5 grid grid-cols-2 sm:grid-cols-3 gap-4">
            <div>
              <p className="text-xs text-slate-500">Registration</p>
              <p className="font-mono font-bold text-lg tracking-wider">{vehicle.registration}</p>
            </div>
            <div>
              <p className="text-xs text-slate-500">Make</p>
              <p className="font-semibold">{vehicle.make}</p>
            </div>
            <div>
              <p className="text-xs text-slate-500">Year</p>
              <p className="font-semibold">{vehicle.year_of_manufacture}</p>
            </div>
            <div>
              <p className="text-xs text-slate-500">Colour</p>
              <p className="font-semibold">{vehicle.colour}</p>
            </div>
            <div>
              <p className="text-xs text-slate-500">Fuel Type</p>
              <p className="font-semibold text-emerald-600">{vehicle.fuel_type}</p>
            </div>
            <div>
              <p className="text-xs text-slate-500">Tax Status</p>
              <p className={`font-semibold ${vehicle.tax_status === "Taxed" ? "text-emerald-600" : "text-red-600"}`}>
                {vehicle.tax_status}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* MOT Summary */}
      {mot_summary && (
        <div className="bg-white border border-slate-200 rounded-xl p-5">
          <h3 className="font-semibold text-slate-900 mb-3 flex items-center gap-2">
            <svg className="w-4 h-4 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            MOT Summary
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="bg-slate-50 rounded-lg p-3 text-center">
              <p className="text-2xl font-bold text-slate-900">{mot_summary.total_tests}</p>
              <p className="text-xs text-slate-500">Total Tests</p>
            </div>
            <div className="bg-slate-50 rounded-lg p-3 text-center">
              <p className="text-2xl font-bold text-emerald-600">{mot_summary.total_passes}</p>
              <p className="text-xs text-slate-500">Passes</p>
            </div>
            <div className="bg-slate-50 rounded-lg p-3 text-center">
              <p className="text-2xl font-bold text-red-600">{mot_summary.total_failures}</p>
              <p className="text-xs text-slate-500">Failures</p>
            </div>
            <div className="bg-slate-50 rounded-lg p-3 text-center">
              <p className="text-2xl font-bold text-slate-900">{mot_summary.current_odometer || "N/A"}</p>
              <p className="text-xs text-slate-500">Odometer (mi)</p>
            </div>
          </div>
        </div>
      )}

      {/* Clocking Analysis */}
      {clocking_analysis && (
        <div className={`border rounded-xl p-5 ${
          clocking_analysis.clocked ? "bg-red-50 border-red-200" : "bg-emerald-50 border-emerald-200"
        }`}>
          <h3 className="font-semibold text-slate-900 mb-2 flex items-center gap-2">
            {clocking_analysis.clocked ? (
              <svg className="w-5 h-5 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
              </svg>
            ) : (
              <svg className="w-5 h-5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            )}
            Mileage Verification
          </h3>
          <p className={`text-sm ${clocking_analysis.clocked ? "text-red-700" : "text-emerald-700"}`}>
            {clocking_analysis.reason || (clocking_analysis.clocked ? "Potential clocking detected" : "No clocking detected — mileage looks consistent")}
          </p>
        </div>
      )}

      {/* Blurred EV Data Previews */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
        {/* Battery Health Preview */}
        <div className="relative bg-white border border-slate-200 rounded-xl p-5 overflow-hidden">
          <div className="blur-sm pointer-events-none">
            <div className="flex items-center justify-center mb-3">
              <div className="w-20 h-20 rounded-full border-4 border-emerald-400 flex items-center justify-center">
                <span className="text-2xl font-bold text-emerald-600">87</span>
              </div>
            </div>
            <p className="text-center text-sm font-semibold text-slate-900">Battery Health: Grade A</p>
            <p className="text-center text-xs text-slate-500">13% degradation estimated</p>
          </div>
          <div className="absolute inset-0 bg-white/60 flex flex-col items-center justify-center">
            <svg className="w-6 h-6 text-emerald-600 mb-1" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
            </svg>
            <p className="text-xs font-semibold text-slate-700">Battery Health</p>
            <p className="text-xs text-slate-500">Unlock for £7.99</p>
          </div>
        </div>

        {/* Range Estimate Preview */}
        <div className="relative bg-white border border-slate-200 rounded-xl p-5 overflow-hidden">
          <div className="blur-sm pointer-events-none">
            <p className="text-sm font-semibold text-slate-900 mb-2">Real-World Range</p>
            <p className="text-3xl font-bold text-emerald-600">186 <span className="text-sm font-normal text-slate-500">miles</span></p>
            <p className="text-xs text-slate-500 mt-1">vs 245 miles official WLTP</p>
            <div className="mt-2 h-2 bg-slate-100 rounded-full">
              <div className="h-2 bg-emerald-400 rounded-full" style={{ width: "76%" }} />
            </div>
          </div>
          <div className="absolute inset-0 bg-white/60 flex flex-col items-center justify-center">
            <svg className="w-6 h-6 text-emerald-600 mb-1" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
            </svg>
            <p className="text-xs font-semibold text-slate-700">Range Estimate</p>
            <p className="text-xs text-slate-500">Unlock for £7.99</p>
          </div>
        </div>

        {/* Charging Costs Preview */}
        <div className="relative bg-white border border-slate-200 rounded-xl p-5 overflow-hidden">
          <div className="blur-sm pointer-events-none">
            <p className="text-sm font-semibold text-slate-900 mb-2">Charging Costs</p>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-slate-500">Home (7kW)</span>
                <span className="font-semibold">5.2p/mi</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-500">Rapid</span>
                <span className="font-semibold">13.8p/mi</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-500">vs Petrol saving</span>
                <span className="font-semibold text-emerald-600">£1,080/yr</span>
              </div>
            </div>
          </div>
          <div className="absolute inset-0 bg-white/60 flex flex-col items-center justify-center">
            <svg className="w-6 h-6 text-emerald-600 mb-1" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
            </svg>
            <p className="text-xs font-semibold text-slate-700">Charging Costs</p>
            <p className="text-xs text-slate-500">Unlock for £7.99</p>
          </div>
        </div>
      </div>
    </div>
  );
}
