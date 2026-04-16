"use client";

export default function PremiumBottomBar({ hasPremium }: { hasPremium: boolean }) {
  if (hasPremium) return null;

  return (
    <div className="fixed bottom-0 left-0 right-0 z-40 md:hidden">
      <div className="bg-gradient-to-r from-purple-600 to-purple-700 px-4 py-3 pb-[max(0.75rem,env(safe-area-inset-bottom))]">
        <a
          href="#section-fullcheck"
          className="flex items-center justify-between"
        >
          <div>
            <p className="text-white font-semibold text-sm">Unlock Full Vehicle Check</p>
            <p className="text-purple-200 text-xs">Finance, stolen, write-off & more</p>
          </div>
          <span className="flex items-center gap-2 bg-white/20 text-white font-bold text-sm px-4 py-2 rounded-lg">
            £9.99
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
            </svg>
          </span>
        </a>
      </div>
    </div>
  );
}
