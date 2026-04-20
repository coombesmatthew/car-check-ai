"use client";

interface PremiumBottomBarProps {
  hasPremium: boolean;
  variant?: "full" | "ev";
}

const VARIANTS = {
  full: {
    title: "Unlock Full Vehicle Check",
    subtitle: "Finance, stolen, write-off & more",
    price: "£9.99",
    href: "#full-report",
    gradient: "from-purple-600 to-purple-700",
    subtitleColor: "text-purple-200",
  },
  ev: {
    title: "Unlock EV Complete",
    subtitle: "Battery, range, provenance & valuation",
    price: "£13.99",
    href: "#unlock",
    gradient: "from-teal-600 to-teal-700",
    subtitleColor: "text-teal-200",
  },
} as const;

export default function PremiumBottomBar({ hasPremium, variant = "full" }: PremiumBottomBarProps) {
  if (hasPremium) return null;
  const v = VARIANTS[variant];

  return (
    <div className="fixed bottom-0 left-0 right-0 z-40 md:hidden">
      <div className={`bg-gradient-to-r ${v.gradient} px-4 py-3 pb-[max(0.75rem,env(safe-area-inset-bottom))]`}>
        <a href={v.href} className="flex items-center justify-between">
          <div>
            <p className="text-white font-semibold text-sm">{v.title}</p>
            <p className={`${v.subtitleColor} text-xs`}>{v.subtitle}</p>
          </div>
          <span className="flex items-center gap-2 bg-white/20 text-white font-bold text-sm px-4 py-2 rounded-lg">
            {v.price}
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
            </svg>
          </span>
        </a>
      </div>
    </div>
  );
}
