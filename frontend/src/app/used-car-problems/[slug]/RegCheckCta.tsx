"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { track } from "@/lib/analytics";

interface RegCheckCtaProps {
  headline?: string;
  subline?: string;
  compact?: boolean;
  slug: string;
}

export default function RegCheckCta({
  headline = "Check a specific car now",
  subline = "Free instant check using official DVLA & DVSA data.",
  compact = false,
  slug,
}: RegCheckCtaProps) {
  const router = useRouter();
  const [registration, setRegistration] = useState("");
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    const cleaned = registration.replace(/[^a-zA-Z0-9]/g, "").toUpperCase();
    if (cleaned.length < 2 || cleaned.length > 8) {
      setError("Please enter a valid UK registration number");
      return;
    }
    track("seo_page_cta_clicked", { slug, reg: cleaned });
    // Route to the homepage with the reg pre-filled + UTM tags so SearchSection
    // can stash source attribution and thread it through the funnel.
    router.push(`/?reg=${cleaned}&utm_source=seo&utm_content=${encodeURIComponent(slug)}`);
  };

  return (
    <div
      className={`bg-white border border-slate-200 rounded-xl ${compact ? "p-5" : "p-6 sm:p-8"} shadow-sm`}
    >
      {!compact && (
        <div className="text-center mb-5">
          <h2 className="text-xl sm:text-2xl font-bold text-slate-900 mb-1.5">
            {headline}
          </h2>
          <p className="text-slate-500 text-sm sm:text-base">{subline}</p>
        </div>
      )}
      {compact && (
        <p className="text-slate-700 font-medium mb-3 text-sm">{headline}</p>
      )}
      <form onSubmit={handleSubmit} className="max-w-md mx-auto">
        <div className="flex flex-col sm:flex-row gap-2">
          <div className="relative flex-1">
            <div className="absolute left-3 top-1/2 -translate-y-1/2 bg-blue-600 text-white text-xs font-bold px-1.5 py-0.5 rounded">
              GB
            </div>
            <input
              type="text"
              value={registration}
              onChange={(e) =>
                setRegistration(e.target.value.toUpperCase().slice(0, 8))
              }
              placeholder="AB12 CDE"
              aria-label="UK registration number"
              className="w-full pl-14 pr-4 py-3 text-lg font-mono font-bold tracking-wider border-2 border-slate-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none bg-yellow-50 text-slate-900 placeholder:text-slate-400 placeholder:font-normal"
              maxLength={8}
            />
          </div>
          <button
            type="submit"
            disabled={registration.length < 2}
            className="w-full sm:w-auto px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:bg-slate-300 disabled:cursor-not-allowed transition-colors"
          >
            Check Now
          </button>
        </div>
        {error && (
          <p className="mt-3 text-red-600 text-sm text-center">{error}</p>
        )}
      </form>
    </div>
  );
}
