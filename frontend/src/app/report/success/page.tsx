"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense } from "react";
import { triggerReportFulfilment, getReportStatus } from "@/lib/api";
import Header from "@/components/Header";
import Footer from "@/components/Footer";

const POLL_INTERVAL_MS = 5000;
const POLL_TIMEOUT_MS = 3 * 60 * 1000;

function SuccessContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const sessionId = searchParams.get("session_id");

  const [status, setStatus] = useState<"loading" | "pending_email" | "error">("loading");
  const [error, setError] = useState<string | null>(null);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!sessionId) {
      setStatus("error");
      setError("No payment session found");
      return;
    }

    let cancelled = false;
    const startedAt = Date.now();

    triggerReportFulfilment(sessionId).catch(() => {
      /* non-fatal: webhook also triggers it */
    });

    const poll = async () => {
      if (cancelled) return;
      try {
        const res = await getReportStatus(sessionId);
        if (res.ready) {
          // Skip the intermediate confirmation screen — go straight to the
          // full report view. The /report page reads session_id from the URL.
          router.replace(`/report?session_id=${encodeURIComponent(sessionId)}`);
          return;
        }
      } catch {
        /* transient — keep polling */
      }

      if (Date.now() - startedAt > POLL_TIMEOUT_MS) {
        setStatus("pending_email");
        return;
      }

      timeoutRef.current = setTimeout(poll, POLL_INTERVAL_MS);
    };

    poll();

    return () => {
      cancelled = true;
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, [sessionId, router]);

  if (status === "loading") {
    return (
      <div className="text-center py-20">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-100 mb-6">
          <svg className="animate-spin h-8 w-8 text-blue-600" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
          </svg>
        </div>
        <h2 className="text-2xl font-bold text-slate-900 mb-2">Generating your report...</h2>
        <p className="text-slate-500">Payment confirmed. Building your full vehicle report — this usually takes 30–90 seconds.</p>
        <p className="text-xs text-slate-400 mt-6">You can safely close this tab. We&apos;ll email your PDF when it&apos;s ready.</p>
      </div>
    );
  }

  if (status === "pending_email") {
    return (
      <div className="text-center py-20">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-emerald-100 mb-6">
          <svg className="w-8 h-8 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
        </div>
        <h2 className="text-2xl font-bold text-slate-900 mb-2">Your report is on its way</h2>
        <p className="text-slate-500 mb-2">Payment received. We&apos;re finishing the PDF and will email it within a few minutes.</p>
        <p className="text-sm text-slate-400">Check your inbox (and spam folder) shortly.</p>
        <a
          href="/"
          className="inline-block mt-8 px-8 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
        >
          Check Another Vehicle
        </a>
      </div>
    );
  }

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
        href="/"
        className="inline-block mt-6 px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
      >
        Back to Home
      </a>
    </div>
  );
}

export default function ReportSuccessPage() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-50 to-white flex flex-col">
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
