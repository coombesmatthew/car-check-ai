"use client";

import { useEffect, useRef, useState } from "react";

/* Asking-price capture modal shown before Stripe redirect.
   Optional — user can skip. Captured price (pence) is forwarded to
   createCheckout so the paid report can show "paying £X vs valuation". */
export interface ListingPriceModalProps {
  open: boolean;
  onClose: () => void;
  onContinue: (listingPricePence: number | null) => void;
  registration: string;
  tierLabel: string;
  tierPrice: string;
  accentColour?: "blue" | "emerald" | "teal" | "purple";
  loading?: boolean;
}

const ACCENT: Record<NonNullable<ListingPriceModalProps["accentColour"]>, string> = {
  blue: "bg-blue-600 hover:bg-blue-700",
  emerald: "bg-emerald-600 hover:bg-emerald-700",
  teal: "bg-teal-600 hover:bg-teal-700",
  purple: "bg-purple-600 hover:bg-purple-700",
};

export default function ListingPriceModal({
  open,
  onClose,
  onContinue,
  registration,
  tierLabel,
  tierPrice,
  accentColour = "blue",
  loading = false,
}: ListingPriceModalProps) {
  const [price, setPrice] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (open) {
      setPrice("");
      setTimeout(() => inputRef.current?.focus(), 40);
    }
  }, [open]);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape" && !loading) onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, loading, onClose]);

  if (!open) return null;

  const parsed = parseFloat(price);
  const pence = Number.isFinite(parsed) && parsed > 0 ? Math.round(parsed * 100) : null;

  const submit = () => {
    if (loading) return;
    onContinue(pence);
  };

  const skip = () => {
    if (loading) return;
    onContinue(null);
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="listing-price-title"
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
      onClick={(e) => {
        if (e.target === e.currentTarget && !loading) onClose();
      }}
    >
      <div className="bg-white rounded-xl shadow-xl max-w-md w-full overflow-hidden">
        <div className="px-6 pt-6 pb-4">
          <h2 id="listing-price-title" className="text-lg font-bold text-slate-900">
            We can make sure you&apos;re getting a good deal
          </h2>
          <p className="text-sm text-slate-500 mt-1.5">
            Enter the asking price for{" "}
            <span className="font-mono font-semibold text-slate-700">{registration}</span>{" "}
            and we&apos;ll compare it against the market valuation in your report.
          </p>

          <div className="mt-5">
            <label htmlFor="listing-price-input" className="block text-xs font-semibold text-slate-600 uppercase tracking-wide mb-1.5">
              Asking price (optional)
            </label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 font-medium">£</span>
              <input
                id="listing-price-input"
                ref={inputRef}
                type="number"
                inputMode="decimal"
                min="0"
                step="1"
                placeholder="9500"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && submit()}
                disabled={loading}
                className="w-full pl-8 pr-4 py-2.5 text-base border border-slate-300 rounded-lg focus:outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100 disabled:bg-slate-50"
              />
            </div>
            <p className="text-xs text-slate-400 mt-1.5">Skip if you&apos;re not ready — you can still unlock the report without a price.</p>
          </div>
        </div>

        <div className="px-6 pb-6 pt-2 space-y-2">
          <button
            type="button"
            onClick={submit}
            disabled={loading}
            className={`w-full inline-flex items-center justify-center gap-2 px-6 py-3 text-white font-semibold rounded-lg transition-colors disabled:opacity-75 disabled:cursor-wait ${ACCENT[accentColour]}`}
          >
            {loading ? (
              <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
              </svg>
            ) : null}
            {loading ? "Redirecting…" : `Continue to payment — ${tierPrice}`}
          </button>
          <button
            type="button"
            onClick={skip}
            disabled={loading}
            className="w-full px-6 py-2 text-sm text-slate-500 hover:text-slate-700 font-medium transition-colors"
          >
            Skip — continue without a price
          </button>
        </div>

        <div className="bg-slate-50 border-t border-slate-100 px-6 py-3 text-xs text-slate-500 text-center">
          {tierLabel} · One-off payment · No subscription
        </div>
      </div>
    </div>
  );
}
