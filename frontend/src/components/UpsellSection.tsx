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

const CheckIcon = ({ className = "w-4 h-4 text-emerald-500" }: { className?: string }) => (
  <svg className={`${className} flex-shrink-0`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
  </svg>
);

const LockIcon = () => (
  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
  </svg>
);

const Spinner = () => (
  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24" fill="none">
    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
  </svg>
);

/* Sample report content for the preview modal */
const sampleReports = {
  lowRisk: {
    label: "Low Risk Example",
    verdict: "BUY",
    verdictColor: "text-emerald-700",
    verdictBg: "bg-emerald-50 border-emerald-200",
    content: [
      { heading: "Vehicle Summary", text: "This 2019 Volkswagen Golf 1.5 TSI presents as a well-maintained vehicle with consistent ownership history. The mileage of 42,318 miles is below average for its age." },
      { heading: "Condition Assessment", text: "MOT pass rate of 100% across 4 tests with only minor advisories (tyre wear, brake pad wear). No failures or dangerous items recorded. Condition score: 87/100." },
      { heading: "Mileage Verification", text: "All mileage readings are consistent and show steady annual usage of approximately 10,500 miles per year. No signs of clocking detected." },
      { heading: "Risk Assessment", text: "No outstanding finance. Not reported stolen. No insurance write-off history. Clean plate history with no changes." },
      { heading: "Verdict", text: "BUY \u2014 This vehicle is well-maintained with consistent mileage, clean history, and no red flags. The below-average mileage and strong MOT record suggest a reliable purchase." },
    ],
  },
  highRisk: {
    label: "High Risk Example",
    verdict: "AVOID",
    verdictColor: "text-red-700",
    verdictBg: "bg-red-50 border-red-200",
    content: [
      { heading: "Vehicle Summary", text: "This 2016 BMW 320d has had 4 registered keepers in 8 years, which is above average. The current mileage of 89,241 miles requires scrutiny." },
      { heading: "Condition Assessment", text: "MOT pass rate of 57% with 3 failures in 7 tests. Recurring issues with suspension components and brake discs. Two dangerous defects recorded. Condition score: 34/100." },
      { heading: "Mileage Verification", text: "WARNING: Mileage dropped from 72,415 to 58,200 between 2022 and 2023 MOT tests. This is a strong indicator of mileage tampering (clocking)." },
      { heading: "Risk Assessment", text: "Outstanding finance of \u00a38,450 with Close Brothers. Category N write-off recorded in March 2021. Two plate changes since 2020." },
      { heading: "Verdict", text: "AVOID \u2014 Multiple red flags including suspected clocking, outstanding finance, insurance write-off, and frequent keeper changes. Do not purchase this vehicle." },
    ],
  },
};

function SampleReportModal({ onClose }: { onClose: () => void }) {
  const [activeTab, setActiveTab] = useState<"lowRisk" | "highRisk">("lowRisk");
  const report = sampleReports[activeTab];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div className="absolute inset-0 bg-black/50" />
      <div
        className="relative bg-white rounded-xl max-w-2xl w-full max-h-[80vh] overflow-hidden shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal header */}
        <div className="bg-gradient-to-r from-slate-800 to-slate-900 px-6 py-4 flex items-center justify-between">
          <div>
            <h3 className="text-white font-semibold text-lg">Sample AI Report</h3>
            <p className="text-slate-400 text-sm">See what you get before you buy</p>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white transition-colors">
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Tab switcher */}
        <div className="flex border-b border-slate-200">
          <button
            onClick={() => setActiveTab("lowRisk")}
            className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
              activeTab === "lowRisk"
                ? "text-emerald-700 border-b-2 border-emerald-600 bg-emerald-50/50"
                : "text-slate-500 hover:text-slate-700"
            }`}
          >
            Low Risk Car
          </button>
          <button
            onClick={() => setActiveTab("highRisk")}
            className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
              activeTab === "highRisk"
                ? "text-red-700 border-b-2 border-red-600 bg-red-50/50"
                : "text-slate-500 hover:text-slate-700"
            }`}
          >
            High Risk Car
          </button>
        </div>

        {/* Report content */}
        <div className="overflow-y-auto max-h-[55vh] px-6 py-5">
          {/* Verdict banner */}
          <div className={`${report.verdictBg} border rounded-lg px-4 py-3 mb-5 flex items-center gap-3`}>
            <span className={`text-2xl font-bold ${report.verdictColor}`}>
              {report.verdict}
            </span>
            <span className="text-sm text-slate-600">AI Verdict</span>
          </div>

          {report.content.map((section, i) => (
            <div key={i} className="mb-4">
              <h4 className="text-sm font-semibold text-slate-900 mb-1">{section.heading}</h4>
              <p className={`text-sm leading-relaxed ${
                section.heading === "Verdict" ? `font-medium ${report.verdictColor}` : "text-slate-600"
              }`}>
                {section.text}
              </p>
            </div>
          ))}
        </div>

        {/* Modal footer */}
        <div className="border-t border-slate-200 px-6 py-4 bg-slate-50">
          <p className="text-xs text-slate-400 text-center">
            Actual reports are generated from real DVLA, DVSA, and Experian data for the specific vehicle you&apos;re checking.
          </p>
        </div>
      </div>
    </div>
  );
}

/* Trust badges row */
function TrustBadges() {
  return (
    <div className="flex flex-wrap items-center justify-center gap-4 text-xs text-slate-400">
      <span className="flex items-center gap-1.5">
        <LockIcon />
        Secure Stripe Checkout
      </span>
      <span className="flex items-center gap-1.5">
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
        </svg>
        256-bit SSL Encrypted
      </span>
      <span className="flex items-center gap-1.5">
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 15L3 9m0 0l6-6M3 9h12a6 6 0 010 12h-3" />
        </svg>
        Money-back Guarantee
      </span>
    </div>
  );
}

type SelectedTier = "basic" | "premium";

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
  const [selectedTier, setSelectedTier] = useState<SelectedTier>("basic");
  const [showSampleReport, setShowSampleReport] = useState(false);

  const tierConfig = {
    basic: { price: "3.99", label: "Full Report" },
    premium: { price: "9.99", label: "Premium Check" },
  };

  const handleCheckout = async (tier: SelectedTier) => {
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
        tier,
        listingUrl || undefined,
        priceInPence
      );

      window.location.href = checkout_url;
    } catch (err) {
      setCheckoutError(
        err instanceof Error ? err.message : "Checkout failed"
      );
      setCheckoutLoading(false);
    }
  };

  const handleSelectTier = (tier: SelectedTier) => {
    setSelectedTier(tier);
    setShowUpsell(true);
  };

  if (!showUpsell) {
    return (
      <>
        {showSampleReport && <SampleReportModal onClose={() => setShowSampleReport(false)} />}
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
            {/* Three-tier comparison */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              {/* Free column */}
              <div className="border border-slate-200 rounded-lg p-4">
                <div className="text-xs font-semibold text-slate-400 mb-1 uppercase tracking-wide">What you got</div>
                <div className="text-lg font-bold text-slate-900 mb-3">Free</div>
                <ul className="space-y-2">
                  {["MOT History", "Tax Status", "Mileage Data", "ULEZ Check"].map((item) => (
                    <li key={item} className="flex items-center gap-2 text-sm text-slate-600">
                      <CheckIcon />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Basic column */}
              <div className="border-2 border-blue-600 rounded-lg p-4 relative">
                <div className="absolute -top-3 left-4 bg-blue-600 text-white text-xs font-bold px-2.5 py-0.5 rounded-full">
                  POPULAR
                </div>
                <div className="text-xs font-semibold text-blue-600 mb-1 uppercase tracking-wide">Full Report</div>
                <div className="text-lg font-bold text-slate-900 mb-3">&pound;3.99</div>
                <ul className="space-y-2 mb-4">
                  {[
                    { text: "Everything in Free", highlight: false },
                    { text: "AI Risk Assessment", highlight: true },
                    { text: "Buy/Avoid Verdict", highlight: true },
                    { text: "Negotiation Points", highlight: true },
                    { text: "PDF Report Emailed", highlight: true },
                  ].map(({ text, highlight }) => (
                    <li key={text} className="flex items-center gap-2 text-sm text-slate-700">
                      <CheckIcon className={`w-4 h-4 ${highlight ? "text-blue-600" : "text-emerald-500"}`} />
                      <span className={highlight ? "font-medium" : ""}>{text}</span>
                    </li>
                  ))}
                </ul>
                <button
                  onClick={() => handleSelectTier("basic")}
                  className="w-full py-2.5 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors text-sm"
                >
                  Get Full Report &mdash; &pound;3.99
                </button>
              </div>

              {/* Premium column */}
              <div className="border-2 border-purple-600 rounded-lg p-4 relative">
                <div className="absolute -top-3 left-4 bg-purple-600 text-white text-xs font-bold px-2.5 py-0.5 rounded-full">
                  BEST VALUE
                </div>
                <div className="text-xs font-semibold text-purple-600 mb-1 uppercase tracking-wide">Premium Check</div>
                <div className="text-lg font-bold text-slate-900 mb-3">&pound;9.99</div>
                <ul className="space-y-2 mb-4">
                  {[
                    { text: "Everything in Full Report", highlight: false },
                    { text: "Finance & Debt Check", highlight: true },
                    { text: "Stolen Vehicle Check", highlight: true },
                    { text: "Write-off & Salvage", highlight: true },
                    { text: "Market Valuation", highlight: true },
                    { text: "Keeper & Plate History", highlight: true },
                  ].map(({ text, highlight }) => (
                    <li key={text} className="flex items-center gap-2 text-sm text-slate-700">
                      <CheckIcon className={`w-4 h-4 ${highlight ? "text-purple-600" : "text-emerald-500"}`} />
                      <span className={highlight ? "font-medium" : ""}>{text}</span>
                    </li>
                  ))}
                </ul>
                <button
                  onClick={() => handleSelectTier("premium")}
                  className="w-full py-2.5 bg-purple-600 text-white font-semibold rounded-lg hover:bg-purple-700 transition-colors text-sm"
                >
                  Get Premium Check &mdash; &pound;9.99
                </button>
              </div>
            </div>

            {/* Sample report preview */}
            <div className="relative mb-6 rounded-lg overflow-hidden border border-slate-200">
              <div className="p-4 bg-slate-50">
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">Sample AI Verdict</p>
                <div className="space-y-1.5 select-none" style={{ filter: "blur(3px)" }}>
                  <p className="text-sm text-slate-700">This 2018 Ford Fiesta presents as a low-risk purchase. The mileage readings are consistent across all 6 MOT tests with no signs of clocking.</p>
                  <p className="text-sm text-slate-700">The vehicle has a strong MOT pass rate of 83% with only minor advisories related to tyre wear.</p>
                  <p className="text-sm font-semibold text-emerald-700">Verdict: BUY — This vehicle is well-maintained with no red flags.</p>
                </div>
              </div>
              <div className="absolute inset-0 bg-gradient-to-t from-white via-white/80 to-transparent flex items-end justify-center pb-4">
                <button
                  onClick={() => setShowSampleReport(true)}
                  className="px-4 py-2 bg-white border border-slate-300 text-slate-700 text-sm font-medium rounded-lg hover:bg-slate-50 transition-colors shadow-sm"
                >
                  View Sample Report
                </button>
              </div>
            </div>

            {/* Trust badges */}
            <TrustBadges />
          </div>
        </div>
      </>
    );
  }

  // Expanded checkout form
  const config = tierConfig[selectedTier];
  const tierColor = selectedTier === "premium" ? "purple" : "blue";

  return (
    <div id="full-report" className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
      <div className={`bg-gradient-to-r ${selectedTier === "premium" ? "from-purple-800 to-purple-900" : "from-slate-800 to-slate-900"} px-6 py-4`}>
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-white font-semibold text-lg">
              {config.label} &mdash; &pound;{config.price}
            </h3>
            <p className="text-slate-300 text-sm">
              Enter your email and optionally add listing details for a personalised report
            </p>
          </div>
          <span className={`${selectedTier === "premium" ? "bg-purple-600" : "bg-blue-600"} text-white text-xs font-bold px-2.5 py-1 rounded-full uppercase`}>
            {selectedTier}
          </span>
        </div>
      </div>
      <div className="p-6 space-y-4">
        {/* Tier switcher */}
        <div className="flex gap-2 p-1 bg-slate-100 rounded-lg">
          <button
            onClick={() => setSelectedTier("basic")}
            className={`flex-1 py-2 text-sm font-medium rounded-md transition-colors ${
              selectedTier === "basic"
                ? "bg-white text-blue-700 shadow-sm"
                : "text-slate-500 hover:text-slate-700"
            }`}
          >
            Full Report &mdash; &pound;3.99
          </button>
          <button
            onClick={() => setSelectedTier("premium")}
            className={`flex-1 py-2 text-sm font-medium rounded-md transition-colors ${
              selectedTier === "premium"
                ? "bg-white text-purple-700 shadow-sm"
                : "text-slate-500 hover:text-slate-700"
            }`}
          >
            Premium &mdash; &pound;9.99
          </button>
        </div>

        {/* What's included summary */}
        {selectedTier === "premium" && (
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-3">
            <p className="text-xs font-semibold text-purple-700 mb-1.5 uppercase tracking-wide">Premium includes</p>
            <div className="grid grid-cols-2 gap-1">
              {["AI Report + PDF", "Finance Check", "Stolen Check", "Write-off History", "Market Valuation", "Keeper History"].map((item) => (
                <span key={item} className="text-xs text-purple-600 flex items-center gap-1">
                  <CheckIcon className="w-3 h-3 text-purple-500" />
                  {item}
                </span>
              ))}
            </div>
          </div>
        )}

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

        {(checkoutError || reportError) && (
          <p className="text-red-600 text-sm">{checkoutError || reportError}</p>
        )}

        <div className="flex gap-3">
          <button
            onClick={() => handleCheckout(selectedTier)}
            disabled={checkoutLoading || !email}
            className={`flex-1 px-6 py-3 text-white font-semibold rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors ${
              selectedTier === "premium"
                ? "bg-purple-600 hover:bg-purple-700"
                : "bg-emerald-600 hover:bg-emerald-700"
            }`}
          >
            {checkoutLoading ? (
              <span className="flex items-center justify-center gap-2">
                <Spinner />
                Redirecting to checkout...
              </span>
            ) : (
              `Pay \u00A3${config.price} \u2014 Secure Checkout`
            )}
          </button>
          <button
            onClick={() => setShowUpsell(false)}
            className="px-4 py-3 border border-slate-300 text-slate-600 rounded-lg hover:bg-slate-50 transition-colors text-sm"
          >
            Cancel
          </button>
        </div>

        {/* Trust badges */}
        <TrustBadges />
      </div>
    </div>
  );
}
