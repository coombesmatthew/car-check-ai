export default function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-slate-50 mt-auto">
      <div className="mx-auto max-w-5xl px-4 py-10">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-8">
          {/* Brand */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <div className="h-8 w-8 rounded-lg bg-blue-600 flex items-center justify-center">
                <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
                </svg>
              </div>
              <span className="font-bold text-slate-900">
                Car<span className="text-blue-600">Verify</span>
              </span>
            </div>
            <p className="text-sm text-slate-500 leading-relaxed">
              AI-powered vehicle checks using official UK government data.
              Make informed decisions when buying a used car.
            </p>
          </div>

          {/* Links */}
          <div>
            <h4 className="font-semibold text-slate-900 mb-3 text-sm">Quick Links</h4>
            <nav className="space-y-2">
              <a href="#search" className="block text-sm text-slate-500 hover:text-slate-700 transition-colors">
                Free Check
              </a>
              <a href="#full-report" className="block text-sm text-slate-500 hover:text-slate-700 transition-colors">
                Full Report
              </a>
              <a href="#how-it-works" className="block text-sm text-slate-500 hover:text-slate-700 transition-colors">
                How It Works
              </a>
              <a href="#" className="block text-sm text-slate-500 hover:text-slate-700 transition-colors">
                Privacy Policy
              </a>
              <a href="#" className="block text-sm text-slate-500 hover:text-slate-700 transition-colors">
                Terms of Service
              </a>
            </nav>
          </div>

          {/* Data sources */}
          <div>
            <h4 className="font-semibold text-slate-900 mb-3 text-sm">Data Sources</h4>
            <p className="text-sm text-slate-500 leading-relaxed">
              Vehicle data sourced from the DVLA Vehicle Enquiry Service and
              DVSA MOT History API — official UK government services.
            </p>
            <p className="text-sm text-slate-400 mt-3">
              Not affiliated with or endorsed by DVLA, DVSA, or GOV.UK.
            </p>
          </div>
        </div>

        <div className="border-t border-slate-200 mt-8 pt-6 text-center text-xs text-slate-400">
          &copy; {new Date().getFullYear()} VeriCar. All rights reserved.
        </div>
      </div>
    </footer>
  );
}
