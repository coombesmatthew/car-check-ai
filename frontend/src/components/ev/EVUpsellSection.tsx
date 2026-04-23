"use client";

import { useState } from "react";
import { createEVCheckout } from "@/lib/api";

interface Props {
  registration: string;
}

type Tier = "ev" | "ev_complete";

// EVUpsellSection: two-tier picker (EV Health £8.99 vs EV Complete £13.99),
// direct-to-Stripe. Email is collected by Stripe. Non-EV "Full Report"
// tier removed — EV owners wanting provenance upgrade to EV Complete.
export default function EVUpsellSection({ registration }: Props) {
  const [selectedTier, setSelectedTier] = useState<Tier>("ev");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCheckout = async () => {
    if (loading) return;
    setError(null);
    setLoading(true);
    try {
      const { checkout_url } = await createEVCheckout(registration, null, selectedTier);
      window.location.href = checkout_url;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Checkout failed");
      setLoading(false);
    }
  };

  const tierCopy: Record<Tier, { price: string; label: string; button: string; bg: string; hover: string }> = {
    ev: {
      price: "8.99",
      label: "EV Health Check",
      button: "Unlock EV Health Check — £8.99",
      bg: "bg-emerald-600",
      hover: "hover:bg-emerald-700",
    },
    ev_complete: {
      price: "13.99",
      label: "EV Complete",
      button: "Unlock EV Complete — £13.99",
      bg: "bg-teal-600",
      hover: "hover:bg-teal-700",
    },
  };

  return (
    <div id="unlock" className="mt-8 bg-gradient-to-br from-emerald-50 to-teal-50 border border-emerald-200 rounded-xl p-6 sm:p-8">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-6">
          <div className="inline-flex items-center gap-2 mb-3 px-3 py-1 bg-emerald-100 rounded-full">
            <svg className="w-4 h-4 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
            </svg>
            <span className="text-sm font-semibold text-emerald-700">Unlock Full EV Report</span>
          </div>
          <h3 className="text-xl font-bold text-slate-900 mb-1">Choose your check</h3>
          <p className="text-sm text-slate-500">Delivered as a PDF to your email within 60 seconds</p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-6">
          {/* EV Health */}
          <button
            type="button"
            onClick={() => setSelectedTier("ev")}
            className={`text-left p-4 rounded-xl border-2 transition-all ${
              selectedTier === "ev" ? "border-emerald-600 bg-white shadow-sm" : "border-slate-200 bg-white/50 hover:border-slate-300"
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-semibold text-emerald-600 uppercase tracking-wide">EV Health Check</span>
              <span className="text-xl font-bold text-slate-900">&pound;8.99</span>
            </div>
            <ul className="space-y-1.5">
              {["Battery Health Score", "Real-World Range", "Charging Costs", "Lifespan Prediction", "PDF emailed in 60s"].map((item) => (
                <li key={item} className="flex items-center gap-1.5 text-xs text-slate-600">
                  <svg className="w-3 h-3 text-emerald-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                  </svg>
                  {item}
                </li>
              ))}
            </ul>
          </button>

          {/* EV Complete */}
          <button
            type="button"
            onClick={() => setSelectedTier("ev_complete")}
            className={`text-left p-4 rounded-xl border-2 transition-all relative ${
              selectedTier === "ev_complete" ? "border-teal-600 bg-white shadow-sm" : "border-slate-200 bg-white/50 hover:border-slate-300"
            }`}
          >
            <div className="absolute -top-2.5 right-3">
              <span className="bg-teal-600 text-white text-xs font-semibold px-2 py-0.5 rounded-full">Best Value</span>
            </div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-semibold text-teal-600 uppercase tracking-wide">EV Complete</span>
              <span className="text-xl font-bold text-slate-900">&pound;13.99</span>
            </div>
            <ul className="space-y-1.5">
              {[
                { label: "Everything in EV Health", base: true },
                { label: "Finance & Debt Check" },
                { label: "Stolen Vehicle Check" },
                { label: "Write-off & Salvage History" },
                { label: "Market Valuation" },
                { label: "Plate & Keeper History" },
              ].map((item) => (
                <li key={item.label} className="flex items-center gap-1.5 text-xs text-slate-600">
                  <svg className={`w-3 h-3 flex-shrink-0 ${item.base ? "text-emerald-500" : "text-teal-500"}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                  </svg>
                  <span className={item.base ? "" : "font-medium"}>{item.label}</span>
                </li>
              ))}
            </ul>
          </button>
        </div>

        <div className="flex justify-center">
          <button
            onClick={handleCheckout}
            disabled={loading}
            className={`px-8 py-3 text-white font-semibold rounded-lg disabled:opacity-50 transition-colors text-sm whitespace-nowrap ${tierCopy[selectedTier].bg} ${tierCopy[selectedTier].hover}`}
          >
            {loading ? "Redirecting…" : tierCopy[selectedTier].button}
          </button>
        </div>

        {error && <p className="mt-3 text-sm text-red-600 text-center">{error}</p>}

        <p className="mt-3 text-xs text-slate-400 text-center">Secure payment via Stripe. Report emailed within 60 seconds.</p>
        <p className="mt-2 text-xs text-slate-400 text-center">
          By purchasing, you agree to our{" "}
          <a href="/terms" className="underline hover:text-slate-600">Terms of Service</a> and{" "}
          <a href="/privacy" className="underline hover:text-slate-600">Privacy Policy</a>.
        </p>
      </div>
    </div>
  );
}
