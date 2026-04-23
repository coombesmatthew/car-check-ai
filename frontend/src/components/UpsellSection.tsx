"use client";

import { useState } from "react";
import { createCheckout } from "@/lib/api";
import ListingPriceModal from "@/components/ListingPriceModal";

interface UpsellSectionProps {
  registration: string;
  showUpsell: boolean;
  setShowUpsell: (show: boolean) => void;
  reportError: string | null;
}

const CheckIcon = ({ className = "w-4 h-4 text-purple-600" }: { className?: string }) => (
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
        256-bit SSL
      </span>
      <span className="flex items-center gap-1.5">
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 15L3 9m0 0l6-6M3 9h12a6 6 0 010 12h-3" />
        </svg>
        One-off payment
      </span>
    </div>
  );
}

// Simple UpsellSection: single Premium Check CTA. Email collected by
// Stripe on the checkout page; no in-page form.
export default function UpsellSection({
  registration,
  showUpsell: _showUpsell,
  setShowUpsell: _setShowUpsell,
  reportError,
}: UpsellSectionProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);

  const handleContinue = async (listingPricePence: number | null) => {
    if (loading) return;
    setError(null);
    setLoading(true);
    try {
      const { checkout_url } = await createCheckout(registration, null, "premium", listingPricePence);
      window.location.href = checkout_url;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Checkout failed");
      setLoading(false);
      setModalOpen(false);
    }
  };

  const premiumIncludes = [
    "Finance & outstanding-debt check",
    "Stolen-vehicle register",
    "Insurance write-off history",
    "Market valuation (four price bands)",
    "Keeper-history timeline",
    "Plate-change history",
    "Salvage-auction records",
    "Emailed & online for 30 days",
  ];

  return (
    <div id="full-report" className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
      <div className="bg-gradient-to-r from-purple-700 to-purple-800 px-6 py-5">
        <h3 className="text-white font-bold text-xl mb-1">
          Unlock Full Vehicle Check &mdash; {registration}
        </h3>
        <p className="text-purple-200 text-sm">
          The full provenance picture: finance, stolen, write-off, valuation, keeper history.
        </p>
      </div>

      <div className="p-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-2 mb-6">
          {premiumIncludes.map((item) => (
            <span key={item} className="flex items-center gap-2 text-sm text-slate-700">
              <CheckIcon />
              {item}
            </span>
          ))}
        </div>

        <div className="text-center mb-4">
          <button
            onClick={() => setModalOpen(true)}
            disabled={loading}
            className="inline-flex items-center gap-2 px-8 py-3.5 bg-purple-600 text-white font-semibold rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-75 disabled:cursor-wait"
          >
            {loading ? (
              <>
                <Spinner />
                Redirecting to checkout&hellip;
              </>
            ) : (
              <>
                <LockIcon />
                Unlock Full Check for {registration} &mdash; &pound;9.99
              </>
            )}
          </button>
          <p className="text-xs text-slate-400 mt-2">One-off payment &middot; No subscription &middot; Instant results</p>
        </div>

        {(error || reportError) && (
          <p className="text-red-600 text-sm text-center mb-3">{error || reportError}</p>
        )}

        <TrustBadges />

        <p className="text-xs text-slate-400 text-center mt-4">
          By purchasing, you agree to our{" "}
          <a href="/terms" className="underline hover:text-slate-600">Terms of Service</a> and{" "}
          <a href="/privacy" className="underline hover:text-slate-600">Privacy Policy</a>.
        </p>
      </div>

      <ListingPriceModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        onContinue={handleContinue}
        registration={registration}
        tierLabel="Premium Check"
        tierPrice="£9.99"
        accentColour="purple"
        loading={loading}
      />
    </div>
  );
}
