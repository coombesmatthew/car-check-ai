"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import CheckResult from "@/components/CheckResult";
import EVCheckResult from "@/components/ev/EVCheckResult";
import { getReportData, ReportDataResponse } from "@/lib/api";

function ReportContent() {
  const searchParams = useSearchParams();
  const sessionId = searchParams.get("session_id");

  const [status, setStatus] = useState<"loading" | "ready" | "pending" | "unpaid" | "error">("loading");
  const [data, setData] = useState<ReportDataResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId) {
      setStatus("error");
      setError("No report session in the URL. Open the link from your email or from the payment success page.");
      return;
    }

    let cancelled = false;

    const load = async () => {
      try {
        const res = await getReportData(sessionId);
        if (cancelled) return;
        setData(res);
        setStatus("ready");
      } catch (err) {
        if (cancelled) return;
        const msg = err instanceof Error ? err.message : "Failed to load report";
        if (/Payment not completed/i.test(msg)) {
          setStatus("unpaid");
        } else if (/Report not found/i.test(msg)) {
          setStatus("pending");
        } else {
          setStatus("error");
          setError(msg);
        }
      }
    };

    load();
    return () => {
      cancelled = true;
    };
  }, [sessionId]);

  if (status === "loading") {
    return (
      <div className="text-center py-20">
        <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-blue-100 mb-4">
          <svg className="animate-spin h-6 w-6 text-blue-600" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
          </svg>
        </div>
        <p className="text-slate-500">Loading your report…</p>
      </div>
    );
  }

  if (status === "pending") {
    return (
      <div className="text-center py-20">
        <h2 className="text-2xl font-bold text-slate-900 mb-2">Report still generating</h2>
        <p className="text-slate-500 mb-6 max-w-md mx-auto">
          Your payment is confirmed but the report is still being built. It usually takes 30–90 seconds. Try reloading this page in a moment.
        </p>
        <button onClick={() => window.location.reload()} className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors">
          Reload
        </button>
      </div>
    );
  }

  if (status === "unpaid") {
    return (
      <div className="text-center py-20">
        <h2 className="text-2xl font-bold text-slate-900 mb-2">Payment not completed</h2>
        <p className="text-slate-500 mb-6">This session hasn&apos;t been paid yet.</p>
        <a href="/" className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors">
          Back to Home
        </a>
      </div>
    );
  }

  if (status === "error" || !data) {
    return (
      <div className="text-center py-20">
        <h2 className="text-2xl font-bold text-slate-900 mb-2">We couldn&apos;t load this report</h2>
        <p className="text-slate-500 mb-2">{error || "Unknown error"}</p>
        <p className="text-sm text-slate-400 mb-6">If you paid and think this is a mistake, reply to your report email — we&apos;ll fix it.</p>
        <a href="/" className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors">
          Back to Home
        </a>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-start justify-between gap-4 mb-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Full Vehicle Report</h1>
          <p className="text-xs text-slate-400 mt-1">Ref: {data.report_ref}</p>
        </div>
      </div>

      <div className="mb-4 flex items-start gap-3 bg-emerald-50 border border-emerald-200 rounded-lg px-4 py-3">
        <svg className="w-5 h-5 text-emerald-600 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
        <p className="text-sm text-emerald-800">
          We&apos;ve also emailed a copy of this report. Can&apos;t find it? Check your spam or junk folder.
        </p>
      </div>

      {data.is_ev ? (
        <EVCheckResult result={data.check_data} reportMode />
      ) : (
        <CheckResult data={data.check_data} reportMode />
      )}
    </div>
  );
}

export default function ReportPage() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-50 to-white flex flex-col">
      <Header />
      <div className="mx-auto max-w-5xl px-4 py-8 w-full flex-1">
        <Suspense fallback={<div className="text-center py-20 text-slate-500">Loading…</div>}>
          <ReportContent />
        </Suspense>
      </div>
      <Footer />
    </main>
  );
}
