"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { track } from "@/lib/analytics";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

interface KnownIssuesResolveResponse {
  slug: string;
  make: string;
  model: string;
  generation: string | null;
}

interface Props {
  make: string | null | undefined;
  model: string | null | undefined;
  year: number | null | undefined;
}

/**
 * Looks up whether the current vehicle has a Vericar "known issues" SEO page
 * and, if so, renders a link card directing the user to it. Renders nothing
 * on 404 / network error / missing inputs.
 */
export default function KnownIssuesCard({ make, model, year }: Props) {
  const [data, setData] = useState<KnownIssuesResolveResponse | null>(null);

  useEffect(() => {
    if (!make || !model || !year) return;
    let cancelled = false;
    const url = `${API_URL}/api/v1/content/known-issues/resolve?make=${encodeURIComponent(
      make,
    )}&model=${encodeURIComponent(model)}&year=${year}`;
    fetch(url)
      .then((res) => (res.ok ? res.json() : null))
      .then((body) => {
        if (!cancelled && body && body.slug) setData(body);
      })
      .catch(() => {
        // swallow — card just won't render
      });
    return () => {
      cancelled = true;
    };
  }, [make, model, year]);

  if (!data) return null;

  const label = `${data.make} ${data.model}${data.generation ? " " + data.generation : ""}`;

  return (
    <Link
      href={`/used-car-problems/${data.slug}`}
      onClick={() => track("upsell_clicked", { target: "known_issues", slug: data.slug })}
      className="block bg-white border border-slate-200 border-l-4 border-l-blue-500 rounded-xl p-5 hover:border-l-blue-600 hover:shadow-sm transition-all"
    >
      <div className="flex items-center justify-between gap-3">
        <div className="min-w-0">
          <p className="font-semibold text-slate-900">
            Known problems for your <span className="text-blue-600">{label}</span>
          </p>
          <p className="text-sm text-slate-500 mt-0.5">
            Read common issues, repair costs &amp; what to inspect before buying.
          </p>
        </div>
        <span className="text-blue-600 text-xl font-bold shrink-0" aria-hidden>
          →
        </span>
      </div>
    </Link>
  );
}
