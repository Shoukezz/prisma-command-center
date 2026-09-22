"use client";

import { Panel } from "@/components/ui/panel";
import { ConfidenceIndicator } from "@/features/command-center/components/confidence-indicator";
import { formatGameTime } from "@/features/command-center/lib/format-time";
import { useSimulationStore } from "@/features/command-center/stores/simulation-store";

import { IntelActions } from "./intel-actions";

export function IntelligenceFeedPanel({ className = "" }: { className?: string }) {
  const intelReports = useSimulationStore((s) => s.intelReports);
  const selectedIntelId = useSimulationStore((s) => s.selectedIntelId);
  const selectIntel = useSimulationStore((s) => s.selectIntel);
  const gameMinutes = useSimulationStore((s) => s.gameMinutes);

  return (
    <Panel
      title="Стрічка розвідданих"
      className={`min-h-0 flex-1 ${className}`}
      headerRight={
        <span className="font-mono text-[10px] text-muted">{intelReports.length} RPT</span>
      }
      bodyClassName="p-0"
    >
      <ul className="divide-y divide-panel-border">
        {intelReports.length === 0 ? (
          <li className="p-3 text-muted">Звітів немає.</li>
        ) : (
          intelReports.map((report) => {
            const isSelected = report.id === selectedIntelId;
            const isNew = gameMinutes - report.gameMinutes < 60;
            return (
              <li key={report.id}>
                <div
                  role="button"
                  tabIndex={0}
                  onClick={() => selectIntel(isSelected ? null : report.id)}
                  onKeyDown={(event) => {
                    if (event.key === "Enter" || event.key === " ") {
                      event.preventDefault();
                      selectIntel(isSelected ? null : report.id);
                    }
                  }}
                  className={`w-full px-3 py-2.5 text-left transition-colors hover:bg-slate-800/50 ${
                    isSelected ? "bg-slate-800/80 ring-1 ring-inset ring-accent/50" : ""
                  }`}
                >
                  <div className="mb-1 flex items-center justify-between gap-2">
                    <span className="font-mono text-[10px] text-accent">
                      {formatGameTime(report.gameMinutes)}
                    </span>
                    <span className="rounded bg-slate-800 px-1.5 py-0.5 font-mono text-[10px] text-slate-300">
                      {report.source}
                    </span>
                  </div>
                  <p className="text-xs font-medium leading-snug text-foreground">
                    {report.title}
                    {isNew ? (
                      <span className="ml-2 text-[10px] font-semibold text-accent">НОВЕ</span>
                    ) : null}
                  </p>
                  <div className="mt-1.5">
                    <ConfidenceIndicator value={report.confidence} />
                    <span className="ml-2 text-[10px] text-muted">збір даних</span>
                  </div>
                  <p className="mt-1 line-clamp-2 text-[11px] leading-relaxed text-muted">
                    {report.summary}
                  </p>
                  <p className="mt-1 font-mono text-[10px] text-slate-500">{report.region}</p>

                  {(report.analystAssessments?.length ?? 0) > 0 ? (
                    <div className="mt-2 space-y-2 border-t border-panel-border pt-2">
                      <p className="font-mono text-[9px] uppercase tracking-wider text-muted">
                        Оцінки аналітиків
                      </p>
                      {report.analystAssessments!.map((a) => (
                        <div
                          key={a.id}
                          className="rounded border border-panel-border/80 bg-slate-900/50 px-2 py-1.5"
                          onClick={(e) => e.stopPropagation()}
                          onKeyDown={(e) => e.stopPropagation()}
                        >
                          <div className="flex items-start justify-between gap-2">
                            <div>
                              <p className="text-[10px] font-medium text-foreground">
                                {a.analystName}
                              </p>
                              <p className="font-mono text-[9px] text-slate-500">
                                {a.specialty} · {a.bias} · R{(a.reliability * 100).toFixed(0)}%
                              </p>
                            </div>
                            <span className="shrink-0 font-mono text-[10px] text-accent">
                              {a.assessedConfidence}%
                            </span>
                          </div>
                          <p className="mt-1 text-[10px] leading-snug text-muted">{a.assessment}</p>
                        </div>
                      ))}

                                      {isSelected ? (
                                        <IntelActions
                                          reportId={report.id}
                                          onActionTaken={() => {
                                            // Refresh the feed after action
                                            selectIntel(null);
                                          }}
                                        />
                                      ) : null}
                    </div>
                  ) : null}
                </div>
              </li>
            );
          })
        )}
      </ul>
    </Panel>
  );
}
