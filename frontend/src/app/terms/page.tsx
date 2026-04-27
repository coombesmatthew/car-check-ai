import { Metadata } from "next";
import Header from "@/components/Header";
import Footer from "@/components/Footer";

export const metadata: Metadata = {
  title: "Terms of Service | VeriCar",
  description: "VeriCar terms of service — the rules governing use of our vehicle checking service.",
};

export default function TermsPage() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-50 to-white flex flex-col">
      <Header />

      <section className="mx-auto max-w-3xl px-4 py-16 w-full flex-1">
        <h1 className="text-3xl font-bold text-slate-900 mb-2">Terms of Service</h1>
        <p className="text-sm text-slate-400 mb-8">Last updated: April 2026</p>

        <div className="prose prose-slate max-w-none space-y-6 text-sm text-slate-600 leading-relaxed">

          <h2 className="text-lg font-semibold text-slate-900 mt-8">1. About VeriCar</h2>
          <p>
            VeriCar is operated by Matthew Coombes trading as VeriCar, a sole trader in the United Kingdom.
          </p>
          <p className="not-italic">
            <strong>Business address:</strong><br />
            1 Farm Close<br />
            Sunderland<br />
            Tyne and Wear<br />
            NE37 1EG
          </p>
          <p>
            <strong>Contact email:</strong>{" "}
            <a href="mailto:matthew@vericar.co.uk" className="text-blue-600 underline">matthew@vericar.co.uk</a>
          </p>
          <p>
            VeriCar provides vehicle history reports and summaries compiled from third-party data sources
            to help users make more informed decisions when purchasing a used vehicle.
          </p>

          <h2 className="text-lg font-semibold text-slate-900 mt-8">2. Our Service</h2>
          <p>
            VeriCar provides informational vehicle reports based on vehicle registration numbers and other
            publicly available or licensed data sources.
          </p>
          <p>Reports may include:</p>
          <ul className="list-disc pl-5 space-y-1">
            <li>DVLA vehicle details</li>
            <li>MOT history and test data</li>
            <li>Vehicle specifications</li>
            <li>Mileage records</li>
            <li>Provenance checks such as finance, theft, write-off records, and plate changes (where available)</li>
          </ul>
          <p>
            Our service provides information only and does not constitute mechanical, legal, or financial advice.
            Users should always carry out additional checks including a physical inspection, test drive, and
            independent professional assessment before purchasing a vehicle.
          </p>
          <p>
            VeriCar is intended for private consumer use only. It is <strong>not</strong> designed, licensed, or
            warranted for commercial, trade, dealer, wholesale, auction, or professional-intermediary use.
            Any reliance on our reports for commercial purposes is at the user&apos;s own risk and outside the
            scope of our service.
          </p>

          <h2 className="text-lg font-semibold text-slate-900 mt-8">3. Third-Party Data Sources</h2>
          <p>Vehicle data displayed in our reports is obtained from third-party sources including:</p>
          <ul className="list-disc pl-5 space-y-1">
            <li>DVLA Vehicle Enquiry Service</li>
            <li>DVSA MOT History API</li>
            <li>Experian Automotive</li>
            <li>Other automotive data providers and public databases</li>
          </ul>
          <p>VeriCar does not control these data sources and cannot guarantee that the information provided is accurate, complete, or up to date.</p>
          <ul className="list-disc pl-5 space-y-1">
            <li>Errors, omissions, delays, or outdated records may occur in third-party databases.</li>
            <li>VeriCar is not responsible for inaccuracies originating from third-party data providers.</li>
            <li>A report indicating no adverse history does not guarantee that a vehicle has never been stolen, written off, financed, damaged, or modified.</li>
          </ul>
          <p>
            <strong>Data may lag real-world events.</strong> Provenance records (including finance, stolen,
            and write-off markers) depend on third-party providers being notified and updating their systems.
            There may be a delay of days, weeks, or longer between a real-world event occurring and it
            appearing in our data. Our report reflects the data available at the moment it was generated;
            the absence of an adverse marker at the time of check does not guarantee one does not exist
            or will not appear later.
          </p>

          <h2 className="text-lg font-semibold text-slate-900 mt-8">4. Provenance and Experian Data</h2>
          <p>
            Certain provenance checks (including finance records, stolen vehicle registers, insurance
            write-offs, plate changes, keeper history, high-risk markers and previous-search history) are
            supplied by Experian Automotive under licence via our data partner. Sections of your report
            that draw on this data are individually marked &quot;Source: Experian&quot;.
          </p>
          <p>
            <strong>VeriCar does not currently offer a separate data accuracy guarantee on Experian-sourced
            data.</strong> Any reference to Experian within our reports identifies the supplier of the
            underlying data only. It does not constitute, extend, or underwrite any guarantee, warranty,
            or commitment that Experian may itself offer directly to its own commercial customers, and you
            should not interpret it as such.
          </p>
          <p>
            Your remedy in the event of an error or omission in Experian-sourced data is set out in
            Section 13 (Limitation of Liability). Experian-sourced data is otherwise subject to the same
            third-party data disclaimers in Section 3.
          </p>

          <h2 className="text-lg font-semibold text-slate-900 mt-8">5. Educational Content (Common Problems Pages)</h2>
          <p>
            VeriCar publishes informational pages summarising commonly reported problems for popular UK
            car models (the &quot;Common Problems&quot; library). These pages are generated by artificial
            intelligence systems (large language models) from owner-reported data and are intended as
            general guidance only. They do <strong>not</strong> form part of any individual vehicle report
            you purchase.
          </p>
          <p>AI-generated educational content:</p>
          <ul className="list-disc pl-5 space-y-1">
            <li>Is a best-effort summary, not a professional assessment</li>
            <li>May contain factual errors, omissions, or inconsistencies</li>
            <li>May describe issues not present on a specific vehicle, or omit issues that are</li>
            <li>May produce differing outputs for similar vehicles</li>
            <li>Reflects the data and inputs available at the time of generation only</li>
          </ul>
          <p>
            AI-generated educational content must not be relied upon as mechanical, legal, or financial
            advice. Where the educational content disagrees with the data in your specific VeriCar vehicle
            report, the report data (sourced from DVLA, DVSA, Experian and other licensed providers) takes
            precedence. You should always have a qualified mechanic inspect any vehicle before purchase.
          </p>

          <h2 className="text-lg font-semibold text-slate-900 mt-8">6. Your Responsibilities</h2>
          <p>When using VeriCar you are responsible for:</p>
          <ul className="list-disc pl-5 space-y-1">
            <li>
              <strong>Entering the correct vehicle registration number (VRM).</strong> We generate reports
              for whichever VRM is entered. Reports based on a mistyped or incorrect VRM relate to a
              different vehicle and cannot be relied upon for the one you are buying. We are not liable for
              decisions made on the basis of an incorrectly entered VRM.
            </li>
            <li>
              <strong>Carrying out a physical inspection.</strong> A VeriCar report does not replace a
              physical inspection, test drive, or independent mechanical check by a qualified professional.
            </li>
            <li>
              <strong>Exercising independent judgement.</strong> A VeriCar report is one input into your
              decision. You remain responsible for the decision to buy, the price you pay, and the terms
              of any transaction.
            </li>
          </ul>

          <h2 className="text-lg font-semibold text-slate-900 mt-8">7. Payments</h2>
          <ul className="list-disc pl-5 space-y-1">
            <li>Paid reports are one-off purchases.</li>
            <li>Payments are processed securely through Stripe, our payment provider.</li>
            <li>Once payment has been successfully completed, your report will normally be delivered by email within approximately 60 seconds.</li>
          </ul>

          <h2 className="text-lg font-semibold text-slate-900 mt-8">8. Refunds</h2>
          <p>
            Due to the instant digital nature of our reports, purchases are generally non-refundable once
            the report has been delivered. However, we will provide a refund where appropriate in cases such as:
          </p>
          <ul className="list-disc pl-5 space-y-1">
            <li>Technical failures preventing report delivery</li>
            <li>Duplicate charges</li>
            <li>Incomplete or corrupted reports</li>
          </ul>
          <p>
            If you experience an issue with your report, please contact us at{" "}
            <a href="mailto:matthew@vericar.co.uk" className="text-blue-600 underline">matthew@vericar.co.uk</a>.
            Nothing in this section affects your statutory rights under UK consumer law.
          </p>

          <h2 className="text-lg font-semibold text-slate-900 mt-8">9. Acceptable Use</h2>
          <p>You may use VeriCar for personal vehicle checks only. You must not:</p>
          <ul className="list-disc pl-5 space-y-1">
            <li>Scrape, harvest, or extract data from the service</li>
            <li>Submit automated or bulk queries</li>
            <li>Resell or commercially redistribute reports</li>
            <li>Reproduce or publish reports for commercial purposes</li>
            <li>Attempt to reverse engineer or disrupt the service</li>
          </ul>
          <p>
            We reserve the right to restrict or suspend access where we reasonably believe the service is
            being misused.
          </p>

          <h2 className="text-lg font-semibold text-slate-900 mt-8">10. Intellectual Property</h2>
          <p>
            All content provided by VeriCar, including reports, software, design, and data presentation,
            is protected by intellectual property rights. Reports are licensed to you for personal use
            related to the specific vehicle purchase you are considering.
          </p>
          <p>
            You <strong>may</strong> share a report privately with a family member, partner, or trusted
            professional adviser (for example, a mechanic) for the purpose of evaluating the same vehicle.
          </p>
          <p>
            You <strong>may not</strong> publish reports online, sell or redistribute reports, use reports
            in commercial or trade contexts, or commercially exploit any data obtained from the service
            without our written permission.
          </p>

          <h2 className="text-lg font-semibold text-slate-900 mt-8">11. Not for Use in Legal Proceedings</h2>
          <p>
            VeriCar reports are intended to inform private purchasing decisions only. They are not
            prepared as expert evidence and are not intended for use in litigation, formal disputes,
            insurance claims, or as proof of any fact in legal or regulatory proceedings. If you need
            data for such purposes, please obtain it directly from the underlying authoritative source
            (DVLA, DVSA, or the relevant data provider) with appropriate certification.
          </p>

          <h2 className="text-lg font-semibold text-slate-900 mt-8">12. Service Availability</h2>
          <p>
            We aim to keep VeriCar available at all times, but we do not guarantee that the service will
            be uninterrupted or error-free. Access to the service may occasionally be suspended or restricted
            for maintenance, updates, or technical reasons.
          </p>

          <h2 className="text-lg font-semibold text-slate-900 mt-8">13. Limitation of Liability</h2>
          <p>
            To the fullest extent permitted by law, VeriCar shall not be liable for any indirect,
            consequential, or economic loss arising from the use of our service or reliance on information
            contained in our reports. VeriCar&apos;s total liability for any claim relating to a report shall
            not exceed the amount paid for that report.
          </p>
          <p>Nothing in these terms excludes or limits liability for:</p>
          <ul className="list-disc pl-5 space-y-1">
            <li>Fraud or fraudulent misrepresentation</li>
            <li>Death or personal injury caused by negligence</li>
            <li>Any liability that cannot be excluded under applicable law</li>
          </ul>

          <h2 className="text-lg font-semibold text-slate-900 mt-8">14. Changes to These Terms</h2>
          <p>
            We may update these Terms of Service from time to time. The latest version will always be
            published on our website with the updated date. Continued use of the service after changes
            are posted constitutes acceptance of the revised terms.
          </p>

          <h2 className="text-lg font-semibold text-slate-900 mt-8">15. Governing Law</h2>
          <p>
            These Terms of Service are governed by the laws of England and Wales. Any disputes arising
            from or relating to these terms shall be subject to the exclusive jurisdiction of the courts
            of England and Wales.
          </p>

          <h2 className="text-lg font-semibold text-slate-900 mt-8">16. Contact</h2>
          <p>
            If you have any questions about these Terms of Service, please contact:{" "}
            <a href="mailto:matthew@vericar.co.uk" className="text-blue-600 underline">matthew@vericar.co.uk</a>
          </p>

        </div>
      </section>

      <Footer />
    </main>
  );
}
