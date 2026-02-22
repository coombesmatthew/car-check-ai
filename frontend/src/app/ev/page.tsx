import { Metadata } from "next";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import EVSearchSection from "@/components/ev/EVSearchSection";

export const metadata: Metadata = {
  title: "EV Battery Health Check UK | Range & Degradation Analysis | VeriCar",
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
    title: "EV Battery Health Check UK | VeriCar",
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
      "The free EV check confirms the vehicle is electric, shows MOT history, mileage verification, condition score, and tax status. Battery health, range estimates, charging costs, and the AI report require the paid check (£7.99).",
  },
  {
    question: "What's included in the £7.99 paid report?",
    answer:
      "The full report adds: battery health score with degradation estimate, real-world range across different conditions, home vs rapid charging cost comparison, AI-predicted remaining lifespan, and a personalised AI verdict with buying advice. Delivered as a PDF to your email.",
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
          price: "7.99",
          priceCurrency: "GBP",
          description:
            "Full EV Health Check with battery health score, real-world range, charging costs, lifespan prediction, and AI verdict.",
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

      <EVSearchSection />

      {/* Feature Cards */}
      <section className="bg-white border-t border-slate-100 py-16">
        <div className="mx-auto max-w-5xl px-4">
          <div className="text-center mb-10">
            <h2 className="text-2xl font-bold text-slate-900">
              Everything you need to buy a used EV with confidence
            </h2>
            <p className="text-slate-500 mt-2">
              Battery health, real-world range, and charging costs — all in one check
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-emerald-50 rounded-xl p-6 border border-emerald-100">
              <div className="w-10 h-10 rounded-lg bg-emerald-100 flex items-center justify-center mb-4">
                <svg className="w-5 h-5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M21 10.5h.375c.621 0 1.125.504 1.125 1.125v2.25c0 .621-.504 1.125-1.125 1.125H21M3.75 18h15A2.25 2.25 0 0021 15.75v-6a2.25 2.25 0 00-2.25-2.25h-15A2.25 2.25 0 001.5 9.75v6A2.25 2.25 0 003.75 18z" />
                </svg>
              </div>
              <h3 className="font-semibold text-slate-900 mb-2">Battery Health Score</h3>
              <p className="text-sm text-slate-500 leading-relaxed">
                0-100 score with A-F grade based on real-world degradation data. Know exactly how much battery life remains.
              </p>
            </div>
            <div className="bg-emerald-50 rounded-xl p-6 border border-emerald-100">
              <div className="w-10 h-10 rounded-lg bg-emerald-100 flex items-center justify-center mb-4">
                <svg className="w-5 h-5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 6.75V15m6-6v8.25m.503 3.498l4.875-2.437c.381-.19.622-.58.622-1.006V4.82c0-.836-.88-1.38-1.628-1.006l-3.869 1.934c-.317.159-.69.159-1.006 0L9.503 3.252a1.125 1.125 0 00-1.006 0L3.622 5.689C3.24 5.88 3 6.27 3 6.695V19.18c0 .836.88 1.38 1.628 1.006l3.869-1.934c.317-.159.69-.159 1.006 0l4.994 2.497c.317.158.69.158 1.006 0z" />
                </svg>
              </div>
              <h3 className="font-semibold text-slate-900 mb-2">Real-World Range</h3>
              <p className="text-sm text-slate-500 leading-relaxed">
                Actual range estimates across summer, winter, city, and motorway conditions. Not the manufacturer&apos;s lab numbers.
              </p>
            </div>
            <div className="bg-emerald-50 rounded-xl p-6 border border-emerald-100">
              <div className="w-10 h-10 rounded-lg bg-emerald-100 flex items-center justify-center mb-4">
                <svg className="w-5 h-5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 18.75a60.07 60.07 0 0115.797 2.101c.727.198 1.453-.342 1.453-1.096V18.75M3.75 4.5v.75A.75.75 0 013 6h-.75m0 0v-.375c0-.621.504-1.125 1.125-1.125H20.25M2.25 6v9m18-10.5v.75c0 .414.336.75.75.75h.75m-1.5-1.5h.375c.621 0 1.125.504 1.125 1.125v9.75c0 .621-.504 1.125-1.125 1.125h-.375m1.5-1.5H21a.75.75 0 00-.75.75v.75m0 0H3.75m0 0h-.375a1.125 1.125 0 01-1.125-1.125V15m1.5 1.5v-.75A.75.75 0 003 15h-.75M15 10.5a3 3 0 11-6 0 3 3 0 016 0zm3 0h.008v.008H18V10.5zm-12 0h.008v.008H6V10.5z" />
                </svg>
              </div>
              <h3 className="font-semibold text-slate-900 mb-2">Charging Costs</h3>
              <p className="text-sm text-slate-500 leading-relaxed">
                Home vs rapid charging comparison with exact costs for your vehicle. See how much you&apos;ll save vs petrol.
              </p>
            </div>
            <div className="bg-slate-50 rounded-xl p-6 border border-slate-100">
              <div className="w-10 h-10 rounded-lg bg-slate-100 flex items-center justify-center mb-4">
                <svg className="w-5 h-5 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="font-semibold text-slate-900 mb-2">Lifespan Prediction</h3>
              <p className="text-sm text-slate-500 leading-relaxed">
                AI-predicted remaining years and miles based on current condition, mileage, and battery data.
              </p>
            </div>
            <div className="bg-slate-50 rounded-xl p-6 border border-slate-100">
              <div className="w-10 h-10 rounded-lg bg-slate-100 flex items-center justify-center mb-4">
                <svg className="w-5 h-5 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                </svg>
              </div>
              <h3 className="font-semibold text-slate-900 mb-2">MOT &amp; Mileage</h3>
              <p className="text-sm text-slate-500 leading-relaxed">
                Full MOT history, mileage clocking detection, and condition scoring — included free in every check.
              </p>
            </div>
            <div className="bg-slate-50 rounded-xl p-6 border border-slate-100">
              <div className="w-10 h-10 rounded-lg bg-slate-100 flex items-center justify-center mb-4">
                <svg className="w-5 h-5 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456z" />
                </svg>
              </div>
              <h3 className="font-semibold text-slate-900 mb-2">AI Expert Verdict</h3>
              <p className="text-sm text-slate-500 leading-relaxed">
                Personalised BUY/NEGOTIATE/AVOID recommendation with specific negotiation points tailored to this vehicle.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="py-16">
        <div className="mx-auto max-w-5xl px-4">
          <div className="text-center mb-10">
            <h2 className="text-2xl font-bold text-slate-900">How it works</h2>
            <p className="text-slate-500 mt-2">Three steps to know if that used EV is worth buying</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-12 h-12 rounded-full bg-emerald-600 text-white font-bold text-lg flex items-center justify-center mx-auto mb-4">1</div>
              <h3 className="font-semibold text-slate-900 mb-2">Enter Registration</h3>
              <p className="text-sm text-slate-500">Type any UK electric vehicle registration. We&apos;ll confirm it&apos;s an EV automatically.</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 rounded-full bg-emerald-600 text-white font-bold text-lg flex items-center justify-center mx-auto mb-4">2</div>
              <h3 className="font-semibold text-slate-900 mb-2">Free Instant Check</h3>
              <p className="text-sm text-slate-500">Get MOT history, mileage verification, and condition score — completely free.</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 rounded-full bg-emerald-600 text-white font-bold text-lg flex items-center justify-center mx-auto mb-4">3</div>
              <h3 className="font-semibold text-slate-900 mb-2">Unlock Battery Report</h3>
              <p className="text-sm text-slate-500">For £7.99, get battery health, range estimates, charging costs, and AI verdict delivered to your email.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="bg-white border-t border-slate-100 py-16">
        <div className="mx-auto max-w-2xl px-4">
          <div className="text-center mb-10">
            <h2 className="text-2xl font-bold text-slate-900">Simple pricing</h2>
            <p className="text-slate-500 mt-2">Start free. Unlock the full battery analysis if you need it.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="border border-slate-200 rounded-xl p-6">
              <span className="text-sm font-semibold text-slate-500 uppercase tracking-wide">Free</span>
              <div className="mt-1 mb-4">
                <span className="text-3xl font-bold text-slate-900">&pound;0</span>
              </div>
              <ul className="space-y-2.5 mb-6">
                {["EV Detection", "MOT History", "Mileage Verification", "Condition Score", "Tax & ULEZ Status"].map((item) => (
                  <li key={item} className="flex items-center gap-2 text-sm text-slate-600">
                    <svg className="w-4 h-4 text-emerald-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                    </svg>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
              <a href="#search" className="block text-center py-2.5 border-2 border-slate-300 text-slate-700 font-semibold rounded-lg hover:bg-slate-50 transition-colors text-sm">
                Try Free Check
              </a>
            </div>
            <div className="border-2 border-emerald-600 rounded-xl p-6 relative">
              <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                <span className="bg-emerald-600 text-white text-xs font-semibold px-3 py-1 rounded-full">Recommended</span>
              </div>
              <span className="text-sm font-semibold text-emerald-600 uppercase tracking-wide">Full Report</span>
              <div className="mt-1 mb-4">
                <span className="text-3xl font-bold text-slate-900">&pound;7.99</span>
              </div>
              <ul className="space-y-2.5 mb-6">
                {["Everything in Free", "Battery Health Score", "Real-World Range", "Charging Cost Comparison", "Lifespan Prediction", "AI Expert Verdict", "PDF Report & Email"].map((item, i) => (
                  <li key={item} className="flex items-center gap-2 text-sm text-slate-700">
                    <svg className={`w-4 h-4 flex-shrink-0 ${i === 0 ? "text-emerald-500" : "text-emerald-600"}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                    </svg>
                    <span className={i > 0 ? "font-medium" : ""}>{item}</span>
                  </li>
                ))}
              </ul>
              <a href="#search" className="block text-center py-2.5 bg-emerald-600 text-white font-semibold rounded-lg hover:bg-emerald-700 transition-colors text-sm">
                Get EV Report &mdash; &pound;7.99
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section id="faq" className="py-16">
        <div className="mx-auto max-w-3xl px-4">
          <div className="text-center mb-10">
            <h2 className="text-2xl font-bold text-slate-900">Frequently Asked Questions</h2>
            <p className="text-slate-500 mt-2">Everything you need to know about our EV Health Check</p>
          </div>
          <div className="space-y-3">
            {faqItems.map((item) => (
              <details key={item.question} className="group border border-slate-200 rounded-lg bg-white">
                <summary className="flex items-center justify-between cursor-pointer px-6 py-4 text-left font-medium text-slate-900 hover:bg-slate-50 transition-colors rounded-lg [&::-webkit-details-marker]:hidden list-none">
                  <span>{item.question}</span>
                  <svg className="w-5 h-5 text-slate-400 flex-shrink-0 ml-4 transition-transform group-open:rotate-180" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
                  </svg>
                </summary>
                <div className="px-6 pb-4">
                  <p className="text-sm text-slate-600 leading-relaxed">{item.answer}</p>
                </div>
              </details>
            ))}
          </div>
        </div>
      </section>

      <Footer />
    </main>
  );
}
