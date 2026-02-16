"use client";

import { useState } from "react";
import { checkListing, ListingCheckResponse, ListingData } from "@/lib/api";
import CheckResult from "@/components/CheckResult";
import AIReport from "@/components/AIReport";

/* Format pence as GBP display string */
function formatPrice(pence: number): string {
  return `\u00A3${(pence / 100).toLocaleString("en-GB", {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  })}`;
}

/* Platform display names and brand colours */
const platformInfo: Record<string, { name: string; color: string; bg: string }> = {
  autotrader: { name: "AutoTrader", color: "text-blue-700", bg: "bg-blue-50" },
  gumtree: { name: "Gumtree", color: "text-emerald-700", bg: "bg-emerald-50" },
  facebook: { name: "Facebook Marketplace", color: "text-blue-600", bg: "bg-blue-50" },
  unknown: { name: "Unknown", color: "text-slate-600", bg: "bg-slate-50" },
};

/* Price assessment badge */
function PriceAssessmentBadge({ assessment }: { assessment: string | null }) {
  if (!assessment || assessment === "unknown") return null;

  const styles: Record<string, { bg: string; text: string; label: string }> = {
    "good deal": { bg: "bg-emerald-100", text: "text-emerald-800", label: "Good Deal" },
    fair: { bg: "bg-blue-100", text: "text-blue-800", label: "Fair Price" },
    overpriced: { bg: "bg-red-100", text: "text-red-800", label: "Overpriced" },
  };

  const style = styles[assessment];
  if (!style) return null;

  return (
    <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-semibold ${style.bg} ${style.text}`}>
      {assessment === "good deal" && (
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      )}
      {assessment === "fair" && (
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
        </svg>
      )}
      {assessment === "overpriced" && (
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
        </svg>
      )}
      {style.label}
    </span>
  );
}

/* Listing summary card */
function ListingSummary({ listing, priceAssessment }: { listing: ListingData; priceAssessment: string | null }) {
  const platform = platformInfo[listing.platform] || platformInfo.unknown;

  return (
    <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
      {/* Header with platform badge */}
      <div className="bg-gradient-to-r from-slate-800 to-slate-900 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <svg className="w-5 h-5 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M13.19 8.688a4.5 4.5 0 011.242 7.244l-4.5 4.5a4.5 4.5 0 01-6.364-6.364l1.757-1.757m9.193-9.193a4.5 4.5 0 00-6.364 0l-4.5 4.5a4.5 4.5 0 001.242 7.244" />
              </svg>
              <h2 className="text-white font-semibold text-lg">Listing Analysis</h2>
            </div>
            {listing.title && (
              <p className="text-slate-300 text-sm">{listing.title}</p>
            )}
          </div>
          <span className={`${platform.bg} ${platform.color} text-xs font-bold px-2.5 py-1 rounded-full`}>
            {platform.name}
          </span>
        </div>
      </div>

      <div className="p-6">
        {/* Demo mode banner */}
        {listing.demo_mode && (
          <div className="mb-4 bg-amber-50 border border-amber-200 rounded-lg px-4 py-3 flex items-start gap-2">
            <svg className="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
            </svg>
            <div>
              <p className="text-sm font-medium text-amber-800">Demo Mode</p>
              <p className="text-xs text-amber-600">
                Live scraping is not available for this listing. Showing demo data to illustrate the feature.
                Vehicle check data below (if shown) uses real DVLA/DVSA data.
              </p>
            </div>
          </div>
        )}

        {/* Price + Assessment */}
        <div className="flex items-center justify-between mb-6">
          <div>
            {listing.price_pence !== null && (
              <div className="text-3xl font-bold text-slate-900">
                {formatPrice(listing.price_pence)}
              </div>
            )}
            {listing.mileage !== null && (
              <p className="text-sm text-slate-500 mt-0.5">
                {listing.mileage.toLocaleString()} miles
              </p>
            )}
          </div>
          <PriceAssessmentBadge assessment={priceAssessment} />
        </div>

        {/* Key details grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
          {listing.seller_type && (
            <div className="bg-slate-50 rounded-lg p-3 text-center">
              <p className="text-xs text-slate-400 mb-0.5">Seller</p>
              <p className="text-sm font-medium text-slate-700 capitalize">{listing.seller_type}</p>
            </div>
          )}
          {listing.location && (
            <div className="bg-slate-50 rounded-lg p-3 text-center">
              <p className="text-xs text-slate-400 mb-0.5">Location</p>
              <p className="text-sm font-medium text-slate-700 truncate">{listing.location}</p>
            </div>
          )}
          {listing.images_count !== null && (
            <div className="bg-slate-50 rounded-lg p-3 text-center">
              <p className="text-xs text-slate-400 mb-0.5">Photos</p>
              <p className="text-sm font-medium text-slate-700">{listing.images_count}</p>
            </div>
          )}
          {listing.registration && (
            <div className="bg-slate-50 rounded-lg p-3 text-center">
              <p className="text-xs text-slate-400 mb-0.5">Registration</p>
              <p className="text-sm font-mono font-bold text-slate-900">
                {listing.registration}
              </p>
            </div>
          )}
        </div>

        {/* Description */}
        {listing.description && (
          <div className="mb-6">
            <h4 className="text-sm font-semibold text-slate-700 mb-2">Seller Description</h4>
            <p className="text-sm text-slate-600 leading-relaxed bg-slate-50 rounded-lg p-4 border border-slate-100">
              {listing.description}
            </p>
          </div>
        )}

        {/* Features */}
        {listing.features && listing.features.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-slate-700 mb-2">Key Features</h4>
            <div className="flex flex-wrap gap-2">
              {listing.features.map((feature, i) => (
                <span
                  key={i}
                  className="inline-flex items-center gap-1 bg-slate-50 border border-slate-200 text-slate-600 text-xs px-2.5 py-1 rounded-full"
                >
                  <svg className="w-3 h-3 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                  </svg>
                  {feature}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Link to original listing */}
        <div className="mt-6 pt-4 border-t border-slate-100">
          <a
            href={listing.url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 text-sm text-blue-600 hover:text-blue-700 font-medium"
          >
            View original listing
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
            </svg>
          </a>
        </div>
      </div>
    </div>
  );
}


export default function ListingChecker() {
  const [url, setUrl] = useState("");
  const [registration, setRegistration] = useState("");
  const [showRegOverride, setShowRegOverride] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ListingCheckResponse | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setResult(null);

    const trimmedUrl = url.trim();
    if (!trimmedUrl) {
      setError("Please paste a listing URL");
      return;
    }

    // Basic URL validation
    try {
      new URL(trimmedUrl);
    } catch {
      setError("Please enter a valid URL (e.g. https://www.autotrader.co.uk/...)");
      return;
    }

    setLoading(true);
    try {
      const cleanedReg = registration
        ? registration.replace(/[^a-zA-Z0-9]/g, "").toUpperCase()
        : undefined;
      const data = await checkListing(trimmedUrl, cleanedReg);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit} className="max-w-2xl mx-auto">
        {/* URL input */}
        <div className="relative">
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M13.19 8.688a4.5 4.5 0 011.242 7.244l-4.5 4.5a4.5 4.5 0 01-6.364-6.364l1.757-1.757m9.193-9.193a4.5 4.5 0 00-6.364 0l-4.5 4.5a4.5 4.5 0 001.242 7.244" />
            </svg>
          </div>
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Paste an AutoTrader, Gumtree, or Facebook Marketplace link..."
            className="w-full pl-10 pr-4 py-3.5 text-sm border-2 border-slate-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none bg-white text-slate-900 placeholder:text-slate-400"
          />
        </div>

        {/* Optional registration override */}
        <div className="mt-2">
          {!showRegOverride ? (
            <button
              type="button"
              onClick={() => setShowRegOverride(true)}
              className="text-xs text-slate-400 hover:text-slate-600 transition-colors"
            >
              + Add registration number (optional)
            </button>
          ) : (
            <div className="flex gap-2 items-center">
              <div className="relative flex-1 max-w-[200px]">
                <div className="absolute left-2 top-1/2 -translate-y-1/2 bg-blue-600 text-white text-[10px] font-bold px-1 py-0.5 rounded">
                  GB
                </div>
                <input
                  type="text"
                  value={registration}
                  onChange={(e) =>
                    setRegistration(e.target.value.toUpperCase().slice(0, 8))
                  }
                  placeholder="AB12 CDE"
                  className="w-full pl-10 pr-3 py-2 text-sm font-mono font-bold tracking-wider border border-slate-300 rounded-lg focus:border-blue-500 focus:ring-1 focus:ring-blue-200 outline-none bg-yellow-50 text-slate-900 placeholder:text-slate-400 placeholder:font-normal"
                  maxLength={8}
                />
              </div>
              <button
                type="button"
                onClick={() => {
                  setShowRegOverride(false);
                  setRegistration("");
                }}
                className="text-xs text-slate-400 hover:text-slate-600"
              >
                Remove
              </button>
            </div>
          )}
        </div>

        {/* Submit button */}
        <div className="mt-3">
          <button
            type="submit"
            disabled={loading || !url.trim()}
            className="w-full px-6 py-3.5 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:bg-slate-300 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <svg
                  className="animate-spin h-5 w-5"
                  viewBox="0 0 24 24"
                  fill="none"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
                  />
                </svg>
                Analysing listing...
              </span>
            ) : (
              "Check Listing"
            )}
          </button>
        </div>

        {error && (
          <p className="mt-3 text-red-600 text-sm text-center">{error}</p>
        )}
      </form>

      {/* Supported platforms hint */}
      {!result && (
        <div className="flex items-center justify-center gap-4 mt-4 text-xs text-slate-400">
          <span>Supported:</span>
          <span className="flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-400" />
            AutoTrader
          </span>
          <span className="flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            Gumtree
          </span>
          <span className="flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-500" />
            Facebook Marketplace
          </span>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="mt-8 space-y-6">
          {/* Listing Summary */}
          <ListingSummary
            listing={result.listing}
            priceAssessment={result.price_assessment}
          />

          {/* AI Report */}
          {result.ai_report && result.listing.registration && (
            <AIReport
              report={result.ai_report}
              registration={result.listing.registration}
            />
          )}

          {/* Vehicle Check Results */}
          {result.free_check && (
            <div>
              <h3 className="text-lg font-semibold text-slate-900 mb-4 flex items-center gap-2">
                <svg className="w-5 h-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
                </svg>
                Vehicle Check Results
              </h3>
              <CheckResult data={result.free_check} />
            </div>
          )}

          {/* No registration found notice */}
          {!result.free_check && !result.listing.registration && (
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-6 text-center">
              <svg className="w-10 h-10 text-slate-300 mx-auto mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M15 9h3.75M15 12h3.75M15 15h3.75M4.5 19.5h15a2.25 2.25 0 002.25-2.25V6.75A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25v10.5A2.25 2.25 0 004.5 19.5zm6-10.125a1.875 1.875 0 11-3.75 0 1.875 1.875 0 013.75 0zm1.294 6.336a6.721 6.721 0 01-3.17.789 6.721 6.721 0 01-3.168-.789 3.376 3.376 0 016.338 0z" />
              </svg>
              <p className="text-sm text-slate-600 font-medium mb-1">
                No registration found in the listing
              </p>
              <p className="text-xs text-slate-400">
                Add a registration number above to run a full vehicle check
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
