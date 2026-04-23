"use client";

import { useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";
import { triggerReportFulfilment, getReportStatus, FulfilmentResponse } from "@/lib/api";
import Header from "@/components/Header";
import Footer from "@/components/Footer";

// Poll status every 5s for up to 3 minutes, then fall through to the
// "check your email" success state regardless. The webhook finishes the job
// even if the browser leaves. AI generation takes up to 2 minutes so we
// can't block synchronously without hitting the Cloudflare 100s timeout.
const POLL_INTERVAL_MS = 5000;
const POLL_TIMEOUT_MS = 3 * 60 * 1000;

function SuccessContent() {
  const searchParams = useSearchParams();
  const sessionId = searchParams.get("session_id");

  const [status, setStatus] = useState<"loading" | "success" | "pending_email" | "error">("loading");
  const [result, setResult] = useState<FulfilmentResponse | null>(null);
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

    // Fire-and-forget: ensures fulfilment runs even if the Stripe webhook is delayed or not configured.
    triggerReportFulfilment(sessionId).catch(() => {
      /* non-fatal: webhook will also trigger it */
    });

    const poll = async () => {
      if (cancelled) return;
      try {
        const res = await getReportStatus(sessionId);
        if (res.ready) {
          setResult(res.result);
          setStatus("success");
          return;
        }
      } catch {
        // Transient network hiccup — keep polling within the window.
      }

      if (Date.now() - startedAt > POLL_TIMEOUT_MS) {
        // Fulfilment taking longer than usual — show the email fallback.
        // The backend job continues; user will receive the PDF by email.
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
  }, [sessionId]);

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
        <p className="text-slate-500">Payment confirmed. Building your AI buyer&apos;s report — this usually takes 30–90 seconds.</p>
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
          href="/"
          className="inline-block mt-6 px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
        >
          Back to Home
        </a>
      </div>
    );
  }

  // Success!
  const verdictColour = {
    BUY: "text-emerald-600 bg-emerald-50 border-emerald-200",
    NEGOTIATE: "text-amber-600 bg-amber-50 border-amber-200",
    AVOID: "text-red-600 bg-red-50 border-red-200",
  }[result?.verdict || ""] || "text-slate-600 bg-slate-50 border-slate-200";

  return (
    <div className="text-center py-16">
      <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-emerald-100 mb-6">
        <svg className="w-8 h-8 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
        </svg>
      </div>

      <h2 className="text-2xl font-bold text-slate-900 mb-2">Your report is ready!</h2>
      <p className="text-slate-500 mb-8">
        {result?.email_sent
          ? "Check your email — your PDF report has been sent."
          : "Your report has been generated successfully."}
      </p>
      {result?.email_sent && (
        <p className="text-sm text-slate-400">
          Can&apos;t find it? Check your spam or junk folder.
        </p>
      )}

      {/* Report summary card */}
      <div className="max-w-md mx-auto bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm text-left mb-8">
        <div className="bg-slate-50 px-6 py-4 border-b border-slate-200">
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
            <span className="text-slate-500">PDF Size</span>
            <span className="text-slate-700">{result ? Math.round(result.pdf_size_bytes / 1024) : 0} KB</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-slate-500">Email Delivered</span>
            <span className={result?.email_sent ? "text-emerald-600 font-medium" : "text-amber-600"}>
              {result?.email_sent ? "Sent" : "Pending setup"}
            </span>
          </div>
        </div>
      </div>

      <div className="space-y-3">
        <a
          href="/"
          className="inline-block px-8 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
        >
          Check Another Vehicle
        </a>
        <p className="text-xs text-slate-400">
          Report ref: {result?.report_ref}
        </p>
      </div>

      {/* Legal disclaimer */}
      <p className="text-xs text-slate-400 text-center mt-8 max-w-2xl mx-auto">
        This report is for informational purposes only and should not be the sole basis for a purchasing decision. Data sourced from DVLA, DVSA, and third-party providers &mdash; accuracy not guaranteed. We recommend an independent mechanical inspection before purchase. See our{" "}
        <a href="/terms" className="underline hover:text-slate-600">Terms of Service</a>.
      </p>
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
