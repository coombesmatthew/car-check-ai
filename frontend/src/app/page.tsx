import { Metadata } from "next";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import HomeContent from "@/components/HomeContent";

export const metadata: Metadata = {
  title:
    "Free Car Check UK | Finance, Stolen, MOT & Valuation | VeriCar",
  description:
    "Free instant MOT history, mileage clocking detection, and ULEZ check using official DVLA & DVSA data. Upgrade for finance, stolen, write-off, and valuation checks. No signup required.",
  keywords: [
    "car check",
    "free car check",
    "MOT history",
    "mileage check",
    "clocking detection",
    "ULEZ check",
    "vehicle check UK",
    "HPI alternative",
    "used car check",
    "finance check",
    "stolen check",
    "write off check",
    "car valuation",
    "free HPI check",
  ],
  openGraph: {
    title: "Free Car Check UK | MOT, Mileage & ULEZ | VeriCar",
    description:
      "Free MOT history, mileage clocking detection, and ULEZ check. Upgrade for finance, stolen, write-off, and valuation checks. No signup required.",
    type: "website",
    locale: "en_GB",
  },
};

const faqItems = [
  {
    question: "Is this car check really free?",
    answer:
      "Yes. Our free check uses official DVLA and DVSA government data at zero cost. There are no hidden charges or signup required.",
  },
  {
    question: "How does clocking detection work?",
    answer:
      "We analyse mileage readings recorded at every MOT test. If the mileage drops between tests or shows improbable jumps, we flag it as a potential clocking risk.",
  },
  {
    question: "What data sources do you use?",
    answer:
      "We use the DVLA Vehicle Enquiry Service for vehicle identity and tax data, and the DVSA MOT History API for test results and mileage readings. Both are official UK government data sources.",
  },
  {
    question:
      "What's the difference between the free check and the Premium check?",
    answer:
      "The free check gives you MOT history, mileage analysis, clocking detection, condition score, and ULEZ compliance. The \u00A39.99 Premium check adds finance / outstanding-debt check, stolen-vehicle register, insurance write-off history, salvage auction records, market valuation, plate-change history, and a full keeper-history timeline.",
  },
  {
    question: "How accurate is the condition score?",
    answer:
      "The condition score is based on the vehicle's complete MOT history, including defect severity, failure rate, mileage, and advisory trends. It provides a good indication but should be used alongside a physical inspection.",
  },
  {
    question: "Do you check for outstanding finance or stolen vehicles?",
    answer:
      "Yes! Our Premium check (\u00A39.99) includes finance outstanding, stolen vehicle, insurance write-off, salvage history, plate changes, keeper history, and a market valuation \u2014 all powered by Experian data.",
  },
];

const jsonLd = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "FAQPage",
      mainEntity: faqItems.map((item) => ({
        "@type": "Question",
        name: item.question,
        acceptedAnswer: {
          "@type": "Answer",
          text: item.answer,
        },
      })),
    },
    {
      "@type": "WebApplication",
      name: "VeriCar",
      url: "https://vericar.co.uk",
      applicationCategory: "UtilitiesApplication",
      operatingSystem: "Any",
      offers: [
        {
          "@type": "Offer",
          price: "0",
          priceCurrency: "GBP",
          description:
            "Free vehicle check with MOT history, mileage verification, condition scoring, and ULEZ compliance.",
        },
        {
          "@type": "Offer",
          price: "9.99",
          priceCurrency: "GBP",
          description:
            "Premium vehicle check: finance, stolen, write-off, salvage, market valuation, keeper history, plate changes.",
        },
      ],
      description:
        "Free instant UK vehicle check using official DVLA and DVSA data. MOT history, mileage clocking detection, condition scoring, and ULEZ compliance.",
    },
    {
      "@type": "Organization",
      name: "VeriCar",
      url: "https://vericar.co.uk",
      description:
        "AI-powered vehicle checks using official UK government data.",
    },
  ],
};

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-50 to-white flex flex-col">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />

      <Header />

      <HomeContent />

      <Footer />
    </main>
  );
}
