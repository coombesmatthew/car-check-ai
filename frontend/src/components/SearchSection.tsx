"use client";

import { useState, useEffect } from "react";
import { runFreeCheck, runBasicCheckPreview, getCheckCount, FreeCheckResponse } from "@/lib/api";
import TrustBar from "@/components/ui/TrustBar";
import CheckResult from "@/components/CheckResult";
import AIReport from "@/components/AIReport";
import UpsellSection from "@/components/UpsellSection";

export default function SearchSection() {
  const [registration, setRegistration] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<FreeCheckResponse | null>(null);

  // BASIC tier upsell state
  const [showUpsell, setShowUpsell] = useState(false);
  const [listingUrl, setListingUrl] = useState("");
  const [listingPrice, setListingPrice] = useState("");
  const [aiReport, setAiReport] = useState<string | null>(null);
  const [reportLoading, setReportLoading] = useState(false);
  const [reportError, setReportError] = useState<string | null>(null);
  const [checkCount, setCheckCount] = useState<number | null>(null);

  useEffect(() => {
    getCheckCount().then((count) => {
      if (count > 0) setCheckCount(count);
    });
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setResult(null);
    setAiReport(null);
    setShowUpsell(false);

    const cleaned = registration.replace(/[^a-zA-Z0-9]/g, "").toUpperCase();
    if (cleaned.length < 2 || cleaned.length > 8) {
      setError("Please enter a valid UK registration number");
      return;
    }

    setLoading(true);
    try {
      const data = await runFreeCheck(cleaned);
      setResult(data);
      // Refresh counter after successful check
      getCheckCount().then((c) => { if (c > 0) setCheckCount(c); });
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
      const priceInPence = listingPrice
        ? Math.round(parseFloat(listingPrice) * 100)
        : undefined;

      const data = await runBasicCheckPreview(
        result.registration,
        listingUrl || undefined,
        priceInPence
      );
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
      <section id="search" className="mx-auto max-w-5xl px-4 pt-12 pb-8 w-full">
        <div className="text-center mb-8">
          <h1 className="text-3xl sm:text-5xl font-bold text-slate-900 mb-4 leading-tight">
            Check any car in seconds.
          </h1>
          <p className="text-slate-500 text-lg max-w-2xl mx-auto leading-relaxed">
            Free instant vehicle check using official DVLA &amp; DVSA data.
            Mileage verification, MOT history, tax status, and ULEZ compliance in seconds.
          </p>
        </div>

        {/* Registration search form */}
        <form onSubmit={handleSubmit} className="max-w-md mx-auto">
              <div className="flex gap-2">
                <div className="relative flex-1">
                  <div className="absolute left-3 top-1/2 -translate-y-1/2 bg-blue-600 text-white text-xs font-bold px-1.5 py-0.5 rounded">
                    GB
                  </div>
                  <input
                    type="text"
                    value={registration}
                    onChange={(e) =>
                      setRegistration(e.target.value.toUpperCase().slice(0, 8))
                    }
                    placeholder="AB12 CDE"
                    className="w-full pl-14 pr-4 py-3.5 text-lg font-mono font-bold tracking-wider border-2 border-slate-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none bg-yellow-50 text-slate-900 placeholder:text-slate-400 placeholder:font-normal"
                    maxLength={8}
                    autoFocus
                  />
                </div>
                <button
                  type="submit"
                  disabled={loading || registration.length < 2}
                  className="px-6 py-3.5 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:bg-slate-300 disabled:cursor-not-allowed transition-colors"
                >
                  {loading ? (
                    <span className="flex items-center gap-2">
                      <svg
                        className="animate-spin h-5 w-5"
                        viewBox="0 0 24 24"
                        fill="none"
                      >
                        <circle
                          className="opacity-25"
                          cx="12"
                          cy="12"
                          r="10"
                          stroke="currentColor"
                          strokeWidth="4"
                        />
                        <path
                          className="opacity-75"
                          fill="currentColor"
                          d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
                        />
                      </svg>
                      Checking
                    </span>
                  ) : (
                    "Check"
                  )}
                </button>
              </div>
              {error && (
                <p className="mt-3 text-red-600 text-sm text-center">{error}</p>
              )}
        </form>

        <div className="flex items-center justify-center gap-3 mt-4 flex-wrap">
          {checkCount !== null && checkCount > 0 && (
            <span className="flex items-center gap-1.5 bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-medium px-3 py-1.5 rounded-full">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
              </span>
              {checkCount.toLocaleString()} vehicles checked
            </span>
          )}
          <a
            href="/ev"
            className="inline-flex items-center gap-1.5 bg-emerald-600 text-white text-xs font-semibold px-3.5 py-1.5 rounded-full hover:bg-emerald-700 transition-colors"
          >
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
            </svg>
            Buying an EV? Try our Full EV Check
          </a>
        </div>

        <div className="mt-6">
          <TrustBar />
        </div>
      </section>

      {/* Results */}
      {result && (
        <section className="mx-auto max-w-5xl px-4 pb-8 w-full">
          <CheckResult data={result} />
        </section>
      )}

      {/* EV cross-sell — shown when the checked vehicle is electric */}
      {result && result.vehicle?.fuel_type?.toUpperCase() === "ELECTRICITY" && (
        <section className="mx-auto max-w-5xl px-4 pb-6 w-full">
          <a href={`/ev?reg=${result.registration}`} className="block bg-gradient-to-r from-emerald-600 to-emerald-700 rounded-xl p-5 text-white hover:from-emerald-700 hover:to-emerald-800 transition-all group">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="bg-white/20 rounded-lg p-2">
                  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
                  </svg>
                </div>
                <div>
                  <p className="font-bold text-lg">This is an electric vehicle!</p>
                  <p className="text-emerald-100 text-sm">Get battery health, real-world range, and charging costs with our dedicated EV Health Check.</p>
                </div>
              </div>
              <svg className="w-5 h-5 text-emerald-200 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
              </svg>
            </div>
          </a>
        </section>
      )}

      {/* AI Report (if generated) */}
      {aiReport && result && (
        <section className="mx-auto max-w-5xl px-4 pb-8 w-full">
          <AIReport report={aiReport} registration={result.registration} />
        </section>
      )}

      {/* Upsell CTA - shown after free check, before report */}
      {result && !aiReport && (
        <section className="mx-auto max-w-5xl px-4 pb-16 w-full">
          <UpsellSection
            registration={result.registration}
            showUpsell={showUpsell}
            setShowUpsell={setShowUpsell}
            listingUrl={listingUrl}
            setListingUrl={setListingUrl}
            listingPrice={listingPrice}
            setListingPrice={setListingPrice}
            reportLoading={reportLoading}
            reportError={reportError}
            onGenerateReport={handleGenerateReport}
          />
        </section>
      )}
    </>
  );
}
