import { Metadata } from "next";
import Header from "@/components/Header";
import Footer from "@/components/Footer";

export const metadata: Metadata = {
  title: "Privacy Policy | VeriCar",
  description: "VeriCar privacy policy — how we collect, use, and protect your data.",
};

export default function PrivacyPage() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-50 to-white flex flex-col">
      <Header />

      <section className="mx-auto max-w-3xl px-4 py-16 w-full flex-1">
        <h1 className="text-3xl font-bold text-slate-900 mb-2">Privacy Policy</h1>
        <p className="text-sm text-slate-400 mb-8">Last updated: April 2026</p>

        <div className="prose prose-slate max-w-none space-y-6 text-sm text-slate-600 leading-relaxed">

          <h2 className="text-lg font-semibold text-slate-900 mt-8">1. Who we are</h2>
          <p>
            VeriCar (&ldquo;we&rdquo;, &ldquo;us&rdquo;, &ldquo;our&rdquo;) provides an online vehicle checking
            service at vericar.co.uk. VeriCar is operated by Matthew Coombes, a sole trader based in
            the United Kingdom, and is the data controller for the personal information we process.
          </p>
          <p>
            For any privacy-related questions, contact{" "}
            <a href="mailto:matthew@vericar.co.uk" className="text-blue-600 underline">matthew@vericar.co.uk</a>.
          </p>

          <h2 className="text-lg font-semibold text-slate-900 mt-8">2. What data we collect</h2>
          <ul className="list-disc pl-5 space-y-1">
            <li>Vehicle registration numbers you search for</li>
            <li>Email address (when you purchase a paid report, or voluntarily provide one)</li>
            <li>Payment information — processed directly by Stripe; we receive confirmation and limited metadata only, never full card details</li>
            <li>Basic usage analytics (pages visited, device type, referring website)</li>
            <li>Server logs (IP address, request timestamps) for security and troubleshooting</li>
          </ul>

          <h2 className="text-lg font-semibold text-slate-900 mt-8">3. How we use your data and lawful basis</h2>
          <p>
            Under UK GDPR we must have a lawful basis for each purpose of processing. Our purposes and bases are:
          </p>
          <ul className="list-disc pl-5 space-y-1">
            <li>
              <strong>Delivering the vehicle check service</strong> (running DVLA/DVSA/provenance queries,
              generating reports, emailing you the PDF) — <em>Performance of a contract</em> (UK GDPR Article 6(1)(b)).
            </li>
            <li>
              <strong>Taking payment</strong> — <em>Performance of a contract</em> (Article 6(1)(b)).
            </li>
            <li>
              <strong>Keeping payment and accounting records</strong> — <em>Legal obligation</em> (Article 6(1)(c)),
              specifically UK tax and record-keeping requirements.
            </li>
            <li>
              <strong>Improving our service, fixing bugs, preventing abuse</strong> (usage analytics, server logs) —
              <em> Legitimate interests</em> (Article 6(1)(f)). Our interest is in running a reliable, secure service;
              we balance this against your privacy by minimising data collected and retention.
            </li>
            <li>
              <strong>Customer support</strong> (responding to emails about your order) —
              <em> Legitimate interests</em> (Article 6(1)(f)) or <em>performance of a contract</em> depending on context.
            </li>
          </ul>
          <p>
            We do not currently send marketing emails. If we start, we will obtain your explicit consent
            (Article 6(1)(a)) and you will always be able to unsubscribe.
          </p>

          <h2 className="text-lg font-semibold text-slate-900 mt-8">4. Who we share data with (processors)</h2>
          <p>
            We share the minimum data necessary with the third-party services required to deliver our product.
            Each of these is a data processor acting on our instructions.
          </p>
          <ul className="list-disc pl-5 space-y-1">
            <li><strong>Stripe</strong> — payment processing (card details, billing email)</li>
            <li><strong>DVLA</strong> (Vehicle Enquiry Service) — vehicle lookups by VRM</li>
            <li><strong>DVSA</strong> (MOT History API) — MOT history lookups by VRM</li>
            <li><strong>Experian Automotive</strong> and other automotive data providers — provenance checks (finance, stolen, write-off, plate change) via our data partner</li>
            <li><strong>Anthropic</strong> — AI-generated report text (Claude API; we send vehicle data, not your email or payment info)</li>
            <li><strong>Resend</strong> — transactional email delivery (your email address + the report PDF)</li>
            <li><strong>Railway</strong> and <strong>Cloudflare</strong> — hosting and content delivery</li>
            <li><strong>Plausible Analytics</strong> or Google Analytics — aggregated usage statistics (see &ldquo;Cookies and analytics&rdquo; below)</li>
          </ul>
          <p>We do not sell your personal data. We do not share data with advertisers or data brokers.</p>

          <h2 className="text-lg font-semibold text-slate-900 mt-8">5. International transfers</h2>
          <p>
            Some of our processors are based outside the UK. Where your personal data is transferred outside
            the UK, we rely on the following safeguards:
          </p>
          <ul className="list-disc pl-5 space-y-1">
            <li><strong>EU/EEA transfers</strong> — covered by the UK&apos;s adequacy decision, which recognises the EU as providing an equivalent standard of data protection.</li>
            <li>
              <strong>US transfers</strong> (Stripe, Anthropic, Resend, Cloudflare, Railway) — covered by the UK
              International Data Transfer Agreement, UK Addendum to the EU Standard Contractual Clauses, or the
              UK-US Data Bridge, depending on the processor.
            </li>
          </ul>
          <p>
            You can request more information about the specific safeguards for any transfer by contacting us.
          </p>

          <h2 className="text-lg font-semibold text-slate-900 mt-8">6. Data retention</h2>
          <p>We keep personal data only as long as we need it. Our retention periods are:</p>
          <ul className="list-disc pl-5 space-y-1">
            <li><strong>Payment records</strong> — 6 years from the end of the tax year, to comply with UK tax law (HMRC).</li>
            <li><strong>Email addresses tied to a paid report</strong> — up to 2 years from last purchase, for customer support and refund handling.</li>
            <li><strong>Vehicle check results (VRM + API responses)</strong> — up to 12 months, for debugging and service improvement. VRMs are not stored alongside personally identifying information except where you also made a payment.</li>
            <li><strong>Server logs</strong> — 90 days.</li>
            <li><strong>Aggregated analytics</strong> — up to 14 months (anonymised where possible).</li>
          </ul>
          <p>
            You can request earlier deletion of your data at any time (see &ldquo;Your rights&rdquo; below),
            subject to any legal retention requirements we are bound by.
          </p>

          <h2 className="text-lg font-semibold text-slate-900 mt-8">7. Cookies and analytics</h2>
          <p>
            We use a minimal set of cookies and tracking technologies:
          </p>
          <ul className="list-disc pl-5 space-y-1">
            <li><strong>Essential cookies</strong> — required to operate the site, process payments, and maintain session state. These do not require your consent.</li>
            <li>
              <strong>Analytics</strong> — we use a privacy-respecting analytics tool (Plausible Analytics,
              which does not use cookies and does not track across sites) or Google Analytics 4 with
              IP anonymisation. Analytics data is aggregated and does not identify you personally.
            </li>
          </ul>
          <p>
            We do not use advertising cookies, cross-site trackers, or share data with advertising networks.
          </p>

          <h2 className="text-lg font-semibold text-slate-900 mt-8">8. Automated decision-making</h2>
          <p>
            We do <strong>not</strong> use automated decision-making that produces legal effects or
            similarly significant effects concerning you (UK GDPR Article 22). AI-generated report text
            is informational content and does not make decisions about you as an individual.
          </p>

          <h2 className="text-lg font-semibold text-slate-900 mt-8">9. Children</h2>
          <p>
            VeriCar is not directed at children under the age of 18. We do not knowingly collect personal
            data from under-18s. If you believe a child has provided us with personal data, please contact
            us and we will delete it.
          </p>

          <h2 className="text-lg font-semibold text-slate-900 mt-8">10. Data security</h2>
          <p>
            We take appropriate technical and organisational measures to protect your personal data,
            including encryption in transit (HTTPS/TLS), encrypted storage, access controls, rate limiting,
            and routine security updates. No system is perfectly secure — if we become aware of a data
            breach affecting your personal information, we will notify you and the ICO as required by law.
          </p>

          <h2 className="text-lg font-semibold text-slate-900 mt-8">11. Your rights</h2>
          <p>Under UK GDPR, you have the right to:</p>
          <ul className="list-disc pl-5 space-y-1">
            <li>Access a copy of the personal data we hold about you</li>
            <li>Rectify inaccurate or incomplete personal data</li>
            <li>Erase your personal data (&ldquo;right to be forgotten&rdquo;), subject to legal retention requirements</li>
            <li>Restrict or object to our processing of your data</li>
            <li>Data portability (receive your data in a structured, machine-readable format)</li>
            <li>Withdraw consent, where processing is based on consent</li>
          </ul>
          <p>
            To exercise any of these rights, email{" "}
            <a href="mailto:matthew@vericar.co.uk" className="text-blue-600 underline">matthew@vericar.co.uk</a>.
            We will respond within one month.
          </p>
          <p>
            You also have the right to complain to the Information Commissioner&apos;s Office (the UK data
            protection regulator) if you believe we are handling your data incorrectly. You can contact
            the ICO at{" "}
            <a
              href="https://ico.org.uk"
              className="text-blue-600 underline"
              target="_blank"
              rel="noopener noreferrer"
            >
              ico.org.uk
            </a>{" "}
            or on 0303 123 1113. We would, however, appreciate the chance to resolve any concerns directly first.
          </p>

          <h2 className="text-lg font-semibold text-slate-900 mt-8">12. Changes to this policy</h2>
          <p>
            We may update this Privacy Policy from time to time. The latest version will always be
            published on this page with the updated date. Material changes will be highlighted where
            reasonably possible.
          </p>

          <h2 className="text-lg font-semibold text-slate-900 mt-8">13. Contact</h2>
          <p>
            For any privacy-related questions, data access requests, or other queries about how we
            handle your information, please email{" "}
            <a href="mailto:matthew@vericar.co.uk" className="text-blue-600 underline">matthew@vericar.co.uk</a>.
          </p>

        </div>
      </section>

      <Footer />
    </main>
  );
}
