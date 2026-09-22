"use client";

import { useState } from "react";

import { useSimulationStore } from "@/features/command-center/stores/simulation-store";
import { apiClient } from "@/lib/api-client";

interface IntelActionsProps {
  reportId: string;
  onActionTaken?: () => void;
}

export function IntelActions({ reportId, onActionTaken }: IntelActionsProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const gameMinutes = useSimulationStore((s) => s.gameMinutes);
  const hydrate = useSimulationStore((s) => s.hydrate);

  const takeAction = async (actionType: string) => {
    try {
      setLoading(true);
      setError(null);

      await apiClient.takeIntelligenceAction(reportId, {
        action_type: actionType,
        reason: `Рішення гравця в ігровий час ${gameMinutes}`,
      });
      await hydrate();

      onActionTaken?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Невідома помилка");
    } finally {
      setLoading(false);
    }
  };

  const actions = [
    { type: "ignore", label: "Ігнорувати", color: "bg-slate-700 hover:bg-slate-600" },
    {
      type: "request_more_intel",
      label: "Запитати розвіддані",
      color: "bg-blue-700 hover:bg-blue-600",
    },
    {
      type: "launch_recon",
      label: "Розвідка",
      color: "bg-amber-700 hover:bg-amber-600",
    },
    {
      type: "launch_strike",
      label: "Удар",
      color: "bg-red-700 hover:bg-red-600",
    },
  ];

  return (
    <div className="space-y-2 border-t border-panel-border pt-2">
      <p className="font-mono text-[9px] uppercase tracking-wider text-muted">Дії гравця</p>
      <div className="flex flex-wrap gap-2">
        {actions.map((action) => (
          <button
            key={action.type}
            onClick={(event) => {
              event.stopPropagation();
              void takeAction(action.type);
            }}
            disabled={loading}
            className={`px-2.5 py-1.5 font-mono text-[10px] font-medium rounded transition-colors ${
              action.color
            } text-white disabled:opacity-50 disabled:cursor-not-allowed`}
            title={`${action.label}: виконати дію для цього звіту`}
          >
            {action.label}
          </button>
        ))}
      </div>
      {error && <p className="text-[10px] text-red-400">{error}</p>}
    </div>
  );
}
