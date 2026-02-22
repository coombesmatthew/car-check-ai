"use client";

import { useState } from "react";
import { createEVCheckout } from "@/lib/api";

interface Props {
  registration: string;
}

export default function EVUpsellSection({ registration }: Props) {
  const [email, setEmail] = useState("");
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
      const { checkout_url } = await createEVCheckout(registration, email);
      window.location.href = checkout_url;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Checkout failed");
      setLoading(false);
    }
  };

  return (
    <div id="unlock" className="mt-8 bg-gradient-to-br from-emerald-50 to-teal-50 border border-emerald-200 rounded-xl p-6 sm:p-8">
      <div className="max-w-lg mx-auto text-center">
        <div className="inline-flex items-center gap-2 mb-3 px-3 py-1 bg-emerald-100 rounded-full">
          <svg className="w-4 h-4 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
          </svg>
          <span className="text-sm font-semibold text-emerald-700">Full EV Health Report</span>
        </div>

        <h3 className="text-xl font-bold text-slate-900 mb-2">
          Unlock the complete battery analysis
        </h3>
        <p className="text-sm text-slate-600 mb-6">
          Battery health score, real-world range estimate, charging cost comparison,
          lifespan prediction, and AI expert verdict — delivered as a PDF to your email.
        </p>

        <div className="flex flex-wrap justify-center gap-3 mb-6 text-xs">
          {["Battery Health Score", "Range Reality Check", "Charging Costs", "AI Verdict", "PDF Report"].map((item) => (
            <span key={item} className="inline-flex items-center gap-1 px-2.5 py-1 bg-white border border-emerald-200 rounded-full text-slate-700">
              <svg className="w-3 h-3 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
              </svg>
              {item}
            </span>
          ))}
        </div>

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
            className="px-6 py-3 bg-emerald-600 text-white font-semibold rounded-lg hover:bg-emerald-700 disabled:bg-emerald-300 transition-colors text-sm whitespace-nowrap"
          >
            {loading ? "Processing..." : "Get Report — £7.99"}
          </button>
        </form>

        {error && (
          <p className="mt-3 text-sm text-red-600">{error}</p>
        )}

        <p className="mt-3 text-xs text-slate-400">
          Secure payment via Stripe. Report emailed within 60 seconds.
        </p>
      </div>
    </div>
  );
}
