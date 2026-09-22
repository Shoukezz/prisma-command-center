"use client";

import { useEffect } from "react";

import { useSimulationStore } from "@/features/command-center/stores/simulation-store";

/** Real-time clock that advances game time when simulation is running. */
export function SimulationTicker() {
  const isPaused = useSimulationStore((s) => s.isPaused);
  const speed = useSimulationStore((s) => s.speed);
  const advanceTime = useSimulationStore((s) => s.advanceTime);

  useEffect(() => {
    if (isPaused) return;

    const intervalMs = 1000 / speed;
    const gameMinutesPerTick = 15 * speed;

    const id = window.setInterval(() => {
      void advanceTime(gameMinutesPerTick);
    }, intervalMs);

    return () => window.clearInterval(id);
  }, [isPaused, speed, advanceTime]);

  return null;
}
