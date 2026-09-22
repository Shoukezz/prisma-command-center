"use client";

import { useCallback, useState, type ReactNode } from "react";

import { EventFeedPanel } from "@/features/events/components/event-feed-panel";
import { IntelligenceFeedPanel } from "@/features/intelligence/components/intelligence-feed-panel";
import { StrategicMap } from "@/features/command-center/components/strategic-map";
import { SimulationHydrator } from "@/features/command-center/components/simulation-hydrator";
import { TimeControls } from "@/features/command-center/components/time-controls";
import { OnboardingGuide } from "@/features/command-center/components/onboarding-guide";
import { OperationsQueuePanel } from "@/features/operations/components/operations-queue-panel";
import { formatGameTime } from "@/features/command-center/lib/format-time";
import { useSimulationStore } from "@/features/command-center/stores/simulation-store";

export function CommandCenterShell({ children }: { children: ReactNode }) {
  const [guideTarget, setGuideTarget] = useState<string | null>(null);
  const gameMinutes = useSimulationStore((s) => s.gameMinutes);
  const isPaused = useSimulationStore((s) => s.isPaused);
  const selectedEventId = useSimulationStore((s) => s.selectedEventId);
  const selectedIntelId = useSimulationStore((s) => s.selectedIntelId);
  const operationsCount = useSimulationStore((s) => s.operations.length);
  const isHydrated = useSimulationStore((s) => s.isHydrated);
  const syncError = useSimulationStore((s) => s.syncError);
  const isSyncing = useSimulationStore((s) => s.isSyncing);
  const togglePaused = useSimulationStore((s) => s.togglePaused);
  const advanceTime = useSimulationStore((s) => s.advanceTime);
  const resetWorld = useSimulationStore((s) => s.resetWorld);
  const handleGuideTargetChange = useCallback((target: string | null) => setGuideTarget(target), []);
  const focusClass = (target: string) =>
    guideTarget === target ? "tutorial-focus" : "";

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <SimulationHydrator />
      <header className="flex min-h-11 shrink-0 flex-wrap items-center justify-between gap-2 border-b border-panel-border bg-panel px-4 py-1">
        <div className="flex items-center gap-4">
          <span className="text-sm font-semibold tracking-[0.2em] text-foreground">PRISMA</span>
          <span className="hidden text-xs text-muted sm:inline">КОМАНДНИЙ ЦЕНТР — АКТИВНА СЕСІЯ</span>
        </div>
        <div className="flex items-center gap-4 font-mono text-xs">
          <OnboardingGuide
            onTargetChange={handleGuideTargetChange}
            selectedEventId={selectedEventId}
            selectedIntelId={selectedIntelId}
            operationsCount={operationsCount}
            gameMinutes={gameMinutes}
            isHydrated={isHydrated}
          />
          <button
            type="button"
            onClick={() => void togglePaused()}
            className="rounded border border-panel-border px-2 py-1 text-[10px] text-muted transition-colors hover:border-accent hover:text-foreground"
          >
            {isPaused ? "ЗАПУСТИТИ" : "ПАУЗА"}
          </button>
          <button
            type="button"
            onClick={() => void advanceTime(60)}
            className="rounded border border-panel-border px-2 py-1 text-[10px] text-muted transition-colors hover:border-accent hover:text-foreground"
          >
            +1 ГОД
          </button>
          <button
            type="button"
            onClick={() => {
              if (!window.confirm("Почати нову гру? Поточний прогрес буде скинуто.")) return;
              void resetWorld().then((didReset) => {
                if (!didReset) return;
                window.localStorage.removeItem("prisma-onboarding-complete");
                window.location.reload();
              });
            }}
            className="rounded border border-red-900/70 px-2 py-1 text-[10px] text-red-300 transition-colors hover:border-red-400 hover:text-red-100"
          >
            НОВА ГРА
          </button>
          <span className="text-muted">ЧАС</span>
          <span className="text-accent">{formatGameTime(gameMinutes)}</span>
          <span
            className={`rounded px-2 py-0.5 text-[10px] uppercase ${
              isPaused
                ? "bg-amber-900/40 text-amber-300"
                : "bg-emerald-900/40 text-emerald-300"
            }`}
          >
            {isPaused ? "Пауза" : "Наживо"}
          </span>
          {isSyncing ? (
            <span className="text-[10px] text-muted">СИНХР.</span>
          ) : null}
          {syncError ? (
            <span className="max-w-[200px] truncate text-[10px] text-red-400" title={syncError}>
              API
            </span>
          ) : null}
        </div>
      </header>

      <div className="grid min-h-[720px] flex-1 grid-cols-1 gap-2 p-2 lg:grid-cols-[minmax(240px,280px)_1fr_minmax(260px,320px)] lg:grid-rows-[1fr_auto_auto]">
        <EventFeedPanel className={`min-h-0 ${focusClass("events")}`} />
        <div className={focusClass("map")}>
          <StrategicMap />
        </div>
        <IntelligenceFeedPanel className={focusClass("intelligence")} />
        <TimeControls className={`lg:col-span-3 ${focusClass("time")}`} />
        <OperationsQueuePanel className={`min-h-[160px] lg:col-span-3 ${focusClass("operations")}`} />
      </div>
      {children}
    </div>
  );
}
