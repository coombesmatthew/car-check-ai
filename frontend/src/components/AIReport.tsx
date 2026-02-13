"use client";

interface AIReportProps {
  report: string;
  registration: string;
}

export default function AIReport({ report, registration }: AIReportProps) {
  // Simple markdown-to-HTML for headings, bold, bullets
  const renderMarkdown = (text: string) => {
    return text.split("\n").map((line, i) => {
      // H2
      if (line.startsWith("## ")) {
        return (
          <h3
            key={i}
            className="text-lg font-semibold text-slate-900 mt-5 mb-2 first:mt-0"
          >
            {line.slice(3)}
          </h3>
        );
      }
      // H3
      if (line.startsWith("### ")) {
        return (
          <h4 key={i} className="text-md font-semibold text-slate-800 mt-3 mb-1">
            {line.slice(4)}
          </h4>
        );
      }
      // Bullet
      if (line.startsWith("- ")) {
        const content = line.slice(2);
        return (
          <li key={i} className="text-sm text-slate-700 ml-4 list-disc mb-1">
            {renderInline(content)}
          </li>
        );
      }
      // Empty line
      if (line.trim() === "") {
        return <div key={i} className="h-2" />;
      }
      // Paragraph
      return (
        <p key={i} className="text-sm text-slate-700 mb-1">
          {renderInline(line)}
        </p>
      );
    });
  };

  // Handle **bold** inline
  const renderInline = (text: string) => {
    const parts = text.split(/(\*\*[^*]+\*\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith("**") && part.endsWith("**")) {
        return (
          <strong key={i} className="font-semibold text-slate-900">
            {part.slice(2, -2)}
          </strong>
        );
      }
      return part;
    });
  };

  return (
    <div className="bg-white border border-blue-200 rounded-xl overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-5 py-4">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2">
              <svg
                className="w-5 h-5 text-blue-200"
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
            <p className="text-blue-200 text-sm mt-0.5">
              Powered by Claude AI &middot; {registration}
            </p>
          </div>
          <span className="bg-blue-500 text-white text-xs font-medium px-2.5 py-1 rounded-full">
            BASIC
          </span>
        </div>
      </div>

      {/* Report body */}
      <div className="px-5 py-4">{renderMarkdown(report)}</div>

      {/* Footer */}
      <div className="border-t border-slate-100 px-5 py-3 bg-slate-50">
        <p className="text-xs text-slate-400">
          This report is AI-generated based on official DVLA and DVSA data. It
          is advisory only and should not replace a professional inspection.
        </p>
      </div>
    </div>
  );
}
