import "server-only";

import { promises as fs } from "fs";
import path from "path";

export interface SourceCitation {
  title: string;
  url: string;
}

export interface KnownIssue {
  title: string;
  description: string;
  typical_symptoms: string[];
  affected_years: number[] | null;
  estimated_repair_cost_gbp_range: [number, number] | null;
  severity: "low" | "medium" | "high";
  source_citations: SourceCitation[];
}

export interface HeroImage {
  url: string;
  width: number | null;
  height: number | null;
  source_page_url: string | null;
  artist: string | null;
  license_short: string | null;
  license_url: string | null;
}

export interface KnownIssuesRecord {
  make: string;
  model: string;
  generation: string | null;
  years: string;
  top_issues: KnownIssue[];
  overall_reliability_note: string;
  last_updated: string;
  sources: SourceCitation[];
  hero_image: HeroImage | null;
}

const KNOWN_ISSUES_DIR = path.join(
  process.cwd(),
  "..",
  "backend",
  "data",
  "known_issues",
);

export async function loadKnownIssues(
  slug: string,
): Promise<KnownIssuesRecord | null> {
  // Guard against path traversal.
  if (!/^[a-z0-9-]+$/i.test(slug)) {
    return null;
  }
  const filePath = path.join(KNOWN_ISSUES_DIR, `${slug}.json`);
  try {
    const raw = await fs.readFile(filePath, "utf-8");
    return JSON.parse(raw) as KnownIssuesRecord;
  } catch (err) {
    const code = (err as NodeJS.ErrnoException)?.code;
    if (code === "ENOENT") {
      return null;
    }
    throw err;
  }
}

export async function listKnownIssuesSlugs(): Promise<string[]> {
  try {
    const entries = await fs.readdir(KNOWN_ISSUES_DIR);
    return entries
      .filter((f) => f.endsWith(".json"))
      .map((f) => f.replace(/\.json$/, ""));
  } catch (err) {
    const code = (err as NodeJS.ErrnoException)?.code;
    if (code === "ENOENT") {
      return [];
    }
    throw err;
  }
}
