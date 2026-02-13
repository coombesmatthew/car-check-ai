"use client";

import { useState } from "react";
import { runFreeCheck, runBasicCheckPreview, FreeCheckResponse } from "@/lib/api";
import CheckResult from "@/components/CheckResult";
import AIReport from "@/components/AIReport";

export default function Home() {
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
    <main className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      {/* Header */}
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-5xl px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-blue-600 flex items-center justify-center">
              <span className="text-white font-bold text-sm">CC</span>
            </div>
            <span className="font-semibold text-lg text-slate-900">
              Car Check AI
            </span>
          </div>
          <nav className="hidden sm:flex items-center gap-6 text-sm text-slate-600">
            <span>Free Check</span>
            <span className="text-blue-600 font-medium">
              Full Report &mdash; £3.99
            </span>
          </nav>
        </div>
      </header>

      {/* Hero + Search */}
      <section className="mx-auto max-w-5xl px-4 pt-12 pb-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-3">
            Check any UK vehicle instantly
          </h1>
          <p className="text-slate-500 text-lg max-w-xl mx-auto">
            Free MOT history, tax status, mileage clocking detection, ULEZ
            compliance, and condition scoring. Powered by DVLA &amp; DVSA data.
          </p>
        </div>

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
                className="w-full pl-14 pr-4 py-3 text-lg font-mono font-bold tracking-wider border-2 border-slate-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none bg-yellow-50 text-slate-900 placeholder:text-slate-400 placeholder:font-normal"
                maxLength={8}
                autoFocus
              />
            </div>
            <button
              type="submit"
              disabled={loading || registration.length < 2}
              className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:bg-slate-300 disabled:cursor-not-allowed transition-colors"
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

        <div className="flex justify-center gap-6 mt-6 text-xs text-slate-400">
          <span>DVLA Vehicle Data</span>
          <span>DVSA MOT History</span>
          <span>Mileage Analysis</span>
          <span>ULEZ Check</span>
        </div>
      </section>

      {/* Results */}
      {result && (
        <section className="mx-auto max-w-5xl px-4 pb-8">
          <CheckResult data={result} />
        </section>
      )}

      {/* AI Report (if generated) */}
      {aiReport && result && (
        <section className="mx-auto max-w-5xl px-4 pb-8">
          <AIReport report={aiReport} registration={result.registration} />
        </section>
      )}

      {/* Upsell CTA - shown after free check, before report */}
      {result && !aiReport && (
        <section className="mx-auto max-w-5xl px-4 pb-16">
          {!showUpsell ? (
            /* Collapsed upsell card */
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-6">
              <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                <div className="flex-1">
                  <h3 className="font-semibold text-blue-900 text-lg mb-1">
                    Want the full picture? Get an AI Buyer&apos;s Report
                  </h3>
                  <p className="text-sm text-blue-700 mb-3">
                    Our AI analyses all the data above and writes you a
                    personalised buyer&apos;s report with a clear
                    buy/negotiate/avoid recommendation.
                  </p>
                  <div className="flex flex-wrap gap-3 text-xs">
                    <span className="bg-white border border-blue-200 rounded-full px-3 py-1 text-blue-700">
                      AI Risk Assessment
                    </span>
                    <span className="bg-white border border-blue-200 rounded-full px-3 py-1 text-blue-700">
                      Buy/Avoid Verdict
                    </span>
                    <span className="bg-white border border-blue-200 rounded-full px-3 py-1 text-blue-700">
                      Negotiation Points
                    </span>
                    <span className="bg-white border border-blue-200 rounded-full px-3 py-1 text-blue-700">
                      PDF Report Emailed
                    </span>
                  </div>
                </div>
                <div className="flex flex-col items-center gap-2">
                  <div className="text-center">
                    <span className="text-3xl font-bold text-blue-900">
                      £3.99
                    </span>
                    <span className="text-sm text-blue-600 block">
                      one-time
                    </span>
                  </div>
                  <button
                    onClick={() => setShowUpsell(true)}
                    className="px-6 py-2.5 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors text-sm whitespace-nowrap"
                  >
                    Get Full Report
                  </button>
                </div>
              </div>
            </div>
          ) : (
            /* Expanded upsell form */
            <div className="bg-white border border-blue-200 rounded-xl overflow-hidden">
              <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-4">
                <h3 className="text-white font-semibold text-lg">
                  Generate AI Buyer&apos;s Report &mdash; £3.99
                </h3>
                <p className="text-blue-200 text-sm">
                  Optional: add the listing details for a more personalised
                  report
                </p>
              </div>
              <div className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    Listing URL (optional)
                  </label>
                  <input
                    type="url"
                    value={listingUrl}
                    onChange={(e) => setListingUrl(e.target.value)}
                    placeholder="https://autotrader.co.uk/listing/..."
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    Listed Price (optional)
                  </label>
                  <div className="relative">
                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
                      £
                    </span>
                    <input
                      type="number"
                      value={listingPrice}
                      onChange={(e) => setListingPrice(e.target.value)}
                      placeholder="8,995"
                      className="w-full pl-7 pr-3 py-2 border border-slate-300 rounded-lg text-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none"
                    />
                  </div>
                </div>

                {/* Payment placeholder - will be Stripe Elements */}
                <div className="border-2 border-dashed border-slate-200 rounded-lg p-4 bg-slate-50">
                  <p className="text-sm text-slate-500 text-center">
                    Payment form will appear here (Stripe Elements)
                  </p>
                  <p className="text-xs text-slate-400 text-center mt-1">
                    Demo mode: click below to generate report without payment
                  </p>
                </div>

                {reportError && (
                  <p className="text-red-600 text-sm">{reportError}</p>
                )}

                <div className="flex gap-3">
                  <button
                    onClick={handleGenerateReport}
                    disabled={reportLoading}
                    className="flex-1 px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:bg-blue-400 transition-colors"
                  >
                    {reportLoading ? (
                      <span className="flex items-center justify-center gap-2">
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
                        Generating Report...
                      </span>
                    ) : (
                      "Generate Report (Demo)"
                    )}
                  </button>
                  <button
                    onClick={() => setShowUpsell(false)}
                    className="px-4 py-3 border border-slate-300 text-slate-600 rounded-lg hover:bg-slate-50 transition-colors text-sm"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          )}
        </section>
      )}

      {/* Footer */}
      <footer className="border-t border-slate-200 mt-auto">
        <div className="mx-auto max-w-5xl px-4 py-6 text-center text-xs text-slate-400">
          Car Check AI uses official UK government data sources. Not affiliated
          with DVLA or DVSA.
        </div>
      </footer>
    </main>
  );
}
