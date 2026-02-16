"use client";

import { useState } from "react";
import { createCheckout } from "@/lib/api";

interface UpsellSectionProps {
  registration: string;
  showUpsell: boolean;
  setShowUpsell: (show: boolean) => void;
  listingUrl: string;
  setListingUrl: (url: string) => void;
  listingPrice: string;
  setListingPrice: (price: string) => void;
  reportLoading: boolean;
  reportError: string | null;
  onGenerateReport: () => void;
}

export default function UpsellSection({
  registration,
  showUpsell,
  setShowUpsell,
  listingUrl,
  setListingUrl,
  listingPrice,
  setListingPrice,
  reportLoading,
  reportError,
  onGenerateReport,
}: UpsellSectionProps) {
  const [email, setEmail] = useState("");
  const [checkoutLoading, setCheckoutLoading] = useState(false);
  const [checkoutError, setCheckoutError] = useState<string | null>(null);

  const handleCheckout = async () => {
    if (!email) {
      setCheckoutError("Please enter your email address");
      return;
    }
    setCheckoutError(null);
    setCheckoutLoading(true);

    try {
      const priceInPence = listingPrice
        ? Math.round(parseFloat(listingPrice) * 100)
        : undefined;

      const { checkout_url } = await createCheckout(
        registration,
        email,
        listingUrl || undefined,
        priceInPence
      );

      // Redirect to Stripe Checkout
      window.location.href = checkout_url;
    } catch (err) {
      setCheckoutError(
        err instanceof Error ? err.message : "Checkout failed"
      );
      setCheckoutLoading(false);
    }
  };

  if (!showUpsell) {
    return (
      <div id="full-report" className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
        {/* Header */}
        <div className="bg-gradient-to-r from-slate-800 to-slate-900 px-6 py-5">
          <h3 className="text-white font-bold text-xl mb-1">
            You&apos;ve seen the data. Now get the verdict.
          </h3>
          <p className="text-slate-300 text-sm">
            Our AI analyses all the data above and writes a personalised buyer&apos;s report.
          </p>
        </div>

        <div className="p-6">
          {/* Side-by-side comparison */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            {/* Free column */}
            <div className="border border-slate-200 rounded-lg p-4">
              <div className="text-sm font-semibold text-slate-500 mb-3 uppercase tracking-wide">What you got (Free)</div>
              <ul className="space-y-2">
                {["MOT History", "Tax Status", "Mileage Data", "ULEZ Check"].map((item) => (
                  <li key={item} className="flex items-center gap-2 text-sm text-slate-600">
                    <svg className="w-4 h-4 text-emerald-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                    </svg>
                    {item}
                  </li>
                ))}
              </ul>
            </div>

            {/* Basic column */}
            <div className="border-2 border-blue-600 rounded-lg p-4 relative">
              <div className="absolute -top-3 left-4 bg-blue-600 text-white text-xs font-bold px-2.5 py-0.5 rounded-full">
                RECOMMENDED
              </div>
              <div className="text-sm font-semibold text-blue-700 mb-3 uppercase tracking-wide">
                Full Report (&pound;3.99)
              </div>
              <ul className="space-y-2">
                {[
                  "Everything in Free",
                  "AI Risk Assessment",
                  "Buy/Avoid Verdict",
                  "Negotiation Points",
                  "PDF Report Emailed",
                ].map((item, i) => (
                  <li key={item} className="flex items-center gap-2 text-sm text-slate-700">
                    <svg className={`w-4 h-4 flex-shrink-0 ${i === 0 ? "text-emerald-500" : "text-blue-600"}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                    </svg>
                    <span className={i > 0 ? "font-medium" : ""}>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Sample preview - blurred */}
          <div className="relative mb-6 rounded-lg overflow-hidden border border-slate-200">
            <div className="p-4 bg-slate-50">
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">Sample AI Verdict</p>
              <div className="space-y-1.5 select-none" style={{ filter: "blur(3px)" }}>
                <p className="text-sm text-slate-700">This 2018 Ford Fiesta presents as a low-risk purchase. The mileage readings are consistent across all 6 MOT tests with no signs of clocking.</p>
                <p className="text-sm text-slate-700">The vehicle has a strong MOT pass rate of 83% with only minor advisories related to tyre wear. The current tax and MOT status are both valid.</p>
                <p className="text-sm font-semibold text-emerald-700">Verdict: BUY — This vehicle is well-maintained with no red flags.</p>
              </div>
            </div>
            <div className="absolute inset-0 bg-gradient-to-t from-white via-white/80 to-transparent flex items-end justify-center pb-4">
              <span className="text-sm text-slate-500">Unlock the full AI verdict</span>
            </div>
          </div>

          {/* Price + CTA */}
          <div className="text-center">
            <p className="text-slate-500 text-sm mb-3">Less than a coffee. More than a gut feeling.</p>
            <div className="flex items-center justify-center gap-3 mb-4">
              <span className="text-3xl font-bold text-slate-900">&pound;3.99</span>
              <span className="text-sm text-slate-400">one-time payment</span>
            </div>
            <button
              onClick={() => setShowUpsell(true)}
              className="px-8 py-3 bg-emerald-600 text-white font-semibold rounded-lg hover:bg-emerald-700 transition-colors text-base shadow-sm"
            >
              Get Your Buyer&apos;s Report &mdash; &pound;3.99
            </button>
            <p className="text-xs text-slate-400 mt-3">
              Powered by Claude AI &middot; PDF sent to your email &middot; Money-back guarantee
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Expanded form
  return (
    <div id="full-report" className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
      <div className="bg-gradient-to-r from-slate-800 to-slate-900 px-6 py-4">
        <h3 className="text-white font-semibold text-lg">
          Generate AI Buyer&apos;s Report &mdash; &pound;3.99
        </h3>
        <p className="text-slate-300 text-sm">
          Enter your email and optionally add listing details for a personalised report
        </p>
      </div>
      <div className="p-6 space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Email address <span className="text-red-500">*</span>
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none"
            required
          />
          <p className="text-xs text-slate-400 mt-1">Your PDF report will be sent here</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Listing URL (optional)
          </label>
          <input
            type="url"
            value={listingUrl}
            onChange={(e) => setListingUrl(e.target.value)}
            placeholder="https://autotrader.co.uk/listing/..."
            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Listed Price (optional)
          </label>
          <div className="relative">
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
              &pound;
            </span>
            <input
              type="number"
              value={listingPrice}
              onChange={(e) => setListingPrice(e.target.value)}
              placeholder="8,995"
              className="w-full pl-7 pr-3 py-2 border border-slate-300 rounded-lg text-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none"
            />
          </div>
        </div>

        {/* Stripe checkout info */}
        <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <svg className="w-5 h-5 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
            </svg>
            <span className="text-sm font-medium text-slate-600">Secure payment via Stripe</span>
          </div>
          <p className="text-xs text-slate-400">
            You&apos;ll be redirected to Stripe&apos;s secure checkout page. After payment, your PDF report will be generated and emailed to you.
          </p>
        </div>

        {(checkoutError || reportError) && (
          <p className="text-red-600 text-sm">{checkoutError || reportError}</p>
        )}

        <div className="flex gap-3">
          <button
            onClick={handleCheckout}
            disabled={checkoutLoading || !email}
            className="flex-1 px-6 py-3 bg-emerald-600 text-white font-semibold rounded-lg hover:bg-emerald-700 disabled:bg-emerald-400 disabled:cursor-not-allowed transition-colors"
          >
            {checkoutLoading ? (
              <span className="flex items-center justify-center gap-2">
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
                Redirecting to checkout...
              </span>
            ) : (
              "Pay £3.99 — Secure Checkout"
            )}
          </button>
          <button
            onClick={() => setShowUpsell(false)}
            className="px-4 py-3 border border-slate-300 text-slate-600 rounded-lg hover:bg-slate-50 transition-colors text-sm"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
