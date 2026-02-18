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

/* Sample card used in the preview modal */
function SampleCard({ title, icon, children, accent = "blue" }: { title: string; icon: React.ReactNode; children: React.ReactNode; accent?: "blue" | "purple" | "emerald" | "red" | "amber" }) {
  const accentMap = {
    blue: "border-blue-200 bg-blue-50/30",
    purple: "border-purple-200 bg-purple-50/30",
    emerald: "border-emerald-200 bg-emerald-50/30",
    red: "border-red-200 bg-red-50/30",
    amber: "border-amber-200 bg-amber-50/30",
  };
  return (
    <div className={`border rounded-lg overflow-hidden ${accentMap[accent]}`}>
      <div className="flex items-center gap-2 px-3 py-2 border-b border-slate-100 bg-white/60">
        <span className="text-slate-500">{icon}</span>
        <span className="text-xs font-semibold text-slate-700">{title}</span>
      </div>
      <div className="px-3 py-2.5">{children}</div>
    </div>
  );
}

function SampleReportModal({ onClose }: { onClose: () => void }) {
  const [activeTab, setActiveTab] = useState<"basic" | "premium">("basic");

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div className="absolute inset-0 bg-black/50" />
      <div
        className="relative bg-white rounded-xl max-w-2xl w-full max-h-[85vh] overflow-hidden shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal header */}
        <div className="bg-gradient-to-r from-slate-800 to-slate-900 px-6 py-4 flex items-center justify-between">
          <div>
            <h3 className="text-white font-semibold text-lg">What&apos;s Included</h3>
            <p className="text-slate-400 text-sm">See exactly what you get with each report</p>
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
            onClick={() => setActiveTab("basic")}
            className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
              activeTab === "basic"
                ? "text-blue-700 border-b-2 border-blue-600 bg-blue-50/50"
                : "text-slate-500 hover:text-slate-700"
            }`}
          >
            Full Report &mdash; &pound;3.99
          </button>
          <button
            onClick={() => setActiveTab("premium")}
            className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
              activeTab === "premium"
                ? "text-purple-700 border-b-2 border-purple-600 bg-purple-50/50"
                : "text-slate-500 hover:text-slate-700"
            }`}
          >
            Premium Check &mdash; &pound;9.99
          </button>
        </div>

        {/* Preview content */}
        <div className="overflow-y-auto max-h-[58vh] px-5 py-5 space-y-3">
          {/* --- Full Report cards (shown in both tabs) --- */}

          {/* AI Verdict */}
          <SampleCard
            title="AI Buyer&apos;s Verdict"
            accent="emerald"
            icon={<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" /></svg>}
          >
            <div className="bg-emerald-50 border border-emerald-200 rounded-md px-3 py-2 flex items-center gap-2 mb-2">
              <span className="text-lg font-bold text-emerald-700">BUY</span>
              <span className="text-xs text-slate-500">AI Verdict</span>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              This 2019 Volkswagen Golf 1.5 TSI is a well-maintained vehicle with consistent mileage, 100% MOT pass rate, and no red flags. Below-average mileage and strong service history suggest a reliable purchase.
            </p>
          </SampleCard>

          {/* Condition Score */}
          <SampleCard
            title="Condition Score"
            accent="blue"
            icon={<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" /></svg>}
          >
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-full border-4 border-emerald-500 flex items-center justify-center">
                <span className="text-sm font-bold text-emerald-700">87</span>
              </div>
              <div>
                <p className="text-xs font-semibold text-slate-800">Excellent condition</p>
                <p className="text-xs text-slate-500">Based on MOT history, defects, and mileage patterns</p>
              </div>
            </div>
          </SampleCard>

          {/* Negotiation Points */}
          <SampleCard
            title="Negotiation Points"
            accent="amber"
            icon={<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M12 6v12m-3-2.818l.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.45-.22-2.003-.659-1.106-.879-1.106-2.303 0-3.182s2.9-.879 4.006 0l.415.33M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}
          >
            <ul className="space-y-1.5">
              <li className="flex items-start gap-2 text-xs text-slate-600">
                <span className="text-amber-500 mt-0.5">&#9679;</span>
                Brake pad wear advisory noted — factor in ~&pound;150 for replacement
              </li>
              <li className="flex items-start gap-2 text-xs text-slate-600">
                <span className="text-amber-500 mt-0.5">&#9679;</span>
                MOT due in 47 days — leverage for &pound;50-100 discount
              </li>
              <li className="flex items-start gap-2 text-xs text-slate-600">
                <span className="text-emerald-500 mt-0.5">&#9679;</span>
                Below-average mileage (42,318 mi) — supports asking price
              </li>
            </ul>
          </SampleCard>

          {/* PDF delivery */}
          <SampleCard
            title="PDF Report Emailed"
            accent="blue"
            icon={<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75" /></svg>}
          >
            <p className="text-xs text-slate-600">Full report delivered as a professional PDF to your inbox within 60 seconds. Take it to the dealer or share with your mechanic.</p>
          </SampleCard>

          {/* --- Premium-only cards --- */}
          {activeTab === "premium" && (
            <>
              <div className="flex items-center gap-2 mt-3 mb-1">
                <div className="flex-1 h-px bg-purple-200" />
                <span className="text-xs font-semibold text-purple-600 uppercase tracking-wide">Premium extras</span>
                <div className="flex-1 h-px bg-purple-200" />
              </div>

              {/* Finance Check */}
              <SampleCard
                title="Finance &amp; Outstanding Debt"
                accent="purple"
                icon={<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M2.25 18.75a60.07 60.07 0 0115.797 2.101c.727.198 1.453-.342 1.453-1.096V18.75M3.75 4.5v.75A.75.75 0 013 6h-.75m0 0v-.375c0-.621.504-1.125 1.125-1.125H20.25M2.25 6v9m18-10.5v.75c0 .414.336.75.75.75h.75m-1.5-1.5h.375c.621 0 1.125.504 1.125 1.125v9.75c0 .621-.504 1.125-1.125 1.125h-.375m1.5-1.5H21a.75.75 0 00-.75.75v.75m0 0H3.75m0 0h-.375a1.125 1.125 0 01-1.125-1.125V15m1.5 1.5v-.75A.75.75 0 003 15h-.75M15 10.5a3 3 0 11-6 0 3 3 0 016 0zm3 0h.008v.008H18V10.5zm-12 0h.008v.008H6V10.5z" /></svg>}
              >
                <div className="flex items-center gap-2 mb-1.5">
                  <span className="w-5 h-5 rounded-full bg-emerald-100 flex items-center justify-center">
                    <CheckIcon className="w-3 h-3 text-emerald-600" />
                  </span>
                  <span className="text-xs font-semibold text-emerald-700">No outstanding finance</span>
                </div>
                <p className="text-xs text-slate-500">Checked against all major UK finance providers. Safe to purchase.</p>
              </SampleCard>

              {/* Stolen Check */}
              <SampleCard
                title="Stolen Vehicle Check"
                accent="purple"
                icon={<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" /></svg>}
              >
                <div className="flex items-center gap-2 mb-1.5">
                  <span className="w-5 h-5 rounded-full bg-emerald-100 flex items-center justify-center">
                    <CheckIcon className="w-3 h-3 text-emerald-600" />
                  </span>
                  <span className="text-xs font-semibold text-emerald-700">Not reported stolen</span>
                </div>
                <p className="text-xs text-slate-500">Checked against the Police National Computer (PNC) database.</p>
              </SampleCard>

              {/* Write-off */}
              <SampleCard
                title="Insurance Write-off"
                accent="purple"
                icon={<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" /></svg>}
              >
                <div className="flex items-center gap-2 mb-1.5">
                  <span className="w-5 h-5 rounded-full bg-emerald-100 flex items-center justify-center">
                    <CheckIcon className="w-3 h-3 text-emerald-600" />
                  </span>
                  <span className="text-xs font-semibold text-emerald-700">No write-off history</span>
                </div>
                <p className="text-xs text-slate-500">No Category A, B, N, or S insurance write-off records found.</p>
              </SampleCard>

              {/* Valuation */}
              <SampleCard
                title="Market Valuation"
                accent="purple"
                icon={<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M12 6v12m-3-2.818l.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.45-.22-2.003-.659-1.106-.879-1.106-2.303 0-3.182s2.9-.879 4.006 0l.415.33M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}
              >
                <div className="grid grid-cols-2 gap-2">
                  <div className="bg-white rounded-md px-2.5 py-2 border border-purple-100">
                    <p className="text-[10px] text-slate-400 uppercase">Private Sale</p>
                    <p className="text-sm font-bold text-slate-900">&pound;14,250</p>
                  </div>
                  <div className="bg-white rounded-md px-2.5 py-2 border border-purple-100">
                    <p className="text-[10px] text-slate-400 uppercase">Dealer</p>
                    <p className="text-sm font-bold text-slate-900">&pound;15,800</p>
                  </div>
                  <div className="bg-white rounded-md px-2.5 py-2 border border-purple-100">
                    <p className="text-[10px] text-slate-400 uppercase">Trade-in</p>
                    <p className="text-sm font-bold text-slate-900">&pound;12,100</p>
                  </div>
                  <div className="bg-white rounded-md px-2.5 py-2 border border-purple-100">
                    <p className="text-[10px] text-slate-400 uppercase">Part Exchange</p>
                    <p className="text-sm font-bold text-slate-900">&pound;11,500</p>
                  </div>
                </div>
              </SampleCard>

              {/* Plate & Keeper */}
              <SampleCard
                title="Plate &amp; Keeper History"
                accent="purple"
                icon={<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M15 9h3.75M15 12h3.75M15 15h3.75M4.5 19.5h15a2.25 2.25 0 002.25-2.25V6.75A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25v10.5A2.25 2.25 0 004.5 19.5zm6-10.125a1.875 1.875 0 11-3.75 0 1.875 1.875 0 013.75 0zm1.294 6.336a6.721 6.721 0 01-3.17.789 6.721 6.721 0 01-3.168-.789 3.376 3.376 0 016.338 0z" /></svg>}
              >
                <div className="flex items-center gap-2 mb-1.5">
                  <span className="w-5 h-5 rounded-full bg-emerald-100 flex items-center justify-center">
                    <CheckIcon className="w-3 h-3 text-emerald-600" />
                  </span>
                  <span className="text-xs font-semibold text-emerald-700">No plate changes found</span>
                </div>
                <p className="text-xs text-slate-500">2 registered keepers since first registration. V5C issued 14 months ago.</p>
              </SampleCard>
            </>
          )}

          {activeTab === "basic" && (
            <div className="mt-2 bg-purple-50 border border-purple-200 rounded-lg p-3 text-center">
              <p className="text-xs text-purple-700 font-medium mb-1">Want finance, stolen, write-off &amp; valuation checks?</p>
              <button
                onClick={() => setActiveTab("premium")}
                className="text-xs font-semibold text-purple-600 hover:text-purple-800 underline underline-offset-2"
              >
                See what Premium includes &rarr;
              </button>
            </div>
          )}
        </div>

        {/* Modal footer */}
        <div className="border-t border-slate-200 px-6 py-4 bg-slate-50">
          <p className="text-xs text-slate-400 text-center">
            Sample data shown above. Actual reports use real DVLA, DVSA, and provider data for your specific vehicle.
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
            <div className="text-center mb-6">
              <button
                onClick={() => setShowSampleReport(true)}
                className="inline-flex items-center gap-2 px-5 py-2.5 bg-white border border-slate-300 text-slate-700 text-sm font-medium rounded-lg hover:bg-slate-50 hover:border-slate-400 transition-colors shadow-sm"
              >
                <svg className="w-4 h-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
                  <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                See What&apos;s Included
              </button>
            </div>

            {/* One-off payment note */}
            <p className="text-center text-sm text-slate-500 mb-4">
              One-off payment. No subscriptions.
            </p>

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
