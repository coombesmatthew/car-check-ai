"use client";

interface AIReportProps {
  report: string;
  registration: string;
}

/* Section icons for structured report */
const sectionIcons: Record<string, JSX.Element> = {
  "vehicle summary": (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 18.75a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m3 0h6m-9 0H3.375a1.125 1.125 0 01-1.125-1.125V14.25m17.25 4.5a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m3 0H21M3.375 14.25h17.25" />
    </svg>
  ),
  "condition": (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
    </svg>
  ),
  "mileage": (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  ),
  "risk": (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
    </svg>
  ),
  "recommendation": (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M6.633 10.5c.806 0 1.533-.446 2.031-1.08a9.041 9.041 0 012.861-2.4c.723-.384 1.35-.956 1.653-1.715a4.498 4.498 0 00.322-1.672V3a.75.75 0 01.75-.75A2.25 2.25 0 0116.5 4.5c0 1.152-.26 2.243-.723 3.218-.266.558.107 1.282.725 1.282h3.126c1.026 0 1.945.694 2.054 1.715.045.422.068.85.068 1.285a11.95 11.95 0 01-2.649 7.521c-.388.482-.987.729-1.605.729H13.48c-.483 0-.964-.078-1.423-.23l-3.114-1.04a4.501 4.501 0 00-1.423-.23H5.904M14.25 9h2.25M5.904 18.75c.083.205.173.405.27.602.197.4-.078.898-.523.898h-.908c-.889 0-1.713-.518-1.972-1.368a12 12 0 01-.521-3.507c0-1.553.295-3.036.831-4.398C3.387 10.203 4.167 9.75 5 9.75h1.053c.472 0 .745.556.5.96a8.958 8.958 0 00-1.302 4.665c0 1.194.232 2.333.654 3.375z" />
    </svg>
  ),
  "negotiation": (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 18.75a60.07 60.07 0 0115.797 2.101c.727.198 1.453-.342 1.453-1.096V18.75M3.75 4.5v.75A.75.75 0 013 6h-.75m0 0v-.375c0-.621.504-1.125 1.125-1.125H20.25M2.25 6v9m18-10.5v.75c0 .414.336.75.75.75h.75m-1.5-1.5h.375c.621 0 1.125.504 1.125 1.125v9.75c0 .621-.504 1.125-1.125 1.125h-.375m1.5-1.5H21a.75.75 0 00-.75.75v.75m0 0H3.75m0 0h-.375a1.125 1.125 0 01-1.125-1.125V15m1.5 1.5v-.75A.75.75 0 003 15h-.75M15 10.5a3 3 0 11-6 0 3 3 0 016 0zm3 0h.008v.008H18V10.5zm-12 0h.008v.008H6V10.5z" />
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

/* Extract verdict from report text */
function extractVerdict(text: string): { type: "buy" | "negotiate" | "avoid"; label: string } | null {
  const lower = text.toLowerCase();
  if (lower.includes("verdict: buy") || lower.includes("verdict:**buy") || lower.includes("**buy**")) {
    return { type: "buy", label: "BUY" };
  }
  if (lower.includes("verdict: negotiate") || lower.includes("verdict:**negotiate") || lower.includes("**negotiate**")) {
    return { type: "negotiate", label: "NEGOTIATE" };
  }
  if (lower.includes("verdict: avoid") || lower.includes("verdict:**avoid") || lower.includes("**avoid**")) {
    return { type: "avoid", label: "AVOID" };
  }
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

export default function AIReport({ report, registration }: AIReportProps) {
  const verdict = extractVerdict(report);

  // Simple markdown-to-HTML for headings, bold, bullets
  const renderMarkdown = (text: string) => {
    let inDataSources = false;
    const lines = text.split("\n");
    const elements: JSX.Element[] = [];
    let i = 0;

    while (i < lines.length) {
      const line = lines[i];
      if (line.startsWith("## Data Sources")) inDataSources = true;

      // Table — collect consecutive | rows
      if (line.startsWith("|") && line.endsWith("|")) {
        const tableRows: string[] = [];
        while (i < lines.length && lines[i].startsWith("|") && lines[i].endsWith("|")) {
          tableRows.push(lines[i]);
          i++;
        }
        // Parse: first row = header, second row = separator (skip), rest = body
        const headerCells = tableRows[0].split("|").filter(c => c.trim()).map(c => c.trim());
        const bodyRows = tableRows.slice(2); // skip header + separator
        elements.push(
          <div key={`table-${i}`} className="overflow-x-auto my-2">
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="border-b-2 border-slate-200">
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
          <h3
            key={i}
            className="text-lg font-semibold text-slate-900 mt-6 mb-2 first:mt-0 flex items-center gap-2"
          >
            {icon && <span className="text-blue-500">{icon}</span>}
            {renderInline(heading)}
          </h3>
        );
        i++; continue;
      }
      // H3
      if (line.startsWith("### ")) {
        elements.push(
          <h4 key={i} className="text-md font-semibold text-slate-800 mt-4 mb-1">
            {line.slice(4)}
          </h4>
        );
        i++; continue;
      }
      // Bullet
      if (line.startsWith("- ")) {
        const content = line.slice(2);
        elements.push(
          <li key={i} className="text-sm text-slate-700 ml-4 list-disc mb-1">
            {renderInline(content)}
          </li>
        );
        i++; continue;
      }
      // Numbered list (e.g. Data Sources footer)
      const olMatch = line.match(/^(\d+)\.\s+(.+)$/);
      if (olMatch) {
        elements.push(
          <li
            key={i}
            id={inDataSources ? `source-${olMatch[1]}` : undefined}
            className={`text-sm text-slate-700 ml-4 list-decimal mb-1${inDataSources ? " scroll-mt-4 transition-colors duration-300" : ""}`}
          >
            {renderInline(olMatch[2])}
          </li>
        );
        i++; continue;
      }
      // Horizontal rule
      if (line.trim() === "---") {
        elements.push(<hr key={i} className="my-6 border-slate-200" />);
        i++; continue;
      }
      // Empty line
      if (line.trim() === "") {
        elements.push(<div key={i} className="h-2" />);
        i++; continue;
      }
      // Paragraph
      elements.push(
        <p key={i} className="text-sm text-slate-700 mb-1 leading-relaxed">
          {renderInline(line)}
        </p>
      );
      i++;
    }

    return elements;
  };

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
      // Markdown link [text](url)
      const linkMatch = part.match(/^\[([^\]]+)\]\(([^)]+)\)$/);
      if (linkMatch) {
        const href = linkMatch[2];
        if (!/^https?:\/\//i.test(href)) return <span key={i}>{part}</span>;
        return (
          <a
            key={i}
            href={href}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:text-blue-800 underline"
          >
            {linkMatch[1]}
          </a>
        );
      }
      if (/^\[\d+\]$/.test(part)) {
        const num = part.slice(1, -1);
        return (
          <a
            key={i}
            href={`#source-${num}`}
            onClick={(e) => {
              e.preventDefault();
              document.getElementById(`source-${num}`)?.scrollIntoView({ behavior: "smooth", block: "center" });
            }}
            className="inline-flex items-center justify-center min-w-[18px] h-[16px] px-1 ml-0.5 text-[10px] font-semibold text-slate-500 bg-slate-100 hover:bg-blue-100 hover:text-blue-600 rounded leading-none align-super cursor-pointer transition-colors no-underline"
          >
            {num}
          </a>
        );
      }
      return part;
    });
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
      <div className="bg-gradient-to-r from-slate-800 to-slate-900 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2">
              <svg
                className="w-5 h-5 text-slate-300"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                />
              </svg>
              <h2 className="text-white font-semibold text-lg">
                AI Buyer&apos;s Report
              </h2>
            </div>
            <p className="text-slate-400 text-sm mt-0.5">
              {registration}
            </p>
          </div>
          <span className="bg-blue-600 text-white text-xs font-medium px-2.5 py-1 rounded-full">
            BASIC
          </span>
        </div>
      </div>

      {/* Report body */}
      <div className="px-6 py-5">{renderMarkdown(report)}</div>

      {/* Disclaimer */}
      <div className="border-t border-slate-100 px-6 py-4 bg-slate-50">
        <p className="text-xs text-slate-400">
          This report is AI-generated based on official DVLA and DVSA data. It
          is advisory only and should not replace a professional inspection.
        </p>
      </div>
    </div>
  );
}
