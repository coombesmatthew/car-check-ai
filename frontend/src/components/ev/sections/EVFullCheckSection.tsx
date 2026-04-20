"use client";

import { DetailRow, PeekCard, icons } from "@/components/sections/shared";

interface EVFullCheckSectionProps {
  registration: string;
}

const currentMonth = new Date().toLocaleDateString("en-GB", { month: "long", year: "numeric" });

export default function EVFullCheckSection({ registration }: EVFullCheckSectionProps) {
  return (
    <div className="space-y-5">
      {/* Header text */}
      <p className="text-sm text-slate-500">
        We haven&apos;t checked <span className="font-mono font-bold text-slate-700">{registration}</span> against UK finance, stolen, or write-off databases yet.
      </p>

      {/* Peek cards grid */}
      <div>
        <p className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-3">What you&apos;ll get</p>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">

          {/* Market Valuation */}
          <PeekCard href="#unlock" title="Market Valuation" icon={icons.currency} status="pass">
            <DetailRow label="Private Sale" value="\u00A314,250" />
            <DetailRow label="Dealer Forecourt" value="\u00A315,800" />
            <DetailRow label="Trade-in" value="\u00A312,100" />
            <div className="mt-3 pt-3 border-t border-slate-100">
              <div className="flex justify-between text-xs text-slate-400 mb-1">
                <span>&pound;12,100</span>
                <span>&pound;15,800</span>
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
          <PeekCard href="#unlock" title="Finance Check" icon={icons.document} status="pass">
            <DetailRow label="Records Checked" value="3 finance databases" />
            <DetailRow label="Agreement Type" value="None found" />
            <DetailRow label="Status" value="Clear" />
            <DetailRow label="Last Updated" value={currentMonth} />
          </PeekCard>

          {/* Keeper History */}
          <PeekCard href="#unlock" title="Keeper History" icon={icons.users} status="pass">
            <div className="text-center py-2 mb-2">
              <span className="text-3xl font-bold text-slate-900">3</span>
              <p className="text-sm text-slate-500">Previous Keepers</p>
            </div>
            <DetailRow label="Last Change" value="14 months ago" />
            <DetailRow label="Average Ownership" value="2.3 years" />
            <DetailRow label="Current Keeper Since" value="February 2025" />
          </PeekCard>

          {/* Stolen Check */}
          <PeekCard href="#unlock" title="Stolen Check" icon={icons.shield} status="pass">
            <DetailRow label="Police Database" value="National record checked" />
            <DetailRow label="Status" value="Clear" />
            <DetailRow label="Last Updated" value={currentMonth} />
          </PeekCard>

          {/* Write-off Check */}
          <PeekCard href="#unlock" title="Write-off Check" icon={icons.alert} status="pass">
            <DetailRow label="Insurance Records" value="No claims found" />
            <DetailRow label="Categories Checked" value="A, B, S, N" />
            <DetailRow label="Last Updated" value={currentMonth} />
          </PeekCard>

          {/* Salvage Check */}
          <PeekCard href="#unlock" title="Salvage Check" icon={icons.alert} status="pass">
            <DetailRow label="Auction Records" value="No listings found" />
            <DetailRow label="Database" value="UK salvage auctions" />
            <DetailRow label="Last Updated" value={currentMonth} />
          </PeekCard>

          {/* Plate Changes */}
          <PeekCard href="#unlock" title="Plate Changes" icon={icons.swap} status="pass">
            <DetailRow label="Changes Found" value="1 plate change" />
            <DetailRow label="Previous Plate" value="AB12 XYZ" />
            <DetailRow label="Change Date" value="March 2022" />
            <DetailRow label="Change Type" value="Transfer" />
          </PeekCard>

          {/* High Risk Indicators */}
          <PeekCard href="#unlock" title="High Risk Indicators" icon={icons.alert} status="pass">
            <DetailRow label="Risk Flags" value="0 found" />
            <DetailRow label="Cloning Check" value="Clear" />
            <DetailRow label="Export Marker" value="Clear" />
            <DetailRow label="Scrapped Marker" value="Clear" />
          </PeekCard>

          {/* Previous Searches */}
          <PeekCard href="#unlock" title="Previous Searches" icon={icons.search} status="pass">
            <DetailRow label="Total Searches" value="12 checks" />
            <DetailRow label="Last Searched" value="2 weeks ago" />
            <DetailRow label="Search Frequency" value="Average" />
            <DetailRow label="Last Updated" value={currentMonth} />
          </PeekCard>

        </div>
      </div>

      {/* CTA */}
      <div className="mt-2 text-center">
        <a
          href="#unlock"
          className="inline-flex items-center gap-2 px-8 py-3 bg-teal-600 text-white font-semibold rounded-lg hover:bg-teal-700 transition-colors"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
          </svg>
          Unlock EV Complete for {registration} &mdash; &pound;13.99
        </a>
        <p className="text-xs text-slate-400 mt-2">One-off payment &middot; No subscription &middot; Instant results</p>
      </div>
    </div>
  );
}
