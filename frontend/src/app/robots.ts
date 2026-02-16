import { MetadataRoute } from "next";

export default function robots(): MetadataRoute.Robots {
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://vericar.co.uk";

  return {
    rules: [
      {
        userAgent: "*",
        allow: "/",
        disallow: ["/api/", "/report/success", "/report/cancel"],
      },
    ],
    sitemap: `${siteUrl}/sitemap.xml`,
  };
}
