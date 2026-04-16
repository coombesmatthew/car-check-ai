"use client";

import { useRef, useEffect } from "react";
import { useActiveSection } from "@/hooks/useActiveSection";

export interface SectionConfig {
  id: string;
  label: string;
  locked?: boolean;
  href?: string;
}

const DEFAULT_SECTIONS: SectionConfig[] = [
  { id: "section-overview", label: "Overview" },
  { id: "section-history", label: "History" },
  { id: "section-emissions", label: "Emissions" },
  { id: "section-fullcheck", label: "Full Check", locked: true },
  { id: "nav-ev-check", label: "EV Check", locked: true, href: "/ev" },
];

const LockIcon = () => (
  <svg className="w-3 h-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
  </svg>
);

export default function SectionNav({ sections, hasPremium }: { sections?: SectionConfig[]; hasPremium?: boolean }) {
  const items = sections || DEFAULT_SECTIONS;
  const scrollIds = items.filter((s) => !s.href).map((s) => s.id);
  const activeId = useActiveSection(scrollIds);
  const navRef = useRef<HTMLDivElement>(null);

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

  const pillClass = (active: boolean) =>
    `flex items-center px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all ${
      active
        ? "bg-blue-600 text-white shadow-sm"
        : "text-slate-500 hover:text-slate-700 hover:bg-slate-100"
    }`;

  return (
    <div className="sticky top-0 z-30 bg-white/95 backdrop-blur-sm border-b border-slate-100 -mx-4 px-4">
      <div ref={navRef} className="flex gap-1 py-2 overflow-x-auto scrollbar-hide">
        {items.map((section) => {
          const showLock = section.locked && !hasPremium;
          if (section.href) {
            return (
              <a
                key={section.id}
                data-section={section.id}
                href={section.href}
                className={pillClass(false)}
              >
                {showLock && <LockIcon />}
                {section.label}
              </a>
            );
          }
          return (
            <button
              key={section.id}
              data-section={section.id}
              onClick={() => scrollTo(section.id)}
              className={pillClass(activeId === section.id)}
            >
              {showLock && <LockIcon />}
              {section.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}
