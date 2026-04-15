"use client";

import { useState } from "react";
import SearchSection from "@/components/SearchSection";

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
      "What's the difference between the free check and the full report?",
    answer:
      "The free check gives you MOT history, mileage analysis, clocking detection, condition score, and ULEZ compliance. The \u00A34.99 full report adds an AI-powered buyer's verdict, estimated repair costs, negotiation points, and questions to ask the seller.",
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

export default function HomeContent() {
  const [hasResult, setHasResult] = useState(false);

  return (
    <>
      <SearchSection onCheckComplete={setHasResult} />

      {!hasResult && (
        <>
          {/* Feature Cards */}
          <section className="bg-white border-t border-slate-100 py-16">
            <div className="mx-auto max-w-5xl px-4">
              <div className="text-center mb-10">
                <h2 className="text-2xl font-bold text-slate-900">
                  Everything you need to buy with confidence
                </h2>
                <p className="text-slate-500 mt-2">
                  Free MOT &amp; mileage checks, plus paid tiers for AI verdicts and full history
                </p>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-slate-50 rounded-xl p-6 border border-slate-100">
                  <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center mb-4">
                    <svg
                      className="w-5 h-5 text-blue-600"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      strokeWidth={1.5}
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"
                      />
                    </svg>
                  </div>
                  <h3 className="font-semibold text-slate-900 mb-2">MOT History</h3>
                  <p className="text-sm text-slate-500 leading-relaxed">
                    Full test history, pass/fail rates, advisory tracking, and
                    recurring issue detection.
                  </p>
                </div>
                <div className="bg-slate-50 rounded-xl p-6 border border-slate-100">
                  <div className="w-10 h-10 rounded-lg bg-amber-100 flex items-center justify-center mb-4">
                    <svg
                      className="w-5 h-5 text-amber-600"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      strokeWidth={1.5}
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                  </div>
                  <h3 className="font-semibold text-slate-900 mb-2">
                    Mileage Verification
                  </h3>
                  <p className="text-sm text-slate-500 leading-relaxed">
                    AI-powered clocking detection across all MOT readings. Spot
                    rollbacks and anomalies instantly.
                  </p>
                </div>
                <div className="bg-slate-50 rounded-xl p-6 border border-slate-100">
                  <div className="w-10 h-10 rounded-lg bg-red-100 flex items-center justify-center mb-4">
                    <svg
                      className="w-5 h-5 text-red-600"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      strokeWidth={1.5}
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z"
                      />
                    </svg>
                  </div>
                  <h3 className="font-semibold text-slate-900 mb-2">
                    Finance &amp; Stolen
                    <span className="ml-1.5 text-xs font-medium text-purple-600 bg-purple-50 px-1.5 py-0.5 rounded">Premium</span>
                  </h3>
                  <p className="text-sm text-slate-500 leading-relaxed">
                    Outstanding finance, stolen vehicle, and insurance write-off
                    checks to avoid costly surprises.
                  </p>
                </div>
                <div className="bg-slate-50 rounded-xl p-6 border border-slate-100">
                  <div className="w-10 h-10 rounded-lg bg-emerald-100 flex items-center justify-center mb-4">
                    <svg
                      className="w-5 h-5 text-emerald-600"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      strokeWidth={1.5}
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                  </div>
                  <h3 className="font-semibold text-slate-900 mb-2">
                    ULEZ &amp; Tax
                  </h3>
                  <p className="text-sm text-slate-500 leading-relaxed">
                    Live tax status, MOT validity, and London ULEZ compliance check
                    for clean air zones.
                  </p>
                </div>
                <div className="bg-slate-50 rounded-xl p-6 border border-slate-100">
                  <div className="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center mb-4">
                    <svg
                      className="w-5 h-5 text-purple-600"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      strokeWidth={1.5}
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M2.25 18.75a60.07 60.07 0 0115.797 2.101c.727.198 1.453-.342 1.453-1.096V18.75M3.75 4.5v.75A.75.75 0 013 6h-.75m0 0v-.375c0-.621.504-1.125 1.125-1.125H20.25M2.25 6v9m18-10.5v.75c0 .414.336.75.75.75h.75m-1.5-1.5h.375c.621 0 1.125.504 1.125 1.125v9.75c0 .621-.504 1.125-1.125 1.125h-.375m1.5-1.5H21a.75.75 0 00-.75.75v.75m0 0H3.75m0 0h-.375a1.125 1.125 0 01-1.125-1.125V15m1.5 1.5v-.75A.75.75 0 003 15h-.75M15 10.5a3 3 0 11-6 0 3 3 0 016 0zm3 0h.008v.008H18V10.5zm-12 0h.008v.008H6V10.5z"
                      />
                    </svg>
                  </div>
                  <h3 className="font-semibold text-slate-900 mb-2">
                    Vehicle Valuation
                    <span className="ml-1.5 text-xs font-medium text-purple-600 bg-purple-50 px-1.5 py-0.5 rounded">Premium</span>
                  </h3>
                  <p className="text-sm text-slate-500 leading-relaxed">
                    Private sale, dealer, and trade-in valuations so you know
                    exactly what it&apos;s worth.
                  </p>
                </div>
                {/* EV Battery Health */}
                <div className="bg-gradient-to-br from-emerald-50 to-emerald-100 rounded-xl p-6 border border-emerald-200">
                  <div className="w-10 h-10 rounded-lg bg-emerald-200 flex items-center justify-center mb-4">
                    <svg className="w-5 h-5 text-emerald-700" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
                    </svg>
                  </div>
                  <h3 className="font-semibold text-slate-900 mb-2">
                    EV Battery Health
                    <span className="ml-1.5 text-xs font-medium text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded">NEW</span>
                  </h3>
                  <p className="text-sm text-slate-500 leading-relaxed">
                    Buying electric? Check battery degradation, real-world range, and charging costs before you buy.
                  </p>
                  <a href="/ev" className="inline-flex items-center gap-1 text-sm font-medium text-emerald-600 mt-3 hover:text-emerald-700 transition-colors">
                    Try EV Health Check
                    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
                    </svg>
                  </a>
                </div>
              </div>
            </div>
          </section>

          {/* Trust Signals */}
          <section className="py-12">
            <div className="mx-auto max-w-5xl px-4">
              <div className="flex flex-col md:flex-row items-center justify-center gap-8 md:gap-16 text-center">
                <div>
                  <p className="text-3xl font-bold text-slate-900">5 Reports</p>
                  <p className="text-sm text-slate-500 mt-1">Free, Basic, Premium &amp; EV</p>
                </div>
                <div className="hidden md:block w-px h-12 bg-slate-200" />
                <div>
                  <p className="text-3xl font-bold text-slate-900">DVLA + DVSA</p>
                  <p className="text-sm text-slate-500 mt-1">
                    Official government data
                  </p>
                </div>
                <div className="hidden md:block w-px h-12 bg-slate-200" />
                <div>
                  <p className="text-3xl font-bold text-slate-900">Instant</p>
                  <p className="text-sm text-slate-500 mt-1">
                    Results in seconds
                  </p>
                </div>
                <div className="hidden md:block w-px h-12 bg-slate-200" />
                <div>
                  <p className="text-3xl font-bold text-slate-900">Free</p>
                  <p className="text-sm text-slate-500 mt-1">
                    No signup or payment
                  </p>
                </div>
              </div>
            </div>
          </section>

          {/* How It Works */}
          <section id="how-it-works" className="py-16">
            <div className="mx-auto max-w-5xl px-4">
              <div className="text-center mb-10">
                <h2 className="text-2xl font-bold text-slate-900">How it works</h2>
                <p className="text-slate-500 mt-2">
                  Three simple steps to a smarter car purchase
                </p>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div className="text-center">
                  <div className="w-12 h-12 rounded-full bg-blue-600 text-white font-bold text-lg flex items-center justify-center mx-auto mb-4">
                    1
                  </div>
                  <h3 className="font-semibold text-slate-900 mb-2">
                    Enter Registration
                  </h3>
                  <p className="text-sm text-slate-500">
                    Type any UK vehicle registration number into the search box
                    above.
                  </p>
                </div>
                <div className="text-center">
                  <div className="w-12 h-12 rounded-full bg-blue-600 text-white font-bold text-lg flex items-center justify-center mx-auto mb-4">
                    2
                  </div>
                  <h3 className="font-semibold text-slate-900 mb-2">
                    Get Free Report
                  </h3>
                  <p className="text-sm text-slate-500">
                    Instantly receive MOT history, mileage analysis, tax status, and
                    a condition score.
                  </p>
                </div>
                <div className="text-center">
                  <div className="w-12 h-12 rounded-full bg-emerald-600 text-white font-bold text-lg flex items-center justify-center mx-auto mb-4">
                    3
                  </div>
                  <h3 className="font-semibold text-slate-900 mb-2">
                    Upgrade for AI Verdict
                  </h3>
                  <p className="text-sm text-slate-500">
                    Get a personalised buy/negotiate/avoid recommendation with
                    negotiation points.
                  </p>
                </div>
              </div>
            </div>
          </section>

          {/* Comparison Table */}
          <section
            id="full-report"
            className="bg-white border-t border-slate-100 py-16"
          >
            <div className="mx-auto max-w-3xl px-4">
              <div className="text-center mb-10">
                <h2 className="text-2xl font-bold text-slate-900">
                  Choose your check
                </h2>
                <p className="text-slate-500 mt-2">
                  Start free. Upgrade if you need the full picture.
                </p>
              </div>
              {/* Car checks row */}
              <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">Car Checks</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Free tier */}
                <div className="border border-slate-200 rounded-xl p-6">
                  <div className="mb-4">
                    <span className="text-sm font-semibold text-slate-500 uppercase tracking-wide">Free</span>
                    <div className="mt-1">
                      <span className="text-3xl font-bold text-slate-900">&pound;0</span>
                    </div>
                  </div>
                  <ul className="space-y-2.5 mb-6">
                    {["DVLA Vehicle Data", "Full MOT History", "Mileage & Clocking Detection", "Condition Score", "ULEZ & Tax Check", "Safety Rating"].map((item) => (
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

                {/* Basic tier */}
                <div className="border-2 border-blue-600 rounded-xl p-6 pt-8 relative">
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                    <span className="bg-blue-600 text-white text-xs font-semibold px-3 py-1 rounded-full whitespace-nowrap">Most Popular</span>
                  </div>
                  <div className="mb-4">
                    <span className="text-sm font-semibold text-blue-600 uppercase tracking-wide">Full Report</span>
                    <div className="mt-1">
                      <span className="text-3xl font-bold text-slate-900">&pound;4.99</span>
                    </div>
                  </div>
                  <ul className="space-y-2.5 mb-6">
                    {["Everything in Free", "AI Risk Assessment", "Buy/Avoid Verdict", "Negotiation Points", "PDF Report & Email"].map((item, i) => (
                      <li key={item} className="flex items-center gap-2 text-sm text-slate-700">
                        <svg className={`w-4 h-4 flex-shrink-0 ${i === 0 ? "text-emerald-500" : "text-blue-600"}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                        </svg>
                        <span className={i > 0 ? "font-medium" : ""}>{item}</span>
                      </li>
                    ))}
                  </ul>
                  <a href="#search" className="block text-center py-2.5 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors text-sm">
                    Get Full Report &mdash; &pound;4.99
                  </a>
                </div>

                {/* Premium tier */}
                <div className="border border-slate-200 rounded-xl p-6">
                  <div className="mb-4">
                    <span className="text-sm font-semibold text-purple-600 uppercase tracking-wide">Premium</span>
                    <div className="mt-1">
                      <span className="text-3xl font-bold text-slate-900">&pound;9.99</span>
                    </div>
                  </div>
                  <ul className="space-y-2.5 mb-6">
                    {["Everything in Full Report", "Finance & Debt Check", "Stolen Vehicle Check", "Write-off & Salvage History", "Market Valuation", "Plate & Keeper History"].map((item, i) => (
                      <li key={item} className="flex items-center gap-2 text-sm text-slate-700">
                        <svg className={`w-4 h-4 flex-shrink-0 ${i === 0 ? "text-emerald-500" : "text-purple-600"}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                        </svg>
                        <span className={i > 0 ? "font-medium" : ""}>{item}</span>
                      </li>
                    ))}
                  </ul>
                  <a href="#search" className="block text-center py-2.5 bg-purple-600 text-white font-semibold rounded-lg hover:bg-purple-700 transition-colors text-sm">
                    Get Premium &mdash; &pound;9.99
                  </a>
                </div>
              </div>

              {/* EV checks row */}
              <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mt-10 mb-4 flex items-center gap-2">
                <svg className="w-4 h-4 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" /></svg>
                EV Checks
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-2xl mx-auto">
                {/* EV Health tier */}
                <div className="border-2 border-emerald-600 rounded-xl p-6 pt-8 relative">
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                    <span className="bg-emerald-600 text-white text-xs font-semibold px-3 py-1 rounded-full whitespace-nowrap flex items-center gap-1">
                      <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" /></svg>
                      Battery Focus
                    </span>
                  </div>
                  <div className="mb-4">
                    <span className="text-sm font-semibold text-emerald-600 uppercase tracking-wide">EV Health Check</span>
                    <div className="mt-1">
                      <span className="text-3xl font-bold text-slate-900">&pound;8.99</span>
                    </div>
                  </div>
                  <ul className="space-y-2.5 mb-6">
                    {["Free car check included", "Battery Health Score", "Real-World Range", "Charging Cost Comparison", "Lifespan Prediction", "AI Expert Verdict"].map((item, i) => (
                      <li key={item} className="flex items-center gap-2 text-sm text-slate-700">
                        <svg className={`w-4 h-4 flex-shrink-0 ${i === 0 ? "text-emerald-500" : "text-emerald-600"}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                        </svg>
                        <span className={i > 0 ? "font-medium" : ""}>{item}</span>
                      </li>
                    ))}
                  </ul>
                  <a href="/ev" className="block text-center py-2.5 bg-emerald-600 text-white font-semibold rounded-lg hover:bg-emerald-700 transition-colors text-sm">
                    Get EV Health Check &mdash; &pound;8.99
                  </a>
                </div>

                {/* EV Complete tier */}
                <div className="border-2 border-teal-600 rounded-xl p-6 pt-8 relative">
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                    <span className="bg-teal-600 text-white text-xs font-semibold px-3 py-1 rounded-full whitespace-nowrap">Best Value</span>
                  </div>
                  <div className="mb-4">
                    <span className="text-sm font-semibold text-teal-600 uppercase tracking-wide">EV Complete</span>
                    <div className="mt-1">
                      <span className="text-3xl font-bold text-slate-900">&pound;14.99</span>
                    </div>
                  </div>
                  <ul className="space-y-2.5 mb-6">
                    {["Everything in EV Health", "Finance & Debt Check", "Stolen Vehicle Check", "Write-off & Salvage History", "Market Valuation", "Plate & Keeper History"].map((item, i) => (
                      <li key={item} className="flex items-center gap-2 text-sm text-slate-700">
                        <svg className={`w-4 h-4 flex-shrink-0 ${i === 0 ? "text-emerald-500" : "text-teal-600"}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                        </svg>
                        <span className={i > 0 ? "font-medium" : ""}>{item}</span>
                      </li>
                    ))}
                  </ul>
                  <a href="/ev" className="block text-center py-2.5 bg-teal-600 text-white font-semibold rounded-lg hover:bg-teal-700 transition-colors text-sm">
                    Get EV Complete &mdash; &pound;14.99
                  </a>
                </div>
              </div>
            </div>
          </section>

          {/* FAQ Section */}
          <section id="faq" className="py-16">
            <div className="mx-auto max-w-3xl px-4">
              <div className="text-center mb-10">
                <h2 className="text-2xl font-bold text-slate-900">
                  Frequently Asked Questions
                </h2>
                <p className="text-slate-500 mt-2">
                  Everything you need to know about our vehicle checks
                </p>
              </div>
              <div className="space-y-3">
                {faqItems.map((item) => (
                  <details
                    key={item.question}
                    className="group border border-slate-200 rounded-lg bg-white"
                  >
                    <summary className="flex items-center justify-between cursor-pointer px-6 py-4 text-left font-medium text-slate-900 hover:bg-slate-50 transition-colors rounded-lg [&::-webkit-details-marker]:hidden list-none">
                      <span>{item.question}</span>
                      <svg
                        className="w-5 h-5 text-slate-400 flex-shrink-0 ml-4 transition-transform group-open:rotate-180"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                        strokeWidth={2}
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          d="M19.5 8.25l-7.5 7.5-7.5-7.5"
                        />
                      </svg>
                    </summary>
                    <div className="px-6 pb-4">
                      <p className="text-sm text-slate-600 leading-relaxed">
                        {item.answer}
                      </p>
                    </div>
                  </details>
                ))}
              </div>
            </div>
          </section>
        </>
      )}
    </>
  );
}
