import type { Metadata } from "next";
import "./globals.css";
import { PostHogProvider } from "@/components/PostHogProvider";

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://vericar.co.uk";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default:
      "VeriCar - Free UK Vehicle Check | MOT, Tax, Mileage & Clean Air Zones",
    template: "%s | VeriCar",
  },
  description:
    "Free instant vehicle check using official DVLA & DVSA data. MOT history, mileage clocking detection, tax status, ULEZ and all UK clean air zone compliance. Check any UK vehicle in seconds.",
  keywords: [
    "car check",
    "vehicle check",
    "MOT history",
    "HPI check",
    "mileage clocking",
    "DVLA check",
    "free car check",
    "UK vehicle check",
    "ULEZ check",
    "clean air zone",
    "vehicle valuation",
    "finance check",
    "stolen check",
    "write-off check",
    "used car check",
  ],
  authors: [{ name: "VeriCar" }],
  creator: "VeriCar",
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  openGraph: {
    type: "website",
    locale: "en_GB",
    url: siteUrl,
    siteName: "VeriCar",
    title: "VeriCar - Free UK Vehicle Check | MOT, Tax, Mileage & Clocking Detection",
    description:
      "Check any UK vehicle for free. MOT history, mileage clocking detection, tax status, ULEZ compliance, finance, stolen, and write-off checks. Powered by official DVLA & DVSA data.",
  },
  twitter: {
    card: "summary_large_image",
    title: "VeriCar - Free UK Vehicle Check",
    description:
      "Free instant MOT history, mileage clocking detection, ULEZ compliance, finance & stolen checks for any UK vehicle.",
    creator: "@vericar_uk",
  },
  alternates: {
    canonical: siteUrl,
  },
  verification: {
    // Add these when accounts are created
    // google: "google-site-verification-code",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en-GB">
      <head>
        <link rel="icon" href="/favicon.ico" sizes="any" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
        {process.env.NEXT_PUBLIC_PLAUSIBLE_DOMAIN && (
          <script
            defer
            data-domain={process.env.NEXT_PUBLIC_PLAUSIBLE_DOMAIN}
            src="https://plausible.io/js/script.js"
          />
        )}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "WebApplication",
              name: "VeriCar",
              url: siteUrl,
              description:
                "Free UK vehicle check tool. MOT history, mileage clocking detection, ULEZ compliance, finance, stolen, and write-off checks using official DVLA & DVSA data.",
              applicationCategory: "UtilitiesApplication",
              operatingSystem: "Web",
              offers: [
                {
                  "@type": "Offer",
                  name: "Free Vehicle Check",
                  price: "0",
                  priceCurrency: "GBP",
                  description:
                    "Free MOT history, tax status, mileage analysis, ULEZ compliance",
                },
                {
                  "@type": "Offer",
                  name: "Premium Check",
                  price: "9.99",
                  priceCurrency: "GBP",
                  description:
                    "Full provenance check including finance, stolen, write-off, salvage, valuation, keeper history and plate-change history",
                },
                {
                  "@type": "Offer",
                  name: "EV Health Check",
                  price: "8.99",
                  priceCurrency: "GBP",
                  description:
                    "Battery health score, real-world range, charging costs, and lifespan prediction for electric vehicles",
                },
                {
                  "@type": "Offer",
                  name: "EV Complete",
                  price: "13.99",
                  priceCurrency: "GBP",
                  description:
                    "Everything in EV Health Check plus finance, stolen, write-off, valuation, and keeper history",
                },
              ],
              aggregateRating: {
                "@type": "AggregateRating",
                ratingValue: "4.8",
                ratingCount: "1",
                bestRating: "5",
              },
            }),
          }}
        />
      </head>
      <body>
        <PostHogProvider>{children}</PostHogProvider>
      </body>
    </html>
  );
}
