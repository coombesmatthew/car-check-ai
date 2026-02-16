"use client";

import { useState } from "react";

export default function Header() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto max-w-5xl px-4 py-4 flex items-center justify-between">
        {/* Logo */}
        <a href="#" className="flex items-center gap-2.5">
          <div className="h-9 w-9 rounded-lg bg-blue-600 flex items-center justify-center">
            <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
            </svg>
          </div>
          <span className="font-bold text-lg text-slate-900">
            Veri<span className="text-blue-600">Car</span>
          </span>
        </a>

        {/* Desktop nav */}
        <nav className="hidden sm:flex items-center gap-6 text-sm">
          <a href="#search" className="text-slate-600 hover:text-slate-900 transition-colors">
            Free Check
          </a>
          <a href="#full-report" className="text-slate-600 hover:text-slate-900 transition-colors">
            Full Report
          </a>
          <a href="#how-it-works" className="text-slate-600 hover:text-slate-900 transition-colors">
            How It Works
          </a>
          <a
            href="#full-report"
            className="px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors text-sm"
          >
            Get Report &mdash; &pound;3.99
          </a>
        </nav>

        {/* Mobile hamburger */}
        <button
          className="sm:hidden p-2 text-slate-600"
          onClick={() => setMenuOpen(!menuOpen)}
          aria-label="Toggle menu"
        >
          {menuOpen ? (
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          ) : (
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
            </svg>
          )}
        </button>
      </div>

      {/* Mobile menu */}
      {menuOpen && (
        <div className="sm:hidden border-t border-slate-100 bg-white px-4 py-3 space-y-2">
          <a href="#search" className="block py-2 text-slate-600 hover:text-slate-900" onClick={() => setMenuOpen(false)}>
            Free Check
          </a>
          <a href="#full-report" className="block py-2 text-slate-600 hover:text-slate-900" onClick={() => setMenuOpen(false)}>
            Full Report
          </a>
          <a href="#how-it-works" className="block py-2 text-slate-600 hover:text-slate-900" onClick={() => setMenuOpen(false)}>
            How It Works
          </a>
          <a
            href="#full-report"
            className="block text-center py-2.5 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
            onClick={() => setMenuOpen(false)}
          >
            Get Report &mdash; &pound;3.99
          </a>
        </div>
      )}

      {/* Trust strip */}
      <div className="bg-slate-50 border-t border-slate-100">
        <div className="mx-auto max-w-5xl px-4 py-2 flex justify-center gap-4 sm:gap-6 text-xs text-slate-500">
          <span>Official DVLA &amp; DVSA Data</span>
          <span className="text-slate-300">&middot;</span>
          <span>12-Point Vehicle Analysis</span>
          <span className="text-slate-300">&middot;</span>
          <span>Instant Results</span>
        </div>
      </div>
    </header>
  );
}
