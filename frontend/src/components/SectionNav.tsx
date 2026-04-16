"use client";

import { useRef, useEffect } from "react";
import { useActiveSection } from "@/hooks/useActiveSection";

const SECTIONS = [
  { id: "section-overview", label: "Overview" },
  { id: "section-history", label: "History" },
  { id: "section-emissions", label: "Emissions" },
  { id: "section-fullcheck", label: "Full Check" },
];

export default function SectionNav({ hasPremium }: { hasPremium?: boolean }) {
  const activeId = useActiveSection(SECTIONS.map((s) => s.id));
  const navRef = useRef<HTMLDivElement>(null);

  // Auto-scroll the nav bar to bring the active pill into view
  useEffect(() => {
    if (!navRef.current) return;
    const activeButton = navRef.current.querySelector(`[data-section="${activeId}"]`) as HTMLElement | null;
    if (activeButton) {
      activeButton.scrollIntoView({ behavior: "smooth", block: "nearest", inline: "center" });
    }
  }, [activeId]);

  const scrollTo = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  return (
    <div className="sticky top-0 z-30 bg-white/95 backdrop-blur-sm border-b border-slate-100 -mx-4 px-4">
      <div ref={navRef} className="flex gap-1 py-2 overflow-x-auto scrollbar-hide">
        {SECTIONS.map((section) => (
          <button
            key={section.id}
            data-section={section.id}
            onClick={() => scrollTo(section.id)}
            className={`flex items-center px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all ${
              activeId === section.id
                ? "bg-blue-600 text-white shadow-sm"
                : "text-slate-500 hover:text-slate-700 hover:bg-slate-100"
            }`}
          >
            {section.id === "section-fullcheck" && !hasPremium && (
              <svg className="w-3 h-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
              </svg>
            )}
            {section.label}
          </button>
        ))}
      </div>
    </div>
  );
}
