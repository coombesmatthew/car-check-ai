import Header from "@/components/Header";
import Footer from "@/components/Footer";

export default function EVReportCancelPage() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-emerald-50/30 to-white flex flex-col">
      <Header />
      <div className="mx-auto max-w-5xl px-4 flex-1">
        <div className="text-center py-20">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-slate-100 mb-6">
            <svg className="w-8 h-8 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-slate-900 mb-2">Payment cancelled</h2>
          <p className="text-slate-500 mb-6">
            No worries — you haven&apos;t been charged. Your free EV check results are still available.
          </p>
          <a
            href="/ev"
            className="inline-block px-8 py-3 bg-emerald-600 text-white font-semibold rounded-lg hover:bg-emerald-700 transition-colors"
          >
            Back to EV Check
          </a>
        </div>
      </div>
      <Footer />
    </main>
  );
}
