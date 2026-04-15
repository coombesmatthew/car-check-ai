"use client";

import { useActiveSection } from "@/hooks/useActiveSection";

const SECTIONS = [
  { id: "section-overview", label: "Overview" },
  { id: "section-history", label: "History" },
  { id: "section-emissions", label: "Emissions" },
  { id: "section-fullcheck", label: "Full Check" },
];

export default function SectionNav() {
  const activeId = useActiveSection(SECTIONS.map((s) => s.id));

  const scrollTo = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  return (
    <div className="sticky top-0 z-30 bg-white/95 backdrop-blur-sm border-b border-slate-100 -mx-4 px-4">
      <div className="flex gap-1 py-2 overflow-x-auto scrollbar-hide">
        {SECTIONS.map((section) => (
          <button
            key={section.id}
            onClick={() => scrollTo(section.id)}
            className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all ${
              activeId === section.id
                ? "bg-blue-600 text-white shadow-sm"
                : "text-slate-500 hover:text-slate-700 hover:bg-slate-100"
            }`}
          >
            {section.label}
          </button>
        ))}
      </div>
    </div>
  );
}
