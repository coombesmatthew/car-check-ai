import { Metadata } from "next";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import EVPageContent from "@/components/ev/EVPageContent";

export const metadata: Metadata = {
  title: "EV Health Check UK | Range & Degradation Analysis | VeriCar",
  description:
    "Check your electric car's battery health, real-world range, and charging costs. The UK's most comprehensive used EV check using ClearWatt, EV Database, and AutoPredict data.",
  keywords: [
    "EV battery health check",
    "electric car check",
    "EV range estimate",
    "battery degradation",
    "used electric car",
    "EV health check UK",
    "electric vehicle check",
    "EV battery test",
    "ClearWatt",
    "used EV check",
    "EV charging costs",
    "electric car range",
  ],
  openGraph: {
    title: "EV Health Check UK | VeriCar",
    description:
      "Check your electric car's battery health, real-world range, and charging costs. Instant results using official DVLA data plus specialist EV analytics.",
    type: "website",
    locale: "en_GB",
  },
};

const faqItems = [
  {
    question: "How do you check EV battery health?",
    answer:
      "We use ClearWatt data to estimate real-world range retention, then derive a battery health score (0-100) based on how much range the battery has lost compared to when it was new. This is combined with MOT mileage data and vehicle age for a comprehensive assessment.",
  },
  {
    question: "What electric vehicles can you check?",
    answer:
      "Any UK-registered battery electric vehicle (BEV) or plug-in hybrid (PHEV). We detect the vehicle type automatically from DVLA data. If you enter a petrol or diesel registration, we'll let you know and offer a standard car check instead.",
  },
  {
    question: "How accurate is the range estimate?",
    answer:
      "Our range estimates use ClearWatt's real-world data, which accounts for battery degradation, temperature, and driving style. They're typically more realistic than the manufacturer's official WLTP figures, which are measured under ideal lab conditions.",
  },
  {
    question: "What's included in the free check?",
    answer:
      "The free EV check confirms the vehicle is electric, shows MOT history, mileage verification, condition score, and tax status. Battery health, range estimates, charging costs, and the AI report require the paid check (£8.99).",
  },
  {
    question: "What's included in the £8.99 EV Health report?",
    answer:
      "The EV Health report adds: battery health score with degradation estimate, real-world range across different conditions, home vs rapid charging cost comparison, AI-predicted remaining lifespan, and a personalised AI verdict with buying advice. Delivered as a PDF to your email.",
  },
  {
    question: "What's included in the £13.99 EV Complete report?",
    answer:
      "EV Complete includes everything in EV Health plus full ownership checks: finance & outstanding debt, stolen vehicle check, write-off & salvage history, market valuation, and keeper & plate history. The ultimate pre-purchase check for any used EV.",
  },
  {
    question: "How much does it cost to charge an electric car?",
    answer:
      "It varies by vehicle and tariff. Our report calculates the exact cost for your specific car. As a guide, home charging (7kW) costs around 5-7p per mile, while public rapid chargers cost 12-16p per mile. Both are significantly cheaper than petrol at around 16p per mile.",
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
      name: "VeriCar EV Health Check",
      url: "https://vericar.co.uk/ev",
      applicationCategory: "UtilitiesApplication",
      operatingSystem: "Any",
      offers: [
        {
          "@type": "Offer",
          price: "0",
          priceCurrency: "GBP",
          description:
            "Free EV check with MOT history, mileage verification, and EV detection.",
        },
        {
          "@type": "Offer",
          price: "4.99",
          priceCurrency: "GBP",
          description:
            "Full Report with AI risk assessment, buy/avoid verdict, negotiation points, and PDF emailed.",
        },
        {
          "@type": "Offer",
          price: "8.99",
          priceCurrency: "GBP",
          description:
            "EV Health Check with battery health score, real-world range, charging costs, lifespan prediction, and AI verdict.",
        },
        {
          "@type": "Offer",
          price: "13.99",
          priceCurrency: "GBP",
          description:
            "EV Complete Check with everything in EV Health plus finance, stolen, write-off, valuation, and keeper history.",
        },
      ],
      description:
        "Check your electric car's battery health, real-world range, and charging costs. The UK's most comprehensive used EV check.",
    },
  ],
};

export default function EVPage() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-emerald-50/30 to-white flex flex-col">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />

      <Header />

      <EVPageContent />

      <Footer />
    </main>
  );
}
