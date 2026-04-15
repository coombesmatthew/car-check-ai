"use client";

import { MOTSummary, ClockingAnalysis, MileageReading, FailurePattern, MOTTestRecord, VehicleIdentity } from "@/lib/api";
import Badge from "@/components/ui/Badge";
import Card from "@/components/ui/Card";
import { DetailRow, MileageChart, MOTPassFailBars, MOTTestItem, RecurringIssueItem, icons } from "./shared";

export default function HistorySections({ mot_summary, clocking_analysis, mileage_timeline, failure_patterns, mot_tests, vehicle }: {
  mot_summary: MOTSummary | null;
  clocking_analysis: ClockingAnalysis | null;
  mileage_timeline: MileageReading[];
  failure_patterns: FailurePattern[];
  mot_tests: MOTTestRecord[];
  vehicle: VehicleIdentity | null;
}) {
  return (
    <>
      {/* MOT Summary */}
      {mot_summary && (
        <Card
          title="MOT History"
          icon={icons.document}
          status={
            mot_summary.latest_test?.result === "PASSED" ? "pass"
              : mot_summary.latest_test?.result === "FAILED" ? "fail"
              : "neutral"
          }
        >
          {mot_summary.latest_test && (
            <div className="mb-3 flex items-center justify-between">
              <div>
                <p className="text-xs text-slate-400">Latest Test</p>
                <p className="text-sm font-medium text-slate-700">{mot_summary.latest_test.date}</p>
              </div>
              <Badge
                variant={mot_summary.latest_test.result === "PASSED" ? "pass" : "fail"}
                label={mot_summary.latest_test.result || ""}
                size="md"
              />
            </div>
          )}
          {mot_summary.latest_test?.expiry_date && (
            <DetailRow label="Expires" value={mot_summary.latest_test.expiry_date} />
          )}
          {mot_summary.current_odometer && (
            <DetailRow label="Mileage at Test" value={`${Number(mot_summary.current_odometer).toLocaleString()} miles`} />
          )}
          <div className="mt-3 pt-3 border-t border-slate-100" />
          <div className="flex items-center gap-4 text-sm">
            <span className="text-slate-500">{mot_summary.total_tests} tests</span>
            <span className="text-emerald-600 font-medium">{mot_summary.total_passes} passed</span>
            {mot_summary.total_failures > 0 && (
              <span className="text-red-600 font-medium">{mot_summary.total_failures} failed</span>
            )}
          </div>
          <MOTPassFailBars passes={mot_summary.total_passes} failures={mot_summary.total_failures} />
        </Card>
      )}

      {/* Mileage & Clocking */}
      {clocking_analysis && (
        <Card
          title="Mileage Analysis"
          icon={icons.clock}
          status={
            clocking_analysis.clocked
              ? "fail"
              : clocking_analysis.risk_level === "none"
              ? "pass"
              : clocking_analysis.risk_level === "unknown"
              ? "neutral"
              : "warn"
          }
        >
          {/* Headline mileage numbers */}
          {mot_summary?.current_odometer && (
            <div className="flex items-baseline justify-between mb-3">
              <div>
                <span className="text-2xl font-bold text-slate-900 font-mono">{Number(mot_summary.current_odometer).toLocaleString()}</span>
                <span className="text-sm text-slate-400 ml-1">miles</span>
              </div>
              {mileage_timeline.length >= 2 && (() => {
                const first = mileage_timeline[0];
                const last = mileage_timeline[mileage_timeline.length - 1];
                const years = (new Date(last.date).getTime() - new Date(first.date).getTime()) / (365.25 * 24 * 60 * 60 * 1000);
                const annual = years > 0 ? Math.round((last.miles - first.miles) / years) : null;
                return annual ? (
                  <div className="text-right">
                    <span className="text-lg font-bold text-slate-700 font-mono">{annual.toLocaleString()}</span>
                    <span className="text-xs text-slate-400 ml-1">/yr</span>
                  </div>
                ) : null;
              })()}
            </div>
          )}
          <div className="mb-3">
            {clocking_analysis.clocked ? (
              <div className="flex items-center gap-2 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
                <svg className="w-5 h-5 text-red-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
                </svg>
                <span className="text-sm font-semibold text-red-800">MILEAGE DISCREPANCY FOUND</span>
              </div>
            ) : clocking_analysis.risk_level === "none" ? (
              <div className="flex items-center gap-2 bg-emerald-50 border border-emerald-200 rounded-lg px-3 py-2">
                <svg className="w-5 h-5 text-emerald-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="text-sm font-semibold text-emerald-800">Mileage Consistent</span>
              </div>
            ) : (
              clocking_analysis.risk_level === "unknown" ? (
              <div className="flex items-center gap-2 bg-slate-50 border border-slate-200 rounded-lg px-3 py-2">
                <svg className="w-5 h-5 text-slate-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                <span className="text-sm font-semibold text-slate-600">Not Enough MOT History Yet</span>
              </div>
              ) : (
              <Badge variant="warn" label={`${clocking_analysis.risk_level.toUpperCase()} RISK`} size="md" />
              )
            )}
          </div>
          {clocking_analysis.reason && (
            <p className="text-sm text-slate-500 mb-2">
              {clocking_analysis.reason}
            </p>
          )}
          {clocking_analysis.flags.map((flag, i) => (
            <div
              key={i}
              className={`text-sm p-2 rounded mb-1 ${
                flag.severity === "high"
                  ? "bg-red-50 text-red-800"
                  : flag.severity === "medium"
                  ? "bg-amber-50 text-amber-800"
                  : "bg-slate-50 text-slate-700"
              }`}
            >
              {flag.detail}
            </div>
          ))}
          {mileage_timeline.length >= 2 && (
            <div className="mt-3 pt-3 border-t border-slate-100">
              <p className="text-xs text-slate-400 mb-2">
                Mileage Timeline ({mileage_timeline.length} readings)
              </p>
              <MileageChart readings={mileage_timeline} />
              <div className="flex justify-between text-xs text-slate-400 mt-1">
                <span>{mileage_timeline[0]?.date}</span>
                <span>{mileage_timeline[mileage_timeline.length - 1]?.date}</span>
              </div>
            </div>
          )}
          {mileage_timeline.length === 1 && (() => {
            const regDate = mot_summary?.first_used_date
              || (vehicle?.year_of_manufacture ? `${vehicle.year_of_manufacture}-01-01` : null);
            const syntheticTimeline = regDate
              ? [{ date: regDate, miles: 0 }, ...mileage_timeline]
              : mileage_timeline;
            return (
              <div className="mt-3 pt-3 border-t border-slate-100">
                <p className="text-xs text-slate-400 mb-2">
                  Mileage Timeline (1 reading + registration)
                </p>
                {syntheticTimeline.length >= 2 && (
                  <>
                    <MileageChart readings={syntheticTimeline} />
                    <div className="flex justify-between text-xs text-slate-400 mt-1">
                      <span>{syntheticTimeline[0].date} (registered)</span>
                      <span>{syntheticTimeline[syntheticTimeline.length - 1].date}</span>
                    </div>
                  </>
                )}
                {syntheticTimeline.length < 2 && (
                  <div className="flex justify-between text-xs text-slate-600">
                    <span>{mileage_timeline[0].date}</span>
                    <span className="font-mono">{mileage_timeline[0].miles.toLocaleString()} mi</span>
                  </div>
                )}
              </div>
            );
          })()}
        </Card>
      )}

      {/* Recurring Issues */}
      {failure_patterns.length > 0 && (
        <Card
          title="Recurring Issues"
          icon={icons.wrench}
          status={
            failure_patterns.some((p) => p.concern_level === "high")
              ? "fail"
              : failure_patterns.some((p) => p.concern_level === "medium")
              ? "warn"
              : "neutral"
          }
        >
          <div className="space-y-2">
            {failure_patterns.map((p, i) => {
              const categoryDefects: { text: string; type: string; date: string }[] = [];
              mot_tests.forEach((test) => {
                [...test.advisories, ...test.failures, ...test.dangerous].forEach((d) => {
                  if (d.text.toLowerCase().includes(p.category.toLowerCase())) {
                    categoryDefects.push({ text: d.text, type: d.type, date: test.date });
                  }
                });
              });

              return (
                <RecurringIssueItem
                  key={i}
                  category={p.category}
                  occurrences={p.occurrences}
                  concernLevel={p.concern_level}
                  defects={categoryDefects}
                />
              );
            })}
          </div>
        </Card>
      )}

      {/* Full MOT Test History */}
      {mot_tests && mot_tests.length > 0 && (
        <Card title={`Full MOT History (${mot_tests.length} tests)`} icon={icons.document} status="neutral">
          <div className="space-y-2">
            {mot_tests.map((test) => (
              <MOTTestItem key={test.test_number} test={test} />
            ))}
          </div>
        </Card>
      )}
    </>
  );
}
