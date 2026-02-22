"use client";

import { useState } from "react";
import { createEVCheckout, createCheckout } from "@/lib/api";

interface Props {
  registration: string;
}

type Tier = "basic" | "ev" | "ev_complete";

export default function EVUpsellSection({ registration }: Props) {
  const [email, setEmail] = useState("");
  const [selectedTier, setSelectedTier] = useState<Tier>("ev");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCheckout = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) {
      setError("Please enter your email");
      return;
    }
    setLoading(true);
    setError(null);

    try {
      const { checkout_url } = selectedTier === "basic"
        ? await createCheckout(registration, email, "basic")
        : await createEVCheckout(registration, email, selectedTier);
      window.location.href = checkout_url;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Checkout failed");
      setLoading(false);
    }
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
          <h3 className="text-xl font-bold text-slate-900 mb-1">
            Choose your report
          </h3>
          <p className="text-sm text-slate-500">Delivered as a PDF to your email within 60 seconds</p>
        </div>

        {/* Tier selection */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-6">
          {/* Full Report */}
          <button
            type="button"
            onClick={() => setSelectedTier("basic")}
            className={`text-left p-4 rounded-xl border-2 transition-all relative ${
              selectedTier === "basic"
                ? "border-blue-600 bg-white shadow-sm"
                : "border-slate-200 bg-white/50 hover:border-slate-300"
            }`}
          >
            <div className="absolute -top-2.5 left-3">
              <span className="bg-blue-600 text-white text-xs font-semibold px-2 py-0.5 rounded-full">Popular</span>
            </div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-semibold text-blue-600 uppercase tracking-wide">Full Report</span>
              <span className="text-xl font-bold text-slate-900">&pound;3.99</span>
            </div>
            <ul className="space-y-1.5">
              {["Everything in Free", "AI Risk Assessment", "Buy/Avoid Verdict", "Negotiation Points", "PDF Report Emailed"].map((item) => (
                <li key={item} className="flex items-center gap-1.5 text-xs text-slate-600">
                  <svg className="w-3 h-3 text-blue-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                  </svg>
                  {item}
                </li>
              ))}
            </ul>
          </button>

          {/* EV Health */}
          <button
            type="button"
            onClick={() => setSelectedTier("ev")}
            className={`text-left p-4 rounded-xl border-2 transition-all ${
              selectedTier === "ev"
                ? "border-emerald-600 bg-white shadow-sm"
                : "border-slate-200 bg-white/50 hover:border-slate-300"
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-semibold text-emerald-600 uppercase tracking-wide">EV Health Check</span>
              <span className="text-xl font-bold text-slate-900">&pound;8.99</span>
            </div>
            <ul className="space-y-1.5">
              {["Battery Health Score", "Real-World Range", "Charging Costs", "Lifespan Prediction", "AI Expert Verdict"].map((item) => (
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
              selectedTier === "ev_complete"
                ? "border-teal-600 bg-white shadow-sm"
                : "border-slate-200 bg-white/50 hover:border-slate-300"
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
              {["Everything in EV Health", "Finance & Debt Check", "Stolen Vehicle Check", "Write-off & Salvage History", "Market Valuation", "Plate & Keeper History"].map((item, i) => (
                <li key={item} className="flex items-center gap-1.5 text-xs text-slate-600">
                  <svg className={`w-3 h-3 flex-shrink-0 ${i === 0 ? "text-emerald-500" : "text-teal-500"}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                  </svg>
                  <span className={i > 0 ? "font-medium" : ""}>{item}</span>
                </li>
              ))}
            </ul>
          </button>
        </div>

        {/* Checkout form */}
        <form onSubmit={handleCheckout} className="flex flex-col sm:flex-row gap-2 max-w-md mx-auto">
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="your@email.com"
            required
            className="flex-1 px-4 py-3 border border-slate-300 rounded-lg text-sm focus:outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200"
          />
          <button
            type="submit"
            disabled={loading}
            className={`px-6 py-3 text-white font-semibold rounded-lg disabled:opacity-50 transition-colors text-sm whitespace-nowrap ${
              selectedTier === "basic"
                ? "bg-blue-600 hover:bg-blue-700"
                : selectedTier === "ev_complete"
                  ? "bg-teal-600 hover:bg-teal-700"
                  : "bg-emerald-600 hover:bg-emerald-700"
            }`}
          >
            {loading
              ? "Processing..."
              : selectedTier === "basic"
                ? "Get Full Report — £3.99"
                : selectedTier === "ev_complete"
                  ? "Get EV Complete — £13.99"
                  : "Get EV Health Check — £8.99"}
          </button>
        </form>

        {error && (
          <p className="mt-3 text-sm text-red-600 text-center">{error}</p>
        )}

        <p className="mt-3 text-xs text-slate-400 text-center">
          Secure payment via Stripe. Report emailed within 60 seconds.
        </p>
        <p className="mt-2 text-xs text-slate-400 text-center">
          By purchasing, you agree to our{" "}
          <a href="/terms" className="underline hover:text-slate-600">Terms of Service</a> and{" "}
          <a href="/privacy" className="underline hover:text-slate-600">Privacy Policy</a>.
        </p>
      </div>
    </div>
  );
}
