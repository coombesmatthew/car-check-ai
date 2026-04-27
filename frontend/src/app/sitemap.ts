import { MetadataRoute } from "next";
import fs from "fs";
import path from "path";

export default function sitemap(): MetadataRoute.Sitemap {
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://vericar.co.uk";
  const lastModified = new Date();

  const staticEntries: MetadataRoute.Sitemap = [
    {
      url: siteUrl,
      lastModified,
      changeFrequency: "weekly",
      priority: 1,
    },
    {
      url: `${siteUrl}/ev`,
      lastModified,
      changeFrequency: "weekly",
      priority: 0.9,
    },
  ];

  // Dynamic: one entry per known_issues JSON file in backend/data/known_issues
  const knownIssuesEntries: MetadataRoute.Sitemap = [];
  try {
    const dataDir = path.join(process.cwd(), "../backend/data/known_issues");
    if (fs.existsSync(dataDir)) {
      const files = fs
        .readdirSync(dataDir)
        .filter((f) => f.endsWith(".json") && !f.startsWith("_"));
      for (const file of files) {
        const slug = file.replace(/\.json$/, "");
        const filePath = path.join(dataDir, file);
        const stat = fs.statSync(filePath);
        knownIssuesEntries.push({
          url: `${siteUrl}/used-car-problems/${slug}`,
          lastModified: stat.mtime,
          changeFrequency: "weekly",
          priority: 0.7,
        });
      }
    }
  } catch {
    // Defensive: never break sitemap generation if data dir is missing
    // (e.g. if frontend is built without the backend repo present).
  }

  return [...staticEntries, ...knownIssuesEntries];
}
