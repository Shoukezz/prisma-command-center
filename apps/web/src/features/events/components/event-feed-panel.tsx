"use client";

import { Panel } from "@/components/ui/panel";
import { SeverityBadge } from "@/features/command-center/components/severity-badge";
import { formatGameTime } from "@/features/command-center/lib/format-time";
import { useSimulationStore } from "@/features/command-center/stores/simulation-store";

interface EventFeedPanelProps {
  className?: string;
}

export function EventFeedPanel({ className = "" }: EventFeedPanelProps) {
  const events = useSimulationStore((s) => s.events);
  const selectedEventId = useSimulationStore((s) => s.selectedEventId);
  const selectEvent = useSimulationStore((s) => s.selectEvent);
  const gameMinutes = useSimulationStore((s) => s.gameMinutes);

  return (
    <Panel
      title="Стрічка подій"
      className={className}
      headerRight={
        <span className="font-mono text-[10px] text-muted">{events.length} SIG</span>
      }
      bodyClassName="p-0"
    >
      <ul className="divide-y divide-panel-border">
        {events.length === 0 ? (
          <li className="p-3 text-muted">Подій у зоні спостереження немає.</li>
        ) : (
          events.map((event) => {
            const isSelected = event.id === selectedEventId;
            const isNew = gameMinutes - event.gameMinutes < 60;
            return (
              <li key={event.id}>
                <button
                  type="button"
                  onClick={() => selectEvent(isSelected ? null : event.id)}
                  className={`w-full px-3 py-2.5 text-left transition-colors hover:bg-slate-800/50 ${
                    isSelected ? "bg-slate-800/80 ring-1 ring-inset ring-accent/50" : ""
                  }`}
                >
                  <div className="mb-1 flex items-start justify-between gap-2">
                    <span className="font-mono text-[10px] text-accent">
                      {formatGameTime(event.gameMinutes)}
                    </span>
                    <div className="flex items-center gap-1">
                      {isNew ? (
                        <span className="text-[10px] font-semibold text-accent">НОВЕ</span>
                      ) : null}
                      <SeverityBadge severity={event.severity} />
                    </div>
                  </div>
                  <p className="text-xs font-medium leading-snug text-foreground">
                    {event.title}
                  </p>
                  <p className="mt-1 line-clamp-2 text-[11px] leading-relaxed text-muted">
                    {event.summary}
                  </p>
                  <p className="mt-1 font-mono text-[10px] text-slate-500">{event.region}</p>
                </button>
              </li>
            );
          })
        )}
      </ul>
    </Panel>
  );
}
