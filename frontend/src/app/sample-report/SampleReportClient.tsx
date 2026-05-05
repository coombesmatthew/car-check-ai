"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import CheckResult from "@/components/CheckResult";
import EVCheckResult from "@/components/ev/EVCheckResult";
import { getSampleReport, ReportDataResponse, SampleVariant } from "@/lib/api";
import { track } from "@/lib/analytics";

type Tab = { id: SampleVariant; label: string; sublabel: string };

const TABS: Tab[] = [
  { id: "risks", label: "BMW 320d", sublabel: "Risks found" },
  { id: "clean", label: "MINI", sublabel: "All clear" },
  { id: "ev", label: "Tesla Model 3", sublabel: "Battery + range" },
];

function isValidVariant(v: string | null): v is SampleVariant {
  return v === "clean" || v === "risks" || v === "ev";
}

function SampleReportContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const variantParam = searchParams.get("variant");
  const variant: SampleVariant = isValidVariant(variantParam) ? variantParam : "risks";

  const [status, setStatus] = useState<"loading" | "ready" | "missing" | "error">("loading");
  const [data, setData] = useState<ReportDataResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setStatus("loading");
    setData(null);
    setError(null);

    getSampleReport(variant)
      .then((res) => {
        if (cancelled) return;
        setData(res);
        setStatus("ready");
        track("sample_report_viewed", { variant });
      })
      .catch((err) => {
        if (cancelled) return;
        const msg = err instanceof Error ? err.message : "Failed to load sample";
        if (/not yet available/i.test(msg)) {
          setStatus("missing");
        } else {
          setStatus("error");
          setError(msg);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [variant]);

  const switchTab = (next: SampleVariant) => {
    if (next === variant) return;
    track("sample_report_tab_clicked", { from: variant, to: next });
    router.push(`/sample-report?variant=${next}`, { scroll: false });
  };

  return (
    <div>
      {/* Sticky banner */}
      <div className="sticky top-0 z-30 -mx-4 px-4 mb-4 py-3 bg-blue-50/95 backdrop-blur supports-[backdrop-filter]:bg-blue-50/80 border-b border-blue-200">
        <div className="flex items-center gap-3 max-w-5xl mx-auto">
          <svg className="w-5 h-5 text-blue-600 flex-shrink-0 hidden sm:block" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-sm text-blue-900 flex-1">
            <span className="hidden sm:inline">This is a sample report. Run a free check on your own car to start.</span>
            <span className="sm:hidden font-semibold">Sample report</span>
          </p>
          <a
            href="/#search"
            className="inline-flex items-center justify-center px-4 py-2 bg-blue-600 text-white text-sm font-semibold rounded-lg hover:bg-blue-700 transition-colors flex-shrink-0"
          >
            Check your car →
          </a>
        </div>
      </div>

      {/* Title */}
      <div className="mb-4">
        <h1 className="text-2xl font-bold text-slate-900">Vehicle Report — Sample</h1>
        <p className="text-sm text-slate-500 mt-1">See exactly what you get for £9.99 — same layout, same data, no signup.</p>
      </div>

      {/* Tabs */}
      <div role="tablist" aria-label="Sample variants" className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-6">
        {TABS.map((t) => {
          const active = t.id === variant;
          return (
            <button
              key={t.id}
              role="tab"
              aria-selected={active}
              onClick={() => switchTab(t.id)}
              className={`text-left rounded-lg px-6 py-5 border-2 transition-colors ${
                active
                  ? "border-blue-600 bg-blue-50"
                  : "border-slate-200 bg-white hover:border-slate-300"
              }`}
            >
              <div className={`font-semibold text-lg ${active ? "text-blue-700" : "text-slate-900"}`}>
                {t.label}
              </div>
              <div className="text-sm text-slate-500 mt-1">{t.sublabel}</div>
            </button>
          );
        })}
      </div>

      {/* Body */}
      {status === "loading" && (
        <div className="text-center py-20">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-blue-100 mb-4">
            <svg className="animate-spin h-6 w-6 text-blue-600" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
            </svg>
          </div>
          <p className="text-slate-500">Loading sample…</p>
        </div>
      )}

      {status === "missing" && (
        <div className="text-center py-16 bg-slate-50 border border-slate-200 rounded-xl">
          <h2 className="text-lg font-semibold text-slate-900 mb-2">This sample is coming soon</h2>
          <p className="text-sm text-slate-500 max-w-md mx-auto">
            We&apos;re finalising this example. Try one of the other tabs in the meantime.
          </p>
        </div>
      )}

      {status === "error" && (
        <div className="text-center py-16">
          <h2 className="text-lg font-semibold text-slate-900 mb-2">Couldn&apos;t load sample</h2>
          <p className="text-sm text-slate-500">{error || "Unknown error"}</p>
        </div>
      )}

      {status === "ready" && data && (
        <>
          {data.is_ev ? (
            <EVCheckResult result={data.check_data} reportMode />
          ) : (
            <CheckResult data={data.check_data} reportMode />
          )}

          {/* Bottom CTA */}
          <div className="mt-8 bg-gradient-to-br from-blue-600 to-purple-600 text-white rounded-xl p-6 text-center">
            <h3 className="text-xl font-bold mb-2">Ready to check your car?</h3>
            <p className="text-sm text-blue-100 mb-4">
              Free MOT &amp; mileage check now. Upgrade to the full report for £9.99 if you want the provenance picture too.
            </p>
            <a
              href="/#search"
              className="inline-flex items-center gap-2 px-6 py-3 bg-white text-blue-700 font-semibold rounded-lg hover:bg-blue-50 transition-colors"
            >
              Start a free check
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
              </svg>
            </a>
          </div>
        </>
      )}
    </div>
  );
}

export default function SampleReportClient() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-50 to-white flex flex-col">
      <Header />
      <div className="mx-auto max-w-5xl px-4 py-8 w-full flex-1">
        <Suspense fallback={<div className="text-center py-20 text-slate-500">Loading…</div>}>
          <SampleReportContent />
        </Suspense>
      </div>
      <Footer />
    </main>
  );
}
