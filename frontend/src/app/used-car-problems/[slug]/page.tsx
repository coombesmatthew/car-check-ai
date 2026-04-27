import type { Metadata } from "next";
import { notFound } from "next/navigation";
import Link from "next/link";

import Header from "@/components/Header";
import Footer from "@/components/Footer";
import Badge from "@/components/ui/Badge";
import {
  loadKnownIssues,
  listKnownIssuesSlugs,
  type KnownIssue,
  type KnownIssuesRecord,
} from "@/lib/knownIssues";
import RegCheckCta from "./RegCheckCta";
import SeoPageAnalytics from "./SeoPageAnalytics";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

interface SiblingRecord {
  slug: string;
  make: string;
  model: string;
  generation: string | null;
}

async function loadSiblings(make: string, excludeSlug: string): Promise<SiblingRecord[]> {
  try {
    const url = `${API_URL}/api/v1/content/known-issues/siblings?make=${encodeURIComponent(
      make,
    )}&exclude=${encodeURIComponent(excludeSlug)}`;
    const res = await fetch(url, { next: { revalidate: 3600 } });
    if (!res.ok) return [];
    const body = await res.json();
    const siblings = Array.isArray(body?.siblings) ? body.siblings : [];
    return siblings.slice(0, 4);
  } catch {
    return [];
  }
}

interface PageProps {
  params: { slug: string };
}

export async function generateStaticParams() {
  const slugs = await listKnownIssuesSlugs();
  return slugs.map((slug) => ({ slug }));
}

function titleFor(record: KnownIssuesRecord): string {
  const gen = record.generation ? ` ${record.generation}` : "";
  return `${record.make} ${record.model}${gen} (${record.years})`;
}

export async function generateMetadata({
  params,
}: PageProps): Promise<Metadata> {
  const record = await loadKnownIssues(params.slug);
  if (!record) {
    return {
      title: "Used car problems – Vericar",
      description: "Common problems and repair costs for popular used cars.",
    };
  }
  const name = titleFor(record);
  const title = `${name}: Common Problems, Repair Costs & What to Check`;
  const summary = record.overall_reliability_note.trim();
  const description = `${record.top_issues.length} common issues to watch for on the ${name}. ${summary}`.slice(
    0,
    300,
  );
  return {
    title,
    description,
    alternates: {
      canonical: `/used-car-problems/${params.slug}`,
    },
    openGraph: {
      title,
      description,
      type: "article",
      siteName: "Vericar",
    },
    twitter: {
      card: "summary_large_image",
      title,
      description,
    },
  };
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function severityVariant(severity: KnownIssue["severity"]): {
  pill: "fail" | "warn" | "pass";
  label: string;
  border: string;
} {
  switch (severity) {
    case "high":
      return { pill: "fail", label: "High severity", border: "border-l-red-500" };
    case "medium":
      return {
        pill: "warn",
        label: "Medium severity",
        border: "border-l-amber-500",
      };
    case "low":
      return { pill: "pass", label: "Low severity", border: "border-l-emerald-500" };
  }
}

function formatCostRange(range: [number, number] | null): string {
  if (!range) return "Cost varies";
  const [low, high] = range;
  return `£${low.toLocaleString()} – £${high.toLocaleString()}`;
}

function formatYears(years: number[] | null, fallback: string): string {
  if (!years || years.length === 0) return fallback;
  const sorted = [...years].sort();
  const first = sorted[0];
  const last = sorted[sorted.length - 1];
  if (first === last) return String(first);
  return `${first}–${last}`;
}

function formatDate(iso: string): string {
  try {
    const d = new Date(iso);
    return d.toLocaleDateString("en-GB", {
      day: "numeric",
      month: "long",
      year: "numeric",
    });
  } catch {
    return iso;
  }
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------
export default async function Page({ params }: PageProps) {
  const record = await loadKnownIssues(params.slug);
  if (!record) {
    notFound();
  }

  const siblings = await loadSiblings(record.make, params.slug);

  const name = titleFor(record);
  const heroTitle = `${name}: Common Problems, Costs & What to Check`;
  const updated = formatDate(record.last_updated);

  // Structured data -----------------------------------------------------------
  const breadcrumbLd = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      {
        "@type": "ListItem",
        position: 1,
        name: "Home",
        item: "https://vericar.co.uk/",
      },
      {
        "@type": "ListItem",
        position: 2,
        name: "Used Car Problems",
        item: "https://vericar.co.uk/used-car-problems",
      },
      {
        "@type": "ListItem",
        position: 3,
        name: record.make,
      },
      {
        "@type": "ListItem",
        position: 4,
        name: `${record.model}${record.generation ? " " + record.generation : ""}`,
        item: `https://vericar.co.uk/used-car-problems/${params.slug}`,
      },
    ],
  };

  const articleLd = {
    "@context": "https://schema.org",
    "@type": "Article",
    headline: heroTitle,
    datePublished: record.last_updated,
    dateModified: record.last_updated,
    author: {
      "@type": "Organization",
      name: "Vericar",
      url: "https://vericar.co.uk",
    },
    publisher: {
      "@type": "Organization",
      name: "Vericar",
      url: "https://vericar.co.uk",
    },
    about: {
      "@type": "Car",
      name: name,
      manufacturer: record.make,
      model: record.model,
    },
    mainEntityOfPage: {
      "@type": "WebPage",
      "@id": `https://vericar.co.uk/used-car-problems/${params.slug}`,
    },
  };

  const faqLd = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: record.top_issues.map((issue) => ({
      "@type": "Question",
      name: `${issue.title} – symptoms?`,
      acceptedAnswer: {
        "@type": "Answer",
        text: `${issue.typical_symptoms.join(". ")}. ${issue.description}`,
      },
    })),
  };

  const midCtaIndex = Math.floor(record.top_issues.length / 2); // between issues 2 and 3 when 5 issues

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbLd) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(articleLd) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqLd) }}
      />

      <Header />

      <main className="mx-auto max-w-4xl px-4 pt-6 pb-16 w-full">
        {/* Breadcrumb */}
        <nav
          aria-label="Breadcrumb"
          className="text-sm text-slate-500 mb-6 flex flex-wrap gap-1"
        >
          <Link href="/" className="hover:text-blue-600">
            Home
          </Link>
          <span aria-hidden>›</span>
          <span>Used Car Problems</span>
          <span aria-hidden>›</span>
          <span>{record.make}</span>
          <span aria-hidden>›</span>
          <span className="text-slate-700 font-medium">
            {record.model}
            {record.generation ? ` ${record.generation}` : ""}
          </span>
        </nav>

        {/* Headline */}
        <header className="mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold text-slate-900 leading-tight mb-3">
            {heroTitle}
          </h1>
          <p className="text-slate-500 text-sm sm:text-base">
            Last updated {updated} · Based on HonestJohn owner reports,
            synthesised by Vericar
          </p>
        </header>

        {/* Hero image (Wikimedia / Wikipedia, CC-licensed) */}
        {record.hero_image && (
          <figure className="mb-10">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={record.hero_image.url}
              alt={`${record.make} ${record.model} ${record.generation || ""} — example image`.trim()}
              loading="eager"
              className="w-full max-h-[420px] object-cover rounded-lg"
            />
            <figcaption className="text-xs text-gray-500 mt-1">
              Image:{" "}
              {record.hero_image.artist ? (
                record.hero_image.source_page_url ? (
                  <a
                    href={record.hero_image.source_page_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="underline hover:text-blue-600"
                  >
                    {record.hero_image.artist}
                  </a>
                ) : (
                  record.hero_image.artist
                )
              ) : (
                "Unknown"
              )}
              {record.hero_image.license_short && (
                <>
                  {" "}/{" "}
                  {record.hero_image.license_url ? (
                    <a
                      href={record.hero_image.license_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="underline hover:text-blue-600"
                    >
                      {record.hero_image.license_short}
                    </a>
                  ) : (
                    record.hero_image.license_short
                  )}
                </>
              )}{" "}
              via Wikipedia
            </figcaption>
          </figure>
        )}

        {/* Hero CTA */}
        <div className="mb-10">
          <RegCheckCta
            slug={params.slug}
            headline={`Checking a ${record.make} ${record.model}? Run a free check`}
            subline="Mileage verification, MOT history, tax & ULEZ – free, instant, using official DVLA & DVSA data."
          />
        </div>

        {/* At a glance strip */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-slate-900 mb-4">
            At a glance: the {record.top_issues.length} biggest issues
          </h2>
          <ul className="space-y-3">
            {record.top_issues.map((issue, idx) => {
              const sev = severityVariant(issue.severity);
              return (
                <li
                  key={idx}
                  className={`bg-white border border-slate-200 border-l-4 ${sev.border} rounded-lg p-4 flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-5`}
                >
                  <div className="shrink-0">
                    <Badge variant={sev.pill} label={sev.label} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <a
                      href={`#issue-${idx + 1}`}
                      className="font-semibold text-slate-900 hover:text-blue-600"
                    >
                      {idx + 1}. {issue.title}
                    </a>
                  </div>
                  <div className="text-sm text-slate-600 flex flex-wrap gap-x-4 gap-y-1 sm:justify-end">
                    <span>
                      <span className="text-slate-400">Cost:</span>{" "}
                      <span className="font-medium text-slate-800">
                        {formatCostRange(issue.estimated_repair_cost_gbp_range)}
                      </span>
                    </span>
                    <span>
                      <span className="text-slate-400">Years:</span>{" "}
                      <span className="font-medium text-slate-800">
                        {formatYears(issue.affected_years, record.years)}
                      </span>
                    </span>
                  </div>
                </li>
              );
            })}
          </ul>
        </section>

        {/* Per-issue deep dives */}
        <section className="space-y-10">
          {record.top_issues.map((issue, idx) => {
            const sev = severityVariant(issue.severity);
            return (
              <div key={idx}>
                <article
                  id={`issue-${idx + 1}`}
                  className={`bg-white border border-slate-200 border-l-4 ${sev.border} rounded-xl p-6 sm:p-8 scroll-mt-24`}
                >
                  <div className="flex flex-wrap items-center gap-3 mb-3">
                    <Badge variant={sev.pill} label={sev.label} />
                    <span className="text-xs uppercase tracking-wide text-slate-400 font-semibold">
                      Issue {idx + 1} of {record.top_issues.length}
                    </span>
                  </div>
                  <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 mb-3 leading-tight">
                    {issue.title}
                  </h2>
                  <p className="text-sm text-slate-500 mb-5 flex flex-wrap gap-x-5 gap-y-1">
                    <span>
                      <span className="text-slate-400">Typical repair:</span>{" "}
                      <span className="font-medium text-slate-700">
                        {formatCostRange(issue.estimated_repair_cost_gbp_range)}
                      </span>
                    </span>
                    <span>
                      <span className="text-slate-400">Affected years:</span>{" "}
                      <span className="font-medium text-slate-700">
                        {formatYears(issue.affected_years, record.years)}
                      </span>
                    </span>
                  </p>
                  <p className="text-slate-700 leading-relaxed mb-5">
                    {issue.description}
                  </p>
                  {issue.typical_symptoms.length > 0 && (
                    <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
                      <h3 className="font-semibold text-slate-900 mb-2 text-sm uppercase tracking-wide">
                        Typical symptoms to listen & look for
                      </h3>
                      <ul className="list-disc list-outside pl-5 space-y-1 text-slate-700 text-sm">
                        {issue.typical_symptoms.map((s, i) => (
                          <li key={i}>{s}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {issue.source_citations.length > 0 && (
                    <p className="mt-4 text-xs text-slate-500">
                      Sources:{" "}
                      {issue.source_citations.map((s, i) => (
                        <span key={i}>
                          {i > 0 && ", "}
                          <a
                            href={s.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="underline hover:text-blue-600"
                          >
                            {s.title}
                          </a>
                        </span>
                      ))}
                    </p>
                  )}
                </article>

                {/* Mid-page CTA, inserted once near the middle */}
                {idx + 1 === midCtaIndex && (
                  <div className="mt-10">
                    <RegCheckCta
                      compact
                      slug={params.slug}
                      headline={`Checking a specific ${record.make} ${record.model}? Run a free check →`}
                    />
                  </div>
                )}
              </div>
            );
          })}
        </section>

        {/* Overall reliability callout */}
        <section className="mt-12 bg-blue-50 border border-blue-200 rounded-xl p-6">
          <h2 className="text-xl font-bold text-slate-900 mb-2">
            Overall: is the {name} reliable?
          </h2>
          <p className="text-slate-700 leading-relaxed">
            {record.overall_reliability_note}
          </p>
        </section>

        {/* Sources */}
        {record.sources.length > 0 && (
          <section className="mt-10">
            <h2 className="text-lg font-semibold text-slate-900 mb-3">
              Sources & further reading
            </h2>
            <ul className="space-y-2 text-sm">
              {record.sources.map((s, i) => (
                <li key={i}>
                  <a
                    href={s.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 underline"
                  >
                    {s.title}
                  </a>
                </li>
              ))}
            </ul>
            <p className="text-xs text-slate-500 mt-3">
              Owner-report data aggregated from HonestJohn and synthesised by
              Vericar. Always inspect individual vehicles before purchase.
            </p>
          </section>
        )}

        {/* Related models — same-make siblings from the known_issues catalogue */}
        {siblings.length > 0 && (
          <section className="mt-12">
            <h2 className="text-lg font-semibold text-slate-900 mb-3">
              Related models
            </h2>
            <ul className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              {siblings.map((s) => (
                <li key={s.slug}>
                  <Link
                    href={`/used-car-problems/${s.slug}`}
                    className="block bg-white border border-slate-200 rounded-lg px-3 py-3 text-sm text-slate-700 hover:border-blue-400 hover:text-blue-600 transition-colors"
                  >
                    → {s.make} {s.model}
                    {s.generation ? ` ${s.generation}` : ""}
                  </Link>
                </li>
              ))}
            </ul>
          </section>
        )}
      </main>

      <SeoPageAnalytics
        slug={params.slug}
        make={record.make}
        model={record.model}
        generation={record.generation ?? null}
      />

      <Footer />
    </>
  );
}
