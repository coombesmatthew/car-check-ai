"use client";

import Card from "@/components/ui/Card";
import { DetailRow, icons } from "./shared";

interface PremiumPreviewProps {
  registration: string;
}

export default function PremiumPreview({ registration }: PremiumPreviewProps) {
  return (
    <div className="space-y-6">
      {/* Zone 1: Safety Status Dashboard */}
      <div>
        <div className="flex flex-wrap gap-2">
          {["Finance", "Stolen", "Write-off", "Salvage", "High Risk"].map((label) => (
            <div key={label} className="flex-1 min-w-[140px] bg-amber-50 border border-amber-200 rounded-lg px-3 py-2.5 text-center">
              <div className="text-xs text-amber-600 font-medium mb-0.5">{label}</div>
              <div className="text-sm font-bold text-amber-700">? Unknown</div>
            </div>
          ))}
        </div>
        <p className="text-sm text-slate-500 mt-3">
          We haven&apos;t checked <span className="font-mono font-bold text-slate-700">{registration}</span> against UK finance, stolen, or write-off databases yet.
        </p>
      </div>

      {/* Zone 2: Peek Cards */}
      <div>
        <p className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-3">What you&apos;ll get</p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {/* Card 1: Market Valuation */}
          <div className="relative overflow-hidden">
            <Card title="Market Valuation" icon={icons.currency} status="neutral">
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
            </Card>
            <div className="absolute inset-x-0 bottom-0 h-1/2 bg-gradient-to-t from-white via-white/95 to-transparent pointer-events-none" />
            <span className="absolute top-3 right-3 text-[10px] font-medium text-slate-400 bg-slate-100 px-1.5 py-0.5 rounded">Sample</span>
          </div>

          {/* Card 2: Finance Check */}
          <div className="relative overflow-hidden">
            <Card title="Finance Check" icon={icons.document} status="pass">
              <div className="flex items-center gap-2 bg-emerald-50 border border-emerald-200 rounded-lg px-3 py-2 mb-2">
                <svg className="w-5 h-5 text-emerald-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="text-sm font-semibold text-emerald-800">NO FINANCE OUTSTANDING</span>
              </div>
              <DetailRow label="Records Checked" value="3 finance databases" />
              <DetailRow label="Agreement Type" value="None found" />
              <DetailRow label="Last Updated" value="April 2026" />
            </Card>
            <div className="absolute inset-x-0 bottom-0 h-1/2 bg-gradient-to-t from-white via-white/95 to-transparent pointer-events-none" />
            <span className="absolute top-3 right-3 text-[10px] font-medium text-slate-400 bg-slate-100 px-1.5 py-0.5 rounded">Sample</span>
          </div>

          {/* Card 3: Keeper History */}
          <div className="relative overflow-hidden">
            <Card title="Keeper History" icon={icons.users} status="neutral">
              <div className="text-center py-2 mb-2">
                <span className="text-3xl font-bold text-slate-900">3</span>
                <p className="text-sm text-slate-500">Previous Keepers</p>
              </div>
              <DetailRow label="Last Change" value="14 months ago" />
              <DetailRow label="Average Ownership" value="2.3 years" />
              <DetailRow label="Current Keeper Since" value="February 2025" />
            </Card>
            <div className="absolute inset-x-0 bottom-0 h-1/2 bg-gradient-to-t from-white via-white/95 to-transparent pointer-events-none" />
            <span className="absolute top-3 right-3 text-[10px] font-medium text-slate-400 bg-slate-100 px-1.5 py-0.5 rounded">Sample</span>
          </div>
        </div>
      </div>

      {/* Zone 3: Remaining Checks + CTA */}
      <div>
        <div className="grid grid-cols-2 gap-2 mt-4">
          {["Stolen Vehicle Check", "Insurance Write-off", "Salvage Auction", "Plate Changes", "Previous Searches"].map((item) => (
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
