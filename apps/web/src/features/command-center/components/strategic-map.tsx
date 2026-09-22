"use client";

import dynamic from "next/dynamic";

import { Panel } from "@/components/ui/panel";

const MapView = dynamic(
  () => import("@/features/command-center/components/map-view").then((m) => m.MapView),
  {
    ssr: false,
    loading: () => (
      <div className="flex h-full min-h-[360px] items-center justify-center font-mono text-xs text-muted">
        LOADING MAP…
      </div>
    ),
  },
);

export function StrategicMap() {
  return (
    <Panel
      title="Стратегічна мапа"
      className="min-h-0"
      headerRight={
        <span className="flex gap-3 font-mono text-[10px] text-muted">
          <span className="text-red-400">● EVT</span>
          <span className="text-blue-400">● INTEL</span>
        </span>
      }
      bodyClassName="p-1"
    >
      <MapView />
    </Panel>
  );
}
