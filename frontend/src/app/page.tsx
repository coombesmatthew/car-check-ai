"use client";

import { useState } from "react";
import { runFreeCheck, FreeCheckResponse } from "@/lib/api";
import CheckResult from "@/components/CheckResult";

export default function Home() {
  const [registration, setRegistration] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<FreeCheckResponse | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setResult(null);

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
            <span className="text-slate-300">Full Report - Coming Soon</span>
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
        <section className="mx-auto max-w-5xl px-4 pb-16">
          <CheckResult data={result} />
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
