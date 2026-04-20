"use client";

import { useState } from "react";
import { DetailRow, PeekCard, icons } from "./shared";
import { createCheckout } from "@/lib/api";

interface PremiumPreviewProps {
  registration: string;
}

const currentMonth = new Date().toLocaleDateString("en-GB", { month: "long", year: "numeric" });

export default function PremiumPreview({ registration }: PremiumPreviewProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleUnlock = async () => {
    if (loading) return;
    setError(null);
    setLoading(true);
    try {
      const { checkout_url } = await createCheckout(registration, null, "premium");
      window.location.href = checkout_url;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Checkout failed");
      setLoading(false);
    }
  };

  return (
    <div className="space-y-5">
      {/* Peek cards grid — 6 sample cards */}
      <div>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">

          {/* Market Valuation */}
          <PeekCard title="Market Valuation" icon={icons.currency} status="pass">
            <DetailRow label="Private Sale" value="£14,250" />
            <DetailRow label="Dealer Forecourt" value="£15,800" />
            <DetailRow label="Trade-in" value="£12,100" />
            <div className="mt-3 pt-3 border-t border-slate-100">
              <div className="flex justify-between text-xs text-slate-400 mb-1">
                <span>£12,100</span>
                <span>£15,800</span>
              </div>
              <div className="h-3 bg-gradient-to-r from-amber-200 via-emerald-300 to-blue-300 rounded-full" />
              <div className="flex justify-between text-xs text-slate-400 mt-1">
                <span>Trade-in</span>
                <span>Dealer</span>
              </div>
            </div>
            <DetailRow label="Condition" value="Good" />
            <DetailRow label="Valuation Date" value={currentMonth} />
          </PeekCard>

          {/* Finance Check */}
          <PeekCard title="Finance Check" icon={icons.document} status="pass">
            <DetailRow label="Records Checked" value="3 finance databases" />
            <DetailRow label="Agreement Type" value="None found" />
            <DetailRow label="Status" value="Clear" />
            <DetailRow label="Last Updated" value={currentMonth} />
          </PeekCard>

          {/* Keeper History */}
          <PeekCard title="Keeper History" icon={icons.users} status="pass">
            <div className="text-center py-2 mb-2">
              <span className="text-3xl font-bold text-slate-900">3</span>
              <p className="text-sm text-slate-500">Previous Keepers</p>
            </div>
            <DetailRow label="Last Change" value="14 months ago" />
            <DetailRow label="Average Ownership" value="2.3 years" />
            <DetailRow label="Current Keeper Since" value="February 2025" />
          </PeekCard>

          {/* Stolen Check */}
          <PeekCard title="Stolen Check" icon={icons.shield} status="pass">
            <DetailRow label="Police Database" value="National record checked" />
            <DetailRow label="Status" value="Clear" />
            <DetailRow label="Last Updated" value={currentMonth} />
          </PeekCard>

          {/* Write-off Check */}
          <PeekCard title="Write-off Check" icon={icons.alert} status="pass">
            <DetailRow label="Insurance Records" value="No claims found" />
            <DetailRow label="Categories Checked" value="A, B, S, N" />
            <DetailRow label="Last Updated" value={currentMonth} />
          </PeekCard>

          {/* Salvage Auction */}
          <PeekCard title="Salvage Check" icon={icons.alert} status="pass">
            <DetailRow label="Auction Records" value="No listings found" />
            <DetailRow label="Database" value="UK salvage auctions" />
            <DetailRow label="Last Updated" value={currentMonth} />
          </PeekCard>

          {/* Plate Changes */}
          <PeekCard title="Plate Changes" icon={icons.swap} status="pass">
            <DetailRow label="Changes Found" value="1 plate change" />
            <DetailRow label="Previous Plate" value="AB12 XYZ" />
            <DetailRow label="Change Date" value="March 2022" />
            <DetailRow label="Change Type" value="Transfer" />
          </PeekCard>

          {/* High Risk Indicators */}
          <PeekCard title="High Risk Indicators" icon={icons.alert} status="pass">
            <DetailRow label="Risk Flags" value="0 found" />
            <DetailRow label="Cloning Check" value="Clear" />
            <DetailRow label="Export Marker" value="Clear" />
            <DetailRow label="Scrapped Marker" value="Clear" />
          </PeekCard>

          {/* Previous Searches */}
          <PeekCard title="Previous Searches" icon={icons.search} status="pass">
            <DetailRow label="Total Searches" value="12 checks" />
            <DetailRow label="Last Searched" value="2 weeks ago" />
            <DetailRow label="Search Frequency" value="Average" />
            <DetailRow label="Last Updated" value={currentMonth} />
          </PeekCard>

        </div>
      </div>

      {/* CTA */}
      <div>
        <div className="mt-2 text-center">
          <button
            onClick={handleUnlock}
            disabled={loading}
            className="inline-flex items-center gap-2 px-8 py-3 bg-purple-600 text-white font-semibold rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-75 disabled:cursor-wait"
          >
            {loading ? (
              <svg className="animate-spin w-5 h-5" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
              </svg>
            ) : (
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
              </svg>
            )}
            {loading ? "Redirecting…" : <>Unlock Full Check for {registration} &mdash; £9.99</>}
          </button>
          <p className="text-xs text-slate-400 mt-2">
            {error ? <span className="text-red-500">{error}</span> : "One-off payment · No subscription · Instant results"}
          </p>
        </div>
      </div>
    </div>
  );
}
