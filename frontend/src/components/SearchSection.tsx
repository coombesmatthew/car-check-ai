"use client";

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { runFreeCheck, getCheckCount, FreeCheckResponse } from "@/lib/api";
import TrustBar from "@/components/ui/TrustBar";
import CheckResult from "@/components/CheckResult";
import UpsellSection from "@/components/UpsellSection";

const EV_FUEL_TYPES = ["ELECTRICITY", "ELECTRIC"];

export default function SearchSection({ onCheckComplete }: { onCheckComplete?: (hasResult: boolean) => void }) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialReg = searchParams?.get("reg") || "";
  const utmSource = searchParams?.get("utm_source");
  const utmContent = searchParams?.get("utm_content");

  const [registration, setRegistration] = useState(initialReg);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<FreeCheckResponse | null>(null);

  // BASIC tier upsell state
  const [showUpsell, setShowUpsell] = useState(false);
  const [reportError, setReportError] = useState<string | null>(null);
  const [checkCount, setCheckCount] = useState<number | null>(null);

  useEffect(() => {
    getCheckCount().then((count) => {
      if (count > 0) setCheckCount(count);
    });
  }, []);

  // Stash source attribution from URL params (TTL: 1 hour) so it survives
  // through the free check, upsell, and checkout flow even after navigation.
  useEffect(() => {
    if (utmSource) {
      const data = {
        source: utmSource,
        source_slug: utmContent || null,
        expires_at: Date.now() + 60 * 60 * 1000,
      };
      try {
        sessionStorage.setItem("vericar_source", JSON.stringify(data));
      } catch {
        // sessionStorage unavailable (Safari private mode etc.) — non-fatal
      }
    }
  }, [utmSource, utmContent]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setResult(null);
    setShowUpsell(false);
    onCheckComplete?.(false);

    const cleaned = registration.replace(/[^a-zA-Z0-9]/g, "").toUpperCase();
    if (cleaned.length < 2 || cleaned.length > 8) {
      setError("Please enter a valid UK registration number");
      return;
    }

    setLoading(true);
    try {
      const data = await runFreeCheck(cleaned);
      const fuel = data.vehicle?.fuel_type?.toUpperCase() ?? "";
      if (EV_FUEL_TYPES.includes(fuel)) {
        router.replace(`/ev?reg=${cleaned}`);
        return;
      }
      setResult(data);
      onCheckComplete?.(true);
      getCheckCount().then((c) => { if (c > 0) setCheckCount(c); });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
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
              <div className="flex flex-col sm:flex-row gap-2">
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
                  className="w-full sm:w-auto px-6 py-3.5 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:bg-slate-300 disabled:cursor-not-allowed transition-colors"
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
            Buying an EV? Try our EV Health Check
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

      {/* Upsell CTA - shown after free check */}
      {result && (
        <section className="mx-auto max-w-5xl px-4 pb-16 w-full">
          <UpsellSection
            registration={result.registration}
            showUpsell={showUpsell}
            setShowUpsell={setShowUpsell}
            reportError={reportError}
          />
        </section>
      )}
    </>
  );
}
