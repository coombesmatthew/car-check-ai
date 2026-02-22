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
        <p className="text-sm text-slate-400 mb-8">Last updated: February 2026</p>

        <div className="prose prose-slate max-w-none space-y-6 text-sm text-slate-600 leading-relaxed">
          <h2 className="text-lg font-semibold text-slate-900 mt-8">1. Who we are</h2>
          <p>
            VeriCar (&ldquo;we&rdquo;, &ldquo;us&rdquo;, &ldquo;our&rdquo;) provides an online vehicle checking
            service at vericar.co.uk. We are the data controller for the personal information we process.
          </p>

          <h2 className="text-lg font-semibold text-slate-900 mt-8">2. What data we collect</h2>
          <ul className="list-disc pl-5 space-y-1">
            <li>Vehicle registration numbers you search for</li>
            <li>Email address (only when you purchase a paid report)</li>
            <li>Payment information (processed securely by Stripe &mdash; we never see your full card details)</li>
            <li>Basic usage analytics (pages visited, device type)</li>
          </ul>

          <h2 className="text-lg font-semibold text-slate-900 mt-8">3. How we use your data</h2>
          <ul className="list-disc pl-5 space-y-1">
            <li>To perform vehicle checks using DVLA and DVSA data</li>
            <li>To generate and deliver your paid reports via email</li>
            <li>To process payments securely through Stripe</li>
            <li>To improve our service and fix issues</li>
          </ul>

          <h2 className="text-lg font-semibold text-slate-900 mt-8">4. Data sharing</h2>
          <p>
            We share data only with the third-party services required to deliver our product:
            Stripe (payments), DVLA/DVSA (vehicle data), and our data providers for premium checks.
            We do not sell your personal data.
          </p>

          <h2 className="text-lg font-semibold text-slate-900 mt-8">5. Data retention</h2>
          <p>
            Vehicle check results are retained to improve our service. Email addresses associated with
            paid reports are retained for customer support purposes. You can request deletion of your
            data at any time by contacting us.
          </p>

          <h2 className="text-lg font-semibold text-slate-900 mt-8">6. Your rights</h2>
          <p>
            Under UK GDPR, you have the right to access, rectify, or delete your personal data.
            You can also object to processing or request data portability. Contact us at the
            email below to exercise these rights.
          </p>

          <h2 className="text-lg font-semibold text-slate-900 mt-8">7. Contact</h2>
          <p>
            For any privacy-related questions, please email{" "}
            <span className="font-medium text-slate-900">privacy@vericar.co.uk</span>.
          </p>
        </div>
      </section>

      <Footer />
    </main>
  );
}
