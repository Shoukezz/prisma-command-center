"use client";

import { Panel } from "@/components/ui/panel";
import { formatGameTime } from "@/features/command-center/lib/format-time";
import { useSimulationStore } from "@/features/command-center/stores/simulation-store";
import type { OperationType } from "@/features/command-center/types";

const OPERATION_LABELS = { recon: "розвідка", strike: "удар" } as const;
const STATUS_LABELS = {
  planned: "заплановано",
  active: "виконується",
  completed: "завершено",
  failed: "невдало",
} as const;

interface OperationsQueuePanelProps {
  className?: string;
}

export function OperationsQueuePanel({ className = "" }: OperationsQueuePanelProps) {
  const operations = useSimulationStore((s) => s.operations);
  const assets = useSimulationStore((s) => s.assets);
  const intelReports = useSimulationStore((s) => s.intelReports);
  const selectedIntelId = useSimulationStore((s) => s.selectedIntelId);
  const planOperation = useSimulationStore((s) => s.planOperation);
  const gameMinutes = useSimulationStore((s) => s.gameMinutes);

  const selectedIntel = intelReports.find((r) => r.id === selectedIntelId);
  const availableAssets = assets.filter((a) => a.status === "available");

  const plan = (type: OperationType) => {
    if (!selectedIntel) return;
    const asset = availableAssets.find(
      (a) => (type === "recon" ? a.supportsRecon : a.supportsStrike),
    );
    if (!asset) return;
    void planOperation(type, selectedIntel.id, asset.id);
  };

  return (
    <Panel
      title="Черга операцій"
      className={className}
      headerRight={
        <span className="font-mono text-[10px] text-muted">{operations.length} OPS</span>
      }
      bodyClassName="flex flex-col gap-2 p-2"
    >
      <div className="flex flex-wrap gap-2 border-b border-panel-border pb-2">
        <button
          type="button"
          disabled={!selectedIntel || !availableAssets.some((a) => a.supportsRecon)}
          onClick={() => plan("recon")}
          className="rounded border border-panel-border bg-slate-800 px-2 py-1 font-mono text-[10px] uppercase tracking-wide hover:border-accent disabled:opacity-40"
        >
          Спланувати розвідку
        </button>
        <button
          type="button"
          disabled={!selectedIntel || !availableAssets.some((a) => a.supportsStrike)}
          onClick={() => plan("strike")}
          className="rounded border border-panel-border bg-slate-800 px-2 py-1 font-mono text-[10px] uppercase tracking-wide hover:border-accent disabled:opacity-40"
        >
          Спланувати удар
        </button>
        <span className="self-center text-[10px] text-muted">
          {selectedIntel
            ? `Розвідка ${selectedIntel.confidence}% · ${selectedIntel.source}`
            : "Оберіть розвідувальний звіт"}
        </span>
      </div>

      <ul className="max-h-[140px] divide-y divide-panel-border overflow-auto">
        {operations.length === 0 ? (
          <li className="py-2 text-xs text-muted">У черзі немає операцій.</li>
        ) : (
          operations.map((op) => {
            const active = op.status === "active";
            const done = op.status === "completed" || op.status === "failed";
            return (
              <li key={op.id} className="py-2 text-xs">
                <div className="flex items-center justify-between gap-2">
                  <span className="font-mono uppercase text-accent">
                    {OPERATION_LABELS[op.operationType]}
                  </span>
                  <span
                    className={`font-mono text-[10px] uppercase ${
                      op.status === "completed"
                        ? "text-emerald-400"
                        : op.status === "failed"
                          ? "text-red-400"
                          : "text-amber-300"
                    }`}
                  >
                    {STATUS_LABELS[op.status]}
                  </span>
                </div>
                <p className="mt-0.5 text-foreground">
                  {op.assetName} → {op.regionName}
                </p>
                <p className="font-mono text-[10px] text-muted">
                  {active
                    ? `Завершення ${formatGameTime(op.completesAt)} · достовірність ${op.intelConfidence}%`
                    : `Завершено ${formatGameTime(op.completesAt)} · достовірність ${op.intelConfidence}%`}
                  {gameMinutes >= op.completesAt && active ? " (час настав)" : ""}
                </p>
                {done && op.result ? (
                  <p
                    className={`mt-1 text-[11px] leading-snug ${
                      op.result.success ? "text-slate-300" : "text-red-300/90"
                    }`}
                  >
                    {op.result.outcomeSummary}
                  </p>
                ) : null}
              </li>
            );
          })
        )}
      </ul>
    </Panel>
  );
}
