"use client";

import Card from "@/components/ui/Card";
import { DetailRow, icons } from "./shared";

interface PremiumPreviewProps {
  registration: string;
}

/* Reusable wrapper for peek cards with gradient fade + sample label */
function PeekCard({ children, title, icon, status }: {
  children: React.ReactNode;
  title: string;
  icon: React.ReactNode;
  status: "pass" | "fail" | "warn" | "neutral";
}) {
  return (
    <div className="relative overflow-hidden">
      <Card title={title} icon={icon} status={status}>
        {children}
      </Card>
      <div className="absolute inset-x-0 bottom-0 h-1/2 bg-gradient-to-t from-white via-white/95 to-transparent pointer-events-none" />
      <span className="absolute top-3 right-3 text-[10px] font-medium text-slate-400 bg-slate-100 px-1.5 py-0.5 rounded">Sample</span>
    </div>
  );
}

/* Green status banner used across safety check cards */
function ClearBanner({ text }: { text: string }) {
  return (
    <div className="flex items-center gap-2 bg-emerald-50 border border-emerald-200 rounded-lg px-3 py-2 mb-2">
      <svg className="w-5 h-5 text-emerald-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <span className="text-sm font-semibold text-emerald-800">{text}</span>
    </div>
  );
}

export default function PremiumPreview({ registration }: PremiumPreviewProps) {
  return (
    <div className="space-y-5">
      {/* Header text */}
      <p className="text-sm text-slate-500">
        We haven&apos;t checked <span className="font-mono font-bold text-slate-700">{registration}</span> against UK finance, stolen, or write-off databases yet.
      </p>

      {/* Peek cards grid — 6 sample cards */}
      <div>
        <p className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-3">What you&apos;ll get</p>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">

          {/* Market Valuation */}
          <PeekCard title="Market Valuation" icon={icons.currency} status="neutral">
            <div className="space-y-2 mb-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-500">Private Sale</span>
                <span className="text-lg font-bold text-slate-900 font-mono">&pound;14,250</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-500">Dealer Forecourt</span>
                <span className="text-lg font-bold text-slate-900 font-mono">&pound;15,800</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-500">Trade-in</span>
                <span className="text-lg font-bold text-slate-900 font-mono">&pound;12,100</span>
              </div>
            </div>
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
            <DetailRow label="Valuation Date" value="April 2026" />
          </PeekCard>

          {/* Finance Check */}
          <PeekCard title="Finance Check" icon={icons.document} status="pass">
            <ClearBanner text="NO FINANCE OUTSTANDING" />
            <DetailRow label="Records Checked" value="3 finance databases" />
            <DetailRow label="Agreement Type" value="None found" />
            <DetailRow label="Last Updated" value="April 2026" />
          </PeekCard>

          {/* Keeper History */}
          <PeekCard title="Keeper History" icon={icons.users} status="neutral">
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
            <ClearBanner text="NOT STOLEN" />
            <DetailRow label="Police Database" value="National record checked" />
            <DetailRow label="Status" value="Clear" />
            <DetailRow label="Last Updated" value="April 2026" />
          </PeekCard>

          {/* Write-off Check */}
          <PeekCard title="Write-off Check" icon={icons.alert} status="pass">
            <ClearBanner text="NOT WRITTEN OFF" />
            <DetailRow label="Insurance Records" value="No claims found" />
            <DetailRow label="Categories Checked" value="A, B, S, N" />
            <DetailRow label="Last Updated" value="April 2026" />
          </PeekCard>

          {/* Salvage Auction */}
          <PeekCard title="Salvage Check" icon={icons.alert} status="pass">
            <ClearBanner text="NO SALVAGE RECORDS" />
            <DetailRow label="Auction Records" value="No listings found" />
            <DetailRow label="Database" value="UK salvage auctions" />
            <DetailRow label="Last Updated" value="April 2026" />
          </PeekCard>

        </div>
      </div>

      {/* Remaining checks + CTA */}
      <div>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
          {["Plate Changes", "High Risk Indicators", "Previous Searches"].map((item) => (
            <div key={item} className="flex items-center gap-2 text-sm text-slate-500">
              <svg className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
              </svg>
              <span>{item}</span>
            </div>
          ))}
        </div>
        <div className="mt-6 text-center">
          <a
            href="#full-report"
            className="inline-flex items-center gap-2 px-8 py-3 bg-purple-600 text-white font-semibold rounded-lg hover:bg-purple-700 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
            </svg>
            Unlock Full Check for {registration} &mdash; &pound;9.99
          </a>
          <p className="text-xs text-slate-400 mt-2">One-off payment &middot; No subscription &middot; Instant results</p>
        </div>
      </div>
    </div>
  );
}
