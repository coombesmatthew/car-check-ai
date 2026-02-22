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
        <p className="text-sm text-slate-400 mb-8">Last updated: February 2026</p>

        <div className="prose prose-slate max-w-none space-y-6 text-sm text-slate-600 leading-relaxed">
          <h2 className="text-lg font-semibold text-slate-900 mt-8">1. About our service</h2>
          <p>
            VeriCar provides vehicle history and condition checks using data from the DVLA, DVSA,
            and third-party data providers. Our service is designed to help used car buyers make
            more informed decisions.
          </p>

          <h2 className="text-lg font-semibold text-slate-900 mt-8">2. Accuracy of information</h2>
          <p>
            While we take every care to ensure accuracy, vehicle data is sourced from third-party
            providers and government databases. We cannot guarantee that all information is complete
            or error-free. Our checks should be used as one part of your decision-making process,
            alongside a physical inspection and test drive.
          </p>

          <h2 className="text-lg font-semibold text-slate-900 mt-8">3. AI-generated content</h2>
          <p>
            Our AI reports are generated using artificial intelligence based on the vehicle data
            available. They provide guidance and opinion, not professional mechanical advice.
            Always have a qualified mechanic inspect any vehicle before purchasing.
          </p>

          <h2 className="text-lg font-semibold text-slate-900 mt-8">4. Payments and refunds</h2>
          <p>
            Paid reports are one-off purchases processed securely via Stripe. Reports are delivered
            to your email within 60 seconds. If you experience any issues with your report, please
            contact us and we will resolve the matter or issue a refund.
          </p>

          <h2 className="text-lg font-semibold text-slate-900 mt-8">5. Acceptable use</h2>
          <p>
            You may use VeriCar for personal vehicle checks. Automated scraping, bulk queries, or
            reselling of our data is not permitted. We reserve the right to suspend accounts that
            abuse our service.
          </p>

          <h2 className="text-lg font-semibold text-slate-900 mt-8">6. Limitation of liability</h2>
          <p>
            VeriCar is provided &ldquo;as is&rdquo;. To the extent permitted by law, we are not liable for
            any losses arising from reliance on the information provided by our service. Our maximum
            liability is limited to the amount you paid for the relevant report.
          </p>

          <h2 className="text-lg font-semibold text-slate-900 mt-8">7. Governing law</h2>
          <p>
            These terms are governed by the laws of England and Wales.
          </p>

          <h2 className="text-lg font-semibold text-slate-900 mt-8">8. Contact</h2>
          <p>
            For any questions about these terms, please email{" "}
            <span className="font-medium text-slate-900">hello@vericar.co.uk</span>.
          </p>
        </div>
      </section>

      <Footer />
    </main>
  );
}
