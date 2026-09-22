"use client";

import { Panel } from "@/components/ui/panel";
import { formatGameTime } from "@/features/command-center/lib/format-time";
import type { SimulationSpeed } from "@/features/command-center/types";
import { useSimulationStore } from "@/features/command-center/stores/simulation-store";

const SPEEDS: SimulationSpeed[] = [1, 2, 4];

interface TimeControlsProps {
  className?: string;
}

export function TimeControls({ className = "" }: TimeControlsProps) {
  const gameMinutes = useSimulationStore((s) => s.gameMinutes);
  const isPaused = useSimulationStore((s) => s.isPaused);
  const speed = useSimulationStore((s) => s.speed);
  const crisisStartLabel = useSimulationStore((s) => s.crisisStartLabel);
  const togglePaused = useSimulationStore((s) => s.togglePaused);
  const setSpeed = useSimulationStore((s) => s.setSpeed);
  const advanceTime = useSimulationStore((s) => s.advanceTime);

  return (
    <Panel title="Керування часом" className={className} bodyClassName="p-3">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="space-y-1">
          <p className="font-mono text-[10px] uppercase tracking-widest text-muted">
            Оперативний час
          </p>
          <p className="font-mono text-2xl font-semibold tracking-tight text-foreground">
            {formatGameTime(gameMinutes)}
          </p>
          <p className="font-mono text-[10px] text-slate-500">Початок кризи: {crisisStartLabel}</p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={() => void togglePaused()}
            className="min-w-[100px] rounded border border-panel-border bg-slate-800 px-4 py-2 font-mono text-xs uppercase tracking-wide hover:border-accent"
          >
            {isPaused ? "Продовжити" : "Пауза"}
          </button>
          <button
            type="button"
            onClick={() => void advanceTime(60)}
            className="rounded border border-panel-border bg-slate-800 px-4 py-2 font-mono text-xs uppercase tracking-wide hover:border-accent"
          >
            +1 година
          </button>
          <button
            type="button"
            onClick={() => void advanceTime(360)}
            className="rounded border border-panel-border bg-slate-800 px-4 py-2 font-mono text-xs uppercase tracking-wide hover:border-accent"
          >
            +6 годин
          </button>
        </div>

        <div className="flex flex-col items-end gap-2">
          <span
            className={`font-mono text-[10px] uppercase tracking-widest ${
              isPaused ? "text-amber-400" : "text-emerald-400"
            }`}
          >
            {isPaused ? "Призупинено" : "Виконується"}
          </span>
          <div className="flex gap-1">
            {SPEEDS.map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => void setSpeed(s)}
                className={`rounded px-3 py-1.5 font-mono text-xs ${
                  speed === s
                    ? "bg-accent text-white"
                    : "border border-panel-border bg-slate-800 text-muted hover:text-foreground"
                }`}
              >
                {s}x
              </button>
            ))}
          </div>
        </div>
      </div>
    </Panel>
  );
}
