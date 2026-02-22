"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";
import { fulfilEVReport, EVFulfilmentResponse } from "@/lib/api";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import EVAIReport from "@/components/ev/EVAIReport";
import BatteryHealthGauge from "@/components/ev/BatteryHealthGauge";
import RangeChart from "@/components/ev/RangeChart";
import ChargingCard from "@/components/ev/ChargingCard";

function SuccessContent() {
  const searchParams = useSearchParams();
  const sessionId = searchParams.get("session_id");

  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [result, setResult] = useState<EVFulfilmentResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId) {
      setStatus("error");
      setError("No payment session found");
      return;
    }

    fulfilEVReport(sessionId)
      .then((data) => {
        setResult(data);
        setStatus("success");
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : "Something went wrong");
        setStatus("error");
      });
  }, [sessionId]);

  if (status === "loading") {
    return (
      <div className="text-center py-20">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-emerald-100 mb-6">
          <svg className="animate-spin h-8 w-8 text-emerald-600" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
          </svg>
        </div>
        <h2 className="text-2xl font-bold text-slate-900 mb-2">Generating your EV report...</h2>
        <p className="text-slate-500">Payment confirmed. Analysing battery health and range data now.</p>
      </div>
    );
  }

  if (status === "error") {
    return (
      <div className="text-center py-20">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-red-100 mb-6">
          <svg className="w-8 h-8 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
          </svg>
        </div>
        <h2 className="text-2xl font-bold text-slate-900 mb-2">Something went wrong</h2>
        <p className="text-slate-500 mb-4">{error}</p>
        <p className="text-sm text-slate-400">
          If you were charged, please contact us and we&apos;ll sort this out immediately.
        </p>
        <a
          href="/ev"
          className="inline-block mt-6 px-6 py-3 bg-emerald-600 text-white font-semibold rounded-lg hover:bg-emerald-700 transition-colors"
        >
          Back to EV Check
        </a>
      </div>
    );
  }

  const verdictColour = {
    BUY: "text-emerald-600 bg-emerald-50 border-emerald-200",
    NEGOTIATE: "text-amber-600 bg-amber-50 border-amber-200",
    AVOID: "text-red-600 bg-red-50 border-red-200",
  }[result?.verdict || ""] || "text-slate-600 bg-slate-50 border-slate-200";

  const evCheck = result?.ev_check;
  const batteryHealth = evCheck?.battery_health;
  const chargingCosts = evCheck?.charging_costs;
  const rangeScenarios = evCheck?.range_scenarios || [];
  const rangeEstimate = evCheck?.range_estimate;
  const evSpecs = evCheck?.ev_specs;

  return (
    <div className="py-10">
      {/* Success header */}
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-emerald-100 mb-4">
          <svg className="w-8 h-8 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
          </svg>
        </div>
        <h2 className="text-2xl font-bold text-slate-900 mb-2">Your EV Health Report is ready!</h2>
        <p className="text-slate-500">
          {result?.email_sent
            ? "A PDF copy has been sent to your email."
            : "Your report has been generated successfully."}
        </p>
      </div>

      {/* Report summary card */}
      <div className="max-w-md mx-auto bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm mb-8">
        <div className="bg-emerald-50 px-6 py-4 border-b border-emerald-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-500">Vehicle</p>
              <p className="text-lg font-bold font-mono tracking-wider text-slate-900">
                {result?.registration}
              </p>
            </div>
            {result?.verdict && (
              <span className={`px-4 py-1.5 rounded-lg font-bold text-sm border ${verdictColour}`}>
                {result.verdict}
              </span>
            )}
          </div>
        </div>
        <div className="px-6 py-4 space-y-3">
          <div className="flex justify-between text-sm">
            <span className="text-slate-500">Report Reference</span>
            <span className="font-mono text-slate-700">{result?.report_ref}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-slate-500">Email Delivered</span>
            <span className={result?.email_sent ? "text-emerald-600 font-medium" : "text-amber-600"}>
              {result?.email_sent ? "Sent" : "Pending setup"}
            </span>
          </div>
        </div>
      </div>

      {/* EV Data Visualizations */}
      {(batteryHealth?.score || chargingCosts || rangeScenarios.length > 0) && (
        <div className="space-y-6 mb-8">
          {/* Battery Health + Charging side by side on desktop */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {batteryHealth?.score && batteryHealth.grade && (
              <div className="bg-white border border-slate-200 rounded-xl p-6">
                <h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
                  <svg className="w-4 h-4 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M21 10.5h.375c.621 0 1.125.504 1.125 1.125v2.25c0 .621-.504 1.125-1.125 1.125H21M4.5 10.5H18V15H4.5v-4.5zM3.75 18h15A2.25 2.25 0 0021 15.75v-6a2.25 2.25 0 00-2.25-2.25h-15A2.25 2.25 0 001.5 9.75v6A2.25 2.25 0 003.75 18z" />
                  </svg>
                  Battery Health
                </h3>
                <BatteryHealthGauge score={batteryHealth.score} grade={batteryHealth.grade} />
                {batteryHealth.degradation_estimate_pct !== null && (
                  <p className="text-sm text-slate-500 text-center mt-3">
                    {batteryHealth.degradation_estimate_pct}% degradation estimated
                  </p>
                )}
                {batteryHealth.summary && (
                  <p className="text-sm text-slate-600 text-center mt-1">{batteryHealth.summary}</p>
                )}
              </div>
            )}

            {chargingCosts && (
              <ChargingCard costs={chargingCosts} specs={evSpecs} />
            )}
          </div>

          {/* Range scenarios */}
          {rangeScenarios.length > 0 && (
            <RangeChart
              scenarios={rangeScenarios}
              officialRange={rangeEstimate?.official_range_miles}
            />
          )}
        </div>
      )}

      {/* Full AI Report */}
      {result?.ai_report && (
        <div className="mb-8">
          <EVAIReport report={result.ai_report} registration={result.registration} />
        </div>
      )}

      {/* Actions */}
      <div className="text-center space-y-3">
        <a
          href="/ev"
          className="inline-block px-8 py-3 bg-emerald-600 text-white font-semibold rounded-lg hover:bg-emerald-700 transition-colors"
        >
          Check Another EV
        </a>
        <p className="text-xs text-slate-400">
          Report ref: {result?.report_ref}
        </p>
      </div>
    </div>
  );
}

export default function EVReportSuccessPage() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-emerald-50/30 to-white flex flex-col">
      <Header />
      <div className="mx-auto max-w-5xl px-4 flex-1">
        <Suspense fallback={
          <div className="text-center py-20">
            <p className="text-slate-500">Loading...</p>
          </div>
        }>
          <SuccessContent />
        </Suspense>
      </div>
      <Footer />
    </main>
  );
}
