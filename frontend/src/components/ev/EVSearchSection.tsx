"use client";

import { useState, useEffect } from "react";
import { runEVCheck, runEVPreview, getEVCheckCount, EVCheckResponse } from "@/lib/api";
import EVCheckResult from "./EVCheckResult";
import EVUpsellSection from "./EVUpsellSection";
import EVAIReport from "./EVAIReport";

export default function EVSearchSection() {
  const [registration, setRegistration] = useState("");
  const [loading, setLoading] = useState(false);
  const [evCheckCount, setEvCheckCount] = useState<number | null>(null);

  useEffect(() => {
    getEVCheckCount().then((count) => {
      if (count > 0) setEvCheckCount(count);
    });
  }, []);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<EVCheckResponse | null>(null);

  // AI report preview state
  const [aiReport, setAiReport] = useState<string | null>(null);
  const [reportLoading, setReportLoading] = useState(false);
  const [reportError, setReportError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setResult(null);
    setAiReport(null);
    setReportError(null);

    const cleaned = registration.replace(/[^a-zA-Z0-9]/g, "").toUpperCase();
    if (cleaned.length < 2 || cleaned.length > 8) {
      setError("Please enter a valid UK registration number");
      return;
    }

    setLoading(true);
    try {
      const data = await runEVCheck(cleaned);
      setResult(data);
      getEVCheckCount().then((c) => { if (c > 0) setEvCheckCount(c); });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateReport = async () => {
    if (!result) return;
    setReportLoading(true);
    setReportError(null);

    try {
      const data = await runEVPreview(result.registration);
      setAiReport(data.ai_report);
    } catch (err) {
      setReportError(
        err instanceof Error ? err.message : "Report generation failed"
      );
    } finally {
      setReportLoading(false);
    }
  };

  return (
    <>
      {/* Hero + Search */}
      <section id="search" className="py-12 sm:py-16">
        <div className="mx-auto max-w-5xl px-4">
          <div className="text-center mb-8">
            <div className="inline-flex items-center gap-2 mb-4 px-4 py-1.5 bg-emerald-50 border border-emerald-200 rounded-full">
              <svg className="w-4 h-4 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
              </svg>
              <span className="text-sm font-medium text-emerald-700">EV Health Check</span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-3">
              The UK&apos;s most <span className="text-emerald-600">complete EV check</span>
            </h1>
            <p className="text-slate-500 text-lg max-w-2xl mx-auto">
              Battery health, real-world range, charging costs, MOT history, mileage verification, and more.
              Everything you need before buying a used electric car.
            </p>
          </div>

          {/* Search form */}
          <form onSubmit={handleSubmit} className="max-w-lg mx-auto">
            <div className="flex gap-2">
              <div className="flex-1 relative">
                <div className="absolute left-3 top-1/2 -translate-y-1/2 flex items-center gap-1.5">
                  <div className="w-6 h-4 bg-blue-700 rounded-sm flex items-center justify-center">
                    <span className="text-[8px] font-bold text-white">GB</span>
                  </div>
                </div>
                <input
                  type="text"
                  value={registration}
                  onChange={(e) => setRegistration(e.target.value.toUpperCase())}
                  placeholder="ENTER REG"
                  maxLength={8}
                  className="w-full pl-12 pr-4 py-3.5 text-lg font-mono font-bold tracking-widest text-slate-900 bg-yellow-50 border-2 border-slate-300 rounded-lg focus:outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200 placeholder:text-slate-300 placeholder:font-normal placeholder:tracking-normal"
                />
              </div>
              <button
                type="submit"
                disabled={loading}
                className="px-6 py-3.5 bg-emerald-600 text-white font-semibold rounded-lg hover:bg-emerald-700 disabled:bg-emerald-300 transition-colors flex items-center gap-2"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24" fill="none">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
                    </svg>
                    Checking...
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
                    </svg>
                    Check EV
                  </>
                )}
              </button>
            </div>
            <p className="text-xs text-slate-400 mt-2 text-center">
              Works with all UK-registered electric and plug-in hybrid vehicles
            </p>
          </form>

          <div className="flex items-center justify-center gap-3 mt-4 flex-wrap">
            {evCheckCount !== null && evCheckCount > 0 && (
              <span className="flex items-center gap-1.5 bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-medium px-3 py-1.5 rounded-full">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
                </span>
                {evCheckCount.toLocaleString()} EVs checked
              </span>
            )}
            <a
              href="/"
              className="inline-flex items-center gap-1.5 bg-blue-600 text-white text-xs font-semibold px-3.5 py-1.5 rounded-full hover:bg-blue-700 transition-colors"
            >
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
              </svg>
              Not an EV? Run a free car check instead
            </a>
          </div>

          {/* EV Trust Bar */}
          <div className="flex flex-wrap justify-center gap-6 sm:gap-8 mt-6">
            <div className="flex items-center gap-2 text-slate-500">
              <span className="text-emerald-600">
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
                </svg>
              </span>
              <span className="text-sm font-medium">Official Gov Data</span>
            </div>
            <div className="flex items-center gap-2 text-slate-500">
              <span className="text-emerald-600">
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M21 10.5h.375c.621 0 1.125.504 1.125 1.125v2.25c0 .621-.504 1.125-1.125 1.125H21M4.5 10.5H18V15H4.5v-4.5zM3.75 18h15A2.25 2.25 0 0021 15.75v-6a2.25 2.25 0 00-2.25-2.25h-15A2.25 2.25 0 001.5 9.75v6A2.25 2.25 0 003.75 18z" />
                </svg>
              </span>
              <span className="text-sm font-medium">Battery Analysis</span>
            </div>
            <div className="flex items-center gap-2 text-slate-500">
              <span className="text-emerald-600">
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 6.75V15m6-6v8.25m.503 3.498l4.875-2.437c.381-.19.622-.58.622-1.006V4.82c0-.836-.88-1.38-1.628-1.006l-3.869 1.934c-.317.159-.69.159-1.006 0L9.503 3.252a1.125 1.125 0 00-1.006 0L3.622 5.689C3.24 5.88 3 6.27 3 6.695V19.18c0 .836.88 1.38 1.628 1.006l3.869-1.934c.317-.159.69-.159 1.006 0l4.994 2.497c.317.158.69.158 1.006 0z" />
                </svg>
              </span>
              <span className="text-sm font-medium">Range Verification</span>
            </div>
            <div className="flex items-center gap-2 text-slate-500">
              <span className="text-emerald-600">
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
                </svg>
              </span>
              <span className="text-sm font-medium">Instant Results</span>
            </div>
          </div>

          {error && (
            <div className="max-w-lg mx-auto mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
              {error}
            </div>
          )}
        </div>
      </section>

      {/* Results */}
      {result && (
        <section className="pb-12">
          <div className="mx-auto max-w-5xl px-4">
            {!result.is_electric ? (
              /* Non-EV redirect */
              <div className="max-w-lg mx-auto text-center p-8 bg-amber-50 border border-amber-200 rounded-xl">
                <div className="inline-flex items-center justify-center w-14 h-14 rounded-full bg-amber-100 mb-4">
                  <svg className="w-7 h-7 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
                  </svg>
                </div>
                <h3 className="text-lg font-bold text-slate-900 mb-2">
                  This isn&apos;t an electric vehicle
                </h3>
                <p className="text-sm text-slate-600 mb-4">
                  {result.vehicle?.make} {result.vehicle?.year_of_manufacture} — {result.vehicle?.fuel_type?.toLowerCase() || "Unknown fuel type"}.
                  Our EV Health Check is designed for electric and plug-in hybrid vehicles.
                </p>
                <a
                  href="/"
                  className="inline-flex items-center gap-2 px-6 py-2.5 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors text-sm"
                >
                  Run a free car check instead
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
                  </svg>
                </a>
              </div>
            ) : (
              <>
                <EVCheckResult result={result} />

                {/* AI Report (if generated) */}
                {aiReport && (
                  <div className="mt-6">
                    <EVAIReport report={aiReport} registration={result.registration} />
                  </div>
                )}

                {/* Generate Report CTA (shown before report is generated) */}
                {!aiReport && (
                  <div className="mt-6 text-center">
                    <button
                      onClick={handleGenerateReport}
                      disabled={reportLoading}
                      className="inline-flex items-center gap-2 px-8 py-3.5 bg-emerald-600 text-white font-semibold rounded-xl hover:bg-emerald-700 disabled:bg-emerald-300 transition-colors text-sm shadow-lg shadow-emerald-200"
                    >
                      {reportLoading ? (
                        <>
                          <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24" fill="none">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
                          </svg>
                          Generating AI Report...
                        </>
                      ) : (
                        <>
                          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                          </svg>
                          Generate Free AI Report
                        </>
                      )}
                    </button>
                    <p className="text-xs text-slate-400 mt-2">
                      Free expert analysis of this EV using official DVLA &amp; MOT data
                    </p>
                    {reportError && (
                      <p className="mt-2 text-sm text-red-600">{reportError}</p>
                    )}
                  </div>
                )}

                {/* Upsell — always shown after results, below report if generated */}
                <EVUpsellSection registration={result.registration} />

                {/* Cross-sell: full vehicle history */}
                <div className="mt-6 text-center">
                  <a
                    href="/"
                    className="inline-flex items-center gap-2 text-sm text-slate-500 hover:text-blue-600 transition-colors"
                  >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
                    </svg>
                    Need a full vehicle history check? Finance, stolen, write-off checks from £9.99
                  </a>
                </div>
              </>
            )}
          </div>
        </section>
      )}
    </>
  );
}
