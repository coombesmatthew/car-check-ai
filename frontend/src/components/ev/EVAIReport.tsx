"use client";

interface EVAIReportProps {
  report: string;
  registration: string;
}

/* Section icons for EV report sections */
const sectionIcons: Record<string, JSX.Element> = {
  "buy this ev": (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M6.633 10.5c.806 0 1.533-.446 2.031-1.08a9.041 9.041 0 012.861-2.4c.723-.384 1.35-.956 1.653-1.715a4.498 4.498 0 00.322-1.672V3a.75.75 0 01.75-.75A2.25 2.25 0 0116.5 4.5c0 1.152-.26 2.243-.723 3.218-.266.558.107 1.282.725 1.282h3.126c1.026 0 1.945.694 2.054 1.715.045.422.068.85.068 1.285a11.95 11.95 0 01-2.649 7.521c-.388.482-.987.729-1.605.729H13.48c-.483 0-.964-.078-1.423-.23l-3.114-1.04a4.501 4.501 0 00-1.423-.23H5.904M14.25 9h2.25M5.904 18.75c.083.205.173.405.27.602.197.4-.078.898-.523.898h-.908c-.889 0-1.713-.518-1.972-1.368a12 12 0 01-.521-3.507c0-1.553.295-3.036.831-4.398C3.387 10.203 4.167 9.75 5 9.75h1.053c.472 0 .745.556.5.96a8.958 8.958 0 00-1.302 4.665c0 1.194.232 2.333.654 3.375z" />
    </svg>
  ),
  "full picture": (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
    </svg>
  ),
  "battery": (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M21 10.5h.375c.621 0 1.125.504 1.125 1.125v2.25c0 .621-.504 1.125-1.125 1.125H21M4.5 10.5H18V15H4.5v-4.5zM3.75 18h15A2.25 2.25 0 0021 15.75v-6a2.25 2.25 0 00-2.25-2.25h-15A2.25 2.25 0 001.5 9.75v6A2.25 2.25 0 003.75 18z" />
    </svg>
  ),
  "range": (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 6.75V15m6-6v8.25m.503 3.498l4.875-2.437c.381-.19.622-.58.622-1.006V4.82c0-.836-.88-1.38-1.628-1.006l-3.869 1.934c-.317.159-.69.159-1.006 0L9.503 3.252a1.125 1.125 0 00-1.006 0L3.622 5.689C3.24 5.88 3 6.27 3 6.695V19.18c0 .836.88 1.38 1.628 1.006l3.869-1.934c.317-.159.69-.159 1.006 0l4.994 2.497c.317.158.69.158 1.006 0z" />
    </svg>
  ),
  "charging": (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
    </svg>
  ),
  "running cost": (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 18.75a60.07 60.07 0 0115.797 2.101c.727.198 1.453-.342 1.453-1.096V18.75M3.75 4.5v.75A.75.75 0 013 6h-.75m0 0v-.375c0-.621.504-1.125 1.125-1.125H20.25M2.25 6v9m18-10.5v.75c0 .414.336.75.75.75h.75m-1.5-1.5h.375c.621 0 1.125.504 1.125 1.125v9.75c0 .621-.504 1.125-1.125 1.125h-.375m1.5-1.5H21a.75.75 0 00-.75.75v.75m0 0H3.75m0 0h-.375a1.125 1.125 0 01-1.125-1.125V15m1.5 1.5v-.75A.75.75 0 003 15h-.75M15 10.5a3 3 0 11-6 0 3 3 0 016 0zm3 0h.008v.008H18V10.5zm-12 0h.008v.008H6V10.5z" />
    </svg>
  ),
  "ownership": (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  ),
  "learn": (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
    </svg>
  ),
  "verdict": (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  ),
  "negotiation": (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 21L3 16.5m0 0L7.5 12M3 16.5h13.5m0-13.5L21 7.5m0 0L16.5 12M21 7.5H7.5" />
    </svg>
  ),
};

function getSectionIcon(heading: string): JSX.Element | null {
  const lower = heading.toLowerCase();
  for (const [key, icon] of Object.entries(sectionIcons)) {
    if (lower.includes(key)) return icon;
  }
  return null;
}

/* Extract verdict from report text — handles bold (**BUY**) and plain text */
function extractVerdict(text: string): { type: "buy" | "negotiate" | "avoid"; label: string } | null {
  const lower = text.toLowerCase();
  // Check bold format first (most common from AI + demo reports)
  if (lower.includes("**buy**")) return { type: "buy", label: "BUY" };
  if (lower.includes("**negotiate**")) return { type: "negotiate", label: "NEGOTIATE" };
  if (lower.includes("**avoid**")) return { type: "avoid", label: "AVOID" };
  // Fallback: check for verdict keywords near the start of the report
  const firstSection = lower.slice(0, 500);
  if (/\bavoid\b/.test(firstSection)) return { type: "avoid", label: "AVOID" };
  if (/\bnegotiate\b/.test(firstSection)) return { type: "negotiate", label: "NEGOTIATE" };
  if (/\bbuy\b/.test(firstSection)) return { type: "buy", label: "BUY" };
  return null;
}

const verdictStyles = {
  buy: {
    bg: "bg-emerald-600",
    text: "text-white",
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
  },
  negotiate: {
    bg: "bg-amber-500",
    text: "text-white",
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
      </svg>
    ),
  },
  avoid: {
    bg: "bg-red-600",
    text: "text-white",
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
      </svg>
    ),
  },
};

export default function EVAIReport({ report, registration }: EVAIReportProps) {
  const verdict = extractVerdict(report);

  // Handle **bold**, [N] citations, and [text](url) links inline
  const renderInline = (text: string) => {
    const parts = text.split(/(\*\*[^*]+\*\*|\[\d+\]|\[[^\]]+\]\([^)]+\))/g);
    return parts.map((part, i) => {
      if (part.startsWith("**") && part.endsWith("**")) {
        return (
          <strong key={i} className="font-semibold text-slate-900">
            {part.slice(2, -2)}
          </strong>
        );
      }
      const linkMatch = part.match(/^\[([^\]]+)\]\(([^)]+)\)$/);
      if (linkMatch) {
        const href = linkMatch[2];
        if (!/^https?:\/\//i.test(href)) return <span key={i}>{part}</span>;
        return (
          <a key={i} href={href} target="_blank" rel="noopener noreferrer" className="text-emerald-600 hover:text-emerald-800 underline">
            {linkMatch[1]}
          </a>
        );
      }
      if (/^\[\d+\]$/.test(part)) {
        const num = part.slice(1, -1);
        return (
          <a
            key={i}
            href={`#ev-source-${num}`}
            onClick={(e) => {
              e.preventDefault();
              document.getElementById(`ev-source-${num}`)?.scrollIntoView({ behavior: "smooth", block: "center" });
            }}
            className="inline-flex items-center justify-center min-w-[18px] h-[16px] px-1 ml-0.5 text-[10px] font-semibold text-slate-500 bg-slate-100 hover:bg-emerald-100 hover:text-emerald-600 rounded leading-none align-super cursor-pointer transition-colors no-underline"
          >
            {num}
          </a>
        );
      }
      return part;
    });
  };

  const renderMarkdown = (text: string) => {
    let inDataSources = false;
    const lines = text.split("\n");
    const elements: JSX.Element[] = [];
    let i = 0;

    while (i < lines.length) {
      const line = lines[i];
      if (line.startsWith("## Data Sources")) inDataSources = true;

      // Table
      if (line.startsWith("|") && line.endsWith("|")) {
        const tableRows: string[] = [];
        while (i < lines.length && lines[i].startsWith("|") && lines[i].endsWith("|")) {
          tableRows.push(lines[i]);
          i++;
        }
        const headerCells = tableRows[0].split("|").filter(c => c.trim()).map(c => c.trim());
        const bodyRows = tableRows.slice(2);
        elements.push(
          <div key={`table-${i}`} className="overflow-x-auto my-2">
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="border-b-2 border-emerald-200">
                  {headerCells.map((cell, ci) => (
                    <th key={ci} className="text-left py-2 px-3 font-semibold text-slate-800 text-xs uppercase tracking-wide">
                      {renderInline(cell)}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {bodyRows.map((row, ri) => {
                  const cells = row.split("|").filter(c => c.trim()).map(c => c.trim());
                  return (
                    <tr key={ri} className="border-b border-slate-100">
                      {cells.map((cell, ci) => (
                        <td key={ci} className="py-2 px-3 text-slate-700">
                          {renderInline(cell)}
                        </td>
                      ))}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        );
        continue;
      }

      // H2
      if (line.startsWith("## ")) {
        const heading = line.slice(3);
        const icon = getSectionIcon(heading);
        elements.push(
          <h3 key={i} className="text-lg font-semibold text-slate-900 mt-6 mb-2 first:mt-0 flex items-center gap-2">
            {icon && <span className="text-emerald-500">{icon}</span>}
            {renderInline(heading)}
          </h3>
        );
        i++; continue;
      }
      // H3
      if (line.startsWith("### ")) {
        elements.push(
          <h4 key={i} className="text-md font-semibold text-slate-800 mt-4 mb-1">{line.slice(4)}</h4>
        );
        i++; continue;
      }
      // Bullet
      if (line.startsWith("- ")) {
        elements.push(
          <li key={i} className="text-sm text-slate-700 ml-4 list-disc mb-1">{renderInline(line.slice(2))}</li>
        );
        i++; continue;
      }
      // Numbered list
      const olMatch = line.match(/^(\d+)\.\s+(.+)$/);
      if (olMatch) {
        elements.push(
          <li
            key={i}
            id={inDataSources ? `ev-source-${olMatch[1]}` : undefined}
            className={`text-sm text-slate-700 ml-4 list-decimal mb-1${inDataSources ? " scroll-mt-4 transition-colors duration-300" : ""}`}
          >
            {renderInline(olMatch[2])}
          </li>
        );
        i++; continue;
      }
      // HR
      if (line.trim() === "---") {
        elements.push(<hr key={i} className="my-6 border-slate-200" />);
        i++; continue;
      }
      // Empty
      if (line.trim() === "") {
        elements.push(<div key={i} className="h-2" />);
        i++; continue;
      }
      // Paragraph
      elements.push(
        <p key={i} className="text-sm text-slate-700 mb-1 leading-relaxed">{renderInline(line)}</p>
      );
      i++;
    }

    return elements;
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
      {/* Verdict banner */}
      {verdict && (
        <div className={`${verdictStyles[verdict.type].bg} ${verdictStyles[verdict.type].text} px-6 py-4 flex items-center justify-between`}>
          <div className="flex items-center gap-3">
            {verdictStyles[verdict.type].icon}
            <div>
              <div className="text-sm font-medium opacity-90">AI Verdict</div>
              <div className="text-2xl font-bold">{verdict.label}</div>
            </div>
          </div>
          <span className="text-sm opacity-75">Powered by Claude AI</span>
        </div>
      )}

      {/* Header */}
      <div className="bg-gradient-to-r from-emerald-700 to-emerald-900 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-emerald-200" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
              </svg>
              <h2 className="text-white font-semibold text-lg">
                EV Health Report
              </h2>
            </div>
            <p className="text-emerald-200 text-sm mt-0.5">{registration}</p>
          </div>
          <span className="bg-emerald-500 text-white text-xs font-medium px-2.5 py-1 rounded-full">
            FREE PREVIEW
          </span>
        </div>
      </div>

      {/* Report body */}
      <div className="px-6 py-5">{renderMarkdown(report)}</div>

      {/* Disclaimer */}
      <div className="border-t border-slate-100 px-6 py-4 bg-slate-50">
        <p className="text-xs text-slate-400">
          This is a free preview report generated using official DVLA and DVSA data.
          The full paid report (£7.99) includes real-world battery telemetry and AI lifespan prediction.
        </p>
      </div>
    </div>
  );
}
