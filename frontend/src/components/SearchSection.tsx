"use client";

import { useState } from "react";
import { runFreeCheck, runBasicCheckPreview, FreeCheckResponse } from "@/lib/api";
import TrustBar from "@/components/ui/TrustBar";
import CheckResult from "@/components/CheckResult";
import AIReport from "@/components/AIReport";
import UpsellSection from "@/components/UpsellSection";
import ListingChecker from "@/components/ListingChecker";

type SearchMode = "registration" | "listing";

export default function SearchSection() {
  const [searchMode, setSearchMode] = useState<SearchMode>("registration");
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

        {/* Search mode tabs */}
        <div className="max-w-2xl mx-auto mb-6">
          <div className="flex bg-slate-100 rounded-lg p-1">
            <button
              type="button"
              onClick={() => setSearchMode("registration")}
              className={`flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-md text-sm font-medium transition-all ${
                searchMode === "registration"
                  ? "bg-white text-slate-900 shadow-sm"
                  : "text-slate-500 hover:text-slate-700"
              }`}
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M15 9h3.75M15 12h3.75M15 15h3.75M4.5 19.5h15a2.25 2.25 0 002.25-2.25V6.75A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25v10.5A2.25 2.25 0 004.5 19.5zm6-10.125a1.875 1.875 0 11-3.75 0 1.875 1.875 0 013.75 0zm1.294 6.336a6.721 6.721 0 01-3.17.789 6.721 6.721 0 01-3.168-.789 3.376 3.376 0 016.338 0z" />
              </svg>
              Search by Registration
            </button>
            <button
              type="button"
              onClick={() => setSearchMode("listing")}
              className={`flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-md text-sm font-medium transition-all ${
                searchMode === "listing"
                  ? "bg-white text-slate-900 shadow-sm"
                  : "text-slate-500 hover:text-slate-700"
              }`}
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M13.19 8.688a4.5 4.5 0 011.242 7.244l-4.5 4.5a4.5 4.5 0 01-6.364-6.364l1.757-1.757m9.193-9.193a4.5 4.5 0 00-6.364 0l-4.5 4.5a4.5 4.5 0 001.242 7.244" />
              </svg>
              Check a Listing
            </button>
          </div>
        </div>

        {/* Registration search form */}
        {searchMode === "registration" && (
          <>
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
          </>
        )}

        {/* Listing URL checker */}
        {searchMode === "listing" && (
          <ListingChecker />
        )}

        <div className="mt-8">
          <TrustBar />
        </div>
      </section>

      {/* Results (registration mode only) */}
      {searchMode === "registration" && result && (
        <section className="mx-auto max-w-5xl px-4 pb-8 w-full">
          <CheckResult data={result} />
        </section>
      )}

      {/* AI Report (if generated, registration mode only) */}
      {searchMode === "registration" && aiReport && result && (
        <section className="mx-auto max-w-5xl px-4 pb-8 w-full">
          <AIReport report={aiReport} registration={result.registration} />
        </section>
      )}

      {/* Upsell CTA - shown after free check, before report (registration mode only) */}
      {searchMode === "registration" && result && !aiReport && (
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
