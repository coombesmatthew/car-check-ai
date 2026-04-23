"use client";

import { useState } from "react";
import { createCheckout, createEVCheckout } from "@/lib/api";
import ListingPriceModal from "@/components/ListingPriceModal";

interface PremiumBottomBarProps {
  hasPremium: boolean;
  variant?: "full" | "ev";
  registration?: string;
}

const VARIANTS = {
  full: {
    title: "Unlock Full Vehicle Check",
    subtitle: "Finance, stolen, write-off & more",
    price: "£9.99",
    tier: "premium" as const,
    label: "Premium Check",
    isEv: false,
    gradient: "from-purple-600 to-purple-700",
    subtitleColor: "text-purple-200",
    accent: "purple" as const,
  },
  ev: {
    title: "Unlock EV Complete",
    subtitle: "Battery, range, provenance & valuation",
    price: "£13.99",
    tier: "ev_complete" as const,
    label: "EV Complete",
    isEv: true,
    gradient: "from-teal-600 to-teal-700",
    subtitleColor: "text-teal-200",
    accent: "teal" as const,
  },
} as const;

export default function PremiumBottomBar({ hasPremium, variant = "full", registration }: PremiumBottomBarProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);

  if (hasPremium) return null;
  const v = VARIANTS[variant];

  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    if (!registration || loading) return;
    setError(null);
    setModalOpen(true);
  };

  const handleContinue = async (listingPricePence: number | null) => {
    if (!registration || loading) return;
    setError(null);
    setLoading(true);
    try {
      const { checkout_url } = v.isEv
        ? await createEVCheckout(registration, null, v.tier as "ev" | "ev_complete", listingPricePence)
        : await createCheckout(registration, null, v.tier, listingPricePence);
      window.location.href = checkout_url;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Checkout failed");
      setLoading(false);
      setModalOpen(false);
    }
  };

  return (
    <div className="fixed bottom-0 left-0 right-0 z-40 md:hidden">
      <div className={`bg-gradient-to-r ${v.gradient} px-4 py-3 pb-[max(0.75rem,env(safe-area-inset-bottom))]`}>
        <button
          onClick={handleClick}
          disabled={loading || !registration}
          className="flex items-center justify-between w-full disabled:opacity-80"
        >
          <div className="text-left">
            <p className="text-white font-semibold text-sm">{v.title}</p>
            <p className={`${v.subtitleColor} text-xs`}>
              {error ? error : v.subtitle}
            </p>
          </div>
          <span className="flex items-center gap-2 bg-white/20 text-white font-bold text-sm px-4 py-2 rounded-lg">
            {loading ? (
              <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
              </svg>
            ) : (
              <>
                {v.price}
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
                </svg>
              </>
            )}
          </span>
        </button>
      </div>

      {registration && (
        <ListingPriceModal
          open={modalOpen}
          onClose={() => setModalOpen(false)}
          onContinue={handleContinue}
          registration={registration}
          tierLabel={v.label}
          tierPrice={v.price}
          accentColour={v.accent}
          loading={loading}
        />
      )}
    </div>
  );
}
